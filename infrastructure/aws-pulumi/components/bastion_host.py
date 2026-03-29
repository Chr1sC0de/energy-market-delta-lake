import pulumi
import pulumi_aws as aws
import pulumi_tls as tls

from components.vpc import VpcComponentResource


class BastionHost(pulumi.ComponentResource):
    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:BastionHost", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_private_key()
        self.setup_key_pair()
        self.setup_eip()

    def setup_private_key(self) -> None:
        self.private_key = tls.PrivateKey(
            f"{self.name}-bastion-host-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )

    def setup_key_pair(self) -> None:
        key_pair_name = f"{self.name}-bastion-host-key-pair"
        self.key_pair = aws.ec2.KeyPair(
            key_pair_name,
            key_name=key_pair_name,
            public_key=self.private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def setup_eip(self) -> None:
        eip_name = f"{self.name}-bastion-host-eip"
        self.eip = aws.ec2.Eip(
            eip_name,
            domain="vpc",
            tags={"Name": eip_name},
            opts=self.child_opts,
        )

    def setup_ami(self) -> None:
        self.ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )
