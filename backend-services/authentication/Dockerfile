ARG IMAGE=docker.io/library/python:3.13-slim

# ── builder ───────────────────────────────────────────────────────────────────
FROM ${IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV BUILD_DIR=/build

RUN apt-get update && apt-get upgrade -yqq \
    && apt-get install -y --no-install-recommends git curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

RUN mkdir -p ${BUILD_DIR}
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

RUN uv export --format requirements-txt --no-dev >requirements.txt;
RUN uv pip install . --system --prefix=/install;

# ── runtime ───────────────────────────────────────────────────────────────────
FROM ${IMAGE} AS deploy

COPY --from=builder /install/ /usr/local/

ENV APP_DIR=/opt/authentication
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY main.py ./

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
