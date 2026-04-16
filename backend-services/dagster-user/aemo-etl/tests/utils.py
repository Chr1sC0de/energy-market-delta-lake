import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Protocol

import requests

GBB_DATA_DIR = Path(os.environ["HOME"]) / "localstack-landing-download/bronze/gbb"
LOCALSTACK_IMAGE = "localstack/localstack"
LOCALSTACK_PORT = 4566
LOCALSTACK_HEALTH_PATH = "_localstack/health"
LOCALSTACK_READY_TIMEOUT = 60  # seconds
LOCALSTACK_READY_POLL_INTERVAL = 1  # seconds


class MakeBucketProtocol(Protocol):
    def __call__(self, bucket_name: str, random_suffix: bool = True) -> str: ...


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
        port: int = s.getsockname()[1]

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
