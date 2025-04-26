import datetime as dt
import pathlib as pt
import pickle
from types_boto3_s3 import S3Client
from unittest.mock import patch

import dagster as dg
import polars as pl
import polars.testing
import pytest
from dagster_aws.s3 import S3Resource

from aemo_gas import vichub
from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                       variables                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


cwd = pt.Path(__file__).parent

mock_data_folder = cwd / "@mockdata"

mock_downloaded_public_files = pl.scan_parquet(
    mock_data_folder / "mock_downloaded_public_files.parquet"
)

mock_downloaded_public_files_destination = (
    f"s3://{BRONZE_BUCKET}/aemo/gas/vichub/downloaded_public_files"
)

with open(mock_data_folder / "mock_links.pkl", "rb") as f:
    # for brevity only use 10 links
    mocked_links: list[vichub.assets.bronze.mibb.downloaded_public_files.Link] = (
        pickle.load(f)[0:10]
    )

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                        fixtures                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@pytest.fixture(scope="function")
def upload_mock_downloaded_public_files(
    create_buckets: None,
    create_delta_log: None,
) -> None:
    mock_downloaded_public_files.collect().write_delta(
        mock_downloaded_public_files_destination, mode="overwrite"
    )


@pytest.fixture(scope="function")
def upload_mock_zip_files(
    create_buckets: None,
    s3: S3Client,
) -> list[str]:
    keys = []
    for filename in ("mock_zip_1.zip", "mock_zip_2.zip"):
        key = f"aemo/gas/vichub/{filename}"
        s3.upload_file(
            Filename=mock_data_folder / filename,
            Bucket=LANDING_BUCKET,
            Key=key,
        )
        keys.append(key)
    return keys


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                         tests                                          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def test__get_links_op():
    with patch("requests.get") as mocked_requests_get:
        mocked_requests_get.return_value.status_code = 200
        mocked_requests_get.return_value.text = (
            mock_data_folder / "mock_get_links_page.txt"
        ).read_text()
        results = vichub.assets.bronze.mibb.downloaded_public_files.get_links_op(
            dg.build_op_context()
        )

    assert len(results) == 114, (
        "results len does not match original length of mocked data"
    )


def test__create_dynamic_download_group_op():
    results_generator = vichub.assets.bronze.mibb.downloaded_public_files.create_dynamic_download_group_op(
        dg.build_op_context(), mocked_links, mock_downloaded_public_files
    )

    target_filenames = [link.target_filename for link in mocked_links]

    for i, dynamic_group in enumerate(results_generator):
        assert dynamic_group.value.target_filename in target_filenames, (
            "dynamic group filename does not match target filename"
        )


def test__process_link_op(upload_mock_downloaded_public_files: None):
    link = mocked_links[0]

    with patch("requests.get") as mocked_requests_get:
        mocked_requests_get.return_value.status_code = 200
        mocked_requests_get.return_value.content = (
            mock_data_folder / "mock_system_notices.csv"
        ).read_bytes()

        processed_link = (
            vichub.assets.bronze.mibb.downloaded_public_files.process_link_op(
                dg.build_op_context(), S3Resource(), link
            )
        )

    new_filename = link.target_filename.lower().replace("csv", "parquet")

    uploaded_df = pl.read_parquet(
        f"s3://{LANDING_BUCKET}/aemo/gas/vichub/{new_filename}",
    )

    assert processed_link.source_file == link.href, (
        "source link does not match original link"
    )

    polars.testing.assert_frame_equal(
        uploaded_df,
        pl.read_parquet(mock_data_folder / "mock_processed_link_df.parquet"),
    )


def test__combine_to_dataframe_op():
    processed_links: list[
        vichub.assets.bronze.mibb.downloaded_public_files.ProcessedLink
    ] = []

    configurations = [
        {
            "source_file": "source_file_1",
            "target_file": "target_file_1",
            "upload_datetime": dt.datetime.now(),
            "ingested_datetime": dt.datetime.now(),
        },
        {
            "source_file": "source_file_2",
            "target_file": "target_file_2",
            "upload_datetime": dt.datetime.now(),
            "ingested_datetime": dt.datetime.now(),
        },
    ]

    for configuration in configurations:
        processed_links.append(
            vichub.assets.bronze.mibb.downloaded_public_files.ProcessedLink(
                **configuration
            )
        )

    df = vichub.assets.bronze.mibb.downloaded_public_files.combine_to_dataframe_op(
        dg.build_op_context(), processed_links
    )

    schema = dict(
        source_file=pl.String,
        target_file=pl.String,
        upload_datetime=pl.Datetime,
        ingested_datetime=pl.Datetime,
    )

    polars.testing.assert_frame_equal(
        df,
        pl.LazyFrame(
            dict(
                source_file=[link.source_file for link in processed_links],
                target_file=[link.target_file for link in processed_links],
                upload_datetime=[link.upload_datetime for link in processed_links],
                ingested_datetime=[link.ingested_datetime for link in processed_links],
            ),
            schema=schema,
        ),
    )


def test__process_unzip_op(upload_mock_zip_files: list[str]):
    expected_keys = [
        {
            "Bucket": "dev-energy-market-landing",
            "Key": "aemo/gas/vichub/int029a_v4_system_notices_1.parquet",
        },
        {
            "Bucket": "dev-energy-market-landing",
            "Key": "aemo/gas/vichub/int029a_v4_system_notices_1.parquet",
        },
        {
            "Bucket": "dev-energy-market-landing",
            "Key": "aemo/gas/vichub/int039b_v4_indicative_locational_price_1.parquet",
        },
        {
            "Bucket": "dev-energy-market-landing",
            "Key": "aemo/gas/vichub/int050_v4_sched_withdrawals_1.parquet",
        },
    ]

    returned_keys = []

    for key in upload_mock_zip_files:
        returned_keys.extend(
            vichub.assets.bronze.mibb.downloaded_public_files.process_unzip_op(
                dg.build_op_context(), S3Resource(), key
            )
        )

    assert returned_keys == expected_keys
