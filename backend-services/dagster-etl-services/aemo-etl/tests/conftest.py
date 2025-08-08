import os
import socket
from collections.abc import Generator

import pytest
from polars import Config
from types_boto3_dynamodb import DynamoDBClient
from types_boto3_s3 import S3Client

# pyright: reportUnusedParameter=false, reportTypedDictNotRequiredAccess=false, reportArgumentType=false, reportMissingTypeStubs=false

_ = Config.set_tbl_width_chars(1000)
_ = Config.set_tbl_rows(1000)
_ = Config.set_tbl_cols(100)


def find_open_port(start_port: int, end_port: int) -> int | None:
    for port in range(start_port, end_port + 1):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("localhost", port))
            s.close()
            return port
        except OSError:
            pass
    return None


@pytest.fixture(scope="session", autouse=True)
def aws_credentials() -> None:
    """Mocked AWS Credentials for moto."""
    _ = os.environ.pop("AWS_PROFILE", None)

    os.environ["DEVELOPMENT_ENVIRONMENT"] = "dev"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["AWS_ALLOW_HTTP"] = "true"
    os.environ["AWS_S3_LOCKING_PROVIDER"] = "dynamodb"


# Note: pick an appropriate fixture "scope" for your use case
@pytest.fixture(scope="function")
def moto_server(aws_credentials: None) -> Generator[str]:
    from moto.server import ThreadedMotoServer

    start_port = 5000
    end_port = 6000

    open_port = find_open_port(start_port, end_port)

    assert open_port is not None, "could not find a free port"

    """Fixture to run a mocked AWS server for testing."""
    server = ThreadedMotoServer(port=open_port, ip_address="127.0.0.1")
    server.start()
    host, port = server.get_host_and_port()
    uri = f"http://{host}:{port}"
    os.environ["AWS_ENDPOINT_URL"] = uri
    yield uri
    server.stop()


@pytest.fixture(scope="function")
def s3(moto_server: None) -> Generator[S3Client]:
    import boto3

    client = boto3.client(
        "s3",
        endpoint_url=moto_server,
    )
    yield client
    client.close()


@pytest.fixture(scope="function")
def dynamodb(moto_server: None) -> Generator[DynamoDBClient]:
    import boto3

    client = boto3.client(
        "dynamodb",
        endpoint_url=moto_server,
    )
    yield client
    client.close()


@pytest.fixture(
    scope="function",
)
def create_buckets(s3: S3Client):
    from aemo_etl.configuration import BRONZE_BUCKET, IO_MANAGER_BUCKET, LANDING_BUCKET

    _ = s3.create_bucket(
        Bucket=IO_MANAGER_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
    )

    _ = s3.create_bucket(
        Bucket=BRONZE_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
    )

    _ = s3.create_bucket(
        Bucket=LANDING_BUCKET,
        CreateBucketConfiguration={"LocationConstraint": "ap-southeast-2"},
    )

    yield

    for bucket_name in (LANDING_BUCKET, BRONZE_BUCKET, IO_MANAGER_BUCKET):
        # List and delete all objects
        response = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in response:
            objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
            _ = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": objects})

        # Delete the bucket
        _ = s3.delete_bucket(Bucket=bucket_name)


@pytest.fixture(
    scope="function",
)
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
