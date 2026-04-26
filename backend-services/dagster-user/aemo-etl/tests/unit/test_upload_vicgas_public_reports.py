"""Tests for the ad hoc VicGas public report upload script."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock

from pytest_mock import MockerFixture


def _load_script() -> ModuleType:
    script_path = (
        Path(__file__).resolve().parents[2]
        / "scripts"
        / "upload_vicgas_public_reports.py"
    )
    spec = importlib.util.spec_from_file_location(
        "upload_vicgas_public_reports", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_select_zip_links_selects_public_reports_only_by_default() -> None:
    module = _load_script()
    html = """
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/CurrentDay.zip">CurrentDay.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/INT047.CSV">INT047.CSV</a>
    """

    selected = module.select_zip_links(html)

    assert [link.filename for link in selected] == ["PublicRpts01.zip"]


def test_select_zip_links_includes_current_day_when_requested() -> None:
    module = _load_script()
    html = """
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/CurrentDay.zip">CurrentDay.zip</a>
    """

    selected = module.select_zip_links(html, include_current_day=True)

    assert [link.filename for link in selected] == [
        "PublicRpts01.zip",
        "CurrentDay.zip",
    ]


def test_select_zip_links_can_select_specific_report() -> None:
    module = _load_script()
    html = """
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts24.zip">PublicRpts24.zip</a>
    """

    selected = module.select_zip_links(html, report_names={"PublicRpts24.zip"})

    assert [link.filename for link in selected] == ["PublicRpts24.zip"]


def test_upload_report_dry_run_does_not_upload(
    mocker: MockerFixture, tmp_path: Path
) -> None:
    module = _load_script()
    report = module.ReportLink("PublicRpts24.zip", "https://example.test/report.zip")
    temp_file = tmp_path / "report.zip"
    temp_file.write_bytes(b"zip")
    s3_client = MagicMock()

    mocker.patch.object(
        module, "download_to_tempfile", return_value=(temp_file, len(b"zip"))
    )
    mocker.patch.object(module, "object_exists_with_size", return_value=False)

    result = module.upload_report(
        s3_client=s3_client,
        report=report,
        bucket="landing",
        prefix="bronze/vicgas",
        dry_run=True,
        temp_dir=tmp_path,
    )

    assert result.startswith("would upload:")
    s3_client.upload_fileobj.assert_not_called()
