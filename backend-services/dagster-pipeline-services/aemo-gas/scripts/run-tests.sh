(

    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

    ./scripts/get-common.sh

    uv sync

    . .venv/bin/activate

    pytest \
        --cov=aemo_gas \
        --cov-report=html:reports/coverage \
        tests/
)
