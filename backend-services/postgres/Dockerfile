FROM docker.io/library/postgres:14

# Copy initialisation script — runs once on first container start
# when the data directory is empty (postgres entrypoint convention).
# The script creates the Dagster application user and database using
# env vars passed at runtime via compose.
COPY init.sh /docker-entrypoint-initdb.d/init.sh
