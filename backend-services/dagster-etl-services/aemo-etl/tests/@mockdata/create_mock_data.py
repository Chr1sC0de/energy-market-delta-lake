import pathlib as pt
import polars as pl

cwd = pt.Path(__file__).parent
mock_data_folder = cwd / "@mockdata"


def main() -> None:
    pl.DataFrame(
        {
            "column_a": [1, 2, 3],
            "column_b": [3, 4, 5],
            "column_c": [1, 2, 3],
        }
    ).write_parquet("mock_3.parquet")

    pl.DataFrame(
        {
            "column_a": [1, 2, 3],
            "column_b": [3, 4, 5],
            "column_c": [1, 2, 3],
        }
    ).write_parquet("mOCK_3.Parquet")


if __name__ == "__main__":
    main()
