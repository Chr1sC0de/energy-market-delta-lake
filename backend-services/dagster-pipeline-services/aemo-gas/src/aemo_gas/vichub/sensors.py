import dagster as dg
from aemo_gas.vichub.jobs import process_zip_files_job
from configurations.parameters import DEVELOPMENT_LOCATION

all = []


def register_sensor(sensor: dg.AssetSensorDefinition) -> dg.AssetSensorDefinition:
    all.append(sensor)
    return sensor


@register_sensor
@dg.asset_sensor(
    asset_key=dg.AssetKey([ "bronze","aemo", "gas", "vichub", "downloaded_files_metadata"]),
    job=process_zip_files_job,
    default_status=dg.DefaultSensorStatus.STOPPED
    if DEVELOPMENT_LOCATION == "local"
    else dg.DefaultSensorStatus.RUNNING,
)
def download_files_sensor():
    return dg.RunRequest()
