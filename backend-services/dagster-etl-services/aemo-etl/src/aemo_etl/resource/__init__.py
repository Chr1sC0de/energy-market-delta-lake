from dagster_delta import (
    DeltaLakePolarsIOManager,
    MergeConfig,
    MergeType,
    S3Config,
    SchemaMode,
    WriteMode,
)

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.resource._s3_polars_parquet_io_manager import S3PolarsParquetIOManager
from aemo_etl.resource._s3_polars_deltalake_io_manager import S3PolarsDeltaLakeIOManager

__all__ = ["S3PolarsParquetIOManager", "S3PolarsDeltaLakeIOManager"]

bronze_delta_polars_io_manager = DeltaLakePolarsIOManager(
    root_uri=f"s3://{BRONZE_BUCKET}",
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
