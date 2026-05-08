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

Providers may also write one metadata line to stderr using the prefix
`shape-issues-provider-metadata:` followed by a JSON object. The gate records
that object under `embedding.provider_metadata` and surfaces
`runtime_device` and `batch_size` in `report.md` and `report.json`.

## Hugging Face Default

The default live model is `Qwen/Qwen3-Embedding-0.6B`. Remote model code is
disabled unless the Operator explicitly opts in with `--trust-remote-code`.
The default runtime uses a conservative batch size of 2 and `--device auto`.
Auto mode chooses CUDA only when Torch can confirm at least 6 GiB of free VRAM;
otherwise the provider falls back to CPU and records the fallback reason in the
gate report. This keeps default gate runs usable on constrained, low-VRAM, or
CUDA-unavailable hosts.

Default command:

```bash
uv run --with sentence-transformers --with torch \
  python .agents/skills/shape-issues/scripts/hf_embed_jsonl.py \
  --model Qwen/Qwen3-Embedding-0.6B \
  --no-trust-remote-code \
  --batch-size 2 \
  --device auto \
  --min-free-vram-gb 6
```

Use `CUDA_VISIBLE_DEVICES=""` or pass `--device cpu` to force CPU on hosts where
CUDA is present but should not be used. If dependencies, model download, disk,
RAM, or accelerator support are missing, the provider fails and the gate fails.

`Qwen/Qwen3-Embedding-8B` remains available only as an explicit operator
override for machines with enough memory. When using it, change both the
embedding command and gate `--model-id`, keep `--no-trust-remote-code` unless
the Operator approves remote code, and reduce batch size as needed.

## Fixture Provider

Use `scripts/fixture_embed_jsonl.py` for tests and dry examples. It is
deterministic and standard-library only; it is not a semantic quality substitute
for the Hugging Face provider.
