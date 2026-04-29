"""Tests for DeltaLockingTableComponentResource."""

import warnings

import pulumi

from components.dynamodb import TABLE_NAME, DeltaLockingTableComponentResource


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

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            DeltaLockingTableComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
