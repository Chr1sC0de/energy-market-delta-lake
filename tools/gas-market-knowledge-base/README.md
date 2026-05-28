# Gas Market Knowledge Base

This Subproject is the repo-local **Gas market knowledge base** tool surface.
It currently provides the Python package layout, bronze source manifest command,
archive-prefix completeness audit, archive PDF cache fetcher,
Docling-based silver document extraction,
Docling Hybrid silver chunk generation, retrieval index validation,
gold **Market context** citation validation, generated-artifact policy, a shared
corpus core for reusable bronze/silver/gold mechanics, seed gold glossary
Markdown rendering helpers, external generated corpus roots, and **Unit test**
lane.

The CLI is available inside this Subproject with `uv run`:

```bash
uv run gas-market-kb --help
```

Generated corpus defaults use `ENERGY_MARKET_CORPUS_ROOT` as the artifact
root. If the variable is unset or empty, the root defaults to
`~/energy-market-delta-lake-artifacts/corpora`. The Gas market corpus lives
under `$ENERGY_MARKET_CORPUS_ROOT/gas-market/{bronze,silver,gold}`. Explicit
CLI path options such as `--output-path`, `--manifest-path`, `--output-dir`,
`--document-dir`, `--chunk-dir`, `--index-path`, and `--gold-dir` still
override those defaults.

Build the bronze source manifest from the AEMO gas document metadata table
contract:

```bash
uv run gas-market-kb sync-manifest --environment dev
```

The default `dev` environment reads
`s3://dev-energy-market-aemo/bronze/aemo_gas_documents/bronze_aemo_gas_document_sources`
and writes
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/bronze/source_manifest.jsonl`.
Manifest `document_identity` path parts are bounded with deterministic hash
suffixes so long live metadata titles remain filesystem-safe. Unit tests use
fixture JSON or JSONL metadata rows through `--metadata-path` and do not read
deployed resources.

Audit archive-prefix PDF completeness against the bronze source manifest:

```bash
uv run gas-market-kb audit-archive-prefix --environment dev
```

The default `dev` environment lists
`s3://dev-energy-market-archive/bronze/aemo_gas_documents/` and compares PDF
objects there with
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/bronze/source_manifest.jsonl`. The audit
reports the prefix PDF object total, manifest row total, unique manifest
archive-object total, unique manifest hash total, missing archive PDFs, extra
manifest rows, duplicate archive URIs, duplicate content hashes, and manifest
row errors. It uses unique archive URIs and content hashes for object/hash
totals, so duplicate metadata rows do not require duplicate downloaded PDFs.
Missing archive PDFs, extra manifest rows, and manifest errors fail the audit;
duplicate archive URI and content hash groups are reported as non-fatal
warnings because the live metadata can contain multiple eligible rows for one
archived PDF object.

Use fixture mode for deterministic local coverage or evidence when credentials
are unavailable:

```bash
uv run gas-market-kb audit-archive-prefix \
  --archive-prefix s3://dev-energy-market-archive/bronze/aemo_gas_documents/ \
  --listing-path fixtures/archive-listing.json
```

`--listing-path` accepts JSON arrays, JSONL rows, or an object with an
`objects` array. Listing entries may be S3 URI strings, object keys, or objects
with `uri`, `archive_uri`, `storage_uri`, or `key`. Non-PDF entries are ignored.
Output is sorted and includes a stable `summary:` line for Ralph evidence
comments. Run `make unit-test` for fixture coverage and `make run-prek` before
handoff; if live credentials are available, run the command once without
`--listing-path` and record the summary counts.

Populate the ignored local PDF cache from manifest archive objects:

```bash
uv run gas-market-kb fetch-pdfs
```

The command reads
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/bronze/source_manifest.jsonl`, fetches
each `archive_uri`, validates downloaded bytes against `content_sha256`, and
writes deterministic cache files to `.cache/pdfs/<content_sha256>.pdf`. Valid
existing cache files are reused. Invalid cache files are replaced only after a
fresh download validates against the manifest hash. Row-level failures such as
missing archive URIs, fetch failures, or hash mismatches are reported and cause
a non-zero exit.

Extract silver document Markdown from the bronze manifest and cached PDFs:

```bash
uv run gas-market-kb extract-silver
```

The command reads
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/bronze/source_manifest.jsonl`, validates
cached PDF bytes in `.cache/pdfs/<content_sha256>.pdf`, converts each changed
PDF to Markdown with Docling and OCR disabled, and writes deterministic
document files under
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/documents/<document_identity>.md`.
Each generated file starts with stable JSON frontmatter containing the manifest
line, source document fields, `content_sha256`, and extraction settings hash.
Existing outputs are skipped when the source hash and extraction settings hash
still match. Duplicate manifest rows with the same document identity are
coalesced before extraction so live metadata duplicates do not create duplicate
silver documents or chunks. Failed conversions, missing or mismatched cached
PDFs, and low-text extractions are reported as errors instead of writing empty
Markdown pages.

Build silver Docling Hybrid chunks and the global retrieval index:

```bash
uv run gas-market-kb build-index
```

The command reads the bronze manifest, validates current silver document
Markdown targets and cached PDF bytes, converts each PDF through Docling's
structured document model, runs Docling Hybrid chunking, and writes per-chunk
Markdown files under
`$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/chunks/<document_identity>/<chunk_id>.md`.
Chunk IDs are derived from the source hash, extraction settings, and chunk
content; duplicate chunks are disambiguated deterministically. Each chunk
frontmatter records source hash, document title, corpus, document family,
heading path,
`source_document_markdown_path`, and citations metadata back to the full
document and source manifest. The command also writes one JSONL row per chunk
to `$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/index/chunks.jsonl`.

Validate silver document targets, chunks, the retrieval index, and gold
**Market context** citations:

```bash
uv run gas-market-kb validate
```

Validation fails on missing silver document targets, missing chunk targets,
duplicate chunk IDs, malformed frontmatter, missing citations metadata, body
hash mismatches, chunk files not referenced by the index, stale index rows,
uncited gold glossary definition claims, indented gold Markdown headings or
normal body lines, malformed gold citation lists, broken gold chunk or source
document links, missing source hashes, or stale glossary index references. The
command does not create embeddings or vector storage.

## Shared Corpus Core

Reusable corpus mechanics live under
`src/gas_market_knowledge_base/corpus_core/`. That package owns artifact-root
layout, source manifest row shape, document identity and output path planning,
silver document and chunk rendering, retrieval index validation, and gold
Markdown citation validation. Gas-specific filtering, AEMO gas metadata table
defaults, bucket naming, CLI wording, and **Market context** terminology stay in
the gas wrapper modules and command surface.

Future corpus tools, such as an AEMO major publications corpus, should pass
their own `CorpusArtifactLayout` and source metadata policy into the shared
core instead of copying the Gas market wrappers.

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

- `$ENERGY_MARKET_CORPUS_ROOT/gas-market/bronze`: source manifest inventory
  used to plan extraction.
- `$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/documents`: Docling Markdown
  extraction output tied to source document identity and `content_sha256`.
- `$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/chunks`: Docling Hybrid chunks
  prepared for retrieval.
- `$ENERGY_MARKET_CORPUS_ROOT/gas-market/silver/index/chunks.jsonl`: one index
  row per silver chunk.
- `$ENERGY_MARKET_CORPUS_ROOT/gas-market/gold`: cited, agent-authored
  **Market context** pages.

Default runs write outside the repository, and current repo policy treats
generated bronze, silver, and gold corpus files as external artifact output.
The legacy `tools/gas-market-knowledge-base/generated/` tree is ignored, and
the Subproject **Commit check** rejects staged generated corpus artifacts under
that tree. Explicit CLI paths may still target repo paths for local inspection,
but those generated files must not be committed. This current-tree cleanup does
not purge prior generated corpus files from git history; dependent maintenance
issues own any guarded history rewrite. Raw PDFs are not tracked. Source PDF
bytes stay in S3-compatible archive storage or in the ignored local
`.cache/pdfs/` cache, and repository ignore rules keep `*.pdf` files out of
this Subproject.

The repository **Documentation sync** workflow excludes any repo `generated/`
path from maintained-doc discovery, and external corpus roots are outside the
maintained router documentation scope. Generated corpus Markdown is corpus
artifact output rather than maintained router documentation.

## Layout

- `src/gas_market_knowledge_base/archive_audit.py`: archive-prefix completeness
  audit against the bronze source manifest.
- `src/gas_market_knowledge_base/cli.py`: CLI entrypoint.
- `src/gas_market_knowledge_base/corpus_core/`: reusable corpus artifact
  layout, manifest row, silver, retrieval index, and gold Markdown mechanics.
- `src/gas_market_knowledge_base/corpus_paths.py`: external generated corpus
  artifact root and default path policy.
- `src/gas_market_knowledge_base/docling_adapter.py`: Docling PDF-to-Markdown
  and Hybrid chunking adapters with OCR disabled for v1 extraction.
- `src/gas_market_knowledge_base/gold_context.py`: gold **Market context**
  Markdown rendering helpers, citation validation, and glossary-index
  validation.
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
- `generated/bronze`, `generated/silver`, `generated/gold`: ignored legacy
  local artifact paths; default runs use the external corpus root, and
  generated corpus files must not be committed from these paths.
- `.pre-commit-config.yaml`: Subproject `prek` hook surface, with file-based
  `uv run` hooks serialized so fresh Promotion worktrees do not race while
  creating the Subproject environment.

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
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/archive_audit.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/cli.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/gold_context.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/manifest.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/docling_adapter.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/gold_context.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/pdf_cache.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/source_manifest.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_archive_audit.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_cli.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_corpus_core.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_corpus_paths.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_gold_context.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_pdf_cache.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_precommit_policy.py`
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
  - `uv run gas-market-kb validate`
  - `verify external generated-artifact roots, ENERGY_MARKET_CORPUS_ROOT fallback behavior, raw-PDF ignore policy, CLI help, source manifest fixture behavior, archive-prefix audit fixture behavior, PDF cache fixture behavior, silver document extraction fixture behavior, real Docling adapter smoke lane, chunk index validation, gold citation validation, and no embedding or vector storage behavior`
