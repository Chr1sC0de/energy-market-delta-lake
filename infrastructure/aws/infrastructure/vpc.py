from typing import Unpack

from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from infrastructure.utils import StackKwargs
from cdk_fck_nat import FckNatInstanceProvider
from configurations.parameters import ADMINISTRATOR_IPS, SHARED_PREFIX
from constructs import Construct


class Stack(_Stack):
    vpc: ec2.Vpc

    def __init__(self, scope: Construct, id: str, **kwargs: Unpack[StackKwargs]):
        super().__init__(scope, id, **kwargs)

        # create the eip for the nat instance
        nat_eip = ec2.CfnEIP(
            self,
            "NatGatewayEIP",
            domain="vpc",
            tags=[{"key": "Name", "value": "DagsterNatGatewayEIP"}],
        )

        # create the nat instance with a the ability to ssh
        fk_nat_key_pair = ec2.KeyPair(
            self,
            "FrontEndCfnKeyPair",
            key_pair_name="fk-nat-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        nat_gateway_provider = FckNatInstanceProvider(
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T4G, ec2.InstanceSize.NANO
            ),
            key_pair=fk_nat_key_pair,
            machine_image=ec2.LookupMachineImage(
                name="fck-nat-*-arm*",
                owners=["568608671756"],
            ),
            eip_pool=[nat_eip.attr_allocation_id],
        )

        # create the vpc
        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            create_internet_gateway=True,
            nat_gateway_provider=nat_gateway_provider,
            vpc_name="DagsterVpc",
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24
                ),
                # private subnet with outbound traffic capabilities with with FKNat
                ec2.SubnetConfiguration(
                    name="PrivateWithNAT",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24,
                ),
            ],
            # since we're just using this to play around, and we don't need any redundancy let's
            # just use a single AZ
            max_azs=1,
        )

        # add internet traffic for fknat
        nat_gateway_provider.security_group.add_ingress_rule(
            ec2.Peer.ipv4(self.vpc.vpc_cidr_block), ec2.Port.all_traffic()
        )

        # allow administrator ip ssh into the instance using the created keys
        for ip_address in ADMINISTRATOR_IPS:
            nat_gateway_provider.security_group.add_ingress_rule(
                ec2.Peer.ipv4(f"{ip_address}/32"),
                ec2.Port.tcp(22),
                "Allow SSH access from developer IP",
            )

        _ = ssm.StringParameter(
            self,
            "VpcArnSsm",
            string_value=self.vpc.vpc_id,
            parameter_name=f"/{SHARED_PREFIX}/dagster/vpc/id",
        )
