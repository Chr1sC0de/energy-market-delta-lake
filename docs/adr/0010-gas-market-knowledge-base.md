# Gas Market Knowledge Base Uses a Separate Tools Subproject

The Operator has chosen the first architecture for the **Gas market knowledge
base** before implementation starts. The current AEMO gas document ingestion
path already discovers configured AEMO source pages, downloads included direct
media bytes, writes `bronze_aemo_gas_document_sources` metadata, and archives
the bytes in S3-compatible storage. That path stops at media bytes and
metadata. It does not extract text, build retrieval chunks, create wiki pages,
write embeddings, or update a vector store.
Observation-only configured source pages can still add `needs_human_review`
metadata coverage without landing publication bytes. A later approved AEMO ETL
source-family asset, `bronze_aemo_major_publications_hub_downloads`, uses the
same source-page discovery, direct-media landing/archive, and bronze metadata
boundary for the AEMO energy-systems major publications hub, the library major
publications page, and GSOO and WA GSOO publication bundles without adding text
extraction or corpus-generation side effects to AEMO ETL.
When live source-page scraping is used outside the packaged manifest path,
failed HTTP page loads remain auditable metadata-only source-page observations.

The knowledge-base work needs a repo-owned corpus toolchain with inspectable
external artifacts that agents can cite in future gas-market issues. It also
needs to keep generated corpus outputs and raw PDFs out of git and keep AEMO
ETL focused on ingestion.

## Decision

Implementation work starts in a separate
`tools/gas-market-knowledge-base` **Subproject**. The first scaffold provides
the package layout, local command surface, generated-artifact policy, and
**Unit test** lane before any PDF pipeline runtime code or generated corpus
artifacts are added.

AEMO ETL remains responsible for source-page discovery, direct-media download,
bronze metadata, and archive storage. Raw PDF bytes used by the knowledge-base
tool stay in S3 or in a local cache. The repository must not commit raw PDFs.

The knowledge-base Subproject writes generated text artifacts to an external
corpus artifact root by default. `ENERGY_MARKET_CORPUS_ROOT` selects that root;
when it is unset or empty, the root is
`~/energy-market-delta-lake-artifacts/corpora`. The Gas market corpus lives
under `$ENERGY_MARKET_CORPUS_ROOT/gas-market/{bronze,silver,gold}`:

- `gas-market/bronze`: source manifest inventory used to plan extraction.
- `gas-market/silver/documents`: Docling Markdown extraction output tied to the
  source document identity and source hash.
- `gas-market/silver/chunks`: Docling Hybrid chunks prepared for retrieval.
- `gas-market/gold`: cited, agent-authored **Market context** pages.

The current tree does not track generated corpus artifacts under
`tools/gas-market-knowledge-base/generated/`. That legacy path is ignored, and
the Gas market knowledge base **Commit check** rejects staged generated
bronze, silver, or gold corpus artifacts from that tree. Explicit CLI path
overrides may still target repo paths for local inspection, but those generated
files must stay out of git. Earlier tracked generated corpus artifacts remain
only as history until a separate guarded purge issue rewrites history.

Docling is the accepted PDF-to-Markdown extraction tool. Docling Hybrid chunks
are the accepted silver retrieval unit. Gold **Market context** pages are
authored from retrieved and inspected source text, with citations back to the
extracted artifacts. Agents may draft those pages, but the architecture treats
them as cited review artifacts rather than fully automated truth.

Reusable corpus mechanics belong in a shared core inside the Subproject rather
than in Gas-market-only modules. The shared core owns artifact-root layout,
source manifest row shape, document identity and output path planning, silver
document and chunk rendering, retrieval index validation, and gold Markdown
citation validation. Gas-specific filtering, AEMO gas metadata table defaults,
bucket naming, and CLI terminology remain outside that core.

The same Subproject also hosts the AEMO major publications corpus fixture
surface. Its `aemo-publications-corpus build-fixture` command writes deterministic
fixture bronze, silver, silver index, and gold outputs under
`$ENERGY_MARKET_CORPUS_ROOT/aemo-major-publications/{bronze,silver,gold}` by
default while reusing the shared core. This first AEMO-wide corpus slice does
not consume live `bronze_aemo_major_publications_hub_downloads` metadata.

## Considered Options

- Keep all work inside AEMO ETL: rejected because PDF extraction, corpus review,
  and agent-authored pages add dependencies and write paths that do not belong
  in the daily ingestion asset boundary.
- Commit raw PDFs: rejected because the archive already stores source bytes,
  PDF diffs are not useful for review, and raw document storage would add bulk
  without improving citation quality.
- Store all text evidence outside git with no stable artifact path: rejected
  because agents and operators still need inspectable bronze, silver, and gold
  outputs. The accepted policy keeps those outputs under the external corpus
  artifact root instead of making them reviewable tracked repo output.
- Start with embeddings: rejected because embeddings are not inspectable source
  evidence. The project needs extracted text, stable chunks, and citation
  discipline before any vector-store slice.
- Make gold synthesis fully automated: rejected because **Market context**
  pages need explicit citations and review. Automation may help draft them, but
  uncited generated prose is not accepted gold context.

## Consequences

The Subproject owns its local cache rules, external generated corpus layout,
command surface, dependency files, and maintained README. Future implementation
issues should add the PDF extraction, chunking, citation, and review workflows
without moving those side effects into AEMO ETL.

Future corpus tools should reuse the shared core with their own layout and
source metadata policy instead of copying the Gas market corpus wrappers.

AEMO ETL must not grow Docling dependencies or extraction side effects under
this decision. The AEMO document bronze metadata assets, including
`bronze_aemo_gas_document_sources` and
`bronze_aemo_major_publications_hub_downloads`, remain the boundary for document
discovery, raw media landing/archive, and source metadata.

The external corpus root and ignored repo `generated/` tree are intentionally
separate from maintained repository docs. Future **Market context** pages are
external generated corpus output unless a later ADR changes the tracking
policy. Router docs and Subproject docs still need normal **Documentation
sync** metadata outside generated corpus output.
Runtime dashboards may carry registry-only Market context IDs, source chunk
IDs, source hashes, and optional external artifact references as citation
metadata. These identifiers are metadata only: dashboards must not require
generated gold or silver Markdown artifacts to exist on disk at runtime.
Generated gold Markdown remains read-only corpus output rather than a dashboard
runtime dependency.

Embeddings or vector storage can be added later only after the extracted text
and Docling Hybrid chunks exist. A future irreversible storage choice should get
its own ADR.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `CONTEXT.md`
  - `README.md`
  - `docs/README.md`
  - `docs/agents/README.md`
  - `docs/agents/domain.md`
  - `docs/repository/architecture.md`
  - `docs/repository/workflow.md`
  - `tools/gas-market-knowledge-base/.pre-commit-config.yaml`
  - `tools/gas-market-knowledge-base/Makefile`
  - `tools/gas-market-knowledge-base/README.md`
  - `tools/gas-market-knowledge-base/pyproject.toml`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/cli.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/corpus_paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/fixture_corpus.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/__init__.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/gold_context.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/manifest.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_chunks.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_core/silver_documents.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_paths.py`
  - `tools/gas-market-knowledge-base/tests/unit/test_aemo_publications.py`
  - `docs/repository/documentation-sync.md`
  - `backend-services/dagster-user/aemo-etl/docs/architecture/ingestion_flows.md`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/defs/raw/aemo_gas_documents.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/assets.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/definitions.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/manifest.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/models.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/factories/aemo_gas_documents/scraper.py`
  - `backend-services/dagster-user/aemo-etl/src/aemo_etl/cli/refresh_aemo_gas_document_manifest.py`
- `sync.scope`: `architecture`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `cd tools/gas-market-knowledge-base && make aemo-publications-unit-test`
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify ADR links, Subproject language, AEMO gas document boundaries, and AEMO major publications fixture boundaries`
