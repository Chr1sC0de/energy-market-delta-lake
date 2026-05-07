#!/usr/bin/env python3
"""Evaluate shape-issues bundles for context coverage and stiffness."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shlex
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CATEGORY_LABELS = frozenset({"bug", "enhancement"})
DELIVERY_LABELS = frozenset(
    {"delivery-gitflow", "delivery-trunk", "delivery-exploratory"}
)
READY_LABEL = "ready-for-agent"
NEEDS_TRIAGE_LABEL = "needs-triage"
READY_FOR_HUMAN_LABEL = "ready-for-human"
REQUIRED_SECTIONS = (
    "What to build",
    "Acceptance criteria",
    "Blocked by",
    "Current context",
    "Context anchors",
    "Stiffness estimate",
    "QA plan",
)
EXPLORATORY_REQUIRED_SECTIONS = ("Review focus",)
TEXT_EXTENSIONS = frozenset(
    {
        ".cfg",
        ".ini",
        ".json",
        ".md",
        ".py",
        ".sh",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
)
TEXT_FILE_NAMES = frozenset({"Makefile", "AGENTS.md", "CONTEXT.md", "OPERATOR.md"})
IGNORED_DIRS = frozenset(
    {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ralph",
        ".ruff_cache",
        ".shape-issues",
        ".venv",
        "__pycache__",
        "generated",
        "specs",
        "vendor",
    }
)
ANCHOR_PATTERN = re.compile(
    r"(?im)^\s*[-*]\s*(?P<kind>[A-Za-z][A-Za-z ]+):\s*(?P<value>.+?)\s*$"
)
CHECKBOX_PATTERN = re.compile(r"(?m)^\s*[-*]\s+\[[ xX]\]\s+\S")
STIFFNESS_TERMS = (
    "localstack",
    "s3",
    "dagster",
    "promotion",
    "integration target",
    "local integration",
    "cross-subproject",
    "schema",
    "infrastructure",
    "end-to-end",
    "deployed",
    "push check",
)
STIFFNESS_SCAN_SECTIONS = (
    "What to build",
    "Acceptance criteria",
    "Current context",
    "QA plan",
)
STIFFNESS_DECLARATION_SECTIONS = ("Stiffness estimate",)
STIFFNESS_EXCLUSION_MARKERS = (
    "does not",
    "do not",
    "must not",
    "without",
    "out of scope",
    "non-goal",
    "non-goals",
    "prohibited",
)
ROOT_AGENT_WORKFLOW_FILES = frozenset(
    {
        "AGENTS.md",
        "OPERATOR.md",
        "CONTEXT.md",
        "scripts/ralph.py",
        "docs/repository/documentation-sync.md",
    }
)


class GateError(Exception):
    """Raised when the gate cannot evaluate the bundle."""


@dataclass(frozen=True)
class Thresholds:
    semantic_min_score: float = 0.20
    human_review_stiffness: int = 55
    split_stiffness: int = 70
    max_corpus_files: int = 2000


@dataclass(frozen=True)
class IssueDraft:
    issue_id: str
    title: str
    body: str
    labels: tuple[str, ...]
    classification: str | None
    blocked_by: tuple[str, ...]
    source_digest: str


@dataclass(frozen=True)
class Bundle:
    summary: str
    shared_context: tuple[str, ...]
    operator_overrides: dict[str, str]
    issues: tuple[IssueDraft, ...]
    source_digest: str


@dataclass(frozen=True)
class CorpusDocument:
    doc_id: str
    path: str
    text: str


@dataclass(frozen=True)
class SemanticMatch:
    path: str
    score: float


@dataclass(frozen=True)
class AnchorSummary:
    paths: tuple[str, ...]
    docs: tuple[str, ...]
    symbols: tuple[str, ...]
    labels: tuple[str, ...]
    targets: tuple[str, ...]
    qa: tuple[str, ...]
    test_lanes: tuple[str, ...]
    missing_categories: tuple[str, ...]
    missing_paths: tuple[str, ...]


@dataclass(frozen=True)
class StiffnessResult:
    score: int
    reasons: tuple[str, ...]
    declared_level: str | None
    ignored_terms: tuple[str, ...]
    surface_areas: tuple[str, ...]


def section_body(markdown: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"(?ims)^#{{1,6}}\s+{re.escape(heading)}\s*$\n"
        rf"(?P<body>.*?)(?=^#{{1,6}}\s+\S|\Z)"
    )
    match = pattern.search(markdown)
    if match is None:
        return None
    return match.group("body").strip()


def missing_sections(markdown: str, labels: frozenset[str]) -> list[str]:
    required = list(REQUIRED_SECTIONS)
    if "delivery-exploratory" in labels:
        required.extend(EXPLORATORY_REQUIRED_SECTIONS)
    missing: list[str] = []
    for heading in required:
        body = section_body(markdown, heading)
        if body is None or body.strip() == "":
            missing.append(heading)
    return missing


def parse_bundle(path: Path) -> Bundle:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise GateError("Bundle JSON root must be an object.")

    raw_issues = payload.get("issues")
    if not isinstance(raw_issues, list) or not raw_issues:
        raise GateError("Bundle must include a non-empty issues array.")

    issues: list[IssueDraft] = []
    seen_issue_ids: set[str] = set()
    for index, raw_issue in enumerate(raw_issues, start=1):
        if not isinstance(raw_issue, dict):
            raise GateError(f"Issue entry {index} must be an object.")
        title = str(raw_issue.get("title") or "").strip()
        body = str(raw_issue.get("body") or "").strip()
        if title == "":
            raise GateError(f"Issue entry {index} is missing title.")
        if body == "":
            raise GateError(f"Issue entry {index} is missing body.")
        issue_id = str(raw_issue.get("id") or slugify(title) or f"issue-{index}")
        if issue_id in seen_issue_ids:
            raise GateError(f"Duplicate issue id: {issue_id}")
        seen_issue_ids.add(issue_id)
        labels = parse_string_list(raw_issue.get("labels"))
        classification = optional_string(raw_issue.get("classification"))
        blocked_by = parse_string_list(raw_issue.get("blocked_by"))
        issues.append(
            IssueDraft(
                issue_id=issue_id,
                title=title,
                body=body,
                labels=tuple(sorted(labels)),
                classification=classification,
                blocked_by=tuple(blocked_by),
                source_digest=issue_source_digest(
                    issue_id=issue_id,
                    title=title,
                    body=body,
                    labels=tuple(sorted(labels)),
                    classification=classification,
                    blocked_by=tuple(blocked_by),
                ),
            )
        )

    overrides: dict[str, str] = {}
    raw_overrides = payload.get("operator_overrides", {})
    if isinstance(raw_overrides, dict):
        overrides = {
            str(key): str(value).strip()
            for key, value in raw_overrides.items()
            if str(value).strip() != ""
        }

    summary = str(payload.get("summary") or "").strip()
    shared_context = tuple(parse_string_list(payload.get("shared_context")))
    return Bundle(
        summary=summary,
        shared_context=shared_context,
        operator_overrides=overrides,
        issues=tuple(issues),
        source_digest=bundle_source_digest(
            summary=summary,
            shared_context=shared_context,
            operator_overrides=overrides,
            issues=tuple(issues),
        ),
    )


def parse_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip() != ""]


def optional_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def issue_source_digest(
    *,
    issue_id: str,
    title: str,
    body: str,
    labels: tuple[str, ...],
    classification: str | None,
    blocked_by: tuple[str, ...],
) -> str:
    payload = {
        "blocked_by": list(blocked_by),
        "body": body,
        "classification": classification or "",
        "id": issue_id,
        "labels": sorted(labels),
        "title": title,
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bundle_source_digest(
    *,
    summary: str,
    shared_context: tuple[str, ...],
    operator_overrides: dict[str, str],
    issues: tuple[IssueDraft, ...],
) -> str:
    payload = {
        "issues": [
            {"id": issue.issue_id, "source_digest": issue.source_digest}
            for issue in issues
        ],
        "operator_overrides": operator_overrides,
        "shared_context": list(shared_context),
        "summary": summary,
    }
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def repo_files(repo_root: Path, corpus_paths: tuple[str, ...], max_files: int) -> list[Path]:
    if corpus_paths:
        return [(repo_root / path).resolve() for path in corpus_paths]

    tracked_files = git_ls_files(repo_root)
    if tracked_files:
        return tracked_files[:max_files]

    discovered: list[Path] = []
    for current_root, dir_names, file_names in os.walk(repo_root):
        dir_names[:] = [name for name in dir_names if name not in IGNORED_DIRS]
        for file_name in file_names:
            discovered.append(Path(current_root) / file_name)
    return sorted(discovered)[:max_files]


def git_ls_files(repo_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return []
    paths: list[Path] = []
    for line in result.stdout.splitlines():
        if line.strip() == "":
            continue
        path = repo_root / line.strip()
        if is_candidate_text_file(path):
            paths.append(path)
    return sorted(paths)


def is_candidate_text_file(path: Path) -> bool:
    if path.name in TEXT_FILE_NAMES:
        return True
    return path.suffix in TEXT_EXTENSIONS


def build_corpus(
    repo_root: Path,
    *,
    corpus_paths: tuple[str, ...],
    max_files: int,
) -> tuple[CorpusDocument, ...]:
    documents: list[CorpusDocument] = []
    for path in repo_files(repo_root, corpus_paths, max_files):
        if not path.exists() or not path.is_file() or not is_candidate_text_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative_path = str(path.relative_to(repo_root))
        if text.strip() == "":
            continue
        documents.append(
            CorpusDocument(
                doc_id=f"doc:{len(documents)}",
                path=relative_path,
                text=text[:12000],
            )
        )
    if not documents:
        raise GateError("No corpus documents were available for semantic scoring.")
    return tuple(documents)


def parse_anchors(body: str, repo_root: Path) -> AnchorSummary:
    section = section_body(body, "Context anchors") or ""
    values: dict[str, list[str]] = {
        "paths": [],
        "docs": [],
        "symbols": [],
        "labels": [],
        "targets": [],
        "qa": [],
        "test_lanes": [],
    }
    for match in ANCHOR_PATTERN.finditer(section):
        kind = normalize_anchor_kind(match.group("kind"))
        value = clean_anchor_value(match.group("value"))
        if kind in values and value != "":
            values[kind].append(value)

    missing_categories: list[str] = []
    if not values["paths"] and not values["docs"]:
        missing_categories.append("path_or_doc")
    if not values["symbols"]:
        missing_categories.append("symbol")
    if not values["labels"] and not values["targets"]:
        missing_categories.append("label_or_target")
    if not values["qa"] and not values["test_lanes"]:
        missing_categories.append("qa_or_test_lane")

    missing_paths: list[str] = []
    for candidate in [*values["paths"], *values["docs"]]:
        candidate_path = repo_root / candidate
        if not candidate_path.exists():
            missing_paths.append(candidate)

    return AnchorSummary(
        paths=tuple(sorted(set(values["paths"]))),
        docs=tuple(sorted(set(values["docs"]))),
        symbols=tuple(sorted(set(values["symbols"]))),
        labels=tuple(sorted(set(values["labels"]))),
        targets=tuple(sorted(set(values["targets"]))),
        qa=tuple(sorted(set(values["qa"]))),
        test_lanes=tuple(sorted(set(values["test_lanes"]))),
        missing_categories=tuple(missing_categories),
        missing_paths=tuple(sorted(set(missing_paths))),
    )


def normalize_anchor_kind(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_")
    if normalized in {"path", "file", "source_path"}:
        return "paths"
    if normalized in {"doc", "docs", "documentation"}:
        return "docs"
    if normalized in {"symbol", "constant", "symbols", "constants"}:
        return "symbols"
    if normalized in {"label", "labels"}:
        return "labels"
    if normalized in {"target", "branch", "asset", "command_target"}:
        return "targets"
    if normalized in {"qa", "command", "check"}:
        return "qa"
    if normalized in {"test_lane", "lane"}:
        return "test_lanes"
    return normalized


def clean_anchor_value(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith("`") and "`" in cleaned[1:]:
        return cleaned.split("`", 2)[1].strip()
    return cleaned.strip("`").strip()


def run_embedding_provider(
    command: str,
    records: list[dict[str, str]],
    *,
    repo_root: Path,
) -> dict[str, list[float]]:
    if command.strip() == "":
        raise GateError("Embedding command is required.")
    input_text = "".join(json.dumps(record) + "\n" for record in records)
    result = subprocess.run(
        shlex.split(command),
        cwd=repo_root,
        input=input_text,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateError(f"Embedding provider failed: {detail}")

    vectors: dict[str, list[float]] = {}
    for line_number, line in enumerate(result.stdout.splitlines(), start=1):
        if line.strip() == "":
            continue
        payload = json.loads(line)
        if not isinstance(payload, dict):
            raise GateError(f"Provider output line {line_number} is not an object.")
        record_id = str(payload.get("id") or "")
        vector = payload.get("vector")
        if record_id == "" or not isinstance(vector, list):
            raise GateError(f"Provider output line {line_number} is malformed.")
        vectors[record_id] = [float(value) for value in vector]
    missing = sorted(record["id"] for record in records if record["id"] not in vectors)
    if missing:
        raise GateError(f"Embedding provider omitted vector(s): {', '.join(missing)}")
    return vectors


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise GateError("Embedding vectors must have the same dimension.")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    dot = sum(left_value * right_value for left_value, right_value in zip(left, right))
    return dot / (left_norm * right_norm)


def issue_query(issue: IssueDraft, shared_context: tuple[str, ...]) -> str:
    parts = [
        issue.title,
        section_body(issue.body, "What to build") or "",
        section_body(issue.body, "Current context") or "",
        section_body(issue.body, "Context anchors") or "",
        "\n".join(shared_context),
    ]
    return "\n\n".join(part for part in parts if part.strip() != "")


def operator_approval_evidence(body: str) -> dict[str, Any]:
    evidence = section_body(body, "Operator approval evidence")
    if evidence is None or evidence.strip() == "":
        return {"present": False, "body": "", "warnings": []}

    warnings: list[str] = [
        "Approval evidence is context only; it does not grant tool permission."
    ]
    evidence_lower = evidence.lower()
    if "trust_remote_code" in evidence_lower and "no-trust-remote-code" not in evidence_lower:
        warnings.append("Evidence mentions trust_remote_code without requiring it to be disabled.")
    if "corpus scope" not in evidence_lower:
        warnings.append("Evidence does not name a corpus scope.")
    if "prohibited" not in evidence_lower:
        warnings.append("Evidence does not list prohibited actions.")
    return {"present": True, "body": evidence, "warnings": warnings}


def semantic_matches_for_issue(
    issue: IssueDraft,
    documents: tuple[CorpusDocument, ...],
    vectors: dict[str, list[float]],
) -> list[SemanticMatch]:
    query_vector = vectors[f"issue:{issue.issue_id}"]
    matches = [
        SemanticMatch(
            path=document.path,
            score=cosine_similarity(query_vector, vectors[document.doc_id]),
        )
        for document in documents
    ]
    return sorted(matches, key=lambda match: match.score, reverse=True)[:5]


def area_for_path(path: str) -> str:
    parts = Path(path).parts
    if not parts:
        return path
    normalized = path.replace("\\", "/")
    if normalized in ROOT_AGENT_WORKFLOW_FILES:
        return "root-agent-workflow"
    if parts[0] == ".agents":
        return "root-agent-workflow"
    if parts[0] == "docs" and len(parts) >= 2 and parts[1] == "agents":
        return "root-agent-workflow"
    if parts[0] == "tests":
        return "root-agent-workflow"
    if parts[0] == "backend-services" and len(parts) >= 2:
        return "/".join(parts[:2])
    if parts[0] == "infrastructure" and len(parts) >= 2:
        return "/".join(parts[:2])
    return parts[0]


def declared_stiffness_level(body: str) -> str | None:
    section = section_body(body, "Stiffness estimate")
    if section is None:
        return None
    match = re.search(
        r"\b(?P<level>medium-high|medium high|low|medium|high)\b",
        section,
        flags=re.IGNORECASE,
    )
    if match is None:
        return None
    level = match.group("level").lower().replace(" ", "-")
    if level == "medium-high":
        return level
    if level in {"low", "medium", "high"}:
        return level
    return None


def split_stiffness_fragments(text: str) -> list[str]:
    fragments: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "" or stripped.startswith("```"):
            continue
        stripped = re.sub(r"^\s*[-*]\s*(?:\[[ xX]\]\s*)?", "", stripped).strip()
        fragments.extend(
            fragment.strip()
            for fragment in re.split(r"(?<=[.!?])\s+", stripped)
            if fragment.strip() != ""
        )
    return fragments


def has_stiffness_exclusion_marker(text: str) -> bool:
    text_lower = text.lower()
    if re.search(r"\bno\b", text_lower):
        return True
    return any(marker in text_lower for marker in STIFFNESS_EXCLUSION_MARKERS)


def clipped_evidence(text: str, *, limit: int = 120) -> str:
    single_line = re.sub(r"\s+", " ", text).strip()
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3].rstrip() + "..."


def stiffness_term_evidence(body: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    matched_terms: set[str] = set()
    ignored_terms: list[str] = []
    for heading in STIFFNESS_SCAN_SECTIONS:
        section = section_body(body, heading)
        if section is None:
            continue
        for fragment in split_stiffness_fragments(section):
            fragment_lower = fragment.lower()
            terms = [term for term in STIFFNESS_TERMS if term in fragment_lower]
            if not terms:
                continue
            if has_stiffness_exclusion_marker(fragment):
                ignored_terms.extend(
                    f"{term} in ## {heading}: {clipped_evidence(fragment)}"
                    for term in terms
                )
                continue
            matched_terms.update(terms)
    for heading in STIFFNESS_DECLARATION_SECTIONS:
        section = section_body(body, heading)
        if section is None:
            continue
        for fragment in split_stiffness_fragments(section):
            fragment_lower = fragment.lower()
            terms = [term for term in STIFFNESS_TERMS if term in fragment_lower]
            if not terms or not has_stiffness_exclusion_marker(fragment):
                continue
            ignored_terms.extend(
                f"{term} in ## {heading}: {clipped_evidence(fragment)}"
                for term in terms
            )
    return tuple(sorted(matched_terms)), tuple(sorted(set(ignored_terms)))


def stiffness_score(
    issue: IssueDraft,
    anchors: AnchorSummary,
    matches: list[SemanticMatch],
) -> StiffnessResult:
    reasons: list[str] = []
    score = 0
    area_values = {
        area_for_path(path)
        for path in [*anchors.paths, *anchors.docs, *(match.path for match in matches[:3])]
    }
    if len(area_values) > 1:
        added = min(30, (len(area_values) - 1) * 15)
        score += added
        reasons.append(f"spans {len(area_values)} repo areas")

    matched_terms, ignored_terms = stiffness_term_evidence(issue.body)
    if matched_terms:
        added = min(40, len(matched_terms) * 8)
        score += added
        reasons.append("mentions stiff boundary terms: " + ", ".join(matched_terms))
        if len(matched_terms) >= 5:
            score += 10
            reasons.append("mentions many stiff boundary terms")

    criteria_count = len(CHECKBOX_PATTERN.findall(section_body(issue.body, "Acceptance criteria") or ""))
    if criteria_count > 7:
        score += 20
        reasons.append(f"has {criteria_count} acceptance criteria")
    elif criteria_count > 4:
        score += 10
        reasons.append(f"has {criteria_count} acceptance criteria")

    qa_text = "\n".join([*anchors.qa, *anchors.test_lanes]).lower()
    if any(term in qa_text for term in ("integration", "end-to-end", "deployed", "push check")):
        score += 15
        reasons.append("requires an expensive Test lane")

    blocked_by = (section_body(issue.body, "Blocked by") or "").lower()
    if any(term in blocked_by for term in ("tbd", "unknown", "unclear")):
        score += 15
        reasons.append("has vague blockers")

    context = (section_body(issue.body, "Current context") or "").lower()
    if any(term in context for term in ("tbd", "unknown", "fill in", "todo")):
        score += 10
        reasons.append("has placeholder context")

    return StiffnessResult(
        score=min(score, 100),
        reasons=tuple(reasons or ["low explicit stiffness signals"]),
        declared_level=declared_stiffness_level(issue.body),
        ignored_terms=ignored_terms,
        surface_areas=tuple(sorted(area_values)),
    )


def validate_labels(labels: frozenset[str]) -> list[str]:
    reasons: list[str] = []
    category = labels.intersection(CATEGORY_LABELS)
    delivery = labels.intersection(DELIVERY_LABELS)
    if len(category) != 1:
        reasons.append("expected exactly one category label")
    if len(delivery) != 1:
        reasons.append("expected exactly one Delivery mode label")
    return reasons


def action_for_issue(
    *,
    issue: IssueDraft,
    labels: frozenset[str],
    validation_reasons: list[str],
    semantic_passed: bool,
    stiffness: int,
    thresholds: Thresholds,
    override: str | None,
) -> tuple[str, bool, str]:
    if validation_reasons or not semantic_passed:
        return "needs-context", False, NEEDS_TRIAGE_LABEL
    if stiffness >= thresholds.split_stiffness:
        if override is not None:
            return "ready", True, READY_LABEL
        return "split", False, NEEDS_TRIAGE_LABEL
    if stiffness >= thresholds.human_review_stiffness:
        if override is not None:
            return "ready", True, READY_LABEL
        return "human-review", False, READY_FOR_HUMAN_LABEL
    if "delivery-exploratory" in labels:
        return "exploratory", True, READY_LABEL
    return "ready", True, READY_LABEL


def evaluate_bundle(
    bundle: Bundle,
    *,
    repo_root: Path,
    embedding_command: str,
    corpus_paths: tuple[str, ...],
    thresholds: Thresholds,
    provider_name: str,
    model_id: str,
) -> dict[str, Any]:
    documents = build_corpus(
        repo_root,
        corpus_paths=corpus_paths,
        max_files=thresholds.max_corpus_files,
    )
    records: list[dict[str, str]] = [
        {"id": f"issue:{issue.issue_id}", "kind": "query", "text": issue_query(issue, bundle.shared_context)}
        for issue in bundle.issues
    ]
    records.extend(
        {"id": document.doc_id, "kind": "document", "text": document.text}
        for document in documents
    )
    vectors = run_embedding_provider(embedding_command, records, repo_root=repo_root)

    issue_reports: list[dict[str, Any]] = []
    for issue in bundle.issues:
        labels = frozenset(issue.labels)
        anchors = parse_anchors(issue.body, repo_root)
        matches = semantic_matches_for_issue(issue, documents, vectors)
        top_score = matches[0].score if matches else 0.0
        semantic_passed = top_score >= thresholds.semantic_min_score

        validation_reasons: list[str] = []
        validation_reasons.extend(
            f"missing required section: ## {heading}"
            for heading in missing_sections(issue.body, labels)
        )
        validation_reasons.extend(validate_labels(labels))
        validation_reasons.extend(
            f"missing anchor category: {category}"
            for category in anchors.missing_categories
        )
        validation_reasons.extend(
            f"anchor path does not exist: {path}"
            for path in anchors.missing_paths
        )
        if not semantic_passed:
            validation_reasons.append(
                "semantic coverage below threshold "
                f"{thresholds.semantic_min_score:.2f}: {top_score:.3f}"
            )

        stiffness = stiffness_score(issue, anchors, matches)
        stiffness_level_value = stiffness_level(stiffness.score, thresholds)
        declared_mismatch = declared_stiffness_mismatch(
            stiffness.declared_level,
            stiffness.score,
            thresholds,
        )
        override = bundle.operator_overrides.get(issue.issue_id)
        action, ready, state_label = action_for_issue(
            issue=issue,
            labels=labels,
            validation_reasons=validation_reasons,
            semantic_passed=semantic_passed,
            stiffness=stiffness.score,
            thresholds=thresholds,
            override=override,
        )
        issue_reports.append(
            {
                "id": issue.issue_id,
                "title": issue.title,
                "source_digest": issue.source_digest,
                "action": action,
                "ready": ready,
                "recommended_state_label": state_label,
                "recommended_labels": sorted({state_label, *issue.labels}),
                "operator_override": override,
                "operator_approval_evidence": operator_approval_evidence(issue.body),
                "validation_reasons": validation_reasons,
                "semantic": {
                    "passed": semantic_passed,
                    "top_score": round(top_score, 6),
                    "matches": [
                        {"path": match.path, "score": round(match.score, 6)}
                        for match in matches
                    ],
                },
                "anchors": {
                    "paths": list(anchors.paths),
                    "docs": list(anchors.docs),
                    "symbols": list(anchors.symbols),
                    "labels": list(anchors.labels),
                    "targets": list(anchors.targets),
                    "qa": list(anchors.qa),
                    "test_lanes": list(anchors.test_lanes),
                    "missing_categories": list(anchors.missing_categories),
                    "missing_paths": list(anchors.missing_paths),
                },
                "stiffness": {
                    "score": stiffness.score,
                    "level": stiffness_level_value,
                    "declared_level": stiffness.declared_level,
                    "declared_mismatch": declared_mismatch,
                    "reasons": list(stiffness.reasons),
                    "ignored_terms": list(stiffness.ignored_terms),
                    "surface_areas": list(stiffness.surface_areas),
                },
            }
        )

    return {
        "summary": bundle.summary,
        "bundle_digest": bundle.source_digest,
        "thresholds": {
            "semantic_min_score": thresholds.semantic_min_score,
            "human_review_stiffness": thresholds.human_review_stiffness,
            "split_stiffness": thresholds.split_stiffness,
            "max_corpus_files": thresholds.max_corpus_files,
        },
        "embedding": {
            "provider": provider_name,
            "model": model_id,
            "command": embedding_command,
            "source": embedding_source(provider_name, model_id),
        },
        "corpus": {
            "documents": len(documents),
            "paths": [document.path for document in documents],
        },
        "issues": issue_reports,
    }


def stiffness_level(score: int, thresholds: Thresholds) -> str:
    if score >= thresholds.split_stiffness:
        return "high"
    if score >= thresholds.human_review_stiffness:
        return "medium-high"
    if score >= 30:
        return "medium"
    return "low"


def declared_stiffness_mismatch(
    declared_level: str | None,
    score: int,
    thresholds: Thresholds,
) -> bool:
    if declared_level is None:
        return False
    if declared_level == "low":
        return score >= 30
    if declared_level == "medium":
        return score < 30 or score >= thresholds.split_stiffness
    if declared_level == "medium-high":
        return score < thresholds.human_review_stiffness or score >= thresholds.split_stiffness
    if declared_level == "high":
        return score < thresholds.split_stiffness
    return False


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Shape Issues Gate Report",
        "",
        f"Summary: {report['summary'] or 'No summary provided.'}",
        "",
        "## Embedding",
        "",
        f"- Provider: `{report['embedding']['provider']}`",
        f"- Model: `{report['embedding']['model']}`",
        f"- Source: {report['embedding']['source']}",
        "",
        "## Thresholds",
        "",
        f"- Semantic minimum score: `{report['thresholds']['semantic_min_score']}`",
        f"- Human review stiffness: `{report['thresholds']['human_review_stiffness']}`",
        f"- Split stiffness: `{report['thresholds']['split_stiffness']}`",
        "",
        "## Issues",
        "",
    ]
    for issue in report["issues"]:
        lines.extend(
            [
                f"### {issue['id']}: {issue['title']}",
                "",
                f"- Action: `{issue['action']}`",
                f"- Ready: `{str(issue['ready']).lower()}`",
                f"- Recommended labels: {', '.join(f'`{label}`' for label in issue['recommended_labels'])}",
                f"- Stiffness: `{issue['stiffness']['score']}` ({issue['stiffness']['level']})",
                f"- Stiffness surface areas: {', '.join(f'`{area}`' for area in issue['stiffness']['surface_areas'])}",
                f"- Semantic top score: `{issue['semantic']['top_score']}`",
            ]
        )
        declared_level = issue["stiffness"]["declared_level"]
        if declared_level is not None:
            mismatch = str(issue["stiffness"]["declared_mismatch"]).lower()
            lines.append(f"- Declared stiffness: `{declared_level}` (mismatch: `{mismatch}`)")
        if issue["operator_override"] is not None:
            lines.append(f"- Operator override: {issue['operator_override']}")
        approval = issue["operator_approval_evidence"]
        if approval["present"]:
            lines.append("- Operator approval evidence: present")
            for warning in approval["warnings"]:
                lines.append(f"  - {warning}")
        if issue["validation_reasons"]:
            lines.append("- Validation reasons:")
            lines.extend(f"  - {reason}" for reason in issue["validation_reasons"])
        lines.append("- Top semantic matches:")
        lines.extend(
            f"  - `{match['path']}`: `{match['score']}`"
            for match in issue["semantic"]["matches"][:3]
        )
        lines.append("- Stiffness reasons:")
        lines.extend(f"  - {reason}" for reason in issue["stiffness"]["reasons"])
        if issue["stiffness"]["ignored_terms"]:
            lines.append("- Ignored stiffness mentions:")
            lines.extend(f"  - {term}" for term in issue["stiffness"]["ignored_terms"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def default_embedding_command() -> str:
    env_command = os.environ.get("SHAPE_ISSUES_EMBED_COMMAND")
    if env_command is not None and env_command.strip() != "":
        return env_command
    return (
        "uv run --with sentence-transformers --with torch "
        "python .agents/skills/shape-issues/scripts/hf_embed_jsonl.py "
        "--model Qwen/Qwen3-Embedding-8B"
    )


def embedding_source(provider_name: str, model_id: str) -> str:
    if provider_name.lower() == "huggingface" and model_id.strip() != "":
        return f"https://huggingface.co/{model_id.strip()}"
    return "local"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a shape-issues bundle for readiness and stiffness.",
    )
    parser.add_argument("bundle", type=Path, help="Path to bundle JSON.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--embedding-command", default=default_embedding_command())
    parser.add_argument("--provider-name", default="huggingface")
    parser.add_argument("--model-id", default="Qwen/Qwen3-Embedding-8B")
    parser.add_argument("--corpus-path", action="append", default=[])
    parser.add_argument("--semantic-min-score", type=float, default=0.20)
    parser.add_argument("--human-review-stiffness", type=int, default=55)
    parser.add_argument("--split-stiffness", type=int, default=70)
    parser.add_argument("--max-corpus-files", type=int, default=2000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or args.bundle.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    thresholds = Thresholds(
        semantic_min_score=args.semantic_min_score,
        human_review_stiffness=args.human_review_stiffness,
        split_stiffness=args.split_stiffness,
        max_corpus_files=args.max_corpus_files,
    )
    try:
        bundle = parse_bundle(args.bundle)
        report = evaluate_bundle(
            bundle,
            repo_root=repo_root,
            embedding_command=args.embedding_command,
            corpus_paths=tuple(args.corpus_path),
            thresholds=thresholds,
            provider_name=args.provider_name,
            model_id=args.model_id,
        )
    except (GateError, json.JSONDecodeError, OSError, ValueError) as error:
        sys.stderr.write(f"shape-issues gate failed: {error}\n")
        raise SystemExit(1)

    (out_dir / "report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "report.md").write_text(report_markdown(report), encoding="utf-8")
    sys.stdout.write(str(out_dir / "report.md") + "\n")


if __name__ == "__main__":
    main()
