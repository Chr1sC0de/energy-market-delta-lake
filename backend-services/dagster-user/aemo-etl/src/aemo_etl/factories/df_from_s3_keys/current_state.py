"""Current-state Delta helpers for source-table bronze ingestion."""

from dataclasses import dataclass
from logging import Logger
from typing import Final

from dagster import MetadataValue
from dagster._core.definitions.metadata import RawMetadataValue
from polars import LazyFrame, col

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


@dataclass(frozen=True, slots=True)
class SourceTableBronzeWriteResult:
    """Result metadata for one source-table bronze current-state write."""

    row_count: int
    target_exists_before_write: bool
    wrote_table: bool
    write_mode: str


def collapse_current_state_batch(batch: LazyFrame) -> LazyFrame:
    """Keep the maximum source_file row for each surrogate_key in a batch."""
    latest_keys = batch.group_by("surrogate_key").agg(
        col("source_file").max().alias("source_file")
    )
    deduped = batch.join(
        latest_keys,
        on=["surrogate_key", "source_file"],
        how="semi",
    )
    return deduped.unique("surrogate_key", maintain_order=False)


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
