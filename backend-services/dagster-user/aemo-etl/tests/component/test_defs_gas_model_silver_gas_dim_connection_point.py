from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_connection_point import (
    SOURCE_TABLES,
    STTM_CTP_FLOW_DIRECTION,
    defs,
    silver_gas_dim_connection_point,
    silver_gas_dim_connection_point_required_fields,
)


def _gbb_nodes_connection_points() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "ConnectionPointName": ["Old CP", "New CP"],
            "ConnectionPointId": [200, 200],
            "FacilityId": [10, 10],
            "FacilityName": ["Facility", "Facility"],
            "NodeId": [100, 100],
            "LocationId": [1, 1],
            "LocationName": ["Location", "Location"],
            "StateName": ["VIC", "VIC"],
            "FlowDirection": ["RECEIPT", "RECEIPT"],
            "Exempt": [False, True],
            "ExemptionDescription": [None, "Exempt"],
            "EffectiveDate": ["2024/01/01", "2024/02/01"],
            "LastUpdated": ["01 Jan 2024 00:00:00", "01 Feb 2024 00:00:00"],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["old-source", "new-source"],
            "source_file": ["s3://old", "s3://new"],
        }
    )


def _gbb_demand_zone_mapping() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "DemandZone": ["DZ1"],
            "FacilityName": ["Facility"],
            "FacilityType": ["PIPE"],
            "FacilityId": [10],
            "NodeId": [100],
            "ConnectionPointId": [200],
            "FlowDirection": ["RECEIPT"],
            "State": ["VIC"],
            "ingested_timestamp": [datetime(2024, 1, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["mapping-source"],
            "source_file": ["s3://mapping"],
        }
    )


def _facilities() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["facility-10", "facility-pipe1"],
            "source_system": ["GBB", "STTM"],
            "source_facility_id": ["10", "PIPE1"],
            "source_hub_id": [None, "SYD"],
        }
    )


def _locations() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["location-1"],
            "source_system": ["GBB"],
            "source_location_id": ["1"],
        }
    )


def _zones() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["zone-dz1", "zone-syd"],
            "source_system": ["GBB", "STTM"],
            "zone_type": ["demand_zone", "sttm_hub"],
            "source_zone_id": ["DZ1", "SYD"],
        }
    )


def _sttm_ctp_register() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "hub_identifier": ["SYD"],
            "hub_name": ["Sydney"],
            "facility_identifier": ["PIPE1"],
            "facility_name": ["Sydney Pipeline"],
            "facility_type": ["PIPE"],
            "ctp_identifier": ["CTP1"],
            "ctp_name": ["Custody Transfer Point 1"],
            "effective_from_date": ["2024-03-01"],
            "effective_to_date": ["2024-03-31"],
            "last_update_datetime": ["2024-03-01 04:05:06"],
            "report_datetime": ["2024-03-01 05:00:00"],
            "ingested_timestamp": [datetime(2024, 3, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["sttm-ctp"],
            "source_file": ["s3://sttm-ctp"],
        }
    )


def test_silver_gas_dim_connection_point_transform() -> None:
    fn = silver_gas_dim_connection_point.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            _gbb_nodes_connection_points(),
            _gbb_demand_zone_mapping(),
            _sttm_ctp_register(),
            _facilities(),
            _locations(),
            _zones(),
        ),
    )
    collected = result.value.collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected.height == 2

    row = collected.filter(pl.col("source_system") == "GBB").row(0, named=True)
    assert row["connection_point_name"] == "New CP"
    assert row["facility_key"] == "facility-10"
    assert row["location_key"] == "location-1"
    assert row["zone_key"] == "zone-dz1"
    assert row["source_surrogate_key"] == "new-source"
    assert row["source_tables"] == SOURCE_TABLES[:2]
    assert row["surrogate_key"] is not None

    sttm_row = collected.filter(pl.col("source_system") == "STTM").row(0, named=True)
    assert sttm_row["source_hub_id"] == "SYD"
    assert sttm_row["source_connection_point_id"] == "CTP1"
    assert sttm_row["connection_point_name"] == "Custody Transfer Point 1"
    assert sttm_row["flow_direction"] == STTM_CTP_FLOW_DIRECTION
    assert sttm_row["facility_key"] == "facility-pipe1"
    assert sttm_row["location_key"] is None
    assert sttm_row["zone_key"] == "zone-syd"
    assert sttm_row["source_surrogate_key"] == "sttm-ctp"


def test_required_fields_check_fails_for_null_required_field() -> None:
    check_def = silver_gas_dim_connection_point_required_fields
    check_fn = check_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = check_fn(
        pl.LazyFrame(
            {
                "surrogate_key": ["key-1"],
                "source_system": ["GBB"],
                "source_facility_id": ["10"],
                "source_connection_point_id": [None],
                "flow_direction": ["RECEIPT"],
            }
        )
    )

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()
    asset_key = AssetKey(["silver", "gas_model", "silver_gas_dim_connection_point"])
    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert isinstance(result, Definitions)
    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_dim_connection_point"
    )
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
