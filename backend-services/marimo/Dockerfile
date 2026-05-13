ARG IMAGE=docker.io/library/python:3.13-slim

# ── builder ───────────────────────────────────────────────────────────────────
FROM ${IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV BUILD_DIR=/build

# hadolint ignore=DL3008
RUN apt-get update \
    && apt-get install -y --no-install-recommends git curl build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

# install rust (required by polars / deltalake native extensions)
# hadolint ignore=DL4006
RUN ["/bin/bash", "-o", "pipefail", "-c", "curl https://sh.rustup.rs -sSf | bash -s -- -y"]
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p ${BUILD_DIR}
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

RUN uv export --format requirements-txt --no-dev >requirements.txt \
    && uv pip install . --system --prefix=/install \
    && rm -rf "$HOME/.cargo"

# ── shared runtime ────────────────────────────────────────────────────────────
FROM ${IMAGE} AS runtime

COPY --from=builder /install/ /usr/local/

ENV APP_DIR=/opt/marimo \
    MARIMO_NOTEBOOKS_DIR=/opt/marimo/notebooks
RUN mkdir -p ${APP_DIR} /workspace/notebooks /workspace/issue-drafts
WORKDIR ${APP_DIR}

COPY src/marimoserver/ ./marimoserver/
COPY notebooks/ ./notebooks/

EXPOSE 2718

FROM runtime AS dashboard

ENV MARIMO_WORKSPACE_KIND=dashboard

CMD ["uvicorn", "marimoserver.main:app", "--host", "0.0.0.0", "--port", "2718"]

# Compatibility alias for existing build scripts that still request deploy.
FROM dashboard AS deploy

FROM runtime AS codex-workspace

ENV MARIMO_WORKSPACE_KIND=codex-research \
    MARIMO_NOTEBOOKS_DIR=/workspace/notebooks \
    MARIMO_WORKSPACE_ROOT=/workspace

COPY research-workspace/ /workspace/
WORKDIR /workspace

CMD ["marimo", "edit", "/workspace/notebooks", "--headless", "--host", "0.0.0.0", "--port", "2718", "--no-token"]
