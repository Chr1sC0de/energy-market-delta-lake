"""Shared bounded read helpers for curated silver gas_model tables."""

from collections.abc import Callable, Hashable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from time import perf_counter
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
class GasModelTableRead:
    """Raw gas_model table read cached for a Marimo notebook session."""

    table_name: str
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None
    row_limit: int | None
    load_duration_seconds: float

    @property
    def available(self) -> bool:
        """Return whether the table read produced at least one row."""
        return self.dataframe is not None and not self.dataframe.is_empty()

    @property
    def is_limited(self) -> bool:
        """Return whether the runtime applied a bounded preview row limit."""
        return self.row_limit is not None


@dataclass(frozen=True)
class GasModelTableLoad:
    """Loaded gas_model table or unavailable-state detail."""

    request: GasModelReadRequest
    uri: str
    dataframe: pl.DataFrame | None
    error: str | None
    row_limit: int | None
    load_duration_seconds: float
    cache_hit: bool = False

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
Clock = Callable[[], float]
GasModelTableCacheKey = tuple[
    str,
    str,
    tuple[tuple[str, str], ...],
    int | None,
    Hashable,
]
GasModelSessionCache = MutableMapping[GasModelTableCacheKey, GasModelTableRead]
_REFRESH_CONTROL_STATE_ATTRIBUTE = "_emdl_refresh_control_state"


@dataclass(frozen=True)
class _RefreshControlState:
    token: int = 0
    previous_value: bool = False


def bounded_row_limit(config: BoundedReadConfig) -> int | None:
    """Return the row limit that preserves the configured Marimo read policy."""
    if config.full_table_scan_enabled:
        return None
    return max(1, config.max_preview_rows)


def read_parquet_table(
    uri: str,
    storage_options: Mapping[str, str],
    row_limit: int | None = None,
    filter_expression: pl.Expr | None = None,
) -> pl.DataFrame:
    """Read one gas_model Parquet prefix using Polars storage options."""
    scan = pl.scan_parquet(
        _parquet_dataset_glob(uri),
        storage_options=dict(storage_options),
    )
    if filter_expression is not None:
        scan = scan.filter(filter_expression)
    if row_limit is not None:
        scan = scan.head(row_limit)
    return scan.collect()


def load_gas_model_read_request(
    config: GasModelReadConfig,
    request: GasModelReadRequest,
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> GasModelTableLoad:
    """Load one configured gas_model table with bounded runtime behavior."""
    return load_gas_model_read_requests(
        config,
        (request,),
        reader=reader,
        clock=clock,
    )[0]


def load_gas_model_read_requests(
    config: GasModelReadConfig,
    requests: Sequence[GasModelReadRequest],
    reader: TableReader = read_parquet_table,
    *,
    clock: Clock = perf_counter,
) -> list[GasModelTableLoad]:
    """Load configured gas_model tables, returning empty-state details on errors."""
    storage_options = config.storage_options()
    row_limit = bounded_row_limit(config)
    loads: list[GasModelTableLoad] = []

    for request in requests:
        uri = config.table_uri(request.table_name)
        table_read = _read_gas_model_table(
            request.table_name,
            uri,
            storage_options,
            row_limit,
            reader,
            clock,
        )
        loads.append(_table_load_from_read(request, table_read, cache_hit=False))

    return loads


def cached_gas_model_read_requests(
    config: GasModelReadConfig,
    requests: Sequence[GasModelReadRequest],
    cache: GasModelSessionCache,
    reader: TableReader = read_parquet_table,
    *,
    refresh_token: Hashable = 0,
    clock: Clock = perf_counter,
) -> list[GasModelTableLoad]:
    """Return session-cached gas_model table reads for explicit-refresh dashboards."""
    storage_options = config.storage_options()
    row_limit = bounded_row_limit(config)
    storage_fingerprint = _storage_options_fingerprint(storage_options)
    loads: list[GasModelTableLoad] = []

    for request in requests:
        uri = config.table_uri(request.table_name)
        cache_key = (
            request.table_name,
            uri,
            storage_fingerprint,
            row_limit,
            refresh_token,
        )
        if cache_key in cache:
            table_read = cache[cache_key]
            loads.append(_table_load_from_read(request, table_read, cache_hit=True))
            continue

        table_read = _read_gas_model_table(
            request.table_name,
            uri,
            storage_options,
            row_limit,
            reader,
            clock,
        )
        cache[cache_key] = table_read
        loads.append(_table_load_from_read(request, table_read, cache_hit=False))

    return loads


def refresh_token_from_control(refresh_control: object | None) -> Hashable:
    """Return a stable cache token from a Marimo explicit refresh control."""
    if refresh_control is None:
        return 0

    value = getattr(refresh_control, "value", 0)
    if isinstance(value, bool):
        return _refresh_token_from_boolean_control(refresh_control, value)
    if isinstance(value, Hashable):
        return value
    return repr(value)


def _refresh_token_from_boolean_control(
    refresh_control: object,
    value: bool,
) -> int:
    state = getattr(refresh_control, _REFRESH_CONTROL_STATE_ATTRIBUTE, None)
    if not isinstance(state, _RefreshControlState):
        state = _RefreshControlState()

    if value and not state.previous_value:
        state = _RefreshControlState(
            token=state.token + 1,
            previous_value=True,
        )
    else:
        state = _RefreshControlState(
            token=state.token,
            previous_value=value,
        )

    setattr(refresh_control, _REFRESH_CONTROL_STATE_ATTRIBUTE, state)
    return state.token


def format_load_duration(duration_seconds: float) -> str:
    """Format a measured table-load duration for dashboard display."""
    if duration_seconds < 0.001:
        return "<1 ms"
    if duration_seconds < 1:
        return f"{duration_seconds * 1000:.0f} ms"
    return f"{duration_seconds:.2f} s"


def format_row_limit(row_limit: int | None) -> str:
    """Format row-limit policy for a dashboard diagnostics table."""
    if row_limit is None:
        return "Full table scan"
    return f"Bounded preview: {row_limit:,} rows max"


def row_limit_message(row_limit: int | None) -> str:
    """Return row-limit policy copy for shared dashboard load status."""
    if row_limit is None:
        return "Full table scans are enabled; row counts reflect loaded table data."
    return (
        f"Bounded preview reads are capped at `{row_limit:,}` rows per table by "
        "`MARIMO_MAX_PREVIEW_ROWS`."
    )


def cache_status_label(cache_hit: bool) -> str:
    """Format whether a table read came from the notebook session cache."""
    if cache_hit:
        return "Session cache hit"
    return "Refreshed read"


def _read_gas_model_table(
    table_name: str,
    uri: str,
    storage_options: Mapping[str, str],
    row_limit: int | None,
    reader: TableReader,
    clock: Clock,
) -> GasModelTableRead:
    start_time = clock()
    try:
        dataframe = reader(uri, storage_options, row_limit)
    except Exception as error:
        return GasModelTableRead(
            table_name=table_name,
            uri=uri,
            dataframe=None,
            error=compact_error(error),
            row_limit=row_limit,
            load_duration_seconds=_elapsed_seconds(start_time, clock),
        )

    return GasModelTableRead(
        table_name=table_name,
        uri=uri,
        dataframe=dataframe,
        error=None,
        row_limit=row_limit,
        load_duration_seconds=_elapsed_seconds(start_time, clock),
    )


def _table_load_from_read(
    request: GasModelReadRequest,
    table_read: GasModelTableRead,
    *,
    cache_hit: bool,
) -> GasModelTableLoad:
    if table_read.dataframe is None:
        return GasModelTableLoad(
            request=request,
            uri=table_read.uri,
            dataframe=None,
            error=table_read.error,
            row_limit=table_read.row_limit,
            load_duration_seconds=table_read.load_duration_seconds,
            cache_hit=cache_hit,
        )
    return GasModelTableLoad(
        request=request,
        uri=table_read.uri,
        dataframe=gas_model_table_view(table_read.dataframe, request),
        error=table_read.error,
        row_limit=table_read.row_limit,
        load_duration_seconds=table_read.load_duration_seconds,
        cache_hit=cache_hit,
    )


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


def _storage_options_fingerprint(
    storage_options: Mapping[str, str],
) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((key, str(value)) for key, value in storage_options.items()))


def _elapsed_seconds(start_time: float, clock: Clock) -> float:
    return max(0.0, clock() - start_time)
