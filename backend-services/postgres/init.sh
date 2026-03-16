#!/usr/bin/env bash
# Runs once on first container start (data directory empty).
# Creates the Dagster application user and database.
# Required env vars (set via compose):
#   POSTGRES_USER            - superuser (provided by the postgres image)
#   DAGSTER_POSTGRES_USER    - application user to create
#   DAGSTER_POSTGRES_PASSWORD
#   DAGSTER_POSTGRES_DB

set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER ${DAGSTER_POSTGRES_USER} WITH PASSWORD '${DAGSTER_POSTGRES_PASSWORD}';
	CREATE DATABASE ${DAGSTER_POSTGRES_DB};
	GRANT ALL PRIVILEGES ON DATABASE ${DAGSTER_POSTGRES_DB} TO ${DAGSTER_POSTGRES_USER};
EOSQL

# Connect to the new database and grant schema access
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$DAGSTER_POSTGRES_DB" <<-EOSQL
	GRANT ALL ON SCHEMA public TO ${DAGSTER_POSTGRES_USER};
EOSQL
