#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    uv sync
    . ".venv/bin/activate"
    cdk destroy --method direct --force \
        DevEnergyMarketDagsterAemoETLUserCodeService \
        DevEnergyMarketDagsterWebserverService \
        DevEnergyMarketDagsterDaemonService
    cdk deploy --all --method direct --require-approval never --concurrency 8
)
