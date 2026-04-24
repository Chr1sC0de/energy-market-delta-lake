from typing import Any, Iterable, Mapping, TypedDict

from dagster import (
    AssetCheckKey,
    AssetIn,
    AssetsDefinition,
    AutomationCondition,
    PartitionsDefinition,
    RetryPolicy,
    SourceAsset,
)
from dagster._config.config_schema import UserConfigSchema
from dagster._core.definitions.asset_key import (
    CoercibleToAssetKey,
)
from dagster._core.definitions.assets.definition.asset_dep import CoercibleToAssetDep


class AssetChecksKwargs(TypedDict, total=False):
    asset: CoercibleToAssetKey | AssetsDefinition | SourceAsset
    name: str
    description: str
    blocking: bool
    additional_ins: Mapping[str, AssetIn]
    additional_deps: Iterable[CoercibleToAssetDep]
    required_resource_keys: set[str]
    resource_defs: Mapping[str, object]
    config_schema: UserConfigSchema
    compute_kind: str
    op_tags: Mapping[str, Any]
    retry_policy: RetryPolicy
    metadata: Mapping[str, Any]
    automation_condition: AutomationCondition[AssetCheckKey]
    pool: str
    partitions_def: PartitionsDefinition
