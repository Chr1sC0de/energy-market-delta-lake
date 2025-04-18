(
    ./get-common.sh

    uv sync

    if [[ -d .dagster_home ]]; then
        rm .dagster_home -rf
    fi

    mkdir .dagster_home

    DAGSTER_HOME="$(pwd)/.dagster_home"

    export DAGSTER_HOME

    uv run dagster dev -m aemo_gas --verbose
)
