"""FastAPI authentication server running on a private EC2 instance.

Mirrors CDK: infrastructure/fastapi_authentication_server.py
- t3.nano, Amazon Linux 2023
- Private subnet
- Docker: pulls dagster/authentication image and runs on port 8000
- Cognito env vars are fetched from SSM SecureString parameters at boot
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
    """Private FastAPI authentication service instance."""

    instance: aws.ec2.Instance
    cognito_parameter_names: dict[str, str]

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        ecr: ECRComponentResource,
        security_groups: SecurityGroupsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the FastAPI authentication component."""
        super().__init__(f"{name}:components:FastAPIAuth", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.ecr = ecr
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # Read secrets from Pulumi config
        config = pulumi.Config()
        self._cognito_client_id = config.require_secret("cognito_client_id")
        self._cognito_token_signing_key_url = config.require_secret(
            "cognito_token_signing_key_url"
        )
        self._cognito_client_secret = config.require_secret("cognito_client_secret")
        self._website_root_url = config.require("website_root_url")

        self._setup_iam_role()
        self._setup_cognito_parameters()
        self._setup_ssm_read_policy()
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
        self._role = role

    def _setup_cognito_parameters(self) -> None:
        self.cognito_parameter_names = {
            "client_id": f"/{self.name}/dagster/fastapi-auth/cognito_client_id",
            "token_signing_key_url": f"/{self.name}/dagster/fastapi-auth/cognito_token_signing_key_url",
            "client_secret": f"/{self.name}/dagster/fastapi-auth/cognito_client_secret",
        }
        parameter_values = {
            "client_id": self._cognito_client_id,
            "token_signing_key_url": self._cognito_token_signing_key_url,
            "client_secret": self._cognito_client_secret,
        }
        self._cognito_parameters = [
            aws.ssm.Parameter(
                f"{self.name}-fastapi-auth-{label}-ssm",
                name=parameter_name,
                type="SecureString",
                value=parameter_values[label],
                overwrite=True,
                opts=self.child_opts,
            )
            for label, parameter_name in self.cognito_parameter_names.items()
        ]

    def _setup_ssm_read_policy(self) -> None:
        parameter_arns = [parameter.arn for parameter in self._cognito_parameters]
        self._ssm_read_policy = aws.iam.RolePolicy(
            f"{self.name}-fastapi-auth-ssm-policy",
            role=self._role.name,
            policy=pulumi.Output.all(*parameter_arns).apply(
                lambda arns: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": ["ssm:GetParameter", "ssm:GetParameters"],
                                "Resource": arns,
                            }
                        ],
                    }
                )
            ),
            opts=pulumi.ResourceOptions(parent=self._role),
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

        self.user_data = pulumi.Output.all(
            image_uri=self.ecr._published_image_uri(
                self.ecr.authentication,
                self.ecr.authentication_image,
            ),
            region=region.region,
            cognito_client_id_param=self.cognito_parameter_names["client_id"],
            cognito_token_signing_key_url_param=self.cognito_parameter_names[
                "token_signing_key_url"
            ],
            cognito_client_secret_param=self.cognito_parameter_names["client_secret"],
            website_root_url=self._website_root_url,
        ).apply(
            lambda a: dedent(f"""\
                #!/bin/bash
                set -euo pipefail
                export HOME=/home/ec2-user
                dnf update -y
                dnf install -y awscli docker
                systemctl enable docker
                systemctl start docker
                usermod -a -G docker ec2-user

                ssm_value() {{
                    aws ssm get-parameter \\
                        --name "$1" \\
                        --with-decryption \\
                        --query 'Parameter.Value' \\
                        --output text
                }}

                COGNITO_DAGSTER_AUTH_CLIENT_ID="$(ssm_value '{a["cognito_client_id_param"]}')"
                COGNITO_TOKEN_SIGNING_KEY_URL="$(ssm_value '{a["cognito_token_signing_key_url_param"]}')"
                COGNITO_DAGSTER_AUTH_CLIENT_SECRET="$(ssm_value '{a["cognito_client_secret_param"]}')"
                IMAGE_URI="{a["image_uri"]}"

                aws ecr get-login-password --region {a["region"]} | \\
                    docker login --username AWS --password-stdin "${{IMAGE_URI%%/*}}"
                for attempt in $(seq 1 30); do
                    if docker pull "$IMAGE_URI"; then
                        break
                    fi
                    if [ "$attempt" -eq 30 ]; then
                        echo "ERROR: failed to pull auth image after $attempt attempts" >&2
                        exit 1
                    fi
                    echo "Waiting for auth image to be available... attempt $attempt"
                    sleep 10
                done
                docker run -d \\
                    --restart unless-stopped \\
                    -p 8000:8000 \\
                    -e COGNITO_DAGSTER_AUTH_CLIENT_ID="$COGNITO_DAGSTER_AUTH_CLIENT_ID" \\
                    -e COGNITO_TOKEN_SIGNING_KEY_URL="$COGNITO_TOKEN_SIGNING_KEY_URL" \\
                    -e COGNITO_DAGSTER_AUTH_CLIENT_SECRET="$COGNITO_DAGSTER_AUTH_CLIENT_SECRET" \\
                    -e AWS_DEFAULT_REGION={a["region"]} \\
                    -e WEBSITE_ROOT_URL={a["website_root_url"]} \\
                    "$IMAGE_URI" \\
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
            metadata_options=aws.ec2.InstanceMetadataOptionsArgs(
                http_endpoint="enabled",
                http_tokens="required",
            ),
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(encrypted=True),
            user_data=self.user_data,
            user_data_replace_on_change=True,
            tags={
                "dagster/service": "fastapi-authentication-server",
                "Name": f"{self.name}-fastapi-auth",
            },
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self._ssm_read_policy, *self._cognito_parameters],
            ),
        )
