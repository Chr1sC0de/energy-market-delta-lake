from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls

from configs import ADMINISTRATOR_IPS


class Vpc(pulumi.ComponentResource):
    def __init__(self, name: str, opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__("energy-market:components:Vpc", name, {}, opts)
        child_opts = pulumi.ResourceOptions(parent=self)

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                       create vpc                                       │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯
        vpc = aws.ec2.Vpc(
            f"{name}-vpc",
            cidr_block="10.0.0.0/16",
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags={"Name": f"{name}-vpc"},
            opts=child_opts,
        )

        # Use the first available AZ in the region
        azs = aws.get_availability_zones(state="available")
        self.availability_zone = azs.names[0]

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                    internet gateway                                    │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯
        internet_gateway = aws.ec2.InternetGateway(
            f"{name}-internet-gateway",
            vpc_id=vpc.id,
            opts=child_opts,
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                       resources for the nat gateway using fk nat                       │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯

        # -- fk-nat elastic ip address ---------------------------------------------------
        fk_nat_eip = aws.ec2.Eip(
            f"{name}-fk-nat-eip",
            domain="vpc",
            opts=child_opts,
        )

        # -- fk nat key pair for ssh access ----------------------------------------------
        fk_nat_private_key = tls.PrivateKey(
            f"{name}-fk-nat-private-key",
            algorithm="ED25519",
            opts=child_opts,
        )

        fk_nat_key_pair = aws.ec2.KeyPair(
            f"{name}-fk-nat-key-pair",
            key_name="fck-nat-instance-key-pair",
            public_key=fk_nat_private_key.public_key_openssh,
            tags={"Name": "fck-nat-instance-key-pair"},
            opts=child_opts,
        )

        # -- fk nat security groups ------------------------------------------------------
        self.fk_nat_security_group = aws.ec2.SecurityGroup(
            f"{name}-fk-nat-security-group",
            vpc_id=vpc.id,
            description="fck-nat instance security group",
            tags={"Name": f"{name}-fk-nat-security-group"},
            opts=child_opts,
        )
        aws.ec2.SecurityGroupRule(
            f"{name}-fk-nat-sg-ingress-vpc",
            type="ingress",
            security_group_id=self.fk_nat_security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=[vpc.cidr_block],
            description="Allow all traffic from within VPC",
            opts=child_opts,
        )

        aws.ec2.SecurityGroupRule(
            f"{name}-fk-nat-security-group-egress",
            type="egress",
            security_group_id=self.fk_nat_security_group.id,
            from_port=0,
            to_port=0,
            protocol="-1",
            cidr_blocks=["0.0.0.0/0"],
            description="Allow all outbound",
            opts=child_opts,
        )

        # Allow SSH from admin IPs
        for idx, ip in enumerate(ADMINISTRATOR_IPS):
            aws.ec2.SecurityGroupRule(
                f"{name}-fk-nat-security-group-ingress-ssh-{idx}",
                type="ingress",
                security_group_id=self.fk_nat_security_group.id,
                from_port=22,
                to_port=22,
                protocol="tcp",
                cidr_blocks=[f"{ip}/32"],
                description=f"Allow SSH from admin IP {ip}",
                opts=child_opts,
            )

        # -- define the fk nat instance and it's associations ----------------------------
        fck_nat_ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["568608671756"],
            filters=[aws.ec2.GetAmiFilterArgs(name="name", values=["fck-nat-*-arm*"])],
        )

        #     ╭────────────────────────────────────────────────────────────────────────────────────────╮
        #     │                                        subnets                                         │
        #     ╰────────────────────────────────────────────────────────────────────────────────────────╯
        # -- public subnet ---------------------------------------------------------------
        public_subnet = aws.ec2.Subnet(
            f"{name}-public-subnet",
            vpc_id=vpc.id,
            cidr_block="10.0.0.0/24",
            availability_zone=self.availability_zone,
            map_public_ip_on_launch=True,
            tags={"Name": f"{name}-public-subnet"},
            opts=child_opts,
        )

        public_route_table = aws.ec2.RouteTable(
            "public-route-table",
            vpc_id=vpc.id,
            opts=child_opts,
        )

        aws.ec2.Route(
            "public-default",
            route_table_id=public_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            gateway_id=internet_gateway.id,
            opts=child_opts,
        )

        aws.ec2.RouteTableAssociation(
            "public-route-table-association",
            subnet_id=public_subnet.id,
            route_table_id=public_route_table.id,
            opts=child_opts,
        )

        # -- private subnet --------------------------------------------------------------
        self.private_subnet = aws.ec2.Subnet(
            f"{name}-private-subnet",
            vpc_id=vpc.id,
            cidr_block="10.0.1.0/24",
            availability_zone=self.availability_zone,
            map_public_ip_on_launch=False,
            tags={"Name": f"{name}-private-subnet"},
            opts=child_opts,
        )

        fk_nat_instance = aws.ec2.Instance(
            f"{name}-fk-nat-instance",
            instance_type="t4g.nano",
            ami=fck_nat_ami.id,
            subnet_id=public_subnet.id,
            vpc_security_group_ids=[self.fk_nat_security_group.id],
            key_name=fk_nat_key_pair.key_name,
            source_dest_check=False,
            tags={"Name": f"{name}-fk-nat-instance"},
            user_data=dedent("""#!/bin/bash
                echo "eni_id=${FckNatInterface}" >> /etc/fck-nat.conf
                service fck-nat restart
            """),
            opts=child_opts,
        )

        aws.ec2.EipAssociation(
            f"{name}-fk-nat-eip-assoc",
            instance_id=fk_nat_instance.id,
            allocation_id=fk_nat_eip.allocation_id,
            opts=child_opts,
        )

        private_route_table = aws.ec2.RouteTable(
            f"{name}-private-route-table",
            vpc_id=vpc.id,
            tags={"Name": f"{name}-private-route-table"},
            opts=child_opts,
        )

        aws.ec2.Route(
            f"{name}-private-route-table-default",
            route_table_id=private_route_table.id,
            destination_cidr_block="0.0.0.0/0",
            network_interface_id=fk_nat_instance.primary_network_interface_id,
            opts=child_opts,
        )

        aws.ec2.RouteTableAssociation(
            f"{name}-private-route-table-association",
            subnet_id=self.private_subnet.id,
            route_table_id=private_route_table.id,
            opts=child_opts,
        )

        self.register_outputs(
            {
                "vpc_id": vpc.id,
                "public_subnet_id": public_subnet.id,
                "private_subnet_id": self.private_subnet.id,
                "availability_zone": self.availability_zone,
            }
        )
