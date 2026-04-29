"""Tests for VpcEndpointsComponentResource."""

import warnings

import pulumi

from components.vpc import VpcComponentResource
from components.vpc_endpoints import VpcEndpointsComponentResource


def _make(name: str = "test-energy-market") -> VpcEndpointsComponentResource:
    vpc = VpcComponentResource(name)
    return VpcEndpointsComponentResource(name, vpc)


class TestVpcEndpointsResourceCreation:
    def test_security_group_created(self) -> None:
        assert _make().security_group is not None

    def test_ecr_api_endpoint_created(self) -> None:
        assert _make().endpoint_ecr_api is not None

    def test_ecr_dkr_endpoint_created(self) -> None:
        assert _make().endpoint_ecr_dkr is not None

    def test_logs_endpoint_created(self) -> None:
        assert _make().endpoint_logs is not None

    def test_ssm_endpoint_created(self) -> None:
        assert _make().endpoint_ssm is not None

    def test_s3_gateway_endpoint_created(self) -> None:
        assert _make().endpoint_s3 is not None

    def test_dynamodb_gateway_endpoint_created(self) -> None:
        assert _make().endpoint_dynamodb is not None

    @pulumi.runtime.test
    def test_s3_endpoint_is_gateway_type(self) -> None:
        endpoints = _make()

        def check(endpoint_type: str) -> None:
            assert endpoint_type == "Gateway", (
                f"Expected Gateway endpoint type for S3, got {endpoint_type}"
            )

        return endpoints.endpoint_s3.vpc_endpoint_type.apply(check)

    @pulumi.runtime.test
    def test_dynamodb_endpoint_is_gateway_type(self) -> None:
        endpoints = _make()

        def check(endpoint_type: str) -> None:
            assert endpoint_type == "Gateway", (
                f"Expected Gateway endpoint type for DynamoDB, got {endpoint_type}"
            )

        return endpoints.endpoint_dynamodb.vpc_endpoint_type.apply(check)

    @pulumi.runtime.test
    def test_ecr_api_service_name_contains_ecr_api(self) -> None:
        endpoints = _make()

        def check(service_name: str) -> None:
            assert "ecr.api" in service_name, (
                f"Expected 'ecr.api' in service name, got {service_name}"
            )

        return endpoints.endpoint_ecr_api.service_name.apply(check)

    @pulumi.runtime.test
    def test_ecr_dkr_service_name_contains_ecr_dkr(self) -> None:
        endpoints = _make()

        def check(service_name: str) -> None:
            assert "ecr.dkr" in service_name, (
                f"Expected 'ecr.dkr' in service name, got {service_name}"
            )

        return endpoints.endpoint_ecr_dkr.service_name.apply(check)

    @pulumi.runtime.test
    def test_interface_endpoints_in_private_subnet(self) -> None:
        endpoints = _make()

        def check(subnet_ids: list[str]) -> None:
            assert len(subnet_ids) == 1, f"Expected 1 subnet, got {len(subnet_ids)}"

        return endpoints.endpoint_ecr_api.subnet_ids.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _make("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
