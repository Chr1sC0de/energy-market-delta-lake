#!/bin/bash

# SSH Jump Server Access Script
# -----------------------------
#
# This script provides secure access to the caddy server in the AWS environment.
# It retrieves the necessary SSH key pair from AWS SSM Parameter Store and
# establishes an SSH connection to the caddy server.
#
# Usage:
#   DEVELOPMENT_ENVIRONMENT=dev NAME_PREFIX=energy-market ./ssh-caddy-server.sh
#
# Parameters:
#   DEVELOPMENT_ENVIRONMENT - The environment to connect to (dev, test, prod)
#   NAME_PREFIX - The resource name prefix (defaults to "energy-market")
#
# Requirements:
#   - AWS CLI configured with appropriate permissions
#   - 'rg' (ripgrep) command installed
#   - Valid AWS credentials with access to the specified parameters
#

if [[ -z $name ]]; then
    NAME_PREFIX="energy-market"
fi

DEVELOPMENT_ENVIRONMENT=$(echo "$DEVELOPMENT_ENVIRONMENT" | tr '[:upper:]' '[:lower:]')
GROUP="$DEVELOPMENT_ENVIRONMENT-$NAME_PREFIX"

KEY_PAIR_ID_SSM_PATH="/$GROUP/dagster/caddy-server/key-pair-id"
CADDY_SERVER_INSTANCE_ID_SSM_PATH="/$GROUP/dagster/caddy-server/instance-id"

echo "INFO: GROUP=$GROUP"

echo "INFO: getting parameter $KEY_PAIR_ID_SSM_PATH"

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                              get the id for the key pair                               │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

KEY_PAIR_ID=$(aws ssm get-parameter --name "$KEY_PAIR_ID_SSM_PATH" | rg '"Value": "(.+)",' -r '$1' | tr -d '[:blank:]')

echo "INFO: KEY_PAIR_ID=$KEY_PAIR_ID"

echo "INFO: writing key pair to .scratch folder"

if [[ ! -d .scratch ]]; then
    mkdir .scratch
fi

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │       using the key pair id locate the ssm path and write it to a scratch folder       │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

INSTANCE_KEY_PAIR_SSM_PATH="/ec2/keypair/$KEY_PAIR_ID"

echo -e "$(aws ssm get-parameter --with-decryption --name "$INSTANCE_KEY_PAIR_SSM_PATH" | rg '"Value": "(.+)",' -r '$1' | sed 's/^[[:space:]]*//')" >./.scratch/key-pair.pem

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                 get the caddy server id and get the instance public dns                 │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

CADDY_SERVER_INSTANCE_ID=$(aws ssm get-parameter --name "$CADDY_SERVER_INSTANCE_ID_SSM_PATH" | rg '"Value": "(.+)",' -r '$1' | tr -d '[:blank:]')

CADDY_SERVER_DNS_NAME=$(
    aws ec2 describe-instances \
        --instance-ids "$CADDY_SERVER_INSTANCE_ID" \
        --query 'Reservations[*].Instances[*].PublicDnsName' \
        --output text
)

echo "INFO: CADDY_SERVER_DNS_NAME=$CADDY_SERVER_DNS_NAME"

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                    set the key pair to have the correct permissions                    │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

chmod 700 ./.scratch/key-pair.pem

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                              now ssh into the caddy server                              │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯

ssh -i ./.scratch/key-pair.pem "ec2-user@$CADDY_SERVER_DNS_NAME"
