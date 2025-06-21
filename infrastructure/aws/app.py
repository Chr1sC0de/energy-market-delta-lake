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
    nginx,
)

aws_environment = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"), region=os.getenv("CDK_DEFAULT_REGION")
)

app = cdk.App()

ENV = DEVELOPMENT_ENVIRONMENT.capitalize()

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                       vpc stack                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

VpcStack = vpc.Stack(
    app,
    f"{ENV}{STACK_PREFIX}VPC",
    env=aws_environment,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                      bucket stack                                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

BucketStack = buckets.Stack(
    app,
    f"{ENV}{STACK_PREFIX}Bucket",
    env=aws_environment,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │            create the stacks for the ecr repositories, webserver and daemon            │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

EcrAemoETLUserCode = ecr.user_code.aemo_etl.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrAemoETLUserCode", env=aws_environment
)

EcrDagsterWebserver = ecr.dagster_webserver.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrDagsterWebserver", env=aws_environment
)

EcrDagsterDaemon = ecr.dagster_daemon.Stack(
    app, f"{ENV}{STACK_PREFIX}EcrDagsterDaemon", env=aws_environment
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                               roles and security groups                                │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

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

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                 private dns namespace                                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

PrivateDnsNamespaceStack = service_discovery.Stack(
    app,
    f"{ENV}{STACK_PREFIX}PrivateDnsNamespace",
    env=aws_environment,
    VpcStack=VpcStack,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                 dagster cluster stack                                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

DagsterEcsClusterStack = ecs.cluster.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterEcsCluster",
    env=aws_environment,
    VpcStack=VpcStack,
    SecurityGroupStack=SecurityGroupStack,
    log_group_name="/ecs/dagster-ecs-cluster",
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                  delta locking table                                   │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

DeltaLockingTableStack = locking_table.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DeltaLockingTable",
    env=aws_environment,
    IamRolesStack=IamRolesStack,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                     postgres stack                                     │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

DagsterPostgresStack = postgres.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterPostgres",
    env=aws_environment,
    VpcStack=VpcStack,
    SecurityGroupStack=SecurityGroupStack,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                  nginx instance stack                                  │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

DagsterNginxStack = nginx.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterNginx",
    env=aws_environment,
    VpcStack=VpcStack,
    SecurityGroupStack=SecurityGroupStack,
)

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                      here we start creating the required services                      │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

DagsterAemoETLUserCodeService = ecs.dagster_user_code_service.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterAemoETLUserCodeService",
    env=aws_environment,
    target_module="aemo_etl.definitions",
    VpcStack=VpcStack,
    EcsDagsterClusterStack=DagsterEcsClusterStack,
    PrivateDnsNamespaceStack=PrivateDnsNamespaceStack,
    UserCodeRepositoryStack=EcrAemoETLUserCode,
    PostgresStack=DagsterPostgresStack,
    SecurityGroupStack=SecurityGroupStack,
    service_discovery_name="aemo-etl",
    stream_prefix="dagster-aemo-etl-user-code-service",
)

DagsterWebserverService = ecs.dagster_webserver_service.Stack(
    app,
    f"{ENV}{STACK_PREFIX}DagsterWebserverService",
    env=aws_environment,
    VpcStack=VpcStack,
    EcsDagsterClusterStack=DagsterEcsClusterStack,
    PostgresStack=DagsterPostgresStack,
    PrivateDnsNamespaceStack=PrivateDnsNamespaceStack,
    SecurityGroupStack=SecurityGroupStack,
    stream_prefix="dagster-webserver-service",
    EcrDagsterWebserver=EcrDagsterWebserver,
    IamRolesStack=IamRolesStack,
    user_code_dependencies=[
        DagsterAemoETLUserCodeService,
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
    user_code_dependencies=[
        DagsterAemoETLUserCodeService,
    ],
)


_ = app.synth()
