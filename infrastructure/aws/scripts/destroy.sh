(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    uv sync
    . ".venv/bin/activate"
    cdk destroy --all --force
)
