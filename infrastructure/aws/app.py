#!/usr/bin/env python3
import os

import aws_cdk as cdk
from configurations.parameters import DEVELOPMENT_ENVIRONMENT, STACK_PREFIX

from infrastructure import (
    buckets,
    iam_roles,
    locking_table,
    postgres,
    security_groups,
    service_discovery,
    vpc,
    ecr,
    ecs,
)

aws_environment = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

app = cdk.App()

ENV = DEVELOPMENT_ENVIRONMENT.capitalize()

VpcStack = vpc.Stack(
    app,
    f"{ENV}{STACK_PREFIX}VPC",
    env=aws_environment,
)

BucketStack = buckets.Stack(
    app,
    f"{ENV}{STACK_PREFIX}Bucket",
    env=aws_environment,
)

# create the stacks for the ecr repositories, webserver and daemon

EcrAemoGasPipeline = ecr.pipelines.aemo_gas.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrAemoGasPipeline", env=aws_environment
)

EcrDagsterWebserver = ecr.dagster_webserver.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrDagsterWebserver", env=aws_environment
)

EcrDagsterDaemon = ecr.dagster_daemon.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrDagsterDaemon", env=aws_environment
)

# roles and security groups

IamRolesStack = iam_roles.Stack(
    app,
    f"{ENV}{STACK_PREFIX}IAMRoles",
    env=aws_environment,
)

SecurityGroupStack = security_groups.Stack(
    app,
    f"{ENV}{STACK_PREFIX}SecurityGroups",
    VpcStack=VpcStack,
    env=aws_environment,
)

PrivateDsnNamespaceStack = service_discovery.Stack(
    app,
    f"{ENV}{STACK_PREFIX}PrivateDnsNamespace",
    env=aws_environment,
    VpcStack=VpcStack,
)

DagsterEcsClusterStack = ecs.cluster.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterEcsCluster",
    env=aws_environment,
    VpcStack=VpcStack,
    log_group_name="/ecs/dagster-ecs-cluster",
)

DeltaLockingTableStack = locking_table.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DeltaLockingTable",
    env=aws_environment,
    IamRolesStack=IamRolesStack,
)

DagsterPostgresStack = postgres.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterPostgres",
    env=aws_environment,
    VpcStack=VpcStack,
    SecurityGroupStack=SecurityGroupStack,
)

# here we start creating the required services

DagsterAemoGasPipelineService = ecs.dagster_pipeline_service.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterAemoGasPipelineService",
    env=aws_environment,
    VpcStack=VpcStack,
    EcsDagsterClusterStack=DagsterEcsClusterStack,
    PrivateDsnNamespaceStack=PrivateDsnNamespaceStack,
    PipelineRepositoryStack=EcrAemoGasPipeline,
    PostgresStack=DagsterPostgresStack,
    SecurityGroupStack=SecurityGroupStack,
    service_discovery_name="aemo-gas",
    stream_prefix="dagster-aemo-gas-pipeline-service",
)

DagsterWebserverService = ecs.dagster_webserver_service.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterWebserverService",
    env=aws_environment,
    VpcStack=VpcStack,
    EcsDagsterClusterStack=DagsterEcsClusterStack,
    PostgresStack=DagsterPostgresStack,
    SecurityGroupStack=SecurityGroupStack,
    stream_prefix="dagster-webserver-service",
    EcrDagsterWebserver=EcrDagsterWebserver,
    IamRolesStack=IamRolesStack,
    pipeline_dependencies=[
        DagsterAemoGasPipelineService,
    ],
)

DagsterDaemonService = ecs.dagster_daemon_service.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterDaemonService",
    env=aws_environment,
    VpcStack=VpcStack,
    EcsDagsterClusterStack=DagsterEcsClusterStack,
    PostgresStack=DagsterPostgresStack,
    SecurityGroupStack=SecurityGroupStack,
    stream_prefix="dagster-daemon-service",
    EcrDagsterDaemon=EcrDagsterDaemon,
    IamRolesStack=IamRolesStack,
    pipeline_dependencies=[
        DagsterAemoGasPipelineService,
    ],
)


_ = app.synth()
