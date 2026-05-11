"""Tests for Pulumi stack configuration parsing."""

import importlib
import os

import pytest

os.environ.setdefault("ADMINISTRATOR_IPS", "10.0.0.1")
os.environ.setdefault("DEVELOPMENT_LOCATION", "aws")

configs = importlib.import_module("configs")


def test_administrator_ips_normalize_to_single_host_cidrs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEVELOPMENT_LOCATION", "aws")
    monkeypatch.setenv("ADMINISTRATOR_IPS", "203.0.113.10 203.0.113.11/32")

    assert configs._administrator_cidrs_from_env() == [
        "203.0.113.10/32",
        "203.0.113.11/32",
    ]


def test_administrator_ips_reject_empty_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEVELOPMENT_LOCATION", "aws")
    monkeypatch.setenv("ADMINISTRATOR_IPS", "")

    with pytest.raises(ValueError, match="at least one administrator IP"):
        configs._administrator_cidrs_from_env()


def test_administrator_ips_reject_overbroad_cidrs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DEVELOPMENT_LOCATION", "aws")
    monkeypatch.setenv("ADMINISTRATOR_IPS", "203.0.113.0/24")

    with pytest.raises(ValueError, match="/32 CIDRs"):
        configs._administrator_cidrs_from_env()
