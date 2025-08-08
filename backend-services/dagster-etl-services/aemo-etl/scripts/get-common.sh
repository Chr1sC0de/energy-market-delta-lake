#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cp ../../../@common/configurations ./configurations -r
    cp ../../@common/dagster.yaml .
    cp ../../@common/workspace.yaml .
    uv add configurations/
    uv sync
)
