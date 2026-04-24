# =============================================================================
# dagster-core — webserver and daemon image
#
# Build arguments
#   DAGSTER_DEPLOYMENT  "local" (default) | "aws"
#                       Selects which dagster.<env>.yaml and workspace.<env>.yaml
#                       are baked in as dagster.yaml / workspace.yaml.
#
# Examples
#   # Local development (default)
#   podman build --tag dagster-core:local .
#
#   # AWS deployment (future)
#   podman build --build-arg DAGSTER_DEPLOYMENT=aws --tag dagster-core:aws .
# =============================================================================

# Declare before the first FROM so it is in scope for the final stage selector.
ARG DAGSTER_DEPLOYMENT=local

# ── builder ───────────────────────────────────────────────────────────────────────
FROM docker.io/library/python:3.13-slim AS builder

ENV BUILD_DIR=/build

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

RUN mkdir -p ${BUILD_DIR};
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

RUN uv export --format requirements-txt --no-dev >requirements.txt \
    && uv pip install . --system --prefix=/install

# ── base ──────────────────────────────────────────────────────────────────────────
# Common runtime layer — packages only, no environment-specific config.
FROM docker.io/library/python:3.13-slim AS base

ENV DAGSTER_HOME=/opt/dagster/dagster_home/

COPY --from=builder /install/bin/ /usr/local/bin/
COPY --from=builder /install/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

RUN mkdir -p $DAGSTER_HOME;
WORKDIR $DAGSTER_HOME

# Copy all config files into DAGSTER_HOME so every environment variant is
# present; the environment-specific stages below select the correct pair.
COPY . $DAGSTER_HOME

# ── local ─────────────────────────────────────────────────────────────────────────
# Local development: DockerRunLauncher, LocalStack S3, Podman socket.
FROM base AS local

RUN cp dagster.local.yaml dagster.yaml \
    && cp workspace.local.yaml workspace.yaml;

# ── aws ───────────────────────────────────────────────────────────────────────────
# AWS deployment: EcsRunLauncher, real S3, RDS postgres.
# Run launcher and workspace details to be completed when AWS infra is defined.
FROM base AS aws

RUN cp dagster.aws.yaml dagster.yaml \
    && cp workspace.aws.yaml workspace.yaml;

# ── deploy ────────────────────────────────────────────────────────────────────────
# Final stage — inherits from the stage named by DAGSTER_DEPLOYMENT.
# ARG must be re-declared here to bring the build-arg back into scope after
# the preceding FROM statements (standard multi-stage ARG scoping rule).
ARG DAGSTER_DEPLOYMENT
FROM ${DAGSTER_DEPLOYMENT} AS deploy
