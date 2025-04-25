import pathlib as pt

import polars as pl
import pytest

from aemo_gas.configurations import BRONZE_BUCKET
from aemo_gas.vichub import ops
import polars.testing

cwd = pt.Path(__file__).parent
mock_data_folder = cwd / "@mockdata"


mock_downloaded_public_files = pl.scan_parquet(
    mock_data_folder / "downloaded_public_files_mock.parquet"
)

mock_downloaded_public_files_destination = (
    f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/downloaded_public_files"
)


@pytest.fixture(scope="function")
def upload_mock_downloaded_public_files(
    create_buckets: None,
    create_delta_log: None,
) -> None:
    mock_downloaded_public_files.collect().write_delta(
        mock_downloaded_public_files_destination, mode="overwrite"
    )


def test__get_downloaded_public_files(upload_mock_downloaded_public_files: None):
    df = ops.tables.get_downloaded_public_files()
    assert df is not None, "utput is none"
    polars.testing.assert_frame_equal(df, mock_downloaded_public_files)
