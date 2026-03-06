from unittest.mock import MagicMock

import pytest
from dagster import AssetsDefinition

from aemo_etl.factories.download_nemweb_public_files_to_s3.factory import (
    download_link_and_upload_to_s3_asset_factory,
)
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.dynamic_nemweb_links_fetcher import (
    DynamicNEMWebLinksFetcher,
)
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.nemweb_link_fetcher import (
    NEMWebLinkFetcher,
)
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.nemweb_link_processor import (
    S3NemwebLinkProcessor,
)
from aemo_etl.factories.download_nemweb_public_files_to_s3.ops.processed_link_combiner import (
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
def mock_processed_link_combiner() -> ProcessedLinkedCombiner:
    return MagicMock(spec=ProcessedLinkedCombiner)


def test_factory_returns_assets_definition(
    mock_nemweb_link_fetcher: NEMWebLinkFetcher,
    mock_dynamic_nemweb_links_fetcher: DynamicNEMWebLinksFetcher,
    mock_nemweb_link_processor: S3NemwebLinkProcessor,
    mock_processed_link_combiner: ProcessedLinkedCombiner,
) -> None:
    result = download_link_and_upload_to_s3_asset_factory(
        name="test_asset",
        nemweb_relative_href="Reports/Current",
        s3_landing_prefix="test-prefix",
        nemweb_link_fetcher=mock_nemweb_link_fetcher,
        dynamic_nemweb_links_fetcher=mock_dynamic_nemweb_links_fetcher,
        nemweb_link_processor=mock_nemweb_link_processor,
        processed_link_combiner=mock_processed_link_combiner,
    )

    assert isinstance(result, AssetsDefinition)
