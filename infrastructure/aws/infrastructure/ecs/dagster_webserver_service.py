from typing import Unpack

import aws_cdk as cdk
from aws_cdk import Fn, Tags, aws_ecr, aws_ecs
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from configurations.parameters import DEVELOPMENT_ENVIRONMENT
from infrastructure import (
    ecr,
    ecs,
    iam_roles,
    postgres,
    security_groups,
    service_discovery,
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
        EcrDagsterWebserver: ecr.dagster_webserver.Stack,
        PostgresStack: postgres.Stack,
        SecurityGroupStack: security_groups.Stack,
        PrivateDnsNamespaceStack: service_discovery.Stack,
        IamRolesStack: iam_roles.Stack,
        service_discovery_name: str = "webserver",
        stream_prefix: str = "dagster-webserver-service",
        path_prefix: str = "/dagster-webserver",
        user_code_dependencies: list[ecs.dagster_user_code_service.Stack] | None = None,
        readonly: bool = False,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        # add the dependencies
        self.add_dependency(VpcStack)
        self.add_dependency(EcsDagsterClusterStack)
        self.add_dependency(EcrDagsterWebserver)
        self.add_dependency(PostgresStack)
        self.add_dependency(SecurityGroupStack)
        self.add_dependency(IamRolesStack)
        if user_code_dependencies is not None:
            for service in user_code_dependencies:
                self.add_dependency(service)

        # create the fargate task definition

        postgres_host_param = ssm.StringParameter.value_for_string_parameter(
            self, PostgresStack.postgres_ssm_instance_private_dns, 1
        )

        dagster_webserver_task_execution_role = iam.Role.from_role_arn(
            self,
            "ECSDagsteWebserverTaskExecutionRoleARN",
            Fn.import_value("ECSDagsteWebserverTaskExecutionRoleARN"),
        )

        dagster_webserver_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsteWebserverTaskRoleARN",
            Fn.import_value("ECSDagsteWebserverTaskRoleARN"),
        )

        task_definition = aws_ecs.FargateTaskDefinition(
            self,
            "DagsterWebserverTaskDefinition",
            family="dagster-webserver",
            cpu=512,
            memory_limit_mib=1024,
            execution_role=dagster_webserver_task_execution_role,
            task_role=dagster_webserver_task_role,
        )

        entrypoint_values = ["dagster-webserver"]

        if readonly:
            entrypoint_values.append("--read-only")

        entrypoint_values.extend(
            [
                "-h",
                "0.0.0.0",
                "-p",
                "3000",
                "-w",
                "workspace.yaml",
                "--path-prefix",
                path_prefix,
            ]
        )

        _ = task_definition.add_container(
            "DagsterWebserverContainer",
            container_name="webserver",
            image=aws_ecs.ContainerImage.from_ecr_repository(
                aws_ecr.Repository.from_repository_name(
                    self,
                    "EcrWebserver",
                    EcrDagsterWebserver.repository_name,
                )
            ),
            essential=True,
            entry_point=entrypoint_values,
            environment={
                "DAGSTER_POSTGRES_DB": "dagster",
                "DAGSTER_POSTGRES_HOSTNAME": postgres_host_param,
                "DAGSTER_POSTGRES_USER": "dagster_user",
                "DEVELOPMENT_ENVIRONMENT": DEVELOPMENT_ENVIRONMENT,
                "DEVELOPMENT_LOCATION": "aws",
            },
            secrets={
                "DAGSTER_POSTGRES_PASSWORD": aws_ecs.Secret.from_ssm_parameter(
                    ssm.StringParameter.from_secure_string_parameter_attributes(
                        self,
                        "UserCodeDBPasswordParam",
                        parameter_name=PostgresStack.postgres_ssm_parameter_password,
                        version=1,
                    )
                )
            },
            logging=aws_ecs.LogDriver.aws_logs(
                stream_prefix="dagster-webserver",
                log_group=EcsDagsterClusterStack.log_group,
            ),
            port_mappings=[aws_ecs.PortMapping(container_port=3000, host_port=3000)],
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
            "DagsterWebserverFargateService",
            task_definition=task_definition,
            cluster=EcsDagsterClusterStack.cluster,
            security_groups=[
                SecurityGroupStack.register["DagsterWebServiceSecurityGroup"]
            ],
            min_healthy_percent=0,
            max_healthy_percent=100,
            circuit_breaker=aws_ecs.DeploymentCircuitBreaker(rollback=True),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            deployment_controller=aws_ecs.DeploymentController(
                type=aws_ecs.DeploymentControllerType.ECS
            ),
            cloud_map_options=aws_ecs.CloudMapOptions(
                cloud_map_namespace=PrivateDnsNamespaceStack.private_dns_namespace,
                name=service_discovery_name,
            ),
            capacity_provider_strategies=[
                aws_ecs.CapacityProviderStrategy(
                    capacity_provider="FARGATE_SPOT",
                    weight=1,
                )
            ],
            propagate_tags=aws_ecs.PropagatedTagSource.SERVICE,
        )

        Tags.of(service).add("dagster/job_name", "Webserver")
        Tags.of(service).add("dagster/service", "Webserver")
