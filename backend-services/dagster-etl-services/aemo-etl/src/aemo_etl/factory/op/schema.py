from typing import AbstractSet, Any, Mapping, NotRequired, TypedDict

from dagster import In, Out, RetryPolicy
from dagster._config import UserConfigSchema


class OpKwargs(TypedDict):
    name: NotRequired[str]
    description: NotRequired[str]
    ins: NotRequired[Mapping[str, In]]
    out: NotRequired[Out | Mapping[str, Out]]
    config_schema: NotRequired[UserConfigSchema]
    required_resource_keys: NotRequired[AbstractSet[str]]
    tags: NotRequired[Mapping[str, Any]]
    version: NotRequired[str]
    retry_policy: NotRequired[RetryPolicy]
    code_version: NotRequired[str]
    pool: NotRequired[str]
