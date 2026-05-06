"""Tests for the ad hoc VicGas public report zip-file download job."""

from io import BytesIO
from unittest.mock import MagicMock, call

from dagster import build_op_context
import pytest
from pytest_mock import MockerFixture

from aemo_etl.configs import LANDING_BUCKET
from aemo_etl.defs.jobs import download_vicgas_public_report_zip_files as module


class _FakeS3Resource:
    def __init__(self, client: MagicMock) -> None:
        self._client = client

    def get_client(self) -> MagicMock:
        return self._client


def test_download_vicgas_public_report_zip_files_op_uploads_selected_reports(
    mocker: MockerFixture,
) -> None:
    html = """
    <a href="../">[To Parent Directory]</a>
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts24.zip">PublicRpts24.zip</a>
    <a href="PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/CurrentDay.zip">CurrentDay.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/INT047.CSV">INT047.CSV</a>
    <a>Missing href</a>
    """
    response = mocker.MagicMock(text=html)
    response.raise_for_status.return_value = None
    requests_get = mocker.patch(
        "aemo_etl.defs.jobs.download_vicgas_public_report_zip_files.requests.get",
        return_value=response,
    )
    response_getter = mocker.MagicMock(side_effect=[b"zip-01", b"zip-24"])
    mocker.patch.object(module, "get_response_factory", return_value=response_getter)
    s3_client = mocker.MagicMock()

    module.download_vicgas_public_report_zip_files_op(
        build_op_context(),
        _FakeS3Resource(s3_client),
        module.PublicReportZipDownloadConfig(),
    )

    requests_get.assert_called_once_with(module.REPORT_URL, timeout=30)
    response.raise_for_status.assert_called_once()
    response_getter.assert_has_calls(
        [
            call("https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts01.zip"),
            call("https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts24.zip"),
        ]
    )
    upload_calls = s3_client.upload_fileobj.call_args_list
    assert len(upload_calls) == 2
    first_file, first_bucket, first_key = upload_calls[0].args
    second_file, second_bucket, second_key = upload_calls[1].args

    assert isinstance(first_file, BytesIO)
    assert first_file.getvalue() == b"zip-01"
    assert first_bucket == LANDING_BUCKET
    assert first_key == f"{module.S3_PREFIX}/PublicRpts01.zip"

    assert isinstance(second_file, BytesIO)
    assert second_file.getvalue() == b"zip-24"
    assert second_bucket == LANDING_BUCKET
    assert second_key == f"{module.S3_PREFIX}/PublicRpts24.zip"


def test_download_vicgas_public_report_zip_files_op_honours_target_files(
    mocker: MockerFixture,
) -> None:
    html = """
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts24.zip">PublicRpts24.zip</a>
    """
    response = mocker.MagicMock(text=html)
    response.raise_for_status.return_value = None
    mocker.patch(
        "aemo_etl.defs.jobs.download_vicgas_public_report_zip_files.requests.get",
        return_value=response,
    )
    response_getter = mocker.MagicMock(return_value=b"zip-24")
    mocker.patch.object(module, "get_response_factory", return_value=response_getter)
    s3_client = mocker.MagicMock()

    module.download_vicgas_public_report_zip_files_op(
        build_op_context(),
        _FakeS3Resource(s3_client),
        module.PublicReportZipDownloadConfig(target_files=["publicrpts24.zip"]),
    )

    response_getter.assert_called_once_with(
        "https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts24.zip"
    )
    _, _, s3_key = s3_client.upload_fileobj.call_args.args
    assert s3_key == f"{module.S3_PREFIX}/PublicRpts24.zip"


@pytest.mark.parametrize(
    ("target_file", "match"),
    [
        ("../PublicRpts01.zip", "basename-only"),
        ("CurrentDay.zip", "PublicRptsNN.zip"),
        ("PublicRpts03.zip", "not present"),
    ],
)
def test_download_vicgas_public_report_zip_files_op_rejects_invalid_targets(
    mocker: MockerFixture,
    target_file: str,
    match: str,
) -> None:
    html = """
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    """
    response = mocker.MagicMock(text=html)
    response.raise_for_status.return_value = None
    mocker.patch(
        "aemo_etl.defs.jobs.download_vicgas_public_report_zip_files.requests.get",
        return_value=response,
    )
    get_response_factory = mocker.patch.object(module, "get_response_factory")
    s3_client = mocker.MagicMock()

    with pytest.raises(ValueError, match=match):
        module.download_vicgas_public_report_zip_files_op(
            build_op_context(),
            _FakeS3Resource(s3_client),
            module.PublicReportZipDownloadConfig(target_files=[target_file]),
        )

    get_response_factory.assert_not_called()
    s3_client.upload_fileobj.assert_not_called()


def test_download_sttm_day_zip_files_op_uploads_target_day_zip(
    mocker: MockerFixture,
) -> None:
    html = """
    <a href="../">[To Parent Directory]</a>
    <a href="/REPORTS/CURRENT/STTM/DAY01.ZIP">DAY01.ZIP</a>
    <a href="/REPORTS/CURRENT/STTM/CURRENTDAY.ZIP">CURRENTDAY.ZIP</a>
    <a href="/REPORTS/CURRENT/STTM/DAY31.ZIP">DAY31.ZIP</a>
    <a href="/REPORTS/CURRENT/STTM/DAY00.ZIP">DAY00.ZIP</a>
    <a href="/REPORTS/CURRENT/STTM/INT651.CSV">INT651.CSV</a>
    """
    response = mocker.MagicMock(text=html)
    response.raise_for_status.return_value = None
    requests_get = mocker.patch(
        "aemo_etl.defs.jobs.download_vicgas_public_report_zip_files.requests.get",
        return_value=response,
    )
    response_getter = mocker.MagicMock(return_value=b"day-31")
    mocker.patch.object(module, "get_response_factory", return_value=response_getter)
    s3_client = mocker.MagicMock()

    module.download_sttm_day_zip_files_op(
        build_op_context(),
        _FakeS3Resource(s3_client),
        module.PublicReportZipDownloadConfig(target_files=["day31.zip"]),
    )

    requests_get.assert_called_once_with(module.STTM_REPORT_URL, timeout=30)
    response_getter.assert_called_once_with(
        "https://www.nemweb.com.au/REPORTS/CURRENT/STTM/DAY31.ZIP"
    )
    uploaded_file, bucket, s3_key = s3_client.upload_fileobj.call_args.args
    assert isinstance(uploaded_file, BytesIO)
    assert uploaded_file.getvalue() == b"day-31"
    assert bucket == LANDING_BUCKET
    assert s3_key == f"{module.STTM_S3_PREFIX}/DAY31.ZIP"


def test_zip_selection_logs_selected_and_skipped_targets(mocker: MockerFixture) -> None:
    context = mocker.MagicMock()
    candidates = [
        module.ZipCandidate(
            filename="PublicRpts01.zip",
            url="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts01.zip",
        ),
        module.ZipCandidate(
            filename="PublicRpts24.zip",
            url="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts24.zip",
        ),
    ]

    selected = module._select_zip_candidates(
        context,
        candidates=candidates,
        listing_skipped_filenames=[],
        target_files=["PublicRpts24.zip"],
        spec=module.VICGAS_ZIP_DOWNLOAD_SPEC,
    )

    assert selected == [candidates[1]]
    context.log.info.assert_has_calls(
        [
            call("vicgas zip selected files: PublicRpts24.zip"),
            call("vicgas zip skipped files: PublicRpts01.zip"),
        ]
    )


def test_zip_selection_helpers_reject_empty_targets_and_non_tags() -> None:
    assert module._is_basename("") is False
    assert (
        module._candidate_from_link(object(), spec=module.VICGAS_ZIP_DOWNLOAD_SPEC)
        is None
    )


def test_download_vicgas_public_report_zip_files_job_name() -> None:
    assert (
        module.download_vicgas_public_report_zip_files_job.name
        == "download_vicgas_public_report_zip_files_job"
    )


def test_download_sttm_day_zip_files_job_name() -> None:
    assert (
        module.download_sttm_day_zip_files_job.name == "download_sttm_day_zip_files_job"
    )
