import dagster as dg
from aemo_gas.vichub.jobs import process_zip_files_job


@dg.asset_sensor(
    asset_key=dg.AssetKey(["vichub", "downloaded_files_metadata"]),
    job=process_zip_files_job,
    default_status=dg.DefaultSensorStatus.RUNNING,
)
def download_files_sensor():
    return dg.RunRequest()


all = [download_files_sensor]
