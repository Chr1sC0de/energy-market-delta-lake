from typing import Any, Literal, override
import polars as pl
import dagster as dg
from dagster import IOManager
from dagster_aws.s3 import S3PickleIOManager, S3Resource
from dagster_delta import (
    DeltaLakePolarsIOManager,
    MergeConfig,
    MergeType,
    S3Config,
    WriteMode,
)
import s3fs
from dagster_delta.io_manager import SchemaMode

from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET


PolarsParquetMode = Literal["overwrite"]


class SimplePolarsParquetIOManager(IOManager):
    root_uri: str
    mode: PolarsParquetMode

    def __init__(self, root_uri: str, mode: PolarsParquetMode):
        self.root_uri = root_uri
        self.mode = mode

    def _get_destination(self, context: dg.OutputContext) -> str:
        asset_key_str = context.asset_key.path
        return f"{self.root_uri}/{asset_key_str[-2]}/{asset_key_str[-1]}"

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


bronze_aemo_gas_root_uri = f"s3://{BRONZE_BUCKET}/aemo/gas"

bronze_aemo_gas_deltalake_upsert_io_manager = DeltaLakePolarsIOManager(
    root_uri=bronze_aemo_gas_root_uri,
    storage_options=S3Config(),
    mode=WriteMode.merge,
    schema_mode=SchemaMode.overwrite,
    merge_config=MergeConfig(
        merge_type=MergeType.upsert,
        predicate="s.a=t.a",
        source_alias="s",
        target_alias="t",
    ),
)
bronze_aemo_gas_simple_polars_parquet_io_manager = SimplePolarsParquetIOManager(
    root_uri=bronze_aemo_gas_root_uri, mode="overwrite"
)

s3_pickle_io_manager = S3PickleIOManager(
    s3_resource=S3Resource(),
    s3_bucket=LANDING_BUCKET,
)
