#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cp ../@common/dagster.yaml .
    cp ../@common/workspace.yaml .
)
