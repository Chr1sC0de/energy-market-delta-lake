from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, cast
from unittest.mock import patch

import polars as pl
from dagster import Definitions
from polars import Datetime, Int64, String

from aemo_etl.factories.definitions.df_from_s3_keys import (
    df_from_s3_keys_definitions_factory,
)

SCHEMA = {
    "a": Int64,
    "surrogate_key": String,
    "ingested_timestamp": Datetime("ms", "UTC"),
    "ingested_date": Datetime("ms", "UTC"),
    "source_file": String,
}
DESCRIPTIONS: dict[str, str] = {}


def _silver_fn(defs: Definitions) -> Callable[..., Any]:
    silver = next(
        a
        for a in (defs.assets or [])  # ty:ignore[union-attr]
        if hasattr(a, "key") and "silver" in str(a.key)  # ty:ignore[union-attr]
    )
    return cast(
        Callable[..., Any],
        silver.node_def.compute_fn.decorated_fn,  # type: ignore[union-attr]
    )


def _make_defs() -> Definitions:
    return df_from_s3_keys_definitions_factory(
        domain="test",
        name_suffix="test",
        glob_pattern="*.csv",
        schema=SCHEMA,
        schema_descriptions=DESCRIPTIONS,
        surrogate_key_sources=["a"],
    )


def _input_df() -> pl.LazyFrame:
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    return pl.LazyFrame(
        {
            "a": [1, 2, 2],
            "surrogate_key": ["sk1", "sk2", "sk2"],
            "ingested_timestamp": [now, now, now],
            "ingested_date": [now, now, now],
            "source_file": ["f", "f", "f"],
        },
        schema=SCHEMA,
    )


def test_silver_asset_table_not_exists() -> None:
    defs = _make_defs()
    silver_fn = _silver_fn(defs)
    with patch(
        "aemo_etl.factories.definitions.df_from_s3_keys.table_exists",
        return_value=False,
    ):
        result = silver_fn(df=_input_df())
    assert isinstance(result, pl.LazyFrame)
    # deduplication: sk1 once, sk2 once → 2 rows
    assert result.select(pl.len()).collect().item() == 2  # ty:ignore[unresolved-attribute]


def test_silver_asset_table_exists() -> None:
    now = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    existing = pl.LazyFrame(
        {
            "a": [1],
            "surrogate_key": ["sk1"],
            "ingested_timestamp": [now],
            "ingested_date": [now],
            "source_file": ["f"],
        },
        schema=SCHEMA,
    )

    defs = _make_defs()
    silver_fn = _silver_fn(defs)

    with (
        patch(
            "aemo_etl.factories.definitions.df_from_s3_keys.table_exists",
            return_value=True,
        ),
        patch(
            "aemo_etl.factories.definitions.df_from_s3_keys.scan_delta",
            return_value=existing,
        ),
    ):
        result = silver_fn(df=_input_df())

    assert isinstance(result, pl.LazyFrame)
    rows = result.collect()
    # sk1 already in table → only sk2 should be new
    assert set(rows["surrogate_key"].to_list()) == {"sk2"}
