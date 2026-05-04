"""Unit tests for the e2e archive seed CLI."""

import argparse
import datetime as dt
import json
from pathlib import Path
from unittest.mock import MagicMock

import boto3
import pytest
from pytest_mock import MockerFixture

from aemo_etl.cli import e2e_archive_seed as cli
from aemo_etl.maintenance.e2e_archive_seed import (
    DEFAULT_ARCHIVE_SEED_BUCKET,
    DEFAULT_RAW_LATEST_COUNT,
    DEFAULT_ZIP_LATEST_COUNT,
    ArchiveSeedSpec,
    SeedCoverageError,
    SeedRunManifest,
    SeedRunStatus,
)


def _seed_spec() -> ArchiveSeedSpec:
    return ArchiveSeedSpec(target="gas_model", source_tables=(), zip_domains=())


def _manifest(tmp_path: Path, *, status: SeedRunStatus = "success") -> SeedRunManifest:
    return SeedRunManifest(
        operation="refresh",
        status=status,
        generated_at=dt.datetime.now(dt.UTC),
        seed_root=tmp_path,
        archive_bucket="archive",
        landing_bucket=None,
        raw_latest_count=1,
        zip_latest_count=1,
        spec=_seed_spec(),
        source_table_coverage=(),
        zip_domain_coverage=(),
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


def test_spec_command_emits_seed_spec_json(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "_default_spec", return_value=_seed_spec())

    assert cli.main(["spec"]) == 0

    assert json.loads(capsys.readouterr().out) == {
        "target": "gas_model",
        "source_tables": [],
        "zip_domains": [],
    }


def test_refresh_command_uses_configurable_defaults(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    s3_client = MagicMock()
    refresh_archive_seed = mocker.patch.object(
        cli,
        "refresh_archive_seed",
        return_value=_manifest(tmp_path),
    )
    mocker.patch.object(cli, "_default_spec", return_value=_seed_spec())
    mocker.patch.object(cli, "make_s3_client", return_value=s3_client)

    assert cli.main(["refresh", "--seed-root", str(tmp_path)]) == 0

    refresh_archive_seed.assert_called_once_with(
        s3_client,
        seed_root=tmp_path,
        spec=_seed_spec(),
        archive_bucket=DEFAULT_ARCHIVE_SEED_BUCKET,
        raw_latest_count=DEFAULT_RAW_LATEST_COUNT,
        zip_latest_count=DEFAULT_ZIP_LATEST_COUNT,
    )
    assert json.loads(capsys.readouterr().out)["status"] == "success"


def test_load_localstack_command_uses_landing_bucket(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    s3_client = MagicMock()
    manifest = _manifest(tmp_path)
    load_cached_seed = mocker.patch.object(
        cli,
        "load_cached_seed_to_localstack",
        return_value=manifest,
    )
    mocker.patch.object(cli, "_default_spec", return_value=_seed_spec())
    mocker.patch.object(cli, "make_s3_client", return_value=s3_client)

    assert (
        cli.main(
            [
                "load-localstack",
                "--seed-root",
                str(tmp_path),
                "--landing-bucket",
                "landing",
                "--raw-latest-count",
                "2",
                "--zip-latest-count",
                "1",
            ]
        )
        == 0
    )

    load_cached_seed.assert_called_once_with(
        s3_client,
        seed_root=tmp_path,
        spec=_seed_spec(),
        archive_bucket=DEFAULT_ARCHIVE_SEED_BUCKET,
        landing_bucket="landing",
        raw_latest_count=2,
        zip_latest_count=1,
    )
    assert json.loads(capsys.readouterr().out)["status"] == "success"


def test_coverage_error_returns_nonzero_with_manifest_path(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "_default_spec", return_value=_seed_spec())
    mocker.patch.object(cli, "make_s3_client", return_value=MagicMock())
    mocker.patch.object(
        cli,
        "refresh_archive_seed",
        side_effect=SeedCoverageError(_manifest(tmp_path, status="failed")),
    )

    assert cli.main(["refresh", "--seed-root", str(tmp_path)]) == 1

    error_output = capsys.readouterr().err
    assert "archive seed coverage shortfall" in error_output
    assert "seed-run-manifest.json" in error_output


def test_default_spec_delegates_to_maintenance_builder(
    mocker: MockerFixture,
) -> None:
    build_spec = mocker.patch.object(
        cli,
        "build_default_gas_model_archive_seed_spec",
        return_value=_seed_spec(),
    )

    assert cli._default_spec() == _seed_spec()
    build_spec.assert_called_once_with()


def test_value_error_exits_with_parser_error(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "_default_spec", side_effect=ValueError("bad input"))

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["spec"])

    assert exit_info.value.code == 2
    assert "bad input" in capsys.readouterr().err


def test_unexpected_error_returns_nonzero(
    capsys: pytest.CaptureFixture[str],
    mocker: MockerFixture,
) -> None:
    mocker.patch.object(cli, "_default_spec", side_effect=RuntimeError("boom"))

    assert cli.main(["spec"]) == 1
    assert "boom" in capsys.readouterr().err
