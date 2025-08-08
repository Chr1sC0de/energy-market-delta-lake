import os
from typing import Unpack

from aws_cdk import Duration, RemovalPolicy, Size, Tags
from aws_cdk import Stack as _Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_ssm as ssm
from constructs import Construct

from infrastructure.configurations import SHARED_PREFIX
from infrastructure import ecr, fastapi_authentication_server, security_groups, vpc
from infrastructure.utils import StackKwargs


class Stack(_Stack):
    ecr_repository: ecr.repository.Stack
    authentication_stack: fastapi_authentication_server.Stack

    def __init__(
        self,
        scope: Construct,
        id: str,
        *,
        VpcStack: vpc.Stack,
        EcrStack: ecr.repository.Stack,
        AuthenticationStack: fastapi_authentication_server.Stack,
        SecurityGroupStack: security_groups.Stack,
        **kwargs: Unpack[StackKwargs],
    ):
        super().__init__(scope, id, **kwargs)

        self.add_dependency(VpcStack)
        self.add_dependency(SecurityGroupStack)
        self.add_dependency(AuthenticationStack)

        self.ecr_repository = EcrStack
        self.authentication_stack = AuthenticationStack

        eip = ec2.CfnEIP(
            self,
            "CaddyServerEIP",
            domain="vpc",
            tags=[{"key": "Name", "value": "DagsterCaddyServerEIP"}],
        )

        key_pair = ec2.KeyPair(
            self,
            "CaddyServerKeyPair",
            key_pair_name="dagster-caddy-instance-key-pair",
            type=ec2.KeyPairType.ED25519,
            format=ec2.KeyPairFormat.PEM,
        )

        ebs_volume = ec2.Volume(
            self,
            "CaddyCertificatesVolume",
            availability_zone=VpcStack.vpc.availability_zones[0],
            size=Size.gibibytes(1),  # 8 GB should be plenty for certificates
            volume_type=ec2.EbsDeviceVolumeType.GP3,
            encrypted=True,
            removal_policy=RemovalPolicy.SNAPSHOT,
            volume_name="caddy-certificates-persistent-volume",
        )

        instance = ec2.Instance(
            self,
            "DagsterCaddyServerEC2",
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.T3, ec2.InstanceSize.NANO
            ),
            machine_image=ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2023,
            ),
            vpc=VpcStack.vpc,
            security_group=SecurityGroupStack.register["CaddyInstanceSecurityGroup"],
            role=iam.Role(
                self,
                "DagsterCaddyServerRole",
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                managed_policies=[
                    iam.ManagedPolicy.from_aws_managed_policy_name(
                        "AmazonEC2ContainerRegistryPullOnly"
                    ),
                ],
            ),
            user_data=self.create_user_data(),
            user_data_causes_replacement=True,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            key_pair=key_pair,
            availability_zone=VpcStack.vpc.availability_zones[
                0
            ],  # Must match the volume's AZ
        )

        _ = ec2.CfnVolumeAttachment(
            self,
            "CaddyCertificatesVolumeAttachment",
            device="/dev/sdf",
            instance_id=instance.instance_id,
            volume_id=ebs_volume.volume_id,
        )

        _ = ssm.StringParameter(
            self,
            "InstancePublicDNSName",
            string_value=instance.instance_id,
            parameter_name=f"/{SHARED_PREFIX}/dagster/caddy-server/instance-id",
        )

        _ = ssm.StringParameter(
            self,
            "KeyPairId",
            string_value=key_pair.key_pair_id,
            parameter_name=f"/{SHARED_PREFIX}/dagster/caddy-server/key-pair-id",
        )

        Tags.of(instance).add("dagster/service", "caddy-server")

        # Associate the EIP with the EC2 instance
        _ = ec2.CfnEIPAssociation(
            self,
            "CaddyServerEIPAssociation",
            eip=eip.ref,
            instance_id=instance.instance_id,
        )

        hosted_zone = route53.HostedZone.from_lookup(
            self,
            "HostedZone",
            domain_name="ausenergymarketdata.com",  # Replace with your actual domain
        )

        _ = route53.ARecord(
            self,
            "CaddyServerDnsRecord",
            zone=hosted_zone,
            target=route53.RecordTarget.from_ip_addresses(eip.ref),
            ttl=Duration.minutes(5),
        )

    def create_user_data(self) -> ec2.UserData:
        user_data = ec2.UserData.for_linux()

        user_data.add_commands(
            # this needs to be set for the uv installation to work
            "export HOME=/home/ec2-user",
            "sudo yum update -y",
            "amazon-linux-extras install docker -y",
            "sudo yum install -y docker",
            "sudo usermod -a -G docker ec2-user",
            "service docker start",
            # Setup the EBS volume for SSL certificates
            "DEVICE=/dev/sdf",
            "MOUNT_POINT=/mnt/caddy-certs",
            # Wait for the device to be available
            "while [ ! -e $DEVICE ]; do echo 'Waiting for device $DEVICE to be attached...'; sleep 5; done",
            # Check if the device needs to be formatted
            'if [ "$(file -s $DEVICE)" = "$DEVICE: data" ]; then',
            "    echo 'Formatting empty device'",
            "    mkfs -t ext4 $DEVICE",
            "fi",
            # Create mount point and mount the volume
            "mkdir -p $MOUNT_POINT",
            'echo "$DEVICE $MOUNT_POINT ext4 defaults,nofail 0 2" >> /etc/fstab',
            "mount -a",
            "mkdir -p $MOUNT_POINT/data",
            "chown 1000:1000 $MOUNT_POINT/data",  # Ensure proper permissions for Caddy
            # Docker login and pull
            f"aws ecr get-login-password --region ap-southeast-2 | docker login --username AWS --password-stdin {self.account}.dkr.ecr.{self.region}.amazonaws.com",
            f"docker pull {self.ecr_repository.repository.repository_uri}:latest",
            # Run the docker image with volume mount from EBS
            "docker run -d \\",
            "    --restart unless-stopped \\",
            "    -v /mnt/caddy-certs/data:/data \\",  # Mount EBS volume instead of docker volume
            "    -p 80:80 \\",
            "    -p 443:443 \\",
            "    -p 443:443/udp \\",
            "    -e ROOT_DNS=ausenergymarketdata.com \\",
            f"    -e DAGSTER_AUTHSERVER={self.authentication_stack.instance.instance_private_ip}:8000 \\",
            f"    -e DEVELOPER_EMAIL={os.environ['DEVELOPER_EMAIL']} \\",
            "    -e DAGSTER_WEBSERVER_ADMIN=webserver-admin.dagster:3000 \\",
            "    -e DAGSTER_WEBSERVER_GUEST=webserver-guest.dagster:3000 \\",
            f"     {self.ecr_repository.repository.repository_uri}:latest",
        )

        return user_data
