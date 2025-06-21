from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

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
            "NginxEIP",
            domain="vpc",
            tags=[{"key": "Name", "value": "DagsterNginxEIP"}],
        )

        key_pair = ec2.KeyPair(
            self,
            "NginxKeyPair",
            key_pair_name="dagster-nginx-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        instance = ec2.Instance(
            self,
            "DagsterNginxEC2",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T2, ec2.InstanceSize.MICRO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            ),
            vpc=VpcStack.vpc,
            security_group=SecurityGroupStack.ngnx_instance_security_group,
            user_data=self.creat_user_data(),
            user_data_causes_replacement=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            key_pair=key_pair,
        )

        Tags.of(instance).add("dagster/service", "nginx")

        # Associate the EIP with the EC2 instance
        _ = ec2.CfnEIPAssociation(
            self,
            "NginxEIPAssociation",
            eip=eip.ref,
            instance_id=instance.instance_id,
        )

    def creat_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "sudo yum update -y",
            "sudo amazon-linux-extras enable nginx1",
            "sudo yum clean metadata",
            "sudo yum install -y nginx",
        )
        return user_data
