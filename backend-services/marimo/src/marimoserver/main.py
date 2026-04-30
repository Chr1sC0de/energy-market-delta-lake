"""FastAPI wrapper for the marimo notebook server.

Serves marimo notebooks from the ``notebooks/`` directory using marimo's
built-in ASGI integration (``marimo.create_asgi_app``).  A ``/health``
endpoint is exposed for container healthchecks.

The app is designed to be served behind a reverse proxy (Caddy) which
strips the ``/marimo`` prefix before forwarding traffic here, so all
routes inside the container are rooted at ``/``.

Notebook discovery uses ``with_app`` in a loop so each ``.py`` file in
the notebooks directory is mounted at ``/<stem>``.  A
``with_dynamic_directory`` approach would be preferable for hot-reload,
but marimo does not support ``path="/"`` for dynamic directories.
"""

from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import Any

import marimo
from fastapi import FastAPI
from starlette.responses import HTMLResponse, JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

NOTEBOOKS_DIR = Path(os.environ.get("MARIMO_NOTEBOOKS_DIR", "notebooks"))

# Ensure font MIME types are registered — Python's mimetypes module does not
# always include woff/woff2 depending on the host OS, causing uvicorn to fall
# back to text/plain which the browser rejects for font loading.
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")


# TODO: add test coverage for the following class
class MimeTypeFixMiddleware:  # pragma: no cover
    """Override incorrect MIME types for web font files.

    uvicorn's StaticFiles falls back to ``text/plain`` for ``.woff`` and
    ``.woff2`` on systems where the OS MIME database does not include these
    types.  Browsers refuse to apply fonts served with the wrong MIME type,
    causing the notebook UI to render with fallback fonts.
    """

    _OVERRIDES: dict[str, str] = {
        ".woff2": "font/woff2",
        ".woff": "font/woff",
    }

    def __init__(self, app: ASGIApp) -> None:
        """Store the wrapped ASGI app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Patch font response MIME types before sending HTTP responses."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path: str = scope.get("path", "")
        suffix = Path(path).suffix.lower()
        override = self._OVERRIDES.get(suffix)

        if override is None:
            await self.app(scope, receive, send)
            return

        async def send_with_fixed_mime(message: Any) -> None:  # noqa: ANN401
            if message["type"] == "http.response.start":
                headers = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower() != b"content-type"
                ]
                headers.append((b"content-type", override.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_fixed_mime)


app = FastAPI(title="Marimo Notebook Server")
app.add_middleware(MimeTypeFixMiddleware)  # type: ignore[arg-type]


@app.get("/health")
async def health() -> JSONResponse:
    """Liveness / readiness probe for container orchestrators."""
    return JSONResponse(content={"status": "ok"})


# ---------------------------------------------------------------------------
# Discover notebooks and mount each one as a marimo sub-app.
# ---------------------------------------------------------------------------
server = marimo.create_asgi_app()
app_names: list[str] = []

if NOTEBOOKS_DIR.is_dir():
    for notebook in sorted(NOTEBOOKS_DIR.iterdir()):
        if notebook.suffix == ".py":
            name = notebook.stem
            server = server.with_app(path=f"/marimo/{name}", root=str(notebook))
            app_names.append(name)


@app.get("/marimo")
async def index() -> HTMLResponse:
    """Landing page listing all available notebooks."""
    items = "\n".join(
        f'        <li><a href="marimo/{name}/">{name}</a></li>' for name in app_names
    )
    html = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marimo Notebooks</title>
    <style>
        body {{ font-family: sans-serif; max-width: 600px; margin: 80px auto; padding: 0 20px; color: #333; }}
        h1 {{ color: #1a73e8; }}
        a {{ color: #1a73e8; }}
    </style>
</head>
<body>
    <h1>Marimo Notebooks</h1>
    <p>Available notebooks:</p>
    <ul>
{items}
    </ul>
</body>
</html>"""
    return HTMLResponse(content=html)


app.mount("/", server.build())
