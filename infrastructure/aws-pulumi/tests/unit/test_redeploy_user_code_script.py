"""Tests for the Dagster user-code redeploy script."""

import json
import os
import stat
import subprocess
import textwrap
from pathlib import Path

from code_locations import (
    default_code_location,
    load_code_locations,
    user_code_component_name,
    user_code_ecr_repository_resource_name,
    user_code_ecs_service_resource_name,
    user_code_task_definition_resource_name,
)

PROJECT_DIR = Path(__file__).resolve().parents[2]


def test_redeploy_user_code_uses_non_interactive_targeted_pulumi_up(
    tmp_path: Path,
) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    pulumi_log = tmp_path / "pulumi.jsonl"
    uv_log = tmp_path / "uv.jsonl"

    _write_executable(
        fake_bin / "pulumi",
        """
        #!/usr/bin/env python3
        import json
        import os
        import sys
        from pathlib import Path

        with Path(os.environ["PULUMI_COMMAND_LOG"]).open("a", encoding="utf-8") as log_file:
            json.dump(sys.argv[1:], log_file)
            log_file.write("\\n")
        """,
    )
    _write_executable(
        fake_bin / "uv",
        """
        #!/usr/bin/env python3
        import json
        import os
        import sys
        from pathlib import Path

        with Path(os.environ["UV_COMMAND_LOG"]).open("a", encoding="utf-8") as log_file:
            json.dump(sys.argv[1:], log_file)
            log_file.write("\\n")

        if sys.argv[1:3] != ["run", "python"]:
            print(f"unexpected uv invocation: {sys.argv[1:]}", file=sys.stderr)
            raise SystemExit(2)

        os.execv(sys.executable, [sys.executable, *sys.argv[3:]])
        """,
    )

    stack = "checkpoint-ausenergymarket"
    resource_name = "checkpoint-energy-market"
    env = {
        **os.environ,
        "ENVIRONMENT": "checkpoint",
        "PATH": f"{fake_bin}{os.pathsep}{os.environ['PATH']}",
        "PULUMI_COMMAND_LOG": str(pulumi_log),
        "PULUMI_STACK": stack,
        "UV_COMMAND_LOG": str(uv_log),
    }

    subprocess.run(
        [str(PROJECT_DIR / "scripts" / "redeploy-user-code")],
        cwd=PROJECT_DIR,
        env=env,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )

    pulumi_commands = _read_jsonl(pulumi_log)
    expected_up = ["up", "--yes", "--non-interactive", "--stack", stack]
    for target in _expected_user_code_targets(stack, resource_name):
        expected_up.extend(["--target", target])

    assert _read_jsonl(uv_log) == [["run", "python", "-"]]
    assert pulumi_commands == [
        ["stack", "select", stack],
        expected_up,
    ]


def _write_executable(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _read_jsonl(path: Path) -> list[list[str]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line != ""
    ]


def _expected_user_code_targets(stack: str, resource_name: str) -> list[str]:
    locations = load_code_locations()
    default_location = default_code_location(locations)
    targets: list[str] = []

    for location in locations:
        component_name = user_code_component_name(
            resource_name,
            location,
            default_location,
        )
        repository_name = user_code_ecr_repository_resource_name(
            resource_name,
            location,
        )
        task_definition_name = user_code_task_definition_resource_name(component_name)
        service_name = user_code_ecs_service_resource_name(component_name)

        targets.extend(
            [
                (
                    "urn:pulumi:"
                    f"{stack}::aws-pulumi::{resource_name}:components:ecr"
                    f"$aws:ecr/repository:Repository::{repository_name}"
                ),
                (
                    "urn:pulumi:"
                    f"{stack}::aws-pulumi::{component_name}:components:DagsterUserCodeService"
                    f"$aws:ecs/taskDefinition:TaskDefinition::{task_definition_name}"
                ),
                (
                    "urn:pulumi:"
                    f"{stack}::aws-pulumi::{component_name}:components:DagsterUserCodeService"
                    f"$aws:ecs/service:Service::{service_name}"
                ),
            ]
        )

    return targets
