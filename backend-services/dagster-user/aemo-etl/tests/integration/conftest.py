import uuid
from typing import Callable, Generator

import boto3
import pytest
from types_boto3_dynamodb import DynamoDBClient
from types_boto3_s3 import S3Client
from types_boto3_s3.type_defs import ObjectIdentifierTypeDef

from aemo_etl.configs import (
    AEMO_BUCKET,
    ARCHIVE_BUCKET,
    IO_MANAGER_BUCKET,
    LANDING_BUCKET,
)
from aemo_etl.utils import add_random_suffix
from tests.utils import (
    LOCALSTACK_IMAGE,
    LOCALSTACK_READY_POLL_INTERVAL,
    LOCALSTACK_READY_TIMEOUT,
    MakeBucketProtocol,
    get_unused_port,
    podman,
    wait_for_localstack,
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def session_monkeypatch() -> Generator[pytest.MonkeyPatch]:
    monkeypatch = pytest.MonkeyPatch()
    yield monkeypatch
    monkeypatch.undo()


@pytest.fixture(scope="session", autouse=True)
def aws_credentials(session_monkeypatch: pytest.MonkeyPatch) -> None:
    session_monkeypatch.delenv("AWS_PROFILE", raising=False)
    session_monkeypatch.setenv("DEVELOPMENT_ENVIRONMENT", "dev")
    session_monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    session_monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    session_monkeypatch.setenv("AWS_SECURITY_TOKEN", "test")
    session_monkeypatch.setenv("AWS_SESSION_TOKEN", "test")
    session_monkeypatch.setenv("AWS_DEFAULT_REGION", "ap-southeast-2")
    session_monkeypatch.setenv("AWS_ALLOW_HTTP", "true")
    session_monkeypatch.setenv("AWS_S3_LOCKING_PROVIDER", "dynamodb")


@pytest.fixture(scope="session")
def localstack_endpoint(session_monkeypatch: pytest.MonkeyPatch) -> Generator[str]:
    container_name = f"localstack-pytest-{uuid.uuid4().hex[:8]}"
    ip = "127.0.0.1"
    port = get_unused_port()
    podman(
        *[
            "run",
            "--rm",
            "--detach",
            "--network=host",
            "--name",
            container_name,
            "--env",
            "DISABLE_CORS_CHECKS=1",
            "--env",
            f"GATEWAY_LISTEN={ip}:{port}",
            LOCALSTACK_IMAGE,
        ]
    )
    # ip = container_ip(container_name)

    wait_for_localstack(
        endpoint := f"http://{ip}:{port}",
        LOCALSTACK_READY_TIMEOUT,
        LOCALSTACK_READY_POLL_INTERVAL,
    )
    session_monkeypatch.setenv("AWS_ENDPOINT_URL", endpoint)
    yield endpoint
    podman("stop", container_name)


@pytest.fixture(scope="session")
def s3(localstack_endpoint: str) -> Generator[S3Client]:
    client: S3Client = boto3.client("s3", endpoint_url=localstack_endpoint)
    yield client
    client.close()


@pytest.fixture(scope="session")
def dynamodb(localstack_endpoint: str) -> Generator[DynamoDBClient]:
    client: DynamoDBClient = boto3.client("dynamodb", endpoint_url=localstack_endpoint)
    yield client
    client.close()


@pytest.fixture(scope="session")
def make_bucket(s3: S3Client) -> Generator[MakeBucketProtocol]:
    buckets: list[str] = []

    def _make_bucket(bucket_name: str, random_suffix: bool = True) -> str:
        if random_suffix:
            bucket_name = add_random_suffix(bucket_name)
        _ = s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
        )
        buckets.append(bucket_name)
        return bucket_name

    yield _make_bucket

    for bucket_name in buckets:
        continuation_token: str | None = None
        while True:
            if continuation_token is None:
                response = s3.list_objects_v2(Bucket=bucket_name)
            else:
                response = s3.list_objects_v2(
                    Bucket=bucket_name,
                    ContinuationToken=continuation_token,
                )

            objects: list[ObjectIdentifierTypeDef] = [
                {"Key": obj["Key"]} for obj in response.get("Contents", [])
            ]
            if objects:
                _ = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})

            if not response.get("IsTruncated", False):
                break

            continuation_token = response.get("NextContinuationToken")
        _ = s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture(scope="session")
def create_delta_log(dynamodb: DynamoDBClient) -> Generator[None]:
    _ = dynamodb.create_table(
        AttributeDefinitions=[
            {"AttributeName": "fileName", "AttributeType": "S"},
            {"AttributeName": "tablePath", "AttributeType": "S"},
        ],
        KeySchema=[
            {"AttributeName": "tablePath", "KeyType": "HASH"},
            {"AttributeName": "fileName", "KeyType": "RANGE"},
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 5,
            "WriteCapacityUnits": 5,
        },
        TableName="delta_log",
    )
    yield

    _ = dynamodb.delete_table(TableName="delta_log")


@pytest.fixture(scope="session", autouse=True)
def setup(make_bucket: Callable[[str, bool], str], create_delta_log: None) -> None:
    make_bucket(LANDING_BUCKET, False)
    make_bucket(ARCHIVE_BUCKET, False)
    make_bucket(AEMO_BUCKET, False)
    make_bucket(IO_MANAGER_BUCKET, False)
