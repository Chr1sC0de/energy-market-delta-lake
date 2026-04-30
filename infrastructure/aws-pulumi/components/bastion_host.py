"""Bastion host component for private AWS administration access."""

from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls

from components.iam_roles import IamRolesComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


class BastionHostComponentResource(pulumi.ComponentResource):
    """EC2 bastion host with SSM parameters for administrative access."""

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        security_groups: SecurityGroupsComponentResource,
        iam_roles: IamRolesComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the bastion host component."""
        super().__init__(f"{name}:components:BastionHost", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.security_groups = security_groups
        self.iam_roles = iam_roles
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_private_key()
        self.setup_key_pair()
        self.setup_eip()
        self.setup_ami()
        self.setup_instance()
        self.setup_ssm_parameters()

        self.register_outputs({})

    def setup_private_key(self) -> None:
        """Create the bastion host private key."""
        self.private_key = tls.PrivateKey(
            f"{self.name}-bastion-host-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )

    def setup_key_pair(self) -> None:
        """Create the EC2 key pair for the bastion host."""
        key_pair_name = f"{self.name}-bastion-host-key-pair"
        self.key_pair = aws.ec2.KeyPair(
            key_pair_name,
            key_name=key_pair_name,
            public_key=self.private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def setup_eip(self) -> None:
        """Create the Elastic IP for the bastion host."""
        eip_name = f"{self.name}-bastion-host-eip"
        self.eip = aws.ec2.Eip(
            eip_name,
            domain="vpc",
            opts=self.child_opts,
        )

    def setup_ami(self) -> None:
        """Select the Amazon Linux 2023 AMI for the bastion host."""
        self.ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

    def setup_instance(self) -> None:
        """Create the bastion EC2 instance and attach its Elastic IP."""
        self.instance = aws.ec2.Instance(
            f"{self.name}-bastion-host-instance",
            instance_type="t3.nano",
            ami=self.ami.id,
            subnet_id=self.vpc.public_subnet.id,
            vpc_security_group_ids=[self.security_groups.register.bastion_host.id],
            iam_instance_profile=self.iam_roles.bastion_profile.name,
            key_name=self.key_pair.key_name,
            user_data=dedent("""#!/bin/bash
                set -euo pipefail
                dnf install -y go git
            """),
            user_data_replace_on_change=True,
            opts=self.child_opts,
        )

        aws.ec2.EipAssociation(
            f"{self.name}-bastion-host-eip-assoc",
            instance_id=self.instance.id,
            allocation_id=self.eip.allocation_id,
            opts=self.child_opts,
        )

    def setup_ssm_parameters(self) -> None:
        """Publish bastion host identifiers to SSM Parameter Store."""
        aws.ssm.Parameter(
            f"{self.name}-instance-id-ssm",
            name=f"/{self.name}/dagster/bastion-host/instance-id",
            type="String",
            value=self.instance.id,
            opts=self.child_opts,
            overwrite=True,
        )

        aws.ssm.Parameter(
            f"{self.name}-key-pair-id-ssm",
            name=f"/{self.name}/dagster/bastion-host/key-pair-id",
            type="String",
            value=self.key_pair.key_pair_id,
            opts=self.child_opts,
            overwrite=True,
        )
