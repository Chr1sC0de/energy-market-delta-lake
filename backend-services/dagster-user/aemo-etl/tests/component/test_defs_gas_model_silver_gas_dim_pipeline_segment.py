from datetime import datetime, timezone
from typing import cast

import polars as pl
from dagster import AssetKey, AssetsDefinition, Definitions, MaterializeResult

from aemo_etl.defs.gas_model.silver_gas_dim_pipeline_segment import (
    SOURCE_TABLES,
    defs,
    silver_gas_dim_pipeline_segment,
    silver_gas_dim_pipeline_segment_required_fields,
)


def _vicgas_pipe_segments() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "linepack_zone_id": [5, 5],
            "pipe_segment_id": [77, 77],
            "pipe_segment_name": ["Old Segment", "New Segment"],
            "node_origin_id": [1, 1],
            "node_destination_id": [2, 2],
            "diameter": [10.0, 11.0],
            "length": [20.0, 21.0],
            "max_pressure": [30.0, 31.0],
            "min_pressure": [5.0, 6.0],
            "reverse_flow": ["N", "Y"],
            "compressor": ["N", "Y"],
            "commencement_date": ["2024/01/01", "2024/02/01"],
            "termination_date": [None, None],
            "last_mod_date": ["01 Jan 2024 00:00:00", "01 Feb 2024 00:00:00"],
            "ingested_timestamp": [
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 2, 1, tzinfo=timezone.utc),
            ],
            "surrogate_key": ["old-source", "new-source"],
            "source_file": ["s3://old", "s3://new"],
        }
    )


def _vicgas_mce_nodes() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "point_group_identifier_id": [1, 2],
            "point_group_identifier_name": ["Origin Node", "Destination Node"],
        }
    )


def _zones() -> pl.LazyFrame:
    return pl.LazyFrame(
        {
            "surrogate_key": ["linepack-zone-5"],
            "source_system": ["VICGAS"],
            "zone_type": ["linepack_zone"],
            "source_zone_id": ["5"],
        }
    )


def test_silver_gas_dim_pipeline_segment_transform() -> None:
    fn = silver_gas_dim_pipeline_segment.op.compute_fn.decorated_fn  # type: ignore[union-attr]

    result = cast(
        MaterializeResult[pl.LazyFrame],
        fn(_vicgas_pipe_segments(), _vicgas_mce_nodes(), _zones()),
    )
    collected = result.value.collect()

    assert "dagster/column_lineage" in (result.metadata or {})
    assert collected.height == 1
    row = collected.row(0, named=True)
    assert row["pipe_segment_name"] == "New Segment"
    assert row["zone_key"] == "linepack-zone-5"
    assert row["source_origin_node_name"] == "Origin Node"
    assert row["source_destination_node_name"] == "Destination Node"
    assert row["source_surrogate_key"] == "new-source"
    assert row["source_tables"] == SOURCE_TABLES
    assert row["surrogate_key"] is not None


def test_required_fields_check_fails_for_null_required_field() -> None:
    check_def = silver_gas_dim_pipeline_segment_required_fields
    check_fn = check_def.op.compute_fn.decorated_fn  # type: ignore[union-attr]
    result = check_fn(
        pl.LazyFrame(
            {
                "surrogate_key": ["key-1"],
                "source_system": ["VICGAS"],
                "source_pipe_segment_id": ["77"],
                "pipe_segment_name": [None],
            }
        )
    )

    assert not result.passed


def test_defs_returns_asset_and_checks() -> None:
    result = defs()
    asset_key = AssetKey(["silver", "gas_model", "silver_gas_dim_pipeline_segment"])
    assets = list(result.assets or [])
    asset_checks = list(result.asset_checks or [])

    assert isinstance(result, Definitions)
    assert len(assets) == 1
    assert len(asset_checks) == 4

    asset_def = cast(AssetsDefinition, assets[0])
    assert asset_def.metadata_by_key[asset_key]["dagster/table_name"] == (
        "silver.gas_model.silver_gas_dim_pipeline_segment"
    )
    assert asset_def.metadata_by_key[asset_key]["source_tables"] == SOURCE_TABLES
