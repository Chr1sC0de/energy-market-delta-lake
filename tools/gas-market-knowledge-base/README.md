# Gas Market Knowledge Base

This Subproject is the repo-local **Gas market knowledge base** tool surface.
It currently provides the Python package layout, bronze source manifest command,
archive PDF cache fetcher, Docling-based silver document extraction,
Docling Hybrid silver chunk generation, retrieval index validation,
generated-artifact policy, and **Unit test** lane. It does not add gold
**Market context** pages.

The CLI is available inside this Subproject with `uv run`:

```bash
uv run gas-market-kb --help
```

Build the tracked bronze source manifest from the AEMO gas document metadata
table contract:

```bash
uv run gas-market-kb sync-manifest --environment dev
```

The default `dev` environment reads
`s3://dev-energy-market-aemo/bronze/aemo_gas_documents/bronze_aemo_gas_document_sources`
and writes `generated/bronze/source_manifest.jsonl`. Unit tests use fixture
JSON or JSONL metadata rows through `--metadata-path` and do not read deployed
resources.

Populate the ignored local PDF cache from manifest archive objects:

```bash
uv run gas-market-kb fetch-pdfs
```

The command reads `generated/bronze/source_manifest.jsonl`, fetches each
`archive_uri`, validates downloaded bytes against `content_sha256`, and writes
deterministic cache files to `.cache/pdfs/<content_sha256>.pdf`. Valid existing
cache files are reused. Invalid cache files are replaced only after a fresh
download validates against the manifest hash. Row-level failures such as missing
archive URIs, fetch failures, or hash mismatches are reported and cause a
non-zero exit.

Extract silver document Markdown from the bronze manifest and cached PDFs:

```bash
uv run gas-market-kb extract-silver
```

The command reads `generated/bronze/source_manifest.jsonl`, validates cached
PDF bytes in `.cache/pdfs/<content_sha256>.pdf`, converts each changed PDF to
Markdown with Docling and OCR disabled, and writes deterministic document files
under `generated/silver/documents/<document_identity>.md`. Each generated file
starts with stable JSON frontmatter containing the manifest line, source
document fields, `content_sha256`, and extraction settings hash. Existing
outputs are skipped when the source hash and extraction settings hash still
match. Failed conversions, missing or mismatched cached PDFs, and low-text
extractions are reported as errors instead of writing empty Markdown pages.

Build silver Docling Hybrid chunks and the global retrieval index:

```bash
uv run gas-market-kb build-index
```

The command reads the bronze manifest, validates current silver document
Markdown targets and cached PDF bytes, converts each PDF through Docling's
structured document model, runs Docling Hybrid chunking, and writes per-chunk
Markdown files under `generated/silver/chunks/<document_identity>/<chunk_id>.md`.
Chunk IDs are derived from the source hash, extraction settings, and chunk
content; duplicate chunks are disambiguated deterministically. Each chunk
frontmatter records source hash, document title, corpus, document family,
heading path,
`source_document_markdown_path`, and citations metadata back to the full
document and source manifest. The command also writes one JSONL row per chunk
to `generated/silver/index/chunks.jsonl`.

Validate silver document targets, chunks, and the retrieval index:

```bash
uv run gas-market-kb validate
```

Validation fails on missing silver document targets, missing chunk targets,
duplicate chunk IDs, malformed frontmatter, missing citations metadata, body
hash mismatches, chunk files not referenced by the index, or stale index rows.
The command does not create embeddings or vector storage.

## Local QA

Run from this directory:

```bash
make unit-test
make docling-adapter-test
make fast-test
make run-prek
```

`make unit-test` is the gas-market-knowledge-base **Unit test** lane.
It uses fixtures and mocks, and does not run the real Docling adapter or depend
on live HuggingFace/Docling model downloads. `make docling-adapter-test` is the
Docling adapter **Test lane**. It runs `DoclingMarkdownExtractor` against a
small generated PDF and may require local or downloadable Docling model
artifacts. `make fast-test` currently aliases the **Unit test** lane until the
Subproject has a wider **Fast check** surface. `make run-prek` is the
Subproject **Commit check**.

## Generated Artifacts

Corpus text artifacts belong under these generated roots:

- `generated/bronze`: source manifest inventory used to plan extraction.
- `generated/silver/documents`: Docling Markdown extraction output tied to
  source document identity and `content_sha256`.
- `generated/silver/chunks`: Docling Hybrid chunks prepared for retrieval.
- `generated/silver/index/chunks.jsonl`: one index row per silver chunk.
- `generated/gold`: cited, agent-authored **Market context** pages.

Generated Markdown, JSON, JSONL, YAML, and text files under those roots may be
tracked intentionally when future issues create reviewable corpus artifacts.
Raw PDFs are not tracked. Source PDF bytes stay in S3-compatible archive
storage or in the ignored local `.cache/pdfs/` cache, and repository ignore
rules keep `*.pdf` files out of this Subproject.

The repository **Documentation sync** workflow excludes any `generated/` path
from maintained-doc discovery, so generated corpus Markdown is reviewable
artifact output rather than maintained router documentation.

## Layout

- `src/gas_market_knowledge_base/cli.py`: CLI entrypoint.
- `src/gas_market_knowledge_base/docling_adapter.py`: Docling PDF-to-Markdown
  and Hybrid chunking adapters with OCR disabled for v1 extraction.
- `src/gas_market_knowledge_base/pdf_cache.py`: archive PDF cache fetcher.
- `src/gas_market_knowledge_base/silver_chunks.py`: silver chunk Markdown,
  retrieval index, and validation behavior.
- `src/gas_market_knowledge_base/silver_documents.py`: silver document
  extraction planning, validation, frontmatter, and write behavior.
- `src/gas_market_knowledge_base/source_manifest.py`: bronze source manifest
  writer for AEMO gas document metadata rows.
- `tests/unit/`: package import, command-surface, and manifest writer tests.
- `tests/docling/`: real Docling adapter smoke tests that are intentionally
  outside the **Unit test** lane.
- `generated/bronze`, `generated/silver`, `generated/gold`: reserved text
  artifact roots.
- `.pre-commit-config.yaml`: Subproject `prek` hook surface.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `.gitignore`
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/repository/documentation-sync.md`
  - `tools/gas-market-knowledge-base/.pre-commit-config.yaml`
  - `tools/gas-market-knowledge-base/Makefile`
  - `tools/gas-market-knowledge-base/pyproject.toml`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/cli.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/docling_adapter.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/pdf_cache.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/source_manifest.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_cli.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_pdf_cache.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_silver_chunks.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_silver_documents.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_source_manifest.py`
  - `tools/gas-market-knowledge-base/tests/docling/test_silver_documents_docling.py`
  - `tools/gas-market-knowledge-base/uv.lock`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `make unit-test`
  - `make docling-adapter-test`
  - `make run-prek`
  - `verify generated-artifact roots, raw-PDF ignore policy, CLI help, source manifest fixture behavior, PDF cache fixture behavior, silver document extraction fixture behavior, real Docling adapter smoke lane, chunk index validation, and no embedding or vector storage behavior`
