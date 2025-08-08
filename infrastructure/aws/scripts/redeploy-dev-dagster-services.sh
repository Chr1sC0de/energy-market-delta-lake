#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cp ../../@common/configurations ./configurations -r
    uv sync
    . ".venv/bin/activate"
    cdk destroy --method direct --force \
        DevEnergyMarketDagsterAemoETLUserCodeService \
        DevEnergyMarketDagsterWebserverService \
        DevEnergyMarketDagsterDaemonService
    cdk deploy --all --method direct --require-approval never --concurrency 8
)
