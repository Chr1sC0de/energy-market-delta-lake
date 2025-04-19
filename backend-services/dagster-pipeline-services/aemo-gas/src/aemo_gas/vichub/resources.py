from dagster_aws.s3 import S3PickleIOManager, S3Resource
from dagster_delta import (
    DeltaLakePolarsIOManager,
    MergeConfig,
    MergeType,
    S3Config,
    WriteMode,
)

from dagster_delta.io_manager import SchemaMode

from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET


bronze_aemo_gas_upsert_io_manager = DeltaLakePolarsIOManager(
    root_uri=f"S3://{BRONZE_BUCKET}/aemo/gas",
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

s3_pickle_io_manager = S3PickleIOManager(
    s3_resource=S3Resource(),
    s3_bucket=LANDING_BUCKET,
)
