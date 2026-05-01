from __future__ import annotations

import os
import re
import shlex
import tomllib
import unittest
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
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
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "generated",
        "vendor",
    }
)
SUBPROJECT_PARENT_DIRS = frozenset({"backend-services", "infrastructure"})


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


def _readme_ratchet_section() -> str:
    readme = README_PATH.read_text(encoding="utf-8")
    match = re.search(
        r"^### Documentation QA ratchet$(?P<section>.*?)(?=^## )",
        readme,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        return ""
    return match.group("section")


class DocumentationQaRatchetTests(unittest.TestCase):
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

    def test_readme_names_python_ratchet_scope(self) -> None:
        section = _readme_ratchet_section()
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

    def test_readme_documents_shell_header_checker(self) -> None:
        section = _readme_ratchet_section()

        self.assertIn("scripts/check_shell_script_headers.py", section)
        self.assertIn("enforces shell documentation", section)
        self.assertIn("executable shell scripts", section)


if __name__ == "__main__":
    unittest.main()
