"""Dagster core deployment config contracts for the AWS Pulumi stack."""

DEFAULT_DAGSTER_CORE_DEPLOYMENT = "aws"
EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT = "aws-ec2-run-workers-prototype"
RUN_WORKER_EC2_CAPACITY_PROVIDER_SUFFIX = "run-worker-ec2"
EC2_RUN_WORKERS_PROTOTYPE_STACK_NAME = "dev-energy-market"

SUPPORTED_DAGSTER_CORE_DEPLOYMENTS = frozenset(
    {
        DEFAULT_DAGSTER_CORE_DEPLOYMENT,
        EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT,
    }
)


def run_worker_ec2_capacity_provider_name(stack_name: str) -> str:
    """Return the EC2 run-worker capacity provider name for a stack prefix."""
    return f"{stack_name}-{RUN_WORKER_EC2_CAPACITY_PROVIDER_SUFFIX}"


EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME = (
    run_worker_ec2_capacity_provider_name(EC2_RUN_WORKERS_PROTOTYPE_STACK_NAME)
)


def validate_dagster_core_deployment_config(
    *,
    dagster_core_deployment: str,
    enable_ec2_run_worker_capacity_prototype: bool,
    stack_name: str,
) -> None:
    """Validate the coupled Dagster image and ECS capacity-provider config."""
    if dagster_core_deployment not in SUPPORTED_DAGSTER_CORE_DEPLOYMENTS:
        supported = ", ".join(sorted(SUPPORTED_DAGSTER_CORE_DEPLOYMENTS))
        raise ValueError(
            f"Unsupported Dagster core deployment {dagster_core_deployment!r}; "
            f"expected one of: {supported}"
        )

    uses_ec2_run_worker_image = (
        dagster_core_deployment == EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT
    )
    if uses_ec2_run_worker_image and not enable_ec2_run_worker_capacity_prototype:
        raise ValueError(
            f"dagster_core_deployment={EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT!r} "
            "requires enable_ec2_run_worker_capacity_prototype=true; otherwise "
            "Dagster run workers target the EC2 capacity provider but the stack "
            "will not create it."
        )

    if enable_ec2_run_worker_capacity_prototype and not uses_ec2_run_worker_image:
        raise ValueError(
            "enable_ec2_run_worker_capacity_prototype=true requires "
            f"dagster_core_deployment={EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT!r}; "
            "unused EC2 run-worker capacity previews are rejected so config "
            "drift fails early."
        )

    if uses_ec2_run_worker_image and stack_name != EC2_RUN_WORKERS_PROTOTYPE_STACK_NAME:
        active_provider_name = run_worker_ec2_capacity_provider_name(stack_name)
        raise ValueError(
            f"dagster_core_deployment={EC2_RUN_WORKERS_PROTOTYPE_DEPLOYMENT!r} "
            f"is dev-only: active stack name {stack_name!r} would create "
            f"capacity provider {active_provider_name!r}, but "
            "backend-services/dagster-core/"
            "dagster.aws.ec2-run-workers.prototype.yaml targets "
            f"{EC2_RUN_WORKERS_PROTOTYPE_CAPACITY_PROVIDER_NAME!r}."
        )
