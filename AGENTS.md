# AGENTS.md - Australian Energy Markets Data Repository

## Overview
Multi-service Python project for AEMO energy market data ingestion/processing using Dagster, Polars, and Delta Lake.

**Services:**
- `backend-services/dagster-etl-services/aemo-etl/` — Dagster ETL pipelines (primary service)
- `backend-services/ausenergymarket-api/` — FastAPI data API with Plotly dashboards
- `backend-services/authentication-service/` — OAuth2/OIDC via AWS Cognito
- `backend-services/caddy-service/` — TLS termination and reverse proxy
- `infrastructure/aws/` — AWS CDK stacks

## Commands

### aemo-etl (primary service)
```bash
cd backend-services/dagster-etl-services/aemo-etl

uv sync                          # Install dependencies
uv run pytest tests/             # Run all tests
uv run pytest tests/ -n auto     # Run tests in parallel (all CPU cores)
uv run pytest tests/path/to/test_file.py                   # Run a single test file
uv run pytest tests/path/to/test_file.py::test_function    # Run a single test by name
uv run pytest tests/path/to/test_file.py::Class::method    # Run a single test method
uv run ty check src/             # Type check (preferred over basedpyright)
uv run ruff check .              # Lint
uv run ruff format .             # Format
uv run ruff check --fix . && uv run ruff format .  # Lint + format in one pass
dagster dev -m aemo_etl.definitions --verbose      # Run Dagster dev server
```

### ausenergymarket-api
```bash
cd backend-services/ausenergymarket-api
uv sync
uv run uvicorn ausenergymarket_api:app --reload
```

### authentication-service
```bash
cd backend-services/authentication-service
uv sync
uvicorn main:app --reload
```

### infrastructure/aws (CDK)
```bash
cd infrastructure/aws
uv sync && . .venv/bin/activate
cdk deploy --all --method direct --require-approval never --concurrency 8
```

### Container / local dev
```bash
make development-image      # Build dev container (podman)
make development-container  # Start dev container
make attach                 # Attach to running dev container
make localstack             # Start LocalStack Pro
```

## Code Style Guidelines

### Python Version
- **Required**: Python >= 3.13 across all services
- Runtime image: `python:3.13-slim` in all Dockerfiles

### Package Management
- **Tool**: `uv` (not pip, poetry, or pipenv)
- Lock file: `uv.lock` committed to version control
- Install: `uv sync`; add deps: `uv add <pkg>`

### Import Organization
Three groups separated by blank lines: stdlib, third-party, local.

```python
import pathlib as pt
from collections.abc import Generator
from typing import Any, Unpack

import dagster as dg
import polars as pl
from deltalake import DeltaTable

from aemo_etl.configuration import BRONZE_BUCKET, Link
from aemo_etl.factory.asset.param_spec import GraphAssetParamSpec
from aemo_etl.util import get_metadata_schema
```

### Type Hints
- **Required** on all function signatures (enforced by ruff `ANN` rules)
- Use modern built-in generics: `dict[str, Any]`, `list[str]`, `tuple[int, ...]`
- Prefer `collections.abc.Generator` / `collections.abc.Callable` over `typing` equivalents
- Use `TypedDict` + `Unpack` for typed `**kwargs`
- Type boto3 clients with `types-boto3[service]` stubs (e.g., `S3Client`, `DynamoDBClient`)
- Use `X | Y` union syntax — never `Optional[X]` or `Union[X, Y]`

```python
from collections.abc import Callable
from typing import Unpack

def process_data(
    bucket: str,
    transform: Callable[[str], str] | None = None,
    **kwargs: Unpack[ConfigSpec],
) -> list[dict[str, Any]]:
    ...
```

### Type Checking with ty
- **Tool**: `ty` (preferred; replaces basedpyright)
- Run: `uv run ty check src/`
- `ty` is listed as a dev dependency in `pyproject.toml` (`ty>=0.0.17`)
- For inline suppression of known issues in test files use comment suppressions at file top

```python
# ty: ignore[...] or suppress via pyright-compat comments where needed
```

- `reportUnusedParameter=false` — add at top of all test files (pyright-compat)
- `reportUnknownMemberType=false` — third-party library type gaps
- `reportMissingTypeStubs=false` — when stubs are unavailable

### Linting and Formatting
- **Tool**: `ruff` (not black, flake8, or isort)
- Selected rules: `ANN`, `E`, `F` (see `pyproject.toml`)
- Line length: 88 chars (ruff default)
- `__init__.py` files: import-sort rule `I` is ignored
- Run lint + format together: `uv run ruff check --fix . && uv run ruff format .`

### Naming Conventions
- **Modules/packages**: `snake_case`
- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `BRONZE_BUCKET`, `LANDING_BUCKET`)
- **Private modules/functions**: prefix with `_`
- **Factory functions**: suffix with `_factory`
- **Test files**: `test__<name>.py` (double underscore after `test`)

### Code Formatting
- Indentation: 4 spaces
- String quotes: double quotes preferred
- Trailing commas in multi-line structures

### Dagster-Specific Patterns
- Use factory functions to create reusable assets/ops/checks
- Name pattern: `{purpose}_{asset|op|check}_factory`
- Use `@asset` for data assets, `@op` for operations, `@graph_asset` for composed pipelines
- Set `group_name`, `description`, and `kinds` on every asset

```python
@asset(
    group_name="aemo",
    key_prefix=["bronze", "mibb"],
    name="price_data",
    description="Market price data from AEMO",
    kinds={"source", "table", "deltalake"},
)
def price_data_asset(context: AssetExecutionContext) -> LazyFrame:
    ...
```

### Error Handling
- Use specific exception types; never bare `except:`
- Re-raise with `raise` when not handling fully
- Log context before handling errors using `context.log`
- Use `response.raise_for_status()` for HTTP requests

```python
try:
    table = DeltaTable(table_path, storage_options=storage_options)
except TableNotFoundError:
    context.log.warning(f"Table not found at {table_path}")
    raise
```

### Testing Guidelines
- Tests in `tests/` mirror `src/` structure
- Use pytest fixtures from `conftest.py`
- Mock AWS with `moto` via `ThreadedMotoServer` (not `@mock_aws`) — Polars/DeltaLake
  need to reach the mock S3 endpoint over real HTTP, which `@mock_aws` does not support
- Add `# pyright: reportUnusedParameter=false` at the top of all test files
- Key fixtures (from `conftest.py`): `moto_server`, `s3`, `dynamodb`, `create_buckets`, `create_delta_log`
- `moto_server` is `scope="function"` — a fresh mocked AWS per test

```python
# pyright: reportUnusedParameter=false
import pytest
from types_boto3_s3 import S3Client

from aemo_etl import factory


@pytest.fixture(autouse=True)
def setup_test_data(s3: S3Client, create_buckets: None) -> None:
    ...


def test__feature_name(s3: S3Client, create_buckets: None) -> None:
    result = factory.some_function()
    assert result == expected
```

### Delta Lake Specifics
- S3 + DynamoDB locking provider for ACID transactions (`delta_log` table)
- Always pass `storage_options` when constructing `DeltaTable`
- Use Polars `LazyFrame` for all reads/writes; call `.collect()` as late as possible

### Environment Variables
- `DEVELOPMENT_ENVIRONMENT`: `dev` | `test` | `prod` — bucket name prefix
- `DEVELOPMENT_LOCATION`: `local` | `aws` — controls CORS, sensor status, S3 safety
- `NAME_PREFIX`: default `energy-market` — used in all bucket names
- `AWS_DEFAULT_REGION`: `ap-southeast-2`
- `AWS_ENDPOINT_URL`: set to moto server URL during tests
- `AWS_S3_LOCKING_PROVIDER`: `dynamodb`
- `DAGSTER_POSTGRES_*`: PostgreSQL connection for Dagster storage

## Reference Files
- `backend-services/dagster-etl-services/aemo-etl/src/aemo_etl/factory/asset/_download_nemweb_public_files_to_s3_asset_factory.py`
- `backend-services/dagster-etl-services/aemo-etl/tests/conftest.py`
- `backend-services/ausenergymarket-api/src/ausenergymarket_api/__init__.py`
