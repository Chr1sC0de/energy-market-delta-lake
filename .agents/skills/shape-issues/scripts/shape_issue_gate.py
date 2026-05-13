#!/usr/bin/env python3
"""Evaluate shape-issues bundles for context evidence and stiffness."""

from __future__ import annotations

import argparse
import hashlib
import json
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
CONTEXT_ASSESSOR_SCHEMA_VERSION = "shape-issues-context-assessor-v1"
DEFAULT_CONTEXT_ASSESSOR_PROVIDER = "codex"
DEFAULT_RG_CANDIDATE_FILES = 8
MAX_SEARCH_TERMS = 24
MAX_EVIDENCE_SNIPPETS_PER_FILE = 3
MAX_SNIPPET_CHARS = 900
MAX_FILE_READ_CHARS = 80_000
ASSESSOR_VERDICTS = frozenset({"pass", "weak", "fail"})
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
STOP_WORDS = frozenset(
    {
        "about",
        "after",
        "again",
        "against",
        "agent",
        "before",
        "build",
        "check",
        "context",
        "delivery",
        "draft",
        "drafts",
        "evidence",
        "existing",
        "from",
        "gate",
        "github",
        "implementation",
        "issue",
        "issues",
        "label",
        "labels",
        "local",
        "must",
        "plan",
        "ready",
        "report",
        "reports",
        "root",
        "run",
        "shape",
        "test",
        "tests",
        "that",
        "this",
        "with",
        "work",
    }
)


class GateError(Exception):
    """Raised when the gate cannot evaluate the bundle."""


@dataclass(frozen=True)
class Thresholds:
    human_review_stiffness: int = 55
    split_stiffness: int = 70
    max_rg_candidate_files: int = DEFAULT_RG_CANDIDATE_FILES


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
class EvidenceSnippet:
    start_line: int
    text: str


@dataclass(frozen=True)
class EvidenceDocument:
    path: str
    source: str
    snippets: tuple[EvidenceSnippet, ...]


@dataclass(frozen=True)
class EvidenceCorpus:
    digest: str
    documents: tuple[EvidenceDocument, ...]
    anchor_paths: tuple[str, ...]
    rg_candidate_paths: tuple[str, ...]


@dataclass(frozen=True)
class RawContextAssessment:
    verdict: str
    confidence: float | None
    cited_paths: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ContextAssessorProviderResult:
    assessments: dict[str, RawContextAssessment]
    bundle_digest: str | None
    corpus_digest: str | None


@dataclass(frozen=True)
class ContextAssessment:
    verdict: str
    confidence: float
    cited_paths: tuple[str, ...]
    reasons: tuple[str, ...]
    valid: bool
    validation_reasons: tuple[str, ...]


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


def is_candidate_text_file(path: Path) -> bool:
    if path.name in TEXT_FILE_NAMES:
        return True
    return path.suffix in TEXT_EXTENSIONS


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
        if kind in {"paths", "docs"} and value != "":
            value = normalize_repo_path_text(repo_root, value) or value
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
        relative_path = normalize_repo_path_text(repo_root, candidate)
        if relative_path is None or not (repo_root / relative_path).exists():
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


def normalize_repo_path_text(repo_root: Path, path_text: str) -> str | None:
    if path_text.strip() == "":
        return None
    candidate = Path(path_text)
    if candidate.is_absolute():
        resolved = candidate.resolve()
    else:
        resolved = (repo_root / candidate).resolve()
    try:
        relative = resolved.relative_to(repo_root)
    except ValueError:
        return None
    return relative.as_posix()


def context_search_terms(
    issue: IssueDraft,
    shared_context: tuple[str, ...],
    anchors: AnchorSummary,
) -> tuple[str, ...]:
    terms: list[str] = []

    def add(term: str) -> None:
        cleaned = re.sub(r"\s+", " ", term).strip()
        if len(cleaned) < 4:
            return
        lowered = cleaned.lower()
        if lowered in STOP_WORDS or lowered in {item.lower() for item in terms}:
            return
        terms.append(cleaned)

    for value in [*anchors.symbols, *anchors.labels, *anchors.targets]:
        add(value)
    text_parts = [
        issue.title,
        section_body(issue.body, "What to build") or "",
        section_body(issue.body, "Current context") or "",
        section_body(issue.body, "QA plan") or "",
        "\n".join(shared_context),
    ]
    for text in text_parts:
        for quoted in re.findall(r"`([^`]{4,80})`", text):
            add(quoted)
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", text):
            add(word)
    return tuple(terms[:MAX_SEARCH_TERMS])


def build_issue_evidence(
    issue: IssueDraft,
    shared_context: tuple[str, ...],
    anchors: AnchorSummary,
    *,
    repo_root: Path,
    max_rg_candidate_files: int,
) -> EvidenceCorpus:
    search_terms = context_search_terms(issue, shared_context, anchors)
    anchor_paths = tuple(
        path
        for path in sorted({*anchors.paths, *anchors.docs})
        if is_readable_repo_text_file(repo_root, path)
    )
    rg_paths = rg_candidate_files(
        repo_root,
        search_terms,
        excluded_paths=set(anchor_paths),
        max_files=max_rg_candidate_files,
    )
    documents: list[EvidenceDocument] = []
    for path in anchor_paths:
        document = read_evidence_document(
            repo_root,
            path,
            source="anchor",
            search_terms=search_terms,
        )
        if document is not None:
            documents.append(document)
    for path in rg_paths:
        document = read_evidence_document(
            repo_root,
            path,
            source="rg-candidate",
            search_terms=search_terms,
        )
        if document is not None:
            documents.append(document)

    document_tuple = tuple(documents)
    return EvidenceCorpus(
        digest=evidence_corpus_digest(document_tuple),
        documents=document_tuple,
        anchor_paths=anchor_paths,
        rg_candidate_paths=tuple(rg_paths),
    )


def is_readable_repo_text_file(repo_root: Path, relative_path: str) -> bool:
    normalized = normalize_repo_path_text(repo_root, relative_path)
    if normalized is None:
        return False
    path = repo_root / normalized
    return path.exists() and path.is_file() and is_candidate_text_file(path)


def rg_candidate_files(
    repo_root: Path,
    search_terms: tuple[str, ...],
    *,
    excluded_paths: set[str],
    max_files: int,
) -> tuple[str, ...]:
    if not search_terms or max_files <= 0:
        return ()
    args = [
        "rg",
        "--files-with-matches",
        "--fixed-strings",
        "--ignore-case",
        "--color",
        "never",
    ]
    for ignored_dir in sorted(IGNORED_DIRS):
        args.extend(["--glob", f"!{ignored_dir}/**"])
    for term in search_terms:
        args.extend(["-e", term])
    args.append(".")
    try:
        result = subprocess.run(
            args,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ()
    if result.returncode == 1:
        return ()
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GateError(f"rg candidate search failed: {detail}")

    candidates: set[str] = set()
    for line in result.stdout.splitlines():
        normalized = line.strip().removeprefix("./")
        relative_path = normalize_repo_path_text(repo_root, normalized)
        if relative_path is None:
            continue
        if relative_path in excluded_paths:
            continue
        if not is_readable_repo_text_file(repo_root, relative_path):
            continue
        candidates.add(relative_path)
    return tuple(sorted(candidates)[:max_files])


def read_evidence_document(
    repo_root: Path,
    relative_path: str,
    *,
    source: str,
    search_terms: tuple[str, ...],
) -> EvidenceDocument | None:
    path = repo_root / relative_path
    try:
        text = path.read_text(encoding="utf-8")[:MAX_FILE_READ_CHARS]
    except UnicodeDecodeError:
        return None
    if text.strip() == "":
        return None
    return EvidenceDocument(
        path=relative_path,
        source=source,
        snippets=evidence_snippets(text, search_terms),
    )


def evidence_snippets(
    text: str,
    search_terms: tuple[str, ...],
) -> tuple[EvidenceSnippet, ...]:
    lines = text.splitlines()
    if not lines:
        return ()
    lowered_terms = tuple(term.lower() for term in search_terms)
    hit_indexes: list[int] = []
    for index, line in enumerate(lines):
        line_lower = line.lower()
        if any(term in line_lower for term in lowered_terms):
            hit_indexes.append(index)
        if len(hit_indexes) >= MAX_EVIDENCE_SNIPPETS_PER_FILE:
            break
    if not hit_indexes:
        hit_indexes = [0]

    snippets: list[EvidenceSnippet] = []
    seen_windows: set[tuple[int, int]] = set()
    for index in hit_indexes:
        start = max(0, index - 2)
        end = min(len(lines), index + 3)
        window = (start, end)
        if window in seen_windows:
            continue
        seen_windows.add(window)
        snippet = "\n".join(
            f"{line_number + 1}: {lines[line_number]}"
            for line_number in range(start, end)
        )
        snippets.append(
            EvidenceSnippet(
                start_line=start + 1,
                text=clip_snippet(snippet),
            )
        )
    return tuple(snippets)


def clip_snippet(text: str) -> str:
    if len(text) <= MAX_SNIPPET_CHARS:
        return text
    return text[: MAX_SNIPPET_CHARS - 3].rstrip() + "..."


def evidence_corpus_digest(documents: tuple[EvidenceDocument, ...]) -> str:
    payload = [
        {
            "path": document.path,
            "snippets": [
                {"start_line": snippet.start_line, "text": snippet.text}
                for snippet in document.snippets
            ],
            "source": document.source,
        }
        for document in documents
    ]
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def bundle_context_corpus_digest(
    corpora_by_issue: dict[str, EvidenceCorpus],
) -> str:
    payload = [
        {"id": issue_id, "corpus_digest": corpus.digest}
        for issue_id, corpus in sorted(corpora_by_issue.items())
    ]
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def assessor_request_payload(
    bundle: Bundle,
    anchors_by_issue: dict[str, AnchorSummary],
    corpora_by_issue: dict[str, EvidenceCorpus],
) -> dict[str, Any]:
    corpus_digest = bundle_context_corpus_digest(corpora_by_issue)
    return {
        "schema_version": CONTEXT_ASSESSOR_SCHEMA_VERSION,
        "bundle_digest": bundle.source_digest,
        "corpus_digest": corpus_digest,
        "shared_context": list(bundle.shared_context),
        "issues": [
            {
                "id": issue.issue_id,
                "title": issue.title,
                "body": issue.body,
                "source_digest": issue.source_digest,
                "anchors": anchor_summary_payload(anchors_by_issue[issue.issue_id]),
                "context_corpus": evidence_corpus_payload(
                    corpora_by_issue[issue.issue_id]
                ),
            }
            for issue in bundle.issues
        ],
    }


def anchor_summary_payload(anchors: AnchorSummary) -> dict[str, Any]:
    return {
        "paths": list(anchors.paths),
        "docs": list(anchors.docs),
        "symbols": list(anchors.symbols),
        "labels": list(anchors.labels),
        "targets": list(anchors.targets),
        "qa": list(anchors.qa),
        "test_lanes": list(anchors.test_lanes),
        "missing_categories": list(anchors.missing_categories),
        "missing_paths": list(anchors.missing_paths),
    }


def evidence_corpus_payload(corpus: EvidenceCorpus) -> dict[str, Any]:
    return {
        "digest": corpus.digest,
        "anchor_paths": list(corpus.anchor_paths),
        "rg_candidate_paths": list(corpus.rg_candidate_paths),
        "evidence": [
            {
                "path": document.path,
                "source": document.source,
                "snippets": [
                    {"start_line": snippet.start_line, "text": snippet.text}
                    for snippet in document.snippets
                ],
            }
            for document in corpus.documents
        ],
    }


def run_context_assessor_provider(
    command: str,
    request_payload: dict[str, Any],
    *,
    repo_root: Path,
) -> ContextAssessorProviderResult:
    if command.strip() == "":
        raise GateError("Context assessor command is required.")
    input_text = json.dumps(request_payload, separators=(",", ":"), sort_keys=True)
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
        raise GateError(f"Context assessor provider failed: {detail}")
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise GateError("Context assessor provider returned invalid JSON.") from error
    if not isinstance(payload, dict):
        raise GateError("Context assessor provider output must be a JSON object.")

    raw_assessments = payload.get("assessments")
    if not isinstance(raw_assessments, list):
        raise GateError("Context assessor provider output must include assessments.")

    assessments: dict[str, RawContextAssessment] = {}
    for index, raw_assessment in enumerate(raw_assessments, start=1):
        if not isinstance(raw_assessment, dict):
            raise GateError(f"Assessment entry {index} must be an object.")
        issue_id = str(
            raw_assessment.get("id") or raw_assessment.get("issue_id") or ""
        ).strip()
        if issue_id == "":
            raise GateError(f"Assessment entry {index} is missing id.")
        if issue_id in assessments:
            raise GateError(f"Duplicate assessment id: {issue_id}")
        confidence = optional_float(raw_assessment.get("confidence"))
        assessments[issue_id] = RawContextAssessment(
            verdict=str(raw_assessment.get("verdict") or "").strip().lower(),
            confidence=confidence,
            cited_paths=tuple(parse_string_list(raw_assessment.get("cited_paths"))),
            reasons=tuple(parse_string_list(raw_assessment.get("reasons"))),
        )

    return ContextAssessorProviderResult(
        assessments=assessments,
        bundle_digest=optional_string(payload.get("bundle_digest")),
        corpus_digest=optional_string(payload.get("corpus_digest")),
    )


def optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_context_assessment(
    issue: IssueDraft,
    raw_assessment: RawContextAssessment | None,
    provider_result: ContextAssessorProviderResult,
    *,
    bundle_digest: str,
    corpus_digest: str,
    available_paths: set[str],
) -> ContextAssessment:
    invalid_reasons: list[str] = []
    reasons: list[str] = []
    cited_paths: tuple[str, ...] = ()
    confidence = 0.0
    verdict = "fail"

    if provider_result.bundle_digest != bundle_digest:
        invalid_reasons.append("assessor bundle digest mismatch")
    if provider_result.corpus_digest != corpus_digest:
        invalid_reasons.append("assessor corpus digest mismatch")

    if raw_assessment is None:
        invalid_reasons.append("assessor omitted issue assessment")
    else:
        verdict = raw_assessment.verdict
        confidence = raw_assessment.confidence if raw_assessment.confidence is not None else 0.0
        cited_paths = tuple(dict.fromkeys(raw_assessment.cited_paths))
        reasons = list(raw_assessment.reasons)

        if verdict not in ASSESSOR_VERDICTS:
            invalid_reasons.append(f"invalid assessor verdict: {verdict or 'missing'}")
            verdict = "fail"
        if raw_assessment.confidence is None or not 0.0 <= confidence <= 1.0:
            invalid_reasons.append("assessor confidence must be between 0 and 1")
            confidence = 0.0
        if not cited_paths:
            invalid_reasons.append("assessor did not cite supplied evidence paths")
        invalid_citations = sorted(set(cited_paths) - available_paths)
        if invalid_citations:
            invalid_reasons.append(
                "assessor cited paths outside supplied evidence: "
                + ", ".join(invalid_citations)
            )
        if not reasons:
            invalid_reasons.append("assessor did not provide reasons")

    if invalid_reasons:
        return ContextAssessment(
            verdict="fail",
            confidence=0.0,
            cited_paths=tuple(path for path in cited_paths if path in available_paths),
            reasons=tuple([*invalid_reasons, *reasons]),
            valid=False,
            validation_reasons=tuple(invalid_reasons),
        )

    return ContextAssessment(
        verdict=verdict,
        confidence=confidence,
        cited_paths=cited_paths,
        reasons=tuple(reasons),
        valid=True,
        validation_reasons=(),
    )


def issue_context_validation_reasons(assessment: ContextAssessment) -> list[str]:
    if not assessment.valid:
        return [
            f"Issue context assessor evidence invalid: {reason}"
            for reason in assessment.validation_reasons
        ]
    if assessment.verdict == "pass":
        return []
    detail = "; ".join(assessment.reasons)
    if detail == "":
        return [f"Issue context assessor verdict {assessment.verdict}"]
    return [f"Issue context assessor verdict {assessment.verdict}: {detail}"]


def operator_approval_evidence(body: str) -> dict[str, Any]:
    evidence = section_body(body, "Operator approval evidence")
    if evidence is None or evidence.strip() == "":
        return {"present": False, "body": "", "warnings": []}

    warnings: list[str] = [
        "Approval evidence is context only; it does not grant tool permission."
    ]
    evidence_lower = evidence.lower()
    if "corpus scope" not in evidence_lower:
        warnings.append("Evidence does not name a corpus scope.")
    if "prohibited" not in evidence_lower:
        warnings.append("Evidence does not list prohibited actions.")
    return {"present": True, "body": evidence, "warnings": warnings}


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
    context_paths: tuple[str, ...],
) -> StiffnessResult:
    reasons: list[str] = []
    score = 0
    area_values = {
        area_for_path(path)
        for path in [*anchors.paths, *anchors.docs, *context_paths[:3]]
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

    criteria_count = len(
        CHECKBOX_PATTERN.findall(section_body(issue.body, "Acceptance criteria") or "")
    )
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
    labels: frozenset[str],
    validation_reasons: list[str],
    context_passed: bool,
    stiffness: int,
    thresholds: Thresholds,
    override: str | None,
) -> tuple[str, bool, str]:
    if validation_reasons or not context_passed:
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
    context_assessor_command: str,
    thresholds: Thresholds,
    provider_name: str,
) -> dict[str, Any]:
    anchors_by_issue: dict[str, AnchorSummary] = {}
    corpora_by_issue: dict[str, EvidenceCorpus] = {}
    for issue in bundle.issues:
        anchors = parse_anchors(issue.body, repo_root)
        anchors_by_issue[issue.issue_id] = anchors
        corpora_by_issue[issue.issue_id] = build_issue_evidence(
            issue,
            bundle.shared_context,
            anchors,
            repo_root=repo_root,
            max_rg_candidate_files=thresholds.max_rg_candidate_files,
        )

    request_payload = assessor_request_payload(bundle, anchors_by_issue, corpora_by_issue)
    provider_result = run_context_assessor_provider(
        context_assessor_command,
        request_payload,
        repo_root=repo_root,
    )
    corpus_digest = str(request_payload["corpus_digest"])

    issue_reports: list[dict[str, Any]] = []
    for issue in bundle.issues:
        labels = frozenset(issue.labels)
        anchors = anchors_by_issue[issue.issue_id]
        corpus = corpora_by_issue[issue.issue_id]
        raw_assessment = provider_result.assessments.get(issue.issue_id)
        available_paths = {document.path for document in corpus.documents}
        context_assessment = normalize_context_assessment(
            issue,
            raw_assessment,
            provider_result,
            bundle_digest=bundle.source_digest,
            corpus_digest=corpus_digest,
            available_paths=available_paths,
        )

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
        validation_reasons.extend(issue_context_validation_reasons(context_assessment))

        context_paths = tuple(document.path for document in corpus.documents)
        stiffness = stiffness_score(issue, anchors, context_paths)
        stiffness_level_value = stiffness_level(stiffness.score, thresholds)
        declared_mismatch = declared_stiffness_mismatch(
            stiffness.declared_level,
            stiffness.score,
            thresholds,
        )
        override = bundle.operator_overrides.get(issue.issue_id)
        context_passed = context_assessment.valid and context_assessment.verdict == "pass"
        action, ready, state_label = action_for_issue(
            labels=labels,
            validation_reasons=validation_reasons,
            context_passed=context_passed,
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
                "context_assessment": {
                    "verdict": context_assessment.verdict,
                    "passed": context_passed,
                    "confidence": context_assessment.confidence,
                    "cited_paths": list(context_assessment.cited_paths),
                    "reasons": list(context_assessment.reasons),
                    "valid": context_assessment.valid,
                    "validation_reasons": list(context_assessment.validation_reasons),
                },
                "context_corpus": evidence_corpus_payload(corpus),
                "anchors": anchor_summary_payload(anchors),
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
            "human_review_stiffness": thresholds.human_review_stiffness,
            "split_stiffness": thresholds.split_stiffness,
            "max_rg_candidate_files": thresholds.max_rg_candidate_files,
            "max_evidence_snippets_per_file": MAX_EVIDENCE_SNIPPETS_PER_FILE,
            "max_snippet_chars": MAX_SNIPPET_CHARS,
        },
        "context_assessor": {
            "provider": provider_name,
            "command": context_assessor_command,
            "schema_version": CONTEXT_ASSESSOR_SCHEMA_VERSION,
            "corpus_digest": corpus_digest,
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
        "## Issue Context Assessor",
        "",
        f"- Provider: `{report['context_assessor']['provider']}`",
        f"- Schema: `{report['context_assessor']['schema_version']}`",
        f"- Corpus digest: `{report['context_assessor']['corpus_digest']}`",
        "",
        "## Thresholds",
        "",
        f"- Human review stiffness: `{report['thresholds']['human_review_stiffness']}`",
        f"- Split stiffness: `{report['thresholds']['split_stiffness']}`",
        f"- Max rg candidate files: `{report['thresholds']['max_rg_candidate_files']}`",
        "",
        "## Issues",
        "",
    ]
    for issue in report["issues"]:
        context_assessment = issue["context_assessment"]
        lines.extend(
            [
                f"### {issue['id']}: {issue['title']}",
                "",
                f"- Action: `{issue['action']}`",
                f"- Ready: `{str(issue['ready']).lower()}`",
                "- Recommended labels: "
                + ", ".join(f"`{label}`" for label in issue["recommended_labels"]),
                f"- Context verdict: `{context_assessment['verdict']}`",
                f"- Context confidence: `{context_assessment['confidence']}`",
                f"- Context corpus digest: `{issue['context_corpus']['digest']}`",
                f"- Stiffness: `{issue['stiffness']['score']}` ({issue['stiffness']['level']})",
                "- Stiffness surface areas: "
                + ", ".join(f"`{area}`" for area in issue["stiffness"]["surface_areas"]),
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
        lines.append("- Context cited paths:")
        if context_assessment["cited_paths"]:
            lines.extend(f"  - `{path}`" for path in context_assessment["cited_paths"])
        else:
            lines.append("  - None")
        lines.append("- Context reasons:")
        lines.extend(f"  - {reason}" for reason in context_assessment["reasons"])
        lines.append("- Evidence files:")
        lines.extend(
            f"  - `{entry['path']}` ({entry['source']}, {len(entry['snippets'])} snippet(s))"
            for entry in issue["context_corpus"]["evidence"]
        )
        lines.append("- Stiffness reasons:")
        lines.extend(f"  - {reason}" for reason in issue["stiffness"]["reasons"])
        if issue["stiffness"]["ignored_terms"]:
            lines.append("- Ignored stiffness mentions:")
            lines.extend(f"  - {term}" for term in issue["stiffness"]["ignored_terms"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def default_context_assessor_command() -> str:
    env_command = os.environ.get("SHAPE_ISSUES_CONTEXT_ASSESSOR_COMMAND")
    if env_command is not None and env_command.strip() != "":
        return env_command
    return "python3 .agents/skills/shape-issues/scripts/codex_context_assessor.py --repo-root ."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a shape-issues bundle for readiness and stiffness.",
    )
    parser.add_argument("bundle", type=Path, help="Path to bundle JSON.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--context-assessor-command", default=default_context_assessor_command())
    parser.add_argument("--context-assessor-name", default=DEFAULT_CONTEXT_ASSESSOR_PROVIDER)
    parser.add_argument("--human-review-stiffness", type=int, default=55)
    parser.add_argument("--split-stiffness", type=int, default=70)
    parser.add_argument(
        "--max-rg-candidate-files",
        type=int,
        default=DEFAULT_RG_CANDIDATE_FILES,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    out_dir = (args.out_dir or args.bundle.parent).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    thresholds = Thresholds(
        human_review_stiffness=args.human_review_stiffness,
        split_stiffness=args.split_stiffness,
        max_rg_candidate_files=args.max_rg_candidate_files,
    )
    try:
        bundle = parse_bundle(args.bundle)
        report = evaluate_bundle(
            bundle,
            repo_root=repo_root,
            context_assessor_command=args.context_assessor_command,
            thresholds=thresholds,
            provider_name=args.context_assessor_name,
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
