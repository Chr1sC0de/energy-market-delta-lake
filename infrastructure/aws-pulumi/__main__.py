"""Energy-market data-pipeline – Pulumi infrastructure entry point.

Dependency order (mirrors AWS CDK app.py):
  1.  VPC  (networking foundation)
  2.  VPC endpoints  (depend on VPC — ECR, CloudWatch Logs, SSM, S3, DynamoDB PrivateLink)
  3.  Security groups  (depend on VPC)
  4.  IAM roles        (independent)
  5.  S3 buckets       (independent)
  6.  DynamoDB table   (independent)
  7.  ECR repositories + Docker image build+push (independent)
  8.  Service discovery namespace  (depends on VPC)
  9.  PostgreSQL EC2   (depends on VPC, security groups)
  10. Bastion host     (depends on VPC, security groups, IAM)
  11. ECS cluster      (depends on VPC, security groups)
  12. FastAPI auth server   (depends on VPC, ECR, security groups)
  13. Caddy server          (depends on VPC, ECR, FastAPI auth, security groups)
  14. ECS: user-code service    (depends on cluster, ECR, postgres, service-discovery, SGs)
  15. ECS: webserver-admin      (depends on cluster, ECR, postgres, service-discovery, SGs, IAM)
  16. ECS: webserver-guest      (same)
  17. ECS: daemon               (depends on cluster, ECR, postgres, SGs, IAM)

Docker socket
-------------
pulumi-docker needs to reach the Docker / Podman daemon.  The provider reads
DOCKER_HOST from the environment.  configs.DOCKER_HOST resolves the correct
socket path at startup (Podman socket on Fedora/RHEL, Docker socket elsewhere)
and exports it so it is set before any docker.Provider resource is created.
"""

import os
import pathlib

import pulumi
import pulumi_docker as docker

from code_locations import (
    default_code_location,
    load_code_locations,
    user_code_component_name,
)
from components.bastion_host import BastionHostComponentResource
from components.caddy import CaddyServerComponentResource
from components.dynamodb import DeltaLockingTableComponentResource
from components.ecr import ECRComponentResource
from components.ecs_cluster import EcsClusterComponentResource
from components.ecs_services import (
    DagsterDaemonServiceComponentResource,
    DagsterUserCodeServiceComponentResource,
    DagsterWebserverServiceComponentResource,
)
from components.fastapi_auth import FastAPIAuthComponentResource
from components.iam_roles import IamRolesComponentResource
from components.postgres import PostgresComponentResource
from components.s3_buckets import S3BucketsComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.service_discovery import ServiceDiscoveryComponentResource
from components.vpc import VpcComponentResource
from components.vpc_endpoints import VpcEndpointsComponentResource
from configs import NAME
from dagster_core_deployment import (
    DEFAULT_DAGSTER_CORE_DEPLOYMENT,
    validate_dagster_core_deployment_config,
)

_config = pulumi.Config()
_dagster_core_deployment = (
    _config.get("dagster_core_deployment") or DEFAULT_DAGSTER_CORE_DEPLOYMENT
)
_ec2_capacity_prototype_enabled = (
    _config.get_bool("enable_ec2_run_worker_capacity_prototype") or False
)
validate_dagster_core_deployment_config(
    dagster_core_deployment=_dagster_core_deployment,
    enable_ec2_run_worker_capacity_prototype=_ec2_capacity_prototype_enabled,
    stack_name=NAME,
)

# ── Docker provider ───────────────────────────────────────────────────────────
# Resolve the Docker / Podman socket automatically when DOCKER_HOST is not set.
# Must happen before constructing docker.Provider (which reads DOCKER_HOST).
if not os.environ.get("DOCKER_HOST"):
    _uid = os.getuid()
    _podman_sock = pathlib.Path(f"/run/user/{_uid}/podman/podman.sock")
    if _podman_sock.exists():
        os.environ["DOCKER_HOST"] = f"unix://{_podman_sock}"

_docker_provider = docker.Provider(
    "docker",
    host=os.environ.get("DOCKER_HOST", "unix:///var/run/docker.sock"),
)

dagster_code_locations = load_code_locations()
default_dagster_code_location = default_code_location(dagster_code_locations)

vpc = VpcComponentResource(NAME)

vpc_endpoints = VpcEndpointsComponentResource(NAME, vpc)

security_groups = SecurityGroupsComponentResource(NAME, vpc)

iam_roles = IamRolesComponentResource(NAME)

s3_buckets = S3BucketsComponentResource(NAME)

delta_locking_table = DeltaLockingTableComponentResource(NAME)

ecr = ECRComponentResource(
    NAME,
    code_locations=dagster_code_locations,
    docker_provider=_docker_provider,
    dagster_core_deployment=_dagster_core_deployment,
)

service_discovery = ServiceDiscoveryComponentResource(NAME, vpc)

postgres = PostgresComponentResource(NAME, vpc, security_groups)

bastion_host = BastionHostComponentResource(NAME, vpc, security_groups, iam_roles)

ecs_cluster = EcsClusterComponentResource(
    NAME,
    vpc,
    security_groups,
    enable_ec2_run_worker_capacity_prototype=_ec2_capacity_prototype_enabled,
    run_worker_instance_profile_arn=iam_roles.ecs_instance_profile.arn,
)

fastapi_auth = FastAPIAuthComponentResource(NAME, vpc, ecr, security_groups)

caddy = CaddyServerComponentResource(NAME, vpc, ecr, fastapi_auth, security_groups)

dagster_user_code_services = {
    location.name: DagsterUserCodeServiceComponentResource(
        user_code_component_name(NAME, location, default_dagster_code_location),
        vpc=vpc,
        cluster=ecs_cluster,
        ecr=ecr,
        postgres=postgres,
        security_groups=security_groups,
        service_discovery=service_discovery,
        iam_roles=iam_roles,
        code_location=location,
    )
    for location in dagster_code_locations
}
dagster_user_code = dagster_user_code_services[default_dagster_code_location.name]

dagster_webserver_admin = DagsterWebserverServiceComponentResource(
    f"{NAME}-webserver-admin",
    vpc=vpc,
    cluster=ecs_cluster,
    ecr=ecr,
    postgres=postgres,
    security_groups=security_groups,
    service_discovery=service_discovery,
    iam_roles=iam_roles,
    cloud_map_name="webserver-admin",
    path_prefix="/dagster-webserver/admin",
    stream_prefix="dagster-webserver-service-admin",
    readonly=False,
)

dagster_webserver_guest = DagsterWebserverServiceComponentResource(
    f"{NAME}-webserver-guest",
    vpc=vpc,
    cluster=ecs_cluster,
    ecr=ecr,
    postgres=postgres,
    security_groups=security_groups,
    service_discovery=service_discovery,
    iam_roles=iam_roles,
    cloud_map_name="webserver-guest",
    path_prefix="/dagster-webserver/guest",
    stream_prefix="dagster-webserver-service-guest",
    readonly=True,
)

dagster_daemon = DagsterDaemonServiceComponentResource(
    f"{NAME}-daemon",
    vpc=vpc,
    cluster=ecs_cluster,
    ecr=ecr,
    postgres=postgres,
    security_groups=security_groups,
    iam_roles=iam_roles,
)
