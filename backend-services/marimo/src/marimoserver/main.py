"""
Marimo notebook server — FastAPI wrapper.

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

import os
from pathlib import Path

import marimo
from fastapi import FastAPI
from starlette.responses import HTMLResponse, JSONResponse

NOTEBOOKS_DIR = Path(os.environ.get("MARIMO_NOTEBOOKS_DIR", "notebooks"))

app = FastAPI(title="Marimo Notebook Server")


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
            server = server.with_app(path=f"/{name}", root=str(notebook))
            app_names.append(name)


@app.get("/")
async def index() -> HTMLResponse:
    """Landing page listing all available notebooks."""
    items = "\n".join(
        f'        <li><a href="/{name}/">{name}</a></li>' for name in app_names
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
