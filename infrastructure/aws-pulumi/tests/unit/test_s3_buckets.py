"""Tests for S3BucketsComponentResource."""

import warnings

import pulumi
import pytest

import components.s3_buckets as s3_buckets_module
from components.s3_buckets import S3BucketsComponentResource


@pytest.fixture(autouse=True)
def mock_bucket_exists(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep unit tests hermetic by bypassing live boto3 bucket lookups."""
    monkeypatch.setattr(s3_buckets_module, "bucket_exists", lambda _bucket_name: False)


class TestS3BucketsCreation:
    def test_all_expected_buckets_created(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")
        assert s3.io_manager_bucket is not None
        assert s3.landing is not None
        assert s3.archive is not None
        assert s3.aemo is not None

    @pulumi.runtime.test
    def test_io_manager_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "io-manager" in bucket, (
                f"Expected 'io-manager' in bucket name, got {bucket}"
            )

        return s3.io_manager_bucket.bucket.apply(check)

    @pulumi.runtime.test
    def test_landing_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "landing" in bucket, (
                f"Expected 'landing' in bucket name, got {bucket}"
            )

        return s3.landing.bucket.apply(check)

    @pulumi.runtime.test
    def test_archive_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "archive" in bucket, (
                f"Expected 'archive' in bucket name, got {bucket}"
            )

        return s3.archive.bucket.apply(check)

    @pulumi.runtime.test
    def test_aemo_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "aemo" in bucket, f"Expected 'aemo' in bucket name, got {bucket}"

        return s3.aemo.bucket.apply(check)

    def test_archive_lifecycle_setup_is_invoked(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The component must attach archive lifecycle rules during construction."""
        called = False

        original = S3BucketsComponentResource.setup_archive_lifecycle

        def wrapped(self: S3BucketsComponentResource) -> None:
            nonlocal called
            called = True
            original(self)

        monkeypatch.setattr(
            S3BucketsComponentResource, "setup_archive_lifecycle", wrapped
        )
        s3 = S3BucketsComponentResource("test-energy-market-lifecycle")

        assert s3.archive is not None
        assert called, "Expected setup_archive_lifecycle() to be invoked during init"

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            S3BucketsComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
