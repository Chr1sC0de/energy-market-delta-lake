import boto3
import pulumi
import pulumi_aws as aws
from botocore.exceptions import ClientError


def bucket_exists(bucket_name: str) -> bool:
    s3 = boto3.client("s3")
    try:
        s3.head_bucket(Bucket=bucket_name)
        return True
    except ClientError as e:
        # If a client error is thrown, check if it's a 404 (Not Found) or 403 (Forbidden)
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            return False  # Bucket does not exist
        elif error_code == "403":
            return True  # Bucket exists, but you don't have access
        else:
            raise  # Other unexpected errors


class S3BucketsComponentResource(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:

        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)
        super().__init__(f"{name}:components:S3Buckets", name, {}, opts)

        self.io_manager_bucket = self.create_bucket(f"{name}-io-manager")
        self.landing = self.create_bucket(f"{name}-landing")
        self.archive = self.create_bucket(f"{name}-archive")
        self.aemo = self.create_bucket(f"{name}-aemo")

        self.setup_archive_lifecycle()

        self.register_outputs({})

    def setup_archive_lifecycle(self) -> None:
        aws.s3.BucketLifecycleConfiguration(
            f"{self.name}-archive-lifecycle",
            bucket=self.archive.bucket,
            rules=[
                aws.s3.BucketLifecycleConfigurationRuleArgs(
                    id="TransitionToGlacier",
                    status="Enabled",
                    transitions=[
                        aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                            days=30,
                            storage_class="GLACIER",
                        ),
                        aws.s3.BucketLifecycleConfigurationRuleTransitionArgs(
                            days=180,
                            storage_class="DEEP_ARCHIVE",
                        ),
                    ],
                    expiration=aws.s3.BucketLifecycleConfigurationRuleExpirationArgs(
                        days=3650,
                    ),
                )
            ],
            opts=pulumi.ResourceOptions(parent=self.archive),
        )

    def create_bucket(
        self,
        bucket_name: str,
        force_destroy: bool = False,
        retain_on_delete: bool = True,
    ) -> aws.s3.Bucket:

        # Always declare with the component as parent so the URN is stable.
        # On fresh deployments after pulumi down (buckets retained), Pulumi will
        # fail with BucketAlreadyOwnedByYou — in that case, run:
        #   pulumi import aws:s3/bucket:Bucket <name> <name> --parent <component-urn>
        # for each retained bucket before re-running pulumi up.
        if bucket_exists(bucket_name):
            bucket = aws.s3.Bucket(
                bucket_name,
                bucket=bucket_name,
                force_destroy=force_destroy,
                opts=pulumi.ResourceOptions(import_=bucket_name),
            )
        else:
            bucket = aws.s3.Bucket(
                bucket_name,
                bucket=bucket_name,
                force_destroy=force_destroy,
                opts=pulumi.ResourceOptions(
                    parent=self,
                    retain_on_delete=retain_on_delete,
                ),
            )

        bucket_child_opts = pulumi.ResourceOptions(parent=bucket)

        # Server-side encryption (standalone resource)
        aws.s3.BucketServerSideEncryptionConfiguration(
            f"{bucket_name}-server-side-encryption",
            bucket=bucket.bucket,
            rules=[
                aws.s3.BucketServerSideEncryptionConfigurationRuleArgs(
                    apply_server_side_encryption_by_default=aws.s3.BucketServerSideEncryptionConfigurationRuleApplyServerSideEncryptionByDefaultArgs(
                        sse_algorithm="AES256",
                    ),
                )
            ],
            opts=bucket_child_opts,
        )

        # Block all public access
        aws.s3.BucketPublicAccessBlock(
            f"{bucket_name}-public-access-block",
            bucket=bucket.bucket,
            block_public_acls=True,
            block_public_policy=True,
            ignore_public_acls=True,
            restrict_public_buckets=True,
            opts=bucket_child_opts,
        )

        # Versioning (disabled)
        aws.s3.BucketVersioning(
            f"{bucket_name}-versioning",
            bucket=bucket.bucket,
            versioning_configuration=aws.s3.BucketVersioningVersioningConfigurationArgs(
                status="Disabled",
            ),
            opts=bucket_child_opts,
        )

        return bucket
