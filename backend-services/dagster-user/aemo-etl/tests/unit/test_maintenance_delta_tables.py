from typing import cast

from dagster import (
    DefaultScheduleStatus,
    Definitions,
    ScheduleDefinition,
    asset,
)
from deltalake.exceptions import TableNotFoundError
from pytest_mock import MockerFixture

from aemo_etl.configs import DAGSTER_URI
from aemo_etl.maintenance.delta_tables import (
    DELTA_MAINTENANCE_COMPACT,
    DELTA_MAINTENANCE_DRY_RUN,
    DELTA_MAINTENANCE_ENABLED,
    DELTA_MAINTENANCE_ENFORCE_RETENTION_DURATION,
    DELTA_MAINTENANCE_RETENTION_HOURS,
    DELTA_MAINTENANCE_VACUUM,
    DELTA_TABLE_VACUUM_CRON_SCHEDULE,
    DELTA_TABLE_VACUUM_JOB_NAME,
    DELTA_TABLE_VACUUM_SCHEDULE_NAME,
    DELTA_TABLE_VACUUM_TIMEZONE,
    FULL_VACUUM_DRY_RUN,
    FULL_VACUUM_ENFORCE_RETENTION_DURATION,
    FULL_VACUUM_RETENTION_HOURS,
    DeltaTableMaintenanceConfig,
    DeltaTableMaintenanceTarget,
    collect_delta_table_maintenance_targets,
    delta_table_maintenance_definitions_factory,
    run_delta_table_maintenance,
)


DEFAULT_CONFIG = DeltaTableMaintenanceConfig(
    enabled=True,
    compact=True,
    vacuum=True,
    retention_hours=0,
    enforce_retention_duration=False,
    dry_run=False,
)


def test_collect_delta_table_maintenance_targets_selects_delta_assets() -> None:
    @asset(
        key_prefix=["bronze", "gbb"],
        name="bronze_delta_table",
        io_manager_key="aemo_deltalake_append_io_manager",
        metadata={DAGSTER_URI: "s3://test-aemo/bronze/gbb/bronze_delta_table"},
    )
    def bronze_delta_table() -> None:
        return None

    @asset(
        key_prefix=["silver", "gbb"],
        name="silver_parquet_table",
        io_manager_key="aemo_parquet_overwrite_io_manager",
        metadata={DAGSTER_URI: "s3://test-aemo/silver/gbb/silver_parquet_table"},
    )
    def silver_parquet_table() -> None:
        return None

    @asset(
        key_prefix=["bronze", "gbb"],
        name="missing_uri",
        io_manager_key="aemo_deltalake_append_io_manager",
    )
    def missing_uri() -> None:
        return None

    targets = collect_delta_table_maintenance_targets(
        Definitions(
            assets=[
                bronze_delta_table,
                silver_parquet_table,
                missing_uri,
            ]
        )
    )

    assert targets == (
        DeltaTableMaintenanceTarget(
            asset_key="bronze/gbb/bronze_delta_table",
            table_uri="s3://test-aemo/bronze/gbb/bronze_delta_table",
            config=DEFAULT_CONFIG,
        ),
    )


def test_collect_delta_table_maintenance_targets_reads_per_asset_metadata() -> None:
    @asset(
        key_prefix=["bronze", "gbb"],
        name="configured_delta_table",
        io_manager_key="aemo_deltalake_append_io_manager",
        metadata={
            DAGSTER_URI: "s3://test-aemo/bronze/gbb/configured_delta_table",
            DELTA_MAINTENANCE_ENABLED: True,
            DELTA_MAINTENANCE_COMPACT: False,
            DELTA_MAINTENANCE_VACUUM: True,
            DELTA_MAINTENANCE_RETENTION_HOURS: 168,
            DELTA_MAINTENANCE_ENFORCE_RETENTION_DURATION: True,
            DELTA_MAINTENANCE_DRY_RUN: True,
        },
    )
    def configured_delta_table() -> None:
        return None

    targets = collect_delta_table_maintenance_targets(
        Definitions(assets=[configured_delta_table])
    )

    assert targets == (
        DeltaTableMaintenanceTarget(
            asset_key="bronze/gbb/configured_delta_table",
            table_uri="s3://test-aemo/bronze/gbb/configured_delta_table",
            config=DeltaTableMaintenanceConfig(
                enabled=True,
                compact=False,
                vacuum=True,
                retention_hours=168,
                enforce_retention_duration=True,
                dry_run=True,
            ),
        ),
    )


def test_collect_delta_table_maintenance_targets_rejects_invalid_bool_metadata() -> (
    None
):
    @asset(
        key_prefix=["bronze", "gbb"],
        name="configured_delta_table",
        io_manager_key="aemo_deltalake_append_io_manager",
        metadata={
            DAGSTER_URI: "s3://test-aemo/bronze/gbb/configured_delta_table",
            DELTA_MAINTENANCE_ENABLED: "true",
        },
    )
    def configured_delta_table() -> None:
        return None

    try:
        collect_delta_table_maintenance_targets(
            Definitions(assets=[configured_delta_table])
        )
    except ValueError as error:
        assert (
            str(error) == "bronze/gbb/configured_delta_table metadata "
            "delta_maintenance/enabled must be bool, got str"
        )
    else:
        raise AssertionError("expected invalid metadata to raise ValueError")


def test_collect_delta_table_maintenance_targets_rejects_invalid_retention_metadata() -> (
    None
):
    @asset(
        key_prefix=["bronze", "gbb"],
        name="configured_delta_table",
        io_manager_key="aemo_deltalake_append_io_manager",
        metadata={
            DAGSTER_URI: "s3://test-aemo/bronze/gbb/configured_delta_table",
            DELTA_MAINTENANCE_RETENTION_HOURS: -1,
        },
    )
    def configured_delta_table() -> None:
        return None

    try:
        collect_delta_table_maintenance_targets(
            Definitions(assets=[configured_delta_table])
        )
    except ValueError as error:
        assert (
            str(error) == "bronze/gbb/configured_delta_table metadata "
            "delta_maintenance/retention_hours must be greater than or equal to 0"
        )
    else:
        raise AssertionError("expected invalid metadata to raise ValueError")


def test_collect_delta_table_maintenance_targets_rejects_retention_metadata_type() -> (
    None
):
    @asset(
        key_prefix=["bronze", "gbb"],
        name="configured_delta_table",
        io_manager_key="aemo_deltalake_append_io_manager",
        metadata={
            DAGSTER_URI: "s3://test-aemo/bronze/gbb/configured_delta_table",
            DELTA_MAINTENANCE_RETENTION_HOURS: "168",
        },
    )
    def configured_delta_table() -> None:
        return None

    try:
        collect_delta_table_maintenance_targets(
            Definitions(assets=[configured_delta_table])
        )
    except ValueError as error:
        assert (
            str(error) == "bronze/gbb/configured_delta_table metadata "
            "delta_maintenance/retention_hours must be int, got str"
        )
    else:
        raise AssertionError("expected invalid metadata to raise ValueError")


def test_collect_delta_table_maintenance_targets_ignores_non_asset_definitions(
    mocker: MockerFixture,
) -> None:
    definitions = cast(Definitions, mocker.MagicMock())
    definitions.assets = [object()]

    assert collect_delta_table_maintenance_targets(definitions) == ()


def test_run_delta_table_maintenance_compacts_and_full_vacuums(
    mocker: MockerFixture,
) -> None:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    delta_table = mocker.MagicMock()
    delta_table.optimize.compact.return_value = {"numFilesAdded": 1}
    delta_table.vacuum.return_value = ["s3://test-aemo/old-file.parquet"]
    delta_table_constructor = mocker.patch(
        "aemo_etl.maintenance.delta_tables.DeltaTable",
        return_value=delta_table,
    )

    run_delta_table_maintenance(
        context,
        targets=(
            DeltaTableMaintenanceTarget(
                asset_key="bronze/gbb/bronze_delta_table",
                table_uri="s3://test-aemo/bronze/gbb/bronze_delta_table",
                config=DEFAULT_CONFIG,
            ),
        ),
    )

    delta_table_constructor.assert_called_once_with(
        "s3://test-aemo/bronze/gbb/bronze_delta_table"
    )
    delta_table.optimize.compact.assert_called_once_with()
    delta_table.vacuum.assert_called_once_with(
        retention_hours=FULL_VACUUM_RETENTION_HOURS,
        enforce_retention_duration=FULL_VACUUM_ENFORCE_RETENTION_DURATION,
        dry_run=FULL_VACUUM_DRY_RUN,
    )
    context.add_output_metadata.assert_called_once()
    metadata = context.add_output_metadata.call_args.args[0]
    assert metadata["target_count"] == 1
    assert metadata["processed_count"] == 1
    assert metadata["skipped_count"] == 0


def test_run_delta_table_maintenance_skips_missing_tables(
    mocker: MockerFixture,
) -> None:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    mocker.patch(
        "aemo_etl.maintenance.delta_tables.DeltaTable",
        side_effect=TableNotFoundError("missing"),
    )

    run_delta_table_maintenance(
        context,
        targets=(
            DeltaTableMaintenanceTarget(
                asset_key="bronze/gbb/missing",
                table_uri="s3://test-aemo/bronze/gbb/missing",
                config=DEFAULT_CONFIG,
            ),
        ),
    )

    metadata = context.add_output_metadata.call_args.args[0]
    assert metadata["target_count"] == 1
    assert metadata["processed_count"] == 0
    assert metadata["skipped_count"] == 1


def test_run_delta_table_maintenance_skips_disabled_targets(
    mocker: MockerFixture,
) -> None:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    delta_table_constructor = mocker.patch(
        "aemo_etl.maintenance.delta_tables.DeltaTable"
    )

    run_delta_table_maintenance(
        context,
        targets=(
            DeltaTableMaintenanceTarget(
                asset_key="bronze/gbb/disabled",
                table_uri="s3://test-aemo/bronze/gbb/disabled",
                config=DeltaTableMaintenanceConfig(
                    enabled=False,
                    compact=True,
                    vacuum=True,
                    retention_hours=0,
                    enforce_retention_duration=False,
                    dry_run=False,
                ),
            ),
        ),
    )

    delta_table_constructor.assert_not_called()
    metadata = context.add_output_metadata.call_args.args[0]
    assert metadata["target_count"] == 1
    assert metadata["processed_count"] == 0
    assert metadata["skipped_count"] == 1


def test_run_delta_table_maintenance_honors_operation_toggles(
    mocker: MockerFixture,
) -> None:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    delta_table = mocker.MagicMock()
    delta_table.vacuum.return_value = ["s3://test-aemo/old-file.parquet"]
    mocker.patch(
        "aemo_etl.maintenance.delta_tables.DeltaTable",
        return_value=delta_table,
    )

    run_delta_table_maintenance(
        context,
        targets=(
            DeltaTableMaintenanceTarget(
                asset_key="bronze/gbb/vacuum_only",
                table_uri="s3://test-aemo/bronze/gbb/vacuum_only",
                config=DeltaTableMaintenanceConfig(
                    enabled=True,
                    compact=False,
                    vacuum=True,
                    retention_hours=168,
                    enforce_retention_duration=True,
                    dry_run=True,
                ),
            ),
        ),
    )

    delta_table.optimize.compact.assert_not_called()
    delta_table.vacuum.assert_called_once_with(
        retention_hours=168,
        enforce_retention_duration=True,
        dry_run=True,
    )


def test_run_delta_table_maintenance_skips_targets_with_no_operations(
    mocker: MockerFixture,
) -> None:
    context = mocker.MagicMock()
    context.log = mocker.MagicMock()
    delta_table_constructor = mocker.patch(
        "aemo_etl.maintenance.delta_tables.DeltaTable"
    )

    run_delta_table_maintenance(
        context,
        targets=(
            DeltaTableMaintenanceTarget(
                asset_key="bronze/gbb/no_operations",
                table_uri="s3://test-aemo/bronze/gbb/no_operations",
                config=DeltaTableMaintenanceConfig(
                    enabled=True,
                    compact=False,
                    vacuum=False,
                    retention_hours=0,
                    enforce_retention_duration=False,
                    dry_run=False,
                ),
            ),
        ),
    )

    delta_table_constructor.assert_not_called()
    metadata = context.add_output_metadata.call_args.args[0]
    assert metadata["target_count"] == 1
    assert metadata["processed_count"] == 0
    assert metadata["skipped_count"] == 1


def test_delta_table_maintenance_definitions_factory_wires_schedule() -> None:
    maintenance_definitions = delta_table_maintenance_definitions_factory(
        Definitions(),
        default_status=DefaultScheduleStatus.STOPPED,
    )

    jobs = list(maintenance_definitions.jobs or [])
    schedules = list(maintenance_definitions.schedules or [])

    assert [job_def.name for job_def in jobs] == [DELTA_TABLE_VACUUM_JOB_NAME]
    assert [schedule.name for schedule in schedules] == [
        DELTA_TABLE_VACUUM_SCHEDULE_NAME
    ]
    schedule = schedules[0]
    assert isinstance(schedule, ScheduleDefinition)
    assert schedule.job.name == DELTA_TABLE_VACUUM_JOB_NAME
    assert schedule.cron_schedule == DELTA_TABLE_VACUUM_CRON_SCHEDULE
    assert schedule.execution_timezone == DELTA_TABLE_VACUUM_TIMEZONE
    assert schedule.default_status == DefaultScheduleStatus.STOPPED


def test_delta_table_vacuum_job_executes_with_no_targets() -> None:
    maintenance_definitions = delta_table_maintenance_definitions_factory(
        Definitions(),
        default_status=DefaultScheduleStatus.STOPPED,
    )

    result = maintenance_definitions.get_job_def(
        DELTA_TABLE_VACUUM_JOB_NAME
    ).execute_in_process()

    assert result.success
