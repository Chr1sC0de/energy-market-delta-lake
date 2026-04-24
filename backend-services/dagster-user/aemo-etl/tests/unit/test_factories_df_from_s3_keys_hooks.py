import polars as pl

from aemo_etl.factories.df_from_s3_keys.hooks import Deduplicate


def test_deduplicate_removes_duplicates() -> None:
    df = pl.LazyFrame(
        {
            "surrogate_key": ["a", "a", "b"],
            "value": [1, 2, 3],
        }
    )
    hook = Deduplicate()
    result = hook.process("bucket", "key", df)
    collected = result.collect()
    # Only first occurrence per surrogate_key kept
    assert len(collected) == 2
    assert set(collected["surrogate_key"]) == {"a", "b"}


def test_deduplicate_no_duplicates() -> None:
    df = pl.LazyFrame(
        {
            "surrogate_key": ["x", "y"],
            "value": [10, 20],
        }
    )
    hook = Deduplicate()
    result = hook.process("bucket", "key", df)
    collected = result.collect()
    assert len(collected) == 2
