from datetime import datetime
from typing import Unpack

import aws_cdk as cdk
from aws_cdk import Fn, aws_ecr, aws_ecs
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from configurations.parameters import ADMINISTRATOR_IPS, DEVELOPMENT_ENVIRONMENT
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
        EcrDagsterWebserver: ecr.dagster_webserver.Stack,
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

        task_definition = aws_ecs.Ec2TaskDefinition(
            self,
            "DagsterWebserverTaskDefinition",
            family="dagster-webserver",
            execution_role=dagster_webserver_task_execution_role,
            task_role=dagster_webserver_task_role,
            # network_mode=aws_ecs.NetworkMode.AWS_VPC,
            network_mode=aws_ecs.NetworkMode.HOST,  # using host mode for development
        )

        _ = task_definition.add_container(
            "DagsterWebserverContainer",
            container_name="webserver",
            memory_limit_mib=400,
            image=aws_ecs.ContainerImage.from_ecr_repository(
                aws_ecr.Repository.from_repository_name(
                    self,
                    "EcrWebserver",
                    EcrDagsterWebserver.repository_name,
                )
            ),
            essential=True,
            entry_point=[
                "dagster-webserver",
                "-h",
                "0.0.0.0",
                "-p",
                "3000",
                "-w",
                "workspace.yaml",
            ],
            environment={
                "DAGSTER_POSTGRES_DB": "dagster",
                "DAGSTER_POSTGRES_HOSTNAME": postgres_host_param,
                "DAGSTER_POSTGRES_USER": "dagster_user",
                "DEVELOPMENT_ENVIRONMENT": DEVELOPMENT_ENVIRONMENT,
                "DEVELOPMENT_LOCATION": "aws",
                "DEPLOYMENT_DATETIME": str(datetime.now()),
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

        # add my developer ip address
        for ip_address in ADMINISTRATOR_IPS:
            developer_ip = ec2.Peer.ipv4(f"{ip_address}/32")

            SecurityGroupStack.dagster_webserver_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(3000),
                description="Allow inbound traffic on port 3000",
            )
            # Allow inbound HTTP traffic
            SecurityGroupStack.dagster_webserver_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(80),
                description="Allow inbound HTTP traffic on port 80",
            )
            # Allow inbound HTTPS traffic
            SecurityGroupStack.dagster_webserver_security_group.add_ingress_rule(
                peer=developer_ip,
                connection=ec2.Port.tcp(443),
                description="Allow inbound HTTPS traffic on port 443",
            )

        # Create the EC2 service
        ec2_service = aws_ecs.Ec2Service(
            self,
            "DagsterWebserverEc2Service",
            task_definition=task_definition,
            cluster=EcsDagsterClusterStack.cluster,
            min_healthy_percent=0,
            max_healthy_percent=100,
            deployment_controller=aws_ecs.DeploymentController(
                type=aws_ecs.DeploymentControllerType.ECS
            ),
            circuit_breaker=aws_ecs.DeploymentCircuitBreaker(rollback=True),
            capacity_provider_strategies=[
                aws_ecs.CapacityProviderStrategy(
                    capacity_provider=EcsDagsterClusterStack.capacity_provider.capacity_provider_name,
                    weight=1,
                )
            ],
        )

        cdk.Tags.of(ec2_service).add("Environment", DEVELOPMENT_ENVIRONMENT)
        cdk.Tags.of(ec2_service).add("Service", "DagsterPublicWebserver")

    # generate the load balanced fargate service this can get expensive

    # alb_fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
    #     self,
    #     "DagsterWebserverApplicationLoadBalancedFargateService",
    #     certificate=acm.Certificate.from_certificate_arn(
    #         self,
    #         "LoadBalancerCertificate",
    #         "<certificate arn here>",
    #     ),
    #     cluster=ecs_cluster,
    #     task_definition=task_definition,
    #     security_groups=[
    #         ec2.SecurityGroup.from_security_group_id(
    #             self,
    #             "DagsterWebServiceSecurityGroupId",
    #             Fn.import_value("DagsterWebServiceSecurityGroupId"),
    #         )
    #     ],
    #     min_healthy_percent=50,
    #     # let's make the load balancer public to save on costs
    #     public_load_balancer=True,
    #     # allow us to access the webserver frontend
    #     assign_public_ip=True,
    # )
    #
    # alb_fargate_service.load_balancer.add_security_group(
    #     ec2.SecurityGroup.from_security_group_id(
    #         self,
    #         "DagsterLoadBalancerSecurityGroupId",
    #         Fn.import_value("DagsterLoadBalancerSecurityGroupId"),
    #     )
    # )
    #
    # alb_fargate_service.target_group.configure_health_check(
    #     path="/dagit_info",
    #     port="3000",
    #     interval=cdk.Duration.seconds(30),
    #     timeout=cdk.Duration.seconds(10),
    #     healthy_threshold_count=2,
    #     unhealthy_threshold_count=5,
    # )
