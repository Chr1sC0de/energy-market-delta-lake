import re
from typing import Callable, Unpack

import dagster as dg

from aemo_etl.configuration import Link
from aemo_etl.factory.op.schema import OpKwargs


def _default_link_filter(*_: object) -> bool:
    return True


LinkFilters = Callable[[dg.OpExecutionContext, Link], bool] | None


def get_dynamic_nemweb_links_op_factory(
    link_filter: LinkFilters = None,
    **op_factory_kwargs: Unpack[OpKwargs],
) -> dg.OpDefinition:
    op_factory_kwargs.setdefault("name", "get_dynamic_nemweb_links_op")
    op_factory_kwargs.setdefault("description", "create a dynamic output for each link")
    op_factory_kwargs.setdefault("out", dg.DynamicOut())

    if link_filter is None:
        link_filter = _default_link_filter

    @dg.op(**op_factory_kwargs)
    def get_dynamic_nemweb_links_op(
        context: dg.OpExecutionContext,
        links: list[Link],
    ) -> list[dg.DynamicOutput[Link]]:
        context.log.info("creating dynamic download group")

        output = []

        for link in links:
            if link_filter(context, link):
                output.append(
                    dg.DynamicOutput[Link](
                        link,
                        mapping_key=re.sub(
                            "[^0-9a-zA-Z]+",
                            "_",
                            link.source_absolute_href.split("/")[-1],
                        ),
                    )
                )

        context.log.info("finished creating dynamic download group")
        return output

    return get_dynamic_nemweb_links_op
