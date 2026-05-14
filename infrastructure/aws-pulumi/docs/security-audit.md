# Security Audit

This audit covers the `infrastructure/aws-pulumi` dev deployment path and the
runtime resources it defines for `dev-ausenergymarket`.

## Table of contents

- [Audit result](#audit-result)
- [Remediated findings](#remediated-findings)
- [Deployment proof](#deployment-proof)
- [Residual risks](#residual-risks)
- [Related docs](#related-docs)

## Audit result

The 2026-05-11 audit found no intentional public data-plane entrypoint beyond
Caddy on HTTP/HTTPS, but identified several infrastructure hardening gaps. The
blocking gaps have been remediated in Pulumi code and covered by component or
deployed tests.

## Remediated findings

| Severity | Finding | Remediation |
|---|---|---|
| High | Postgres password was embedded in ECS plain environment variables | ECS task definitions now use ECS `secrets` backed by the SSM SecureString parameter |
| High | Postgres password was rendered into EC2 user data | Postgres bootstraps by fetching the password from SSM at boot |
| High | Cognito values were rendered into FastAPI auth EC2 user data | FastAPI auth stores Cognito values in SSM SecureString parameters and fetches them at boot |
| High | ECS task roles used wildcard `iam:PassRole` | PassRole is scoped to the Dagster daemon task and execution roles |
| Medium | Daemon task role included unused Secrets Manager reads | Secrets Manager permissions were removed |
| Medium | Dagster run-worker launches were blocked by incomplete ECS resource scope | The daemon can register and launch `dagster-*` and `run_*` task definitions, tag created ECS tasks during `RunTask`, and no longer performs the unused default Secrets Manager tag lookup |
| Medium | ECS execution-role SSM access used wildcard resources | Execution roles can read only the Postgres password parameter |
| Medium | EC2 hosts did not require IMDSv2 or encrypted root volumes | NAT, bastion, Postgres, FastAPI auth, Caddy, Marimo dashboard, and optional run-worker ECS container instances now require IMDSv2 and encrypted roots |
| Medium | Postgres accepted `0.0.0.0/0 md5` in `pg_hba.conf` | Postgres now accepts the VPC CIDR with `scram-sha-256` |
| Medium | ECR repositories disabled scan-on-push | All deployment ECR repositories now enable scan-on-push |
| Medium | Administrator ingress accepted empty or broad values | `ADMINISTRATOR_IPS` now requires individual IPv4 addresses or `/32` CIDRs |

## Deployment proof

A dev deployment is accepted only when the repo-local workflow succeeds:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests --with-idempotency --stack dev-ausenergymarket
```

That workflow runs local Pulumi unit/component tests, the **Commit check**,
`pulumi up`, deployed AWS tests, and a no-op preview. The deployed tests verify:

- guest access at `/dagster-webserver/guest` returns `200`, `302`, or `307`
- Marimo health at `/marimo/health` returns `200`
- the exact required ECS Fargate services, including manifest-declared
  user-code services, exist, are `ACTIVE`, have
  `desiredCount >= 1`, `runningCount == desiredCount`, `pendingCount == 0`,
  and have no failed rollout
- Cloud Map registrations and CloudWatch log streams exist
- the current daemon log stream has no post-deploy IAM permission denials
- EC2 hosts require IMDSv2 and encrypted EBS volumes
- ECR repositories enable scan-on-push
- required ECS task definitions use SSM-backed secrets for the Postgres
  password

2026-05-11 dev evidence:

- `uv run pytest tests/unit tests/component -q`: `173 passed`
- AWS Pulumi **Commit check**: `prek run -a` passed
- root **Commit check**: `prek run -a` passed
- `scripts/run-integration-tests --with-idempotency --stack dev-ausenergymarket`
  completed successfully
- deployed AWS tests: `26 passed`
- Pulumi no-op preview: `173 unchanged`
- final ECS status for the four required services:
  `desired=1`, `running=1`, `pending=0`, rollout `COMPLETED`
- post-fix live check found 20 running `run_*` Dagster run-worker Fargate
  tasks and no new permission-denial log events after IAM propagation
- a temporary Fargate task called the internal admin Dagster GraphQL endpoint,
  deleted 171 historical run records, verified zero remaining records at that
  checkpoint, and was deregistered after completion

## Residual risks

- ECR tags remain mutable because runtime task definitions and EC2 service
  bootstraps deploy digest-pinned image URIs. A future supply-chain hardening
  pass can move the repositories to immutable tags after confirming the Pulumi
  image-publish path.
- The deployed test suite verifies daemon permission health and service
  stability, but it does not wait for every newly launched run-worker job to
  complete successfully.
- SNS alert-topic creation remains manual. Pulumi scopes publish access when a
  topic ARN is configured.
- The issue #126 EC2 run-worker capacity provider is default-off Exploratory
  infrastructure. It adds an ECS container-instance profile and Auto Scaling
  group only when explicitly paired with the matching dev-only Dagster image
  target, and still needs deployed smoke evidence before it should become part
  of the normal Gitflow runtime.

## Related docs

- [AWS Pulumi infrastructure overview](../README.md)
- [Identity and discovery](identity-and-discovery.md)
- [Runtime](runtime.md)
- [Storage](storage.md)
- [Edge and access](edge-and-access.md)
- [Connectivity](connectivity.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `infrastructure/aws-pulumi/configs.py`
  - `infrastructure/aws-pulumi/dagster_core_deployment.py`
  - `backend-services/dagster-core/code-locations.aws.toml`
  - `infrastructure/aws-pulumi/code_locations.py`
  - `infrastructure/aws-pulumi/components/bastion_host.py`
  - `infrastructure/aws-pulumi/components/caddy.py`
  - `infrastructure/aws-pulumi/components/ecr.py`
  - `infrastructure/aws-pulumi/components/ecs_cluster.py`
  - `infrastructure/aws-pulumi/components/ecs_services.py`
  - `infrastructure/aws-pulumi/components/fastapi_auth.py`
  - `infrastructure/aws-pulumi/components/iam_roles.py`
  - `infrastructure/aws-pulumi/components/marimo.py`
  - `infrastructure/aws-pulumi/components/postgres.py`
  - `infrastructure/aws-pulumi/components/s3_buckets.py`
  - `infrastructure/aws-pulumi/components/security_groups.py`
  - `infrastructure/aws-pulumi/components/vpc.py`
  - `infrastructure/aws-pulumi/scripts/redeploy-user-code`
  - `infrastructure/aws-pulumi/scripts/run-integration-tests`
  - `infrastructure/aws-pulumi/tests/component/conftest.py`
  - `infrastructure/aws-pulumi/tests/component/test_bastion_host.py`
  - `infrastructure/aws-pulumi/tests/component/test_caddy.py`
  - `infrastructure/aws-pulumi/tests/component/test_ecr.py`
  - `infrastructure/aws-pulumi/tests/component/test_ecs_services.py`
  - `infrastructure/aws-pulumi/tests/component/test_fastapi_auth.py`
  - `infrastructure/aws-pulumi/tests/component/test_iam_roles.py`
  - `infrastructure/aws-pulumi/tests/component/test_marimo.py`
  - `infrastructure/aws-pulumi/tests/component/test_postgres.py`
  - `infrastructure/aws-pulumi/tests/component/test_vpc.py`
  - `infrastructure/aws-pulumi/tests/deployed/conftest.py`
  - `infrastructure/aws-pulumi/tests/deployed/test_integration.py`
  - `infrastructure/aws-pulumi/tests/unit/test_configs.py`
- `sync.scope`: `security, deployment`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure`
  - `verify links, commands, paths, env vars, resource names, and test claims`
