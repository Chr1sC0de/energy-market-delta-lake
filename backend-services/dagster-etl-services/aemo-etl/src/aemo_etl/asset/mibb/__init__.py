from dagster import AssetsDefinition
from aemo_etl.asset.mibb import (
    silver_int029a_system_notices,
    silver_int037b_indicative_mkt_price,
    silver_int037c_indicative_price,
    silver_int041_market_and_reference_prices,
)

_assets = [
    silver_int029a_system_notices,
    silver_int037b_indicative_mkt_price,
    silver_int037c_indicative_price,
    silver_int041_market_and_reference_prices,
]

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
