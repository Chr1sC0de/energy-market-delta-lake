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
import { type KeyboardEvent, type MouseEvent, useEffect, useRef, useState } from "react";
import "@xyflow/react/dist/style.css";

const modalCloseDurationMs = 180;

type WorkflowNodeData = {
  detail: string;
  kind: "human" | "ai" | "outcome" | "failure" | "input";
  label: string;
  meta: string;
};

type WorkflowNode = Node<WorkflowNodeData, "workflow">;

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

const workflowSteps: Array<Omit<WorkflowNode, "position">> = [
  {
    id: "human-goal",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Human sets goal",
      detail: "Scope and direction",
      meta: "human",
      kind: "human",
    },
  },
  {
    id: "ralph-starts",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Ralph reads issue",
      detail: "The AI loop starts",
      meta: "Ralph",
      kind: "ai",
    },
  },
  {
    id: "ai-builds",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "AI makes change",
      detail: "Code and docs",
      meta: "AI",
      kind: "ai",
    },
  },
  {
    id: "checks-run",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Checks run",
      detail: "Build and tests",
      meta: "check",
      kind: "outcome",
    },
  },
  {
    id: "ready",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Ready to integrate",
      detail: "Prepared for delivery",
      meta: "handoff",
      kind: "outcome",
    },
  },
  {
    id: "human-approves",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Human approves",
      detail: "Review before delivery",
      meta: "human",
      kind: "human",
    },
  },
];

const desktopPositions: Record<string, WorkflowNode["position"]> = {
  "human-goal": { x: 42, y: 54 },
  "ralph-starts": { x: 286, y: 54 },
  "ai-builds": { x: 530, y: 54 },
  "checks-run": { x: 42, y: 232 },
  ready: { x: 286, y: 232 },
  "human-approves": { x: 530, y: 232 },
};

const mobilePositions: Record<string, WorkflowNode["position"]> = {
  "human-goal": { x: 74, y: 32 },
  "ralph-starts": { x: 74, y: 150 },
  "ai-builds": { x: 74, y: 268 },
  "checks-run": { x: 74, y: 386 },
  ready: { x: 74, y: 504 },
  "human-approves": { x: 74, y: 622 },
};

function buildNodes(positions: Record<string, WorkflowNode["position"]>) {
  return workflowSteps.map((node) => ({
    ...node,
    position: positions[node.id],
    initialWidth: nodeWidth,
    initialHeight: nodeHeight,
    handles: nodeHandles,
  }));
}

const desktopNodes = buildNodes(desktopPositions);
const mobileNodes = buildNodes(mobilePositions);

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

const desktopEdges: Edge[] = withEdgeStyle([
  {
    id: "goal-ralph",
    source: "human-goal",
    sourceHandle: "source-right",
    target: "ralph-starts",
    targetHandle: "target-left",
  },
  {
    id: "ralph-builds",
    source: "ralph-starts",
    sourceHandle: "source-right",
    target: "ai-builds",
    targetHandle: "target-left",
  },
  {
    id: "builds-checks",
    source: "ai-builds",
    sourceHandle: "source-bottom",
    target: "checks-run",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "checks-ready",
    source: "checks-run",
    sourceHandle: "source-right",
    target: "ready",
    targetHandle: "target-left",
  },
  {
    id: "ready-approves",
    source: "ready",
    sourceHandle: "source-right",
    target: "human-approves",
    targetHandle: "target-left",
  },
]);

const mobileEdges: Edge[] = withEdgeStyle([
  {
    id: "goal-ralph-mobile",
    source: "human-goal",
    sourceHandle: "source-bottom",
    target: "ralph-starts",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "ralph-builds-mobile",
    source: "ralph-starts",
    sourceHandle: "source-bottom",
    target: "ai-builds",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "builds-checks-mobile",
    source: "ai-builds",
    sourceHandle: "source-bottom",
    target: "checks-run",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "checks-ready-mobile",
    source: "checks-run",
    sourceHandle: "source-bottom",
    target: "ready",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "ready-approves-mobile",
    source: "ready",
    sourceHandle: "source-bottom",
    target: "human-approves",
    targetHandle: "target-top",
    type: "smoothstep",
  },
]);

const detailSteps: Array<Omit<WorkflowNode, "position">> = [
  {
    id: "specs",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Specs array",
      detail: "Issue, context, checks",
      meta: "input",
      kind: "input",
    },
  },
  {
    id: "each-spec",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "For each spec",
      detail: "Pick the next backing item",
      meta: "outer loop",
      kind: "input",
    },
  },
  {
    id: "goal",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Goal for spec",
      detail: "Current task and context",
      meta: "goal",
      kind: "input",
    },
  },
  {
    id: "ralph-detail",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Ralph works",
      detail: "Edits code and docs",
      meta: "AI",
      kind: "ai",
    },
  },
  {
    id: "detail-checks",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Checks run",
      detail: "Pass or fail",
      meta: "check",
      kind: "outcome",
    },
  },
  {
    id: "detail-ready",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "All specs done",
      detail: "Prepared handoff",
      meta: "exit",
      kind: "outcome",
    },
  },
  {
    id: "detail-human",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Human reviews",
      detail: "Approve or send back",
      meta: "human",
      kind: "human",
    },
  },
  {
    id: "failure",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Failure found",
      detail: "Feeds the inner loop",
      meta: "inner loop",
      kind: "failure",
    },
  },
  {
    id: "next-fix",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Tighten goal",
      detail: "Add failure context",
      meta: "loop",
      kind: "ai",
    },
  },
  {
    id: "spec-complete",
    type: "workflow",
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Spec complete",
      detail: "Next spec or finish",
      meta: "outer loop",
      kind: "outcome",
    },
  },
];

const detailDesktopPositions: Record<string, WorkflowNode["position"]> = {
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

const detailMobilePositions: Record<string, WorkflowNode["position"]> = {
  specs: { x: 74, y: 32 },
  "each-spec": { x: 74, y: 142 },
  goal: { x: 74, y: 252 },
  "ralph-detail": { x: 74, y: 362 },
  "detail-checks": { x: 74, y: 472 },
  failure: { x: 74, y: 582 },
  "next-fix": { x: 74, y: 692 },
  "spec-complete": { x: 74, y: 802 },
  "detail-ready": { x: 74, y: 912 },
  "detail-human": { x: 74, y: 1022 },
};

function buildDetailNodes(positions: Record<string, WorkflowNode["position"]>) {
  return detailSteps.map((node) => ({
    ...node,
    position: positions[node.id],
    initialWidth: nodeWidth,
    initialHeight: nodeHeight,
    handles: nodeHandles,
  }));
}

const detailDesktopNodes = buildDetailNodes(detailDesktopPositions);
const detailMobileNodes = buildDetailNodes(detailMobilePositions);

const detailDesktopEdges: Edge[] = withEdgeStyle([
  {
    id: "specs-each-spec",
    source: "specs",
    sourceHandle: "source-right",
    target: "each-spec",
    targetHandle: "target-left",
  },
  {
    id: "each-spec-goal",
    source: "each-spec",
    sourceHandle: "source-right",
    target: "goal",
    targetHandle: "target-left",
  },
  {
    id: "goal-ralph-detail",
    source: "goal",
    sourceHandle: "source-right",
    target: "ralph-detail",
    targetHandle: "target-left",
  },
  {
    id: "ralph-checks-detail",
    source: "ralph-detail",
    sourceHandle: "source-bottom",
    target: "detail-checks",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "checks-spec-complete-detail",
    source: "detail-checks",
    sourceHandle: "source-left",
    target: "spec-complete",
    targetHandle: "target-right",
  },
  {
    id: "spec-complete-each-spec",
    source: "spec-complete",
    sourceHandle: "source-top",
    target: "each-spec",
    targetHandle: "target-bottom",
    type: "smoothstep",
  },
  {
    id: "spec-complete-ready-detail",
    source: "spec-complete",
    sourceHandle: "source-right",
    target: "detail-ready",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "ready-human-detail",
    source: "detail-ready",
    sourceHandle: "source-right",
    target: "detail-human",
    targetHandle: "target-left",
  },
  {
    id: "checks-failure-detail",
    source: "detail-checks",
    sourceHandle: "source-bottom",
    target: "failure",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "failure-next-fix",
    source: "failure",
    sourceHandle: "source-left",
    target: "next-fix",
    targetHandle: "target-right",
  },
  {
    id: "next-fix-ralph",
    source: "next-fix",
    sourceHandle: "source-top",
    target: "goal",
    targetHandle: "target-bottom",
    type: "smoothstep",
  },
]);

const detailMobileEdges: Edge[] = withEdgeStyle([
  {
    id: "specs-each-spec-mobile-detail",
    source: "specs",
    sourceHandle: "source-bottom",
    target: "each-spec",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "each-spec-goal-mobile-detail",
    source: "each-spec",
    sourceHandle: "source-bottom",
    target: "goal",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "goal-ralph-mobile-detail",
    source: "goal",
    sourceHandle: "source-bottom",
    target: "ralph-detail",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "ralph-checks-mobile-detail",
    source: "ralph-detail",
    sourceHandle: "source-bottom",
    target: "detail-checks",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "checks-failure-mobile-detail",
    source: "detail-checks",
    sourceHandle: "source-bottom",
    target: "failure",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "checks-spec-complete-mobile",
    source: "detail-checks",
    sourceHandle: "source-right",
    target: "spec-complete",
    targetHandle: "target-right",
    type: "smoothstep",
  },
  {
    id: "failure-next-fix-mobile",
    source: "failure",
    sourceHandle: "source-bottom",
    target: "next-fix",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "next-fix-goal-mobile",
    source: "next-fix",
    sourceHandle: "source-right",
    target: "goal",
    targetHandle: "target-right",
    type: "smoothstep",
  },
  {
    id: "spec-complete-each-spec-mobile",
    source: "spec-complete",
    sourceHandle: "source-left",
    target: "each-spec",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "spec-complete-ready-mobile",
    source: "spec-complete",
    sourceHandle: "source-bottom",
    target: "detail-ready",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "ready-human-mobile-detail",
    source: "detail-ready",
    sourceHandle: "source-bottom",
    target: "detail-human",
    targetHandle: "target-top",
    type: "smoothstep",
  },
]);

const workflowLoopCode = `const backingSpecs = [
  issue,
  context,
  acceptanceCriteria,
  checks,
];

for (const spec of backingSpecs) {
  let goal = makeGoal(spec);
  let result = { ok: false };

  while (!result.ok) {
    change = ralph.run(goal);
    result = runChecks(change);

    if (!result.ok) {
      goal = tightenGoal(goal, result);
    }
  }
}

humanReview(change);`;

function WorkflowNode({ data }: NodeProps<WorkflowNode>) {
  return (
    <div className={`workflow-node workflow-node-${data.kind}`}>
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

export default function AutomationWorkflowFlow() {
  const isNarrow = useNarrowWorkflow();
  const [isDetailActive, setIsDetailActive] = useState(false);
  const [isDetailClosing, setIsDetailClosing] = useState(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const closeTimerRef = useRef<number | null>(null);

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
  const openDetail = () => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    clearCloseTimer();
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
  const handleCardKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    openDetail();
  };
  const handleDialogClick = (event: MouseEvent<HTMLDialogElement>) => {
    if (event.target === event.currentTarget) {
      closeDetail();
    }
  };

  return (
    <>
      <div
        className="workflow-flow-card workflow-flow-card-action"
        role="button"
        tabIndex={0}
        aria-label="Open low-level Ralph workflow model"
        onClick={openDetail}
        onKeyDown={handleCardKeyDown}
      >
        <div className="workflow-flow-header">
          <span>High-level workflow</span>
          <strong>Human control, AI execution</strong>
          <span className="workflow-open-detail">Open detail</span>
        </div>
        <div className="workflow-flow">
          <ReactFlow
            nodes={isNarrow ? mobileNodes : desktopNodes}
            edges={isNarrow ? mobileEdges : desktopEdges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.14 }}
            minZoom={0.25}
            maxZoom={1.2}
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
              <span>Low-level workflow</span>
              <h3 id="workflow-detail-title">Ralph runs a nested loop.</h3>
            </div>
            <button className="workflow-detail-close" type="button" onClick={closeDetail}>
              Close
            </button>
          </header>

          <div className="workflow-detail-body">
            <div className="workflow-detail-flow" aria-label="Low-level Ralph workflow model">
              {isDetailActive ? (
                <ReactFlow
                  nodes={isNarrow ? detailMobileNodes : detailDesktopNodes}
                  edges={isNarrow ? detailMobileEdges : detailDesktopEdges}
                  nodeTypes={nodeTypes}
                  fitView
                  fitViewOptions={{ padding: 0.13 }}
                  minZoom={0.22}
                  maxZoom={1.2}
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

            <aside className="workflow-loop-code" aria-label="For loop model">
              <span>For loop model</span>
              <strong>Outer loop over specs, inner loop over failures.</strong>
              <pre>
                <code>{workflowLoopCode}</code>
              </pre>
            </aside>
          </div>
        </div>
      </dialog>
    </>
  );
}
