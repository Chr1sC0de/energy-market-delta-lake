"""Current-state Delta helpers for source-table bronze ingestion."""

from dataclasses import dataclass
from logging import Logger
from typing import Final

from dagster import MetadataValue
from dagster._core.definitions.metadata import RawMetadataValue
from polars import LazyFrame, col
from polars import len as pl_len

from aemo_etl.utils import get_lazyframe_num_rows, table_exists

CURRENT_STATE_DELTA_MERGE_OPTIONS: Final = {
    "predicate": "source.surrogate_key = target.surrogate_key",
    "source_alias": "source",
    "target_alias": "target",
}
CURRENT_STATE_MERGE_UPDATE_PREDICATE: Final = (
    "target.source_content_hash IS NULL OR "
    "source.source_content_hash != target.source_content_hash"
)
SOURCE_TABLE_BRONZE_SINK_DELTA_KWARGS: Final = {
    "mode": "merge",
    "delta_merge_options": CURRENT_STATE_DELTA_MERGE_OPTIONS,
}
SOURCE_CONTENT_HASH_COLUMN: Final = "source_content_hash"
SURROGATE_KEY_SAMPLE_LIMIT: Final = 10


@dataclass(frozen=True, slots=True)
class SourceTableBronzeWriteResult:
    """Result metadata for one source-table bronze current-state write."""

    row_count: int
    target_exists_before_write: bool
    wrote_table: bool
    write_mode: str


@dataclass(frozen=True, slots=True)
class SurrogateKeyDuplicateSummary:
    """Duplicate surrogate-key summary suitable for diagnostics."""

    duplicate_key_count: int
    duplicate_row_count: int
    sample_surrogate_keys: tuple[str | None, ...]

    @property
    def has_duplicates(self) -> bool:
        """Return whether duplicate surrogate-key groups were found."""
        return self.duplicate_key_count > 0


class SourceTableDuplicateSurrogateKeyError(ValueError):
    """Raised when source-table current-state rows are not key-unique."""


def _surrogate_key_error_message(
    *,
    operation: str,
    summary: SurrogateKeyDuplicateSummary,
) -> str:
    return (
        "source-table current-state rows contain duplicate surrogate_key values "
        f"before {operation}: duplicate_key_count={summary.duplicate_key_count}, "
        f"duplicate_row_count={summary.duplicate_row_count}, "
        f"sample_surrogate_keys={list(summary.sample_surrogate_keys)}. "
        "Deepen surrogate_key_sources or add a source-specific dedupe hook before "
        "writing the Delta table."
    )


def summarize_duplicate_surrogate_keys(
    batch: LazyFrame,
    *,
    distinct_source_content_only: bool = False,
    sample_limit: int = SURROGATE_KEY_SAMPLE_LIMIT,
) -> SurrogateKeyDuplicateSummary:
    """Return duplicate surrogate-key diagnostics for a current-state batch."""
    schema = batch.collect_schema()
    aggregations = [pl_len().alias("row_count")]
    has_source_content_hash = SOURCE_CONTENT_HASH_COLUMN in schema
    if distinct_source_content_only and has_source_content_hash:
        aggregations.append(
            col(SOURCE_CONTENT_HASH_COLUMN)
            .n_unique()
            .alias("source_content_hash_count")
        )

    duplicate_groups = batch.group_by("surrogate_key").agg(aggregations)
    duplicate_filter = col("row_count") > 1
    if distinct_source_content_only and has_source_content_hash:
        duplicate_filter = duplicate_filter & (col("source_content_hash_count") > 1)
    duplicate_groups = duplicate_groups.filter(duplicate_filter)

    totals = duplicate_groups.select(
        pl_len().alias("duplicate_key_count"),
        col("row_count").sum().alias("duplicate_row_count"),
    ).collect()
    duplicate_key_count = totals.item(0, "duplicate_key_count")
    duplicate_row_count = totals.item(0, "duplicate_row_count") or 0
    samples = (
        duplicate_groups.sort("row_count", descending=True)
        .limit(sample_limit)
        .select("surrogate_key")
        .collect()["surrogate_key"]
        .to_list()
    )

    return SurrogateKeyDuplicateSummary(
        duplicate_key_count=duplicate_key_count,
        duplicate_row_count=duplicate_row_count,
        sample_surrogate_keys=tuple(samples),
    )


def assert_unique_surrogate_keys(batch: LazyFrame, *, operation: str) -> None:
    """Raise when a current-state write source contains duplicate keys."""
    summary = summarize_duplicate_surrogate_keys(batch)
    if summary.has_duplicates:
        raise SourceTableDuplicateSurrogateKeyError(
            _surrogate_key_error_message(operation=operation, summary=summary)
        )


def _latest_source_rows(batch: LazyFrame) -> LazyFrame:
    """Return rows belonging to the maximum source_file for each surrogate_key."""
    latest_keys = batch.group_by("surrogate_key").agg(
        col("source_file").max().alias("source_file")
    )
    return batch.join(
        latest_keys,
        on=["surrogate_key", "source_file"],
        how="semi",
    )


def collapse_current_state_batch(batch: LazyFrame) -> LazyFrame:
    """Keep the maximum source_file row for each surrogate_key in a batch."""
    latest_rows = _latest_source_rows(batch)
    summary = summarize_duplicate_surrogate_keys(
        latest_rows,
        distinct_source_content_only=True,
    )
    if summary.has_duplicates:
        raise SourceTableDuplicateSurrogateKeyError(
            _surrogate_key_error_message(
                operation="collapsing latest source-file rows",
                summary=summary,
            )
        )
    return latest_rows.unique("surrogate_key", maintain_order=False)


def source_table_bronze_materialization_metadata(
    write_result: SourceTableBronzeWriteResult,
) -> dict[str, RawMetadataValue]:
    """Return stable Dagster materialization metadata for source-table bronze."""
    return {
        "sink_delta_kwargs": MetadataValue.json(SOURCE_TABLE_BRONZE_SINK_DELTA_KWARGS),
        "dagster/row_count": write_result.row_count,
    }


def write_source_table_current_state_batch(
    batch: LazyFrame,
    *,
    target_table_uri: str,
    replace_existing: bool = False,
    logger: Logger | None = None,
) -> SourceTableBronzeWriteResult:
    """Write a source-table bronze current-state batch to a Delta table."""
    row_count = get_lazyframe_num_rows(batch)
    assert_unique_surrogate_keys(batch, operation="Delta write")

    if replace_existing:
        batch.sink_delta(
            target_table_uri,
            mode="overwrite",
            delta_write_options={"schema_mode": "overwrite"},
        )
        return SourceTableBronzeWriteResult(
            row_count=row_count,
            target_exists_before_write=False,
            wrote_table=True,
            write_mode="overwrite",
        )

    target_exists = table_exists(target_table_uri)

    if row_count == 0 and target_exists:
        return SourceTableBronzeWriteResult(
            row_count=row_count,
            target_exists_before_write=target_exists,
            wrote_table=False,
            write_mode="skip",
        )

    if not target_exists:
        batch.sink_delta(target_table_uri, mode="append")
        return SourceTableBronzeWriteResult(
            row_count=row_count,
            target_exists_before_write=target_exists,
            wrote_table=True,
            write_mode="append",
        )

    merge_builder = batch.sink_delta(
        target_table_uri,
        mode="merge",
        delta_merge_options=CURRENT_STATE_DELTA_MERGE_OPTIONS,
    )
    assert merge_builder is not None, "mode was set to merge but result is None"
    if logger is not None:
        logger.info(
            "merging source-table bronze data with settings "
            f"{SOURCE_TABLE_BRONZE_SINK_DELTA_KWARGS}"
        )
    merge_results = (
        merge_builder.when_matched_update_all(
            predicate=CURRENT_STATE_MERGE_UPDATE_PREDICATE
        )
        .when_not_matched_insert_all()
        .execute()
    )
    if logger is not None:
        logger.info(f"merged source-table bronze data with results {merge_results}")

    return SourceTableBronzeWriteResult(
        row_count=row_count,
        target_exists_before_write=target_exists,
        wrote_table=True,
        write_mode="merge",
    )
