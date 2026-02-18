# AGENTS.md - Australian Energy Markets Data Repository

## Overview
Multi-service Python project for AEMO energy market data ingestion/processing using Dagster, Polars, and Delta Lake.

**Structure**: `dagster-etl-services/aemo-etl/` (ETL), `ausenergymarket-api/` (FastAPI), `authentication-service/` (OAuth), `infrastructure/aws/` (CDK)

## Commands

**aemo-etl**: `cd backend-services/dagster-etl-services/aemo-etl`
- `uv sync` - Install deps
- `uv run pytest` / `--cov=src --cov-report=html` / `-n auto` - Test
- `dagster dev` - Run server
- `basedpyright src/` - Type check

**API**: `cd backend-services/ausenergymarket-api && uv sync && uv run uvicorn ausenergymarket_api:app --reload`

## Code Style Guidelines

### Python Version

- **Required**: Python >= 3.13
- Specified in `pyproject.toml` and `.python-version` files

### Package Management

- **Tool**: UV (not pip, poetry, or pipenv)
- Lock file: `uv.lock` (committed to version control)

### Import Organization

Imports should be organized in the following order with blank lines between groups:

1. Standard library imports
2. Third-party library imports  
3. Local application imports

**Example:**
```python
import pathlib as pt
from collections.abc import Generator
from typing import Any, Callable, Unpack

import dagster as dg
import polars as pl
from deltalake import DeltaTable

from aemo_etl.configuration import BRONZE_BUCKET, Link
from aemo_etl.factory.asset.param_spec import GraphAssetParamSpec
from aemo_etl.util import get_metadata_schema
```

### Type Hints

- **Required**: All function signatures must have type hints
- Use modern type hints from `typing` module and `collections.abc`
- Prefer `collections.abc.Generator` over `typing.Generator`
- Prefer `collections.abc.Callable` over `typing.Callable`
- Use `dict[str, Any]` not `Dict[str, Any]` (Python 3.9+ style)
- Use `list[str]` not `List[str]`
- Use `TypedDict` for structured dictionaries
- Use `Unpack` for unpacking kwargs with TypedDict
- Type boto3 clients with `types-boto3[service]` stubs (e.g., `S3Client`, `DynamoDBClient`)

**Example:**
```python
from collections.abc import Callable
from typing import Unpack

def process_data(
    bucket: str,
    prefix: str,
    transform: Callable[[str], str] | None = None,
    **kwargs: Unpack[ConfigSpec],
) -> list[dict[str, Any]]:
    ...
```

### Type Checking with Pyright

- **Tool**: basedpyright (configured in `pyproject.toml`)
- **Mode**: `standard` type checking
- Use inline comments to suppress specific warnings when necessary:

```python
# pyright: reportUnknownMemberType=false, reportAny=false
```

Common suppressions in this codebase:
- `reportUnknownMemberType=false` - for third-party library type issues
- `reportMissingTypeStubs=false` - when stubs unavailable
- `reportExplicitAny=false` - when `Any` is intentional
- `reportUnusedParameter=false` - for pytest fixtures

### Naming Conventions

- **Modules/packages**: `snake_case` (e.g., `aemo_etl`, `factory`)
- **Functions/variables**: `snake_case` (e.g., `download_link_and_upload_to_s3_op`)
- **Classes**: `PascalCase` (e.g., `ProcessedLink`, `S3Resource`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `BRONZE_BUCKET`, `LANDING_BUCKET`)
- **Private functions**: prefix with `_` (e.g., `_download_nemweb_public_files_to_s3_asset_factory.py`)
- **Factory functions**: suffix with `_factory` (e.g., `download_nemweb_public_files_to_s3_asset_factory`)

### File Naming

- Source files in `src/` use `snake_case.py`
- Test files use `test_` prefix: `test__factory_name.py` (note double underscore)
- Private modules start with `_`: `_internal_module.py`

### Code Formatting

- **Line length**: No strict limit visible, but keep reasonable (~100-120 chars)
- **Indentation**: 4 spaces (Python standard)
- **String quotes**: Double quotes preferred for consistency
- **Trailing commas**: Use in multi-line data structures

### Dagster-Specific Patterns

- Use factory functions to create reusable assets/ops
- Name patterns: `{purpose}_{asset|op|check}_factory`
- Use `@asset` for data assets, `@op` for operations
- Use `@graph_asset` for composed assets
- Include metadata schemas with `get_metadata_schema()`
- Set meaningful `group_name`, `description`, and `kinds` on assets

**Example:**
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

- Use specific exception types, not bare `except:`
- Re-raise exceptions when appropriate with `raise`
- Log context before handling errors
- Use `response.raise_for_status()` for HTTP requests
- Import specific exceptions: `from deltalake.exceptions import TableNotFoundError`

**Example:**
```python
try:
    table = DeltaTable(table_path, storage_options=storage_options)
except TableNotFoundError:
    context.log.warning(f"Table not found at {table_path}")
    raise
except Exception as e:
    context.log.error(f"Failed to process: {e}")
    # Fallback logic
```

### Testing Guidelines

- Tests in `tests/` directory mirror `src/` structure
- Use pytest fixtures defined in `conftest.py`
- Mock AWS services with `moto` library
- Common fixtures: `moto_server`, `s3`, `dynamodb`, `create_buckets`, `create_delta_log`
- Use `@pytest.fixture(autouse=True)` for setup/teardown
- Disable pyright warnings in test files: `# pyright: reportUnusedParameter=false`

**Test file structure:**
```python
import pytest
from aemo_etl import factory

# pyright: reportUnusedParameter=false


@pytest.fixture(autouse=True)
def setup_test_data():
    # Setup code
    yield
    # Teardown code


def test__feature_name(s3: S3Client, create_buckets):
    # Test implementation
    assert result == expected
```

### Documentation

- Use docstrings for public functions and classes
- Keep inline comments minimal and meaningful
- Document complex logic and non-obvious decisions
- Include type hints instead of documenting types in docstrings

### Environment Variables

Key environment variables used:
- `DEVELOPMENT_ENVIRONMENT`: "DEV", "TEST", "PROD"
- `DEVELOPMENT_LOCATION`: "LOCAL", "AWS"
- `AWS_*`: Standard AWS credentials and configuration
- `DAGSTER_POSTGRES_*`: Database connection settings

### Delta Lake Specifics

- Use S3 with DynamoDB locking provider for ACID transactions
- Storage options passed to `DeltaTable` constructor
- Always specify `storage_options` when working with S3-backed tables
- Use Polars for reading/writing Delta tables

### Common Patterns

**S3 operations:**
```python
from types_boto3_s3 import S3Client

def process_s3_files(s3_client: S3Client, bucket: str, prefix: str):
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        if "Contents" in page:
            for obj in page["Contents"]:
                key = obj["Key"]
                # Process object
```

**Polars DataFrames:**
```python
import polars as pl
from polars import LazyFrame

# Prefer LazyFrame for better performance
lf = pl.scan_parquet("s3://bucket/path/*.parquet")
result = lf.filter(pl.col("date") > "2024-01-01").collect()
```

## Reference Files

For code style examples, see:
- `backend-services/dagster-etl-services/aemo-etl/src/aemo_etl/factory/asset/_download_nemweb_public_files_to_s3_asset_factory.py`
- `backend-services/dagster-etl-services/aemo-etl/tests/conftest.py`
- `backend-services/ausenergymarket-api/src/ausenergymarket_api/__init__.py`
