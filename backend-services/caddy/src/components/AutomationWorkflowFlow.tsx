import {
  Background,
  Handle,
  MarkerType,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import { type CSSProperties, type MouseEvent, useEffect, useMemo, useRef, useState } from "react";
import "@xyflow/react/dist/style.css";

const modalCloseDurationMs = 180;
const repoBaseUrl = "https://github.com/Chr1sC0de/energy-market-delta-lake/blob/main";

type WorkflowTopicId = "goal" | "build-check" | "doc-sync" | "test-lane" | "approval";
type WorkflowTabId = "overview" | "deep-dive" | "delivery-modes";

type WorkflowNodeData = {
  detail: string;
  isActive?: boolean;
  isDimmed?: boolean;
  kind: "human" | "ai" | "outcome" | "failure" | "input";
  label: string;
  meta: string;
};

type WorkflowNode = Node<WorkflowNodeData, "workflow">;

type WorkflowStep = {
  detail: string;
  id: string;
  kind: WorkflowNodeData["kind"];
  label: string;
  meta: string;
};

type WorkflowLink = {
  href: string;
  label: string;
};

type WorkflowPanel = {
  code?: string;
  copy: string;
  flowLabel: string;
  links: WorkflowLink[];
  nodes: WorkflowStep[];
  positions: {
    desktop: Record<string, WorkflowNode["position"]>;
    mobile: Record<string, WorkflowNode["position"]>;
  };
  sideTitle: string;
  title: string;
};

type WorkflowTopic = {
  detail: string;
  id: WorkflowTopicId;
  label: string;
  meta: string;
  overview: WorkflowPanel;
  previewNodes: string[];
  summary: string;
  tone: "amber" | "blue" | "green";
};

const nodeWidth = 178;
const nodeHeight = 84;
const nodeHandles = [
  {
    id: "target-left",
    type: "target",
    position: Position.Left,
    x: 0,
    y: nodeHeight / 2,
    width: 1,
    height: 1,
  },
  {
    id: "source-right",
    type: "source",
    position: Position.Right,
    x: nodeWidth,
    y: nodeHeight / 2,
    width: 1,
    height: 1,
  },
  {
    id: "source-left",
    type: "source",
    position: Position.Left,
    x: 0,
    y: nodeHeight / 2,
    width: 1,
    height: 1,
  },
  {
    id: "target-right",
    type: "target",
    position: Position.Right,
    x: nodeWidth,
    y: nodeHeight / 2,
    width: 1,
    height: 1,
  },
  {
    id: "source-top",
    type: "source",
    position: Position.Top,
    x: nodeWidth / 2,
    y: 0,
    width: 1,
    height: 1,
  },
  {
    id: "target-top",
    type: "target",
    position: Position.Top,
    x: nodeWidth / 2,
    y: 0,
    width: 1,
    height: 1,
  },
  {
    id: "target-bottom",
    type: "target",
    position: Position.Bottom,
    x: nodeWidth / 2,
    y: nodeHeight,
    width: 1,
    height: 1,
  },
  {
    id: "source-bottom",
    type: "source",
    position: Position.Bottom,
    x: nodeWidth / 2,
    y: nodeHeight,
    width: 1,
    height: 1,
  },
] satisfies NonNullable<WorkflowNode["handles"]>;

const previewSteps: WorkflowStep[] = [
  {
    id: "human-goal",
    label: "Human sets goal",
    detail: "Operator workflow",
    meta: "human",
    kind: "human",
  },
  {
    id: "ralph-starts",
    label: "Ralph reads issue",
    detail: "Contract and context",
    meta: "Ralph",
    kind: "ai",
  },
  {
    id: "ai-builds",
    label: "AI makes change",
    detail: "Code and docs",
    meta: "AI",
    kind: "ai",
  },
  {
    id: "docs-sync",
    label: "Docs sync",
    detail: "Maintained docs",
    meta: "docs",
    kind: "input",
  },
  {
    id: "checks-run",
    label: "Checks run",
    detail: "Test lane evidence",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "test-lane",
    label: "Test lane",
    detail: "Scope and evidence",
    meta: "lane",
    kind: "input",
  },
  {
    id: "ready",
    label: "Ready to review",
    detail: "Evidence handoff",
    meta: "handoff",
    kind: "outcome",
  },
  {
    id: "human-approves",
    label: "Human approves",
    detail: "Promotion decision",
    meta: "human",
    kind: "human",
  },
];

const previewPositions = {
  desktop: {
    "human-goal": { x: 42, y: 54 },
    "ralph-starts": { x: 286, y: 54 },
    "ai-builds": { x: 530, y: 54 },
    "docs-sync": { x: 774, y: 54 },
    "checks-run": { x: 42, y: 232 },
    "test-lane": { x: 286, y: 232 },
    ready: { x: 530, y: 232 },
    "human-approves": { x: 774, y: 232 },
  },
  mobile: {
    "human-goal": { x: 74, y: 24 },
    "ralph-starts": { x: 74, y: 110 },
    "ai-builds": { x: 74, y: 196 },
    "docs-sync": { x: 74, y: 282 },
    "checks-run": { x: 74, y: 368 },
    "test-lane": { x: 74, y: 454 },
    ready: { x: 74, y: 540 },
    "human-approves": { x: 74, y: 626 },
  },
} satisfies WorkflowPanel["positions"];

type StaticPreviewLayout = keyof typeof previewPositions;

const previewDimensions = {
  desktop: { width: 994, height: 360 },
  mobile: { width: 326, height: 734 },
} satisfies Record<StaticPreviewLayout, { height: number; width: number }>;

const goalSteps: WorkflowStep[] = [
  {
    id: "intent",
    label: "Intent",
    detail: "Human goal and tradeoffs",
    meta: "human",
    kind: "human",
  },
  {
    id: "grill",
    label: "$grill-with-docs",
    detail: "Stress-test the plan",
    meta: "skill",
    kind: "input",
  },
  {
    id: "shape",
    label: "$shape-issues",
    detail: "Tracer-bullet issues",
    meta: "skill",
    kind: "input",
  },
  {
    id: "triage",
    label: "$ralph-triage",
    detail: "Labels and Delivery mode",
    meta: "skill",
    kind: "input",
  },
  {
    id: "ready",
    label: "Ready issue",
    detail: "Clear agent contract",
    meta: "queue",
    kind: "outcome",
  },
];

const buildSteps: WorkflowStep[] = [
  {
    id: "contract",
    label: "Issue contract",
    detail: "What to build",
    meta: "input",
    kind: "input",
  },
  {
    id: "context",
    label: "Context anchors",
    detail: "Files and docs",
    meta: "input",
    kind: "input",
  },
  {
    id: "codex",
    label: "Codex implements",
    detail: "Code and docs",
    meta: "AI",
    kind: "ai",
  },
  {
    id: "qa",
    label: "Selected QA",
    detail: "Test lane evidence",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "failure",
    label: "Failure context",
    detail: "Tighten and retry",
    meta: "loop",
    kind: "failure",
  },
  {
    id: "handoff",
    label: "Handoff evidence",
    detail: "Ready for review",
    meta: "exit",
    kind: "outcome",
  },
];

const docSyncSteps: WorkflowStep[] = [
  {
    id: "changed-paths",
    label: "Changed paths",
    detail: "git diff --name-only",
    meta: "input",
    kind: "input",
  },
  {
    id: "sync-sources",
    label: "sync.sources",
    detail: "Maintained doc matches",
    meta: "contract",
    kind: "input",
  },
  {
    id: "maintained-docs",
    label: "Maintained docs",
    detail: "Update or record no change",
    meta: "docs",
    kind: "input",
  },
  {
    id: "doc-qa",
    label: "Doc QA",
    detail: "Links, anchors, metadata",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "root-commit-check",
    label: "Commit check",
    detail: "Root doc surface",
    meta: "commit",
    kind: "outcome",
  },
  {
    id: "doc-evidence",
    label: "Sync evidence",
    detail: "Commands and decisions",
    meta: "handoff",
    kind: "outcome",
  },
];

const testLaneSteps: WorkflowStep[] = [
  {
    id: "criteria",
    label: "Acceptance criteria",
    detail: "Expected behavior",
    meta: "issue",
    kind: "input",
  },
  {
    id: "lane",
    label: "Test lane",
    detail: "Boundary and cost",
    meta: "scope",
    kind: "input",
  },
  {
    id: "fast-check",
    label: "Fast check",
    detail: "Local confidence",
    meta: "local",
    kind: "outcome",
  },
  {
    id: "commit-check",
    label: "Commit check",
    detail: "Pre-commit surface",
    meta: "commit",
    kind: "outcome",
  },
  {
    id: "push-check",
    label: "Push check",
    detail: "Promotion confidence",
    meta: "push",
    kind: "outcome",
  },
  {
    id: "evidence",
    label: "QA evidence",
    detail: "Commands and logs",
    meta: "handoff",
    kind: "outcome",
  },
];

const approvalSteps: WorkflowStep[] = [
  {
    id: "review-dev",
    label: "Review dev",
    detail: "Inspect target range",
    meta: "human",
    kind: "human",
  },
  {
    id: "evidence",
    label: "Evidence check",
    detail: "Issues, QA, docs",
    meta: "review",
    kind: "input",
  },
  {
    id: "exploratory",
    label: "Exploratory call",
    detail: "Accept, hold, reject",
    meta: "optional",
    kind: "input",
  },
  {
    id: "promote",
    label: "Promotion",
    detail: "Move dev to main",
    meta: "Ralph",
    kind: "ai",
  },
  {
    id: "closed",
    label: "Verified closure",
    detail: "Evidence-backed issues",
    meta: "outcome",
    kind: "outcome",
  },
];

const testLaneDeepSteps: WorkflowStep[] = [
  {
    id: "unit",
    label: "Unit test",
    detail: "Pure or mocked code",
    meta: "lane",
    kind: "input",
  },
  {
    id: "component",
    label: "Component test",
    detail: "Runtime wiring in process",
    meta: "lane",
    kind: "input",
  },
  {
    id: "integration",
    label: "Integration test",
    detail: "Local external dependency",
    meta: "lane",
    kind: "input",
  },
  {
    id: "commit",
    label: "Commit check",
    detail: "Fast local gate",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "push",
    label: "Push check",
    detail: "Promotion gate input",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "record",
    label: "Recorded evidence",
    detail: "QA commands in Ralph output",
    meta: "evidence",
    kind: "outcome",
  },
];

const nestedLoopSteps: WorkflowStep[] = [
  {
    id: "specs",
    label: "Backing specs",
    detail: "Issue, context, checks",
    meta: "input",
    kind: "input",
  },
  {
    id: "each-spec",
    label: "For each spec",
    detail: "Pick the next item",
    meta: "outer loop",
    kind: "input",
  },
  {
    id: "goal",
    label: "Goal for spec",
    detail: "Task plus context",
    meta: "goal",
    kind: "input",
  },
  {
    id: "ralph-detail",
    label: "Ralph works",
    detail: "Edits code and docs",
    meta: "AI",
    kind: "ai",
  },
  {
    id: "detail-checks",
    label: "Checks run",
    detail: "Pass or fail",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "failure",
    label: "Failure found",
    detail: "Feeds the loop",
    meta: "inner loop",
    kind: "failure",
  },
  {
    id: "next-fix",
    label: "Tighten goal",
    detail: "Add failure context",
    meta: "loop",
    kind: "ai",
  },
  {
    id: "spec-complete",
    label: "Spec complete",
    detail: "Next spec or finish",
    meta: "outer loop",
    kind: "outcome",
  },
  {
    id: "detail-ready",
    label: "All specs done",
    detail: "Prepared handoff",
    meta: "exit",
    kind: "outcome",
  },
  {
    id: "detail-human",
    label: "Human reviews",
    detail: "Approve or send back",
    meta: "human",
    kind: "human",
  },
];

const approvalDeepSteps: WorkflowStep[] = [
  {
    id: "status",
    label: "Status",
    detail: "Read Operator run",
    meta: "review",
    kind: "input",
  },
  {
    id: "diff",
    label: "Inspect diff",
    detail: "Range and files",
    meta: "human",
    kind: "human",
  },
  {
    id: "qa",
    label: "Push check",
    detail: "Aggregate QA",
    meta: "check",
    kind: "outcome",
  },
  {
    id: "promotion",
    label: "Promote",
    detail: "dev reaches main",
    meta: "Ralph",
    kind: "ai",
  },
  {
    id: "metadata",
    label: "Metadata",
    detail: "Close verified issues",
    meta: "GitHub",
    kind: "outcome",
  },
  {
    id: "follow-up",
    label: "Follow-ups",
    detail: "Post-promotion review",
    meta: "review",
    kind: "outcome",
  },
];

const approvalDeliveryModeSteps: WorkflowStep[] = [
  {
    id: "validated",
    label: "Validated issue",
    detail: "QA evidence exists",
    meta: "input",
    kind: "outcome",
  },
  {
    id: "gitflow",
    label: "Gitflow delivery",
    detail: "Default safer path",
    meta: "mode",
    kind: "input",
  },
  {
    id: "trunk",
    label: "Trunk delivery",
    detail: "Opt-in low-risk path",
    meta: "mode",
    kind: "input",
  },
  {
    id: "dev-integration",
    label: "Local integration",
    detail: "Squash to dev",
    meta: "dev",
    kind: "ai",
  },
  {
    id: "review-dev",
    label: "Review dev",
    detail: "Human evidence check",
    meta: "human",
    kind: "human",
  },
  {
    id: "main-integration",
    label: "Local integration",
    detail: "Squash to main",
    meta: "main",
    kind: "ai",
  },
  {
    id: "promotion",
    label: "Promotion",
    detail: "dev reaches main",
    meta: "Ralph",
    kind: "ai",
  },
  {
    id: "closed",
    label: "Issue closed",
    detail: "Verified main work",
    meta: "GitHub",
    kind: "outcome",
  },
];

const linearFiveDesktop = {
  intent: { x: 20, y: 150 },
  grill: { x: 230, y: 150 },
  shape: { x: 440, y: 150 },
  triage: { x: 650, y: 150 },
  ready: { x: 860, y: 150 },
};

const buildDesktopPositions = {
  contract: { x: 20, y: 78 },
  context: { x: 230, y: 78 },
  codex: { x: 440, y: 78 },
  qa: { x: 650, y: 78 },
  failure: { x: 440, y: 240 },
  handoff: { x: 860, y: 78 },
};

const docSyncDesktopPositions = {
  "changed-paths": { x: 72, y: 70 },
  "sync-sources": { x: 322, y: 70 },
  "maintained-docs": { x: 572, y: 70 },
  "doc-qa": { x: 572, y: 250 },
  "root-commit-check": { x: 322, y: 250 },
  "doc-evidence": { x: 72, y: 250 },
};

const testLaneDesktopPositions = {
  criteria: { x: 72, y: 70 },
  lane: { x: 322, y: 70 },
  "fast-check": { x: 572, y: 70 },
  "commit-check": { x: 572, y: 250 },
  "push-check": { x: 322, y: 250 },
  evidence: { x: 72, y: 250 },
};

const approvalDesktopPositions = {
  "review-dev": { x: 20, y: 150 },
  evidence: { x: 230, y: 150 },
  exploratory: { x: 440, y: 150 },
  promote: { x: 650, y: 150 },
  closed: { x: 860, y: 150 },
};

const testLaneDeepDesktopPositions = {
  unit: { x: 72, y: 70 },
  component: { x: 322, y: 70 },
  commit: { x: 572, y: 70 },
  integration: { x: 72, y: 250 },
  push: { x: 322, y: 250 },
  record: { x: 572, y: 250 },
};

const nestedLoopDesktopPositions = {
  specs: { x: 20, y: 44 },
  "each-spec": { x: 230, y: 44 },
  goal: { x: 440, y: 44 },
  "ralph-detail": { x: 650, y: 44 },
  "detail-checks": { x: 650, y: 206 },
  failure: { x: 440, y: 206 },
  "next-fix": { x: 230, y: 206 },
  "spec-complete": { x: 20, y: 206 },
  "detail-ready": { x: 230, y: 360 },
  "detail-human": { x: 440, y: 360 },
};

const approvalDeepDesktopPositions = {
  status: { x: 20, y: 80 },
  diff: { x: 230, y: 80 },
  qa: { x: 440, y: 80 },
  promotion: { x: 650, y: 80 },
  metadata: { x: 440, y: 250 },
  "follow-up": { x: 650, y: 250 },
};

const approvalDeliveryModeDesktopPositions = {
  validated: { x: 322, y: 32 },
  gitflow: { x: 72, y: 150 },
  trunk: { x: 572, y: 150 },
  "dev-integration": { x: 72, y: 285 },
  "review-dev": { x: 322, y: 285 },
  "main-integration": { x: 572, y: 285 },
  promotion: { x: 322, y: 420 },
  closed: { x: 572, y: 420 },
};

function verticalPositions(ids: string[], startY = 32, stepY = 116) {
  return Object.fromEntries(ids.map((id, index) => [id, { x: 74, y: startY + stepY * index }]));
}

const workflowLoopCode = `const backingSpecs = [
  issueContract,
  contextAnchors,
  acceptanceCriteria,
  selectedChecks,
];

for (const spec of backingSpecs) {
  let goal = makeGoal(spec);
  let result = { ok: false };

  while (!result.ok) {
    const change = codex.run(goal);
    result = ralph.runChecks(change);

    if (!result.ok) {
      goal = tightenGoal(goal, result);
    }
  }
}

humanReview(change);`;

const docSyncCode = `git diff --name-only
rg -n "<changed path>" README.md docs backend-services infrastructure tools
python3 -m unittest discover -s tests
prek run -a`;

const promotionCode = `$ralph-loop drain
review dev and evidence
$ralph-loop promote`;

const topics: WorkflowTopic[] = [
  {
    id: "goal",
    label: "Human sets the goal",
    meta: "01",
    summary: "The Operator workflow turns intent into a checked issue contract.",
    detail: "Shaping, issue creation, triage",
    tone: "amber",
    previewNodes: ["human-goal", "ralph-starts"],
    overview: {
      title: "Goal setting is an Operator workflow.",
      sideTitle: "Agent skills make the workflow repeatable.",
      copy:
        "The human owns intent and judgment. Agent skills turn that intent into a reusable path: stress-test the plan, shape independently workable issues, and triage them with the right Delivery mode.",
      flowLabel: "Operator goal-setting workflow",
      nodes: goalSteps,
      positions: {
        desktop: linearFiveDesktop,
        mobile: verticalPositions(["intent", "grill", "shape", "triage", "ready"]),
      },
      links: [
        { label: "Operator workflow", href: `${repoBaseUrl}/OPERATOR.md` },
        { label: "$shape-issues", href: `${repoBaseUrl}/.agents/skills/shape-issues/SKILL.md` },
        { label: "$ralph-triage", href: `${repoBaseUrl}/.agents/skills/ralph-triage/SKILL.md` },
        { label: "OpenAI Skills guide", href: "https://developers.openai.com/api/docs/guides/tools-skills" },
        {
          label: "Save workflows as skills",
          href: "https://developers.openai.com/codex/use-cases/reusable-codex-skills",
        },
      ],
    },
  },
  {
    id: "build-check",
    label: "AI does the build and check work",
    meta: "02",
    summary: "Ralph gives Codex a bounded contract, runs QA, and loops on failures.",
    detail: "Nested Ralph loop",
    tone: "blue",
    previewNodes: ["ralph-starts", "ai-builds", "checks-run"],
    overview: {
      title: "Ralph runs build and check work as a loop.",
      sideTitle: "Conceptual deep dive",
      copy:
        "The issue body stays the contract. Ralph creates the work context, Codex edits code and docs, selected Test lane QA and Commit check evidence decide whether the loop tightens the goal or hands off a validated result.",
      flowLabel: "AI build and check workflow",
      nodes: buildSteps,
      positions: {
        desktop: buildDesktopPositions,
        mobile: verticalPositions(["contract", "context", "codex", "qa", "failure", "handoff"]),
      },
      links: [
        { label: "Ralph loop docs", href: `${repoBaseUrl}/docs/agents/ralph-loop.md` },
        { label: "$ralph-loop", href: `${repoBaseUrl}/.agents/skills/ralph-loop/SKILL.md` },
        { label: "Agent workflow map", href: `${repoBaseUrl}/docs/agents/README.md` },
      ],
      code: workflowLoopCode,
    },
  },
  {
    id: "doc-sync",
    label: "Documentation sync",
    meta: "03",
    summary: "Changed paths drive maintained docs, sync metadata, and doc QA.",
    detail: "Maintained docs and sync evidence",
    tone: "blue",
    previewNodes: ["ai-builds", "docs-sync", "checks-run"],
    overview: {
      title: "Documentation sync keeps repo guidance current.",
      sideTitle: "Maintained-doc contract",
      copy:
        "Changed files are matched against sync.sources. Any matched maintained doc is updated or explicitly judged still correct, then doc QA checks metadata, links, anchors, and route coverage before the root Commit check runs.",
      flowLabel: "Documentation sync workflow",
      nodes: docSyncSteps,
      positions: {
        desktop: docSyncDesktopPositions,
        mobile: verticalPositions([
          "changed-paths",
          "sync-sources",
          "maintained-docs",
          "doc-qa",
          "root-commit-check",
          "doc-evidence",
        ]),
      },
      links: [
        { label: "Documentation sync workflow", href: `${repoBaseUrl}/docs/repository/documentation-sync.md` },
        { label: "Caddy README", href: `${repoBaseUrl}/backend-services/caddy/README.md` },
        { label: "Doc QA ratchet", href: `${repoBaseUrl}/tests/test_documentation_qa_ratchet.py` },
      ],
      code: docSyncCode,
    },
  },
  {
    id: "test-lane",
    label: "Test lane contract",
    meta: "04",
    summary: "Acceptance criteria choose the Test lane and check evidence Ralph must satisfy.",
    detail: "Test lane scope and QA evidence",
    tone: "green",
    previewNodes: ["checks-run", "test-lane", "ready"],
    overview: {
      title: "Test lanes turn acceptance criteria into evidence.",
      sideTitle: "QA boundary and proof",
      copy:
        "The issue declares expected behavior, then Ralph selects the right Test lane and check surface. Unit, Component, and Integration work stay separated so the evidence matches risk and runtime cost.",
      flowLabel: "Test lane contract workflow",
      nodes: testLaneSteps,
      positions: {
        desktop: testLaneDesktopPositions,
        mobile: verticalPositions(["criteria", "lane", "fast-check", "commit-check", "push-check", "evidence"]),
      },
      links: [
        { label: "Canonical language", href: `${repoBaseUrl}/CONTEXT.md` },
        { label: "Ralph QA policy", href: `${repoBaseUrl}/docs/agents/ralph-loop.md#qa-policy` },
        { label: "Subproject QA", href: `${repoBaseUrl}/AGENTS.md#subproject-qa` },
      ],
    },
  },
  {
    id: "approval",
    label: "Human approves the result",
    meta: "05",
    summary: "The human reviews evidence before Promotion closes verified work.",
    detail: "Review and Promotion",
    tone: "amber",
    previewNodes: ["ready", "human-approves"],
    overview: {
      title: "Approval is review plus Promotion.",
      sideTitle: "Evidence before closure",
      copy:
        "The human reviews the Integration target, checks the changed files and Ralph evidence, handles any Exploratory decisions, then runs Promotion so only verified issue work reaches main and closes.",
      flowLabel: "Human approval and Promotion workflow",
      nodes: approvalSteps,
      positions: {
        desktop: approvalDesktopPositions,
        mobile: verticalPositions(["review-dev", "evidence", "exploratory", "promote", "closed"]),
      },
      links: [
        { label: "Review dev checklist", href: `${repoBaseUrl}/OPERATOR.md#review-dev` },
        { label: "Promotion pass", href: `${repoBaseUrl}/docs/agents/ralph-loop.md#promotion-pass` },
        {
          label: "Exploratory branch ADR",
          href: `${repoBaseUrl}/docs/adr/0005-ralph-exploratory-branches-stay-outside-automatic-promotion.md`,
        },
      ],
      code: promotionCode,
    },
  },
];

const deepDiveByTopic: Record<WorkflowTopicId, WorkflowPanel> = {
  goal: {
    ...topics[0].overview,
    title: "Agent skills codify repeated Operator work.",
    sideTitle: "What an Agent skill is",
    copy:
      "An Agent skill is a local instruction bundle invoked as $skill-name. In this repo, skills keep shaping, issue triage, and Ralph operation consistent without pasting the same runbook into every thread.",
  },
  "build-check": {
    ...topics[1].overview,
    title: "The Ralph loop tightens the goal until checks pass.",
    copy:
      "The deeper model is still simple: iterate over the backing specs, run Codex against the current goal, run selected checks, and feed failure evidence back into the next goal until the issue has handoff evidence.",
    flowLabel: "Nested Ralph loop",
    nodes: nestedLoopSteps,
    positions: {
      desktop: nestedLoopDesktopPositions,
      mobile: verticalPositions([
        "specs",
        "each-spec",
        "goal",
        "ralph-detail",
        "detail-checks",
        "failure",
        "next-fix",
        "spec-complete",
        "detail-ready",
        "detail-human",
      ]),
    },
  },
  "doc-sync": {
    ...topics[2].overview,
    title: "Sync metadata makes stale docs visible.",
    copy:
      "The deeper contract is explicit: sync.sources names the files that can make a maintained doc stale, doc QA verifies the metadata and links, and review records when a matched doc did not need wording changes.",
  },
  "test-lane": {
    ...topics[3].overview,
    title: "Test lane boundaries keep QA evidence honest.",
    copy:
      "A Unit test proves isolated logic, a Component test proves in-process wiring, and an Integration test proves local external dependencies. Commit check evidence stays fast; Push check evidence can include guarded Integration tests before Promotion.",
    flowLabel: "Test lane evidence workflow",
    nodes: testLaneDeepSteps,
    positions: {
      desktop: testLaneDeepDesktopPositions,
      mobile: verticalPositions(["unit", "component", "commit", "integration", "push", "record"]),
    },
  },
  approval: {
    ...topics[4].overview,
    title: "Promotion closes only evidence-backed work.",
    copy:
      "The approval path checks the target range before merge, runs the aggregate Push check during Promotion, then updates GitHub Issues only when the promoted branch contains verified Ralph evidence.",
    flowLabel: "Promotion evidence workflow",
    nodes: approvalDeepSteps,
    positions: {
      desktop: approvalDeepDesktopPositions,
      mobile: verticalPositions(["status", "diff", "qa", "promotion", "metadata", "follow-up"]),
    },
  },
};

const approvalDeliveryModePanel: WorkflowPanel = {
  title: "Delivery modes decide when approval closes work.",
  sideTitle: "Gitflow vs Trunk",
  copy:
    "Gitflow delivery is the default: Ralph integrates validated work to dev, leaves the issue open for human review, and closes it after Promotion verifies the work on main. Trunk delivery is opt-in for low-risk changes: Ralph integrates directly to main and closes the issue immediately after verified Local integration.",
  flowLabel: "Gitflow and Trunk delivery comparison",
  nodes: approvalDeliveryModeSteps,
  positions: {
    desktop: approvalDeliveryModeDesktopPositions,
    mobile: verticalPositions([
      "validated",
      "gitflow",
      "dev-integration",
      "review-dev",
      "promotion",
      "trunk",
      "main-integration",
      "closed",
    ]),
  },
  links: [
    { label: "Delivery mode ADR", href: `${repoBaseUrl}/docs/adr/0002-ralph-delivery-modes.md` },
    { label: "Ralph delivery labels", href: `${repoBaseUrl}/docs/agents/ralph-loop.md#labels` },
    { label: "Promotion pass", href: `${repoBaseUrl}/docs/agents/ralph-loop.md#promotion-pass` },
  ],
};

function withEdgeStyle(edges: Edge[]) {
  return edges.map((edge) => ({
    ...edge,
    focusable: false,
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: "rgba(27, 35, 36, 0.76)",
      width: 16,
      height: 16,
    },
    style: {
      stroke: "rgba(27, 35, 36, 0.62)",
      strokeWidth: 2.5,
    },
  }));
}

function edge(
  id: string,
  source: string,
  target: string,
  sourceHandle = "source-right",
  targetHandle = "target-left",
  type?: Edge["type"],
): Edge {
  return { id, source, sourceHandle, target, targetHandle, type };
}

const panelEdgesByStepCount: Record<string, Edge[]> = {
  goal: withEdgeStyle([
    edge("intent-grill", "intent", "grill"),
    edge("grill-shape", "grill", "shape"),
    edge("shape-triage", "shape", "triage"),
    edge("triage-ready", "triage", "ready"),
  ]),
  goalMobile: withEdgeStyle([
    edge("intent-grill-mobile", "intent", "grill", "source-bottom", "target-top", "smoothstep"),
    edge("grill-shape-mobile", "grill", "shape", "source-bottom", "target-top", "smoothstep"),
    edge("shape-triage-mobile", "shape", "triage", "source-bottom", "target-top", "smoothstep"),
    edge("triage-ready-mobile", "triage", "ready", "source-bottom", "target-top", "smoothstep"),
  ]),
  build: withEdgeStyle([
    edge("contract-context", "contract", "context"),
    edge("context-codex", "context", "codex"),
    edge("codex-qa", "codex", "qa"),
    edge("qa-handoff", "qa", "handoff"),
    edge("qa-failure", "qa", "failure", "source-bottom", "target-top", "smoothstep"),
    edge("failure-codex", "failure", "codex", "source-top", "target-bottom", "smoothstep"),
  ]),
  buildMobile: withEdgeStyle([
    edge("contract-context-mobile", "contract", "context", "source-bottom", "target-top", "smoothstep"),
    edge("context-codex-mobile", "context", "codex", "source-bottom", "target-top", "smoothstep"),
    edge("codex-qa-mobile", "codex", "qa", "source-bottom", "target-top", "smoothstep"),
    edge("qa-failure-mobile", "qa", "failure", "source-bottom", "target-top", "smoothstep"),
    edge("failure-codex-mobile", "failure", "codex", "source-right", "target-right", "smoothstep"),
    edge("qa-handoff-mobile", "qa", "handoff", "source-right", "target-right", "smoothstep"),
  ]),
  docSync: withEdgeStyle([
    edge("changed-sources", "changed-paths", "sync-sources"),
    edge("sources-docs", "sync-sources", "maintained-docs"),
    edge("docs-qa", "maintained-docs", "doc-qa", "source-bottom", "target-top", "smoothstep"),
    edge("qa-commit", "doc-qa", "root-commit-check", "source-left", "target-right"),
    edge("commit-evidence", "root-commit-check", "doc-evidence", "source-left", "target-right"),
  ]),
  docSyncMobile: withEdgeStyle([
    edge("changed-sources-mobile", "changed-paths", "sync-sources", "source-bottom", "target-top", "smoothstep"),
    edge("sources-docs-mobile", "sync-sources", "maintained-docs", "source-bottom", "target-top", "smoothstep"),
    edge("docs-qa-mobile", "maintained-docs", "doc-qa", "source-bottom", "target-top", "smoothstep"),
    edge("qa-commit-mobile", "doc-qa", "root-commit-check", "source-bottom", "target-top", "smoothstep"),
    edge("commit-evidence-mobile", "root-commit-check", "doc-evidence", "source-bottom", "target-top", "smoothstep"),
  ]),
  testLane: withEdgeStyle([
    edge("criteria-lane", "criteria", "lane"),
    edge("lane-fast", "lane", "fast-check"),
    edge("fast-commit", "fast-check", "commit-check", "source-bottom", "target-top", "smoothstep"),
    edge("commit-push", "commit-check", "push-check", "source-left", "target-right"),
    edge("push-evidence", "push-check", "evidence", "source-left", "target-right"),
  ]),
  testLaneMobile: withEdgeStyle([
    edge("criteria-lane-mobile", "criteria", "lane", "source-bottom", "target-top", "smoothstep"),
    edge("lane-fast-mobile", "lane", "fast-check", "source-bottom", "target-top", "smoothstep"),
    edge("fast-commit-mobile", "fast-check", "commit-check", "source-bottom", "target-top", "smoothstep"),
    edge("commit-push-mobile", "commit-check", "push-check", "source-bottom", "target-top", "smoothstep"),
    edge("push-evidence-mobile", "push-check", "evidence", "source-bottom", "target-top", "smoothstep"),
  ]),
  testLaneDeep: withEdgeStyle([
    edge("unit-commit", "unit", "commit", "source-top", "target-top", "smoothstep"),
    edge("component-commit", "component", "commit", "source-right", "target-left"),
    edge("integration-push", "integration", "push", "source-right", "target-left"),
    edge("commit-push", "commit", "push", "source-bottom", "target-top", "smoothstep"),
    edge("push-record", "push", "record"),
  ]),
  testLaneDeepMobile: withEdgeStyle([
    edge("unit-commit-mobile", "unit", "commit", "source-right", "target-right", "smoothstep"),
    edge("component-commit-mobile", "component", "commit", "source-bottom", "target-top", "smoothstep"),
    edge("integration-push-mobile", "integration", "push", "source-bottom", "target-top", "smoothstep"),
    edge("commit-push-mobile", "commit", "push", "source-right", "target-right", "smoothstep"),
    edge("push-record-mobile", "push", "record", "source-bottom", "target-top", "smoothstep"),
  ]),
  approval: withEdgeStyle([
    edge("review-evidence", "review-dev", "evidence"),
    edge("evidence-exploratory", "evidence", "exploratory"),
    edge("exploratory-promote", "exploratory", "promote"),
    edge("promote-closed", "promote", "closed"),
  ]),
  approvalMobile: withEdgeStyle([
    edge("review-evidence-mobile", "review-dev", "evidence", "source-bottom", "target-top", "smoothstep"),
    edge("evidence-exploratory-mobile", "evidence", "exploratory", "source-bottom", "target-top", "smoothstep"),
    edge("exploratory-promote-mobile", "exploratory", "promote", "source-bottom", "target-top", "smoothstep"),
    edge("promote-closed-mobile", "promote", "closed", "source-bottom", "target-top", "smoothstep"),
  ]),
  nested: withEdgeStyle([
    edge("specs-each-spec", "specs", "each-spec"),
    edge("each-spec-goal", "each-spec", "goal"),
    edge("goal-ralph-detail", "goal", "ralph-detail"),
    edge("ralph-checks-detail", "ralph-detail", "detail-checks", "source-bottom", "target-top", "smoothstep"),
    edge("checks-spec-complete-detail", "detail-checks", "spec-complete", "source-left", "target-right"),
    edge("spec-complete-each-spec", "spec-complete", "each-spec", "source-top", "target-bottom", "smoothstep"),
    edge("spec-complete-ready-detail", "spec-complete", "detail-ready", "source-right", "target-left", "smoothstep"),
    edge("ready-human-detail", "detail-ready", "detail-human"),
    edge("checks-failure-detail", "detail-checks", "failure", "source-bottom", "target-top", "smoothstep"),
    edge("failure-next-fix", "failure", "next-fix", "source-left", "target-right"),
    edge("next-fix-ralph", "next-fix", "goal", "source-top", "target-bottom", "smoothstep"),
  ]),
  nestedMobile: withEdgeStyle([
    edge("specs-each-spec-mobile", "specs", "each-spec", "source-bottom", "target-top", "smoothstep"),
    edge("each-spec-goal-mobile", "each-spec", "goal", "source-bottom", "target-top", "smoothstep"),
    edge("goal-ralph-mobile", "goal", "ralph-detail", "source-bottom", "target-top", "smoothstep"),
    edge("ralph-checks-mobile", "ralph-detail", "detail-checks", "source-bottom", "target-top", "smoothstep"),
    edge("checks-failure-mobile", "detail-checks", "failure", "source-bottom", "target-top", "smoothstep"),
    edge("failure-next-fix-mobile", "failure", "next-fix", "source-bottom", "target-top", "smoothstep"),
    edge("next-fix-goal-mobile", "next-fix", "goal", "source-right", "target-right", "smoothstep"),
    edge("checks-spec-complete-mobile", "detail-checks", "spec-complete", "source-right", "target-right", "smoothstep"),
    edge("spec-complete-each-spec-mobile", "spec-complete", "each-spec", "source-left", "target-left", "smoothstep"),
    edge("spec-complete-ready-mobile", "spec-complete", "detail-ready", "source-bottom", "target-top", "smoothstep"),
    edge("ready-human-mobile", "detail-ready", "detail-human", "source-bottom", "target-top", "smoothstep"),
  ]),
  approvalDeep: withEdgeStyle([
    edge("status-diff", "status", "diff"),
    edge("diff-qa", "diff", "qa"),
    edge("qa-promotion", "qa", "promotion"),
    edge("promotion-metadata", "promotion", "metadata", "source-bottom", "target-top", "smoothstep"),
    edge("metadata-follow-up", "metadata", "follow-up"),
  ]),
  approvalDeepMobile: withEdgeStyle([
    edge("status-diff-mobile", "status", "diff", "source-bottom", "target-top", "smoothstep"),
    edge("diff-qa-mobile", "diff", "qa", "source-bottom", "target-top", "smoothstep"),
    edge("qa-promotion-mobile", "qa", "promotion", "source-bottom", "target-top", "smoothstep"),
    edge("promotion-metadata-mobile", "promotion", "metadata", "source-bottom", "target-top", "smoothstep"),
    edge("metadata-follow-up-mobile", "metadata", "follow-up", "source-bottom", "target-top", "smoothstep"),
  ]),
  approvalDeliveryModes: withEdgeStyle([
    edge("validated-gitflow", "validated", "gitflow", "source-bottom", "target-top", "smoothstep"),
    edge("validated-trunk", "validated", "trunk", "source-bottom", "target-top", "smoothstep"),
    edge("gitflow-dev", "gitflow", "dev-integration", "source-bottom", "target-top", "smoothstep"),
    edge("dev-review", "dev-integration", "review-dev"),
    edge("review-promotion", "review-dev", "promotion", "source-bottom", "target-top", "smoothstep"),
    edge("promotion-closed", "promotion", "closed"),
    edge("trunk-main", "trunk", "main-integration", "source-bottom", "target-top", "smoothstep"),
    edge("main-closed", "main-integration", "closed", "source-bottom", "target-top", "smoothstep"),
  ]),
  approvalDeliveryModesMobile: withEdgeStyle([
    edge("validated-gitflow-mobile", "validated", "gitflow", "source-bottom", "target-top", "smoothstep"),
    edge("gitflow-dev-mobile", "gitflow", "dev-integration", "source-bottom", "target-top", "smoothstep"),
    edge("dev-review-mobile", "dev-integration", "review-dev", "source-bottom", "target-top", "smoothstep"),
    edge("review-promotion-mobile", "review-dev", "promotion", "source-bottom", "target-top", "smoothstep"),
    edge("promotion-closed-mobile", "promotion", "closed", "source-right", "target-right", "smoothstep"),
    edge("validated-trunk-mobile", "validated", "trunk", "source-right", "target-right", "smoothstep"),
    edge("trunk-main-mobile", "trunk", "main-integration", "source-bottom", "target-top", "smoothstep"),
    edge("main-closed-mobile", "main-integration", "closed", "source-bottom", "target-top", "smoothstep"),
  ]),
};

function getPanelEdges(topicId: WorkflowTopicId, tabId: WorkflowTabId, isNarrow: boolean) {
  if (topicId === "goal") return panelEdgesByStepCount[isNarrow ? "goalMobile" : "goal"];
  if (topicId === "doc-sync") return panelEdgesByStepCount[isNarrow ? "docSyncMobile" : "docSync"];
  if (topicId === "test-lane" && tabId === "deep-dive") {
    return panelEdgesByStepCount[isNarrow ? "testLaneDeepMobile" : "testLaneDeep"];
  }
  if (topicId === "test-lane") return panelEdgesByStepCount[isNarrow ? "testLaneMobile" : "testLane"];
  if (topicId === "approval" && tabId === "deep-dive") {
    return panelEdgesByStepCount[isNarrow ? "approvalDeepMobile" : "approvalDeep"];
  }
  if (topicId === "approval" && tabId === "delivery-modes") {
    return panelEdgesByStepCount[isNarrow ? "approvalDeliveryModesMobile" : "approvalDeliveryModes"];
  }
  if (topicId === "approval") return panelEdgesByStepCount[isNarrow ? "approvalMobile" : "approval"];
  if (tabId === "deep-dive") return panelEdgesByStepCount[isNarrow ? "nestedMobile" : "nested"];
  return panelEdgesByStepCount[isNarrow ? "buildMobile" : "build"];
}

function buildNodes(
  steps: WorkflowStep[],
  positions: Record<string, WorkflowNode["position"]>,
  activeIds?: Set<string>,
) {
  return steps.map((step) => ({
    id: step.id,
    type: "workflow" as const,
    width: nodeWidth,
    height: nodeHeight,
    position: positions[step.id],
    initialWidth: nodeWidth,
    initialHeight: nodeHeight,
    handles: nodeHandles,
    data: {
      ...step,
      isActive: activeIds?.has(step.id),
      isDimmed: activeIds !== undefined && !activeIds.has(step.id),
    },
  }));
}

function WorkflowNode({ data }: NodeProps<WorkflowNode>) {
  return (
    <div
      className={`workflow-node workflow-node-${data.kind}${data.isActive ? " is-active" : ""}${
        data.isDimmed ? " is-dimmed" : ""
      }`}
    >
      <Handle id="target-left" type="target" position={Position.Left} />
      <Handle id="source-left" type="source" position={Position.Left} />
      <Handle id="source-right" type="source" position={Position.Right} />
      <Handle id="target-right" type="target" position={Position.Right} />
      <Handle id="target-top" type="target" position={Position.Top} />
      <Handle id="source-top" type="source" position={Position.Top} />
      <Handle id="target-bottom" type="target" position={Position.Bottom} />
      <Handle id="source-bottom" type="source" position={Position.Bottom} />
      <span>{data.meta}</span>
      <strong>{data.label}</strong>
      <small>{data.detail}</small>
    </div>
  );
}

function previewPercent(value: number, total: number) {
  return `${(value / total) * 100}%`;
}

function previewNodeStyle(stepId: string, layout: StaticPreviewLayout): CSSProperties {
  const dimensions = previewDimensions[layout];
  const position = previewPositions[layout][stepId];

  return {
    left: previewPercent(position.x, dimensions.width),
    minHeight: previewPercent(nodeHeight, dimensions.height),
    top: previewPercent(position.y, dimensions.height),
    width: previewPercent(nodeWidth, dimensions.width),
  };
}

function previewAnchor(stepId: string, layout: StaticPreviewLayout, side: "bottom" | "left" | "right" | "top") {
  const position = previewPositions[layout][stepId];

  if (side === "right") return { x: position.x + nodeWidth, y: position.y + nodeHeight / 2 };
  if (side === "left") return { x: position.x, y: position.y + nodeHeight / 2 };
  if (side === "bottom") return { x: position.x + nodeWidth / 2, y: position.y + nodeHeight };
  return { x: position.x + nodeWidth / 2, y: position.y };
}

function previewLinePath(
  sourceId: string,
  targetId: string,
  layout: StaticPreviewLayout,
  sourceSide: "bottom" | "left" | "right" | "top",
  targetSide: "bottom" | "left" | "right" | "top",
) {
  const source = previewAnchor(sourceId, layout, sourceSide);
  const target = previewAnchor(targetId, layout, targetSide);
  return `M${source.x} ${source.y}L${target.x} ${target.y}`;
}

function previewStepPath(
  sourceId: string,
  targetId: string,
  layout: StaticPreviewLayout,
  sourceSide: "bottom" | "left" | "right" | "top",
  targetSide: "bottom" | "left" | "right" | "top",
) {
  const source = previewAnchor(sourceId, layout, sourceSide);
  const target = previewAnchor(targetId, layout, targetSide);
  const middleY = (source.y + target.y) / 2;
  return `M${source.x} ${source.y}V${middleY}H${target.x}V${target.y}`;
}

function staticPreviewPaths(layout: StaticPreviewLayout) {
  if (layout === "mobile") {
    return [
      previewLinePath("human-goal", "ralph-starts", layout, "bottom", "top"),
      previewLinePath("ralph-starts", "ai-builds", layout, "bottom", "top"),
      previewLinePath("ai-builds", "docs-sync", layout, "bottom", "top"),
      previewLinePath("docs-sync", "checks-run", layout, "bottom", "top"),
      previewLinePath("checks-run", "test-lane", layout, "bottom", "top"),
      previewLinePath("test-lane", "ready", layout, "bottom", "top"),
      previewLinePath("ready", "human-approves", layout, "bottom", "top"),
    ];
  }

  return [
    previewLinePath("human-goal", "ralph-starts", layout, "right", "left"),
    previewLinePath("ralph-starts", "ai-builds", layout, "right", "left"),
    previewLinePath("ai-builds", "docs-sync", layout, "right", "left"),
    previewStepPath("docs-sync", "checks-run", layout, "bottom", "top"),
    previewLinePath("checks-run", "test-lane", layout, "right", "left"),
    previewLinePath("test-lane", "ready", layout, "right", "left"),
    previewLinePath("ready", "human-approves", layout, "right", "left"),
  ];
}

function StaticWorkflowPreviewStage({
  activePreviewIds,
  layout,
}: {
  activePreviewIds: Set<string>;
  layout: StaticPreviewLayout;
}) {
  const dimensions = previewDimensions[layout];
  const markerId = `static-workflow-arrow-${layout}`;

  return (
    <div
      className={`static-flow-stage static-workflow-stage static-workflow-stage-${layout}`}
      aria-hidden="true"
    >
      <svg
        className="static-flow-edges"
        viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        preserveAspectRatio="none"
      >
        <defs>
          <marker
            id={markerId}
            markerHeight="8"
            markerWidth="8"
            orient="auto"
            refX="7"
            refY="4"
            viewBox="0 0 8 8"
          >
            <path d="M0 0L8 4L0 8Z" />
          </marker>
        </defs>
        {staticPreviewPaths(layout).map((path) => (
          <path d={path} key={path} markerEnd={`url(#${markerId})`} />
        ))}
      </svg>
      {previewSteps.map((step) => {
        const isActive = activePreviewIds.has(step.id);
        return (
          <div
            className={`workflow-node workflow-node-${step.kind}${isActive ? " is-active" : " is-dimmed"} static-flow-node`}
            key={`${layout}-${step.id}`}
            style={previewNodeStyle(step.id, layout)}
          >
            <span>{step.meta}</span>
            <strong>{step.label}</strong>
            <small>{step.detail}</small>
          </div>
        );
      })}
    </div>
  );
}

function StaticWorkflowPreview({ activePreviewIds }: { activePreviewIds: Set<string> }) {
  return (
    <div className="workflow-flow workflow-static-flow">
      <StaticWorkflowPreviewStage activePreviewIds={activePreviewIds} layout="desktop" />
      <StaticWorkflowPreviewStage activePreviewIds={activePreviewIds} layout="mobile" />
    </div>
  );
}

const nodeTypes = {
  workflow: WorkflowNode,
};

function useNarrowWorkflow() {
  const [isNarrow, setIsNarrow] = useState(false);

  useEffect(() => {
    const query = window.matchMedia("(max-width: 700px)");
    const update = () => setIsNarrow(query.matches);
    update();
    query.addEventListener("change", update);
    return () => query.removeEventListener("change", update);
  }, []);

  return isNarrow;
}

function renderLinks(links: WorkflowLink[]) {
  if (links.length === 0) return null;

  return (
    <div className="workflow-detail-links" aria-label="Related links">
      {links.map((link) => (
        <a href={link.href} key={link.href} target="_blank" rel="noreferrer">
          {link.label}
        </a>
      ))}
    </div>
  );
}

export default function AutomationWorkflowFlow() {
  const isNarrow = useNarrowWorkflow();
  const [activeTopicId, setActiveTopicId] = useState<WorkflowTopicId>("goal");
  const [detailTopicId, setDetailTopicId] = useState<WorkflowTopicId>("goal");
  const [detailTabId, setDetailTabId] = useState<WorkflowTabId>("overview");
  const [isDetailActive, setIsDetailActive] = useState(false);
  const [isDetailClosing, setIsDetailClosing] = useState(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const closeTimerRef = useRef<number | null>(null);
  const lastTriggerRef = useRef<HTMLButtonElement | null>(null);

  const activeTopic = topics.find((topic) => topic.id === activeTopicId) ?? topics[0];
  const detailTopic = topics.find((topic) => topic.id === detailTopicId) ?? activeTopic;
  const detailTabs: Array<{ id: WorkflowTabId; label: string }> =
    detailTopic.id === "approval"
      ? [
          { id: "overview", label: "Overview" },
          { id: "deep-dive", label: "Deep dive" },
          { id: "delivery-modes", label: "Delivery modes" },
        ]
      : [
          { id: "overview", label: "Overview" },
          { id: "deep-dive", label: "Deep dive" },
        ];
  const selectedDetailTabId = detailTabs.some((tab) => tab.id === detailTabId) ? detailTabId : "overview";
  const detailPanel =
    detailTopic.id === "approval" && selectedDetailTabId === "delivery-modes"
      ? approvalDeliveryModePanel
      : selectedDetailTabId === "overview"
        ? detailTopic.overview
        : deepDiveByTopic[detailTopic.id];

  const activePreviewIds = useMemo(() => new Set(activeTopic.previewNodes), [activeTopic]);
  const panelNodes = useMemo(
    () =>
      buildNodes(
        detailPanel.nodes,
        isNarrow ? detailPanel.positions.mobile : detailPanel.positions.desktop,
      ),
    [detailPanel, isNarrow],
  );
  const panelEdges = useMemo(
    () => getPanelEdges(detailTopic.id, selectedDetailTabId, isNarrow),
    [detailTopic.id, isNarrow, selectedDetailTabId],
  );

  useEffect(() => {
    return () => {
      if (closeTimerRef.current !== null) {
        window.clearTimeout(closeTimerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleClose = () => {
      setIsDetailActive(false);
      setIsDetailClosing(false);
      window.setTimeout(() => lastTriggerRef.current?.focus(), 0);
    };
    dialog.addEventListener("close", handleClose);
    return () => dialog.removeEventListener("close", handleClose);
  }, []);

  const clearCloseTimer = () => {
    if (closeTimerRef.current === null) return;
    window.clearTimeout(closeTimerRef.current);
    closeTimerRef.current = null;
  };
  const finishClose = () => {
    const dialog = dialogRef.current;
    clearCloseTimer();
    if (dialog?.open) {
      dialog.close();
    }
    setIsDetailActive(false);
    setIsDetailClosing(false);
  };
  const openDetail = (topicId: WorkflowTopicId, trigger: HTMLButtonElement) => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    clearCloseTimer();
    lastTriggerRef.current = trigger;
    setActiveTopicId(topicId);
    setDetailTopicId(topicId);
    setDetailTabId("overview");
    setIsDetailClosing(false);
    if (!dialog.open) {
      dialog.showModal();
    }
    setIsDetailActive(true);
  };
  const closeDetail = () => {
    const dialog = dialogRef.current;
    if (!dialog?.open) {
      setIsDetailActive(false);
      setIsDetailClosing(false);
      return;
    }

    if (isDetailClosing) return;

    setIsDetailClosing(true);
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduceMotion) {
      finishClose();
      return;
    }

    closeTimerRef.current = window.setTimeout(finishClose, modalCloseDurationMs);
  };
  const handleDialogClick = (event: MouseEvent<HTMLDialogElement>) => {
    if (event.target === event.currentTarget) {
      closeDetail();
    }
  };

  return (
    <>
      <div className="workflow-workbench">
        <div className="workflow-control-list" aria-label="AI delivery stages">
          {topics.map((topic) => {
            const isActive = topic.id === activeTopicId;
            return (
              <article
                className={`workflow-control workflow-control-${topic.tone}${isActive ? " is-active" : ""}`}
                key={topic.id}
              >
                <button
                  aria-pressed={isActive}
                  className="workflow-control-select"
                  type="button"
                  onClick={() => setActiveTopicId(topic.id)}
                >
                  <span>{topic.meta}</span>
                  <strong>{topic.label}</strong>
                  <small>{topic.summary}</small>
                </button>
                <button
                  className="workflow-control-detail"
                  type="button"
                  onClick={(event) => openDetail(topic.id, event.currentTarget)}
                >
                  Open detail
                </button>
              </article>
            );
          })}
        </div>

        <div className="workflow-flow-card" aria-label="Selected AI delivery workflow preview">
          <div className="workflow-flow-header">
            <span>Selected stage</span>
            <strong>{activeTopic.label}</strong>
            <span className="workflow-open-detail">{activeTopic.detail}</span>
          </div>
          <StaticWorkflowPreview activePreviewIds={activePreviewIds} />
        </div>
      </div>

      <dialog
        ref={dialogRef}
        className={`workflow-detail-dialog${isDetailActive ? " is-open" : ""}${
          isDetailClosing ? " is-closing" : ""
        }`}
        aria-labelledby="workflow-detail-title"
        onClick={handleDialogClick}
        onCancel={(event) => {
          event.preventDefault();
          closeDetail();
        }}
      >
        <div className="workflow-detail-shell">
          <header className="workflow-detail-header">
            <div>
              <span>{detailTopic.label}</span>
              <h3 id="workflow-detail-title">{detailPanel.title}</h3>
            </div>
            <button className="workflow-detail-close" type="button" onClick={closeDetail}>
              Close
            </button>
          </header>

          <div className="workflow-detail-tabs" role="tablist" aria-label="Workflow detail depth">
            {detailTabs.map((tab) => (
              <button
                aria-selected={selectedDetailTabId === tab.id}
                className={selectedDetailTabId === tab.id ? "is-active" : ""}
                key={tab.id}
                role="tab"
                type="button"
                onClick={() => setDetailTabId(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="workflow-detail-body">
            <aside className="workflow-detail-copy">
              <span>{detailPanel.sideTitle}</span>
              <p>{detailPanel.copy}</p>
              {detailTopic.id === "goal" && selectedDetailTabId === "deep-dive" ? (
                <div className="workflow-skill-card">
                  <strong>Agent skill</strong>
                  <p>
                    A reusable local workflow instruction bundle. This project invokes them as
                    <code>$skill-name</code> to make shaping, triage, and Ralph operation repeatable.
                  </p>
                </div>
              ) : null}
              {renderLinks(detailPanel.links)}
            </aside>

            <div className="workflow-detail-visual">
              <div className="workflow-detail-flow" aria-label={detailPanel.flowLabel}>
                {isDetailActive ? (
                  <ReactFlow
                    key={`${detailTopic.id}-${selectedDetailTabId}-${isNarrow ? "mobile" : "desktop"}`}
                    nodes={panelNodes}
                    edges={panelEdges}
                    nodeTypes={nodeTypes}
                    fitView
                    fitViewOptions={{
                      padding:
                        !isNarrow && (detailTopic.id === "test-lane" || selectedDetailTabId === "delivery-modes")
                          ? 0.07
                          : 0.13,
                    }}
                    minZoom={0.22}
                    maxZoom={
                      !isNarrow && (detailTopic.id === "test-lane" || selectedDetailTabId === "delivery-modes")
                        ? 1.45
                        : 1.2
                    }
                    nodesDraggable={false}
                    nodesConnectable={false}
                    elementsSelectable={false}
                    panOnDrag={false}
                    panOnScroll={false}
                    zoomOnScroll={false}
                    zoomOnPinch={false}
                    zoomOnDoubleClick={false}
                    preventScrolling={false}
                    proOptions={{ hideAttribution: true }}
                  >
                    <Background color="rgb(27 35 36 / 0.16)" gap={30} size={1} />
                  </ReactFlow>
                ) : null}
              </div>

              {detailPanel.code ? (
                <div className="workflow-loop-code" aria-label="Workflow model">
                  <span>Workflow model</span>
                  <strong>
                    {detailTopic.id === "build-check"
                      ? "Outer loop over specs, inner loop over failures."
                      : detailTopic.id === "doc-sync"
                        ? "Changed paths drive maintained-doc updates and QA."
                        : "Review first, promote after evidence."}
                  </strong>
                  <pre>
                    <code>{detailPanel.code}</code>
                  </pre>
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </dialog>
    </>
  );
}
