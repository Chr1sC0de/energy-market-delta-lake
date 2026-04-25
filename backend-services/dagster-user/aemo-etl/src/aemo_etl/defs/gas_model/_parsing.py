import polars as pl

MONTH_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("september", "09"),
    ("january", "01"),
    ("february", "02"),
    ("november", "11"),
    ("december", "12"),
    ("october", "10"),
    ("august", "08"),
    ("march", "03"),
    ("april", "04"),
    ("june", "06"),
    ("july", "07"),
    ("sept", "09"),
    ("jan", "01"),
    ("feb", "02"),
    ("mar", "03"),
    ("apr", "04"),
    ("may", "05"),
    ("jun", "06"),
    ("jul", "07"),
    ("aug", "08"),
    ("sep", "09"),
    ("oct", "10"),
    ("nov", "11"),
    ("dec", "12"),
)

TRUE_VALUES = ("1", "true", "y", "yes")
FALSE_VALUES = ("0", "false", "n", "no")


def _normalised_string(column: str) -> pl.Expr:
    return pl.col(column).cast(pl.String).str.to_lowercase().str.strip_chars()


def parse_gas_datetime(column: str) -> pl.Expr:
    source = _normalised_string(column)

    for month_name, month_number in MONTH_REPLACEMENTS:
        source = source.str.replace_all(rf"\b{month_name}\b", month_number)

    return pl.coalesce(
        source.str.strptime(pl.Datetime("us"), "%d %m %Y %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%d %m %Y", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y/%m/%d", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y-%m-%d %H:%M:%S", strict=False),
        source.str.strptime(pl.Datetime("us"), "%Y-%m-%d", strict=False),
    )


def parse_yes_no_bool(column: str) -> pl.Expr:
    source = _normalised_string(column)

    return (
        pl.when(source.is_in(TRUE_VALUES))
        .then(pl.lit(True))
        .when(source.is_in(FALSE_VALUES))
        .then(pl.lit(False))
        .otherwise(pl.lit(None))
        .cast(pl.Boolean)
    )
