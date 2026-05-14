"""Private EC2 deployment for the curated Marimo dashboard."""

import json
from textwrap import dedent

import pulumi
import pulumi_aws as aws

from components.ecr import ECRComponentResource
from components.s3_buckets import S3BucketsComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource
from configs import ENVIRONMENT

MARIMO_PORT = 2718
MARIMO_CLOUD_MAP_NAME = "marimo-dashboard"
MARIMO_ROOT_VOLUME_GIB = 30
MARIMO_BOOTSTRAP_VERSION = "2026-05-13-root-volume-replacement"
DEFAULT_NAME_PREFIX = "energy-market"


class MarimoDashboardComponentResource(pulumi.ComponentResource):
    """Private Marimo dashboard instance with read-only curated S3 access."""

    instance: aws.ec2.Instance
    service: aws.servicediscovery.Service
    cloud_map_instance: aws.servicediscovery.Instance
    endpoint: str = f"{MARIMO_CLOUD_MAP_NAME}.dagster:{MARIMO_PORT}"

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        ecr: ECRComponentResource,
        security_groups: SecurityGroupsComponentResource,
        service_discovery: ServiceDiscoveryComponentResource,
        s3_buckets: S3BucketsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the Marimo dashboard component."""
        super().__init__(f"{name}:components:MarimoDashboard", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.ecr = ecr
        self.security_groups = security_groups
        self.service_discovery = service_discovery
        self.s3_buckets = s3_buckets
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self._name_prefix = _name_prefix_from_stack_name(name)

        self._setup_iam_role()
        self._setup_s3_read_policy()
        self._setup_ami()
        self._setup_instance()
        self._setup_service_discovery()
        self._setup_ssm_parameters()

        self.register_outputs(
            {
                "instance_id": self.instance.id,
                "endpoint": self.endpoint,
            }
        )

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
        self.role = aws.iam.Role(
            f"{self.name}-marimo-dashboard-role",
            assume_role_policy=assume_role,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
            ],
            opts=self.child_opts,
        )
        self.instance_profile = aws.iam.InstanceProfile(
            f"{self.name}-marimo-dashboard-profile",
            role=self.role.name,
            opts=pulumi.ResourceOptions(parent=self.role),
        )

    def _setup_s3_read_policy(self) -> None:
        self.s3_read_policy = aws.iam.RolePolicy(
            f"{self.name}-marimo-dashboard-s3-read-policy",
            role=self.role.name,
            policy=pulumi.Output.all(
                aemo_bucket_arn=self.s3_buckets.aemo.arn,
                io_manager_bucket_arn=self.s3_buckets.io_manager_bucket.arn,
            ).apply(
                lambda arns: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "s3:GetBucketLocation",
                                    "s3:ListBucket",
                                ],
                                "Resource": [
                                    arns["aemo_bucket_arn"],
                                    arns["io_manager_bucket_arn"],
                                ],
                            },
                            {
                                "Effect": "Allow",
                                "Action": ["s3:GetObject"],
                                "Resource": [
                                    f"{arns['aemo_bucket_arn']}/*",
                                    f"{arns['io_manager_bucket_arn']}/*",
                                ],
                            },
                        ],
                    }
                )
            ),
            opts=pulumi.ResourceOptions(parent=self.role),
        )

    def _setup_ami(self) -> None:
        self.ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

    def _setup_instance(self) -> None:
        region = aws.get_region()

        self.user_data = pulumi.Output.all(
            image_uri=self.ecr._published_image_uri(
                self.ecr.marimo_dashboard,
                self.ecr.marimo_dashboard_image,
            ),
            region=region.region,
            aemo_bucket=self.s3_buckets.aemo.bucket,
            io_manager_bucket=self.s3_buckets.io_manager_bucket.bucket,
        ).apply(
            lambda values: dedent(f"""\
                #!/bin/bash
                set -euo pipefail
                export HOME=/home/ec2-user
                MARIMO_BOOTSTRAP_VERSION="{MARIMO_BOOTSTRAP_VERSION}"
                echo "Marimo dashboard bootstrap $MARIMO_BOOTSTRAP_VERSION"

                dnf update -y
                dnf install -y awscli docker
                systemctl enable docker
                systemctl start docker
                usermod -a -G docker ec2-user

                IMAGE_URI="{values["image_uri"]}"
                AWS_REGION="{values["region"]}"
                AEMO_BUCKET="{values["aemo_bucket"]}"
                IO_MANAGER_BUCKET="{values["io_manager_bucket"]}"
                MARIMO_TABLE_BUCKETS="$AEMO_BUCKET,$IO_MANAGER_BUCKET"

                aws ecr get-login-password --region "$AWS_REGION" | \\
                    docker login --username AWS --password-stdin "${{IMAGE_URI%%/*}}"
                for attempt in $(seq 1 30); do
                    if docker pull "$IMAGE_URI"; then
                        break
                    fi
                    if [ "$attempt" -eq 30 ]; then
                        echo "ERROR: failed to pull Marimo dashboard image after $attempt attempts" >&2
                        exit 1
                    fi
                    echo "Waiting for Marimo dashboard image to be available... attempt $attempt"
                    sleep 10
                done

                docker run -d \\
                    --restart unless-stopped \\
                    -p {MARIMO_PORT}:{MARIMO_PORT} \\
                    -e DEVELOPMENT_LOCATION=aws \\
                    -e DEVELOPMENT_ENVIRONMENT={ENVIRONMENT} \\
                    -e NAME_PREFIX={self._name_prefix} \\
                    -e MARIMO_WORKSPACE_KIND=dashboard \\
                    -e MARIMO_NOTEBOOKS_DIR=/opt/marimo/notebooks \\
                    -e MARIMO_TABLE_BUCKETS="$MARIMO_TABLE_BUCKETS" \\
                    -e MARIMO_MAX_PREVIEW_ROWS=100 \\
                    -e MARIMO_FULL_TABLE_SCAN_ENABLED=false \\
                    -e AEMO_BUCKET="$AEMO_BUCKET" \\
                    -e IO_MANAGER_BUCKET="$IO_MANAGER_BUCKET" \\
                    -e AWS_DEFAULT_REGION="$AWS_REGION" \\
                    -e AWS_ALLOW_HTTP=false \\
                    -e DAGSTER_GRAPHQL_URL=http://webserver-guest.dagster:3000/dagster-webserver/guest/graphql \\
                    "$IMAGE_URI"
            """)
        )

        self.instance = aws.ec2.Instance(
            f"{self.name}-marimo-dashboard-instance",
            instance_type="t3.small",
            ami=self.ami.id,
            subnet_id=self.vpc.private_subnet.id,
            associate_public_ip_address=False,
            vpc_security_group_ids=[self.security_groups.register.marimo_dashboard.id],
            iam_instance_profile=self.instance_profile.name,
            metadata_options=aws.ec2.InstanceMetadataOptionsArgs(
                http_endpoint="enabled",
                http_put_response_hop_limit=2,
                http_tokens="required",
            ),
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
                encrypted=True,
                volume_size=MARIMO_ROOT_VOLUME_GIB,
                volume_type="gp3",
            ),
            user_data=self.user_data,
            user_data_replace_on_change=True,
            availability_zone=self.vpc.availability_zone,
            tags={
                "dagster/service": "marimo-dashboard",
                "Name": f"{self.name}-marimo-dashboard",
            },
            opts=pulumi.ResourceOptions(
                parent=self,
                depends_on=[self.s3_read_policy],
                replace_on_changes=["rootBlockDevice"],
            ),
        )

    def _setup_service_discovery(self) -> None:
        self.service = aws.servicediscovery.Service(
            f"{self.name}-marimo-dashboard-sd",
            name=MARIMO_CLOUD_MAP_NAME,
            dns_config=aws.servicediscovery.ServiceDnsConfigArgs(
                namespace_id=self.service_discovery.namespace.id,
                dns_records=[
                    aws.servicediscovery.ServiceDnsConfigDnsRecordArgs(
                        type="A",
                        ttl=10,
                    )
                ],
                routing_policy="MULTIVALUE",
            ),
            health_check_custom_config=aws.servicediscovery.ServiceHealthCheckCustomConfigArgs(),
            force_destroy=True,
            opts=pulumi.ResourceOptions.merge(
                self.child_opts,
                pulumi.ResourceOptions(ignore_changes=["healthCheckCustomConfig"]),
            ),
        )
        self.cloud_map_instance = aws.servicediscovery.Instance(
            f"{self.name}-marimo-dashboard-sd-instance",
            service_id=self.service.id,
            instance_id=f"{self.name}-marimo-dashboard",
            attributes={
                "AWS_INSTANCE_IPV4": self.instance.private_ip,
                "AWS_INSTANCE_PORT": str(MARIMO_PORT),
            },
            opts=pulumi.ResourceOptions(parent=self.service),
        )

    def _setup_ssm_parameters(self) -> None:
        aws.ssm.Parameter(
            f"{self.name}-marimo-dashboard-instance-id-ssm",
            name=f"/{self.name}/dagster/marimo-dashboard/instance-id",
            type="String",
            value=self.instance.id,
            opts=pulumi.ResourceOptions(parent=self.instance),
            overwrite=True,
        )


def _name_prefix_from_stack_name(name: str) -> str:
    prefix = f"{ENVIRONMENT}-"
    if name.startswith(prefix):
        return name.removeprefix(prefix)
    return DEFAULT_NAME_PREFIX
