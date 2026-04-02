# AWS CDK to Pulumi Migration Plan

## Overview

This document is the authoritative specification for completing the migration of the
energy-market data-pipeline infrastructure from AWS CDK (Python) to Pulumi (Python).
It covers every resource that must be created, the dependency ordering, how to deploy
and validate each phase, and how to remediate common failures.

---

## 1. Current State

### 1.1 Already migrated (Pulumi)

| Component | File |
|-----------|------|
| VPC, subnets, IGW, FCK-NAT, route tables | `components/vpc.py` |
| Bastion-host security group + SSH ingress | `components/security_groups.py` |
| S3 buckets: io-manager, landing, archive, aemo | `components/s3_buckets.py` |
| ECR repository: dagster/postgres | `components/ecr.py` |
| IAM: bastion role + instance profile | `components/iam_roles.py` |
| Bastion host EC2 + EIP + SSM params | `components/bastion_host.py` |

### 1.2 Not yet migrated

| CDK module | Resources |
|-----------|-----------|
| `infrastructure/buckets.py` | S3 bronze, silver, gold buckets |
| `infrastructure/locking_table.py` | DynamoDB delta_log table |
| `infrastructure/postgres.py` | PostgreSQL EC2 (t4g.nano), key pair, SSM params |
| `infrastructure/security_groups.py` | DagsterWebService, DagsterUserCode, DagsterDaemon, DagsterPostgres, CaddyInstance, FastAPIAuthentication security groups |
| `infrastructure/service_discovery.py` | Cloud Map private DNS namespace `dagster` |
| `infrastructure/iam_roles.py` | ECS task execution/task roles for webserver and daemon |
| `infrastructure/ecs/cluster.py` | ECS Fargate cluster, CloudWatch log group |
| `infrastructure/ecr/` | ECR repos: webserver, daemon, user-code/aemo-etl, caddy, authentication |
| `infrastructure/ecs/dagster_user_code_service.py` | Fargate service: aemo-etl user code |
| `infrastructure/ecs/dagster_webserver_service.py` | Fargate service: webserver-admin, webserver-guest |
| `infrastructure/ecs/dagster_daemon_service.py` | Fargate service: daemon |
| `infrastructure/fastapi_authentication_server.py` | FastAPI auth EC2 (t3.nano) |
| `infrastructure/caddy_server.py` | Caddy EC2 (t3.nano), EBS volume, EIP, Route 53 A-record |

---

## 2. Target Architecture

```
VPC (10.0.0.0/16)
├── Public subnet (10.0.0.0/24)
│   ├── FCK-NAT instance (t4g.nano)
│   ├── Bastion host (t3.nano) + EIP
│   └── Caddy reverse-proxy (t3.nano) + EIP + EBS cert volume
└── Private subnet (10.0.1.0/24)
    ├── FastAPI authentication server (t3.nano)
    ├── PostgreSQL server (t4g.nano ARM)
    └── ECS Fargate cluster
        ├── dagster-user-code-aemo-etl  (FARGATE_SPOT)
        ├── dagster-webserver-admin      (FARGATE_SPOT)
        ├── dagster-webserver-guest      (FARGATE_SPOT)
        └── dagster-daemon               (FARGATE_SPOT)

Storage
├── S3: io-manager, landing, archive (Glacier lifecycle), aemo
├── S3: bronze, silver, gold          ← NEW
└── DynamoDB: delta_log               ← NEW

Service discovery: Cloud Map namespace "dagster"
  ├── aemo-etl          → port 4000
  ├── webserver-admin   → port 3000
  └── webserver-guest   → port 3000

ECR repositories
  ├── <env>-energy-market/dagster/postgres  (existing)
  ├── <env>-energy-market/dagster/webserver
  ├── <env>-energy-market/dagster/daemon
  ├── <env>-energy-market/dagster/user-code/aemo-etl
  ├── <env>-energy-market/dagster/caddy
  └── <env>-energy-market/dagster/authentication
```

---

## 3. New Pulumi Component Files

| New file | Purpose |
|----------|---------|
| `components/dynamodb.py` | DeltaLockingTableComponentResource |
| `components/postgres.py` | PostgresComponentResource |
| `components/service_discovery.py` | ServiceDiscoveryComponentResource |
| `components/ecs_cluster.py` | EcsClusterComponentResource |
| `components/ecs_services.py` | Dagster Fargate services |
| `components/fastapi_auth.py` | FastAPIAuthComponentResource |
| `components/caddy.py` | CaddyServerComponentResource |

The existing files are extended as follows:

| Existing file | Changes |
|---------------|---------|
| `components/s3_buckets.py` | Add bronze, silver, gold buckets |
| `components/security_groups.py` | Add all Dagster + Caddy + FastAPI security groups |
| `components/iam_roles.py` | Add ECS task execution / task roles |
| `components/ecr.py` | Add webserver, daemon, user-code/aemo-etl, caddy, auth repos |
| `__main__.py` | Instantiate every new component in dependency order |

---

## 4. Resource Specifications

### 4.1 S3 – Bronze / Silver / Gold

- Bucket names: `{env}-energy-market-bronze`, `…-silver`, `…-gold`
- Encryption: AES256 (S3 managed)
- Versioning: Disabled
- Public access: Blocked
- Lifecycle: None (data lake tiers managed by application)
- Retain on delete: True

### 4.2 DynamoDB – delta_log

- Table name: `delta_log`
- Partition key: `tablePath` (String)
- Sort key: `fileName` (String)
- Billing: PAY_PER_REQUEST
- Deletion: retain (protect live data)

### 4.3 PostgreSQL EC2

- Instance type: `t4g.nano` (ARM)
- AMI: Amazon Linux 2 ARM64
- Subnet: private
- Key pair: ED25519, stored in SSM
- Security group: `DagsterPostgresSecurityGroup`
- IAM role: EC2 with AmazonEC2ReadOnlyAccess
- User data: installs PostgreSQL 14, creates `dagster` DB and `dagster_user` user
- SSM parameters:
  - `/{name}/dagster/postgres/password` (SecureString, auto-generated)
  - `/{name}/dagster/postgres/instance_private_dns`

### 4.4 Security Groups (additions)

| Name | Inbound rules |
|------|---------------|
| `dagster-webserver` | TCP 3000 from bastion, caddy |
| `dagster-user-code` | TCP 4000 from daemon, webserver |
| `dagster-daemon` | (no inbound required) |
| `dagster-postgres` | TCP 5432 from user-code, webserver, daemon |
| `caddy-instance` | TCP 22 from admin IPs; TCP 80, 443 from 0.0.0.0/0 |
| `fastapi-auth` | TCP 8000 from caddy; TCP 22 from bastion |

All security groups: egress allow-all 0.0.0.0/0.

### 4.5 Cloud Map

- Namespace name: `dagster`
- Type: private DNS, attached to the VPC

### 4.6 IAM – ECS roles

**Webserver execution role**
- Managed policy: `AmazonECSTaskExecutionRolePolicy`

**Webserver task role**
- `ecs:DescribeTasks`, `ecs:StopTask` on `*`
- `iam:PassRole` (condition: `ecs-tasks.amazonaws.com`) on `*`

**Daemon execution role**
- Managed policy: `AmazonECSTaskExecutionRolePolicy`
- `ssm:GetParameters` on `*`

**Daemon task role**
- EC2/ECS orchestration actions on `*`
- DynamoDB CRUD on `arn:aws:dynamodb:…:table/delta_log`
- S3 CRUD on `arn:aws:s3:::{env}-energy-market*`
- `iam:PassRole` (condition: `ecs-tasks.amazonaws.com`) on `*`

### 4.7 ECS Cluster

- Cluster name: `{name}-dagster-cluster`
- Capacity providers: FARGATE, FARGATE_SPOT
- CloudWatch log group: `/ecs/{name}-dagster-cluster`, retention 1 day

### 4.8 ECR Repositories

Repos added (all: mutable tags, keep 5 images lifecycle policy):

- `{name}/dagster/webserver`
- `{name}/dagster/daemon`
- `{name}/dagster/user-code/aemo-etl`
- `{name}/dagster/caddy`
- `{name}/dagster/authentication`

### 4.9 Fargate Services

All services use:
- `FARGATE_SPOT` capacity provider (weight 1)
- Private subnet placement
- Circuit-breaker with rollback enabled
- `min_healthy_percent=0`, `max_healthy_percent=100`
- Tags: `dagster/service`, `dagster/job_name`

#### dagster-user-code-aemo-etl

- Task family: `dagster-user-code-aemo-etl`
- CPU: 256, Memory: 1024 MiB
- Task role: daemon task role
- Container: image from `dagster/user-code/aemo-etl`
- Entry point: `dagster api grpc -h 0.0.0.0 -p 4000 -m aemo_etl.definitions`
- Port: 4000
- Cloud Map: name `aemo-etl`
- Security group: `dagster-user-code`

#### dagster-webserver-admin

- Task family: `dagster-webserver`
- CPU: 512, Memory: 1024 MiB
- Execution role: webserver execution role
- Task role: webserver task role
- Entry point: `dagster-webserver -h 0.0.0.0 -p 3000 -w workspace.yaml --path-prefix /dagster-webserver/admin`
- Port: 3000
- Cloud Map: name `webserver-admin`
- Security group: `dagster-webserver`

#### dagster-webserver-guest

- Same as admin with `--read-only` flag and Cloud Map name `webserver-guest`

#### dagster-daemon

- Task family: `dagster-daemon`
- CPU: 256, Memory: 1024 MiB
- Execution role: daemon execution role
- Task role: daemon task role
- Entry point: `dagster-daemon run`
- No port mapping, no Cloud Map
- Security group: `dagster-daemon`

All Fargate containers share these env vars (resolved at deploy time):

```
DAGSTER_POSTGRES_DB=dagster
DAGSTER_POSTGRES_HOSTNAME=<SSM param>
DAGSTER_POSTGRES_USER=dagster_user
DAGSTER_POSTGRES_PASSWORD=<SSM SecureString>
DEVELOPMENT_ENVIRONMENT={env}
DEVELOPMENT_LOCATION=aws
AWS_S3_LOCKING_PROVIDER=dynamodb        # user-code + daemon only
DAGSTER_GRPC_TIMEOUT_SECONDS=300        # user-code + daemon only
```

### 4.10 FastAPI Authentication Server

- Instance type: `t3.nano`
- AMI: Amazon Linux 2023
- Subnet: private
- Security group: `fastapi-auth`
- IAM role: `AmazonEC2ContainerRegistryPullOnly`
- Key pair: ED25519
- User data: installs Docker, pulls `dagster/authentication:latest`, runs on port 8000
- Env vars passed to container via `pulumi.Config` secrets:
  - `COGNITO_DAGSTER_AUTH_CLIENT_ID`
  - `COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL`
  - `COGNITO_TOKEN_SIGNING_KEY_URL`
  - `COGNITO_DAGSTER_AUTH_CLIENT_SECRET`
  - `WEBSITE_ROOT_URL`

### 4.11 Caddy Server

- Instance type: `t3.nano`
- AMI: Amazon Linux 2023
- Subnet: public
- Security group: `caddy-instance`
- IAM role: `AmazonEC2ContainerRegistryPullOnly`
- Key pair: ED25519
- EIP: associated to instance
- EBS volume: 1 GiB GP3 encrypted, mounted at `/mnt/caddy-certs`
- Route 53 A-record: `ausenergymarketdata.com` → EIP
- User data: installs Docker, mounts EBS, pulls and runs `dagster/caddy:latest`
- SSM parameters:
  - `/{name}/dagster/caddy-server/instance-id`
  - `/{name}/dagster/caddy-server/key-pair-id`
- Env vars for container (from `pulumi.Config`):
  - `ROOT_DNS=ausenergymarketdata.com`
  - `DEVELOPER_EMAIL`
  - `DAGSTER_AUTHSERVER={fastapi_private_ip}:8000`
  - `DAGSTER_WEBSERVER_ADMIN=webserver-admin.dagster:3000`
  - `DAGSTER_WEBSERVER_GUEST=webserver-guest.dagster:3000`

---

## 5. Deployment Process

### 5.1 Prerequisites

```bash
# 1. Install Pulumi CLI
curl -fsSL https://get.pulumi.com | sh

# 2. Configure AWS credentials
export AWS_PROFILE=<your-profile>
# or
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=ap-southeast-2

# 3. Set required Pulumi config secrets
cd infrastructure/aws-pulumi
pulumi stack select dev-ausenergymarket

pulumi config set --secret cognito_client_id        <value>
pulumi config set --secret cognito_server_metadata_url <value>
pulumi config set --secret cognito_token_signing_key_url <value>
pulumi config set --secret cognito_client_secret    <value>
pulumi config set         website_root_url          https://ausenergymarketdata.com
pulumi config set         developer_email           <your-email>
```

### 5.2 Phased deployment commands

Always preview before applying:

```bash
# Preview all changes
pulumi preview

# Deploy a named resource type (phase-by-phase)
pulumi up --target-dependents \
  --target 'urn:pulumi:dev-ausenergymarket::aws-pulumi::*DeltaLocking*'
```

Recommended deploy order (each `pulumi up` deploys cumulative state):

```
Phase 1  →  S3 data-lake tiers  +  DynamoDB
Phase 2  →  Security groups (all)
Phase 3  →  IAM (ECS roles)
Phase 4  →  Service Discovery
Phase 5  →  PostgreSQL EC2
Phase 6  →  ECS Cluster  +  ECR repos
Phase 7  →  FastAPI auth server
Phase 8  →  Caddy server
Phase 9  →  ECS Fargate services (user-code first, then webservers, then daemon)
```

Full deploy (after all components are coded and tested):

```bash
pulumi up --yes
```

### 5.3 Environment variables required at runtime

```
DEVELOPMENT_LOCATION=aws       # triggers admin IP lookup from config, not HTTP
ADMINISTRATOR_IPS="x.x.x.x"   # space-separated list, used if DEVELOPMENT_LOCATION=aws
ENVIRONMENT=dev
```

---

## 6. Testing Strategy

### 6.1 Pre-deployment checks (static)

```bash
# Lint / type-check Pulumi code
cd infrastructure/aws-pulumi
uv run ruff check .
uv run pyright .

# Dry-run preview (no AWS calls mutated)
pulumi preview --diff
```

### 6.2 Post-phase smoke tests

After each `pulumi up` phase:

| Phase | Test |
|-------|------|
| S3 | `aws s3 ls | grep energy-market` – expect bronze/silver/gold |
| DynamoDB | `aws dynamodb describe-table --table-name delta_log` |
| Security groups | `aws ec2 describe-security-groups --filters Name=group-name,Values="*dagster*"` |
| Postgres | SSH via bastion → `psql -h <private_dns> -U dagster_user -d dagster` |
| ECS cluster | `aws ecs describe-clusters --clusters {name}-dagster-cluster` |
| Service discovery | `aws servicediscovery list-namespaces` – expect `dagster` |
| FastAPI auth | SSH via bastion → `curl http://<private_ip>:8000/health` → `200 OK` |
| Caddy | `curl https://ausenergymarketdata.com` → proxy response |
| Dagster services | Dagster UI accessible at `https://ausenergymarketdata.com/dagster-webserver/admin` |

### 6.3 Integration / end-to-end tests

1. **Pipeline execution**: trigger a Dagster job from the admin UI; confirm it runs and writes to an S3 bronze bucket.
2. **Delta Lake locking**: confirm the `delta_log` DynamoDB table receives items during a job run.
3. **Authentication flow**: open the guest UI; confirm Cognito redirect and successful login.
4. **Log delivery**: confirm CloudWatch log group `/ecs/{name}-dagster-cluster` receives entries from all four services.

### 6.4 Rollback test

1. Destroy a single resource with `pulumi destroy --target <urn>`.
2. Re-apply with `pulumi up`.
3. Verify service recovers automatically.

---

## 7. Remediation Guide

### 7.1 Resource already exists (state drift)

**Symptom**: `pulumi up` errors with "resource already exists".

**Fix**:
```bash
pulumi import aws:<type>:<resource> <pulumi-name> <aws-id>
# e.g. for an existing S3 bucket:
pulumi import aws:s3/bucket:Bucket dev-energy-market-bronze dev-energy-market-bronze
```

### 7.2 IAM permission errors on ECS task start

**Symptom**: ECS task stops immediately; CloudWatch shows `CannotPullContainerError` or `AccessDenied`.

**Fix**:
1. Check task execution role has `AmazonECSTaskExecutionRolePolicy`.
2. Check ECR repo policy allows the account's task execution role.
3. Run: `aws iam simulate-principal-policy --policy-source-arn <role-arn> --action-names ecr:GetAuthorizationToken ecr:BatchGetImage`.

### 7.3 Fargate tasks fail health checks

**Symptom**: Service stays in ACTIVATING, tasks are repeatedly replaced.

**Fix**:
1. Open CloudWatch Logs → confirm container actually starts.
2. Check security group: Dagster webserver needs port 3000 open from the load balancer / Caddy.
3. If Postgres is unreachable, confirm SSM parameter `postgres/instance_private_dns` is populated and the postgres security group allows TCP 5432.

### 7.4 Service discovery DNS not resolving

**Symptom**: `aemo-etl.dagster` not resolving from webserver container.

**Fix**:
1. Confirm Cloud Map namespace is attached to the VPC (`aws servicediscovery list-namespaces`).
2. Confirm ECS service has `cloud_map_options` referencing correct namespace and service name.
3. From the bastion host: `nslookup aemo-etl.dagster 169.254.169.253`.

### 7.5 Caddy certificate errors

**Symptom**: HTTPS shows untrusted certificate or Caddy fails to start.

**Fix**:
1. Confirm EBS volume is mounted: `ssh caddy-ec2 "ls /mnt/caddy-certs/data"`.
2. Confirm EIP is associated with the instance and Route 53 A-record points to it.
3. Confirm TCP 80 + 443 are open in the Caddy security group (ACME HTTP-01 challenge).

### 7.6 PostgreSQL not accessible

**Symptom**: ECS tasks cannot connect to Postgres.

**Fix**:
1. Verify SSM parameter `/{name}/dagster/postgres/instance_private_dns` is a non-empty string.
2. SSH via bastion → `psql -h <dns> -U dagster_user -d dagster -W`.
3. Verify security group `dagster-postgres` allows TCP 5432 from the ECS security groups.
4. Verify PostgreSQL `pg_hba.conf` allows `md5` auth from `0.0.0.0/0` (set by user data).

### 7.7 EBS volume not attached to Caddy

**Symptom**: Caddy user-data script loops forever waiting for `/dev/sdf`.

**Fix**:
1. In AWS Console → EC2 → Volumes → confirm attachment to the Caddy instance.
2. In Pulumi: confirm `aws.ec2.VolumeAttachment` resource is present in the state.
3. The Caddy EC2 instance must be in the **same AZ** as the volume; both use `vpc.availability_zone`.

---

## 8. Post-Migration Cleanup

Once Pulumi infrastructure is validated in production:

1. Run `cdk destroy --all` in `infrastructure/aws-legacy/` to delete CDK-managed stacks.
2. Remove CDK bootstrap resources if no other CDK project uses them.
3. Archive `infrastructure/aws-legacy/` (keep for reference; do not delete immediately).
4. Update CI/CD pipelines to use `pulumi up` instead of `cdk deploy`.
5. Update team runbooks and architecture diagrams.

---

## 9. File Map – CDK → Pulumi

| CDK file | Pulumi file |
|----------|-------------|
| `infrastructure/buckets.py` (bronze/silver/gold) | `components/s3_buckets.py` |
| `infrastructure/locking_table.py` | `components/dynamodb.py` |
| `infrastructure/postgres.py` | `components/postgres.py` |
| `infrastructure/security_groups.py` (new groups) | `components/security_groups.py` |
| `infrastructure/service_discovery.py` | `components/service_discovery.py` |
| `infrastructure/iam_roles.py` (ECS roles) | `components/iam_roles.py` |
| `infrastructure/ecs/cluster.py` | `components/ecs_cluster.py` |
| `infrastructure/ecr/{webserver,daemon,caddy,auth,user_code/}` | `components/ecr.py` |
| `infrastructure/ecs/dagster_*_service.py` | `components/ecs_services.py` |
| `infrastructure/fastapi_authentication_server.py` | `components/fastapi_auth.py` |
| `infrastructure/caddy_server.py` | `components/caddy.py` |
| `app.py` orchestration | `__main__.py` |

---

*Document version: 1.0 — generated as part of the CDK → Pulumi migration.*
