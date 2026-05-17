---
name: repo-knowledge-base
description: Query this repo's generated Gas market knowledge base and guide cited gold Market context writing or review. Use when asked repo knowledge, gas-market corpus questions, generated bronze/silver/gold artifacts, generated chunks, chunk citations, or Market context drafting/review.
---

# Repo Knowledge Base

Use this skill for gas-market questions that should be grounded in the
repo-owned generated corpus, and for writing or reviewing cited gold
**Market context** pages. It is not a replacement for normal code search or
maintained documentation search.

## Read First

- Read `CONTEXT.md` for canonical language, especially **Subproject**,
  **Documentation sync**, **Agent skill**, **Gas market knowledge base**, and
  **Market context**.
- Read `docs/adr/0010-gas-market-knowledge-base.md` and
  `tools/gas-market-knowledge-base/README.md` for corpus architecture,
  generated-artifact roots, commands, and citation expectations.
- For Ralph work, remember that issues whose `## Context anchors` include
  `.agents/` paths require an operator-approved **Full-access implementation
  pass** before implementation.

## Artifact Boundaries

- Maintained repo docs live in `README.md`, `docs/**/*.md`, and the maintained
  Subproject Markdown named by `docs/repository/documentation-sync.md`. Changes
  there must follow **Documentation sync** and carry sync metadata.
- Generated corpus artifacts live under
  `tools/gas-market-knowledge-base/generated/{bronze,silver,gold}`. Generated
  Markdown under those roots is reviewable corpus output, not maintained router
  documentation, and must not get sync metadata.
- Raw PDFs stay outside git in archive storage or ignored local cache paths.
  Do not cite or commit raw PDF cache files.
- Do not copy bronze, silver, or gold corpus content into this skill body or
  maintained docs. Route agents to the generated artifacts instead.

## Query Workflow

1. Work from the Gas market knowledge base **Subproject** when running
   corpus-local commands:

   ```bash
   cd tools/gas-market-knowledge-base
   ```

2. Prefer generated artifacts in this order:
   - `generated/gold`: existing cited **Market context** pages.
   - `generated/silver/index/chunks.jsonl`: retrieval index rows with
     `chunk_id`, `content_sha256`, paths, and citations metadata.
   - `generated/silver/chunks`: chunk Markdown files to inspect the exact
     cited text.
   - `generated/silver/documents`: full extracted source-document Markdown for
     surrounding context.
   - `generated/bronze/source_manifest.jsonl`: source inventory, document
     identity, source URLs, and expected generated paths.
3. Search the generated corpus with `rg`, then open the cited chunk files and
   relevant index rows before answering:

   ```bash
   rg -n "<market term>" generated/gold generated/silver generated/bronze
   rg -n "\"chunk_id\"|<chunk-or-document-id>" generated/silver/index/chunks.jsonl
   ```

4. If the generated corpus is missing, stale, or unbuilt, say so and use the
   Subproject command surface such as `uv run gas-market-kb validate` to check
   integrity before relying on the artifacts.

## Citation Rules

- Every factual gas-market claim must cite generated evidence. Prefer a silver
  chunk citation that names `chunk_id`, chunk file path, `content_sha256`,
  source document Markdown path, and source URL or manifest line from
  `citations`.
- A gold **Market context** citation is acceptable only when the gold page
  itself cites silver chunks. Follow the chain to the chunk before repeating or
  extending the claim.
- Bronze source manifest rows and silver document pages can identify available
  sources, but do not use them alone for factual synthesis when chunk evidence
  is available.
- Reject or flag uncited factual synthesis. If evidence is absent, answer that
  the claim is not supported by the generated artifacts instead of filling the
  gap from memory.
- Mark inference separately from direct source evidence and cite the chunks that
  support the inference.

## Market Context Writing Or Review

- Write gold pages under `tools/gas-market-knowledge-base/generated/gold/`.
- Keep claims tight and cited near the sentence or paragraph they support.
- Include enough citation detail for reviewers to find the exact silver chunk
  and source hash without re-running retrieval.
- During review, fail the page for uncited factual claims, citations that do
  not resolve to generated chunks, stale source hashes, or prose that blurs
  maintained documentation with generated corpus output.
- Use root **Commit check** or Subproject QA only when the change touches the
  corresponding maintained docs, skill files, or corpus tool behavior.
