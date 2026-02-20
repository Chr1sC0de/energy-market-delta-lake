import datetime as dt
from collections import deque
from typing import Callable, Sequence, Unpack

import bs4
import dagster as dg
import requests

from aemo_etl.configuration import Link
from aemo_etl.factory.op.schema import OpKwargs

root_url: str = "https://www.nemweb.com.au"


def _default_hyperlink_tag_folder_filter(_: object, tag: bs4.Tag) -> bool:
    return tag.text != "[To Parent Directory]"


def _default_hyperlink_tag_file_filter(_: object, tag: bs4.Tag) -> bool:
    return tag.text != "CURRENTDAY.ZIP"


TagFilter = Callable[[dg.OpExecutionContext, bs4.Tag], bool] | None
OverrideGetLinksFilterFunction = Callable[[dg.OpExecutionContext], list[Link]] | None


def get_nemweb_links_op_factory(
    relative_root_href: str,
    hyperlink_tag_folder_filter: TagFilter = None,
    hyperlink_tag_file_filter: TagFilter = None,
    override_get_links_fn: OverrideGetLinksFilterFunction = None,
    **op_kwargs: Unpack[OpKwargs],
) -> dg.OpDefinition:
    op_kwargs.setdefault("name", "get_nemweb_links_op")
    op_kwargs.setdefault(
        "description",
        f"get list of file links from {root_url}/{relative_root_href}",
    )
    if hyperlink_tag_folder_filter is None:
        hyperlink_tag_folder_filter = _default_hyperlink_tag_folder_filter

    if hyperlink_tag_file_filter is None:
        hyperlink_tag_file_filter = _default_hyperlink_tag_file_filter

    @dg.op(**op_kwargs)
    def get_nemweb_links_op(context: dg.OpExecutionContext) -> list[Link]:
        if override_get_links_fn is None:
            tag: bs4.Tag

            paths = deque([f"{root_url}/{relative_root_href}"])
            links: list[Link] = []

            while paths:
                path = paths.popleft()
                response = requests.get(path)

                response.raise_for_status()

                soup = bs4.BeautifulSoup(response.text, features="html.parser")

                hyperlinks: Sequence[bs4.Tag] = [
                    element
                    for element in soup.find_all("a")
                    if isinstance(element, bs4.Tag)
                ]

                for tag in hyperlinks:
                    relative_href: str = str(tag.get("href"))
                    relative_href = relative_href.lstrip("/")
                    absolute_href: str = f"{root_url}/{relative_href}"
                    if relative_href.endswith("/"):
                        if hyperlink_tag_folder_filter(context, tag):
                            paths.append(absolute_href)
                    else:
                        if hyperlink_tag_file_filter(context, tag):
                            if isinstance(tag.previous_element, str):
                                datetime_string = " ".join(
                                    tag.previous_element.split()[:-1]
                                )
                                upload_datetime = dt.datetime.strptime(
                                    datetime_string, "%A, %B %d, %Y %I:%M %p"
                                )
                                links.append(
                                    Link(
                                        source_absolute_href=absolute_href,
                                        source_upload_datetime=upload_datetime,
                                    )
                                )
            return links
        else:
            return override_get_links_fn(context)

    return get_nemweb_links_op
