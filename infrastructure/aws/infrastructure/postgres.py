from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import Tags
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure.configurations import DEVELOPMENT_ENVIRONMENT, NAME_PREFIX
from infrastructure import security_groups, vpc
from infrastructure.utils import (
    StackKwargs,
    generate_secure_password,
    put_secret_parameter,
)


class Stack(_Stack):
    postgres_password: str
    postgres_ssm_parameter_password: str
    postgres_ssm_instance_private_dns: str

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

        # create the ec2 password

        SSM_PREFIX = f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}"

        self.postgres_ssm_parameter_password = (
            f"/{SSM_PREFIX}/dagster/postgres/password"
        )

        self.postgres_ssm_instance_private_dns = (
            f"/{SSM_PREFIX}/dagster/postgres/instance_private_dns"
        )

        self.postgres_password = generate_secure_password(
            self.postgres_ssm_parameter_password, self.region
        )

        _ = put_secret_parameter(
            self,
            "DagsterPostgresSSMPassword",
            self.postgres_ssm_parameter_password,
            self.postgres_password,
        )

        key_pair = ec2.KeyPair(
            self,
            "PostgresServerKeyPair",
            key_pair_name="dagster-postgres-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        # create the ec2 instance

        instance = ec2.Instance(
            self,
            "DagsterPostgresEC2",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.NANO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
                # Ensure ARM64 compatibility
                cpu_type=ec2.AmazonLinuxCpuType.ARM_64,
            ),
            vpc=VpcStack.vpc,
            security_group=SecurityGroupStack.register["DagsterPostgresSecurityGroup"],
            role=self.create_postgres_role(),
            user_data=self.create_postgres_user_data(),
            user_data_causes_replacement=True,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            key_pair=key_pair,
        )

        instance_private_dns_name = ssm.StringParameter(
            self,
            "PostgresInstancePrivateDNSName",
            parameter_name=self.postgres_ssm_instance_private_dns,
            string_value=instance.instance_private_dns_name,
        )

        instance_private_dns_name.node.add_dependency(instance)

        Tags.of(instance).add("dagster/service", "postgres")

    def create_postgres_role(self) -> iam.Role:
        return iam.Role(
            self,
            "DagsterPostgreseEC2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonEC2ReadOnlyAccess"
                ),
            ],
        )

    def create_postgres_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()

        # Simple user data script that just installs and configures PostgreSQL
        user_data.add_commands(
            # Update and install PostgreSQL
            "yum update -y",
            "amazon-linux-extras enable postgresql14",
            "yum install -y postgresql-server postgresql",
            # Initialize PostgreSQL database
            "postgresql-setup initdb",
            # Start PostgreSQL service
            "systemctl enable postgresql",
            "systemctl start postgresql",
            # Configure PostgreSQL to accept remote connections
            "sed -i \"s/#listen_addresses = 'localhost'/listen_addresses = '*'/\" /var/lib/pgsql/data/postgresql.conf",
            "echo 'host all all 0.0.0.0/0 md5' >> /var/lib/pgsql/data/pg_hba.conf",
            # Restart PostgreSQL to apply changes
            "systemctl restart postgresql",
            # Wait for PostgreSQL to be ready
            "echo 'Waiting for PostgreSQL to start...'",
            "until sudo -u postgres psql -c 'SELECT 1;' > /dev/null 2>&1; do",
            "  echo 'Waiting for PostgreSQL to become available...'",
            "  sleep 2",
            "done",
            # Create database user and database
            f"sudo -u postgres psql -c \"CREATE USER dagster_user WITH PASSWORD '{self.postgres_password}';\"",
            'sudo -u postgres psql -c "CREATE DATABASE dagster;"',
            'sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE dagster TO dagster_user;"',
        )
        return user_data
