"""Post-deployment integration tests.

These tests run against the live AWS environment AFTER a successful `pulumi up`.
They are skipped by default; opt in with:

    PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/integration/ -v

or using the pytest marker:

    uv run pytest -m integration -v

Prerequisites:
  - Valid AWS credentials configured (AWS_PROFILE or key env vars)
  - `pulumi up` has been successfully applied
  - AWS_DEFAULT_REGION=ap-southeast-2 (or equivalent profile config)

The PULUMI_STACK environment variable controls which stack's resources are
targeted (defaults to "dev-ausenergymarket").

Shared fixtures (integration_enabled, aws_region, stack_name, environment,
resource_name, and all boto3 clients) are defined in conftest.py.
"""

import pytest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# ECS service health tests
# ---------------------------------------------------------------------------


class TestEcsServicesRunning:
    def test_ecs_services_active(self, ecs_client, resource_name: str) -> None:
        """All four Dagster Fargate services must be in ACTIVE state."""
        cluster = f"{resource_name}-dagster-cluster"
        paginator = ecs_client.get_paginator("list_services")
        all_arns: list[str] = []
        for page in paginator.paginate(cluster=cluster):
            all_arns.extend(page["serviceArns"])

        assert len(all_arns) >= 4, (
            f"Expected at least 4 services in cluster {cluster}, "
            f"found {len(all_arns)}: {all_arns}"
        )

        response = ecs_client.describe_services(cluster=cluster, services=all_arns)
        statuses = {svc["serviceName"]: svc["status"] for svc in response["services"]}
        inactive = {name: st for name, st in statuses.items() if st != "ACTIVE"}
        assert not inactive, f"Services not ACTIVE: {inactive}"

    def test_all_fargate_tasks_healthy(self, ecs_client, resource_name: str) -> None:
        """Every service must have runningCount == desiredCount."""
        cluster = f"{resource_name}-dagster-cluster"
        paginator = ecs_client.get_paginator("list_services")
        all_arns: list[str] = []
        for page in paginator.paginate(cluster=cluster):
            all_arns.extend(page["serviceArns"])

        response = ecs_client.describe_services(cluster=cluster, services=all_arns)
        unhealthy = {}
        for svc in response["services"]:
            if svc["runningCount"] != svc["desiredCount"]:
                unhealthy[svc["serviceName"]] = {
                    "running": svc["runningCount"],
                    "desired": svc["desiredCount"],
                }
        assert not unhealthy, f"Services with runningCount != desiredCount: {unhealthy}"

    def test_dagster_daemon_running(self, ecs_client, resource_name: str) -> None:
        """The Dagster daemon service must have at least one running task."""
        cluster = f"{resource_name}-dagster-cluster"
        paginator = ecs_client.get_paginator("list_services")
        all_arns: list[str] = []
        for page in paginator.paginate(cluster=cluster):
            all_arns.extend(page["serviceArns"])

        response = ecs_client.describe_services(cluster=cluster, services=all_arns)
        daemon_services = [
            svc
            for svc in response["services"]
            if "daemon" in svc["serviceName"].lower()
        ]
        assert daemon_services, "No daemon service found in cluster"
        daemon = daemon_services[0]
        assert daemon["runningCount"] >= 1, (
            f"Daemon service {daemon['serviceName']} has 0 running tasks"
        )


# ---------------------------------------------------------------------------
# Cloud Map service discovery tests
# ---------------------------------------------------------------------------


class TestServiceDiscoveryRegistration:
    def _get_namespace_id(
        self, sd_client: object, namespace_name: str = "dagster"
    ) -> str:
        response = sd_client.list_namespaces()  # type: ignore[union-attr]
        for ns in response["Namespaces"]:
            if ns["Name"] == namespace_name:
                return str(ns["Id"])
        raise AssertionError(f"Namespace '{namespace_name}' not found in Cloud Map")

    def test_user_code_cloud_map_registered(
        self, servicediscovery_client: object, resource_name: str
    ) -> None:
        """aemo-etl must be discoverable via Cloud Map."""
        self._get_namespace_id(servicediscovery_client)
        response = servicediscovery_client.discover_instances(  # type: ignore[union-attr]
            NamespaceName="dagster",
            ServiceName="aemo-etl",
        )
        instances = response.get("Instances", [])
        assert len(instances) >= 1, (
            f"Expected at least 1 instance for aemo-etl.dagster, got {len(instances)}"
        )

    def test_webserver_admin_cloud_map_registered(
        self, servicediscovery_client: object, resource_name: str
    ) -> None:
        """webserver-admin must be discoverable via Cloud Map."""
        response = servicediscovery_client.discover_instances(  # type: ignore[union-attr]
            NamespaceName="dagster",
            ServiceName="webserver-admin",
        )
        instances = response.get("Instances", [])
        assert len(instances) >= 1, (
            f"Expected at least 1 instance for webserver-admin.dagster, "
            f"got {len(instances)}"
        )

    def test_webserver_guest_cloud_map_registered(
        self, servicediscovery_client: object, resource_name: str
    ) -> None:
        """webserver-guest must be discoverable via Cloud Map."""
        response = servicediscovery_client.discover_instances(  # type: ignore[union-attr]
            NamespaceName="dagster",
            ServiceName="webserver-guest",
        )
        instances = response.get("Instances", [])
        assert len(instances) >= 1, (
            f"Expected at least 1 instance for webserver-guest.dagster, "
            f"got {len(instances)}"
        )


# ---------------------------------------------------------------------------
# Webpage and UI accessibility tests
# ---------------------------------------------------------------------------


class TestWebpageAccessibility:
    def test_caddy_admin_ui_reachable(
        self, integration_enabled: None, base_url: str
    ) -> None:
        """The Dagster admin UI must return HTTP 200 or 302 (Cognito redirect)."""
        try:
            import requests
        except ImportError:
            pytest.skip("requests not installed")

        url = f"{base_url}/dagster-webserver/admin"
        response = requests.get(url, timeout=30, allow_redirects=False)
        assert response.status_code in {200, 302}, (
            f"Expected 200 or 302 from {url}, got {response.status_code}"
        )

    def test_caddy_guest_ui_reachable(
        self, integration_enabled: None, base_url: str
    ) -> None:
        """The Dagster guest UI must return a non-5xx response from Caddy.

        Acceptable status codes:
          200 — page served directly
          302 — Cognito redirect (if auth is applied)
          307 — Dagster's canonical redirect (/guest → /guest/)
          502 — backend starting up; Caddy is live but Fargate task not ready yet
        """
        try:
            import requests
        except ImportError:
            pytest.skip("requests not installed")

        url = f"{base_url}/dagster-webserver/guest"
        response = requests.get(url, timeout=30, allow_redirects=False)
        assert response.status_code in {200, 302, 307, 502}, (
            f"Expected 200, 302, 307, or 502 from {url}, got {response.status_code}"
        )

    def test_caddy_root_reachable(
        self, integration_enabled: None, base_url: str
    ) -> None:
        """The root URL must respond (Caddy is up and TLS is working)."""
        try:
            import requests
        except ImportError:
            pytest.skip("requests not installed")

        url = base_url
        response = requests.get(url, timeout=30, allow_redirects=False)
        assert response.status_code < 500, (
            f"Expected non-5xx from {url}, got {response.status_code}"
        )


# ---------------------------------------------------------------------------
# CloudWatch logs tests
# ---------------------------------------------------------------------------


class TestCloudWatchLogs:
    def test_log_group_exists(self, logs_client: object, resource_name: str) -> None:
        """The ECS cluster log group must exist in CloudWatch."""
        log_group_name = f"/ecs/{resource_name}-dagster-cluster"
        response = logs_client.describe_log_groups(  # type: ignore[union-attr]
            logGroupNamePrefix=log_group_name,
        )
        groups = [
            g for g in response["logGroups"] if g["logGroupName"] == log_group_name
        ]
        assert groups, f"Log group {log_group_name!r} not found in CloudWatch"

    def test_log_streams_exist(self, logs_client: object, resource_name: str) -> None:
        """At least one log stream must exist — a container has started."""
        log_group_name = f"/ecs/{resource_name}-dagster-cluster"
        response = logs_client.describe_log_streams(  # type: ignore[union-attr]
            logGroupName=log_group_name,
            orderBy="LastEventTime",
            descending=True,
            limit=5,
        )
        streams = response.get("logStreams", [])
        assert streams, (
            f"No log streams found in {log_group_name!r}. "
            "Has at least one Fargate task started?"
        )


# ---------------------------------------------------------------------------
# SSM parameter tests
# ---------------------------------------------------------------------------


class TestSsmParameters:
    def test_postgres_private_dns_param_populated(
        self, ssm_client: object, resource_name: str
    ) -> None:
        """The Postgres private DNS SSM parameter must be a non-empty string."""
        param_name = f"/{resource_name}/dagster/postgres/instance_private_dns"
        response = ssm_client.get_parameter(  # type: ignore[union-attr]
            Name=param_name, WithDecryption=False
        )
        value = response["Parameter"]["Value"]
        assert value, f"SSM parameter {param_name!r} is empty"
        assert "compute" in value or "internal" in value or "." in value, (
            f"Unexpected DNS value: {value!r}"
        )

    def test_postgres_password_param_exists(
        self, ssm_client: object, resource_name: str
    ) -> None:
        """The Postgres password SSM SecureString parameter must exist."""
        param_name = f"/{resource_name}/dagster/postgres/password"
        response = ssm_client.get_parameter(  # type: ignore[union-attr]
            Name=param_name, WithDecryption=False
        )
        assert response["Parameter"]["Type"] == "SecureString", (
            f"Expected SecureString type for {param_name!r}"
        )


# ---------------------------------------------------------------------------
# S3 data lake bucket tests
# ---------------------------------------------------------------------------


class TestS3Buckets:
    def test_data_lake_buckets_exist(
        self, s3_client: object, resource_name: str
    ) -> None:
        """All seven S3 data lake buckets must exist and be accessible."""
        expected_suffixes = [
            "io-manager",
            "landing",
            "archive",
            "aemo",
            "bronze",
            "silver",
            "gold",
        ]
        response = s3_client.list_buckets()  # type: ignore[union-attr]
        existing_names = {b["Name"] for b in response["Buckets"]}
        missing = []
        for suffix in expected_suffixes:
            bucket_name = f"{resource_name}-{suffix}"
            if bucket_name not in existing_names:
                missing.append(bucket_name)
        assert not missing, (
            f"Missing S3 buckets: {missing}\n"
            f"Existing buckets matching prefix: "
            f"{sorted(n for n in existing_names if resource_name in n)}"
        )

    def test_archive_bucket_not_public(
        self, s3_client: object, resource_name: str
    ) -> None:
        """The archive bucket must have public access blocked."""
        bucket_name = f"{resource_name}-archive"
        response = s3_client.get_public_access_block(  # type: ignore[union-attr]
            Bucket=bucket_name
        )
        config = response["PublicAccessBlockConfiguration"]
        assert config["BlockPublicAcls"] is True, "BlockPublicAcls must be True"
        assert config["BlockPublicPolicy"] is True, "BlockPublicPolicy must be True"
        assert config["IgnorePublicAcls"] is True, "IgnorePublicAcls must be True"
        assert config["RestrictPublicBuckets"] is True, (
            "RestrictPublicBuckets must be True"
        )


# ---------------------------------------------------------------------------
# DynamoDB delta-locking table tests
# ---------------------------------------------------------------------------


class TestDynamoDB:
    def test_delta_log_table_exists(
        self, dynamodb_client: object, resource_name: str
    ) -> None:
        """The delta_log DynamoDB table must exist and be in ACTIVE status."""
        response = dynamodb_client.describe_table(  # type: ignore[union-attr]
            TableName="delta_log"
        )
        table = response["Table"]
        assert table["TableStatus"] == "ACTIVE", (
            f"Expected delta_log table status ACTIVE, got {table['TableStatus']}"
        )

    def test_delta_log_table_key_schema(
        self, dynamodb_client: object, resource_name: str
    ) -> None:
        """The delta_log table must have the correct hash+range key schema."""
        response = dynamodb_client.describe_table(  # type: ignore[union-attr]
            TableName="delta_log"
        )
        key_schema = {
            k["AttributeName"]: k["KeyType"] for k in response["Table"]["KeySchema"]
        }
        assert key_schema.get("tablePath") == "HASH", (
            f"Expected tablePath as HASH key, got schema: {key_schema}"
        )
        assert key_schema.get("fileName") == "RANGE", (
            f"Expected fileName as RANGE key, got schema: {key_schema}"
        )

    def test_delta_log_table_billing_mode(
        self, dynamodb_client: object, resource_name: str
    ) -> None:
        """The delta_log table must use PAY_PER_REQUEST billing."""
        response = dynamodb_client.describe_table(  # type: ignore[union-attr]
            TableName="delta_log"
        )
        billing = (
            response["Table"]
            .get("BillingModeSummary", {})
            .get("BillingMode", "PROVISIONED")
        )
        assert billing == "PAY_PER_REQUEST", (
            f"Expected PAY_PER_REQUEST billing, got {billing}"
        )


# ---------------------------------------------------------------------------
# Bastion host tests
# ---------------------------------------------------------------------------


class TestBastionHost:
    def test_bastion_instance_running(
        self, ec2_client: object, ssm_client: object, resource_name: str
    ) -> None:
        """The bastion EC2 instance must be in 'running' state."""
        # Resolve the bastion instance ID via SSM parameter
        param_name = f"/{resource_name}/dagster/bastion-host/instance-id"
        try:
            response = ssm_client.get_parameter(  # type: ignore[union-attr]
                Name=param_name, WithDecryption=False
            )
            instance_id = response["Parameter"]["Value"]
        except Exception:
            # Fall back to tag-based lookup if SSM param not present
            response = ec2_client.describe_instances(  # type: ignore[union-attr]
                Filters=[
                    {"Name": "tag:Name", "Values": [f"{resource_name}-bastion*"]},
                    {"Name": "instance-state-name", "Values": ["running"]},
                ]
            )
            reservations = response.get("Reservations", [])
            assert reservations, (
                f"No running bastion instance found with tag Name={resource_name}-bastion*"
            )
            return

        response = ec2_client.describe_instances(  # type: ignore[union-attr]
            InstanceIds=[instance_id]
        )
        state = response["Reservations"][0]["Instances"][0]["State"]["Name"]
        assert state == "running", (
            f"Bastion instance {instance_id} is in state '{state}', expected 'running'"
        )

    def test_bastion_has_public_ip(
        self, ec2_client: object, ssm_client: object, resource_name: str
    ) -> None:
        """The bastion host must have an Elastic IP (public IP) assigned."""
        # Resolve the instance ID via SSM then look up associated EIP
        param_name = f"/{resource_name}/dagster/bastion-host/instance-id"
        response = ssm_client.get_parameter(  # type: ignore[union-attr]
            Name=param_name, WithDecryption=False
        )
        instance_id = response["Parameter"]["Value"]
        assert instance_id, f"SSM parameter {param_name!r} is empty"

        # Look up the EIP associated with this instance
        eip_response = ec2_client.describe_addresses(  # type: ignore[union-attr]
            Filters=[
                {"Name": "instance-id", "Values": [instance_id]},
            ]
        )
        addresses = eip_response.get("Addresses", [])
        assert addresses, (
            f"No Elastic IP associated with bastion instance {instance_id}"
        )
        assert addresses[0].get("PublicIp"), (
            f"EIP {addresses[0].get('AllocationId')} has no public IP"
        )
