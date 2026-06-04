"""
Test suite for authentication service main.py.

Achieves 100% coverage of every branch:
  - get_user_pool_token_signing_key()
  - get_hmac_key_data()          (key found / key not found)
  - verify_jwt()                 (valid / exception path)
  - clear_session()
  - _validate_session()          (shared helper)
  - GET /oauth2/dagster-webserver/admin/validate
      missing fields → 401
      expired token  → 401
      verify_jwt True  → 200
      verify_jwt False → 401
  - GET /oauth2/marimo/validate
      missing fields → 401
      expired token  → 401
      verify_jwt True  → 200
      verify_jwt False → 401
      verify_jwt raises HTTPException → 401

Session injection strategy: build a signed Starlette session cookie using
itsdangerous with the fixed TEST_SESSION_SECRET set in conftest.py before
main.py is imported, so the real SessionMiddleware can decode it.
"""

import base64
import json
from http.cookies import SimpleCookie
from time import time
from typing import Any, cast
from unittest.mock import MagicMock

import itsdangerous
import pytest
from fastapi.testclient import TestClient
from httpx import Response as HttpxResponse
from pytest_mock import MockerFixture

# conftest.py has already set env vars + patched token_urlsafe before this
# import runs.
import main
from main import (
    app,
    clear_session,
    get_hmac_key_data,
    get_user_pool_token_signing_key,
    verify_jwt,
)
from tests.component.conftest import TEST_SESSION_SECRET

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

FAKE_JWKS: dict[str, list[dict[str, str]]] = {
    "keys": [
        {
            "kid": "test-kid",
            "kty": "RSA",
            "alg": "RS256",
            "use": "sig",
            "n": "somenvalue",
            "e": "AQAB",
        }
    ]
}

FAKE_TOKEN = "header.payload.signature"


@pytest.fixture(autouse=True)
def _clear_auth_sessions() -> None:
    main.AUTH_SESSIONS.clear()


def _make_session_cookie(data: dict[str, Any]) -> str:
    """
    Build a signed Starlette session cookie using the same secret the
    SessionMiddleware was initialised with (TEST_SESSION_SECRET from conftest).

    Starlette's SessionMiddleware uses itsdangerous.TimestampSigner directly:
      raw  = base64.b64encode(json.dumps(session).encode())
      cookie = signer.sign(raw).decode()
    """
    signer = itsdangerous.TimestampSigner(TEST_SESSION_SECRET)
    raw = base64.b64encode(json.dumps(data).encode("utf-8"))
    return signer.sign(raw).decode("utf-8")


def _client_with_session(
    session_data: dict[str, Any],
) -> tuple[TestClient, dict[str, str]]:
    """Return a TestClient and the Cookie header needed to inject session_data."""
    client = TestClient(app, raise_server_exceptions=False)
    cookie_value = _make_session_cookie(session_data)
    headers = {"Cookie": f"session={cookie_value}"}
    return client, headers


def _decode_session_cookie(cookie_value: str) -> dict[str, Any]:
    signer = itsdangerous.TimestampSigner(TEST_SESSION_SECRET)
    raw = signer.unsign(cookie_value.encode("utf-8"))
    return json.loads(base64.b64decode(raw).decode("utf-8"))


def _session_cookie_from_response(response: HttpxResponse) -> dict[str, Any]:
    cookie = SimpleCookie()
    cookie.load(response.headers["set-cookie"])
    return _decode_session_cookie(cookie["session"].value)


def _auth_session_data(
    *,
    access_token: str = FAKE_TOKEN,
    expires_at: float | None = None,
) -> main.AuthSession:
    return {
        "user": {"sub": "abc"},
        "token_type": "Bearer",
        "access_token": access_token,
        "expires_at": expires_at if expires_at is not None else time() + 3600,
    }


def _client_with_auth_session(
    auth_session: main.AuthSession,
) -> tuple[TestClient, dict[str, str], str]:
    session_id = "test-auth-session-id"
    main.AUTH_SESSIONS[session_id] = auth_session
    client, headers = _client_with_session({main.AUTH_SESSION_ID_FIELD: session_id})
    return client, headers, session_id


def _same_origin_headers() -> dict[str, str]:
    return {"Origin": "https://example.com", "Referer": "https://example.com/login"}


# ---------------------------------------------------------------------------
# TestGetUserPoolTokenSigningKey
# ---------------------------------------------------------------------------


class TestGetUserPoolTokenSigningKey:
    def test_returns_jwks(self, mocker: MockerFixture) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = FAKE_JWKS
        mocker.patch("main.requests.get", return_value=mock_response)

        result = get_user_pool_token_signing_key()

        assert result == FAKE_JWKS
        main.requests.get.assert_called_once_with(  # type: ignore[attr-defined]
            main.environ["COGNITO_TOKEN_SIGNING_KEY_URL"]
        )


class TestAuthenticateWithCognitoPassword:
    def test_calls_cognito_user_password_auth(self, mocker: MockerFixture) -> None:
        cognito_client = MagicMock()
        cognito_client.initiate_auth.return_value = {"AuthenticationResult": {}}
        boto3_client = mocker.patch("main.boto3.client", return_value=cognito_client)

        result = main.authenticate_with_cognito_password(
            identifier="user@example.com",
            password="password",
            secret_hash="secret-hash",
        )

        assert result == {"AuthenticationResult": {}}
        boto3_client.assert_called_once_with("cognito-idp")
        cognito_client.initiate_auth.assert_called_once_with(
            AuthFlow="USER_PASSWORD_AUTH",
            ClientId="test-client-id",
            AuthParameters={
                "USERNAME": "user@example.com",
                "PASSWORD": "password",
                "SECRET_HASH": "secret-hash",
            },
        )


class TestLoginRequestHelpers:
    @pytest.mark.parametrize("url", ["", "/relative", "ftp://example.com"])
    def test_origin_for_url_rejects_non_http_origins(self, url: str) -> None:
        assert main._origin_for_url(url) is None

    def test_configured_bad_website_origin_rejects_request(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("main._website_root_url", "/relative")
        authenticate = mocker.patch("main.authenticate_with_cognito_password")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            TestCustomLoginEndpoint.URL,
            headers=_same_origin_headers(),
            json={"identifier": "user@example.com", "password": "password"},
        )

        assert response.status_code == 403
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        authenticate.assert_not_called()


# ---------------------------------------------------------------------------
# TestGetHmacKeyData
# ---------------------------------------------------------------------------


class TestGetHmacKeyData:
    def test_key_found(self, mocker: MockerFixture) -> None:
        mocker.patch("main.jwt.get_unverified_header", return_value={"kid": "test-kid"})
        result = get_hmac_key_data(FAKE_TOKEN, FAKE_JWKS)
        assert result == FAKE_JWKS["keys"][0]

    def test_key_not_found_returns_none(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "main.jwt.get_unverified_header", return_value={"kid": "no-match-kid"}
        )
        result = get_hmac_key_data(FAKE_TOKEN, FAKE_JWKS)
        assert result is None


# ---------------------------------------------------------------------------
# TestVerifyJwt
# ---------------------------------------------------------------------------


class TestVerifyJwt:
    def _patch_dependencies(
        self, mocker: MockerFixture, verify_return: bool = True
    ) -> None:
        mock_response = MagicMock()
        mock_response.json.return_value = FAKE_JWKS
        mocker.patch("main.requests.get", return_value=mock_response)
        mocker.patch("main.jwt.get_unverified_header", return_value={"kid": "test-kid"})
        mock_hmac_key = MagicMock()
        mock_hmac_key.verify.return_value = verify_return
        mocker.patch("main.jwk.construct", return_value=mock_hmac_key)
        mocker.patch("main.base64url_decode", return_value=b"decoded-sig")
        mocker.patch(
            "main.jwt.get_unverified_claims",
            return_value={
                "iss": "https://cognito.example.com",
                "exp": time() + 3600,
                "token_use": "access",
                "client_id": "test-client-id",
            },
        )

    def test_valid_jwt_returns_true(self, mocker: MockerFixture) -> None:
        self._patch_dependencies(mocker, verify_return=True)
        result = verify_jwt(FAKE_TOKEN)
        assert result is True

    def test_valid_issuer_can_be_configured_without_well_known_path(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(
            main.environ,
            {
                "COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL": "https://cognito.example.com/"
            },
        )
        assert main._configured_cognito_issuer() == "https://cognito.example.com"

    def test_invalid_signature_returns_false(self, mocker: MockerFixture) -> None:
        self._patch_dependencies(mocker, verify_return=False)
        get_claims = mocker.patch("main.jwt.get_unverified_claims")

        result = verify_jwt(FAKE_TOKEN)

        assert result is False
        get_claims.assert_not_called()

    def test_exception_raises_http_exception(self, mocker: MockerFixture) -> None:
        # Make requests.get raise so the except branch is hit.
        mocker.patch("main.requests.get", side_effect=RuntimeError("network error"))

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(FAKE_TOKEN)

        assert exc_info.value.status_code == 401
        assert "network error" in exc_info.value.detail

    def test_no_matching_key_raises_http_exception(self, mocker: MockerFixture) -> None:
        # get_hmac_key_data returns None (no matching kid) → ValueError → HTTPException
        mock_response = MagicMock()
        mock_response.json.return_value = FAKE_JWKS
        mocker.patch("main.requests.get", return_value=mock_response)
        # kid in token header does not match any key in JWKS
        mocker.patch(
            "main.jwt.get_unverified_header", return_value={"kid": "no-match-kid"}
        )

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(FAKE_TOKEN)

        assert exc_info.value.status_code == 401
        assert "No pubic key found!" in exc_info.value.detail

    @pytest.mark.parametrize(
        ("claims", "detail"),
        [
            (
                {
                    "iss": "https://wrong.example.com",
                    "exp": time() + 3600,
                    "token_use": "access",
                    "client_id": "test-client-id",
                },
                "Invalid token issuer",
            ),
            (
                {
                    "iss": "https://cognito.example.com",
                    "exp": time() - 1,
                    "token_use": "access",
                    "client_id": "test-client-id",
                },
                "Token has expired",
            ),
            (
                {
                    "iss": "https://cognito.example.com",
                    "exp": time() + 3600,
                    "token_use": "id",
                    "client_id": "test-client-id",
                },
                "Invalid token use",
            ),
            (
                {
                    "iss": "https://cognito.example.com",
                    "exp": time() + 3600,
                    "token_use": "access",
                    "client_id": "wrong-client-id",
                },
                "Invalid token client",
            ),
        ],
    )
    def test_claim_validation_failures_raise_http_exception(
        self, mocker: MockerFixture, claims: dict[str, Any], detail: str
    ) -> None:
        self._patch_dependencies(mocker, verify_return=True)
        mocker.patch("main.jwt.get_unverified_claims", return_value=claims)

        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_jwt(FAKE_TOKEN)

        assert exc_info.value.status_code == 401
        assert detail in exc_info.value.detail


# ---------------------------------------------------------------------------
# TestClearSession
# ---------------------------------------------------------------------------


class TestClearSession:
    def test_clears_all_session_fields(self) -> None:
        main.AUTH_SESSIONS["session-id"] = _auth_session_data()
        session: dict[str, Any] = {
            main.AUTH_SESSION_ID_FIELD: "session-id",
            "user": {"sub": "abc"},
            "token_type": "Bearer",
            "access_token": "tok",
            "expires_at": 9999999999,
            "extra_field": "should_remain",
        }
        clear_session(session)
        assert "user" not in session
        assert "token_type" not in session
        assert "access_token" not in session
        assert "expires_at" not in session
        assert main.AUTH_SESSION_ID_FIELD not in session
        assert "session-id" not in main.AUTH_SESSIONS
        # unrelated keys are untouched
        assert session["extra_field"] == "should_remain"

    def test_clears_empty_session_without_error(self) -> None:
        session: dict[str, Any] = {}
        clear_session(session)  # must not raise
        assert session == {}


# ---------------------------------------------------------------------------
# TestValidateEndpoint
# ---------------------------------------------------------------------------


class TestValidateEndpoint:
    URL = "/oauth2/dagster-webserver/admin/validate"

    def test_missing_session_fields_returns_401(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(self.URL)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}

    def test_partial_session_fields_returns_401(self) -> None:
        # Only some fields present — still missing others
        client, headers = _client_with_session({"user": "bob", "token_type": "Bearer"})
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401

    def test_expired_token_returns_401(self) -> None:
        client, headers, session_id = _client_with_auth_session(
            _auth_session_data(expires_at=time() - 3600)
        )
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}
        assert session_id not in main.AUTH_SESSIONS

    def test_valid_token_returns_200(self, mocker: MockerFixture) -> None:
        # Patch verify_jwt to return True so we exercise the 200 branch.
        mocker.patch("main.verify_jwt", return_value=True)

        client, headers, _ = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 200
        assert response.json() == {"status": "authorized access"}

    def test_verify_jwt_false_returns_401(self, mocker: MockerFixture) -> None:
        # verify_jwt returning False exercises the else branch → clear + 401.
        mocker.patch("main.verify_jwt", return_value=False)

        client, headers, session_id = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}
        assert session_id not in main.AUTH_SESSIONS

    def test_verify_jwt_raises_http_exception_propagates(
        self, mocker: MockerFixture
    ) -> None:
        # verify_jwt can raise HTTPException (401) — the route lets it bubble up.
        from fastapi import HTTPException

        mocker.patch(
            "main.verify_jwt",
            side_effect=HTTPException(status_code=401, detail="Invalid token, err"),
        )

        client, headers, _ = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401

    def test_missing_server_side_state_returns_401(self) -> None:
        client, headers = _client_with_session(
            {main.AUTH_SESSION_ID_FIELD: "missing-session-id"}
        )
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}

    def test_incomplete_server_side_state_returns_401(self) -> None:
        session_id = "partial-server-side-session-id"
        main.AUTH_SESSIONS[session_id] = cast(
            main.AuthSession,
            {"user": {"sub": "abc"}},
        )
        client, headers = _client_with_session({main.AUTH_SESSION_ID_FIELD: session_id})

        response = client.get(self.URL, headers=headers)

        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}
        assert session_id not in main.AUTH_SESSIONS

    def test_server_side_state_lookup_supplies_access_token(
        self, mocker: MockerFixture
    ) -> None:
        verify_jwt = mocker.patch("main.verify_jwt", return_value=True)

        client, headers, _ = _client_with_auth_session(
            _auth_session_data(access_token="server-side-token")
        )
        response = client.get(self.URL, headers=headers)

        assert response.status_code == 200
        verify_jwt.assert_called_once_with("server-side-token")


# ---------------------------------------------------------------------------
# TestCustomLoginEndpoint
# ---------------------------------------------------------------------------


class TestCustomLoginEndpoint:
    URL = "/auth/login"

    def _successful_cognito_response(self) -> dict[str, Any]:
        return {
            "AuthenticationResult": {
                "AccessToken": FAKE_TOKEN,
                "TokenType": "Bearer",
                "ExpiresIn": 3600,
                "IdToken": "id-token-not-stored",
                "RefreshToken": "refresh-token-not-stored",
            }
        }

    def test_json_login_success_sets_only_opaque_cookie(
        self, mocker: MockerFixture
    ) -> None:
        authenticate = mocker.patch(
            "main.authenticate_with_cognito_password",
            return_value=self._successful_cognito_response(),
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={
                "identifier": "user@example.com",
                "password": "correct-password",
                "next": "/marimo",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"redirect": "/marimo"}
        expected_secret_hash = main.compute_secret_hash("user@example.com")
        authenticate.assert_called_once_with(
            identifier="user@example.com",
            password="correct-password",
            secret_hash=expected_secret_hash,
        )

        cookie_payload = _session_cookie_from_response(response)
        assert set(cookie_payload) == {main.AUTH_SESSION_ID_FIELD}
        session_id = cookie_payload[main.AUTH_SESSION_ID_FIELD]
        assert session_id in main.AUTH_SESSIONS
        assert main.AUTH_SESSIONS[session_id]["user"] == {
            "identifier": "user@example.com"
        }
        assert main.AUTH_SESSIONS[session_id]["token_type"] == "Bearer"
        assert main.AUTH_SESSIONS[session_id]["access_token"] == FAKE_TOKEN
        assert main.AUTH_SESSIONS[session_id]["expires_at"] > time()

        response_text = response.text.lower()
        cookie_text = response.headers["set-cookie"].lower()
        server_state_text = json.dumps(main.AUTH_SESSIONS[session_id]).lower()
        for forbidden in (
            "correct-password",
            expected_secret_hash.lower(),
            "id-token-not-stored",
            "refresh-token-not-stored",
            "authenticationresult",
        ):
            assert forbidden not in response_text
            assert forbidden not in cookie_text
            assert forbidden not in server_state_text

    def test_form_login_success(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "main.authenticate_with_cognito_password",
            return_value=self._successful_cognito_response(),
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            data={
                "identifier": "user@example.com",
                "password": "correct-password",
                "next": "/dagster-webserver/admin",
            },
        )

        assert response.status_code == 200
        assert response.json() == {"redirect": "/dagster-webserver/admin"}

    def test_failed_credentials_returns_generic_error_and_no_session(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "main.authenticate_with_cognito_password",
            side_effect=RuntimeError("not authorized"),
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={"identifier": "user@example.com", "password": "wrong-password"},
        )

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        assert main.AUTH_SESSIONS == {}
        assert "not authorized" not in response.text.lower()
        assert "wrong-password" not in response.text

    def test_challenge_response_does_not_authenticate(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "main.authenticate_with_cognito_password",
            return_value={
                "ChallengeName": "NEW_PASSWORD_REQUIRED",
                "Session": "challenge-session",
            },
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={"identifier": "user@example.com", "password": "password"},
        )

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        assert main.AUTH_SESSIONS == {}
        assert "challenge-session" not in response.text

    @pytest.mark.parametrize(
        "cognito_response",
        [
            {},
            {"AuthenticationResult": None},
            {"AuthenticationResult": {"TokenType": "Bearer", "ExpiresIn": 3600}},
            {
                "AuthenticationResult": {
                    "AccessToken": FAKE_TOKEN,
                    "ExpiresIn": 3600,
                }
            },
            {
                "AuthenticationResult": {
                    "AccessToken": FAKE_TOKEN,
                    "TokenType": "Bearer",
                    "ExpiresIn": 0,
                }
            },
        ],
    )
    def test_malformed_cognito_response_does_not_authenticate(
        self, mocker: MockerFixture, cognito_response: dict[str, Any]
    ) -> None:
        mocker.patch(
            "main.authenticate_with_cognito_password", return_value=cognito_response
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={"identifier": "user@example.com", "password": "password"},
        )

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        assert main.AUTH_SESSIONS == {}

    @pytest.mark.parametrize(
        "payload",
        [
            {},
            {"identifier": "user@example.com"},
            {"password": "password"},
            {"identifier": "", "password": "password"},
            {"identifier": "user@example.com", "password": ""},
        ],
    )
    def test_malformed_request_does_not_call_cognito(
        self, mocker: MockerFixture, payload: dict[str, str]
    ) -> None:
        authenticate = mocker.patch("main.authenticate_with_cognito_password")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(self.URL, headers=_same_origin_headers(), json=payload)

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        authenticate.assert_not_called()
        assert main.AUTH_SESSIONS == {}

    @pytest.mark.parametrize("body", ["[1, 2, 3]", "{"])
    def test_malformed_json_body_does_not_call_cognito(
        self, mocker: MockerFixture, body: str
    ) -> None:
        authenticate = mocker.patch("main.authenticate_with_cognito_password")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers={**_same_origin_headers(), "Content-Type": "application/json"},
            content=body,
        )

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        authenticate.assert_not_called()
        assert main.AUTH_SESSIONS == {}

    @pytest.mark.parametrize(
        "headers",
        [
            {"Origin": "https://attacker.example.com"},
            {"Referer": "https://attacker.example.com/login"},
            {
                "Origin": "https://example.com",
                "Referer": "https://attacker.example.com/login",
            },
        ],
    )
    def test_origin_rejection_happens_before_cognito(
        self, mocker: MockerFixture, headers: dict[str, str]
    ) -> None:
        authenticate = mocker.patch("main.authenticate_with_cognito_password")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=headers,
            json={"identifier": "user@example.com", "password": "password"},
        )

        assert response.status_code == 403
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        authenticate.assert_not_called()
        assert main.AUTH_SESSIONS == {}

    @pytest.mark.parametrize(
        "next_path",
        [
            "/",
            "/dagster-webserver/admin",
            "/dagster-webserver/admin/runs",
            "/marimo",
            "/marimo/notebooks",
        ],
    )
    def test_safe_next_values_are_returned(
        self, mocker: MockerFixture, next_path: str
    ) -> None:
        mocker.patch(
            "main.authenticate_with_cognito_password",
            return_value=self._successful_cognito_response(),
        )

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={
                "identifier": "user@example.com",
                "password": "password",
                "next": next_path,
            },
        )

        assert response.status_code == 200
        assert response.json() == {"redirect": next_path}

    @pytest.mark.parametrize(
        "next_path",
        [
            "https://example.com/marimo",
            "http://example.com/marimo",
            "//example.com/marimo",
            "//",
            "/%2fexample.com/marimo",
            "/%5cexample.com/marimo",
            "/marimo%0d%0aSet-Cookie:%20x=y",
            "/marimo\nx",
            "/marimo\\x",
            "/dagster-webserver",
            "/dagster-webserver/administer",
            "/other",
            "marimo",
        ],
    )
    def test_unsafe_next_values_do_not_call_cognito(
        self, mocker: MockerFixture, next_path: str
    ) -> None:
        authenticate = mocker.patch("main.authenticate_with_cognito_password")

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post(
            self.URL,
            headers=_same_origin_headers(),
            json={
                "identifier": "user@example.com",
                "password": "password",
                "next": next_path,
            },
        )

        assert response.status_code == 401
        assert response.json() == {"message": main.LOGIN_FAILURE_MESSAGE}
        authenticate.assert_not_called()
        assert main.AUTH_SESSIONS == {}


class TestCustomLogoutEndpoint:
    URL = "/logout"

    def test_post_logout_clears_opaque_session(self) -> None:
        client, headers, session_id = _client_with_auth_session(_auth_session_data())

        response = client.post(self.URL, headers=headers)

        assert response.status_code == 200
        assert response.json() == {"redirect": "/"}
        assert session_id not in main.AUTH_SESSIONS
        cookie = SimpleCookie()
        cookie.load(response.headers["set-cookie"])
        assert cookie["session"].value == "null"

    def test_get_logout_is_out_of_scope(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(self.URL)

        assert response.status_code == 405


class TestRemovedHostedOidcEndpoints:
    @pytest.mark.parametrize(
        "url",
        [
            "/dagster-webserver/admin/login",
            "/oauth2/dagster-webserver/admin/authorize",
            "/marimo/login",
            "/oauth2/marimo/authorize",
        ],
    )
    def test_hosted_oidc_routes_are_not_registered(self, url: str) -> None:
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get(url)

        assert response.status_code == 404


class TestWebsiteRootUrlNormalisation:
    """Unit tests for _normalise_website_root_url().

    Tests call the real function from main.py so coverage is recorded against
    the actual implementation rather than a duplicated helper.
    """

    def test_already_https_unchanged(self) -> None:
        assert (
            main._normalise_website_root_url("https://example.com")
            == "https://example.com"
        )

    def test_already_https_trailing_slash_stripped(self) -> None:
        assert (
            main._normalise_website_root_url("https://example.com/")
            == "https://example.com"
        )

    def test_plain_http_upgraded_to_https(self) -> None:
        """Plain http:// must be upgraded, not passed through."""
        result = main._normalise_website_root_url("http://example.com")
        assert result == "https://example.com", (
            f"Expected http:// to be upgraded to https://, got {result!r}"
        )

    def test_no_scheme_gets_https_prepended(self) -> None:
        """Bare domain (no scheme) must have https:// prepended."""
        result = main._normalise_website_root_url("example.com")
        assert result == "https://example.com", (
            f"Expected https:// to be prepended to bare domain, got {result!r}"
        )

    def test_no_scheme_with_path_gets_https_prepended(self) -> None:
        result = main._normalise_website_root_url("example.com/some/path")
        assert result == "https://example.com/some/path"


# ===========================================================================
# Marimo endpoint tests
# ===========================================================================


# ---------------------------------------------------------------------------
# TestMarimoValidateEndpoint
# ---------------------------------------------------------------------------


class TestMarimoValidateEndpoint:
    URL = "/oauth2/marimo/validate"

    def test_missing_session_fields_returns_401(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get(self.URL)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}

    def test_partial_session_fields_returns_401(self) -> None:
        client, headers = _client_with_session({"user": "bob", "token_type": "Bearer"})
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401

    def test_expired_token_returns_401(self) -> None:
        client, headers, session_id = _client_with_auth_session(
            _auth_session_data(expires_at=time() - 3600)
        )
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}
        assert session_id not in main.AUTH_SESSIONS

    def test_valid_token_returns_200(self, mocker: MockerFixture) -> None:
        mocker.patch("main.verify_jwt", return_value=True)

        client, headers, _ = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 200
        assert response.json() == {"status": "authorized access"}

    def test_verify_jwt_false_returns_401(self, mocker: MockerFixture) -> None:
        mocker.patch("main.verify_jwt", return_value=False)

        client, headers, session_id = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
        assert response.json() == {"message": "unauthorized access"}
        assert session_id not in main.AUTH_SESSIONS

    def test_verify_jwt_raises_http_exception_propagates(
        self, mocker: MockerFixture
    ) -> None:
        from fastapi import HTTPException

        mocker.patch(
            "main.verify_jwt",
            side_effect=HTTPException(status_code=401, detail="Invalid token, err"),
        )

        client, headers, _ = _client_with_auth_session(_auth_session_data())
        response = client.get(self.URL, headers=headers)
        assert response.status_code == 401
