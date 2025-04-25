import dagster as dg
from dagster_aws.s3 import S3Resource

from aemo_gas import utils


def get_s3_object_keys_from_prefix_factory(
    bucket: str, search_prefix: str, file_glob: str
) -> dg.OpDefinition:
    @dg.op(
        name="get_s3_object_keys_from_prefix",
    )
    def asset(
        context: dg.OpExecutionContext,
        s3_resource: S3Resource,
    ) -> list[str]:
        context.log.info(f"getting object keys s3://{bucket}/{search_prefix}")

        s3_object_keys = utils.get_s3_object_keys_from_prefix_and_name_glob(
            s3_resource=s3_resource,
            bucket=bucket,
            prefix=search_prefix,
            file_glob=file_glob,
        )
        context.log.info(f"finished getting object keys s3://{bucket}/{search_prefix}")
        return s3_object_keys

    return asset
