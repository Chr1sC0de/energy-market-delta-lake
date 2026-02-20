import os
import subprocess
import time
import uuid
from collections.abc import Generator

import boto3
import pytest
import requests
from polars import Config
from types_boto3_dynamodb import DynamoDBClient
from types_boto3_s3 import S3Client

_ = Config.set_tbl_width_chars(1000)
_ = Config.set_tbl_rows(1000)
_ = Config.set_tbl_cols(100)

_LOCALSTACK_IMAGE = "localstack/localstack-pro"
_LOCALSTACK_PORT = 4566
_LOCALSTACK_HEALTH_PATH = "/_localstack/health"
_LOCALSTACK_READY_TIMEOUT = 60  # seconds
_LOCALSTACK_READY_POLL_INTERVAL = 1  # seconds


def _podman(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["podman", "--remote", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def _container_ip(container_name: str) -> str:
    result = _podman(
        "inspect",
        container_name,
        "--format",
        "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
    )
    ip = result.stdout.strip()
    if not ip:
        raise RuntimeError(
            f"Could not determine IP for container {container_name!r}. "
            "Ensure it is running on the podman network."
        )
    return ip


def _wait_for_localstack(endpoint: str, timeout: int, interval: float) -> None:
    deadline = time.monotonic() + timeout
    url = f"{endpoint}{_LOCALSTACK_HEALTH_PATH}"
    last_exc: Exception = RuntimeError("timed out before first attempt")
    while time.monotonic() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return
        except requests.RequestException as exc:
            last_exc = exc
        time.sleep(interval)
    raise TimeoutError(
        f"LocalStack at {endpoint} did not become healthy within {timeout}s. "
        f"Last error: {last_exc}"
    )


@pytest.fixture(scope="session", autouse=True)
def aws_credentials() -> None:
    """Configure AWS environment variables for LocalStack."""
    _ = os.environ.pop("AWS_PROFILE", None)

    os.environ["DEVELOPMENT_ENVIRONMENT"] = "dev"
    os.environ["AWS_ACCESS_KEY_ID"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "ap-southeast-2"
    os.environ["AWS_ALLOW_HTTP"] = "true"
    os.environ["AWS_S3_LOCKING_PROVIDER"] = "dynamodb"


@pytest.fixture(scope="session")
def localstack_endpoint(aws_credentials: None) -> Generator[str]:
    """Start a LocalStack container via podman --remote, yield its HTTP endpoint.

    The container is started on the host podman network.  Because the default
    podman network has dns_enabled=false, the container hostname is not
    resolvable by name; we inspect the container after start to retrieve its
    assigned IP address and build the endpoint URL from that.

    A UUID-based container name is used so concurrent pytest sessions (e.g.
    running tests on multiple git worktrees) never collide.
    """
    container_name = f"localstack-pytest-{uuid.uuid4().hex[:8]}"
    auth_token = os.environ.get("LOCALSTACK_AUTH_TOKEN", "")

    run_args = [
        "run",
        "--rm",
        "--detach",
        "--network=podman",
        "--name",
        container_name,
        "--env",
        f"LOCALSTACK_AUTH_TOKEN={auth_token}",
        "--env",
        "DISABLE_CORS_CHECKS=1",
        _LOCALSTACK_IMAGE,
    ]
    _podman(*run_args)

    try:
        ip = _container_ip(container_name)
        endpoint = f"http://{ip}:{_LOCALSTACK_PORT}"

        _wait_for_localstack(
            endpoint, _LOCALSTACK_READY_TIMEOUT, _LOCALSTACK_READY_POLL_INTERVAL
        )

        os.environ["AWS_ENDPOINT_URL"] = endpoint
        yield endpoint
    finally:
        try:
            _podman("stop", container_name)
        except subprocess.CalledProcessError:
            pass  # container may have already exited


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
    from aemo_etl.configuration import BRONZE_BUCKET, IO_MANAGER_BUCKET, LANDING_BUCKET

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
