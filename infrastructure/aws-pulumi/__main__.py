"""An AWS Python Pulumi program"""

from components.bastion_host import BastionHostComponentResource
from components.ecr import ECRComponentResource
from components.iam_roles import IamRolesComponentResource
from components.s3_buckets import S3BucketsComponentResource
from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource
from configs import NAME

vpc = VpcComponentResource(NAME)

security_groups = SecurityGroupsComponentResource(NAME, vpc)

s3_buckets = S3BucketsComponentResource(NAME)

ecr = ECRComponentResource(NAME)

iam_roles = IamRolesComponentResource(NAME)

bastion_host = BastionHostComponentResource(NAME, vpc, security_groups, iam_roles)
