"""Shared fixtures for post-deployment integration tests.

All fixtures are session-scoped for efficiency — boto3 clients are created once
per test session. Every fixture that needs live AWS access depends on
`integration_enabled`, which skips the entire suite unless
PULUMI_INTEGRATION_TESTS=1 is set in the environment.

Usage:
    PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/integration/ -v
"""

import os

import pytest

# ---------------------------------------------------------------------------
# Skip guard
# ---------------------------------------------------------------------------

_INTEGRATION_ENABLED = os.environ.get("PULUMI_INTEGRATION_TESTS") == "1"


@pytest.fixture(scope="session", autouse=True)
def integration_enabled() -> None:
    """Skip ALL integration tests unless PULUMI_INTEGRATION_TESTS=1 is set.

    autouse=True applies this to every test in the integration suite, so even
    tests that don't use a boto3 client fixture are still skipped correctly.
    """
    if not _INTEGRATION_ENABLED:
        pytest.skip(
            "Integration tests disabled. Set PULUMI_INTEGRATION_TESTS=1 to enable."
        )


# ---------------------------------------------------------------------------
# Stack / resource name helpers
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def aws_region() -> str:
    return os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-2")


@pytest.fixture(scope="session")
def stack_name() -> str:
    """Pulumi stack name — override with PULUMI_STACK env var."""
    return os.environ.get("PULUMI_STACK", "dev-ausenergymarket")


@pytest.fixture(scope="session")
def environment(stack_name: str) -> str:
    """Environment prefix extracted from the stack name, e.g. 'dev'."""
    return stack_name.split("-")[0]


@pytest.fixture(scope="session")
def resource_name(environment: str) -> str:
    """Canonical resource name prefix, e.g. 'dev-energy-market'."""
    return f"{environment}-energy-market"


# ---------------------------------------------------------------------------
# AWS boto3 client fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def ecs_client(integration_enabled: None, aws_region: str):
    """Boto3 ECS client."""
    try:
        import boto3

        return boto3.client("ecs", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def ssm_client(integration_enabled: None, aws_region: str):
    """Boto3 SSM client."""
    try:
        import boto3

        return boto3.client("ssm", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def servicediscovery_client(integration_enabled: None, aws_region: str):
    """Boto3 Service Discovery client."""
    try:
        import boto3

        return boto3.client("servicediscovery", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def logs_client(integration_enabled: None, aws_region: str):
    """Boto3 CloudWatch Logs client."""
    try:
        import boto3

        return boto3.client("logs", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def s3_client(integration_enabled: None, aws_region: str):
    """Boto3 S3 client."""
    try:
        import boto3

        return boto3.client("s3", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def dynamodb_client(integration_enabled: None, aws_region: str):
    """Boto3 DynamoDB client."""
    try:
        import boto3

        return boto3.client("dynamodb", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")


@pytest.fixture(scope="session")
def ec2_client(integration_enabled: None, aws_region: str):
    """Boto3 EC2 client."""
    try:
        import boto3

        return boto3.client("ec2", region_name=aws_region)
    except ImportError as exc:
        pytest.skip(f"boto3 not installed: {exc}")
