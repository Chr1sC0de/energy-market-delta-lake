# ------------------------------------------------------------------------------------ base
FROM python:3.13-slim AS base

ENV DEBIAN_FRONTEND=noninteractive

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
