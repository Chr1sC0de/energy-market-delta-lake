from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_zone import (
    SOURCE_TABLES,
    defs,
    silver_gas_dim_zone,
    silver_gas_dim_zone_required_fields,
)


def _gbb_demand_zone_mapping() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "DemandZone": ["DZ1", "DZ1"],
            "FacilityName": ["Facility", "Facility"],
            "FacilityType": ["PIPE", "PIPE"],
            "FacilityId": [10, 10],
            "NodeId": [100, 100],
            "ConnectionPointId": [200, 200],
            "FlowDirection": ["RECEIPT", "RECEIPT"],
            "State": ["VIC", "VIC"],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["demand-old", "demand-new"],
            "source_file": ["s3://demand-old", "s3://demand-new"],
        }
    )


def _gbb_linepack_zones() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "Operator": ["Operator"],
            "LinepackZone": ["GBB-LP1"],
            "LinepackZoneDescription": ["GBB linepack zone"],
            "ingested_timestamp": [datetime(2024, 1, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["gbb-linepack"],
            "source_file": ["s3://gbb-linepack"],
        }
    )


def _vicgas_hv_zone_mapping() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "mirn": ["5000000000"],
            "site_company": ["Company"],
            "hv_zone": [401],
            "hv_zone_desc": ["HV zone"],
            "ingested_timestamp": [datetime(2024, 1, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["hv-zone"],
            "source_file": ["s3://hv-zone"],
        }
    )


def _vicgas_tuos_zone_mapping() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "postcode": ["3000"],
            "tuos_zone": [7],
            "tuos_zone_desc": ["TUOS zone"],
            "ingested_timestamp": [datetime(2024, 1, 1, tzinfo=timezone.utc)],
            "surrogate_key": ["tuos-zone"],
            "source_file": ["s3://tuos-zone"],
        }
    )


def _vicgas_pipe_segments() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "linepack_zone_id": [5, 5],
            "pipe_segment_id": [77, 78],
            "pipe_segment_name": ["Segment 77", "Segment 78"],
            "node_origin_id": [1, 1],
            "node_destination_id": [2, 2],
            "diameter": [10.0, 10.0],
            "length": [20.0, 20.0],
            "max_pressure": [30.0, 30.0],
            "min_pressure": [5.0, 5.0],
            "reverse_flow": ["N", "N"],
            "compressor": ["N", "N"],
            "commencement_date": ["2024/01/01", "2024/01/01"],
            "termination_date": [None, None],
            "last_mod_date": ["01 Jan 2024 00:00:00", "01 Feb 2024 00:00:00"],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["vic-linepack-old", "vic-linepack-new"],
            "source_file": ["s3://vic-linepack-old", "s3://vic-linepack-new"],
        }
    )


def test_silver_gas_dim_zone_transform() -> None:
    fn = silver_gas_dim_zone.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(
            _gbb_demand_zone_mapping(),
            _gbb_linepack_zones(),
            _vicgas_hv_zone_mapping(),
            _vicgas_tuos_zone_mapping(),
            _vicgas_pipe_segments(),
        ),
    )
    collected = result.value.collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected.height == 5
    assert collected["surrogate_key"].null_count() == 0
    assert collected["surrogate_key"].n_unique() == collected.height
    assert set(collected["zone_type"]) == {
        "demand_zone",
        "heating_value_zone",
        "linepack_zone",
        "tuos_zone",
    }

    demand_zone = collected.filter(pl.col("source_zone_id") == "DZ1").row(0, named=True)
    assert demand_zone["source_system"] == "GBB"
    assert demand_zone["source_surrogate_keys"] == ["demand-new", "demand-old"]
    assert demand_zone["source_files"] == ["s3://demand-new", "s3://demand-old"]


def test_required_fields_check_fails_for_null_required_field() -> None:
    check_fn = silver_gas_dim_zone_required_fields.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = check_fn(
        pl.LazyFrame(
            {
                "surrogate_key": ["key-1"],
                "source_system": ["GBB"],
                "zone_type": ["demand_zone"],
                "source_zone_id": [None],
            }
        )
    )

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()
    asset_key = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])
    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert isinstance(result, Definitions)
    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_dim_zone"
    )
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
