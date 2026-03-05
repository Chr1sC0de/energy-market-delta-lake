from typing import AbstractSet, Any, Mapping, TypedDict

from dagster import In, Out, RetryPolicy
from dagster._config.config_schema import UserConfigSchema


class OpKwargs(TypedDict, total=False):
    name: str | None
    description: str | None
    ins: Mapping[str, In] | None
    out: Out | Mapping[str, Out] | None
    config_schema: UserConfigSchema | None
    required_resource_keys: AbstractSet[str] | None
    tags: Mapping[str, Any] | None
    version: str | None  # deprecated in Dagster 2.0
    retry_policy: RetryPolicy | None
    code_version: str | None
    pool: str | None
