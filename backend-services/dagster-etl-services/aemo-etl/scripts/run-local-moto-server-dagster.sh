#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

    ./scripts/get-common.sh

    uv sync

    if [[ -d .dagster_home ]]; then
        rm .dagster_home -rf
    fi

    mkdir .dagster_home

    DAGSTER_HOME="$(pwd)/.dagster_home"

    DEVELOPMENT_ENVIRONMENT="dev"
    AWS_ACCESS_KEY_ID=testing
    AWS_SECRET_ACCESS_KEY=testing
    AWS_SECURITY_TOKEN=testing
    AWS_SESSION_TOKEN=testing
    AWS_DEFAULT_REGION=ap-southeast-2
    AWS_ALLOW_HTTP=true
    AWS_S3_LOCKING_PROVIDER=dynamodb
    AWS_ENDPOINT_URL=http://127.0.0.1:5000

    export DEVELOPMENT_ENVIRONMENT
    export DAGSTER_HOME
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_SECURITY_TOKEN
    export AWS_SESSION_TOKEN
    export AWS_DEFAULT_REGION
    export AWS_ALLOW_HTTP
    export AWS_S3_LOCKING_PROVIDER
    export AWS_ENDPOINT_URL

    moto_server -H "127.0.0.1" -p "5000" &

    aws dynamodb create-table \
        --table-name delta_log \
        --attribute-definitions AttributeName=tablePath,AttributeType=S AttributeName=fileName,AttributeType=S \
        --key-schema AttributeName=tablePath,KeyType=HASH AttributeName=fileName,KeyType=RANGE \
        --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

    aws s3api create-bucket \
        --bucket dev-energy-market-bronze \
        --region $AWS_DEFAULT_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    aws s3api create-bucket \
        --bucket dev-energy-market-silver \
        --region $AWS_DEFAULT_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    aws s3api create-bucket \
        --bucket dev-energy-market-gold \
        --region $AWS_DEFAULT_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    aws s3api create-bucket \
        --bucket dev-energy-market-landing \
        --region $AWS_DEFAULT_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    aws s3api create-bucket \
        --bucket dev-energy-market-io-manager \
        --region $AWS_DEFAULT_REGION \
        --create-bucket-configuration LocationConstraint=$AWS_DEFAULT_REGION

    dagster dev -m aemo_etl.definitions --verbose
)
