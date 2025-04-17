import dagster as dg
from aemo_gas.vichub.ops import process_zip_files

all = []


def register_job(job: dg.JobDefinition):
    all.append(job)
    return job


vichub_downloaded_files_metadata_job = register_job(
    dg.define_asset_job(
        "vichub_downloaded_files_metadata_job",
        selection=["key:vichub/downloaded_files_metadata"],
    )
)


@register_job
@dg.job()
def process_zip_files_job():
    _ = process_zip_files.op()
