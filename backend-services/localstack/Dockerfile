FROM docker.io/localstack/localstack:latest

RUN apt-get update && apt-get upgrade -yqq \
    && apt-get install -y --no-install-recommends jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*;

COPY init-s3.sh /etc/localstack/init/ready.d/init-s3.sh
