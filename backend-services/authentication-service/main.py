# pyright: reportUntypedFunctionDecorator=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportExplicitAny=false
import os
from collections.abc import Awaitable
from secrets import token_urlsafe
from time import time
from typing import Any, Callable, cast

import requests
from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from fastapi import APIRouter, FastAPI, HTTPException, Request
from jose import jwk, jwt
from jose.utils import base64url_decode
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from starlette.status import (
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)

app = FastAPI()

router = APIRouter()

app.add_middleware(SessionMiddleware, secret_key=token_urlsafe(32))


oauth = OAuth()

oauth.register = cast(Callable[..., OAuth], oauth.register)

_ = oauth.register(
    name="oidc",
    client_id=os.environ["COGNITO_DAGSTER_AUTH_CLIENT_ID"],
    server_metadata_url=os.environ["COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL"],
    client_secret=os.environ["COGNITO_DAGSTER_AUTH_CLIENT_SECRET"],
    client_kwargs={"scope": "openid email phone"},
)

oidc = cast(StarletteOAuth2App, oauth.oidc)

authorize_redirect = cast(
    Callable[..., Awaitable[RedirectResponse]], oidc.authorize_redirect
)

JWK = dict[str, str]
JWKS = dict[str, list[JWK]]


def get_user_pool_token_signing_key() -> JWKS:
    return cast(
        JWKS,
        requests.get(os.environ["COGNITO_TOKEN_SIGNING_KEY_URL"]).json(),
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


@router.get("/oauth2/dagster-webserver/admin/validate")
async def oauth2_dagster_webserver_validate(request: Request):
    request.session

    login_redirect_uri = str(request.url_for("oauth2_dagster_webserver_login"))
    if "localhost" not in login_redirect_uri:
        login_redirect_uri = login_redirect_uri.replace("http", "https", 1)

    if any(
        [
            field not in request.session
            for field in ("user", "token_type", "access_token", "expires_at")
        ]
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


@router.get("/dagster-webserver/admin/login")
async def oauth2_dagster_webserver_login(request: Request):
    redirect_uri = str(request.url_for("oauth2_dagster_webserver_authorize"))
    if "localhost" not in redirect_uri:
        redirect_uri = redirect_uri.replace("http", "https", 1)
    return await authorize_redirect(request, redirect_uri)


@router.get("/oauth2/dagster-webserver/admin/authorize")
async def oauth2_dagster_webserver_authorize(request: Request):
    try:
        token = await oidc.authorize_access_token(request)
        request.session["user"] = token["userinfo"]
        request.session["token_type"] = token["token_type"]
        request.session["access_token"] = token["access_token"]
        request.session["expires_at"] = token["expires_at"]
        return RedirectResponse(
            f"{os.environ['WEBSITE_ROOT_URL']}/dagster-webserver/admin"
        )
    except Exception as e:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": str(e)},
        )


app.include_router(router)
