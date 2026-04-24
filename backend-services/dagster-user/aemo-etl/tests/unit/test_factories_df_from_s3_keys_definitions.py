from dagster import Definitions
from polars import String

from aemo_etl.factories.df_from_s3_keys.definitions import (
    df_from_s3_keys_definitions_factory,
)


def test_df_from_s3_keys_definitions_factory_returns_definitions() -> None:
    schema = {
        "col1": String,
    }
    defs = df_from_s3_keys_definitions_factory(
        domain="gbb",
        name_suffix="test_table",
        glob_pattern="test*",
        schema=schema,
        schema_descriptions={"col1": "test column"},
        surrogate_key_sources=["col1"],
        description="A test table",
    )
    assert isinstance(defs, Definitions)
