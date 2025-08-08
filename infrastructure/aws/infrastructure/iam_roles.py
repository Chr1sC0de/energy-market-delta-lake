from typing import Unpack

from aws_cdk import Stack as _Stack, CfnOutput
from aws_cdk import aws_iam as iam
from constructs import Construct

from configurations.parameters import DEVELOPMENT_ENVIRONMENT, NAME_PREFIX
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        # dagster webserver execution role
        dagster_webserver_execution_role = iam.Role(
            self,
            "ECSDagsteWebserverTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
            ],
        )

        # dagster webserver task role
        dagster_webserver_task_role = iam.Role(
            self,
            "ECSDagsteWebserverTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        _ = dagster_webserver_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ecs:DescribeTasks",
                    "ecs:StopTask",
                ],
                resources=["*"],
            )
        )

        _ = dagster_webserver_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}
                },
            )
        )

        # dagster daemon execution roles
        dagster_daemon_task_execution_role = iam.Role(
            self,
            "ECSDagsterDaemonTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
            ],
        )

        _ = dagster_daemon_task_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameters"],
                resources=["*"],
            )
        )

        # dagster daemon task roles
        dagster_daemon_task_role = iam.Role(
            self,
            "ECSDagsterDaemonTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        _ = dagster_daemon_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ec2:DescribeNetworkInterfaces",
                    "ecs:DescribeTasks",
                    "ecs:DescribeTaskDefinition",
                    "ecs:ListAccountSettings",
                    "ecs:RegisterTaskDefinition",
                    "ecs:RunTask",
                    "ecs:StopTask",
                    "ecs:TagResource",
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:ListSecrets",
                ],
                resources=["*"],
            )
        )

        _ = dagster_daemon_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:DeleteItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                ],
                resources=[
                    f"arn:aws:dynamodb:{self.region}:{self.account}:table/delta_log"
                ],
            )
        )

        _ = dagster_daemon_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:GetBucketLocation",
                ],
                resources=[
                    f"arn:aws:s3:::{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}*",
                ],
            )
        )

        _ = dagster_daemon_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["iam:PassRole"],
                resources=["*"],
                conditions={
                    "StringLike": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}
                },
            )
        )

        # now create cfn outputs to avoid circular dependencies
        for export_name, iam_role in [
            (
                "ECSDagsteWebserverTaskExecutionRoleARN",
                dagster_webserver_execution_role,
            ),
            (
                "ECSDagsteWebserverTaskRoleARN",
                dagster_webserver_task_role,
            ),
            (
                "ECSDagsterDaemonTaskExecutionRoleARN",
                dagster_daemon_task_execution_role,
            ),
            (
                "ECSDagsterDaemonTaskRoleARN",
                dagster_daemon_task_role,
            ),
        ]:
            _ = CfnOutput(
                self,
                export_name,
                value=iam_role.role_arn,
                export_name=export_name,
            )
