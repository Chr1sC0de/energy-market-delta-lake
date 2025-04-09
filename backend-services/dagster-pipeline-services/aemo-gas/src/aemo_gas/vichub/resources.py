from aemo_gas.configurations import BRONZE_AEMO_GAS_DIRECTORY, LANDING_BUCKET
from dagster_aws.s3 import S3PickleIOManager, S3Resource
from dagster_delta import WriteMode, MergeConfig, MergeType, S3Config
from dagster_delta.io_manager import SchemaMode
from dagster_delta_polars import DeltaLakePolarsIOManager


bronze_aemo_gas_upsert_io_manager = DeltaLakePolarsIOManager(
    root_uri=BRONZE_AEMO_GAS_DIRECTORY,
    storage_options=S3Config(),
    mode=WriteMode.merge,
    schema_mode=SchemaMode.overwrite,
    merge_config=MergeConfig(
        merge_type=MergeType.upsert,
        source_alias="s",
        target_alias="t",
    ),
)

s3_pickle_io_manager = S3PickleIOManager(
    s3_resource=S3Resource(),
    s3_bucket=LANDING_BUCKET,
)
