from collections.abc import Callable
from typing import Any, TypedDict, NotRequired

import dagster as dg
import polars as pl


class MibbFactoryKwargs(TypedDict):
    group_name: str
    key_prefix: list[str]
    name: str
    schema: dict[str, Any]
    search_prefix: str
    io_manager_key: str
    bucket: NotRequired[str]
    description: NotRequired[str]
    metadata: NotRequired[dict[str, Any]]
    retention_hours: NotRequired[int]
    compact_and_vacuum_cron_schedule: NotRequired[str]
    execution_timezone: NotRequired[str]
    check_factories: NotRequired[
        list[Callable[[dg.AssetsDefinition], dg.AssetChecksDefinition]]
    ]
    job_tags: NotRequired[dict[str, Any]]
    post_process_hook: NotRequired[Callable[[pl.LazyFrame], pl.LazyFrame]]
