"""Tests for DeltaLockingTableComponentResource."""

import warnings

import pulumi

from components.dynamodb import (
    TABLE_NAME,
    TTL_ATTRIBUTE_NAME,
    DeltaLockingTableComponentResource,
)


def _set_adopt_existing_delta_log_table(enabled: bool) -> None:
    pulumi.runtime.set_config(
        "aws-pulumi:adopt_existing_delta_log_table",
        "true" if enabled else "false",
    )


def _assert_ttl_enabled_for_expire_time(ttl: object) -> None:
    if hasattr(ttl, "attribute_name"):
        attribute_name = getattr(ttl, "attribute_name")
    elif isinstance(ttl, dict):
        attribute_name = ttl.get("attributeName", ttl.get("attribute_name"))
    else:
        attribute_name = None

    if hasattr(ttl, "enabled"):
        enabled = getattr(ttl, "enabled")
    elif isinstance(ttl, dict):
        enabled = ttl.get("enabled")
    else:
        enabled = None

    assert attribute_name == TTL_ATTRIBUTE_NAME, (
        f"Expected TTL attribute '{TTL_ATTRIBUTE_NAME}', got {ttl}"
    )
    assert enabled is True, f"Expected TTL enabled, got {ttl}"


class TestDeltaLockingTable:
    def test_table_created(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")
        assert ddb.table is not None

    def test_table_name_constant(self) -> None:
        assert TABLE_NAME == "delta_log"

    @pulumi.runtime.test
    def test_table_name_attribute(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")

        def check(name: str) -> None:
            assert name == "delta_log", f"Expected table name 'delta_log', got {name}"

        return ddb.table.name.apply(check)

    @pulumi.runtime.test
    def test_billing_mode_pay_per_request(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")

        def check(billing_mode: str) -> None:
            assert billing_mode == "PAY_PER_REQUEST", (
                f"Expected PAY_PER_REQUEST, got {billing_mode}"
            )

        return ddb.table.billing_mode.apply(check)

    @pulumi.runtime.test
    def test_hash_key_is_table_path(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")

        def check(hash_key: str) -> None:
            assert hash_key == "tablePath", (
                f"Expected hash key 'tablePath', got {hash_key}"
            )

        return ddb.table.hash_key.apply(check)

    @pulumi.runtime.test
    def test_range_key_is_file_name(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")

        def check(range_key: str) -> None:
            assert range_key == "fileName", (
                f"Expected range key 'fileName', got {range_key}"
            )

        return ddb.table.range_key.apply(check)

    @pulumi.runtime.test
    def test_ttl_uses_expire_time_attribute(self) -> None:
        ddb = DeltaLockingTableComponentResource("test-energy-market")

        def check(ttl: object) -> None:
            _assert_ttl_enabled_for_expire_time(ttl)

        return ddb.table.ttl.apply(check)

    @pulumi.runtime.test
    def test_adopted_table_ttl_uses_expire_time_attribute(self) -> None:
        _set_adopt_existing_delta_log_table(True)
        try:
            ddb = DeltaLockingTableComponentResource("test-energy-market-adopted")
        finally:
            _set_adopt_existing_delta_log_table(False)

        def check(ttl: object) -> None:
            _assert_ttl_enabled_for_expire_time(ttl)

        return ddb.table.ttl.apply(check)

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DeltaLockingTableComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
