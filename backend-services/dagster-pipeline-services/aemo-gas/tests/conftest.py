import os
from collections.abc import Generator

import boto3
import pytest
from moto.server import ThreadedMotoServer
from types_boto3_s3 import S3Client
from types_boto3_dynamodb import DynamoDBClient
from moto import mock_aws


@pytest.fixture(scope="session")
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["AWS_ALLOW_HTTP"] = "true"
    os.environ["AWS_S3_ALLOW_UNSAFE_RENAME"] = "true"

    os.environ["DEVELOPMENT_LOCATION"] = "pytest"


# Note: pick an appropriate fixture "scope" for your use case
@pytest.fixture(scope="session")
def moto_server(aws_credentials: None) -> Generator[str]:  # pyright: ignore[reportUnusedParameter]
    """Fixture to run a mocked AWS server for testing."""
    server = ThreadedMotoServer(port=0, ip_address="127.0.0.1")
    server.start()
    host, port = server.get_host_and_port()
    uri = f"http://{host}:{port}"
    os.environ["AWS_ENDPOINT_URL"] = uri
    yield uri
    server.stop()


@pytest.fixture(scope="function")
def s3(moto_server: None) -> Generator[S3Client]:  # pyright: ignore[reportUnusedParameter]
    client = boto3.client("s3")
    yield client
    client.close()


@pytest.fixture(scope="function")
def dynamodb(moto_server: None) -> Generator[DynamoDBClient]:  # pyright: ignore[reportUnusedParameter]
    client = boto3.client("dynamodb")
    yield client
    client.close()


@pytest.fixture(scope="function")
def create_buckets(s3: S3Client):
    from aemo_gas.configurations import BRONZE_BUCKET, LANDING_BUCKET

    _ = s3.create_bucket(
        Bucket=BRONZE_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
    )

    _ = s3.create_bucket(
        Bucket=LANDING_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
    )

    yield

    for bucket_name in (LANDING_BUCKET, BRONZE_BUCKET):
        # List and delete all objects
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]  # pyright: ignore[reportTypedDictNotRequiredAccess]
            _ = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})  # pyright: ignore[reportArgumentType]

        # Delete the bucket
        _ = s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture(scope="function")
def create_delta_log(dynamodb: DynamoDBClient):
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
