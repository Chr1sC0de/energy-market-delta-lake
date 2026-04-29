"""
Conftest for the authentication service test suite.

Environment variables consumed at module-import time by main.py (lines 32-34)
must be set before main is imported. We set them here at module level so that
by the time pytest collects test_main.py (which does `import main`), the env
vars are already present.

We also patch `secrets.token_urlsafe` to return a fixed key so that the
SessionMiddleware is initialised with a known secret_key. This lets tests
build correctly-signed session cookies via itsdangerous.
"""

import os
from unittest.mock import patch

import pytest


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        item.add_marker(pytest.mark.component)


# ---------------------------------------------------------------------------
# Fixed secret used by SessionMiddleware during tests.
# Must be set before main.py is imported.
# ---------------------------------------------------------------------------
TEST_SESSION_SECRET = "test-secret-key-32-bytes-padding!"

# Patch token_urlsafe BEFORE main.py is imported so the SessionMiddleware
# picks up our known secret.
_token_patch = patch("secrets.token_urlsafe", return_value=TEST_SESSION_SECRET)
_token_patch.start()

# Set required environment variables before main.py is imported.
os.environ.setdefault("COGNITO_DAGSTER_AUTH_CLIENT_ID", "test-client-id")
os.environ.setdefault(
    "COGNITO_DAGSTER_AUTH_SERVER_METADATA_URL",
    "https://cognito.example.com/.well-known/openid-configuration",
)
os.environ.setdefault("COGNITO_DAGSTER_AUTH_CLIENT_SECRET", "test-client-secret")
os.environ.setdefault(
    "COGNITO_TOKEN_SIGNING_KEY_URL",
    "https://cognito.example.com/.well-known/jwks.json",
)
os.environ["WEBSITE_ROOT_URL"] = "https://example.com"
