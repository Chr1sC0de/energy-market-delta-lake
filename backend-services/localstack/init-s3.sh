#!/usr/bin/env bash
# Runs inside LocalStack on first boot via /etc/localstack/init/ready.d/
# Creates the S3 buckets and DynamoDB locking table required by the aemo-etl
# code location.
# Bucket names mirror aemo_etl/configs.py defaults (DEVELOPMENT_ENVIRONMENT=dev,
# NAME_PREFIX=energy-market).
# The delta_log DynamoDB table schema matches the conftest.py create_delta_log
# fixture and is required by delta-rs when AWS_S3_LOCKING_PROVIDER=dynamodb.

set -euo pipefail

REGION="${AWS_DEFAULT_REGION:-ap-southeast-4}"

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

# --- Cognito -------------------------------------------------------------

# awslocal cognito-idp create-user-pool --pool-name p1 --user-pool-tags "_custom_id_=us-east-1_myid123"
#
# echo "Creating Cognito-idp user pool and client id"
# awslocal \
# 	cognito-idp \
# 	create-user-pool-client \
# 	--user-pool-id "$COGNITO_DAGSTER_USER_POOL_ID" \
# 	--client-name _custom_id_:"$COGNITO_DAGSTER_AUTH_CLIENT_ID"

# to retrieve the client sercret run
#
# export client_secret=$(
# 	awslocal \
# 		cognito-idp \
# 		describe-user-pool-client \
# 		--user-pool-id $pool_id \
# 		--client-id $client_id |
# 		jq -r '.UserPoolClient.ClientSecret'
# )

# echo "Cognito-idp initialisation complete"
