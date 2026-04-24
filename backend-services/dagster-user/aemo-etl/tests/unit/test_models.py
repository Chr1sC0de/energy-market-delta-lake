from aemo_etl.models import GraphAssetKwargs, OpKwargs
from aemo_etl.models._graph_asset_kwargs import AssetDefinitonParamSpec
from aemo_etl.models._op_kwargs import OpKwargs as OpKwargsAlias


def test_models_importable() -> None:
    # TypedDicts are defined – importing them covers the class declarations.
    assert GraphAssetKwargs is not None
    assert OpKwargs is not None
    assert AssetDefinitonParamSpec is not None
    assert OpKwargsAlias is OpKwargs
