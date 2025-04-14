import dagster as dg
from aemo_gas.vichub.ops import process_zip_files_op

vichub_downloaded_files_metadata_job = dg.define_asset_job(
    "vichub_downloaded_files_metadata_job",
    selection=["key:vichub/downloaded_files_metadata"],
)


@dg.job()
def process_zip_files_job():
    _ = process_zip_files_op()


all = [vichub_downloaded_files_metadata_job, process_zip_files_job]
