from collections.abc import Iterable, Mapping
from typing import cast
from unittest.mock import MagicMock

import polars as pl
from botocore.exceptions import ClientError
from dagster import AssetKey, RunConfig, RunRequest
from dagster_aws.s3 import S3Resource
from polars._typing import PolarsDataType
from polars import DataFrame
from types_boto3_s3 import S3Client

from aemo_etl.configs import AEMO_BUCKET, ARCHIVE_BUCKET, LANDING_BUCKET
from aemo_etl.definitions import defs
from aemo_etl.defs.raw.sttm._manifest import (
    get_sttm_report_manifest,
    sttm_landing_only_gap_report_ids,
    sttm_report_schema,
)
from aemo_etl.factories.df_from_s3_keys.assets import (
    DFFromS3KeysConfiguration,
    SOURCE_CONTENT_HASH_COLUMN,
    get_source_content_hash,
    source_content_hash_columns,
    with_source_content_hash_schema,
)
from aemo_etl.utils import get_surrogate_key

ROOT_DEFINITIONS = defs()
REPOSITORY_DEF = ROOT_DEFINITIONS.get_repository_def()
INT651_REPORT = get_sttm_report_manifest("INT651")
INT651_SUFFIX = INT651_REPORT["name_suffix"]
INT651_LANDING_KEY = f"bronze/sttm/{INT651_SUFFIX}~20260506090000.csv"
INT651_BRONZE_KEY = AssetKey(["bronze", "sttm", f"bronze_{INT651_SUFFIX}"])
INT651_SILVER_KEY = AssetKey(["silver", "sttm", f"silver_{INT651_SUFFIX}"])
INT651_ROW: dict[str, str | None] = {
    "gas_date": "2026-05-06",
    "hub_identifier": "SYD",
    "hub_name": "Sydney",
    "schedule_identifier": "EA-0001",
    "ex_ante_market_price": "12.34",
    "administered_price_period": "N",
    "cap_applied": "N",
    "administered_price_cap": None,
    "schedule_price": None,
    "approval_datetime": "2026-05-05 13:00:00",
    "report_datetime": "2026-05-05 13:15:00",
}
INT651_CSV = (
    ",".join(INT651_ROW)
    + "\n"
    + ",".join("" if value is None else value for value in INT651_ROW.values())
    + "\n"
).encode()
STTM_GAP_KEYS = (
    "bronze/sttm/int685_v1_sttm_prices_rpt_13.csv",
    "bronze/sttm/int685b_v1_sttm_prices_rpt_13.csv",
)


def _object_exists(s3: S3Client, *, bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code")
        if error_code in {"404", "NoSuchKey", "NotFound"}:
            return False
        raise
    return True


def _put_text_object(s3: S3Client, *, key: str, body: bytes) -> None:
    s3.put_object(Bucket=LANDING_BUCKET, Key=key, Body=body)


def _sensor_context() -> MagicMock:
    context = MagicMock()
    context.log = MagicMock()
    context.repository_def = REPOSITORY_DEF
    context.instance.get_runs.side_effect = [[], []]
    return context


def _sttm_sensor_run_requests(localstack_endpoint: str) -> list[RunRequest]:
    sensor = next(
        sensor
        for sensor in ROOT_DEFINITIONS.sensors or ()
        if sensor.name == "sttm_event_driven_assets_sensor"
    )
    s3_resource = S3Resource(endpoint_url=localstack_endpoint)
    raw_result = sensor._raw_fn(_sensor_context(), s3=s3_resource)  # type: ignore[attr-defined]
    if raw_result is None:
        return []
    if isinstance(raw_result, RunRequest):
        return [raw_result]
    return list(cast(Iterable[RunRequest], raw_result))


def _s3_keys_from_run_request(
    run_request: RunRequest, asset_key: AssetKey
) -> list[str]:
    run_config = run_request.run_config
    config = run_config["ops"][asset_key.to_python_identifier()]["config"]
    return list(config["s3_keys"])


def _expected_schema() -> Mapping[str, PolarsDataType]:
    return with_source_content_hash_schema(sttm_report_schema(INT651_REPORT))


def _expected_surrogate_key() -> str:
    value = (
        DataFrame([INT651_ROW])
        .lazy()
        .select(get_surrogate_key(["gas_date", "hub_identifier"]).alias("value"))
        .collect()
        .item()
    )
    assert isinstance(value, str)
    return value


def _expected_source_content_hash() -> str:
    source_columns = source_content_hash_columns(_expected_schema())
    value = (
        DataFrame([INT651_ROW])
        .lazy()
        .select(get_source_content_hash(source_columns).alias("value"))
        .collect()
        .item()
    )
    assert isinstance(value, str)
    return value


def _assert_source_table_frame(frame: DataFrame) -> None:
    expected_schema = _expected_schema()
    assert dict(frame.schema) == dict(expected_schema)
    assert frame.height == 1

    row = frame.row(0, named=True)
    assert row["gas_date"] == INT651_ROW["gas_date"]
    assert row["hub_identifier"] == INT651_ROW["hub_identifier"]
    assert row["surrogate_key"] == _expected_surrogate_key()
    assert row[SOURCE_CONTENT_HASH_COLUMN] == _expected_source_content_hash()
    assert row["source_file"] == f"s3://{ARCHIVE_BUCKET}/{INT651_LANDING_KEY}"


def test_sttm_int651_source_table_materializes_through_localstack_s3(
    s3: S3Client,
    localstack_endpoint: str,
) -> None:
    _put_text_object(s3, key=INT651_LANDING_KEY, body=INT651_CSV)
    for gap_key in STTM_GAP_KEYS:
        _put_text_object(s3, key=gap_key, body=b"gap\nvalue\n")

    run_requests = _sttm_sensor_run_requests(localstack_endpoint)

    assert sttm_landing_only_gap_report_ids() == ("INT685", "INT685B")
    assert len(run_requests) == 1
    assert run_requests[0].job_name == f"{INT651_SUFFIX}_job"
    assert _s3_keys_from_run_request(run_requests[0], INT651_BRONZE_KEY) == [
        INT651_LANDING_KEY
    ]

    bronze_result = (
        ROOT_DEFINITIONS.get_implicit_global_asset_job_def().execute_in_process(
            run_config=RunConfig(
                ops={
                    INT651_BRONZE_KEY.to_python_identifier(): DFFromS3KeysConfiguration(
                        s3_keys=[INT651_LANDING_KEY]
                    ),
                }
            ),
            asset_selection=[INT651_BRONZE_KEY],
        )
    )

    assert bronze_result.success
    assert not _object_exists(s3, bucket=LANDING_BUCKET, key=INT651_LANDING_KEY)
    assert _object_exists(s3, bucket=ARCHIVE_BUCKET, key=INT651_LANDING_KEY)
    for gap_key in STTM_GAP_KEYS:
        assert _object_exists(s3, bucket=LANDING_BUCKET, key=gap_key)
        assert not _object_exists(s3, bucket=ARCHIVE_BUCKET, key=gap_key)

    bronze_frame = pl.scan_delta(
        f"s3://{AEMO_BUCKET}/bronze/sttm/bronze_{INT651_SUFFIX}"
    ).collect()
    _assert_source_table_frame(bronze_frame)

    silver_result = (
        ROOT_DEFINITIONS.get_implicit_global_asset_job_def().execute_in_process(
            asset_selection=[INT651_SILVER_KEY],
        )
    )

    assert silver_result.success
    for check in silver_result.get_asset_check_evaluations():
        assert check.passed, check.metadata

    silver_frame = pl.scan_parquet(
        f"s3://{AEMO_BUCKET}/silver/sttm/silver_{INT651_SUFFIX}/*.parquet"
    ).collect()
    _assert_source_table_frame(silver_frame)

    assert _sttm_sensor_run_requests(localstack_endpoint) == []
