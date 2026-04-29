from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_facility import (
    SOURCE_TABLES,
    defs,
    silver_gas_dim_facility,
    silver_gas_dim_facility_required_fields,
)


def _gbb_facilities() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "FacilityName": ["Old Facility", "New Facility"],
            "FacilityShortName": ["OLD", "NEW"],
            "FacilityId": [10, 10],
            "FacilityType": ["PIPE", "PIPE"],
            "FacilityTypeDescription": ["Pipeline", "Pipeline"],
            "OperatingState": ["ACTIVE", "ACTIVE"],
            "OperatingStateDate": ["2024/01/01", "2024/02/01"],
            "OperatorName": ["Operator", "Operator"],
            "OperatorId": [1, 1],
            "OperatorChangeDate": ["2024/01/01", "2024/02/01"],
            "LastUpdated": ["01 Jan 2024 00:00:00", "01 Feb 2024 00:00:00"],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["old-source", "new-source"],
            "source_file": ["s3://old", "s3://new"],
        }
    )


def _participants() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["participant-1"],
            "participant_identity_source": ["company_id"],
            "participant_identity_value": ["1"],
        }
    )


def test_silver_gas_dim_facility_transform() -> None:
    fn = silver_gas_dim_facility.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame], fn(_gbb_facilities(), _participants())
    )
    collected = result.value.collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected.height == 1
    row = collected.row(0, named=True)
    assert row["facility_name"] == "New Facility"
    assert row["participant_key"] == "participant-1"
    assert row["source_surrogate_key"] == "new-source"
    assert row["surrogate_key"] is not None


def test_required_fields_check_fails_for_null_required_field() -> None:
    check_fn = silver_gas_dim_facility_required_fields.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = check_fn(
        pl.LazyFrame(
            {
                "surrogate_key": ["key-1"],
                "source_system": ["GBB"],
                "source_facility_id": ["10"],
                "facility_name": [None],
            }
        )
    )

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()
    asset_key = AssetKey(["silver", "gas_model", "silver_gas_dim_facility"])
    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert isinstance(result, Definitions)
    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_dim_facility"
    )
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
