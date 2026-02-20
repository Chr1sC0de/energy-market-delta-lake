FROM ubuntu:26.04

USER root

ENV DEBIAN_FRONTEND=noninteractive
ENV TAR_OPTIONS="--no-same-owner --no-same-permissions"
ENV DOTFILES_INSTALL_SCRIPT=https://raw.githubusercontent.com/Chr1sC0de/dotfiles/refs/heads/master/install.sh

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    curl \
    openssh-server \ 
    openssh-client \
    ca-certificates \
    bash-completion \
    podman \
    podman-docker \
    entr \
    tar;

RUN curl $DOTFILES_INSTALL_SCRIPT | bash -;

RUN bash -l -i -c "\. $HOME/.bashrc && nvim --headless '+Lazy! sync\' +MasonToolsInstallSync +q!";

RUN curl -fsSL https://opencode.ai/install | bash;

# install dockerfmt
RUN curl -LO https://github.com/reteps/dockerfmt/releases/download/v0.3.9/dockerfmt-v0.3.9-linux-amd64.tar.gz;
RUN tar -xzf dockerfmt-*-linux-amd64.tar.gz -C /usr/local/bin && \
    rm dockerfmt-*-linux-amd64.tar.gz;

# install localstack
RUN curl -LO https://github.com/localstack/localstack-cli/releases/download/v4.13.1/localstack-cli-4.13.1-linux-amd64-onefile.tar.gz;
RUN tar xvzf localstack-cli-4.13.1-linux-*-onefile.tar.gz -C /usr/local/bin && \
    rm localstack-cli-4.13.1-linux-*-onefile.tar.gz;

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip";
RUN unzip awscliv2.zip;
RUN ./aws/install;
RUN /root/.local/bin/uv tool install awscli-local;
RUN /root/.local/bin/uv tool install prek
