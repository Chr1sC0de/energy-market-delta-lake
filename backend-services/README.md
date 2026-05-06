# Local Development and Testing — Podman Compose Stack

Local development and testing harness for the repository using Podman Compose.
This stack is useful for validating service interactions and Dagster workflows
locally, but it is not the canonical architecture. The primary deployed
architecture is defined in `infrastructure/aws-pulumi/`.

## Table of contents

- [Prerequisites](#prerequisites)
- [Directory layout](#directory-layout)
- [Deployment configuration](#deployment-configuration)
- [Setup](#setup)
- [Environment variables](#environment-variables)
- [LocalStack S3 buckets](#localstack-s3-buckets)
- [Cached Archive seed](#cached-archive-seed)
- [Isolated AEMO ETL e2e stack](#isolated-aemo-etl-e2e-stack)
- [Launching a job via the GraphQL API](#launching-a-job-via-the-graphql-api)
- [Useful commands](#useful-commands)
- [Related docs](#related-docs)
- [Teardown](#teardown)
- [Architecture notes](#architecture-notes)

| Container | Role | Port |
|---|---|---|
| `postgres` | Dagster instance storage (run, schedule, event-log) | `5432` |
| `localstack` | Mocked AWS services for local storage workflows | `4566` |
| `aemo-etl-seed-localstack` | Optional cached Archive seed loader for local **End-to-end test** setup | — |
| `aemo-etl` | Dagster gRPC code-location server | `4000` |
| `dagster-webserver-admin` | Protected Dagster UI + GraphQL API | internal |
| `dagster-webserver-guest` | Guest Dagster UI + GraphQL API | internal |
| `dagster-daemon` | Schedule, sensor, and run queue processor | — |
| `authentication` | OIDC/session bridge for protected routes | internal |
| `marimo` | Local notebook service | internal |
| `caddy` | Local reverse proxy and public entrypoint | `80`, `443` |

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

to expose the required ports locally

```bash
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
```

to revert

```bash
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=1024
```

______________________________________________________________________

## Directory layout

```text
backend-services/
├── compose.yaml                   # Podman Compose — local test/dev service stack
├── .e2e/aemo-etl/                 # Ignored cached Archive seed and manifests
├── localstack/
│   └── init-s3.sh                 # Auto-creates S3 buckets on LocalStack boot
├── postgres/
│   ├── Dockerfile                 # postgres:14 image + init script
│   └── init.sh                    # Creates dagster_user and dagster DB
├── dagster-core/
│   ├── Dockerfile                 # dagster-webserver / dagster-daemon image
│   │                              # Accepts DAGSTER_DEPLOYMENT build arg (local | aws)
│   ├── dagster.local.yaml         # Instance config: DockerRunLauncher, LocalStack S3
│   ├── dagster.aws.yaml           # Instance config: EcsRunLauncher, deployed AWS runtime
│   ├── workspace.local.yaml       # gRPC code-location — local container network
│   └── workspace.aws.yaml         # gRPC code-location — AWS network
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
| `aws` | `dagster.aws.yaml` | `workspace.aws.yaml` | `EcsRunLauncher` |

`compose.yaml` passes `DAGSTER_DEPLOYMENT=local` as a build arg for the two
Dagster webservers and the daemon. To target AWS, update the build arg
to `aws` and supply the appropriate environment variables.

For the AWS deployment, `dagster.aws.yaml` caps queued runs at 20 concurrent
tasks. Run-worker ECS tasks and the long-running Dagster services use
`FARGATE_SPOT` in the AWS dev deployment. Spot capacity can be unavailable or
interrupted, so Dagster run monitoring is enabled for AWS runs. The monitor
polls every 120 seconds, allows 180 seconds for run start and cancellation, caps
run runtime at 30 minutes, and marks unrecovered runs failed without automatic
resume attempts so the failure alert sensor can publish to SNS.

______________________________________________________________________

## Setup

### 1. Load environment variables

`compose.yaml` reads environment variables from the shell at invocation time.
The variables are defined in `.envrc` in this directory (`backend-services/.envrc`).

#### Option A — direnv (recommended)

Install [direnv](https://direnv.net/docs/installation.html) and allow the file
once:

```bash
# from backend-services/
direnv allow
```

direnv will reload the variables automatically whenever you `cd` into this directory.

#### Option B — manual source

Run this once per shell session before using `podman-compose`:

```bash
source .envrc
```

Verify the variables are set:

```bash
echo $DAGSTER_POSTGRES_USER   # should print: dagster_user
```

### 2. Build images and start the stack

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

Expected output: all containers are up, with `postgres`, `localstack`,
`aemo-etl`, and `marimo` eventually becoming healthy.

```text
NAMES                    STATUS                   PORTS
postgres                 Up 30 seconds (healthy)  0.0.0.0:5432->5432/tcp
localstack               Up 30 seconds (healthy)  0.0.0.0:4566->4566/tcp
aemo-etl                 Up 20 seconds (healthy)
dagster-webserver-admin  Up 20 seconds
dagster-webserver-guest  Up 20 seconds
dagster-daemon           Up 20 seconds
authentication           Up 20 seconds
marimo                   Up 20 seconds (healthy)
caddy                    Up 20 seconds            0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
```

### 3. Open the Dagster UI

Navigate to <https://localhost> in your browser.

Useful routes:

- `/dagster-webserver/guest` for the guest Dagster UI
- `/dagster-webserver/admin` for the protected admin Dagster UI
- `/marimo` for local notebooks

The `aemo-etl` code location should appear in Dagster under
**Deployment → Code locations** with its assets and jobs loaded.

______________________________________________________________________

## Environment variables

All variables are defined in `backend-services/.envrc` with mock values for local
development. Do not use these in any non-local environment. See [Setup →
Load environment variables](#1-load-environment-variables) for how to load
them before starting the stack.

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
| `DAGSTER_FAILURE_ALERT_TOPIC_ARN` | empty | Optional SNS topic ARN for failed-run alert fan-out |
| `DAGSTER_FAILURE_ALERT_BASE_URL` | `https://localhost/dagster-webserver/admin` | Dagster UI base URL included in failed-run alerts |
| `AEMO_ETL_E2E_SEED_ENABLED` | `0` | Set to `1` to require cached Archive seed loading before `aemo-etl` starts |
| `AEMO_ETL_E2E_SEED_RAW_LATEST_COUNT` | `3` | Required cached raw source-table objects per table |
| `AEMO_ETL_E2E_SEED_ZIP_LATEST_COUNT` | `3` | Required cached zip objects per domain |

______________________________________________________________________

## LocalStack S3 buckets

The `localstack/init-s3.sh` script runs automatically inside LocalStack on first
boot and creates the four buckets used by the `aemo-etl` code location, plus
the DynamoDB `delta_log` table used for Delta locking:

| Bucket | Purpose |
|---|---|
| `dev-energy-market-io-manager` | Dagster IO manager intermediate storage |
| `dev-energy-market-landing` | Raw landing zone |
| `dev-energy-market-archive` | Archived source files and successful zip payloads |
| `dev-energy-market-aemo` | AEMO source data |

Bucket names are derived from the defaults in `aemo_etl/configs.py`
(`DEVELOPMENT_ENVIRONMENT=dev`, `NAME_PREFIX=energy-market`).

## Cached Archive seed

The local stack includes a one-shot `aemo-etl-seed-localstack` service. It is a
no-op by default. When `AEMO_ETL_E2E_SEED_ENABLED=1`, the service validates the
cache under `backend-services/.e2e/aemo-etl`, uploads the selected cached
Archive objects into LocalStack landing storage, writes
`seed-run-manifest.json`, and must complete successfully before `aemo-etl`
starts.

Refresh the cache from the live dev archive bucket with the AEMO ETL CLI:

```bash
cd backend-services/dagster-user/aemo-etl
uv run aemo-e2e-archive-seed refresh
```

The refresh path defaults to `dev-energy-market-archive`, requires 3 latest raw
objects for each required `gas_model` source table and 3 latest zip objects for
each required zip domain, and fails with a manifest if coverage is short.

## Isolated AEMO ETL e2e stack

Use the isolated AEMO ETL **End-to-end test** stack when the validation should
avoid the broader fixed developer compose stack:

```bash
backend-services/scripts/aemo-etl-e2e run
```

The command uses the fixed e2e stack name `aemo-etl-e2e` and writes generated
runtime files under `backend-services/.e2e/aemo-etl/runs/<run-id>/`. The
generated stack contains Postgres, LocalStack, the cached Archive seed loader,
the AEMO ETL gRPC service, one Dagster webserver, and the Dagster daemon. It
does not start Caddy, authentication, Marimo, or the second developer webserver.
The seed loader validates the cached Archive seed under
`backend-services/.e2e/aemo-etl`, or under the explicit `--seed-root` path when
the stack runs from an ephemeral worktree. Refresh that cache with
`uv run aemo-e2e-archive-seed refresh` only when the local seed needs to change.

| Option | Default | Purpose |
|---|---:|---|
| `--scenario` | `full-gas-model` | Named target profile; `promotion-gas-model` narrows seed volume and launches the explicit `gas_model` upstream asset graph for Ralph **Promotion** |
| `--webserver-port` | `3001` | Host port for the isolated Dagster webserver |
| `--seed-root` | `backend-services/.e2e/aemo-etl` | Cached Archive seed root mounted into the isolated stack |
| `--raw-latest-count` | scenario-specific | Cached raw source-table objects required per table; `3` for `full-gas-model`, `1` for `promotion-gas-model` |
| `--zip-latest-count` | scenario-specific | Cached zip objects required per domain; `3` for `full-gas-model`, `1` for `promotion-gas-model` |
| `--timeout-seconds` | scenario-specific | Overall stack and dataflow timeout; `5400` for `full-gas-model`, `1200` for `promotion-gas-model` |
| `--max-concurrent-runs` | scenario-specific | Dagster queued run coordinator `max_concurrent_runs`; `6` for `full-gas-model`, `6` for `promotion-gas-model` |

After the isolated stack reaches readiness, the command drives the Dagster
dataflow through GraphQL. The `full-gas-model` scenario starts only the unzipper
sensors, event-driven raw sensors, and gas model automation sensors; NEMWeb
discovery schedules, the failed-run alert sensor, the daily date-dimension
schedule, and maintenance schedules stay stopped. It bootstraps non-sensor
prerequisites, including the date dimension and table-metadata prerequisite,
then polls Dagster until the full `gas_model` target has materialized and
required checks have reported success. The `promotion-gas-model` scenario keeps
automation stopped and launches explicit Dagster asset-run batches by dependency
wave for every materializable `gas_model` asset plus its materializable upstream
closure. It skips live `bronze_nemweb_public_files_*` discovery/listing assets
so the gate starts from seeded LocalStack objects, matching
`+group:gas_model` targeting without creating one sensor-triggered run per
upstream source table. Each Promotion batch uses Dagster's in-process executor
inside its Podman run-worker container to avoid a subprocess storm against
LocalStack and the Delta Lake DynamoDB lock table. Background or queued runs may
still exist after
target/check coverage is complete. Failed runs, failed or missing target
materializations, and failed asset checks fail the command, including
WARN-level checks such as skipped selected S3 keys.

### Promotion gate contract

Ralph uses the `promotion-gas-model` scenario as the AEMO ETL
**End-to-end test** gate during **Promotion** when a Gitflow **Delivery mode**
range changes non-doc runtime files under
`backend-services/dagster-user/aemo-etl/`. The gate runs from the same source
worktree as the aggregate **Push check**, after that **Push check** and before
the Promotion worktree, merge to `main`, push, `dev` branch sync, GitHub
metadata update, or issue closure. It protects work already accepted through
**Local integration** to `dev`; it is not a standalone **Test lane**, and it is
not part of the local **Fast check** or **Commit check**.

The gate exists because AEMO ETL runtime changes can pass narrowed unit,
component, static, or script checks while still breaking the complete local
Dagster dataflow. The approved #77 coverage invariants are:

- exercise Dagster orchestration, LocalStack/S3 storage, Podman run-worker
  containers, and the Dagster GraphQL monitor
- materialize every materializable Dagster asset in group `gas_model`
- preserve final asset-check status for that target as part of the
  **Promotion** decision
- keep current discovery evidence visible:
  `dg list defs --assets "group:gas_model" --json` reports 29 `gas_model`
  assets and 112 asset checks, including
  `silver/metadata/silver_table_metadata` as a group member

The full scenario remains the sensor/dependency-path reference. The
`promotion-gas-model` scenario uses the #78 targeted launch shape to preserve
the same final coverage inside the guard budget: it narrows the raw and zip seed
horizon to 1 object, keeps automation stopped, launches explicit
dependency-wave asset batches for the `gas_model` upstream asset graph, and
skips live `bronze_nemweb_public_files_*` discovery/listing assets so the gate
starts from seeded LocalStack objects. Each batch still runs inside a Podman
run-worker container, and direct launches pace submission against Dagster
`max_concurrent_runs` so dependency-wave ordering is preserved and queued runs
remain bounded.

### Promotion telemetry and budgets

Each `run-manifest.json` includes the structured telemetry added in #75 and the
budget report fields added in #76. The command output prints either an
informational `E2E budget report` for non-enforced scenarios or
`E2E Promotion guard regression budgets` for `promotion-gas-model`.
Successful and failed runs write whatever telemetry is available; if the
failure occurs after Dagster monitoring starts, samples captured before the
failure remain in the manifest.

| Field | Meaning |
|---|---|
| `telemetry.total_gate_duration_seconds` | Whole gate runtime, including stack startup, dataflow monitoring, and cleanup |
| `telemetry.stack_startup_duration_seconds` | Time spent rendering config, starting the isolated stack, and reaching readiness |
| `telemetry.dagster_dataflow_monitor_duration_seconds` | Time spent driving and polling the Dagster dataflow through GraphQL |
| `telemetry.cleanup_duration_seconds`, `telemetry.cleanup_phases`, `cleanup`, `cleanup_issues` | Cleanup time, per-phase cleanup status, and non-benign cleanup evidence |
| `telemetry.dagster_dataflow.peak_active_run_count` | Highest non-queued Dagster run count observed by the monitor |
| `telemetry.dagster_dataflow.peak_queued_run_count` | Highest queued Dagster run count observed by the monitor |
| `telemetry.dagster_dataflow.final_run_status_counts` | Final Dagster run counts by status; the budget report also derives total and successful run counts from this map |
| `telemetry.dagster_dataflow.final_target_progress` | Materialized, missing, failed, and total target asset counts for the `gas_model` gate target |
| `telemetry.dagster_dataflow.first_target_materialization_at`, `last_target_materialization_at` | First and last observed target materialization timestamps |
| `telemetry.dagster_dataflow.final_missing_asset_check_count`, `final_failed_asset_check_count` | Final asset-check drift for the gate target |
| `dataflow.scenario_evidence` | Direct-launch coverage evidence: scenario, launch mode, target group, target asset count, selected upstream closure count, skipped live source keys, wave count, batch count, and asset batch size |
| `budget.status`, `budget.thresholds`, `budget.failures`, `budget.run_manifest` | Enforced Promotion budget result, threshold values, actionable failure lines, and the manifest path operators should inspect |

The `promotion-gas-model` scenario enforces #79 Promotion guard regression
budgets from the approved #78 targeted baseline: total gate duration at or
below 20 minutes, peak active runs at or below `6`, peak queued runs at or
below `6`, total Dagster runs at or below `48`, target progress exactly
`29/29`, and missing or failed target assets and asset checks at `0`. These
budgets protect **Promotion** from run explosion and missing coverage; they are
not generic local development performance claims. The full scenario prints the
same telemetry for review without enforcing those Promotion budgets.

Interpret failures by the failed field. Duration, peak-run, queued-run, or
total-run failures usually mean run explosion, run queue contention, or a local
environment slowdown that needs evidence before retrying or changing the launch
shape. Target progress, missing target asset, failed target asset, missing
asset-check, or failed asset-check failures mean the approved #77 coverage
contract was not met and the source revision must not be promoted until the
dataflow or check regression is fixed. Missing telemetry is also a gate failure
because Ralph cannot prove the **Promotion** source revision satisfied the
contract. Budget failures mark the run manifest failed and print observed
values, thresholds, and the `run-manifest.json` path; keep that manifest and
logs as the first inspection target instead of weakening the guard.

Local service images are tagged for the e2e stack. Missing images are built
automatically, existing images are reused by default, and `--rebuild` forces all
local images to rebuild before startup.

The command derives the host Podman socket from
`$XDG_RUNTIME_DIR/podman/podman.sock` and fails before startup if the socket is
missing. The generated e2e Dagster config uses that socket for run-worker
containers and attaches them to the e2e network. The generated compose stack
uses fixed service IPs for Postgres, LocalStack, and the AEMO ETL code server so
run-worker containers do not depend on Podman DNS during high-concurrency
Promotion gates. The `full-gas-model` scenario
defaults to a 90 minute timeout and Dagster `max_concurrent_runs` `6`; override
them with `--timeout-seconds` and `--max-concurrent-runs`.

Successful runs attempt to clean e2e containers, Dagster run-worker
containers, named volumes, and the e2e network by default after the full
dataflow completes. Pre-run cleanup treats already-absent e2e resources as
benign. Post-success cleanup also treats an already-absent e2e network as
benign when compose has already removed the stack. Other post-run cleanup
warnings or failures do not change a successful dataflow result, but they do
change the manifest cleanup status and are captured as `cleanup_issues`. Failed
runs, including cached seed coverage shortfalls, preserve containers, volumes,
service logs, the run manifest, and the seed-run manifest for inspection. Use
`--reuse` to keep and reuse the e2e stack after a successful run, or
`--always-clean` to clean containers, volumes, and run-worker containers even
after failure.

______________________________________________________________________

## Launching a job via the GraphQL API

The guest Dagster GraphQL API is available through Caddy at
`https://localhost/graphql`.

### Discover available jobs

```bash
curl -sk -X POST https://localhost/graphql \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ repositoryOrError(repositorySelector: {repositoryName: \"__repository__\", repositoryLocationName: \"aemo-etl\"}) { ... on Repository { name jobs { name } } } }"
  }' | python3 -m json.tool
```

### Launch a run

```bash
curl -sk -X POST https://localhost/graphql \
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
curl -sk -X POST https://localhost/graphql \
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
podman logs -f dagster-webserver-admin
podman logs -f dagster-webserver-guest
podman logs -f aemo-etl
podman logs -f postgres
podman logs -f localstack
podman logs -f caddy
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

## Related docs

- [Repository overview](../README.md)
- [Repository architecture](../docs/repository/architecture.md)
- [AWS Pulumi infrastructure](../infrastructure/aws-pulumi/README.md)
- [Authentication service](authentication/README.md)
- [Marimo notebook service](marimo/README.md)
- [aemo-etl project docs](dagster-user/aemo-etl/README.md)

### Rebuild a single service after a code change

```bash
podman-compose build aemo-etl
podman-compose up -d --no-build aemo-etl
```

For `dagster-core` changes (e.g. `dagster.local.yaml`):

```bash
podman-compose build dagster-webserver-admin dagster-webserver-guest dagster-daemon
podman rm -f dagster-webserver-admin dagster-webserver-guest dagster-daemon
podman-compose up -d --no-build dagster-webserver-admin dagster-webserver-guest dagster-daemon
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
> ```text
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
  localhost/dagster-local_dagster-webserver-admin:latest \
  localhost/dagster-local_dagster-webserver-guest:latest \
  localhost/dagster-local_dagster-daemon:latest \
  localhost/dagster-local_postgres:latest
```

After a full teardown the next `podman-compose up --build` starts from a clean
slate — postgres initialises a fresh database and LocalStack recreates the S3
buckets via `init-s3.sh`.

______________________________________________________________________

## Architecture notes

### Startup order

```text
postgres  ──(healthy)──► dagster-webserver-admin
                      ├─► dagster-webserver-guest
                      └─► dagster-daemon

localstack ──(healthy)──► aemo-etl-seed-localstack ──(completed)──► aemo-etl
                                                                  ├─► dagster-webserver-admin
                                                                  ├─► dagster-webserver-guest
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

The isolated `backend-services/scripts/aemo-etl-e2e run` path does not use that
developer-stack setting. It renders e2e Dagster config per run from the current
`XDG_RUNTIME_DIR` socket.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/compose.yaml`
  - `backend-services/.envrc`
  - `backend-services/localstack/init-s3.sh`
  - `backend-services/scripts/aemo-etl-e2e`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/e2e_archive_seed.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/maintenance/e2e_archive_seed.py`
  - `backend-services/dagster-core/dagster.local.yaml`
  - `backend-services/dagster-core/dagster.aws.yaml`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
