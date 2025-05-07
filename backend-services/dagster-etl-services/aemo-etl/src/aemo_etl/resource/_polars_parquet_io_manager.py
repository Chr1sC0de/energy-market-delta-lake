from typing import Literal, override

import dagster as dg
import polars as pl
import s3fs
from dagster import IOManager


# pyright: reportArgumentType=false

PolarsParquetMode = Literal["overwrite"]


class PolarsParquetIOManager(IOManager):
    root_uri: str
    schema: str
    mode: PolarsParquetMode

    def __init__(
        self, root_uri: str, schema: str, mode: PolarsParquetMode = "overwrite"
    ):
        self.root_uri = root_uri
        self.schema = schema
        self.mode = mode

    def _get_destination(self, context: dg.InputContext | dg.OutputContext) -> str:
        asset_key_path = context.asset_key.path

        return f"{self.root_uri}/{self.schema}/{asset_key_path[-1]}"

    @override
    def handle_output(self, context: dg.OutputContext, obj: pl.LazyFrame):
        fs = s3fs.S3FileSystem()
        s3_path = self._get_destination(context)
        with fs.open(f"{s3_path}/result.parquet", mode="wb") as f:
            obj.sink_parquet(f)
        context.add_output_metadata(context.metadata)
        context.add_output_metadata(
            {
                "table_uri": dg.MetadataValue.path(s3_path),
                "preview": dg.MetadataValue.md(
                    obj.head().collect().to_pandas().to_markdown()
                ),
                "dagster/row_count": dg.MetadataValue.int(
                    obj.select(pl.len()).collect().item()
                ),
            }
        )

    @override
    def load_input(self, context: dg.InputContext) -> pl.LazyFrame:
        return pl.scan_parquet(f"{self._get_destination(context)}/*.parquet")
