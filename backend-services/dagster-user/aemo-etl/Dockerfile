# ── builder ───────────────────────────────────────────────────────────────────────
FROM docker.io/library/python:3.13-slim AS builder

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install the required build tools
RUN apt-get update  && \
    apt-get install -y --no-install-recommends \
    git \
    curl \
    netcat-openbsd \
    build-essential \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*;


# install rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y;
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc;
ENV PATH="/root/.cargo/bin:${PATH}"

# create a build folder and copy contents to folder
ENV BUILD_DIR=/build

# copy the build files
RUN mkdir -p ${BUILD_DIR};
COPY . ${BUILD_DIR}
WORKDIR ${BUILD_DIR}

# install all the dependencies
RUN uv export --format requirements-txt --no-dev > requirements.txt;
RUN uv pip install . --system --prefix=/install;
RUN rm -rf $HOME/.cargo;

# ── dagster-grpc ──────────────────────────────────────────────────────────────────
FROM docker.io/library/python:3.13-slim AS dagster-grpc

# Copy installed packages and created binaries from builder
COPY --from=builder /install/ /usr/local/

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME;
WORKDIR $DAGSTER_HOME

# Copy minimal dagster.yaml so the runtime doesn't fall back to SQLite storage
COPY dagster.yaml $DAGSTER_HOME
