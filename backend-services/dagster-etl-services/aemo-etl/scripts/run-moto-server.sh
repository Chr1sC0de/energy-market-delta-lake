#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

    uv sync

    if [[ -d .dagster_home ]]; then
        rm .dagster_home -rf
    fi

    mkdir .dagster_home

    . .venv/bin/activate

    DAGSTER_HOME="$(pwd)/.dagster_home"
    export DAGSTER_HOME

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
    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_SECURITY_TOKEN
    export AWS_SESSION_TOKEN
    export AWS_DEFAULT_REGION
    export AWS_ALLOW_HTTP
    export AWS_S3_LOCKING_PROVIDER
    export AWS_ENDPOINT_URL

    uv run moto_server -H "127.0.0.1" -p "5000" &

)
