from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import CfnOutput
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from configurations.parameters import ADMINISTRATOR_IPS
from infrastructure.utils import StackKwargs
from infrastructure import vpc


class Stack(_Stack):
    dagster_user_code_security_group: ec2.SecurityGroup
    dagster_daemon_security_group: ec2.SecurityGroup
    dagster_webserver_security_group: ec2.SecurityGroup
    postgres_instance_security_group: ec2.SecurityGroup
    ngnx_instance_security_group: ec2.SecurityGroup

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)
        self.add_dependency(VpcStack)

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                     nginx instance                                     │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.ngnx_instance_security_group = ec2.SecurityGroup(
            self,
            "NginxSecurityGroup",
            vpc=VpcStack.vpc,
            allow_all_outbound=True,
        )

        for ip_address in ADMINISTRATOR_IPS:
            developer_ip = ec2.Peer.ipv4(f"{ip_address}/32")

            self.ngnx_instance_security_group.add_ingress_rule(
                developer_ip,
                ec2.Port.tcp(22),
                "Allow SSH access",
            )

            self.ngnx_instance_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(80),
                description="Allow inbound HTTP traffic on port 80",
            )

            self.ngnx_instance_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(3000),
                description="Allow traffic to Dagster Webserver on port 3000",
            )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                   dagster webserver                                    │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.dagster_webserver_security_group = ec2.SecurityGroup(
            self,
            "DagsterWebServiceSecurityGroup",
            vpc=VpcStack.vpc,
            allow_all_outbound=True,
        )

        self.dagster_webserver_security_group.add_ingress_rule(
            peer=self.ngnx_instance_security_group,
            connection=ec2.Port.tcp(3000),  # Dagster user code
            description="Dagster User Code access across the VPC",
        )

        # ── add the appropriate security groups ─────────────────────────────────────────

        for ip_address in ADMINISTRATOR_IPS:
            developer_ip = ec2.Peer.ipv4(f"{ip_address}/32")

            self.dagster_webserver_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(80),
                description="Allow inbound HTTP traffic on port 80",
            )

            self.dagster_webserver_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(3000),
                description="Allow traffic to Dagster Dagster Webserver on port 3000",
            )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                   dagster user code                                    │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.dagster_user_code_security_group = ec2.SecurityGroup(
            self,
            "DagsterUserCodeSecurityGroup",
            vpc=VpcStack.vpc,
            allow_all_outbound=True,
        )

        self.dagster_user_code_security_group.add_ingress_rule(
            peer=self.dagster_webserver_security_group,
            connection=ec2.Port.tcp(4000),  # Dagster user code
            description="Dagster User Code access across the VPC",
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                     dagster daemon                                     │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.dagster_daemon_security_group = ec2.SecurityGroup(
            self,
            "DagsterDaemonSecurityGroup",
            vpc=VpcStack.vpc,
            allow_all_outbound=True,
        )

        self.dagster_user_code_security_group.add_ingress_rule(
            peer=self.dagster_daemon_security_group,
            connection=ec2.Port.tcp(4000),
            description="Allow daemon to access user code",
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                   postgres instance                                    │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self.postgres_instance_security_group = ec2.SecurityGroup(
            self,
            "DagsterPostgresSecurityGroup",
            vpc=VpcStack.vpc,
            security_group_name="DagsterPostgresSecurityGroup",
            allow_all_outbound=True,
        )

        for security_group in (
            self.dagster_webserver_security_group,
            self.dagster_user_code_security_group,
            self.dagster_daemon_security_group,
        ):
            self.postgres_instance_security_group.add_ingress_rule(
                peer=security_group,
                connection=ec2.Port.tcp(5432),
                description="Allow PostgreSQL access from within VPC",
            )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                 create the cfn outputs to avoid circular dependencies                  │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        for export_name, security_group in [
            (
                "DagsterWebServiceSecurityGroupId",
                self.dagster_webserver_security_group,
            ),
            (
                "DagsterDaemonSecurityGroupId",
                self.dagster_daemon_security_group,
            ),
            (
                "DagsterUserCodeSecurityGroupId",
                self.dagster_user_code_security_group,
            ),
            (
                "DagsterPostgresSecurityGroupId",
                self.postgres_instance_security_group,
            ),
            (
                "NginxSecurityGroupId",
                self.ngnx_instance_security_group,
            ),
        ]:
            _ = CfnOutput(
                self,
                export_name,
                value=security_group.security_group_id,
                export_name=export_name,
            )
