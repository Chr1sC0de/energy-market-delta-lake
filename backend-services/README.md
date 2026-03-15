# Local Development — Dagster OSS Stack

Full local deployment of the Dagster OSS architecture using Podman Compose.
Spins up five containers that mirror a production deployment:

| Container | Role | Port |
|---|---|---|
| `postgres` | Dagster instance storage (run, schedule, event-log) | `5432` |
| `localstack` | Mocked AWS S3 | `4566` |
| `aemo-etl` | Dagster gRPC code-location server | `4000` |
| `dagster-webserver` | Dagster UI + GraphQL API | `3000` |
| `dagster-daemon` | Schedule, sensor, and run queue processor | — |

______________________________________________________________________

## Prerequisites

| Tool | Minimum version |
|---|---|
| [Podman](https://podman.io/docs/installation) | 4.9 |
| [podman-compose](https://github.com/containers/podman-compose) | 1.5 |

Verify your installation:

```bash
podman --version
podman-compose --version
```

The Podman socket must be running for `DockerRunLauncher` to spawn run-worker
containers. Enable it for your user session:

```bash
systemctl --user enable --now podman.socket
echo $XDG_RUNTIME_DIR   # should print /run/user/<UID>
ls $XDG_RUNTIME_DIR/podman/podman.sock  # socket must exist
```

______________________________________________________________________

## Directory layout

```
backend-services/
├── compose.yaml                   # Podman Compose — all five services (local deployment)
├── .env                           # Mocked local environment variables
├── localstack/
│   └── init-s3.sh                 # Auto-creates S3 buckets on LocalStack boot
├── postgres/
│   ├── Dockerfile                 # postgres:16 image + init script
│   └── init.sh                    # Creates dagster_user and dagster DB
├── dagster-core/
│   ├── Dockerfile                 # dagster-webserver / dagster-daemon image
│   │                              # Accepts DAGSTER_DEPLOYMENT build arg (local | aws)
│   ├── dagster.local.yaml         # Instance config: DockerRunLauncher, LocalStack S3
│   ├── dagster.aws.yaml           # Instance config: EcsRunLauncher, real S3 (future)
│   ├── workspace.local.yaml       # gRPC code-location — local container network
│   └── workspace.aws.yaml         # gRPC code-location — AWS network (future)
└── dagster-user/
    └── aemo-etl/
        ├── Dockerfile             # aemo-etl gRPC code-location + run-worker image
        └── dagster.yaml           # Minimal dagster.yaml (suppresses SQLite fallback warning)
```

______________________________________________________________________

## Deployment configuration

The `dagster-core` image supports two deployment targets controlled by the
`DAGSTER_DEPLOYMENT` build argument. The correct environment-specific YAML pair
is baked into the image at build time as `dagster.yaml` and `workspace.yaml`.

| `DAGSTER_DEPLOYMENT` | `dagster.yaml` source | `workspace.yaml` source | Run launcher |
|---|---|---|---|
| `local` (default) | `dagster.local.yaml` | `workspace.local.yaml` | `DockerRunLauncher` (Podman) |
| `aws` | `dagster.aws.yaml` | `workspace.aws.yaml` | `EcsRunLauncher` (future) |

`compose.yaml` passes `DAGSTER_DEPLOYMENT=local` as a build arg for both
`dagster-webserver` and `dagster-daemon`. To target AWS, update the build arg
to `aws` and supply the appropriate environment variables.

______________________________________________________________________

## Setup

### 1. Build images and start the stack

All images are built from local Dockerfiles; no pre-built images are pulled for
application code.

```bash
cd backend-services
podman-compose up --build -d
```

Build time is ~5–10 minutes on first run (Rust toolchain for `aemo-etl`, Python
dependency downloads). Subsequent runs use the layer cache and are near-instant.

### 2. Verify services are healthy

```bash
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

Expected output (all containers up, `postgres` and `localstack` show `healthy`):

```
NAMES              STATUS                   PORTS
postgres           Up 30 seconds (healthy)  0.0.0.0:5432->5432/tcp
localstack         Up 30 seconds (healthy)  0.0.0.0:4566->4566/tcp
aemo-etl           Up 20 seconds            0.0.0.0:4000->4000/tcp
dagster-webserver  Up 20 seconds            0.0.0.0:3000->3000/tcp
dagster-daemon     Up 20 seconds
```

### 3. Open the Dagster UI

Navigate to **http://localhost:3000** in your browser.

The `aemo-etl` code location should appear under **Deployment → Code locations**
with its assets and jobs loaded.

______________________________________________________________________

## Environment variables

All variables are defined in `.env` and consumed by `compose.yaml`. Values are
mocked for local development — do not use these in any non-local environment.

| Variable | Value | Purpose |
|---|---|---|
| `POSTGRES_USER` | `postgres` | PostgreSQL superuser |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL superuser password |
| `DAGSTER_POSTGRES_HOSTNAME` | `postgres` | Hostname of the postgres container |
| `DAGSTER_POSTGRES_USER` | `dagster_user` | Dagster application DB user |
| `DAGSTER_POSTGRES_PASSWORD` | `dagster_pass` | Dagster application DB password |
| `DAGSTER_POSTGRES_DB` | `dagster` | Dagster database name |
| `AWS_ENDPOINT_URL` | `http://localstack:4566` | Routes all AWS SDK calls to LocalStack |
| `AWS_DEFAULT_REGION` | `ap-southeast-2` | AWS region |
| `AWS_ACCESS_KEY_ID` | `test` | Dummy credential accepted by LocalStack |
| `AWS_SECRET_ACCESS_KEY` | `test` | Dummy credential accepted by LocalStack |

______________________________________________________________________

## LocalStack S3 buckets

The `localstack/init-s3.sh` script runs automatically inside LocalStack on first
boot and creates the three buckets used by the `aemo-etl` code location:

| Bucket | Purpose |
|---|---|
| `dev-energy-market-io-manager` | Dagster IO manager intermediate storage |
| `dev-energy-market-landing` | Raw landing zone |
| `dev-energy-market-aemo` | AEMO source data |

Bucket names are derived from the defaults in `aemo_etl/configs.py`
(`DEVELOPMENT_ENVIRONMENT=dev`, `NAME_PREFIX=energy-market`).

______________________________________________________________________

## Launching a job via the GraphQL API

The Dagster GraphQL API is available at `http://localhost:3000/graphql`.

### Discover available jobs

```bash
curl -s -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ repositoryOrError(repositorySelector: {repositoryName: \"__repository__\", repositoryLocationName: \"aemo-etl\"}) { ... on Repository { name jobs { name } } } }"
  }' | python3 -m json.tool
```

### Launch a run

```bash
curl -s -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation LaunchRun($executionParams: ExecutionParams!) { launchRun(executionParams: $executionParams) { __typename ... on LaunchRunSuccess { run { runId status } } ... on PythonError { message } } }",
    "variables": {
      "executionParams": {
        "selector": {
          "repositoryLocationName": "aemo-etl",
          "repositoryName": "__repository__",
          "jobName": "__ASSET_JOB"
        },
        "runConfigData": {},
        "mode": "default"
      }
    }
  }' | python3 -m json.tool
```

### Poll run status

Replace `<RUN_ID>` with the `runId` from the launch response:

```bash
curl -s -X POST http://localhost:3000/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ runOrError(runId: \"<RUN_ID>\") { ... on Run { runId status startTime endTime } } }"
  }' | python3 -m json.tool
```

Possible `status` values: `QUEUED` → `STARTING` → `STARTED` → `SUCCESS` / `FAILURE`.

______________________________________________________________________

## Useful commands

### Tail logs for a specific service

```bash
podman logs -f dagster-daemon
podman logs -f dagster-webserver
podman logs -f aemo-etl
podman logs -f postgres
podman logs -f localstack
```

### Connect to the Dagster database directly

```bash
podman exec -it postgres psql -U dagster_user -d dagster
```

### List LocalStack S3 buckets

```bash
podman exec localstack awslocal s3 ls
```

### Inspect a run-worker container

Run-worker containers are ephemeral. List all containers including exited ones:

```bash
podman ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
podman logs <container-name>
```

### Rebuild a single service after a code change

```bash
podman-compose build aemo-etl
podman-compose up -d --no-build aemo-etl
```

For `dagster-core` changes (e.g. `dagster.local.yaml`):

```bash
podman-compose build dagster-webserver   # also rebuilds dagster-daemon image
podman rm -f dagster-webserver dagster-daemon
podman-compose up -d --no-build dagster-webserver dagster-daemon
```

To build for a specific deployment target manually:

```bash
# Local (default — same as compose.yaml)
podman build --build-arg DAGSTER_DEPLOYMENT=local \
  -t dagster-core:local ./dagster-core

# AWS (future — bakes dagster.aws.yaml + workspace.aws.yaml)
podman build --build-arg DAGSTER_DEPLOYMENT=aws \
  -t dagster-core:aws ./dagster-core
```

______________________________________________________________________

## Teardown

> **Note — run-worker containers**
>
> Every job run spawns an ephemeral container via `DockerRunLauncher`. These
> containers exit when the run finishes but are **not** removed automatically.
> They remain attached to `dagster_network`, which causes `podman-compose down`
> to print a network-removal warning:
>
> ```
> Error: "dagster_network" has associated containers with it.
> ```
>
> Remove them before tearing down:
>
> ```bash
> # List all exited run-worker containers
> podman ps -a --format "table {{.Names}}\t{{.Status}}" | grep Exited
>
> # Remove them (adjust names to match)
> podman rm $(podman ps -a -q --filter status=exited --filter network=dagster_network)
> ```

### Stop all containers (preserve volumes)

```bash
# Remove any exited run-worker containers first (see note above)
podman rm $(podman ps -a -q --filter status=exited --filter network=dagster_network) 2>/dev/null || true

podman-compose down
```

Data in the `postgres_data`, `localstack_data`, and `io_manager_storage` volumes
is retained. The next `podman-compose up` resumes from the existing state with no
rebuild required.

### Full teardown — remove containers, network, and volumes

```bash
# Remove any exited run-worker containers first (see note above)
podman rm $(podman ps -a -q --filter status=exited --filter network=dagster_network) 2>/dev/null || true

podman-compose down

podman volume rm \
  dagster-local_postgres_data \
  dagster-local_localstack_data \
  dagster-local_io_manager_storage
```

To also remove all locally built images:

```bash
podman rmi \
  localhost/dagster-local_aemo-etl:latest \
  localhost/dagster-local_dagster-webserver:latest \
  localhost/dagster-local_dagster-daemon:latest \
  localhost/dagster-local_postgres:latest
```

After a full teardown the next `podman-compose up --build` starts from a clean
slate — postgres initialises a fresh database and LocalStack recreates the S3
buckets via `init-s3.sh`.

______________________________________________________________________

## Architecture notes

### Startup order

```
postgres  ──(healthy)──► dagster-webserver
                      └─► dagster-daemon

localstack ──(healthy)──► aemo-etl ──(started)──► dagster-webserver
                                              └─► dagster-daemon
```

### Run execution flow

1. A run is launched via the UI or GraphQL API → stored as `QUEUED` in postgres
1. `dagster-daemon` dequeues the run via `QueuedRunCoordinator`
1. `DockerRunLauncher` pulls `localhost/dagster-local_aemo-etl:latest` and creates
   a new ephemeral run-worker container attached to `dagster_network`
1. The run-worker executes ops, writes intermediate results to S3 via the IO
   manager, and records all events back to postgres
1. The run-worker container exits when the run completes

### Podman socket

`DockerRunLauncher` uses the Python `docker` SDK. The `DOCKER_HOST` environment
variable is set to `unix:///run/podman/podman.sock` in the webserver and daemon
containers to redirect the SDK to Podman. The socket is bind-mounted from
`$XDG_RUNTIME_DIR/podman/podman.sock` on the host.

The same socket path is hard-coded in `dagster.local.yaml` under
`run_launcher.config.container_kwargs.volumes` for run-worker containers
(`/run/user/1000/podman/podman.sock`). If your UID is not `1000`, update
that path accordingly.
