# Embedding Providers

`shape_issue_gate.py` calls an embedding provider command. The command reads
JSONL records from stdin and writes JSONL records to stdout.

Input record:

```json
{"id": "record-id", "kind": "query", "text": "Text to embed"}
```

Output record:

```json
{"id": "record-id", "vector": [0.1, 0.2, 0.3]}
```

## Hugging Face Default

The v1 default live model is `Qwen/Qwen3-Embedding-8B`. The model page records
it as Apache-2.0, 8B parameters, 32K context, up to 4096 dimensions, and No. 1
on the MTEB multilingual leaderboard as of June 5, 2025 with score 70.58.

Default command:

```bash
uv run --with sentence-transformers --with torch \
  python .agents/skills/shape-issues/scripts/hf_embed_jsonl.py \
  --model Qwen/Qwen3-Embedding-8B
```

If dependencies, model download, disk, RAM, or accelerator support are missing,
the provider fails and the gate fails. Choose a smaller model only through an
explicit command/config change and record that downgrade in the report.

## Fixture Provider

Use `scripts/fixture_embed_jsonl.py` for tests and dry examples. It is
deterministic and standard-library only; it is not a semantic quality substitute
for the Hugging Face provider.
