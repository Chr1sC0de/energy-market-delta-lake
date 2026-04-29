"""Tests for IamRolesComponentResource."""

import json
import warnings

import pulumi

from components.iam_roles import IamRolesComponentResource


class TestIamRolesCreation:
    def test_bastion_profile_created(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")
        assert iam.bastion_profile is not None

    def test_webserver_execution_role_created(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")
        assert iam.webserver_execution_role is not None

    def test_daemon_execution_role_created(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")
        assert iam.daemon_execution_role is not None

    def test_webserver_task_role_created(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")
        assert iam.webserver_task_role is not None

    def test_daemon_task_role_created(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")
        assert iam.daemon_task_role is not None

    @pulumi.runtime.test
    def test_webserver_execution_role_assumes_ecs_tasks(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            principals = [
                p
                for stmt in policy.get("Statement", [])
                for p in (
                    [stmt["Principal"]["Service"]]
                    if isinstance(stmt.get("Principal", {}).get("Service"), str)
                    else stmt.get("Principal", {}).get("Service", [])
                )
            ]
            assert "ecs-tasks.amazonaws.com" in principals, (
                f"Expected ecs-tasks.amazonaws.com in principals, got {principals}"
            )

        return iam.webserver_execution_role.assume_role_policy.apply(check)

    @pulumi.runtime.test
    def test_daemon_execution_role_assumes_ecs_tasks(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            principals = [
                p
                for stmt in policy.get("Statement", [])
                for p in (
                    [stmt["Principal"]["Service"]]
                    if isinstance(stmt.get("Principal", {}).get("Service"), str)
                    else stmt.get("Principal", {}).get("Service", [])
                )
            ]
            assert "ecs-tasks.amazonaws.com" in principals, (
                f"Expected ecs-tasks.amazonaws.com in principals, got {principals}"
            )

        return iam.daemon_execution_role.assume_role_policy.apply(check)

    @pulumi.runtime.test
    def test_daemon_task_role_can_publish_sns_alerts(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            statements = policy.get("Statement", [])
            assert any(
                "sns:Publish" in statement.get("Action", [])
                and statement.get("Resource")
                == "arn:aws:sns:ap-southeast-2:123456789012:dagster-failed-run-alerts"
                for statement in statements
            )

        return iam.daemon_task_policy.policy.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: .region must be used, not .name, on GetRegionResult."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            IamRolesComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
