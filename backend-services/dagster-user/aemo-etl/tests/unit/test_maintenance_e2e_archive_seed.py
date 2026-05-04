"""Unit tests for cached e2e archive seed maintenance helpers."""

import datetime as dt
import json
import shutil
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from aemo_etl.maintenance.e2e_archive_seed import (
    DEFAULT_RAW_LATEST_COUNT,
    DEFAULT_ZIP_LATEST_COUNT,
    ArchiveSeedSpec,
    SeedCoverageError,
    SourceTableSeedSpec,
    ZipDomainSeedSpec,
    _zip_domain_seed_spec,
    build_default_gas_model_archive_seed_spec,
    cache_path_for_key,
    default_seed_root,
    load_cached_seed_to_localstack,
    refresh_archive_seed,
    seed_objects_root,
    seed_run_manifest_path,
    seed_spec_path,
)


def _seed_spec() -> ArchiveSeedSpec:
    return ArchiveSeedSpec(
        target="gas_model",
        source_tables=(
            SourceTableSeedSpec(
                table_id="gbb.bronze_table",
                domain="gbb",
                bronze_asset_key=("bronze", "gbb", "bronze_table"),
                silver_asset_key=("silver", "gbb", "silver_table"),
                archive_prefix="bronze/gbb",
                glob_pattern="table_*.csv",
            ),
        ),
        zip_domains=(
            ZipDomainSeedSpec(
                domain="gbb",
                unzipper_asset_key=("bronze", "gbb", "unzipper_gbb"),
                archive_prefix="bronze/gbb",
            ),
        ),
    )


def _s3_client_with_objects(objects: list[dict[str, object]]) -> MagicMock:
    paginator = MagicMock()
    paginator.paginate.return_value = [{"Contents": objects}]
    s3_client = MagicMock()
    s3_client.get_paginator.return_value = paginator
    return s3_client


def test_default_seed_latest_counts() -> None:
    assert DEFAULT_RAW_LATEST_COUNT == 10
    assert DEFAULT_ZIP_LATEST_COUNT == 3


def test_default_seed_root_uses_env_and_repo_layouts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configured_root = tmp_path / "configured"
    monkeypatch.setenv("AEMO_ETL_E2E_SEED_ROOT", str(configured_root))
    assert default_seed_root() == configured_root

    monkeypatch.delenv("AEMO_ETL_E2E_SEED_ROOT")
    repo_root = tmp_path / "repo"
    aemo_etl_dir = repo_root / "backend-services/dagster-user/aemo-etl"
    aemo_etl_dir.mkdir(parents=True)
    (aemo_etl_dir / "pyproject.toml").write_text("", encoding="utf-8")
    monkeypatch.chdir(repo_root)
    assert default_seed_root() == repo_root / "backend-services/.e2e/aemo-etl"

    backend_root = tmp_path / "backend-services"
    backend_aemo_etl_dir = backend_root / "dagster-user/aemo-etl"
    backend_aemo_etl_dir.mkdir(parents=True)
    (backend_aemo_etl_dir / "pyproject.toml").write_text("", encoding="utf-8")
    monkeypatch.chdir(backend_root)
    assert default_seed_root() == backend_root / ".e2e/aemo-etl"

    shutil.rmtree(repo_root)
    shutil.rmtree(backend_root)
    empty_root = tmp_path / "empty"
    empty_root.mkdir()
    monkeypatch.chdir(empty_root)
    assert default_seed_root() == Path("backend-services/.e2e/aemo-etl")


def test_build_default_gas_model_archive_seed_spec_imports_defs(
    mocker: MockerFixture,
) -> None:
    definitions = MagicMock()
    expected_spec = _seed_spec()
    mocker.patch("aemo_etl.definitions.defs", return_value=definitions)
    build_spec = mocker.patch(
        "aemo_etl.maintenance.e2e_archive_seed.build_gas_model_archive_seed_spec",
        return_value=expected_spec,
    )

    assert build_default_gas_model_archive_seed_spec() == expected_spec
    build_spec.assert_called_once_with(definitions)


def test_refresh_archive_seed_writes_failure_manifest_for_shortfall(
    tmp_path: Path,
) -> None:
    s3_client = _s3_client_with_objects(
        [
            {"Key": "bronze/gbb/table_20240101.csv", "Size": 10},
            {"Key": "bronze/gbb/publicrpts_20240101.zip", "Size": 20},
        ]
    )

    with pytest.raises(SeedCoverageError) as error_info:
        refresh_archive_seed(
            s3_client,
            seed_root=tmp_path,
            spec=_seed_spec(),
            archive_bucket="archive",
            raw_latest_count=2,
            zip_latest_count=3,
            current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
        )

    manifest = error_info.value.manifest
    assert manifest.status == "failed"
    assert [entry.name for entry in manifest.shortfalls] == [
        "gbb.bronze_table",
        "gbb",
    ]
    manifest_payload = json.loads(seed_run_manifest_path(tmp_path).read_text())
    assert manifest_payload["status"] == "failed"
    assert manifest_payload["shortfalls"][0]["shortfall"] == 1
    s3_client.download_file.assert_not_called()


def test_refresh_archive_seed_downloads_latest_slice_and_manifest(
    tmp_path: Path,
) -> None:
    s3_client = _s3_client_with_objects(
        [
            {"Key": "bronze/gbb/table_20240101.csv", "Size": 10},
            {"Key": "bronze/gbb/table_20240102.csv", "Size": 11},
            {"Key": "bronze/gbb/table_20240103.csv", "Size": 12},
            {"Key": "bronze/gbb/publicrpts_20240101.zip", "Size": 20},
            {"Key": "bronze/gbb/publicrpts_20240102.zip", "Size": 21},
        ]
    )

    def download_file(_: str, key: str, filename: str) -> None:
        Path(filename).write_text(key, encoding="utf-8")

    s3_client.download_file.side_effect = download_file
    stale_path = cache_path_for_key(tmp_path, "bronze/gbb/stale.csv")
    stale_path.parent.mkdir(parents=True, exist_ok=True)
    stale_path.write_text("stale", encoding="utf-8")

    manifest = refresh_archive_seed(
        s3_client,
        seed_root=tmp_path,
        spec=_seed_spec(),
        archive_bucket="archive",
        raw_latest_count=2,
        zip_latest_count=1,
        current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
    )

    assert manifest.status == "success"
    assert [selected.key for selected in manifest.selected_objects] == [
        "bronze/gbb/publicrpts_20240102.zip",
        "bronze/gbb/table_20240102.csv",
        "bronze/gbb/table_20240103.csv",
    ]
    assert (
        cache_path_for_key(tmp_path, "bronze/gbb/table_20240103.csv").read_text(
            encoding="utf-8"
        )
        == "bronze/gbb/table_20240103.csv"
    )
    assert not stale_path.exists()
    assert json.loads(seed_spec_path(tmp_path).read_text())["target"] == "gas_model"
    assert (
        json.loads(seed_run_manifest_path(tmp_path).read_text())["status"] == "success"
    )


def test_load_cached_seed_to_localstack_uses_cache_without_live_s3(
    tmp_path: Path,
) -> None:
    for key in (
        "bronze/gbb/table_20240101.csv",
        "bronze/gbb/table_20240102.csv",
        "bronze/gbb/publicrpts_20240101.zip",
    ):
        path = cache_path_for_key(tmp_path, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(key, encoding="utf-8")
    (seed_objects_root(tmp_path) / "bronze/gbb/nested").mkdir()
    s3_client = MagicMock()

    manifest = load_cached_seed_to_localstack(
        s3_client,
        seed_root=tmp_path,
        spec=_seed_spec(),
        archive_bucket="archive",
        landing_bucket="landing",
        raw_latest_count=1,
        zip_latest_count=1,
        current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
    )

    assert manifest.status == "success"
    assert [selected.key for selected in manifest.selected_objects] == [
        "bronze/gbb/publicrpts_20240101.zip",
        "bronze/gbb/table_20240102.csv",
    ]
    assert s3_client.upload_file.call_count == 2
    s3_client.get_paginator.assert_not_called()
    assert (
        json.loads(seed_run_manifest_path(tmp_path).read_text())["landing_bucket"]
        == "landing"
    )


def test_load_cached_seed_to_localstack_records_cache_shortfall(
    tmp_path: Path,
) -> None:
    s3_client = MagicMock()

    with pytest.raises(SeedCoverageError):
        load_cached_seed_to_localstack(
            s3_client,
            seed_root=tmp_path,
            spec=_seed_spec(),
            archive_bucket="archive",
            landing_bucket="landing",
            raw_latest_count=1,
            zip_latest_count=1,
            current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
        )

    payload = json.loads(seed_run_manifest_path(tmp_path).read_text())
    assert payload["status"] == "failed"
    assert {entry["name"] for entry in payload["shortfalls"]} == {
        "gbb.bronze_table",
        "gbb",
    }
    s3_client.upload_file.assert_not_called()


def test_load_cached_seed_to_localstack_records_prefix_shortfall(
    tmp_path: Path,
) -> None:
    seed_objects_root(tmp_path).mkdir(parents=True)

    with pytest.raises(SeedCoverageError):
        load_cached_seed_to_localstack(
            MagicMock(),
            seed_root=tmp_path,
            spec=_seed_spec(),
            archive_bucket="archive",
            landing_bucket="landing",
            raw_latest_count=1,
            zip_latest_count=1,
            current_time=dt.datetime(2024, 1, 1, tzinfo=dt.UTC),
        )

    payload = json.loads(seed_run_manifest_path(tmp_path).read_text())
    assert payload["status"] == "failed"


def test_cache_path_rejects_unsafe_keys(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="invalid S3 key"):
        cache_path_for_key(tmp_path, "../outside.csv")


def test_zip_domain_seed_spec_returns_none_without_unzipper_asset() -> None:
    assert _zip_domain_seed_spec("gbb", {}) is None


def test_latest_counts_must_be_positive(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="raw_latest_count"):
        load_cached_seed_to_localstack(
            MagicMock(),
            seed_root=tmp_path,
            spec=_seed_spec(),
            archive_bucket="archive",
            landing_bucket="landing",
            raw_latest_count=0,
            zip_latest_count=1,
        )
