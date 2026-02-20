#!/usr/bin/env bash
# Starts a LocalStack Pro container via podman --remote.
# Discovers the container IP, waits for LocalStack to be healthy, then writes
# the resolved endpoint to .localstack.env in the project root so that other
# scripts and VS Code launch configurations can source it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.localstack.env"

CONTAINER_NAME="localstack-dagster-dev"
LOCALSTACK_IMAGE="localstack/localstack-pro"
LOCALSTACK_PORT=4566
READY_TIMEOUT=60

# Remove any stale container with the same name
if podman --remote container exists "${CONTAINER_NAME}" 2>/dev/null; then
	echo "Removing stale container: ${CONTAINER_NAME}" >&2
	podman --remote rm --force "${CONTAINER_NAME}" >/dev/null
fi

echo "Starting LocalStack container: ${CONTAINER_NAME}" >&2
podman --remote run \
	--rm \
	--detach \
	--network=podman \
	--name "${CONTAINER_NAME}" \
	--env "LOCALSTACK_AUTH_TOKEN=${LOCALSTACK_AUTH_TOKEN:-}" \
	--env "DISABLE_CORS_CHECKS=1" \
	"${LOCALSTACK_IMAGE}" >/dev/null

# Inspect the container to get its IP on the podman network
echo "Resolving container IP..." >&2
IP=$(podman --remote inspect "${CONTAINER_NAME}" \
	--format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')

if [[ -z "${IP}" ]]; then
	echo "ERROR: Could not determine IP for container ${CONTAINER_NAME}." >&2
	exit 1
fi

ENDPOINT="http://${IP}:${LOCALSTACK_PORT}"
echo "Container IP: ${IP}, endpoint: ${ENDPOINT}" >&2

# Wait for LocalStack to be healthy
echo "Waiting for LocalStack to be healthy (timeout: ${READY_TIMEOUT}s)..." >&2
deadline=$(($(date +%s) + READY_TIMEOUT))
while true; do
	if curl --silent --fail "${ENDPOINT}/_localstack/health" >/dev/null 2>&1; then
		echo "LocalStack is ready." >&2
		break
	fi
	if [[ $(date +%s) -ge $deadline ]]; then
		echo "ERROR: LocalStack did not become healthy within ${READY_TIMEOUT}s." >&2
		exit 1
	fi
	sleep 1
done

# Write the resolved endpoint to the env file for other scripts and VS Code to consume
cat >"${ENV_FILE}" <<EOF
AWS_ENDPOINT_URL=${ENDPOINT}
EOF

echo "Endpoint written to ${ENV_FILE}" >&2
