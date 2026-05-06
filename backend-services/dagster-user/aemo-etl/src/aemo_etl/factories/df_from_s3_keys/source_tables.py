"""Registry for source-table bronze definitions."""

import importlib
import pkgutil
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

from polars import LazyFrame
from polars._typing import PolarsDataType

from aemo_etl.configs import AEMO_BUCKET
from aemo_etl.factories.df_from_s3_keys.hooks import Hook

RAW_SOURCE_TABLE_PACKAGES: Final = (
    "aemo_etl.defs.raw.gbb",
    "aemo_etl.defs.raw.sttm",
    "aemo_etl.defs.raw.vicgas",
)


@dataclass(frozen=True, slots=True)
class DFFromS3KeysSourceTableSpec:
    """Replay-relevant configuration for one source-table bronze asset."""

    domain: str
    name_suffix: str
    glob_pattern: str
    schema: Mapping[str, PolarsDataType]
    surrogate_key_sources: tuple[str, ...]
    postprocess_object_hooks: tuple[Hook[bytes], ...] = ()
    postprocess_lazyframe_hooks: tuple[Hook[LazyFrame], ...] = ()

    @property
    def bronze_table_name(self) -> str:
        """Return the bronze table asset name."""
        return f"bronze_{self.name_suffix}"

    @property
    def archive_prefix(self) -> str:
        """Return the source archive prefix for this table's domain."""
        return f"bronze/{self.domain}"

    @property
    def table_id(self) -> str:
        """Return a stable domain-qualified table identifier."""
        return f"{self.domain}.{self.bronze_table_name}"

    def target_table_uri(self, aemo_bucket: str = AEMO_BUCKET) -> str:
        """Return the Delta table URI for this bronze asset."""
        return f"s3://{aemo_bucket}/bronze/{self.domain}/{self.bronze_table_name}"

    def matches_table(self, table: str) -> bool:
        """Return whether a CLI table selector refers to this source table."""
        normalized = table.strip().strip("/")
        return normalized in {
            self.name_suffix,
            self.bronze_table_name,
            f"{self.domain}.{self.name_suffix}",
            f"{self.domain}.{self.bronze_table_name}",
            f"bronze/{self.domain}/{self.name_suffix}",
            f"bronze/{self.domain}/{self.bronze_table_name}",
        }


_SOURCE_TABLE_SPECS: dict[tuple[str, str], DFFromS3KeysSourceTableSpec] = {}


def register_source_table_spec(spec: DFFromS3KeysSourceTableSpec) -> None:
    """Register one source-table spec by domain and suffix."""
    _SOURCE_TABLE_SPECS[(spec.domain, spec.name_suffix)] = spec


def get_registered_source_table_specs() -> tuple[DFFromS3KeysSourceTableSpec, ...]:
    """Return registered source-table specs in stable order."""
    return tuple(_SOURCE_TABLE_SPECS[key] for key in sorted(_SOURCE_TABLE_SPECS))


def load_source_table_specs() -> tuple[DFFromS3KeysSourceTableSpec, ...]:
    """Import raw source-table modules and return their registered specs."""
    for package_name in RAW_SOURCE_TABLE_PACKAGES:
        package = importlib.import_module(package_name)
        package_paths = getattr(package, "__path__", ())
        for module_info in pkgutil.iter_modules(package_paths, f"{package.__name__}."):
            if not module_info.ispkg:
                importlib.import_module(module_info.name)

    return get_registered_source_table_specs()


def select_source_table_specs(
    specs: tuple[DFFromS3KeysSourceTableSpec, ...],
    *,
    include_all: bool = False,
    domain: str | None = None,
    table: str | None = None,
) -> tuple[DFFromS3KeysSourceTableSpec, ...]:
    """Select source-table specs for all tables, one domain, or one table."""
    selected_modes = int(include_all) + int(domain is not None) + int(table is not None)
    if selected_modes != 1:
        raise ValueError("select exactly one of all, domain, or table")

    if include_all:
        return specs

    if domain is not None:
        selected = tuple(spec for spec in specs if spec.domain == domain)
        if not selected:
            raise ValueError(f"unknown source-table domain: {domain}")
        return selected

    assert table is not None
    selected = tuple(spec for spec in specs if spec.matches_table(table))
    if not selected:
        raise ValueError(f"unknown source table: {table}")
    if len(selected) > 1:
        table_ids = ", ".join(spec.table_id for spec in selected)
        raise ValueError(f"ambiguous source table {table}: {table_ids}")
    return selected
