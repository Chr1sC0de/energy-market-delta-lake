(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cdk deploy --all --method direct --require-approval never --concurrency 8
)
