import typing

import boto3
import botocore.exceptions
from aws_cdk import RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_s3 as s3
from constructs import Construct

from configurations.parameters import (
    STACK_PREFIX,
    DEVELOPMENT_ENVIRONMENT,
    NAME_PREFIX,
)
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    bucket_register: list[tuple[str, str]]

    def __init__(
        self,
        scope: Construct | None,
        id: str | None,
        **kwargs: typing.Unpack[StackKwargs],
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # create a register so we can loop through each bucket to add permissions in other stacks

        self.bucket_register = []

        # create a different landing bucket i.e. landing, bronze, silver and gold for our data

        _ = self.create_bucket(
            f"{STACK_PREFIX}LandingBucket",
            f"{DEVELOPMENT_ENVIRONMENT}-landing-{NAME_PREFIX}",
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}BronzeBucket",
            f"{DEVELOPMENT_ENVIRONMENT}-bronze-{NAME_PREFIX}",
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}SilverBucket",
            f"{DEVELOPMENT_ENVIRONMENT}-silver-{NAME_PREFIX}",
        )

        _ = self.create_bucket(
            f"{STACK_PREFIX}GoldBucket",
            f"{DEVELOPMENT_ENVIRONMENT}-gold-{NAME_PREFIX}",
        )

    def create_bucket(self, bucket_construct_name: str, bucket_name: str) -> s3.Bucket:
        """repeated method for creating a bucket"""
        client_s3 = boto3.client("s3")
        bucket_exists = True

        # check if the bucket exists
        try:
            _ = client_s3.head_bucket(Bucket=bucket_name)
        except botocore.exceptions.ClientError:
            bucket_exists = False

        if bucket_exists:
            # when the bucket already exists load the bucket
            s3_bucket = s3.Bucket.from_bucket_name(
                self, f"Existing{bucket_construct_name}", bucket_name
            )
        else:
            # when not create the bucket
            s3_bucket = s3.Bucket(
                self,
                bucket_construct_name,
                bucket_name=bucket_name,
                removal_policy=RemovalPolicy.RETAIN_ON_UPDATE_OR_DELETE,
                encryption=s3.BucketEncryption.S3_MANAGED,
                versioned=True,
                block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            )

        client_s3.close()

        self.bucket_register.append((bucket_construct_name, bucket_name))

        return s3_bucket
