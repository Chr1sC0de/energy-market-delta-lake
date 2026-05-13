"""Dagster Fargate services.

Mirrors CDK:
  infrastructure/ecs/dagster_user_code_service.py
  infrastructure/ecs/dagster_webserver_service.py
  infrastructure/ecs/dagster_daemon_service.py
"""

import pulumi
import pulumi_aws as aws

from code_locations import (
    DagsterCodeLocation,
    default_code_location,
    load_code_locations,
)
from components.dagster_runtime_task import (
    DagsterRuntimeEnvironmentVariable,
    DagsterRuntimeHealthCheck,
    DagsterRuntimeTaskSharedInputs,
    DagsterRuntimeTaskSpec,
    build_dagster_runtime_task_definition,
)
from components.ecr import ECRComponentResource
from components.ecs_cluster import EcsClusterComponentResource
from components.iam_roles import IamRolesComponentResource
from components.postgres import PostgresComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource
from configs import ENVIRONMENT

DAGSTER_ADMIN_PATH_PREFIX = "/dagster-webserver/admin"
FAILURE_ALERT_TOPIC_ARN_CONFIG_KEY = "dagster_failure_alert_topic_arn"


def _tcp_socket_health_check_command(port: int) -> tuple[str, str]:
    return (
        "CMD-SHELL",
        f"python -c \"import socket; s=socket.socket(); s.connect(('localhost',{port})); s.close()\" || exit 1",
    )


def _run_worker_prototype_environment(
    shared: DagsterRuntimeTaskSharedInputs,
    iam_roles: IamRolesComponentResource,
) -> tuple[DagsterRuntimeEnvironmentVariable, ...]:
    return (
        DagsterRuntimeEnvironmentVariable(
            name="AWS_DEFAULT_REGION",
            value=shared.region,
        ),
        DagsterRuntimeEnvironmentVariable(
            name="DAGSTER_ECS_LOG_GROUP_NAME",
            value=shared.log_group_name,
        ),
        DagsterRuntimeEnvironmentVariable(
            name="DAGSTER_RUN_WORKER_EXECUTION_ROLE_ARN",
            value=iam_roles.daemon_execution_role.arn,
        ),
        DagsterRuntimeEnvironmentVariable(
            name="DAGSTER_RUN_WORKER_TASK_ROLE_ARN",
            value=iam_roles.daemon_task_role.arn,
        ),
        DagsterRuntimeEnvironmentVariable(
            name="DAGSTER_POSTGRES_PASSWORD_PARAMETER_ARN",
            value=shared.postgres_password_parameter_arn,
        ),
    )


def _fargate_service(
    resource_name: str,
    cluster: aws.ecs.Cluster,
    task_definition: aws.ecs.TaskDefinition,
    security_group: aws.ec2.SecurityGroup,
    private_subnet_id: pulumi.Input[str],
    namespace_id: pulumi.Input[str] | None = None,
    cloud_map_name: str | None = None,
    tags: dict[str, str] | None = None,
    child_opts: pulumi.ResourceOptions | None = None,
) -> aws.ecs.Service:

    sd_registration: aws.ecs.ServiceServiceRegistriesArgs | None = None
    if namespace_id is not None and cloud_map_name is not None:
        sd_service = aws.servicediscovery.Service(
            f"{resource_name}-sd",
            name=cloud_map_name,
            dns_config=aws.servicediscovery.ServiceDnsConfigArgs(
                namespace_id=namespace_id,
                dns_records=[
                    aws.servicediscovery.ServiceDnsConfigDnsRecordArgs(
                        type="A",
                        ttl=10,
                    )
                ],
                routing_policy="MULTIVALUE",
            ),
            # health_check_custom_config (empty) signals to AWS Cloud Map that
            # ECS manages health — without it Cloud Map may attempt its own
            # health checks and interfere with service routing.
            # failure_threshold is intentionally omitted: AWS ignores it and
            # always uses 1; passing it emits a DeprecationWarning from the SDK.
            # force_destroy deregisters ECS instances before deletion, preventing
            # the ResourceInUse error when the ECS service still has live tasks.
            health_check_custom_config=aws.servicediscovery.ServiceHealthCheckCustomConfigArgs(),
            force_destroy=True,
            opts=pulumi.ResourceOptions.merge(
                child_opts,
                pulumi.ResourceOptions(ignore_changes=["healthCheckCustomConfig"]),
            ),
        )
        sd_registration = aws.ecs.ServiceServiceRegistriesArgs(
            registry_arn=sd_service.arn
        )

    return aws.ecs.Service(
        resource_name,
        name=resource_name,
        cluster=cluster.arn,
        task_definition=task_definition.arn,
        desired_count=1,
        launch_type=None,  # managed by capacity_provider_strategies
        capacity_provider_strategies=[
            aws.ecs.ServiceCapacityProviderStrategyArgs(
                capacity_provider="FARGATE_SPOT",
                weight=1,
                base=0,
            ),
        ],
        network_configuration=aws.ecs.ServiceNetworkConfigurationArgs(
            subnets=[private_subnet_id],
            security_groups=[security_group.id],
            assign_public_ip=False,
        ),
        deployment_minimum_healthy_percent=0,
        deployment_maximum_percent=100,
        deployment_circuit_breaker=aws.ecs.ServiceDeploymentCircuitBreakerArgs(
            enable=True,
            rollback=True,
        ),
        force_new_deployment=True,
        propagate_tags="SERVICE",
        service_registries=sd_registration,
        tags=tags or {},
        opts=child_opts,
    )


# ---------------------------------------------------------------------------
# dagster-user-code locations
# ---------------------------------------------------------------------------


class DagsterUserCodeServiceComponentResource(pulumi.ComponentResource):
    """Fargate service running the Dagster gRPC user-code server.

    Mirrors CDK: infrastructure/ecs/dagster_user_code_service.py
    """

    service: aws.ecs.Service
    task_definition: aws.ecs.TaskDefinition

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        cluster: EcsClusterComponentResource,
        ecr: ECRComponentResource,
        postgres: PostgresComponentResource,
        security_groups: SecurityGroupsComponentResource,
        service_discovery: ServiceDiscoveryComponentResource,
        iam_roles: IamRolesComponentResource,
        code_location: DagsterCodeLocation | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the Dagster user-code ECS service component."""
        super().__init__(f"{name}:components:DagsterUserCodeService", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)
        self.code_location = code_location or default_code_location(
            load_code_locations()
        )

        # Use direct Output references – avoids SSM data-source calls during preview
        shared_task_inputs = DagsterRuntimeTaskSharedInputs(
            postgres_hostname=postgres.private_dns,
            postgres_password_parameter_arn=postgres.ssm_param_password_arn,
            log_group_name=cluster.log_group.name,
            region=aws.get_region().region,
            development_environment=ENVIRONMENT,
            development_location="aws",
        )
        config = pulumi.Config()
        failure_alert_topic_arn = (
            config.get_secret(FAILURE_ALERT_TOPIC_ARN_CONFIG_KEY) or ""
        )
        website_root_url = config.get("website_root_url")
        failure_alert_base_url = (
            f"{website_root_url.rstrip('/')}{DAGSTER_ADMIN_PATH_PREFIX}"
            if website_root_url is not None
            else ""
        )

        self.task_definition = build_dagster_runtime_task_definition(
            shared_task_inputs,
            DagsterRuntimeTaskSpec(
                resource_name=f"{name}-user-code-task-def",
                family=f"dagster-user-code-{self.code_location.resource_suffix}",
                cpu=self.code_location.cpu,
                memory=self.code_location.memory,
                execution_role_arn=iam_roles.daemon_execution_role.arn,
                task_role_arn=iam_roles.daemon_task_role.arn,
                container_name=self.code_location.container_name,
                image_uri=ecr.dagster_user_code_image_uri(self.code_location),
                entry_point=(
                    "dagster",
                    "api",
                    "grpc",
                    "-h",
                    "0.0.0.0",
                    "-p",
                    str(self.code_location.port),
                    "-m",
                    self.code_location.module,
                ),
                log_stream_prefix=self.code_location.effective_log_stream_prefix,
                health_check=DagsterRuntimeHealthCheck(
                    command=_tcp_socket_health_check_command(self.code_location.port)
                ),
                container_port=self.code_location.port,
                environment_after_postgres=(
                    DagsterRuntimeEnvironmentVariable(
                        name="AWS_S3_LOCKING_PROVIDER",
                        value="dynamodb",
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="AWS_DEFAULT_REGION",
                        value=shared_task_inputs.region,
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_CURRENT_IMAGE",
                        value=ecr.dagster_user_code_image_uri(self.code_location),
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_GRPC_TIMEOUT_SECONDS",
                        value=self.code_location.grpc_timeout_seconds,
                    ),
                ),
                environment_after_development=(
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_FAILURE_ALERT_TOPIC_ARN",
                        value=failure_alert_topic_arn,
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_FAILURE_ALERT_BASE_URL",
                        value=failure_alert_base_url,
                    ),
                ),
                child_opts=self.child_opts,
            ),
        )

        self.service = _fargate_service(
            f"{name}-user-code-service",
            cluster=cluster.cluster,
            task_definition=self.task_definition,
            security_group=security_groups.register.dagster_user_code,
            private_subnet_id=vpc.private_subnet.id,
            namespace_id=service_discovery.namespace.id,
            cloud_map_name=self.code_location.cloud_map_name,
            tags={
                "dagster/service": "user-code",
                "dagster/job_name": f"Code Location: {self.code_location.module}",
            },
            child_opts=self.child_opts,
        )

        self.register_outputs({"service_name": self.service.name})


# ---------------------------------------------------------------------------
# dagster-webserver (admin + guest)
# ---------------------------------------------------------------------------


class DagsterWebserverServiceComponentResource(pulumi.ComponentResource):
    """Fargate service running the Dagster webserver.

    Mirrors CDK: infrastructure/ecs/dagster_webserver_service.py
    Instantiate once for admin (readonly=False) and once for guest (readonly=True).
    """

    service: aws.ecs.Service
    task_definition: aws.ecs.TaskDefinition

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        cluster: EcsClusterComponentResource,
        ecr: ECRComponentResource,
        postgres: PostgresComponentResource,
        security_groups: SecurityGroupsComponentResource,
        service_discovery: ServiceDiscoveryComponentResource,
        iam_roles: IamRolesComponentResource,
        cloud_map_name: str = "webserver-admin",
        path_prefix: str = "/dagster-webserver/admin",
        stream_prefix: str = "dagster-webserver-admin",
        readonly: bool = False,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create a Dagster webserver ECS service component."""
        super().__init__(f"{name}:components:DagsterWebserverService", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # Use direct Output references – avoids SSM data-source calls during preview
        shared_task_inputs = DagsterRuntimeTaskSharedInputs(
            postgres_hostname=postgres.private_dns,
            postgres_password_parameter_arn=postgres.ssm_param_password_arn,
            log_group_name=cluster.log_group.name,
            region=aws.get_region().region,
            development_environment=ENVIRONMENT,
            development_location="aws",
        )

        entry_point = (
            "dagster-webserver",
            "-h",
            "0.0.0.0",
            "-p",
            "3000",
            "-w",
            "workspace.yaml",
            "--path-prefix",
            path_prefix,
        )
        if readonly:
            # Insert --read-only after dagster-webserver
            entry_point = (entry_point[0], "--read-only", *entry_point[1:])

        # Derive a distinct task definition family per service variant so that
        # admin and guest task definitions don't share revision numbers under
        # the same family (which could cause a stale revision to be used).
        # cloud_map_name is "webserver-admin" or "webserver-guest".
        td_family = f"dagster-{cloud_map_name}"

        self.task_definition = build_dagster_runtime_task_definition(
            shared_task_inputs,
            DagsterRuntimeTaskSpec(
                resource_name=f"{name}-webserver-task-def",
                family=td_family,
                cpu="256",
                memory="1024",
                execution_role_arn=iam_roles.webserver_execution_role.arn,
                task_role_arn=iam_roles.webserver_task_role.arn,
                container_name="webserver",
                image_uri=ecr.dagster_webserver_image_uri,
                entry_point=entry_point,
                log_stream_prefix=stream_prefix,
                health_check=DagsterRuntimeHealthCheck(
                    command=_tcp_socket_health_check_command(3000)
                ),
                container_port=3000,
                environment_after_postgres=(
                    DagsterRuntimeEnvironmentVariable(
                        name="AWS_S3_LOCKING_PROVIDER",
                        value="dynamodb",
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_GRPC_TIMEOUT_SECONDS",
                        value="300",
                    ),
                    *_run_worker_prototype_environment(shared_task_inputs, iam_roles),
                ),
                child_opts=self.child_opts,
            ),
        )

        self.service = _fargate_service(
            f"{name}-webserver-service",
            cluster=cluster.cluster,
            task_definition=self.task_definition,
            security_group=security_groups.register.dagster_webserver,
            private_subnet_id=vpc.private_subnet.id,
            namespace_id=service_discovery.namespace.id,
            cloud_map_name=cloud_map_name,
            tags={
                "dagster/service": "Webserver",
                "dagster/job_name": "Webserver",
            },
            child_opts=self.child_opts,
        )

        self.register_outputs({"service_name": self.service.name})


# ---------------------------------------------------------------------------
# dagster-daemon
# ---------------------------------------------------------------------------


class DagsterDaemonServiceComponentResource(pulumi.ComponentResource):
    """Fargate service running the Dagster daemon.

    Mirrors CDK: infrastructure/ecs/dagster_daemon_service.py
    """

    service: aws.ecs.Service
    task_definition: aws.ecs.TaskDefinition

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        cluster: EcsClusterComponentResource,
        ecr: ECRComponentResource,
        postgres: PostgresComponentResource,
        security_groups: SecurityGroupsComponentResource,
        iam_roles: IamRolesComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the Dagster daemon ECS service component."""
        super().__init__(f"{name}:components:DagsterDaemonService", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # Use direct Output references – avoids SSM data-source calls during preview
        shared_task_inputs = DagsterRuntimeTaskSharedInputs(
            postgres_hostname=postgres.private_dns,
            postgres_password_parameter_arn=postgres.ssm_param_password_arn,
            log_group_name=cluster.log_group.name,
            region=aws.get_region().region,
            development_environment=ENVIRONMENT,
            development_location="aws",
        )

        self.task_definition = build_dagster_runtime_task_definition(
            shared_task_inputs,
            DagsterRuntimeTaskSpec(
                resource_name=f"{name}-daemon-task-def",
                family="dagster-daemon",
                cpu="256",
                memory="1024",
                execution_role_arn=iam_roles.daemon_execution_role.arn,
                task_role_arn=iam_roles.daemon_task_role.arn,
                container_name="DagsterDaemonContainer",
                image_uri=ecr.dagster_daemon_image_uri,
                entry_point=("dagster-daemon", "run"),
                log_stream_prefix="dagster-daemon",
                health_check=DagsterRuntimeHealthCheck(command=("CMD-SHELL", "true")),
                environment_after_postgres=(
                    DagsterRuntimeEnvironmentVariable(
                        name="AWS_S3_LOCKING_PROVIDER",
                        value="dynamodb",
                    ),
                    DagsterRuntimeEnvironmentVariable(
                        name="DAGSTER_GRPC_TIMEOUT_SECONDS",
                        value="300",
                    ),
                    *_run_worker_prototype_environment(shared_task_inputs, iam_roles),
                ),
                child_opts=self.child_opts,
            ),
        )

        self.service = _fargate_service(
            f"{name}-daemon-service",
            cluster=cluster.cluster,
            task_definition=self.task_definition,
            security_group=security_groups.register.dagster_daemon,
            private_subnet_id=vpc.private_subnet.id,
            # No Cloud Map – daemon does not receive inbound connections
            namespace_id=None,
            cloud_map_name=None,
            tags={
                "dagster/service": "Daemon",
                "dagster/job_name": "Daemon",
            },
            child_opts=self.child_opts,
        )

        self.register_outputs({"service_name": self.service.name})
