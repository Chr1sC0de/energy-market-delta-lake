from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import aws_servicediscovery as servicediscovery
from constructs import Construct
from infrastructure.utils import StackKwargs
from infrastructure import vpc


class Stack(_Stack):
    private_dns_namespace: servicediscovery.PrivateDnsNamespace

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)
        self.add_dependency(VpcStack)

        self.private_dns_namespace = servicediscovery.PrivateDnsNamespace(
            self,
            "PrivateDnsNamespace",
            name="dagster",
            vpc=VpcStack.vpc,
        )
