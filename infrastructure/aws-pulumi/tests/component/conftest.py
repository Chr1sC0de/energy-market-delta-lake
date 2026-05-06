"""Shared Pulumi mock infrastructure for all unit tests.

The Pulumi runtime mocks MUST be installed before any component module is
imported, so this conftest sets everything up at module-load time — the same
"env-vars-and-patches-first" pattern used in backend-services/authentication/.

Environment variables are also set here before configs.py can be imported
as a side effect of importing any component.
"""

import asyncio
import os
from collections.abc import Callable

import pulumi
import pulumi.runtime
import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.component)


# ---------------------------------------------------------------------------
# 1. Environment variables — set before configs.py is imported
# ---------------------------------------------------------------------------
os.environ.setdefault("ADMINISTRATOR_IPS", "10.0.0.1")
os.environ.setdefault("ENVIRONMENT", "test")
# Prevent configs.py from hitting ipify.org
os.environ["DEVELOPMENT_LOCATION"] = "aws"


MockOutputs = dict[str, object]
ResourceOutputAugmenter = Callable[[pulumi.runtime.MockResourceArgs, MockOutputs], None]


def _augment_vpc_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("defaultRouteTableId", f"{args.name}-default-rt-mock-id")


def _augment_ec2_instance_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("privateDns", f"{args.name}.internal.test")
    outputs.setdefault("privateIp", "10.0.1.42")
    outputs.setdefault("publicIp", "1.2.3.4")
    outputs.setdefault("publicDns", f"{args.name}.compute.test")


def _augment_eip_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("publicIp", "54.1.2.3")


def _augment_ecr_repository_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault(
        "repositoryUrl",
        f"123456789012.dkr.ecr.ap-southeast-2.amazonaws.com/{args.name}",
    )


def _augment_docker_image_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    image_name = outputs.get("imageName") or outputs.get("image_name")
    outputs.setdefault("repoDigest", f"{image_name}@sha256:testdigest")


def _augment_s3_bucket_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("bucket", args.name)
    outputs.setdefault("bucketDomainName", f"{args.name}.s3.amazonaws.com")


def _augment_ecs_cluster_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault(
        "clusterArn",
        f"arn:aws:ecs:ap-southeast-2:123456789012:cluster/{args.name}",
    )


def _augment_ecs_service_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault(
        "clusterArn",
        "arn:aws:ecs:ap-southeast-2:123456789012:cluster/test-cluster",
    )


def _augment_cloudwatch_log_group_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("retentionInDays", 1)


def _augment_random_password_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("result", "MockPassword123!")


def _augment_tls_private_key_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("privateKeyOpenssh", "mock-private-key")
    outputs.setdefault("publicKeyOpenssh", "mock-public-key")


def _augment_service_discovery_namespace_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault(
        "arn",
        "arn:aws:servicediscovery:ap-southeast-2:123456789012:namespace/ns-mock",
    )
    outputs.setdefault("hostedZone", "ZTEST123")


def _augment_dynamodb_table_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    outputs.setdefault("tableName", args.inputs.get("name", "delta_log"))


RESOURCE_OUTPUT_AUGMENTERS: tuple[tuple[str, ResourceOutputAugmenter], ...] = (
    ("ec2/vpc:Vpc", _augment_vpc_outputs),
    ("ec2/instance:Instance", _augment_ec2_instance_outputs),
    ("ec2/eip:Eip", _augment_eip_outputs),
    ("ecr/repository:Repository", _augment_ecr_repository_outputs),
    ("docker:index/image:Image", _augment_docker_image_outputs),
    ("s3/bucket:Bucket", _augment_s3_bucket_outputs),
    ("ecs/cluster:Cluster", _augment_ecs_cluster_outputs),
    ("ecs/service:Service", _augment_ecs_service_outputs),
    ("cloudwatch/logGroup:LogGroup", _augment_cloudwatch_log_group_outputs),
    ("random/randomPassword:RandomPassword", _augment_random_password_outputs),
    ("tls/privateKey:PrivateKey", _augment_tls_private_key_outputs),
    (
        "servicediscovery/privateDnsNamespace:PrivateDnsNamespace",
        _augment_service_discovery_namespace_outputs,
    ),
    ("dynamodb/table:Table", _augment_dynamodb_table_outputs),
)


def _augment_resource_outputs(
    args: pulumi.runtime.MockResourceArgs,
    outputs: MockOutputs,
) -> None:
    resource_type = args.typ or ""
    for resource_type_fragment, augment_outputs in RESOURCE_OUTPUT_AUGMENTERS:
        if resource_type_fragment in resource_type:
            augment_outputs(args, outputs)


# ---------------------------------------------------------------------------
# 2. Pulumi mock implementation
# ---------------------------------------------------------------------------
class InfrastructureMocks(pulumi.runtime.Mocks):
    """Intercepts all provider calls and resource registrations.

    call()         — handles data-source / provider-function invocations
    new_resource() — handles every resource construction; returns a synthetic
                     physical ID and passes inputs straight through as outputs
                     so that Output[T] chains resolve during tests.
    """

    def call(self, args: pulumi.runtime.MockCallArgs) -> dict:  # type: ignore[override]
        token = args.token

        if token == "aws:index/getRegion:getRegion":
            return {
                "id": "ap-southeast-2",
                "region": "ap-southeast-2",
                "description": "Asia Pacific (Sydney)",
                "endpoint": "ec2.ap-southeast-2.amazonaws.com",
                "name": "ap-southeast-2",
            }

        if token == "aws:index/getAvailabilityZones:getAvailabilityZones":
            return {
                "id": "ap-southeast-2",
                "names": ["ap-southeast-2a", "ap-southeast-2b", "ap-southeast-2c"],
                "zoneIds": ["apse2-az1", "apse2-az2", "apse2-az3"],
                "state": "available",
            }

        if token == "aws:index/getCallerIdentity:getCallerIdentity":
            return {
                "accountId": "123456789012",
                "arn": "arn:aws:iam::123456789012:user/test",
                "id": "123456789012",
                "userId": "AKIAIOSFODNN7EXAMPLE",
            }

        if token == "aws:ec2/getAmi:getAmi":
            return {
                "id": "ami-0test12345678abcd",
                "imageId": "ami-0test12345678abcd",
                "architecture": "x86_64",
                "name": "al2023-ami-2023.0.0.0-kernel-6.1-x86_64",
                "ownerId": "137112412989",
                "state": "available",
                "virtualizationType": "hvm",
                "rootDeviceType": "ebs",
                "rootDeviceName": "/dev/xvda",
            }

        if token == "aws:ecr/getAuthorizationToken:getAuthorizationToken":
            return {
                "id": "ap-southeast-2",
                "authorizationToken": "dGVzdA==",
                "proxyEndpoint": "https://123456789012.dkr.ecr.ap-southeast-2.amazonaws.com",
                "password": "test-ecr-password",
                "userName": "AWS",
                "expiresAt": "2099-01-01T00:00:00Z",
            }

        if token == "aws:ecr/getImage:getImage":
            repository_name = args.args.get("repositoryName", "test-repo")
            return {
                "id": f"{repository_name}@sha256:testdigest",
                "imageDigest": "sha256:testdigest",
                "imagePushedAt": 1_765_000_000,
                "imageSizeInBytes": 123,
                "imageTag": args.args.get("imageTag", "latest"),
                "imageTags": [args.args.get("imageTag", "latest")],
                "imageUri": f"123456789012.dkr.ecr.ap-southeast-2.amazonaws.com/{repository_name}@sha256:testdigest",
                "registryId": "123456789012",
                "repositoryName": repository_name,
            }

        if token == "aws:ec2/getAvailabilityZone:getAvailabilityZone":
            return {
                "id": "ap-southeast-2a",
                "name": "ap-southeast-2a",
                "zoneName": "ap-southeast-2a",
                "zoneId": "apse2-az1",
                "state": "available",
                "region": "ap-southeast-2",
            }

        if token == "aws:route53/getZone:getZone":
            return {
                "id": "ZTEST123456789",
                "zoneId": "ZTEST123456789",
                "name": "ausenergymarketdata.com",
                "privateZone": False,
                "callerReference": "test-ref",
            }

        # Default: return empty dict for unknown calls
        return {}

    def new_resource(self, args: pulumi.runtime.MockResourceArgs) -> tuple[str, dict]:  # type: ignore[override]
        """Return a synthetic physical ID and pass inputs through as outputs."""
        resource_id = f"{args.name}-mock-id"
        outputs = dict(args.inputs)

        # Augment outputs with commonly expected fields that aren't in inputs
        if "arn" not in outputs:
            outputs["arn"] = f"arn:aws:mock::123456789012:{args.name}"
        if "id" not in outputs:
            outputs["id"] = resource_id
        # Ensure name is always present (many resources expose .name as an Output)
        if "name" not in outputs:
            outputs["name"] = args.name

        _augment_resource_outputs(args, outputs)

        return resource_id, outputs


# ---------------------------------------------------------------------------
# 3. Ensure an asyncio event loop exists before set_mocks creates the root
#    Stack resource. Python 3.10+ no longer auto-creates a loop in the main
#    thread, and Python 3.14 raises RuntimeError if none exists.
#
#    get_running_loop() raises RuntimeError when no loop is *running* — which
#    is always true at module-import time regardless of whether a loop is set.
#    We therefore check whether the policy already has a loop set before
#    creating a new one, so pytest-asyncio or other test-runner loops are not
#    silently overwritten.
# ---------------------------------------------------------------------------
try:
    asyncio.get_running_loop()
except RuntimeError:
    # No loop is running. Check whether one is already set before creating a
    # new one so we don't silently overwrite a loop configured by the test
    # runner (e.g. pytest-asyncio). On Python 3.14, get_event_loop() raises
    # RuntimeError instead of returning None when no loop is set, so we treat
    # that exception the same as a None result.
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = None
    if loop is None:
        asyncio.set_event_loop(asyncio.new_event_loop())

# ---------------------------------------------------------------------------
# 4. Install mocks at module scope (runs once per test session)
# ---------------------------------------------------------------------------
pulumi.runtime.set_mocks(
    InfrastructureMocks(),
    project="aws-pulumi",
    stack="test",
    preview=False,
)

# ---------------------------------------------------------------------------
# 5. Inject all config values required by components that call pulumi.Config()
#    FastAPIAuthComponentResource and CaddyServerComponentResource both read
#    secrets from Pulumi config at construction time.
# ---------------------------------------------------------------------------
pulumi.runtime.set_all_config(
    {
        "aws-pulumi:cognito_client_id": "test-cognito-client-id",
        "aws-pulumi:cognito_server_metadata_url": "https://cognito.test.example.com/.well-known/openid-configuration",
        "aws-pulumi:cognito_token_signing_key_url": "https://cognito.test.example.com/.well-known/jwks.json",
        "aws-pulumi:cognito_client_secret": "test-cognito-client-secret",
        "aws-pulumi:website_root_url": "https://test.ausenergymarketdata.com",
        "aws-pulumi:developer_email": "test@example.com",
        "aws-pulumi:dagster_failure_alert_topic_arn": "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts",
    },
    secret_keys=[
        "aws-pulumi:cognito_client_id",
        "aws-pulumi:cognito_server_metadata_url",
        "aws-pulumi:cognito_token_signing_key_url",
        "aws-pulumi:cognito_client_secret",
        "aws-pulumi:dagster_failure_alert_topic_arn",
    ],
)
