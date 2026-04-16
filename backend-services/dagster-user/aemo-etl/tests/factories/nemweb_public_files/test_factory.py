from unittest.mock import MagicMock

import pytest
from dagster import AssetsDefinition

from aemo_etl.factories.assets.nemweb_public_files.factory import (
    nemweb_public_files_asset_factory,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_nemweb_links_fetcher import (
    DynamicNEMWebLinksFetcher,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.dynamic_zip_links_fetcher import (
    DynamicZipLinksFetcher,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.file_unzipper import FileUnzipper
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_fetcher import (
    NEMWebLinkFetcher,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.nemweb_link_processor import (
    S3NemwebLinkProcessor,
)
from aemo_etl.factories.assets.nemweb_public_files.ops.processed_link_combiner import (
    ProcessedLinkedCombiner,
)


@pytest.fixture
def mock_nemweb_link_fetcher() -> NEMWebLinkFetcher:
    return MagicMock(spec=NEMWebLinkFetcher)


@pytest.fixture
def mock_dynamic_nemweb_links_fetcher() -> DynamicNEMWebLinksFetcher:
    return MagicMock(spec=DynamicNEMWebLinksFetcher)


@pytest.fixture
def mock_nemweb_link_processor() -> S3NemwebLinkProcessor:
    return MagicMock(spec=S3NemwebLinkProcessor)


@pytest.fixture
def mock_dynamic_zip_link_fetcher() -> DynamicZipLinksFetcher:
    return MagicMock(spec=DynamicZipLinksFetcher)


@pytest.fixture
def mock_file_unzipper() -> FileUnzipper:
    return MagicMock(spec=FileUnzipper)


@pytest.fixture
def mock_processed_link_combiner() -> ProcessedLinkedCombiner:
    return MagicMock(spec=ProcessedLinkedCombiner)


def test_factory_returns_assets_definition(
    mock_nemweb_link_fetcher: NEMWebLinkFetcher,
    mock_dynamic_nemweb_links_fetcher: DynamicNEMWebLinksFetcher,
    mock_nemweb_link_processor: S3NemwebLinkProcessor,
    mock_dynamic_zip_link_fetcher: DynamicZipLinksFetcher,
    mock_file_unzipper: FileUnzipper,
    mock_processed_link_combiner: ProcessedLinkedCombiner,
) -> None:
    result = nemweb_public_files_asset_factory(
        name="test_asset",
        nemweb_relative_href="Reports/Current",
        s3_landing_prefix="test-prefix",
        nemweb_link_fetcher=mock_nemweb_link_fetcher,
        dynamic_nemweb_links_fetcher=mock_dynamic_nemweb_links_fetcher,
        nemweb_link_processor=mock_nemweb_link_processor,
        dynamic_zip_link_fetcher=mock_dynamic_zip_link_fetcher,
        file_unzipper=mock_file_unzipper,
        processed_link_combiner=mock_processed_link_combiner,
    )

    assert isinstance(result, AssetsDefinition)
