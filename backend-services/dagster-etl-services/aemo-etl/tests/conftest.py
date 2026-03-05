import uuid
from typing import Callable, Generator

import boto3
import pytest
from types_boto3_dynamodb import DynamoDBClient
from types_boto3_s3 import S3Client
from types_boto3_s3.type_defs import ObjectIdentifierTypeDef

from tests.utils import (
    LOCALSTACK_IMAGE,
    LOCALSTACK_READY_POLL_INTERVAL,
    LOCALSTACK_READY_TIMEOUT,
    get_unused_port,
    podman,
    wait_for_localstack,
)


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


@pytest.fixture(scope="function")
def s3(localstack_endpoint: str) -> Generator[S3Client]:
    client: S3Client = boto3.client("s3", endpoint_url=localstack_endpoint)
    yield client
    client.close()


@pytest.fixture(scope="function")
def dynamodb(localstack_endpoint: str) -> Generator[DynamoDBClient]:
    client: DynamoDBClient = boto3.client("dynamodb", endpoint_url=localstack_endpoint)
    yield client
    client.close()


@pytest.fixture(scope="function")
def make_bucket(s3: S3Client) -> Generator[Callable[[str], str]]:
    buckets: list[str] = []

    def _make_bucket(prefix: str) -> str:
        bucket_name = f"{prefix}-{uuid.uuid4().hex[:8]}"
        _ = s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
        )
        buckets.append(bucket_name)
        return bucket_name

    yield _make_bucket

    for bucket_name in buckets:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            objects: list[ObjectIdentifierTypeDef] = [
                {"Key": obj["Key"]} for obj in response["Contents"]
            ]
            _ = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})
        _ = s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture(scope="function")
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
