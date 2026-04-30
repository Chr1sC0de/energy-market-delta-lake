#!/usr/bin/env python3
"""Check executable shell scripts for human purpose headers."""

from __future__ import annotations

import argparse
import shlex
import stat
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path


SHELL_INTERPRETERS = frozenset({"bash", "sh"})
DIRECTIVE_PREFIXES = ("shellcheck ", "shellcheck:", "shfmt ", "shfmt:")
EXECUTABLE_BITS = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH


@dataclass(frozen=True)
class ShellHeaderFailure:
    path: Path
    line_number: int
    message: str

    def format(self) -> str:
        location = str(self.path)
        if self.line_number > 0:
            location = f"{location}:{self.line_number}"
        return f"{location}: {self.message}"


def is_regular_executable(path: Path) -> bool:
    if not path.exists():
        return False
    mode = path.stat().st_mode
    return stat.S_ISREG(mode) and bool(mode & EXECUTABLE_BITS)


def shell_from_direct_interpreter(tokens: Sequence[str]) -> bool:
    if len(tokens) == 0:
        return False
    return Path(tokens[0]).name in SHELL_INTERPRETERS


def shell_from_env_interpreter(tokens: Sequence[str]) -> bool:
    for token in tokens:
        if token == "-S":
            continue
        if token.startswith("-"):
            continue
        if "=" in token:
            continue
        return Path(token).name in SHELL_INTERPRETERS
    return False


def is_shell_shebang(line: str) -> bool:
    if not line.startswith("#!"):
        return False

    try:
        tokens = shlex.split(line[2:].strip())
    except ValueError:
        tokens = line[2:].strip().split()

    if len(tokens) == 0:
        return False
    if shell_from_direct_interpreter(tokens):
        return True
    if Path(tokens[0]).name != "env":
        return False
    return shell_from_env_interpreter(tokens[1:])


def is_comment_line(line: str) -> bool:
    return line.lstrip().startswith("#")


def comment_text(line: str) -> str:
    return line.lstrip()[1:].strip()


def is_tooling_directive(text: str) -> bool:
    normalized = text.lower()
    return any(normalized.startswith(prefix) for prefix in DIRECTIVE_PREFIXES)


def has_human_header_line(header_lines: Iterable[str]) -> bool:
    for line in header_lines:
        text = comment_text(line)
        if text == "":
            continue
        if is_tooling_directive(text):
            continue
        if any(character.isalpha() for character in text):
            return True
    return False


def check_shell_header(path: Path, lines: Sequence[str]) -> ShellHeaderFailure | None:
    if len(lines) < 2 or not is_comment_line(lines[1]):
        return ShellHeaderFailure(
            path=path,
            line_number=2,
            message=(
                "missing shell header: add a human purpose/context comment "
                "block immediately after the shebang"
            ),
        )

    header_lines: list[str] = []
    for line in lines[1:]:
        if not is_comment_line(line):
            break
        header_lines.append(line)

    if has_human_header_line(header_lines):
        return None

    return ShellHeaderFailure(
        path=path,
        line_number=2,
        message=(
            "invalid shell header: comment block after the shebang must include "
            "human purpose/context text, not only tooling directives or "
            "separators"
        ),
    )


def check_path(path: Path) -> ShellHeaderFailure | None:
    if not path.exists():
        return ShellHeaderFailure(
            path=path,
            line_number=0,
            message="file does not exist",
        )
    if not is_regular_executable(path):
        return None

    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ShellHeaderFailure(
            path=path,
            line_number=0,
            message="could not read executable file as UTF-8",
        )

    lines = text.splitlines()
    if len(lines) == 0 or not is_shell_shebang(lines[0]):
        return None
    return check_shell_header(path, lines)


def check_paths(paths: Iterable[Path]) -> list[ShellHeaderFailure]:
    failures: list[ShellHeaderFailure] = []
    for path in paths:
        failure = check_path(path)
        if failure is not None:
            failures.append(failure)
    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Require executable shell scripts to document their purpose with "
            "a human comment header immediately after the shebang."
        )
    )
    parser.add_argument("paths", nargs="*", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    failures = check_paths(args.paths)

    for failure in failures:
        sys.stderr.write(f"{failure.format()}\n")
    if len(failures) > 0:
        sys.stderr.write(
            f"shell script header check failed for {len(failures)} file(s).\n"
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
