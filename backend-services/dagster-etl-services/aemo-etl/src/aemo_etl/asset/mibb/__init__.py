from dagster import AssetsDefinition
from aemo_etl.asset.mibb import silver_int029a_system_notices

report_assets = [silver_int029a_system_notices.asset]

compact_and_vacuum_assets = [silver_int029a_system_notices.compact_and_vacuum_asset]


assets: list[AssetsDefinition] = [
    *report_assets,
    *compact_and_vacuum_assets,
]

asset_checks = [
    silver_int029a_system_notices.asset_check,
]
