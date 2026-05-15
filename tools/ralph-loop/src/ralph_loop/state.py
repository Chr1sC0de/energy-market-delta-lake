from __future__ import annotations

import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .workflow import *  # noqa: F403


def utc_now_text() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def path_text(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path)


def run_configuration_payload(config: LoopConfig) -> dict[str, Any]:
    return {
        "exploratory_concurrency": config.exploratory_concurrency,
    }


def promotion_issue_metadata_log_path(
    run_dir: Path, issue_number: int, step: str
) -> Path:
    return run_dir / f"gh-issue-{issue_number}-promotion-{step}.log"


def branch_sync_worktree_path(
    *,
    worktree_container: Path,
    source_branch: str,
    target_branch: str,
) -> Path:
    return worktree_container / (
        f"agent-sync-{slugify(source_branch)}-into-{slugify(target_branch)}"
    )


class RunManifest:
    """Machine-readable recovery state for a single Ralph run."""

    def __init__(self, path: Path, data: dict[str, Any]) -> None:
        self.path = path
        self.data = data

    @classmethod
    def for_implementation(
        cls,
        *,
        run_dir: Path,
        issue: Issue,
        delivery_plan: DeliveryPlan,
        branch: str,
        worktree_path: Path,
        integration_path: Path | None,
        config: LoopConfig,
    ) -> "RunManifest":
        data: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "run_kind": "implementation",
            "status": "running",
            "stage": "created",
            "started_at": utc_now_text(),
            "updated_at": utc_now_text(),
            "repo": config.repo,
            "configuration": run_configuration_payload(config),
            "issue": {
                "number": issue.number,
                "title": issue.title,
                "url": issue.url,
            },
            "delivery_mode": delivery_plan.mode,
            "integration_target": delivery_plan.target_branch,
            "branches": {
                "issue": branch,
                "integration_target": delivery_plan.target_branch,
            },
            "paths": {
                "repo_root": str(config.repo_root),
                "run_dir": str(run_dir),
                "worktree_container": str(config.worktree_container),
                "implementation_worktree": str(worktree_path),
                "integration_worktree": path_text(integration_path),
                "branch_sync_worktree": None,
            },
            "branch_sync": {
                "status": "not_started",
                "source_branch": None,
                "target_branch": None,
                "worktree_path": None,
                "log_path": None,
                "conflicted_files": [],
                "recovery_guidance": None,
                "failure_type": None,
                "error": None,
            },
            "changed_files": [],
            "qa_results": [],
            "qa_runtime_env": {"status": "not_started"},
            "formatter_recovery": {
                "status": "not_started",
                "modified_files": [],
                "staged_files": [],
                "initial_commit_log_path": None,
                "commit_check_results": [],
                "retry_commit_log_path": None,
                "recovery_guidance": None,
                "failure_type": None,
                "error": None,
            },
            "codex_attempts": [],
            "sandboxed_issue_access": {"status": "not_started"},
            "full_access_implementation": {
                "enabled": config.allow_full_access_implementation,
                "required": False,
                "status": "not_required",
                "context_anchor_paths": [],
                "changed_files": [],
                "out_of_scope_files": [],
                "recovery_guidance": None,
            },
            "ready_issue_refresh": {
                "enabled": config.ready_issue_refresh_enabled,
                "status": "not_started",
                "candidate_issue_numbers": [],
                "candidate_issues": [],
                "log_path": None,
                "artifact_path": None,
                "mutation_results": [],
                "recovery_guidance": None,
                "failure": None,
            },
            "drain_scheduler": {
                "enabled": config.drain and config.issue is None,
                "fatal_stop": {
                    "status": "not_triggered",
                    "reason": None,
                    "message": None,
                    "log_path": None,
                    "active_issue_numbers": [],
                    "observed_at": None,
                },
            },
            "commits": {},
            "integration_commit": None,
            "pushes": {},
            "github_metadata": {"status": "not_started"},
            "failure": None,
            "events": [],
        }
        manifest = cls(run_dir / MANIFEST_NAME, data)
        manifest.record_event("created")
        return manifest

    @classmethod
    def for_promotion(
        cls,
        *,
        run_dir: Path,
        source_branch: str,
        target_branch: str,
        source_path: Path,
        promote_path: Path,
        config: LoopConfig,
    ) -> "RunManifest":
        followups_enabled = (
            not config.skip_post_promotion_review
            and not config.skip_post_promotion_followups
        )
        data: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "run_kind": "promotion",
            "status": "running",
            "stage": "created",
            "started_at": utc_now_text(),
            "updated_at": utc_now_text(),
            "repo": config.repo,
            "configuration": run_configuration_payload(config),
            "delivery_mode": GITFLOW_MODE,
            "source_branch": source_branch,
            "integration_target": target_branch,
            "branches": {
                "source": source_branch,
                "integration_target": target_branch,
            },
            "paths": {
                "repo_root": str(config.repo_root),
                "run_dir": str(run_dir),
                "worktree_container": str(config.worktree_container),
                "promotion_source_worktree": str(source_path),
                "promotion_worktree": str(promote_path),
            },
            "promotion_worktree_preflight": {
                "status": "not_started",
                "checks": [],
                "failure_type": None,
                "recovery_guidance": None,
                "error": None,
            },
            "changed_files": [],
            "qa_results": [],
            "qa_runtime_env": {"status": "not_started"},
            "commits": {},
            "source_tree": None,
            "promotion_commit_inventory": {
                "status": "not_started",
                "base_ref": None,
                "head_ref": None,
                "commits": [],
            },
            "deployment_classification": {
                "status": "not_started",
                "tier": None,
                "reason": None,
                "recommended_action": None,
                "deployable_paths": [],
                "user_code_redeploy_paths": [],
                "full_workflow_paths": [],
                "agent_workflow_paths": [],
                "non_triggering_paths": [],
            },
            "deployment_execution": {
                "status": "not_started",
                "tier": None,
                "reason": None,
                "command_path": None,
                "command": [],
                "cwd": None,
                "log_path": None,
                "exit_status": None,
                "error": None,
                "deployed_test_evidence": {
                    "status": "not_started",
                    "log_path": None,
                    "command_path": None,
                },
                "full_tier_idempotency_evidence": {
                    "status": "not_started",
                    "log_path": None,
                    "command_path": None,
                    "argument": POST_PROMOTION_DEPLOYMENT_FULL_WORKFLOW_IDEMPOTENCY_ARG,
                },
            },
            "promotion_commit": None,
            "local_branch_fast_forwards": {
                "source_branch": {
                    "branch": source_branch,
                    "status": "not_started",
                    "worktree_path": None,
                    "current_commit": None,
                    "target_commit": None,
                    "log_path": None,
                    "reason": None,
                    "recovery_command": None,
                    "error": None,
                },
                "integration_target": {
                    "branch": target_branch,
                    "status": "not_started",
                    "worktree_path": None,
                    "current_commit": None,
                    "target_commit": None,
                    "log_path": None,
                    "reason": None,
                    "recovery_command": None,
                    "error": None,
                },
            },
            "post_promotion_review": {
                "enabled": not config.skip_post_promotion_review,
                "status": (
                    "skipped_by_operator"
                    if config.skip_post_promotion_review
                    else "pending"
                ),
                "log_path": None,
                "artifact_path": None,
            },
            "post_promotion_followups": {
                "enabled": followups_enabled,
                "status": (
                    "pending"
                    if followups_enabled
                    else (
                        "skipped_review_disabled"
                        if config.skip_post_promotion_review
                        else "skipped_by_operator"
                    )
                ),
                "created": [],
                "duplicates": [],
                "validation_downgrades": [],
                "failures": [],
                "recovery_guidance": None,
            },
            "ready_issue_refresh": {
                "enabled": config.ready_issue_refresh_enabled,
                "status": "not_started",
                "candidate_issue_numbers": [],
                "candidate_issues": [],
                "log_path": None,
                "artifact_path": None,
                "mutation_results": [],
                "recovery_guidance": None,
                "failure": None,
            },
            "pushes": {},
            "github_metadata": {"status": "not_started", "issues": []},
            "failure": None,
            "events": [],
        }
        manifest = cls(run_dir / MANIFEST_NAME, data)
        manifest.record_event("created")
        return manifest

    @classmethod
    def for_exploratory_acceptance_apply(
        cls,
        *,
        run_dir: Path,
        decision_file: Path,
        source_branch: str,
        acceptance_path: Path,
        config: LoopConfig,
    ) -> "RunManifest":
        data: dict[str, Any] = {
            "schema_version": MANIFEST_SCHEMA_VERSION,
            "run_kind": "exploratory_acceptance_apply",
            "status": "running",
            "stage": "created",
            "started_at": utc_now_text(),
            "updated_at": utc_now_text(),
            "repo": config.repo,
            "configuration": run_configuration_payload(config),
            "delivery_mode": EXPLORATORY_MODE,
            "source_branch": source_branch,
            "integration_target": source_branch,
            "branches": {
                "source": source_branch,
                "integration_target": source_branch,
            },
            "paths": {
                "repo_root": str(config.repo_root),
                "run_dir": str(run_dir),
                "worktree_container": str(config.worktree_container),
                "acceptance_worktree": str(acceptance_path),
                "decision_file": str(decision_file),
            },
            "decisions": [],
            "acceptance_conflict": {
                "status": "not_started",
                "worktree_path": str(acceptance_path),
                "conflicted_files": [],
                "artifacts": {},
                "continue_command": None,
                "recovery_guidance": None,
                "failure_type": None,
                "error": None,
            },
            "changed_files": [],
            "qa_results": [],
            "qa_runtime_env": {"status": "not_started"},
            "commits": {},
            "integration_commit": None,
            "pushes": {},
            "github_metadata": {"status": "not_started", "issues": []},
            "failure": None,
            "events": [],
        }
        manifest = cls(run_dir / MANIFEST_NAME, data)
        manifest.record_event("created")
        return manifest

    def record_event(
        self,
        stage: str,
        *,
        status: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if status is not None:
            self.data["status"] = status
        self.data["stage"] = stage
        event: dict[str, Any] = {
            "timestamp": utc_now_text(),
            "stage": stage,
            "status": self.data["status"],
        }
        if details is not None:
            event["details"] = details
        events = self.data.setdefault("events", [])
        if not isinstance(events, list):
            raise RalphError("Manifest events field is not a list.")
        events.append(event)
        self._write()

    def record_changed_files(self, changed_files: list[str], *, stage: str) -> None:
        self.data["changed_files"] = list(changed_files)
        self.record_event(stage, details={"count": len(changed_files)})

    def record_deployment_classification(
        self, classification: PostPromotionDeploymentClassification
    ) -> None:
        payload = {"status": "classified", **classification.to_manifest()}
        self.data["deployment_classification"] = payload
        self.record_event(
            "deployment_classification_recorded",
            details={
                "tier": classification.tier,
                "deployable_path_count": len(classification.deployable_paths),
                "agent_workflow_path_count": len(classification.agent_workflow_paths),
            },
        )

    def record_deployment_execution(
        self,
        status: str,
        *,
        tier: str,
        reason: str | None = None,
        command_path: str | None = None,
        command: list[str] | tuple[str, ...] | None = None,
        cwd: Path | None = None,
        log_path: Path | None = None,
        exit_status: int | None = None,
        error: str | None = None,
        deployed_test_evidence: dict[str, Any] | None = None,
        full_tier_idempotency_evidence: dict[str, Any] | None = None,
    ) -> None:
        execution = self.data.setdefault("deployment_execution", {})
        if not isinstance(execution, dict):
            raise RalphError("Manifest deployment_execution field is not an object.")
        execution["status"] = status
        execution["tier"] = tier
        if reason is not None:
            execution["reason"] = reason
        if command_path is not None:
            execution["command_path"] = command_path
        if command is not None:
            execution["command"] = list(command)
        if cwd is not None:
            execution["cwd"] = str(cwd)
        if log_path is not None or "log_path" not in execution:
            execution["log_path"] = path_text(log_path)
        if exit_status is not None or "exit_status" not in execution:
            execution["exit_status"] = exit_status
        if error is not None:
            execution["error"] = error
        elif status != "failed":
            execution["error"] = None
        if deployed_test_evidence is not None:
            execution["deployed_test_evidence"] = deployed_test_evidence
        if full_tier_idempotency_evidence is not None:
            execution["full_tier_idempotency_evidence"] = full_tier_idempotency_evidence
        self.record_event(f"deployment_execution_{status}", details=dict(execution))

    def record_commit(self, name: str, sha: str) -> None:
        commits = self.data.setdefault("commits", {})
        if not isinstance(commits, dict):
            raise RalphError("Manifest commits field is not an object.")
        commits[name] = sha
        self.record_event(f"{name}_recorded", details={"commit": sha})

    def record_integration_commit(self, sha: str, *, branch: str) -> None:
        self.data["integration_commit"] = {"sha": sha, "branch": branch}
        self.record_event(
            "integration_commit_recorded", details={"commit": sha, "branch": branch}
        )

    def record_promotion_commit(self, sha: str, *, branch: str) -> None:
        self.data["promotion_commit"] = {"sha": sha, "branch": branch}
        self.record_event(
            "promotion_commit_recorded", details={"commit": sha, "branch": branch}
        )

    def record_local_branch_fast_forward(
        self,
        role: str,
        *,
        branch: str,
        status: str,
        target_commit: str,
        worktree_path: Path | None = None,
        current_commit: str | None = None,
        log_path: Path | None = None,
        reason: str | None = None,
        recovery_command: str | None = None,
        error: str | None = None,
    ) -> None:
        fast_forwards = self.data.setdefault("local_branch_fast_forwards", {})
        if not isinstance(fast_forwards, dict):
            raise RalphError(
                "Manifest local_branch_fast_forwards field is not an object."
            )
        entry = {
            "branch": branch,
            "status": status,
            "worktree_path": path_text(worktree_path),
            "current_commit": current_commit,
            "target_commit": target_commit,
            "log_path": path_text(log_path),
            "reason": reason,
            "recovery_command": recovery_command,
            "error": error,
        }
        fast_forwards[role] = entry
        self.record_event(
            f"local_branch_fast_forward_{role}_{status}",
            details=entry,
        )

    def record_post_promotion_review(
        self,
        status: str,
        *,
        log_path: Path | None = None,
        artifact_path: Path | None = None,
        reason: str | None = None,
        error: str | None = None,
    ) -> None:
        review = self.data.setdefault("post_promotion_review", {})
        if not isinstance(review, dict):
            raise RalphError("Manifest post_promotion_review field is not an object.")
        review["status"] = status
        review["log_path"] = path_text(log_path)
        if artifact_path is not None or "artifact_path" not in review:
            review["artifact_path"] = path_text(artifact_path)
        if reason is not None:
            review["reason"] = reason
        if error is not None:
            review["error"] = error
        self.record_event(f"post_promotion_review_{status}", details=dict(review))

    def record_post_promotion_followups(
        self,
        status: str,
        *,
        created: list[dict[str, Any]] | None = None,
        duplicates: list[dict[str, Any]] | None = None,
        validation_downgrades: list[dict[str, Any]] | None = None,
        failures: list[dict[str, Any]] | None = None,
        reason: str | None = None,
        recovery_guidance: str | None = None,
    ) -> None:
        followups = self.data.setdefault("post_promotion_followups", {})
        if not isinstance(followups, dict):
            raise RalphError(
                "Manifest post_promotion_followups field is not an object."
            )
        followups["status"] = status
        if created is not None:
            followups["created"] = created
        if duplicates is not None:
            followups["duplicates"] = duplicates
        if validation_downgrades is not None:
            followups["validation_downgrades"] = validation_downgrades
        if failures is not None:
            followups["failures"] = failures
        if reason is not None:
            followups["reason"] = reason
        if recovery_guidance is not None:
            followups["recovery_guidance"] = recovery_guidance
        self.record_event(f"post_promotion_followups_{status}", details=dict(followups))

    def record_source_tree(
        self, *, branch: str, revision: str, worktree_path: Path
    ) -> None:
        source_tree = {
            "branch": branch,
            "revision": revision,
            "worktree": str(worktree_path),
        }
        self.data["source_tree"] = source_tree
        self.record_event("source_tree_recorded", details=source_tree)

    def record_codex_attempt(
        self,
        attempt: int,
        *,
        status: str,
        log_path: Path,
        error: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "attempt": attempt,
            "status": status,
            "log_path": str(log_path),
        }
        if error is not None:
            entry["error"] = error
        self._upsert_list_entry("codex_attempts", "attempt", attempt, entry)
        self.record_event(
            f"codex_attempt_{attempt}_{status}",
            details={"attempt": attempt, "log_path": str(log_path)},
        )

    def record_qa(
        self,
        command: QACommand,
        *,
        log_path: Path,
        status: str,
        error: str | None = None,
        run_manifest_evidence: QARunManifestEvidence | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "name": command.name,
            "command": list(command.args),
            "cwd": str(command.cwd),
            "log_path": str(log_path),
            "status": status,
        }
        if error is not None:
            entry["error"] = error
        if run_manifest_evidence is not None:
            entry["run_manifest_evidence"] = run_manifest_evidence.to_manifest()
        self._upsert_list_entry("qa_results", "log_path", str(log_path), entry)
        self.record_event(
            f"qa_{status}",
            details={"name": command.name, "log_path": str(log_path)},
        )

    def record_qa_runtime_env(self, qa_runtime_env: QARuntimeEnv) -> None:
        metadata = {
            "status": "ready",
            "variables": qa_runtime_env.metadata,
        }
        self.data["qa_runtime_env"] = metadata
        self.record_event("qa_runtime_env_ready", details=metadata)

    def record_formatter_recovery(
        self,
        status: str,
        *,
        modified_files: list[str] | None = None,
        staged_files: list[str] | None = None,
        initial_commit_log_path: Path | None = None,
        commit_check_results: list[QAResult] | None = None,
        retry_commit_log_path: Path | None = None,
        recovery_guidance: str | None = None,
        failure_type: str | None = None,
        error: str | None = None,
    ) -> None:
        recovery = self.data.setdefault("formatter_recovery", {})
        if not isinstance(recovery, dict):
            raise RalphError("Manifest formatter_recovery field is not an object.")
        recovery["status"] = status
        if modified_files is not None:
            recovery["modified_files"] = list(modified_files)
        if staged_files is not None:
            recovery["staged_files"] = list(staged_files)
        if (
            initial_commit_log_path is not None
            or "initial_commit_log_path" not in recovery
        ):
            recovery["initial_commit_log_path"] = path_text(initial_commit_log_path)
        if commit_check_results is not None:
            recovery["commit_check_results"] = [
                {
                    "name": result.command.name,
                    "command": list(result.command.args),
                    "cwd": str(result.command.cwd),
                    "log_path": path_text(result.log_path),
                    "status": "passed",
                }
                for result in commit_check_results
            ]
        if retry_commit_log_path is not None or "retry_commit_log_path" not in recovery:
            recovery["retry_commit_log_path"] = path_text(retry_commit_log_path)
        if recovery_guidance is not None:
            recovery["recovery_guidance"] = recovery_guidance
        if failure_type is not None:
            recovery["failure_type"] = failure_type
        if error is not None:
            recovery["error"] = error
        elif status != "failed":
            recovery["error"] = None
        self.record_event(f"formatter_recovery_{status}", details=dict(recovery))

    def record_push(
        self,
        *,
        key: str,
        branch: str,
        status: str,
        commit_sha: str | None,
        log_path: Path | None,
        error: str | None = None,
    ) -> None:
        pushes = self.data.setdefault("pushes", {})
        if not isinstance(pushes, dict):
            raise RalphError("Manifest pushes field is not an object.")
        entry = {
            "branch": branch,
            "status": status,
            "commit": commit_sha,
            "log_path": path_text(log_path),
        }
        if error is not None:
            entry["error"] = error
        pushes[key] = entry
        self.record_event(
            f"push_{key}_{status}",
            details={
                "branch": branch,
                "commit": commit_sha,
                "log_path": path_text(log_path),
            },
        )

    def record_branch_sync(
        self,
        *,
        status: str,
        source_branch: str,
        target_branch: str,
        worktree_path: Path,
        log_path: Path | None = None,
        conflicted_files: list[str] | None = None,
        recovery_guidance: str | None = None,
        failure_type: str | None = None,
        error: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "status": status,
            "source_branch": source_branch,
            "target_branch": target_branch,
            "worktree_path": str(worktree_path),
            "log_path": path_text(log_path),
            "conflicted_files": list(conflicted_files or []),
            "recovery_guidance": recovery_guidance,
            "failure_type": failure_type,
            "error": error,
        }
        self.data["branch_sync"] = entry
        paths = self.data.setdefault("paths", {})
        if not isinstance(paths, dict):
            raise RalphError("Manifest paths field is not an object.")
        paths["branch_sync_worktree"] = str(worktree_path)
        self.record_event(f"branch_sync_{status}", details=entry)

    def record_promotion_worktree_preflight(
        self,
        status: str,
        *,
        checks: list[dict[str, Any]],
        failure_type: str | None = None,
        recovery_guidance: str | None = None,
        error: str | None = None,
    ) -> None:
        preflight = {
            "status": status,
            "checks": checks,
            "failure_type": failure_type,
            "recovery_guidance": recovery_guidance,
            "error": error,
        }
        self.data["promotion_worktree_preflight"] = preflight
        self.record_event(f"promotion_worktree_preflight_{status}", details=preflight)

    def record_metadata_status(
        self,
        status: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        metadata = self.data.setdefault("github_metadata", {})
        if not isinstance(metadata, dict):
            raise RalphError("Manifest github_metadata field is not an object.")
        metadata["status"] = status
        if details is not None:
            metadata.update(details)
        self.record_event(f"github_metadata_{status}", details=details)

    def record_sandboxed_issue_access(self, access: SandboxIssueAccess) -> None:
        metadata = {
            "status": "ready",
            "token_source": access.token_source,
            "wrapper_path": str(access.wrapper_path),
            "allowed_commands": [
                "gh auth status",
                *[f"gh issue {command}" for command in access.allowed_issue_commands],
            ],
            "network_access": True,
        }
        self.data["sandboxed_issue_access"] = metadata
        self.record_event("sandboxed_issue_access_ready", details=metadata)

    def record_full_access_implementation(
        self,
        status: str,
        *,
        required: bool | None = None,
        context_anchor_paths: tuple[ContextAnchorPath, ...] | None = None,
        changed_files: list[str] | None = None,
        out_of_scope_files: list[str] | None = None,
        recovery_guidance: str | None = None,
    ) -> None:
        full_access = self.data.setdefault("full_access_implementation", {})
        if not isinstance(full_access, dict):
            raise RalphError(
                "Manifest full_access_implementation field is not an object."
            )
        full_access["status"] = status
        if required is not None:
            full_access["required"] = required
        if context_anchor_paths is not None:
            full_access["context_anchor_paths"] = [
                {"path": anchor.path, "prefix": anchor.prefix}
                for anchor in context_anchor_paths
            ]
        if changed_files is not None:
            full_access["changed_files"] = list(changed_files)
        if out_of_scope_files is not None:
            full_access["out_of_scope_files"] = list(out_of_scope_files)
        if recovery_guidance is not None:
            full_access["recovery_guidance"] = recovery_guidance
        self.record_event(f"full_access_implementation_{status}", details=full_access)

    def record_ready_issue_refresh(
        self,
        status: str,
        *,
        enabled: bool | None = None,
        candidates: list[Issue] | None = None,
        log_path: Path | None = None,
        artifact_path: Path | None = None,
        error: str | None = None,
        recovery_guidance: str | None = None,
        reason: str | None = None,
    ) -> None:
        refresh = self.data.setdefault("ready_issue_refresh", {})
        if not isinstance(refresh, dict):
            raise RalphError("Manifest ready_issue_refresh field is not an object.")
        if enabled is not None:
            refresh["enabled"] = enabled
        refresh["status"] = status
        if candidates is not None:
            refresh["candidate_issue_numbers"] = [issue.number for issue in candidates]
            refresh["candidate_issues"] = [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.url,
                }
                for issue in candidates
            ]
        if log_path is not None or "log_path" not in refresh:
            refresh["log_path"] = path_text(log_path)
        if artifact_path is not None or "artifact_path" not in refresh:
            refresh["artifact_path"] = path_text(artifact_path)
        if error is not None:
            refresh["failure"] = {
                "message": error,
                "log_path": path_text(log_path),
            }
        elif status != "failed":
            refresh["failure"] = None
        if recovery_guidance is not None:
            refresh["recovery_guidance"] = recovery_guidance
        if reason is not None:
            refresh["reason"] = reason
        self.record_event(f"ready_issue_refresh_{status}", details=dict(refresh))

    def record_ready_issue_refresh_mutation(
        self,
        *,
        issue_number: int,
        status: str,
        action: str,
        issue: Issue | None = None,
        operations: dict[str, Any] | None = None,
        error: str | None = None,
        log_path: Path | None = None,
    ) -> None:
        refresh = self.data.setdefault("ready_issue_refresh", {})
        if not isinstance(refresh, dict):
            raise RalphError("Manifest ready_issue_refresh field is not an object.")
        results = refresh.setdefault("mutation_results", [])
        if not isinstance(results, list):
            raise RalphError(
                "Manifest ready_issue_refresh.mutation_results is not a list."
            )
        entry: dict[str, Any] = {
            "issue_number": issue_number,
            "status": status,
            "action": action,
            "operations": operations or {},
            "error": error,
            "log_path": path_text(log_path),
        }
        if issue is not None:
            entry["title"] = issue.title
            entry["url"] = issue.url
        replaced = False
        for index, existing in enumerate(results):
            if (
                isinstance(existing, dict)
                and existing.get("issue_number") == issue_number
            ):
                results[index] = {**existing, **entry}
                replaced = True
                break
        if not replaced:
            results.append(entry)
        self.record_event(f"ready_issue_refresh_mutation_{status}", details=entry)

    def record_drain_scheduler_fatal_stop(
        self,
        status: str,
        *,
        error: Exception,
        active_issue_numbers: list[int] | tuple[int, ...] | None = None,
    ) -> None:
        scheduler = self.data.setdefault("drain_scheduler", {})
        if not isinstance(scheduler, dict):
            raise RalphError("Manifest drain_scheduler field is not an object.")
        log_path = getattr(error, "log_path", None)
        fatal_stop = {
            "status": status,
            "reason": drain_fatal_stop_reason(error) or "fatal_error",
            "message": str(error),
            "log_path": path_text(log_path if isinstance(log_path, Path) else None),
            "active_issue_numbers": list(active_issue_numbers or []),
            "observed_at": utc_now_text(),
        }
        scheduler["fatal_stop"] = fatal_stop
        self.record_event(f"drain_scheduler_fatal_stop_{status}", details=fatal_stop)

    def record_promoted_issues(
        self,
        issues: list[tuple[Issue, str]],
        *,
        issue_warnings: list[PromotionIssueWarning] | None = None,
    ) -> None:
        metadata = self.data.setdefault("github_metadata", {})
        if not isinstance(metadata, dict):
            raise RalphError("Manifest github_metadata field is not an object.")
        verified_entries = [
            {
                "number": issue.number,
                "title": issue.title,
                "url": issue.url,
                "integrated_commit": integrated_commit,
                "metadata_status": "verified",
            }
            for issue, integrated_commit in issues
        ]
        warning_entries = [
            {
                "number": warning.issue.number,
                "title": warning.issue.title,
                "url": warning.issue.url,
                "integrated_commit": None,
                "metadata_status": warning.metadata_status,
                "warning": warning.reason,
                "recovery_action": warning.recovery_action,
            }
            for warning in issue_warnings or []
        ]
        metadata["issues"] = [*verified_entries, *warning_entries]
        metadata["status"] = (
            "verified_issues_with_warnings" if warning_entries else "verified_issues"
        )
        self.record_event(
            "github_metadata_verified_issues",
            details={"count": len(issues), "warnings": len(warning_entries)},
        )

    def record_promotion_commit_inventory(
        self,
        *,
        base_ref: str,
        head_ref: str,
        commits: list[PromotedSourceCommit],
        integrated_issues: list[tuple[Issue, str]],
    ) -> list[dict[str, Any]]:
        entries = promotion_commit_inventory_entries(
            commits,
            integrated_issues,
        )
        inventory = {
            "status": "classified",
            "base_ref": base_ref,
            "head_ref": head_ref,
            "commits": entries,
        }
        self.data["promotion_commit_inventory"] = inventory
        self.record_event(
            "promotion_commit_inventory_recorded",
            details={"count": len(commits), "base_ref": base_ref, "head_ref": head_ref},
        )
        return entries

    def record_promoted_issue_metadata(
        self,
        issue: Issue,
        *,
        integrated_commit: str,
        status: str,
        log_path: Path | None = None,
        metadata_log_key: str | None = None,
    ) -> None:
        metadata = self.data.setdefault("github_metadata", {})
        if not isinstance(metadata, dict):
            raise RalphError("Manifest github_metadata field is not an object.")
        issues = metadata.setdefault("issues", [])
        if not isinstance(issues, list):
            raise RalphError("Manifest github_metadata.issues field is not a list.")
        entry: dict[str, Any] = {
            "number": issue.number,
            "title": issue.title,
            "url": issue.url,
            "integrated_commit": integrated_commit,
            "metadata_status": status,
        }
        if log_path is not None:
            entry["log_path"] = path_text(log_path)
        if metadata_log_key is not None and log_path is not None:
            entry["metadata_log_paths"] = {metadata_log_key: path_text(log_path)}
        replaced = False
        for index, existing in enumerate(issues):
            if isinstance(existing, dict) and existing.get("number") == issue.number:
                existing_log_paths = existing.get("metadata_log_paths")
                merged_log_paths = (
                    dict(existing_log_paths)
                    if isinstance(existing_log_paths, dict)
                    else {}
                )
                entry_log_paths = entry.get("metadata_log_paths")
                if isinstance(entry_log_paths, dict):
                    merged_log_paths.update(entry_log_paths)
                updated = {**existing, **entry}
                if merged_log_paths:
                    updated["metadata_log_paths"] = merged_log_paths
                issues[index] = updated
                replaced = True
                break
        if not replaced:
            issues.append(entry)
        metadata["status"] = status
        self.record_event(
            f"github_metadata_issue_{status}",
            details={
                "issue": issue.number,
                "integrated_commit": integrated_commit,
                "log_path": path_text(log_path),
                "metadata_log_key": metadata_log_key,
            },
        )

    def record_exploratory_acceptance_decision(
        self,
        *,
        issue_number: int,
        decision: str,
        status: str,
        issue: Issue | None = None,
        branch: str | None = None,
        handoff_commit: str | None = None,
        acceptance_commit: str | None = None,
        reason: str | None = None,
        changed_files: list[str] | tuple[str, ...] | None = None,
        operations: dict[str, Any] | None = None,
        log_path: Path | None = None,
        error: str | None = None,
        recovery_guidance: str | None = None,
    ) -> None:
        decisions = self.data.setdefault("decisions", [])
        if not isinstance(decisions, list):
            raise RalphError("Manifest decisions field is not a list.")
        entry: dict[str, Any] = {
            "issue_number": issue_number,
            "decision": decision,
            "status": status,
        }
        if issue is not None:
            entry["title"] = issue.title
            entry["url"] = issue.url
        if branch is not None:
            entry["branch"] = branch
        if handoff_commit is not None:
            entry["handoff_commit"] = handoff_commit
        if acceptance_commit is not None:
            entry["acceptance_commit"] = acceptance_commit
        if reason is not None:
            entry["reason"] = reason
        if changed_files is not None:
            entry["changed_files"] = list(changed_files)
        if operations is not None:
            entry["operations"] = operations
        if log_path is not None:
            entry["log_path"] = path_text(log_path)
        if error is not None:
            entry["error"] = error
        if recovery_guidance is not None:
            entry["recovery_guidance"] = recovery_guidance

        replaced = False
        for index, existing in enumerate(decisions):
            if (
                isinstance(existing, dict)
                and existing.get("issue_number") == issue_number
            ):
                decisions[index] = {**existing, **entry}
                replaced = True
                break
        if not replaced:
            decisions.append(entry)
        self.record_event(
            f"exploratory_acceptance_{decision}_{status}",
            details=entry,
        )

    def record_exploratory_acceptance_conflict(
        self,
        *,
        worktree_path: Path,
        conflicted_files: list[str],
        current_issue: Issue,
        current_branch: str,
        current_handoff_commit: str,
        source_branch: str,
        log_path: Path | None,
        artifacts: dict[str, str],
        continue_command: str,
        recovery_guidance: str,
        error: str,
    ) -> None:
        entry: dict[str, Any] = {
            "status": EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS,
            "worktree_path": str(worktree_path),
            "source_branch": source_branch,
            "current_issue": issue_payload_for_operator(current_issue),
            "current_branch": current_branch,
            "current_handoff_commit": current_handoff_commit,
            "conflicted_files": list(conflicted_files),
            "log_path": path_text(log_path),
            "artifacts": dict(artifacts),
            "continue_command": continue_command,
            "recovery_guidance": recovery_guidance,
            "failure_type": "merge_conflict",
            "error": error,
        }
        self.data["acceptance_conflict"] = entry
        self.record_event(
            "exploratory_acceptance_conflict",
            status=EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS,
            details=entry,
        )

    def record_exploratory_acceptance_continue_refusal(
        self,
        *,
        failure_type: str,
        recovery_guidance: str,
        error: str,
        log_path: Path | None = None,
    ) -> None:
        conflict = self.data.setdefault("acceptance_conflict", {})
        if not isinstance(conflict, dict):
            raise RalphError("Manifest acceptance_conflict field is not an object.")
        conflict["last_continue_failure"] = {
            "type": failure_type,
            "message": error,
            "log_path": path_text(log_path),
            "recovery_guidance": recovery_guidance,
            "timestamp": utc_now_text(),
        }
        self.record_event(
            "exploratory_acceptance_continue_refused",
            status=EXPLORATORY_ACCEPTANCE_CONFLICT_STATUS,
            details=conflict["last_continue_failure"],
        )

    def record_failure(self, error: Exception, *, log_path: Path | None = None) -> None:
        failure = {
            "message": str(error),
            "log_path": path_text(log_path),
        }
        if isinstance(error, IssueFailure):
            if error.failure_type is not None:
                failure["type"] = error.failure_type
            if error.recovery_guidance is not None:
                failure["recovery_guidance"] = error.recovery_guidance
        if isinstance(error, FormatterRewriteRecoveryFailure):
            failure["modified_files"] = list(error.modified_files)
            failure["initial_commit_log_path"] = path_text(
                error.initial_commit_log_path
            )
            failure["commit_check_log_paths"] = [
                str(log_path) for log_path in error.commit_check_log_paths
            ]
            failure["retry_commit_log_path"] = path_text(error.retry_commit_log_path)
        if drain_fatal_stop_reason(error) is not None:
            scheduler = self.data.setdefault("drain_scheduler", {})
            if not isinstance(scheduler, dict):
                raise RalphError("Manifest drain_scheduler field is not an object.")
            if scheduler.get("enabled") is True:
                failure["fatal_stop"] = True
                scheduler["fatal_stop"] = {
                    "status": "triggered",
                    "reason": drain_fatal_stop_reason(error),
                    "message": str(error),
                    "log_path": path_text(log_path),
                    "active_issue_numbers": [],
                    "observed_at": utc_now_text(),
                }
        self.data["failure"] = failure
        self.record_event("failed", status="failed", details=failure)

    def record_success(self, stage: str = "succeeded") -> None:
        self.data["failure"] = None
        self.record_event(stage, status="succeeded")

    def _upsert_list_entry(
        self,
        field: str,
        key: str,
        value: Any,
        entry: dict[str, Any],
    ) -> None:
        items = self.data.setdefault(field, [])
        if not isinstance(items, list):
            raise RalphError(f"Manifest {field} field is not a list.")
        for index, item in enumerate(items):
            if isinstance(item, dict) and item.get(key) == value:
                items[index] = entry
                return
        items.append(entry)

    def _write(self) -> None:
        self.data["updated_at"] = utc_now_text()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_name(f"{self.path.name}.tmp")
        tmp_path.write_text(
            json.dumps(self.data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(self.path)


class OperatorRunManifest:
    """Machine-readable checkpoint state for a drain-and-Promotion Operator run."""

    def __init__(self, path: Path, data: dict[str, Any]) -> None:
        self.path = path
        self.data = data

    @classmethod
    def start(
        cls,
        *,
        run_dir: Path,
        config: LoopConfig,
        max_cycles: int,
    ) -> "OperatorRunManifest":
        path = run_dir / OPERATOR_MANIFEST_NAME
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                raise RalphError(
                    f"Operator run manifest is invalid JSON: {path}: {error}"
                ) from error
            if not isinstance(data, dict):
                raise RalphError(f"Operator run manifest is not a JSON object: {path}")
        else:
            data = {
                "schema_version": MANIFEST_SCHEMA_VERSION,
                "run_kind": "operator",
                "status": "running",
                "state": "created",
                "started_at": utc_now_text(),
                "updated_at": utc_now_text(),
                "repo": config.repo,
                "configuration": run_configuration_payload(config),
                "max_cycles": max_cycles,
                "cycle": 0,
                "current": None,
                "last_checkpoint": None,
                "checkpoints": [],
                "child_run_manifests": [],
                "queue": operator_queue_payload(
                    OperatorQueueSnapshot((), (), (), (), ())
                ),
                "rollup_artifacts": operator_rollup_artifact_payload(run_dir),
                "recovery_guidance": None,
                "failure": None,
                "events": [],
            }
        data["repo"] = config.repo
        data["configuration"] = run_configuration_payload(config)
        data["max_cycles"] = max_cycles
        paths = data.setdefault("paths", {})
        if not isinstance(paths, dict):
            paths = {}
            data["paths"] = paths
        paths["repo_root"] = str(config.repo_root)
        paths["run_dir"] = str(run_dir)
        paths["child_run_root"] = str(config.log_root)
        manifest = cls(path, data)
        manifest.record_event("started", status="running")
        return manifest

    @classmethod
    def for_detached_launch(
        cls,
        *,
        run_dir: Path,
        config: LoopConfig,
        max_cycles: int,
        command: list[str],
        stdout_log: Path,
        stderr_log: Path,
        pid: int,
    ) -> "OperatorRunManifest":
        manifest = cls.start(run_dir=run_dir, config=config, max_cycles=max_cycles)
        manifest.data["detached"] = {
            "pid": pid,
            "command": list(command),
            "stdout_log": str(stdout_log),
            "stderr_log": str(stderr_log),
        }
        manifest.record_checkpoint(
            "detached_launched",
            message="Detached Operator run launched.",
            details={
                "pid": pid,
                "stdout_log": str(stdout_log),
                "stderr_log": str(stderr_log),
            },
            status="running",
        )
        return manifest

    def record_event(
        self,
        state: str,
        *,
        status: str | None = None,
        current: dict[str, Any] | None = None,
        recovery_guidance: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        if status is not None:
            self.data["status"] = status
        self.data["state"] = state
        if current is not None:
            self.data["current"] = current
        if recovery_guidance is not None:
            self.data["recovery_guidance"] = recovery_guidance
        event: dict[str, Any] = {
            "timestamp": utc_now_text(),
            "state": state,
            "status": self.data.get("status") or "unknown",
        }
        if current is not None:
            event["current"] = current
        if details is not None:
            event["details"] = details
        events = self.data.setdefault("events", [])
        if not isinstance(events, list):
            raise RalphError("Operator manifest events field is not a list.")
        events.append(event)
        self._write()

    def record_queue(self, snapshot: OperatorQueueSnapshot) -> None:
        self.data["queue"] = operator_queue_payload(snapshot)
        self.record_event(
            "checking_queue",
            details={
                "ready": len(snapshot.ready),
                "integrated": len(snapshot.integrated),
                "reviewing": len(snapshot.reviewing),
                "running": len(snapshot.running),
                "failed": len(snapshot.failed),
            },
        )

    def record_cycle(self, cycle: int) -> None:
        self.data["cycle"] = cycle
        self.record_event("cycle_started", details={"cycle": cycle})

    def record_current_issue(self, issue: Issue) -> None:
        self.record_event(
            "running_issue",
            current={"kind": "issue", "issue": issue_payload_for_operator(issue)},
        )

    def record_current_promotion(
        self, *, source_branch: str, target_branch: str
    ) -> None:
        self.record_event(
            "running_promotion",
            current={
                "kind": "promotion",
                "source_branch": source_branch,
                "target_branch": target_branch,
            },
        )

    def record_current_deployment(
        self,
        *,
        tier: str,
        command_path: str | None,
        child_manifest_path: Path,
    ) -> None:
        self.record_event(
            "running_deployment",
            current={
                "kind": "deployment",
                "tier": tier,
                "command_path": command_path,
                "child_manifest_path": str(child_manifest_path),
            },
        )

    def clear_current(self) -> None:
        self.data["current"] = None
        self._write()

    def record_checkpoint(
        self,
        checkpoint: str,
        *,
        message: str,
        child_manifest_path: Path | None = None,
        issue: Issue | None = None,
        issue_payload: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
        status: str | None = None,
        recovery_guidance: str | None = None,
    ) -> None:
        entry: dict[str, Any] = {
            "timestamp": utc_now_text(),
            "checkpoint": checkpoint,
            "message": message,
        }
        if child_manifest_path is not None:
            entry["child_manifest_path"] = str(child_manifest_path)
            self.record_child_run(child_manifest_path)
        if issue is not None:
            entry["issue"] = issue_payload_for_operator(issue)
        elif issue_payload is not None:
            entry["issue"] = issue_payload
        if details is not None:
            entry["details"] = details
        self.data["last_checkpoint"] = entry
        checkpoints = self.data.setdefault("checkpoints", [])
        if not isinstance(checkpoints, list):
            raise RalphError("Operator manifest checkpoints field is not a list.")
        checkpoints.append(entry)
        if recovery_guidance is not None:
            self.data["recovery_guidance"] = recovery_guidance
        self.record_event(
            checkpoint,
            status=status,
            recovery_guidance=recovery_guidance,
            details=entry,
        )

    def record_child_run(self, child_manifest_path: Path) -> None:
        child_runs = self.data.setdefault("child_run_manifests", [])
        if not isinstance(child_runs, list):
            raise RalphError(
                "Operator manifest child_run_manifests field is not a list."
            )
        entry = child_manifest_entry(child_manifest_path)
        for index, existing in enumerate(child_runs):
            if isinstance(existing, dict) and existing.get("path") == str(
                child_manifest_path
            ):
                child_runs[index] = {**existing, **entry}
                self._write()
                return
        child_runs.append(entry)
        self._write()

    def record_exploratory_acceptance_review(self, review: dict[str, Any]) -> None:
        self.data["exploratory_acceptance_review"] = review
        artifacts = (
            review.get("artifacts") if isinstance(review.get("artifacts"), dict) else {}
        )
        self.record_event(
            "exploratory_acceptance_review_written",
            details={
                "markdown": artifacts.get("markdown"),
                "json": artifacts.get("json"),
                "reviewing_issues": review.get("reviewing_issue_count"),
                "downstream_ready_issues": review.get("downstream_ready_issue_count"),
            },
        )

    def record_failure(
        self,
        error: Exception,
        *,
        recovery_guidance: str,
        child_manifest_path: Path | None = None,
    ) -> None:
        self.data["failure"] = {
            "message": str(error),
            "child_manifest_path": path_text(child_manifest_path),
        }
        self.data["recovery_guidance"] = recovery_guidance
        if child_manifest_path is not None:
            self.record_child_run(child_manifest_path)
        self.record_event(
            "failed",
            status="failed",
            recovery_guidance=recovery_guidance,
            details=self.data["failure"],
        )

    def _write(self) -> None:
        self.data["updated_at"] = utc_now_text()
        self.data["rollup_artifacts"] = operator_rollup_artifact_payload(
            self.path.parent
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = self.path.with_name(f"{self.path.name}.tmp")
        tmp_path.write_text(
            json.dumps(self.data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        tmp_path.replace(self.path)
        if operator_run_has_terminal_status(self.data):
            write_operator_rollup_artifacts(self.path, self.data)


def issue_payload_for_operator(issue: Issue) -> dict[str, Any]:
    return {
        "number": issue.number,
        "title": issue.title,
        "url": issue.url,
        "labels": sorted(issue.labels),
    }


def operator_queue_payload(snapshot: OperatorQueueSnapshot) -> dict[str, Any]:
    return {
        "ready": [issue_payload_for_operator(issue) for issue in snapshot.ready],
        "integrated": [
            issue_payload_for_operator(issue) for issue in snapshot.integrated
        ],
        "reviewing": [
            issue_payload_for_operator(issue) for issue in snapshot.reviewing
        ],
        "running": [issue_payload_for_operator(issue) for issue in snapshot.running],
        "failed": [issue_payload_for_operator(issue) for issue in snapshot.failed],
    }


def operator_rollup_artifact_payload(run_dir: Path) -> dict[str, str]:
    return {
        "markdown": str(run_dir / OPERATOR_ROLLUP_MARKDOWN_NAME),
        "json": str(run_dir / OPERATOR_ROLLUP_JSON_NAME),
        "exploratory_acceptance_review_markdown": str(
            run_dir / EXPLORATORY_ACCEPTANCE_REVIEW_MARKDOWN_NAME
        ),
        "exploratory_acceptance_review_json": str(
            run_dir / EXPLORATORY_ACCEPTANCE_REVIEW_JSON_NAME
        ),
    }


def operator_run_has_terminal_status(data: dict[str, Any]) -> bool:
    return str(data.get("status") or "") in {"succeeded", "failed", "needs_review"}


def write_operator_rollup_artifacts(
    operator_manifest_path: Path,
    data: dict[str, Any],
) -> None:
    rollup = build_operator_run_rollup(operator_manifest_path, data)
    run_dir = operator_manifest_path.parent
    json_path = run_dir / OPERATOR_ROLLUP_JSON_NAME
    markdown_path = run_dir / OPERATOR_ROLLUP_MARKDOWN_NAME
    write_json_artifact(json_path, rollup)
    write_text_artifact(markdown_path, render_operator_run_rollup_markdown(rollup))


def write_json_artifact(path: Path, payload: dict[str, Any]) -> None:
    write_text_artifact(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


def write_text_artifact(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def latest_run_manifest_path_from_log(log_text: str, *, cwd: Path) -> Path | None:
    matches = list(RUN_MANIFEST_LINE_PATTERN.finditer(log_text))
    if not matches:
        return None
    raw_path = matches[-1].group("path").strip().strip("`")
    source_path = Path(raw_path).expanduser()
    if source_path.is_absolute():
        return source_path
    return cwd / source_path


def capture_qa_run_manifest_evidence(
    command: QACommand,
    *,
    log_path: Path,
    run_dir: Path,
) -> QARunManifestEvidence | None:
    if not log_path.exists():
        return None
    log_text = log_path.read_text(encoding="utf-8")
    source_path = latest_run_manifest_path_from_log(log_text, cwd=command.cwd)
    if source_path is None:
        return None

    artifact_stem = f"{log_path.stem}-run-manifest"
    if source_path.exists() and source_path.is_file():
        artifact_path = run_dir / f"{artifact_stem}.json"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.resolve() != artifact_path.resolve():
            shutil.copy2(source_path, artifact_path)
        payload = json_object_from_path(artifact_path)
        observations = (
            e2e_run_manifest_observations(payload)
            if payload is not None
            else e2e_log_observations(log_text)
        )
        return QARunManifestEvidence(
            source_path=source_path,
            artifact_path=artifact_path,
            artifact_kind="copied_run_manifest",
            observations=observations,
        )

    observations = e2e_log_observations(log_text)
    artifact_path = run_dir / f"{artifact_stem}-evidence.json"
    write_json_artifact(
        artifact_path,
        {
            "source_path": str(source_path),
            "source_available": False,
            "log_path": str(log_path),
            "artifact_kind": "log_extract",
            "observations": observations,
        },
    )
    return QARunManifestEvidence(
        source_path=source_path,
        artifact_path=artifact_path,
        artifact_kind="log_extract",
        observations=observations,
    )


def json_object_from_path(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def e2e_run_manifest_observations(payload: dict[str, Any]) -> dict[str, Any]:
    observations: dict[str, Any] = {}
    options = mapping_value(payload.get("options"))
    source_definitions = mapping_value(payload.get("source_definitions"))
    dataflow = mapping_value(payload.get("dataflow"))
    scenario_evidence = mapping_value(
        dataflow.get("scenario_evidence") if dataflow is not None else None
    )
    telemetry = mapping_value(payload.get("telemetry"))
    dagster_dataflow = mapping_value(
        telemetry.get("dagster_dataflow") if telemetry is not None else None
    )
    target_progress = mapping_value(
        dagster_dataflow.get("final_target_progress")
        if dagster_dataflow is not None
        else None
    )
    run_status_counts = mapping_value(
        dagster_dataflow.get("final_run_status_counts")
        if dagster_dataflow is not None
        else None
    )
    budget = mapping_value(payload.get("budget"))
    budget_observations = mapping_value(
        budget.get("observations") if budget is not None else None
    )

    set_observation(observations, "status", scalar_value(payload.get("status")))
    set_observation(
        observations,
        "scenario",
        first_scalar(
            options.get("scenario") if options is not None else None,
            scenario_evidence.get("scenario")
            if scenario_evidence is not None
            else None,
            budget.get("scenario") if budget is not None else None,
        ),
    )
    set_observation(
        observations,
        "launch_mode",
        first_scalar(
            options.get("launch_mode") if options is not None else None,
            scenario_evidence.get("launch_mode")
            if scenario_evidence is not None
            else None,
        ),
    )
    set_observation(
        observations,
        "target_group",
        scalar_value(
            scenario_evidence.get("target_group")
            if scenario_evidence is not None
            else None
        ),
    )

    for key in (
        "total_gate_duration_seconds",
        "peak_active_run_count",
        "peak_queued_run_count",
        "successful_run_count",
        "total_run_count",
        "materialized_target_asset_count",
        "target_asset_count",
        "target_asset_check_count",
        "missing_target_asset_count",
        "failed_target_asset_count",
        "missing_asset_check_count",
        "failed_asset_check_count",
    ):
        set_observation(
            observations,
            key,
            first_scalar(
                budget_observations.get(key)
                if budget_observations is not None
                else None,
                target_progress.get(key) if target_progress is not None else None,
                dagster_dataflow.get(key) if dagster_dataflow is not None else None,
                dagster_dataflow.get("final_missing_asset_check_count")
                if key == "missing_asset_check_count" and dagster_dataflow is not None
                else None,
                dagster_dataflow.get("final_failed_asset_check_count")
                if key == "failed_asset_check_count" and dagster_dataflow is not None
                else None,
                telemetry.get(key) if telemetry is not None else None,
                scenario_evidence.get(key) if scenario_evidence is not None else None,
                source_definitions.get("asset_check_count")
                if key == "target_asset_check_count" and source_definitions is not None
                else None,
            ),
        )

    if "successful_run_count" not in observations and run_status_counts is not None:
        set_observation(
            observations,
            "successful_run_count",
            scalar_value(run_status_counts.get("SUCCESS")),
        )
    if "total_run_count" not in observations and run_status_counts is not None:
        total_runs = sum(
            value for value in run_status_counts.values() if isinstance(value, int)
        )
        set_observation(observations, "total_run_count", total_runs)
    return observations


def e2e_log_observations(log_text: str) -> dict[str, Any]:
    observations: dict[str, Any] = {}
    line_extracts = {
        "total_gate_duration": r"^\s*-\s*total gate duration:\s*(?P<value>.+?)\s*$",
        "peak_active_queued": r"^\s*-\s*peak active/queued runs:\s*(?P<value>.+?)\s*$",
        "successful_runs": r"^\s*-\s*final successful runs:\s*(?P<value>.+?)\s*$",
        "total_runs": r"^\s*-\s*total Dagster runs:\s*(?P<value>.+?)\s*$",
        "target_progress": r"^\s*-\s*target progress:\s*(?P<value>.+?)\s*$",
        "target_asset_checks": r"^\s*-\s*target asset checks:\s*(?P<value>.+?)\s*$",
        "asset_check_status": r"^\s*-\s*final asset-check status:\s*(?P<value>.+?)\s*$",
    }
    for key, pattern in line_extracts.items():
        match = re.search(pattern, log_text, flags=re.MULTILINE)
        if match is not None:
            observations[key] = match.group("value").strip()
    return observations


def mapping_value(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    return None


def scalar_value(value: Any) -> str | int | float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, str | int | float):
        return value
    return None


def first_scalar(*values: Any) -> str | int | float | None:
    for value in values:
        scalar = scalar_value(value)
        if scalar is not None:
            return scalar
    return None


def set_observation(
    observations: dict[str, Any],
    key: str,
    value: str | int | float | None,
) -> None:
    if value is not None:
        observations[key] = value


def build_operator_run_rollup(
    operator_manifest_path: Path,
    data: dict[str, Any],
) -> dict[str, Any]:
    child_sources = operator_child_manifest_sources(data)
    issue_entries = operator_rollup_issue_entries(data, child_sources)
    promotion_entries = operator_rollup_promotion_entries(data, child_sources)
    local_integrations = operator_rollup_local_integrations(issue_entries)
    deployment_executions = [
        deployment
        for promotion in promotion_entries
        if isinstance(promotion.get("deployment_execution"), dict)
        for deployment in [operator_rollup_deployment_entry(promotion)]
        if deployment is not None
    ]
    qa_surfaces = [
        surface
        for source in child_sources
        for surface in operator_rollup_qa_surfaces(source)
    ]
    post_promotion_followups = [
        operator_rollup_followup_entry(promotion)
        for promotion in promotion_entries
        if promotion.get("post_promotion_followups") is not None
    ]
    manual_recoveries = [
        recovery
        for promotion in promotion_entries
        for recovery in promotion.get("manual_recoveries", [])
        if isinstance(recovery, dict)
    ]
    final_queue = operator_rollup_final_queue(data)
    stop_reason = operator_rollup_stop_reason(data)
    failed_attempts = [
        *issue_entries["failed"],
        *[
            promotion
            for promotion in promotion_entries
            if promotion.get("status") not in {"succeeded"}
        ],
    ]

    return {
        "schema_version": OPERATOR_ROLLUP_SCHEMA_VERSION,
        "run_kind": "operator_rollup",
        "operator_run": {
            "repo": data.get("repo"),
            "status": data.get("status"),
            "state": data.get("state"),
            "started_at": data.get("started_at"),
            "updated_at": data.get("updated_at"),
            "cycle": data.get("cycle"),
            "max_cycles": data.get("max_cycles"),
            "run_dir": str(operator_manifest_path.parent),
            "manifest_path": str(operator_manifest_path),
            "recovery_guidance": data.get("recovery_guidance"),
            "failure": data.get("failure"),
        },
        "artifacts": {
            "operator_manifest": str(operator_manifest_path),
            "markdown_rollup": str(
                operator_manifest_path.parent / OPERATOR_ROLLUP_MARKDOWN_NAME
            ),
            "json_rollup": str(
                operator_manifest_path.parent / OPERATOR_ROLLUP_JSON_NAME
            ),
            "child_run_root": operator_child_run_root(data),
        },
        "summary": {
            "succeeded_issues": len(issue_entries["succeeded"]),
            "failed_issues": len(issue_entries["failed"]),
            "failed_attempts": len(failed_attempts),
            "local_integrations": len(local_integrations),
            "promotions": len(promotion_entries),
            "deployment_executions": len(deployment_executions),
            "manual_recoveries": len(manual_recoveries),
            "qa_surfaces": len(qa_surfaces),
            "post_promotion_followups": len(post_promotion_followups),
            "final_queue_clean": final_queue["clean"],
        },
        "issues": issue_entries,
        "failed_attempts": failed_attempts,
        "manual_recoveries": manual_recoveries,
        "local_integrations": local_integrations,
        "promotions": promotion_entries,
        "deployment_executions": deployment_executions,
        "qa_surfaces": qa_surfaces,
        "post_promotion_followups": post_promotion_followups,
        "exploratory_acceptance_review": data.get("exploratory_acceptance_review"),
        "final_queue": final_queue,
        "stop_reason": stop_reason,
    }


def operator_child_run_root(data: dict[str, Any]) -> str | None:
    paths = data.get("paths")
    if not isinstance(paths, dict):
        return None
    child_run_root = paths.get("child_run_root")
    return str(child_run_root) if child_run_root else None


def operator_child_manifest_sources(data: dict[str, Any]) -> list[dict[str, Any]]:
    child_runs = data.get("child_run_manifests")
    if not isinstance(child_runs, list):
        return []

    sources: list[dict[str, Any]] = []
    for child in child_runs:
        if not isinstance(child, dict):
            continue
        manifest_path = str(child.get("path") or "")
        child_data, read_status, error = read_rollup_child_manifest(manifest_path)
        kind = (
            child_data.get("run_kind") if child_data is not None else child.get("kind")
        )
        status = (
            child_data.get("status") if child_data is not None else child.get("status")
        )
        stage = (
            child_data.get("stage") if child_data is not None else child.get("stage")
        )
        source: dict[str, Any] = {
            "manifest_path": manifest_path,
            "manifest_read_status": read_status,
            "manifest_error": error,
            "child_entry": child,
            "data": child_data,
            "kind": str(kind or "unknown"),
            "status": str(status or "unknown"),
            "stage": str(stage or "unknown"),
        }
        issue = operator_issue_payload_from_values(
            child.get("issue"),
            child_data.get("issue") if child_data is not None else None,
        )
        if issue is not None:
            source["issue"] = issue
        sources.append(source)
    return sources


def read_rollup_child_manifest(
    manifest_path: str,
) -> tuple[dict[str, Any] | None, str, str | None]:
    if manifest_path == "":
        return None, "missing_path", None
    path = Path(manifest_path)
    if not path.exists():
        return None, "missing", None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return None, "invalid", str(error)
    if not isinstance(data, dict):
        return None, "invalid", "manifest root is not an object"
    return data, "loaded", None


def operator_issue_payload_from_values(*values: Any) -> dict[str, Any] | None:
    for value in values:
        if not isinstance(value, dict):
            continue
        number = value.get("number")
        if number is None:
            continue
        return {
            "number": number,
            "title": value.get("title"),
            "url": value.get("url"),
        }
    return None


def operator_rollup_issue_entries(
    data: dict[str, Any],
    child_sources: list[dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    child_by_path = {
        str(source.get("manifest_path") or ""): source
        for source in child_sources
        if source.get("kind") == "implementation"
    }
    entries: dict[str, list[dict[str, Any]]] = {"succeeded": [], "failed": []}
    seen_paths: set[str] = set()
    checkpoints = data.get("checkpoints")
    if isinstance(checkpoints, list):
        for checkpoint in checkpoints:
            if not isinstance(checkpoint, dict):
                continue
            checkpoint_name = str(checkpoint.get("checkpoint") or "")
            if checkpoint_name not in {"issue_succeeded", "issue_failed"}:
                continue
            manifest_path = str(checkpoint.get("child_manifest_path") or "")
            child_source = child_by_path.get(manifest_path)
            issue = operator_issue_payload_from_values(
                checkpoint.get("issue"),
                child_source.get("issue") if child_source is not None else None,
            )
            entry = operator_issue_rollup_entry(
                issue=issue,
                child_source=child_source,
                checkpoint=checkpoint,
            )
            status_key = (
                "succeeded" if checkpoint_name == "issue_succeeded" else "failed"
            )
            entries[status_key].append(entry)
            if manifest_path:
                seen_paths.add(manifest_path)

    for source in child_sources:
        if source.get("kind") != "implementation":
            continue
        manifest_path = str(source.get("manifest_path") or "")
        if manifest_path in seen_paths:
            continue
        entry = operator_issue_rollup_entry(
            issue=source.get("issue")
            if isinstance(source.get("issue"), dict)
            else None,
            child_source=source,
            checkpoint=None,
        )
        status_key = "succeeded" if source.get("status") == "succeeded" else "failed"
        entries[status_key].append(entry)
    return entries


def operator_issue_rollup_entry(
    *,
    issue: dict[str, Any] | None,
    child_source: dict[str, Any] | None,
    checkpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    child_data = child_source.get("data") if child_source is not None else None
    child_data = child_data if isinstance(child_data, dict) else {}
    manifest_path = (
        str(child_source.get("manifest_path") or "") if child_source is not None else ""
    )
    entry: dict[str, Any] = {
        "issue": issue,
        "status": (
            str(child_source.get("status") or "unknown")
            if child_source is not None
            else "unknown"
        ),
        "checkpoint": checkpoint.get("checkpoint") if checkpoint is not None else None,
        "message": checkpoint.get("message") if checkpoint is not None else None,
        "manifest_path": manifest_path,
        "manifest_read_status": (
            child_source.get("manifest_read_status")
            if child_source is not None
            else None
        ),
        "delivery_mode": child_data.get("delivery_mode"),
        "integration_target": child_data.get("integration_target"),
        "local_integration_commit": normalized_commit_payload(
            child_data.get("integration_commit")
        ),
        "qa": operator_rollup_qa_summary(child_data),
        "ready_issue_refresh_status": operator_rollup_nested_status(
            child_data, "ready_issue_refresh"
        ),
        "failure": child_data.get("failure"),
    }
    if child_source is not None and child_source.get("manifest_error") is not None:
        entry["manifest_error"] = child_source.get("manifest_error")
    return entry


def normalized_commit_payload(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    sha = value.get("sha")
    if not sha:
        return None
    return {"sha": sha, "branch": value.get("branch")}


def operator_rollup_nested_status(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if not isinstance(value, dict):
        return None
    status = value.get("status")
    return str(status) if status is not None else None


def operator_rollup_qa_summary(data: dict[str, Any]) -> dict[str, Any]:
    results = data.get("qa_results")
    if not isinstance(results, list) or not results:
        return {"status": "not_started", "surfaces": [], "counts": {}}
    surfaces = [
        operator_rollup_qa_result(result)
        for result in results
        if isinstance(result, dict)
    ]
    counts: dict[str, int] = {}
    for surface in surfaces:
        status = str(surface.get("status") or "unknown")
        counts[status] = counts.get(status, 0) + 1
    if counts.get("failed", 0) > 0:
        status = "failed"
    elif counts.get("running", 0) > 0:
        status = "running"
    elif surfaces and counts.get("passed", 0) == len(surfaces):
        status = "passed"
    else:
        status = "mixed"
    return {"status": status, "surfaces": surfaces, "counts": counts}


def operator_rollup_qa_result(result: dict[str, Any]) -> dict[str, Any]:
    command_value = result.get("command")
    command = (
        [str(part) for part in command_value] if isinstance(command_value, list) else []
    )
    payload = {
        "name": result.get("name") or format_command(command),
        "status": result.get("status") or "unknown",
        "command": command,
        "command_text": format_command(command),
        "cwd": result.get("cwd"),
        "log_path": result.get("log_path"),
    }
    evidence = result.get("run_manifest_evidence")
    if isinstance(evidence, dict):
        payload["run_manifest_evidence"] = evidence
    return payload


def operator_rollup_qa_surfaces(source: dict[str, Any]) -> list[dict[str, Any]]:
    data = source.get("data")
    if not isinstance(data, dict):
        return []
    qa = operator_rollup_qa_summary(data)
    surfaces = qa.get("surfaces")
    if not isinstance(surfaces, list):
        return []
    context = {
        "run_kind": source.get("kind"),
        "status": source.get("status"),
        "manifest_path": source.get("manifest_path"),
    }
    if isinstance(source.get("issue"), dict):
        context["issue"] = source["issue"]
    promotion_commit = normalized_commit_payload(data.get("promotion_commit"))
    if promotion_commit is not None:
        context["promotion_commit"] = promotion_commit
    return [{**context, **surface} for surface in surfaces if isinstance(surface, dict)]


def operator_rollup_local_integrations(
    issue_entries: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    integrations: list[dict[str, Any]] = []
    for entry in [*issue_entries["succeeded"], *issue_entries["failed"]]:
        commit = entry.get("local_integration_commit")
        if not isinstance(commit, dict):
            continue
        if entry.get("delivery_mode") == EXPLORATORY_MODE:
            continue
        integrations.append(
            {
                "issue": entry.get("issue"),
                "status": entry.get("status"),
                "delivery_mode": entry.get("delivery_mode"),
                "integration_target": entry.get("integration_target"),
                "commit": commit,
                "manifest_path": entry.get("manifest_path"),
            }
        )
    return integrations


def operator_rollup_promotion_entries(
    data: dict[str, Any],
    child_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    child_by_path = {
        str(source.get("manifest_path") or ""): source
        for source in child_sources
        if source.get("kind") == "promotion"
    }
    entries: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    checkpoints = data.get("checkpoints")
    if isinstance(checkpoints, list):
        for checkpoint in checkpoints:
            if not isinstance(checkpoint, dict):
                continue
            checkpoint_name = str(checkpoint.get("checkpoint") or "")
            if checkpoint_name not in {"promotion_succeeded", "promotion_failed"}:
                continue
            manifest_path = str(checkpoint.get("child_manifest_path") or "")
            source = child_by_path.get(manifest_path)
            entries.append(
                operator_promotion_rollup_entry(source, checkpoint=checkpoint)
            )
            if manifest_path:
                seen_paths.add(manifest_path)

    for source in child_sources:
        if source.get("kind") != "promotion":
            continue
        manifest_path = str(source.get("manifest_path") or "")
        if manifest_path in seen_paths:
            continue
        entries.append(operator_promotion_rollup_entry(source, checkpoint=None))
    return entries


def operator_promotion_rollup_entry(
    source: dict[str, Any] | None,
    *,
    checkpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    child_data = source.get("data") if source is not None else None
    child_data = child_data if isinstance(child_data, dict) else {}
    manifest_path = str(source.get("manifest_path") or "") if source is not None else ""
    followups = child_data.get("post_promotion_followups")
    followups = followups if isinstance(followups, dict) else None
    deployment_execution = child_data.get("deployment_execution")
    deployment_execution = (
        deployment_execution if isinstance(deployment_execution, dict) else None
    )
    review = child_data.get("post_promotion_review")
    review = review if isinstance(review, dict) else None
    metadata = child_data.get("github_metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    inventory = child_data.get("promotion_commit_inventory")
    inventory = inventory if isinstance(inventory, dict) else {}
    changed_files = child_data.get("changed_files")
    changed_files = changed_files if isinstance(changed_files, list) else []
    issues = metadata.get("issues")
    issues = issues if isinstance(issues, list) else []
    manual_recoveries = operator_rollup_manual_recoveries(issues, manifest_path)
    return {
        "status": (
            str(source.get("status") or "unknown") if source is not None else "unknown"
        ),
        "checkpoint": checkpoint.get("checkpoint") if checkpoint is not None else None,
        "message": checkpoint.get("message") if checkpoint is not None else None,
        "manifest_path": manifest_path,
        "manifest_read_status": (
            source.get("manifest_read_status") if source is not None else None
        ),
        "source_branch": child_data.get("source_branch"),
        "target_branch": child_data.get("integration_target"),
        "promotion_commit": normalized_commit_payload(
            child_data.get("promotion_commit")
        ),
        "qa": operator_rollup_qa_summary(child_data),
        "changed_files_count": len(changed_files),
        "verified_issues": [
            operator_rollup_metadata_issue(issue)
            for issue in issues
            if isinstance(issue, dict) and issue.get("integrated_commit")
        ],
        "manual_recoveries": manual_recoveries,
        "unverified_commits": operator_rollup_unverified_commits(inventory),
        "post_promotion_review": review,
        "post_promotion_followups": followups,
        "deployment_execution": deployment_execution,
        "failure": child_data.get("failure"),
    }


def operator_rollup_metadata_issue(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "number": issue.get("number"),
        "title": issue.get("title"),
        "url": issue.get("url"),
        "integrated_commit": issue.get("integrated_commit"),
        "metadata_status": issue.get("metadata_status"),
    }


def operator_rollup_manual_recoveries(
    issues: list[Any],
    manifest_path: str,
) -> list[dict[str, Any]]:
    recoveries: list[dict[str, Any]] = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        metadata_status = str(issue.get("metadata_status") or "")
        warning = str(issue.get("warning") or "")
        recovery_action = str(issue.get("recovery_action") or "")
        if (
            "manual" not in metadata_status
            and "manual" not in warning.lower()
            and "manual" not in recovery_action.lower()
        ):
            continue
        recoveries.append(
            {
                "issue": operator_rollup_metadata_issue(issue),
                "metadata_status": metadata_status,
                "warning": warning or None,
                "recovery_action": recovery_action or None,
                "manifest_path": manifest_path,
            }
        )
    return recoveries


def operator_rollup_unverified_commits(
    inventory: dict[str, Any],
) -> list[dict[str, Any]]:
    commits = inventory.get("commits")
    if not isinstance(commits, list):
        return []
    return [
        {
            "sha": commit.get("sha"),
            "subject": commit.get("subject"),
            "classification": commit.get("classification"),
        }
        for commit in commits
        if isinstance(commit, dict)
        and commit.get("classification") == "unverified_promotion_commit"
    ]


def operator_rollup_followup_entry(promotion: dict[str, Any]) -> dict[str, Any]:
    followups = promotion.get("post_promotion_followups")
    followups = followups if isinstance(followups, dict) else {}
    return {
        "status": followups.get("status"),
        "enabled": followups.get("enabled"),
        "created": followups.get("created")
        if isinstance(followups.get("created"), list)
        else [],
        "duplicates": (
            followups.get("duplicates")
            if isinstance(followups.get("duplicates"), list)
            else []
        ),
        "validation_downgrades": (
            followups.get("validation_downgrades")
            if isinstance(followups.get("validation_downgrades"), list)
            else []
        ),
        "failures": (
            followups.get("failures")
            if isinstance(followups.get("failures"), list)
            else []
        ),
        "recovery_guidance": followups.get("recovery_guidance"),
        "manifest_path": promotion.get("manifest_path"),
        "review_artifact_path": (
            promotion.get("post_promotion_review", {}).get("artifact_path")
            if isinstance(promotion.get("post_promotion_review"), dict)
            else None
        ),
    }


def operator_rollup_deployment_entry(
    promotion: dict[str, Any],
) -> dict[str, Any] | None:
    execution = promotion.get("deployment_execution")
    if not isinstance(execution, dict):
        return None
    status = str(execution.get("status") or "")
    if status in {"", "not_started"}:
        return None
    return {
        "status": status,
        "tier": execution.get("tier"),
        "reason": execution.get("reason"),
        "command_path": execution.get("command_path"),
        "command": (
            execution.get("command")
            if isinstance(execution.get("command"), list)
            else []
        ),
        "cwd": execution.get("cwd"),
        "log_path": execution.get("log_path"),
        "exit_status": execution.get("exit_status"),
        "deployed_test_evidence": execution.get("deployed_test_evidence"),
        "full_tier_idempotency_evidence": execution.get(
            "full_tier_idempotency_evidence"
        ),
        "error": execution.get("error"),
        "manifest_path": promotion.get("manifest_path"),
    }


def operator_rollup_final_queue(data: dict[str, Any]) -> dict[str, Any]:
    queue = data.get("queue")
    queue = queue if isinstance(queue, dict) else {}
    counts = {
        key: len(queue.get(key)) if isinstance(queue.get(key), list) else 0
        for key in ("ready", "integrated", "reviewing", "running", "failed")
    }
    clean = all(count == 0 for count in counts.values())
    return {
        "clean": clean,
        "counts": counts,
        "issues": {
            key: queue.get(key) if isinstance(queue.get(key), list) else []
            for key in ("ready", "integrated", "reviewing", "running", "failed")
        },
    }


def operator_rollup_stop_reason(data: dict[str, Any]) -> dict[str, Any] | None:
    last_checkpoint = data.get("last_checkpoint")
    last_checkpoint = last_checkpoint if isinstance(last_checkpoint, dict) else {}
    checkpoint_name = str(last_checkpoint.get("checkpoint") or "")
    failure = data.get("failure")
    status = str(data.get("status") or "")
    if status == "succeeded" and checkpoint_name == "queue_clean":
        return None
    if checkpoint_name == "" and not isinstance(failure, dict):
        return None
    return {
        "checkpoint": checkpoint_name or None,
        "message": last_checkpoint.get("message"),
        "recovery_guidance": data.get("recovery_guidance"),
        "failure": failure if isinstance(failure, dict) else None,
        "stopped_by_guard": checkpoint_name == "stopped_by_guard",
    }


def render_operator_run_rollup_markdown(rollup: dict[str, Any]) -> str:
    operator_run = rollup["operator_run"]
    summary = rollup["summary"]
    lines = [
        "# Ralph Operator Run Rollup",
        "",
        f"- Status: `{operator_run.get('status')}` / `{operator_run.get('state')}`",
        f"- Run directory: `{operator_run.get('run_dir')}`",
        f"- Cycle: `{operator_run.get('cycle')}` / `{operator_run.get('max_cycles')}`",
        f"- Issues: {summary['succeeded_issues']} succeeded, {summary['failed_issues']} failed",
        f"- Promotions: {summary['promotions']}",
        f"- Final queue clean: {'yes' if summary['final_queue_clean'] else 'no'}",
        "",
        "## Issues",
        "",
        *operator_rollup_issue_markdown_lines(
            "Succeeded", rollup["issues"]["succeeded"]
        ),
        "",
        *operator_rollup_issue_markdown_lines("Failed", rollup["issues"]["failed"]),
        "",
        "## Local Integration",
        "",
        *operator_rollup_local_integration_markdown_lines(rollup["local_integrations"]),
        "",
        "## Promotion",
        "",
        *operator_rollup_promotion_markdown_lines(rollup["promotions"]),
        "",
        "## Deployment",
        "",
        *operator_rollup_deployment_markdown_lines(rollup["deployment_executions"]),
        "",
        "## QA Surfaces",
        "",
        *operator_rollup_qa_markdown_lines(rollup["qa_surfaces"]),
        "",
        "## Exploratory Acceptance Review",
        "",
        *operator_rollup_exploratory_acceptance_review_markdown_lines(
            rollup.get("exploratory_acceptance_review")
        ),
        "",
        "## Final Queue",
        "",
        *operator_rollup_final_queue_markdown_lines(rollup["final_queue"]),
        "",
        "## Stop Or Failure",
        "",
        *operator_rollup_stop_markdown_lines(rollup.get("stop_reason")),
        "",
    ]
    return "\n".join(lines)


def operator_rollup_issue_markdown_lines(
    heading: str,
    entries: list[dict[str, Any]],
) -> list[str]:
    lines = [f"### {heading}"]
    if not entries:
        return [*lines, "- None"]
    for entry in entries:
        issue = entry.get("issue") if isinstance(entry.get("issue"), dict) else {}
        commit = entry.get("local_integration_commit")
        commit_text = ""
        if isinstance(commit, dict) and commit.get("sha"):
            commit_text = (
                f"; Local integration `{commit['sha']}` to `{commit.get('branch')}`"
            )
        lines.append(
            "- "
            + operator_issue_title(issue)
            + f" - `{entry.get('status')}`"
            + commit_text
            + f"; QA `{entry.get('qa', {}).get('status')}`"
            + f"; manifest {markdown_path_link(entry.get('manifest_path'))}"
        )
    return lines


def operator_rollup_local_integration_markdown_lines(
    entries: list[dict[str, Any]],
) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        commit = entry.get("commit") if isinstance(entry.get("commit"), dict) else {}
        issue = entry.get("issue") if isinstance(entry.get("issue"), dict) else {}
        lines.append(
            "- "
            + operator_issue_title(issue)
            + f" - `{commit.get('sha')}` to `{commit.get('branch')}`"
            + f"; manifest {markdown_path_link(entry.get('manifest_path'))}"
        )
    return lines


def operator_rollup_promotion_markdown_lines(
    entries: list[dict[str, Any]],
) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        commit = entry.get("promotion_commit")
        commit_text = commit.get("sha") if isinstance(commit, dict) else "none"
        followups = entry.get("post_promotion_followups")
        followups = followups if isinstance(followups, dict) else {}
        created = (
            followups.get("created")
            if isinstance(followups.get("created"), list)
            else []
        )
        failures = (
            followups.get("failures")
            if isinstance(followups.get("failures"), list)
            else []
        )
        lines.append(
            "- "
            + f"`{entry.get('source_branch')}` -> `{entry.get('target_branch')}`"
            + f" - `{entry.get('status')}`; Promotion commit `{commit_text}`"
            + f"; QA `{entry.get('qa', {}).get('status')}`"
            + f"; Deployment `{operator_rollup_nested_status(entry, 'deployment_execution') or 'not_started'}`"
            + f"; Post-promotion follow-ups `{followups.get('status')}` "
            + f"(created={len(created)}, failures={len(failures)})"
            + f"; manifest {markdown_path_link(entry.get('manifest_path'))}"
        )
        for recovery in entry.get("manual_recoveries", []):
            if not isinstance(recovery, dict):
                continue
            issue = (
                recovery.get("issue") if isinstance(recovery.get("issue"), dict) else {}
            )
            lines.append(
                "  - Manual recovery: "
                + operator_issue_title(issue)
                + f" - `{recovery.get('metadata_status')}`"
            )
    return lines


def operator_rollup_deployment_markdown_lines(
    entries: list[dict[str, Any]],
) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        command_path = entry.get("command_path") or "none"
        log_path = markdown_path_link(entry.get("log_path"))
        lines.append(
            "- "
            + f"`{entry.get('tier')}` - `{entry.get('status')}`"
            + f"; command `{command_path}`"
            + f"; exit `{entry.get('exit_status')}`"
            + f"; log {log_path}"
        )
    return lines


def operator_rollup_qa_markdown_lines(entries: list[dict[str, Any]]) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        context = str(entry.get("run_kind") or "unknown")
        issue = entry.get("issue")
        if isinstance(issue, dict) and issue.get("number") is not None:
            context = f"{context} #{issue.get('number')}"
        lines.append(
            f"- {context}: `{entry.get('name')}` `{entry.get('status')}`; "
            f"manifest {markdown_path_link(entry.get('manifest_path'))}"
        )
    return lines


def operator_rollup_exploratory_acceptance_review_markdown_lines(
    value: Any,
) -> list[str]:
    if not isinstance(value, dict):
        return ["- None"]
    artifacts = (
        value.get("artifacts") if isinstance(value.get("artifacts"), dict) else {}
    )
    return [
        f"- Status: `{value.get('status') or 'unknown'}`",
        f"- Reviewing issues: {value.get('reviewing_issue_count') or 0}",
        f"- Downstream ready issues: {value.get('downstream_ready_issue_count') or 0}",
        f"- Markdown: {markdown_artifact_link(artifacts.get('markdown'), 'review markdown')}",
        f"- JSON: {markdown_artifact_link(artifacts.get('json'), 'review json')}",
    ]


def operator_rollup_final_queue_markdown_lines(queue: dict[str, Any]) -> list[str]:
    counts = queue.get("counts") if isinstance(queue.get("counts"), dict) else {}
    return [
        f"- ready={counts.get('ready', 0)}",
        f"- integrated={counts.get('integrated', 0)}",
        f"- reviewing={counts.get('reviewing', 0)}",
        f"- running={counts.get('running', 0)}",
        f"- failed={counts.get('failed', 0)}",
        f"- clean={'yes' if queue.get('clean') else 'no'}",
    ]


def operator_rollup_stop_markdown_lines(stop_reason: Any) -> list[str]:
    if not isinstance(stop_reason, dict):
        return ["- None"]
    lines = [
        f"- Checkpoint: `{stop_reason.get('checkpoint')}`",
        f"- Message: {stop_reason.get('message')}",
    ]
    guidance = stop_reason.get("recovery_guidance")
    if guidance:
        lines.append(f"- Recovery guidance: {guidance}")
    failure = stop_reason.get("failure")
    if isinstance(failure, dict) and failure.get("message"):
        lines.append(f"- Failure: {failure.get('message')}")
    return lines


def operator_issue_title(issue: dict[str, Any]) -> str:
    number = issue.get("number")
    title = str(issue.get("title") or "")
    if number is None:
        return title or "unknown issue"
    return f"#{number} {title}".strip()


def markdown_path_link(value: Any) -> str:
    path = str(value or "")
    if path == "":
        return "`missing`"
    return f"[`ralph-run.json`](<{path}>)"


def markdown_artifact_link(value: Any, label: str) -> str:
    path = str(value or "")
    if path == "":
        return "`missing`"
    return f"[`{label}`](<{path}>)"


def child_manifest_entry(child_manifest_path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": str(child_manifest_path)}
    if not child_manifest_path.exists():
        entry["status"] = "missing"
        return entry
    try:
        data = json.loads(child_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        entry["status"] = "invalid"
        entry["error"] = str(error)
        return entry
    if not isinstance(data, dict):
        entry["status"] = "invalid"
        entry["error"] = "manifest root is not an object"
        return entry
    entry["kind"] = str(data.get("run_kind") or "unknown")
    entry["status"] = str(data.get("status") or "unknown")
    entry["stage"] = str(data.get("stage") or "unknown")
    issue = data.get("issue")
    if isinstance(issue, dict):
        entry["issue"] = {
            "number": issue.get("number"),
            "title": issue.get("title"),
            "url": issue.get("url"),
        }
    if isinstance(data.get("promotion_commit"), dict):
        entry["promotion_commit"] = data["promotion_commit"]
    return entry


def promotion_commit_inventory_entries(
    commits: list[PromotedSourceCommit],
    integrated_issues: list[tuple[Issue, str]],
) -> list[dict[str, Any]]:
    verified_by_commit: dict[str, list[Issue]] = {}
    for issue, integrated_commit in integrated_issues:
        verified_by_commit.setdefault(integrated_commit, []).append(issue)

    entries: list[dict[str, Any]] = []
    for commit in commits:
        issues = verified_by_commit.get(commit.sha, [])
        entry: dict[str, Any] = {
            "sha": commit.sha,
            "subject": commit.subject,
            "verified_local_integration": bool(issues),
            "classification": (
                "verified_local_integration"
                if issues
                else "unverified_promotion_commit"
            ),
        }
        if issues:
            issue_payloads = [
                {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.url,
                }
                for issue in issues
            ]
            if len(issue_payloads) == 1:
                entry["issue"] = issue_payloads[0]
            else:
                entry["issues"] = issue_payloads
            entry["integrated_commit"] = commit.sha
        entries.append(entry)
    return entries


def emit(message: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    stream.write(f"{message}\n")
    stream.flush()
