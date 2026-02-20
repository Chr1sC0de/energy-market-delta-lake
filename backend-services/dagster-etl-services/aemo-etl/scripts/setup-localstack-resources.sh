#!/usr/bin/env bash
# Creates the S3 buckets and DynamoDB locking table required by the Dagster ETL
# service in LocalStack.  Idempotent: existing resources are left untouched.
#
# AWS_ENDPOINT_URL is sourced from .localstack.env (written by start-localstack.sh)
# if it is not already set in the environment.
set -euo pipefail

mkdir -p .dagster_home

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.localstack.env"

if [[ -z "${AWS_ENDPOINT_URL:-}" ]]; then
	if [[ -f "${ENV_FILE}" ]]; then
		# shellcheck source=/dev/null
		source "${ENV_FILE}"
		echo "Loaded AWS_ENDPOINT_URL from ${ENV_FILE}: ${AWS_ENDPOINT_URL}" >&2
	else
		echo "ERROR: AWS_ENDPOINT_URL is not set and ${ENV_FILE} does not exist." >&2
		echo "       Run scripts/start-localstack.sh first." >&2
		exit 1
	fi
fi

REGION="${AWS_DEFAULT_REGION:-ap-southeast-2}"
PREFIX="${NAME_PREFIX:-energy-market}"
ENV="${DEVELOPMENT_ENVIRONMENT:-dev}"

AWS_CLI="aws --endpoint-url=${AWS_ENDPOINT_URL} --region=${REGION}"

BUCKETS=(
	"${ENV}-${PREFIX}-bronze"
	"${ENV}-${PREFIX}-silver"
	"${ENV}-${PREFIX}-gold"
	"${ENV}-${PREFIX}-landing"
	"${ENV}-${PREFIX}-io-manager"
)

echo "Creating S3 buckets..." >&2
for bucket in "${BUCKETS[@]}"; do
	if $AWS_CLI s3api head-bucket --bucket "${bucket}" 2>/dev/null; then
		echo "  Bucket already exists: ${bucket}" >&2
	else
		$AWS_CLI s3api create-bucket \
			--bucket "${bucket}" \
			--create-bucket-configuration "LocationConstraint=${REGION}" >/dev/null
		echo "  Created bucket: ${bucket}" >&2
	fi
done

echo "Creating DynamoDB delta_log table..." >&2
if $AWS_CLI dynamodb describe-table --table-name delta_log >/dev/null 2>&1; then
	echo "  Table already exists: delta_log" >&2
else
	$AWS_CLI dynamodb create-table \
		--table-name delta_log \
		--attribute-definitions \
		AttributeName=tablePath,AttributeType=S \
		AttributeName=fileName,AttributeType=S \
		--key-schema \
		AttributeName=tablePath,KeyType=HASH \
		AttributeName=fileName,KeyType=RANGE \
		--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 >/dev/null
	echo "  Created table: delta_log" >&2
fi

echo "LocalStack resources ready." >&2
