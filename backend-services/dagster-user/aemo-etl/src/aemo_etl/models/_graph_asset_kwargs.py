from typing import AbstractSet, Any, Iterable, Mapping, Sequence, TypedDict

from dagster import (
    AssetCheckSpec,
    AssetIn,
    AssetKey,
    AutoMaterializePolicy,
    AutomationCondition,
    BackfillPolicy,
    ConfigMapping,
    DagsterType,
    HookDefinition,
    LegacyFreshnessPolicy,
    PartitionsDefinition,
    ResourceDefinition,
    RetryPolicy,
)
from dagster._config import UserConfigSchema
from dagster._core.definitions.asset_key import (
    CoercibleToAssetKey,
    CoercibleToAssetKeyPrefix,
)
from dagster._core.definitions.assets.definition.asset_dep import CoercibleToAssetDep
from dagster._core.definitions.metadata import RawMetadataMapping


class GraphAssetKwargs(TypedDict, total=False):
    description: str | None
    ins: Mapping[str, AssetIn] | None
    config: ConfigMapping | Mapping[str, Any] | None
    key_prefix: CoercibleToAssetKeyPrefix | None
    group_name: str | None
    partitions_def: PartitionsDefinition[str] | None
    hooks: AbstractSet[HookDefinition] | None
    metadata: RawMetadataMapping | None
    tags: Mapping[str, str] | None
    owners: Sequence[str] | None
    kinds: AbstractSet[str] | None

    # Automation / policies
    legacy_freshness_policy: LegacyFreshnessPolicy | None
    auto_materialize_policy: AutoMaterializePolicy | None
    automation_condition: AutomationCondition[AssetKey] | None
    backfill_policy: BackfillPolicy | None

    resource_defs: Mapping[str, ResourceDefinition] | None
    check_specs: Sequence[AssetCheckSpec] | None
    code_version: str | None
    key: CoercibleToAssetKey | None


class AssetDefinitonParamSpec(TypedDict, total=False):
    name: str
    key_prefix: CoercibleToAssetKeyPrefix
    metadata: dict[str, Any]
    io_manager_key: str
    io_manager_def: object
    key: CoercibleToAssetKey
    ins: Mapping[str, AssetIn]
    deps: Iterable[CoercibleToAssetDep] | None
    tags: Mapping[str, str]
    description: str
    config_schema: UserConfigSchema
    required_resource_keys: AbstractSet[str]
    resource_defs: Mapping[str, object]
    dagster_type: DagsterType
    partitions_def: PartitionsDefinition[str]
    op_tags: Mapping[str, Any]
    group_name: str | None
    output_required: bool
    automation_condition: AutomationCondition[AssetKey]
    backfill_policy: BackfillPolicy
    retry_policy: RetryPolicy
    code_version: str
    check_specs: Sequence[AssetCheckSpec]
    owners: Sequence[str]
    kinds: AbstractSet[str]
    pool: str
