from typing import Unpack

from aws_cdk import Stack as _Stack, Fn
from constructs import Construct

from infrastructure.utils import StackKwargs
from infrastructure import iam_roles
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import RemovalPolicy
from aws_cdk import aws_iam as iam


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

        self.add_dependency(IamRolesStack)

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
            removal_policy=RemovalPolicy.DESTROY,
        )

        # grant the required permissiosn to the roles
        dagster_daemon_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskRole",
            Fn.import_value("ECSDagsterDaemonTaskRoleARN"),
        )

        _ = delta_locking_table.grant_read_write_data(dagster_daemon_task_role)
