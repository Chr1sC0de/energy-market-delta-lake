import datetime as dt
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Callable

import bs4
from dagster import OpDefinition, OpExecutionContext, op
from requests.models import Response

from aemo_etl.factories.nemweb_public_files.data_models import Link
from aemo_etl.utils import request_get

ROOT_URL = "https://www.nemweb.com.au"

TagFilter = Callable[[OpExecutionContext, bs4.Tag], bool]


class NEMWebLinkFetcher(ABC):
    @abstractmethod
    def fetch(self, context: OpExecutionContext, relative_root_href: str) -> list[Link]:
        raise NotImplementedError


def build_nemweb_link_fetcher_op(
    name: str,
    href: str,
    fetcher: NEMWebLinkFetcher,
) -> OpDefinition:

    @op(
        name=f"{name}_nemweb_link_fetcher_op",
        description=f"fetch the list of links from {href}",
    )
    def _op(context: OpExecutionContext) -> list[Link]:
        return fetcher.fetch(context, href)

    return _op


def default_folder_filter(_: OpExecutionContext, tag: bs4.Tag) -> bool:
    tag_text: str = tag.text
    return tag_text != "[To Parent Directory]"


def default_file_filter(_: OpExecutionContext, tag: bs4.Tag) -> bool:
    tag_text: str = tag.text
    return tag_text != "CURRENTDAY.ZIP"


def soup_getter(html: str) -> bs4.BeautifulSoup:
    return bs4.BeautifulSoup(html, features="html.parser")


@dataclass
class HTTPNEMWebLinkFetcher(NEMWebLinkFetcher):
    folder_filter: TagFilter = default_folder_filter
    file_filter: TagFilter = default_file_filter
    soup_getter: Callable[[str], bs4.BeautifulSoup] = soup_getter
    request_getter: Callable[[str], Response] = request_get

    def fetch(self, context: OpExecutionContext, relative_root_href: str) -> list[Link]:
        tag: bs4.Tag

        paths = deque([f"{ROOT_URL}/{relative_root_href}"])
        links: list[Link] = []

        while paths:
            path = paths.popleft()

            response = self.request_getter(path)
            soup = self.soup_getter(response.text)

            hyperlinks: Sequence[bs4.Tag] = [
                element
                for element in soup.find_all("a")
                if isinstance(element, bs4.Tag)
            ]

            for tag in hyperlinks:
                relative_href: str = str(tag.get("href"))
                relative_href = relative_href.lstrip("/")
                absolute_href: str = f"{ROOT_URL}/{relative_href}"
                if relative_href.endswith("/"):
                    if self.folder_filter(context, tag):
                        paths.append(absolute_href)
                else:
                    if self.file_filter(context, tag):
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
