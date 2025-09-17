import pathlib as pt

import dagster as dg
import polars as pl
import pytest

from aemo_etl import factory
from aemo_etl.configuration import BRONZE_BUCKET

# pyright: reportUnusedParameter=false

bucket = BRONZE_BUCKET
s3_schema = "aemo_vicgas"
table_name = "mock_table"


@pytest.fixture(autouse=True)
def bulid_mock_table():
    write_path = pt.Path(__file__).parent / "@mockdata/.mock_table"
    for item in write_path.rglob("*"):
        if item.is_file():
            item.unlink(missing_ok=True)

    for item in write_path.rglob("*"):
        if item.is_dir():
            item.rmdir()

    for i in range(0, 20):
        if i == 0:
            pl.DataFrame({"col1": [i], "col2": [i]}).write_delta(write_path)
        else:
            pl.DataFrame({"col1": [i], "col2": [i]}).write_delta(
                write_path, mode="append"
            )


def test__compact_and_vacuum():
    captured_response = {}
    compact_and_vacuum_dataframe_asset = (
        factory.asset.compact_and_vacuum_dataframe_asset_factory(
            group_name="aemo",
            s3_target_bucket=bucket,
            s3_target_prefix=s3_schema,
            s3_target_table_name=table_name,
            table_path_override=pt.Path(__file__).parent / "@mockdata/.mock_table",
            key_prefix=["aemo_vicgas", "optimize"],
            captured_response=captured_response,
        )
    )

    compact_and_vacuum_dataframe_asset(
        dg.build_asset_context(),
    )

    assert (
        captured_response["filesAdded"]
        == '{"avg":1011.0,"max":1011,"min":1011,"totalFiles":1,"totalSize":1011}'
    )
