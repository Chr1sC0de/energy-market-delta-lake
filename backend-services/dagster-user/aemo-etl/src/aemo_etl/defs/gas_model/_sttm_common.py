"""Shared helpers for STTM silver gas_model facts."""

import polars as pl
from dagster import AssetKey
from polars import LazyFrame

from aemo_etl.defs.gas_model._parsing import parse_gas_datetime

SOURCE_SYSTEM = "STTM"
PARTICIPANTS_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_participant"])
FACILITIES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_facility"])
ZONES_KEY = AssetKey(["silver", "gas_model", "silver_gas_dim_zone"])


def source_table(name_suffix: str) -> str:
    """Return the silver STTM source table name for a manifest report suffix."""
    return f"silver.sttm.silver_{name_suffix}"


def source_asset_key(name_suffix: str) -> AssetKey:
    """Return the silver STTM source asset key for a manifest report suffix."""
    return AssetKey(["silver", "sttm", f"silver_{name_suffix}"])


def parse_datetime(column: str) -> pl.Expr:
    """Parse a gas source date or timestamp column."""
    return parse_gas_datetime(column)


def source_metadata(
    *,
    table_name: str,
    report_id: str,
    updated_column: str = "report_datetime",
) -> tuple[pl.Expr, ...]:
    """Return common STTM source lineage expressions for a source table."""
    return (
        pl.lit(SOURCE_SYSTEM).alias("source_system"),
        pl.lit([table_name]).cast(pl.List(pl.String)).alias("source_tables"),
        pl.lit(table_name).alias("source_table"),
        pl.lit(report_id).alias("source_report_id"),
        pl.col(updated_column).cast(pl.String).alias("source_last_updated"),
        parse_datetime(updated_column).alias("source_last_updated_timestamp"),
        pl.col("surrogate_key").cast(pl.String).alias("source_surrogate_key"),
        pl.col("source_file").cast(pl.String).alias("source_file"),
        pl.col("ingested_timestamp").alias("ingested_timestamp"),
    )


def with_facility_zone_keys(
    df: LazyFrame,
    facilities: LazyFrame,
    zones: LazyFrame,
) -> LazyFrame:
    """Attach conformed STTM facility and hub zone keys where resolvable."""
    facility_keys = facilities.filter(pl.col("source_system") == SOURCE_SYSTEM).select(
        facility_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_hub_id"),
        source_facility_id=pl.col("source_facility_id"),
    )
    zone_keys = zones.filter(
        (pl.col("source_system") == SOURCE_SYSTEM) & (pl.col("zone_type") == "sttm_hub")
    ).select(
        zone_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_zone_id"),
    )
    return df.join(
        facility_keys,
        on=["source_system", "source_hub_id", "source_facility_id"],
        how="left",
    ).join(zone_keys, on=["source_system", "source_hub_id"], how="left")


def with_zone_key(df: LazyFrame, zones: LazyFrame) -> LazyFrame:
    """Attach the conformed STTM hub zone key where resolvable."""
    zone_keys = zones.filter(
        (pl.col("source_system") == SOURCE_SYSTEM) & (pl.col("zone_type") == "sttm_hub")
    ).select(
        zone_key=pl.col("surrogate_key"),
        source_system=pl.col("source_system"),
        source_hub_id=pl.col("source_zone_id"),
    )
    return df.join(zone_keys, on=["source_system", "source_hub_id"], how="left")


def with_participant_key(
    df: LazyFrame,
    participants: LazyFrame,
    *,
    participant_id_column: str = "participant_id",
) -> LazyFrame:
    """Attach the conformed STTM participant key for source company identifiers."""
    participant_keys = participants.filter(
        pl.col("participant_identity_source") == "company_id"
    ).select(
        participant_key=pl.col("surrogate_key"),
        **{participant_id_column: pl.col("participant_identity_value")},
    )
    return df.join(participant_keys, on=participant_id_column, how="left")
