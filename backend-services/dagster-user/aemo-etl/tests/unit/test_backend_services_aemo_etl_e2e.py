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

    args = build_parser().parse_args(["run"])

    assert getattr(args, "raw_latest_count") == 3
    assert getattr(args, "zip_latest_count") == 3
    assert getattr(args, "timeout_seconds") == 90 * 60
    assert getattr(args, "max_concurrent_runs") == 6

    override_args = build_parser().parse_args(
        ["run", "--raw-latest-count", "5", "--zip-latest-count", "2"]
    )
    assert getattr(override_args, "raw_latest_count") == 5
    assert getattr(override_args, "zip_latest_count") == 2


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
    assert "aemo-etl-seed-localstack:" in compose
    assert "depends_on:" not in compose
    assert "dagster-webserver-admin" not in compose
    assert "dagster-webserver-guest" not in compose
    assert "authentication:" not in compose
    assert "marimo:" not in compose
    assert "caddy:" not in compose


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
        rebuild=False,
        reuse=False,
        always_clean=False,
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

    cleanup_stack(runner, compose_command)

    assert ["podman", "rm", "-f", "worker-before"] in runner.calls
    assert [*compose_command, "down", "-v", "--remove-orphans"] in runner.calls
    assert ["podman", "rm", "-f", "worker-after"] in runner.calls
    assert ["podman", "network", "rm", "aemo-etl-e2e-dagster-network"] in runner.calls


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
        ) -> Mapping[str, object]:
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
        selectors.append(selector)

    assert run_ids == ["run-1", "run-2"]
    assert selectors[0]["pipelineName"] == "silver_gas_dim_date_job"
    assert selectors[1]["pipelineName"] == "__ASSET_JOB"
    assert selectors[1]["assetSelection"] == [
        {"path": ["bronze", "metadata", "bronze_table_metadata"]}
    ]


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
    """The monitor reports target progress without querying every asset check."""
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
    assert status.target_asset_count == 2
    assert status.materialized_target_assets == ("silver/gas_model/done",)
    assert status.missing_target_assets == ("silver/gas_model/missing",)
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
