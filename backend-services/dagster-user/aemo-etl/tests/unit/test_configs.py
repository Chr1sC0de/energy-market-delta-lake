import aemo_etl.configs as cfg


def test_configs_are_strings() -> None:
    assert isinstance(cfg.NAME_PREFIX, str)
    assert isinstance(cfg.DEVELOPMENT_ENVIRONMENT, str)
    assert isinstance(cfg.DEVELOPMENT_LOCATION, str)
    assert isinstance(cfg.SHARED_PREFIX, str)
    assert isinstance(cfg.IO_MANAGER_BUCKET, str)
    assert isinstance(cfg.LANDING_BUCKET, str)
    assert isinstance(cfg.ARCHIVE_BUCKET, str)
    assert isinstance(cfg.AEMO_BUCKET, str)
    assert isinstance(cfg.DAGSTER_URI, str)
