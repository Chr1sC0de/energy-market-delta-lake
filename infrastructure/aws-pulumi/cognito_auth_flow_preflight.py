"""Validate Cognito app-client auth flows required by the custom login API."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError

REQUIRED_AUTH_FLOW = "ALLOW_USER_PASSWORD_AUTH"


class CognitoAuthFlowPreflightError(RuntimeError):
    """Raised when the configured Cognito app client cannot serve login."""


class SsmClient(Protocol):
    """Subset of the boto3 SSM client used by this preflight."""

    def get_parameter(self, *, Name: str, WithDecryption: bool) -> dict[str, object]:
        """Return one SSM parameter response."""


class CognitoIdentityProviderClient(Protocol):
    """Subset of the boto3 Cognito IDP client used by this preflight."""

    def describe_user_pool_client(
        self,
        *,
        UserPoolId: str,
        ClientId: str,
    ) -> dict[str, object]:
        """Return one Cognito app-client response."""


@dataclass(frozen=True)
class CognitoAppClientReference:
    """Non-secret reference values needed to describe a Cognito app client."""

    user_pool_id: str
    client_id: str
    client_id_parameter_name: str
    metadata_url_parameter_name: str


def user_pool_id_from_metadata_url(metadata_url: str) -> str:
    """Return the user-pool ID from a Cognito OIDC metadata URL."""
    path_parts = [part for part in urlparse(metadata_url).path.split("/") if part]
    if len(path_parts) < 2 or path_parts[1] != ".well-known":
        message = (
            "Cognito metadata URL did not contain the expected "
            "`/<user-pool-id>/.well-known/...` path."
        )
        raise CognitoAuthFlowPreflightError(message)
    return path_parts[0]


def cognito_parameter_names(resource_name: str) -> dict[str, str]:
    """Return SSM parameter names for the FastAPI auth Cognito config."""
    prefix = f"/{resource_name}/dagster/fastapi-auth"
    return {
        "client_id": f"{prefix}/cognito_client_id",
        "server_metadata_url": f"{prefix}/cognito_server_metadata_url",
    }


def load_app_client_reference(
    *,
    ssm_client: SsmClient,
    resource_name: str,
) -> CognitoAppClientReference:
    """Load the configured Cognito app-client reference from SSM."""
    parameter_names = cognito_parameter_names(resource_name)
    client_id = _ssm_parameter_value(
        ssm_client=ssm_client,
        name=parameter_names["client_id"],
    )
    metadata_url = _ssm_parameter_value(
        ssm_client=ssm_client,
        name=parameter_names["server_metadata_url"],
    )
    return CognitoAppClientReference(
        user_pool_id=user_pool_id_from_metadata_url(metadata_url),
        client_id=client_id,
        client_id_parameter_name=parameter_names["client_id"],
        metadata_url_parameter_name=parameter_names["server_metadata_url"],
    )


def explicit_auth_flows(
    *,
    cognito_client: CognitoIdentityProviderClient,
    app_client: CognitoAppClientReference,
) -> list[str]:
    """Return the configured explicit auth flows for the app client."""
    try:
        response = cognito_client.describe_user_pool_client(
            UserPoolId=app_client.user_pool_id,
            ClientId=app_client.client_id,
        )
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "unknown")
        message = (
            "Could not describe the Cognito app client referenced by "
            f"{app_client.client_id_parameter_name!r} "
            f"(AWS error: {error_code})."
        )
        raise CognitoAuthFlowPreflightError(message) from exc
    user_pool_client = response.get("UserPoolClient")
    if not isinstance(user_pool_client, dict):
        raise CognitoAuthFlowPreflightError("Cognito app-client response was empty.")
    flows = user_pool_client.get("ExplicitAuthFlows", [])
    if not isinstance(flows, list):
        raise CognitoAuthFlowPreflightError(
            "Cognito app-client ExplicitAuthFlows response was invalid."
        )
    return [str(flow) for flow in flows]


def validate_required_auth_flow(
    *,
    auth_flows: Sequence[str],
    app_client: CognitoAppClientReference,
) -> None:
    """Fail when the app client cannot run the custom login password flow."""
    if REQUIRED_AUTH_FLOW in auth_flows:
        return
    message = (
        f"Cognito app client from {app_client.client_id_parameter_name!r} "
        f"does not enable {REQUIRED_AUTH_FLOW}. The deployed `/auth/login` "
        "endpoint uses Cognito USER_PASSWORD_AUTH, so the external app client "
        "must allow that flow before Pulumi deployment or deployed tests run."
    )
    raise CognitoAuthFlowPreflightError(message)


def check_cognito_auth_flow(
    *,
    region_name: str,
    resource_name: str,
) -> None:
    """Check the configured Cognito app client in AWS."""
    ssm_client: SsmClient = boto3.client("ssm", region_name=region_name)
    cognito_client: CognitoIdentityProviderClient = boto3.client(
        "cognito-idp",
        region_name=region_name,
    )
    app_client = load_app_client_reference(
        ssm_client=ssm_client,
        resource_name=resource_name,
    )
    auth_flows = explicit_auth_flows(
        cognito_client=cognito_client,
        app_client=app_client,
    )
    validate_required_auth_flow(auth_flows=auth_flows, app_client=app_client)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Cognito auth-flow preflight CLI."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--region", required=True)
    parser.add_argument("--resource-name", required=True)
    args = parser.parse_args(argv)

    try:
        check_cognito_auth_flow(
            region_name=args.region,
            resource_name=args.resource_name,
        )
    except CognitoAuthFlowPreflightError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        "Cognito app client auth-flow preflight passed: "
        f"{REQUIRED_AUTH_FLOW} is enabled."
    )
    return 0


def _ssm_parameter_value(*, ssm_client: SsmClient, name: str) -> str:
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "unknown")
        message = f"Could not read SSM parameter {name!r} (AWS error: {error_code})."
        raise CognitoAuthFlowPreflightError(message) from exc
    parameter = response.get("Parameter")
    if not isinstance(parameter, dict):
        raise CognitoAuthFlowPreflightError(f"SSM parameter {name!r} was missing.")
    value = parameter.get("Value")
    if not isinstance(value, str) or value == "":
        raise CognitoAuthFlowPreflightError(f"SSM parameter {name!r} is empty.")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
