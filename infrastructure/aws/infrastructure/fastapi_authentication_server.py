import os
from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from constructs import Construct

from infrastructure import ecr, security_groups, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    ecr_repository: ecr.repository.Stack
    instance: ec2.Instance

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        EcrStack: ecr.repository.Stack,
        SecurityGroupStack: security_groups.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        self.add_dependency(VpcStack)
        self.add_dependency(SecurityGroupStack)

        self.ecr_repository = EcrStack

        key_pair = ec2.KeyPair(
            self,
            "FastAPIAuthenticationServerKeyPair",
            key_pair_name="fastapi-authentication-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        self.instance = ec2.Instance(
            self,
            "FastAPIAuthenticationServerEC2",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.NANO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023,
            ),
            vpc=VpcStack.vpc,
            security_group=SecurityGroupStack.register[
                "FastAPIAuthenticationSecurityGroup"
            ],
            role=iam.Role(
                self,
                "FastAPIAuthenticationServerRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonEC2ContainerRegistryPullOnly"
                    ),
                ],
            ),
            user_data=self.create_user_data(),
            user_data_causes_replacement=True,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            key_pair=key_pair,
        )

        Tags.of(self.instance).add("dagster/service", "fastapi-authentication-server")

    def create_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "export HOME=/home/ec2-user",
            "sudo yum update -y",
            "amazon-linux-extras install docker -y",
            "sudo yum install -y docker",
            "sudo usermod -a -G docker ec2-user",
            "service docker start",
            f"aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin {self.account}.dkr.ecr.{self.region}.amazonaws.com",
            f"docker pull {self.ecr_repository.repository.repository_uri}:latest",
            # command to start the docker image
            "docker run -d \\",
            "--restart unless-stopped \\",
            "    -p 8000:8000 \\",
            f"    -e COGNITO_DAGSTER_AUTH_CLIENT_ID={os.environ['COGNITO_DAGSTER_AUTH_CLIENT_ID']} \\",
            f"    -e COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL={os.environ['COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL']} \\",
            f"    -e COGNITO_TOKEN_SIGNING_KEY_URL={os.environ['COGNITO_TOKEN_SIGNING_KEY_URL']} \\",
            f"    -e COGNITO_DAGSTER_AUTH_CLIENT_SECRET={os.environ['COGNITO_DAGSTER_AUTH_CLIENT_SECRET']} \\",
            f"    -e WEBSITE_ROOT_URL={os.environ['WEBSITE_ROOT_URL']} \\",
            f"    {self.ecr_repository.repository.repository_uri}:latest \\",
            "    uvicorn main:app --host 0.0.0.0 --port 8000",
        )
        return user_data
