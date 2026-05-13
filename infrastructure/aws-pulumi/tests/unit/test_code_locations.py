"""Tests for AWS Dagster code-location manifest handling."""

import importlib.util
from pathlib import Path
from types import ModuleType

from code_locations import (
    default_code_location,
    load_code_locations,
    render_workspace_yaml,
    user_code_component_name,
    user_code_ecs_service_resource_name,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
DAGSTER_CORE = REPO_ROOT / "backend-services" / "dagster-core"
TWO_LOCATION_MANIFEST = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "code-locations-two-location.toml"
)


def _core_workspace_renderer() -> ModuleType:
    renderer_path = DAGSTER_CORE / "render_aws_workspace.py"
    spec = importlib.util.spec_from_file_location(
        "render_aws_workspace",
        renderer_path,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_default_manifest_keeps_aemo_etl_location_contract() -> None:
    locations = load_code_locations()
    default_location = default_code_location(locations)

    assert len(locations) == 1
    assert default_location.name == "aemo-etl"
    assert default_location.module == "aemo_etl.definitions"
    assert default_location.port == 4000
    assert default_location.cloud_map_name == "aemo-etl"
    assert default_location.workspace_host == "aemo-etl.dagster"


def test_checked_in_workspace_matches_manifest_render() -> None:
    locations = load_code_locations()
    workspace = (DAGSTER_CORE / "workspace.aws.yaml").read_text(encoding="utf-8")

    assert render_workspace_yaml(locations) == workspace


def test_core_renderer_matches_pulumi_workspace_rendering() -> None:
    renderer = _core_workspace_renderer()
    locations = load_code_locations(TWO_LOCATION_MANIFEST)

    assert renderer.render_workspace(TWO_LOCATION_MANIFEST) == render_workspace_yaml(
        locations
    )


def test_two_location_fixture_renders_distinct_workspace_entries() -> None:
    locations = load_code_locations(TWO_LOCATION_MANIFEST)
    rendered = render_workspace_yaml(locations)

    assert 'location_name: "aemo-etl"' in rendered
    assert "host: aemo-etl.dagster" in rendered
    assert "port: 4000" in rendered
    assert 'location_name: "fixture-etl"' in rendered
    assert "host: fixture-etl.dagster" in rendered
    assert "port: 4100" in rendered


def test_manifest_naming_keeps_default_user_code_service_name() -> None:
    locations = load_code_locations(TWO_LOCATION_MANIFEST)
    default_location = default_code_location(locations)
    service_names = {
        location.name: user_code_ecs_service_resource_name(
            user_code_component_name("test-energy-market", location, default_location)
        )
        for location in locations
    }

    assert service_names == {
        "aemo-etl": "test-energy-market-user-code-user-code-service",
        "fixture-etl": "test-energy-market-user-code-fixture-etl-user-code-service",
    }
