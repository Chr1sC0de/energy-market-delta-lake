from typing import Unpack

import boto3
from aws_cdk import CfnResource, Fn, RemovalPolicy, RemovalPolicyOptions
from aws_cdk import Stack as _Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from botocore.exceptions import ClientError
from constructs import Construct

from infrastructure import iam_roles
from infrastructure.utils import StackKwargs

table_name = "delta_log"


class Stack(_Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        IamRolesStack: iam_roles.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        client = boto3.client("dynamodb")

        self.add_dependency(IamRolesStack)

        try:
            client.describe_table(TableName=table_name)

            delta_locking_table = dynamodb.TableV2.from_table_name(
                self, "DeltaRsLockTable", table_name
            )
        except ClientError:
            delta_locking_table = dynamodb.TableV2(
                self,
                "DeltaRsLockTable",
                table_name="delta_log",
                partition_key=dynamodb.Attribute(
                    name="tablePath", type=dynamodb.AttributeType.STRING
                ),
                sort_key=dynamodb.Attribute(
                    name="fileName", type=dynamodb.AttributeType.STRING
                ),
                removal_policy=RemovalPolicy.RETAIN,  # Prevent deletion during updates
            )

            # Enable deletion during explicit destroy command
            delta_locking_table.apply_removal_policy(RemovalPolicy.DESTROY)

        # grant the required permissions to the roles
        dagster_daemon_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskRole",
            Fn.import_value("ECSDagsterDaemonTaskRoleARN"),
        )

        _ = delta_locking_table.grant_read_write_data(dagster_daemon_task_role)
