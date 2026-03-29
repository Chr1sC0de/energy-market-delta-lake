import json

import pulumi
import pulumi_aws as aws


class IamRoles(pulumi.ComponentResource):
    bastion_profile: aws.iam.InstanceProfile

    def __init__(self, name: str, opts: pulumi.ResourceOptions | None = None) -> None:
        super().__init__("energy-market:components:IamRoles", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        self.setup_bastion_host()
        self.register_outputs({})

    def setup_bastion_host(
        self,
    ) -> None:
        bastion_role = aws.iam.Role(
            f"{self.name}-bastion-role",
            assume_role_policy=json.dumps(
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
            ),
            managed_policy_arns=[
                "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
                "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess",
            ],
            opts=self.child_opts,
        )

        self.bastion_profile = aws.iam.InstanceProfile(
            f"{self.name}-bastion-profile",
            role=bastion_role.name,
            opts=pulumi.ResourceOptions(parent=bastion_role),
        )

        self.register_outputs({})
