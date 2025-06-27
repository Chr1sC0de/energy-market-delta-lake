from typing import TypedDict, Unpack, cast

from aws_cdk import CfnOutput
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from configurations.parameters import ADMINISTRATOR_IPS
from infrastructure import vpc
from infrastructure.utils import StackKwargs


class SecurityGroupRegister(TypedDict):
    BastionHostSecurityGroup: ec2.SecurityGroup
    DagsterWebServiceSecurityGroup: ec2.SecurityGroup
    DagsterUserCodeSecurityGroup: ec2.SecurityGroup
    DagsterDaemonSecurityGroup: ec2.SecurityGroup
    DagsterPostgresSecurityGroup: ec2.SecurityGroup
    CaddyInstanceSecurityGroup: ec2.SecurityGroup
    FastAPIAuthenticationSecurityGroup: ec2.SecurityGroup


def allow_all_outbound_traffic(security_group: ec2.SecurityGroup):
    security_group.add_egress_rule(
        peer=ec2.Peer.any_ipv4(),
        connection=ec2.Port.all_traffic(),
        description="Allow all outbound traffic",
    )


class Stack(_Stack):
    register: SecurityGroupRegister
    VpcStack: vpc.Stack
    cfn_export_list: list[tuple[str, ec2.SecurityGroup]] = []

    def _initialize_security_group_register(self):
        self.register = cast(
            SecurityGroupRegister,
            cast(
                object,
                {
                    key: ec2.SecurityGroup(
                        self,
                        key,
                        vpc=self.VpcStack.vpc,
                    )
                    for key in SecurityGroupRegister.__annotations__.keys()
                },
            ),
        )
        for key, security_group in self.register.items():
            self.cfn_export_list.append((f"{key}Id", security_group))

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

        self.VpcStack = VpcStack

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                         initialize the security group register                         │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self._initialize_security_group_register()

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                            now updated each security group                             │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        self._bastion_host_security_group()
        self._update_dagster_webserver_security_group()
        self._update_dagster_daemon_security_group()
        self._update_dagster_user_code_security_group()
        self._update_postgres_instance_security_group()
        self._update_caddy_server_security_group()
        self._update_fastapi_authentication_security_group()

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                 create the cfn outputs to avoid circular dependencies                  │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        for export_name, security_group in self.cfn_export_list:
            _ = CfnOutput(
                self,
                export_name,
                value=security_group.security_group_id,
                export_name=export_name,
            )

    def _bastion_host_security_group(self) -> None:
        security_group = self.register["BastionHostSecurityGroup"]
        allow_all_outbound_traffic(security_group)
        for ip_address in ADMINISTRATOR_IPS:
            developer_ip = ec2.Peer.ipv4(f"{ip_address}/32")
            security_group.add_ingress_rule(
                developer_ip,
                ec2.Port.tcp(22),
                "Allow SSH access",
            )

    def _update_dagster_webserver_security_group(self) -> None:
        security_group = self.register["DagsterWebServiceSecurityGroup"]
        allow_all_outbound_traffic(security_group)
        for security_group_name in [
            "BastionHostSecurityGroup",
            "CaddyInstanceSecurityGroup",
        ]:
            security_group.add_ingress_rule(
                peer=self.register[security_group_name],
                connection=ec2.Port.tcp(3000),
                description="Allow ingress access by the jump server",
            )

    def _update_dagster_daemon_security_group(self) -> None:
        security_group = self.register["DagsterDaemonSecurityGroup"]
        allow_all_outbound_traffic(security_group)
        security_group.add_egress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.all_traffic(),
            description="Allow all outbound traffic",
        )

    def _update_dagster_user_code_security_group(self) -> None:
        security_group = self.register["DagsterUserCodeSecurityGroup"]
        allow_all_outbound_traffic(security_group)
        security_group.add_ingress_rule(
            peer=self.register["DagsterDaemonSecurityGroup"],
            connection=ec2.Port.tcp(4000),  # Dagster user code
            description="Dagster User Code access across the VPC",
        )
        security_group.add_ingress_rule(
            peer=self.register["DagsterWebServiceSecurityGroup"],
            connection=ec2.Port.tcp(4000),  # Dagster user code
            description="Dagster User Code access across the VPC",
        )

    def _update_postgres_instance_security_group(self) -> None:
        security_group = self.register["DagsterPostgresSecurityGroup"]
        allow_all_outbound_traffic(security_group)
        for service_security_group in (
            self.register["DagsterUserCodeSecurityGroup"],
            self.register["DagsterWebServiceSecurityGroup"],
            self.register["DagsterDaemonSecurityGroup"],
        ):
            security_group.add_ingress_rule(
                peer=service_security_group,
                connection=ec2.Port.tcp(5432),
                description="Allow PostgreSQL access from within VPC",
            )

    def _update_caddy_server_security_group(self) -> None:
        security_group = self.register["CaddyInstanceSecurityGroup"]
        allow_all_outbound_traffic(security_group)

        for ip_address in ADMINISTRATOR_IPS:
            developer_ip = ec2.Peer.ipv4(f"{ip_address}/32")
            security_group.add_ingress_rule(
                developer_ip,
                ec2.Port.tcp(22),
                "Allow SSH access",
            )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(80),
            description="Allow HTTP",
        )

        security_group.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(443),
            description="Allow HTTPS",
        )

    def _update_fastapi_authentication_security_group(self) -> None:
        security_group = self.register["FastAPIAuthenticationSecurityGroup"]

        security_group.add_ingress_rule(
            peer=self.register["CaddyInstanceSecurityGroup"],
            connection=ec2.Port.tcp(8000),
            description="Allow Reverse Proxy Ingress",
        )

        security_group.add_egress_rule(
            peer=self.register["CaddyInstanceSecurityGroup"],
            connection=ec2.Port.tcp(8000),
            description="Allow Reverse Proxy Egress",
        )

        security_group.add_ingress_rule(
            self.register["BastionHostSecurityGroup"],
            ec2.Port.tcp(22),
            "Allow SSH access",
        )

        # Egress: Allow access to Cognito
        security_group.add_egress_rule(
            ec2.Peer.any_ipv4(), ec2.Port.tcp(443), "Allow HTTPS out"
        )
