(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    uv sync
    . ".venv/bin/activate"
    cdk deploy --all --method direct --require-approval never --concurrency 8
)
