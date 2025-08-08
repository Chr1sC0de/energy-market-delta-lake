from pathlib import Path

import polars as pl

CWD = Path(__file__).parent

MOCKDATA_FOLDER = CWD
TARGET_FILE_SIZE = 0.0075


def main():
    namelist = list(CWD.glob("*.parquet"))
    for file_name in namelist:
        parquet_file = pl.read_parquet(file_name)

        file_size = parquet_file.estimated_size("mb")

        if file_size > TARGET_FILE_SIZE:
            n_rows = len(parquet_file)
            size_per_row = file_size / n_rows
            n_rows_to_keep = int(TARGET_FILE_SIZE / size_per_row)
            parquet_file.head(n_rows_to_keep).write_parquet(file_name)
        else:
            parquet_file.write_parquet(file_name)

    return


if __name__ == "__main__":
    main()
