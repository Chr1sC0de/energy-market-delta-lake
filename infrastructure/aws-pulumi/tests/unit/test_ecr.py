"""Tests for ECRComponentResource."""

import warnings

import pulumi

from components.ecr import ECRComponentResource


class TestEcrRepositories:
    def test_all_six_repos_created(self) -> None:
        ecr = ECRComponentResource("test-energy-market")
        assert ecr.dagster_postgres is not None
        assert ecr.dagster_webserver is not None
        assert ecr.dagster_daemon is not None
        assert ecr.dagster_user_code_aemo_etl is not None
        assert ecr.caddy is not None
        assert ecr.authentication is not None

    @pulumi.runtime.test
    def test_postgres_repo_url_contains_dagster_postgres(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "postgres" in url.lower(), (
                f"Expected 'postgres' in repo URL, got {url}"
            )

        return ecr.dagster_postgres.repository_url.apply(check)

    @pulumi.runtime.test
    def test_webserver_repo_url_contains_dagster_webserver(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "webserver" in url.lower(), (
                f"Expected 'webserver' in repo URL, got {url}"
            )

        return ecr.dagster_webserver.repository_url.apply(check)

    @pulumi.runtime.test
    def test_daemon_repo_url_contains_dagster_daemon(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "daemon" in url.lower(), f"Expected 'daemon' in repo URL, got {url}"

        return ecr.dagster_daemon.repository_url.apply(check)

    @pulumi.runtime.test
    def test_user_code_repo_url_contains_aemo_etl(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "aemo" in url.lower() or "user-code" in url.lower(), (
                f"Expected 'aemo' or 'user-code' in repo URL, got {url}"
            )

        return ecr.dagster_user_code_aemo_etl.repository_url.apply(check)

    @pulumi.runtime.test
    def test_caddy_repo_url_contains_caddy(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "caddy" in url.lower(), f"Expected 'caddy' in repo URL, got {url}"

        return ecr.caddy.repository_url.apply(check)

    @pulumi.runtime.test
    def test_authentication_repo_url_contains_authentication(self) -> None:
        ecr = ECRComponentResource("test-energy-market")

        def check(url: str) -> None:
            assert "auth" in url.lower(), f"Expected 'auth' in repo URL, got {url}"

        return ecr.authentication.repository_url.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        """Regression guard: dead aws.get_region() call removed from ecr.py."""
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            ECRComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
