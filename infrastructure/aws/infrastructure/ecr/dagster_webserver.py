import pathlib as pt
from infrastructure.ecr import repository


from typing import Unpack

from constructs import Construct

from infrastructure.utils import StackKwargs


class Stack(repository.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs: Unpack[StackKwargs],
    ):
        directory = (
            pt.Path("../../backend-services/dagster-webserver-service")
            .absolute()
            .resolve()
            .as_posix()
        )

        super().__init__(
            scope,
            id,
            repository_prefix="dagster",
            repository_suffix="webserver",
            directory=directory,
            image_target="dagster-webserver",
            **kwargs,
        )
