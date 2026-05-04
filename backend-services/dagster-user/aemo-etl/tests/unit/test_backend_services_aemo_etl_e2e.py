"""Unit tests for the backend-services AEMO ETL e2e stack command."""

import socket
import runpy
from collections.abc import Callable, Mapping
from pathlib import Path


def load_e2e_command_module() -> dict[str, object]:
    """Load the extensionless backend-services command as a Python module."""
    script_path = (
        Path(__file__).resolve().parents[4] / "scripts/aemo-etl-e2e"
    )
    return runpy.run_path(
        str(script_path),
        run_name="backend_services_aemo_etl_e2e",
    )


def get_callable(
    module_globals: Mapping[str, object],
    name: str,
) -> Callable[..., object]:
    """Return a callable loaded from the command module."""
    value = module_globals[name]
    assert callable(value)
    return value


def get_exception_class(
    module_globals: Mapping[str, object],
    name: str,
) -> type[Exception]:
    """Return an exception class loaded from the command module."""
    value = module_globals[name]
    assert isinstance(value, type)
    assert issubclass(value, Exception)
    return value


def test_podman_socket_is_derived_from_xdg_runtime_dir(tmp_path: Path) -> None:
    """The command uses the current user runtime dir, not a fixed UID path."""
    module = load_e2e_command_module()
    runtime_dir = tmp_path / "runtime"
    socket_dir = runtime_dir / "podman"
    socket_dir.mkdir(parents=True)
    socket_path = socket_dir / "podman.sock"

    with socket.socket(socket.AF_UNIX) as podman_socket:
        podman_socket.bind(str(socket_path))

        podman_socket_from_xdg_runtime_dir = get_callable(
            module,
            "podman_socket_from_xdg_runtime_dir",
        )
        assert (
            podman_socket_from_xdg_runtime_dir(
                {"XDG_RUNTIME_DIR": str(runtime_dir)}
            )
            == socket_path
        )


def test_podman_socket_fails_when_xdg_runtime_dir_missing() -> None:
    """The command fails before falling back to a hard-coded socket path."""
    module = load_e2e_command_module()
    podman_socket_from_xdg_runtime_dir = get_callable(
        module,
        "podman_socket_from_xdg_runtime_dir",
    )
    command_error = get_exception_class(module, "CommandError")

    try:
        podman_socket_from_xdg_runtime_dir({})
    except command_error as error:
        assert "XDG_RUNTIME_DIR" in str(error)
    else:
        raise AssertionError("missing XDG_RUNTIME_DIR did not fail")


def test_image_selection_reuses_existing_images_by_default(tmp_path: Path) -> None:
    """Only missing image tags are built unless an explicit rebuild is requested."""
    module = load_e2e_command_module()
    image_spec = get_callable(module, "ImageSpec")
    select_images_to_build = get_callable(module, "select_images_to_build")
    image_specs = (
        image_spec("postgres", "localhost/e2e_postgres:latest", tmp_path),
        image_spec("localstack", "localhost/e2e_localstack:latest", tmp_path),
    )

    selected = select_images_to_build(
        {"localhost/e2e_postgres:latest"},
        image_specs=image_specs,
        rebuild=False,
    )
    rebuild_selected = select_images_to_build(
        {"localhost/e2e_postgres:latest", "localhost/e2e_localstack:latest"},
        image_specs=image_specs,
        rebuild=True,
    )

    assert isinstance(selected, tuple)
    assert isinstance(rebuild_selected, tuple)
    assert [getattr(spec, "name") for spec in selected] == ["localstack"]
    assert rebuild_selected == image_specs


def test_generated_dagster_config_uses_e2e_socket_and_network(tmp_path: Path) -> None:
    """Run workers use the generated e2e network and current Podman socket."""
    module = load_e2e_command_module()
    render_dagster_yaml = get_callable(module, "render_dagster_yaml")
    socket_path = tmp_path / "runtime/podman/podman.sock"

    config = render_dagster_yaml(
        aemo_etl_image="localhost/aemo-etl-e2e_aemo-etl:latest",
        podman_socket=socket_path,
    )

    assert isinstance(config, str)
    assert str(socket_path) in config
    assert "localhost/aemo-etl-e2e_aemo-etl:latest" in config
    assert "network: \"aemo-etl-e2e-dagster-network\"" in config
    assert "/" + "/".join(("run", "user", "1000")) not in config


def test_generated_compose_is_isolated_e2e_stack(tmp_path: Path) -> None:
    """The generated compose file omits the broader developer stack services."""
    module = load_e2e_command_module()
    render_compose_yaml = get_callable(module, "render_compose_yaml")
    images = {
        "postgres": "localhost/aemo-etl-e2e_postgres:latest",
        "localstack": "localhost/aemo-etl-e2e_localstack:latest",
        "aemo-etl": "localhost/aemo-etl-e2e_aemo-etl:latest",
        "dagster-core": "localhost/aemo-etl-e2e_dagster-core:latest",
    }

    compose = render_compose_yaml(
        images=images,
        seed_root=tmp_path / "seed",
        podman_socket=tmp_path / "runtime/podman/podman.sock",
        dagster_config_file=tmp_path / "dagster.yaml",
        workspace_file=tmp_path / "workspace.yaml",
        webserver_port=3001,
        raw_latest_count=10,
        zip_latest_count=3,
    )

    assert isinstance(compose, str)
    assert "name: aemo-etl-e2e" in compose
    assert "container_name: aemo-etl-e2e-dagster-webserver" in compose
    assert "aemo-etl-seed-localstack:" in compose
    assert "dagster-webserver-admin" not in compose
    assert "dagster-webserver-guest" not in compose
    assert "authentication:" not in compose
    assert "marimo:" not in compose
    assert "caddy:" not in compose
