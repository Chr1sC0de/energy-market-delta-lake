from collections.abc import Awaitable
from os import environ
from secrets import token_urlsafe
from time import time
from typing import Any, Callable, cast

import requests
from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from fastapi import APIRouter, FastAPI, HTTPException, Request
from jose import jwk, jwt
from jose.utils import base64url_decode
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)

app = FastAPI()

router = APIRouter()

app.add_middleware(SessionMiddleware, secret_key=token_urlsafe(32))


def _normalise_website_root_url(raw: str) -> str:
    """Normalise WEBSITE_ROOT_URL to a scheme-qualified, slash-free base URL.

    Handles three input forms:
      - Already correct: "https://example.com"     → "https://example.com"
      - Plain HTTP:      "http://example.com"       → "https://example.com"
      - No scheme:       "example.com"              → "https://example.com"

    Trailing slashes are always stripped so callers can safely append a path
    without producing double-slashes.

    This guards against the config being set without a scheme, which would
    cause Starlette to treat the redirect as relative and produce a malformed
    URL such as:
      /oauth2/…/authorize/ausenergymarketdata.com/dagster-webserver/admin
    """
    url = raw.rstrip("/")
    if url.startswith("http://"):
        # Upgrade plain HTTP to HTTPS — production must always use TLS.
        return "https://" + url[len("http://") :]
    if not url.startswith("https://"):
        # No scheme at all — prepend https://.
        return f"https://{url}"
    return url


_website_root_url: str = _normalise_website_root_url(environ["WEBSITE_ROOT_URL"])


oauth = OAuth()


_ = oauth.register(
    name="oidc",
    client_id=environ["COGNITO_DAGSTER_AUTH_CLIENT_ID"],
    server_metadata_url=environ["COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL"],
    client_secret=environ["COGNITO_DAGSTER_AUTH_CLIENT_SECRET"],
    client_kwargs={"scope": "openid email phone"},
)

oidc = cast(StarletteOAuth2App, oauth.oidc)

authorize_redirect = cast(
    Callable[..., Awaitable[RedirectResponse]], oidc.authorize_redirect
)

# JSON Web Key
JWK = dict[str, str]

# JSON Web Key Set
JWKS = dict[str, list[JWK]]


def get_user_pool_token_signing_key() -> JWKS:
    return cast(
        JWKS,
        requests.get(environ["COGNITO_TOKEN_SIGNING_KEY_URL"]).json(),
    )


def get_hmac_key_data(token: str, jwks: JWKS) -> JWK | None:
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key


def verify_jwt(token: str) -> bool:
    try:
        jwks = get_user_pool_token_signing_key()

        assert jwks is not None

        hmac_key = get_hmac_key_data(token, jwks)

        if not hmac_key:
            raise ValueError("No pubic key found!")

        hmac_key_data = cast(JWK, get_hmac_key_data(token, jwks))

        hmac_key = jwk.construct(hmac_key_data)

        message, encoded_signature = token.rsplit(".", 1)

        return hmac_key.verify(
            message.encode(), base64url_decode(encoded_signature.encode())
        )
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token, {e}",
        )


def clear_session(session: dict[str, Any]) -> None:
    session.pop("user", None)
    session.pop("token_type", None)
    session.pop("access_token", None)
    session.pop("expires_at", None)


def _validate_session(request: Request) -> JSONResponse:
    """Shared session validation logic for protected service endpoints."""
    if any(
        field not in request.session
        for field in ("user", "token_type", "access_token", "expires_at")
    ):
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    if time() >= request.session["expires_at"]:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    if verify_jwt(
        cast(
            str,
            request.session["access_token"],
        )
    ):
        return JSONResponse(
            status_code=HTTP_200_OK, content={"status": "authorized access"}
        )
    else:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )


def _build_redirect_uri(request: Request, route_name: str) -> str:
    """Build a redirect URI, rewriting http→https for non-localhost hosts."""
    redirect_uri = str(request.url_for(route_name))
    if "localhost" not in redirect_uri:
        redirect_uri = redirect_uri.replace("http", "https", 1)
    return redirect_uri


async def _authorize_callback(request: Request, redirect_path: str) -> Response:
    """Shared OIDC callback logic — exchanges code for token, sets session."""
    try:
        token = await oidc.authorize_access_token(request)
        request.session["user"] = token["userinfo"]
        request.session["token_type"] = token["token_type"]
        request.session["access_token"] = token["access_token"]
        request.session["expires_at"] = token["expires_at"]
        return RedirectResponse(f"{_website_root_url}{redirect_path}")
    except Exception as e:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": str(e)},
        )


# ---------------------------------------------------------------------------
# Dagster webserver admin routes
# ---------------------------------------------------------------------------


@router.get("/oauth2/dagster-webserver/admin/validate")
async def oauth2_dagster_webserver_validate(request: Request) -> JSONResponse:
    request.session

    login_redirect_uri = str(request.url_for("oauth2_dagster_webserver_login"))
    if "localhost" not in login_redirect_uri:
        login_redirect_uri = login_redirect_uri.replace("http", "https", 1)

    return _validate_session(request)


@router.get("/dagster-webserver/admin/login")
async def oauth2_dagster_webserver_login(request: Request) -> RedirectResponse:
    redirect_uri = _build_redirect_uri(request, "oauth2_dagster_webserver_authorize")
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get("/oauth2/dagster-webserver/admin/authorize", response_model=None)
async def oauth2_dagster_webserver_authorize(
    request: Request,
) -> Response:
    return await _authorize_callback(request, "/dagster-webserver/admin")


# ---------------------------------------------------------------------------
# Marimo notebook server routes
# ---------------------------------------------------------------------------


@router.get("/oauth2/marimo/validate")
async def oauth2_marimo_validate(request: Request) -> JSONResponse:
    return _validate_session(request)


@router.get("/marimo/login")
async def oauth2_marimo_login(request: Request) -> RedirectResponse:
    redirect_uri = _build_redirect_uri(request, "oauth2_marimo_authorize")
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get("/oauth2/marimo/authorize", response_model=None)
async def oauth2_marimo_authorize(request: Request) -> Response:
    return await _authorize_callback(request, "/marimo")


app.include_router(router)
