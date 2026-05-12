"""Shared Dagster ECS runtime task-definition builder."""

import json
from dataclasses import dataclass

import pulumi
import pulumi_aws as aws


@dataclass(frozen=True, kw_only=True)
class DagsterRuntimeTaskSharedInputs:
    """Inputs shared by all Dagster runtime ECS task definitions."""

    postgres_hostname: pulumi.Input[str]
    postgres_password_parameter_arn: pulumi.Input[str]
    log_group_name: pulumi.Input[str]
    region: pulumi.Input[str]
    development_environment: str
    development_location: str


@dataclass(frozen=True, kw_only=True)
class DagsterRuntimeEnvironmentVariable:
    """Environment variable injected into the Dagster runtime container."""

    name: str
    value: pulumi.Input[str]


@dataclass(frozen=True, kw_only=True)
class DagsterRuntimeHealthCheck:
    """ECS health-check settings for a Dagster runtime container."""

    command: tuple[str, ...]
    interval: int = 15
    timeout: int = 5
    retries: int = 4
    start_period: int = 60


@dataclass(frozen=True, kw_only=True)
class DagsterRuntimeTaskSpec:
    """Role-specific task-definition and one-container runtime settings."""

    resource_name: str
    family: str
    cpu: str
    memory: str
    execution_role_arn: pulumi.Input[str] | None
    task_role_arn: pulumi.Input[str]
    container_name: str
    image_uri: pulumi.Input[str]
    entry_point: tuple[str, ...]
    log_stream_prefix: str
    health_check: DagsterRuntimeHealthCheck
    container_port: int | None = None
    environment_after_postgres: tuple[DagsterRuntimeEnvironmentVariable, ...] = ()
    environment_after_development: tuple[DagsterRuntimeEnvironmentVariable, ...] = ()
    child_opts: pulumi.ResourceOptions | None = None


def build_dagster_runtime_task_definition(
    shared: DagsterRuntimeTaskSharedInputs,
    spec: DagsterRuntimeTaskSpec,
) -> aws.ecs.TaskDefinition:
    """Build a Fargate task definition with one Dagster runtime container."""
    return aws.ecs.TaskDefinition(
        spec.resource_name,
        family=spec.family,
        requires_compatibilities=["FARGATE"],
        network_mode="awsvpc",
        cpu=spec.cpu,
        memory=spec.memory,
        execution_role_arn=spec.execution_role_arn,
        task_role_arn=spec.task_role_arn,
        container_definitions=_container_definitions(shared, spec),
        opts=spec.child_opts,
    )


def _container_definitions(
    shared: DagsterRuntimeTaskSharedInputs,
    spec: DagsterRuntimeTaskSpec,
) -> pulumi.Output[str]:
    output_values: dict[str, pulumi.Input[str]] = {
        "image": spec.image_uri,
        "pg_host": shared.postgres_hostname,
        "pg_pass_param": shared.postgres_password_parameter_arn,
        "log_group": shared.log_group_name,
        "region": shared.region,
    }
    environment_after_postgres = tuple(spec.environment_after_postgres)
    environment_after_development = tuple(spec.environment_after_development)

    for index, variable in enumerate(environment_after_postgres):
        output_values[f"env_after_postgres_{index}"] = variable.value

    for index, variable in enumerate(environment_after_development):
        output_values[f"env_after_development_{index}"] = variable.value

    return pulumi.Output.all(**output_values).apply(
        lambda values: json.dumps(
            [
                _container_definition(
                    shared,
                    spec,
                    values,
                    environment_after_postgres,
                    environment_after_development,
                )
            ]
        )
    )  # ty:ignore[missing-argument]


def _container_definition(
    shared: DagsterRuntimeTaskSharedInputs,
    spec: DagsterRuntimeTaskSpec,
    values: dict[str, str],
    environment_after_postgres: tuple[DagsterRuntimeEnvironmentVariable, ...],
    environment_after_development: tuple[DagsterRuntimeEnvironmentVariable, ...],
) -> dict[str, object]:
    container: dict[str, object] = {
        "name": spec.container_name,
        "image": values["image"],
        "essential": True,
        "entryPoint": list(spec.entry_point),
        "environment": _environment(
            shared,
            values,
            environment_after_postgres,
            environment_after_development,
        ),
        "secrets": [
            {
                "name": "DAGSTER_POSTGRES_PASSWORD",
                "valueFrom": values["pg_pass_param"],
            }
        ],
    }

    if spec.container_port is not None:
        container["portMappings"] = [
            {
                "containerPort": spec.container_port,
                "hostPort": spec.container_port,
                "protocol": "tcp",
            }
        ]

    container["logConfiguration"] = {
        "logDriver": "awslogs",
        "options": {
            "awslogs-group": values["log_group"],
            "awslogs-region": values["region"],
            "awslogs-stream-prefix": spec.log_stream_prefix,
        },
    }
    container["healthCheck"] = {
        "command": list(spec.health_check.command),
        "interval": spec.health_check.interval,
        "timeout": spec.health_check.timeout,
        "retries": spec.health_check.retries,
        "startPeriod": spec.health_check.start_period,
    }

    return container


def _environment(
    shared: DagsterRuntimeTaskSharedInputs,
    values: dict[str, str],
    environment_after_postgres: tuple[DagsterRuntimeEnvironmentVariable, ...],
    environment_after_development: tuple[DagsterRuntimeEnvironmentVariable, ...],
) -> list[dict[str, str]]:
    environment = [
        {"name": "DAGSTER_POSTGRES_DB", "value": "dagster"},
        {"name": "DAGSTER_POSTGRES_HOSTNAME", "value": values["pg_host"]},
        {"name": "DAGSTER_POSTGRES_USER", "value": "dagster_user"},
    ]
    environment.extend(
        {
            "name": variable.name,
            "value": values[f"env_after_postgres_{index}"],
        }
        for index, variable in enumerate(environment_after_postgres)
    )
    environment.extend(
        [
            {
                "name": "DEVELOPMENT_ENVIRONMENT",
                "value": shared.development_environment,
            },
            {"name": "DEVELOPMENT_LOCATION", "value": shared.development_location},
        ]
    )
    environment.extend(
        {
            "name": variable.name,
            "value": values[f"env_after_development_{index}"],
        }
        for index, variable in enumerate(environment_after_development)
    )
    return environment
