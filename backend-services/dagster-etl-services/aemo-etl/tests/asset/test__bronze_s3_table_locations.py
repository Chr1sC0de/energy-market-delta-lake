from typing import cast, Iterable
from aemo_etl.asset import (
    bronze_s3_table_locations_asset,
    bronze_s3_table_locations_asset_check,
)


def test__bronze_mibb_report_list() -> None:
    asset = bronze_s3_table_locations_asset()
    asset_check_results = bronze_s3_table_locations_asset_check(asset)

    asset_check_results = cast(Iterable, asset_check_results)

    for check_results in asset_check_results:
        assert check_results[0]
