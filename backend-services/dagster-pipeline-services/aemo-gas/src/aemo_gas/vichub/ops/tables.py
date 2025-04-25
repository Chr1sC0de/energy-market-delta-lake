from aemo_gas import factory
from aemo_gas.configurations import BRONZE_BUCKET

get_downloaded_public_files = factory.ops.get_dataframe_from_path_factory(
    "downloaded_public_files_table",
    f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/downloaded_public_files",
)
