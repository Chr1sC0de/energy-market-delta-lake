from aemo_etl.asset._bronze_mibb_report_list import (
    bronze_vicgas_mibb_report_list_asset,
    bronze_vicgas_mibb_report_list_asset_check,
)

from aemo_etl.asset._bronze_s3_table_locations import (
    bronze_s3_table_locations_asset,
    bronze_s3_table_locations_asset_check,
)

from aemo_etl.asset import mibb

asset_list = [
    bronze_vicgas_mibb_report_list_asset,
    bronze_s3_table_locations_asset,
    *mibb.assets,
]

asset_check_list = [
    bronze_vicgas_mibb_report_list_asset_check,
    bronze_s3_table_locations_asset_check,
    *mibb.asset_checks,
]

__all__ = [
    "bronze_vicgas_mibb_report_list_asset",
    "bronze_vicgas_mibb_report_list_asset_check",
    "bronze_s3_table_locations_asset",
    "bronze_s3_table_locations_asset_check",
    "mibb",
]
