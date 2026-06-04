"""FastAPI OIDC authentication service for protected backend routes."""

from base64 import b64encode
from collections.abc import Awaitable
from hmac import new as hmac_new
from hashlib import sha256
from os import environ
from secrets import token_urlsafe
from time import time
from typing import Any, Callable, NotRequired, TypedDict, cast
from urllib.parse import unquote, urlsplit

import boto3
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
    HTTP_403_FORBIDDEN,
)

app = FastAPI()

router = APIRouter()

app.add_middleware(SessionMiddleware, secret_key=token_urlsafe(32))

AUTH_SESSION_ID_FIELD = "auth_session_id"
LOGIN_FAILURE_MESSAGE = "login failed"
ALLOWED_LOGIN_REDIRECT_PATHS = ("/dagster-webserver/admin", "/marimo", "/")


class AuthSession(TypedDict):
    """Server-side authentication fields for one browser session."""

    user: Any
    token_type: str
    access_token: str
    expires_at: float


class CognitoAccessTokenClaims(TypedDict):
    """Cognito access-token claims required by this service."""

    iss: str
    exp: int | float
    token_use: str
    client_id: NotRequired[str]


class CognitoAuthenticationResult(TypedDict):
    """Cognito token fields this service needs for a browser auth session."""

    AccessToken: str
    TokenType: str
    ExpiresIn: int | float


AUTH_SESSIONS: dict[str, AuthSession] = {}


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
    """Fetch the configured Cognito token signing key set."""
    return cast(
        JWKS,
        requests.get(environ["COGNITO_TOKEN_SIGNING_KEY_URL"]).json(),
    )


def compute_secret_hash(identifier: str) -> str:
    """Return Cognito SECRET_HASH for a username and configured app client."""
    client_id = environ["COGNITO_DAGSTER_AUTH_CLIENT_ID"]
    client_secret = environ["COGNITO_DAGSTER_AUTH_CLIENT_SECRET"]
    digest = hmac_new(
        client_secret.encode("utf-8"),
        f"{identifier}{client_id}".encode("utf-8"),
        sha256,
    ).digest()
    return b64encode(digest).decode("utf-8")


def authenticate_with_cognito_password(
    *,
    identifier: str,
    password: str,
    secret_hash: str,
) -> dict[str, Any]:
    """Authenticate username/password credentials with Cognito user-pool auth."""
    cognito = boto3.client("cognito-idp")
    return cast(
        dict[str, Any],
        cognito.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId=environ["COGNITO_DAGSTER_AUTH_CLIENT_ID"],
            AuthParameters={
                "USERNAME": identifier,
                "PASSWORD": password,
                "SECRET_HASH": secret_hash,
            },
        ),
    )


def get_hmac_key_data(token: str, jwks: JWKS) -> JWK | None:
    """Return the JWKS key matching the JWT key ID."""
    kid = jwt.get_unverified_header(token).get("kid")
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key


def _configured_cognito_issuer() -> str:
    """Return the configured Cognito user-pool issuer URL."""
    metadata_url = environ["COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL"]
    well_known_path = "/.well-known/openid-configuration"
    if metadata_url.endswith(well_known_path):
        return metadata_url[: -len(well_known_path)]
    return metadata_url.rstrip("/")


def _validate_access_token_claims(claims: CognitoAccessTokenClaims) -> None:
    """Validate Cognito access-token claims bound to this app client."""
    issuer = claims.get("iss")
    if issuer != _configured_cognito_issuer():
        raise ValueError("Invalid token issuer")

    expires_at = claims.get("exp")
    if expires_at is None or time() >= float(expires_at):
        raise ValueError("Token has expired")

    if claims.get("token_use") != "access":
        raise ValueError("Invalid token use")

    if claims.get("client_id") != environ["COGNITO_DAGSTER_AUTH_CLIENT_ID"]:
        raise ValueError("Invalid token client")


def verify_jwt(token: str) -> bool:
    """Verify a JWT signature and required Cognito access-token claims."""
    try:
        jwks = get_user_pool_token_signing_key()

        assert jwks is not None

        hmac_key = get_hmac_key_data(token, jwks)

        if not hmac_key:
            raise ValueError("No pubic key found!")

        hmac_key_data = cast(JWK, get_hmac_key_data(token, jwks))

        hmac_key = jwk.construct(hmac_key_data)

        message, encoded_signature = token.rsplit(".", 1)

        verified = hmac_key.verify(
            message.encode(), base64url_decode(encoded_signature.encode())
        )
        if not verified:
            return False

        claims = cast(CognitoAccessTokenClaims, jwt.get_unverified_claims(token))
        _validate_access_token_claims(claims)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token, {e}",
        )


def clear_session(session: dict[str, Any]) -> None:
    """Clear the browser session id and matching server-side auth state."""
    session_id = session.pop(AUTH_SESSION_ID_FIELD, None)
    if isinstance(session_id, str):
        AUTH_SESSIONS.pop(session_id, None)

    # Remove legacy auth fields if an older cookie is presented.
    session.pop("user", None)
    session.pop("token_type", None)
    session.pop("access_token", None)
    session.pop("expires_at", None)


def _origin_for_url(url: str) -> str | None:
    """Return scheme://host[:port] for a configured or request header URL."""
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or parts.netloc == "":
        return None
    return f"{parts.scheme}://{parts.netloc}"


def _request_origin_is_allowed(request: Request) -> bool:
    """Validate browser origin headers against the configured website origin."""
    expected_origin = _origin_for_url(_website_root_url)
    if expected_origin is None:
        return False

    for header_name in ("origin", "referer"):
        header_value = request.headers.get(header_name)
        if header_value is None:
            continue

        request_origin = _origin_for_url(header_value)
        if request_origin != expected_origin:
            return False

    return True


def _has_encoded_slash_or_backslash(value: str) -> bool:
    """Return true when a value contains percent-encoded slash characters."""
    lowered = value.lower()
    return "%2f" in lowered or "%5c" in lowered


def _contains_control_character(value: str) -> bool:
    """Return true when a value contains CRLF or another control character."""
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def sanitize_login_redirect(raw_next: str | None) -> str | None:
    """Return an allowed local redirect path, or None when unsafe."""
    if raw_next is None or raw_next == "":
        return "/"

    decoded_next = unquote(raw_next)
    if (
        _contains_control_character(raw_next)
        or _contains_control_character(decoded_next)
        or _has_encoded_slash_or_backslash(raw_next)
        or "\\" in raw_next
        or "\\" in decoded_next
    ):
        return None

    parts = urlsplit(raw_next)
    if parts.scheme != "" or parts.netloc != "" or not raw_next.startswith("/"):
        return None
    if raw_next.startswith("//"):
        return None

    if raw_next == "/":
        return raw_next

    for allowed_path in ALLOWED_LOGIN_REDIRECT_PATHS[:-1]:
        if raw_next == allowed_path or raw_next.startswith(f"{allowed_path}/"):
            return raw_next

    return None


async def _login_payload(request: Request) -> dict[str, str] | None:
    """Read JSON or form login payload fields from the request."""
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
        if not isinstance(payload, dict):
            return None
    else:
        payload = await request.form()

    login_payload: dict[str, str] = {}
    for field in ("identifier", "password", "next"):
        value = payload.get(field)
        if isinstance(value, str):
            login_payload[field] = value

    return login_payload


def _normal_authentication_result(
    response: dict[str, Any],
) -> CognitoAuthenticationResult | None:
    """Return Cognito AuthenticationResult when the response is session-safe."""
    if "ChallengeName" in response:
        return None

    authentication_result = response.get("AuthenticationResult")
    if not isinstance(authentication_result, dict):
        return None

    access_token = authentication_result.get("AccessToken")
    token_type = authentication_result.get("TokenType")
    expires_in = authentication_result.get("ExpiresIn")
    if not isinstance(access_token, str) or access_token == "":
        return None
    if not isinstance(token_type, str) or token_type == "":
        return None
    if not isinstance(expires_in, (int, float)) or expires_in <= 0:
        return None

    return {
        "AccessToken": access_token,
        "TokenType": token_type,
        "ExpiresIn": expires_in,
    }


def _store_auth_session(
    request: Request,
    *,
    identifier: str,
    authentication_result: CognitoAuthenticationResult,
) -> None:
    """Store successful Cognito auth material in server-side auth state."""
    clear_session(request.session)
    session_id = token_urlsafe(32)
    AUTH_SESSIONS[session_id] = {
        "user": {"identifier": identifier},
        "token_type": authentication_result["TokenType"],
        "access_token": authentication_result["AccessToken"],
        "expires_at": time() + float(authentication_result["ExpiresIn"]),
    }
    request.session[AUTH_SESSION_ID_FIELD] = session_id


def _validate_session(request: Request) -> JSONResponse:
    """Shared session validation logic for protected service endpoints."""
    session_id = request.session.get(AUTH_SESSION_ID_FIELD)
    if not isinstance(session_id, str):
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    auth_session = AUTH_SESSIONS.get(session_id)
    if auth_session is None:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    if any(
        field not in auth_session
        for field in ("user", "token_type", "access_token", "expires_at")
    ):
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    if time() >= auth_session["expires_at"]:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": "unauthorized access"},
        )

    if verify_jwt(
        cast(
            str,
            auth_session["access_token"],
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


@router.post("/auth/login")
async def auth_login(request: Request) -> JSONResponse:
    """Authenticate credentials through Cognito and start an opaque session."""
    if not _request_origin_is_allowed(request):
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_403_FORBIDDEN,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    try:
        payload = await _login_payload(request)
    except Exception:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    if payload is None:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    identifier = payload.get("identifier")
    password = payload.get("password")
    redirect_path = sanitize_login_redirect(payload.get("next"))
    if (
        identifier is None
        or identifier == ""
        or password is None
        or password == ""
        or redirect_path is None
    ):
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    secret_hash = compute_secret_hash(identifier)
    try:
        response = authenticate_with_cognito_password(
            identifier=identifier,
            password=password,
            secret_hash=secret_hash,
        )
    except Exception:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    authentication_result = _normal_authentication_result(response)
    if authentication_result is None:
        clear_session(request.session)
        return JSONResponse(
            status_code=HTTP_401_UNAUTHORIZED,
            content={"message": LOGIN_FAILURE_MESSAGE},
        )

    _store_auth_session(
        request,
        identifier=identifier,
        authentication_result=authentication_result,
    )
    return JSONResponse(status_code=HTTP_200_OK, content={"redirect": redirect_path})


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    """Clear the opaque auth session and return the default local redirect."""
    clear_session(request.session)
    return JSONResponse(status_code=HTTP_200_OK, content={"redirect": "/"})


async def _authorize_callback(request: Request, redirect_path: str) -> Response:
    """Shared OIDC callback logic — exchanges code for token, sets session."""
    try:
        token = await oidc.authorize_access_token(request)
        clear_session(request.session)
        session_id = token_urlsafe(32)
        AUTH_SESSIONS[session_id] = {
            "user": token["userinfo"],
            "token_type": token["token_type"],
            "access_token": token["access_token"],
            "expires_at": token["expires_at"],
        }
        request.session[AUTH_SESSION_ID_FIELD] = session_id
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
    """Validate the Dagster webserver admin browser session."""
    request.session

    login_redirect_uri = str(request.url_for("oauth2_dagster_webserver_login"))
    if "localhost" not in login_redirect_uri:
        login_redirect_uri = login_redirect_uri.replace("http", "https", 1)

    return _validate_session(request)


@router.get("/dagster-webserver/admin/login")
async def oauth2_dagster_webserver_login(request: Request) -> RedirectResponse:
    """Start the Dagster webserver admin OIDC login flow."""
    redirect_uri = _build_redirect_uri(request, "oauth2_dagster_webserver_authorize")
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get("/oauth2/dagster-webserver/admin/authorize", response_model=None)
async def oauth2_dagster_webserver_authorize(
    request: Request,
) -> Response:
    """Handle the Dagster webserver admin OIDC authorization callback."""
    return await _authorize_callback(request, "/dagster-webserver/admin")


# ---------------------------------------------------------------------------
# Marimo notebook server routes
# ---------------------------------------------------------------------------


@router.get("/oauth2/marimo/validate")
async def oauth2_marimo_validate(request: Request) -> JSONResponse:
    """Validate the marimo browser session."""
    return _validate_session(request)


@router.get("/marimo/login")
async def oauth2_marimo_login(request: Request) -> RedirectResponse:
    """Start the marimo OIDC login flow."""
    redirect_uri = _build_redirect_uri(request, "oauth2_marimo_authorize")
    return await oidc.authorize_redirect(request, redirect_uri)


@router.get("/oauth2/marimo/authorize", response_model=None)
async def oauth2_marimo_authorize(request: Request) -> Response:
    """Handle the marimo OIDC authorization callback."""
    return await _authorize_callback(request, "/marimo")


app.include_router(router)
