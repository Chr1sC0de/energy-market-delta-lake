import pathlib as pt

from dagster import materialize
from dagster_aws.s3 import S3Resource
from polars import DataFrame
from types_boto3_s3.client import S3Client
from aemo_gas.vichub import assets, definitions, resources

cwd = pt.Path(__file__).parent
mock_folder = cwd / "@mockdata"
mock_delta_table_factory_folder = mock_folder / "mock_delta_table_factory"


def test__get_s3_object_keys_from_prefix_factory(
    s3: S3Client, create_buckets: None, create_delta_log: None
):
    definition_config = definitions.bronze.config.int029a_system_wide_notices.config

    config = assets.bronze.mibb.factory.MibbDeltaTableAssetFactoryConfig(
        io_manager_key=definition_config.io_manager_key,
        group_name=definition_config.group_name,
        key_prefix=definition_config.key_prefix,
        source_bucket=definition_config.source_bucket,
        source_s3_prefix=definition_config.source_s3_prefix,
        source_s3_glob=definition_config.source_s3_glob,
        target_bucket=definition_config.target_bucket,
        target_s3_prefix=definition_config.target_s3_prefix,
        target_s3_name=definition_config.target_s3_name,
        df_schema=definition_config.df_schema,
        description=definition_config.description,
        metadata=definition_config.metadata,
        post_process_hook=definition_config.post_process_hook,
        metadata_builders=definition_config.metadata_builders,
    )

    # now upload all the files to the required s3 bucket

    files = mock_delta_table_factory_folder.glob(
        config.source_s3_glob, case_sensitive=False
    )

    for file in files:
        s3.upload_file(
            Bucket=config.source_bucket,
            Filename=file.as_posix(),
            Key=f"{config.source_s3_prefix}/{file.name}",
        )

    asset_function = assets.bronze.mibb.factory.delta_table(config)

    in_process_result = materialize(
        assets=[asset_function],
        resources={
            "s3_resource": S3Resource(),
            config.io_manager_key: resources.bronze_aemo_gas_deltalake_upsert_io_manager,
        },
    )

    df: DataFrame = in_process_result.output_for_node(
        f"bronze__aemo__gas__vichub__{config.target_s3_name}"
    ).collect()

    assert set(config.df_schema.items()).issubset(set(df.schema.items()))
