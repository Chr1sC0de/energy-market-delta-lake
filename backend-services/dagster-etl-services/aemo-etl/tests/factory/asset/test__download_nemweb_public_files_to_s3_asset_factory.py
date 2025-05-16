import datetime as dt
import pathlib as pt
from io import BytesIO

import dagster as dg
import pytest
from dagster_aws.s3 import S3Resource
from types_boto3_s3 import S3Client

import aemo_etl
from aemo_etl.configuration import LANDING_BUCKET, Link

# pyright: reportUnusedParameter=false, reportUnknownMemberType=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownArgumentType=false

cwd = pt.Path(__file__).parent

mock_data_folder = cwd / "@mockdata"

mock_files = list((mock_data_folder / "upload_sample_1").glob("*"))


@pytest.fixture(scope="function", autouse=True)
def upload_mock_data_to_s3(create_buckets: None, create_delta_log: None, s3: S3Client):
    for file in mock_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=LANDING_BUCKET,
            Key=f"aemo/vicgas/{file.name}",
        )


def mocked_get_links_fn(*_) -> list[Link]:
    output = []
    for file in mock_files:
        output.append(
            Link(
                source_absolute_href=file.as_posix(),
                source_upload_datetime=dt.datetime.now(),
            )
        )
    return output


def mocked_get_buffer_from_link_fn(link: Link) -> BytesIO:
    return BytesIO(pt.Path(link.source_absolute_href).read_bytes())


def mocked_link_filters(*_) -> bool:
    return True


def test__download_nemweb_public_files_to_s3_asset_factory(s3: S3Client):
    key_prefix = ["bronze", "aemo", "vicgas"]
    schema = "aemo_vicgas"
    table_name = "bronze_vicgas_downloaded_public_files"

    asset = aemo_etl.factory.asset.download_nemweb_public_files_to_s3_asset_factory(
        io_manager_key="in_memory_io_manager",
        key_prefix=key_prefix,
        nemweb_relative_href="REPORTS/CURRENT/VicGas",
        s3_source_bucket=LANDING_BUCKET,
        s3_source_prefix=schema,
        name=table_name,
        override_get_links_fn=mocked_get_links_fn,
        get_buffer_from_link_hook=mocked_get_buffer_from_link_fn,
        link_filter=mocked_link_filters,
    )

    result = dg.materialize(
        assets=[asset],
        resources={
            "s3_resource": S3Resource(),
            "in_memory_io_manager": dg.InMemoryIOManager(),
        },
    )

    value_for_node = result.output_for_node(
        "bronze__aemo__vicgas__bronze_vicgas_downloaded_public_files.final_passthrough_op"
    )

    assert value_for_node.collect().shape == (
        23,
        7,
    )
