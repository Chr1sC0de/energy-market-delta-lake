"""Tests for the deployed AWS workflow integration-test script."""

import json
import os
import stat
import subprocess
import textwrap
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]


def test_rejects_inherited_aws_endpoint_override_before_commands(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    command_log = tmp_path / "commands.jsonl"

    for command_name in ("aws", "pulumi", "uv", "prek"):
        _write_logging_executable(fake_bin / command_name, command_name, command_log)

    env = {
        **os.environ,
        "AWS_ENDPOINT_URL": "http://localhost:4566",
        "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
    }

    result = subprocess.run(
        [str(PROJECT_DIR / "scripts" / "run-integration-tests"), "--with-idempotency"],
        cwd=PROJECT_DIR,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 2
    assert "requires real AWS endpoints" in result.stderr
    assert "AWS_ENDPOINT_URL" in result.stderr
    assert "localhost:4566" not in result.stderr
    assert not command_log.exists()


def test_runs_deployed_workflow_with_fake_commands_when_no_endpoint_override(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    command_log = tmp_path / "commands.jsonl"

    _write_fake_aws(fake_bin / "aws", command_log)
    _write_fake_pulumi(fake_bin / "pulumi", command_log)
    _write_fake_uv(fake_bin / "uv", command_log)
    _write_logging_executable(fake_bin / "prek", "prek", command_log)

    env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith("AWS_ENDPOINT_URL")
    }
    env.update(
        {
            "ECS_STABILITY_HOLD_SECONDS": "0",
            "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
            "PULUMI_STACK": "test-ausenergymarket",
        }
    )

    subprocess.run(
        [
            str(PROJECT_DIR / "scripts" / "run-integration-tests"),
            "--skip-up",
            "--with-idempotency",
        ],
        cwd=PROJECT_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert _read_jsonl(command_log) == [
        {"command": "aws", "argv": ["sts", "get-caller-identity"]},
        {"command": "pulumi", "argv": ["stack", "select", "test-ausenergymarket"]},
        {
            "command": "uv",
            "argv": ["run", "pytest", "tests/unit", "tests/component", "-q"],
        },
        {"command": "prek", "argv": ["run", "-a"]},
        {
            "command": "uv",
            "argv": [
                "run",
                "python",
                "-m",
                "cognito_auth_flow_preflight",
                "--region",
                "ap-southeast-2",
                "--resource-name",
                "test-energy-market",
            ],
        },
        {
            "command": "uv",
            "argv": ["run", "python", "-"],
        },
        {
            "command": "aws",
            "argv": [
                "ecs",
                "wait",
                "services-stable",
                "--cluster",
                "test-energy-market-dagster-cluster",
                "--services",
                "test-energy-market-dagster",
                "test-energy-market-user-code",
            ],
        },
        {
            "command": "uv",
            "argv": [
                "run",
                "python",
                "-m",
                "ecs_rollouts",
                "--cluster",
                "test-energy-market-dagster-cluster",
                "--services",
                "test-energy-market-dagster",
                "test-energy-market-user-code",
                "--timeout-seconds",
                "900",
                "--poll-seconds",
                "15",
            ],
        },
        {
            "command": "uv",
            "argv": ["run", "pytest", "tests/deployed", "-v"],
            "pulumi_integration_tests": "1",
        },
        {
            "command": "pulumi",
            "argv": [
                "preview",
                "--expect-no-changes",
                "--non-interactive",
                "--stack",
                "test-ausenergymarket",
            ],
        },
    ]


def _write_logging_executable(path: Path, command_name: str, command_log: Path) -> None:
    _write_executable(
        path,
        f"""
        #!/usr/bin/env python3
        import json
        import sys
        from pathlib import Path

        with Path({str(command_log)!r}).open("a", encoding="utf-8") as log_file:
            json.dump({{"command": {command_name!r}, "argv": sys.argv[1:]}}, log_file)
            log_file.write("\\n")
        """,
    )


def _write_fake_aws(path: Path, command_log: Path) -> None:
    _write_logging_executable(path, "aws", command_log)


def _write_fake_pulumi(path: Path, command_log: Path) -> None:
    _write_logging_executable(path, "pulumi", command_log)


def _write_fake_uv(path: Path, command_log: Path) -> None:
    _write_executable(
        path,
        f"""
        #!/usr/bin/env python3
        import json
        import os
        import sys
        from pathlib import Path

        entry = {{"command": "uv", "argv": sys.argv[1:]}}
        if sys.argv[1:] == ["run", "pytest", "tests/deployed", "-v"]:
            entry["pulumi_integration_tests"] = os.environ.get("PULUMI_INTEGRATION_TESTS")

        with Path({str(command_log)!r}).open("a", encoding="utf-8") as log_file:
            json.dump(entry, log_file)
            log_file.write("\\n")

        if sys.argv[1:] == ["run", "python", "-"]:
            print("test-energy-market-dagster")
            print("test-energy-market-user-code")
        """,
    )


def _write_executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line != ""
    ]
