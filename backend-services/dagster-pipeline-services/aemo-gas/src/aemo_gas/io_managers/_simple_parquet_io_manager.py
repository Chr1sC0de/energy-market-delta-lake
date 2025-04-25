import s3fs

from typing import Literal, override
import polars as pl
import dagster as dg
from dagster import IOManager


PolarsParquetMode = Literal["overwrite"]


class SimplePolarsParquetIOManager(IOManager):
    root_uri: str
    mode: PolarsParquetMode

    def __init__(self, root_uri: str, mode: PolarsParquetMode):
        self.root_uri = root_uri
        self.mode = mode

    def _get_destination(self, context: dg.OutputContext) -> str:
        asset_key_path = context.asset_key.path
        schema, table_name = asset_key_path[-2:]
        return f"{self.root_uri}/{schema}/{table_name}"

    @override
    def handle_output(self, context: dg.OutputContext, obj: pl.LazyFrame):
        fs = s3fs.S3FileSystem()
        with fs.open(
            f"{self._get_destination(context)}/result.parquet", mode="wb"
        ) as f:
            obj.collect().write_parquet(f)

    @override
    def load_input(self, context: dg.InputContext) -> pl.LazyFrame:
        return pl.scan_parquet(f"{self._get_destination(context)}/*.parquet")
