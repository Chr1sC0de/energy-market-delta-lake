"""Pure archive source object planning for maintenance workflows."""

import fnmatch
from collections.abc import Mapping
from dataclasses import dataclass

type ArchiveObjectHead = Mapping[str, object]


@dataclass(frozen=True, slots=True)
class ArchiveSourceRequirement:
    """Archive object requirement for one source-table or archive domain."""

    kind: str
    name: str
    archive_prefix: str
    glob_pattern: str


@dataclass(frozen=True, slots=True)
class ArchiveSourceObject:
    """Normalized archive object selected by the pure planner."""

    key: str
    size: int

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {"key": self.key, "size": self.size}


@dataclass(frozen=True, slots=True)
class ArchiveSourceSelectionPolicy:
    """Selection and batching policy for archive source planning."""

    latest_count: int | None
    max_batch_bytes: int | None
    max_batch_files: int | None


@dataclass(frozen=True, slots=True)
class ArchiveSourceCoverage:
    """Coverage result for one archive source requirement."""

    requirement: ArchiveSourceRequirement
    requested_count: int | None
    available_count: int
    selected_objects: tuple[ArchiveSourceObject, ...]

    @property
    def kind(self) -> str:
        """Return the requirement kind."""
        return self.requirement.kind

    @property
    def name(self) -> str:
        """Return the requirement name."""
        return self.requirement.name

    @property
    def archive_prefix(self) -> str:
        """Return the archive prefix."""
        return self.requirement.archive_prefix

    @property
    def glob_pattern(self) -> str:
        """Return the archive glob pattern."""
        return self.requirement.glob_pattern

    @property
    def shortfall(self) -> int:
        """Return how many requested objects were unavailable."""
        if self.requested_count is None:
            return 0
        return max(0, self.requested_count - self.available_count)


@dataclass(frozen=True, slots=True)
class ArchiveSourceBatch:
    """One bounded batch of archive source objects."""

    objects: tuple[ArchiveSourceObject, ...]

    @property
    def total_bytes(self) -> int:
        """Return the total object size for this batch."""
        return sum(object_.size for object_ in self.objects)


@dataclass(frozen=True, slots=True)
class ArchiveSourcePlan:
    """Archive source coverage and batch plan."""

    selection_policy: ArchiveSourceSelectionPolicy
    coverage: tuple[ArchiveSourceCoverage, ...]
    batches: tuple[ArchiveSourceBatch, ...]

    @property
    def selected_objects(self) -> tuple[ArchiveSourceObject, ...]:
        """Return de-duplicated selected objects in batch order."""
        return tuple(object_ for batch in self.batches for object_ in batch.objects)

    @property
    def selected_object_count(self) -> int:
        """Return the de-duplicated selected object count."""
        return len(self.selected_objects)

    @property
    def planned_batch_count(self) -> int:
        """Return the number of planned archive source batches."""
        return len(self.batches)

    @property
    def total_bytes(self) -> int:
        """Return the total bytes across selected archive source objects."""
        return sum(batch.total_bytes for batch in self.batches)


def match_archive_source_objects(
    object_heads: Mapping[str, ArchiveObjectHead],
    *,
    archive_prefix: str,
    glob_pattern: str,
) -> tuple[ArchiveSourceObject, ...]:
    """Return normalized archive objects matching a prefix and file-name glob."""
    matching_keys = _matching_archive_source_keys(
        archive_prefix=archive_prefix,
        glob_pattern=glob_pattern,
        object_keys=sorted(object_heads),
    )
    return tuple(
        ArchiveSourceObject(
            key=key,
            size=_normalize_object_size(object_heads[key]),
        )
        for key in matching_keys
    )


def plan_archive_source_batches(
    objects: tuple[ArchiveSourceObject, ...],
    *,
    max_batch_bytes: int | None,
    max_batch_files: int | None,
) -> tuple[ArchiveSourceBatch, ...]:
    """Group archive source objects into bounded batches."""
    _validate_positive_optional(max_batch_bytes, "max_batch_bytes")
    _validate_positive_optional(max_batch_files, "max_batch_files")
    if len(objects) == 0:
        return ()

    batches: list[ArchiveSourceBatch] = []
    current_objects: list[ArchiveSourceObject] = []
    current_bytes = 0

    for object_ in objects:
        would_exceed_files = (
            max_batch_files is not None and len(current_objects) >= max_batch_files
        )
        would_exceed_bytes = (
            max_batch_bytes is not None
            and current_bytes + object_.size > max_batch_bytes
            and len(current_objects) > 0
        )
        if would_exceed_files or would_exceed_bytes:
            batches.append(ArchiveSourceBatch(objects=tuple(current_objects)))
            current_objects = []
            current_bytes = 0

        current_objects.append(object_)
        current_bytes += object_.size

    if len(current_objects) > 0:
        batches.append(ArchiveSourceBatch(objects=tuple(current_objects)))

    return tuple(batches)


def plan_archive_sources(
    object_heads: Mapping[str, ArchiveObjectHead],
    *,
    requirements: tuple[ArchiveSourceRequirement, ...],
    selection_policy: ArchiveSourceSelectionPolicy,
) -> ArchiveSourcePlan:
    """Plan coverage and batches for archive source requirements."""
    _validate_positive_optional(selection_policy.latest_count, "latest_count")

    coverage: list[ArchiveSourceCoverage] = []
    selected_objects: list[ArchiveSourceObject] = []
    for requirement in requirements:
        matched_objects = match_archive_source_objects(
            object_heads,
            archive_prefix=requirement.archive_prefix,
            glob_pattern=requirement.glob_pattern,
        )
        requirement_selection = _select_archive_source_objects(
            matched_objects,
            selection_policy=selection_policy,
        )
        coverage.append(
            ArchiveSourceCoverage(
                requirement=requirement,
                requested_count=selection_policy.latest_count,
                available_count=len(matched_objects),
                selected_objects=requirement_selection,
            )
        )
        selected_objects.extend(requirement_selection)

    deduped_objects = _dedupe_archive_source_objects(tuple(selected_objects))
    return ArchiveSourcePlan(
        selection_policy=selection_policy,
        coverage=tuple(coverage),
        batches=plan_archive_source_batches(
            deduped_objects,
            max_batch_bytes=selection_policy.max_batch_bytes,
            max_batch_files=selection_policy.max_batch_files,
        ),
    )


def _matching_archive_source_keys(
    *,
    archive_prefix: str,
    glob_pattern: str,
    object_keys: list[str],
) -> tuple[str, ...]:
    case_insensitive_keys = [key.lower() for key in object_keys]
    original_key_by_insensitive_key = {
        case_insensitive_key: original_key
        for case_insensitive_key, original_key in zip(
            case_insensitive_keys,
            object_keys,
            strict=True,
        )
    }
    matching_keys = fnmatch.filter(
        case_insensitive_keys,
        f"{archive_prefix}/{glob_pattern}",
    )
    return tuple(
        original_key_by_insensitive_key[matching_key] for matching_key in matching_keys
    )


def _normalize_object_size(object_head: ArchiveObjectHead) -> int:
    size = object_head.get("Size", 0)
    if isinstance(size, int):
        return size
    if isinstance(size, str) and size.isdecimal():
        return int(size)
    return 0


def _select_archive_source_objects(
    objects: tuple[ArchiveSourceObject, ...],
    *,
    selection_policy: ArchiveSourceSelectionPolicy,
) -> tuple[ArchiveSourceObject, ...]:
    if selection_policy.latest_count is None:
        return objects
    return objects[-selection_policy.latest_count :]


def _dedupe_archive_source_objects(
    objects: tuple[ArchiveSourceObject, ...],
) -> tuple[ArchiveSourceObject, ...]:
    object_by_key: dict[str, ArchiveSourceObject] = {}
    for object_ in objects:
        object_by_key[object_.key] = object_
    return tuple(object_by_key[key] for key in sorted(object_by_key))


def _validate_positive_optional(value: int | None, name: str) -> None:
    if value is not None and value <= 0:
        raise ValueError(f"{name} must be greater than zero")
