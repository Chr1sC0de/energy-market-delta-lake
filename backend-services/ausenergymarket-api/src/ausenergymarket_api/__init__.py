# pyright: reportMissingTypeStubs=false
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from ausenergymarket_api import dashboards, plots
from ausenergymarket_api.configurations import (
    DEVELOPMENT_LOCATION,
    templates,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


if DEVELOPMENT_LOCATION == "local":
    from fastapi.middleware.cors import CORSMiddleware

    origins = [
        "https://0.0.0.0:3000",
        "https://localhost:3000",
        "http://0.0.0.0:3000",
        "http://localhost:3000",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Type", "Authorization"],
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


app.include_router(plots.gas.router, prefix="/plots/gas")
app.include_router(dashboards.gas.router, prefix="/dashboards/gas")
