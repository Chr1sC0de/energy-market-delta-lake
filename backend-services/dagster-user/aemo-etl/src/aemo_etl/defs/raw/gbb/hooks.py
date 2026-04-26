"""
GBB-specific Hook[bytes] implementations.

These hooks preprocess raw S3 file bytes before they are parsed into a LazyFrame
by the df_from_s3_keys asset factory.  Preprocessing at the bytes level is
necessary for transformations that affect columns referenced by the surrogate-key
expression (which is computed during LazyFrame construction, before any
LazyFrame-level hooks would run).
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING

import polars as pl

from aemo_etl.factories.df_from_s3_keys.hooks import Hook

if TYPE_CHECKING:
    from polars._typing import PolarsDataType


class EnsureColumnsHook(Hook[bytes]):
    """Add missing columns to a parquet file with a null literal of the given type.

    Use this when different vintages of the same source file omit certain
    columns, causing surrogate-key expressions to fail schema resolution.
    """

    def __init__(self, columns: list[tuple[str, PolarsDataType]]) -> None:
        self._columns = columns

    def process(self, s3_bucket: str, s3_key: str, object_: bytes) -> bytes:
        df = pl.read_parquet(io.BytesIO(object_))
        missing = [
            (name, dtype) for name, dtype in self._columns if name not in df.columns
        ]
        if not missing:
            return object_
        df = df.with_columns(
            [pl.lit(None, dtype=dtype).alias(name) for name, dtype in missing]
        )
        out = io.BytesIO()
        df.write_parquet(out)
        return out.getvalue()


class LowercaseColumnsHook(Hook[bytes]):
    """Rename all parquet columns to lowercase.

    Use this when source files have inconsistent casing across vintages and the
    target schema uses lowercase column names.
    """

    def process(self, s3_bucket: str, s3_key: str, object_: bytes) -> bytes:
        df = pl.read_parquet(io.BytesIO(object_))
        keep_by_lowercase: dict[str, str] = {}
        columns_to_drop: list[str] = []
        for column in df.columns:
            lowercase_column = column.lower()
            existing = keep_by_lowercase.get(lowercase_column)
            if existing is None:
                keep_by_lowercase[lowercase_column] = column
                continue
            if existing == lowercase_column:
                columns_to_drop.append(column)
                continue
            if column == lowercase_column:
                columns_to_drop.append(existing)
                keep_by_lowercase[lowercase_column] = column
                continue
            columns_to_drop.append(column)
        rename_map = {
            column: column.lower()
            for column in df.columns
            if column != column.lower() and column not in columns_to_drop
        }
        if not columns_to_drop and not rename_map:
            return object_
        if columns_to_drop:
            df = df.drop(columns_to_drop)
        if not rename_map:
            out = io.BytesIO()
            df.write_parquet(out)
            return out.getvalue()
        df = df.rename(rename_map)
        out = io.BytesIO()
        df.write_parquet(out)
        return out.getvalue()


class GshGasTradesParseHook(Hook[bytes]):
    """Strip AEMO NEMWEB envelope rows and leading metadata columns from a GSH
    gas-trades CSV file.

    The raw file format is::

        C,NEMP.WORLD,GSH_GAS_TRADES_WEB,...          <- file metadata (row 0)
        I,GSH,GAS_TRADES,1,TRADE_DATE,TYPE,...       <- header + 4 prefix cols
        D,GSH,GAS_TRADES,1,"2026/04/11",...          <- data rows + 4 prefix cols
        ...
        C,"END OF REPORT",...                         <- footer rows (last 2)

    After the hook the output is a plain CSV with the correct headers and data.
    """

    def process(self, s3_bucket: str, s3_key: str, object_: bytes) -> bytes:
        lines = object_.decode("utf-8").replace("\r\n", "\n").split("\n")
        # lines[0]    – file-level metadata row, skip
        # lines[1:-2] – header + data rows, each with 4 leading metadata cols
        # lines[-2:]  – footer rows, skip
        csv_string = "\n".join(
            ",".join(line.split(",")[4:]) for line in lines[1:-2]
        ).encode()
        return csv_string


_FORECAST_FIXED_COLS: frozenset[str] = frozenset(
    [
        "State",
        "FacilityId",
        "FacilityName",
        "FacilityType",
        "ReceiptLocationId",
        "ReceiptLocationName",
        "DeliveryLocationId",
        "DeliveryLocationName",
        "Description",
        "ForecastMethod",
        "Units",
        "Nameplate",
    ]
)


class ForecastUtilisationUnpivotHook(Hook[bytes]):
    """Unpivot a wide-format forecast-utilisation parquet from AEMO to long format.

    The source file has one column per forecast date::

        State | FacilityId | ... | Thursday 5 Aug 2021 | Friday 6 Aug 2021 | ...

    This hook unpivots those date columns to::

        (
            State
            | FacilityId
            | ...
            | ForecastDate
            | ForecastValue
            | ForecastDay
            | ForecastedFrom
        )

    ``ForecastDay`` and ``ForecastedFrom`` are not present in the raw file and
    are set to ``null``; they can be populated by a downstream transformation
    once the porting of the legacy hook is complete.
    """

    def process(self, s3_bucket: str, s3_key: str, object_: bytes) -> bytes:
        df = pl.read_parquet(io.BytesIO(object_))
        date_cols = [c for c in df.columns if c not in _FORECAST_FIXED_COLS]
        if not date_cols:
            return object_
        index_cols = [c for c in df.columns if c in _FORECAST_FIXED_COLS]
        df = df.unpivot(
            on=date_cols,
            index=index_cols,
            variable_name="ForecastDate",
            value_name="ForecastValue",
        ).with_columns(
            ForecastDay=pl.lit(None, dtype=pl.String),
            ForecastedFrom=pl.lit(None, dtype=pl.String),
        )
        out = io.BytesIO()
        df.write_parquet(out)
        return out.getvalue()
