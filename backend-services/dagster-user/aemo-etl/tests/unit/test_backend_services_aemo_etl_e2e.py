"""Unit tests for the backend-services AEMO ETL e2e stack command."""

import runpy
import socket
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, cast


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
    assert "dagster-webserver-admin" not in compose
    assert "dagster-webserver-guest" not in compose
    assert "authentication:" not in compose
    assert "marimo:" not in compose
    assert "caddy:" not in compose


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
