from dataclasses import dataclass

import pulumi
import pulumi_aws as aws

from components.vpc import VpcComponentResource
from configs import ADMINISTRATOR_IPS


@dataclass
class SecurityGroupRegister:
    bastion_host: aws.ec2.SecurityGroup


class SecurityGroupsComponentResource(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:SecurityGroups", name, {}, opts)

        self.name = name
        self.vpc = vpc
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.register = SecurityGroupRegister(
            bastion_host=self.initialize_security_group("bastion-host"),
        )

        self.setup_bastion_host_ingress_rules()
        self.allow_all_egress(self.register.bastion_host)

        self.register_outputs({})

    def initialize_security_group(
        self,
        security_group_name: str,
    ) -> aws.ec2.SecurityGroup:
        security_group = aws.ec2.SecurityGroup(
            f"{self.name}-{security_group_name}-security-group",
            vpc_id=self.vpc.vpc.id,
            description=security_group_name,
            opts=self.child_opts,
        )
        return security_group

    def allow_all_egress(
        self,
        security_group: aws.ec2.SecurityGroup,
    ) -> None:
        aws.ec2.SecurityGroupRule(
            f"{security_group._name}-egress-all",
            type="egress",
            security_group_id=security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound traffic",
            opts=self.child_opts,
        )

    def ssh_ingress_rule(
        self,
        ip: str,
    ) -> None:
        aws.ec2.SecurityGroupRule(
            f"{self.name}-bastion-host-ingress-{ip.replace('.', '-')}",
            type="ingress",
            security_group_id=self.register.bastion_host.id,
            from_port=22,
            to_port=22,
            protocol="tcp",
            cidr_blocks=[f"{ip}/32"],
            description=f"Allow SSH from admin {ip}",
            opts=self.child_opts,
        )

    def setup_bastion_host_ingress_rules(self) -> None:
        for ip_address in ADMINISTRATOR_IPS:
            self.ssh_ingress_rule(
                ip_address,
            )
