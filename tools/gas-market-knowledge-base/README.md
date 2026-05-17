# Gas Market Knowledge Base

This Subproject is the scaffold for the repo-local **Gas market knowledge
base**. It currently provides the Python package layout, local command surface,
generated-artifact policy, and **Unit test** lane. It does not read live S3,
run Docling extraction, create retrieval chunks, or add gold **Market context**
pages.

The placeholder command is available inside this Subproject with `uv run`:

```bash
uv run gas-market-kb --help
```

## Local QA

Run from this directory:

```bash
make unit-test
make fast-test
make run-prek
```

`make unit-test` is the gas-market-knowledge-base **Unit test** lane.
`make fast-test` currently aliases that lane until the Subproject has a wider
**Fast check** surface. `make run-prek` is the Subproject **Commit check**.

## Generated Artifacts

Future corpus text artifacts belong under these generated roots:

- `generated/bronze`: Docling Markdown extraction output and extraction
  metadata tied to source document identity.
- `generated/silver`: Docling Hybrid chunks prepared for retrieval.
- `generated/gold`: cited, agent-authored **Market context** pages.

Generated Markdown, JSON, YAML, and text files under those roots may be tracked
intentionally when future issues create reviewable corpus artifacts. Raw PDFs
are not tracked. Source PDF bytes stay in S3-compatible archive storage or in a
local cache such as `.pdf-cache/`, `cache/`, or `raw-pdfs/`, and repository
ignore rules keep `*.pdf` files out of this Subproject.

The repository **Documentation sync** workflow excludes any `generated/` path
from maintained-doc discovery, so generated corpus Markdown is reviewable
artifact output rather than maintained router documentation.

## Layout

- `src/gas_market_knowledge_base/cli.py`: placeholder CLI entrypoint.
- `tests/unit/`: package import and command-surface tests.
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
  - `tools/gas-market-knowledge-base/tests/unit/test_cli.py`
  - `tools/gas-market-knowledge-base/uv.lock`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `make unit-test`
  - `make run-prek`
  - `verify generated-artifact roots, raw-PDF ignore policy, and CLI help`
