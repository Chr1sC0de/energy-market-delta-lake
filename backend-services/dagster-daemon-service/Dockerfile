FROM python:3.13-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get upgrade -yqq && \
    apt-get install -y --no-install-recommends git curl netcat-openbsd && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME
WORKDIR $DAGSTER_HOME

FROM base AS dagster-daemon

COPY . $DAGSTER_HOME
RUN uv pip install --system dagster dagster-docker dagster-aws dagster-postgres
