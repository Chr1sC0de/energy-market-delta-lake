"""Unit tests for the bronze archive replay CLI."""

import argparse
import boto3
import json
from unittest.mock import MagicMock

from polars import Datetime, String
import pytest
from pytest_mock import MockerFixture

from aemo_etl.cli import replay_bronze_archive as cli
from aemo_etl.factories.df_from_s3_keys.assets import SOURCE_CONTENT_HASH_COLUMN
from aemo_etl.factories.df_from_s3_keys.source_tables import (
    DFFromS3KeysSourceTableSpec,
)
from aemo_etl.maintenance.archive_replay import (
    ArchiveObject,
    ArchiveReplayBatch,
    ArchiveReplayMode,
    ArchiveReplayPlan,
    ArchiveReplayResult,
)

_SCHEMA = {
    "col1": String,
    "ingested_timestamp": Datetime("us", time_zone="UTC"),
    "ingested_date": Datetime("us", time_zone="UTC"),
    "surrogate_key": String,
    "source_file": String,
    SOURCE_CONTENT_HASH_COLUMN: String,
}


def _spec(
    *,
    domain: str = "gbb",
    name_suffix: str = "table",
) -> DFFromS3KeysSourceTableSpec:
    return DFFromS3KeysSourceTableSpec(
        domain=domain,
        name_suffix=name_suffix,
        glob_pattern="table*.csv",
        schema=_SCHEMA,
        surrogate_key_sources=("col1",),
    )


def _result(
    *,
    mode: ArchiveReplayMode = "dry-run",
    matching_objects: tuple[ArchiveObject, ...] = (
        ArchiveObject(key="bronze/gbb/table_20240101.csv", size=40),
    ),
    written_batches: int = 0,
    written_files: int = 0,
    skipped_files: tuple[str, ...] = (),
) -> ArchiveReplayResult:
    return ArchiveReplayResult(
        plan=ArchiveReplayPlan(
            spec=_spec(),
            archive_bucket="archive",
            target_table_uri="s3://aemo/bronze/gbb/bronze_table",
            batches=(ArchiveReplayBatch(objects=matching_objects),),
        ),
        mode=mode,
        written_batches=written_batches,
        written_files=written_files,
        skipped_files=skipped_files,
    )


def test_positive_int_rejects_non_positive_values() -> None:
    assert cli._positive_int("5") == 5

    with pytest.raises(argparse.ArgumentTypeError, match="greater than zero"):
        cli._positive_int("0")


def test_make_s3_client_uses_default_or_configured_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    mocker: MockerFixture,
) -> None:
    s3_client = MagicMock()
    boto_client = mocker.patch.object(boto3, "client", return_value=s3_client)

    monkeypatch.delenv("AWS_ENDPOINT_URL", raising=False)
    assert cli.make_s3_client() is s3_client
    boto_client.assert_called_once_with("s3")

    boto_client.reset_mock()
    monkeypatch.setenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    assert cli.make_s3_client() is s3_client
    boto_client.assert_called_once_with("s3", endpoint_url="http://localhost:4566")


def test_emit_results_formats_text_for_dry_run_and_replace(
    capsys: pytest.CaptureFixture[str],
) -> None:
    cli._emit_results(
        (
            _result(),
            _result(
                mode="replace",
                written_batches=1,
                written_files=1,
                skipped_files=("bronze/gbb/skipped.csv",),
            ),
        ),
        json_output=False,
    )

    output = capsys.readouterr().out
    assert "dry-run: gbb.bronze_table" in output
    assert "files:\n    - bronze/gbb/table_20240101.csv" in output
    assert "replace: gbb.bronze_table" in output
    assert "written batches: 1" in output
    assert "skipped files: 1" in output


def test_main_emits_json_for_selected_domain(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    spec = _spec()
    s3_client = MagicMock()
    result = _result()
    mocker.patch.object(cli, "load_source_table_specs", return_value=(spec,))
    mocker.patch.object(cli, "make_s3_client", return_value=s3_client)
    run_archive_replay = mocker.patch.object(
        cli,
        "run_archive_replay",
        return_value=(result,),
    )

    exit_code = cli.main(
        [
            "--domain",
            "gbb",
            "--json",
            "--batch-bytes",
            "5",
            "--batch-files",
            "2",
            "--archive-bucket",
            "archive",
            "--aemo-bucket",
            "aemo",
        ]
    )

    assert exit_code == 0
    assert json.loads(capsys.readouterr().out)[0]["table"] == "gbb.bronze_table"
    run_archive_replay.assert_called_once_with(
        s3_client,
        specs=(spec,),
        replace=False,
        archive_bucket="archive",
        aemo_bucket="aemo",
        max_batch_bytes=5,
        max_batch_files=2,
    )


def test_main_exits_for_invalid_target(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "load_source_table_specs", return_value=())

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["--domain", "missing"])

    assert exit_info.value.code == 2
    assert "unknown source-table domain" in capsys.readouterr().err


def test_main_returns_error_for_unexpected_failure(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "load_source_table_specs", return_value=(_spec(),))
    mocker.patch.object(cli, "make_s3_client", return_value=MagicMock())
    mocker.patch.object(
        cli,
        "run_archive_replay",
        side_effect=RuntimeError("s3 unavailable"),
    )

    assert cli.main(["--all"]) == 1
    assert "s3 unavailable" in capsys.readouterr().err
