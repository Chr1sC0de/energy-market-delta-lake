"""Unit tests for the aemo-etl Docker runtime install surface."""

from pathlib import Path


def test_dockerfile_installs_runtime_dependencies_from_frozen_lock_export() -> None:
    project_root = Path(__file__).resolve().parents[2]
    dockerfile = (project_root / "Dockerfile").read_text(encoding="utf-8")

    assert (
        "uv export --frozen --format requirements-txt --no-dev "
        "--no-emit-project --output-file requirements.txt"
    ) in dockerfile
    assert "uv pip install --system --prefix=/install -r requirements.txt" in dockerfile
    assert "uv pip install --system --prefix=/install --no-deps ." in dockerfile
    assert "uv pip install . --system" not in dockerfile
