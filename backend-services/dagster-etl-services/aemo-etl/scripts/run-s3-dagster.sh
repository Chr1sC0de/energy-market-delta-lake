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
    DEVELOPMENT_LOCATION="local"
    AWS_DEFAULT_REGION=ap-southeast-2
    AWS_S3_ALLOW_UNSAFE_RENAME="true"

    export DAGSTER_HOME AWS_DEFAULT_REGION DEVELOPMENT_LOCATION AWS_S3_ALLOW_UNSAFE_RENAME

    uv run dagster dev -m aemo_etl.definitions --verbose
)
