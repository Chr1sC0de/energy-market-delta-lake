from typing import Unpack

import aws_cdk as cdk
from aws_cdk import Fn, Tags, aws_ecr, aws_ecs
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure.configurations import DEVELOPMENT_ENVIRONMENT
from infrastructure import (
    ecr,
    ecs,
    iam_roles,
    postgres,
    security_groups,
    vpc,
)
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        EcsDagsterClusterStack: ecs.cluster.Stack,
        EcrDagsterDaemon: ecr.dagster_webserver.Stack,
        PostgresStack: postgres.Stack,
        SecurityGroupStack: security_groups.Stack,
        IamRolesStack: iam_roles.Stack,
        stream_prefix: str = "dagster-webserver-service",
        user_code_dependencies: list[ecs.dagster_user_code_service.Stack] | None = None,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        # add the dependencies
        self.add_dependency(VpcStack)
        self.add_dependency(EcsDagsterClusterStack)
        self.add_dependency(EcrDagsterDaemon)
        self.add_dependency(PostgresStack)
        self.add_dependency(SecurityGroupStack)
        self.add_dependency(IamRolesStack)
        if user_code_dependencies is not None:
            for service in user_code_dependencies:
                self.add_dependency(service)

        postgres_host_param = ssm.StringParameter.value_for_string_parameter(
            self, PostgresStack.postgres_ssm_instance_private_dns, 1
        )

        dagster_daemon_task_execution_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskExecutionRoleARN",
            Fn.import_value("ECSDagsterDaemonTaskExecutionRoleARN"),
        )

        dagster_daemon_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskRoleARN",
            Fn.import_value("ECSDagsterDaemonTaskRoleARN"),
        )

        task_definition = aws_ecs.FargateTaskDefinition(
            self,
            "DagsterDaemonDefinition",
            family="dagster-daemon",
            cpu=256,
            memory_limit_mib=1024,
            execution_role=dagster_daemon_task_execution_role,
            task_role=dagster_daemon_task_role,
        )

        _ = task_definition.add_container(
            "DagsterDaemonContainer",
            container_name="DagsterDaemonContainer",
            image=aws_ecs.ContainerImage.from_ecr_repository(
                aws_ecr.Repository.from_repository_name(
                    self, "DagsterDaemonEcr", EcrDagsterDaemon.repository_name
                )
            ),
            essential=True,
            entry_point=["dagster-daemon", "run"],
            environment={
                "DAGSTER_POSTGRES_DB": "dagster",
                "DAGSTER_POSTGRES_HOSTNAME": postgres_host_param,
                "DAGSTER_POSTGRES_USER": "dagster_user",
                "AWS_S3_LOCKING_PROVIDER": "dynamodb",
                "DAGSTER_GRPC_TIMEOUT_SECONDS": "300",
                "DEVELOPMENT_ENVIRONMENT": DEVELOPMENT_ENVIRONMENT,
                "DEVELOPMENT_LOCATION": "aws",
            },
            secrets={
                "DAGSTER_POSTGRES_PASSWORD": aws_ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self,
                        "DagsterDaemonUserCodeDBPasswordParam",
                        parameter_name=PostgresStack.postgres_ssm_parameter_password,
                        version=1,
                    )
                )
            },
            logging=aws_ecs.LogDriver.aws_logs(
                stream_prefix="dagster-daemon",
                log_group=EcsDagsterClusterStack.log_group,
            ),
            health_check=aws_ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    "true",
                ],
                interval=cdk.Duration.seconds(15),
                timeout=cdk.Duration.seconds(5),
                retries=4,
                start_period=cdk.Duration.seconds(60),
            ),
        )

        service = aws_ecs.FargateService(
            self,
            "DagsterDaemonFargateService",
            task_definition=task_definition,
            cluster=EcsDagsterClusterStack.cluster,
            security_groups=[SecurityGroupStack.register["DagsterDaemonSecurityGroup"]],
            min_healthy_percent=0,
            max_healthy_percent=100,
            circuit_breaker=aws_ecs.DeploymentCircuitBreaker(rollback=True),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            deployment_controller=aws_ecs.DeploymentController(
                type=aws_ecs.DeploymentControllerType.ECS
            ),
            capacity_provider_strategies=[
                aws_ecs.CapacityProviderStrategy(
                    capacity_provider="FARGATE_SPOT",
                    weight=1,
                )
            ],
            propagate_tags=aws_ecs.PropagatedTagSource.SERVICE,
        )

        Tags.of(service).add("dagster/job_name", "Daemon")
        Tags.of(service).add("dagster/service", "Daemon")
