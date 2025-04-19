from collections.abc import Callable
from typing import Any, TypedDict

import dagster as dg
import polars as pl


class MibbFactoryKwargs(TypedDict):
    group_name: str
    key_prefix: list[str]
    name: str
    schema: dict[str, type]
    search_prefix: str
    io_manager_key: str
    bucket: str
    description: str | None
    metadata: dict[str, Any] | None
    retention_hours: int
    compact_and_vacuum_cron_schedule: str | None
    execution_timezone: str
    check_factories: list[Callable[[dg.AssetsDefinition], dg.AssetChecksDefinition]]
    job_tags: dict[str, Any] | None
    post_process_hook: Callable[[pl.LazyFrame], pl.LazyFrame] | None
