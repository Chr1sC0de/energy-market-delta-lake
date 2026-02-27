import uuid
from typing import Generator

import boto3
import pytest
from types_boto3_dynamodb import DynamoDBClient
from types_boto3_s3 import S3Client

from aemo_etl.configs import BRONZE_BUCKET, IO_MANAGER_BUCKET, LANDING_BUCKET
from tests.utils import (
    LOCALSTACK_IMAGE,
    LOCALSTACK_PORT,
    LOCALSTACK_READY_POLL_INTERVAL,
    LOCALSTACK_READY_TIMEOUT,
    container_ip,
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
    session_monkeypatch.setenv("AWS_PROFILE", "")
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
    podman(
        *[
            "run",
            "--rm",
            "--detach",
            "--network=podman",
            "--name",
            container_name,
            "--env",
            "--env",
            "DISABLE_CORS_CHECKS=1",
            LOCALSTACK_IMAGE,
        ]
    )
    ip = container_ip(container_name)
    endpoint = f"http://{ip}:{LOCALSTACK_PORT}"
    wait_for_localstack(
        endpoint, LOCALSTACK_READY_TIMEOUT, LOCALSTACK_READY_POLL_INTERVAL
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
def create_buckets(s3: S3Client) -> Generator[None]:

    for bucket in (IO_MANAGER_BUCKET, BRONZE_BUCKET, LANDING_BUCKET):
        _ = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
        )

    yield

    for bucket_name in (LANDING_BUCKET, BRONZE_BUCKET, IO_MANAGER_BUCKET):
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
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
