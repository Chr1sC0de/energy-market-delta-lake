"""Central registry for bronze report configurations with decorator-based registration."""

from collections.abc import Callable
from typing import overload

from aemo_etl.configuration.report_config import ReportConfig

# Global registries - populated as config modules are imported
GASBB_CONFIGS: dict[str, ReportConfig] = {}
MIBB_CONFIGS: dict[str, ReportConfig] = {}


@overload
def gasbb_report(config: ReportConfig) -> ReportConfig: ...


@overload
def gasbb_report(func: Callable[[], ReportConfig]) -> ReportConfig: ...


def gasbb_report(
    config_or_func: ReportConfig | Callable[[], ReportConfig],
) -> ReportConfig:
    """Decorator to register a GASBB report config.

    Supports two usage patterns:

    1. As a decorator on a function (recommended):
        @gasbb_report
        def CONFIG() -> ReportConfig:
            return gasbb_config_factory(...)

    2. As a wrapper function:
        CONFIG = gasbb_report(gasbb_config_factory(...))

    Both patterns register the config in GASBB_CONFIGS and return it.

    Args:
        config_or_func: Either a config instance or a callable that returns a config

    Returns:
        The registered ReportConfig instance
    """
    # Check if it's a callable (function) or already a config
    if callable(config_or_func):
        # Pattern 1: decorator on function
        config = config_or_func()
    else:
        # Pattern 2: direct wrapper
        config = config_or_func

    GASBB_CONFIGS[config.table_name] = config
    return config


@overload
def mibb_report(config: ReportConfig) -> ReportConfig: ...


@overload
def mibb_report(func: Callable[[], ReportConfig]) -> ReportConfig: ...


def mibb_report(
    config_or_func: ReportConfig | Callable[[], ReportConfig],
) -> ReportConfig:
    """Decorator to register a MIBB report config.

    Supports two usage patterns:

    1. As a decorator on a function (recommended):
        @mibb_report
        def CONFIG() -> ReportConfig:
            return mibb_config_factory(...)

    2. As a wrapper function:
        CONFIG = mibb_report(mibb_config_factory(...))

    Both patterns register the config in MIBB_CONFIGS and return it.

    Args:
        config_or_func: Either a config instance or a callable that returns a config

    Returns:
        The registered ReportConfig instance
    """
    if callable(config_or_func):
        config = config_or_func()
    else:
        config = config_or_func

    MIBB_CONFIGS[config.table_name] = config
    return config
