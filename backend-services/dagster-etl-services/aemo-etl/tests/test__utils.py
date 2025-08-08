from pathlib import Path
from collections.abc import Generator
from io import BytesIO, StringIO
from logging import INFO, Formatter, Logger, StreamHandler

from dagster import build_op_context
from pytest import fixture
from types_boto3_s3 import S3Client

from aemo_etl.configuration import BRONZE_BUCKET
from aemo_etl.util import (
    get_df_from_s3_keys,
    get_s3_object_keys_from_prefix_and_name_glob,
    newline_join,
)
from aemo_etl.util import get_lazyframe_num_rows, get_metadata_schema, split_list

# pyright: reportUnusedParameter=false

cwd = Path(__file__).parent
mock_data_folder = cwd / "@mockdata"

mock_files = [
    file for file in mock_data_folder.glob("*") if not file.name.endswith(".py")
]

#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                        fixtures                                        │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


@fixture(scope="function", autouse=True)
def upload_files(create_buckets: None, s3: S3Client):
    for file in mock_files:
        s3.upload_fileobj(
            Fileobj=BytesIO(file.read_bytes()),
            Bucket=BRONZE_BUCKET,
            Key=f"prefix/{file.name}",
        )


@fixture(scope="function")
def string_logger() -> Generator[Logger]:
    stream = StringIO()

    logger = Logger("test_logger")
    handler = StreamHandler(stream)
    formatter = Formatter("%(levelname)s-%(message)s")

    handler.setFormatter((formatter))
    logger.addHandler(handler)
    logger.setLevel(INFO)
    yield logger
    stream.close()


#     ╭────────────────────────────────────────────────────────────────────────────────────────╮
#     │                                         tests                                          │
#     ╰────────────────────────────────────────────────────────────────────────────────────────╯


def test__newline_join():
    assert "\n".join(["line 1", "line 2"]) == newline_join("line 1", "line 2")


class Test__get_s3_object_keys_from_prefix_and_name_glob:
    def test__case_insensitive(
        self,
        s3: S3Client,
    ):
        s3_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3, BRONZE_BUCKET, "prefix", "mock*"
        )

        assert s3_keys == [
            "prefix/mock_3.parquet",
            "prefix/mOck_2.CSV",
            "prefix/mock_1.csv",
            "prefix/mock_3.parquet",
            "prefix/mock_3.unsupported",
        ]

    def test__case_sensitive(
        self,
        s3: S3Client,
    ):
        s3_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3,
            BRONZE_BUCKET,
            "prefix",
            "mock*",
            case_insensitive=False,
        )

        assert s3_keys == [
            "prefix/mock_1.csv",
            "prefix/mock_3.parquet",
            "prefix/mock_3.unsupported",
        ]


class Test__get_df_from_s3_keys:
    def test__existing_object_keys(self, s3: S3Client):
        s3_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3, BRONZE_BUCKET, "prefix", "mock_*", case_insensitive=False
        )
        df = get_df_from_s3_keys(
            s3, BRONZE_BUCKET, s3_keys, logger=build_op_context().log
        )
        assert {k: v.to_list() for k, v in df.collect().to_dict().items()} == {
            "column_a": [1, 4, 7, 1, 2, 3],
            "column_b": [2, 5, 8, 3, 4, 5],
            "column_c": [3, 6, 9, 1, 2, 3],
            "source_file": [
                "s3://dev-energy-market-bronze/prefix/mock_1.csv",
                "s3://dev-energy-market-bronze/prefix/mock_1.csv",
                "s3://dev-energy-market-bronze/prefix/mock_1.csv",
                "s3://dev-energy-market-bronze/prefix/mock_3.parquet",
                "s3://dev-energy-market-bronze/prefix/mock_3.parquet",
                "s3://dev-energy-market-bronze/prefix/mock_3.parquet",
            ],
        }

    def test__zero_bytes(self, s3: S3Client, string_logger: Logger):
        s3_keys = get_s3_object_keys_from_prefix_and_name_glob(
            s3, BRONZE_BUCKET, "prefix", "mock_*", case_insensitive=False
        )

        class PatchedS3Client:
            def get_object(*args, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType, reportUnusedParameter]
                return {"Body": BytesIO()}

        _ = get_df_from_s3_keys(
            PatchedS3Client(),  # pyright: ignore[reportArgumentType]
            BRONZE_BUCKET,
            s3_keys,
            logger=string_logger,
        )

        stream_content: str = string_logger.handlers[0].stream.getvalue().strip("\n")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportUnknownMemberType, reportUnknownMemberType, reportAttributeAccessIssue]

        assert stream_content == newline_join(
            "INFO-processing s3://dev-energy-market-bronze/prefix/mock_1.csv",
            "INFO-prefix/mock_1.csv contains 0 bytes",
            "INFO-processing s3://dev-energy-market-bronze/prefix/mock_3.parquet",
            "INFO-prefix/mock_3.parquet contains 0 bytes",
            "INFO-processing s3://dev-energy-market-bronze/prefix/mock_3.unsupported",
            "INFO-prefix/mock_3.unsupported contains 0 bytes",
            "INFO-no valid dataframes found returning empty dataframe",
        )

    def test__failed_to_get(self, s3: S3Client, string_logger: Logger):
        s3_keys = [
            key.replace("mock", "failed_mock")
            for key in get_s3_object_keys_from_prefix_and_name_glob(
                s3, BRONZE_BUCKET, "prefix", "mock_*", case_insensitive=False
            )
        ]

        _ = get_df_from_s3_keys(
            s3,
            BRONZE_BUCKET,
            s3_keys,
            logger=string_logger,
        )

        stream_content: str = string_logger.handlers[0].stream.getvalue().strip("\n")  # pyright: ignore[reportUnknownVariableType, reportUnknownMemberType, reportUnknownMemberType, reportUnknownMemberType, reportAttributeAccessIssue]

        assert stream_content == newline_join(
            "INFO-processing s3://dev-energy-market-bronze/prefix/failed_mock_1.csv",
            "INFO-key prefix/failed_mock_1.csv does not exist",
            "INFO-processing s3://dev-energy-market-bronze/prefix/failed_mock_3.parquet",
            "INFO-key prefix/failed_mock_3.parquet does not exist",
            "INFO-processing s3://dev-energy-market-bronze/prefix/failed_mock_3.unsupported",
            "INFO-key prefix/failed_mock_3.unsupported does not exist",
            "INFO-no valid dataframes found returning empty dataframe",
        )


def test__get_metadata_schema():
    import polars as pl
    from dagster import TableColumn, TableSchema

    # Test with schema only (no descriptions)
    schema = {"id": pl.Int64, "name": pl.String, "value": pl.Float64}

    result = get_metadata_schema(schema)

    assert isinstance(result, TableSchema)
    assert len(result.columns) == 3
    assert result.columns[0] == TableColumn(name="id", type="Int64", description=None)
    assert result.columns[1] == TableColumn(
        name="name", type="String", description=None
    )
    assert result.columns[2] == TableColumn(
        name="value", type="Float64", description=None
    )

    # Test with schema and descriptions
    descriptions = {
        "id": "Unique identifier",
        "name": "Item name",
        # Deliberately omit description for "value" to test default behavior
    }

    result_with_desc = get_metadata_schema(schema, descriptions)

    assert isinstance(result_with_desc, TableSchema)
    assert len(result_with_desc.columns) == 3
    assert result_with_desc.columns[0] == TableColumn(
        name="id", type="Int64", description="Unique identifier"
    )
    assert result_with_desc.columns[1] == TableColumn(
        name="name", type="String", description="Item name"
    )
    assert result_with_desc.columns[2] == TableColumn(
        name="value", type="Float64", description=None
    )


def test__get_lazyframe_num_rows():
    import polars as pl

    # Test with empty dataframe
    empty_df = pl.LazyFrame()
    assert get_lazyframe_num_rows(empty_df) == 0

    # Test with dataframe containing rows
    data = {"column_a": [1, 2, 3, 4, 5], "column_b": ["a", "b", "c", "d", "e"]}
    df = pl.DataFrame(data).lazy()
    assert get_lazyframe_num_rows(df) == 5

    # Test with single row dataframe
    single_row_df = pl.DataFrame({"column_a": [1], "column_b": ["a"]}).lazy()
    assert get_lazyframe_num_rows(single_row_df) == 1


def test__split_list():
    empty_list: list[str] = []
    splits = list(split_list(empty_list, 3))
    assert splits == []

    small_list = [1, 2]
    splits = list(split_list(small_list, 3))
    assert splits == [[1], [2]]

    equal_list = [1, 2, 3]
    splits = list(split_list(equal_list, 3))
    assert splits == [[1], [2], [3]]

    large_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    splits = list(split_list(large_list, 3))
    assert splits == [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10]]

    uneven_list = [1, 2, 3, 4, 5]
    splits = list(split_list(uneven_list, 3))
    assert splits == [[1, 2], [3, 4], [5]]

    string_list = ["a", "b", "c", "d", "e", "f"]
    splits = list(split_list(string_list, 2))
    assert splits == [["a", "b", "c"], ["d", "e", "f"]]
