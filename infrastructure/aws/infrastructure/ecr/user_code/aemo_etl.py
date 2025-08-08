import pathlib as pt
from typing import Unpack

from constructs import Construct

from infrastructure.ecr import repository
from infrastructure.utils import StackKwargs


class Stack(repository.Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        **kwargs: Unpack[StackKwargs],
    ):
        directory = (
            pt.Path("../../backend-services/dagster-etl-services/aemo-etl/")
            .absolute()
            .resolve()
            .as_posix()
        )

        super().__init__(
            scope,
            id,
            repository_prefix="dagster/user-code",
            repository_suffix="aemo-etl",
            directory=directory,
            image_target="dagster-grpc",
            **kwargs,
        )
