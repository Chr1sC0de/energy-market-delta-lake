# Issue Context Assessors

`shape_issue_gate.py` calls an **Issue context assessor** provider command. The
gate reads the bundle, parses each issue's `## Context anchors`, assembles a
bounded evidence corpus, then passes that evidence to the provider. The provider
must judge the supplied evidence only; it must not freely explore the repo.

## Evidence Corpus

For each issue, the gate includes:

- existing files declared through `Path:` and `Doc:` anchors
- up to eight deterministic `rg` candidate files selected from issue text,
  symbols, labels, targets, QA commands, and shared context
- capped snippets from each evidence file
- a per-issue corpus digest and a top-level corpus digest

The report records the same corpus digests and snippets so the Operator can
audit what the assessor saw.

## Provider Protocol

The provider reads one JSON object from stdin and writes one JSON object to
stdout.

Input shape:

```json
{
  "schema_version": "shape-issues-context-assessor-v1",
  "bundle_digest": "<sha256>",
  "corpus_digest": "<sha256>",
  "shared_context": ["..."],
  "issues": [
    {
      "id": "issue-id",
      "title": "Issue title",
      "body": "## What to build\n...",
      "source_digest": "<sha256>",
      "anchors": {"paths": ["..."], "docs": ["..."]},
      "context_corpus": {
        "digest": "<sha256>",
        "anchor_paths": ["..."],
        "rg_candidate_paths": ["..."],
        "evidence": [
          {
            "path": "docs/agents/ralph-loop.md",
            "source": "anchor",
            "snippets": [{"start_line": 10, "text": "10: ..."}]
          }
        ]
      }
    }
  ]
}
```

Output shape:

```json
{
  "schema_version": "shape-issues-context-assessor-v1",
  "bundle_digest": "<same sha256>",
  "corpus_digest": "<same sha256>",
  "assessments": [
    {
      "id": "issue-id",
      "verdict": "pass",
      "confidence": 0.91,
      "cited_paths": ["docs/agents/ralph-loop.md"],
      "reasons": ["The supplied anchors identify the implementation surface."]
    }
  ]
}
```

Verdicts:

- `pass`: supplied evidence is enough for an implementation agent to work
  independently.
- `weak`: supplied evidence is relevant but likely missing important context.
- `fail`: supplied evidence is missing, stale, unrelated, or too vague.

The gate maps `weak`, `fail`, stale digests, invalid verdicts, invalid
confidence values, missing reasons, or citations outside supplied evidence to
`needs-context`.

## Default Provider

Default command:

```bash
python3 .agents/skills/shape-issues/scripts/codex_context_assessor.py --repo-root .
```

The wrapper invokes `codex exec` with read-only sandboxing and
`approval_policy="never"`, requests schema-shaped JSON, and instructs Codex to
judge only the supplied JSON evidence.

## Fixture Provider

Use `scripts/fixture_context_assessor.py` for tests and dry contract examples.
It is deterministic and standard-library only; it is not a quality substitute
for the Codex-backed assessor. Fixture-gated reports may be published only as
`--dry-run` previews unless the Operator passes `--allow-fixture-publish`; that
override leaves fixture provenance in `publish-manifest.json` and the final
issue body.
