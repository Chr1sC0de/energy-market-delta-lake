from . import config
from . import mibb

definitions = [
    mibb.downloaded_public_files.definition,
    *[mibb.factory(**c) for c in config.all],
]

__all__ = ["config", "mibb"]
