FROM python:3.13-slim AS base
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN apt-get update && apt-get upgrade -yqq && \                                                                                                                                                                                                                                     
    apt-get install -y --no-install-recommends \
    git \
    curl \
    netcat-openbsd \
    build-essential \
    && \                                                                                                                                                                                                         
    apt-get clean && \                                                                                                                                                                                                                                                              
    rm -rf /var/lib/apt/lists/*                                                                                                                                                                                                                                                     
ENV DAGSTER_HOME=/opt/dagster/dagster_home/
RUN mkdir -p $DAGSTER_HOME
WORKDIR $DAGSTER_HOME

# Get Rust
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
ENV PATH="/root/.cargo/bin:${PATH}"

FROM base AS dagster-grpc

COPY . $DAGSTER_HOME
RUN uv export --format requirements-txt --no-dev > requirements.txt
RUN uv pip install -r requirements.txt --system
RUN rm -rf $HOME/.cargo
# Remove build-essential and clean up
RUN apt-get purge -y --auto-remove build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
