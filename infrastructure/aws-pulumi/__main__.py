"""An AWS Python Pulumi program"""

from components.vpc import Vpc

NAME = "ausenergymarket"

vpc = Vpc(NAME)
