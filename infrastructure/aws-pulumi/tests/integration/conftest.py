"""Shared fixtures for post-deployment integration tests.

All fixtures are session-scoped for efficiency — boto3 clients are created once
per test session. Every fixture that needs live AWS access depends on
`integration_enabled`, which skips the entire suite unless
PULUMI_INTEGRATION_TESTS=1 is set in the environment.

Usage:
    PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/integration/ -v
"""

import os
import pathlib

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.integration)


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
def stack_config_path(stack_name: str) -> pathlib.Path:
    return pathlib.Path(f"Pulumi.{stack_name}.yaml")


@pytest.fixture(scope="session")
def environment(stack_name: str) -> str:
    """Environment prefix extracted from the stack name, e.g. 'dev'."""
    return stack_name.split("-")[0]


@pytest.fixture(scope="session")
def resource_name(environment: str) -> str:
    """Canonical resource name prefix, e.g. 'dev-energy-market'."""
    return f"{environment}-energy-market"


@pytest.fixture(scope="session")
def base_url(
    integration_enabled: None, stack_name: str, stack_config_path: pathlib.Path
) -> str:
    """Base URL for the selected stack.

    Resolution order:
      1. PULUMI_BASE_URL env var (explicit CI/test override)
      2. aws-pulumi:website_root_url in Pulumi.<stack>.yaml
    """
    env_url = os.environ.get("PULUMI_BASE_URL")
    if env_url:
        return env_url.rstrip("/")

    if not stack_config_path.exists():
        pytest.fail(
            f"Stack config {stack_config_path} not found for stack {stack_name!r}. "
            "Set PULUMI_BASE_URL to override the test target."
        )

    prefix = "  aws-pulumi:website_root_url:"
    for line in stack_config_path.read_text().splitlines():
        if line.startswith(prefix):
            value = line.split(":", 2)[-1].strip()
            if value:
                return value.rstrip("/")

    pytest.fail(
        f"aws-pulumi:website_root_url not found in {stack_config_path}. "
        "Set PULUMI_BASE_URL to override the test target."
    )


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
def route53_client(integration_enabled: None):
    """Boto3 Route53 client."""
    try:
        import boto3

        return boto3.client("route53")
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
