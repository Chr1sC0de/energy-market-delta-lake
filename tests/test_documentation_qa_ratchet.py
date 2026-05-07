from __future__ import annotations

import os
import re
import shlex
import tomllib
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_SYNC_CONTRACT_PATH = REPO_ROOT / "docs" / "repository" / "documentation-sync.md"
DOCS_README_PATH = REPO_ROOT / "docs" / "README.md"
AGENTS_README_PATH = REPO_ROOT / "docs" / "agents" / "README.md"
SHELL_HEADER_CHECKER = REPO_ROOT / "scripts" / "check_shell_script_headers.py"

PYTHON_DOCSTRING_RATCHET_SUBPROJECTS = (
    Path("backend-services/authentication"),
    Path("backend-services/marimo"),
    Path("backend-services/dagster-user/aemo-etl"),
    Path("infrastructure/aws-pulumi"),
)
PYTHON_DOCSTRING_RATCHET_EXCLUDED_SUBPROJECTS = (
    Path("backend-services/dagster-core"),
)
SHELL_HEADER_RATCHET_SUBPROJECTS = (
    Path("backend-services"),
    Path("backend-services/dagster-user/aemo-etl"),
    Path("infrastructure/aws-pulumi"),
)

IGNORED_DISCOVERY_DIRS = frozenset(
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
SUBPROJECT_PARENT_DIRS = frozenset({"backend-services", "infrastructure"})
DOC_DISCOVERY_REQUIRED_EXCLUSIONS = frozenset(
    {
        ".ralph",
        ".shape-issues",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        "generated",
        "vendor",
        "specs",
    }
)
SYNC_METADATA_KEYS = ("sync.owner", "sync.sources", "sync.scope", "sync.qa")
MAINTAINED_ROOT_DOCS = frozenset({Path("README.md"), Path("OPERATOR.md")})
DOCS_README_REQUIRED_TARGETS = frozenset(
    {
        "README.md",
        "OPERATOR.md",
        "AGENTS.md",
        "CONTEXT.md",
        "docs/agents/README.md",
        "docs/agents/domain.md",
        "docs/agents/issue-tracker.md",
        "docs/agents/ralph-loop.md",
        "docs/agents/triage-labels.md",
        "docs/repository/architecture.md",
        "docs/repository/documentation-sync.md",
        "docs/repository/workflow.md",
        "backend-services/README.md",
        "backend-services/authentication/README.md",
        "backend-services/marimo/README.md",
        "backend-services/dagster-user/aemo-etl/README.md",
        "backend-services/dagster-user/aemo-etl/docs/architecture/high_level_architecture.md",
        "backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md",
        "backend-services/dagster-user/aemo-etl/docs/gas_model/README.md",
        "infrastructure/aws-pulumi/README.md",
        "infrastructure/aws-pulumi/docs/README.md",
    }
)
AGENTS_README_REQUIRED_TARGETS = frozenset(
    {
        "AGENTS.md",
        "OPERATOR.md",
        "CONTEXT.md",
        "docs/repository/documentation-sync.md",
        "docs/agents/domain.md",
        "docs/agents/issue-tracker.md",
        "docs/agents/ralph-loop.md",
        "docs/agents/triage-labels.md",
    }
)


def _repo_files_named(file_name: str) -> tuple[Path, ...]:
    paths: list[Path] = []
    for current_root, dir_names, file_names in os.walk(REPO_ROOT):
        dir_names[:] = [
            name for name in dir_names if name not in IGNORED_DISCOVERY_DIRS
        ]
        if file_name in file_names:
            paths.append(Path(current_root) / file_name)
    return tuple(sorted(paths))


def _candidate_pyprojects() -> tuple[Path, ...]:
    pyprojects: list[Path] = []
    for pyproject_path in _repo_files_named("pyproject.toml"):
        relative_path = pyproject_path.relative_to(REPO_ROOT)
        if relative_path.parts[0] in SUBPROJECT_PARENT_DIRS:
            pyprojects.append(pyproject_path)
    return tuple(pyprojects)


def _candidate_pre_commit_configs() -> tuple[Path, ...]:
    return _repo_files_named(".pre-commit-config.yaml")


def _load_pyproject(pyproject_path: Path) -> dict[str, Any]:
    with pyproject_path.open("rb") as pyproject_file:
        return tomllib.load(pyproject_file)


def _ruff_lint_config(pyproject_path: Path) -> dict[str, Any]:
    pyproject = _load_pyproject(pyproject_path)
    tool_config = pyproject.get("tool", {})
    if not isinstance(tool_config, dict):
        return {}
    ruff_config = tool_config.get("ruff", {})
    if not isinstance(ruff_config, dict):
        return {}
    lint_config = ruff_config.get("lint", {})
    if not isinstance(lint_config, dict):
        return {}
    return lint_config


def _ruff_selected_rules(pyproject_path: Path) -> tuple[str, ...]:
    select = _ruff_lint_config(pyproject_path).get("select", ())
    if not isinstance(select, list):
        return ()
    return tuple(rule for rule in select if isinstance(rule, str))


def _pydocstyle_convention(pyproject_path: Path) -> str | None:
    pydocstyle_config = _ruff_lint_config(pyproject_path).get("pydocstyle", {})
    if not isinstance(pydocstyle_config, dict):
        return None
    convention = pydocstyle_config.get("convention")
    if not isinstance(convention, str):
        return None
    return convention


def _yaml_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _pre_commit_hook_entries(config_path: Path) -> dict[str, str | None]:
    hooks: dict[str, str | None] = {}
    current_hook_id: str | None = None
    current_hook_indent = -1
    for line in config_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "" or stripped.startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        if stripped.startswith("- id:"):
            current_hook_id = _yaml_scalar(stripped.removeprefix("- id:").strip())
            current_hook_indent = indent
            hooks[current_hook_id] = None
            continue

        if current_hook_id is None:
            continue
        if indent <= current_hook_indent:
            current_hook_id = None
            current_hook_indent = -1
            continue
        if stripped.startswith("entry:"):
            hooks[current_hook_id] = _yaml_scalar(
                stripped.removeprefix("entry:").strip()
            )
    return hooks


def _entry_contains_tokens(entry: str | None, expected_tokens: tuple[str, ...]) -> bool:
    if entry is None:
        return False
    tokens = shlex.split(entry)
    expected_length = len(expected_tokens)
    return any(
        tuple(tokens[index : index + expected_length]) == expected_tokens
        for index in range(len(tokens) - expected_length + 1)
    )


def _entry_invokes_shell_header_checker(config_path: Path, entry: str | None) -> bool:
    if entry is None:
        return False
    for token in shlex.split(entry):
        token_path = Path(token)
        if token_path.suffix != ".py":
            continue
        if token_path.is_absolute():
            candidate = token_path.resolve()
        else:
            candidate = (config_path.parent / token_path).resolve()
        if candidate == SHELL_HEADER_CHECKER.resolve():
            return True
    return False


def _has_ruff_check_hook(subproject: Path) -> bool:
    config_path = REPO_ROOT / subproject / ".pre-commit-config.yaml"
    if not config_path.is_file():
        return False
    entry = _pre_commit_hook_entries(config_path).get("ruff-check")
    return _entry_contains_tokens(entry, ("ruff", "check"))


def _python_docstring_ratchet_enabled(subproject: Path) -> bool:
    pyproject_path = REPO_ROOT / subproject / "pyproject.toml"
    if not pyproject_path.is_file():
        return False
    return (
        "D" in _ruff_selected_rules(pyproject_path)
        and _pydocstyle_convention(pyproject_path) == "google"
        and _has_ruff_check_hook(subproject)
    )


def _subproject_path_strings(paths: set[Path] | tuple[Path, ...]) -> set[str]:
    return {path.as_posix() for path in paths}


def _doc_sync_ratchet_section() -> str:
    doc_sync = DOC_SYNC_CONTRACT_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^### Documentation QA ratchet$(?P<section>.*?)(?=^## )",
        doc_sync,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        match = re.search(
            r"^## Documentation QA ratchets$(?P<section>.*?)(?=^## )",
            doc_sync,
            flags=re.MULTILINE | re.DOTALL,
        )
    if match is None:
        return ""
    return match.group("section")


def _is_excluded_path(path: Path) -> bool:
    return any(part in IGNORED_DISCOVERY_DIRS for part in path.parts)


def _is_maintained_doc_path(relative_path: Path) -> bool:
    if relative_path.suffix != ".md":
        return False
    if _is_excluded_path(relative_path):
        return False
    if relative_path in MAINTAINED_ROOT_DOCS:
        return True
    if len(relative_path.parts) == 0:
        return False
    if relative_path.parts[0] == "docs":
        return True
    if relative_path.parts[0] == "backend-services":
        return True
    return relative_path.parts[:2] == ("infrastructure", "aws-pulumi")


def _maintained_docs() -> tuple[Path, ...]:
    docs: list[Path] = []
    for current_root, dir_names, file_names in os.walk(REPO_ROOT):
        root_path = Path(current_root)
        relative_root = root_path.relative_to(REPO_ROOT)
        dir_names[:] = [
            name
            for name in dir_names
            if name not in IGNORED_DISCOVERY_DIRS
            and not _is_excluded_path(relative_root / name)
        ]
        for file_name in file_names:
            path = root_path / file_name
            relative_path = path.relative_to(REPO_ROOT)
            if _is_maintained_doc_path(relative_path):
                docs.append(path)
    return tuple(sorted(docs))


def _sync_metadata_section(doc_path: Path) -> str:
    text = doc_path.read_text(encoding="utf-8")
    match = re.search(
        r"^## Sync metadata$(?P<section>.*)\Z",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return ""
    return match.group("section")


def _sync_sources(doc_path: Path) -> tuple[str, ...]:
    sources: list[str] = []
    in_sources = False
    for line in _sync_metadata_section(doc_path).splitlines():
        if line == "- `sync.sources`:":
            in_sources = True
            continue
        if in_sources and line.startswith("- `sync."):
            break
        if in_sources:
            match = re.fullmatch(r"  - `([^`]+)`", line)
            if match is not None:
                sources.append(match.group(1))
    return tuple(sources)


def _strip_fenced_code_blocks(markdown: str) -> str:
    stripped_lines: list[str] = []
    in_fence = False
    fence_marker = ""
    for line in markdown.splitlines():
        fence_match = re.match(r"^\s*(```|~~~)", line)
        if fence_match is not None:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = ""
            stripped_lines.append("")
            continue
        if in_fence:
            stripped_lines.append("")
        else:
            stripped_lines.append(line)
    return "\n".join(stripped_lines)


def _markdown_links(doc_path: Path) -> tuple[str, ...]:
    markdown = _strip_fenced_code_blocks(doc_path.read_text(encoding="utf-8"))
    links: list[str] = []
    for match in re.finditer(r"(?<!!)\[[^\]]+\]\(([^)]+)\)", markdown):
        target = match.group(1).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if " " in target:
            target = target.split(" ", maxsplit=1)[0]
        links.append(target)
    return tuple(links)


def _is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, flags=re.IGNORECASE))


def _split_link_target(target: str) -> tuple[str, str]:
    path_part, separator, anchor = target.partition("#")
    if separator == "":
        return path_part, ""
    return path_part, anchor


def _github_anchor(heading_text: str) -> str:
    text = re.sub(r"`([^`]*)`", r"\1", heading_text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text


def _markdown_anchors(doc_path: Path) -> set[str]:
    markdown = _strip_fenced_code_blocks(doc_path.read_text(encoding="utf-8"))
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    for line in markdown.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match is None:
            continue
        anchor = _github_anchor(match.group(2))
        count = seen.get(anchor, 0)
        seen[anchor] = count + 1
        if count > 0:
            anchor = f"{anchor}-{count}"
        anchors.add(anchor)
    return anchors


def _resolve_internal_link(doc_path: Path, target: str) -> tuple[Path, str] | None:
    if _is_external_link(target):
        return None
    path_part, anchor = _split_link_target(target)
    if path_part == "":
        return doc_path, anchor
    return (doc_path.parent / path_part).resolve(), anchor


def _internal_link_targets(doc_path: Path) -> set[str]:
    targets: set[str] = set()
    for target in _markdown_links(doc_path):
        resolved = _resolve_internal_link(doc_path, target)
        if resolved is None:
            continue
        target_path, _anchor = resolved
        if target_path.is_relative_to(REPO_ROOT):
            targets.add(target_path.relative_to(REPO_ROOT).as_posix())
    return targets


def _stale_moved_paths() -> tuple[str, ...]:
    return tuple(
        (Path("docs") / file_name).as_posix()
        for file_name in (
            "architecture.md",
            "workflow.md",
            "documentation-sync.md",
            "agent-issue-loop.md",
        )
    )


def _stale_sweep_paths() -> tuple[Path, ...]:
    roots = (
        REPO_ROOT / "README.md",
        REPO_ROOT / "OPERATOR.md",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "CONTEXT.md",
        REPO_ROOT / "docs",
        REPO_ROOT / "backend-services",
        REPO_ROOT / "infrastructure",
        REPO_ROOT / "tests",
        REPO_ROOT / "scripts",
    )
    paths: list[Path] = []
    for root in roots:
        if root.is_file():
            paths.append(root)
            continue
        for current_root, dir_names, file_names in os.walk(root):
            relative_root = Path(current_root).relative_to(REPO_ROOT)
            dir_names[:] = [
                name
                for name in dir_names
                if name not in IGNORED_DISCOVERY_DIRS
                and not _is_excluded_path(relative_root / name)
            ]
            for file_name in file_names:
                path = Path(current_root) / file_name
                if path.suffix in {".md", ".py"} or path.name in {
                    "SKILL.md",
                    "AGENTS.md",
                }:
                    paths.append(path)
    return tuple(sorted(paths))


class DocumentationQaRatchetTests(unittest.TestCase):
    def test_doc_discovery_exclusions_are_explicit(self) -> None:
        self.assertTrue(
            DOC_DISCOVERY_REQUIRED_EXCLUSIONS.issubset(IGNORED_DISCOVERY_DIRS)
        )

    def test_maintained_docs_have_required_sync_metadata(self) -> None:
        for doc_path in _maintained_docs():
            with self.subTest(path=doc_path.relative_to(REPO_ROOT).as_posix()):
                section = _sync_metadata_section(doc_path)

                self.assertNotEqual("", section)
                for key in SYNC_METADATA_KEYS:
                    self.assertIn(f"- `{key}`:", section)

    def test_sync_source_paths_exist(self) -> None:
        for doc_path in _maintained_docs():
            for source in _sync_sources(doc_path):
                with self.subTest(
                    doc=doc_path.relative_to(REPO_ROOT).as_posix(),
                    source=source,
                ):
                    self.assertNotIn("*", source)
                    self.assertTrue(
                        (REPO_ROOT / source).exists(),
                        f"{source} is listed in sync.sources but does not exist",
                    )

    def test_internal_markdown_links_and_anchors_resolve(self) -> None:
        anchors_by_path: dict[Path, set[str]] = {}
        for doc_path in _maintained_docs():
            for target in _markdown_links(doc_path):
                with self.subTest(
                    doc=doc_path.relative_to(REPO_ROOT).as_posix(),
                    target=target,
                ):
                    resolved = _resolve_internal_link(doc_path, target)
                    if resolved is None:
                        continue
                    target_path, anchor = resolved

                    self.assertTrue(
                        target_path.exists(),
                        f"{target} resolves to missing path {target_path}",
                    )
                    if anchor == "" or target_path.is_dir():
                        continue
                    self.assertEqual(
                        ".md",
                        target_path.suffix,
                        f"{target} has an anchor but does not target Markdown",
                    )
                    if target_path not in anchors_by_path:
                        anchors_by_path[target_path] = _markdown_anchors(target_path)
                    self.assertIn(anchor, anchors_by_path[target_path])

    def test_docs_readme_has_required_human_routes(self) -> None:
        self.assertTrue(
            DOCS_README_REQUIRED_TARGETS.issubset(
                _internal_link_targets(DOCS_README_PATH)
            )
        )

    def test_agents_readme_has_required_agent_routes(self) -> None:
        self.assertTrue(
            AGENTS_README_REQUIRED_TARGETS.issubset(
                _internal_link_targets(AGENTS_README_PATH)
            )
        )

    def test_moved_repo_docs_have_no_stale_references(self) -> None:
        stale_paths = _stale_moved_paths()
        for path in _stale_sweep_paths():
            text = path.read_text(encoding="utf-8")
            for stale_path in stale_paths:
                with self.subTest(
                    path=path.relative_to(REPO_ROOT).as_posix(),
                    stale_path=stale_path,
                ):
                    self.assertNotIn(stale_path, text)

    def test_python_docstring_ratchet_coverage_is_exact(self) -> None:
        actual_subprojects = {
            pyproject_path.parent.relative_to(REPO_ROOT)
            for pyproject_path in _candidate_pyprojects()
            if _python_docstring_ratchet_enabled(
                pyproject_path.parent.relative_to(REPO_ROOT)
            )
        }

        self.assertEqual(
            _subproject_path_strings(actual_subprojects),
            _subproject_path_strings(PYTHON_DOCSTRING_RATCHET_SUBPROJECTS),
        )

    def test_python_docstring_ratchet_subprojects_keep_ruff_config(self) -> None:
        for subproject in PYTHON_DOCSTRING_RATCHET_SUBPROJECTS:
            with self.subTest(subproject=subproject.as_posix()):
                pyproject_path = REPO_ROOT / subproject / "pyproject.toml"

                self.assertTrue(pyproject_path.is_file())
                self.assertIn("D", _ruff_selected_rules(pyproject_path))
                self.assertEqual("google", _pydocstyle_convention(pyproject_path))
                self.assertTrue(
                    _has_ruff_check_hook(subproject),
                    f"{subproject}/.pre-commit-config.yaml must run ruff check "
                    "through a ruff-check hook",
                )

    def test_documentation_sync_names_python_ratchet_scope(self) -> None:
        section = _doc_sync_ratchet_section()
        coverage_match = re.search(
            r"The current ratchet covers(?P<coverage>.*?)with each Subproject's "
            r"pyproject",
            section,
            flags=re.DOTALL,
        )

        self.assertIsNotNone(coverage_match)
        if coverage_match is None:
            return
        documented_subprojects = set(
            re.findall(r"`([^`]+)`", coverage_match.group("coverage"))
        )

        self.assertEqual(
            documented_subprojects,
            _subproject_path_strings(PYTHON_DOCSTRING_RATCHET_SUBPROJECTS),
        )
        for subproject in PYTHON_DOCSTRING_RATCHET_EXCLUDED_SUBPROJECTS:
            self.assertIn(
                f"`{subproject.as_posix()}` is not currently on this ratchet.",
                section,
            )

    def test_shell_header_hook_coverage_is_exact(self) -> None:
        actual_subprojects: set[Path] = set()
        for config_path in _candidate_pre_commit_configs():
            entries = _pre_commit_hook_entries(config_path)
            entry = entries.get("shell-script-headers")
            if _entry_invokes_shell_header_checker(config_path, entry):
                actual_subprojects.add(config_path.parent.relative_to(REPO_ROOT))

        self.assertEqual(
            _subproject_path_strings(actual_subprojects),
            _subproject_path_strings(SHELL_HEADER_RATCHET_SUBPROJECTS),
        )

    def test_shell_header_subprojects_keep_checker_hook(self) -> None:
        for subproject in SHELL_HEADER_RATCHET_SUBPROJECTS:
            with self.subTest(subproject=subproject.as_posix()):
                config_path = REPO_ROOT / subproject / ".pre-commit-config.yaml"
                entries = _pre_commit_hook_entries(config_path)

                self.assertIn("shell-script-headers", entries)
                self.assertTrue(
                    _entry_invokes_shell_header_checker(
                        config_path,
                        entries.get("shell-script-headers"),
                    ),
                    f"{config_path.relative_to(REPO_ROOT)} must invoke "
                    "scripts/check_shell_script_headers.py",
                )

    def test_documentation_sync_documents_shell_header_checker(self) -> None:
        section = _doc_sync_ratchet_section()

        self.assertIn("scripts/check_shell_script_headers.py", section)
        self.assertIn("enforces shell documentation", section)
        self.assertIn("executable shell scripts", section)


if __name__ == "__main__":
    unittest.main()
