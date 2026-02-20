import pathlib as pt

import boto3
import polars as pl

# pyright: reportTypedDictNotRequiredAccess=false

CWD = pt.Path(__file__).parent

MOCKDATA_FOLDER = CWD

TARGET_FILE_SIZE = 0.0075

BUCKET = "dev-energy-market-bronze"


def main() -> None:
    s3_client = boto3.client("s3")

    objects = s3_client.list_objects_v2(
        Bucket=BUCKET,
        Prefix="aemo/gasbb/",
        Delimiter="/",
    )

    for common_prefix in objects["CommonPrefixes"]:
        prefix = common_prefix["Prefix"]

        table_name = prefix.rsplit("/", 1)[0].split("/")[-1]

        df = pl.read_delta(f"s3://{BUCKET}/{prefix}")

        file_size = df.estimated_size("mb")

        write_file = MOCKDATA_FOLDER / table_name

        if file_size > TARGET_FILE_SIZE:
            n_rows = len(df)
            size_per_row = file_size / n_rows
            n_rows_to_keep = int(TARGET_FILE_SIZE / size_per_row)
            df.head(n_rows_to_keep).write_delta(write_file)
        else:
            df.write_delta(write_file)


if __name__ == "__main__":
    main()
