import socket
import subprocess
import time

import requests

LOCALSTACK_IMAGE = "localstack/localstack"
LOCALSTACK_PORT = 4566
LOCALSTACK_HEALTH_PATH = "_localstack/health"
LOCALSTACK_READY_TIMEOUT = 60  # seconds
LOCALSTACK_READY_POLL_INTERVAL = 1  # seconds


def podman(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["podman", *args],
        check=True,
        capture_output=True,
        text=True,
    )


def container_ip(container_name: str) -> str:
    result = podman(
        "inspect",
        container_name,
        "--format",
        "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
    )
    ip = result.stdout.strip()
    if not ip:
        raise RuntimeError(
            f"Could not determine IP for container {container_name!r}. "
            "Ensure it is running on the podman network."
        )
    return ip


def get_unused_port() -> int:

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]

    return port


def wait_for_localstack(endpoint: str, timeout: int, interval: float) -> None:
    deadline = time.monotonic() + timeout
    url = f"{endpoint}/{LOCALSTACK_HEALTH_PATH}"
    last_exc: Exception = RuntimeError("timed out before first attempt")
    while time.monotonic() < deadline:
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                return
        except requests.RequestException as exc:
            last_exc = exc
        time.sleep(interval)
    raise TimeoutError(
        f"LocalStack at {endpoint} did not become healthy within {timeout}s. "
        f"Last error: {last_exc}"
    )
