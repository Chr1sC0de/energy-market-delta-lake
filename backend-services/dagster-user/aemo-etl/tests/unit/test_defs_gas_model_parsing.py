from datetime import datetime

import polars as pl

from aemo_etl.defs.gas_model._parsing import parse_gas_datetime, parse_yes_no_bool


def test_parse_gas_datetime_handles_source_date_formats() -> None:
    df = pl.LazyFrame(
        {
            "source_value": [
                "01 Jan 2024",
                "01 January 2024",
                "01 Jan 2024 03:00:00",
                "01 January 2024 03:00:00",
                "2024-01-01",
                "2024/01/01 03:00:00",
                None,
            ]
        }
    )

    result = df.select(parse_gas_datetime("source_value").alias("parsed")).collect()

    assert result["parsed"].to_list() == [
        datetime(2024, 1, 1),
        datetime(2024, 1, 1),
        datetime(2024, 1, 1, 3),
        datetime(2024, 1, 1, 3),
        datetime(2024, 1, 1),
        datetime(2024, 1, 1, 3),
        None,
    ]


def test_parse_yes_no_bool_handles_source_boolean_formats() -> None:
    df = pl.LazyFrame(
        {
            "source_value": [
                "Y",
                "N",
                "yes",
                "no",
                "true",
                "false",
                "1",
                "0",
                "unknown",
                None,
            ]
        }
    )

    result = df.select(parse_yes_no_bool("source_value").alias("parsed")).collect()

    assert result["parsed"].to_list() == [
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
        None,
        None,
    ]
