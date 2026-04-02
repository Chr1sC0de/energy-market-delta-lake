import json

import pulumi
import pulumi_aws as aws

from configs import ENVIRONMENT


class IamRolesComponentResource(pulumi.ComponentResource):
    bastion_profile: aws.iam.InstanceProfile
    # ECS task execution roles
    webserver_execution_role: aws.iam.Role
    daemon_execution_role: aws.iam.Role
    # ECS task roles
    webserver_task_role: aws.iam.Role
    daemon_task_role: aws.iam.Role

    def __init__(self, name: str, opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__(f"{name}:components:IamRoles", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_bastion_host()
        self.setup_ecs_webserver_roles()
        self.setup_ecs_daemon_roles()

        self.register_outputs({})

    # ── helpers ──────────────────────────────────────────────────────────────

    def get_ec2_assume_role(self) -> str:
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
        # Execution role: allows ECS to pull images and write logs
        self.webserver_execution_role = aws.iam.Role(
            f"{self.name}-ecs-webserver-execution-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            ],
            opts=self.child_opts,
        )

        # Task role: permissions the webserver container uses at runtime
        self.webserver_task_role = aws.iam.Role(
            f"{self.name}-ecs-webserver-task-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            opts=self.child_opts,
        )

        aws.iam.RolePolicy(
            f"{self.name}-ecs-webserver-task-ecs-policy",
            role=self.webserver_task_role.name,
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["ecs:DescribeTasks", "ecs:StopTask"],
                            "Resource": "*",
                        },
                        {
                            "Effect": "Allow",
                            "Action": ["iam:PassRole"],
                            "Resource": "*",
                            "Condition": {
                                "StringLike": {
                                    "iam:PassedToService": "ecs-tasks.amazonaws.com"
                                }
                            },
                        },
                    ],
                }
            ),
            opts=pulumi.ResourceOptions(parent=self.webserver_task_role),
        )

    # ── ECS – daemon ──────────────────────────────────────────────────────────

    def setup_ecs_daemon_roles(self) -> None:
        # Execution role: allows ECS to pull images, write logs, fetch SSM secrets
        self.daemon_execution_role = aws.iam.Role(
            f"{self.name}-ecs-daemon-execution-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy",
            ],
            opts=self.child_opts,
        )

        aws.iam.RolePolicy(
            f"{self.name}-ecs-daemon-execution-ssm-policy",
            role=self.daemon_execution_role.name,
            policy=json.dumps(
                {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": ["ssm:GetParameters"],
                            "Resource": "*",
                        }
                    ],
                }
            ),
            opts=pulumi.ResourceOptions(parent=self.daemon_execution_role),
        )

        # Task role: orchestrates ECS tasks, reads/writes DynamoDB and S3
        self.daemon_task_role = aws.iam.Role(
            f"{self.name}-ecs-daemon-task-role",
            assume_role_policy=self.get_ecs_task_assume_role(),
            opts=self.child_opts,
        )

        # Retrieve the current AWS caller identity to build ARNs
        caller = aws.get_caller_identity()
        region = aws.get_region()

        aws.iam.RolePolicy(
            f"{self.name}-ecs-daemon-task-policy",
            role=self.daemon_task_role.name,
            policy=pulumi.Output.all(
                account=caller.account_id,
                region=region.name,
            ).apply(
                lambda args: json.dumps(
                    {
                        "Version": "2012-10-17",
                        "Statement": [
                            # ECS orchestration
                            {
                                "Effect": "Allow",
                                "Action": [
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
                                "Resource": "*",
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
                                "Resource": f"arn:aws:s3:::{ENVIRONMENT}-energy-market*",
                            },
                            # Allow passing this role to ECS
                            {
                                "Effect": "Allow",
                                "Action": ["iam:PassRole"],
                                "Resource": "*",
                                "Condition": {
                                    "StringLike": {
                                        "iam:PassedToService": "ecs-tasks.amazonaws.com"
                                    }
                                },
                            },
                        ],
                    }
                )  # ty:ignore[invalid-argument-type]
            ),  # ty:ignore[missing-argument]
            opts=pulumi.ResourceOptions(parent=self.daemon_task_role),
        )
