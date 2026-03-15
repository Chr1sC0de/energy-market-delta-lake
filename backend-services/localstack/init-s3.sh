#!/usr/bin/env bash
# Runs inside LocalStack on first boot via /etc/localstack/init/ready.d/
# Creates the S3 buckets and DynamoDB locking table required by the aemo-etl
# code location.
# Bucket names mirror aemo_etl/configs.py defaults (DEVELOPMENT_ENVIRONMENT=dev,
# NAME_PREFIX=energy-market).
# The delta_log DynamoDB table schema matches the conftest.py create_delta_log
# fixture and is required by delta-rs when AWS_S3_LOCKING_PROVIDER=dynamodb.

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-ap-southeast-2}"

# --- S3 buckets -----------------------------------------------------------
for bucket in \
	dev-energy-market-io-manager \
	dev-energy-market-landing \
	dev-energy-market-aemo; do
	echo "Creating bucket: $bucket"
	awslocal s3 mb "s3://${bucket}" --region "$REGION" 2>/dev/null || echo "Bucket $bucket already exists"
done

echo "S3 bucket initialisation complete."

# --- DynamoDB delta_log locking table ------------------------------------
echo "Creating DynamoDB table: delta_log"
awslocal dynamodb create-table \
	--table-name delta_log \
	--attribute-definitions \
	AttributeName=tablePath,AttributeType=S \
	AttributeName=fileName,AttributeType=S \
	--key-schema \
	AttributeName=tablePath,KeyType=HASH \
	AttributeName=fileName,KeyType=RANGE \
	--provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
	--region "$REGION" \
	2>/dev/null || echo "Table delta_log already exists"

echo "DynamoDB initialisation complete."
