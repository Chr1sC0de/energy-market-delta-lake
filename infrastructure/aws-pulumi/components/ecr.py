"""ECR repositories with automated Docker image build and push.

Each repository is coupled to a `docker.Image` resource that builds the
corresponding Dockerfile and pushes the result to ECR whenever the build
context changes (Pulumi tracks a hash of the context directory).

Authentication to ECR uses a short-lived token obtained via
`aws.ecr.get_authorization_token()` — no static credentials needed.

Backend-service layout (relative to repo root):
  backend-services/
    dagster-core/          → webserver + daemon images (build target: deploy, arg: DAGSTER_DEPLOYMENT=aws)
    dagster-user/aemo-etl/ → user-code gRPC server
    authentication/        → FastAPI auth server
    caddy/                 → Caddy reverse proxy
    postgres/              → Postgres sidecar (not deployed to ECS, kept for local dev)
"""

import json
import pathlib

import pulumi
import pulumi_aws as aws
import pulumi_docker as docker

# Resolve the backend-services directory relative to this file so the path
# is correct regardless of the working directory used to run `pulumi up`.
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
_SERVICES = _REPO_ROOT / "backend-services"

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
    """All ECR repositories plus automated build-and-push for each image."""

    def __init__(
        self,
        name: str,
        docker_provider: docker.Provider | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:ecr", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)
        # Provider used for all docker.Image build+push resources.
        self._docker_provider = docker_provider

        # Obtain an ECR auth token (valid 12 h; refreshed on every pulumi up).
        token = aws.ecr.get_authorization_token_output()
        aws.get_region()

        # Shared ECR registry credentials for docker.Image resources.
        # The registry server is the account-level ECR endpoint (no repo path).
        self._registry = pulumi.Output.all(
            password=token.password,
            server=token.proxy_endpoint,  # e.g. https://123456789.dkr.ecr.ap-southeast-2.amazonaws.com
        ).apply(
            lambda a: docker.RegistryArgs(
                server=a["server"],
                username="AWS",
                password=a["password"],
            )  # ty:ignore[invalid-argument-type]
        )  # ty:ignore[missing-argument]

        # ── postgres (local-dev only, no image build needed for ECS) ─────────
        self.dagster_postgres = self._make_repo(f"{name}/dagster/postgres")

        # ── dagster-core: webserver ───────────────────────────────────────────
        self.dagster_webserver = self._make_repo(f"{name}/dagster/webserver")
        self._build_image(
            resource_name=f"{name}-dagster-webserver-image",
            repo=self.dagster_webserver,
            context=str(_SERVICES / "dagster-core"),
            target="deploy",
            build_args={"DAGSTER_DEPLOYMENT": "aws"},
            platform="linux/amd64",
        )

        # ── dagster-core: daemon (same Dockerfile, same target) ───────────────
        self.dagster_daemon = self._make_repo(f"{name}/dagster/daemon")
        self._build_image(
            resource_name=f"{name}-dagster-daemon-image",
            repo=self.dagster_daemon,
            context=str(_SERVICES / "dagster-core"),
            target="deploy",
            build_args={"DAGSTER_DEPLOYMENT": "aws"},
            platform="linux/amd64",
        )

        # ── user-code: aemo-etl ───────────────────────────────────────────────
        self.dagster_user_code_aemo_etl = self._make_repo(
            f"{name}/dagster/user-code/aemo-etl"
        )
        self._build_image(
            resource_name=f"{name}-dagster-user-code-aemo-etl-image",
            repo=self.dagster_user_code_aemo_etl,
            context=str(_SERVICES / "dagster-user" / "aemo-etl"),
            platform="linux/amd64",
        )

        # ── caddy ─────────────────────────────────────────────────────────────
        self.caddy = self._make_repo(f"{name}/dagster/caddy")
        self._build_image(
            resource_name=f"{name}-dagster-caddy-image",
            repo=self.caddy,
            context=str(_SERVICES / "caddy"),
            platform="linux/amd64",
        )

        # ── authentication ────────────────────────────────────────────────────
        self.authentication = self._make_repo(f"{name}/dagster/authentication")
        self._build_image(
            resource_name=f"{name}-dagster-authentication-image",
            repo=self.authentication,
            context=str(_SERVICES / "authentication"),
            platform="linux/amd64",
        )

        self.register_outputs({})

    # ── helpers ───────────────────────────────────────────────────────────────

    def _make_repo(self, repository_name: str) -> aws.ecr.Repository:
        """Create an ECR repository with a keep-5 lifecycle policy."""
        slug = repository_name.replace("/", "-")
        repo = aws.ecr.Repository(
            f"{self.name}-{slug}",
            name=repository_name,
            image_tag_mutability="MUTABLE",
            force_delete=True,
            image_scanning_configuration=aws.ecr.RepositoryImageScanningConfigurationArgs(
                scan_on_push=False,
            ),
            opts=self.child_opts,
        )
        aws.ecr.LifecyclePolicy(
            f"{self.name}-{slug}-lifecycle",
            repository=repo.name,
            policy=LIFECYCLE_POLICY,
            opts=pulumi.ResourceOptions(parent=repo),
        )
        return repo

    def _build_image(
        self,
        resource_name: str,
        repo: aws.ecr.Repository,
        context: str,
        target: str | None = None,
        build_args: dict[str, str] | None = None,
        platform: str = "linux/amd64",
    ) -> docker.Image:
        """Build a Docker image and push it to the given ECR repository.

        Pulumi hashes the build context; a rebuild is triggered only when
        source files change.
        """
        image_name = repo.repository_url.apply(lambda url: f"{url}:latest")  # ty:ignore[missing-argument, invalid-argument-type]

        image = docker.Image(
            resource_name,
            image_name=image_name,
            build=docker.DockerBuildArgs(
                context=context,
                dockerfile=f"{context}/Dockerfile",
                target=target,
                args=build_args or {},
                platform=platform,
                # Use the legacy builder (V1) — BuildKit's gRPC session is not
                # supported by Podman's Docker-compatibility shim.
                builder_version=docker.BuilderVersion.BUILDER_V1,
            ),
            registry=self._registry,
            opts=pulumi.ResourceOptions(
                parent=repo,
                provider=self._docker_provider,
            ),
        )
        return image
