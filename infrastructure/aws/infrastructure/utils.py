import collections.abc
import secrets
import string
import typing

import requests
from aws_cdk import (
    Environment,
    IStackSynthesizer,
    PermissionsBoundary,
    Stack,
    custom_resources,
)
from boto3 import client


def get_administrator_ip_address() -> str:
    return requests.get("https://api.ipify.org").text


class StackKwargs(typing.TypedDict, total=False):
    analytics_reporting: bool
    cross_region_references: bool
    description: str
    env: Environment | dict[str, typing.Any]
    notification_arns: collections.abc.Sequence[str]
    permissions_boundary: PermissionsBoundary
    stack_name: str
    suppress_template_indentation: bool
    synthesizer: IStackSynthesizer
    tags: collections.abc.Mapping[str, str]
    termination_protection: bool


def generate_secure_password(
    parameter_name: str, region_name: str, password_length: int = 20
) -> str:
    ssm = client("ssm", region_name=region_name)
    parameters = ssm.get_parameters(Names=[parameter_name], WithDecryption=True)

    # ── if the password does not exist create a new password ────────────────────────
    if parameter_name in parameters.get("InvalidParameters"):
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(password_length))

    return parameters["Parameters"][0]["Value"]


def put_secret_parameter(
    stack: Stack, id: str, name: str, value: str
) -> custom_resources.AwsCustomResource:
    return custom_resources.AwsCustomResource(
        stack,
        id,
        on_update=custom_resources.AwsSdkCall(
            service="SSM",
            action="PutParameter",
            parameters={
                "Name": name,
                "Value": value,
                "Type": "SecureString",
                "Overwrite": True,
            },
            physical_resource_id=custom_resources.PhysicalResourceId.of(name),
        ),
        on_delete=custom_resources.AwsSdkCall(
            service="SSM",
            action="DeleteParameter",
            parameters={
                "Name": name,
            },
        ),
        policy=custom_resources.AwsCustomResourcePolicy.from_sdk_calls(
            resources=custom_resources.AwsCustomResourcePolicy.ANY_RESOURCE
        ),
    )
