from dagster import AssetsDefinition

from aemo_etl.defs.gasbb import silver_gasbb_short_term_capacity_outlook


_assets = [silver_gasbb_short_term_capacity_outlook]

report_assets = []
compact_and_vacuum_assets = []
asset_checks = []

for asset in _assets:
    report_assets.append(getattr(asset, "table_asset"))
    compact_and_vacuum_assets.append(getattr(asset, "compact_and_vacuum_asset"))
    asset_checks.append(getattr(asset, "asset_check"))


assets: list[AssetsDefinition] = [
    *report_assets,
    *compact_and_vacuum_assets,
]
