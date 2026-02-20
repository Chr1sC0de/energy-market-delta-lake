from typing import cast

from dagster import AssetCheckResult, AssetsDefinition, asset
from polars import LazyFrame

from aemo_etl.factory.check import duplicate_row_check_factory


class Test__duplicate_row_check_factory:
    def test__no_duplicate_rows(self) -> None:
        @asset
        def mock_asset() -> LazyFrame:
            return LazyFrame({"col_1": [1, 2, 3], "col_2": [1, 2, 3]})

        asset_check = duplicate_row_check_factory(assets_definition=mock_asset)

        asset_check_result = cast(AssetCheckResult, asset_check(mock_asset()))
        assert asset_check_result.passed

    def test__with_duplicate_rows(self) -> None:
        @asset
        def mock_asset() -> LazyFrame:
            return LazyFrame({"col_1": [1, 1, 3], "col_2": [1, 1, 3]})

        asset_check = duplicate_row_check_factory(assets_definition=mock_asset)

        assert not cast(AssetCheckResult, asset_check(mock_asset())).passed

    def test__with_no_duplicate_primary_key(self) -> None:
        @asset
        def mock_asset() -> LazyFrame:
            return LazyFrame({"col_1": [1, 2, 3], "col_2": [1, 1, 3]})

        asset_check = duplicate_row_check_factory(
            assets_definition=mock_asset, primary_key="col_1"
        )

        assert cast(AssetCheckResult, asset_check(mock_asset())).passed

    def test__with_duplicate_primary_key(self) -> None:
        @asset
        def mock_asset() -> LazyFrame:
            return LazyFrame({"col_1": [1, 1, 3], "col_2": [1, 2, 3]})

        assert isinstance(mock_asset, AssetsDefinition)

        asset_check = duplicate_row_check_factory(
            assets_definition=mock_asset, primary_key="col_1"
        )

        assert not cast(AssetCheckResult, asset_check(mock_asset())).passed
