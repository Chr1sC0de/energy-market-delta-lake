import datetime as dt
import importlib
import pkgutil
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import MagicMock

import polars as pl
from polars import Datetime, String
import pytest
from pytest_mock import MockerFixture

from aemo_etl.defs.resources import (
    CURRENT_STATE_DELTA_MERGE_OPTIONS,
    CURRENT_STATE_MERGE_UPDATE_PREDICATE,
)
from aemo_etl.factories.df_from_s3_keys import source_tables as source_tables_registry
from aemo_etl.factories.df_from_s3_keys.assets import (
    SOURCE_CONTENT_HASH_COLUMN,
)
from aemo_etl.factories.df_from_s3_keys.source_tables import (
    DFFromS3KeysSourceTableSpec,
    select_source_table_specs,
)
from aemo_etl.maintenance.archive_replay import (
    DEFAULT_MAX_BATCH_BYTES,
    DEFAULT_MAX_BATCH_FILES,
    ArchiveObject,
    ArchiveReplayBatch,
    ArchiveReplayPlan,
    ArchiveReplayResult,
    _StagedArchiveBatch,
    _stage_archive_batch,
    build_archive_replay_plans,
    plan_archive_batches,
    rebuild_archive_table,
    run_archive_replay,
    write_current_state_batch,
)

_SCHEMA = {
    "col1": String,
    "ingested_timestamp": Datetime("us", time_zone="UTC"),
    "ingested_date": Datetime("us", time_zone="UTC"),
    "surrogate_key": String,
    "source_file": String,
    SOURCE_CONTENT_HASH_COLUMN: String,
}


@dataclass(frozen=True, slots=True)
class _ModuleInfo:
    name: str
    ispkg: bool


def _spec(
    *,
    domain: str = "gbb",
    name_suffix: str = "table",
    glob_pattern: str = "table*.csv",
) -> DFFromS3KeysSourceTableSpec:
    return DFFromS3KeysSourceTableSpec(
        domain=domain,
        name_suffix=name_suffix,
        glob_pattern=glob_pattern,
        schema=_SCHEMA,
        surrogate_key_sources=("col1",),
    )


def _s3_client_with_archive_keys(
    mocker: MockerFixture,
    objects: list[dict[str, object]],
) -> MagicMock:
    paginator = MagicMock()
    paginator.paginate.return_value = [{"Contents": objects}]
    s3_client = MagicMock()
    s3_client.get_paginator.return_value = paginator
    return s3_client


def test_default_batch_limits() -> None:
    assert DEFAULT_MAX_BATCH_BYTES == 128 * 1024 * 1024
    assert DEFAULT_MAX_BATCH_FILES == 25


def test_select_source_table_specs_targets_all_domain_or_table() -> None:
    gbb = _spec(domain="gbb", name_suffix="gasbb_contacts")
    vicgas = _spec(domain="vicgas", name_suffix="int041_v4_market_prices_1")
    specs = (gbb, vicgas)

    assert select_source_table_specs(specs, include_all=True) == specs
    assert select_source_table_specs(specs, domain="gbb") == (gbb,)
    assert select_source_table_specs(
        specs,
        table="vicgas.bronze_int041_v4_market_prices_1",
    ) == (vicgas,)


def test_source_table_spec_matches_paths_and_builds_uris() -> None:
    spec = _spec(domain="gbb", name_suffix="gasbb_contacts")

    assert spec.bronze_table_name == "bronze_gasbb_contacts"
    assert spec.archive_prefix == "bronze/gbb"
    assert spec.table_id == "gbb.bronze_gasbb_contacts"
    assert spec.target_table_uri("aemo") == "s3://aemo/bronze/gbb/bronze_gasbb_contacts"
    assert spec.matches_table("/bronze/gbb/bronze_gasbb_contacts/")


def test_select_source_table_specs_rejects_invalid_targets() -> None:
    gbb = _spec(domain="gbb", name_suffix="table")
    vicgas = _spec(domain="vicgas", name_suffix="table")

    with pytest.raises(ValueError, match="select exactly one"):
        select_source_table_specs((gbb,), include_all=True, domain="gbb")

    with pytest.raises(ValueError, match="unknown source-table domain"):
        select_source_table_specs((gbb,), domain="missing")

    with pytest.raises(ValueError, match="unknown source table"):
        select_source_table_specs((gbb,), table="missing")

    with pytest.raises(ValueError, match="ambiguous source table"):
        select_source_table_specs((gbb, vicgas), table="table")


def test_load_source_table_specs_imports_registered_raw_modules(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry: dict[tuple[str, str], DFFromS3KeysSourceTableSpec] = {}
    imported_modules: list[str] = []
    package = SimpleNamespace(__name__="rawpkg", __path__=("rawpath",))

    def import_module(name: str) -> object:
        imported_modules.append(name)
        if name == "rawpkg":
            return package

        source_tables_registry.register_source_table_spec(
            _spec(domain="loaded", name_suffix="table")
        )
        return SimpleNamespace()

    def iter_modules(paths: object, prefix: str) -> tuple[_ModuleInfo, ...]:
        assert paths == ("rawpath",)
        assert prefix == "rawpkg."
        return (
            _ModuleInfo(name="rawpkg.package", ispkg=True),
            _ModuleInfo(name="rawpkg.table", ispkg=False),
        )

    monkeypatch.setattr(source_tables_registry, "_SOURCE_TABLE_SPECS", registry)
    monkeypatch.setattr(
        source_tables_registry,
        "RAW_SOURCE_TABLE_PACKAGES",
        ("rawpkg",),
    )
    monkeypatch.setattr(importlib, "import_module", import_module)
    monkeypatch.setattr(pkgutil, "iter_modules", iter_modules)

    specs = source_tables_registry.load_source_table_specs()

    assert tuple(spec.table_id for spec in specs) == ("loaded.bronze_table",)
    assert imported_modules == ["rawpkg", "rawpkg.table"]


def test_plan_archive_batches_respects_byte_and_file_caps() -> None:
    batches = plan_archive_batches(
        (
            ArchiveObject(key="a.csv", size=40),
            ArchiveObject(key="b.csv", size=60),
            ArchiveObject(key="c.csv", size=1),
            ArchiveObject(key="d.csv", size=150),
        ),
        max_batch_bytes=100,
        max_batch_files=2,
    )

    assert [[object_.key for object_ in batch.objects] for batch in batches] == [
        ["a.csv", "b.csv"],
        ["c.csv"],
        ["d.csv"],
    ]
    assert [batch.total_bytes for batch in batches] == [100, 1, 150]


def test_plan_archive_batches_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError, match="max_batch_bytes"):
        plan_archive_batches((), max_batch_bytes=0)

    with pytest.raises(ValueError, match="max_batch_files"):
        plan_archive_batches((), max_batch_files=0)


def test_dry_run_reports_matching_archive_plan_without_writing(
    mocker: MockerFixture,
) -> None:
    s3_client = _s3_client_with_archive_keys(
        mocker,
        [
            {"Key": "bronze/gbb/other.csv", "Size": 999},
            {"Key": "bronze/gbb/table_20240101.csv", "Size": 40},
            {"Key": "bronze/gbb/table_20240102.csv", "Size": 70},
        ],
    )
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    results = run_archive_replay(
        s3_client,
        specs=(_spec(),),
        archive_bucket="archive",
        aemo_bucket="aemo",
        max_batch_bytes=100,
        max_batch_files=25,
    )

    result = results[0]
    assert result.mode == "dry-run"
    assert result.plan.matching_archive_files == (
        "bronze/gbb/table_20240101.csv",
        "bronze/gbb/table_20240102.csv",
    )
    assert result.plan.planned_batch_count == 2
    assert result.plan.total_bytes == 110
    assert result.plan.target_table_uri == "s3://aemo/bronze/gbb/bronze_table"
    s3_client.get_object.assert_not_called()
    sink_delta.assert_not_called()


def test_build_archive_replay_plans_reports_target_uri_and_totals(
    mocker: MockerFixture,
) -> None:
    s3_client = _s3_client_with_archive_keys(
        mocker,
        [
            {"Key": "bronze/gbb/table_20240102.csv", "Size": 70},
            {"Key": "bronze/gbb/table_20240101.csv", "Size": 40},
        ],
    )

    plan = build_archive_replay_plans(
        s3_client,
        specs=(_spec(),),
        archive_bucket="archive",
        aemo_bucket="aemo",
        max_batch_bytes=200,
        max_batch_files=25,
    )[0]

    assert plan.matching_file_count == 2
    assert plan.planned_batch_count == 1
    assert plan.total_bytes == 110
    assert plan.target_table_uri == "s3://aemo/bronze/gbb/bronze_table"
    assert plan.matching_archive_files == (
        "bronze/gbb/table_20240101.csv",
        "bronze/gbb/table_20240102.csv",
    )


def test_archive_replay_result_as_dict_is_serializable() -> None:
    plan = ArchiveReplayPlan(
        spec=_spec(),
        archive_bucket="archive",
        target_table_uri="s3://aemo/bronze/gbb/bronze_table",
        batches=(
            ArchiveReplayBatch(
                objects=(ArchiveObject(key="bronze/gbb/table_20240101.csv", size=40),)
            ),
        ),
    )
    result = ArchiveReplayResult(
        plan=plan,
        mode="replace",
        written_batches=1,
        written_files=1,
        skipped_files=("bronze/gbb/table_20240102.csv",),
    )

    assert result.as_dict() == {
        "mode": "replace",
        "table": "gbb.bronze_table",
        "archive_bucket": "archive",
        "archive_prefix": "bronze/gbb",
        "glob_pattern": "table*.csv",
        "matching_archive_files": ["bronze/gbb/table_20240101.csv"],
        "matching_file_count": 1,
        "planned_batch_count": 1,
        "total_bytes": 40,
        "target_table_uri": "s3://aemo/bronze/gbb/bronze_table",
        "written_batches": 1,
        "written_files": 1,
        "skipped_files": ["bronze/gbb/table_20240102.csv"],
    }


def test_write_current_state_batch_uses_replace_then_merge(
    mocker: MockerFixture,
) -> None:
    df = pl.LazyFrame(
        {
            "col1": ["value"],
            "ingested_timestamp": [dt.datetime(2024, 1, 1, tzinfo=dt.UTC)],
            "ingested_date": [dt.datetime(2024, 1, 1, tzinfo=dt.UTC)],
            "surrogate_key": ["key"],
            "source_file": ["s3://archive/bronze/gbb/table.csv"],
            SOURCE_CONTENT_HASH_COLUMN: ["hash"],
        }
    )
    sink_delta = mocker.patch.object(pl.LazyFrame, "sink_delta", return_value=None)

    write_current_state_batch(
        df,
        target_table_uri="s3://aemo/bronze/gbb/bronze_table",
        replace_existing=True,
    )

    sink_delta.assert_called_once_with(
        "s3://aemo/bronze/gbb/bronze_table",
        mode="overwrite",
        delta_write_options={"schema_mode": "overwrite"},
    )

    merge_builder = mocker.MagicMock()
    merge_builder.when_matched_update_all.return_value = merge_builder
    merge_builder.when_not_matched_insert_all.return_value = merge_builder
    sink_delta.reset_mock()
    sink_delta.return_value = merge_builder

    write_current_state_batch(
        df,
        target_table_uri="s3://aemo/bronze/gbb/bronze_table",
        replace_existing=False,
    )

    sink_delta.assert_called_once_with(
        "s3://aemo/bronze/gbb/bronze_table",
        mode="merge",
        delta_merge_options=CURRENT_STATE_DELTA_MERGE_OPTIONS,
    )
    merge_builder.when_matched_update_all.assert_called_once_with(
        predicate=CURRENT_STATE_MERGE_UPDATE_PREDICATE
    )
    merge_builder.when_not_matched_insert_all.assert_called_once_with()
    merge_builder.execute.assert_called_once_with()


def test_stage_archive_batch_skips_invalid_or_empty_files(
    mocker: MockerFixture,
) -> None:
    staged_frame = MagicMock()
    get_from_s3 = mocker.patch(
        "aemo_etl.maintenance.archive_replay.get_from_s3",
        side_effect=(b"", b"payload"),
    )
    source_frame_from_bytes = mocker.patch(
        "aemo_etl.maintenance.archive_replay.source_table_bronze_frame_from_bytes",
        return_value=staged_frame,
    )

    result = _stage_archive_batch(
        MagicMock(),
        archive_bucket="archive",
        batch=ArchiveReplayBatch(
            objects=(
                ArchiveObject(key="bronze/gbb/table.txt", size=100),
                ArchiveObject(key="bronze/gbb/table_empty.csv", size=0),
                ArchiveObject(key="bronze/gbb/table_no_body.csv", size=10),
                ArchiveObject(key="bronze/gbb/table_valid.csv", size=10),
            )
        ),
        spec=_spec(),
        current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
        staging_uri="/tmp/replay-stage",
    )

    assert result.staged_file_count == 1
    assert result.skipped_files == (
        "bronze/gbb/table.txt",
        "bronze/gbb/table_empty.csv",
        "bronze/gbb/table_no_body.csv",
    )
    assert get_from_s3.call_count == 2
    source_frame_from_bytes.assert_called_once()
    staged_frame.sink_delta.assert_called_once_with("/tmp/replay-stage", mode="append")


def test_rebuild_archive_table_writes_non_empty_staged_batches(
    mocker: MockerFixture,
) -> None:
    plan = ArchiveReplayPlan(
        spec=_spec(),
        archive_bucket="archive",
        target_table_uri="s3://aemo/bronze/gbb/bronze_table",
        batches=(
            ArchiveReplayBatch(
                objects=(ArchiveObject(key="bronze/gbb/table_1.csv", size=10),)
            ),
            ArchiveReplayBatch(
                objects=(ArchiveObject(key="bronze/gbb/table_2.csv", size=10),)
            ),
        ),
    )
    collapsed_frame = MagicMock()
    stage_archive_batch = mocker.patch(
        "aemo_etl.maintenance.archive_replay._stage_archive_batch",
        side_effect=(
            _StagedArchiveBatch(staged_file_count=2, skipped_files=("skip.csv",)),
            _StagedArchiveBatch(staged_file_count=0, skipped_files=("empty.csv",)),
        ),
    )
    scan_delta = mocker.patch(
        "aemo_etl.maintenance.archive_replay.scan_delta",
        return_value=MagicMock(),
    )
    collapse_current_state_batch = mocker.patch(
        "aemo_etl.maintenance.archive_replay.collapse_current_state_batch",
        return_value=collapsed_frame,
    )
    write_current_state_batch = mocker.patch(
        "aemo_etl.maintenance.archive_replay.write_current_state_batch"
    )

    result = rebuild_archive_table(
        MagicMock(),
        plan=plan,
        current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
    )

    assert result.mode == "replace"
    assert result.written_batches == 1
    assert result.written_files == 2
    assert result.skipped_files == ("skip.csv", "empty.csv")
    assert stage_archive_batch.call_count == 2
    scan_delta.assert_called_once()
    collapse_current_state_batch.assert_called_once_with(scan_delta.return_value)
    write_current_state_batch.assert_called_once_with(
        collapsed_frame,
        target_table_uri="s3://aemo/bronze/gbb/bronze_table",
        replace_existing=True,
    )


def test_run_archive_replay_replace_rebuilds_planned_tables(
    mocker: MockerFixture,
) -> None:
    s3_client = _s3_client_with_archive_keys(
        mocker,
        [{"Key": "bronze/gbb/table_20240101.csv", "Size": 40}],
    )
    replay_result = ArchiveReplayResult(
        plan=ArchiveReplayPlan(
            spec=_spec(),
            archive_bucket="archive",
            target_table_uri="s3://aemo/bronze/gbb/bronze_table",
            batches=(),
        ),
        mode="replace",
        written_batches=1,
    )
    rebuild = mocker.patch(
        "aemo_etl.maintenance.archive_replay.rebuild_archive_table",
        return_value=replay_result,
    )

    results = run_archive_replay(
        s3_client,
        specs=(_spec(),),
        replace=True,
        archive_bucket="archive",
        aemo_bucket="aemo",
    )

    assert results == (replay_result,)
    rebuild.assert_called_once()
