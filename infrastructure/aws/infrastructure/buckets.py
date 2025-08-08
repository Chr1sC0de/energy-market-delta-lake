from collections.abc import Sequence
from typing import Any, NotRequired, TypedDict, Unpack

import boto3
import botocore.exceptions
from aws_cdk import RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_s3 as s3
from aws_cdk.aws_iam import IRole
from aws_cdk.aws_kms import IKey
from constructs import Construct
from jsii import Number

from infrastructure.configurations import (
    DEVELOPMENT_ENVIRONMENT,
    NAME_PREFIX,
    STACK_PREFIX,
)
from infrastructure.utils import StackKwargs

# pyright: reportExplicitAny=false


class BucketKwargs(TypedDict):
    access_control: NotRequired[s3.BucketAccessControl]
    auto_delete_objects: NotRequired[bool]
    block_public_access: NotRequired[s3.BlockPublicAccess]
    bucket_key_enabled: NotRequired[bool]
    bucket_name: NotRequired[str]
    cors: NotRequired[Sequence[s3.CorsRule | dict[str, Any]]]
    encryption: NotRequired[s3.BucketEncryption]
    encryption_key: NotRequired[IKey]
    enforce_ssl: NotRequired[bool]
    event_bridge_enabled: NotRequired[bool]
    intelligent_tiering_configurations: NotRequired[
        Sequence[s3.IntelligentTieringConfiguration | dict[str, Any]]
    ]
    inventories: NotRequired[Sequence[s3.Inventory | dict[str, Any]]]
    lifecycle_rules: NotRequired[Sequence[s3.LifecycleRule | dict[str, Any]]]
    metrics: NotRequired[Sequence[s3.BucketMetrics | dict[str, Any]]]
    minimum_tls_version: NotRequired[Number]
    notifications_handler_role: NotRequired[IRole]
    notifications_skip_destination_validation: NotRequired[bool]
    object_lock_default_retention: NotRequired[s3.ObjectLockRetention]
    object_lock_enabled: NotRequired[bool]
    object_ownership: NotRequired[s3.ObjectOwnership]
    public_read_access: NotRequired[bool]
    removal_policy: NotRequired[RemovalPolicy]
    replication_rules: NotRequired[Sequence[s3.ReplicationRule | dict[str, Any]]]
    server_access_logs_bucket: NotRequired[s3.IBucket]
    server_access_logs_prefix: NotRequired[str]
    target_object_key_format: NotRequired[s3.TargetObjectKeyFormat]
    transfer_acceleration: NotRequired[bool]
    transition_default_minimum_object_size: NotRequired[
        s3.TransitionDefaultMinimumObjectSize
    ]
    versioned: NotRequired[bool]
    website_error_document: NotRequired[str]
    website_index_document: NotRequired[str]
    website_redirect: NotRequired[s3.RedirectTarget | dict[str, Any]]
    website_routing_rules: NotRequired[Sequence[s3.RoutingRule | dict[str, Any]]]


class Stack(_Stack):
    bucket_register: list[tuple[str, str]]

    def __init__(
        self,
        scope: Construct | None,
        id: str | None,
        **kwargs: Unpack[StackKwargs],
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # create a register so we can loop through each bucket to add permissions in other stacks

        self.bucket_register = []

        # create a different landing bucket i.e. landing, bronze, silver and gold for our data

        _ = self.create_bucket(
            f"{STACK_PREFIX}IOManagerBucket",
            bucket_name=f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-io-manager",
            removal_policy=RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}LandingBucket",
            bucket_name=f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-landing",
            removal_policy=RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        bucket_table_policies = dict(
            removal_policy=RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}BronzeBucket",
            bucket_name=f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-bronze",
            **bucket_table_policies,
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}SilverBucket",
            bucket_name=f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-silver",
            **bucket_table_policies,
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}GoldBucket",
            bucket_name=f"{DEVELOPMENT_ENVIRONMENT}-{NAME_PREFIX}-gold",
            **bucket_table_policies,
        )

    def create_bucket(
        self, bucket_construct_name: str, **kwargs: Unpack[BucketKwargs]
    ) -> s3.Bucket:
        """repeated method for creating a bucket"""
        client_s3 = boto3.client("s3")
        bucket_exists = True

        # check if the bucket exists
        try:
            _ = client_s3.head_bucket(Bucket=kwargs["bucket_name"])
        except botocore.exceptions.ClientError:
            bucket_exists = False

        if bucket_exists:
            # when the bucket already exists load the bucket
            s3_bucket = s3.Bucket.from_bucket_name(
                self, f"Existing{bucket_construct_name}", kwargs["bucket_name"]
            )
        else:
            # when not create the bucket
            s3_bucket = s3.Bucket(
                self,
                bucket_construct_name,
                **kwargs,
            )

        client_s3.close()

        self.bucket_register.append((bucket_construct_name, kwargs["bucket_name"]))

        return s3_bucket
