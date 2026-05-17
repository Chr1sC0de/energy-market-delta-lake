"""Command line interface for the Gas market knowledge base scaffold."""

import click


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
def main() -> None:
    """Work with Gas market knowledge base artifacts."""
