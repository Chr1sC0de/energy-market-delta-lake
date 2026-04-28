# AEMO document corpus architecture spec

## Table of contents

- [Goals and non-goals](#goals-and-non-goals)
- [Recommended architecture](#recommended-architecture)
- [Why this instead of plain vector RAG](#why-this-instead-of-plain-vector-rag)
- [Compliance and crawling constraints](#compliance-and-crawling-constraints)
- [Discovery and change-detection design](#discovery-and-change-detection-design)
- [Storage and Delta table design](#storage-and-delta-table-design)
- [Parsing and extraction design](#parsing-and-extraction-design)
- [Retrieval and indexing architecture](#retrieval-and-indexing-architecture)
- [Dagster implementation shape](#dagster-implementation-shape)
- [Minimal viable implementation (MVP)](#minimal-viable-implementation-mvp)
- [Long-term architecture roadmap](#long-term-architecture-roadmap)
- [Open questions and risks](#open-questions-and-risks)

---

## Goals and non-goals

### Goals

1. Build a durable **AEMO unstructured document corpus** that is independent from existing market-data ingestion assets.
2. Support reproducible reprocessing when parser/chunker quality improves.
3. Support operational search use-cases first (find the right source/version fast), with optional answer generation later.
4. Preserve lineage from answerable text chunk back to archived source bytes.

### Non-goals

1. Do not make a chatbot the system of record.
2. Do not rely on one-off scraping jobs without manifesting/version controls.
3. Do not couple the corpus ingestion lifecycle to existing structured NEMWeb/VICGAS/GBB batch tables.

---

## Recommended architecture

**Recommendation:** implement a layered architecture:

1. **Acquisition layer (manifest-first)**
   - Discover URLs from an allowlist + sitemap + link expansion policy.
   - Persist discovery events and canonicalized URL identities before downloading content.
2. **Document lake layer (S3 + Delta as source of truth)**
   - Store immutable raw bytes and normalized extraction outputs in Delta tables.
   - Track content hash, parser version, extraction status, and supersession.
3. **Retrieval layer (hybrid index)**
   - Build derived lexical + vector indexes from silver chunks.
   - Query using metadata filters + rank fusion + optional reranking.
4. **Consumer layer**
   - RAG assistant, analyst UI, and batch compliance checks are consumers of the retrieval/document layer.

This follows the hypothesis from the parent PR and keeps RAG optional rather than foundational.

---

## Why this instead of plain vector RAG

A pure vector-store-first architecture underperforms for regulation-heavy corpora where:

- exact phrases, clause IDs, and version notices matter;
- historical superseded procedures must still be discoverable but de-prioritized;
- users need deterministic citations to specific files/pages/sections.

A document-intelligence layer improves outcomes because it enables:

- provenance and repeatability,
- deterministic keyword retrieval (BM25/FTS),
- semantic retrieval, and
- policy-aware filtering (effective date, market, status, confidentiality tags).

**Decision:** RAG is a downstream interface, not the data architecture.

---

## Compliance and crawling constraints

### Baseline policy

Use a crawler policy document committed in-repo (for example `policies/aemo_website_crawling.md`) with explicit defaults:

- allowlisted site sections only;
- robots and terms checks at each run startup;
- conservative rate limits;
- conditional requests (`ETag`, `Last-Modified`) where available;
- immediate stoplist support for URLs/paths.

### AEMO legal/compliance observations to incorporate

1. AEMO publishes website legal notices and copyright permission guidance.
2. Public AEMO material may generally be reused with attribution, but exceptions (for third-party/confidential content) must be handled explicitly.
3. Some endpoints are protected by anti-bot controls and may not reliably serve to naive scripts; pipeline should support graceful skip/retry and manual allowlisting.

### Practical controls

- classify each source with `usage_class`: `public_reusable`, `restricted_review_required`, or `blocked`;
- prohibit indexing for `blocked` classes;
- store attribution fields for every document and include them in retrieval responses.

---

## Discovery and change-detection design

### Discovery inputs

1. Seed allowlist (`yaml`) of primary sections (e.g. market notices, rules/procedures, consultations).
2. XML sitemap polling.
3. HTML link extraction from allowlisted parents.
4. Targeted catalogue parsers for known listing pages/PDF hubs.

### URL identity and canonicalization

Canonical key components:

- normalized scheme/host/path (lowercased host, stripped tracking params);
- stable query param allowlist for content-identifying params;
- trailing slash normalization;
- optional canonical link tag if trustworthy.

Persist both `source_url` and `canonical_url`.

### Change detection

For each canonical URL:

1. `HEAD` or lightweight `GET` probe.
2. Capture `ETag` and `Last-Modified` when returned.
3. If uncertain, fetch content and compute `content_hash_sha256` on bytes.
4. Create new document revision when hash changes.

### Deduplication

- Hard dedupe: identical byte hash.
- Soft dedupe: normalized text hash + title/date similarity.

### Version/effective-date extraction

- Parse explicit version labels (`vX`, `amendment`, `effective from`, etc.).
- Maintain `supersedes_document_id` and `superseded_by_document_id` links when derivable.
- Keep unresolved relationships nullable and backfillable.

---

## Storage and Delta table design

Use S3 object storage for bytes/text artifacts and Delta tables for metadata/state.

### 1) `bronze_aemo_document_manifest`

One row per discovered or fetched URL revision.

Suggested columns:

- `manifest_id` (uuid)
- `crawl_run_id` (string)
- `discovered_at_utc` (timestamp)
- `fetched_at_utc` (timestamp, nullable)
- `source_url` (string)
- `canonical_url` (string)
- `source_section` (string)
- `http_status` (int)
- `content_type` (string)
- `etag` (string)
- `last_modified_http` (timestamp)
- `content_length_bytes` (bigint)
- `content_hash_sha256` (string)
- `raw_storage_uri` (string)
- `retrieval_status` (string)
- `retrieval_error` (string)
- `usage_class` (string)

Partition suggestion: `date(discovered_at_utc)`.

### 2) `bronze_aemo_document_raw_text`

One row per extraction attempt.

- `extract_id` (uuid)
- `manifest_id` (uuid)
- `parser_family` (string: html/pdf/ocr/table)
- `parser_version` (string)
- `extracted_at_utc` (timestamp)
- `text_storage_uri` (string)
- `text_hash_sha256` (string)
- `page_count` (int)
- `extract_status` (string)
- `extract_error` (string)
- `metadata_json` (json)

### 3) `silver_aemo_documents`

Canonical document-level view.

- `document_id` (uuid)
- `latest_manifest_id` (uuid)
- `canonical_url` (string)
- `title` (string)
- `content_type` (string)
- `published_date` (date)
- `effective_date` (date)
- `version_label` (string)
- `is_current` (boolean)
- `supersedes_document_id` (uuid)
- `superseded_by_document_id` (uuid)
- `attribution_text` (string)
- `markets` (array<string>)
- `topics` (array<string>)

### 4) `silver_aemo_document_chunks`

Chunk-level retrieval substrate.

- `chunk_id` (uuid)
- `document_id` (uuid)
- `manifest_id` (uuid)
- `chunk_index` (int)
- `chunk_text` (string)
- `chunk_text_hash` (string)
- `heading_path` (array<string>)
- `page_start` (int)
- `page_end` (int)
- `token_count` (int)
- `language` (string)
- `effective_date` (date)
- `is_current` (boolean)
- `metadata_json` (json)

### Optional tables

- `silver_aemo_document_facts` for extracted entities/facts with provenance.
- `silver_aemo_procedure_versions` for explicit version timelines.
- `silver_aemo_consultations` for submissions/deadlines/stage tracking.

---

## Parsing and extraction design

### Parser stack

1. **HTML parser**
   - readability/boilerplate removal;
   - heading structure capture (`h1..h6`);
   - table and list retention.
2. **PDF text parser**
   - preserve page boundaries;
   - retain table hints and section headers.
3. **OCR fallback** for scanned PDFs
   - trigger when extracted text density below threshold.
4. **Metadata extractor**
   - title, publication date, effective date, reference code.

### Repeatable reprocessing

- extraction outputs are versioned by `parser_version`;
- reprocessing creates new records, never in-place overwrite;
- silver views select preferred parser profile via deterministic precedence.

### Chunking

- structure-aware chunking by heading/page boundaries first;
- token-window fallback with overlap;
- keep `heading_path` and page ranges for citations.

---

## Retrieval and indexing architecture

## Recommended stack

### Production default

**OpenSearch hybrid + reranking** as primary serving index, with Delta tables as truth:

- BM25 for keyword precision,
- vector search for semantic recall,
- metadata filtering on source/effective/current status,
- rank normalization and weighted fusion.

### Low-complexity alternative

**Postgres FTS + pgvector** for smaller deployments/local-first operations:

- one service for metadata + lexical + vector,
- easier local reproducibility,
- lower ops overhead early on.

### Local development

- DuckDB/LanceDB can be used for quick experiments, but treat as ephemeral derived indexes from silver tables.

### Retrieval policy

1. Query rewrite (optional).
2. Parallel lexical + vector retrieval.
3. Filter by `usage_class != blocked`, `is_current` toggle, market/topic filters.
4. Fuse ranks (RRF or weighted normalization).
5. Optional cross-encoder reranker.
6. Return chunks + document-level citation metadata.

---

## Dagster implementation shape

Proposed modules:

```text
backend-services/dagster-user/aemo-etl/src/aemo_etl/resources/aemo_website.py

backend-services/dagster-user/aemo-etl/src/aemo_etl/assets/aemo_documents/
  discovery.py
  landing.py
  parsing.py
  chunking.py
  indexing.py
  definitions.py
```

Proposed asset graph:

```text
aemo_document_discovery
  → aemo_document_downloads
  → aemo_document_text_extraction
  → aemo_document_chunks
  → aemo_document_search_index
```

### Asset responsibilities

- `aemo_document_discovery`: emit candidate URLs + metadata.
- `aemo_document_downloads`: fetch bytes conditionally and update manifest.
- `aemo_document_text_extraction`: parse/OCR and write raw text table.
- `aemo_document_chunks`: create chunk rows with heading/page provenance.
- `aemo_document_search_index`: build/update serving index aliases.

---

## Minimal viable implementation (MVP)

1. Build section allowlist and crawler policy.
2. Implement `bronze_aemo_document_manifest` + raw byte archiving.
3. Add HTML/PDF extraction into `bronze_aemo_document_raw_text`.
4. Add layout-aware chunking into `silver_aemo_document_chunks`.
5. Implement one hybrid retrieval index (Postgres or OpenSearch).
6. Add offline retrieval evaluation harness (query set + relevance labels).
7. Only then add first RAG endpoint consuming retrieval API.

### MVP quality gates

- >=95% successful fetches for allowlisted pages.
- >=90% non-empty text extraction for fetched documents.
- citation completeness: 100% chunks mapped to document + source URI.
- retrieval benchmark created before assistant release.

---

## Long-term architecture roadmap

### Phase 1: Corpus foundation

- manifest-first ingestion
- immutable archive
- parser/chunker baseline

### Phase 2: Retrieval hardening

- hybrid retrieval + metadata filters
- reranking and evaluation loops
- procedure-version awareness

### Phase 3: Document intelligence

- fact/entity extraction tables
- consultation timeline intelligence
- graph overlays for entity relationships

### Phase 4: Consumer experiences

- analyst search UI
- RAG assistant with strict citations
- compliance monitors for stale/superseded references

---

## Open questions and risks

1. **Anti-bot and transient blocking risk:** some AEMO endpoints may return interstitial failures to scripted clients; need browser-assisted fallback or manual acquisition path.
2. **Version-link ambiguity:** supersession relationships are inconsistently expressed; requires rule heuristics + possible human review queue.
3. **OCR cost/latency:** scanned PDFs can materially increase runtime and cost; enforce OCR gating thresholds.
4. **Evaluation debt:** retrieval quality cannot be inferred from “looks good” manual checks; build benchmark set early.
5. **Licensing edge cases:** third-party or confidential attachments may appear in consultations; enforce `usage_class` policies at ingest time.

---

## Recommended next actions in this PR series

1. Add scaffold modules/resources under `aemo_etl/assets/aemo_documents` and `resources/aemo_website.py`.
2. Add Delta schemas and table-create utilities for manifest/raw_text/documents/chunks.
3. Add two maintained docs:
   - `backend-services/dagster-user/aemo-etl/docs/sources/aemo-website.md`
   - `backend-services/dagster-user/aemo-etl/docs/sources/aemo-document-corpus.md`
4. Add a small retrieval evaluation dataset and harness.
5. Defer assistant/RAG endpoint until retrieval gates pass.
