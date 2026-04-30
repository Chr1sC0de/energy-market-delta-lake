"""PostgreSQL component for Dagster metadata storage."""

import json
from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_random as random
import pulumi_tls as tls

from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


class PostgresComponentResource(pulumi.ComponentResource):
    """PostgreSQL EC2 instance for Dagster metadata storage.

    Mirrors CDK: infrastructure/postgres.py
    - t4g.nano (ARM) in the private subnet
    - Amazon Linux 2 ARM64
    - PostgreSQL 14 installed via user data
    - Password stored in SSM as a SecureString
    - Private DNS name stored in SSM as a plain String
    """

    instance: aws.ec2.Instance
    ssm_param_password_name: str
    ssm_param_private_dns_name: str
    # Direct Output references – use these in ECS task definitions to avoid
    # SSM data-source lookups that fail during `pulumi preview` before the
    # parameter exists.
    private_dns: pulumi.Output[str]
    password: pulumi.Output[str]

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        security_groups: SecurityGroupsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the PostgreSQL component."""
        super().__init__(f"{name}:components:Postgres", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.ssm_param_password_name = f"/{name}/dagster/postgres/password"
        self.ssm_param_private_dns_name = (
            f"/{name}/dagster/postgres/instance_private_dns"
        )

        self._setup_password()
        self._setup_iam_role()
        self._setup_key_pair()
        self._setup_ami()
        self._setup_instance()
        self._setup_ssm_parameters()

        # Expose direct Outputs so ECS services can reference them without
        # needing an SSM data-source lookup (which fails before the param exists).
        self.private_dns = self.instance.private_dns
        self.password = self._password

        self.register_outputs(
            {
                "instance_id": self.instance.id,
                "ssm_password_name": self.ssm_param_password_name,
                "ssm_private_dns_name": self.ssm_param_private_dns_name,
            }
        )

    def _setup_password(self) -> None:
        # RandomPassword generates once and stores in state; stable across previews.
        self._random_password = random.RandomPassword(
            f"{self.name}-postgres-password",
            length=32,
            special=False,  # keeps the password safe for psql connection strings
            opts=self.child_opts,
        )
        self._password = self._random_password.result

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
            f"{self.name}-postgres-role",
            assume_role_policy=assume_role,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess",
            ],
            opts=self.child_opts,
        )
        self._instance_profile = aws.iam.InstanceProfile(
            f"{self.name}-postgres-instance-profile",
            role=role.name,
            opts=pulumi.ResourceOptions(parent=role),
        )

    def _setup_key_pair(self) -> None:
        self._private_key = tls.PrivateKey(
            f"{self.name}-postgres-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )
        self._key_pair = aws.ec2.KeyPair(
            f"{self.name}-postgres-key-pair",
            key_name=f"{self.name}-postgres-instance-key-pair",
            public_key=self._private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def _setup_ami(self) -> None:
        self._ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                # Amazon Linux 2 ARM64 (Graviton)
                aws.ec2.GetAmiFilterArgs(
                    name="name",
                    values=["amzn2-ami-hvm-*-arm64-gp2"],
                ),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["arm64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

    def _setup_instance(self) -> None:
        user_data = self._password.apply(
            lambda pw: dedent(f"""\
                #!/bin/bash
                set -euo pipefail

                yum update -y
                amazon-linux-extras enable postgresql14
                yum install -y postgresql-server postgresql

                postgresql-setup initdb

                # Configure BEFORE first start so PostgreSQL binds on all interfaces
                # and uses MD5 authentication from the start.
                #
                # shared_buffers default (128MB) exceeds available RAM on t4g.nano (512MB).
                # Set to 64MB to leave headroom for the OS and other processes.
                sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" \\
                    /var/lib/pgsql/data/postgresql.conf
                grep -q '^shared_buffers' /var/lib/pgsql/data/postgresql.conf \\
                    && sed -i "s/^shared_buffers.*/shared_buffers = 64MB/" /var/lib/pgsql/data/postgresql.conf \\
                    || echo "shared_buffers = 64MB" >> /var/lib/pgsql/data/postgresql.conf
                echo 'host all all 0.0.0.0/0 md5' >> /var/lib/pgsql/data/pg_hba.conf

                systemctl enable postgresql
                systemctl start postgresql

                # Wait up to 60 seconds for PostgreSQL to accept connections.
                for i in $(seq 1 30); do
                    if sudo -u postgres psql -c 'SELECT 1;' > /dev/null 2>&1; then
                        break
                    fi
                    sleep 2
                done

                # Idempotent: || true so re-runs on the same instance never fail.
                sudo -u postgres psql -c "CREATE USER dagster_user WITH PASSWORD '{pw}';" || true
                sudo -u postgres psql -c "CREATE DATABASE dagster;" || true
                sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dagster TO dagster_user;" || true
            """)  # ty:ignore[invalid-argument-type]
        )  # ty:ignore[missing-argument]

        self.instance = aws.ec2.Instance(
            f"{self.name}-postgres-instance",
            instance_type="t4g.nano",
            ami=self._ami.id,
            subnet_id=self.vpc.private_subnet.id,
            vpc_security_group_ids=[self.security_groups.register.dagster_postgres.id],
            iam_instance_profile=self._instance_profile.name,
            key_name=self._key_pair.key_name,
            user_data=user_data,
            user_data_replace_on_change=True,
            tags={"dagster/service": "postgres", "Name": f"{self.name}-postgres"},
            opts=self.child_opts,
        )

    def _setup_ssm_parameters(self) -> None:
        aws.ssm.Parameter(
            f"{self.name}-postgres-password-ssm",
            name=self.ssm_param_password_name,
            type="SecureString",
            value=self._password,
            opts=self.child_opts,
            overwrite=True,
        )

        aws.ssm.Parameter(
            f"{self.name}-postgres-private-dns-ssm",
            name=self.ssm_param_private_dns_name,
            type="String",
            value=self.instance.private_dns,
            opts=pulumi.ResourceOptions(parent=self.instance),
            overwrite=True,
        )
