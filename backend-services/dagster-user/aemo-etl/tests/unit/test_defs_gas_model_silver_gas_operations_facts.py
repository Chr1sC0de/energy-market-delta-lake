from datetime import date, datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_date import (
    SOURCE_TABLES as DATE_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_dim_date import (
    defs as date_defs,
)
from aemo_etl.defs.gas_model.silver_gas_dim_date import (
    silver_gas_dim_date,
)
from aemo_etl.defs.gas_model.silver_gas_dim_date import (
    silver_gas_dim_date_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_dim_operational_point import (
    SOURCE_TABLES as OPERATIONAL_POINT_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_dim_operational_point import (
    defs as operational_point_defs,
)
from aemo_etl.defs.gas_model.silver_gas_dim_operational_point import (
    silver_gas_dim_operational_point,
)
from aemo_etl.defs.gas_model.silver_gas_dim_operational_point import (
    silver_gas_dim_operational_point_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_fact_connection_point_flow import (
    SOURCE_TABLES as CONNECTION_POINT_FLOW_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_fact_connection_point_flow import (
    defs as connection_point_flow_defs,
)
from aemo_etl.defs.gas_model.silver_gas_fact_connection_point_flow import (
    silver_gas_fact_connection_point_flow,
)
from aemo_etl.defs.gas_model.silver_gas_fact_connection_point_flow import (
    silver_gas_fact_connection_point_flow_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_fact_facility_flow_storage import (
    SOURCE_TABLES as FACILITY_FLOW_STORAGE_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_fact_facility_flow_storage import (
    defs as facility_flow_storage_defs,
)
from aemo_etl.defs.gas_model.silver_gas_fact_facility_flow_storage import (
    silver_gas_fact_facility_flow_storage,
)
from aemo_etl.defs.gas_model.silver_gas_fact_facility_flow_storage import (
    silver_gas_fact_facility_flow_storage_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_fact_linepack import (
    SOURCE_TABLES as LINEPACK_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_fact_linepack import (
    defs as linepack_defs,
)
from aemo_etl.defs.gas_model.silver_gas_fact_linepack import (
    silver_gas_fact_linepack,
)
from aemo_etl.defs.gas_model.silver_gas_fact_linepack import (
    silver_gas_fact_linepack_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_fact_nomination_forecast import (
    SOURCE_TABLES as NOMINATION_FORECAST_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_fact_nomination_forecast import (
    defs as nomination_forecast_defs,
)
from aemo_etl.defs.gas_model.silver_gas_fact_nomination_forecast import (
    silver_gas_fact_nomination_forecast,
)
from aemo_etl.defs.gas_model.silver_gas_fact_nomination_forecast import (
    silver_gas_fact_nomination_forecast_required_fields,
)
from aemo_etl.defs.gas_model.silver_gas_fact_operational_meter_flow import (
    SOURCE_TABLES as OPERATIONAL_METER_FLOW_SOURCE_TABLES,
)
from aemo_etl.defs.gas_model.silver_gas_fact_operational_meter_flow import (
    defs as operational_meter_flow_defs,
)
from aemo_etl.defs.gas_model.silver_gas_fact_operational_meter_flow import (
    silver_gas_fact_operational_meter_flow,
)
from aemo_etl.defs.gas_model.silver_gas_fact_operational_meter_flow import (
    silver_gas_fact_operational_meter_flow_required_fields,
)


def _ingested() -> datetime:
    return datetime(2024, 1, 2, tzinfo=timezone.utc)


def _dates() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["date-2024-01-01", "date-2024-01-02"],
            "gas_date": [date(2024, 1, 1), date(2024, 1, 2)],
        }
    )


def _facilities() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["facility-10"],
            "source_system": ["GBB"],
            "source_facility_id": ["10"],
        }
    )


def _locations() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["location-20"],
            "source_system": ["GBB"],
            "source_location_id": ["20"],
        }
    )


def _connection_points() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["connection-point-30"],
            "zone_key": ["zone-1"],
            "source_system": ["GBB"],
            "source_facility_id": ["10"],
            "source_connection_point_id": ["30"],
            "flow_direction": ["RECEIPT"],
        }
    )


def _operational_points() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["op-meter", "op-mirn"],
            "source_system": ["VICGAS", "VICGAS"],
            "point_type": ["direction_code_name", "phy_mirn"],
            "source_point_id": ["METER-A", "MIRN-1"],
            "zone_key": [None, None],
            "pipeline_segment_key": [None, None],
        }
    )


def _minimal_date_source(column: str, value: str) -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            column: [value],
            "surrogate_key": [f"{column}-source-key"],
            "source_file": [f"s3://archive/{column}.csv"],
            "ingested_timestamp": [_ingested()],
        }
    )


def test_silver_gas_dim_date_transform() -> None:
    fn = silver_gas_dim_date.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            _minimal_date_source("GasDate", "01 Jan 2024"),
            _minimal_date_source("GasDate", "01 Jan 2024"),
            _minimal_date_source("Gasdate", "01 Jan 2024"),
            _minimal_date_source("GasDate", "02 Jan 2024"),
            _minimal_date_source("gas_date", "01 Jan 2024"),
            _minimal_date_source("forecast_date", "01 Jan 2024"),
            _minimal_date_source("commencement_datetime", "02 Jan 2024 06:00:00"),
            _minimal_date_source("gas_date", "01 Jan 2024"),
            _minimal_date_source("gas_date", "01 Jan 2024"),
        ),
    )
    collected = result.value.sort("gas_date").collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected["gas_date"].to_list() == [date(2024, 1, 1), date(2024, 1, 2)]
    assert collected["day_name"].to_list() == ["Monday", "Tuesday"]


def test_silver_gas_dim_operational_point_transform() -> None:
    fn = silver_gas_dim_operational_point.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "direction_code_name": ["METER-A"],
                    "surrogate_key": ["meter-source"],
                    "source_file": ["s3://archive/meter.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            pl.LazyFrame(
                {
                    "phy_mirn": ["MIRN-1"],
                    "site_company": ["Site Co"],
                    "surrogate_key": ["mirn-source"],
                    "source_file": ["s3://archive/alloc.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
        ),
    )
    collected = result.value.sort("point_type").collect()

    assert collected["source_point_id"].to_list() == ["METER-A", "MIRN-1"]
    assert collected["point_type"].to_list() == ["direction_code_name", "phy_mirn"]


def test_silver_gas_fact_connection_point_flow_transform() -> None:
    fn = silver_gas_fact_connection_point_flow.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "GasDate": ["01 Jan 2024"],
                    "FacilityId": [10],
                    "ConnectionPointId": [30],
                    "ActualQuantity": [1.5],
                    "FlowDirection": ["RECEIPT"],
                    "LocationId": [20],
                    "Quality": ["OK"],
                    "LastUpdated": ["01 Jan 2024 12:00:00"],
                    "surrogate_key": ["source-key"],
                    "source_file": ["s3://archive/flow.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            _dates(),
            _facilities(),
            _locations(),
            _connection_points(),
        ),
    )
    row = result.value.collect().row(0, named=True)

    assert row["date_key"] == "date-2024-01-01"
    assert row["facility_key"] == "facility-10"
    assert row["location_key"] == "location-20"
    assert row["connection_point_key"] == "connection-point-30"
    assert row["zone_key"] == "zone-1"
    assert row["actual_quantity_tj"] == 1.5
    assert row["source_surrogate_key"] == "source-key"


def test_silver_gas_fact_facility_flow_storage_transform() -> None:
    fn = silver_gas_fact_facility_flow_storage.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "GasDate": ["01 Jan 2024"],
                    "FacilityId": [10],
                    "LocationId": [20],
                    "Demand": [1.0],
                    "Supply": [2.0],
                    "TransferIn": [3.0],
                    "TransferOut": [4.0],
                    "HeldInStorage": [5.0],
                    "CushionGasStorage": [6.0],
                    "LastUpdated": ["01 Jan 2024 12:00:00"],
                    "surrogate_key": ["source-key"],
                    "source_file": ["s3://archive/storage.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            _dates(),
            _facilities(),
            _locations(),
        ),
    )
    row = result.value.collect().row(0, named=True)

    assert row["date_key"] == "date-2024-01-01"
    assert row["facility_key"] == "facility-10"
    assert row["location_key"] == "location-20"
    assert row["held_in_storage_tj"] == 5.0
    assert row["cushion_gas_storage_tj"] == 6.0


def test_silver_gas_fact_nomination_forecast_transform() -> None:
    fn = silver_gas_fact_nomination_forecast.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "Gasdate": ["01 Jan 2024"],
                    "FacilityId": [10],
                    "LocationId": [20],
                    "Demand": [1.0],
                    "Supply": [2.0],
                    "TransferIn": [3.0],
                    "TransferOut": [4.0],
                    "LastUpdated": ["01 Jan 2024 12:00:00"],
                    "surrogate_key": ["gbb-source"],
                    "source_file": ["s3://archive/gbb-forecast.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            pl.LazyFrame(
                {
                    "gas_date": ["01 Jan 2024"],
                    "dfs_version": [7],
                    "total_demand_forecast": [900],
                    "last_update_datetime": ["01 Jan 2024 06:00:00"],
                    "surrogate_key": ["dfs-source"],
                    "source_file": ["s3://archive/dfs.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            pl.LazyFrame(
                {
                    "forecast_date": ["01 Jan 2024"],
                    "version_id": [8],
                    "ti": [1],
                    "forecast_demand_gj": [1000],
                    "vc_override_gj": [50],
                    "current_date": ["01 Jan 2024 07:00:00"],
                    "surrogate_key": ["int153-source"],
                    "source_file": ["s3://archive/int153.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            _dates(),
            _facilities(),
            _locations(),
        ),
    )
    collected = result.value.sort("source_table").collect()

    assert collected.height == 3
    assert collected["demand_forecast_gj"].to_list() == [1000.0, 900.0, 1000.0]
    assert collected["override_quantity_gj"].drop_nulls().to_list() == [50.0]


def test_silver_gas_fact_linepack_transform() -> None:
    fn = silver_gas_fact_linepack.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "GasDate": ["01 Jan 2024"],
                    "FacilityId": [10],
                    "Flag": ["Green"],
                    "Description": ["Adequate"],
                    "LastUpdated": ["01 Jan 2024 12:00:00"],
                    "surrogate_key": ["gbb-linepack"],
                    "source_file": ["s3://archive/gbb-linepack.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            pl.LazyFrame(
                {
                    "commencement_datetime": ["02 Jan 2024 06:00:00"],
                    "actual_linepack": [123.0],
                    "current_date": ["02 Jan 2024 07:00:00"],
                    "surrogate_key": ["vic-linepack"],
                    "source_file": ["s3://archive/vic-linepack.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            _dates(),
            _facilities(),
        ),
    )
    collected = result.value.sort("source_system").collect()

    assert collected.height == 2
    assert collected["adequacy_flag"].drop_nulls().to_list() == ["Green"]
    assert collected["actual_linepack_gj"].drop_nulls().to_list() == [123.0]


def test_silver_gas_fact_operational_meter_flow_transform() -> None:
    fn = silver_gas_fact_operational_meter_flow.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            pl.LazyFrame(
                {
                    "gas_date": ["01 Jan 2024"],
                    "direction_code_name": ["METER-A"],
                    "direction": ["Withdrawals"],
                    "commencement_datetime": ["01 Jan 2024 06:00:00"],
                    "termination_datetime": ["01 Jan 2024 07:00:00"],
                    "quantity": [10.0],
                    "time_sort_order": [1],
                    "mod_datetime": ["01 Jan 2024 07:05:00"],
                    "surrogate_key": ["meter-source"],
                    "source_file": ["s3://archive/meter.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            pl.LazyFrame(
                {
                    "gas_date": ["02 Jan 2024"],
                    "gas_hour": ["06:00:00"],
                    "site_company": ["Site Co"],
                    "phy_mirn": ["MIRN-1"],
                    "inject_withdraw": ["Injection"],
                    "energy_flow_gj": [20.0],
                    "surrogate_key": ["alloc-source"],
                    "source_file": ["s3://archive/alloc.csv"],
                    "ingested_timestamp": [_ingested()],
                }
            ),
            _dates(),
            _operational_points(),
        ),
    )
    collected = result.value.sort("point_type").collect()

    assert collected.height == 2
    assert collected["operational_point_key"].to_list() == ["op-meter", "op-mirn"]
    assert collected["quantity_gj"].to_list() == [10.0, 20.0]
    assert collected["gas_interval"].to_list() == ["1", "06:00:00"]


def test_new_operations_defs_return_asset_and_checks() -> None:
    definitions_by_table = [
        (
            date_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_dim_date"]),
            DATE_SOURCE_TABLES,
            "gas_model",
        ),
        (
            operational_point_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_dim_operational_point"]),
            OPERATIONAL_POINT_SOURCE_TABLES,
            "gas_model",
        ),
        (
            connection_point_flow_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_fact_connection_point_flow"]),
            CONNECTION_POINT_FLOW_SOURCE_TABLES,
            "gas_model",
        ),
        (
            facility_flow_storage_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_fact_facility_flow_storage"]),
            FACILITY_FLOW_STORAGE_SOURCE_TABLES,
            "gas_model",
        ),
        (
            nomination_forecast_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_fact_nomination_forecast"]),
            NOMINATION_FORECAST_SOURCE_TABLES,
            "gas_model",
        ),
        (
            linepack_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_fact_linepack"]),
            LINEPACK_SOURCE_TABLES,
            "gas_model",
        ),
        (
            operational_meter_flow_defs(),
            AssetKey(["silver", "gas_model", "silver_gas_fact_operational_meter_flow"]),
            OPERATIONAL_METER_FLOW_SOURCE_TABLES,
            "gas_model",
        ),
    ]

    for result, asset_key, source_tables, group_name in definitions_by_table:
        assets = list(result.assets or [])
        asset_checks = list(result.asset_checks or [])
        asset_def = cast(AssetsDefinition, assets[0])

        assert isinstance(result, Definitions)
        assert len(assets) == 1
        assert len(asset_checks) == 4
        assert asset_def.group_names_by_key[asset_key] == group_name
        assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
            ".".join(asset_key.path)
        )
        assert asset_def.metadata_by_key[asset_key]["source_tables"] == source_tables


def test_new_operations_required_field_checks_pass_for_complete_rows() -> None:
    input_df = pl.LazyFrame(
        {
            "surrogate_key": ["key-1"],
            "date_key": ["date-2024-01-01"],
            "source_system": ["GBB"],
            "gas_date": [date(2024, 1, 1)],
            "source_facility_id": ["10"],
            "source_connection_point_id": ["30"],
            "source_location_id": ["20"],
            "flow_direction": ["RECEIPT"],
            "point_type": ["direction_code_name"],
            "source_point_id": ["METER-A"],
        }
    )
    check_functions = [
        silver_gas_dim_date_required_fields,
        silver_gas_dim_operational_point_required_fields,
        silver_gas_fact_connection_point_flow_required_fields,
        silver_gas_fact_facility_flow_storage_required_fields,
        silver_gas_fact_nomination_forecast_required_fields,
        silver_gas_fact_linepack_required_fields,
        silver_gas_fact_operational_meter_flow_required_fields,
    ]

    for check_function in check_functions:
        fn = check_function.op.compute_fn.decorated_fn  # type: ignore[union-attr]
        result = fn(input_df)

        assert result.passed
