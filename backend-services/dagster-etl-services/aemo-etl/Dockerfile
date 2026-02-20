# base builder image

FROM python:3.13-slim AS builder

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# install the required build tools
RUN apt-get update && apt-get upgrade -yqq && \
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

# dagster grpc

FROM python:3.13-slim AS dagster-grpc

RUN apt-get update && apt-get upgrade -yqq && \
    apt-get install -y --no-install-recommends \
    curl \
    vim \
    netcat-openbsd \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*;

# Copy installed packages and created binaries to the current folder

COPY --from=builder /install/bin/ /usr/local/bin/
COPY --from=builder /install/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME;
WORKDIR $DAGSTER_HOME

COPY scripts/ $DAGSTER_HOME
COPY dagster.yaml $DAGSTER_HOME
COPY workspace.yaml $DAGSTER_HOME
