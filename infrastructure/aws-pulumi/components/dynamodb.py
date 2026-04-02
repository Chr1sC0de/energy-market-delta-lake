import pulumi
import pulumi_aws as aws

TABLE_NAME = "delta_log"


class DeltaLockingTableComponentResource(pulumi.ComponentResource):
    """DynamoDB table used by delta-rs for distributed locking.

    Mirrors CDK: infrastructure/locking_table.py
    Table name: delta_log
    Partition key: tablePath (String)
    Sort key:      fileName  (String)
    Billing:       PAY_PER_REQUEST

    The table is retained on stack destruction (retain_on_delete=True) to
    protect live data.  On the next pulumi up the table is automatically
    re-imported rather than recreated — matching the same create-or-adopt
    pattern used by S3BucketsComponentResource.
    """

    table: aws.dynamodb.Table

    def __init__(
        self,
        name: str,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__(f"{name}:components:DeltaLockingTable", name, {}, opts)
        self.name = name
        self.child_opts = pulumi.ResourceOptions(parent=self)

        try:
            aws.dynamodb.get_table(name=TABLE_NAME)
            # Table already exists — adopt it rather than create it.
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
                opts=pulumi.ResourceOptions(
                    parent=self,
                    retain_on_delete=True,
                    import_=TABLE_NAME,
                ),
            )
        except Exception:
            # Table does not exist — create it fresh.
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
                opts=pulumi.ResourceOptions(
                    parent=self,
                    retain_on_delete=True,
                ),
            )

        self.register_outputs({"table_name": self.table.name})
