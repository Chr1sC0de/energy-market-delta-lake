"""Shared bounded read helpers for curated silver gas_model tables."""

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

import polars as pl

SILVER_GAS_MODEL_PREFIX = "silver/gas_model"


class BoundedReadConfig(Protocol):
    """Configuration fields that control bounded Marimo table reads."""

    @property
    def max_preview_rows(self) -> int:
        """Return the configured bounded preview row cap."""
        ...

    @property
    def full_table_scan_enabled(self) -> bool:
        """Return whether the runtime allows full table scans."""
        ...


class GasModelReadConfig(BoundedReadConfig, Protocol):
    """S3 configuration required to read configured gas_model tables."""

    def table_uri(self, table_name: str) -> str:
        """Return the S3 URI for a configured gas_model table."""
        ...

    def storage_options(self) -> dict[str, str]:
        """Return Polars S3 storage options for the configured runtime."""
        ...


class GasModelTableView(StrEnum):
    """Bounded table view shape requested by a dashboard helper."""

    SAMPLE = "sample"
    RECENT = "recent"


@dataclass(frozen=True)
class GasModelReadRequest:
    """One configured gas_model table read requested by a dashboard."""

    table_name: str
    view: GasModelTableView = GasModelTableView.SAMPLE
    date_columns: tuple[str, ...] = ()


@dataclass(frozen=True)
class GasModelTableLoad:
    """Loaded gas_model table or unavailable-state detail."""

    request: GasModelReadRequest
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None
    row_limit: int | None

    @property
    def table_name(self) -> str:
        """Return the configured gas_model table name."""
        return self.request.table_name

    @property
    def available(self) -> bool:
        """Return whether the table loaded and contains at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()

    @property
    def is_limited(self) -> bool:
        """Return whether the runtime applied a bounded preview row limit."""
        return self.row_limit is not None


TableReader = Callable[[str, Mapping[str, str], int | None], pl.DataFrame]


def bounded_row_limit(config: BoundedReadConfig) -> int | None:
    """Return the row limit that preserves the configured Marimo read policy."""
    if config.full_table_scan_enabled:
        return None
    return max(1, config.max_preview_rows)


def read_parquet_table(
    uri: str,
    storage_options: Mapping[str, str],
    row_limit: int | None = None,
) -> pl.DataFrame:
    """Read one gas_model Parquet prefix using Polars storage options."""
    scan = pl.scan_parquet(
        _parquet_dataset_glob(uri),
        storage_options=dict(storage_options),
    )
    if row_limit is not None:
        scan = scan.head(row_limit)
    return scan.collect()


def load_gas_model_read_request(
    config: GasModelReadConfig,
    request: GasModelReadRequest,
    reader: TableReader = read_parquet_table,
) -> GasModelTableLoad:
    """Load one configured gas_model table with bounded runtime behavior."""
    return load_gas_model_read_requests(config, (request,), reader=reader)[0]


def load_gas_model_read_requests(
    config: GasModelReadConfig,
    requests: Sequence[GasModelReadRequest],
    reader: TableReader = read_parquet_table,
) -> list[GasModelTableLoad]:
    """Load configured gas_model tables, returning empty-state details on errors."""
    storage_options = config.storage_options()
    row_limit = bounded_row_limit(config)
    loads: list[GasModelTableLoad] = []

    for request in requests:
        uri = config.table_uri(request.table_name)
        try:
            dataframe = reader(uri, storage_options, row_limit)
        except Exception as error:
            loads.append(
                GasModelTableLoad(
                    request=request,
                    uri=uri,
                    dataframe=None,
                    error=compact_error(error),
                    row_limit=row_limit,
                )
            )
            continue

        loads.append(
            GasModelTableLoad(
                request=request,
                uri=uri,
                dataframe=gas_model_table_view(dataframe, request),
                error=None,
                row_limit=row_limit,
            )
        )

    return loads


def gas_model_table_view(
    dataframe: pl.DataFrame,
    request: GasModelReadRequest,
) -> pl.DataFrame:
    """Apply a dashboard-requested view to an already bounded table load."""
    if dataframe.is_empty() or request.view == GasModelTableView.SAMPLE:
        return dataframe

    sort_columns = [
        column for column in request.date_columns if column in dataframe.columns
    ]
    if not sort_columns:
        return dataframe

    return dataframe.sort(
        sort_columns,
        descending=[True] * len(sort_columns),
        nulls_last=True,
    )


def compact_error(error: Exception) -> str:
    """Return a single-line error detail suitable for dashboard empty states."""
    message = str(error).strip().splitlines()
    if not message:
        return error.__class__.__name__
    return f"{error.__class__.__name__}: {message[0]}"


def _parquet_dataset_glob(uri: str) -> str:
    return f"{uri.rstrip('/')}/*.parquet"
