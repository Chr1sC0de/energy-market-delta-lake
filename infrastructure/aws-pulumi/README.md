# AWS Pulumi Infrastructure

Pulumi infrastructure for the AWS-hosted energy-market Dagster deployment.

## Full Integration Tests

The live integration workflow targets the existing `dev-ausenergymarket` stack by
default. It applies the stack, then runs the AWS integration suite against the
deployed resources.

Prerequisites:

- Pulumi CLI installed and logged in.
- AWS credentials configured for the target account.
- `uv` installed.
- Docker or Podman available for Pulumi image builds.
- Stack config secrets already set, for example via `scripts/setup_secrets`.

Run the full workflow from this directory:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests
```

Run tests against an already-deployed stack:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests --skip-up
```

Include the no-op idempotency check after the integration suite:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests --with-idempotency
```

Override the stack when needed:

```bash
AWS_DEFAULT_REGION=ap-southeast-2 scripts/run-integration-tests --stack dev-ausenergymarket
```

The idempotency check runs:

```bash
pulumi preview --expect-no-changes --non-interactive --stack "$PULUMI_STACK"
```

Only run it after a successful `pulumi up`. The first deployment after changing
Fargate images from `:latest` to immutable digests is expected to update the
Fargate task definitions once; the no-op preview should pass after that rollout
has been applied.

The integration suite remains opt-in. To run it directly:

```bash
PULUMI_INTEGRATION_TESTS=1 PULUMI_STACK=dev-ausenergymarket uv run pytest tests/integration -v
```

## Overview

This template provisions an S3 bucket (`pulumi_aws.s3.BucketV2`) in your AWS account and exports its ID as an output. It’s an ideal starting point when:

- You want to learn Pulumi with AWS in Python.
- You need a barebones S3 bucket deployment to build upon.
- You prefer a minimal template without extra dependencies.

## Prerequisites

- An AWS account with permissions to create S3 buckets.
- AWS credentials configured in your environment (for example via AWS CLI or environment variables).
- Python 3.6 or later installed.
- Pulumi CLI already installed and logged in.

## Getting Started

1. Generate a new project from this template:
   ```bash
   pulumi new aws-python
   ```
1. Follow the prompts to set your project name and AWS region (default: `us-east-1`).
1. Change into your project directory:
   ```bash
   cd <project-name>
   ```
1. Preview the planned changes:
   ```bash
   pulumi preview
   ```
1. Deploy the stack:
   ```bash
   pulumi up
   ```
1. Tear down when finished:
   ```bash
   pulumi destroy
   ```

## Project Layout

After running `pulumi new`, your directory will look like:

```
├── __main__.py         # Entry point of the Pulumi program
├── Pulumi.yaml         # Project metadata and template configuration
├── requirements.txt    # Python dependencies
└── Pulumi.<stack>.yaml # Stack-specific configuration (e.g., Pulumi.dev.yaml)
```

## Configuration

This template defines the following config value:

- `aws:region` (string)
  The AWS region to deploy resources into.
  Default: `us-east-1`

View or update configuration with:

```bash
pulumi config get aws:region
pulumi config set aws:region us-west-2
```

## Outputs

Once deployed, the stack exports:

- `bucket_name` — the ID of the created S3 bucket.

Retrieve outputs with:

```bash
pulumi stack output bucket_name
```

## Next Steps

- Customize `__main__.py` to add or configure additional resources.
- Explore the Pulumi AWS SDK: https://www.pulumi.com/registry/packages/aws/
- Break your infrastructure into modules for better organization.
- Integrate into CI/CD pipelines for automated deployments.

## Help and Community

If you have questions or need assistance:

- Pulumi Documentation: https://www.pulumi.com/docs/
- Community Slack: https://slack.pulumi.com/
- GitHub Issues: https://github.com/pulumi/pulumi/issues

Contributions and feedback are always welcome!
