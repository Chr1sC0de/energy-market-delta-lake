if [[ -d .dagster_home ]]; then
    rm .dagster_home -rf
fi

mkdir .dagster_home

DAGSTER_HOME="$(pwd)/.dagster_home"

export DAGSTER_HOME

dagster dev -m aemo_gas --verbose
