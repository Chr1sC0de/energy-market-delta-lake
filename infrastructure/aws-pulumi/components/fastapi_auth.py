"""FastAPI authentication server running on a private EC2 instance.

Mirrors CDK: infrastructure/fastapi_authentication_server.py
- t3.nano, Amazon Linux 2023
- Private subnet
- Docker: pulls dagster/authentication image and runs on port 8000
- Cognito env vars injected via Pulumi config secrets
"""

import json
from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls

from components.ecr import ECRComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


class FastAPIAuthComponentResource(pulumi.ComponentResource):
    instance: aws.ec2.Instance

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        ecr: ECRComponentResource,
        security_groups: SecurityGroupsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:FastAPIAuth", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.ecr = ecr
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # Read secrets from Pulumi config
        config = pulumi.Config()
        self._cognito_client_id = config.require_secret("cognito_client_id")
        self._cognito_server_metadata_url = config.require_secret(
            "cognito_server_metadata_url"
        )
        self._cognito_token_signing_key_url = config.require_secret(
            "cognito_token_signing_key_url"
        )
        self._cognito_client_secret = config.require_secret("cognito_client_secret")
        self._website_root_url = config.require("website_root_url")

        self._setup_iam_role()
        self._setup_key_pair()
        self._setup_ami()
        self._setup_instance()

        self.register_outputs({"instance_id": self.instance.id})

    def _setup_iam_role(self) -> None:
        assume_role = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )
        role = aws.iam.Role(
            f"{self.name}-fastapi-auth-role",
            assume_role_policy=assume_role,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
            ],
            opts=self.child_opts,
        )
        self._instance_profile = aws.iam.InstanceProfile(
            f"{self.name}-fastapi-auth-profile",
            role=role.name,
            opts=pulumi.ResourceOptions(parent=role),
        )

    def _setup_key_pair(self) -> None:
        self._private_key = tls.PrivateKey(
            f"{self.name}-fastapi-auth-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )
        self._key_pair = aws.ec2.KeyPair(
            f"{self.name}-fastapi-auth-key-pair",
            key_name=f"{self.name}-fastapi-authentication-instance-key-pair",
            public_key=self._private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def _setup_ami(self) -> None:
        self._ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

    def _setup_instance(self) -> None:
        region = aws.get_region()

        user_data = pulumi.Output.all(
            repo_uri=self.ecr.authentication.repository_url,
            region=region.region,
            cognito_client_id=self._cognito_client_id,
            cognito_server_metadata_url=self._cognito_server_metadata_url,
            cognito_token_signing_key_url=self._cognito_token_signing_key_url,
            cognito_client_secret=self._cognito_client_secret,
            website_root_url=self._website_root_url,
        ).apply(
            lambda a: dedent(f"""\
                #!/bin/bash
                set -euo pipefail
                export HOME=/home/ec2-user
                dnf update -y
                dnf install -y docker
                systemctl enable docker
                systemctl start docker
                usermod -a -G docker ec2-user
                aws ecr get-login-password --region {a["region"]} | \\
                    docker login --username AWS --password-stdin {a["repo_uri"].split("/")[0]}
                docker pull {a["repo_uri"]}:latest
                docker run -d \\
                    --restart unless-stopped \\
                    -p 8000:8000 \\
                    -e COGNITO_DAGSTER_AUTH_CLIENT_ID={a["cognito_client_id"]} \\
                    -e COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL={a["cognito_server_metadata_url"]} \\
                    -e COGNITO_TOKEN_SIGNING_KEY_URL={a["cognito_token_signing_key_url"]} \\
                    -e COGNITO_DAGSTER_AUTH_CLIENT_SECRET={a["cognito_client_secret"]} \\
                    -e WEBSITE_ROOT_URL={a["website_root_url"]} \\
                    {a["repo_uri"]}:latest \\
                    uvicorn main:app --host 0.0.0.0 --port 8000
            """)  # ty:ignore[invalid-argument-type]
        )  # ty:ignore[missing-argument]

        self.instance = aws.ec2.Instance(
            f"{self.name}-fastapi-auth-instance",
            instance_type="t3.nano",
            ami=self._ami.id,
            subnet_id=self.vpc.private_subnet.id,
            vpc_security_group_ids=[self.security_groups.register.fastapi_auth.id],
            iam_instance_profile=self._instance_profile.name,
            key_name=self._key_pair.key_name,
            user_data=user_data,
            user_data_replace_on_change=True,
            tags={
                "dagster/service": "fastapi-authentication-server",
                "Name": f"{self.name}-fastapi-auth",
            },
            opts=self.child_opts,
        )
