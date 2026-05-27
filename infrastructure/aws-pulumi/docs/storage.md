# Storage

This page documents the stateful data-plane resources used by the platform:
S3 buckets, the DynamoDB Delta locking table, and the PostgreSQL host used for
Dagster metadata.

## Table of contents

- [What this page covers](#what-this-page-covers)
- [Storage topology](#storage-topology)
- [Bucket roles](#bucket-roles)
- [Component summary](#component-summary)
- [Implementation notes](#implementation-notes)
- [Postgres root-volume resize operations](#postgres-root-volume-resize-operations)
- [Related docs](#related-docs)

## What this page covers

- `S3BucketsComponentResource`
- `DeltaLockingTableComponentResource`
- `PostgresComponentResource`

## Storage topology

```mermaid
flowchart LR
    subgraph ECS[Dagster runtime]
        UCODE[aemo-etl user code]
        WEB[Dagster webservers]
        DAEMON[Dagster daemon]
    end

    subgraph S3Buckets[S3 buckets]
        LANDING[landing]
        ARCHIVE[archive]
        AEMO[aemo]
        IOMANAGER[io-manager]
    end

    DDB[(DynamoDB delta_log)]
    PG[(PostgreSQL EC2)]
    SSM[SSM parameters]

    UCODE --> LANDING
    UCODE --> ARCHIVE
    UCODE --> AEMO
    UCODE --> IOMANAGER
    UCODE --> DDB
    DAEMON --> AEMO
    DAEMON --> IOMANAGER
    WEB --> PG
    UCODE --> PG
    DAEMON --> PG
    PG --> SSM
```

## Bucket roles

| Bucket suffix | Role |
|---|---|
| `-landing` | raw source landing zone |
| `-archive` | processed and archived source files |
| `-aemo` | Delta tables and lakehouse outputs |
| `-io-manager` | Dagster IO manager payloads and intermediates |

All bucket names are prefixed by `"{ENVIRONMENT}-energy-market"`.

## Component summary

| Component | Key resources | Purpose |
|---|---|---|
| `S3BucketsComponentResource` | 4 S3 buckets plus encryption, public-access-block, versioning, archive lifecycle | Host raw files, Delta tables, and Dagster intermediates |
| `DeltaLockingTableComponentResource` | 1 DynamoDB table named `delta_log` with TTL on `expireTime` | Distributed lock table for `delta-rs` |
| `PostgresComponentResource` | 1 private EC2 instance with encrypted 32 GiB `gp3` root volume, password generator, 2 SSM params | Dagster run, schedule, and event-log metadata |

## Implementation notes

- The archive bucket has lifecycle transitions to `GLACIER` after 30 days and
  `DEEP_ARCHIVE` after 180 days, with long-term expiration after 3650 days.
- The S3 and DynamoDB components both support adoption/import of existing
  retained resources through Pulumi config flags.
- The DynamoDB Delta locking table uses `tablePath` as the partition key,
  `fileName` as the sort key, `PAY_PER_REQUEST` billing, and `expireTime` as
  the TTL attribute for automatic lock metadata expiry.
- Postgres is provisioned on a private `t4g.nano` instance with IMDSv2
  required and encrypted 32 GiB `gp3` root storage. User data installs
  PostgreSQL 14, fetches the database password from SSM at boot, configures
  `scram-sha-256` password auth for the VPC CIDR, creates `dagster_user`, and
  creates the `dagster` database.
- Postgres writes two SSM parameters:
  - password as `SecureString` by default
  - password as SSM `String` only when
    `aws-pulumi:allow_dev_string_postgres_password_parameter=true` and the
    component name is exactly `dev-energy-market`
  - private DNS name as `String`
- ECS services consume the Postgres private DNS as a Pulumi output and the
  password as an ECS task secret backed by the SSM password parameter. The
  dev-only SSM `String` exception weakens at-rest protection for that dev
  password, but it does not move `DAGSTER_POSTGRES_PASSWORD` into plain
  container environment variables.

## Postgres root-volume resize operations

`PostgresComponentResource` declares a 32 GiB `gp3` root EBS volume. Component
tests check the Pulumi root-block-device config, and deployed tests check the
live EC2/EBS metadata for the `{resource_name}-postgres` root volume. That
metadata check proves the attached root EBS volume type and size, but it does
not prove the mounted Linux `/` filesystem has expanded to the same capacity.

After increasing `POSTGRES_ROOT_VOLUME_GIB` or recovering from a manual EBS
resize, operators must treat the Linux partition and filesystem as a separate
verification boundary:

1. Create or confirm a recent snapshot before changing the root volume.
1. Confirm the EBS volume modification is `optimizing` or `completed`.
1. Connect through an approved maintenance path for the private Postgres host,
   such as a reviewed temporary SSM/SSH access change or a helper instance flow
   for an offline root volume.
1. Identify the root mount and filesystem:

   ```bash
   findmnt -no SOURCE,FSTYPE,SIZE,USED,AVAIL,TARGET /
   lsblk -f
   df -hT /
   ```

1. If `/` is smaller than the EBS volume, extend the root partition first when
   the root device has a partition, for example `sudo growpart /dev/nvme0n1 1`
   on Nitro instances where `/` is mounted from `/dev/nvme0n1p1`.
1. Extend the filesystem with the tool that matches `findmnt` output: use
   `sudo xfs_growfs -d /` for XFS, or `sudo resize2fs <root-partition>` for
   ext4.
1. Re-run `df -hT /` and record the mounted filesystem size in the Operator
   workflow evidence.

The repo does not currently automate this mounted-filesystem check. Until a
read-only deployed check is added, `scripts/run-integration-tests
--with-idempotency` verifies only the EBS metadata target for the Postgres root
volume.

## Related docs

- [Connectivity](connectivity.md)
- [Identity and discovery](identity-and-discovery.md)
- [Runtime](runtime.md)
- [Edge and access](edge-and-access.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/components/s3_buckets.py`
  - `infrastructure/aws-pulumi/components/dynamodb.py`
  - `infrastructure/aws-pulumi/components/postgres.py`
  - `infrastructure/aws-pulumi/components/postgres_settings.py`
  - `infrastructure/aws-pulumi/Pulumi.dev-ausenergymarket.yaml`
  - `infrastructure/aws-pulumi/tests/component/test_postgres.py`
  - `infrastructure/aws-pulumi/tests/deployed/test_integration.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
