"""Command line interface for the AEMO major publications corpus."""

from pathlib import Path

import click

from gas_market_knowledge_base.aemo_publications.corpus_paths import (
    CORPUS_ROOT_ENV_VAR,
    default_corpus_paths,
)
from gas_market_knowledge_base.aemo_publications.fixture_corpus import (
    FixtureCorpusBuildError,
    build_fixture_corpus,
)
from gas_market_knowledge_base.aemo_publications.validation import (
    validate_aemo_publications_corpus,
)
from gas_market_knowledge_base.corpus_core.silver_documents import (
    DEFAULT_MIN_TEXT_CHARS,
)

_SOURCE_MANIFEST_DEFAULT_HELP = (
    f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/bronze/source_manifest.jsonl"
)
_SOURCE_CACHE_DEFAULT_HELP = (
    f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/bronze/fixture-pdfs"
)
_SILVER_DOCUMENTS_DEFAULT_HELP = (
    f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/silver/documents"
)
_SILVER_CHUNKS_DEFAULT_HELP = (
    f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/silver/chunks"
)
_SILVER_INDEX_DEFAULT_HELP = (
    f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/silver/index/chunks.jsonl"
)
_GOLD_DEFAULT_HELP = f"${CORPUS_ROOT_ENV_VAR}/aemo-major-publications/gold"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option()
def main() -> None:
    """Work with AEMO major publications corpus artifacts."""


@main.command("build-fixture")
@click.option(
    "--artifact-root",
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Override the corpus artifact root. Defaults to ENERGY_MARKET_CORPUS_ROOT "
        "or the user-home corpus root."
    ),
)
@click.option(
    "--manifest-path",
    type=click.Path(dir_okay=False, path_type=Path),
    show_default=_SOURCE_MANIFEST_DEFAULT_HELP,
    help="Bronze source manifest JSONL path to write.",
)
@click.option(
    "--source-cache-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SOURCE_CACHE_DEFAULT_HELP,
    help="Bronze fixture source byte cache directory to write.",
)
@click.option(
    "--document-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SILVER_DOCUMENTS_DEFAULT_HELP,
    help="Silver document Markdown directory to write.",
)
@click.option(
    "--chunk-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SILVER_CHUNKS_DEFAULT_HELP,
    help="Silver chunk Markdown directory to write.",
)
@click.option(
    "--index-path",
    type=click.Path(dir_okay=False, path_type=Path),
    show_default=_SILVER_INDEX_DEFAULT_HELP,
    help="Silver chunk index JSONL path to write.",
)
@click.option(
    "--gold-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_GOLD_DEFAULT_HELP,
    help="Gold Markdown directory to write.",
)
@click.option(
    "--min-text-chars",
    type=click.IntRange(min=1),
    default=DEFAULT_MIN_TEXT_CHARS,
    show_default=True,
    help="Minimum extracted non-whitespace text characters required per document.",
)
def build_fixture(
    artifact_root: Path | None,
    manifest_path: Path | None,
    source_cache_dir: Path | None,
    document_dir: Path | None,
    chunk_dir: Path | None,
    index_path: Path | None,
    gold_dir: Path | None,
    min_text_chars: int,
) -> None:
    """Build the local fixture bronze, silver, index, and gold outputs."""
    try:
        result = build_fixture_corpus(
            artifact_root=artifact_root,
            source_manifest_path=manifest_path,
            source_cache_dir=source_cache_dir,
            silver_documents_dir=document_dir,
            silver_chunks_dir=chunk_dir,
            silver_index_path=index_path,
            gold_dir=gold_dir,
            min_text_chars=min_text_chars,
        )
    except FixtureCorpusBuildError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1) from e

    summary = (
        f"summary: manifest_rows={result.manifest_result.row_count} "
        f"silver_documents={result.silver_document_result.extracted_count} "
        f"chunks={result.silver_index_result.chunk_count} "
        f"gold_pages={result.gold_page_count} "
        f"errors={result.error_count}"
    )
    if result.error_count:
        click.echo(
            f"Error: build-fixture found {result.error_count} problem(s)", err=True
        )
        for error in (
            *result.silver_document_result.errors,
            *result.silver_index_result.errors,
            *result.silver_validation_result.errors,
            *result.gold_validation_result.errors,
        ):
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(f"wrote fixture manifest to {result.paths.source_manifest_path}")
    click.echo(f"wrote silver documents to {result.paths.silver_documents_dir}")
    click.echo(f"wrote silver chunk index to {result.paths.silver_index_path}")
    click.echo(f"wrote gold pages to {result.paths.gold_dir}")
    click.echo(summary)


@main.command("validate")
@click.option(
    "--artifact-root",
    type=click.Path(file_okay=False, path_type=Path),
    help=(
        "Override the corpus artifact root. Defaults to ENERGY_MARKET_CORPUS_ROOT "
        "or the user-home corpus root."
    ),
)
@click.option(
    "--manifest-path",
    type=click.Path(dir_okay=False, path_type=Path),
    show_default=_SOURCE_MANIFEST_DEFAULT_HELP,
    help="Bronze source manifest JSONL path to validate.",
)
@click.option(
    "--source-cache-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SOURCE_CACHE_DEFAULT_HELP,
    help="Bronze source byte cache directory to validate.",
)
@click.option(
    "--document-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SILVER_DOCUMENTS_DEFAULT_HELP,
    help="Silver document Markdown directory to validate.",
)
@click.option(
    "--chunk-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_SILVER_CHUNKS_DEFAULT_HELP,
    help="Silver chunk Markdown directory to validate.",
)
@click.option(
    "--index-path",
    type=click.Path(dir_okay=False, path_type=Path),
    show_default=_SILVER_INDEX_DEFAULT_HELP,
    help="Silver chunk index JSONL path to validate.",
)
@click.option(
    "--gold-dir",
    type=click.Path(file_okay=False, path_type=Path),
    show_default=_GOLD_DEFAULT_HELP,
    help="Gold Markdown directory to validate.",
)
@click.option(
    "--min-text-chars",
    type=click.IntRange(min=1),
    default=DEFAULT_MIN_TEXT_CHARS,
    show_default=True,
    help="Minimum extracted text setting used by silver document extraction.",
)
def validate(
    artifact_root: Path | None,
    manifest_path: Path | None,
    source_cache_dir: Path | None,
    document_dir: Path | None,
    chunk_dir: Path | None,
    index_path: Path | None,
    gold_dir: Path | None,
    min_text_chars: int,
) -> None:
    """Validate AEMO publications coverage, silver index, and gold citations."""
    paths = default_corpus_paths(
        artifact_root=artifact_root,
        source_manifest_path=manifest_path,
        source_cache_dir=source_cache_dir,
        silver_documents_dir=document_dir,
        silver_chunks_dir=chunk_dir,
        silver_index_path=index_path,
        gold_dir=gold_dir,
    )
    result = validate_aemo_publications_corpus(
        paths=paths,
        min_text_chars=min_text_chars,
    )
    silver_result = result.silver_result
    gold_result = result.gold_result
    summary = (
        "summary: "
        f"manifest_rows={result.coverage.manifest_row_count} "
        f"hub_source_families={result.coverage.hub_source_family_count} "
        f"library_source_families={result.coverage.library_source_family_count} "
        f"supported_media={result.coverage.supported_media_count} "
        f"unsupported_media={result.coverage.unsupported_media_count} "
        f"review_needed={result.coverage.review_needed_count} "
        f"silver_index_rows={silver_result.index_row_count if silver_result else 0} "
        f"silver_chunk_files={silver_result.chunk_file_count if silver_result else 0} "
        f"gold_pages={gold_result.page_count if gold_result else 0} "
        f"gold_glossary_pages={gold_result.glossary_page_count if gold_result else 0} "
        f"errors={result.error_count}"
    )
    if result.errors:
        click.echo(
            f"Error: validate found {result.error_count} problem(s)",
            err=True,
        )
        for error in result.errors:
            click.echo(f"- {error}", err=True)
        click.echo(summary, err=True)
        raise SystemExit(1)

    click.echo(
        f"validated AEMO publications source manifest {paths.source_manifest_path}"
    )
    click.echo(f"validated silver chunk index {paths.silver_index_path}")
    if gold_result is not None and gold_result.page_count:
        click.echo(f"validated gold Market context {paths.gold_dir}")
    click.echo(summary)
