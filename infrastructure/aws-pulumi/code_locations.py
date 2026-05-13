"""AWS Dagster code-location manifest loading and naming helpers."""

import re
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CODE_LOCATION_MANIFEST = (
    _REPO_ROOT / "backend-services" / "dagster-core" / "code-locations.aws.toml"
)

_RESOURCE_SUFFIX_PATTERN = re.compile(r"[^a-z0-9-]+")


@dataclass(frozen=True, kw_only=True)
class DagsterCodeLocation:
    """Manifest declaration for one AWS Dagster gRPC code location."""

    name: str
    module: str
    port: int
    cloud_map_name: str
    source_path: Path
    image_repository: str
    is_default: bool = False
    cpu: str = "256"
    memory: str = "1024"
    container_name: str = "dagster-grpc"
    grpc_timeout_seconds: str = "300"
    log_stream_prefix: str = ""

    @property
    def resource_suffix(self) -> str:
        """Return the Pulumi-safe resource suffix for this location."""
        suffix = _RESOURCE_SUFFIX_PATTERN.sub("-", self.name.lower()).strip("-")
        if suffix == "":
            raise ValueError(f"code location {self.name!r} has no resource suffix")
        return suffix

    @property
    def source_dir(self) -> Path:
        """Return the absolute Docker build context path."""
        return _REPO_ROOT / self.source_path

    @property
    def workspace_host(self) -> str:
        """Return the Cloud Map hostname used by the Dagster workspace."""
        return f"{self.cloud_map_name}.dagster"

    @property
    def effective_log_stream_prefix(self) -> str:
        """Return the manifest log-stream prefix or the location default."""
        if self.log_stream_prefix != "":
            return self.log_stream_prefix
        return f"dagster-{self.resource_suffix}-user-code"


def load_code_locations(
    manifest_path: Path | str = DEFAULT_CODE_LOCATION_MANIFEST,
) -> tuple[DagsterCodeLocation, ...]:
    """Load AWS Dagster code locations from a TOML manifest."""
    path = Path(manifest_path)
    manifest = tomllib.loads(path.read_text(encoding="utf-8"))
    raw_locations = manifest.get("locations")
    if not isinstance(raw_locations, list) or len(raw_locations) == 0:
        raise ValueError("code-location manifest must contain at least one location")

    locations = tuple(
        _parse_location(raw_location, index)
        for index, raw_location in enumerate(raw_locations)
    )
    _validate_locations(locations)
    return locations


def default_code_location(
    locations: tuple[DagsterCodeLocation, ...],
) -> DagsterCodeLocation:
    """Return the one manifest location marked as the default."""
    default_locations = [location for location in locations if location.is_default]
    if len(default_locations) != 1:
        raise ValueError("code-location manifest must define exactly one default")
    return default_locations[0]


def render_workspace_yaml(locations: tuple[DagsterCodeLocation, ...]) -> str:
    """Render Dagster workspace YAML from manifest locations."""
    lines = ["load_from:"]
    for location in locations:
        lines.extend(
            [
                "  - grpc_server:",
                f"      host: {location.workspace_host}",
                f"      port: {location.port}",
                f'      location_name: "{location.name}"',
            ]
        )
    return "\n".join(lines) + "\n"


def user_code_component_name(
    resource_name: str,
    location: DagsterCodeLocation,
    default_location: DagsterCodeLocation,
) -> str:
    """Return the top-level Pulumi component name for a user-code location."""
    if location.name == default_location.name:
        return f"{resource_name}-user-code"
    return f"{resource_name}-user-code-{location.resource_suffix}"


def user_code_ecr_repository_resource_name(
    resource_name: str,
    location: DagsterCodeLocation,
) -> str:
    """Return the Pulumi ECR repository resource name for a user-code location."""
    repository_slug = f"{resource_name}/{location.image_repository}".replace("/", "-")
    return f"{resource_name}-{repository_slug}"


def user_code_task_definition_resource_name(component_name: str) -> str:
    """Return the Pulumi ECS task-definition resource name for user code."""
    return f"{component_name}-user-code-task-def"


def user_code_ecs_service_resource_name(component_name: str) -> str:
    """Return the Pulumi ECS service resource name for user code."""
    return f"{component_name}-user-code-service"


def _parse_location(
    raw_location: object,
    index: int,
) -> DagsterCodeLocation:
    if not isinstance(raw_location, dict):
        raise ValueError(f"location #{index + 1} must be a table")

    name = _required_str(raw_location, "name", index)
    source_path = _relative_path(_required_str(raw_location, "source_path", index))
    return DagsterCodeLocation(
        name=name,
        module=_required_str(raw_location, "module", index),
        port=_required_int(raw_location, "port", index),
        cloud_map_name=_required_str(raw_location, "cloud_map_name", index),
        source_path=source_path,
        image_repository=_optional_str(
            raw_location,
            "image_repository",
            f"dagster/user-code/{name}",
            index,
        ),
        is_default=_optional_bool(raw_location, "default", False, index),
        cpu=_optional_str(raw_location, "cpu", "256", index),
        memory=_optional_str(raw_location, "memory", "1024", index),
        container_name=_optional_str(
            raw_location, "container_name", "dagster-grpc", index
        ),
        grpc_timeout_seconds=_optional_str(
            raw_location,
            "grpc_timeout_seconds",
            "300",
            index,
        ),
        log_stream_prefix=_optional_str(
            raw_location,
            "log_stream_prefix",
            "",
            index,
            allow_empty=True,
        ),
    )


def _required_str(
    raw_location: dict[object, object],
    key: str,
    index: int,
) -> str:
    value = raw_location.get(key)
    if not isinstance(value, str) or value == "":
        raise ValueError(f"location #{index + 1} must define non-empty {key}")
    return value


def _optional_str(
    raw_location: dict[object, object],
    key: str,
    default: str,
    index: int,
    *,
    allow_empty: bool = False,
) -> str:
    value = raw_location.get(key, default)
    if not isinstance(value, str) or (not allow_empty and value == ""):
        raise ValueError(f"location #{index + 1} must define non-empty {key}")
    return value


def _required_int(
    raw_location: dict[object, object],
    key: str,
    index: int,
) -> int:
    value = raw_location.get(key)
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"location #{index + 1} must define positive integer {key}")
    return value


def _optional_bool(
    raw_location: dict[object, object],
    key: str,
    default: bool,
    index: int,
) -> bool:
    value = raw_location.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"location #{index + 1} must define boolean {key}")
    return value


def _relative_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"code-location source_path must be repo-relative: {raw_path}")
    return path


def _validate_locations(locations: tuple[DagsterCodeLocation, ...]) -> None:
    default_code_location(locations)
    _validate_unique("code-location names", (location.name for location in locations))
    _validate_unique(
        "code-location resource suffixes",
        (location.resource_suffix for location in locations),
    )
    _validate_unique(
        "code-location Cloud Map names",
        (location.cloud_map_name for location in locations),
    )
    _validate_unique(
        "code-location image repositories",
        (location.image_repository for location in locations),
    )


def _validate_unique(label: str, values: Iterable[str]) -> None:
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{label} must be strings")
        if value in seen:
            raise ValueError(f"duplicate {label}: {value}")
        seen.add(value)
