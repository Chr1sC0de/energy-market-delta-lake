"""DynamoDB table component for Delta Lake lock coordination."""

import pulumi
import pulumi_aws as aws

TABLE_NAME = "delta_log"
TTL_ATTRIBUTE_NAME = "expireTime"


class DeltaLockingTableComponentResource(pulumi.ComponentResource):
    """DynamoDB table used by delta-rs for distributed locking.

    Mirrors CDK: infrastructure/locking_table.py
    Table name: delta_log
    Partition key: tablePath (String)
    Sort key:      fileName  (String)
    Billing:       PAY_PER_REQUEST
    TTL attribute: expireTime

    Existing retained tables can be adopted by setting
    `aws-pulumi:adopt_existing_delta_log_table=true` before running Pulumi.
    """

    table: aws.dynamodb.Table

    def __init__(
        self,
        name: str,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """Create the Delta locking table component."""
        super().__init__(f"{name}:components:DeltaLockingTable", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        config = pulumi.Config()
        adopt_existing_table = (
            config.get_bool("adopt_existing_delta_log_table") or False
        )
        table_exists = False
        if adopt_existing_table:
            try:
                aws.dynamodb.get_table(name=TABLE_NAME)
                table_exists = True
            except Exception:
                table_exists = False

        table_opts = (
            pulumi.ResourceOptions(
                parent=self,
                retain_on_delete=True,
                import_=TABLE_NAME,
            )
            if table_exists
            else pulumi.ResourceOptions(
                parent=self,
                retain_on_delete=False,
            )
        )

        self.table = aws.dynamodb.Table(
            f"{name}-delta-locking-table",
            name=TABLE_NAME,
            billing_mode="PAY_PER_REQUEST",
            hash_key="tablePath",
            range_key="fileName",
            attributes=[
                aws.dynamodb.TableAttributeArgs(name="tablePath", type="S"),
                aws.dynamodb.TableAttributeArgs(name="fileName", type="S"),
            ],
            ttl=aws.dynamodb.TableTtlArgs(
                attribute_name=TTL_ATTRIBUTE_NAME,
                enabled=True,
            ),
            opts=table_opts,
        )

        self.register_outputs({"table_name": self.table.name})
