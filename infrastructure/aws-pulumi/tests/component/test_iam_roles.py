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

    @pulumi.runtime.test
    def test_daemon_task_policy_does_not_grant_secrets_manager(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            actions = [
                action
                for statement in policy.get("Statement", [])
                for action in statement.get("Action", [])
            ]
            assert not any(action.startswith("secretsmanager:") for action in actions)

        return iam.daemon_task_policy.policy.apply(check)

    @pulumi.runtime.test
    def test_daemon_task_policy_allows_dagster_run_worker_task_definitions(
        self,
    ) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            statements = policy.get("Statement", [])
            task_definition_statements = [
                statement
                for statement in statements
                if set(statement.get("Action", []))
                & {"ecs:RegisterTaskDefinition", "ecs:RunTask"}
            ]
            assert task_definition_statements
            for statement in task_definition_statements:
                resources = statement.get("Resource", [])
                assert (
                    "arn:aws:ecs:ap-southeast-2:123456789012:task-definition/run_*:*"
                    in resources
                )
                assert (
                    "arn:aws:ecs:ap-southeast-2:123456789012:task-definition/dagster-*:*"
                    in resources
                )

        return iam.daemon_task_policy.policy.apply(check)

    @pulumi.runtime.test
    def test_daemon_task_policy_allows_run_task_tagging_in_cluster(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            statements = policy.get("Statement", [])
            task_tag_statements = [
                statement
                for statement in statements
                if "ecs:TagResource" in statement.get("Action", [])
                and statement.get("Resource")
                == "arn:aws:ecs:ap-southeast-2:123456789012:task/test-energy-market-dagster-cluster/*"
            ]
            assert task_tag_statements
            assert task_tag_statements[0].get("Condition") == {
                "StringEquals": {"ecs:CreateAction": "RunTask"}
            }

        return iam.daemon_task_policy.policy.apply(check)

    @pulumi.runtime.test
    def test_daemon_task_pass_role_is_scoped(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            pass_role_statements = [
                statement
                for statement in policy.get("Statement", [])
                if "iam:PassRole" in statement.get("Action", [])
            ]
            assert pass_role_statements
            for statement in pass_role_statements:
                assert statement.get("Resource") != "*"
                assert statement.get("Condition") == {
                    "StringEquals": {"iam:PassedToService": "ecs-tasks.amazonaws.com"}
                }

        return iam.daemon_task_policy.policy.apply(check)

    @pulumi.runtime.test
    def test_execution_ssm_policy_is_scoped_to_postgres_password(self) -> None:
        iam = IamRolesComponentResource("test-energy-market")

        def check(policy_doc: str) -> None:
            policy = json.loads(policy_doc)
            statements = policy["Statement"]
            assert statements == [
                {
                    "Effect": "Allow",
                    "Action": ["ssm:GetParameters"],
                    "Resource": "arn:aws:ssm:ap-southeast-2:123456789012:parameter/test-energy-market/dagster/postgres/password",
                }
            ]

        return iam.daemon_execution_ssm_policy.policy.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: .region must be used, not .name, on GetRegionResult."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            IamRolesComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
