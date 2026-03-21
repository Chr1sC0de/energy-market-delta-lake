ARG IMAGE=docker.io/library/python:3.13-slim

# ── builder ───────────────────────────────────────────────────────────────────
FROM ${IMAGE} AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV BUILD_DIR=/build

RUN apt-get update && apt-get upgrade -yqq \
    && apt-get install -y --no-install-recommends git curl build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

# install rust (required by polars / deltalake native extensions)
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y;
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc;
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p ${BUILD_DIR}
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

RUN uv export --format requirements-txt --no-dev >requirements.txt;
RUN uv pip install . --system --prefix=/install;
RUN rm -rf $HOME/.cargo;

# ── runtime ───────────────────────────────────────────────────────────────────
FROM ${IMAGE} AS deploy

RUN apt-get update && apt-get upgrade -yqq \
    && apt-get install -y --no-install-recommends curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

COPY --from=builder /install/ /usr/local/

ENV APP_DIR=/opt/marimo
RUN mkdir -p ${APP_DIR}
WORKDIR ${APP_DIR}

COPY src/marimoserver/ ./marimoserver/
COPY notebooks/ ./notebooks/

EXPOSE 2718

CMD ["uvicorn", "marimoserver.main:app", "--host", "0.0.0.0", "--port", "2718"]
