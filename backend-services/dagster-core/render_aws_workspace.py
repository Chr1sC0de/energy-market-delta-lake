"""Render the AWS Dagster workspace from the code-location manifest."""

import argparse
import sys
import tomllib
from pathlib import Path


def render_workspace(manifest_path: Path) -> str:
    """Render a Dagster workspace YAML document from a TOML manifest."""
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    raw_locations = manifest.get("locations")
    if not isinstance(raw_locations, list) or len(raw_locations) == 0:
        raise ValueError("code-location manifest must contain at least one location")

    lines = ["load_from:"]
    for index, raw_location in enumerate(raw_locations):
        if not isinstance(raw_location, dict):
            raise ValueError(f"location #{index + 1} must be a table")

        cloud_map_name = _required_str(raw_location, "cloud_map_name", index)
        location_name = _required_str(raw_location, "name", index)
        port = _required_int(raw_location, "port", index)
        lines.extend(
            [
                "  - grpc_server:",
                f"      host: {cloud_map_name}.dagster",
                f"      port: {port}",
                f'      location_name: "{location_name}"',
            ]
        )

    return "\n".join(lines) + "\n"


def _required_str(
    raw_location: dict[object, object],
    key: str,
    index: int,
) -> str:
    value = raw_location.get(key)
    if not isinstance(value, str) or value == "":
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


def main(argv: list[str] | None = None) -> int:
    """Run the workspace renderer CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "manifest",
        nargs="?",
        default="code-locations.aws.toml",
        type=Path,
        help="Path to the AWS code-location manifest.",
    )
    args = parser.parse_args(argv)
    sys.stdout.write(render_workspace(args.manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
