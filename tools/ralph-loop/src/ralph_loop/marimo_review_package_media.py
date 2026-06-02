import argparse
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

DEFAULT_SERVER_START_TIMEOUT_SECONDS = 60
DEFAULT_HEALTHCHECK_TIMEOUT_SECONDS = 1
DEFAULT_REVIEW_TIMEOUT_SECONDS = 180


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    marimo_root = args.marimo_root.resolve()
    if not marimo_root.is_dir():
        _emit_error(f"Marimo root does not exist: {marimo_root}")
        return 1

    routes = tuple(args.route)
    if not routes:
        _emit_error("at least one --route is required")
        return 1

    artifact_dir = args.artifact_dir.resolve()
    artifact_dir.mkdir(parents=True, exist_ok=True)
    env = _marimo_review_env()
    try:
        if args.base_url:
            _run_dashboard_review(
                marimo_root=marimo_root,
                base_url=args.base_url,
                artifact_dir=artifact_dir,
                routes=routes,
                timeout_seconds=args.review_timeout_seconds,
                env=env,
            )
            return 0

        with _serve_marimo(
            marimo_root=marimo_root,
            timeout_seconds=args.server_start_timeout_seconds,
            env=env,
        ) as base_url:
            _run_dashboard_review(
                marimo_root=marimo_root,
                base_url=base_url,
                artifact_dir=artifact_dir,
                routes=routes,
                timeout_seconds=args.review_timeout_seconds,
                env=env,
            )
    except (
        RuntimeError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as error:
        _emit_error(str(error))
        return 1
    return 0


def _marimo_review_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("MARIMO_NOTEBOOKS_DIR", "notebooks")
    env.setdefault("AWS_ENDPOINT_URL", "http://localhost:4566")
    env.setdefault("AWS_MAX_ATTEMPTS", "1")
    env.setdefault("AWS_DEFAULT_REGION", "ap-southeast-2")
    env.setdefault("AWS_ACCESS_KEY_ID", "test")
    env.setdefault("AWS_SECRET_ACCESS_KEY", "test")
    return env


@contextmanager
def _serve_marimo(
    *,
    marimo_root: Path,
    timeout_seconds: int,
    env: dict[str, str],
) -> Iterator[str]:
    port = _free_loopback_port()
    base_url = f"http://127.0.0.1:{port}"
    command = [
        "uv",
        "run",
        "uvicorn",
        "marimoserver.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    process = subprocess.Popen(command, cwd=marimo_root, env=env)
    try:
        _wait_for_health(base_url, process=process, timeout_seconds=timeout_seconds)
        print(f"started Marimo Review package media server: {base_url}", flush=True)
        yield base_url
    finally:
        _terminate_process(process)


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_health(
    base_url: str,
    *,
    process: subprocess.Popen[bytes],
    timeout_seconds: int,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    health_url = f"{base_url}/health"
    while time.monotonic() < deadline:
        returncode = process.poll()
        if returncode is not None:
            raise RuntimeError(
                "Marimo Review package media server exited before healthcheck "
                f"passed with status {returncode}."
            )
        try:
            with urllib.request.urlopen(
                health_url,
                timeout=DEFAULT_HEALTHCHECK_TIMEOUT_SECONDS,
            ) as response:
                if response.status < 400:
                    return
        except (OSError, urllib.error.URLError):
            time.sleep(0.25)
    raise RuntimeError(
        "Timed out waiting for Marimo Review package media server healthcheck: "
        f"{health_url}"
    )


def _run_dashboard_review(
    *,
    marimo_root: Path,
    base_url: str,
    artifact_dir: Path,
    routes: tuple[str, ...],
    timeout_seconds: int,
    env: dict[str, str],
) -> None:
    command = [
        "uv",
        "run",
        "--with",
        "playwright",
        "python",
        "scripts/review_promoted_dashboards.py",
        "--base-url",
        base_url,
        "--artifact-dir",
        str(artifact_dir),
        "--videos",
    ]
    for route in routes:
        command.extend(["--route", route])
    subprocess.run(
        command,
        cwd=marimo_root,
        env=env,
        check=True,
        timeout=timeout_seconds,
    )


def _terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def _emit_error(message: str) -> None:
    print(f"ralph Marimo Review package media: {message}", file=sys.stderr)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Record Marimo Review package media with a Ralph-owned server."
    )
    parser.add_argument(
        "--marimo-root",
        type=Path,
        required=True,
        help="Marimo Subproject root to serve and review.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        required=True,
        help="Directory for .webm artifacts.",
    )
    parser.add_argument(
        "--route",
        action="append",
        default=[],
        help="Marimo route to review; may be repeated.",
    )
    parser.add_argument(
        "--base-url",
        help="Use an already-running Marimo server instead of starting one.",
    )
    parser.add_argument(
        "--server-start-timeout-seconds",
        type=int,
        default=DEFAULT_SERVER_START_TIMEOUT_SECONDS,
        help="Seconds to wait for the Ralph-owned Marimo server healthcheck.",
    )
    parser.add_argument(
        "--review-timeout-seconds",
        type=int,
        default=DEFAULT_REVIEW_TIMEOUT_SECONDS,
        help="Seconds to allow the dashboard review subprocess.",
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    raise SystemExit(main())
