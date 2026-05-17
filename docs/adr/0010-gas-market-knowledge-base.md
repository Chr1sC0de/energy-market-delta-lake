# Gas Market Knowledge Base Uses a Separate Tools Subproject

The Operator has chosen the first architecture for the **Gas market knowledge
base** before implementation starts. The current AEMO gas document ingestion
path already discovers configured AEMO source pages, downloads included direct
media PDF bytes, writes `bronze_aemo_gas_document_sources` metadata, and
archives the bytes in S3-compatible storage. That path stops at PDF bytes and
metadata. It does not extract text, build retrieval chunks, create wiki pages,
write embeddings, or update a vector store.

The knowledge-base work needs a repo-owned corpus that agents can review in
diffs and cite in future gas-market issues. It also needs to keep raw PDFs out
of git and keep AEMO ETL focused on ingestion.

## Decision

Implementation work starts in a separate
`tools/gas-market-knowledge-base` **Subproject**. The first scaffold provides
the package layout, local command surface, generated-artifact policy, and
**Unit test** lane before any PDF pipeline runtime code or generated corpus
artifacts are added.

AEMO ETL remains responsible for source-page discovery, direct-media download,
bronze metadata, and archive storage. Raw PDF bytes stay in S3 or in a local
cache used by the knowledge-base tool. The repository must not commit raw PDFs.

The knowledge-base Subproject tracks or reserves text artifacts under
`generated/{bronze,silver,gold}`:

- `generated/bronze`: source manifest inventory used to plan extraction.
- `generated/silver/documents`: Docling Markdown extraction output tied to the
  source document identity and source hash.
- `generated/silver/chunks`: Docling Hybrid chunks prepared for retrieval.
- `generated/gold`: cited, agent-authored **Market context** pages.

Docling is the accepted PDF-to-Markdown extraction tool. Docling Hybrid chunks
are the accepted silver retrieval unit. Gold **Market context** pages are
authored from retrieved and inspected source text, with citations back to the
extracted artifacts. Agents may draft those pages, but the architecture treats
them as cited review artifacts rather than fully automated truth.

## Considered Options

- Keep all work inside AEMO ETL: rejected because PDF extraction, corpus review,
  and agent-authored pages add dependencies and write paths that do not belong
  in the daily ingestion asset boundary.
- Commit raw PDFs: rejected because the archive already stores source bytes,
  PDF diffs are not useful for review, and raw document storage would add bulk
  without improving citation quality.
- Store everything outside git: rejected because agents and operators need
  reviewable text diffs for extracted Markdown, retrieval chunks, and cited
  **Market context** pages.
- Start with embeddings: rejected because embeddings are not inspectable source
  evidence. The project needs extracted text, stable chunks, and citation
  discipline before any vector-store slice.
- Make gold synthesis fully automated: rejected because **Market context**
  pages need explicit citations and review. Automation may help draft them, but
  uncited generated prose is not accepted gold context.

## Consequences

The Subproject owns its local cache rules, generated corpus layout, command
surface, dependency files, and maintained README. Future implementation issues
should add the PDF extraction, chunking, citation, and review workflows without
moving those side effects into AEMO ETL.

AEMO ETL must not grow Docling dependencies or extraction side effects under
this decision. `bronze_aemo_gas_document_sources` remains the boundary for
document discovery, raw PDF landing/archive, and source metadata.

The `generated/` corpus is intentionally separate from maintained repository
docs. Future **Market context** pages can be tracked artifacts under
`generated/gold`, but router docs and Subproject docs still need normal
**Documentation sync** metadata outside that generated corpus.

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
  - `python3 -m unittest discover -s tests`
  - `prek run -a`
  - `verify ADR links, Subproject language, and AEMO gas document boundaries`
