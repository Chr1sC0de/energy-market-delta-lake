from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure.configurations import SHARED_PREFIX
from infrastructure import security_groups, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        SecurityGroupStack: security_groups.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        self.add_dependency(VpcStack)
        self.add_dependency(SecurityGroupStack)

        eip = ec2.CfnEIP(
            self,
            "BastionHostEIP",
            domain="vpc",
            tags=[{"key": "Name", "value": "DagsterBastionHostEIP"}],
        )

        key_pair = ec2.KeyPair(
            self,
            "BastionHostKeyPair",
            key_pair_name="dagster-bastion-host-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        instance = ec2.Instance(
            self,
            "DagsterBastionHostEC2",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.NANO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023,
            ),
            vpc=VpcStack.vpc,
            security_group=SecurityGroupStack.register["BastionHostSecurityGroup"],
            role=iam.Role(
                self,
                "DagsterBastionHostRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonSSMManagedInstanceCore"
                    ),
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonSSMReadOnlyAccess"
                    ),
                ],
            ),
            user_data=self.create_user_data(),
            user_data_causes_replacement=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            key_pair=key_pair,
        )

        _ = ssm.StringParameter(
            self,
            "InstancePublicDNSName",
            string_value=instance.instance_id,
            parameter_name=f"/{SHARED_PREFIX}/dagster/bastion-host/instance-id",
        )

        _ = ssm.StringParameter(
            self,
            "KeyPairId",
            string_value=key_pair.key_pair_id,
            parameter_name=f"/{SHARED_PREFIX}/dagster/bastion-host/key-pair-id",
        )

        Tags.of(instance).add("dagster/service", "bastion-host")

        # Associate the EIP with the EC2 instance
        _ = ec2.CfnEIPAssociation(
            self,
            "BastionHostEIPAssociation",
            eip=eip.ref,
            instance_id=instance.instance_id,
        )

    def create_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            # this needs to be set for the uv installation to work
            "export HOME=/home/ec2-user",
            "sudo yum install go git -y",
            "sudo yum -y install yum-plugin-copr",
            "sudo yum -y copr enable @caddy/caddy epel-9-$(arch)",
            "sudo yum -y install caddy",
            "curl -LsSf https://astral.sh/uv/install.sh | sh",
        )
        return user_data
