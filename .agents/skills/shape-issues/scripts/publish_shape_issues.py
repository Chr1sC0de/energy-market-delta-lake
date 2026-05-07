#!/usr/bin/env python3
"""Publish confirmed shape-issues gate outputs as GitHub Issues."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


NEEDS_TRIAGE_LABEL = "needs-triage"
PUBLISHABLE_ACTIONS = frozenset({"ready", "exploratory"})
SOURCE_MARKER_PREFIX = "shape-issues-source"
SECTION_PATTERN_TEMPLATE = (
    r"(?ims)^#{{1,6}}\s+{heading}\s*$\n"
    r"(?P<body>.*?)(?=^#{{1,6}}\s+\S|\Z)"
)
BLOCKER_PATTERN = re.compile(r"(?:#|/issues/)(?P<number>\d+)")


class PublishError(Exception):
    """Raised when a shape-issues bundle cannot be safely published."""


@dataclass(frozen=True)
class IssueDraft:
    issue_id: str
    title: str
    body: str
    labels: tuple[str, ...]
    blocked_by: tuple[str, ...]
    classification: str | None
    source_digest: str


@dataclass(frozen=True)
class BundleDraft:
    summary: str
    shared_context: tuple[str, ...]
    operator_overrides: dict[str, str]
    issues: tuple[IssueDraft, ...]
    source_digest: str


@dataclass(frozen=True)
class GateIssue:
    issue_id: str
    action: str
    source_digest: str | None


@dataclass(frozen=True)
class GateReport:
    bundle_digest: str | None
    issues: dict[str, GateIssue]


@dataclass(frozen=True)
class IssueReference:
    number: int | None
    title: str
    url: str


@dataclass(frozen=True)
class PublishConfig:
    bundle_path: Path
    report_path: Path
    out_dir: Path
    repo_root: Path
    repo: str
    confirm_publish: bool
    dry_run: bool
    gh_binary: str


class GithubClient:
    def __init__(self, *, repo: str, repo_root: Path, gh_binary: str) -> None:
        self.repo = repo
        self.repo_root = repo_root
        self.gh_binary = gh_binary

    def find_issue_by_source_marker(self, marker: str) -> IssueReference | None:
        payload = self._json(
            [
                self.gh_binary,
                "issue",
                "list",
                "-R",
                self.repo,
                "--state",
                "all",
                "--limit",
                "1",
                "--search",
                f'"{marker}" in:body',
                "--json",
                "number,title,url",
            ]
        )
        if not isinstance(payload, list) or len(payload) == 0:
            return None
        item = payload[0]
        if not isinstance(item, dict):
            return None
        return issue_reference_from_payload(item)

    def create_issue(self, *, title: str, body_path: Path, labels: tuple[str, ...]) -> IssueReference:
        args = [
            self.gh_binary,
            "issue",
            "create",
            "-R",
            self.repo,
            "--title",
            title,
            "--body-file",
            str(body_path),
        ]
        for label in labels:
            args.extend(["--label", label])
        result = self._run(args)
        return parse_issue_reference_from_create_stdout(result.stdout, title=title)

    def _json(self, args: list[str]) -> Any:
        result = self._run(args)
        if result.stdout.strip() == "":
            return None
        return json.loads(result.stdout)

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            args,
            cwd=self.repo_root,
            check=True,
            capture_output=True,
            text=True,
        )


def parse_string_list(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = [str(item) for item in value]
    else:
        values = []
    return tuple(item.strip() for item in values if item.strip() != "")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def read_json_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise PublishError(f"{path} must contain a JSON object.")
    return payload


def parse_bundle(path: Path) -> BundleDraft:
    payload = read_json_object(path)
    raw_issues = payload.get("issues")
    if not isinstance(raw_issues, list) or len(raw_issues) == 0:
        raise PublishError("Bundle must include a non-empty issues array.")

    issues: list[IssueDraft] = []
    for index, raw_issue in enumerate(raw_issues, start=1):
        if not isinstance(raw_issue, dict):
            raise PublishError(f"Issue entry {index} must be an object.")
        title = str(raw_issue.get("title") or "").strip()
        body = str(raw_issue.get("body") or "").strip()
        issue_id = str(raw_issue.get("id") or slugify(title) or f"issue-{index}").strip()
        if title == "":
            raise PublishError(f"Issue entry {index} is missing title.")
        if body == "":
            raise PublishError(f"Issue entry {index} is missing body.")
        issues.append(
            IssueDraft(
                issue_id=issue_id,
                title=title,
                body=body,
                labels=tuple(sorted(parse_string_list(raw_issue.get("labels")))),
                blocked_by=parse_string_list(raw_issue.get("blocked_by")),
                classification=optional_string(raw_issue.get("classification")),
                source_digest=issue_source_digest(
                    issue_id=issue_id,
                    title=title,
                    body=body,
                    labels=tuple(sorted(parse_string_list(raw_issue.get("labels")))),
                    classification=optional_string(raw_issue.get("classification")),
                    blocked_by=parse_string_list(raw_issue.get("blocked_by")),
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
    shared_context = parse_string_list(payload.get("shared_context"))
    issue_tuple = tuple(issues)
    return BundleDraft(
        summary=summary,
        shared_context=shared_context,
        operator_overrides=overrides,
        issues=issue_tuple,
        source_digest=bundle_source_digest(
            summary=summary,
            shared_context=shared_context,
            operator_overrides=overrides,
            issues=issue_tuple,
        ),
    )


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


def parse_gate_report(path: Path) -> GateReport:
    payload = read_json_object(path)
    raw_issues = payload.get("issues")
    if not isinstance(raw_issues, list):
        raise PublishError("Gate report must include an issues array.")

    issues: dict[str, GateIssue] = {}
    for index, raw_issue in enumerate(raw_issues, start=1):
        if not isinstance(raw_issue, dict):
            raise PublishError(f"Gate report issue entry {index} must be an object.")
        issue_id = str(raw_issue.get("id") or "").strip()
        action = str(raw_issue.get("action") or "").strip()
        source_digest = optional_string(raw_issue.get("source_digest"))
        if issue_id == "":
            raise PublishError(f"Gate report issue entry {index} is missing id.")
        if action == "":
            raise PublishError(f"Gate report issue entry {index} is missing action.")
        if issue_id in issues:
            raise PublishError(f"Gate report has duplicate issue id: {issue_id}.")
        issues[issue_id] = GateIssue(
            issue_id=issue_id,
            action=action,
            source_digest=source_digest,
        )
    return GateReport(
        bundle_digest=optional_string(payload.get("bundle_digest")),
        issues=issues,
    )


def source_marker(bundle_path: Path, issue: IssueDraft) -> str:
    run_slug = slugify(bundle_path.parent.name) or "run"
    issue_slug = slugify(issue.issue_id) or slugify(issue.title)
    return f"{SOURCE_MARKER_PREFIX}:{run_slug}:{issue_slug}"


def section_body(markdown: str, heading: str) -> str | None:
    pattern = re.compile(SECTION_PATTERN_TEMPLATE.format(heading=re.escape(heading)))
    match = pattern.search(markdown)
    if match is None:
        return None
    return match.group("body").strip()


def replace_section(markdown: str, heading: str, body: str) -> str:
    pattern = re.compile(
        rf"(?ims)^(?P<header>#{{1,6}}\s+{re.escape(heading)}\s*$\n)"
        rf"(?P<body>.*?)(?=^#{{1,6}}\s+\S|\Z)"
    )
    replacement = f"## {heading}\n{body.strip()}\n\n"
    if pattern.search(markdown) is None:
        return markdown.rstrip() + "\n\n" + replacement
    return pattern.sub(lambda _match: replacement, markdown).rstrip() + "\n"


def final_blocked_by_section(
    issue: IssueDraft,
    references: dict[str, IssueReference],
) -> str:
    if len(issue.blocked_by) == 0:
        return "None - can start immediately."

    lines: list[str] = []
    for blocker_id in issue.blocked_by:
        if blocker_id not in references:
            raise PublishError(
                f"Issue {issue.issue_id} references unpublished blocker {blocker_id}."
            )
        reference = references[blocker_id]
        if reference.number is not None:
            lines.append(f"- #{reference.number}")
        elif reference.url != "":
            lines.append(f"- {reference.url}")
        else:
            raise PublishError(
                f"Issue {issue.issue_id} blocker {blocker_id} has no number or URL."
            )
    return "\n".join(lines)


def bundle_reference(bundle_path: Path) -> str:
    parts = bundle_path.parts
    if ".shape-issues" in parts:
        index = parts.index(".shape-issues")
        return str(Path(*parts[index:]))
    return str(Path(bundle_path.parent.name) / bundle_path.name)


def append_source_section(markdown: str, *, marker: str, bundle_path: Path) -> str:
    source_body = "\n".join(
        [
            f"- Source marker: `{marker}`",
            f"- Bundle: `{bundle_reference(bundle_path)}`",
        ]
    )
    return replace_section(markdown, "Shape Issues source", source_body)


def final_issue_body(
    issue: IssueDraft,
    *,
    references: dict[str, IssueReference],
    marker: str,
    bundle_path: Path,
) -> str:
    body = replace_section(
        issue.body,
        "Blocked by",
        final_blocked_by_section(issue, references),
    )
    body = append_source_section(body, marker=marker, bundle_path=bundle_path)
    validate_final_blockers(issue, body, references)
    return body


def validate_final_blockers(
    issue: IssueDraft,
    body: str,
    references: dict[str, IssueReference],
) -> None:
    if len(issue.blocked_by) == 0:
        return
    blocked_by = section_body(body, "Blocked by")
    if blocked_by is None:
        raise PublishError(f"Issue {issue.issue_id} final body is missing ## Blocked by.")
    parsed_numbers = {int(match.group("number")) for match in BLOCKER_PATTERN.finditer(blocked_by)}
    for blocker_id in issue.blocked_by:
        reference = references[blocker_id]
        if reference.number is not None and reference.number not in parsed_numbers:
            raise PublishError(
                f"Issue {issue.issue_id} final blocker section does not parse #{reference.number}."
            )


def parse_issue_reference_from_create_stdout(stdout: str, *, title: str) -> IssueReference:
    match = re.search(r"https://github\.com/[^/\s]+/[^/\s]+/issues/(?P<number>\d+)", stdout)
    if match is None:
        url = stdout.strip().splitlines()[-1] if stdout.strip() else ""
        return IssueReference(number=None, title=title, url=url)
    return IssueReference(number=int(match.group("number")), title=title, url=match.group(0))


def issue_reference_from_payload(payload: dict[str, Any]) -> IssueReference:
    number: int | None = None
    if payload.get("number") is not None:
        number = int(payload["number"])
    return IssueReference(
        number=number,
        title=str(payload.get("title") or ""),
        url=str(payload.get("url") or ""),
    )


def validate_publishable(
    bundle: BundleDraft,
    report: GateReport,
    *,
    confirm_publish: bool,
    bundle_path: Path,
) -> None:
    if not confirm_publish:
        raise PublishError("Refusing to publish without --confirm-publish.")

    if report.bundle_digest is None:
        raise PublishError("Gate report is missing bundle_digest; rerun the gate.")
    if report.bundle_digest != bundle.source_digest:
        raise PublishError("Bundle changed after gate report was written; rerun the gate.")

    issues = bundle.issues
    report_issues = report.issues
    validate_issue_identity(issues, bundle_path)

    missing = sorted(issue.issue_id for issue in issues if issue.issue_id not in report_issues)
    if missing:
        raise PublishError(f"Gate report is missing issue(s): {', '.join(missing)}.")

    blocked_ids = {blocker_id for issue in issues for blocker_id in issue.blocked_by}
    known_ids = {issue.issue_id for issue in issues}
    unknown_blockers = sorted(blocked_ids - known_ids)
    if unknown_blockers:
        raise PublishError(f"Unknown blocked_by issue id(s): {', '.join(unknown_blockers)}.")

    for issue in issues:
        report_issue = report_issues[issue.issue_id]
        action = report_issue.action
        if report_issue.source_digest is None:
            raise PublishError(
                f"Gate report issue {issue.issue_id} is missing source_digest; rerun the gate."
            )
        if report_issue.source_digest != issue.source_digest:
            raise PublishError(
                f"Issue {issue.issue_id} changed after gate report was written; rerun the gate."
            )
        if action not in PUBLISHABLE_ACTIONS:
            raise PublishError(
                f"Issue {issue.issue_id} is not publishable: gate action is {action}."
            )
        if issue.classification not in {"afk", "exploratory"}:
            classification = issue.classification or "missing"
            raise PublishError(
                f"Issue {issue.issue_id} has non-publishable classification: {classification}."
            )
        if issue.classification == "afk" and action != "ready":
            raise PublishError(
                f"Issue {issue.issue_id} classification afk requires gate action ready."
            )
        if issue.classification == "exploratory" and action != "exploratory":
            raise PublishError(
                f"Issue {issue.issue_id} classification exploratory requires gate action exploratory."
            )


def validate_issue_identity(issues: tuple[IssueDraft, ...], bundle_path: Path) -> None:
    issue_ids = [issue.issue_id for issue in issues]
    duplicate_ids = sorted({issue_id for issue_id in issue_ids if issue_ids.count(issue_id) > 1})
    if duplicate_ids:
        raise PublishError(f"Duplicate issue id(s): {', '.join(duplicate_ids)}.")

    markers = [source_marker(bundle_path, issue) for issue in issues]
    duplicate_markers = sorted({marker for marker in markers if markers.count(marker) > 1})
    if duplicate_markers:
        raise PublishError(
            "Duplicate generated source marker(s): " + ", ".join(duplicate_markers)
        )

    body_paths = [body_file_name(issue) for issue in issues]
    duplicate_body_paths = sorted(
        {body_path for body_path in body_paths if body_paths.count(body_path) > 1}
    )
    if duplicate_body_paths:
        raise PublishError(
            "Duplicate generated body file name(s): " + ", ".join(duplicate_body_paths)
        )


def body_file_name(issue: IssueDraft) -> str:
    return f"{slugify(issue.issue_id) or 'issue'}.md"


def publication_order(issues: tuple[IssueDraft, ...]) -> tuple[IssueDraft, ...]:
    by_id = {issue.issue_id: issue for issue in issues}
    permanent: set[str] = set()
    temporary: set[str] = set()
    ordered: list[IssueDraft] = []

    def visit(issue_id: str) -> None:
        if issue_id in permanent:
            return
        if issue_id in temporary:
            raise PublishError(f"blocked_by cycle includes issue {issue_id}.")
        temporary.add(issue_id)
        for blocker_id in by_id[issue_id].blocked_by:
            visit(blocker_id)
        temporary.remove(issue_id)
        permanent.add(issue_id)
        ordered.append(by_id[issue_id])

    for issue in issues:
        visit(issue.issue_id)
    return tuple(ordered)


def manifest_entry(
    *,
    issue: IssueDraft,
    action: str,
    state: str,
    marker: str,
    body_path: Path,
    reference: IssueReference | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "id": issue.issue_id,
        "title": issue.title,
        "gate_action": action,
        "state": state,
        "source_marker": marker,
        "labels": [NEEDS_TRIAGE_LABEL],
        "blocked_by": list(issue.blocked_by),
        "body_path": str(body_path),
    }
    if issue.classification is not None:
        entry["classification"] = issue.classification
    if reference is not None:
        entry["number"] = reference.number
        entry["url"] = reference.url
    if error is not None:
        entry["error"] = error
    return entry


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def publish(config: PublishConfig) -> dict[str, Any]:
    bundle = parse_bundle(config.bundle_path)
    report = parse_gate_report(config.report_path)
    validate_publishable(
        bundle,
        report,
        confirm_publish=config.confirm_publish,
        bundle_path=config.bundle_path,
    )
    issues = bundle.issues
    report_issues = report.issues
    ordered = publication_order(issues)

    config.out_dir.mkdir(parents=True, exist_ok=True)
    bodies_dir = config.out_dir / "publish-bodies"
    bodies_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = config.out_dir / "publish-manifest.json"
    manifest: dict[str, Any] = {
        "bundle": str(config.bundle_path),
        "confirmed": config.confirm_publish,
        "dry_run": config.dry_run,
        "issues": [],
        "published_at": datetime.now(UTC).isoformat(),
        "report": str(config.report_path),
        "repo": config.repo,
        "summary": bundle.summary,
    }
    write_manifest(manifest_path, manifest)

    github = GithubClient(
        repo=config.repo,
        repo_root=config.repo_root,
        gh_binary=config.gh_binary,
    )
    references: dict[str, IssueReference] = {}

    for issue in ordered:
        marker = source_marker(config.bundle_path, issue)
        action = report_issues[issue.issue_id].action
        body_path = bodies_dir / body_file_name(issue)
        try:
            body = final_issue_body(
                issue,
                references=references,
                marker=marker,
                bundle_path=config.bundle_path,
            )
            body_path.write_text(body, encoding="utf-8")

            if config.dry_run:
                reference = IssueReference(
                    number=None,
                    title=issue.title,
                    url=f"dry-run:{issue.issue_id}",
                )
                references[issue.issue_id] = reference
                manifest["issues"].append(
                    manifest_entry(
                        issue=issue,
                        action=action,
                        state="dry-run",
                        marker=marker,
                        body_path=body_path,
                        reference=reference,
                    )
                )
                write_manifest(manifest_path, manifest)
                continue

            duplicate = github.find_issue_by_source_marker(marker)
            if duplicate is not None:
                references[issue.issue_id] = duplicate
                manifest["issues"].append(
                    manifest_entry(
                        issue=issue,
                        action=action,
                        state="duplicate",
                        marker=marker,
                        body_path=body_path,
                        reference=duplicate,
                    )
                )
                write_manifest(manifest_path, manifest)
                continue

            created = github.create_issue(
                title=issue.title,
                body_path=body_path,
                labels=(NEEDS_TRIAGE_LABEL,),
            )
            references[issue.issue_id] = created
            manifest["issues"].append(
                manifest_entry(
                    issue=issue,
                    action=action,
                    state="created",
                    marker=marker,
                    body_path=body_path,
                    reference=created,
                )
            )
            write_manifest(manifest_path, manifest)
        except (OSError, subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as error:
            manifest["issues"].append(
                manifest_entry(
                    issue=issue,
                    action=action,
                    state="failed",
                    marker=marker,
                    body_path=body_path,
                    error=str(error),
                )
            )
            manifest["recovery"] = (
                "Inspect publish-manifest.json, keep any created issues, then rerun "
                "the publisher with the same bundle. Source markers will skip duplicates."
            )
            write_manifest(manifest_path, manifest)
            raise PublishError(
                "Issue publishing failed after writing recovery details to "
                f"{manifest_path}."
            ) from error

    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Publish confirmed shape-issues gate outputs as needs-triage GitHub Issues.",
    )
    parser.add_argument("bundle", type=Path, help="Path to shape-issues bundle.json.")
    parser.add_argument("--report", type=Path, default=None, help="Path to gate report.json.")
    parser.add_argument("--repo", required=True, help="GitHub repository in owner/name form.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--confirm-publish", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gh-binary", default="gh")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    bundle_path = args.bundle.resolve()
    report_path = (args.report or bundle_path.parent / "report.json").resolve()
    out_dir = (args.out_dir or bundle_path.parent).resolve()
    config = PublishConfig(
        bundle_path=bundle_path,
        report_path=report_path,
        out_dir=out_dir,
        repo_root=args.repo_root.resolve(),
        repo=args.repo,
        confirm_publish=args.confirm_publish,
        dry_run=args.dry_run,
        gh_binary=args.gh_binary,
    )
    try:
        manifest = publish(config)
    except (PublishError, json.JSONDecodeError, OSError, ValueError) as error:
        sys.stderr.write(f"shape-issues publish failed: {error}\n")
        raise SystemExit(1)
    sys.stdout.write(str(out_dir / "publish-manifest.json") + "\n")
    created = [
        issue
        for issue in manifest["issues"]
        if issue["state"] in {"created", "duplicate", "dry-run"}
    ]
    sys.stdout.write(f"publishable issue entries: {len(created)}\n")


if __name__ == "__main__":
    main()
