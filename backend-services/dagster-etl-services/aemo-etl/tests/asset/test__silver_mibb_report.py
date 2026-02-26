import typing as tp
from pathlib import Path
from typing import cast

import polars as pl
import pytest
from dagster import AssetsDefinition, load_assets_from_package_module

from aemo_etl.defs import mibb

CWD = Path(__file__).parent
MOCK_DATA_FOLDER = CWD / "@mockdata/silver-mibb"

assets_list = [
    asset
    for asset in tp.cast(list[AssetsDefinition], load_assets_from_package_module(mibb))
    if not asset.key.path[-1].endswith("compact_and_vacuum")
]


@pytest.mark.parametrize(
    "asset",
    assets_list,
    ids=[asset.key.path[-1] for asset in assets_list],
)
def test__asset(asset: AssetsDefinition) -> None:
    asset_name = asset.key.path[-1]

    input_assets = list(asset.input_names)

    input_kwargs = {}

    for input_asset_name in input_assets:
        input_kwargs[input_asset_name] = pl.read_delta(
            list(MOCK_DATA_FOLDER.glob(input_asset_name))[0].as_posix()
        ).lazy()

    results = cast(pl.LazyFrame, asset(**input_kwargs))

    # get the asset check ans apply it to the results if it exists

    if asset_name in mibb.__dict__:
        assert getattr(mibb, asset_name).asset_check(results)[0]

    assert cast(pl.DataFrame, results.select(pl.len()).collect()).item() > 0
