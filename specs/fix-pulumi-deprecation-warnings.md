# Fix Pulumi Deprecation Warnings & Automated Test Suite

## Overview

This document is the authoritative specification for:

1. Fixing all deprecation warnings emitted during `pulumi preview`
2. Establishing a pytest-based automated test suite covering all 14 Pulumi components
3. Defining post-deployment integration tests to verify the live system

---

## 1. Deprecation Warnings Analysis

Running `pulumi preview` produces **13 warning instances** across **2 categories**:

### 1.1 `name is deprecated. Use region instead.` (10 occurrences)

**Root cause:** The `GetRegionResult` object returned by `aws.get_region()` has a `.name`
property decorated with `@deprecated`. The replacement is `.region`. Every call-site that
accesses `result.name` triggers the warning through the `@_utilities.deprecated` decorator
in `pulumi_aws._utilities`.

**Affected files and lines:**

| File | Line | Current | Fix |
|------|------|---------|-----|
| `components/ecs_services.py` | 153 | `region=aws.get_region().name` | `region=aws.get_region().region` |
| `components/ecs_services.py` | 301 | `region=aws.get_region().name` | `region=aws.get_region().region` |
| `components/ecs_services.py` | 413 | `region=aws.get_region().name` | `region=aws.get_region().region` |
| `components/iam_roles.py` | 173 | `region=region.name` | `region=region.region` |
| `components/fastapi_auth.py` | 115 | `region=region.name` | `region=region.region` |
| `components/caddy.py` | 140 | `region=region.name` | `region=region.region` |
| `components/ecr.py` | 66 | `aws.get_region()` (result discarded) | Remove dead call |

### 1.2 `failure_threshold is deprecated` (3 occurrences)

**Root cause:** `aws.servicediscovery.ServiceHealthCheckCustomConfigArgs(failure_threshold=1)`
passes a parameter that AWS no longer supports. The provider always sets it to 1 internally.
The warning fires once per `aws.servicediscovery.Service` resource that receives this argument —
one for each of the three Cloud Map-registered Fargate services (user-code, webserver-admin,
webserver-guest).

**Affected file:**

| File | Lines | Current | Fix |
|------|-------|---------|-----|
| `components/ecs_services.py` | 52–54 | `ServiceHealthCheckCustomConfigArgs(failure_threshold=1)` | `ServiceHealthCheckCustomConfigArgs()` |

---

## 2. Code Changes

### 2.1 `components/ecs_services.py`

Four edits required:

**Edit A — remove `failure_threshold` (lines 52–54):**
```python
# Before
health_check_custom_config=aws.servicediscovery.ServiceHealthCheckCustomConfigArgs(
    failure_threshold=1,
),

# After
health_check_custom_config=aws.servicediscovery.ServiceHealthCheckCustomConfigArgs(),
```

**Edits B, C, D — use `.region` instead of `.name` (lines 153, 301, 413):**
```python
# Before
region=aws.get_region().name,

# After
region=aws.get_region().region,
```

### 2.2 `components/iam_roles.py`

```python
# Before (line 173)
region=region.name,

# After
region=region.region,
```

### 2.3 `components/fastapi_auth.py`

```python
# Before (line 115)
region=region.name,

# After
region=region.region,
```

### 2.4 `components/caddy.py`

```python
# Before (line 140)
region=region.name,

# After
region=region.region,
```

### 2.5 `components/ecr.py`

Remove the dead call at line 66:
```python
# Before
token = aws.ecr.get_authorization_token_output()
aws.get_region()   # ← remove this line

# After
token = aws.ecr.get_authorization_token_output()
```

---

## 3. Code Quality Verification

After applying all code changes, run the full pre-commit hook suite and a dry-run preview:

```bash
# Stage all changes
git add .

# Run all pre-commit hooks across all files
prek run -a
```

This executes, in order:

| Hook | Tool | What it checks |
|------|------|----------------|
| `trailing-whitespace` | pre-commit-hooks | No trailing spaces |
| `end-of-file-fixer` | pre-commit-hooks | Files end with newline |
| `check-yaml` | pre-commit-hooks | Valid YAML syntax |
| `check-added-large-files` | pre-commit-hooks | No accidental large file commits |
| `pyproject-fmt` | tox-dev/pyproject-fmt | Canonical pyproject.toml formatting |
| `ruff-check` | ruff | Lint rules: ANN, E, F, I (line length 200) |
| `ruff-format` | ruff | Code formatting |
| `zuban-check` | zuban | Type checking (strict mode) |
| `pytest` | pytest | Unit test suite (see section 4) |

Then verify the preview is clean:

```bash
pulumi preview
# Expected: "0 warnings" — no `name is deprecated` or `failure_threshold is deprecated`
```

---

## 4. Automated Test Suite

### 4.1 Project setup

Add to `pyproject.toml`:

```toml
[dependency-groups]
dev = [
  "pyproject-fmt>=2.20",
  "pytest>=9.0.2",
  "pytest-cov>=7",
  "pytest-mock>=3.15.1",
  "ruff>=0.15.8",
  "zuban>=0.6.2",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
  "integration: post-deployment integration tests (requires live AWS environment)",
]
```

Add to `.pre-commit-config.yaml` (local hooks section):

```yaml
- id: pytest
  name: pytest unit tests
  language: system
  entry: uv run pytest tests/ -x -q --ignore=tests/test_integration.py
  pass_filenames: false
  always_run: true
```

Install new dependencies:

```bash
uv sync
```

### 4.2 Test directory layout

```
infrastructure/aws-pulumi/
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Shared Pulumi mock infrastructure + env setup
    ├── test_vpc.py
    ├── test_security_groups.py
    ├── test_iam_roles.py
    ├── test_s3_buckets.py
    ├── test_dynamodb.py
    ├── test_ecr.py
    ├── test_service_discovery.py
    ├── test_postgres.py
    ├── test_bastion_host.py
    ├── test_ecs_cluster.py
    ├── test_ecs_services.py         # Fargate connectivity assertions
    ├── test_fastapi_auth.py
    ├── test_caddy.py
    ├── test_deprecation_warnings.py # Zero-warning regression guard
    └── test_integration.py          # Post-deployment integration tests
```

### 4.3 `tests/conftest.py` design

The conftest establishes the Pulumi mocking environment **before any component module is
imported**, following the same "env-vars-first" pattern used in `backend-services/`.

```python
import os
import warnings
import pulumi
import pulumi.runtime

# 1. Environment variables MUST be set before configs.py is imported
os.environ.setdefault("ADMINISTRATOR_IPS", "10.0.0.1")
os.environ.setdefault("ENVIRONMENT", "test")

class InfrastructureMocks(pulumi.runtime.Mocks):
    """Intercepts all provider calls and resource registrations."""

    def call(self, args: pulumi.runtime.MockCallArgs):
        """Handle provider function calls (data sources)."""
        token = args.token
        if token == "aws:index/getRegion:getRegion":
            return {"id": "ap-southeast-2", "region": "ap-southeast-2", "description": "Asia Pacific (Sydney)"}
        if token == "aws:index/getAvailabilityZones:getAvailabilityZones":
            return {"id": "ap-southeast-2", "names": ["ap-southeast-2a", "ap-southeast-2b"], "zoneIds": ["apse2-az1", "apse2-az2"]}
        if token == "aws:index/getCallerIdentity:getCallerIdentity":
            return {"accountId": "123456789012", "arn": "arn:aws:iam::123456789012:user/test", "id": "123456789012", "userId": "AKIAIOSFODNN7EXAMPLE"}
        if token == "aws:ec2/getAmi:getAmi":
            return {"id": "ami-0test1234", "imageId": "ami-0test1234", "architecture": "x86_64", "name": "amzn2-ami-hvm-2.0.0-x86_64-gp2"}
        if token == "aws:ecr/getAuthorizationToken:getAuthorizationToken":
            return {"id": "ap-southeast-2", "authorizationToken": "dGVzdA==", "proxyEndpoint": "https://123456789012.dkr.ecr.ap-southeast-2.amazonaws.com", "password": "test-password", "userName": "AWS"}
        if token == "aws:ec2/getAvailabilityZone:getAvailabilityZone":
            return {"id": "ap-southeast-2a", "name": "ap-southeast-2a", "zoneName": "ap-southeast-2a", "zoneId": "apse2-az1", "state": "available"}
        return {}

    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        """Return a mock ID and pass inputs through as outputs."""
        return (f"{args.name}-id", args.inputs)

# 2. Install mocks at module scope (runs once per test session)
pulumi.runtime.set_mocks(
    InfrastructureMocks(),
    project="aws-pulumi",
    stack="test",
    preview=False,
)

# 3. Set all config values required by components
pulumi.runtime.set_all_config({
    "aws-pulumi:cognito_client_id": "test-cognito-client-id",
    "aws-pulumi:cognito_server_metadata_url": "https://cognito.test.example.com/.well-known/openid-configuration",
    "aws-pulumi:cognito_token_signing_key_url": "https://cognito.test.example.com/.well-known/jwks.json",
    "aws-pulumi:cognito_client_secret": "test-cognito-client-secret",
    "aws-pulumi:website_root_url": "https://test.ausenergymarketdata.com",
    "aws-pulumi:developer_email": "test@example.com",
})
```

### 4.4 Unit test specifications

All unit tests use the `@pulumi.runtime.test` decorator to await `pulumi.Output` values.

---

#### `test_vpc.py`

| Test | Assertion |
|------|-----------|
| `test_vpc_cidr_block` | VPC CIDR block is `10.0.0.0/16` |
| `test_vpc_dns_enabled` | VPC has `enable_dns_hostnames=True` and `enable_dns_support=True` |
| `test_public_subnet_cidr` | Public subnet CIDR is `10.0.0.0/24` |
| `test_private_subnet_cidr` | Private subnet CIDR is `10.0.1.0/24` |
| `test_nat_instance_type` | fck-nat EC2 instance type is `t4g.nano` |
| `test_nat_key_pair_created` | `fk_nat_key_pair` is created |
| `test_internet_gateway_created` | `internet_gateway` resource exists |
| `test_route_tables_created` | Both `public_route_table` and `private_route_table` exist |
| `test_resource_naming` | All resources use `{name}-` prefix |

---

#### `test_security_groups.py`

| Test | Assertion |
|------|-----------|
| `test_all_security_groups_created` | `register` has all 7 SG attributes non-None |
| `test_bastion_sg_name` | Bastion SG resource name contains `bastion-host-sg` |
| `test_dagster_webserver_sg_name` | Webserver SG resource name contains `dagster-webserver-sg` |
| `test_dagster_user_code_sg_name` | User-code SG resource name contains `dagster-user-code-sg` |
| `test_dagster_daemon_sg_name` | Daemon SG resource name contains `dagster-daemon-sg` |
| `test_dagster_postgres_sg_name` | Postgres SG resource name contains `dagster-postgres-sg` |
| `test_caddy_sg_name` | Caddy SG resource name contains `caddy-instance-sg` |
| `test_fastapi_auth_sg_name` | FastAPI SG resource name contains `fastapi-auth-sg` |

---

#### `test_iam_roles.py`

| Test | Assertion |
|------|-----------|
| `test_bastion_profile_created` | `bastion_profile` is not None |
| `test_webserver_execution_role_created` | `webserver_execution_role` is not None |
| `test_daemon_execution_role_created` | `daemon_execution_role` is not None |
| `test_webserver_task_role_created` | `webserver_task_role` is not None |
| `test_daemon_task_role_created` | `daemon_task_role` is not None |
| `test_ecs_trust_policy` | All ECS roles assume `ecs-tasks.amazonaws.com` |
| `test_no_region_name_deprecation` | No `DeprecationWarning` raised during instantiation |

---

#### `test_s3_buckets.py`

| Test | Assertion |
|------|-----------|
| `test_seven_buckets_created` | All 7 bucket attributes are non-None |
| `test_io_manager_bucket_name` | `io_manager_bucket` resource contains `io-manager` |
| `test_landing_bucket_name` | `landing` bucket resource contains `landing` |
| `test_archive_bucket_name` | `archive` bucket resource contains `archive` |
| `test_aemo_bucket_name` | `aemo` bucket resource contains `aemo` |
| `test_bronze_bucket_name` | `bronze` bucket resource contains `bronze` |
| `test_silver_bucket_name` | `silver` bucket resource contains `silver` |
| `test_gold_bucket_name` | `gold` bucket resource contains `gold` |

---

#### `test_dynamodb.py`

| Test | Assertion |
|------|-----------|
| `test_table_name` | Table name is `delta_log` |
| `test_billing_mode` | Billing mode is `PAY_PER_REQUEST` |
| `test_hash_key` | Hash key attribute is `tablePath` of type `S` |
| `test_range_key` | Range key attribute is `fileName` of type `S` |

---

#### `test_ecr.py`

| Test | Assertion |
|------|-----------|
| `test_six_repos_created` | All 6 repo attributes are non-None |
| `test_postgres_repo_name` | Contains `dagster-postgres` |
| `test_webserver_repo_name` | Contains `dagster-webserver` |
| `test_daemon_repo_name` | Contains `dagster-daemon` |
| `test_user_code_repo_name` | Contains `dagster-user-code-aemo-etl` |
| `test_caddy_repo_name` | Contains `dagster-caddy` |
| `test_authentication_repo_name` | Contains `dagster-authentication` |
| `test_no_dead_get_region_call` | No `DeprecationWarning` raised during instantiation |

---

#### `test_service_discovery.py`

| Test | Assertion |
|------|-----------|
| `test_namespace_created` | `namespace` is not None |
| `test_namespace_name` | Namespace name is `dagster` |

---

#### `test_postgres.py`

| Test | Assertion |
|------|-----------|
| `test_instance_created` | `instance` is not None |
| `test_instance_type` | Instance type is `t4g.nano` |
| `test_ssm_password_param_name` | `ssm_param_password_name` matches `/{name}/dagster/postgres/password` |
| `test_ssm_dns_param_name` | `ssm_param_private_dns_name` matches `/{name}/dagster/postgres/instance_private_dns` |
| `test_private_dns_output` | `private_dns` Output is not None |
| `test_password_output` | `password` Output is not None |

---

#### `test_bastion_host.py`

| Test | Assertion |
|------|-----------|
| `test_instance_created` | `instance` is not None |
| `test_instance_type` | Instance type is `t3.nano` |
| `test_key_pair_created` | `key_pair` is not None |
| `test_eip_created` | `eip` is not None |
| `test_private_key_algorithm` | `private_key` algorithm is `ED25519` |

---

#### `test_ecs_cluster.py`

| Test | Assertion |
|------|-----------|
| `test_cluster_created` | `cluster` is not None |
| `test_log_group_created` | `log_group` is not None |
| `test_log_group_retention` | Log group retention is `1` day |
| `test_cluster_name_contains_dagster` | Cluster resource name contains `dagster-cluster` |

---

#### `test_ecs_services.py` (Fargate Connectivity)

This is the most important test file — it verifies that all four Fargate services are
correctly wired to communicate with each other via Cloud Map service discovery.

| Test | Assertion |
|------|-----------|
| `test_user_code_service_created` | `DagsterUserCodeServiceComponentResource.service` is not None |
| `test_user_code_cloud_map_name` | `_fargate_service` called with `cloud_map_name="aemo-etl"` |
| `test_user_code_port_mapping` | Container port 4000 in task definition |
| `test_user_code_entry_point` | Entry point contains `grpc`, `-p`, `4000`, `-m`, `aemo_etl.definitions` |
| `test_user_code_fargate_spot` | Capacity provider strategy uses `FARGATE_SPOT` |
| `test_user_code_circuit_breaker` | `deployment_circuit_breaker.enable=True`, `rollback=True` |
| `test_user_code_private_subnet` | Network config uses private subnet (not public) |
| `test_user_code_no_public_ip` | `assign_public_ip=False` |
| `test_webserver_admin_cloud_map_name` | `cloud_map_name="webserver-admin"` |
| `test_webserver_admin_port_mapping` | Container port 3000 in task definition |
| `test_webserver_admin_path_prefix` | Entry point contains `/dagster-webserver/admin` |
| `test_webserver_admin_not_readonly` | Entry point does NOT contain `--read-only` |
| `test_webserver_guest_cloud_map_name` | `cloud_map_name="webserver-guest"` |
| `test_webserver_guest_port_mapping` | Container port 3000 in task definition |
| `test_webserver_guest_path_prefix` | Entry point contains `/dagster-webserver/guest` |
| `test_webserver_guest_readonly` | Entry point contains `--read-only` |
| `test_daemon_no_cloud_map` | Daemon service has no Cloud Map registration |
| `test_daemon_no_port_mapping` | Daemon task definition has no port mappings |
| `test_daemon_entry_point` | Entry point is `["dagster-daemon", "run"]` |
| `test_service_discovery_namespace_used` | User-code and webserver services pass `namespace_id` |
| `test_all_services_same_cluster` | All 4 services reference same cluster ARN |
| `test_all_services_private_subnet` | All 4 services use same private subnet ID |
| `test_no_failure_threshold_deprecation` | No `DeprecationWarning` from `failure_threshold` |
| `test_no_name_deprecation_in_ecs_services` | No `DeprecationWarning` from `.name` on region |

---

#### `test_fastapi_auth.py`

| Test | Assertion |
|------|-----------|
| `test_instance_created` | `instance` is not None |
| `test_instance_type` | Instance type is `t3.nano` |
| `test_no_region_name_deprecation` | No `DeprecationWarning` raised during instantiation |

---

#### `test_caddy.py`

| Test | Assertion |
|------|-----------|
| `test_instance_created` | `instance` is not None |
| `test_instance_type` | Instance type is `t3.nano` |
| `test_eip_created` | `eip` is not None |
| `test_no_region_name_deprecation` | No `DeprecationWarning` raised during instantiation |

---

#### `test_deprecation_warnings.py` (Zero-warning regression guard)

This file is the definitive regression guard. It captures Python `DeprecationWarning`
and Pulumi log warnings during a full stack instantiation of all components and asserts
none are emitted.

| Test | Assertion |
|------|-----------|
| `test_no_deprecation_warnings_vpc` | `VpcComponentResource` emits zero `DeprecationWarning` |
| `test_no_deprecation_warnings_iam_roles` | `IamRolesComponentResource` emits zero `DeprecationWarning` |
| `test_no_deprecation_warnings_ecr` | `ECRComponentResource` emits zero `DeprecationWarning` |
| `test_no_deprecation_warnings_ecs_services` | All 3 ECS service components emit zero `DeprecationWarning` |
| `test_no_deprecation_warnings_fastapi_auth` | `FastAPIAuthComponentResource` emits zero `DeprecationWarning` |
| `test_no_deprecation_warnings_caddy` | `CaddyServerComponentResource` emits zero `DeprecationWarning` |

---

### 4.5 Integration Tests (`test_integration.py`)

Integration tests run **post-`pulumi up`** against the live AWS environment. They are
skipped by default and must be explicitly opted-in with the `--run-integration` flag or
the `PULUMI_INTEGRATION_TESTS=1` environment variable.

**Prerequisites:**
- Valid AWS credentials configured
- `pulumi up` has been applied successfully
- `PULUMI_STACK=dev-ausenergymarket` set, or `pulumi stack select dev-ausenergymarket`

**How to run:**
```bash
# Run integration tests only
PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/test_integration.py -v

# Or using the pytest marker
uv run pytest -m integration -v
```

**Test specifications:**

| Test | Method | Assertion |
|------|--------|-----------|
| `test_ecs_services_running` | `aws ecs list-services` | 4 services in ACTIVE state in `{name}-dagster-cluster` |
| `test_all_fargate_tasks_healthy` | `aws ecs describe-services` | `runningCount == desiredCount` for all 4 services |
| `test_user_code_cloud_map_registered` | `aws servicediscovery discover-instances` | `aemo-etl` resolves in `dagster` namespace |
| `test_webserver_admin_cloud_map_registered` | `aws servicediscovery discover-instances` | `webserver-admin` resolves in `dagster` namespace |
| `test_webserver_guest_cloud_map_registered` | `aws servicediscovery discover-instances` | `webserver-guest` resolves in `dagster` namespace |
| `test_caddy_webpage_accessible` | HTTP GET | `https://ausenergymarketdata.com/dagster-webserver/admin` returns 200 or 302 |
| `test_dagster_admin_ui_reachable` | HTTP GET | Response body contains `dagster` (case-insensitive) or Cognito redirect |
| `test_cloudwatch_logs_exist` | `aws logs describe-log-groups` | Log group `/ecs/{name}-dagster-cluster` exists |
| `test_cloudwatch_logs_streaming` | `aws logs describe-log-streams` | At least one log stream exists per service prefix |
| `test_postgres_ssm_param_populated` | `aws ssm get-parameter` | `/{name}/dagster/postgres/instance_private_dns` is non-empty |
| `test_dagster_daemon_running` | `aws ecs describe-services` | Daemon service `runningCount >= 1` |

**Implementation approach:**

Integration tests use `boto3` and `httpx` (or `requests`):

```python
import pytest
import boto3
import os

@pytest.fixture(scope="session")
def is_integration():
    return os.environ.get("PULUMI_INTEGRATION_TESTS") == "1"

@pytest.fixture(scope="session")
def ecs_client(is_integration):
    if not is_integration:
        pytest.skip("Integration tests disabled")
    return boto3.client("ecs", region_name="ap-southeast-2")

@pytest.fixture(scope="session")
def stack_name():
    return os.environ.get("PULUMI_STACK", "dev-ausenergymarket")

@pytest.fixture(scope="session")
def resource_name(stack_name):
    env = stack_name.split("-")[0]  # e.g., "dev"
    return f"{env}-energy-market"

@pytest.mark.integration
def test_all_fargate_tasks_healthy(ecs_client, resource_name):
    cluster = f"{resource_name}-dagster-cluster"
    response = ecs_client.describe_services(
        cluster=cluster,
        services=ecs_client.list_services(cluster=cluster)["serviceArns"],
    )
    for svc in response["services"]:
        assert svc["runningCount"] == svc["desiredCount"], (
            f"Service {svc['serviceName']}: running={svc['runningCount']} "
            f"desired={svc['desiredCount']}"
        )
```

---

## 5. Execution Order

```
1. Apply 8 code fixes (section 2)
2. Update pyproject.toml (test deps + pytest config)
3. Update .pre-commit-config.yaml (add pytest hook)
4. Create tests/ directory and all test files
5. uv sync
6. uv run pytest tests/unit/ -q                          # all unit tests pass
7. git add . && prek run -a                               # all quality hooks pass
8. pulumi preview                                         # zero warnings
9. pulumi up                                              # deploy
10. PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/integration/ -v
```

---

## 6. Acceptance Criteria

- [ ] `pulumi preview` emits **zero** deprecation warnings
- [ ] `prek run -a` exits with code 0 (all hooks pass)
- [ ] `uv run pytest tests/unit/` exits with code 0 (all 116+ unit tests pass)
- [ ] All 14 component test files have at least one passing test
- [ ] `test_deprecation_warnings.py` all tests pass
- [ ] `test_ecs_services.py` verifies Cloud Map names: `aemo-etl`, `webserver-admin`, `webserver-guest`
- [ ] Post-deployment: `https://ausenergymarketdata.com/dagster-webserver/admin` returns HTTP 200/302
- [ ] Post-deployment: `https://ausenergymarketdata.com/dagster-webserver/guest` returns HTTP 200
- [ ] Post-deployment: all 4 Fargate services show `runningCount == desiredCount`

---

## 7. Post-Deployment Verification Checks

These checks must pass after every `pulumi up`. Run them in order.

### 7.1 Quality checks (pre-deployment)

```bash
git add .
prek run -a
# Expected: all 9 hooks pass, including 116+ pytest unit tests
```

### 7.2 Infrastructure sanity (`pulumi preview` idempotency)

```bash
pulumi preview
# Expected: "N unchanged" — zero creates, updates, replaces, or deletes
# Any non-zero plan indicates state drift and must be investigated before proceeding
```

### 7.3 Automated integration tests

```bash
PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/integration/ -v
```

Expected results (all 20 tests pass):

| Test class | Tests | What is verified |
|------------|-------|-----------------|
| `TestEcsServicesRunning` | 3 | All 4 services ACTIVE; runningCount == desiredCount; daemon running |
| `TestServiceDiscoveryRegistration` | 3 | `aemo-etl`, `webserver-admin`, `webserver-guest` discoverable in Cloud Map |
| `TestWebpageAccessibility` | 3 | Admin UI → 302 (Cognito); Guest UI → 200; Root → 200 |
| `TestCloudWatchLogs` | 2 | Log group exists; at least one log stream present |
| `TestSsmParameters` | 2 | Postgres DNS param non-empty; password param is SecureString |
| `TestS3Buckets` | 2 | All 7 data lake buckets exist; archive bucket has public access blocked |
| `TestDynamoDB` | 3 | `delta_log` table ACTIVE; correct key schema; PAY_PER_REQUEST billing |
| `TestBastionHost` | 2 | Bastion instance running; EIP associated |

### 7.4 URL verification (manual spot-check)

```bash
# Admin — must return 302 redirect to Cognito login
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://ausenergymarketdata.com/dagster-webserver/admin
# Expected: 302

# Guest — must return 200 (no auth required)
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://ausenergymarketdata.com/dagster-webserver/guest
# Expected: 200

# Root — static landing page served by Caddy
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://ausenergymarketdata.com/
# Expected: 200

# OAuth2 endpoint — FastAPI auth server
curl -sS -o /dev/null -w '%{http_code}\n' \
  https://ausenergymarketdata.com/oauth2/
# Expected: 200
```

### 7.5 ECS service health (manual spot-check)

```bash
aws ecs describe-services \
  --cluster dev-energy-market-dagster-cluster \
  --services $(aws ecs list-services \
    --cluster dev-energy-market-dagster-cluster \
    --query 'serviceArns' --output text --region ap-southeast-2) \
  --region ap-southeast-2 \
  --query 'services[*].{name:serviceName,running:runningCount,desired:desiredCount,status:status}' \
  --output table
# Expected: all 4 services ACTIVE with running == desired == 1
```

### 7.6 Postgres connectivity verification

```bash
# Check PostgreSQL is running on the instance
aws ssm get-parameter \
  --name /dev-energy-market/dagster/postgres/instance_private_dns \
  --region ap-southeast-2 \
  --query 'Parameter.Value' --output text
# Expected: ip-10-0-X-X.ap-southeast-2.compute.internal (non-empty)

# Check all Fargate tasks can connect (no crash-loop in recent logs)
aws logs filter-log-events \
  --log-group-name /ecs/dev-energy-market-dagster-cluster \
  --filter-pattern "DagsterPostgresException" \
  --start-time $(date -d '5 minutes ago' +%s000) \
  --region ap-southeast-2 \
  --query 'events[*].message' --output text
# Expected: empty output (no postgres errors in the last 5 minutes)
```

### 7.7 Idempotency check

```bash
pulumi preview
# Expected: "168 unchanged" — running twice in a row produces zero changes
```

---

## 8. Known Issues and Mitigations

| Issue | Status | Mitigation |
|-------|--------|------------|
| FARGATE_SPOT interruptions cause brief downtime | **Fixed** | Added `FARGATE` on-demand fallback with `base=1` |
| PostgreSQL failed to start on t4g.nano (512MB) | **Fixed** | Set `shared_buffers=64MB` and moved config before first start |
| ServiceDiscovery `ResourceInUse` on delete | **Fixed** | Added `force_destroy=True` to SD service |
| S3 bucket state drift (double-import loop) | **Fixed** | Removed `try/except` import logic from `create_bucket` |
| `healthCheckCustomConfig` replace loop | **Fixed** | Patched state; `health_check_custom_config` re-added without `failure_threshold` |
| Shared task definition family for admin/guest | **Fixed** | Distinct families `dagster-webserver-admin` and `dagster-webserver-guest` |

---

*Document version: 2.0*
