import json

import pulumi
import pulumi_aws as aws

LIFECYCLE_POLICY = json.dumps(
    {
        "rules": [
            {
                "rulePriority": 1,
                "description": "Keep only the latest 5 images",
                "selection": {
                    "tagStatus": "any",
                    "countType": "imageCountMoreThan",
                    "countNumber": 5,
                },
                "action": {"type": "expire"},
            }
        ]
    }
)


class ECRComponentResource(pulumi.ComponentResource):
    def __init__(self, name: str, opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__(f"{name}:components:ecr", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.dagster_postgres = self.get_repository(f"{self.name}/dagster/postgres")

    def get_repository(self, repository_name: str) -> aws.ecr.Repository:
        repo = aws.ecr.Repository(
            f"{self.name}-{repository_name}",
            name=repository_name,
            image_tag_mutability="MUTABLE",
            force_delete=True,
            image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
                scan_on_push=False,
            ),
            opts=self.child_opts,
        )

        aws.ecr.LifecyclePolicy(
            f"{self.name}-{repository_name}-lifecycle",
            repository=repo.name,
            policy=LIFECYCLE_POLICY,
            opts=pulumi.ResourceOptions(parent=repo),
        )
        return repo
