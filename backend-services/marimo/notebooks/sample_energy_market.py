import marimo

__generated_with = "0.21.1"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(
        """
        # Energy Market Delta Lake — Sample Notebook

        This notebook demonstrates reading from the Delta Lake tables produced by
        the AEMO ETL pipeline.  It uses **Polars** with the **deltalake** backend
        to query data stored in S3 (LocalStack in local dev).

        ## Configuration

        The S3 endpoint and bucket names are derived from environment variables
        that are injected by the compose file.
        """
    )
    return


@app.cell
def _():
    import os

    # S3 / Delta Lake configuration — mirrors aemo_etl.configs
    NAME_PREFIX = os.environ.get("NAME_PREFIX", "energy-market")
    DEV_ENV = os.environ.get("DEVELOPMENT_ENVIRONMENT", "dev").lower()
    AEMO_BUCKET = f"{DEV_ENV}-{NAME_PREFIX}-aemo"
    LANDING_BUCKET = f"{DEV_ENV}-{NAME_PREFIX}-landing"

    AWS_ENDPOINT_URL = os.environ.get("AWS_ENDPOINT_URL", "http://localstack:4566")
    AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "ap-southeast-4")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "test")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "test")

    storage_options = {
        "AWS_ENDPOINT_URL": AWS_ENDPOINT_URL,
        "AWS_REGION": AWS_REGION,
        "AWS_ACCESS_KEY_ID": AWS_ACCESS_KEY_ID,
        "AWS_SECRET_ACCESS_KEY": AWS_SECRET_ACCESS_KEY,
        "AWS_ALLOW_HTTP": "true",
        "AWS_S3_ALLOW_UNSAFE_RENAME": "true",
    }

    return (
        AEMO_BUCKET,
        AWS_ACCESS_KEY_ID,
        AWS_ENDPOINT_URL,
        AWS_REGION,
        AWS_SECRET_ACCESS_KEY,
        DEV_ENV,
        LANDING_BUCKET,
        NAME_PREFIX,
        storage_options,
    )


@app.cell
def _(AEMO_BUCKET, mo, storage_options):
    import polars as pl

    VICGAS_TABLE = f"s3://{AEMO_BUCKET}/bronze/vicgas/bronze_nemweb_public_files_vicgas"

    try:
        df = pl.read_delta(VICGAS_TABLE, storage_options=storage_options)
        result = mo.ui.table(df.head(100))
    except Exception as e:
        result = mo.md(
            f"""
            > **Note:** Could not read Delta table at `{VICGAS_TABLE}`.
            >
            > This is expected if the ETL pipeline has not yet run.
            > Start the Dagster daemon and trigger a materialisation first.
            >
            > Error: `{e}`
            """
        )

    result
    return VICGAS_TABLE, df, pl, result


@app.cell
def _(mo):
    mo.md(
        """
        ## Next Steps

        - Trigger the `bronze_nemweb_public_files_vicgas` asset in Dagster
        - Re-run this notebook to see the ingested data
        - Add more cells to explore and visualise the data
        """
    )
    return


if __name__ == "__main__":
    app.run()
