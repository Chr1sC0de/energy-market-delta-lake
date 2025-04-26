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
        s3_path = self._get_destination(context)
        with fs.open(f"{s3_path}/result.parquet", mode="wb") as f:
            obj.collect().write_parquet(f)

        context.add_output_metadata(context.metadata)

        context.add_output_metadata(
            {
                "path": s3_path,
                "preview": dg.MetadataValue.md(
                    obj.head().collect().to_pandas().to_markdown()
                ),
                "row_count": dg.MetadataValue.int(
                    obj.select(pl.len()).collect().item()
                ),
                "column_count": dg.MetadataValue.int(len(obj.collect_schema())),
            }
        )

    @override
    def load_input(self, context: dg.InputContext) -> pl.LazyFrame:
        return pl.scan_parquet(f"{self._get_destination(context)}/*.parquet")
