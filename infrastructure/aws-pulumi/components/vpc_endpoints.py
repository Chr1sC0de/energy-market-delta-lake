import pulumi
import pulumi_aws as aws

from components.vpc import VpcComponentResource

_REGION: str = aws.config.region or "ap-southeast-2"


class VpcEndpointsComponentResource(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:VpcEndpoints", name, {}, opts)

        self.name = name
        self.vpc = vpc
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self._setup_security_group()
        self._setup_interface_endpoints()
        self._setup_gateway_endpoints()

        self.register_outputs({})

    def _setup_security_group(self) -> None:
        self.security_group = aws.ec2.SecurityGroup(
            f"{self.name}-vpc-endpoints-sg",
            vpc_id=self.vpc.vpc.id,
            description="VPC interface endpoint security group",
            opts=self.child_opts,
        )

        aws.ec2.SecurityGroupRule(
            f"{self.name}-vpc-endpoints-sg-ingress-https",
            type="ingress",
            security_group_id=self.security_group.id,
            from_port=443,
            to_port=443,
            protocol="tcp",
            cidr_blocks=[self.vpc.vpc.cidr_block],
            description="Allow HTTPS from within VPC",
            opts=pulumi.ResourceOptions(parent=self.security_group),
        )

        aws.ec2.SecurityGroupRule(
            f"{self.name}-vpc-endpoints-sg-egress-all",
            type="egress",
            security_group_id=self.security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound",
            opts=pulumi.ResourceOptions(parent=self.security_group),
        )

    def _setup_interface_endpoints(self) -> None:
        interface_services = {
            "ecr-api": f"com.amazonaws.{_REGION}.ecr.api",
            "ecr-dkr": f"com.amazonaws.{_REGION}.ecr.dkr",
            "logs": f"com.amazonaws.{_REGION}.logs",
            "ssm": f"com.amazonaws.{_REGION}.ssm",
        }

        for short_name, service_name in interface_services.items():
            endpoint = aws.ec2.VpcEndpoint(
                f"{self.name}-vpce-{short_name}",
                vpc_id=self.vpc.vpc.id,
                service_name=service_name,
                vpc_endpoint_type="Interface",
                subnet_ids=[self.vpc.private_subnet.id],
                security_group_ids=[self.security_group.id],
                private_dns_enabled=False,
                opts=self.child_opts,
            )
            setattr(self, f"endpoint_{short_name.replace('-', '_')}", endpoint)

    def _setup_gateway_endpoints(self) -> None:
        self.endpoint_s3 = aws.ec2.VpcEndpoint(
            f"{self.name}-vpce-s3",
            vpc_id=self.vpc.vpc.id,
            service_name=f"com.amazonaws.{_REGION}.s3",
            vpc_endpoint_type="Gateway",
            route_table_ids=[self.vpc.private_route_table.id],
            opts=self.child_opts,
        )

        self.endpoint_dynamodb = aws.ec2.VpcEndpoint(
            f"{self.name}-vpce-dynamodb",
            vpc_id=self.vpc.vpc.id,
            service_name=f"com.amazonaws.{_REGION}.dynamodb",
            vpc_endpoint_type="Gateway",
            route_table_ids=[self.vpc.private_route_table.id],
            opts=self.child_opts,
        )
