"""IAM role component for AWS runtime and administration permissions."""

import json

import pulumi
import pulumi_aws as aws

from configs import ENVIRONMENT

FAILURE_ALERT_TOPIC_ARN_CONFIG_KEY = "dagster_failure_alert_topic_arn"


def _postgres_password_parameter_arn(name: str, account: str, region: str) -> str:
    return f"arn:aws:ssm:{region}:{account}:parameter/{name}/dagster/postgres/password"


def _ecs_cluster_arn(name: str, account: str, region: str) -> str:
    return f"arn:aws:ecs:{region}:{account}:cluster/{name}-dagster-cluster"


def _daemon_task_policy_document(args: dict[str, str]) -> str:
    cluster_arn = _ecs_cluster_arn(args["name"], args["account"], args["region"])
    task_arn = f"arn:aws:ecs:{args['region']}:{args['account']}:task/{args['name']}-dagster-cluster/*"
    task_definition_arns = [
        f"arn:aws:ecs:{args['region']}:{args['account']}:task-definition/dagster-*:*",
        f"arn:aws:ecs:{args['region']}:{args['account']}:task-definition/run_*:*",
    ]
    statements: list[dict[str, object]] = [
        # ECS read/list actions either do not support resource scoping or need
        # account-wide visibility for Dagster run-worker reconciliation.
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeNetworkInterfaces",
                "ecs:DescribeTasks",
                "ecs:DescribeTaskDefinition",
                "ecs:ListAccountSettings",
            ],
            "Resource": "*",
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RegisterTaskDefinition",
                "ecs:TagResource",
            ],
            "Resource": task_definition_arns,
        },
        {
            "Effect": "Allow",
            "Action": ["ecs:TagResource"],
            "Resource": task_arn,
            "Condition": {
                "StringEquals": {
                    "ecs:CreateAction": "RunTask",
                }
            },
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:RunTask",
            ],
            "Resource": task_definition_arns,
            "Condition": {
                "ArnEquals": {
                    "ecs:cluster": cluster_arn,
                }
            },
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:StopTask",
            ],
            "Resource": task_arn,
        },
        # DynamoDB delta-rs locking table
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:DeleteItem",
                "dynamodb:UpdateItem",
                "dynamodb:Query",
            ],
            "Resource": f"arn:aws:dynamodb:{args['region']}:{args['account']}:table/delta_log",
        },
        # S3 data-lake buckets
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetBucketLocation",
            ],
            "Resource": [
                f"arn:aws:s3:::{ENVIRONMENT}-energy-market*",
                f"arn:aws:s3:::{ENVIRONMENT}-energy-market*/*",
            ],
        },
        # Allow passing this role to ECS
        {
            "Effect": "Allow",
            "Action": ["iam:PassRole"],
            "Resource": [
                args["daemon_execution_role_arn"],
                args["daemon_task_role_arn"],
            ],
            "Condition": {
                "StringEquals": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}
            },
        },
    ]

    if args["failure_alert_topic_arn"] != "":
        statements.append(
            {
                "Effect": "Allow",
                "Action": ["sns:Publish"],
                "Resource": args["failure_alert_topic_arn"],
            }
        )

    return json.dumps({"Version": "2012-10-17", "Statement": statements})


def _webserver_task_policy_document(args: dict[str, str]) -> str:
    task_arn = f"arn:aws:ecs:{args['region']}:{args['account']}:task/{args['name']}-dagster-cluster/*"
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["ecs:DescribeTasks", "ecs:StopTask"],
                    "Resource": task_arn,
                },
                {
                    "Effect": "Allow",
                    "Action": ["iam:PassRole"],
                    "Resource": [
                        args["daemon_execution_role_arn"],
                        args["daemon_task_role_arn"],
                    ],
                    "Condition": {
                        "StringEquals": {
                            "iam:PassedToService": "ecs-tasks.amazonaws.com"
                        }
                    },
                },
            ],
        }
    )


def _execution_ssm_policy_document(args: dict[str, str]) -> str:
    return json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": ["ssm:GetParameters"],
                    "Resource": _postgres_password_parameter_arn(
                        args["name"], args["account"], args["region"]
                    ),
                }
            ],
        }
    )


class IamRolesComponentResource(pulumi.ComponentResource):
    """IAM roles and policies shared by bastion and ECS resources."""

    bastion_profile: aws.iam.InstanceProfile
    # ECS task execution roles
    webserver_execution_role: aws.iam.Role
    daemon_execution_role: aws.iam.Role
    # ECS task roles
    webserver_task_role: aws.iam.Role
    daemon_task_role: aws.iam.Role
    webserver_execution_ssm_policy: aws.iam.RolePolicy
    daemon_execution_ssm_policy: aws.iam.RolePolicy
    daemon_task_policy: aws.iam.RolePolicy

    def __init__(self, name: str, opts: pulumi.ResourceOptions | None = None) -> None:
        """Create the IAM roles component."""
        super().__init__(f"{name}:components:IamRoles", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_bastion_host()
        self.setup_ecs_webserver_roles()
        self.setup_ecs_daemon_roles()
        self.setup_ecs_webserver_task_policy()

        self.register_outputs({})

    # ── helpers ──────────────────────────────────────────────────────────────

    def get_ec2_assume_role(self) -> str:
        """Return an EC2 assume-role policy document."""
        return json.dumps(
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

    def get_ecs_task_assume_role(self) -> str:
        """Return an ECS task assume-role policy document."""
        return json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )

    # ── bastion host ─────────────────────────────────────────────────────────

    def setup_bastion_host(self) -> None:
        """Create the bastion host IAM role and instance profile."""
        bastion_role = aws.iam.Role(
            f"{self.name}-bastion-role",
            assume_role_policy=self.get_ec2_assume_role(),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
                "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess",
            ],
            opts=self.child_opts,
        )

        self.bastion_profile = aws.iam.InstanceProfile(
            f"{self.name}-bastion-profile",
            role=bastion_role.name,
            opts=pulumi.ResourceOptions(parent=bastion_role),
        )

    # ── ECS – webserver ───────────────────────────────────────────────────────

    def setup_ecs_webserver_roles(self) -> None:
        """Create ECS execution and task roles for Dagster webservers."""
        # Execution role: allows ECS to pull images and write logs
        self.webserver_execution_role = aws.iam.Role(
            f"{self.name}-ecs-webserver-execution-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            ],
            opts=self.child_opts,
        )

        # Task role: permissions the webserver container uses at runtime.
        # The policy is attached after daemon roles exist so PassRole can be
        # scoped to the exact roles Dagster needs for ECS run workers.
        self.webserver_task_role = aws.iam.Role(
            f"{self.name}-ecs-webserver-task-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            opts=self.child_opts,
        )

        caller = aws.get_caller_identity()
        region = aws.get_region()
        self.webserver_execution_ssm_policy = aws.iam.RolePolicy(
            f"{self.name}-ecs-webserver-execution-ssm-policy",
            role=self.webserver_execution_role.name,
            policy=pulumi.Output.all(
                name=self.name,
                account=caller.account_id,
                region=region.region,
            ).apply(_execution_ssm_policy_document),  # ty:ignore[missing-argument]
            opts=pulumi.ResourceOptions(parent=self.webserver_execution_role),
        )

    # ── ECS – daemon ──────────────────────────────────────────────────────────

    def setup_ecs_daemon_roles(self) -> None:
        """Create ECS execution and task roles for the Dagster daemon."""
        # Execution role: allows ECS to pull images, write logs, fetch SSM secrets
        self.daemon_execution_role = aws.iam.Role(
            f"{self.name}-ecs-daemon-execution-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            ],
            opts=self.child_opts,
        )

        caller = aws.get_caller_identity()
        region = aws.get_region()
        self.daemon_execution_ssm_policy = aws.iam.RolePolicy(
            f"{self.name}-ecs-daemon-execution-ssm-policy",
            role=self.daemon_execution_role.name,
            policy=pulumi.Output.all(
                name=self.name,
                account=caller.account_id,
                region=region.region,
            ).apply(_execution_ssm_policy_document),  # ty:ignore[missing-argument]
            opts=pulumi.ResourceOptions(parent=self.daemon_execution_role),
        )

        # Task role: orchestrates ECS tasks, reads/writes DynamoDB and S3
        self.daemon_task_role = aws.iam.Role(
            f"{self.name}-ecs-daemon-task-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            opts=self.child_opts,
        )

        failure_alert_topic_arn = (
            pulumi.Config().get_secret(FAILURE_ALERT_TOPIC_ARN_CONFIG_KEY) or ""
        )

        self.daemon_task_policy = aws.iam.RolePolicy(
            f"{self.name}-ecs-daemon-task-policy",
            role=self.daemon_task_role.name,
            policy=pulumi.Output.all(
                name=self.name,
                account=caller.account_id,
                region=region.region,
                failure_alert_topic_arn=failure_alert_topic_arn,
                daemon_execution_role_arn=self.daemon_execution_role.arn,
                daemon_task_role_arn=self.daemon_task_role.arn,
            ).apply(_daemon_task_policy_document),  # ty:ignore[missing-argument]
            opts=pulumi.ResourceOptions(parent=self.daemon_task_role),
        )

    def setup_ecs_webserver_task_policy(self) -> None:
        """Attach scoped ECS runtime permissions to Dagster webservers."""
        caller = aws.get_caller_identity()
        region = aws.get_region()
        aws.iam.RolePolicy(
            f"{self.name}-ecs-webserver-task-ecs-policy",
            role=self.webserver_task_role.name,
            policy=pulumi.Output.all(
                name=self.name,
                account=caller.account_id,
                region=region.region,
                daemon_execution_role_arn=self.daemon_execution_role.arn,
                daemon_task_role_arn=self.daemon_task_role.arn,
            ).apply(_webserver_task_policy_document),  # ty:ignore[missing-argument]
            opts=pulumi.ResourceOptions(parent=self.webserver_task_role),
        )
