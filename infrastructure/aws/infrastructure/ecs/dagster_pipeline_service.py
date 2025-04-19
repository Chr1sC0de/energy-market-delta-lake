from typing import Unpack

import aws_cdk as cdk
from aws_cdk import Fn, aws_ecr, aws_ecs
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from configurations.parameters import DEVELOPMENT_ENVIRONMENT
from constructs import Construct

from infrastructure import ecr, ecs, postgres, security_groups, service_discovery, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        EcsDagsterClusterStack: ecs.cluster.Stack,
        PrivateDsnNamespaceStack: service_discovery.Stack,
        PipelineRepositoryStack: ecr.repository.Stack,
        PostgresStack: postgres.Stack,
        SecurityGroupStack: security_groups.Stack,
        service_discovery_name: str,
        stream_prefix: str = "pipeline",
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        # add the dependencies
        self.add_dependency(VpcStack)
        self.add_dependency(EcsDagsterClusterStack)
        self.add_dependency(PrivateDsnNamespaceStack)
        self.add_dependency(PipelineRepositoryStack)
        self.add_dependency(PostgresStack)
        self.add_dependency(SecurityGroupStack)

        # create the fargate task definition

        postgres_host_param = ssm.StringParameter.value_for_string_parameter(
            self, PostgresStack.postgres_ssm_instance_private_dns, None
        )

        dagster_daemon_task_role = iam.Role.from_role_arn(
            self,
            "ECSDagsterDaemonTaskRoleARN",
            Fn.import_value("ECSDagsterDaemonTaskRoleARN"),
        )

        task_definition = aws_ecs.FargateTaskDefinition(
            self,
            "FargateTaskDefinition",
            family="dagster-pipeline",
            cpu=256,
            memory_limit_mib=512,
            task_role=dagster_daemon_task_role,
        )

        _ = task_definition.add_container(
            "DagsterUserCodeContainer",
            container_name="dagster-grpc",
            image=aws_ecs.ContainerImage.from_ecr_repository(
                aws_ecr.Repository.from_repository_name(
                    self, "PipelineCode", PipelineRepositoryStack.repository_name
                )
            ),
            essential=True,
            entry_point=[
                "dagster",
                "api",
                "grpc",
                "-h",
                "0.0.0.0",
                "-p",
                "4000",
                "-m",
                "aemo_gas",
            ],
            environment={
                "DAGSTER_POSTGRES_DB": "dagster",
                "DAGSTER_POSTGRES_HOSTNAME": postgres_host_param,
                "DAGSTER_POSTGRES_USER": "dagster_user",
                "AWS_S3_LOCKING_PROVIDER": "dynamodb",
                "DAGSTER_GRPC_TIMEOUT_SECONDS": "300",
                "DAGSTER_CURRENT_IMAGE": f"{self.account}.dkr.ecr.{self.region}.amazonaws.com/{PipelineRepositoryStack.repository_name}:latest",
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
                stream_prefix=stream_prefix,
                log_group=EcsDagsterClusterStack.log_group,
            ),
            port_mappings=[aws_ecs.PortMapping(container_port=4000, host_port=4000)],
            health_check=aws_ecs.HealthCheck(
                command=[
                    "CMD-SHELL",
                    """echo "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.connect(('localhost', 4000)) if True else None; exit(0)"| uv run - || exit 1""",
                ],
                interval=cdk.Duration.seconds(15),
                timeout=cdk.Duration.seconds(5),
                retries=4,
                start_period=cdk.Duration.seconds(60),
            ),
        )

        # generate the fargate service

        fargate_service = aws_ecs.FargateService(
            self,
            "DagsterUserCodeFargateService",
            task_definition=task_definition,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            cluster=EcsDagsterClusterStack.cluster,
            cloud_map_options=aws_ecs.CloudMapOptions(
                cloud_map_namespace=PrivateDsnNamespaceStack.private_dns_namespace,
                name=service_discovery_name,
            ),
            security_groups=[SecurityGroupStack.dagster_pipeline_security_group],
            min_healthy_percent=50,
        )

        cdk.Tags.of(fargate_service).add("Environment", DEVELOPMENT_ENVIRONMENT)
        cdk.Tags.of(fargate_service).add("Service", "DagsterPipeline")
