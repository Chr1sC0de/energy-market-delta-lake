#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cp ../../@common/configurations ./configurations -r
    uv sync
    . ".venv/bin/activate"
    cdk destroy --method direct --force \
        DevEnergyMarketCaddyServer \
        DevEnergyMarketFastApiAuthenticationServer \
        DevEnergyMarketDagsterWebserverServiceAdmin \
        DevEnergyMarketDagsterWebserverServiceGuest

    cdk deploy --method direct --require-approval never --concurrency 8 \
        DevEnergyMarketCaddyServer \
        DevEnergyMarketFastApiAuthenticationServer \
        DevEnergyMarketDagsterWebserverServiceAdmin \
        DevEnergyMarketDagsterWebserverServiceGuest
)
