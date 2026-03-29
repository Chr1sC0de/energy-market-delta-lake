"""An AWS Python Pulumi program"""

from components.security_groups import SecurityGroupsComponentResource
from components.vpc import VpcComponentResource
from configs import NAME

vpc = VpcComponentResource(NAME)
security_groups = SecurityGroupsComponentResource(NAME, vpc)
