from typing import Unpack

from aws_cdk import Fn, RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam

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

        self.add_dependency(IamRolesStack)

        # Create the table - no need for try/catch
        delta_locking_table = dynamodb.TableV2(
            self,
            "DeltaRsLockTable",
            table_name=table_name,
            # This will retain the table during deployments but destroy it on cdk destroy
            removal_policy=RemovalPolicy.RETAIN,
            partition_key=dynamodb.Attribute(
                name="tablePath", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="fileName", type=dynamodb.AttributeType.STRING
            ),
        )

        cfn_table = delta_locking_table.node.default_child
        cfn_table.add_override("DeletionPolicy", "Delete")

        # grant the required permissions to the roles
        dagster_daemon_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskRole",
            Fn.import_value("ECSDagsterDaemonTaskRoleARN"),
        )

        _ = delta_locking_table.grant_read_write_data(dagster_daemon_task_role)
