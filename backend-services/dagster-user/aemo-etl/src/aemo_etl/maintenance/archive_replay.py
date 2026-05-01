"""Memory-bounded archive replay for source-table bronze Delta rebuilds."""

import tempfile
from dataclasses import dataclass
from datetime import datetime
from logging import Logger
from typing import Final, Literal

from polars import LazyFrame, scan_delta
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET
from aemo_etl.defs.resources import (
    CURRENT_STATE_DELTA_MERGE_OPTIONS,
    CURRENT_STATE_MERGE_UPDATE_PREDICATE,
)
from aemo_etl.factories.df_from_s3_keys.assets import (
    collapse_current_state_batch,
    source_table_bronze_frame_from_bytes,
)
from aemo_etl.factories.df_from_s3_keys.source_tables import (
    DFFromS3KeysSourceTableSpec,
)
from aemo_etl.utils import (
    AEST,
    BYTES_TO_LAZYFRAME_REGISTER,
    get_from_s3,
    get_object_head_from_pages,
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
)

DEFAULT_MAX_BATCH_BYTES: Final = 128 * 1024 * 1024
DEFAULT_MAX_BATCH_FILES: Final = 25
ArchiveReplayMode = Literal["dry-run", "replace"]
REPLAY_MODE_DRY_RUN: Final[ArchiveReplayMode] = "dry-run"
REPLAY_MODE_REPLACE: Final[ArchiveReplayMode] = "replace"


@dataclass(frozen=True, slots=True)
class ArchiveObject:
    """S3 archive object selected for replay."""

    key: str
    size: int


@dataclass(frozen=True, slots=True)
class ArchiveReplayBatch:
    """One bounded batch of archive objects."""

    objects: tuple[ArchiveObject, ...]

    @property
    def total_bytes(self) -> int:
        """Return the total object size for this batch."""
        return sum(object_.size for object_ in self.objects)


@dataclass(frozen=True, slots=True)
class ArchiveReplayPlan:
    """Dry-run and execution plan for one source-table bronze rebuild."""

    spec: DFFromS3KeysSourceTableSpec
    archive_bucket: str
    target_table_uri: str
    batches: tuple[ArchiveReplayBatch, ...]

    @property
    def matching_file_count(self) -> int:
        """Return the number of matching archive files."""
        return sum(len(batch.objects) for batch in self.batches)

    @property
    def planned_batch_count(self) -> int:
        """Return the number of planned replay batches."""
        return len(self.batches)

    @property
    def total_bytes(self) -> int:
        """Return the total bytes across matching archive files."""
        return sum(batch.total_bytes for batch in self.batches)

    @property
    def matching_archive_files(self) -> tuple[str, ...]:
        """Return matching archive object keys in replay order."""
        return tuple(object_.key for batch in self.batches for object_ in batch.objects)


@dataclass(frozen=True, slots=True)
class ArchiveReplayResult:
    """Result for one dry-run or replace replay target."""

    plan: ArchiveReplayPlan
    mode: ArchiveReplayMode
    written_batches: int = 0
    written_files: int = 0
    skipped_files: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        """Return a serializable CLI representation."""
        return {
            "mode": self.mode,
            "table": self.plan.spec.table_id,
            "archive_bucket": self.plan.archive_bucket,
            "archive_prefix": self.plan.spec.archive_prefix,
            "glob_pattern": self.plan.spec.glob_pattern,
            "matching_archive_files": list(self.plan.matching_archive_files),
            "matching_file_count": self.plan.matching_file_count,
            "planned_batch_count": self.plan.planned_batch_count,
            "total_bytes": self.plan.total_bytes,
            "target_table_uri": self.plan.target_table_uri,
            "written_batches": self.written_batches,
            "written_files": self.written_files,
            "skipped_files": list(self.skipped_files),
        }


@dataclass(frozen=True, slots=True)
class _StagedArchiveBatch:
    staged_file_count: int
    skipped_files: tuple[str, ...]


def plan_archive_batches(
    objects: tuple[ArchiveObject, ...],
    *,
    max_batch_bytes: int = DEFAULT_MAX_BATCH_BYTES,
    max_batch_files: int = DEFAULT_MAX_BATCH_FILES,
) -> tuple[ArchiveReplayBatch, ...]:
    """Group archive objects into bounded replay batches."""
    if max_batch_bytes <= 0:
        raise ValueError("max_batch_bytes must be greater than zero")
    if max_batch_files <= 0:
        raise ValueError("max_batch_files must be greater than zero")

    batches: list[ArchiveReplayBatch] = []
    current_objects: list[ArchiveObject] = []
    current_bytes = 0

    for object_ in objects:
        would_exceed_files = len(current_objects) >= max_batch_files
        would_exceed_bytes = (
            current_bytes + object_.size > max_batch_bytes and len(current_objects) > 0
        )
        if would_exceed_files or would_exceed_bytes:
            batches.append(ArchiveReplayBatch(objects=tuple(current_objects)))
            current_objects = []
            current_bytes = 0

        current_objects.append(object_)
        current_bytes += object_.size

    if current_objects:
        batches.append(ArchiveReplayBatch(objects=tuple(current_objects)))

    return tuple(batches)


def list_matching_archive_objects(
    s3_client: S3Client,
    *,
    archive_bucket: str,
    spec: DFFromS3KeysSourceTableSpec,
    logger: Logger | None = None,
) -> tuple[ArchiveObject, ...]:
    """List archive objects matching a source-table glob pattern."""
    pages = get_s3_pagination(
        s3_client,
        archive_bucket,
        spec.archive_prefix,
        logger=logger,
    )
    object_heads = get_object_head_from_pages(pages, logger=logger)
    matching_keys = get_s3_object_keys_from_prefix_and_name_glob(
        spec.archive_prefix,
        spec.glob_pattern,
        sorted(object_heads),
    )
    return tuple(
        ArchiveObject(key=key, size=int(object_heads[key].get("Size", 0)))
        for key in matching_keys
    )


def build_archive_replay_plans(
    s3_client: S3Client,
    *,
    specs: tuple[DFFromS3KeysSourceTableSpec, ...],
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    max_batch_bytes: int = DEFAULT_MAX_BATCH_BYTES,
    max_batch_files: int = DEFAULT_MAX_BATCH_FILES,
    logger: Logger | None = None,
) -> tuple[ArchiveReplayPlan, ...]:
    """Build replay plans for selected source-table specs."""
    return tuple(
        ArchiveReplayPlan(
            spec=spec,
            archive_bucket=archive_bucket,
            target_table_uri=spec.target_table_uri(aemo_bucket),
            batches=plan_archive_batches(
                list_matching_archive_objects(
                    s3_client,
                    archive_bucket=archive_bucket,
                    spec=spec,
                    logger=logger,
                ),
                max_batch_bytes=max_batch_bytes,
                max_batch_files=max_batch_files,
            ),
        )
        for spec in specs
    )


def write_current_state_batch(
    batch: LazyFrame,
    *,
    target_table_uri: str,
    replace_existing: bool,
) -> None:
    """Write a current-state batch using replacement or merge semantics."""
    if replace_existing:
        batch.sink_delta(
            target_table_uri,
            mode="overwrite",
            delta_write_options={"schema_mode": "overwrite"},
        )
        return

    merge_builder = batch.sink_delta(
        target_table_uri,
        mode="merge",
        delta_merge_options=CURRENT_STATE_DELTA_MERGE_OPTIONS,
    )
    assert merge_builder is not None, "mode was set to merge but result is None"
    merge_builder.when_matched_update_all(
        predicate=CURRENT_STATE_MERGE_UPDATE_PREDICATE
    ).when_not_matched_insert_all().execute()


def _stage_archive_batch(
    s3_client: S3Client,
    *,
    archive_bucket: str,
    batch: ArchiveReplayBatch,
    spec: DFFromS3KeysSourceTableSpec,
    current_time: datetime,
    staging_uri: str,
    logger: Logger | None = None,
) -> _StagedArchiveBatch:
    staged_file_count = 0
    skipped_files: list[str] = []

    for archive_object in batch.objects:
        filetype = archive_object.key.rsplit(".")[-1].lower()
        if filetype not in BYTES_TO_LAZYFRAME_REGISTER:
            skipped_files.append(archive_object.key)
            continue
        if archive_object.size == 0:
            skipped_files.append(archive_object.key)
            continue

        object_bytes = get_from_s3(
            s3_client,
            archive_bucket,
            archive_object.key,
            logger=logger,
        )
        if object_bytes is None or len(object_bytes) == 0:
            skipped_files.append(archive_object.key)
            continue

        df = source_table_bronze_frame_from_bytes(
            s3_bucket=archive_bucket,
            s3_key=archive_object.key,
            object_bytes=object_bytes,
            schema=spec.schema,
            surrogate_key_sources=spec.surrogate_key_sources,
            current_time=current_time,
            postprocess_object_hooks=spec.postprocess_object_hooks,
            postprocess_lazyframe_hooks=spec.postprocess_lazyframe_hooks,
            source_file_bucket=archive_bucket,
        )
        df.sink_delta(staging_uri, mode="append")
        staged_file_count += 1

    return _StagedArchiveBatch(
        staged_file_count=staged_file_count,
        skipped_files=tuple(skipped_files),
    )


def rebuild_archive_table(
    s3_client: S3Client,
    *,
    plan: ArchiveReplayPlan,
    current_time: datetime | None = None,
    logger: Logger | None = None,
) -> ArchiveReplayResult:
    """Rebuild one bronze table from archived source files."""
    replay_time = current_time or datetime.now(AEST)
    has_replaced_table = False
    written_batches = 0
    written_files = 0
    skipped_files: list[str] = []

    for batch in plan.batches:
        with tempfile.TemporaryDirectory() as temp_dir:
            staging_uri = f"{temp_dir}/bronze_replay_staging"
            staged = _stage_archive_batch(
                s3_client,
                archive_bucket=plan.archive_bucket,
                batch=batch,
                spec=plan.spec,
                current_time=replay_time,
                staging_uri=staging_uri,
                logger=logger,
            )
            skipped_files.extend(staged.skipped_files)
            if staged.staged_file_count == 0:
                continue

            current_state_batch = collapse_current_state_batch(scan_delta(staging_uri))
            write_current_state_batch(
                current_state_batch,
                target_table_uri=plan.target_table_uri,
                replace_existing=not has_replaced_table,
            )
            has_replaced_table = True
            written_batches += 1
            written_files += staged.staged_file_count

    return ArchiveReplayResult(
        plan=plan,
        mode=REPLAY_MODE_REPLACE,
        written_batches=written_batches,
        written_files=written_files,
        skipped_files=tuple(skipped_files),
    )


def run_archive_replay(
    s3_client: S3Client,
    *,
    specs: tuple[DFFromS3KeysSourceTableSpec, ...],
    replace: bool = False,
    archive_bucket: str = ARCHIVE_BUCKET,
    aemo_bucket: str = AEMO_BUCKET,
    max_batch_bytes: int = DEFAULT_MAX_BATCH_BYTES,
    max_batch_files: int = DEFAULT_MAX_BATCH_FILES,
    logger: Logger | None = None,
) -> tuple[ArchiveReplayResult, ...]:
    """Plan and optionally execute source-table bronze archive replay."""
    plans = build_archive_replay_plans(
        s3_client,
        specs=specs,
        archive_bucket=archive_bucket,
        aemo_bucket=aemo_bucket,
        max_batch_bytes=max_batch_bytes,
        max_batch_files=max_batch_files,
        logger=logger,
    )

    if not replace:
        return tuple(
            ArchiveReplayResult(plan=plan, mode=REPLAY_MODE_DRY_RUN) for plan in plans
        )

    return tuple(
        rebuild_archive_table(s3_client, plan=plan, logger=logger) for plan in plans
    )
