"""Command line interface for the Gas market knowledge base."""

from pathlib import Path

import click

from gas_market_knowledge_base.pdf_cache import (
    PdfCacheInputError,
    default_pdf_cache_dir,
    fetch_pdf_cache,
)
from gas_market_knowledge_base.source_manifest import (
    DEFAULT_ENVIRONMENT,
    ManifestInputError,
    ManifestValidationError,
    default_metadata_table_uri,
    default_source_manifest_path,
    load_metadata_rows_from_delta,
    load_metadata_rows_from_json,
    sync_source_manifest,
)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
def main() -> None:
    """Work with Gas market knowledge base artifacts."""


@main.command("sync-manifest")
@click.option(
    "--environment",
    default=DEFAULT_ENVIRONMENT,
    show_default=True,
    help="AEMO deployment environment used for default bucket names.",
)
@click.option(
    "--metadata-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help=(
        "Fixture JSON or JSONL metadata rows. When omitted, read the "
        "environment Delta table."
    ),
)
@click.option(
    "--table-uri",
    help="Override the source metadata Delta table URI.",
)
@click.option(
    "--output-path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=default_source_manifest_path(),
    show_default=True,
    help="JSONL source manifest path to write.",
)
def sync_manifest(
    environment: str,
    metadata_path: Path | None,
    table_uri: str | None,
    output_path: Path,
) -> None:
    """Build the tracked bronze PDF source manifest."""
    try:
        effective_table_uri = table_uri or default_metadata_table_uri(environment)
        if metadata_path is None:
            metadata_rows = load_metadata_rows_from_delta(effective_table_uri)
        else:
            metadata_rows = load_metadata_rows_from_json(metadata_path)
        result = sync_source_manifest(
            metadata_rows,
            output_path=output_path,
            environment=environment,
        )
    except (ManifestInputError, ManifestValidationError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = result.summary
    click.echo(
        f"wrote {summary.manifest_row_count} manifest rows to {result.output_path}"
    )
    click.echo(
        "summary: "
        f"metadata_rows={summary.metadata_row_count} "
        f"excluded_by_decision={summary.excluded_by_decision_count} "
        "excluded_without_content_sha256="
        f"{summary.excluded_without_content_sha256_count} "
        "excluded_without_archive_storage="
        f"{summary.excluded_without_archive_storage_count}"
    )


@main.command("fetch-pdfs")
@click.option(
    "--manifest-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=default_source_manifest_path(),
    show_default=True,
    help="Bronze source manifest JSONL path to read.",
)
@click.option(
    "--cache-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_pdf_cache_dir(),
    show_default=True,
    help="Ignored local PDF cache directory to populate.",
)
def fetch_pdfs(manifest_path: Path, cache_dir: Path) -> None:
    """Populate the ignored local PDF cache from archive objects."""
    try:
        result = fetch_pdf_cache(manifest_path=manifest_path, cache_dir=cache_dir)
    except PdfCacheInputError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = (
        f"summary: manifest_rows={result.manifest_row_count} "
        f"fetchable_rows={result.fetchable_row_count} "
        f"downloaded={result.downloaded_count} "
        f"refreshed={result.refreshed_count} "
        f"reused={result.reused_count} "
        f"invalid_cache_entries={result.invalid_cache_entry_count} "
        f"errors={result.error_count}"
    )
    if result.errors:
        click.echo(f"Error: fetch-pdfs found {result.error_count} problem(s)", err=True)
        for error in result.errors:
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"cached PDFs in {result.cache_dir}")
    click.echo(summary)
