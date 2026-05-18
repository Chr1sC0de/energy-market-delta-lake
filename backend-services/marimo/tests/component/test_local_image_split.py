"""Component tests for the local Marimo image split."""

from pathlib import Path


MARIMO_DIR = Path(__file__).resolve().parents[2]
BACKEND_SERVICES_DIR = MARIMO_DIR.parent


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _service_block(compose: str, service_name: str, next_service_name: str) -> str:
    start = compose.index(f"  {service_name}:")
    end = compose.index(f"  {next_service_name}:", start)
    return compose[start:end]


def _caddy_matcher_block(caddyfile: str, matcher_name: str) -> str:
    start = caddyfile.index(f"    {matcher_name} {{")
    end = caddyfile.index("    }", start)
    return caddyfile[start:end]


class TestLocalMarimoImageSplit:
    def test_compose_declares_distinct_local_services(self) -> None:
        compose = _read(BACKEND_SERVICES_DIR / "compose.yaml")

        assert "  marimo-dashboard:" in compose
        assert "      target: dashboard" in compose
        assert "    container_name: marimo-dashboard" in compose
        assert "  marimo-codex-workspace:" in compose
        assert "      target: codex-workspace" in compose
        assert "    container_name: marimo-codex-workspace" in compose
        assert '      - "127.0.0.1:2719:2718"' in compose

    def test_dashboard_service_uses_curated_read_only_notebooks(self) -> None:
        compose = _read(BACKEND_SERVICES_DIR / "compose.yaml")
        dashboard = _service_block(
            compose,
            "marimo-dashboard",
            "marimo-codex-workspace",
        )

        assert "      DEVELOPMENT_LOCATION: local" in dashboard
        assert "      MARIMO_WORKSPACE_KIND: dashboard" in dashboard
        assert "      MARIMO_NOTEBOOKS_DIR: /opt/marimo/notebooks" in dashboard
        assert (
            "      DAGSTER_GRAPHQL_URL: "
            "${DAGSTER_GRAPHQL_URL:-"
            "http://dagster-webserver-guest:3000/dagster-webserver/guest/graphql}"
        ) in dashboard
        assert "      - ./marimo/notebooks:/opt/marimo/notebooks:ro" in dashboard

    def test_research_workspace_uses_separate_writable_workspace(self) -> None:
        compose = _read(BACKEND_SERVICES_DIR / "compose.yaml")
        workspace = _service_block(compose, "marimo-codex-workspace", "authentication")

        assert "      DEVELOPMENT_LOCATION: local" in workspace
        assert "      MARIMO_WORKSPACE_KIND: codex-research" in workspace
        assert "      MARIMO_WORKSPACE_ROOT: /workspace" in workspace
        assert "      MARIMO_NOTEBOOKS_DIR: /workspace/notebooks" in workspace
        assert (
            "      DAGSTER_GRAPHQL_URL: "
            "${DAGSTER_GRAPHQL_URL:-"
            "http://dagster-webserver-guest:3000/dagster-webserver/guest/graphql}"
        ) in workspace
        assert "      - ./marimo/research-workspace:/workspace" in workspace

    def test_dockerfile_keeps_dashboard_and_workspace_commands_separate(self) -> None:
        dockerfile = _read(MARIMO_DIR / "Dockerfile")
        dashboard_start = dockerfile.index("FROM runtime AS dashboard")
        deploy_start = dockerfile.index("FROM dashboard AS deploy")
        workspace_start = dockerfile.index("FROM runtime AS codex-workspace")

        dashboard_target = dockerfile[dashboard_start:deploy_start]
        workspace_target = dockerfile[workspace_start:]

        assert '"uvicorn", "marimoserver.main:app"' in dashboard_target
        assert '"marimo", "edit"' not in dashboard_target
        assert "MARIMO_WORKSPACE_KIND=dashboard" in dashboard_target
        assert '"marimo", "edit", "/workspace/notebooks"' in workspace_target
        assert "MARIMO_WORKSPACE_KIND=codex-research" in workspace_target

    def test_research_workspace_bakes_agent_guidance(self) -> None:
        agents = _read(MARIMO_DIR / "research-workspace" / "AGENTS.md")
        dockerfile = _read(MARIMO_DIR / "Dockerfile")

        assert "COPY research-workspace/ /workspace/" in dockerfile
        assert "local notebook research only" in agents
        assert "Do not access deployed AWS services" in agents
        assert "Write proposed issue drafts under `issue-drafts/`" in agents
        assert "Deployed Codex execution is deferred" in agents

    def test_caddy_proxies_marimo_static_assets_without_auth(self) -> None:
        caddyfile = _read(BACKEND_SERVICES_DIR / "caddy" / "Caddyfile")
        protected_marimo = _caddy_matcher_block(caddyfile, "@protectedMarimo")

        assert "not path /marimo/health" in protected_marimo
        assert "not header Connection *Upgrade*" in protected_marimo
        assert "not path /marimo/*/assets/*" in protected_marimo
        assert "/marimo/*/favicon.ico" in protected_marimo
        assert "/marimo/*/manifest.json" in protected_marimo
        assert "reverse_proxy /marimo* {$MARIMO_SERVER}" in caddyfile
