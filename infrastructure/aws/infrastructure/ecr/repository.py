from typing import Unpack

from aws_cdk import RemovalPolicy
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecr_assets as ecr_assets
from cdk_ecr_deployment import DockerImageName, ECRDeployment
from constructs import Construct

from infrastructure.configurations import SHARED_PREFIX
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    repository_name: str
    repository: ecr.Repository
    image_asset: ecr_assets.DockerImageAsset

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        repository_prefix: str,
        repository_suffix: str,
        directory: str,
        image_target: str | None = None,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        self.repository_name = (
            f"{SHARED_PREFIX}/{repository_prefix}/{repository_suffix}"
        )

        self.repository = ecr.Repository(
            self,
            "ECRRepository",
            repository_name=self.repository_name,
            empty_on_delete=True,
            removal_policy=RemovalPolicy.DESTROY,
            image_tag_mutability=ecr.TagMutability.MUTABLE,
            lifecycle_rules=[
                ecr.LifecycleRule(
                    description="Keep only the latest 5 images",
                    max_image_count=5,
                )
            ],
        )

        self.image_asset = ecr_assets.DockerImageAsset(
            self,
            "DockerImageAsset",
            directory=directory,
            target=image_target,
        )

        _ = ECRDeployment(
            self,
            "ECRDeployment",
            src=DockerImageName(self.image_asset.image_uri),
            dest=DockerImageName(f"{self.repository.repository_uri}:latest"),
        )
