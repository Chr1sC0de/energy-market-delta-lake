import polars as pl
import pathlib as pt

cwd = pt.Path(__file__).parent

data_folder = cwd / "mock_delta_table_factory"


def main():
    csv_files = data_folder.glob("*")

    for file in csv_files:
        _ = pl.read_csv(file, infer_schema_length=None).head().write_csv(file)


if __name__ == "__main__":
    main()
