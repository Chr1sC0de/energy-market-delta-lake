(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit
    cdk destroy --all --force
)
