import pulumi
import pulumi_aws as aws

from components.vpc import VpcComponentResource


class ServiceDiscoveryComponentResource(pulumi.ComponentResource):
    """AWS Cloud Map private DNS namespace for Dagster service-to-service discovery.

    Mirrors CDK: infrastructure/service_discovery.py
    Namespace: "dagster" (private DNS, attached to the VPC)

    Services registered by the ECS tasks:
      aemo-etl        → port 4000
      webserver-admin → port 3000
      webserver-guest → port 3000
    """

    namespace: aws.servicediscovery.PrivateDnsNamespace

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:ServiceDiscovery", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.namespace = aws.servicediscovery.PrivateDnsNamespace(
            f"{name}-dagster-namespace",
            name="dagster",
            vpc=vpc.vpc.id,
            description="Private DNS namespace for Dagster service discovery",
            opts=self.child_opts,
        )

        self.register_outputs({"namespace_id": self.namespace.id})
