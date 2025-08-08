import datetime as dt
import zipfile
from collections import deque
from io import BytesIO
from pathlib import Path
from typing import Sequence

import bs4
import polars as pl
import requests

CWD = Path(__file__).parent

MOCKDATA_FOLDER = CWD
TARGET_FILE_SIZE = 0.0075


def get_nemweb_links_op() -> list[str]:
    root_url = "https://www.nemweb.com.au"
    relative_url = "REPORTS/CURRENT/VicGas"

    paths = deque([f"{root_url}/{relative_url}"])

    links: list[str] = []

    while paths:
        path = paths.popleft()
        response = requests.get(path)

        response.raise_for_status()

        soup = bs4.BeautifulSoup(response.text, features="html.parser")

        hyperlinks: Sequence[bs4.Tag] = [
            element for element in soup.find_all("a") if isinstance(element, bs4.Tag)
        ]

        for tag in hyperlinks:
            relative_href: str = str(tag.get("href"))
            relative_href = relative_href.lstrip("/")
            absolute_href: str = f"{root_url}/{relative_href}"
            if not relative_href.endswith("/"):
                if isinstance(tag.previous_element, str):
                    if absolute_href.lower().endswith(".csv"):
                        links.append(absolute_href)
    return links


def main():
    # download base csv files
    nemweb_links = get_nemweb_links_op()

    for link in nemweb_links:
        filename = link.rsplit("/", 1)[-1]
        parquet_file = pl.read_csv(
            BytesIO(requests.get(link).content), infer_schema_length=None
        )

        file_name = filename.lower()
        file_size = parquet_file.estimated_size("mb")
        write_file = MOCKDATA_FOLDER / file_name.replace("csv", "parquet")

        if file_size > TARGET_FILE_SIZE:
            n_rows = len(parquet_file)
            size_per_row = file_size / n_rows
            n_rows_to_keep = int(TARGET_FILE_SIZE / size_per_row)
            parquet_file.head(n_rows_to_keep).write_parquet(write_file)
        else:
            parquet_file.write_parquet(write_file)

    # now get some historical data to add some spice

    zip_bytes = BytesIO(
        requests.get(
            "https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/PUBLICRPTS31.ZIP"
        ).content
    )

    with zipfile.ZipFile(zip_bytes) as f:
        namelist = f.namelist()
        for file_name in namelist:
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
