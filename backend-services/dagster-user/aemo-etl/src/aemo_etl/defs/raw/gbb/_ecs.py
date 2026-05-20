"""Shared ECS run tags for GBB raw source-table jobs."""

import json

SPOT_FARGATE_RUN_TASK_KWARGS = json.dumps(
    {"capacityProviderStrategy": [{"capacityProvider": "FARGATE_SPOT", "weight": 1}]},
    separators=(",", ":"),
)


def rebuild_sized_spot_ecs_tags() -> dict[str, str]:
    """Return run tags for larger rebuild workers on Fargate Spot."""
    return {
        "ecs/cpu": "1024",
        "ecs/memory": "8192",
        "ecs/run_task_kwargs": SPOT_FARGATE_RUN_TASK_KWARGS,
    }


def pipeline_connection_flow_v2_hotfix_ecs_tags() -> dict[str, str]:
    """Return run tags for the pipeline connection flow v2 compute hot fix."""
    return {
        "ecs/cpu": "2048",
        "ecs/memory": "16384",
        "ecs/run_task_kwargs": SPOT_FARGATE_RUN_TASK_KWARGS,
    }
