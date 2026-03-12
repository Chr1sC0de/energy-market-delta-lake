from typing import AbstractSet, Any, Mapping, Sequence, TypedDict

from dagster import (
    AssetCheckSpec,
    AssetIn,
    AssetKey,
    AutoMaterializePolicy,
    AutomationCondition,
    BackfillPolicy,
    ConfigMapping,
    HookDefinition,
    LegacyFreshnessPolicy,
    PartitionsDefinition,
    ResourceDefinition,
)
from dagster._core.definitions.asset_key import (
    CoercibleToAssetKey,
    CoercibleToAssetKeyPrefix,
)
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
