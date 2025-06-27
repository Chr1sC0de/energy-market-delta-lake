import os
from collections.abc import Awaitable
from secrets import token_urlsafe
from typing import Callable, cast

from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from fastapi import APIRouter, FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

# pyright: reportUntypedFunctionDecorator=false, reportMissingTypeStubs=false, reportUnknownVariableType=false, reportUnknownMemberType=false

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


@router.get("/oauth2/dagster-webserver/authorize")
async def oauth2_dagster_webserver_authorize(
    request: Request,
):
    if "user" in request.session:
        return {"status": "success"}
    redirect_uri = str(request.url_for("oauth2_dagster_webserver_callback")).replace(
        "http", "https", 1
    )
    return await authorize_redirect(request, redirect_uri)


@router.get("/oauth2/dagster-webserver/callback")
async def oauth2_dagster_webserver_callback(request: Request):
    token = await oidc.authorize_access_token(request)
    user = token["userinfo"]
    request.session["user"] = user
    return RedirectResponse(f"{os.environ['WEBSITE_ROOT_URL']}/dagster-webserver/")


app.include_router(router)
