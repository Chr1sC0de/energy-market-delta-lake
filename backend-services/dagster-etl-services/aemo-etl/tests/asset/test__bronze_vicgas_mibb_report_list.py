from aemo_etl.defs.bronze_mibb_report_list import (
    bronze_vicgas_mibb_report_list_asset,
    bronze_vicgas_mibb_report_list_asset_check,
)


def test__bronze_vicgas_mibb_report_list() -> None:
    asset = bronze_vicgas_mibb_report_list_asset()

    assert bronze_vicgas_mibb_report_list_asset_check(asset)
