import pathlib as pt
from infrastructure.ecr import repository


from typing import Unpack

import subprocess
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
            pt.Path("../../backend-services/dagster-etl-services/aemo-etl/")
            .absolute()
            .resolve()
            .as_posix()
        )

        _ = subprocess.run(
            f"cd {directory}; ./scripts/get-common.sh",
            shell=True,
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
