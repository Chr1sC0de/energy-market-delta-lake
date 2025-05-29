from typing import Unpack

from aws_cdk import RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_autoscaling as autoscaling
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_logs as logs
from constructs import Construct

from aws_cdk import custom_resources as cr
from infrastructure import security_groups, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    cluster: ecs.Cluster
    log_group: logs.LogGroup | None
    capacity_provider: ecs.AsgCapacityProvider

    def __init__(
        self,
        scope: Construct,
        id: str,
        log_group_name: str | None = None,
        *,
        VpcStack: vpc.Stack,
        SecurityGroupStack: security_groups.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)
        self.add_dependency(VpcStack)
        self.add_dependency(SecurityGroupStack)

        self.cluster = ecs.Cluster(self, "DagsterEcsCluster", vpc=VpcStack.vpc)

        if log_group_name is not None:
            self.log_group = logs.LogGroup(
                self,
                "LogGroup",
                log_group_name=log_group_name,
                removal_policy=RemovalPolicy.DESTROY,
                retention=logs.RetentionDays.ONE_DAY,
            )

        # Create an autoscaling group and capacity provider for the ec2 service
        auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "DagsterWebserverASG",
            vpc=VpcStack.vpc,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.NANO
            ),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            min_capacity=1,
            max_capacity=1,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=SecurityGroupStack.dagster_webserver_security_group,
        )

        self.capacity_provider = ecs.AsgCapacityProvider(
            self,
            "DagsterWebserverCapacityProvider",
            auto_scaling_group=auto_scaling_group,
        )

        # This is essentially calling some cli magic to kill that pesky ass autoscaling group
        asg_force_delete = cr.AwsCustomResource(
            self,
            "AsgForceDelete",
            on_delete={
                "service": "AutoScaling",
                "action": "DeleteAutoScalingGroup",
                "parameters": {
                    "AutoScalingGroupName": auto_scaling_group.auto_scaling_group_name,
                    "ForceDelete": True,
                },
            },
            policy=cr.AwsCustomResourcePolicy.from_sdk_calls(
                resources=cr.AwsCustomResourcePolicy.ANY_RESOURCE
            ),
        )
        asg_force_delete.node.add_dependency(auto_scaling_group)

        self.cluster.add_asg_capacity_provider(self.capacity_provider)
