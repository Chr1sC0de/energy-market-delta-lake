"""Tests for the ad hoc VicGas public report zip-file download job."""

from io import BytesIO
from unittest.mock import MagicMock, call

from dagster import build_op_context
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
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts01.zip">PublicRpts01.zip</a>
    <a href="/REPORTS/CURRENT/VicGas/PublicRpts24.zip">PublicRpts24.zip</a>
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
        build_op_context(), _FakeS3Resource(s3_client)
    )

    requests_get.assert_called_once_with(module.REPORT_URL, timeout=30)
    response.raise_for_status.assert_called_once()
    response_getter.assert_has_calls(
        [
            call("https://nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts01.zip"),
            call("https://nemweb.com.au/REPORTS/CURRENT/VicGas/PublicRpts24.zip"),
        ]
    )
    upload_calls = s3_client.upload_fileobj.call_args_list
    assert len(upload_calls) == 2
    first_file, first_bucket, first_key = upload_calls[0].args
    second_file, second_bucket, second_key = upload_calls[1].args

    assert isinstance(first_file, BytesIO)
    assert first_file.getvalue() == b"zip-01"
    assert first_bucket == LANDING_BUCKET
    assert first_key == module.S3_PREFIX

    assert isinstance(second_file, BytesIO)
    assert second_file.getvalue() == b"zip-24"
    assert second_bucket == LANDING_BUCKET
    assert second_key == module.S3_PREFIX


def test_download_vicgas_public_report_zip_files_job_name() -> None:
    assert (
        module.download_vicgas_public_report_zip_files_job.name
        == "download_vicgas_public_report_zip_files_job"
    )
