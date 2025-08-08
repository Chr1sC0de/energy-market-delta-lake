#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit

(. ./scripts/get-common.sh)

source .venv/bin/activate
