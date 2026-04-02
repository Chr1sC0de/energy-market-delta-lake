"""Caddy reverse-proxy server running on a public EC2 instance.

Mirrors CDK: infrastructure/caddy_server.py
- t3.nano, Amazon Linux 2023
- Public subnet + Elastic IP
- 1 GiB EBS volume mounted at /mnt/caddy-certs for SSL certificate persistence
- Route 53 A-record pointing to EIP
- Docker: pulls dagster/caddy image, proxies to Dagster webservers and FastAPI auth
"""

import json
from textwrap import dedent

import pulumi
import pulumi_aws as aws
import pulumi_tls as tls

from components.ecr import ECRComponentResource
from components.fastapi_auth import FastAPIAuthComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource


class CaddyServerComponentResource(pulumi.ComponentResource):
    instance: aws.ec2.Instance
    eip: aws.ec2.Eip

    def __init__(
        self,
        name: str,
        vpc: VpcComponentResource,
        ecr: ECRComponentResource,
        fastapi_auth: FastAPIAuthComponentResource,
        security_groups: SecurityGroupsComponentResource,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:CaddyServer", name, {}, opts)
        self.name = name
        self.vpc = vpc
        self.ecr = ecr
        self.fastapi_auth = fastapi_auth
        self.security_groups = security_groups
        self.child_opts = pulumi.ResourceOptions(parent=self)

        # Read config
        config = pulumi.Config()
        self._developer_email = config.require("developer_email")

        self._setup_iam_role()
        self._setup_key_pair()
        self._setup_ami()
        self._setup_eip()
        self._setup_ebs_volume()
        self._setup_instance()
        self._attach_ebs_volume()
        self._setup_route53()
        self._setup_ssm_parameters()

        self.register_outputs(
            {
                "instance_id": self.instance.id,
                "eip": self.eip.public_ip,
            }
        )

    def _setup_iam_role(self) -> None:
        assume_role = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "ec2.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )
        role = aws.iam.Role(
            f"{self.name}-caddy-role",
            assume_role_policy=assume_role,
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
            ],
            opts=self.child_opts,
        )
        self._instance_profile = aws.iam.InstanceProfile(
            f"{self.name}-caddy-profile",
            role=role.name,
            opts=pulumi.ResourceOptions(parent=role),
        )

    def _setup_key_pair(self) -> None:
        self._private_key = tls.PrivateKey(
            f"{self.name}-caddy-private-key",
            algorithm="ED25519",
            opts=self.child_opts,
        )
        self._key_pair = aws.ec2.KeyPair(
            f"{self.name}-caddy-key-pair",
            key_name=f"{self.name}-caddy-instance-key-pair",
            public_key=self._private_key.public_key_openssh,
            opts=self.child_opts,
        )

    def _setup_ami(self) -> None:
        self._ami = aws.ec2.get_ami(
            most_recent=True,
            owners=["amazon"],
            filters=[
                aws.ec2.GetAmiFilterArgs(name="name", values=["al2023-ami-*-x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="architecture", values=["x86_64"]),
                aws.ec2.GetAmiFilterArgs(name="virtualization-type", values=["hvm"]),
            ],
        )

    def _setup_eip(self) -> None:
        self.eip = aws.ec2.Eip(
            f"{self.name}-caddy-eip",
            domain="vpc",
            opts=self.child_opts,
        )

    def _setup_ebs_volume(self) -> None:
        self._ebs_volume = aws.ebs.Volume(
            f"{self.name}-caddy-certs-volume",
            availability_zone=self.vpc.availability_zone,
            size=1,  # 1 GiB – plenty for Caddy certificate storage
            type="gp3",
            encrypted=True,
            tags={"Name": "caddy-certificates-persistent-volume"},
            opts=self.child_opts,
        )

    def _setup_instance(self) -> None:
        region = aws.get_region()

        user_data = pulumi.Output.all(
            repo_uri=self.ecr.caddy.repository_url,
            region=region.name,
            auth_ip=self.fastapi_auth.instance.private_ip,
            developer_email=self._developer_email,
        ).apply(
            lambda a: dedent(f"""\
                #!/bin/bash
                set -euo pipefail
                export HOME=/home/ec2-user
                dnf update -y
                dnf install -y docker
                systemctl enable docker
                systemctl start docker
                usermod -a -G docker ec2-user

                # Wait for EBS volume to be attached.
                # On Nitro instances the xvdf/sdf attachment maps to nvme1n1.
                # We resolve the actual block device from the NVMe serial number
                # (AWS embeds the attachment name in the serial, e.g. "vol..." or
                # falls back to scanning for the first non-root nvme device).
                MOUNT_POINT=/mnt/caddy-certs

                # Find the EBS volume device: look for the nvme device that is
                # NOT the root volume (nvme0n1) and is not a partition.
                DEVICE=""
                for attempt in $(seq 1 30); do
                    for dev in /dev/nvme[1-9]n1; do
                        if [ -b "$dev" ]; then
                            DEVICE="$dev"
                            break 2
                        fi
                    done
                    echo "Waiting for EBS device... attempt $attempt"
                    sleep 5
                done

                if [ -z "$DEVICE" ]; then
                    echo "ERROR: EBS volume not found after 150 seconds" >&2
                    exit 1
                fi

                echo "Found EBS device: $DEVICE"

                # Format if no filesystem present (blkid returns empty for unformatted)
                if ! blkid "$DEVICE" &>/dev/null; then
                    echo "Formatting $DEVICE as ext4..."
                    mkfs -t ext4 "$DEVICE"
                fi

                mkdir -p "$MOUNT_POINT"
                # Use UUID-based fstab entry to survive device renames
                UUID=$(blkid -s UUID -o value "$DEVICE")
                if ! grep -q "$UUID" /etc/fstab; then
                    echo "UUID=$UUID $MOUNT_POINT ext4 defaults,nofail 0 2" >> /etc/fstab
                fi
                mount -a
                mkdir -p "$MOUNT_POINT/data"
                chown 1000:1000 "$MOUNT_POINT/data"

                # ECR login and pull
                aws ecr get-login-password --region {a["region"]} | \\
                    docker login --username AWS --password-stdin {a["repo_uri"].split("/")[0]}
                docker pull {a["repo_uri"]}:latest

                docker run -d \\
                    --restart unless-stopped \\
                    -v /mnt/caddy-certs/data:/data \\
                    -p 80:80 \\
                    -p 443:443 \\
                    -p 443:443/udp \\
                    -e ROOT_DNS=ausenergymarketdata.com \\
                    -e DAGSTER_AUTHSERVER={a["auth_ip"]}:8000 \\
                    -e DEVELOPER_EMAIL={a["developer_email"]} \\
                    -e DAGSTER_WEBSERVER_ADMIN=webserver-admin.dagster:3000 \\
                    -e DAGSTER_WEBSERVER_GUEST=webserver-guest.dagster:3000 \\
                    {a["repo_uri"]}:latest
            """)  # ty:ignore[invalid-argument-type]
        )  # ty:ignore[missing-argument]

        self.instance = aws.ec2.Instance(
            f"{self.name}-caddy-instance",
            instance_type="t3.nano",
            ami=self._ami.id,
            subnet_id=self.vpc.public_subnet.id,
            vpc_security_group_ids=[self.security_groups.register.caddy_instance.id],
            iam_instance_profile=self._instance_profile.name,
            key_name=self._key_pair.key_name,
            user_data=user_data,
            user_data_replace_on_change=True,
            availability_zone=self.vpc.availability_zone,
            tags={
                "dagster/service": "caddy-server",
                "Name": f"{self.name}-caddy",
            },
            opts=self.child_opts,
        )

        aws.ec2.EipAssociation(
            f"{self.name}-caddy-eip-assoc",
            instance_id=self.instance.id,
            allocation_id=self.eip.allocation_id,
            opts=pulumi.ResourceOptions(parent=self.instance),
        )

    def _attach_ebs_volume(self) -> None:
        aws.ec2.VolumeAttachment(
            f"{self.name}-caddy-certs-attachment",
            device_name="/dev/sdf",
            instance_id=self.instance.id,
            volume_id=self._ebs_volume.id,
            # Stop the instance before detaching on destroy (safe for cert volumes)
            stop_instance_before_detaching=True,
            opts=pulumi.ResourceOptions(parent=self.instance),
        )

    def _setup_route53(self) -> None:
        hosted_zone = aws.route53.get_zone(name="ausenergymarketdata.com")

        aws.route53.Record(
            f"{self.name}-caddy-dns-record",
            zone_id=hosted_zone.zone_id,
            name="ausenergymarketdata.com",
            type="A",
            ttl=300,
            records=[self.eip.public_ip],
            opts=pulumi.ResourceOptions(parent=self.eip),
        )

    def _setup_ssm_parameters(self) -> None:
        aws.ssm.Parameter(
            f"{self.name}-caddy-instance-id-ssm",
            name=f"/{self.name}/dagster/caddy-server/instance-id",
            type="String",
            value=self.instance.id,
            opts=pulumi.ResourceOptions(parent=self.instance),
        )

        aws.ssm.Parameter(
            f"{self.name}-caddy-key-pair-id-ssm",
            name=f"/{self.name}/dagster/caddy-server/key-pair-id",
            type="String",
            value=self._key_pair.key_pair_id,
            opts=pulumi.ResourceOptions(parent=self._key_pair),
        )
