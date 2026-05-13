"""ECS cluster component for the Dagster runtime services."""

import base64
from textwrap import dedent

import pulumi
import pulumi_aws as aws

from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource
from dagster_core_deployment import run_worker_ec2_capacity_provider_name

RUN_WORKER_EC2_INSTANCE_TYPE = "t3.medium"
RUN_WORKER_EC2_ASG_MAX_SIZE = 2
RUN_WORKER_EC2_ROOT_VOLUME_GB = 30
RUN_WORKER_ECS_OPTIMIZED_AMI = (
    "resolve:ssm:/aws/service/ecs/optimized-ami/amazon-linux-2023/recommended/image_id"
)


def _ecs_container_instance_user_data(cluster_name: str) -> str:
    user_data = dedent(
        f"""\
        #!/bin/bash
        cat <<'EOF' >> /etc/ecs/ecs.config
        ECS_CLUSTER={cluster_name}
        ECS_ENABLE_TASK_IAM_ROLE=true
        ECS_ENABLE_TASK_IAM_ROLE_NETWORK_HOST=true
        ECS_AVAILABLE_LOGGING_DRIVERS=["json-file","awslogs"]
        EOF
        """
    )
    return base64.b64encode(user_data.encode("utf-8")).decode("ascii")


class EcsClusterComponentResource(pulumi.ComponentResource):
    """ECS cluster for Dagster services + shared CloudWatch log group.

    Mirrors CDK: infrastructure/ecs/cluster.py
    """

    cluster: aws.ecs.Cluster
    capacity_providers: aws.ecs.ClusterCapacityProviders
    log_group: aws.cloudwatch.LogGroup
    run_worker_launch_template: aws.ec2.LaunchTemplate | None
    run_worker_auto_scaling_group: aws.autoscaling.Group | None
    run_worker_capacity_provider: aws.ecs.CapacityProvider | None

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        security_groups: SecurityGroupsComponentResource,
        enable_ec2_run_worker_capacity_prototype: bool = False,
        run_worker_instance_profile_arn: pulumi.Input[str] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the ECS cluster component."""
        super().__init__(f"{name}:components:EcsCluster", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)
        self.enable_ec2_run_worker_capacity_prototype = (
            enable_ec2_run_worker_capacity_prototype
        )
        self.run_worker_instance_profile_arn = run_worker_instance_profile_arn
        self.run_worker_launch_template = None
        self.run_worker_auto_scaling_group = None
        self.run_worker_capacity_provider = None

        self._setup_log_group()
        self._setup_cluster()
        if self.enable_ec2_run_worker_capacity_prototype:
            self._setup_run_worker_ec2_capacity_provider()
        self._setup_cluster_capacity_providers()

        self.register_outputs(
            {
                "cluster_arn": self.cluster.arn,
                "log_group_name": self.log_group.name,
            }
        )

    def _setup_log_group(self) -> None:
        self.log_group = aws.cloudwatch.LogGroup(
            f"{self.name}-dagster-log-group",
            name=f"/ecs/{self.name}-dagster-cluster",
            retention_in_days=1,
            opts=self.child_opts,
        )

    def _setup_cluster(self) -> None:
        self.cluster = aws.ecs.Cluster(
            f"{self.name}-dagster-cluster",
            name=f"{self.name}-dagster-cluster",
            settings=[
                aws.ecs.ClusterSettingArgs(
                    name="containerInsights",
                    value="disabled",
                )
            ],
            opts=self.child_opts,
        )

    def _setup_run_worker_ec2_capacity_provider(self) -> None:
        if self.run_worker_instance_profile_arn is None:
            raise ValueError(
                "run_worker_instance_profile_arn is required when "
                "enable_ec2_run_worker_capacity_prototype is true"
            )

        self.run_worker_launch_template = aws.ec2.LaunchTemplate(
            f"{self.name}-run-worker-ec2-launch-template",
            name=f"{self.name}-run-worker-ec2",
            image_id=RUN_WORKER_ECS_OPTIMIZED_AMI,
            instance_type=RUN_WORKER_EC2_INSTANCE_TYPE,
            iam_instance_profile=aws.ec2.LaunchTemplateIamInstanceProfileArgs(
                arn=self.run_worker_instance_profile_arn,
            ),
            vpc_security_group_ids=[self.security_groups.register.dagster_daemon.id],
            metadata_options=aws.ec2.LaunchTemplateMetadataOptionsArgs(
                http_endpoint="enabled",
                http_tokens="required",
            ),
            block_device_mappings=[
                aws.ec2.LaunchTemplateBlockDeviceMappingArgs(
                    device_name="/dev/xvda",
                    ebs=aws.ec2.LaunchTemplateBlockDeviceMappingEbsArgs(
                        delete_on_termination="true",
                        encrypted="true",
                        volume_size=RUN_WORKER_EC2_ROOT_VOLUME_GB,
                        volume_type="gp3",
                    ),
                )
            ],
            tag_specifications=[
                aws.ec2.LaunchTemplateTagSpecificationArgs(
                    resource_type="instance",
                    tags={
                        "Name": f"{self.name}-run-worker-ec2",
                        "dagster/service": "run-worker-capacity",
                    },
                ),
                aws.ec2.LaunchTemplateTagSpecificationArgs(
                    resource_type="volume",
                    tags={"dagster/service": "run-worker-capacity"},
                ),
            ],
            user_data=self.cluster.name.apply(_ecs_container_instance_user_data),
            update_default_version=True,
            opts=self.child_opts,
        )

        self.run_worker_auto_scaling_group = aws.autoscaling.Group(
            f"{self.name}-run-worker-ec2-asg",
            name=f"{self.name}-run-worker-ec2",
            min_size=0,
            desired_capacity=0,
            max_size=RUN_WORKER_EC2_ASG_MAX_SIZE,
            health_check_type="EC2",
            launch_template=aws.autoscaling.GroupLaunchTemplateArgs(
                id=self.run_worker_launch_template.id,
                version="$Latest",
            ),
            vpc_zone_identifiers=[self.vpc.private_subnet.id],
            wait_for_capacity_timeout="0",
            tags=[
                aws.autoscaling.GroupTagArgs(
                    key="Name",
                    value=f"{self.name}-run-worker-ec2",
                    propagate_at_launch=True,
                ),
                aws.autoscaling.GroupTagArgs(
                    key="dagster/service",
                    value="run-worker-capacity",
                    propagate_at_launch=True,
                ),
                aws.autoscaling.GroupTagArgs(
                    key="AmazonECSManaged",
                    value="true",
                    propagate_at_launch=True,
                ),
            ],
            opts=self.child_opts,
        )

        self.run_worker_capacity_provider = aws.ecs.CapacityProvider(
            f"{self.name}-run-worker-ec2-capacity-provider",
            name=run_worker_ec2_capacity_provider_name(self.name),
            auto_scaling_group_provider=aws.ecs.CapacityProviderAutoScalingGroupProviderArgs(
                auto_scaling_group_arn=self.run_worker_auto_scaling_group.arn,
                managed_draining="ENABLED",
                managed_termination_protection="DISABLED",
                managed_scaling=aws.ecs.CapacityProviderAutoScalingGroupProviderManagedScalingArgs(
                    status="ENABLED",
                    target_capacity=100,
                    minimum_scaling_step_size=1,
                    maximum_scaling_step_size=RUN_WORKER_EC2_ASG_MAX_SIZE,
                    instance_warmup_period=60,
                ),
            ),
            tags={"dagster/service": "run-worker-capacity"},
            opts=self.child_opts,
        )

    def _setup_cluster_capacity_providers(self) -> None:
        capacity_providers: list[pulumi.Input[str]] = ["FARGATE", "FARGATE_SPOT"]
        depends_on: list[pulumi.Resource] = []
        if self.run_worker_capacity_provider is not None:
            capacity_providers.append(self.run_worker_capacity_provider.name)
            depends_on.append(self.run_worker_capacity_provider)

        self.capacity_providers = aws.ecs.ClusterCapacityProviders(
            f"{self.name}-dagster-cluster-capacity-providers",
            cluster_name=self.cluster.name,
            capacity_providers=capacity_providers,
            default_capacity_provider_strategies=[
                aws.ecs.ClusterCapacityProvidersDefaultCapacityProviderStrategyArgs(
                    capacity_provider="FARGATE_SPOT",
                    weight=1,
                )
            ],
            opts=pulumi.ResourceOptions(parent=self.cluster, depends_on=depends_on),
        )
