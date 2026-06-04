"""Tests for Cognito auth-flow preflight."""

from __future__ import annotations

import pytest

from cognito_auth_flow_preflight import (
    REQUIRED_AUTH_FLOW,
    CognitoAppClientReference,
    CognitoAuthFlowPreflightError,
    cognito_parameter_names,
    load_app_client_reference,
    user_pool_id_from_metadata_url,
    validate_required_auth_flow,
)


class FakeSsmClient:
    def __init__(self, values: dict[str, str]) -> None:
        self.values = values
        self.calls: list[dict[str, object]] = []

    def get_parameter(self, *, Name: str, WithDecryption: bool) -> dict[str, object]:
        self.calls.append({"Name": Name, "WithDecryption": WithDecryption})
        return {"Parameter": {"Value": self.values[Name]}}


def test_user_pool_id_from_metadata_url() -> None:
    assert (
        user_pool_id_from_metadata_url(
            "https://cognito-idp.ap-southeast-2.amazonaws.com/"
            "ap-southeast-2_example/.well-known/openid-configuration"
        )
        == "ap-southeast-2_example"
    )


def test_user_pool_id_rejects_unexpected_metadata_url() -> None:
    with pytest.raises(CognitoAuthFlowPreflightError, match="metadata URL"):
        user_pool_id_from_metadata_url("https://example.com/not-cognito")


def test_load_app_client_reference_reads_non_secret_reference_values() -> None:
    parameter_names = cognito_parameter_names("test-energy-market")
    ssm_client = FakeSsmClient(
        {
            parameter_names["client_id"]: "client-id-123",
            parameter_names["server_metadata_url"]: (
                "https://cognito-idp.ap-southeast-2.amazonaws.com/"
                "ap-southeast-2_pool/.well-known/openid-configuration"
            ),
        }
    )

    reference = load_app_client_reference(
        ssm_client=ssm_client,
        resource_name="test-energy-market",
    )

    assert reference == CognitoAppClientReference(
        user_pool_id="ap-southeast-2_pool",
        client_id="client-id-123",
        client_id_parameter_name=parameter_names["client_id"],
        metadata_url_parameter_name=parameter_names["server_metadata_url"],
    )
    assert ssm_client.calls == [
        {"Name": parameter_names["client_id"], "WithDecryption": True},
        {"Name": parameter_names["server_metadata_url"], "WithDecryption": True},
    ]


def test_validate_required_auth_flow_passes_when_enabled() -> None:
    validate_required_auth_flow(
        auth_flows=["ALLOW_REFRESH_TOKEN_AUTH", REQUIRED_AUTH_FLOW],
        app_client=_app_client_reference(),
    )


def test_validate_required_auth_flow_fails_when_missing() -> None:
    with pytest.raises(CognitoAuthFlowPreflightError) as exc_info:
        validate_required_auth_flow(
            auth_flows=["ALLOW_REFRESH_TOKEN_AUTH", "ALLOW_USER_SRP_AUTH"],
            app_client=_app_client_reference(),
        )

    message = str(exc_info.value)
    assert REQUIRED_AUTH_FLOW in message
    assert "/test/dagster/fastapi-auth/cognito_client_id" in message
    assert "client-id-123" not in message


def _app_client_reference() -> CognitoAppClientReference:
    return CognitoAppClientReference(
        user_pool_id="ap-southeast-2_pool",
        client_id="client-id-123",
        client_id_parameter_name="/test/dagster/fastapi-auth/cognito_client_id",
        metadata_url_parameter_name=(
            "/test/dagster/fastapi-auth/cognito_server_metadata_url"
        ),
    )
