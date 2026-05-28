from __future__ import annotations

import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .workflow import *  # noqa: F403

FAILURE_SUMMARY_ARTIFACT_MAX_BYTES = 256_000
FAILURE_SUMMARY_MAX_CHARS = 1_000
FAILURE_SUMMARY_MAX_LINES = 8
FAILURE_SUMMARY_MARKDOWN_MAX_CHARS = 420
ADAPTIVE_EVENT_TYPES: frozenset[str] = frozenset(
    {"hard_stop", "gated_retry", "residual_update"}
)
ADAPTIVE_EVENT_DEFAULTS: dict[str, dict[str, bool]] = {
    "hard_stop": {
        "automatic_retry_allowed": False,
        "consumes_attempt_budget": False,
    },
    "gated_retry": {
        "automatic_retry_allowed": True,
        "consumes_attempt_budget": True,
    },
    "residual_update": {
        "automatic_retry_allowed": False,
        "consumes_attempt_budget": False,
    },
}


def utc_now_text() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def path_text(path: Path | None) -> str | None:
    if path is None:
        return None
    return str(path)


def run_configuration_payload(config: LoopConfig) -> dict[str, Any]:
    return {
        "max_codex_attempts": config.max_codex_attempts,
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
            "issue_completion_review": {
                "enabled": True,
                "required": False,
                "status": "not_started",
                "reasons": [],
                "deployment_classification": None,
                "high_stiffness_evidence": [],
                "log_path": None,
                "artifact_path": None,
                "attempts": [],
                "repair_attempts": [],
                "failure": None,
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
            "operator_smoke": {
                "status": "not_requested",
                "smoke_id": None,
                "command_path": None,
                "command_args": [],
                "cwd": None,
                "log_path": None,
                "timeout": None,
                "evidence_path": None,
                "exit_status": None,
                "error": None,
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
            "adaptive_events": [],
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
            "source_table_replay_recovery": {
                "status": "not_started",
                "reason": None,
                "affected_tables": [],
                "credential_boundary": None,
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
            "deploy_repair_issues": {
                "enabled": True,
                "status": "not_started",
                "log_path": None,
                "artifact_path": None,
                "created": [],
                "duplicates": [],
                "validation_downgrades": [],
                "failures": [],
                "recovery_guidance": None,
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
            "adaptive_events": [],
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
            "adaptive_events": [],
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

    def record_adaptive_event(
        self,
        event_type: str,
        *,
        trigger_reason: str,
        issue_number: int | None = None,
        residual_work_summary: str | None = None,
        automatic_retry_allowed: bool | None = None,
        consumes_attempt_budget: bool | None = None,
    ) -> dict[str, Any]:
        if event_type not in ADAPTIVE_EVENT_TYPES:
            supported_types = ", ".join(sorted(ADAPTIVE_EVENT_TYPES))
            raise RalphError(
                f"Unsupported adaptive event type: {event_type}. "
                f"Expected one of: {supported_types}."
            )
        if trigger_reason.strip() == "":
            raise RalphError("Adaptive event trigger_reason must not be empty.")

        defaults = ADAPTIVE_EVENT_DEFAULTS[event_type]
        retry_allowed = (
            defaults["automatic_retry_allowed"]
            if automatic_retry_allowed is None
            else automatic_retry_allowed
        )
        budget_consumed = (
            defaults["consumes_attempt_budget"]
            if consumes_attempt_budget is None
            else consumes_attempt_budget
        )
        if event_type == "hard_stop" and (retry_allowed or budget_consumed):
            raise RalphError(
                "Adaptive hard_stop events must not allow automatic Codex retry "
                "or consume the per-issue attempt budget."
            )

        entry: dict[str, Any] = {
            "timestamp": utc_now_text(),
            "event_type": event_type,
            "trigger_reason": trigger_reason,
            "issue_number": (
                issue_number
                if issue_number is not None
                else self._manifest_issue_number_or_none()
            ),
            "residual_work_summary": residual_work_summary,
            "automatic_retry_allowed": retry_allowed,
            "consumes_attempt_budget": budget_consumed,
        }
        adaptive_events = self.data.setdefault("adaptive_events", [])
        if not isinstance(adaptive_events, list):
            raise RalphError("Manifest adaptive_events field is not a list.")
        adaptive_events.append(entry)
        self.record_event(f"adaptive_{event_type}", details=entry)
        return entry

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

    def record_source_table_replay_recovery(
        self, recovery: PostPromotionSourceTableReplayRecovery
    ) -> None:
        self.data["source_table_replay_recovery"] = recovery.to_manifest()
        self.record_event(
            "source_table_replay_recovery_recorded",
            details={
                "status": recovery.status,
                "affected_table_count": len(recovery.affected_tables),
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

    def record_deploy_repair_issues(
        self,
        status: str,
        *,
        log_path: Path | None = None,
        artifact_path: Path | None = None,
        created: list[dict[str, Any]] | None = None,
        duplicates: list[dict[str, Any]] | None = None,
        validation_downgrades: list[dict[str, Any]] | None = None,
        failures: list[dict[str, Any]] | None = None,
        reason: str | None = None,
        recovery_guidance: str | None = None,
    ) -> None:
        repairs = self.data.setdefault("deploy_repair_issues", {})
        if not isinstance(repairs, dict):
            raise RalphError("Manifest deploy_repair_issues field is not an object.")
        repairs["status"] = status
        if log_path is not None or "log_path" not in repairs:
            repairs["log_path"] = path_text(log_path)
        if artifact_path is not None or "artifact_path" not in repairs:
            repairs["artifact_path"] = path_text(artifact_path)
        if created is not None:
            repairs["created"] = created
        if duplicates is not None:
            repairs["duplicates"] = duplicates
        if validation_downgrades is not None:
            repairs["validation_downgrades"] = validation_downgrades
        if failures is not None:
            repairs["failures"] = failures
        if reason is not None:
            repairs["reason"] = reason
        if recovery_guidance is not None:
            repairs["recovery_guidance"] = recovery_guidance
        self.record_event(f"deploy_repair_issues_{status}", details=dict(repairs))

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
        target_commit: str | None,
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

    def record_issue_completion_review(
        self,
        status: str,
        *,
        trigger: IssueCompletionReviewTrigger | None = None,
        log_path: Path | None = None,
        artifact_path: Path | None = None,
        review_attempt: int | None = None,
        result: str | None = None,
        findings: str | None = None,
        repair_attempt: int | None = None,
        error: str | None = None,
    ) -> None:
        review = self.data.setdefault("issue_completion_review", {})
        if not isinstance(review, dict):
            raise RalphError("Manifest issue_completion_review field is not an object.")
        review["status"] = status
        if trigger is not None:
            trigger_payload = trigger.to_manifest()
            review["required"] = trigger.required
            review["reasons"] = trigger_payload["reasons"]
            review["deployment_classification"] = trigger_payload[
                "deployment_classification"
            ]
            review["high_stiffness_evidence"] = trigger_payload[
                "high_stiffness_evidence"
            ]
        if log_path is not None or "log_path" not in review:
            review["log_path"] = path_text(log_path)
        if artifact_path is not None or "artifact_path" not in review:
            review["artifact_path"] = path_text(artifact_path)
        if error is not None:
            review["failure"] = {
                "message": error,
                "log_path": path_text(log_path),
                "artifact_path": path_text(artifact_path),
            }
        elif status not in {"failed", "failed_exhausted", "failed_invalid_result"}:
            review["failure"] = None

        if review_attempt is not None:
            attempts = review.setdefault("attempts", [])
            if not isinstance(attempts, list):
                raise RalphError(
                    "Manifest issue_completion_review.attempts field is not a list."
                )
            entry: dict[str, Any] = {
                "attempt": review_attempt,
                "status": status,
                "log_path": path_text(log_path),
                "artifact_path": path_text(artifact_path),
            }
            if result is not None:
                entry["result"] = result
            if findings is not None:
                entry["findings"] = findings
            if error is not None:
                entry["error"] = error
            replaced = False
            for index, existing in enumerate(attempts):
                if (
                    isinstance(existing, dict)
                    and existing.get("attempt") == review_attempt
                ):
                    attempts[index] = {**existing, **entry}
                    replaced = True
                    break
            if not replaced:
                attempts.append(entry)

        if repair_attempt is not None:
            repairs = review.setdefault("repair_attempts", [])
            if not isinstance(repairs, list):
                raise RalphError(
                    "Manifest issue_completion_review.repair_attempts field is not a list."
                )
            entry = {
                "attempt": repair_attempt,
                "status": status,
                "log_path": path_text(log_path),
            }
            if error is not None:
                entry["error"] = error
            replaced = False
            for index, existing in enumerate(repairs):
                if (
                    isinstance(existing, dict)
                    and existing.get("attempt") == repair_attempt
                ):
                    repairs[index] = {**existing, **entry}
                    replaced = True
                    break
            if not replaced:
                repairs.append(entry)

        self.record_event(f"issue_completion_review_{status}", details=dict(review))

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

    def record_operator_smoke(
        self,
        status: str,
        *,
        command: OperatorSmokeCommand | None = None,
        result: OperatorSmokeResult | None = None,
        log_path: Path | None = None,
        evidence_path: Path | None = None,
        exit_status: int | None = None,
        error: str | None = None,
    ) -> None:
        smoke = self.data.setdefault("operator_smoke", {})
        if not isinstance(smoke, dict):
            raise RalphError("Manifest operator_smoke field is not an object.")

        if result is not None:
            smoke.update(result.to_manifest())
        elif command is not None:
            smoke.update(command.to_manifest(log_path=log_path))

        smoke["status"] = status
        if log_path is not None or "log_path" not in smoke:
            smoke["log_path"] = path_text(log_path)
        if evidence_path is not None or "evidence_path" not in smoke:
            smoke["evidence_path"] = path_text(evidence_path)
        if exit_status is not None or "exit_status" not in smoke:
            smoke["exit_status"] = exit_status
        if error is not None:
            smoke["error"] = error
        elif status not in {"failed", "timed_out"}:
            smoke["error"] = None
        self.record_event(f"operator_smoke_{status}", details=dict(smoke))

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

    def record_drain_scheduler_fatal_stop_recovered(self) -> None:
        scheduler = self.data.get("drain_scheduler")
        if not isinstance(scheduler, dict):
            return
        fatal_stop = scheduler.get("fatal_stop")
        if not isinstance(fatal_stop, dict):
            return
        if fatal_stop.get("status") != "triggered":
            return
        fatal_stop["status"] = "recovered"
        fatal_stop["recovered_at"] = utc_now_text()
        self.record_event("drain_scheduler_fatal_stop_recovered", details=fatal_stop)

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
                "integrated_commit": warning.integrated_commit,
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

    def _manifest_issue_number_or_none(self) -> int | None:
        issue = self.data.get("issue")
        if not isinstance(issue, dict):
            return None
        try:
            return int(issue["number"])
        except (KeyError, TypeError, ValueError):
            return None

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
        ensure_operator_deploy_repair_state(data)
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
        self.record_current_issue_payload(issue_payload_for_operator(issue))

    def record_current_issue_payload(self, issue_payload: dict[str, Any]) -> None:
        self.record_event(
            "running_issue",
            current={
                "kind": "issue",
                "issue": issue_payload,
                "started_at": utc_now_text(),
            },
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
                "started_at": utc_now_text(),
            },
        )

    def record_active_child_manifest(self, child_manifest_path: Path) -> None:
        current = self.data.get("current")
        if not isinstance(current, dict):
            current = self._current_from_child_manifest(child_manifest_path)
        else:
            current = dict(current)
        current.setdefault("started_at", utc_now_text())
        current["child_run_dir"] = str(child_manifest_path.parent)
        current["child_manifest_path"] = str(child_manifest_path)
        current["child_last_observed_at"] = utc_now_text()

        entry = child_manifest_entry(child_manifest_path)
        for key in ("kind", "status", "stage", "started_at", "updated_at"):
            value = entry.get(key)
            if value is not None:
                current[f"child_{key}"] = value
        if isinstance(entry.get("issue"), dict) and current.get("kind") != "promotion":
            current["kind"] = "issue"
            current["issue"] = entry["issue"]

        self.record_child_run(child_manifest_path)
        self.record_event(
            "active_child_manifest_recorded",
            current=current,
            details={
                "child_manifest_path": str(child_manifest_path),
                "child_run_dir": str(child_manifest_path.parent),
            },
        )

    def _current_from_child_manifest(self, child_manifest_path: Path) -> dict[str, Any]:
        entry = child_manifest_entry(child_manifest_path)
        kind = str(entry.get("kind") or "child")
        if kind == "implementation" and isinstance(entry.get("issue"), dict):
            return {
                "kind": "issue",
                "issue": entry["issue"],
                "started_at": utc_now_text(),
            }
        if kind == "promotion":
            data = child_manifest_data_for_operator(child_manifest_path)
            return {
                "kind": "promotion",
                "source_branch": str(data.get("source_branch") or "unknown")
                if isinstance(data, dict)
                else "unknown",
                "target_branch": str(data.get("integration_target") or "unknown")
                if isinstance(data, dict)
                else "unknown",
                "started_at": utc_now_text(),
            }
        return {"kind": kind, "started_at": utc_now_text()}

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

    def deploy_repair_target(self) -> dict[str, Any] | None:
        state = ensure_operator_deploy_repair_state(self.data)
        target = state.get("target_issue")
        if state.get("status") != "active" or not isinstance(target, dict):
            return None
        return target

    def deploy_repair_cycle_count(self) -> int:
        state = ensure_operator_deploy_repair_state(self.data)
        return operator_manifest_int(state.get("cycle_count"), default=0)

    def deploy_repair_cycle_limit(self) -> int:
        state = ensure_operator_deploy_repair_state(self.data)
        return operator_manifest_int(
            state.get("cycle_limit"),
            default=DEFAULT_DEPLOY_REPAIR_CYCLE_LIMIT,
        )

    def can_start_deploy_repair_cycle(self) -> bool:
        return self.deploy_repair_cycle_count() < self.deploy_repair_cycle_limit()

    def record_deploy_repair_target(
        self,
        issue_entry: dict[str, Any],
        *,
        child_manifest_path: Path | None,
    ) -> None:
        issue = deploy_repair_target_payload(issue_entry)
        state = ensure_operator_deploy_repair_state(self.data)
        cycle = self.deploy_repair_cycle_count() + 1
        state["status"] = "active"
        state["target_issue"] = issue
        state["cycle_count"] = cycle
        state["cycle_limit"] = self.deploy_repair_cycle_limit()
        history = state.setdefault("history", [])
        if not isinstance(history, list):
            history = []
            state["history"] = history
        history.append(
            {
                "timestamp": utc_now_text(),
                "event": "target_recorded",
                "cycle": cycle,
                "issue": issue,
                "child_manifest_path": path_text(child_manifest_path),
            }
        )
        if child_manifest_path is not None:
            self.record_child_run(child_manifest_path)
        self.record_event(
            "deploy_repair_target_recorded",
            details={
                "cycle": cycle,
                "cycle_limit": state["cycle_limit"],
                "issue": issue,
                "child_manifest_path": path_text(child_manifest_path),
            },
        )

    def clear_deploy_repair_target(
        self,
        *,
        child_manifest_path: Path | None,
        reason: str,
    ) -> None:
        state = ensure_operator_deploy_repair_state(self.data)
        target = state.get("target_issue")
        if state.get("status") != "active" or not isinstance(target, dict):
            return
        state["status"] = "inactive"
        state["target_issue"] = None
        history = state.setdefault("history", [])
        if not isinstance(history, list):
            history = []
            state["history"] = history
        history.append(
            {
                "timestamp": utc_now_text(),
                "event": "target_cleared",
                "reason": reason,
                "issue": target,
                "child_manifest_path": path_text(child_manifest_path),
            }
        )
        if child_manifest_path is not None:
            self.record_child_run(child_manifest_path)
        self.record_event(
            "deploy_repair_target_cleared",
            details={
                "reason": reason,
                "issue": target,
                "child_manifest_path": path_text(child_manifest_path),
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


def operator_manifest_int(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def ensure_operator_deploy_repair_state(data: dict[str, Any]) -> dict[str, Any]:
    state = data.setdefault("deploy_repair", {})
    if not isinstance(state, dict):
        state = {}
        data["deploy_repair"] = state
    state.setdefault("status", "inactive")
    state.setdefault("target_issue", None)
    state["cycle_count"] = operator_manifest_int(state.get("cycle_count"), default=0)
    state["cycle_limit"] = operator_manifest_int(
        state.get("cycle_limit"),
        default=DEFAULT_DEPLOY_REPAIR_CYCLE_LIMIT,
    )
    history = state.setdefault("history", [])
    if not isinstance(history, list):
        state["history"] = []
    return state


def deploy_repair_target_payload(entry: dict[str, Any]) -> dict[str, Any]:
    issue_number = operator_manifest_int(entry.get("number"), default=0)
    if issue_number <= 0:
        raise RalphError("Deploy-repair target entry does not include an issue number.")
    labels_value = entry.get("labels")
    labels = (
        sorted(str(label) for label in labels_value if isinstance(label, str))
        if isinstance(labels_value, list)
        else []
    )
    return {
        "number": issue_number,
        "title": str(entry.get("title") or f"Deploy-repair issue #{issue_number}"),
        "url": entry.get("url"),
        "labels": labels,
        "source_marker": entry.get("source_marker"),
        "validation_status": entry.get("validation_status"),
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


def capture_operator_smoke_evidence_path(
    *,
    log_path: Path,
    cwd: Path,
    run_dir: Path,
) -> Path | None:
    if not log_path.exists():
        return None
    log_text = log_path.read_text(encoding="utf-8")
    source_path = latest_run_manifest_path_from_log(log_text, cwd=cwd)
    if source_path is None:
        return None

    if source_path.exists() and source_path.is_file():
        suffix = source_path.suffix or ".txt"
        artifact_path = run_dir / f"{log_path.stem}-evidence{suffix}"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.resolve() != artifact_path.resolve():
            shutil.copy2(source_path, artifact_path)
        return artifact_path

    artifact_path = run_dir / f"{log_path.stem}-evidence.json"
    write_json_artifact(
        artifact_path,
        {
            "source_path": str(source_path),
            "source_available": False,
            "log_path": str(log_path),
            "artifact_kind": "operator_smoke_log_extract",
        },
    )
    return artifact_path


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
    deploy_repair_issues = [
        repair
        for promotion in promotion_entries
        if promotion.get("deploy_repair_issues") is not None
        for repair in [operator_rollup_deploy_repair_entry(promotion)]
        if repair is not None
    ]
    operator_smokes = [
        smoke
        for entry in [*issue_entries["succeeded"], *issue_entries["failed"]]
        for smoke in [operator_rollup_operator_smoke_entry(entry)]
        if smoke is not None
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
    requeue_recovery = operator_rollup_requeue_recovery(final_queue, child_sources)
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
            "deploy_repair": data.get("deploy_repair")
            if isinstance(data.get("deploy_repair"), dict)
            else None,
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
            "deploy_repair_issue_phases": len(deploy_repair_issues),
            "operator_smokes": len(operator_smokes),
            "manual_recoveries": len(manual_recoveries),
            "qa_surfaces": len(qa_surfaces),
            "post_promotion_followups": len(post_promotion_followups),
            "pre_push_requeue_eligible": len(requeue_recovery["eligible_pre_push"]),
            "final_queue_clean": final_queue["clean"],
        },
        "issues": issue_entries,
        "failed_attempts": failed_attempts,
        "manual_recoveries": manual_recoveries,
        "local_integrations": local_integrations,
        "promotions": promotion_entries,
        "deployment_executions": deployment_executions,
        "deploy_repair_issues": deploy_repair_issues,
        "operator_smokes": operator_smokes,
        "qa_surfaces": qa_surfaces,
        "post_promotion_followups": post_promotion_followups,
        "exploratory_acceptance_review": data.get("exploratory_acceptance_review"),
        "final_queue": final_queue,
        "requeue_recovery": requeue_recovery,
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
        str(source.get("manifest_path") or ""): source for source in child_sources
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
    status = (
        str(child_source.get("status") or "unknown")
        if child_source is not None
        else "unknown"
    )
    entry: dict[str, Any] = {
        "issue": issue,
        "status": status,
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
        "operator_smoke": child_data.get("operator_smoke")
        if isinstance(child_data.get("operator_smoke"), dict)
        else None,
        "ready_issue_refresh_status": operator_rollup_nested_status(
            child_data, "ready_issue_refresh"
        ),
        "failure": child_data.get("failure"),
    }
    if child_source is not None and child_source.get("manifest_error") is not None:
        entry["manifest_error"] = child_source.get("manifest_error")
    if operator_rollup_entry_failed(status, checkpoint):
        entry["failure_summary"] = operator_rollup_failure_summary(
            run_kind="implementation",
            child_data=child_data,
            manifest_path=manifest_path,
            manifest_read_status=entry.get("manifest_read_status"),
            manifest_error=entry.get("manifest_error"),
            checkpoint=checkpoint,
        )
    return entry


def operator_rollup_operator_smoke_entry(
    issue_entry: dict[str, Any],
) -> dict[str, Any] | None:
    smoke = issue_entry.get("operator_smoke")
    if not isinstance(smoke, dict):
        return None
    status = str(smoke.get("status") or "")
    if status in {"", "not_requested"}:
        return None
    return {
        "issue": issue_entry.get("issue"),
        "status": status,
        "smoke_id": smoke.get("smoke_id"),
        "command_path": smoke.get("command_path"),
        "command_args": (
            smoke.get("command_args")
            if isinstance(smoke.get("command_args"), list)
            else []
        ),
        "cwd": smoke.get("cwd"),
        "log_path": smoke.get("log_path"),
        "timeout": smoke.get("timeout"),
        "evidence_path": smoke.get("evidence_path"),
        "exit_status": smoke.get("exit_status"),
        "error": smoke.get("error"),
        "manifest_path": issue_entry.get("manifest_path"),
    }


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
        str(source.get("manifest_path") or ""): source for source in child_sources
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
    deploy_repair_issues = child_data.get("deploy_repair_issues")
    deploy_repair_issues = (
        deploy_repair_issues if isinstance(deploy_repair_issues, dict) else None
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
    status = str(source.get("status") or "unknown") if source is not None else "unknown"
    entry: dict[str, Any] = {
        "status": status,
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
        "deploy_repair_issues": deploy_repair_issues,
        "failure": child_data.get("failure"),
    }
    if source is not None and source.get("manifest_error") is not None:
        entry["manifest_error"] = source.get("manifest_error")
    if operator_rollup_entry_failed(status, checkpoint):
        entry["failure_summary"] = operator_rollup_failure_summary(
            run_kind="promotion",
            child_data=child_data,
            manifest_path=manifest_path,
            manifest_read_status=entry.get("manifest_read_status"),
            manifest_error=entry.get("manifest_error"),
            checkpoint=checkpoint,
        )
    return entry


def operator_rollup_entry_failed(
    status: str,
    checkpoint: dict[str, Any] | None,
) -> bool:
    checkpoint_name = str(checkpoint.get("checkpoint") or "") if checkpoint else ""
    return checkpoint_name in {"issue_failed", "promotion_failed"} or status not in {
        "succeeded"
    }


def operator_rollup_failure_summary(
    *,
    run_kind: str,
    child_data: dict[str, Any],
    manifest_path: str,
    manifest_read_status: Any,
    manifest_error: Any,
    checkpoint: dict[str, Any] | None,
) -> dict[str, Any]:
    checkpoint_name = str(checkpoint.get("checkpoint") or "") if checkpoint else None
    read_status = str(manifest_read_status or "unknown")
    if read_status != "loaded":
        excerpt = f"Child manifest {read_status}: {manifest_path or '<missing path>'}."
        if manifest_error:
            excerpt = f"{excerpt} {manifest_error}"
        return {
            "status": "unavailable",
            "failure_type": f"manifest_{read_status}",
            "checkpoint": checkpoint_name,
            "test_lane": None,
            "phase": "child manifest read",
            "command": [],
            "command_text": None,
            "exit_code": None,
            "primary_log_path": None,
            "log_read_status": "not_available",
            "excerpt": operator_rollup_bounded_excerpt(excerpt),
            "excerpt_source": "manifest_read_status",
        }

    failure = child_data.get("failure")
    failure = failure if isinstance(failure, dict) else {}
    failed_qa = operator_rollup_first_failed_qa_result(child_data)
    primary_log_path = operator_rollup_failure_primary_log_path(
        child_data,
        failure=failure,
        failed_qa=failed_qa,
    )
    log_summary = operator_rollup_command_log_summary(primary_log_path)
    comment_summary = operator_rollup_failure_comment_summary(child_data)
    command = operator_rollup_failure_command(failed_qa)
    command_text = format_command(command) if command else log_summary["command_text"]
    excerpt = log_summary["excerpt"]
    excerpt_source = log_summary["excerpt_source"]
    if excerpt is None and comment_summary["excerpt"] is not None:
        excerpt = comment_summary["excerpt"]
        excerpt_source = comment_summary["excerpt_source"]
    if excerpt is None:
        excerpt = operator_rollup_bounded_excerpt(str(failure.get("message") or ""))
        excerpt_source = "failure_message" if excerpt else None
    if excerpt is None and log_summary["log_read_status"] == "missing":
        excerpt = f"Primary log path is missing: {primary_log_path}."
        excerpt_source = "log_read_status"

    return {
        "status": "summarized",
        "failure_type": operator_rollup_failure_type(
            child_data,
            failure=failure,
            failed_qa=failed_qa,
            checkpoint_name=checkpoint_name,
        ),
        "checkpoint": checkpoint_name,
        "test_lane": operator_rollup_failure_test_lane(failed_qa),
        "phase": operator_rollup_failure_phase(
            run_kind=run_kind,
            log_path=primary_log_path,
            failed_qa=failed_qa,
            failure_type=operator_rollup_failure_type(
                child_data,
                failure=failure,
                failed_qa=failed_qa,
                checkpoint_name=checkpoint_name,
            ),
            checkpoint_name=checkpoint_name,
        ),
        "command": command,
        "command_text": command_text,
        "exit_code": log_summary["exit_code"],
        "primary_log_path": primary_log_path,
        "log_read_status": log_summary["log_read_status"],
        "excerpt": excerpt,
        "excerpt_source": excerpt_source,
    }


def operator_rollup_first_failed_qa_result(
    child_data: dict[str, Any],
) -> dict[str, Any] | None:
    results = child_data.get("qa_results")
    if not isinstance(results, list):
        return None
    for result in results:
        if not isinstance(result, dict):
            continue
        if str(result.get("status") or "") == "failed":
            return result
    return None


def operator_rollup_failure_primary_log_path(
    child_data: dict[str, Any],
    *,
    failure: dict[str, Any],
    failed_qa: dict[str, Any] | None,
) -> str | None:
    if failed_qa is not None:
        log_path = str(failed_qa.get("log_path") or "")
        if log_path:
            return log_path

    formatter_recovery = child_data.get("formatter_recovery")
    if isinstance(formatter_recovery, dict):
        commit_check_paths = failure.get("commit_check_log_paths")
        if isinstance(commit_check_paths, list):
            for path in commit_check_paths:
                path_text_value = str(path or "")
                if path_text_value:
                    return path_text_value
        formatter_commit_results = formatter_recovery.get("commit_check_results")
        if isinstance(formatter_commit_results, list):
            for result in formatter_commit_results:
                if not isinstance(result, dict):
                    continue
                if str(result.get("status") or "") != "failed":
                    continue
                log_path = str(result.get("log_path") or "")
                if log_path:
                    return log_path

    log_path = str(failure.get("log_path") or "")
    if log_path:
        return log_path

    for key in ("branch_sync", "ready_issue_refresh", "post_promotion_review"):
        value = child_data.get(key)
        if not isinstance(value, dict):
            continue
        nested_failure = value.get("failure")
        if isinstance(nested_failure, dict):
            log_path = str(nested_failure.get("log_path") or "")
            if log_path:
                return log_path
        log_path = str(value.get("log_path") or "")
        if log_path and str(value.get("status") or "") in {
            "failed",
            "failed_warning_only",
        }:
            return log_path
    return None


def operator_rollup_failure_command(failed_qa: dict[str, Any] | None) -> list[str]:
    if failed_qa is None:
        return []
    command = failed_qa.get("command")
    if not isinstance(command, list):
        return []
    return [str(part) for part in command]


def operator_rollup_failure_test_lane(failed_qa: dict[str, Any] | None) -> str | None:
    if failed_qa is None:
        return None
    name = str(failed_qa.get("name") or "")
    return name or None


def operator_rollup_failure_type(
    child_data: dict[str, Any],
    *,
    failure: dict[str, Any],
    failed_qa: dict[str, Any] | None,
    checkpoint_name: str | None,
) -> str | None:
    failure_type = str(failure.get("type") or "")
    if failure_type:
        return failure_type
    for key in ("formatter_recovery", "branch_sync", "promotion_worktree_preflight"):
        value = child_data.get(key)
        if not isinstance(value, dict):
            continue
        failure_type = str(value.get("failure_type") or "")
        if failure_type:
            return failure_type
    if failed_qa is not None:
        return "qa_failed"
    return checkpoint_name


def operator_rollup_failure_phase(
    *,
    run_kind: str,
    log_path: str | None,
    failed_qa: dict[str, Any] | None,
    failure_type: str | None,
    checkpoint_name: str | None,
) -> str | None:
    log_name = Path(str(log_path)).name if log_path else ""
    if failed_qa is not None:
        if "formatter-recovery-commit-check" in log_name:
            return "formatter recovery Commit check"
        if run_kind == "promotion":
            return "Promotion QA"
        return "QA"
    if "integration-git-commit" in log_name:
        return "Local integration commit"
    if "issue-git-commit" in log_name:
        return "implementation commit"
    if "git-push" in log_name and run_kind == "promotion":
        return "Promotion push"
    if "git-push" in log_name:
        return "Integration target push"
    if failure_type == FORMATTER_REWRITE_RECOVERY_FAILURE_TYPE:
        return "formatter recovery"
    if checkpoint_name == "promotion_failed":
        return "Promotion"
    if checkpoint_name == "issue_failed":
        return "issue implementation"
    return None


def operator_rollup_command_log_summary(log_path: str | None) -> dict[str, Any]:
    if not log_path:
        return {
            "log_read_status": "missing_path",
            "command_text": None,
            "exit_code": None,
            "excerpt": None,
            "excerpt_source": None,
        }
    path = Path(log_path)
    if path.suffix == ".jsonl":
        return {
            "log_read_status": "skipped_jsonl",
            "command_text": None,
            "exit_code": None,
            "excerpt": None,
            "excerpt_source": None,
        }
    if not path.exists():
        return {
            "log_read_status": "missing",
            "command_text": None,
            "exit_code": None,
            "excerpt": None,
            "excerpt_source": None,
        }
    try:
        text = operator_rollup_read_text_bounded(path)
    except OSError as error:
        return {
            "log_read_status": "unreadable",
            "command_text": None,
            "exit_code": None,
            "excerpt": operator_rollup_bounded_excerpt(str(error)),
            "excerpt_source": "log_read_error",
        }
    metadata = operator_rollup_command_log_metadata(text)
    streams = operator_rollup_command_log_streams(text)
    excerpt_source = "stderr" if streams["stderr"] else "stdout"
    excerpt_text = streams["stderr"] or streams["stdout"] or text
    return {
        "log_read_status": "loaded",
        "command_text": metadata["command_text"],
        "exit_code": metadata["exit_code"],
        "excerpt": operator_rollup_bounded_excerpt(excerpt_text),
        "excerpt_source": excerpt_source if excerpt_text.strip() else None,
    }


def operator_rollup_read_text_bounded(path: Path) -> str:
    size = path.stat().st_size
    if size <= FAILURE_SUMMARY_ARTIFACT_MAX_BYTES:
        return path.read_text(encoding="utf-8", errors="replace")
    head_bytes = FAILURE_SUMMARY_ARTIFACT_MAX_BYTES // 4
    tail_bytes = FAILURE_SUMMARY_ARTIFACT_MAX_BYTES - head_bytes
    with path.open("rb") as handle:
        head = handle.read(head_bytes)
        handle.seek(max(0, size - tail_bytes))
        tail = handle.read(tail_bytes)
    omitted = max(0, size - len(head) - len(tail))
    return (
        head.decode("utf-8", "replace")
        + f"\n[... omitted {omitted} bytes ...]\n"
        + tail.decode("utf-8", "replace")
    )


def operator_rollup_command_log_metadata(text: str) -> dict[str, Any]:
    command_text: str | None = None
    exit_code: int | None = None
    for line in text.splitlines()[:20]:
        if line.startswith("$ "):
            command_text = line[2:]
            continue
        if line.startswith("exit: "):
            exit_code = operator_rollup_parse_exit_code(line.removeprefix("exit: "))
    return {"command_text": command_text, "exit_code": exit_code}


def operator_rollup_parse_exit_code(value: str) -> int | None:
    stripped = value.strip()
    if stripped.startswith("-") and stripped[1:].isdigit():
        return int(stripped)
    if stripped.isdigit():
        return int(stripped)
    return None


def operator_rollup_command_log_streams(text: str) -> dict[str, str]:
    streams: dict[str, list[str]] = {"stdout": [], "stderr": []}
    section: str | None = None
    for line in text.splitlines():
        if line == "STDOUT:":
            section = "stdout"
            continue
        if line == "STDERR:":
            section = "stderr"
            continue
        if section in streams:
            streams[section].append(line)
    return {
        "stdout": "\n".join(streams["stdout"]).strip(),
        "stderr": "\n".join(streams["stderr"]).strip(),
    }


def operator_rollup_failure_comment_summary(
    child_data: dict[str, Any],
) -> dict[str, Any]:
    comment_path = operator_rollup_failure_comment_path(child_data)
    if comment_path is None or not comment_path.exists():
        return {"excerpt": None, "excerpt_source": None}
    try:
        text = operator_rollup_read_text_bounded(comment_path)
    except OSError:
        return {"excerpt": None, "excerpt_source": None}
    return {
        "excerpt": operator_rollup_bounded_excerpt(text),
        "excerpt_source": "failure_comment",
    }


def operator_rollup_failure_comment_path(child_data: dict[str, Any]) -> Path | None:
    paths = child_data.get("paths")
    issue = child_data.get("issue")
    if not isinstance(paths, dict) or not isinstance(issue, dict):
        return None
    run_dir = str(paths.get("run_dir") or "")
    issue_number = issue.get("number")
    if run_dir == "" or issue_number is None:
        return None
    return Path(run_dir) / f"issue-{issue_number}-comment.md"


def operator_rollup_bounded_excerpt(value: str | None) -> str | None:
    if value is None:
        return None
    lines = [line.rstrip() for line in value.strip().splitlines() if line.strip()]
    if not lines:
        return None
    excerpt = "\n".join(lines[-FAILURE_SUMMARY_MAX_LINES:])
    if len(excerpt) <= FAILURE_SUMMARY_MAX_CHARS:
        return excerpt
    return "[...]" + excerpt[-FAILURE_SUMMARY_MAX_CHARS:]


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


def operator_rollup_deploy_repair_entry(
    promotion: dict[str, Any],
) -> dict[str, Any] | None:
    repairs = promotion.get("deploy_repair_issues")
    if not isinstance(repairs, dict):
        return None
    status = str(repairs.get("status") or "")
    if status in {"", "not_started"}:
        return None
    return {
        "status": status,
        "created": repairs.get("created")
        if isinstance(repairs.get("created"), list)
        else [],
        "duplicates": (
            repairs.get("duplicates")
            if isinstance(repairs.get("duplicates"), list)
            else []
        ),
        "validation_downgrades": (
            repairs.get("validation_downgrades")
            if isinstance(repairs.get("validation_downgrades"), list)
            else []
        ),
        "failures": (
            repairs.get("failures") if isinstance(repairs.get("failures"), list) else []
        ),
        "recovery_guidance": repairs.get("recovery_guidance"),
        "manifest_path": promotion.get("manifest_path"),
        "artifact_path": repairs.get("artifact_path"),
        "log_path": repairs.get("log_path"),
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


def requeue_eligibility_for_manifest_data(
    data: dict[str, Any],
) -> tuple[str, tuple[str, ...]]:
    run_kind = str(data.get("run_kind") or "")
    if run_kind != "implementation":
        return (
            "not applicable",
            ("run is not an implementation manifest",),
        )

    reasons: list[str] = []
    if str(data.get("status") or "") != "failed":
        reasons.append("run status is not failed")
    if normalized_commit_payload(data.get("integration_commit")) is not None:
        reasons.append("manifest already records integration_commit")

    push_status = manifest_data_push_status_value(data)
    if push_status == "pushed":
        reasons.append("manifest records a pushed Integration target")
    elif push_status != "not_started":
        reasons.append(f"Integration target push status is {push_status}")

    branch_sync = data.get("branch_sync")
    if isinstance(branch_sync, dict):
        branch_sync_status = str(branch_sync.get("status") or "not_started")
        if branch_sync_status in {"failed", "running"}:
            reasons.append(f"branch sync status is {branch_sync_status}")

    if not manifest_data_qa_passed_for_requeue(data):
        reasons.append("implementation QA did not fully pass")
    if not manifest_data_issue_completion_review_passed_for_requeue(data):
        reasons.append("Issue completion review did not pass or was not skipped")

    if reasons:
        return ("not eligible", tuple(reasons))
    return (
        "eligible",
        (
            "implementation QA passed",
            "Issue completion review passed or was not required",
            "no integration_commit was recorded",
            "no Integration target push was recorded",
        ),
    )


def manifest_data_push_entry(data: dict[str, Any]) -> dict[str, Any] | None:
    pushes = data.get("pushes")
    if not isinstance(pushes, dict):
        return None
    run_kind = str(data.get("run_kind") or "")
    key = "promotion_target" if run_kind == "promotion" else "integration_target"
    entry = pushes.get(key)
    return entry if isinstance(entry, dict) else None


def manifest_data_push_status_value(data: dict[str, Any]) -> str:
    entry = manifest_data_push_entry(data)
    if entry is None:
        return "not_started"
    return str(entry.get("status") or "unknown")


def manifest_data_qa_passed_for_requeue(data: dict[str, Any]) -> bool:
    results = data.get("qa_results")
    if not isinstance(results, list) or not results:
        return False
    statuses = [
        str(item.get("status") or "unknown")
        for item in results
        if isinstance(item, dict)
    ]
    return bool(statuses) and all(status == "passed" for status in statuses)


def manifest_data_issue_completion_review_passed_for_requeue(
    data: dict[str, Any],
) -> bool:
    review = data.get("issue_completion_review")
    if not isinstance(review, dict):
        return False
    status = str(review.get("status") or "not_started")
    return status in {"passed", "skipped_not_required"}


def operator_rollup_requeue_recovery(
    final_queue: dict[str, Any],
    child_sources: list[dict[str, Any]],
) -> dict[str, Any]:
    failed_issues = operator_queue_issue_payloads(final_queue, "failed")
    entries = [
        operator_requeue_recovery_entry(issue, child_sources) for issue in failed_issues
    ]
    eligible = [
        entry
        for entry in entries
        if entry.get("classification") == "eligible_pre_push_requeue"
    ]
    return {
        "eligible_pre_push": eligible,
        "failed_issues": entries,
        "guidance": operator_requeue_recovery_guidance(entries),
    }


def operator_queue_issue_payloads(
    final_queue: dict[str, Any],
    key: str,
) -> list[dict[str, Any]]:
    issues = final_queue.get("issues")
    issues = issues if isinstance(issues, dict) else {}
    values = issues.get(key)
    if not isinstance(values, list):
        return []
    return [value for value in values if isinstance(value, dict)]


def operator_requeue_recovery_entry(
    issue: dict[str, Any],
    child_sources: list[dict[str, Any]],
) -> dict[str, Any]:
    issue_number = operator_manifest_int(issue.get("number"), default=0)
    child_source = operator_requeue_child_source_for_issue(
        child_sources,
        issue_number=issue_number,
    )
    if child_source is None:
        return {
            "issue": issue,
            "classification": "unknown_no_child_manifest",
            "eligibility": "unknown",
            "reasons": [
                "no matching implementation child manifest was recorded for this agent-failed issue"
            ],
            "manifest_path": None,
            "guidance": (
                "Inspect the GitHub Issue labels, comments, and Ralph run "
                "manifests before choosing recovery."
            ),
        }

    manifest_path = str(child_source.get("manifest_path") or "")
    read_status = str(child_source.get("manifest_read_status") or "unknown")
    child_data = child_source.get("data")
    if not isinstance(child_data, dict):
        reason = f"child manifest read status is {read_status}"
        error = child_source.get("manifest_error")
        if error:
            reason = f"{reason}: {error}"
        return {
            "issue": issue,
            "classification": "unknown_child_manifest_unavailable",
            "eligibility": "unknown",
            "reasons": [reason],
            "manifest_path": manifest_path,
            "guidance": "Open the child manifest path before choosing recovery.",
        }

    eligibility, reasons = requeue_eligibility_for_manifest_data(child_data)
    classification = operator_requeue_recovery_classification(
        child_data,
        eligibility=eligibility,
    )
    run_dir = operator_manifest_run_dir_from_child_data(child_data, manifest_path)
    return {
        "issue": issue,
        "classification": classification,
        "eligibility": eligibility,
        "reasons": list(reasons),
        "manifest_path": manifest_path,
        "run_dir": run_dir,
        "dry_run_command": operator_requeue_dry_run_command(run_dir)
        if classification == "eligible_pre_push_requeue"
        else None,
        "live_command": operator_requeue_live_command(run_dir)
        if classification == "eligible_pre_push_requeue"
        else None,
        "guidance": operator_requeue_entry_guidance(
            classification,
            run_dir=run_dir,
        ),
    }


def operator_requeue_child_source_for_issue(
    child_sources: list[dict[str, Any]],
    *,
    issue_number: int,
) -> dict[str, Any] | None:
    if issue_number <= 0:
        return None
    candidates = []
    for source in child_sources:
        if source.get("kind") != "implementation":
            continue
        issue = source.get("issue")
        if not isinstance(issue, dict):
            continue
        if operator_manifest_int(issue.get("number"), default=0) != issue_number:
            continue
        candidates.append(source)
    if not candidates:
        return None
    return candidates[-1]


def operator_requeue_recovery_classification(
    child_data: dict[str, Any],
    *,
    eligibility: str,
) -> str:
    failure = child_data.get("failure")
    failure_message = ""
    failure_type = ""
    if isinstance(failure, dict):
        failure_message = str(failure.get("message") or "")
        failure_type = str(failure.get("type") or "")
    if "Missing required issue section" in failure_message:
        return "malformed_issue_contract"
    if failure_type == ISSUE_COMPLETION_REVIEW_FAILURE_TYPE:
        return "unrecoverable_implementation_failure"
    if eligibility == "eligible":
        return "eligible_pre_push_requeue"
    if normalized_commit_payload(child_data.get("integration_commit")) is not None:
        return "post_push_metadata_recovery"
    if manifest_data_push_status_value(child_data) == "pushed":
        return "post_push_metadata_recovery"

    branch_sync = child_data.get("branch_sync")
    if isinstance(branch_sync, dict):
        branch_sync_status = str(branch_sync.get("status") or "not_started")
        if branch_sync_status in {"failed", "running"}:
            return "manual_gitflow_recovery"

    if not manifest_data_qa_passed_for_requeue(child_data):
        return "unrecoverable_implementation_failure"
    if not manifest_data_issue_completion_review_passed_for_requeue(child_data):
        return "unrecoverable_implementation_failure"
    return "not_requeue_eligible"


def operator_manifest_run_dir_from_child_data(
    child_data: dict[str, Any],
    manifest_path: str,
) -> str:
    paths = child_data.get("paths")
    if isinstance(paths, dict):
        run_dir = str(paths.get("run_dir") or "")
        if run_dir:
            return run_dir
    if manifest_path:
        return str(Path(manifest_path).parent)
    return ""


def operator_requeue_dry_run_command(run_dir: str) -> str | None:
    if run_dir == "":
        return None
    return f"python3 scripts/ralph.py --recover-run {run_dir} --dry-run"


def operator_requeue_live_command(run_dir: str) -> str | None:
    if run_dir == "":
        return None
    return f"python3 scripts/ralph.py --recover-run {run_dir}"


def operator_requeue_entry_guidance(classification: str, *, run_dir: str) -> str:
    if classification == "eligible_pre_push_requeue":
        return (
            "Run the Ralph-owned pre-push requeue dry-run first. Do not start a "
            "competing Operator run; after the issue is restored to "
            "ready-for-agent, the normal Operator queue scan can claim it."
        )
    if classification == "post_push_metadata_recovery":
        return (
            "This is post-push metadata recovery, not pre-push requeue. Inspect "
            "the run and use --recover-run only after the recorded Local "
            "integration commit is verified on the expected Integration target."
        )
    if classification == "manual_gitflow_recovery":
        return (
            "This needs manual Gitflow recovery or branch-sync reconciliation, "
            "not pre-push requeue. Resolve the recorded Gitflow recovery state "
            "before normal drain or Promotion continues."
        )
    if classification == "malformed_issue_contract":
        return (
            "The issue contract is malformed. Fix the GitHub Issue body and "
            "labels instead of requeueing the failed implementation run."
        )
    if classification == "unrecoverable_implementation_failure":
        return (
            "The preserved implementation attempt did not pass the gates needed "
            "for requeue. Inspect the child run manifest and rerun Ralph for the "
            "issue after repair."
        )
    if run_dir:
        return f"Inspect run `{run_dir}` before choosing recovery."
    return "Inspect the issue and child run manifests before choosing recovery."


def operator_requeue_recovery_guidance(entries: list[dict[str, Any]]) -> str:
    if not entries:
        return "No open agent-failed issues are recorded in the Operator queue."
    eligible = [
        entry
        for entry in entries
        if entry.get("classification") == "eligible_pre_push_requeue"
    ]
    if eligible:
        issue_text = ", ".join(
            operator_issue_title(entry.get("issue") or {}) for entry in eligible
        )
        return (
            f"Pre-push requeue is available for {issue_text}. Run the dry-run "
            "recovery command first, then the live recovery only if the plan "
            "restores agent-failed to ready-for-agent. Do not start a competing "
            "Operator run while the existing session can continue after requeue."
        )
    return (
        "No recorded agent-failed issue is eligible for pre-push requeue. Follow "
        "the per-issue classification before rerunning drain or Promotion."
    )


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
        "## Deploy Repair Issues",
        "",
        *operator_rollup_deploy_repair_markdown_lines(rollup["deploy_repair_issues"]),
        "",
        "## Operator Smokes",
        "",
        *operator_rollup_operator_smoke_markdown_lines(rollup["operator_smokes"]),
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
        "## Requeue Recovery",
        "",
        *operator_rollup_requeue_markdown_lines(rollup["requeue_recovery"]),
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
        lines.extend(
            operator_rollup_failure_summary_markdown_lines(entry.get("failure_summary"))
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
            + f"; Deploy repair `{operator_rollup_nested_status(entry, 'deploy_repair_issues') or 'not_started'}`"
            + f"; Post-promotion follow-ups `{followups.get('status')}` "
            + f"(created={len(created)}, failures={len(failures)})"
            + f"; manifest {markdown_path_link(entry.get('manifest_path'))}"
        )
        lines.extend(
            operator_rollup_failure_summary_markdown_lines(entry.get("failure_summary"))
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


def operator_rollup_failure_summary_markdown_lines(value: Any) -> list[str]:
    if not isinstance(value, dict):
        return []
    pieces = []
    failure_type = value.get("failure_type")
    if failure_type:
        pieces.append(f"type `{failure_type}`")
    checkpoint = value.get("checkpoint")
    if checkpoint:
        pieces.append(f"checkpoint `{checkpoint}`")
    test_lane = value.get("test_lane")
    if test_lane:
        pieces.append(f"Test lane `{test_lane}`")
    phase = value.get("phase")
    if phase:
        pieces.append(f"phase `{phase}`")
    command_text = value.get("command_text")
    if command_text:
        pieces.append(f"command {markdown_inline_code(str(command_text))}")
    exit_code = value.get("exit_code")
    if exit_code is not None:
        pieces.append(f"exit `{exit_code}`")
    primary_log_path = value.get("primary_log_path")
    if primary_log_path:
        pieces.append(f"log {markdown_artifact_link(primary_log_path, 'failure log')}")
    elif value.get("log_read_status"):
        pieces.append(f"log `{value.get('log_read_status')}`")
    lines = ["  - Failure summary: " + ("; ".join(pieces) or "not recorded")]
    excerpt = operator_rollup_markdown_excerpt(value.get("excerpt"))
    if excerpt:
        lines.append(f"    - Excerpt: {markdown_inline_code(excerpt)}")
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


def operator_rollup_deploy_repair_markdown_lines(
    entries: list[dict[str, Any]],
) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        created = entry.get("created") if isinstance(entry.get("created"), list) else []
        duplicates = (
            entry.get("duplicates") if isinstance(entry.get("duplicates"), list) else []
        )
        downgrades = (
            entry.get("validation_downgrades")
            if isinstance(entry.get("validation_downgrades"), list)
            else []
        )
        failures = (
            entry.get("failures") if isinstance(entry.get("failures"), list) else []
        )
        lines.append(
            "- "
            + f"`{entry.get('status')}`"
            + f"; created `{len(created)}`"
            + f"; duplicates `{len(duplicates)}`"
            + f"; validation downgrades `{len(downgrades)}`"
            + f"; failures `{len(failures)}`"
            + f"; artifact {markdown_path_link(entry.get('artifact_path'))}"
        )
    return lines


def operator_rollup_operator_smoke_markdown_lines(
    entries: list[dict[str, Any]],
) -> list[str]:
    if not entries:
        return ["- None"]
    lines: list[str] = []
    for entry in entries:
        issue = entry.get("issue") if isinstance(entry.get("issue"), dict) else {}
        log_path = markdown_artifact_link(entry.get("log_path"), "smoke log")
        lines.append(
            "- "
            + operator_issue_title(issue)
            + f" - `{entry.get('status')}`"
            + f"; smoke `{entry.get('smoke_id')}`"
            + f"; command `{entry.get('command_path')}`"
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


def operator_rollup_requeue_markdown_lines(
    recovery: dict[str, Any],
) -> list[str]:
    entries = recovery.get("failed_issues")
    entries = entries if isinstance(entries, list) else []
    lines = [f"- Guidance: {recovery.get('guidance') or 'not_recorded'}"]
    if not entries:
        return [*lines, "- No open agent-failed issues recorded"]
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        issue = entry.get("issue") if isinstance(entry.get("issue"), dict) else {}
        command = entry.get("dry_run_command") or "not_applicable"
        reasons = entry.get("reasons")
        reasons_text = (
            "; ".join(str(reason) for reason in reasons)
            if isinstance(reasons, list)
            else "not_recorded"
        )
        lines.append(
            "- "
            + operator_issue_title(issue)
            + f" - `{entry.get('classification')}`"
            + f"; eligibility `{entry.get('eligibility')}`"
            + f"; dry-run `{command}`"
            + f"; reasons {reasons_text}"
        )
    return lines


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


def markdown_inline_code(value: str) -> str:
    return "`" + value.replace("`", "'") + "`"


def operator_rollup_markdown_excerpt(value: Any) -> str | None:
    text = " ".join(str(value or "").split())
    if text == "":
        return None
    if len(text) <= FAILURE_SUMMARY_MARKDOWN_MAX_CHARS:
        return text
    return text[: FAILURE_SUMMARY_MARKDOWN_MAX_CHARS - 3] + "..."


def child_manifest_entry(child_manifest_path: Path) -> dict[str, Any]:
    entry: dict[str, Any] = {"path": str(child_manifest_path)}
    if not child_manifest_path.exists():
        entry["status"] = "missing"
        return entry
    data, error = child_manifest_data_for_operator_with_error(child_manifest_path)
    if error is not None:
        entry["status"] = "invalid"
        entry["error"] = error
        return entry
    if not isinstance(data, dict):
        entry["status"] = "invalid"
        entry["error"] = "manifest root is not an object"
        return entry
    entry["kind"] = str(data.get("run_kind") or "unknown")
    entry["status"] = str(data.get("status") or "unknown")
    entry["stage"] = str(data.get("stage") or "unknown")
    if data.get("started_at") is not None:
        entry["started_at"] = data.get("started_at")
    if data.get("updated_at") is not None:
        entry["updated_at"] = data.get("updated_at")
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


def child_manifest_data_for_operator_with_error(
    child_manifest_path: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        data = json.loads(child_manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return None, str(error)
    if not isinstance(data, dict):
        return None, "manifest root is not an object"
    return data, None


def child_manifest_data_for_operator(
    child_manifest_path: Path,
) -> dict[str, Any] | None:
    data, error = child_manifest_data_for_operator_with_error(child_manifest_path)
    if error is not None:
        return None
    return data


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
