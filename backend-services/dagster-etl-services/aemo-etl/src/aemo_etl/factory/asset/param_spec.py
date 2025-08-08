from typing import AbstractSet, Any, Iterable, Mapping, NotRequired, Sequence, TypedDict

from dagster import (
    AssetCheckSpec,
    AssetIn,
    AutomationCondition,
    BackfillPolicy,
    ConfigMapping,
    DagsterType,
    PartitionsDefinition,
    ResourceDefinition,
    RetryPolicy,
)
from dagster._config import UserConfigSchema
from dagster._core.definitions.asset_dep import CoercibleToAssetDep
from dagster._core.definitions.events import (
    CoercibleToAssetKey,
    CoercibleToAssetKeyPrefix,
)
from dagster._core.definitions.metadata import (
    RawMetadataMapping,
)


class GraphAssetParamSpec(TypedDict):
    name: NotRequired[str]
    key_prefix: NotRequired[CoercibleToAssetKeyPrefix]
    description: NotRequired[str]
    ins: NotRequired[Mapping[str, AssetIn]]
    config: NotRequired[ConfigMapping | Mapping[str, Any]]
    group_name: NotRequired[str]
    partitions_def: NotRequired[PartitionsDefinition]
    metadata: NotRequired[RawMetadataMapping]
    tags: NotRequired[Mapping[str, str]]
    owners: NotRequired[Sequence[str]]
    automation_condition: NotRequired[AutomationCondition]
    backfill_policy: NotRequired[BackfillPolicy]
    resource_defs: NotRequired[Mapping[str, ResourceDefinition]]
    check_specs: NotRequired[Sequence[AssetCheckSpec]]
    code_version: NotRequired[str]
    key: NotRequired[CoercibleToAssetKey]
    kinds: NotRequired[AbstractSet[str]]


class AssetDefinitonParamSpec(TypedDict):
    name: NotRequired[str]
    key_prefix: NotRequired[CoercibleToAssetKeyPrefix]
    metadata: NotRequired[dict[str, Any]]
    io_manager_key: NotRequired[str]
    key: NotRequired[CoercibleToAssetKey]
    ins: NotRequired[Mapping[str, AssetIn]]
    deps: NotRequired[Iterable[CoercibleToAssetDep]]
    tags: NotRequired[Mapping[str, str]]
    description: NotRequired[str]
    config_schema: NotRequired[UserConfigSchema]
    required_resource_keys: NotRequired[AbstractSet[str]]
    resource_defs: NotRequired[Mapping[str, object]]
    dagster_type: NotRequired[DagsterType]
    partitions_def: NotRequired[PartitionsDefinition[str]]
    op_tags: NotRequired[Mapping[str, Any]]
    group_name: NotRequired[str]
    output_required: NotRequired[bool]
    automation_condition: NotRequired[AutomationCondition]
    backfill_policy: NotRequired[BackfillPolicy]
    retry_policy: NotRequired[RetryPolicy]
    code_version: NotRequired[str]
    check_specs: NotRequired[Sequence[AssetCheckSpec]]
    owners: NotRequired[Sequence[str]]
    kinds: NotRequired[AbstractSet[str]]
    pool: NotRequired[str]
