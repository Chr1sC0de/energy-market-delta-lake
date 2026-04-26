"""Unit tests for defs/raw/gbb/hooks.py – all four hook classes."""

import io
import tempfile

import polars as pl

from aemo_etl.defs.raw.gbb.hooks import (
    EnsureColumnsHook,
    ForecastUtilisationUnpivotHook,
    GshGasTradesParseHook,
    LowercaseColumnsHook,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parquet_bytes(df: pl.DataFrame) -> bytes:
    buf = io.BytesIO()
    df.write_parquet(buf)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# EnsureColumnsHook
# ---------------------------------------------------------------------------


def test_ensure_columns_hook_all_present() -> None:
    """No-op when all required columns already exist."""
    df = pl.DataFrame({"col1": [1], "col2": ["a"]})
    original = _parquet_bytes(df)
    hook = EnsureColumnsHook([("col1", pl.Int64), ("col2", pl.String)])
    result = hook.process("bucket", "key", original)
    assert result == original  # unchanged


def test_ensure_columns_hook_missing_column() -> None:
    """Missing column is added with null values."""
    df = pl.DataFrame({"col1": [1]})
    raw = _parquet_bytes(df)
    hook = EnsureColumnsHook([("col1", pl.Int64), ("col2", pl.String)])
    result = hook.process("bucket", "key", raw)
    out_df = pl.read_parquet(io.BytesIO(result))
    assert "col2" in out_df.columns
    assert out_df["col2"].dtype == pl.String


# ---------------------------------------------------------------------------
# LowercaseColumnsHook
# ---------------------------------------------------------------------------


def test_lowercase_columns_hook_already_lowercase() -> None:
    df = pl.DataFrame({"lowercase_col": [1]})
    original = _parquet_bytes(df)
    hook = LowercaseColumnsHook()
    result = hook.process("bucket", "key", original)
    assert result == original


def test_lowercase_columns_hook_mixed_case() -> None:
    df = pl.DataFrame({"ColA": [1], "ColB": ["x"]})
    raw = _parquet_bytes(df)
    hook = LowercaseColumnsHook()
    result = hook.process("bucket", "key", raw)
    out_df = pl.read_parquet(io.BytesIO(result))
    assert "cola" in out_df.columns
    assert "colb" in out_df.columns


def test_lowercase_columns_hook_drops_mixed_case_duplicates() -> None:
    df = pl.DataFrame(
        {
            "receiptlocationname": ["declared"],
            "receiptlocationName": ["duplicate"],
            "DeliveryLocationName": ["mixed"],
        }
    )
    raw = _parquet_bytes(df)
    hook = LowercaseColumnsHook()

    result = hook.process("bucket", "key", raw)

    out_df = pl.read_parquet(io.BytesIO(result))
    assert out_df.columns == ["receiptlocationname", "deliverylocationname"]
    assert out_df["receiptlocationname"].to_list() == ["declared"]
    assert out_df["deliverylocationname"].to_list() == ["mixed"]


def test_lowercase_columns_hook_deduplicates_mixed_case_pair() -> None:
    df = pl.DataFrame({"ReceiptLocationName": ["kept"], "receiptlocationName": ["dup"]})
    raw = _parquet_bytes(df)
    hook = LowercaseColumnsHook()

    result = hook.process("bucket", "key", raw)

    out_df = pl.read_parquet(io.BytesIO(result))
    assert out_df.columns == ["receiptlocationname"]
    assert out_df["receiptlocationname"].to_list() == ["kept"]


def test_lowercase_columns_hook_prefers_existing_lowercase_duplicate() -> None:
    df = pl.DataFrame(
        {
            "ReceiptLocationName": ["mixed"],
            "receiptlocationname": ["lowercase"],
        }
    )
    raw = _parquet_bytes(df)
    hook = LowercaseColumnsHook()

    result = hook.process("bucket", "key", raw)

    out_df = pl.read_parquet(io.BytesIO(result))
    assert out_df.columns == ["receiptlocationname"]
    assert out_df["receiptlocationname"].to_list() == ["lowercase"]


def test_lowercase_columns_hook_drops_duplicate_without_renaming() -> None:
    df = pl.DataFrame({"cola": ["lowercase"], "Cola": ["mixed"]})
    raw = _parquet_bytes(df)
    hook = LowercaseColumnsHook()

    result = hook.process("bucket", "key", raw)

    out_df = pl.read_parquet(io.BytesIO(result))
    assert out_df.columns == ["cola"]
    assert out_df["cola"].to_list() == ["lowercase"]


def test_lowercase_columns_hook_normalizes_archived_nameplate_variants_for_delta() -> (
    None
):
    archived_full_file = pl.DataFrame(
        {
            "FacilityName": ["full"],
            "facilityid": [1],
            "ReceiptLocationName": ["receipt"],
            "DeliveryLocationName": ["delivery"],
            "LastUpdated": ["2026-04-25"],
        }
    )
    archived_current_file = pl.DataFrame(
        {
            "facilityname": ["current"],
            "facilityid": [2],
            "ReceiptLocationName": ["receipt"],
            "DeliveryLocationName": ["delivery"],
            "LastUpdated": ["2026-04-25"],
        }
    )
    hook = LowercaseColumnsHook()

    with tempfile.TemporaryDirectory() as tmp_dir:
        table_uri = f"{tmp_dir}/nameplate"
        for source in [archived_full_file, archived_current_file]:
            processed = pl.read_parquet(
                io.BytesIO(
                    hook.process("archive", "nameplate.parquet", _parquet_bytes(source))
                )
            )
            processed.lazy().sink_delta(table_uri, mode="append")

        out_schema = pl.scan_delta(table_uri).collect_schema()

    assert out_schema.names() == [
        "facilityname",
        "facilityid",
        "receiptlocationname",
        "deliverylocationname",
        "lastupdated",
    ]


# ---------------------------------------------------------------------------
# GshGasTradesParseHook
# ---------------------------------------------------------------------------


def test_gsh_gas_trades_parse_hook() -> None:
    """Strips NEMWEB envelope and leading metadata columns."""
    # Format:
    # row0: file metadata (skip)
    # row1: header with 4 leading cols + real headers
    # row2+: data with 4 leading cols + real data
    # last 2 rows: footer (skip)
    raw_csv = (
        "C,NEMP.WORLD,GSH_GAS_TRADES_WEB,meta1,meta2\r\n"
        "I,GSH,GAS_TRADES,1,TRADE_DATE,TYPE,PRICE\r\n"
        'D,GSH,GAS_TRADES,1,"2024-01-01",spot,100\r\n'
        "C,END OF REPORT\r\n"
        "\r\n"
    )
    hook = GshGasTradesParseHook()
    result = hook.process("bucket", "key", raw_csv.encode())
    # Result should be CSV with TRADE_DATE,TYPE,PRICE header + data row
    text = result.decode()
    assert "TRADE_DATE" in text
    assert "2024-01-01" in text
    # Leading metadata columns should be stripped
    assert "GSH" not in text


# ---------------------------------------------------------------------------
# ForecastUtilisationUnpivotHook
# ---------------------------------------------------------------------------


def test_forecast_utilisation_unpivot_hook_no_date_cols() -> None:
    """No-op when all columns are fixed (no date columns)."""
    df = pl.DataFrame(
        {
            "State": ["VIC"],
            "FacilityId": [1],
            "FacilityName": ["test"],
            "FacilityType": ["gas"],
            "ReceiptLocationId": [10],
            "ReceiptLocationName": ["RL"],
            "DeliveryLocationId": [20],
            "DeliveryLocationName": ["DL"],
            "Description": ["desc"],
            "ForecastMethod": ["method"],
            "Units": ["TJ"],
            "Nameplate": [100.0],
        }
    )
    raw = _parquet_bytes(df)
    hook = ForecastUtilisationUnpivotHook()
    result = hook.process("bucket", "key", raw)
    assert result == raw  # unchanged


def test_forecast_utilisation_unpivot_hook_with_date_cols() -> None:
    """Date columns are unpivoted to long format."""
    df = pl.DataFrame(
        {
            "State": ["VIC"],
            "FacilityId": [1],
            "FacilityName": ["test"],
            "FacilityType": ["gas"],
            "ReceiptLocationId": [10],
            "ReceiptLocationName": ["RL"],
            "DeliveryLocationId": [20],
            "DeliveryLocationName": ["DL"],
            "Description": ["desc"],
            "ForecastMethod": ["method"],
            "Units": ["TJ"],
            "Nameplate": [100.0],
            "Thursday 5 Aug 2021": [50.0],
            "Friday 6 Aug 2021": [60.0],
        }
    )
    raw = _parquet_bytes(df)
    hook = ForecastUtilisationUnpivotHook()
    result = hook.process("bucket", "key", raw)
    out_df = pl.read_parquet(io.BytesIO(result))
    assert "ForecastDate" in out_df.columns
    assert "ForecastValue" in out_df.columns
    assert "ForecastDay" in out_df.columns
    assert "ForecastedFrom" in out_df.columns
    # 2 date cols × 1 row = 2 rows
    assert len(out_df) == 2
