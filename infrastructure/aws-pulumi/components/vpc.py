"""VPC component for the AWS network foundation."""

from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls
from pulumi_aws import get_availability_zones

from configs import ADMINISTRATOR_IPS


class VpcComponentResource(pulumi.ComponentResource):
    """VPC, subnets, NAT instance, and route tables for the stack."""

    def __init__(
        self,
        name: str,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the VPC component."""
        super().__init__(f"{name}:components:vpc", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_vpc()
        self.setup_availability_zones()
        self.setup_internet_gateways()
        self.setup_fk_nat_eip()
        self.setup_fk_nat_private_key()
        self.setup_fk_nat_key_pair()
        self.setup_fk_nat_security_groups()
        self.setup_fk_nat_security_group_private_ingress()
        self.setup_fk_nat_security_group_egress()
        self.setup_subnets()
        self.setup_fk_nat_instance()
        self.setup_route_tables()
        self.setup_routes()

        self.register_outputs({})

    def setup_vpc(self) -> None:
        """Create the base VPC."""
        self.vpc = aws.ec2.Vpc(
            f"{self.name}-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            opts=self.child_opts,
        )

    def setup_availability_zones(self) -> None:
        """Select the first available Availability Zone."""
        self.availability_zone_results = get_availability_zones(state="available")
        self.availability_zone = self.availability_zone_results.names[0]

    def setup_internet_gateways(self) -> None:
        """Create the internet gateway for public routing."""
        self.internet_gateway = aws.ec2.InternetGateway(
            f"{self.name}-internet-gateway",
            vpc_id=self.vpc.id,
            opts=self.child_opts,
        )

    def setup_fk_nat_eip(self) -> None:
        """Create the Elastic IP for the fck-nat instance."""
        self.fk_nat_eip = aws.ec2.Eip(
            f"{self.name}-fk-nat-eip",
            domain="vpc",
            opts=self.child_opts,
        )

    def setup_fk_nat_private_key(self) -> None:
        """Create the private key for the fck-nat instance."""
        self.fk_nat_private_key = tls.PrivateKey(
            f"{self.name}-fk-nat-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )

    def setup_fk_nat_key_pair(self) -> None:
        """Create the EC2 key pair for the fck-nat instance."""
        self.fk_nat_key_pair = aws.ec2.KeyPair(
            f"{self.name}-fck-nat-instance-key-pair",
            key_name="fck-nat-instance-key-pair",
            public_key=self.fk_nat_private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def setup_fk_nat_security_groups(self) -> None:
        """Create the security group for the fck-nat instance."""
        self.fk_nat_security_group = aws.ec2.SecurityGroup(
            f"{self.name}-fk-nat-security-group",
            vpc_id=self.vpc.id,
            description="fck-nat instance security group",
            opts=self.child_opts,
        )

    def setup_fk_nat_security_group_private_ingress(self) -> None:
        """Allow private VPC ingress to the fck-nat instance."""
        aws.ec2.SecurityGroupRule(
            f"{self.name}-fk-nat-sg-ingress-vpc",
            type="ingress",
            security_group_id=self.fk_nat_security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=[self.vpc.cidr_block],
            description="Allow all traffic from within VPC",
            opts=self.child_opts,
        )

    def setup_fk_nat_security_group_egress(self) -> None:
        """Allow outbound and administrator SSH access for fck-nat."""
        aws.ec2.SecurityGroupRule(
            f"{self.name}-fk-nat-security-group-egress",
            type="egress",
            security_group_id=self.fk_nat_security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound",
            opts=self.child_opts,
        )

        # Allow SSH from admin IPs
        for idx, ip in enumerate(ADMINISTRATOR_IPS):
            aws.ec2.SecurityGroupRule(
                f"{self.name}-fk-nat-security-group-ingress-ssh-{idx}",
                type="ingress",
                security_group_id=self.fk_nat_security_group.id,
                from_port=22,
                to_port=22,
                protocol="tcp",
                cidr_blocks=[f"{ip}/32"],
                description=f"Allow SSH from admin IP {ip}",
                opts=self.child_opts,
            )

    def setup_subnets(self) -> None:
        """Create the public and private subnets."""
        self.public_subnet = aws.ec2.Subnet(
            f"{self.name}-public-subnet",
            vpc_id=self.vpc.id,
            cidr_block="10.0.0.0/24",
            availability_zone=self.availability_zone,
            map_public_ip_on_launch=True,
            opts=self.child_opts,
        )

        # -- private subnet --------------------------------------------------------------
        self.private_subnet = aws.ec2.Subnet(
            f"{self.name}-private-subnet",
            vpc_id=self.vpc.id,
            cidr_block="10.0.16.0/20",
            availability_zone=self.availability_zone,
            map_public_ip_on_launch=False,
            opts=self.child_opts,
        )

    def setup_fk_nat_instance(self) -> None:
        """Create the fck-nat EC2 instance and attach its Elastic IP."""
        fck_nat_ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["568608671756"],
            filters=[aws.ec2.GetAmiFilterArgs(name="name", values=["fck-nat-*-arm*"])],
        )

        self.fk_nat_instance = aws.ec2.Instance(
            f"{self.name}-fk-nat-instance",
            instance_type="t4g.nano",
            ami=fck_nat_ami.id,
            subnet_id=self.public_subnet.id,
            vpc_security_group_ids=[self.fk_nat_security_group.id],
            key_name=self.fk_nat_key_pair.key_name,
            source_dest_check=False,
            user_data=dedent("""#!/bin/bash
                echo "eni_id=${FckNatInterface}" >> /etc/fck-nat.conf
                service fck-nat restart
            """),
            opts=self.child_opts,
        )

        aws.ec2.EipAssociation(
            f"{self.name}-fk-nat-eip-assoc",
            instance_id=self.fk_nat_instance.id,
            allocation_id=self.fk_nat_eip.allocation_id,
            opts=self.child_opts,
        )

    def setup_route_tables(self) -> None:
        """Create public and private route tables."""
        self.private_route_table = aws.ec2.RouteTable(
            f"{self.name}-private-route-table",
            vpc_id=self.vpc.id,
            opts=self.child_opts,
        )

        self.public_route_table = aws.ec2.RouteTable(
            f"{self.name}-public-route-table",
            vpc_id=self.vpc.id,
            opts=self.child_opts,
        )

    def setup_routes(self) -> None:
        """Create public and private route table associations."""
        # -- public routes ---------------------------------------------------------------

        aws.ec2.Route(
            f"{self.name}-public-route-default",
            route_table_id=self.public_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=self.internet_gateway.id,
            opts=self.child_opts,
        )

        aws.ec2.RouteTableAssociation(
            f"{self.name}-public-route-table-association",
            subnet_id=self.public_subnet.id,
            route_table_id=self.public_route_table.id,
            opts=self.child_opts,
        )

        # -- private routes --------------------------------------------------------------

        aws.ec2.Route(
            f"{self.name}-private-route-table-default",
            route_table_id=self.private_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            network_interface_id=self.fk_nat_instance.primary_network_interface_id,
            opts=self.child_opts,
        )

        aws.ec2.RouteTableAssociation(
            f"{self.name}-private-route-table-association",
            subnet_id=self.private_subnet.id,
            route_table_id=self.private_route_table.id,
            opts=self.child_opts,
        )
