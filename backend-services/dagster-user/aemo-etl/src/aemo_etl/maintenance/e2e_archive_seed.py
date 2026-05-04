"""Cached archive seed refresh support for local AEMO ETL End-to-end tests."""

import fnmatch
import json
import os
import shutil
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Final, Literal

from dagster import AssetKey, AssetSelection, Definitions
from types_boto3_s3 import S3Client

from aemo_etl.factories.df_from_s3_keys.source_tables import (
    DFFromS3KeysSourceTableSpec,
    load_source_table_specs,
)
from aemo_etl.utils import (
    S3ObjectHead,
    get_object_head_from_pages,
    get_s3_object_keys_from_prefix_and_name_glob,
    get_s3_pagination,
)

DEFAULT_ARCHIVE_SEED_BUCKET: Final = "dev-energy-market-archive"
DEFAULT_RAW_LATEST_COUNT: Final = 10
DEFAULT_ZIP_LATEST_COUNT: Final = 3
SEED_ROOT_ENV_VAR: Final = "AEMO_ETL_E2E_SEED_ROOT"
SEED_CACHE_DIR_NAME: Final = "archive-seed"
SEED_OBJECTS_DIR_NAME: Final = "objects"
SEED_SPEC_FILE_NAME: Final = "seed-spec.json"
SEED_RUN_MANIFEST_FILE_NAME: Final = "seed-run-manifest.json"
GAS_MODEL_TARGET: Final = "gas_model"
ZIP_GLOB_PATTERN: Final = "*.zip"
SeedRunOperation = Literal["refresh", "load-localstack"]
SeedRunStatus = Literal["success", "failed"]


@dataclass(frozen=True, slots=True)
class SourceTableSeedSpec:
    """Seed specification for one required source-table archive slice."""

    table_id: str
    domain: str
    bronze_asset_key: tuple[str, ...]
    silver_asset_key: tuple[str, ...]
    archive_prefix: str
    glob_pattern: str

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "table_id": self.table_id,
            "domain": self.domain,
            "bronze_asset_key": list(self.bronze_asset_key),
            "silver_asset_key": list(self.silver_asset_key),
            "archive_prefix": self.archive_prefix,
            "glob_pattern": self.glob_pattern,
        }


@dataclass(frozen=True, slots=True)
class ZipDomainSeedSpec:
    """Seed specification for one required zip archive domain."""

    domain: str
    unzipper_asset_key: tuple[str, ...]
    archive_prefix: str
    glob_pattern: str = ZIP_GLOB_PATTERN

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "domain": self.domain,
            "unzipper_asset_key": list(self.unzipper_asset_key),
            "archive_prefix": self.archive_prefix,
            "glob_pattern": self.glob_pattern,
        }


@dataclass(frozen=True, slots=True)
class ArchiveSeedSpec:
    """Full archive seed specification for a local End-to-end test target."""

    target: str
    source_tables: tuple[SourceTableSeedSpec, ...]
    zip_domains: tuple[ZipDomainSeedSpec, ...]

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "target": self.target,
            "source_tables": [
                source_table.as_dict() for source_table in self.source_tables
            ],
            "zip_domains": [zip_domain.as_dict() for zip_domain in self.zip_domains],
        }


@dataclass(frozen=True, slots=True)
class SeedObject:
    """Archive object selected for a seed refresh or local cache load."""

    key: str
    size: int

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {"key": self.key, "size": self.size}


@dataclass(frozen=True, slots=True)
class SeedCoverageEntry:
    """Coverage result for one source table or zip domain."""

    kind: Literal["source-table", "zip-domain"]
    name: str
    archive_prefix: str
    glob_pattern: str
    requested_count: int
    available_count: int
    selected_objects: tuple[SeedObject, ...]

    @property
    def shortfall(self) -> int:
        """Return how many requested objects were unavailable."""
        return max(0, self.requested_count - self.available_count)

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "kind": self.kind,
            "name": self.name,
            "archive_prefix": self.archive_prefix,
            "glob_pattern": self.glob_pattern,
            "requested_count": self.requested_count,
            "available_count": self.available_count,
            "shortfall": self.shortfall,
            "selected_objects": [
                selected_object.as_dict() for selected_object in self.selected_objects
            ],
        }


@dataclass(frozen=True, slots=True)
class SeedRunManifest:
    """Seed run manifest written beside the local archive seed cache."""

    operation: SeedRunOperation
    status: SeedRunStatus
    generated_at: datetime
    seed_root: Path
    archive_bucket: str
    landing_bucket: str | None
    raw_latest_count: int
    zip_latest_count: int
    spec: ArchiveSeedSpec
    source_table_coverage: tuple[SeedCoverageEntry, ...]
    zip_domain_coverage: tuple[SeedCoverageEntry, ...]

    @property
    def shortfalls(self) -> tuple[SeedCoverageEntry, ...]:
        """Return coverage entries that have fewer objects than requested."""
        return tuple(
            entry
            for entry in (*self.source_table_coverage, *self.zip_domain_coverage)
            if entry.shortfall > 0
        )

    @property
    def selected_objects(self) -> tuple[SeedObject, ...]:
        """Return de-duplicated selected seed objects in stable key order."""
        objects_by_key: dict[str, SeedObject] = {}
        for entry in (*self.source_table_coverage, *self.zip_domain_coverage):
            for selected_object in entry.selected_objects:
                objects_by_key[selected_object.key] = selected_object
        return tuple(objects_by_key[key] for key in sorted(objects_by_key))

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "operation": self.operation,
            "status": self.status,
            "generated_at": self.generated_at.isoformat(),
            "seed_root": str(self.seed_root),
            "archive_bucket": self.archive_bucket,
            "landing_bucket": self.landing_bucket,
            "raw_latest_count": self.raw_latest_count,
            "zip_latest_count": self.zip_latest_count,
            "spec": self.spec.as_dict(),
            "source_table_coverage": [
                entry.as_dict() for entry in self.source_table_coverage
            ],
            "zip_domain_coverage": [
                entry.as_dict() for entry in self.zip_domain_coverage
            ],
            "shortfalls": [entry.as_dict() for entry in self.shortfalls],
            "selected_object_count": len(self.selected_objects),
            "selected_objects": [
                selected_object.as_dict() for selected_object in self.selected_objects
            ],
        }


class SeedCoverageError(RuntimeError):
    """Raised when the archive seed cache cannot satisfy requested coverage."""

    def __init__(self, manifest: SeedRunManifest) -> None:
        """Create the exception from the failed seed-run manifest."""
        self.manifest = manifest
        super().__init__(
            "archive seed coverage shortfall: "
            f"{len(manifest.shortfalls)} requirement(s) missing objects"
        )


def default_seed_root() -> Path:
    """Return the host-local seed root, honoring the container env override."""
    configured_seed_root = os.environ.get(SEED_ROOT_ENV_VAR)
    if configured_seed_root is not None and configured_seed_root != "":
        return Path(configured_seed_root)

    cwd = Path.cwd().resolve()
    for candidate in (cwd, *cwd.parents):
        repo_aemo_etl = candidate / "backend-services/dagster-user/aemo-etl"
        if (repo_aemo_etl / "pyproject.toml").exists():
            return candidate / "backend-services/.e2e/aemo-etl"

        backend_aemo_etl = candidate / "dagster-user/aemo-etl"
        if (backend_aemo_etl / "pyproject.toml").exists():
            return candidate / ".e2e/aemo-etl"

        if (
            candidate.name == "aemo-etl"
            and candidate.parent.name == "dagster-user"
            and (candidate / "pyproject.toml").exists()
        ):
            return candidate.parent.parent / ".e2e/aemo-etl"

    return Path("backend-services/.e2e/aemo-etl")


def seed_cache_root(seed_root: Path) -> Path:
    """Return the archive seed cache root under the seed root."""
    return seed_root / SEED_CACHE_DIR_NAME


def seed_objects_root(seed_root: Path) -> Path:
    """Return the cached object root under the seed root."""
    return seed_cache_root(seed_root) / SEED_OBJECTS_DIR_NAME


def seed_spec_path(seed_root: Path) -> Path:
    """Return the cached seed spec path under the seed root."""
    return seed_cache_root(seed_root) / SEED_SPEC_FILE_NAME


def seed_run_manifest_path(seed_root: Path) -> Path:
    """Return the seed-run manifest path under the seed root."""
    return seed_root / SEED_RUN_MANIFEST_FILE_NAME


def build_gas_model_archive_seed_spec(definitions: Definitions) -> ArchiveSeedSpec:
    """Derive the full gas_model archive seed spec from Dagster definitions."""
    repository_def = definitions.get_repository_def()
    assets_defs = repository_def.assets_defs_by_key.values()
    selected_keys = (
        AssetSelection.groups(GAS_MODEL_TARGET).upstream().resolve(assets_defs)
    )

    source_tables: list[SourceTableSeedSpec] = []
    for source_table in load_source_table_specs():
        bronze_asset_key = AssetKey(
            ["bronze", source_table.domain, source_table.bronze_table_name]
        )
        if bronze_asset_key not in selected_keys:
            continue
        source_tables.append(_source_table_seed_spec(source_table))

    domains = sorted({source_table.domain for source_table in source_tables})
    zip_domains = tuple(
        zip_domain
        for zip_domain in (
            _zip_domain_seed_spec(domain, repository_def.assets_defs_by_key)
            for domain in domains
        )
        if zip_domain is not None
    )

    return ArchiveSeedSpec(
        target=GAS_MODEL_TARGET,
        source_tables=tuple(sorted(source_tables, key=lambda item: item.table_id)),
        zip_domains=zip_domains,
    )


def build_default_gas_model_archive_seed_spec() -> ArchiveSeedSpec:
    """Import aemo_etl.definitions.defs and derive the gas_model seed spec."""
    from aemo_etl.definitions import defs

    return build_gas_model_archive_seed_spec(defs())


def refresh_archive_seed(
    s3_client: S3Client,
    *,
    seed_root: Path,
    spec: ArchiveSeedSpec,
    archive_bucket: str,
    raw_latest_count: int,
    zip_latest_count: int,
    current_time: datetime | None = None,
) -> SeedRunManifest:
    """Refresh the local archive seed cache from the live archive bucket."""
    manifest = _build_s3_seed_manifest(
        s3_client,
        operation="refresh",
        seed_root=seed_root,
        spec=spec,
        archive_bucket=archive_bucket,
        landing_bucket=None,
        raw_latest_count=raw_latest_count,
        zip_latest_count=zip_latest_count,
        current_time=current_time,
    )
    if manifest.shortfalls:
        write_seed_run_manifest(manifest)
        raise SeedCoverageError(manifest)

    objects_root = seed_objects_root(seed_root)
    if objects_root.exists():
        shutil.rmtree(objects_root)
    objects_root.mkdir(parents=True, exist_ok=True)
    seed_spec_path(seed_root).parent.mkdir(parents=True, exist_ok=True)
    seed_spec_path(seed_root).write_text(
        json.dumps(spec.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    for selected_object in manifest.selected_objects:
        target_path = cache_path_for_key(seed_root, selected_object.key)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        s3_client.download_file(archive_bucket, selected_object.key, str(target_path))

    write_seed_run_manifest(manifest)
    return manifest


def load_cached_seed_to_localstack(
    s3_client: S3Client,
    *,
    seed_root: Path,
    spec: ArchiveSeedSpec,
    archive_bucket: str,
    landing_bucket: str,
    raw_latest_count: int,
    zip_latest_count: int,
    current_time: datetime | None = None,
) -> SeedRunManifest:
    """Validate cached seed coverage and upload selected objects to landing."""
    manifest = _build_cached_seed_manifest(
        operation="load-localstack",
        seed_root=seed_root,
        spec=spec,
        archive_bucket=archive_bucket,
        landing_bucket=landing_bucket,
        raw_latest_count=raw_latest_count,
        zip_latest_count=zip_latest_count,
        current_time=current_time,
    )
    if manifest.shortfalls:
        write_seed_run_manifest(manifest)
        raise SeedCoverageError(manifest)

    for selected_object in manifest.selected_objects:
        source_path = cache_path_for_key(seed_root, selected_object.key)
        s3_client.upload_file(str(source_path), landing_bucket, selected_object.key)

    write_seed_run_manifest(manifest)
    return manifest


def cache_path_for_key(seed_root: Path, key: str) -> Path:
    """Return the cache path for a safe relative S3 key."""
    key_path = PurePosixPath(key)
    if key_path.is_absolute() or any(
        part in {"", ".", ".."} for part in key_path.parts
    ):
        raise ValueError(f"invalid S3 key for archive seed cache: {key}")
    return seed_objects_root(seed_root).joinpath(*key_path.parts)


def write_seed_run_manifest(manifest: SeedRunManifest) -> None:
    """Write the seed-run manifest under the seed root."""
    manifest_path = seed_run_manifest_path(manifest.seed_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_table_seed_spec(
    source_table: DFFromS3KeysSourceTableSpec,
) -> SourceTableSeedSpec:
    return SourceTableSeedSpec(
        table_id=source_table.table_id,
        domain=source_table.domain,
        bronze_asset_key=(
            "bronze",
            source_table.domain,
            source_table.bronze_table_name,
        ),
        silver_asset_key=(
            "silver",
            source_table.domain,
            f"silver_{source_table.name_suffix}",
        ),
        archive_prefix=source_table.archive_prefix,
        glob_pattern=source_table.glob_pattern,
    )


def _zip_domain_seed_spec(
    domain: str,
    assets_defs_by_key: Mapping[AssetKey, object],
) -> ZipDomainSeedSpec | None:
    unzipper_asset_key = AssetKey(["bronze", domain, f"unzipper_{domain}"])
    if unzipper_asset_key not in assets_defs_by_key:
        return None
    return ZipDomainSeedSpec(
        domain=domain,
        unzipper_asset_key=tuple(unzipper_asset_key.path),
        archive_prefix=f"bronze/{domain}",
    )


def _build_s3_seed_manifest(
    s3_client: S3Client,
    *,
    operation: SeedRunOperation,
    seed_root: Path,
    spec: ArchiveSeedSpec,
    archive_bucket: str,
    landing_bucket: str | None,
    raw_latest_count: int,
    zip_latest_count: int,
    current_time: datetime | None,
) -> SeedRunManifest:
    _validate_latest_count(raw_latest_count, "raw_latest_count")
    _validate_latest_count(zip_latest_count, "zip_latest_count")
    source_table_coverage = tuple(
        _build_s3_coverage_entry(
            s3_client,
            kind="source-table",
            name=source_table.table_id,
            archive_bucket=archive_bucket,
            archive_prefix=source_table.archive_prefix,
            glob_pattern=source_table.glob_pattern,
            requested_count=raw_latest_count,
        )
        for source_table in spec.source_tables
    )
    zip_domain_coverage = tuple(
        _build_s3_coverage_entry(
            s3_client,
            kind="zip-domain",
            name=zip_domain.domain,
            archive_bucket=archive_bucket,
            archive_prefix=zip_domain.archive_prefix,
            glob_pattern=zip_domain.glob_pattern,
            requested_count=zip_latest_count,
        )
        for zip_domain in spec.zip_domains
    )
    return _manifest_from_coverage(
        operation=operation,
        seed_root=seed_root,
        spec=spec,
        archive_bucket=archive_bucket,
        landing_bucket=landing_bucket,
        raw_latest_count=raw_latest_count,
        zip_latest_count=zip_latest_count,
        source_table_coverage=source_table_coverage,
        zip_domain_coverage=zip_domain_coverage,
        current_time=current_time,
    )


def _build_cached_seed_manifest(
    *,
    operation: SeedRunOperation,
    seed_root: Path,
    spec: ArchiveSeedSpec,
    archive_bucket: str,
    landing_bucket: str | None,
    raw_latest_count: int,
    zip_latest_count: int,
    current_time: datetime | None,
) -> SeedRunManifest:
    _validate_latest_count(raw_latest_count, "raw_latest_count")
    _validate_latest_count(zip_latest_count, "zip_latest_count")
    source_table_coverage = tuple(
        _build_cached_coverage_entry(
            seed_root=seed_root,
            kind="source-table",
            name=source_table.table_id,
            archive_prefix=source_table.archive_prefix,
            glob_pattern=source_table.glob_pattern,
            requested_count=raw_latest_count,
        )
        for source_table in spec.source_tables
    )
    zip_domain_coverage = tuple(
        _build_cached_coverage_entry(
            seed_root=seed_root,
            kind="zip-domain",
            name=zip_domain.domain,
            archive_prefix=zip_domain.archive_prefix,
            glob_pattern=zip_domain.glob_pattern,
            requested_count=zip_latest_count,
        )
        for zip_domain in spec.zip_domains
    )
    return _manifest_from_coverage(
        operation=operation,
        seed_root=seed_root,
        spec=spec,
        archive_bucket=archive_bucket,
        landing_bucket=landing_bucket,
        raw_latest_count=raw_latest_count,
        zip_latest_count=zip_latest_count,
        source_table_coverage=source_table_coverage,
        zip_domain_coverage=zip_domain_coverage,
        current_time=current_time,
    )


def _build_s3_coverage_entry(
    s3_client: S3Client,
    *,
    kind: Literal["source-table", "zip-domain"],
    name: str,
    archive_bucket: str,
    archive_prefix: str,
    glob_pattern: str,
    requested_count: int,
) -> SeedCoverageEntry:
    object_heads = _list_matching_s3_object_heads(
        s3_client,
        archive_bucket=archive_bucket,
        archive_prefix=archive_prefix,
        glob_pattern=glob_pattern,
    )
    selected_objects = _latest_objects(object_heads, requested_count=requested_count)
    return SeedCoverageEntry(
        kind=kind,
        name=name,
        archive_prefix=archive_prefix,
        glob_pattern=glob_pattern,
        requested_count=requested_count,
        available_count=len(object_heads),
        selected_objects=selected_objects,
    )


def _build_cached_coverage_entry(
    *,
    seed_root: Path,
    kind: Literal["source-table", "zip-domain"],
    name: str,
    archive_prefix: str,
    glob_pattern: str,
    requested_count: int,
) -> SeedCoverageEntry:
    object_heads = _list_matching_cached_object_heads(
        seed_root=seed_root,
        archive_prefix=archive_prefix,
        glob_pattern=glob_pattern,
    )
    selected_objects = _latest_objects(object_heads, requested_count=requested_count)
    return SeedCoverageEntry(
        kind=kind,
        name=name,
        archive_prefix=archive_prefix,
        glob_pattern=glob_pattern,
        requested_count=requested_count,
        available_count=len(object_heads),
        selected_objects=selected_objects,
    )


def _list_matching_s3_object_heads(
    s3_client: S3Client,
    *,
    archive_bucket: str,
    archive_prefix: str,
    glob_pattern: str,
) -> dict[str, S3ObjectHead]:
    pages = get_s3_pagination(s3_client, archive_bucket, archive_prefix)
    object_heads = get_object_head_from_pages(pages)
    matching_keys = get_s3_object_keys_from_prefix_and_name_glob(
        archive_prefix,
        glob_pattern,
        sorted(object_heads),
    )
    return {key: object_heads[key] for key in matching_keys}


def _list_matching_cached_object_heads(
    *,
    seed_root: Path,
    archive_prefix: str,
    glob_pattern: str,
) -> dict[str, S3ObjectHead]:
    objects_root = seed_objects_root(seed_root)
    if not objects_root.exists():
        return {}

    prefix_path = objects_root / archive_prefix
    if not prefix_path.exists():
        return {}

    object_heads: dict[str, S3ObjectHead] = {}
    for path in prefix_path.rglob("*"):
        if not path.is_file():
            continue
        relative_key = path.relative_to(objects_root).as_posix()
        normalized_pattern = f"{archive_prefix}/{glob_pattern}".lower()
        if not fnmatch.fnmatch(relative_key.lower(), normalized_pattern):
            continue
        object_heads[relative_key] = {
            "Key": relative_key,
            "Size": path.stat().st_size,
        }
    return object_heads


def _latest_objects(
    object_heads: dict[str, S3ObjectHead],
    *,
    requested_count: int,
) -> tuple[SeedObject, ...]:
    selected_keys = sorted(object_heads)[-requested_count:]
    return tuple(
        SeedObject(
            key=key,
            size=int(object_heads[key].get("Size", 0)),
        )
        for key in selected_keys
    )


def _manifest_from_coverage(
    *,
    operation: SeedRunOperation,
    seed_root: Path,
    spec: ArchiveSeedSpec,
    archive_bucket: str,
    landing_bucket: str | None,
    raw_latest_count: int,
    zip_latest_count: int,
    source_table_coverage: tuple[SeedCoverageEntry, ...],
    zip_domain_coverage: tuple[SeedCoverageEntry, ...],
    current_time: datetime | None,
) -> SeedRunManifest:
    status: SeedRunStatus = (
        "failed"
        if any(
            entry.shortfall > 0
            for entry in (*source_table_coverage, *zip_domain_coverage)
        )
        else "success"
    )
    return SeedRunManifest(
        operation=operation,
        status=status,
        generated_at=current_time or datetime.now(timezone.utc),
        seed_root=seed_root,
        archive_bucket=archive_bucket,
        landing_bucket=landing_bucket,
        raw_latest_count=raw_latest_count,
        zip_latest_count=zip_latest_count,
        spec=spec,
        source_table_coverage=source_table_coverage,
        zip_domain_coverage=zip_domain_coverage,
    )


def _validate_latest_count(value: int, name: str) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero")
