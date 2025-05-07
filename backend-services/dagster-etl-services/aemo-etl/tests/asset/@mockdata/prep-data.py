import polars as pl
from io import BytesIO
from pathlib import Path
import requests
import zipfile


CWD = Path(__file__).parent

MOCKDATA_FOLDER = CWD
TARGET_FILE_SIZE = 0.0075


def main():
    zip_bytes = BytesIO(
        requests.get(
            "https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PUBLICRPTS01.ZIP"
        ).content
    )

    with zipfile.ZipFile(zip_bytes) as f:
        for file_name in f.namelist():
            if file_name.lower().endswith("csv"):
                parquet_file = pl.read_csv(
                    BytesIO(f.read(file_name)), infer_schema_length=None
                )

                file_name = file_name.lower()
                file_size = parquet_file.estimated_size("mb")
                write_file = MOCKDATA_FOLDER / file_name.replace("csv", "parquet")

                if file_size > TARGET_FILE_SIZE:
                    n_rows = len(parquet_file)
                    size_per_row = file_size / n_rows
                    n_rows_to_keep = int(TARGET_FILE_SIZE / size_per_row)
                    parquet_file.head(n_rows_to_keep).write_parquet(write_file)
                else:
                    parquet_file.write_parquet(write_file)

    return


if __name__ == "__main__":
    main()
