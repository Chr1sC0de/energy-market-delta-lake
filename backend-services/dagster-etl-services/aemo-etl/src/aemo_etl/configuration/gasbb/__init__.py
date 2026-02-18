import pathlib as pt
from importlib import import_module

# Get all bronze_*.py files in this directory
_config_dir = pt.Path(__file__).parent
_config_modules = [
    f.stem
    for f in _config_dir.glob("bronze_*.py")
    if f.is_file() and not f.name.startswith("_")
]

# Dynamically import all configuration modules
for _module_name in _config_modules:
    globals()[_module_name] = import_module(f".{_module_name}", package=__name__)

# Re-export the registry for easy access
from aemo_etl.configuration.registry import GASBB_CONFIGS

__all__ = _config_modules + ["GASBB_CONFIGS"]
