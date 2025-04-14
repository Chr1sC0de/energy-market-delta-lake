import dagster as dg
from dagster_aws import s3 as dgs3
from aemo_gas.vichub.assets._downloaded_files_metadata import (
    get_links_op,
    get_current_download_file_metadata_df_op,
)

from aemo_gas.vichub.ops._process_zip_files import (
    create_dynamic_process_zip_op,
    process_zip_op,
)


def test__get_current_metadata_df():
    df = get_current_download_file_metadata_df_op()


def test__get_links_op():
    context = dg.build_op_context()
    get_links_op(context)


def test__create_dynamic_process_zip_op():
    context = dg.build_op_context()
    s3_resource = dgs3.S3Resource()
    create_dynamic_process_zip_op(context, s3_resource)


def test__process_zip_op():
    context = dg.build_op_context()
    s3_resource = dgs3.S3Resource()
    process_zip_op(context, s3_resource, "aemo/gas/vichub/PUBLICRPTS07.ZIP")
