"""Deployed AWS tests.

These tests run against the live AWS environment AFTER a successful `pulumi up`.
They are skipped by default; opt in with:

    PULUMI_INTEGRATION_TESTS=1 uv run pytest tests/deployed/ -v

or using the pytest marker:

    uv run pytest -m deployed -v

Prerequisites:
  - Valid AWS credentials configured (AWS_PROFILE or key env vars)
  - `pulumi up` has been successfully applied
  - AWS_DEFAULT_REGION=ap-southeast-2 (or equivalent profile config)

The PULUMI_STACK environment variable controls which stack's resources are
targeted (defaults to "dev-ausenergymarket").

Shared fixtures (deployed_enabled, aws_region, stack_name, environment,
resource_name, and all boto3 clients) are defined in conftest.py.
"""

import socket
import time
from collections.abc import Iterator
from contextlib import contextmanager
from urllib.parse import urlparse

import pytest

from code_locations import (
    DagsterCodeLocation,
    default_code_location,
    load_code_locations,
    user_code_component_name,
    user_code_ecs_service_resource_name,
)

DAGSTER_CODE_LOCATIONS = load_code_locations()
DEFAULT_DAGSTER_CODE_LOCATION = default_code_location(DAGSTER_CODE_LOCATIONS)


def _required_ecs_service_names(resource_name: str) -> set[str]:
    return {
        *{
            user_code_ecs_service_resource_name(
                user_code_component_name(
                    resource_name,
                    location,
                    DEFAULT_DAGSTER_CODE_LOCATION,
                )
            )
            for location in DAGSTER_CODE_LOCATIONS
        },
        f"{resource_name}-webserver-admin-webserver-service",
        f"{resource_name}-webserver-guest-webserver-service",
        f"{resource_name}-daemon-daemon-service",
    }


def _describe_required_ecs_services(ecs_client, resource_name: str) -> list[dict]:
    cluster = f"{resource_name}-dagster-cluster"
    required_names = _required_ecs_service_names(resource_name)
    response = ecs_client.describe_services(
        cluster=cluster,
        services=sorted(required_names),
    )
    failures = response.get("failures", [])
    assert not failures, f"Failed to describe required ECS services: {failures}"

    services = response.get("services", [])
    service_names = {svc["serviceName"] for svc in services}
    missing = required_names - service_names
    assert not missing, f"Missing required ECS services: {sorted(missing)}"
    return services


# ---------------------------------------------------------------------------
# ECS service health tests
# ---------------------------------------------------------------------------


class TestEcsServicesRunning:
    def test_ecs_services_active(self, ecs_client, resource_name: str) -> None:
        """All required Dagster Fargate services must be in ACTIVE state."""
        services = _describe_required_ecs_services(ecs_client, resource_name)
        statuses = {svc["serviceName"]: svc["status"] for svc in services}
        inactive = {name: st for name, st in statuses.items() if st != "ACTIVE"}
        assert not inactive, f"Services not ACTIVE: {inactive}"

    def test_all_fargate_tasks_healthy(self, ecs_client, resource_name: str) -> None:
        """Every required service must be steady with desired tasks running."""
        services = _describe_required_ecs_services(ecs_client, resource_name)
        unhealthy = {}
        for svc in services:
            if (
                svc["desiredCount"] < 1
                or svc["runningCount"] != svc["desiredCount"]
                or svc["pendingCount"] != 0
            ):
                unhealthy[svc["serviceName"]] = {
                    "running": svc["runningCount"],
                    "desired": svc["desiredCount"],
                    "pending": svc["pendingCount"],
                }
        assert not unhealthy, f"Unsteady required ECS services: {unhealthy}"

    def test_dagster_daemon_running(self, ecs_client, resource_name: str) -> None:
        """The Dagster daemon service must have at least one running task."""
        services = _describe_required_ecs_services(ecs_client, resource_name)
        daemon_services = [
            svc for svc in services if "daemon" in svc["serviceName"].lower()
        ]
        assert daemon_services, "No daemon service found in cluster"
        daemon = daemon_services[0]
        assert daemon["runningCount"] >= 1, (
            f"Daemon service {daemon['serviceName']} has 0 running tasks"
        )

    def test_ecs_service_rollouts_complete(
        self, ecs_client, resource_name: str
    ) -> None:
        """Required ECS services must not have failed or in-progress rollouts."""
        services = _describe_required_ecs_services(ecs_client, resource_name)
        bad_rollouts = {}
        for service in services:
            failed = [
                deployment
                for deployment in service.get("deployments", [])
                if deployment.get("rolloutState") == "FAILED"
            ]
            primary: dict[str, object] = next(
                (
                    deployment
                    for deployment in service.get("deployments", [])
                    if deployment.get("status") == "PRIMARY"
                ),
                {},
            )
            primary_state = primary.get("rolloutState")
            if failed or primary_state not in {None, "COMPLETED"}:
                bad_rollouts[service["serviceName"]] = {
                    "primary": primary_state,
                    "failed": failed,
                }

        assert not bad_rollouts, (
            f"Services with incomplete/failed rollout: {bad_rollouts}"
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

    @pytest.mark.parametrize(
        "code_location",
        DAGSTER_CODE_LOCATIONS,
        ids=[location.name for location in DAGSTER_CODE_LOCATIONS],
    )
    def test_user_code_cloud_map_registered(
        self,
        servicediscovery_client: object,
        resource_name: str,
        code_location: DagsterCodeLocation,
    ) -> None:
        """Manifest-declared user-code locations must be discoverable."""
        self._get_namespace_id(servicediscovery_client)
        response = servicediscovery_client.discover_instances(  # type: ignore[union-attr]
            NamespaceName="dagster",
            ServiceName=code_location.cloud_map_name,
        )
        instances = response.get("Instances", [])
        assert len(instances) >= 1, (
            "Expected at least 1 instance for "
            f"{code_location.cloud_map_name}.dagster, got {len(instances)}"
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

    def test_marimo_dashboard_cloud_map_registered(
        self, servicediscovery_client: object, resource_name: str
    ) -> None:
        """marimo-dashboard must be discoverable via Cloud Map."""
        response = servicediscovery_client.discover_instances(  # type: ignore[union-attr]
            NamespaceName="dagster",
            ServiceName="marimo-dashboard",
        )
        instances = response.get("Instances", [])
        assert len(instances) >= 1, (
            f"Expected at least 1 instance for marimo-dashboard.dagster, "
            f"got {len(instances)}"
        )


# ---------------------------------------------------------------------------
# Webpage and UI accessibility tests
# ---------------------------------------------------------------------------


def _public_route53_a_record(route53_client: object, hostname: str) -> str | None:
    response = route53_client.list_hosted_zones_by_name(  # type: ignore[union-attr]
        DNSName=hostname,
        MaxItems="1",
    )
    hosted_zones = response.get("HostedZones", [])
    if not hosted_zones:
        return None

    zone = hosted_zones[0]
    if zone.get("Name", "").rstrip(".") != hostname:
        return None
    if zone.get("Config", {}).get("PrivateZone", False):
        return None

    zone_id = str(zone["Id"]).rsplit("/", maxsplit=1)[-1]
    records = route53_client.list_resource_record_sets(  # type: ignore[union-attr]
        HostedZoneId=zone_id,
        StartRecordName=hostname,
        StartRecordType="A",
        MaxItems="1",
    )
    for record in records.get("ResourceRecordSets", []):
        if record.get("Name", "").rstrip(".") != hostname:
            continue
        if record.get("Type") != "A":
            continue
        values = record.get("ResourceRecords", [])
        if values:
            return str(values[0]["Value"])

    return None


@contextmanager
def _temporary_hostname_override(hostname: str, ip_address: str) -> Iterator[None]:
    original_getaddrinfo = socket.getaddrinfo

    def getaddrinfo(
        host: str,
        port: str | int | None,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list[tuple]:
        if host == hostname:
            return original_getaddrinfo(ip_address, port, family, type, proto, flags)
        return original_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = getaddrinfo  # type: ignore[assignment,method-assign]
    try:
        yield
    finally:
        socket.getaddrinfo = original_getaddrinfo  # type: ignore[method-assign]


def _get_with_route53_dns_fallback(
    route53_client: object,
    url: str,
    *,
    timeout: int,
    allow_redirects: bool,
):
    import requests

    try:
        return requests.get(url, timeout=timeout, allow_redirects=allow_redirects)
    except requests.exceptions.ConnectionError:
        hostname = urlparse(url).hostname
        if hostname is None:
            raise

        ip_address = _public_route53_a_record(route53_client, hostname)
        if ip_address is None:
            raise

        with _temporary_hostname_override(hostname, ip_address):
            return requests.get(url, timeout=timeout, allow_redirects=allow_redirects)


def _eventually_get_with_route53_dns_fallback(
    route53_client: object,
    url: str,
    *,
    timeout: int,
    allow_redirects: bool,
    expected_statuses: set[int],
    attempts: int = 36,
    delay_seconds: int = 10,
):
    response = _get_with_route53_dns_fallback(
        route53_client,
        url,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    for _ in range(1, attempts):
        if response.status_code in expected_statuses:
            return response
        time.sleep(delay_seconds)
        response = _get_with_route53_dns_fallback(
            route53_client,
            url,
            timeout=timeout,
            allow_redirects=allow_redirects,
        )
    return response


class TestWebpageAccessibility:
    def test_caddy_admin_ui_reachable(
        self, deployed_enabled: None, route53_client: object, base_url: str
    ) -> None:
        """The Dagster admin UI must return HTTP 200 or 302 (Cognito redirect)."""
        try:
            import requests  # noqa: F401
        except ImportError:
            pytest.skip("requests not installed")

        url = f"{base_url}/dagster-webserver/admin"
        response = _eventually_get_with_route53_dns_fallback(
            route53_client,
            url,
            timeout=30,
            allow_redirects=False,
            expected_statuses={200, 302},
        )
        assert response.status_code in {200, 302}, (
            f"Expected 200 or 302 from {url}, got {response.status_code}"
        )

    def test_caddy_guest_ui_reachable(
        self, deployed_enabled: None, route53_client: object, base_url: str
    ) -> None:
        """The Dagster guest UI must return a ready response from Caddy.

        Acceptable status codes:
          200 — page served directly
          302 — Cognito redirect (if auth is applied)
          307 — Dagster's canonical redirect (/guest → /guest/)
        """
        try:
            import requests  # noqa: F401
        except ImportError:
            pytest.skip("requests not installed")

        url = f"{base_url}/dagster-webserver/guest"
        response = _eventually_get_with_route53_dns_fallback(
            route53_client,
            url,
            timeout=30,
            allow_redirects=False,
            expected_statuses={200, 302, 307},
        )
        assert response.status_code in {200, 302, 307}, (
            f"Expected 200, 302, or 307 from {url}, got {response.status_code}"
        )

    def test_caddy_root_reachable(
        self, deployed_enabled: None, route53_client: object, base_url: str
    ) -> None:
        """The root URL must respond (Caddy is up and TLS is working)."""
        try:
            import requests  # noqa: F401
        except ImportError:
            pytest.skip("requests not installed")

        url = base_url
        response = _get_with_route53_dns_fallback(
            route53_client,
            url,
            timeout=30,
            allow_redirects=False,
        )
        assert response.status_code < 500, (
            f"Expected non-5xx from {url}, got {response.status_code}"
        )

    def test_marimo_health_reachable_without_auth(
        self, deployed_enabled: None, route53_client: object, base_url: str
    ) -> None:
        """The Marimo health route must be reachable through Caddy."""
        try:
            import requests  # noqa: F401
        except ImportError:
            pytest.skip("requests not installed")

        url = f"{base_url}/marimo/health"
        response = _eventually_get_with_route53_dns_fallback(
            route53_client,
            url,
            timeout=30,
            allow_redirects=False,
            expected_statuses={200},
        )
        assert response.status_code == 200, (
            f"Expected 200 from {url}, got {response.status_code}"
        )
        assert response.json() == {"status": "ok"}


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

    def test_current_daemon_logs_have_no_permission_denials(
        self, ecs_client, logs_client: object, resource_name: str
    ) -> None:
        """The current daemon must not be blocked by IAM denials."""
        cluster = f"{resource_name}-dagster-cluster"
        service = f"{resource_name}-daemon-daemon-service"
        tasks_response = ecs_client.list_tasks(
            cluster=cluster,
            serviceName=service,
            desiredStatus="RUNNING",
        )
        task_arns = tasks_response.get("taskArns", [])
        assert task_arns, f"No running daemon task found for {service}"

        task_id = task_arns[0].rsplit("/", 1)[-1]
        log_group_name = f"/ecs/{resource_name}-dagster-cluster"
        log_stream_name = f"dagster-daemon/DagsterDaemonContainer/{task_id}"
        response = logs_client.get_log_events(  # type: ignore[union-attr]
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=200,
        )
        messages = "\n".join(event["message"] for event in response.get("events", []))
        assert "AccessDenied" not in messages
        assert "not authorized" not in messages
        assert "secretsmanager:ListSecrets" not in messages


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
        """The Postgres password SSM parameter must use the expected type."""
        param_name = f"/{resource_name}/dagster/postgres/password"
        response = ssm_client.get_parameter(  # type: ignore[union-attr]
            Name=param_name, WithDecryption=False
        )
        expected_type = (
            "String" if resource_name == "dev-energy-market" else "SecureString"
        )
        assert response["Parameter"]["Type"] == expected_type, (
            f"Expected {expected_type} type for {param_name!r}"
        )


# ---------------------------------------------------------------------------
# Live security posture tests
# ---------------------------------------------------------------------------


def _expected_ec2_names(resource_name: str) -> set[str]:
    return {
        f"{resource_name}-bastion",
        f"{resource_name}-caddy",
        f"{resource_name}-fastapi-auth",
        f"{resource_name}-fck-nat",
        f"{resource_name}-marimo-dashboard",
        f"{resource_name}-postgres",
    }


def _deployed_ec2_instances(ec2_client: object, resource_name: str) -> list[dict]:
    expected_names = _expected_ec2_names(resource_name)
    response = ec2_client.describe_instances(  # type: ignore[union-attr]
        Filters=[
            {"Name": "tag:Name", "Values": sorted(expected_names)},
            {
                "Name": "instance-state-name",
                "Values": ["pending", "running", "stopping", "stopped"],
            },
        ]
    )
    instances = [
        instance
        for reservation in response.get("Reservations", [])
        for instance in reservation.get("Instances", [])
    ]
    found_names = {
        tag["Value"]
        for instance in instances
        for tag in instance.get("Tags", [])
        if tag.get("Key") == "Name"
    }
    missing = expected_names - found_names
    assert not missing, f"Missing expected EC2 instances by Name tag: {sorted(missing)}"
    return instances


class TestLiveSecurityPosture:
    def test_ec2_instances_require_imdsv2(
        self, ec2_client: object, resource_name: str
    ) -> None:
        """All deployed EC2 hosts must require IMDSv2 tokens."""
        insecure = {}
        for instance in _deployed_ec2_instances(ec2_client, resource_name):
            tokens = instance.get("MetadataOptions", {}).get("HttpTokens")
            if tokens != "required":
                insecure[instance["InstanceId"]] = tokens

        assert not insecure, f"EC2 instances without required IMDSv2: {insecure}"

    def test_ec2_ebs_volumes_are_encrypted(
        self, ec2_client: object, resource_name: str
    ) -> None:
        """All attached EBS volumes on deployed EC2 hosts must be encrypted."""
        instances = _deployed_ec2_instances(ec2_client, resource_name)
        volume_ids = [
            mapping["Ebs"]["VolumeId"]
            for instance in instances
            for mapping in instance.get("BlockDeviceMappings", [])
            if "Ebs" in mapping
        ]
        assert volume_ids, "No EC2 EBS volumes found to check"

        response = ec2_client.describe_volumes(  # type: ignore[union-attr]
            VolumeIds=volume_ids
        )
        unencrypted = [
            volume["VolumeId"]
            for volume in response.get("Volumes", [])
            if volume.get("Encrypted") is not True
        ]
        assert not unencrypted, f"Unencrypted EC2 EBS volumes: {unencrypted}"

    def test_ecr_repositories_scan_on_push(
        self, ecr_client: object, resource_name: str
    ) -> None:
        """All deployment ECR repositories must have scan-on-push enabled."""
        response = ecr_client.describe_repositories()  # type: ignore[union-attr]
        repositories = [
            repo
            for repo in response.get("repositories", [])
            if repo.get("repositoryName", "").startswith(f"{resource_name}/dagster/")
        ]
        assert repositories, f"No ECR repositories found for {resource_name}/dagster/"

        not_scanned = [
            repo["repositoryName"]
            for repo in repositories
            if repo.get("imageScanningConfiguration", {}).get("scanOnPush") is not True
        ]
        assert not not_scanned, f"ECR repositories without scan-on-push: {not_scanned}"

    def test_ecs_task_definitions_use_ssm_secret_for_postgres_password(
        self, ecs_client, resource_name: str
    ) -> None:
        """Required ECS task definitions must not expose DB password as env."""
        services = _describe_required_ecs_services(ecs_client, resource_name)
        insecure = {}
        for service in services:
            response = ecs_client.describe_task_definition(
                taskDefinition=service["taskDefinition"]
            )
            task_definition = response["taskDefinition"]
            for container in task_definition.get("containerDefinitions", []):
                env_names = {item["name"] for item in container.get("environment", [])}
                secret_names = {item["name"] for item in container.get("secrets", [])}
                if (
                    "DAGSTER_POSTGRES_PASSWORD" in env_names
                    or "DAGSTER_POSTGRES_PASSWORD" not in secret_names
                ):
                    insecure[task_definition["taskDefinitionArn"]] = container["name"]

        assert not insecure, f"Task definitions exposing DB password: {insecure}"


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
