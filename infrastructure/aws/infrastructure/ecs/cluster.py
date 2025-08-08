from typing import Unpack

from aws_cdk import RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_logs as logs
from constructs import Construct

from infrastructure import security_groups, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    cluster: ecs.Cluster
    log_group: logs.LogGroup | None

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
