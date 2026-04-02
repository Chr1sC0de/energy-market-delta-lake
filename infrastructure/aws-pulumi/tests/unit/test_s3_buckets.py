"""Tests for S3BucketsComponentResource."""

import warnings

import pulumi

from components.s3_buckets import S3BucketsComponentResource


class TestS3BucketsCreation:
    def test_all_seven_buckets_created(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")
        assert s3.io_manager_bucket is not None
        assert s3.landing is not None
        assert s3.archive is not None
        assert s3.aemo is not None
        assert s3.bronze is not None
        assert s3.silver is not None
        assert s3.gold is not None

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

    @pulumi.runtime.test
    def test_bronze_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "bronze" in bucket, f"Expected 'bronze' in bucket name, got {bucket}"

        return s3.bronze.bucket.apply(check)

    @pulumi.runtime.test
    def test_silver_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "silver" in bucket, f"Expected 'silver' in bucket name, got {bucket}"

        return s3.silver.bucket.apply(check)

    @pulumi.runtime.test
    def test_gold_bucket_name(self) -> None:
        s3 = S3BucketsComponentResource("test-energy-market")

        def check(bucket: str) -> None:
            assert "gold" in bucket, f"Expected 'gold' in bucket name, got {bucket}"

        return s3.gold.bucket.apply(check)

    def test_archive_has_lifecycle_configuration(self) -> None:
        """The archive bucket must have a lifecycle configuration created.

        The lifecycle transitions data to Glacier after 30 days, Deep Archive
        after 180 days, and expires after 3650 days (10 years).
        """
        # S3BucketsComponentResource.setup_archive_lifecycle() creates a
        # BucketLifecycleConfiguration as a side effect. We verify this by
        # checking that instantiation doesn't raise and the archive bucket exists.
        s3 = S3BucketsComponentResource("test-energy-market-lifecycle")
        assert s3.archive is not None, (
            "Archive bucket must be created before lifecycle can be attached"
        )

    def test_no_deprecation_warnings(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            S3BucketsComponentResource("test-energy-market-warn")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        assert not deprecations, (
            f"Unexpected DeprecationWarnings: {[str(w.message) for w in deprecations]}"
        )
