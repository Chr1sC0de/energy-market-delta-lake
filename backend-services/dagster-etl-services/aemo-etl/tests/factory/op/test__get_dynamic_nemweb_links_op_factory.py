from datetime import datetime

from dagster import OpExecutionContext, build_op_context
from pytest import fixture

from aemo_etl.configuration import Link
from aemo_etl.factory.op._get_dynamic_nemweb_links_op_factory import (
    get_dynamic_nemweb_links_op_factory,
)


@fixture(scope="function")
def links() -> list[Link]:
    return [
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT029A_V4_SYSTEM_NOTICES_1.CSV",
            source_upload_datetime=datetime(2025, 4, 27, 9, 10),
        ),
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT037B_V4_INDICATIVE_MKT_PRICE_1.CSV",
            source_upload_datetime=datetime(2025, 4, 27, 15, 16),
        ),
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT037C_V4_INDICATIVE_PRICE_1.CSV",
            source_upload_datetime=datetime(2025, 4, 27, 14, 12),
        ),
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT039B_V4_INDICATIVE_LOCATIONAL_PRICE_1.CSV",
            source_upload_datetime=datetime(2024, 12, 23, 9, 21),
        ),
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT041_V4_MARKET_AND_REFERENCE_PRICES_1.CSV",
            source_upload_datetime=datetime(2025, 4, 27, 8, 7),
        ),
        Link(
            source_absolute_href="https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT042_V4_WEIGHTED_AVERAGE_DAILY_PRICES_1.CSV",
            source_upload_datetime=datetime(2025, 3, 26, 11, 16),
        ),
    ]


class Test__get_dynamic_download_groups_op_factory:
    def test__no_filter(self, links: list[Link]) -> None:
        outputs = list(get_dynamic_nemweb_links_op_factory()(build_op_context(), links))

        assert set([output.value.source_absolute_href for output in outputs]) == set(
            [link.source_absolute_href for link in links]
        )

    def test__with_filter(self, links: list[Link]) -> None:
        excludeed_link = "https://www.nemweb.com.au/REPORTS/CURRENT/VicGas/INT029A_V4_SYSTEM_NOTICES_1.CSV"

        def _link_filter(_: OpExecutionContext, link: Link) -> bool:
            return link.source_absolute_href != excludeed_link

        outputs = list(
            get_dynamic_nemweb_links_op_factory(link_filter=_link_filter)(
                build_op_context(),
                links,
            )
        )

        assert set(
            [
                output.value.source_absolute_href
                for output in outputs
                if output.value.source_absolute_href != excludeed_link
            ]
        ) == set(
            [
                link.source_absolute_href
                for link in links
                if link.source_absolute_href != excludeed_link
            ]
        )
