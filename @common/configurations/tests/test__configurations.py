import os

os.environ["NAME_PREFIX"] = "some-delta-lake"
os.environ["DEVELOPMENT_ENVIRONMENT"] = "TEST"

from configurations import parameters, utils


def test__get_administrator_id():
    assert utils.get_administrator_ip_address is not None


def test__name_prefix():
    assert parameters.NAME_PREFIX == "some-delta-lake"


def test__stack_prefix():
    assert parameters.STACK_PREFIX == "SomeDeltaLake"


def test__development_environment():
    assert parameters.DEVELOPMENT_ENVIRONMENT == "test"


def test__shared_prefix():
    assert parameters.SHARED_PREFIX == "test-some-delta-lake"
