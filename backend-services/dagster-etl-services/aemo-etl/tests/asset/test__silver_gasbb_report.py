from pathlib import Path
from typing import cast

import polars as pl
import pytest
from dagster import AssetsDefinition

from aemo_etl.asset import gasbb

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata/silver-gasbb"

# get the mibb reports


@pytest.mark.parametrize(
    "asset",
    gasbb.report_assets,
    ids=[asset.key.path[-1] for asset in gasbb.report_assets],
)
def test__asset(asset: AssetsDefinition):
    asset_name = asset.key.path[-1]

    input_assets = list(asset.input_names.mapping.keys())  # pyright: ignore[reportAttributeAccessIssue]

    input_kwargs = {}

    for input_asset_name in input_assets:
        input_kwargs[input_asset_name] = pl.read_delta(
            list(MOCK_DATA_FOLDER.glob(input_asset_name))[0].as_posix()
        ).lazy()

    results = cast(pl.LazyFrame, asset(**input_kwargs))

    # get the asset check ans apply it to the results if it exists

    if asset_name in gasbb.__dict__:
        assert getattr(gasbb, asset_name).asset_check(results)[0]

    assert results.select(pl.len()).collect().item() > 0
