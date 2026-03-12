import pytest
from dagster import asset, materialize
from polars import Int64, LazyFrame, scan_delta
from polars.testing import assert_frame_equal

from aemo_etl.configs import AEMO_BUCKET
from aemo_etl.defs.resources.s3_polars_deltalake_io_manager import (
    PolarsDataFrameSinkDeltaIoManager,
)
from tests.utils import MakeBucketProtocol


@pytest.fixture()
def root_uri(
    localstack_endpoint: str, create_delta_log: None, make_bucket: MakeBucketProtocol
) -> str:
    bronze_bucket_name = make_bucket(AEMO_BUCKET, random_suffix=True)
    return f"s3://{bronze_bucket_name}"


@pytest.fixture
def asset_path(root_uri: str) -> str:
    target_uri = f"{root_uri}/bronze/gasbb/asset_"
    return target_uri


class TestPolarsDataFrameSinkDeltaIoManager:
    def test_handle_output_write(self, asset_path: str, root_uri: str) -> None:
        target_df = LazyFrame(
            {"a": [1, 2, 3], "b": [4, 5, 6]}, schema={"a": Int64, "b": Int64}
        )

        @asset(
            key_prefix=["bronze", "gasbb"],
        )
        def asset_() -> LazyFrame:
            return target_df

        _ = materialize(
            [asset_],
            resources={
                "io_manager": PolarsDataFrameSinkDeltaIoManager(
                    root=root_uri,
                )
            },
        )

        assert_frame_equal(scan_delta(asset_path).sort("a"), target_df)

    # parameterize this to also cover the metadata definition
    @pytest.mark.parametrize(
        "metadata",
        [None, {"column_description": {"a": "a column", "b": "b column"}}],
    )
    def test_handle_output_merge(
        self, metadata: None | dict[str, str], asset_path: str, root_uri: str
    ) -> None:
        source_df = LazyFrame(
            {"a": [1, 2, 3], "b": [3, 4, 5]},
        )
        source_df.sink_delta(asset_path)
        upsert_df = LazyFrame({"a": [1, 2, 3, 4], "b": [3, 4, 6, 7]})

        @asset(key_prefix=["bronze", "gasbb"], metadata=metadata)
        def asset_() -> LazyFrame:
            return upsert_df

        _ = materialize(
            [asset_],
            resources={
                "io_manager": PolarsDataFrameSinkDeltaIoManager(
                    root=root_uri,
                    sink_delta_kwargs={
                        "mode": "merge",
                        "delta_merge_options": {
                            "source_alias": "s",
                            "target_alias": "t",
                            "predicate": "s.a = t.a",
                            "merge_schema": True,
                        },
                    },
                )
            },
        )
        assert_frame_equal(scan_delta(asset_path).sort("a"), upsert_df)

    def test_load_input(self, asset_path: str, root_uri: str) -> None:
        target_df = LazyFrame(
            {"a": [1, 2, 3], "b": [4, 5, 6]}, schema={"a": Int64, "b": Int64}
        )

        @asset(
            key_prefix=["bronze", "gasbb"],
        )
        def asset_1() -> LazyFrame:
            return target_df

        @asset(
            key_prefix=["bronze", "gasbb"],
        )
        def asset_(asset_1: LazyFrame) -> LazyFrame:
            return asset_1.sum()

        _ = materialize(
            [asset_, asset_1],
            resources={
                "io_manager": PolarsDataFrameSinkDeltaIoManager(
                    root=root_uri,
                )
            },
        )

        assert_frame_equal(scan_delta(asset_path), LazyFrame({"a": [6], "b": [15]}))
