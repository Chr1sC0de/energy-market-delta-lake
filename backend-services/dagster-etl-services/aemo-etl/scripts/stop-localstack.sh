#!/usr/bin/env bash
# Stops and removes the LocalStack development container.
set -euo pipefail

CONTAINER_NAME="localstack-dagster-dev"

if podman --remote container exists "${CONTAINER_NAME}" 2>/dev/null; then
	echo "Stopping LocalStack container: ${CONTAINER_NAME}" >&2
	podman --remote rm --force "${CONTAINER_NAME}" >/dev/null
	echo "LocalStack container stopped." >&2
else
	echo "LocalStack container not running." >&2
fi
