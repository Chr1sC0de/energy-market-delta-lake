"""Security group component for AWS network access controls."""

from dataclasses import dataclass

import pulumi
import pulumi_aws as aws

from components.vpc import VpcComponentResource
from configs import ADMINISTRATOR_IPS


@dataclass
class SecurityGroupRegister:
    """Container for security groups created by the component."""

    # Existing
    bastion_host: aws.ec2.SecurityGroup
    # New – Dagster ECS services
    dagster_webserver: aws.ec2.SecurityGroup
    dagster_user_code: aws.ec2.SecurityGroup
    dagster_daemon: aws.ec2.SecurityGroup
    # New – Infrastructure EC2 instances
    dagster_postgres: aws.ec2.SecurityGroup
    caddy_instance: aws.ec2.SecurityGroup
    fastapi_auth: aws.ec2.SecurityGroup


class SecurityGroupsComponentResource(pulumi.ComponentResource):
    """Security groups and ingress rules for AWS runtime resources."""

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the security groups component."""
        super().__init__(f"{name}:components:SecurityGroups", name, {}, opts)

        self.name = name
        self.vpc = vpc
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # ── create all security groups ───────────────────────────────────────
        self.register = SecurityGroupRegister(
            bastion_host=self._make_sg("bastion-host"),
            dagster_webserver=self._make_sg("dagster-webserver"),
            dagster_user_code=self._make_sg("dagster-user-code"),
            dagster_daemon=self._make_sg("dagster-daemon"),
            dagster_postgres=self._make_sg("dagster-postgres"),
            caddy_instance=self._make_sg("caddy-instance"),
            fastapi_auth=self._make_sg("fastapi-auth"),
        )

        # ── configure each group ─────────────────────────────────────────────
        self._setup_bastion_host()
        self._setup_dagster_webserver()
        self._setup_dagster_user_code()
        self._setup_dagster_daemon()
        self._setup_dagster_postgres()
        self._setup_caddy_instance()
        self._setup_fastapi_auth()

        # All groups get allow-all egress
        for sg in vars(self.register).values():
            self._allow_all_egress(sg)

        self.register_outputs({})

    # ── helpers ──────────────────────────────────────────────────────────────

    def _make_sg(self, label: str) -> aws.ec2.SecurityGroup:
        return aws.ec2.SecurityGroup(
            f"{self.name}-{label}-sg",
            vpc_id=self.vpc.vpc.id,
            description=f"{self.name} {label}",
            opts=self.child_opts,
        )

    def _allow_all_egress(self, sg: aws.ec2.SecurityGroup) -> None:
        aws.ec2.SecurityGroupRule(
            f"{sg._name}-egress-all",
            type="egress",
            security_group_id=sg.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound traffic",
            opts=pulumi.ResourceOptions(parent=sg),
        )

    def _tcp_ingress_from_sg(
        self,
        label: str,
        target_sg: aws.ec2.SecurityGroup,
        source_sg: aws.ec2.SecurityGroup,
        port: int,
        description: str,
    ) -> None:
        aws.ec2.SecurityGroupRule(
            f"{label}-ingress-{port}",
            type="ingress",
            security_group_id=target_sg.id,
            from_port=port,
            to_port=port,
            protocol="tcp",
            source_security_group_id=source_sg.id,
            description=description,
            opts=pulumi.ResourceOptions(parent=target_sg),
        )

    def _tcp_ingress_from_cidr(
        self,
        label: str,
        target_sg: aws.ec2.SecurityGroup,
        cidr: str,
        port: int,
        description: str,
    ) -> None:
        aws.ec2.SecurityGroupRule(
            f"{label}-ingress-{port}",
            type="ingress",
            security_group_id=target_sg.id,
            from_port=port,
            to_port=port,
            protocol="tcp",
            cidr_blocks=[cidr],
            description=description,
            opts=pulumi.ResourceOptions(parent=target_sg),
        )

    # ── per-group rules ───────────────────────────────────────────────────────

    def _setup_bastion_host(self) -> None:
        sg = self.register.bastion_host
        for idx, ip in enumerate(ADMINISTRATOR_IPS):
            aws.ec2.SecurityGroupRule(
                f"{self.name}-bastion-ssh-{idx}",
                type="ingress",
                security_group_id=sg.id,
                from_port=22,
                to_port=22,
                protocol="tcp",
                cidr_blocks=[f"{ip}/32"],
                description=f"SSH from admin {ip}",
                opts=pulumi.ResourceOptions(parent=sg),
            )

    def _setup_dagster_webserver(self) -> None:
        sg = self.register.dagster_webserver
        # Port 3000 from bastion (for direct access) and from caddy (reverse proxy)
        for idx, source_sg in enumerate(
            [self.register.bastion_host, self.register.caddy_instance]
        ):
            self._tcp_ingress_from_sg(
                f"{self.name}-dagster-webserver-3000-src{idx}",
                sg,
                source_sg,
                3000,
                "Dagster webserver port 3000",
            )

    def _setup_dagster_user_code(self) -> None:
        sg = self.register.dagster_user_code
        # Port 4000 from daemon and webserver
        for idx, source_sg in enumerate(
            [self.register.dagster_daemon, self.register.dagster_webserver]
        ):
            self._tcp_ingress_from_sg(
                f"{self.name}-dagster-user-code-4000-src{idx}",
                sg,
                source_sg,
                4000,
                "Dagster gRPC user-code port 4000",
            )

    def _setup_dagster_daemon(self) -> None:
        # Daemon does not require inbound rules – it initiates connections
        pass

    def _setup_dagster_postgres(self) -> None:
        sg = self.register.dagster_postgres
        for idx, source_sg in enumerate(
            [
                self.register.dagster_user_code,
                self.register.dagster_webserver,
                self.register.dagster_daemon,
            ]
        ):
            self._tcp_ingress_from_sg(
                f"{self.name}-dagster-postgres-5432-src{idx}",
                sg,
                source_sg,
                5432,
                "PostgreSQL from ECS services",
            )
        # Also allow bastion host access for manual administration
        self._tcp_ingress_from_sg(
            f"{self.name}-dagster-postgres-5432-bastion",
            sg,
            self.register.bastion_host,
            5432,
            "PostgreSQL from bastion host",
        )

    def _setup_caddy_instance(self) -> None:
        sg = self.register.caddy_instance
        # SSH from admin IPs
        for idx, ip in enumerate(ADMINISTRATOR_IPS):
            aws.ec2.SecurityGroupRule(
                f"{self.name}-caddy-ssh-{idx}",
                type="ingress",
                security_group_id=sg.id,
                from_port=22,
                to_port=22,
                protocol="tcp",
                cidr_blocks=[f"{ip}/32"],
                description=f"SSH from admin {ip}",
                opts=pulumi.ResourceOptions(parent=sg),
            )
        # HTTP + HTTPS from anywhere (ACME challenge + user traffic)
        for port, label in [(80, "http"), (443, "https")]:
            self._tcp_ingress_from_cidr(
                f"{self.name}-caddy-{label}",
                sg,
                "0.0.0.0/0",
                port,
                f"Allow {label.upper()} from internet",
            )

    def _setup_fastapi_auth(self) -> None:
        sg = self.register.fastapi_auth
        # Port 8000 from caddy only
        self._tcp_ingress_from_sg(
            f"{self.name}-fastapi-auth-8000",
            sg,
            self.register.caddy_instance,
            8000,
            "FastAPI auth port 8000 from Caddy",
        )
        # SSH from bastion
        self._tcp_ingress_from_sg(
            f"{self.name}-fastapi-auth-ssh",
            sg,
            self.register.bastion_host,
            22,
            "SSH from bastion host",
        )
