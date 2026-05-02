"""ECS cluster component for the Dagster runtime services."""

import pulumi
import pulumi_aws as aws

from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


class EcsClusterComponentResource(pulumi.ComponentResource):
    """ECS Fargate cluster for Dagster services + shared CloudWatch log group.

    Mirrors CDK: infrastructure/ecs/cluster.py
    """

    cluster: aws.ecs.Cluster
    capacity_providers: aws.ecs.ClusterCapacityProviders
    log_group: aws.cloudwatch.LogGroup

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        security_groups: SecurityGroupsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the ECS cluster component."""
        super().__init__(f"{name}:components:EcsCluster", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self._setup_log_group()
        self._setup_cluster()

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

        self.capacity_providers = aws.ecs.ClusterCapacityProviders(
            f"{self.name}-dagster-cluster-capacity-providers",
            cluster_name=self.cluster.name,
            capacity_providers=["FARGATE", "FARGATE_SPOT"],
            default_capacity_provider_strategies=[
                aws.ecs.ClusterCapacityProvidersDefaultCapacityProviderStrategyArgs(
                    capacity_provider="FARGATE_SPOT",
                    weight=1,
                )
            ],
            opts=pulumi.ResourceOptions(parent=self.cluster),
        )
