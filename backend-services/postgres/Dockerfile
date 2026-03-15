FROM docker.io/library/postgres:16

# Copy initialisation script — runs once on first container start
# when the data directory is empty (postgres entrypoint convention).
# The script creates the Dagster application user and database using
# env vars passed at runtime via compose.
COPY init.sh /docker-entrypoint-initdb.d/init.sh

# Accept remote connections from any address (pg 16 image already sets
# listen_addresses='*' by default; the line below makes it explicit and
# ensures md5 password auth is enforced for all remote connections)
ENV POSTGRES_HOST_AUTH_METHOD=md5

EXPOSE 5432
