import type { LucideIcon } from "lucide-react";
import {
  Activity,
  BookOpenCheck,
  Boxes,
  Cable,
  DatabaseZap,
  GitMerge,
  Landmark,
  LineChart,
  Map,
  RadioTower,
  Route,
  ShieldCheck,
} from "lucide-react";

export type AtlasRouteId =
  | "source"
  | "curation"
  | "notebooks"
  | "evidence"
  | "delivery";

export type AtlasRoute = {
  coordinate: string;
  description: string;
  href: string;
  icon: LucideIcon;
  id: AtlasRouteId;
  label: string;
  metric: string;
  status: string;
  title: string;
};

export type MarketTheatreStage = {
  description: string;
  evidenceItems: string[];
  href: string;
  icon: LucideIcon;
  id: "source" | "curation" | "notebooks" | "evidence";
  label: string;
  sourcePath: string;
  status: string;
  summary: string;
  targetRoute: string;
  title: string;
  tokens: string[];
};

export type StoryGroup = {
  audience: string;
  description: string;
  href: string;
  label: string;
  status: "Available" | "Planned" | "Preview";
  title: string;
};

export const serviceLinks = [
  {
    href: "/marimo",
    label: "Dashboards",
    meta: "prices, flows, status",
  },
  {
    href: "/dagster-webserver/guest",
    label: "Source map",
    meta: "trace each number",
  },
  {
    href: "/dagster-webserver/admin",
    label: "Admin tools",
    meta: "maintainer access",
  },
];

export const atlasRoutes: AtlasRoute[] = [
  {
    coordinate: "Market reports",
    description:
      "Follow public gas market reports into dashboard-ready records.",
    href: "#journey",
    icon: RadioTower,
    id: "source",
    label: "Sources",
    metric: "AEMO",
    status: "covered",
    title: "Source records",
  },
  {
    coordinate: "Clean data",
    description:
      "Open the asset map to see the checks behind current market views.",
    href: "/dagster-webserver/guest",
    icon: DatabaseZap,
    id: "curation",
    label: "Curation",
    metric: "Refresh",
    status: "running",
    title: "Data checks",
  },
  {
    coordinate: "Dashboards",
    description:
      "Open dashboard views for prices, flows, capacity, storage, and health.",
    href: "/marimo",
    icon: LineChart,
    id: "notebooks",
    label: "Dashboards",
    metric: "Gallery",
    status: "available",
    title: "Market views",
  },
  {
    coordinate: "Trust trail",
    description:
      "Review source labels, current-data checks, protected tools, and change records.",
    href: "#trust",
    icon: ShieldCheck,
    id: "evidence",
    label: "Evidence",
    metric: "Evidence",
    status: "visible",
    title: "Trust checks",
  },
  {
    coordinate: "Admin",
    description:
      "Use the protected route when a maintainer needs to inspect operations.",
    href: "/dagster-webserver/admin",
    icon: GitMerge,
    id: "delivery",
    label: "Delivery",
    metric: "Protected",
    status: "restricted",
    title: "Operations",
  },
];

export const marketTheatreStages: MarketTheatreStage[] = [
  {
    evidenceItems: [
      "Price and schedule reports",
      "Flow, storage, and capacity records",
      "Market notices and operating updates",
    ],
    description:
      "The platform starts with public market publications, so each view can point back to a known public source.",
    href: "#journey",
    icon: RadioTower,
    id: "source",
    label: "Reports",
    sourcePath: "AEMO public market publications",
    status: "covered",
    summary:
      "Market records enter with their origin visible, not hidden in a spreadsheet folder.",
    targetRoute: "Clean source records",
    title: "Reports arrive",
    tokens: ["Prices", "Schedules", "Flows", "Capacity", "Public reports"],
  },
  {
    evidenceItems: [
      "Fresh reports are checked before they appear in views",
      "Prices, flows, locations, and dates are connected",
      "Dashboard labels stay tied to source records",
    ],
    description:
      "The platform checks new files and connects related records before anyone uses them.",
    href: "/dagster-webserver/guest",
    icon: DatabaseZap,
    id: "curation",
    label: "Clean",
    sourcePath: "checked source records",
    status: "running",
    summary:
      "The platform turns report files into joined market data that can be reused.",
    targetRoute: "Market tables",
    title: "The platform checks the data",
    tokens: ["Refresh", "Checks", "Joined records", "Labels", "Coverage"],
  },
  {
    evidenceItems: [
      "Market views explain price, schedules, settlement, and capacity",
      "Operations views show flow, storage, forecasts, and notices",
      "Trust views show health, freshness, coverage, and source links",
    ],
    description:
      "Dashboards group the market into practical questions, so you can start with the answer before drilling into tables.",
    href: "/marimo",
    icon: LineChart,
    id: "notebooks",
    label: "Views",
    sourcePath: "clean market records",
    status: "available",
    summary:
      "Dashboard views translate market data into prices, flows, capacity, storage, and health.",
    targetRoute: "Dashboard gallery",
    title: "Dashboards answer the question",
    tokens: ["Prices", "Flow", "Storage", "Capacity", "Health"],
  },
  {
    evidenceItems: [
      "Source labels show where the dashboard values came from",
      "Current-data checks show whether the view is ready",
      "Screenshots and checks support each visible change",
    ],
    description:
      "Source labels and status checks stay near the dashboard, so you can judge the answer without reading technical notes.",
    href: "#trust",
    icon: ShieldCheck,
    id: "evidence",
    label: "Trust",
    sourcePath: "source labels, freshness checks, and change records",
    status: "visible",
    summary:
      "The page keeps confidence signals near the numbers, not buried in an implementation page.",
    targetRoute: "Trust checks",
    title: "Evidence stays close",
    tokens: ["Sources", "Current data", "Access", "Review", "Changes"],
  },
];

export const dashboardStories: StoryGroup[] = [
  {
    audience: "Market readers",
    description:
      "Track prices, scheduled quantities, market movement, and settlement notes without opening raw files.",
    href: "/marimo",
    label: "Market",
    status: "Available",
    title: "What changed in the market?",
  },
  {
    audience: "Operators",
    description:
      "See flows, storage levels, capacity outlooks, and notices in one operating view.",
    href: "/marimo",
    label: "Operations",
    status: "Available",
    title: "Is the system moving as expected?",
  },
  {
    audience: "Reviewers",
    description:
      "Check whether recent data arrived, source links are visible, and the dashboard is ready to use.",
    href: "/marimo",
    label: "Trust",
    status: "Available",
    title: "Can I trust this view today?",
  },
  {
    audience: "Stakeholders",
    description:
      "Connect market language to assets, participants, and dashboard concepts.",
    href: "/marimo",
    label: "Concepts",
    status: "Planned",
    title: "What does this market term mean?",
  },
];

export const platformLayers = [
  {
    icon: Cable,
    label: "Ingestion",
    text: "AEMO gas publications and public report files enter bounded bronze assets.",
  },
  {
    icon: Boxes,
    label: "Modeling",
    text: "Silver gas_model assets normalize operational, schedule, capacity, settlement, and lineage tables.",
  },
  {
    icon: Map,
    label: "Market context",
    text: "Generated gold context and glossary entries keep dashboard language tied to source material.",
  },
  {
    icon: Landmark,
    label: "Access",
    text: "Caddy serves static public routes and proxies Dagster, OAuth, and Marimo paths.",
  },
];

export const deliverySteps = [
  "Source labels stay attached to the dashboard story.",
  "Current-data and coverage checks show when a view is ready.",
  "Protected tools keep admin actions away from public browsing.",
  "Screenshots and checks make visible changes easier to inspect.",
];

export const designBrief = {
  audience:
    "Primary: nontechnical stakeholders. Secondary: operators and energy-market analysts.",
  focalPoint:
    "A Market atlas route scene connects sources, curated data, notebooks, evidence, and delivery waypoints.",
  interaction:
    "Route spotlight buttons and cards share one active route state, exposing how each path links source evidence to dashboard review.",
  tone: "Industrial, technical, dense, high-trust, and specific to Australian energy market analytics.",
  typography:
    "Editorial serif headings, compact mono labels, clear sans body text, and stable tabular numerals.",
  visualReferences:
    "Bloomberg Terminal density, Linear typography discipline, Stripe spacing, TradingView analytical structure, and Apple-style restrained motion.",
};

export const routeIconMap = {
  Activity,
  BookOpenCheck,
  Route,
};
