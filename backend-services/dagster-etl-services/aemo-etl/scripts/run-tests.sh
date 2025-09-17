#!/bin/bash
(

    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

    uv sync

    . .venv/bin/activate

    pytest \
        -n 4 \
        --cov=aemo_etl \
        --cov-report=html:.reports/coverage \
        --html=.reports/test-report.html \
        --self-contained-html \
        tests/
)
