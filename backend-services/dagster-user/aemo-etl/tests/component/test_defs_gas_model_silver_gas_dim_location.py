from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_location import (
    SOURCE_TABLES,
    defs,
    silver_gas_dim_location,
    silver_gas_dim_location_required_fields,
)


def _make_bronze_locations() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "LocationName": ["Older Location", "Newer Location", "Other Location"],
            "LocationId": [1, 1, 2],
            "State": ["VIC", "VIC", "NSW"],
            "LocationType": ["Demand", "Demand", "Supply"],
            "Description": ["old description", "new description", "other description"],
            "LastUpdated": [
                "01 Jan 2024 00:00:00",
                "01 Feb 2024 00:00:00",
                "2024/03/01",
            ],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
                datetime(2024, 3, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["bronze-old", "bronze-new", "bronze-other"],
            "source_file": ["s3://old", "s3://new", "s3://other"],
        }
    )


def test_silver_gas_dim_location_transform() -> None:
    fn = silver_gas_dim_location.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(MaterializeResult[pl.LazyFrame], fn(_make_bronze_locations()))

    assert "dagster/column_lineage" in (result.metadata or {})
    collected = result.value.collect().sort("source_location_id")

    assert collected.columns == [
        "surrogate_key",
        "source_system",
        "source_tables",
        "source_location_id",
        "location_name",
        "state",
        "location_type",
        "location_description",
        "source_last_updated",
        "source_last_updated_timestamp",
        "source_surrogate_key",
        "source_file",
        "ingested_timestamp",
    ]
    assert collected.height == 2

    location_one = collected.filter(pl.col("source_location_id") == "1").row(
        0, named=True
    )
    assert location_one["location_name"] == "Newer Location"
    assert location_one["source_system"] == "GBB"
    assert location_one["source_tables"] == SOURCE_TABLES
    assert location_one["source_surrogate_key"] == "bronze-new"
    assert location_one["source_file"] == "s3://new"
    assert location_one["surrogate_key"] is not None


def test_silver_gas_dim_location_surrogate_key_is_silver_key() -> None:
    fn = silver_gas_dim_location.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(MaterializeResult[pl.LazyFrame], fn(_make_bronze_locations()))
    collected = result.value.collect()

    assert collected["surrogate_key"].null_count() == 0
    assert collected["surrogate_key"].n_unique() == collected.height
    assert set(collected["source_surrogate_key"]) == {"bronze-new", "bronze-other"}
    assert set(collected["surrogate_key"]) != set(collected["source_surrogate_key"])


def test_required_fields_check_fails_for_null_required_field() -> None:
    check_fn = silver_gas_dim_location_required_fields.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    input_df = pl.LazyFrame(
        {
            "surrogate_key": ["key-1"],
            "source_system": ["GBB"],
            "source_location_id": ["1"],
            "location_name": [None],
        }
    )

    result = check_fn(input_df)

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()

    assert isinstance(result, Definitions)
    asset_key = AssetKey(["silver", "gas_model", "silver_gas_dim_location"])

    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.group_names_by_key[asset_key] == "gas_model"
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_dim_location"
    )
    assert asset_def.metadata_by_key[asset_key]["grain"] == (
        "one current row per source-qualified gas location"
    )
    assert asset_def.metadata_by_key[asset_key]["surrogate_key_sources"] == [
        "source_system",
        "source_location_id",
    ]
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
