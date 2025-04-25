from typing import Any, Callable

from dagster import AssetChecksDefinition, AssetsDefinition
from aemo_gas.vichub.assets.bronze.mibb.factory import MibbDeltaTableAssetFactoryConfig


class MibbDeltaTableDefinitionFactoryConfig(MibbDeltaTableAssetFactoryConfig):
    retention_hours: int | None = None
    compact_and_vacuum_cron_schedule: str | None = None
    execution_timezone: str | None = None
    check_factories: (
        list[Callable[[AssetsDefinition], AssetChecksDefinition]] | None
    ) = None
    job_tags: dict[str, Any] | None = None
