"""Tests for MarimoDashboardComponentResource."""

import json
import warnings

import pulumi
import pytest

import components.s3_buckets as s3_buckets_module
from components.ecr import ECRComponentResource
from components.marimo import (
    MARIMO_BOOTSTRAP_VERSION,
    MARIMO_ROOT_VOLUME_GIB,
    MarimoDashboardComponentResource,
)
from components.s3_buckets import S3BucketsComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource


@pytest.fixture(autouse=True)
def mock_bucket_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep tests hermetic by bypassing live boto3 bucket lookups."""
    monkeypatch.setattr(s3_buckets_module, "bucket_exists", lambda _bucket_name: False)


def _make_deps() -> tuple[
    VpcComponentResource,
    ECRComponentResource,
    SecurityGroupsComponentResource,
    ServiceDiscoveryComponentResource,
    S3BucketsComponentResource,
]:
    vpc = VpcComponentResource("test-energy-market")
    sgs = SecurityGroupsComponentResource("test-energy-market", vpc)
    ecr = ECRComponentResource("test-energy-market")
    service_discovery = ServiceDiscoveryComponentResource("test-energy-market", vpc)
    s3_buckets = S3BucketsComponentResource("test-energy-market")
    return vpc, ecr, sgs, service_discovery, s3_buckets


class TestMarimoDashboardComponent:
    def test_instance_created(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        assert marimo.instance is not None
        assert marimo.service is not None
        assert marimo.cloud_map_instance is not None

    @pulumi.runtime.test
    def test_instance_type_is_t3_small(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(instance_type: str) -> None:
            assert instance_type == "t3.small", (
                f"Expected t3.small, got {instance_type}"
            )

        return marimo.instance.instance_type.apply(check)

    @pulumi.runtime.test
    def test_instance_in_private_subnet_without_public_ip(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(values: list) -> None:
            instance_subnet, private_id, public_id, associate_public_ip = values
            assert instance_subnet == private_id
            assert instance_subnet != public_id
            assert associate_public_ip is False

        return pulumi.Output.all(
            marimo.instance.subnet_id,
            vpc.private_subnet.id,
            vpc.public_subnet.id,
            marimo.instance.associate_public_ip_address,
        ).apply(check)

    @pulumi.runtime.test
    def test_instance_requires_imdsv2_and_encrypted_root_volume(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(values: list) -> None:
            metadata_options, root_block_device = values
            assert metadata_options.get("http_tokens") == "required"
            assert metadata_options.get("http_endpoint") == "enabled"
            assert metadata_options.get("http_put_response_hop_limit") == 2
            assert root_block_device.get("encrypted") is True
            assert root_block_device.get("volume_size") == MARIMO_ROOT_VOLUME_GIB
            assert root_block_device.get("volume_type") == "gp3"

        return pulumi.Output.all(
            marimo.instance.metadata_options,
            marimo.instance.root_block_device,
        ).apply(check)

    @pulumi.runtime.test
    def test_user_data_uses_digest_image_and_instance_credentials(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(user_data: str) -> None:
            assert "@sha256:" in user_data
            assert f'MARIMO_BOOTSTRAP_VERSION="{MARIMO_BOOTSTRAP_VERSION}"' in user_data
            assert "DEVELOPMENT_LOCATION=aws" in user_data
            assert "MARIMO_TABLE_BUCKETS" in user_data
            assert "MARIMO_FULL_TABLE_SCAN_ENABLED=false" in user_data
            assert "MARIMO_MAX_PREVIEW_ROWS=100" in user_data
            assert "MARIMO_OUTPUT_MAX_BYTES=16000000" in user_data
            assert (
                "DAGSTER_GRAPHQL_URL=http://webserver-guest.dagster:3000/dagster-webserver/guest/graphql"
                in user_data
            )
            assert "AWS_ACCESS_KEY_ID" not in user_data
            assert "AWS_SECRET_ACCESS_KEY" not in user_data

        return marimo.user_data.apply(check)

    @pulumi.runtime.test
    def test_role_uses_ecr_and_ssm_managed_policies(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(policy_arns: list[str]) -> None:
            assert "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly" in (
                policy_arns
            )
            assert "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore" in (
                policy_arns
            )

        return marimo.role.managed_policy_arns.apply(check)

    @pulumi.runtime.test
    def test_s3_policy_is_read_only_for_curated_buckets(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(policy: str) -> None:
            document = json.loads(policy)
            serialized = json.dumps(document)
            assert "s3:ListBucket" in serialized
            assert "s3:GetBucketLocation" in serialized
            assert "s3:GetObject" in serialized
            assert "s3:PutObject" not in serialized
            assert "s3:DeleteObject" not in serialized
            assert "aemo" in serialized
            assert "io-manager" in serialized
            assert "landing" not in serialized
            assert "archive" not in serialized

        return marimo.s3_read_policy.policy.apply(check)

    @pulumi.runtime.test
    def test_cloud_map_registers_marimo_dashboard_endpoint(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        marimo = MarimoDashboardComponentResource(
            "test-energy-market",
            vpc,
            ecr,
            sgs,
            service_discovery,
            s3_buckets,
        )

        def check(values: list) -> None:
            service_name, attributes = values
            assert service_name == "marimo-dashboard"
            assert attributes["AWS_INSTANCE_PORT"] == "2718"
            assert attributes["AWS_INSTANCE_IPV4"] == "10.0.1.42"

        return pulumi.Output.all(
            marimo.service.name,
            marimo.cloud_map_instance.attributes,
        ).apply(check)

    def test_no_deprecation_warnings(self) -> None:
        vpc, ecr, sgs, service_discovery, s3_buckets = _make_deps()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            MarimoDashboardComponentResource(
                "test-energy-market-warn",
                vpc,
                ecr,
                sgs,
                service_discovery,
                s3_buckets,
            )
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
