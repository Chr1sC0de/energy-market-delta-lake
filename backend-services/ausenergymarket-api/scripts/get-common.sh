#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cp ../../@common/configurations ./configurations -r
    uv add configurations/
    uv sync
)
