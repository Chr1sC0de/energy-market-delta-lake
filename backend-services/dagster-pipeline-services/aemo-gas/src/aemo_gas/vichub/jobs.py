import dagster as dg

vichub_downloaded_files_metadata_job = dg.define_asset_job(
    "vichub_downloaded_files_metadata_job",
    selection=["key:vichub/downloaded_files_metadata"],
)

all = [vichub_downloaded_files_metadata_job]
