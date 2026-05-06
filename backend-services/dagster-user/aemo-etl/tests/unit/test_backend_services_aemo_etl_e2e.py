"""Unit tests for the backend-services AEMO ETL e2e stack command."""

import json
import runpy
import socket
import subprocess
import tempfile
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, cast

import pytest
from dagster_graphql.schema import create_schema
from graphql import GraphQLError, GraphQLSchema, Source, parse, validate


EMBEDDED_DAGSTER_GRAPHQL_DOCUMENTS = (
    ("ping query", "PING_QUERY"),
    ("definition-state query", "DAGSTER_DEFINITION_STATE_QUERY"),
    ("sensor mutation", "START_SENSOR_MUTATION"),
    ("launch mutation", "LAUNCH_RUN_MUTATION"),
    ("dataflow run status query", "DAGSTER_DATAFLOW_RUN_STATUS_QUERY"),
    ("asset graph query", "DAGSTER_ASSET_GRAPH_QUERY"),
    ("dataflow target status query", "DAGSTER_DATAFLOW_TARGET_STATUS_QUERY"),
)


def load_e2e_command_module() -> dict[str, Any]:
    """Load the extensionless backend-services command as a Python module."""
    script_path = Path(__file__).resolve().parents[4] / "scripts/aemo-etl-e2e"
    return runpy.run_path(
        str(script_path),
        run_name="backend_services_aemo_etl_e2e",
    )


def get_callable(
    module_globals: Mapping[str, Any],
    name: str,
) -> Callable[..., Any]:
    """Return a callable loaded from the command module."""
    value = module_globals[name]
    assert callable(value)
    return cast("Callable[..., Any]", value)


def get_exception_class(
    module_globals: Mapping[str, Any],
    name: str,
) -> type[Exception]:
    """Return an exception class loaded from the command module."""
    value = module_globals[name]
    assert isinstance(value, type)
    assert issubclass(value, Exception)
    return value


@pytest.fixture(scope="module")
def dagster_graphql_schema() -> GraphQLSchema:
    """Return the installed Dagster GraphQL schema without a running webserver."""
    schema = create_schema().graphql_schema
    assert isinstance(schema, GraphQLSchema)
    return schema


def validate_dagster_graphql_document(
    *,
    schema: GraphQLSchema,
    document_name: str,
    document: str,
) -> None:
    """Validate one e2e monitor document against the installed Dagster schema."""
    source = Source(document, name=document_name)

    try:
        parsed_document = parse(source)
    except GraphQLError as error:
        raise AssertionError(
            format_dagster_graphql_validation_errors(document_name, (error,)),
        ) from error

    validation_errors = validate(schema, parsed_document)
    if validation_errors:
        raise AssertionError(
            format_dagster_graphql_validation_errors(
                document_name,
                validation_errors,
            ),
        )


def format_dagster_graphql_validation_errors(
    document_name: str,
    validation_errors: Sequence[GraphQLError],
) -> str:
    """Return actionable validation output for embedded monitor documents."""
    details = "\n".join(
        f"- {error.message}{format_graphql_error_locations(error)}"
        for error in validation_errors
    )
    return (
        f"{document_name} is not valid against the installed Dagster GraphQL "
        "schema.\n"
        "This Unit test lane check protects the AEMO ETL End-to-end test "
        "monitor from Dagster schema drift before Local integration or "
        "Promotion.\n"
        f"{details}"
    )


def format_graphql_error_locations(error: GraphQLError) -> str:
    """Return a compact GraphQL source location suffix for an error."""
    if error.locations is None:
        return ""
    locations = ", ".join(
        f"{location.line}:{location.column}" for location in error.locations
    )
    return f" at {locations}"


@pytest.mark.parametrize(
    ("document_name", "global_name"),
    EMBEDDED_DAGSTER_GRAPHQL_DOCUMENTS,
)
def test_embedded_dagster_graphql_documents_match_installed_schema(
    dagster_graphql_schema: GraphQLSchema,
    document_name: str,
    global_name: str,
) -> None:
    """Schema-validate e2e monitor GraphQL in the Unit test lane."""
    module = load_e2e_command_module()
    document = module[global_name]
    assert isinstance(document, str)

    validate_dagster_graphql_document(
        schema=dagster_graphql_schema,
        document_name=document_name,
        document=document,
    )


@pytest.mark.parametrize(
    ("document_name", "document", "expected_error"),
    (
        (
            "invalid field fixture",
            "query E2EBadField { definitelyMissingField }",
            "Cannot query field 'definitelyMissingField'",
        ),
        (
            "invalid type placement fixture",
            """
            mutation E2EBadTypePlacement($executionParams: ExecutionParams!) {
              launchRun(executionParams: $executionParams) {
                runId
              }
            }
            """,
            "Cannot query field 'runId' on type 'LaunchRunResult'",
        ),
    ),
)
def test_graphql_document_validation_reports_actionable_schema_errors(
    dagster_graphql_schema: GraphQLSchema,
    document_name: str,
    document: str,
    expected_error: str,
) -> None:
    """Invalid fields and type placement produce useful Unit test failures."""
    with pytest.raises(AssertionError) as caught:
        validate_dagster_graphql_document(
            schema=dagster_graphql_schema,
            document_name=document_name,
            document=document,
        )

    message = str(caught.value)
    assert document_name in message
    assert expected_error in message
    assert "Unit test lane" in message
    assert "Local integration or Promotion" in message


def test_dagster_graphql_client_wraps_connection_reset() -> None:
    """Transient socket resets are retried by the Dagster readiness wait loop."""
    module = load_e2e_command_module()
    dagster_graphql_client = cast("Any", get_callable(module, "DagsterGraphQLClient"))
    command_error = get_exception_class(module, "CommandError")

    def raise_connection_reset(*args: object, **kwargs: object) -> object:
        del args, kwargs
        raise ConnectionResetError("connection reset by peer")

    dagster_graphql_client.execute.__globals__["urlopen"] = raise_connection_reset
    client = dagster_graphql_client("http://127.0.0.1:3001/graphql")

    try:
        client.execute("query E2EPing { version }")
    except command_error as error:
        assert "Dagster GraphQL request failed" in str(error)
        assert "connection reset by peer" in str(error)
    else:
        raise AssertionError("connection reset was not wrapped")


def test_transient_dagster_graphql_errors_are_retried() -> None:
    """Idempotent GraphQL calls retry local transport failures."""
    module = load_e2e_command_module()
    execute_with_retries = get_callable(module, "execute_dagster_graphql_with_retries")
    command_error = get_exception_class(module, "CommandError")

    class FakeClient:
        """Fail once with a transient transport error, then return data."""

        def __init__(self) -> None:
            self.attempts = 0

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
        ) -> Mapping[str, object]:
            del query, variables
            self.attempts += 1
            if self.attempts == 1:
                raise command_error(
                    "Dagster GraphQL request failed at http://127.0.0.1:3001/graphql: timed out"
                )
            return {"ok": True}

    client = FakeClient()

    payload = execute_with_retries(client, "query E2EPing { version }", context="ping")

    assert payload == {"ok": True}
    assert client.attempts == 2


def test_podman_socket_is_derived_from_xdg_runtime_dir() -> None:
    """The command uses the current user runtime dir, not a fixed UID path."""
    module = load_e2e_command_module()
    with tempfile.TemporaryDirectory(
        prefix="aemo-e2e-runtime-",
        dir="/tmp",
    ) as runtime_dir_name:
        runtime_dir = Path(runtime_dir_name)
        socket_dir = runtime_dir / "podman"
        socket_dir.mkdir(parents=True)
        socket_path = socket_dir / "podman.sock"
        assert len(str(socket_path)) < 100

        with socket.socket(socket.AF_UNIX) as podman_socket:
            podman_socket.bind(str(socket_path))

            podman_socket_from_xdg_runtime_dir = get_callable(
                module,
                "podman_socket_from_xdg_runtime_dir",
            )
            assert (
                podman_socket_from_xdg_runtime_dir(
                    {"XDG_RUNTIME_DIR": str(runtime_dir)}
                )
                == socket_path
            )


def test_podman_socket_fails_when_xdg_runtime_dir_missing() -> None:
    """The command fails before falling back to a hard-coded socket path."""
    module = load_e2e_command_module()
    podman_socket_from_xdg_runtime_dir = get_callable(
        module,
        "podman_socket_from_xdg_runtime_dir",
    )
    command_error = get_exception_class(module, "CommandError")

    try:
        podman_socket_from_xdg_runtime_dir({})
    except command_error as error:
        assert "XDG_RUNTIME_DIR" in str(error)
    else:
        raise AssertionError("missing XDG_RUNTIME_DIR did not fail")


def test_image_selection_reuses_existing_images_by_default(tmp_path: Path) -> None:
    """Only missing image tags are built unless an explicit rebuild is requested."""
    module = load_e2e_command_module()
    image_spec = get_callable(module, "ImageSpec")
    select_images_to_build = get_callable(module, "select_images_to_build")
    image_specs = (
        image_spec("postgres", "localhost/e2e_postgres:latest", tmp_path),
        image_spec("localstack", "localhost/e2e_localstack:latest", tmp_path),
    )

    selected = select_images_to_build(
        {"localhost/e2e_postgres:latest"},
        image_specs=image_specs,
        rebuild=False,
    )
    rebuild_selected = select_images_to_build(
        {"localhost/e2e_postgres:latest", "localhost/e2e_localstack:latest"},
        image_specs=image_specs,
        rebuild=True,
    )

    assert isinstance(selected, tuple)
    assert isinstance(rebuild_selected, tuple)
    assert [getattr(spec, "name") for spec in selected] == ["localstack"]
    assert rebuild_selected == image_specs


def test_generated_dagster_config_uses_e2e_socket_and_network(tmp_path: Path) -> None:
    """Run workers use the generated e2e network and current Podman socket."""
    module = load_e2e_command_module()
    render_dagster_yaml = get_callable(module, "render_dagster_yaml")
    socket_path = tmp_path / "runtime/podman/podman.sock"

    config = render_dagster_yaml(
        aemo_etl_image="localhost/aemo-etl-e2e_aemo-etl:latest",
        podman_socket=socket_path,
    )

    assert isinstance(config, str)
    assert str(socket_path) in config
    assert "localhost/aemo-etl-e2e_aemo-etl:latest" in config
    assert 'network: "aemo-etl-e2e-dagster-network"' in config
    assert "max_concurrent_runs: 6" in config
    assert "/" + "/".join(("run", "user", "1000")) not in config


def test_generated_dagster_config_allows_run_queue_override(tmp_path: Path) -> None:
    """The e2e command can tune Dagster run queue concurrency."""
    module = load_e2e_command_module()
    render_dagster_yaml = get_callable(module, "render_dagster_yaml")

    config = render_dagster_yaml(
        aemo_etl_image="localhost/aemo-etl-e2e_aemo-etl:latest",
        podman_socket=tmp_path / "runtime/podman/podman.sock",
        max_concurrent_runs=3,
    )

    assert isinstance(config, str)
    assert "max_concurrent_runs: 3" in config


def test_run_parser_defaults_to_full_dataflow_timeout_and_concurrency() -> None:
    """The e2e run defaults match the full dataflow acceptance criteria."""
    module = load_e2e_command_module()
    build_parser = get_callable(module, "build_parser")
    run_options_from_args = get_callable(module, "run_options_from_args")

    options = run_options_from_args(build_parser().parse_args(["run"]))

    assert getattr(options, "scenario") == "full-gas-model"
    assert getattr(options, "raw_latest_count") == 3
    assert getattr(options, "zip_latest_count") == 3
    assert getattr(options, "timeout_seconds") == 90 * 60
    assert getattr(options, "max_concurrent_runs") == 6
    assert getattr(options, "launch_mode") == "sensor-driven"

    promotion_options = run_options_from_args(
        build_parser().parse_args(["run", "--scenario", "promotion-gas-model"])
    )
    assert getattr(promotion_options, "raw_latest_count") == 1
    assert getattr(promotion_options, "zip_latest_count") == 1
    assert getattr(promotion_options, "timeout_seconds") == 20 * 60
    assert getattr(promotion_options, "max_concurrent_runs") == 6
    assert getattr(promotion_options, "launch_mode") == "direct-upstream-asset-launch"

    override_options = run_options_from_args(
        build_parser().parse_args(
            [
                "run",
                "--scenario",
                "promotion-gas-model",
                "--raw-latest-count",
                "5",
                "--zip-latest-count",
                "2",
                "--timeout-seconds",
                "1800",
                "--max-concurrent-runs",
                "4",
            ]
        )
    )
    assert getattr(override_options, "raw_latest_count") == 5
    assert getattr(override_options, "zip_latest_count") == 2
    assert getattr(override_options, "timeout_seconds") == 1800
    assert getattr(override_options, "max_concurrent_runs") == 4
    assert getattr(override_options, "launch_mode") == "direct-upstream-asset-launch"


def test_promotion_scenario_keeps_approved_sensor_and_target_contract() -> None:
    """Promotion targeting narrows seed volume without bypassing coverage."""
    module = load_e2e_command_module()
    expected_sensor_names = set(module["EXPECTED_DATAFLOW_SENSOR_NAMES"])
    asset_graph_query = module["DAGSTER_ASSET_GRAPH_QUERY"]
    target_status_query = module["DAGSTER_DATAFLOW_TARGET_STATUS_QUERY"]

    assert "gbb_event_driven_assets_sensor" in expected_sensor_names
    assert "vicgas_event_driven_assets_sensor" in expected_sensor_names
    assert "gbb_unzipper_sensor" in expected_sensor_names
    assert "vicgas_unzipper_sensor" in expected_sensor_names
    assert "silver_table_metadata_sensor" in expected_sensor_names
    assert "silver_gas_fact_operational_meter_flow_sensor" in expected_sensor_names
    assert "dependencyKeys" in asset_graph_query
    assert 'groupName: "gas_model"' in target_status_query
    assert "isMaterializable" in target_status_query


def test_generated_compose_is_isolated_e2e_stack(tmp_path: Path) -> None:
    """The generated compose file omits the broader developer stack services."""
    module = load_e2e_command_module()
    render_compose_yaml = get_callable(module, "render_compose_yaml")
    images = {
        "postgres": "localhost/aemo-etl-e2e_postgres:latest",
        "localstack": "localhost/aemo-etl-e2e_localstack:latest",
        "aemo-etl": "localhost/aemo-etl-e2e_aemo-etl:latest",
        "dagster-core": "localhost/aemo-etl-e2e_dagster-core:latest",
    }

    compose = render_compose_yaml(
        images=images,
        seed_root=tmp_path / "seed",
        podman_socket=tmp_path / "runtime/podman/podman.sock",
        dagster_config_file=tmp_path / "dagster.yaml",
        workspace_file=tmp_path / "workspace.yaml",
        webserver_port=3001,
        raw_latest_count=10,
        zip_latest_count=3,
    )

    assert isinstance(compose, str)
    assert "name: aemo-etl-e2e" in compose
    assert "container_name: aemo-etl-e2e-dagster-webserver" in compose
    assert 'subnet: "10.89.10.0/24"' in compose
    assert 'DAGSTER_POSTGRES_HOSTNAME: "10.89.10.10"' in compose
    assert 'AWS_ENDPOINT_URL: "http://10.89.10.11:4566"' in compose
    assert 'ipv4_address: "10.89.10.12"' in compose
    assert "aemo-etl-seed-localstack:" in compose
    assert "depends_on:" not in compose
    assert "dagster-webserver-admin" not in compose
    assert "dagster-webserver-guest" not in compose
    assert "authentication:" not in compose
    assert "marimo:" not in compose
    assert "caddy:" not in compose


def test_generated_workspace_uses_static_code_server_address() -> None:
    """Dagster workspace loading does not depend on container DNS."""
    module = load_e2e_command_module()
    render_workspace_yaml = get_callable(module, "render_workspace_yaml")

    workspace = render_workspace_yaml()

    assert "host: 10.89.10.12" in workspace
    assert "host: aemo-etl" not in workspace


def test_start_stack_services_runs_compose_in_dependency_phases(tmp_path: Path) -> None:
    """The e2e command avoids Podman dependency graph hangs by phasing startup."""
    module = load_e2e_command_module()
    run_options_class = get_callable(module, "RunOptions")
    start_stack_services = get_callable(module, "start_stack_services")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Record commands and return ready container states."""

        def __init__(self) -> None:
            self.calls: list[list[str]] = []

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, check
            self.calls.append(list(args))
            if capture_output and args[:2] == ["podman", "inspect"]:
                container_name = args[2]
                state = {
                    "Status": "running",
                    "ExitCode": 0,
                    "Health": {"Status": "healthy"},
                }
                if container_name == "aemo-etl-e2e-seed-localstack":
                    state = {"Status": "exited", "ExitCode": 0}
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout=json.dumps([{"State": state}]),
                    stderr="",
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    runner = FakeRunner()
    options = run_options_class(
        scenario="full-gas-model",
        launch_mode="sensor-driven",
        rebuild=False,
        reuse=False,
        always_clean=False,
        seed_root=None,
        webserver_port=3001,
        raw_latest_count=3,
        zip_latest_count=3,
        timeout_seconds=90 * 60,
        max_concurrent_runs=6,
    )

    start_stack_services(
        runner,
        compose_command,
        backend_dir=tmp_path,
        options=options,
        deadline=1_000_000_000.0,
    )

    compose_up_calls = [
        call
        for call in runner.calls
        if call[: len(compose_command) + 1] == [*compose_command, "up"]
    ]
    assert compose_up_calls == [
        [
            *compose_command,
            "up",
            "-d",
            "--no-build",
            "postgres",
            "localstack",
        ],
        [*compose_command, "up", "--no-build", "aemo-etl-seed-localstack"],
        [*compose_command, "up", "-d", "--no-build", "aemo-etl"],
        [
            *compose_command,
            "up",
            "-d",
            "--no-build",
            "dagster-webserver",
            "dagster-daemon",
        ],
    ]


def test_cleanup_stack_removes_dagster_worker_containers() -> None:
    """Dagster run workers are not compose services and need explicit cleanup."""
    module = load_e2e_command_module()
    cleanup_stack = get_callable(module, "cleanup_stack")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Return stale workers before and after compose cleanup."""

        def __init__(self) -> None:
            self.calls: list[list[str]] = []
            self.worker_lists = iter(("worker-before\n", "worker-after\n"))

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, check
            self.calls.append(list(args))
            if capture_output and args[:3] == ["podman", "ps", "-aq"]:
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout=next(self.worker_lists),
                    stderr="",
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    runner = FakeRunner()

    issues = cleanup_stack(runner, compose_command)

    assert issues == []
    assert ["podman", "rm", "-f", "worker-before"] in runner.calls
    assert [*compose_command, "down", "-v", "--remove-orphans"] in runner.calls
    assert ["podman", "rm", "-f", "worker-after"] in runner.calls
    assert [
        "podman",
        "network",
        "rm",
        "aemo-etl-e2e-dagster-network",
    ] in runner.calls


@pytest.mark.parametrize(
    ("failing_command", "expected_command_prefix"),
    (
        ("compose-down", ("podman-compose", "--no-ansi", "-f", "compose.yaml")),
        ("worker-rm", ("podman", "rm", "-f")),
        ("network-rm", ("podman", "network", "rm")),
    ),
)
def test_cleanup_stack_reports_cleanup_command_failures(
    failing_command: str,
    expected_command_prefix: Sequence[str],
) -> None:
    """Cleanup failures stay visible in the e2e run manifest evidence."""
    module = load_e2e_command_module()
    cleanup_stack = get_callable(module, "cleanup_stack")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Fail one cleanup command while allowing the cleanup flow to continue."""

        def __init__(self) -> None:
            self.worker_lists = iter(("worker-before\n", "worker-after\n"))
            self.failure_reported = False

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            command_name = classify_cleanup_command(args)
            if command_name == "worker-ps":
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout=next(self.worker_lists),
                    stderr="",
                )
            if command_name == failing_command and not self.failure_reported:
                self.failure_reported = True
                return subprocess.CompletedProcess(
                    args,
                    1,
                    stdout="",
                    stderr=f"{failing_command} failed\n",
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    issues = cleanup_stack(FakeRunner(), compose_command)

    assert len(issues) == 1
    issue = issues[0]
    assert issue["severity"] == "error"
    assert issue["returncode"] == 1
    assert issue["stderr"] == f"{failing_command} failed"
    command = tuple(cast("Sequence[str]", issue["command"]))
    assert command[: len(expected_command_prefix)] == tuple(expected_command_prefix)


def test_cleanup_stack_reports_cleanup_command_warnings() -> None:
    """Successful cleanup commands with stderr are visible as warnings."""
    module = load_e2e_command_module()
    cleanup_stack = get_callable(module, "cleanup_stack")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Emit a Podman warning from worker cleanup."""

        def __init__(self) -> None:
            self.worker_lists = iter(("worker-before\n", ""))

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            command_name = classify_cleanup_command(args)
            if command_name == "worker-ps":
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout=next(self.worker_lists),
                    stderr="",
                )
            if command_name == "worker-rm":
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout="",
                    stderr="StopSignal SIGTERM failed, resorting to SIGKILL\n",
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    issues = cleanup_stack(FakeRunner(), compose_command)

    assert len(issues) == 1
    assert all(issue["severity"] == "warning" for issue in issues)
    assert {tuple(cast("Sequence[str]", issue["command"]))[:3] for issue in issues} == {
        ("podman", "rm", "-f")
    }


def test_cleanup_stack_with_telemetry_ignores_missing_pre_run_resources() -> None:
    """Pre-run cleanup treats already-absent e2e resources as benign."""
    module = load_e2e_command_module()
    cleanup_stack_with_telemetry = get_callable(
        module,
        "cleanup_stack_with_telemetry",
    )
    telemetry_class = get_callable(module, "GateRunTelemetry")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Report no prior compose stack or e2e network."""

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            command_name = classify_cleanup_command(args)
            if command_name == "worker-ps":
                return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
            if command_name == "compose-down":
                return subprocess.CompletedProcess(
                    args,
                    0,
                    stdout="",
                    stderr=(
                        'Error: no container with name or ID "aemo-etl-e2e" '
                        "found: no such container\n"
                        "Error: no pod with name or ID pod_aemo-etl-e2e "
                        "found: no such pod\n"
                    ),
                )
            if command_name == "network-rm":
                return subprocess.CompletedProcess(
                    args,
                    1,
                    stdout="",
                    stderr=(
                        "Error: unable to find network with name or ID "
                        "aemo-etl-e2e-dagster-network: network not found\n"
                    ),
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    telemetry = telemetry_class(started_monotonic=100.0)

    issues = cleanup_stack_with_telemetry(
        FakeRunner(),
        compose_command,
        telemetry=telemetry,
        phase="pre-run",
    )
    manifest = telemetry.to_manifest()
    cleanup_phases = cast(
        "Sequence[Mapping[str, object]]",
        manifest["cleanup_phases"],
    )

    assert issues == []
    assert cleanup_phases[0]["phase"] == "pre-run"
    assert cleanup_phases[0]["status"] == "completed"
    assert "issues" not in cleanup_phases[0]


def test_cleanup_stack_with_telemetry_ignores_post_success_missing_network() -> None:
    """Post-success cleanup treats a compose-removed e2e network as benign."""
    module = load_e2e_command_module()
    cleanup_stack_with_telemetry = get_callable(
        module,
        "cleanup_stack_with_telemetry",
    )
    cleanup_manifest_status = get_callable(module, "cleanup_manifest_status")
    telemetry_class = get_callable(module, "GateRunTelemetry")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Report compose cleanup success followed by an absent e2e network."""

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            command_name = classify_cleanup_command(args)
            if command_name == "worker-ps":
                return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
            if command_name == "network-rm":
                return subprocess.CompletedProcess(
                    args,
                    1,
                    stdout="",
                    stderr=(
                        "Error: unable to find network with name or ID "
                        "aemo-etl-e2e-dagster-network: network not found\n"
                    ),
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    telemetry = telemetry_class(started_monotonic=100.0)

    issues = cleanup_stack_with_telemetry(
        FakeRunner(),
        compose_command,
        telemetry=telemetry,
        phase="post-success",
    )
    manifest = telemetry.to_manifest()
    cleanup_phases = cast(
        "Sequence[Mapping[str, object]]",
        manifest["cleanup_phases"],
    )
    run_manifest: dict[str, object] = {
        "cleanup": cleanup_manifest_status(
            base_status="completed-after-success",
            warning_status="completed-with-warnings-after-success",
            error_status="incomplete-after-success",
            issues=issues,
        )
    }
    if len(issues) > 0:
        run_manifest["cleanup_issues"] = issues

    assert issues == []
    assert cleanup_phases[0]["phase"] == "post-success"
    assert cleanup_phases[0]["status"] == "completed"
    assert "issues" not in cleanup_phases[0]
    assert run_manifest == {"cleanup": "completed-after-success"}


def test_cleanup_stack_with_telemetry_records_incomplete_cleanup() -> None:
    """Cleanup telemetry records failed cleanup phases in the run manifest."""
    module = load_e2e_command_module()
    cleanup_stack_with_telemetry = get_callable(
        module,
        "cleanup_stack_with_telemetry",
    )
    cleanup_manifest_status = get_callable(module, "cleanup_manifest_status")
    telemetry_class = get_callable(module, "GateRunTelemetry")
    compose_command = ("podman-compose", "--no-ansi", "-f", "compose.yaml")

    class FakeRunner:
        """Fail network cleanup for telemetry assertions."""

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            if classify_cleanup_command(args) == "worker-ps":
                return subprocess.CompletedProcess(args, 0, stdout="", stderr="")
            if classify_cleanup_command(args) == "network-rm":
                return subprocess.CompletedProcess(
                    args,
                    1,
                    stdout="",
                    stderr="network is being used\n",
                )
            return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    telemetry = telemetry_class(started_monotonic=100.0)

    issues = cleanup_stack_with_telemetry(
        FakeRunner(),
        compose_command,
        telemetry=telemetry,
        phase="post-success",
    )
    manifest = telemetry.to_manifest()
    cleanup_phases = cast(
        "Sequence[Mapping[str, object]]",
        manifest["cleanup_phases"],
    )
    run_manifest: dict[str, object] = {
        "cleanup": cleanup_manifest_status(
            base_status="completed-after-success",
            warning_status="completed-with-warnings-after-success",
            error_status="incomplete-after-success",
            issues=issues,
        )
    }
    if len(issues) > 0:
        run_manifest["cleanup_issues"] = issues

    assert len(issues) == 1
    assert cleanup_phases[0]["phase"] == "post-success"
    assert cleanup_phases[0]["status"] == "incomplete"
    assert cleanup_phases[0]["issues"] == issues
    assert run_manifest["cleanup"] == "incomplete-after-success"
    assert run_manifest["cleanup_issues"] == issues


def classify_cleanup_command(args: Sequence[str]) -> str:
    """Return a compact cleanup command label for e2e unit tests."""
    if args[:3] == ["podman", "ps", "-aq"]:
        return "worker-ps"
    if args[:3] == ["podman", "rm", "-f"]:
        return "worker-rm"
    if args[:3] == ["podman", "network", "rm"]:
        return "network-rm"
    if len(args) >= 3 and args[-3:] == ["down", "-v", "--remove-orphans"]:
        return "compose-down"
    return "other"


def test_automation_validation_allows_only_expected_sensors() -> None:
    """Only the intended e2e sensors may run while schedules stay stopped."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    definition_state_class = get_callable(module, "DagsterDefinitionState")
    validate_dagster_automation_state = get_callable(
        module,
        "validate_dagster_automation_state",
    )
    command_error = get_exception_class(module, "CommandError")
    expected_sensor_names = module["EXPECTED_DATAFLOW_SENSOR_NAMES"]
    protected_schedule_names = module["PROTECTED_STOPPED_SCHEDULE_NAMES"]

    selector = selector_class("repo", "aemo-etl")
    valid_state = definition_state_class(
        selector=selector,
        max_concurrent_runs=6,
        sensors={
            **{name: "STOPPED" for name in expected_sensor_names},
            "aemo_etl_failed_run_alert_sensor": "STOPPED",
        },
        schedules={name: "STOPPED" for name in protected_schedule_names},
    )

    validate_dagster_automation_state(valid_state)

    invalid_state = definition_state_class(
        selector=selector,
        max_concurrent_runs=6,
        sensors={
            **{name: "STOPPED" for name in expected_sensor_names},
            "aemo_etl_failed_run_alert_sensor": "RUNNING",
        },
        schedules={name: "STOPPED" for name in protected_schedule_names},
    )
    try:
        validate_dagster_automation_state(invalid_state)
    except command_error as error:
        assert "unexpected Dagster sensors are running" in str(error)
    else:
        raise AssertionError("running alert sensor did not fail validation")


def test_start_expected_sensors_uses_graphql_for_intended_sensors_only() -> None:
    """The command starts the expected sensor set through GraphQL."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    start_expected_sensors = get_callable(module, "start_expected_sensors")
    expected_sensor_names = tuple(module["EXPECTED_DATAFLOW_SENSOR_NAMES"])

    class FakeClient:
        """Record GraphQL requests and return successful sensor starts."""

        def __init__(self) -> None:
            self.sensor_names: list[str] = []

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
        ) -> Mapping[str, object]:
            assert "startSensor" in query
            assert variables is not None
            selector = variables["selector"]
            assert isinstance(selector, Mapping)
            sensor_name = selector["sensorName"]
            assert isinstance(sensor_name, str)
            self.sensor_names.append(sensor_name)
            return {
                "startSensor": {
                    "__typename": "Sensor",
                    "name": sensor_name,
                    "sensorState": {"status": "RUNNING"},
                }
            }

    client = FakeClient()

    start_expected_sensors(client, selector_class("repo", "aemo-etl"))

    assert tuple(client.sensor_names) == expected_sensor_names
    assert "aemo_etl_failed_run_alert_sensor" not in client.sensor_names


def test_bootstrap_runs_launch_date_job_and_metadata_asset() -> None:
    """Non-sensor prerequisites are bootstrapped without starting schedules."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    launch_bootstrap_runs = get_callable(module, "launch_bootstrap_runs")

    class FakeClient:
        """Record launch requests for bootstrap runs."""

        def __init__(self) -> None:
            self.execution_params: list[Mapping[str, object]] = []

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            assert timeout_seconds == module["DAGSTER_LAUNCH_RUN_TIMEOUT_SECONDS"]
            assert "launchRun" in query
            assert variables is not None
            execution_params = variables["executionParams"]
            assert isinstance(execution_params, Mapping)
            self.execution_params.append(execution_params)
            return {
                "launchRun": {
                    "__typename": "LaunchRunSuccess",
                    "run": {
                        "runId": f"run-{len(self.execution_params)}",
                        "status": "QUEUED",
                    },
                }
            }

    client = FakeClient()

    run_ids = launch_bootstrap_runs(
        client,
        selector_class("repo", "aemo-etl"),
        run_id="e2e-run",
    )

    selectors: list[Mapping[str, object]] = []
    for params in client.execution_params:
        selector = params["selector"]
        assert isinstance(selector, Mapping)
        assert params["runConfigData"] == {}
        selectors.append(selector)

    assert run_ids == ["run-1", "run-2"]
    assert selectors[0]["pipelineName"] == "silver_gas_dim_date_job"
    assert selectors[1]["pipelineName"] == "__ASSET_JOB"
    assert selectors[1]["assetSelection"] == [
        {"path": ["bronze", "metadata", "bronze_table_metadata"]}
    ]


def test_select_gas_model_upstream_materializable_asset_keys() -> None:
    """Promotion targeting keeps the gas_model closure and skips source stubs."""
    module = load_e2e_command_module()
    asset_node_class = get_callable(module, "DagsterAssetNode")
    select_asset_keys = get_callable(
        module,
        "select_gas_model_upstream_materializable_asset_keys",
    )

    selected = select_asset_keys(
        [
            asset_node_class(
                key=("silver", "gas_model", "silver_gas_fact_flow"),
                group_name="gas_model",
                is_materializable=True,
                dependency_keys=(
                    ("silver", "gbb", "silver_gasbb_flow"),
                    ("external", "archive"),
                ),
            ),
            asset_node_class(
                key=("silver", "gbb", "silver_gasbb_flow"),
                group_name="gas_raw_cleansed",
                is_materializable=True,
                dependency_keys=(("bronze", "gbb", "bronze_gasbb_flow"),),
            ),
            asset_node_class(
                key=("bronze", "gbb", "bronze_gasbb_flow"),
                group_name="gas_raw",
                is_materializable=True,
                dependency_keys=(
                    ("bronze", "gbb", "bronze_nemweb_public_files_gbb"),
                    ("external", "archive"),
                ),
            ),
            asset_node_class(
                key=("bronze", "gbb", "bronze_nemweb_public_files_gbb"),
                group_name="gas_raw",
                is_materializable=True,
                dependency_keys=(),
            ),
            asset_node_class(
                key=("external", "archive"),
                group_name="",
                is_materializable=False,
                dependency_keys=(),
            ),
            asset_node_class(
                key=("silver", "other", "unrelated"),
                group_name="other",
                is_materializable=True,
                dependency_keys=(),
            ),
        ]
    )

    assert selected == (
        ("bronze", "gbb", "bronze_gasbb_flow"),
        ("silver", "gas_model", "silver_gas_fact_flow"),
        ("silver", "gbb", "silver_gasbb_flow"),
    )


def test_promotion_upstream_launch_uses_dependency_waves() -> None:
    """Promotion launch evidence records dependency-wave coverage."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    launch_assets = get_callable(module, "launch_gas_model_upstream_assets")

    class FakeClient:
        """Return a tiny asset graph and record launch requests."""

        def __init__(self) -> None:
            self.execution_params: list[Mapping[str, object]] = []
            self.status_checks = 0

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            if "assetNodes" in query:
                assert timeout_seconds is None
                return {
                    "assetNodes": [
                        {
                            "assetKey": {"path": ["silver", "gas_model", "target"]},
                            "groupName": "gas_model",
                            "isMaterializable": True,
                            "dependencyKeys": [
                                {"path": ["silver", "gbb", "upstream"]},
                                {"path": ["silver", "vicgas", "upstream"]},
                            ],
                        },
                        {
                            "assetKey": {"path": ["silver", "gbb", "upstream"]},
                            "groupName": "gas_raw_cleansed",
                            "isMaterializable": True,
                            "dependencyKeys": [
                                {"path": ["bronze", "gbb", f"raw_{index}"]}
                                for index in range(5)
                            ],
                        },
                        {
                            "assetKey": {"path": ["silver", "vicgas", "upstream"]},
                            "groupName": "gas_raw_cleansed",
                            "isMaterializable": True,
                            "dependencyKeys": [{"path": ["bronze", "vicgas", "raw"]}],
                        },
                        *[
                            {
                                "assetKey": {"path": ["bronze", "gbb", f"raw_{index}"]},
                                "groupName": "gas_raw",
                                "isMaterializable": True,
                                "dependencyKeys": [
                                    {
                                        "path": [
                                            "bronze",
                                            "gbb",
                                            "bronze_nemweb_public_files_gbb",
                                        ]
                                    }
                                ],
                            }
                            for index in range(5)
                        ],
                        {
                            "assetKey": {"path": ["bronze", "vicgas", "raw"]},
                            "groupName": "gas_raw",
                            "isMaterializable": True,
                            "dependencyKeys": [
                                {
                                    "path": [
                                        "bronze",
                                        "vicgas",
                                        "bronze_nemweb_public_files_vicgas",
                                    ]
                                }
                            ],
                        },
                        {
                            "assetKey": {
                                "path": [
                                    "bronze",
                                    "gbb",
                                    "bronze_nemweb_public_files_gbb",
                                ]
                            },
                            "groupName": "gas_raw",
                            "isMaterializable": True,
                            "dependencyKeys": [],
                        },
                        {
                            "assetKey": {
                                "path": [
                                    "bronze",
                                    "vicgas",
                                    "bronze_nemweb_public_files_vicgas",
                                ]
                            },
                            "groupName": "gas_raw",
                            "isMaterializable": True,
                            "dependencyKeys": [],
                        },
                    ]
                }
            if "activeRuns: runsOrError" in query:
                self.status_checks += 1
                return {
                    "activeRuns": {"__typename": "Runs", "results": []},
                    "failedRuns": {"__typename": "Runs", "results": []},
                    "allRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": f"run-{self.status_checks}",
                                "jobName": "__ASSET_JOB",
                                "status": "SUCCESS",
                            }
                        ],
                    },
                }
            assert "launchRun" in query
            assert timeout_seconds == module["DAGSTER_LAUNCH_RUN_TIMEOUT_SECONDS"]
            assert variables is not None
            execution_params = variables["executionParams"]
            assert isinstance(execution_params, Mapping)
            self.execution_params.append(execution_params)
            return {
                "launchRun": {
                    "__typename": "LaunchRunSuccess",
                    "run": {"runId": "run-1", "status": "QUEUED"},
                }
            }

    class FakeRunner:
        """Return no failed asset checks for dependency wave waits."""

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            assert args[:3] == ["podman", "exec", "aemo-etl-e2e-postgres"]
            return subprocess.CompletedProcess(args, 0, stdout="[]\n", stderr="")

    client = FakeClient()

    launch_result = launch_assets(
        client,
        selector_class("repo", "aemo-etl"),
        run_id="e2e",
        started_after=100.0,
        timeout_seconds=1200,
        runner=FakeRunner(),
    )

    assert getattr(launch_result, "run_ids") == ("run-1", "run-1", "run-1", "run-1")
    assert client.status_checks == 3
    selectors: list[Mapping[str, object]] = []
    for params in client.execution_params:
        selector = params["selector"]
        assert isinstance(selector, Mapping)
        assert selector["pipelineName"] == "__ASSET_JOB"
        assert params["runConfigData"] == module["PROMOTION_ASSET_RUN_CONFIG"]
        selectors.append(selector)
    assert [selector["assetSelection"] for selector in selectors] == [
        [
            {"path": ["bronze", "gbb", "raw_0"]},
            {"path": ["bronze", "gbb", "raw_1"]},
            {"path": ["bronze", "gbb", "raw_2"]},
            {"path": ["bronze", "gbb", "raw_3"]},
        ],
        [
            {"path": ["bronze", "gbb", "raw_4"]},
            {"path": ["bronze", "vicgas", "raw"]},
        ],
        [
            {"path": ["silver", "gbb", "upstream"]},
            {"path": ["silver", "vicgas", "upstream"]},
        ],
        [{"path": ["silver", "gas_model", "target"]}],
    ]
    assert getattr(launch_result, "scenario_evidence") == {
        "scenario": "promotion-gas-model",
        "launch_mode": "direct-upstream-asset-launch",
        "target_group": "gas_model",
        "target_asset_count": 1,
        "selected_upstream_closure_count": 9,
        "skipped_live_source_asset_keys": [
            "bronze/gbb/bronze_nemweb_public_files_gbb",
            "bronze/vicgas/bronze_nemweb_public_files_vicgas",
        ],
        "wave_count": 3,
        "batch_count": 4,
        "asset_batch_size": 4,
    }


def test_asset_launch_timeout_propagates_without_retry() -> None:
    """A launch timeout fails without retrying the non-idempotent mutation."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    launch_dagster_run = get_callable(module, "launch_dagster_run")
    command_error = get_exception_class(module, "CommandError")

    class FakeClient:
        """Raise one launch transport timeout."""

        def __init__(self) -> None:
            self.launch_attempts = 0

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            assert "launchRun" in query
            assert variables is not None
            assert timeout_seconds == module["DAGSTER_LAUNCH_RUN_TIMEOUT_SECONDS"]
            self.launch_attempts += 1
            raise command_error(
                "Dagster GraphQL request failed at http://127.0.0.1:3001/graphql: timed out"
            )

    client = FakeClient()

    try:
        launch_dagster_run(
            client,
            selector_class("repo", "aemo-etl"),
            pipeline_name="__ASSET_JOB",
            run_id="e2e",
            asset_keys=(("silver", "gas_model", "target"),),
        )
    except command_error as error:
        assert "timed out" in str(error)
    else:
        raise AssertionError("launch timeout did not fail")

    assert client.launch_attempts == 1


def test_dataflow_status_fails_warn_level_asset_checks() -> None:
    """WARN-level failed checks still fail the End-to-end dataflow monitor."""
    module = load_e2e_command_module()
    evaluate_dagster_dataflow_status = get_callable(
        module,
        "evaluate_dagster_dataflow_status",
    )

    status = evaluate_dagster_dataflow_status(
        active_runs=[],
        failed_runs=[],
        target_assets=[
            {
                "assetKey": {"path": ["silver", "gas_model", "target"]},
                "isMaterializable": True,
                "assetMaterializations": [{"runId": "run-target", "timestamp": 200.0}],
                "assetEventHistory": {"results": []},
                "assetChecksOrError": {
                    "__typename": "AssetChecks",
                    "checks": [],
                },
            }
        ],
        target_asset_events=[],
        checked_assets=[
            {
                "assetKey": {"path": ["bronze", "vicgas", "raw"]},
                "assetChecksOrError": {
                    "__typename": "AssetChecks",
                    "checks": [
                        {
                            "name": "check_skipped_s3_keys",
                            "executionForLatestMaterialization": {
                                "runId": "run-raw",
                                "status": "FAILED",
                                "timestamp": 201.0,
                                "evaluation": {
                                    "success": False,
                                    "severity": "WARN",
                                },
                            },
                        }
                    ],
                },
            }
        ],
        started_after=100.0,
    )

    assert status.failed_asset_checks == (
        "bronze/vicgas/raw:check_skipped_s3_keys=FAILED/WARN",
    )


def test_postgres_asset_check_rows_are_failed_check_labels() -> None:
    """Dagster DB check rows keep the same failed-check label contract."""
    module = load_e2e_command_module()
    format_failed_asset_check_row = get_callable(
        module,
        "format_failed_asset_check_row",
    )

    label = format_failed_asset_check_row(
        {
            "asset_key": '["silver", "gas_model", "target"]',
            "check_name": "check_required_fields",
            "execution_status": "FAILED",
            "evaluation_event": {
                "dagster_event": {
                    "event_specific_data": {
                        "success": False,
                        "severity": {"__enum__": "AssetCheckSeverity.ERROR"},
                    }
                }
            },
        }
    )

    assert label == "silver/gas_model/target:check_required_fields=FAILED/ERROR"


def test_dataflow_failure_waits_for_active_runs_before_failing_checks() -> None:
    """Transient failed checks can clear while related Dagster runs are active."""
    module = load_e2e_command_module()
    status_class = get_callable(module, "DagsterDataflowStatus")
    dagster_dataflow_failure_summary = get_callable(
        module,
        "dagster_dataflow_failure_summary",
    )

    active_status = status_class(
        active_runs=("run-active(job=STARTED)",),
        failed_runs=(),
        materialized_target_assets=("silver/gas_model/target",),
        missing_target_assets=(),
        failed_target_assets=(),
        missing_asset_checks=(),
        failed_asset_checks=("bronze/vicgas/raw:check_skipped_s3_keys=FAILED/WARN",),
    )
    terminal_status = status_class(
        active_runs=(),
        failed_runs=(),
        materialized_target_assets=("silver/gas_model/target",),
        missing_target_assets=(),
        failed_target_assets=(),
        missing_asset_checks=(),
        failed_asset_checks=("bronze/vicgas/raw:check_skipped_s3_keys=FAILED/WARN",),
    )

    assert dagster_dataflow_failure_summary(active_status) is None
    assert (
        dagster_dataflow_failure_summary(terminal_status)
        == "failed asset checks: bronze/vicgas/raw:check_skipped_s3_keys=FAILED/WARN"
    )


def test_dataflow_telemetry_aggregates_monitor_status_samples() -> None:
    """Monitor samples produce peak, final, target, and check telemetry."""
    module = load_e2e_command_module()
    status_class = get_callable(module, "DagsterDataflowStatus")
    telemetry_class = get_callable(module, "DagsterDataflowTelemetry")
    telemetry = telemetry_class()

    telemetry.record_status_sample(
        status_class(
            active_runs=("queued-1(job=QUEUED)", "started-1(job=STARTED)"),
            failed_runs=(),
            materialized_target_assets=("silver/gas_model/a",),
            missing_target_assets=("silver/gas_model/b", "silver/gas_model/c"),
            failed_target_assets=(),
            missing_asset_checks=(),
            failed_asset_checks=(),
            run_status_counts={"QUEUED": 2, "STARTED": 1, "SUCCESS": 1},
            target_materialization_timestamps=(1_700_000_060.0,),
        )
    )
    telemetry.record_status_sample(
        status_class(
            active_runs=(
                "queued-2(job=QUEUED)",
                "not-started(job=NOT_STARTED)",
                "starting(job=STARTING)",
                "started-2(job=STARTED)",
                "started-3(job=STARTED)",
            ),
            failed_runs=("failed(job=FAILURE)",),
            materialized_target_assets=("silver/gas_model/a", "silver/gas_model/b"),
            missing_target_assets=("silver/gas_model/c",),
            failed_target_assets=("silver/gas_model/c (failed)",),
            missing_asset_checks=(),
            failed_asset_checks=(
                "silver/gas_model/b:check_required_fields=FAILED/ERROR",
            ),
            run_status_counts={
                "FAILURE": 1,
                "NOT_STARTED": 1,
                "QUEUED": 1,
                "STARTED": 2,
                "STARTING": 1,
                "SUCCESS": 4,
            },
            target_materialization_timestamps=(
                1_700_000_000.0,
                1_700_000_120.0,
            ),
        )
    )

    payload = telemetry.to_manifest()

    assert payload["sample_count"] == 2
    assert payload["peak_active_run_count"] == 4
    assert payload["peak_queued_run_count"] == 2
    assert payload["final_run_status_counts"] == {
        "FAILURE": 1,
        "NOT_STARTED": 1,
        "QUEUED": 1,
        "STARTED": 2,
        "STARTING": 1,
        "SUCCESS": 4,
    }
    assert payload["final_target_progress"] == {
        "materialized_target_asset_count": 2,
        "target_asset_count": 3,
        "missing_target_asset_count": 1,
        "failed_target_asset_count": 1,
    }
    assert payload["first_target_materialization_at"] == "2023-11-14T22:13:20+00:00"
    assert payload["last_target_materialization_at"] == "2023-11-14T22:15:20+00:00"
    assert payload["final_missing_asset_check_count"] == 0
    assert payload["final_failed_asset_check_count"] == 1


def test_run_wave_wait_records_peak_run_telemetry() -> None:
    """Dependency-wave samples contribute to the budget report telemetry."""
    module = load_e2e_command_module()
    wait_for_dagster_run_wave = get_callable(module, "wait_for_dagster_run_wave")
    telemetry_class = get_callable(module, "DagsterDataflowTelemetry")

    class FakeClient:
        """Return one active wave sample and one drained wave sample."""

        def __init__(self) -> None:
            self.status_checks = 0

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            del variables
            assert timeout_seconds == module["DAGSTER_DATAFLOW_STATUS_TIMEOUT_SECONDS"]
            assert "activeRuns: runsOrError" in query
            self.status_checks += 1
            if self.status_checks == 1:
                return {
                    "activeRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-started",
                                "jobName": "__ASSET_JOB",
                                "status": "STARTED",
                            },
                            {
                                "runId": "run-starting",
                                "jobName": "__ASSET_JOB",
                                "status": "STARTING",
                            },
                            {
                                "runId": "run-queued",
                                "jobName": "__ASSET_JOB",
                                "status": "QUEUED",
                            },
                        ],
                    },
                    "failedRuns": {"__typename": "Runs", "results": []},
                    "allRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-started",
                                "jobName": "__ASSET_JOB",
                                "status": "STARTED",
                            },
                            {
                                "runId": "run-starting",
                                "jobName": "__ASSET_JOB",
                                "status": "STARTING",
                            },
                            {
                                "runId": "run-queued-1",
                                "jobName": "__ASSET_JOB",
                                "status": "QUEUED",
                            },
                            {
                                "runId": "run-queued-2",
                                "jobName": "__ASSET_JOB",
                                "status": "QUEUED",
                            },
                            {
                                "runId": "run-queued-3",
                                "jobName": "__ASSET_JOB",
                                "status": "QUEUED",
                            },
                        ],
                    },
                }
            return {
                "activeRuns": {"__typename": "Runs", "results": []},
                "failedRuns": {"__typename": "Runs", "results": []},
                "allRuns": {
                    "__typename": "Runs",
                    "results": [
                        {
                            "runId": f"run-success-{index}",
                            "jobName": "__ASSET_JOB",
                            "status": "SUCCESS",
                        }
                        for index in range(5)
                    ],
                },
            }

    class FakeRunner:
        """Return no failed asset checks after the wave drains."""

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, capture_output, check
            assert args[:3] == ["podman", "exec", "aemo-etl-e2e-postgres"]
            return subprocess.CompletedProcess(args, 0, stdout="[]\n", stderr="")

    telemetry = telemetry_class()

    wait_for_dagster_run_wave(
        FakeClient(),
        started_after=100.0,
        timeout_seconds=30,
        runner=FakeRunner(),
        poll_interval_seconds=0,
        telemetry=telemetry,
    )

    payload = telemetry.to_manifest()
    assert payload["sample_count"] == 2
    assert payload["peak_active_run_count"] == 2
    assert payload["peak_queued_run_count"] == 3
    assert payload["final_run_status_counts"] == {"SUCCESS": 5}


def test_gate_run_telemetry_manifest_records_durations() -> None:
    """Gate telemetry reports total, stack, monitor, and cleanup durations."""
    module = load_e2e_command_module()
    telemetry_class = get_callable(module, "GateRunTelemetry")
    telemetry = telemetry_class(started_monotonic=100.0)

    telemetry.record_stack_startup(101.0, 103.25)
    telemetry.record_dagster_dataflow_monitor(104.0, 109.5)
    telemetry.record_cleanup("post-success", 109.5, 110.75)
    telemetry.completed_monotonic = 112.0

    payload = telemetry.to_manifest()

    assert payload["total_gate_duration_seconds"] == 12.0
    assert payload["stack_startup_duration_seconds"] == 2.25
    assert payload["dagster_dataflow_monitor_duration_seconds"] == 5.5
    assert payload["cleanup_duration_seconds"] == 1.25
    assert payload["cleanup_phases"] == [
        {
            "phase": "post-success",
            "duration_seconds": 1.25,
            "status": "completed",
        }
    ]


def test_e2e_promotion_regression_budgets_pass_for_approved_baseline() -> None:
    """The Promotion guard budgets pass for the approved targeted baseline."""
    module = load_e2e_command_module()
    format_e2e_budget_report = get_callable(module, "format_e2e_budget_report")
    e2e_budget_failures = get_callable(module, "e2e_budget_failures")
    e2e_regression_budgets_for_scenario = get_callable(
        module,
        "e2e_regression_budgets_for_scenario",
    )
    budgets = e2e_regression_budgets_for_scenario("promotion-gas-model")

    report = format_e2e_budget_report(
        {
            "total_gate_duration_seconds": 475.152,
            "dagster_dataflow": {
                "peak_active_run_count": 6,
                "peak_queued_run_count": 0,
                "final_run_status_counts": {"SUCCESS": 48},
                "final_target_progress": {
                    "materialized_target_asset_count": 29,
                    "target_asset_count": 29,
                    "missing_target_asset_count": 0,
                    "failed_target_asset_count": 0,
                },
                "final_missing_asset_check_count": 0,
                "final_failed_asset_check_count": 0,
            },
        },
        manifest_path=Path("/tmp/run-manifest.json"),
        budgets=budgets,
    )

    assert (
        e2e_budget_failures(
            {
                "total_gate_duration_seconds": 475.152,
                "dagster_dataflow": {
                    "peak_active_run_count": 6,
                    "peak_queued_run_count": 0,
                    "final_run_status_counts": {"SUCCESS": 48},
                    "final_target_progress": {
                        "materialized_target_asset_count": 29,
                        "target_asset_count": 29,
                        "missing_target_asset_count": 0,
                        "failed_target_asset_count": 0,
                    },
                    "final_missing_asset_check_count": 0,
                    "final_failed_asset_check_count": 0,
                },
            },
            budgets,
        )
        == ()
    )
    assert "E2E Promotion guard regression budgets (passed):" in report
    assert "run manifest: /tmp/run-manifest.json" in report
    assert "7m55s; threshold <= 20m00s" in report
    assert "total Dagster runs: observed 48; threshold <= 48" in report
    assert "target progress: observed 29/29 materialized" in report
    assert "failed target asset checks: observed 0; threshold <= 0" in report


def test_e2e_promotion_regression_budgets_fail_duration_and_run_counts() -> None:
    """Duration and run-count regressions fail the Promotion guard budgets."""
    module = load_e2e_command_module()
    format_e2e_budget_report = get_callable(module, "format_e2e_budget_report")
    e2e_budget_failures = get_callable(module, "e2e_budget_failures")
    e2e_regression_budgets_for_scenario = get_callable(
        module,
        "e2e_regression_budgets_for_scenario",
    )
    budgets = e2e_regression_budgets_for_scenario("promotion-gas-model")
    telemetry = {
        "total_gate_duration_seconds": 20 * 60 + 1,
        "dagster_dataflow": {
            "peak_active_run_count": 7,
            "peak_queued_run_count": 7,
            "final_run_status_counts": {"SUCCESS": 49},
            "final_target_progress": {
                "materialized_target_asset_count": 29,
                "target_asset_count": 29,
                "missing_target_asset_count": 0,
                "failed_target_asset_count": 0,
            },
            "final_missing_asset_check_count": 0,
            "final_failed_asset_check_count": 0,
        },
    }

    report = format_e2e_budget_report(
        telemetry,
        manifest_path=Path("/tmp/run-manifest.json"),
        budgets=budgets,
    )
    failures = e2e_budget_failures(telemetry, budgets)

    assert "E2E Promotion guard regression budgets (failed):" in report
    assert "total gate duration observed 20m01s; threshold <= 20m00s" in failures
    assert "peak active runs observed 7; threshold <= 6" in failures
    assert "peak queued runs observed 7; threshold <= 6" in failures
    assert "total Dagster runs observed 49; threshold <= 48" in failures
    assert "total gate duration observed 20m01s; threshold <= 20m00s" in report
    assert "total Dagster runs observed 49; threshold <= 48" in report


def test_e2e_promotion_regression_budget_enforcement_fails_command(
    tmp_path: Path,
) -> None:
    """Promotion budget failures mark the manifest failed and raise CommandError."""
    module = load_e2e_command_module()
    enforce_budgets = get_callable(module, "enforce_e2e_regression_budgets_for_run")
    run_options_class = get_callable(module, "RunOptions")
    status_class = get_callable(module, "DagsterDataflowStatus")
    telemetry_class = get_callable(module, "GateRunTelemetry")
    dataflow_telemetry_class = get_callable(module, "DagsterDataflowTelemetry")
    command_error = get_exception_class(module, "CommandError")
    manifest_path = tmp_path / "run-manifest.json"
    telemetry = telemetry_class(started_monotonic=0.0, completed_monotonic=1201.0)
    dataflow_telemetry = dataflow_telemetry_class()
    dataflow_telemetry.record_status_sample(
        status_class(
            active_runs=(),
            failed_runs=(),
            materialized_target_assets=tuple(
                f"silver/gas_model/asset_{index}" for index in range(29)
            ),
            missing_target_assets=(),
            failed_target_assets=(),
            missing_asset_checks=(),
            failed_asset_checks=(),
            run_status_counts={"SUCCESS": 49},
        )
    )
    telemetry.dataflow = dataflow_telemetry
    manifest: dict[str, object] = {"status": "running"}
    options = run_options_class(
        scenario="promotion-gas-model",
        launch_mode="direct-upstream-asset-launch",
        rebuild=False,
        reuse=False,
        always_clean=False,
        seed_root=None,
        webserver_port=3001,
        raw_latest_count=1,
        zip_latest_count=1,
        timeout_seconds=1200,
        max_concurrent_runs=6,
    )

    with pytest.raises(command_error) as caught:
        enforce_budgets(
            telemetry=telemetry,
            manifest=manifest,
            manifest_path=manifest_path,
            options=options,
        )

    assert "E2E Promotion guard regression budget failed" in str(caught.value)
    assert str(manifest_path) in str(caught.value)
    written_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert written_manifest["status"] == "failed"
    assert written_manifest["budget"]["status"] == "failed"
    assert written_manifest["budget"]["run_manifest"] == str(manifest_path)


def test_e2e_promotion_regression_budgets_fail_coverage_contract() -> None:
    """Target progress and final asset-check drift fail the Promotion budgets."""
    module = load_e2e_command_module()
    e2e_budget_failures = get_callable(module, "e2e_budget_failures")
    e2e_regression_budgets_for_scenario = get_callable(
        module,
        "e2e_regression_budgets_for_scenario",
    )
    budgets = e2e_regression_budgets_for_scenario("promotion-gas-model")

    failures = e2e_budget_failures(
        {
            "total_gate_duration_seconds": 600,
            "dagster_dataflow": {
                "peak_active_run_count": 6,
                "peak_queued_run_count": 0,
                "final_run_status_counts": {"SUCCESS": 48},
                "final_target_progress": {
                    "materialized_target_asset_count": 28,
                    "target_asset_count": 29,
                    "missing_target_asset_count": 1,
                    "failed_target_asset_count": 0,
                },
                "final_missing_asset_check_count": 1,
                "final_failed_asset_check_count": 1,
            },
        },
        budgets,
    )

    assert (
        "target progress observed 28/29 materialized; required 29/29 materialized"
        in failures
    )
    assert "missing target assets observed 1; threshold <= 0" in failures
    assert "missing target asset checks observed 1; threshold <= 0" in failures
    assert "failed target asset checks observed 1; threshold <= 0" in failures


def test_e2e_promotion_regression_budgets_fail_missing_telemetry() -> None:
    """Missing telemetry produces actionable Promotion budget failures."""
    module = load_e2e_command_module()
    format_e2e_budget_report = get_callable(module, "format_e2e_budget_report")
    e2e_budget_failures = get_callable(module, "e2e_budget_failures")
    e2e_regression_budgets_for_scenario = get_callable(
        module,
        "e2e_regression_budgets_for_scenario",
    )
    budgets = e2e_regression_budgets_for_scenario("promotion-gas-model")

    report = format_e2e_budget_report(
        {},
        manifest_path=Path("/tmp/run-manifest.json"),
        budgets=budgets,
    )
    failures = e2e_budget_failures({}, budgets)

    assert "run manifest: /tmp/run-manifest.json" in report
    assert "total gate duration unavailable; threshold <= 20m00s" in failures
    assert "peak active runs unavailable; threshold <= 6" in failures
    assert "target progress unavailable; required 29/29 materialized" in failures
    assert "failed target asset checks unavailable; threshold <= 0" in failures
    assert "total gate duration unavailable; threshold <= 20m00s" in report


def test_monitor_records_telemetry_before_failed_run_error() -> None:
    """Failed monitor samples are retained for the run manifest."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    monitor_dagster_dataflow = get_callable(module, "monitor_dagster_dataflow")
    telemetry_class = get_callable(module, "DagsterDataflowTelemetry")
    command_error = get_exception_class(module, "CommandError")

    class FakeClient:
        """Return one failed Dagster run monitor sample."""

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            del variables, timeout_seconds
            if "E2EDataflowRunStatus" in query:
                failed_run = {
                    "runId": "failed-run",
                    "jobName": "gasbb_facilities_job",
                    "status": "FAILURE",
                }
                return {
                    "activeRuns": {"__typename": "Runs", "results": []},
                    "failedRuns": {
                        "__typename": "Runs",
                        "results": [failed_run],
                    },
                    "allRuns": {"__typename": "Runs", "results": [failed_run]},
                }
            assert "E2EDataflowTargetStatus" in query
            return {
                "targetAssets": [],
                "targetAssetEvents": {"__typename": "AssetConnection", "nodes": []},
            }

    telemetry = telemetry_class()

    with pytest.raises(command_error) as caught:
        monitor_dagster_dataflow(
            FakeClient(),
            selector_class("repo", "aemo-etl"),
            started_after=100.0,
            timeout_seconds=30,
            poll_interval_seconds=1,
            telemetry=telemetry,
        )

    assert "Dagster dataflow failed: failed runs" in str(caught.value)
    assert telemetry.to_manifest()["sample_count"] == 1
    assert telemetry.to_manifest()["final_run_status_counts"] == {"FAILURE": 1}


def test_dataflow_status_fails_target_materialization_failure() -> None:
    """Failed target materialization events fail the End-to-end dataflow monitor."""
    module = load_e2e_command_module()
    evaluate_dagster_dataflow_status = get_callable(
        module,
        "evaluate_dagster_dataflow_status",
    )

    status = evaluate_dagster_dataflow_status(
        active_runs=[],
        failed_runs=[],
        target_assets=[
            {
                "assetKey": {"path": ["silver", "gas_model", "target"]},
                "isMaterializable": True,
                "assetMaterializations": [{"runId": "run-target", "timestamp": 200.0}],
                "assetChecksOrError": {
                    "__typename": "AssetChecks",
                    "checks": [],
                },
            }
        ],
        target_asset_events=[
            {
                "key": {"path": ["silver", "gas_model", "target"]},
                "assetEventHistory": {
                    "results": [
                        {
                            "__typename": "FailedToMaterializeEvent",
                            "runId": "run-target",
                            "timestamp": 201.0,
                            "message": "target failed",
                        }
                    ]
                },
            }
        ],
        checked_assets=[],
        started_after=100.0,
    )

    assert status.failed_target_assets == ("silver/gas_model/target (target failed)",)


def test_dataflow_status_reports_missing_target_materialization() -> None:
    """A target asset without a materialization after monitor start is missing."""
    module = load_e2e_command_module()
    evaluate_dagster_dataflow_status = get_callable(
        module,
        "evaluate_dagster_dataflow_status",
    )

    status = evaluate_dagster_dataflow_status(
        active_runs=[],
        failed_runs=[],
        target_assets=[
            {
                "assetKey": {"path": ["silver", "gas_model", "missing"]},
                "isMaterializable": True,
                "assetMaterializations": [],
                "assetEventHistory": {"results": []},
                "assetChecksOrError": {
                    "__typename": "AssetChecks",
                    "checks": [],
                },
            }
        ],
        target_asset_events=[],
        checked_assets=[],
        started_after=100.0,
    )

    assert status.missing_target_assets == ("silver/gas_model/missing",)


def test_dataflow_status_reports_target_progress_while_runs_are_active() -> None:
    """Target/check coverage can succeed while background runs remain active."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    fetch_dagster_dataflow_status = get_callable(
        module,
        "fetch_dagster_dataflow_status",
    )

    class FakeClient:
        """Return active run status, then partial target status."""

        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            del variables, timeout_seconds
            self.queries.append(query)
            assert "E2EDataflowCheckStatus" not in query
            if "E2EDataflowRunStatus" in query:
                return {
                    "activeRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-active",
                                "jobName": "gasbb_facilities_job",
                                "status": "STARTED",
                            }
                        ],
                    },
                    "failedRuns": {"__typename": "Runs", "results": []},
                    "allRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-active",
                                "jobName": "gasbb_facilities_job",
                                "status": "STARTED",
                            },
                            {
                                "runId": "run-done",
                                "jobName": "silver_gas_dim_date_job",
                                "status": "SUCCESS",
                            },
                        ],
                    },
                }
            assert "E2EDataflowTargetStatus" in query
            return {
                "targetAssets": [
                    {
                        "assetKey": {"path": ["silver", "gas_model", "done"]},
                        "isMaterializable": True,
                        "assetMaterializations": [
                            {"runId": "run-target", "timestamp": 200.0}
                        ],
                        "assetChecksOrError": {
                            "__typename": "AssetChecks",
                            "checks": [],
                        },
                    },
                    {
                        "assetKey": {"path": ["silver", "gas_model", "missing"]},
                        "isMaterializable": True,
                        "assetMaterializations": [],
                        "assetChecksOrError": {
                            "__typename": "AssetChecks",
                            "checks": [],
                        },
                    },
                ],
                "targetAssetEvents": {"__typename": "AssetConnection", "nodes": []},
            }

    client = FakeClient()

    status = fetch_dagster_dataflow_status(
        client,
        selector_class("repo", "aemo-etl"),
        started_after=100.0,
    )

    assert status.active_runs == ("run-active(gasbb_facilities_job=STARTED)",)
    assert status.run_status_counts == {"STARTED": 1, "SUCCESS": 1}
    assert status.target_asset_count == 2
    assert status.materialized_target_assets == ("silver/gas_model/done",)
    assert status.missing_target_assets == ("silver/gas_model/missing",)
    assert status.target_materialization_timestamps == (200.0,)
    assert ["E2EDataflowCheckStatus" in query for query in client.queries] == [
        False,
        False,
    ]


def test_dataflow_status_reads_postgres_checks_after_target_materializes() -> None:
    """Failed asset check validation waits for target completion."""
    module = load_e2e_command_module()
    selector_class = get_callable(module, "DagsterRepositorySelector")
    fetch_dagster_dataflow_status = get_callable(
        module,
        "fetch_dagster_dataflow_status",
    )

    class FakeClient:
        """Return active run status, then complete target status."""

        def __init__(self) -> None:
            self.queries: list[str] = []

        def execute(
            self,
            query: str,
            variables: Mapping[str, object] | None = None,
            *,
            timeout_seconds: int | None = None,
        ) -> Mapping[str, object]:
            del variables, timeout_seconds
            self.queries.append(query)
            if "E2EDataflowRunStatus" in query:
                return {
                    "activeRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-active",
                                "jobName": "background_job",
                                "status": "STARTED",
                            }
                        ],
                    },
                    "failedRuns": {"__typename": "Runs", "results": []},
                    "allRuns": {
                        "__typename": "Runs",
                        "results": [
                            {
                                "runId": "run-active",
                                "jobName": "background_job",
                                "status": "STARTED",
                            },
                            {
                                "runId": "run-target",
                                "jobName": "target_job",
                                "status": "SUCCESS",
                            },
                        ],
                    },
                }
            assert "E2EDataflowTargetStatus" in query
            return {
                "targetAssets": [
                    {
                        "assetKey": {"path": ["silver", "gas_model", "target"]},
                        "isMaterializable": True,
                        "assetMaterializations": [
                            {"runId": "run-target", "timestamp": 200.0}
                        ],
                    }
                ],
                "targetAssetEvents": {"__typename": "AssetConnection", "nodes": []},
            }

    class FakeRunner:
        """Return an empty Dagster asset-check failure result."""

        def __init__(self) -> None:
            self.calls: list[list[str]] = []

        def run(
            self,
            args: list[str],
            *,
            cwd: Path | None = None,
            env: Mapping[str, str] | None = None,
            capture_output: bool = False,
            check: bool = True,
        ) -> subprocess.CompletedProcess[str]:
            del cwd, env, check
            self.calls.append(list(args))
            assert capture_output
            return subprocess.CompletedProcess(args, 0, stdout="[]\n", stderr="")

    client = FakeClient()
    runner = FakeRunner()

    status = fetch_dagster_dataflow_status(
        client,
        selector_class("repo", "aemo-etl"),
        started_after=100.0,
        runner=runner,
    )

    assert status.is_successful
    assert status.active_runs == ("run-active(background_job=STARTED)",)
    assert status.run_status_counts == {"STARTED": 1, "SUCCESS": 1}
    assert status.target_materialization_timestamps == (200.0,)
    assert ["E2EDataflowRunStatus" in query for query in client.queries] == [
        True,
        False,
    ]
    assert ["E2EDataflowTargetStatus" in query for query in client.queries] == [
        False,
        True,
    ]
    assert all("E2EDataflowCheckStatus" not in query for query in client.queries)
    assert len(runner.calls) == 1
    assert runner.calls[0][:4] == ["podman", "exec", "aemo-etl-e2e-postgres", "psql"]
