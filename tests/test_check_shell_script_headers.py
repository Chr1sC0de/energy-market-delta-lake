from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path


CHECKER_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "check_shell_script_headers.py"
)
SPEC = importlib.util.spec_from_file_location("check_shell_script_headers", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Could not load scripts/check_shell_script_headers.py")
checker = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checker
SPEC.loader.exec_module(checker)


class ShellScriptHeaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_file(self, name: str, content: str, *, executable: bool = True) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        path.chmod(0o755 if executable else 0o644)
        return path

    def test_valid_header_passes(self) -> None:
        path = self.write_file(
            "valid.sh",
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "# Syncs LocalStack files for local development.",
                    "set -euo pipefail",
                ]
            ),
        )

        self.assertEqual(checker.check_paths([path]), [])

    def test_missing_header_fails(self) -> None:
        path = self.write_file(
            "missing.sh",
            "\n".join(
                [
                    "#!/bin/bash",
                    "set -euo pipefail",
                ]
            ),
        )

        failures = checker.check_paths([path])

        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].line_number, 2)
        self.assertIn("missing shell header", failures[0].message)

    def test_extensionless_shell_script_passes(self) -> None:
        path = self.write_file(
            "deploy",
            "\n".join(
                [
                    "#!/usr/bin/env -S bash -euo pipefail",
                    "# Deploys the current Pulumi stack for local validation.",
                    "pulumi preview",
                ]
            ),
        )

        self.assertEqual(checker.check_paths([path]), [])

    def test_non_shell_files_are_skipped(self) -> None:
        python_script = self.write_file(
            "tool.py",
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "print('not shell')",
                ]
            ),
        )
        non_executable_shell = self.write_file(
            "library.sh",
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "set -euo pipefail",
                ]
            ),
            executable=False,
        )

        self.assertEqual(checker.check_paths([python_script, non_executable_shell]), [])

    def test_directive_only_header_fails(self) -> None:
        path = self.write_file(
            "directive.sh",
            "\n".join(
                [
                    "#!/usr/bin/env bash",
                    "# shellcheck disable=SC1091",
                    "source ./common",
                ]
            ),
        )

        failures = checker.check_paths([path])

        self.assertEqual(len(failures), 1)
        self.assertIn("tooling directives", failures[0].message)

    def test_cli_reports_clear_failure_output(self) -> None:
        path = self.write_file(
            "missing.sh",
            "\n".join(
                [
                    "#!/usr/bin/env sh",
                    "echo missing header",
                ]
            ),
        )
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            exit_code = checker.main([str(path)])

        self.assertEqual(exit_code, 1)
        self.assertIn(f"{path}:2", stderr.getvalue())
        self.assertIn("human purpose/context", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
