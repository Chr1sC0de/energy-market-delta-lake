#!/bin/bash
(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
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
