"""Command line interface for the Gas market knowledge base."""

from pathlib import Path

import click

from gas_market_knowledge_base.archive_audit import (
    ArchiveAuditInputError,
    ArchiveListingReadError,
    audit_archive_prefix,
    default_archive_prefix_uri,
)
from gas_market_knowledge_base.gold_context import validate_gold_context
from gas_market_knowledge_base.pdf_cache import (
    PdfCacheInputError,
    default_pdf_cache_dir,
    fetch_pdf_cache,
)
from gas_market_knowledge_base.silver_chunks import (
    HybridChunkExtractionError,
    HybridChunkExtractor,
    SilverChunkInputError,
    build_silver_index,
    default_silver_chunks_dir,
    default_silver_index_path,
    validate_silver_index,
)
from gas_market_knowledge_base.silver_documents import (
    DEFAULT_MIN_TEXT_CHARS,
    MarkdownExtractor,
    SilverExtractionInputError,
    default_silver_documents_dir,
    extract_silver_documents,
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


@main.command("audit-archive-prefix")
@click.option(
    "--environment",
    default=DEFAULT_ENVIRONMENT,
    show_default=True,
    help="AEMO deployment environment used for the default archive prefix.",
)
@click.option(
    "--archive-prefix",
    help="Override the source PDF archive prefix S3 URI.",
)
@click.option(
    "--listing-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help=(
        "Fixture JSON or JSONL archive listing. When omitted, list the "
        "archive prefix from S3."
    ),
)
@click.option(
    "--manifest-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=default_source_manifest_path(),
    show_default=True,
    help="Bronze source manifest JSONL path to audit.",
)
def audit_archive_prefix_command(
    environment: str,
    archive_prefix: str | None,
    listing_path: Path | None,
    manifest_path: Path,
) -> None:
    """Audit archive-prefix PDF completeness against the source manifest."""
    try:
        effective_archive_prefix = archive_prefix or default_archive_prefix_uri(
            environment
        )
        result = audit_archive_prefix(
            manifest_path=manifest_path,
            archive_prefix_uri=effective_archive_prefix,
            listing_path=listing_path,
        )
    except (ArchiveAuditInputError, ArchiveListingReadError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = result.summary_text()
    if result.problem_count:
        click.echo(
            f"Error: audit-archive-prefix found {result.problem_count} problem(s)",
            err=True,
        )
        for line in result.problem_lines():
            click.echo(f"- {line}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"audited archive prefix {result.archive_prefix_uri}")
    click.echo(summary)


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


@main.command("extract-silver")
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
    help="Local PDF cache directory populated by fetch-pdfs.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_silver_documents_dir(),
    show_default=True,
    help="Silver document Markdown directory to write.",
)
@click.option(
    "--min-text-chars",
    type=click.IntRange(min=1),
    default=DEFAULT_MIN_TEXT_CHARS,
    show_default=True,
    help="Minimum extracted non-whitespace text characters required per document.",
)
def extract_silver(
    manifest_path: Path,
    cache_dir: Path,
    output_dir: Path,
    min_text_chars: int,
) -> None:
    """Convert cached PDFs into silver document Markdown."""
    try:
        result = extract_silver_documents(
            extractor=_default_markdown_extractor(),
            manifest_path=manifest_path,
            cache_dir=cache_dir,
            output_dir=output_dir,
            min_text_chars=min_text_chars,
        )
    except SilverExtractionInputError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = (
        f"summary: manifest_rows={result.manifest_row_count} "
        f"extractable_rows={result.extractable_row_count} "
        f"extracted={result.extracted_count} "
        f"skipped={result.skipped_count} "
        f"errors={result.error_count}"
    )
    if result.errors:
        click.echo(
            f"Error: extract-silver found {result.error_count} problem(s)", err=True
        )
        for error in result.errors:
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"wrote silver documents to {result.output_dir}")
    click.echo(summary)


@main.command("build-index")
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
    help="Local PDF cache directory populated by fetch-pdfs.",
)
@click.option(
    "--document-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_silver_documents_dir(),
    show_default=True,
    help="Silver document Markdown directory produced by extract-silver.",
)
@click.option(
    "--chunk-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_silver_chunks_dir(),
    show_default=True,
    help="Silver chunk Markdown directory to write.",
)
@click.option(
    "--index-path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=default_silver_index_path(),
    show_default=True,
    help="Silver chunk index JSONL path to write.",
)
@click.option(
    "--min-text-chars",
    type=click.IntRange(min=1),
    default=DEFAULT_MIN_TEXT_CHARS,
    show_default=True,
    help="Minimum extracted text setting used by extract-silver.",
)
def build_index(
    manifest_path: Path,
    cache_dir: Path,
    document_dir: Path,
    chunk_dir: Path,
    index_path: Path,
    min_text_chars: int,
) -> None:
    """Build silver Docling Hybrid chunks and the retrieval index."""
    try:
        result = build_silver_index(
            extractor=_default_hybrid_chunk_extractor(),
            manifest_path=manifest_path,
            cache_dir=cache_dir,
            document_dir=document_dir,
            chunk_dir=chunk_dir,
            index_path=index_path,
            min_text_chars=min_text_chars,
        )
    except (SilverChunkInputError, SilverExtractionInputError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e
    except HybridChunkExtractionError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = (
        f"summary: manifest_rows={result.manifest_row_count} "
        f"source_documents={result.source_document_count} "
        f"chunks={result.chunk_count} "
        f"errors={result.error_count}"
    )
    if result.errors:
        click.echo(
            f"Error: build-index found {result.error_count} problem(s)", err=True
        )
        for error in result.errors:
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"wrote silver chunks to {result.chunk_dir}")
    click.echo(f"wrote silver chunk index to {result.index_path}")
    click.echo(summary)


@main.command("validate")
@click.option(
    "--manifest-path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default=default_source_manifest_path(),
    show_default=True,
    help="Bronze source manifest JSONL path to read.",
)
@click.option(
    "--document-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_silver_documents_dir(),
    show_default=True,
    help="Silver document Markdown directory produced by extract-silver.",
)
@click.option(
    "--chunk-dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=default_silver_chunks_dir(),
    show_default=True,
    help="Silver chunk Markdown directory to validate.",
)
@click.option(
    "--index-path",
    type=click.Path(dir_okay=False, path_type=Path),
    default=default_silver_index_path(),
    show_default=True,
    help="Silver chunk index JSONL path to validate.",
)
@click.option(
    "--gold-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Gold Market context directory to validate. Defaults to the generated/gold "
        "directory beside --index-path."
    ),
)
@click.option(
    "--min-text-chars",
    type=click.IntRange(min=1),
    default=DEFAULT_MIN_TEXT_CHARS,
    show_default=True,
    help="Minimum extracted text setting used by extract-silver.",
)
def validate(
    manifest_path: Path,
    document_dir: Path,
    chunk_dir: Path,
    index_path: Path,
    gold_dir: Path | None,
    min_text_chars: int,
) -> None:
    """Validate silver chunks, retrieval index, and gold citations."""
    try:
        silver_result = validate_silver_index(
            manifest_path=manifest_path,
            document_dir=document_dir,
            chunk_dir=chunk_dir,
            index_path=index_path,
            min_text_chars=min_text_chars,
        )
    except (SilverChunkInputError, SilverExtractionInputError) as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    gold_result = validate_gold_context(gold_dir=gold_dir, index_path=index_path)
    errors = (*silver_result.errors, *gold_result.errors)
    summary = (
        f"summary: manifest_rows={silver_result.manifest_row_count} "
        f"index_rows={silver_result.index_row_count} "
        f"chunk_files={silver_result.chunk_file_count} "
        f"gold_pages={gold_result.page_count} "
        f"gold_glossary_pages={gold_result.glossary_page_count} "
        f"errors={len(errors)}"
    )
    if errors:
        click.echo(f"Error: validate found {len(errors)} problem(s)", err=True)
        for error in errors:
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"validated silver chunk index {silver_result.index_path}")
    if gold_result.page_count:
        click.echo(f"validated gold Market context {gold_result.gold_dir}")
    click.echo(summary)


def _default_markdown_extractor() -> MarkdownExtractor:
    # Docling imports large ML packages and adds about 5s to CLI startup.
    from gas_market_knowledge_base.docling_adapter import DoclingMarkdownExtractor

    return DoclingMarkdownExtractor()


def _default_hybrid_chunk_extractor() -> HybridChunkExtractor:
    # Docling imports large ML packages and may fetch tokenizer metadata.
    from gas_market_knowledge_base.docling_adapter import DoclingHybridChunkExtractor

    return DoclingHybridChunkExtractor()
