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

type ArchitectureNodeData = {
  detail: string;
  label: string;
  meta: string;
  tone: "blue" | "green" | "amber" | "red" | "slate";
};

type ArchitectureNode = Node<ArchitectureNodeData, "architecture">;
type ArchitectureGroupNodeData = {
  detail: string;
  label: string;
  tone: ArchitectureNodeData["tone"];
};
type ArchitectureGroupNode = Node<ArchitectureGroupNodeData, "architectureGroup">;
type ArchitectureDetailNode = ArchitectureNode | ArchitectureGroupNode;

const nodeWidth = 156;
const nodeHeight = 78;
const detailNodeWidth = 176;
const detailNodeHeight = 86;
const layoutOffsetX = 64;
const layoutOffsetY = 25;

function createNodeHandles(width: number, height: number) {
  return [
    {
      id: "target-left",
      type: "target",
      position: Position.Left,
      x: 0,
      y: height / 2,
      width: 1,
      height: 1,
    },
    {
      id: "source-right",
      type: "source",
      position: Position.Right,
      x: width,
      y: height / 2,
      width: 1,
      height: 1,
    },
    {
      id: "source-left",
      type: "source",
      position: Position.Left,
      x: 0,
      y: height / 2,
      width: 1,
      height: 1,
    },
    {
      id: "target-right",
      type: "target",
      position: Position.Right,
      x: width,
      y: height / 2,
      width: 1,
      height: 1,
    },
    {
      id: "source-top",
      type: "source",
      position: Position.Top,
      x: width / 2,
      y: 0,
      width: 1,
      height: 1,
    },
    {
      id: "target-top",
      type: "target",
      position: Position.Top,
      x: width / 2,
      y: 0,
      width: 1,
      height: 1,
    },
    {
      id: "source-bottom",
      type: "source",
      position: Position.Bottom,
      x: width / 2,
      y: height,
      width: 1,
      height: 1,
    },
    {
      id: "target-bottom",
      type: "target",
      position: Position.Bottom,
      x: width / 2,
      y: height,
      width: 1,
      height: 1,
    },
  ] satisfies NonNullable<ArchitectureNode["handles"]>;
}

const nodeHandles = createNodeHandles(nodeWidth, nodeHeight);
const detailNodeHandles = createNodeHandles(detailNodeWidth, detailNodeHeight);

const nodes: ArchitectureNode[] = ([
  {
    id: "aemo",
    type: "architecture",
    position: { x: layoutOffsetX + 20, y: layoutOffsetY + 78 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "AEMO files",
      detail: "Market source inputs",
      meta: "source",
      tone: "green",
    },
  },
  {
    id: "dagster-assets",
    type: "architecture",
    position: { x: layoutOffsetX + 224, y: layoutOffsetY + 78 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Dagster assets",
      detail: "Orchestrated ETL",
      meta: "runtime",
      tone: "slate",
    },
  },
  {
    id: "delta",
    type: "architecture",
    position: { x: layoutOffsetX + 428, y: layoutOffsetY + 78 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Delta lake",
      detail: "Curated tables",
      meta: "storage",
      tone: "green",
    },
  },
  {
    id: "caddy",
    type: "architecture",
    position: { x: layoutOffsetX + 20, y: layoutOffsetY + 254 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Caddy edge",
      detail: "Public entrypoint",
      meta: "access",
      tone: "blue",
    },
  },
  {
    id: "dagster-ui",
    type: "architecture",
    position: { x: layoutOffsetX + 224, y: layoutOffsetY + 216 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Dagster UI",
      detail: "Guest and admin",
      meta: "service",
      tone: "blue",
    },
  },
  {
    id: "marimo",
    type: "architecture",
    position: { x: layoutOffsetX + 224, y: layoutOffsetY + 330 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "Marimo",
      detail: "Protected notebooks",
      meta: "service",
      tone: "green",
    },
  },
  {
    id: "delivery",
    type: "architecture",
    position: { x: layoutOffsetX + 428, y: layoutOffsetY + 254 },
    width: nodeWidth,
    height: nodeHeight,
    data: {
      label: "AI delivery system",
      detail: "Checked changes",
      meta: "automation",
      tone: "slate",
    },
  },
] as ArchitectureNode[]).map((node) => ({
  ...node,
  initialWidth: nodeWidth,
  initialHeight: nodeHeight,
  handles: nodeHandles,
}));

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

const edges: Edge[] = withEdgeStyle([
  {
    id: "aemo-dagster",
    source: "aemo",
    sourceHandle: "source-right",
    target: "dagster-assets",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "dagster-delta",
    source: "dagster-assets",
    sourceHandle: "source-right",
    target: "delta",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "caddy-dagster",
    source: "caddy",
    sourceHandle: "source-right",
    target: "dagster-ui",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "caddy-marimo",
    source: "caddy",
    sourceHandle: "source-right",
    target: "marimo",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "delivery-dagster",
    source: "delivery",
    sourceHandle: "source-left",
    target: "dagster-assets",
    targetHandle: "target-right",
    type: "smoothstep",
  },
]);

type DetailLayoutName = "desktop" | "tablet" | "mobile";
type DetailGroupConfig = {
  detail: string;
  height: number;
  id: string;
  label: string;
  position: ArchitectureGroupNode["position"];
  tone: ArchitectureNodeData["tone"];
  width: number;
};
type DetailNodePosition = {
  parentId: string;
  x: number;
  y: number;
};
type DetailLayout = {
  groups: DetailGroupConfig[];
  positions: Record<string, DetailNodePosition>;
};

const detailSteps: Array<Omit<ArchitectureNode, "position">> = [
  {
    id: "browser",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Browser",
      detail: "Portfolio and apps",
      meta: "public",
      tone: "blue",
    },
  },
  {
    id: "dns",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Route 53",
      detail: "DNS and HTTPS",
      meta: "entry",
      tone: "blue",
    },
  },
  {
    id: "edge",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Caddy edge",
      detail: "Public proxy",
      meta: "edge",
      tone: "blue",
    },
  },
  {
    id: "auth",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Auth check",
      detail: "Protects admin apps",
      meta: "access",
      tone: "blue",
    },
  },
  {
    id: "dagster-ui",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Dagster UI",
      detail: "Admin and guest",
      meta: "service",
      tone: "blue",
    },
  },
  {
    id: "marimo",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Marimo",
      detail: "Protected notebooks",
      meta: "service",
      tone: "green",
    },
  },
  {
    id: "aemo",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "AEMO files",
      detail: "Market source data",
      meta: "source",
      tone: "green",
    },
  },
  {
    id: "dagster-work",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "Dagster work",
      detail: "Daemon and user code",
      meta: "runtime",
      tone: "slate",
    },
  },
  {
    id: "s3",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "S3 Delta lake",
      detail: "Curated tables",
      meta: "data",
      tone: "green",
    },
  },
  {
    id: "postgres",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "PostgreSQL",
      detail: "Dagster state",
      meta: "state",
      tone: "green",
    },
  },
  {
    id: "dynamodb",
    type: "architecture",
    width: detailNodeWidth,
    height: detailNodeHeight,
    data: {
      label: "DynamoDB",
      detail: "Delta lock table",
      meta: "state",
      tone: "green",
    },
  },
];

const detailLayouts: Record<DetailLayoutName, DetailLayout> = {
  desktop: {
    groups: [
      {
        id: "group-public",
        label: "Public access",
        detail: "Browser to protected routes",
        tone: "blue",
        position: { x: 20, y: 20 },
        width: 1050,
        height: 200,
      },
      {
        id: "group-private",
        label: "Private services",
        detail: "Dagster, Marimo, and source work",
        tone: "slate",
        position: { x: 20, y: 270 },
        width: 1050,
        height: 320,
      },
      {
        id: "group-data",
        label: "Data and state",
        detail: "Tables, run state, and locks",
        tone: "green",
        position: { x: 20, y: 640 },
        width: 1050,
        height: 200,
      },
    ],
    positions: {
      browser: { parentId: "group-public", x: 30, y: 76 },
      dns: { parentId: "group-public", x: 286, y: 76 },
      edge: { parentId: "group-public", x: 542, y: 76 },
      auth: { parentId: "group-public", x: 798, y: 76 },
      "dagster-ui": { parentId: "group-private", x: 542, y: 76 },
      marimo: { parentId: "group-private", x: 798, y: 76 },
      aemo: { parentId: "group-private", x: 30, y: 190 },
      "dagster-work": { parentId: "group-private", x: 286, y: 190 },
      postgres: { parentId: "group-data", x: 542, y: 76 },
      s3: { parentId: "group-data", x: 798, y: 76 },
      dynamodb: { parentId: "group-data", x: 286, y: 76 },
    },
  },
  tablet: {
    groups: [
      {
        id: "group-public",
        label: "Public access",
        detail: "Browser to protected routes",
        tone: "blue",
        position: { x: 20, y: 20 },
        width: 500,
        height: 325,
      },
      {
        id: "group-private",
        label: "Private services",
        detail: "Dagster, Marimo, and source work",
        tone: "slate",
        position: { x: 20, y: 395 },
        width: 500,
        height: 405,
      },
      {
        id: "group-data",
        label: "Data and state",
        detail: "Tables, run state, and locks",
        tone: "green",
        position: { x: 20, y: 850 },
        width: 500,
        height: 330,
      },
    ],
    positions: {
      browser: { parentId: "group-public", x: 34, y: 76 },
      dns: { parentId: "group-public", x: 290, y: 76 },
      edge: { parentId: "group-public", x: 34, y: 206 },
      auth: { parentId: "group-public", x: 290, y: 206 },
      "dagster-ui": { parentId: "group-private", x: 34, y: 76 },
      marimo: { parentId: "group-private", x: 290, y: 76 },
      aemo: { parentId: "group-private", x: 34, y: 250 },
      "dagster-work": { parentId: "group-private", x: 290, y: 250 },
      postgres: { parentId: "group-data", x: 34, y: 76 },
      s3: { parentId: "group-data", x: 290, y: 76 },
      dynamodb: { parentId: "group-data", x: 34, y: 206 },
    },
  },
  mobile: {
    groups: [
      {
        id: "group-public",
        label: "Public access",
        detail: "Browser to protected routes",
        tone: "blue",
        position: { x: 20, y: 20 },
        width: 250,
        height: 545,
      },
      {
        id: "group-private",
        label: "Private services",
        detail: "Dagster, Marimo, and source work",
        tone: "slate",
        position: { x: 20, y: 620 },
        width: 250,
        height: 545,
      },
      {
        id: "group-data",
        label: "Data and state",
        detail: "Tables, run state, and locks",
        tone: "green",
        position: { x: 20, y: 1220 },
        width: 250,
        height: 420,
      },
    ],
    positions: {
      browser: { parentId: "group-public", x: 37, y: 76 },
      dns: { parentId: "group-public", x: 37, y: 190 },
      edge: { parentId: "group-public", x: 37, y: 304 },
      auth: { parentId: "group-public", x: 37, y: 418 },
      "dagster-ui": { parentId: "group-private", x: 37, y: 76 },
      marimo: { parentId: "group-private", x: 37, y: 190 },
      aemo: { parentId: "group-private", x: 37, y: 304 },
      "dagster-work": { parentId: "group-private", x: 37, y: 418 },
      postgres: { parentId: "group-data", x: 37, y: 76 },
      s3: { parentId: "group-data", x: 37, y: 190 },
      dynamodb: { parentId: "group-data", x: 37, y: 304 },
    },
  },
};

function buildDetailNodes(layout: DetailLayout): ArchitectureDetailNode[] {
  const groupNodes = layout.groups.map((group) => ({
    id: group.id,
    type: "architectureGroup",
    position: group.position,
    width: group.width,
    height: group.height,
    style: {
      width: group.width,
      height: group.height,
    },
    data: {
      label: group.label,
      detail: group.detail,
      tone: group.tone,
    },
    selectable: false,
  })) satisfies ArchitectureGroupNode[];

  const childNodes = detailSteps.map((node) => ({
    ...node,
    parentId: layout.positions[node.id].parentId,
    extent: "parent" as const,
    position: {
      x: layout.positions[node.id].x,
      y: layout.positions[node.id].y,
    },
    initialWidth: detailNodeWidth,
    initialHeight: detailNodeHeight,
    handles: detailNodeHandles,
  })) satisfies ArchitectureNode[];

  return [...groupNodes, ...childNodes];
}

const detailNodesByLayout = {
  desktop: buildDetailNodes(detailLayouts.desktop),
  tablet: buildDetailNodes(detailLayouts.tablet),
  mobile: buildDetailNodes(detailLayouts.mobile),
} satisfies Record<DetailLayoutName, ArchitectureDetailNode[]>;

const detailDesktopEdges: Edge[] = withEdgeStyle([
  {
    id: "browser-dns",
    source: "browser",
    sourceHandle: "source-right",
    target: "dns",
    targetHandle: "target-left",
  },
  {
    id: "dns-edge",
    source: "dns",
    sourceHandle: "source-right",
    target: "edge",
    targetHandle: "target-left",
  },
  {
    id: "edge-auth",
    source: "edge",
    sourceHandle: "source-right",
    target: "auth",
    targetHandle: "target-left",
  },
  {
    id: "auth-dagster-ui",
    source: "auth",
    sourceHandle: "source-bottom",
    target: "dagster-ui",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "auth-marimo",
    source: "auth",
    sourceHandle: "source-bottom",
    target: "marimo",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-ui-postgres",
    source: "dagster-ui",
    sourceHandle: "source-bottom",
    target: "postgres",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "marimo-s3",
    source: "marimo",
    sourceHandle: "source-bottom",
    target: "s3",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "aemo-dagster-work",
    source: "aemo",
    sourceHandle: "source-right",
    target: "dagster-work",
    targetHandle: "target-left",
  },
  {
    id: "dagster-work-s3",
    source: "dagster-work",
    sourceHandle: "source-right",
    target: "s3",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "dagster-work-dynamodb",
    source: "dagster-work",
    sourceHandle: "source-bottom",
    target: "dynamodb",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-postgres",
    source: "dagster-work",
    sourceHandle: "source-right",
    target: "postgres",
    targetHandle: "target-left",
    type: "smoothstep",
  },
]);

const detailTabletEdges: Edge[] = withEdgeStyle([
  {
    id: "browser-dns-tablet",
    source: "browser",
    sourceHandle: "source-right",
    target: "dns",
    targetHandle: "target-left",
  },
  {
    id: "dns-edge-tablet",
    source: "dns",
    sourceHandle: "source-left",
    target: "edge",
    targetHandle: "target-right",
    type: "smoothstep",
  },
  {
    id: "edge-auth-tablet",
    source: "edge",
    sourceHandle: "source-right",
    target: "auth",
    targetHandle: "target-left",
  },
  {
    id: "auth-dagster-ui-tablet",
    source: "auth",
    sourceHandle: "source-left",
    target: "dagster-ui",
    targetHandle: "target-left",
    type: "smoothstep",
  },
  {
    id: "auth-marimo-tablet",
    source: "auth",
    sourceHandle: "source-bottom",
    target: "marimo",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "aemo-dagster-work-tablet",
    source: "aemo",
    sourceHandle: "source-right",
    target: "dagster-work",
    targetHandle: "target-left",
  },
  {
    id: "dagster-ui-postgres-tablet",
    source: "dagster-ui",
    sourceHandle: "source-bottom",
    target: "postgres",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "marimo-s3-tablet",
    source: "marimo",
    sourceHandle: "source-bottom",
    target: "s3",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-s3-tablet",
    source: "dagster-work",
    sourceHandle: "source-bottom",
    target: "s3",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-dynamodb-tablet",
    source: "dagster-work",
    sourceHandle: "source-left",
    target: "dynamodb",
    targetHandle: "target-right",
    type: "smoothstep",
  },
  {
    id: "dagster-work-postgres-tablet",
    source: "dagster-work",
    sourceHandle: "source-left",
    target: "postgres",
    targetHandle: "target-right",
    type: "smoothstep",
  },
]);

const detailMobileEdges: Edge[] = withEdgeStyle([
  {
    id: "browser-dns-mobile",
    source: "browser",
    sourceHandle: "source-bottom",
    target: "dns",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dns-edge-mobile",
    source: "dns",
    sourceHandle: "source-bottom",
    target: "edge",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "edge-auth-mobile",
    source: "edge",
    sourceHandle: "source-bottom",
    target: "auth",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "auth-dagster-ui-mobile",
    source: "auth",
    sourceHandle: "source-bottom",
    target: "dagster-ui",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "auth-marimo-mobile",
    source: "auth",
    sourceHandle: "source-bottom",
    target: "marimo",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "aemo-dagster-work-mobile",
    source: "aemo",
    sourceHandle: "source-bottom",
    target: "dagster-work",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-ui-postgres-mobile",
    source: "dagster-ui",
    sourceHandle: "source-bottom",
    target: "postgres",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "marimo-s3-mobile",
    source: "marimo",
    sourceHandle: "source-bottom",
    target: "s3",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-s3-mobile",
    source: "dagster-work",
    sourceHandle: "source-bottom",
    target: "s3",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-dynamodb-mobile",
    source: "dagster-work",
    sourceHandle: "source-bottom",
    target: "dynamodb",
    targetHandle: "target-top",
    type: "smoothstep",
  },
  {
    id: "dagster-work-postgres-mobile",
    source: "dagster-work",
    sourceHandle: "source-left",
    target: "postgres",
    targetHandle: "target-right",
    type: "smoothstep",
  },
]);

const detailEdgesByLayout = {
  desktop: detailDesktopEdges,
  tablet: detailTabletEdges,
  mobile: detailMobileEdges,
} satisfies Record<DetailLayoutName, Edge[]>;

function ArchitectureNode({ data }: NodeProps<ArchitectureNode>) {
  return (
    <div className={`architecture-node architecture-node-${data.tone}`}>
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

function ArchitectureGroup({ data }: NodeProps<ArchitectureGroupNode>) {
  return (
    <div className={`architecture-group-node architecture-group-node-${data.tone}`}>
      <span>{data.label}</span>
      <small>{data.detail}</small>
    </div>
  );
}

const nodeTypes = {
  architecture: ArchitectureNode,
  architectureGroup: ArchitectureGroup,
};

function useArchitectureLayout() {
  const [layoutName, setLayoutName] = useState<DetailLayoutName>("desktop");

  useEffect(() => {
    const mobileQuery = window.matchMedia("(max-width: 700px)");
    const tabletQuery = window.matchMedia("(max-width: 1100px)");
    const update = () => {
      if (mobileQuery.matches) {
        setLayoutName("mobile");
        return;
      }

      if (tabletQuery.matches) {
        setLayoutName("tablet");
        return;
      }

      setLayoutName("desktop");
    };

    update();
    mobileQuery.addEventListener("change", update);
    tabletQuery.addEventListener("change", update);
    return () => {
      mobileQuery.removeEventListener("change", update);
      tabletQuery.removeEventListener("change", update);
    };
  }, []);

  return layoutName;
}

export default function HeroArchitectureFlow() {
  const layoutName = useArchitectureLayout();
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
        className="architecture-flow-card architecture-flow-card-action"
        role="button"
        tabIndex={0}
        aria-label="Open deployed runtime architecture detail"
        onClick={openDetail}
        onKeyDown={handleCardKeyDown}
      >
        <div className="architecture-flow-header">
          <span>Architecture overview</span>
          <strong>Public edge to data products</strong>
          <span className="architecture-open-detail">Open detail</span>
        </div>
        <div className="architecture-flow">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            fitView
            fitViewOptions={{ padding: 0.12 }}
            minZoom={0.8}
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
            <Background color="rgb(27 35 36 / 0.16)" gap={28} size={1} />
          </ReactFlow>
        </div>
      </div>

      <dialog
        ref={dialogRef}
        className={`architecture-detail-dialog${isDetailActive ? " is-open" : ""}${
          isDetailClosing ? " is-closing" : ""
        }`}
        aria-labelledby="architecture-detail-title"
        onClick={handleDialogClick}
        onCancel={(event) => {
          event.preventDefault();
          closeDetail();
        }}
      >
        <div className="architecture-detail-shell">
          <header className="architecture-detail-header">
            <div>
              <span>Deployed runtime</span>
              <h3 id="architecture-detail-title">Public entry, private services, shared state.</h3>
            </div>
            <button className="architecture-detail-close" type="button" onClick={closeDetail}>
              Close
            </button>
          </header>

          <div className="architecture-detail-body">
            <div className="architecture-detail-flow" aria-label="Low-level deployed runtime architecture">
              {isDetailActive ? (
                <ReactFlow
                  nodes={detailNodesByLayout[layoutName]}
                  edges={detailEdgesByLayout[layoutName]}
                  nodeTypes={nodeTypes}
                  fitView
                  fitViewOptions={{ padding: layoutName === "desktop" ? 0.08 : 0.04 }}
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
          </div>
        </div>
      </dialog>
    </>
  );
}
