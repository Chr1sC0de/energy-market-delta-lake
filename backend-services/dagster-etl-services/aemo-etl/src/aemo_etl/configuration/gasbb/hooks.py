"""GASBB Custom Processing Hooks Registry.

This module centralizes all custom data processing functions for GASBB reports.
Most reports use standard processing, but ~10 reports need special handling.
"""

from datetime import timedelta
from logging import Logger
from typing import Protocol

from dagster import AssetExecutionContext
from polars import LazyFrame, col, lit, read_csv

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class PreprocessHook(Protocol):
    """Protocol for preprocess hooks that transform LazyFrames before standard processing."""

    def __call__(self, logger: Logger | None, df: LazyFrame) -> LazyFrame: ...


class ProcessObjectHook(Protocol):
    """Protocol for process_object hooks that parse raw bytes into LazyFrames."""

    def __call__(self, logger: Logger | None, contents: bytes) -> LazyFrame: ...


class PostProcessHook(Protocol):
    """Protocol for post-process hooks that apply custom deduplication logic."""

    def __call__(
        self,
        context: AssetExecutionContext,
        df: LazyFrame,
        *,
        primary_keys: list[str],
        datetime_pattern: str | None = None,
        datetime_column_name: str | None = None,
    ) -> LazyFrame: ...


# ============================================================================
# PRE-PROCESS HOOKS (DataFrame transformations before standard processing)
# ============================================================================


def forecast_utilisation_preprocess(logger: Logger | None, df: LazyFrame) -> LazyFrame:
    """Unpivot forecast columns from wide to long format.

    Used by: bronze_gasbb_forecast_utilisation

    Transforms wide-format forecast data:
        State | FacilityId | Monday 1 Jan | Tuesday 2 Jan | ...
        ------|------------|---------------|----------------|----
        VIC   | 123        | 100.0         | 105.0          | ...

    Into long format:
        State | FacilityId | ForecastDate      | ForecastValue | ForecastDay
        ------|------------|-------------------|---------------|------------
        VIC   | 123        | Monday 1 Jan      | 100.0         | d+1
        VIC   | 123        | Tuesday 2 Jan     | 105.0         | d+2
    """
    if logger:
        logger.info("upivoting data and adding new columns")

    core_columns = [
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
        "source_file",
    ]

    # Identify forecast columns (all non-core columns)
    all_columns = df.collect_schema().keys()
    forecast_columns = [
        col_name
        for col_name in all_columns
        if col_name not in core_columns and col_name != "source_file"
    ]

    # Create mapping: "Monday 1 Jan" -> "d+1"
    forecast_column_mapping = {c: f"d+{i + 1}" for i, c in enumerate(forecast_columns)}

    # Unpivot
    df_unpivoted = df.unpivot(
        index=core_columns,
        variable_name="ForecastDate",
        value_name="ForecastValue",
    ).with_columns(ForecastDay=col.ForecastDate.replace(forecast_column_mapping))

    # Calculate forecast period start date
    forecast_period = (
        df_unpivoted.select("ForecastDate")
        .unique()
        .with_columns(col("ForecastDate").str.to_datetime(format="%A %d %b %Y"))
        .collect()
        .min()
        .item()
        - timedelta(days=1)
    ).strftime("%A %d %b %Y")

    if logger:
        logger.info("finished upivoting data and adding new columns")

    return df_unpivoted.select(
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
        "ForecastDate",
        "ForecastValue",
        "ForecastDay",
        lit(forecast_period).alias("ForecastPeriod"),
        "source_file",
    ).sort(["State", "FacilityId", "ForecastDate"])


def nameplate_rating_preprocess(logger: Logger | None, df: LazyFrame) -> LazyFrame:
    """Convert all column names to lowercase.

    Used by: bronze_gasbb_nameplate_rating

    The source data has inconsistent column name casing. This normalizes
    all columns to lowercase for consistent schema matching.
    """
    if logger:
        logger.info("making all columns lowercase")
    columns = df.collect_schema().keys()
    return df.rename({c: c.lower() for c in columns})


# ============================================================================
# PROCESS OBJECT HOOKS (Custom file parsing before DataFrame creation)
# ============================================================================


def gsh_gas_trades_process_object(logger: Logger | None, contents: bytes) -> LazyFrame:
    """Parse GSH Gas Trades CSV with non-standard format.

    Used by: bronze_gasbb_gsh_gas_trades

    The CSV has:
    - First 4 columns are metadata (not data)
    - Header row that needs stripping
    - Footer rows that need removing

    This hook removes first 4 columns and header/footer rows before parsing.
    """
    csv_string = "\n".join(
        [
            ",".join(line.split(",")[4:])  # Remove first 4 columns
            for line in contents.decode("utf-8")
            .replace("\r\n", "\n")
            .split("\n")[1:-2]  # Skip header + footer
        ]
    ).encode()
    return read_csv(csv_string).lazy()


# ============================================================================
# POST-PROCESS HOOKS (Custom deduplication after standard processing)
# ============================================================================


def add_missing_primary_keys_postprocess(
    context: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: list[str],
    datetime_pattern: str | None = None,
    datetime_column_name: str | None = None,
) -> LazyFrame:
    """Add missing primary key columns as NULL before deduplication.

    Used by multiple reports that have optional primary key columns:
    - bronze_gasbb_short_term_transactions
    - bronze_gasbb_short_term_swap_transactions
    - bronze_gasbb_nodes_connection_points
    - bronze_gasbb_nt_lng_flow
    - bronze_gasbb_shippers_list
    - bronze_gasbb_gsh_gas_trades

    Some reports have primary keys that aren't always present in the data.
    This hook adds them as NULL so deduplication logic doesn't fail.
    """
    from aemo_etl.definitions.bronze_gasbb_reports.utils import (
        default_post_process_hook,
    )

    context.log.info("ensuring rows are not duplicates")
    schema = df.collect_schema()

    # Add missing primary keys as NULL
    for key in primary_keys:
        if key not in schema:
            df = df.with_columns(lit(None).alias(key))

    # Apply standard deduplication
    return default_post_process_hook(
        context,
        df,
        primary_keys=primary_keys,
        datetime_pattern=datetime_pattern,
        datetime_column_name=datetime_column_name,
    )


def medium_term_capacity_anti_join_postprocess(
    context: AssetExecutionContext,
    df: LazyFrame,
    *,
    primary_keys: list[str],
    datetime_pattern: str | None = None,
    datetime_column_name: str | None = None,
) -> LazyFrame:
    """Prevent duplicates using anti-join with existing Delta table.

    Used by: bronze_gasbb_medium_term_capacity_outlook

    This report has overlapping historical data that causes duplicates.
    Use anti-join to exclude rows already in the Delta table.
    """
    from polars import scan_delta

    from aemo_etl.configuration.registry import GASBB_CONFIGS
    from aemo_etl.definitions.bronze_gasbb_reports.utils import (
        default_post_process_hook,
    )

    # Apply standard deduplication first
    df = default_post_process_hook(
        context,
        df,
        primary_keys=primary_keys,
        datetime_pattern=datetime_pattern,
        datetime_column_name=datetime_column_name,
    )

    try:
        config = GASBB_CONFIGS["bronze_gasbb_medium_term_capacity_outlook"]
        target_df = scan_delta(config.s3_table_location)

        # Cast types to match target
        type_matched_df = df.with_columns(
            [
                col(col_).cast(type_)
                for col_, type_ in target_df.collect_schema().items()
                if col_ in df.collect_schema()
            ]
        )

        # Anti-join to exclude already existing rows
        output = type_matched_df.join(
            target_df,
            how="anti",
            on=primary_keys,
            nulls_equal=True,
        ).lazy()

        context.log.info("anti-join complete")
        return output

    except Exception as e:
        context.log.warning(f"anti-join failed, continuing with all data: {e}")
        return df


# ============================================================================
# HOOK REGISTRIES (maps table_name -> hook function)
# ============================================================================

PREPROCESS_HOOKS: dict[str, PreprocessHook] = {
    "bronze_gasbb_forecast_utilisation": forecast_utilisation_preprocess,
    "bronze_gasbb_nameplate_rating": nameplate_rating_preprocess,
}

PROCESS_OBJECT_HOOKS: dict[str, ProcessObjectHook] = {
    "bronze_gasbb_gsh_gas_trades": gsh_gas_trades_process_object,
}

POST_PROCESS_HOOKS: dict[str, PostProcessHook] = {
    # Reports that need missing PK handling
    "bronze_gasbb_short_term_transactions": add_missing_primary_keys_postprocess,
    "bronze_gasbb_short_term_swap_transactions": add_missing_primary_keys_postprocess,
    "bronze_gasbb_nodes_connection_points": add_missing_primary_keys_postprocess,
    "bronze_gasbb_nt_lng_flow": add_missing_primary_keys_postprocess,
    "bronze_gasbb_shippers_list": add_missing_primary_keys_postprocess,
    "bronze_gasbb_gsh_gas_trades": add_missing_primary_keys_postprocess,
    # Reports with special deduplication logic
    "bronze_gasbb_medium_term_capacity_outlook": medium_term_capacity_anti_join_postprocess,
}

DATETIME_PATTERNS: dict[str, str] = {
    "bronze_gasbb_facilities": "%Y-%m-%d %H:%M:%S",
}

DATETIME_COLUMN_NAMES: dict[str, str] = {
    # Override auto-detection if needed (rare)
    # Most reports auto-detect "current_date" or "current_datetime"
}


# ============================================================================
# HELPER FUNCTION
# ============================================================================


def get_hooks_for_report(
    table_name: str,
) -> dict[str, PreprocessHook | ProcessObjectHook | PostProcessHook | str | None]:
    """Get all hooks for a given report (helper for definitions).

    Args:
        table_name: Name of the table to look up hooks for

    Returns:
        Dictionary with keys: preprocess_hook, process_object_hook, post_process_hook,
        datetime_pattern, datetime_column_name. Values are None if no custom hook needed.
    """
    return {
        "preprocess_hook": PREPROCESS_HOOKS.get(table_name),
        "process_object_hook": PROCESS_OBJECT_HOOKS.get(table_name),
        "post_process_hook": POST_PROCESS_HOOKS.get(table_name),
        "datetime_pattern": DATETIME_PATTERNS.get(table_name),
        "datetime_column_name": DATETIME_COLUMN_NAMES.get(table_name),
    }
