import pytest

from aemo_etl.maintenance.archive_source_planning import (
    ArchiveSourceObject,
    ArchiveSourceRequirement,
    ArchiveSourceSelectionPolicy,
    match_archive_source_objects,
    plan_archive_sources,
)


def _requirement(
    *,
    name: str = "gbb.bronze_table",
    glob_pattern: str = "table_*.csv",
) -> ArchiveSourceRequirement:
    return ArchiveSourceRequirement(
        kind="source-table",
        name=name,
        archive_prefix="bronze/gbb",
        glob_pattern=glob_pattern,
    )


def test_match_archive_source_objects_normalizes_matching_heads() -> None:
    objects = match_archive_source_objects(
        {
            "bronze/gbb/other.csv": {"Size": 999},
            "bronze/gbb/table_20231231.csv": {"Size": None},
            "bronze/gbb/table_20240102.CSV": {"Size": "20"},
            "bronze/vicgas/table_20240101.csv": {"Size": 10},
            "bronze/gbb/table_20240101.csv": {},
        },
        archive_prefix="bronze/gbb",
        glob_pattern="table_*.csv",
    )

    assert objects == (
        ArchiveSourceObject(key="bronze/gbb/table_20231231.csv", size=0),
        ArchiveSourceObject(key="bronze/gbb/table_20240101.csv", size=0),
        ArchiveSourceObject(key="bronze/gbb/table_20240102.CSV", size=20),
    )


def test_plan_archive_sources_records_missing_coverage() -> None:
    plan = plan_archive_sources(
        {},
        requirements=(_requirement(),),
        selection_policy=ArchiveSourceSelectionPolicy(
            latest_count=2,
            max_batch_bytes=None,
            max_batch_files=None,
        ),
    )

    coverage = plan.coverage[0]
    assert coverage.available_count == 0
    assert coverage.selected_objects == ()
    assert coverage.shortfall == 2
    assert plan.batches == ()


def test_plan_archive_sources_deduplicates_selected_objects() -> None:
    plan = plan_archive_sources(
        {
            "bronze/gbb/table_20240101.csv": {"Size": 10},
            "bronze/gbb/table_20240102.csv": {"Size": 20},
        },
        requirements=(
            _requirement(name="wide", glob_pattern="*.csv"),
            _requirement(name="narrow", glob_pattern="table_20240102.csv"),
        ),
        selection_policy=ArchiveSourceSelectionPolicy(
            latest_count=None,
            max_batch_bytes=None,
            max_batch_files=None,
        ),
    )

    assert [object_.key for object_ in plan.coverage[0].selected_objects] == [
        "bronze/gbb/table_20240101.csv",
        "bronze/gbb/table_20240102.csv",
    ]
    assert [object_.key for object_ in plan.coverage[1].selected_objects] == [
        "bronze/gbb/table_20240102.csv"
    ]
    assert plan.coverage[0].shortfall == 0
    assert [object_.key for object_ in plan.selected_objects] == [
        "bronze/gbb/table_20240101.csv",
        "bronze/gbb/table_20240102.csv",
    ]


def test_plan_archive_sources_selects_latest_objects_by_key_order() -> None:
    plan = plan_archive_sources(
        {
            "bronze/gbb/table_20240103.csv": {"Size": 30},
            "bronze/gbb/table_20240101.csv": {"Size": 10},
            "bronze/gbb/table_20240102.csv": {"Size": 20},
        },
        requirements=(_requirement(),),
        selection_policy=ArchiveSourceSelectionPolicy(
            latest_count=2,
            max_batch_bytes=None,
            max_batch_files=None,
        ),
    )

    coverage = plan.coverage[0]
    assert coverage.available_count == 3
    assert coverage.shortfall == 0
    assert [object_.key for object_ in coverage.selected_objects] == [
        "bronze/gbb/table_20240102.csv",
        "bronze/gbb/table_20240103.csv",
    ]
    assert plan.selected_object_count == 2
    assert plan.planned_batch_count == 1
    assert plan.total_bytes == 50


def test_plan_archive_sources_batches_selected_objects() -> None:
    plan = plan_archive_sources(
        {
            "bronze/gbb/a.csv": {"Size": 40},
            "bronze/gbb/b.csv": {"Size": 60},
            "bronze/gbb/c.csv": {"Size": 1},
            "bronze/gbb/d.csv": {"Size": 150},
        },
        requirements=(_requirement(glob_pattern="*.csv"),),
        selection_policy=ArchiveSourceSelectionPolicy(
            latest_count=None,
            max_batch_bytes=100,
            max_batch_files=2,
        ),
    )

    assert [[object_.key for object_ in batch.objects] for batch in plan.batches] == [
        ["bronze/gbb/a.csv", "bronze/gbb/b.csv"],
        ["bronze/gbb/c.csv"],
        ["bronze/gbb/d.csv"],
    ]
    assert [batch.total_bytes for batch in plan.batches] == [100, 1, 150]


def test_plan_archive_sources_rejects_invalid_policy_limits() -> None:
    with pytest.raises(ValueError, match="latest_count"):
        plan_archive_sources(
            {},
            requirements=(_requirement(),),
            selection_policy=ArchiveSourceSelectionPolicy(
                latest_count=0,
                max_batch_bytes=None,
                max_batch_files=None,
            ),
        )

    with pytest.raises(ValueError, match="max_batch_files"):
        plan_archive_sources(
            {},
            requirements=(_requirement(),),
            selection_policy=ArchiveSourceSelectionPolicy(
                latest_count=None,
                max_batch_bytes=None,
                max_batch_files=0,
            ),
        )
