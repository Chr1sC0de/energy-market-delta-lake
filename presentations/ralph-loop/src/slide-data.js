const mainPath = [
  {
    label: "Shape",
    meta: "PRD to drafts",
    tone: "operator",
  },
  {
    label: "Triage",
    meta: "labels set",
    tone: "operator",
  },
  {
    label: "Drain",
    meta: "Ralph claims",
    tone: "branch",
  },
  {
    label: "QA",
    meta: "Test lane",
    tone: "validation",
  },
  {
    label: "Review Package",
    meta: "evidence",
    tone: "validation",
  },
  {
    label: "Local integration",
    meta: "target update",
    tone: "branch",
  },
  {
    label: "Promotion",
    meta: "main closes",
    tone: "operator",
  },
];

const mentalModelLoop = [
  {
    label: "Start with work",
    owner: "Operator",
    meta: "A PRD or GitHub Issues defines the task list.",
    tone: "operator",
  },
  {
    label: "Run one task",
    owner: "Ralph",
    meta: "The agent picks one item and makes the change.",
    tone: "branch",
  },
  {
    label: "Check and commit",
    owner: "Ralph",
    meta: "Ralph runs tests and type checks, then commits the change.",
    tone: "validation",
  },
  {
    label: "Review progress",
    owner: "Operator",
    meta: "Progress, logs, and branch state tell you whether to repeat, stop, or promote.",
    tone: "operator",
  },
];

const labelGroups = [
  {
    role: "Category",
    purpose: "What kind of work",
    tone: "neutral",
    labels: ["bug", "enhancement"],
  },
  {
    role: "State",
    purpose: "Queue readiness",
    tone: "operator",
    labels: ["needs-triage", "ready-for-agent", "ready-for-human"],
  },
  {
    role: "Runtime",
    purpose: "Ralph attempt status",
    tone: "validation",
    labels: [
      "agent-running",
      "agent-integrated",
      "agent-merged",
      "agent-reviewing",
      "agent-failed",
    ],
  },
  {
    role: "Delivery mode",
    purpose: "Publication path",
    tone: "branch",
    labels: [
      "delivery-gitflow",
      "delivery-trunk",
      "delivery-exploratory",
    ],
  },
];

const deliveryLanes = [
  {
    label: "Gitflow delivery",
    flag: "Default",
    tone: "branch",
    steps: ["Local integration to dev", "Human dev review", "Promotion to main"],
  },
  {
    label: "Trunk delivery",
    flag: "Opt in",
    tone: "validation",
    steps: ["Small low-risk work", "Local integration to main", "Close issue"],
  },
  {
    label: "Exploratory delivery",
    flag: "Review path",
    tone: "operator",
    steps: ["Exploratory branch", "agent-reviewing", "Human decision"],
  },
];

const qaSteps = [
  {
    label: "Changed files",
    meta: "scope",
    tone: "neutral",
  },
  {
    label: "Select Test lane",
    meta: "Subproject command",
    tone: "branch",
  },
  {
    label: "Run QA",
    meta: "Fast check or lane QA",
    tone: "validation",
  },
  {
    label: "Repair retry",
    meta: "same issue budget",
    tone: "operator",
  },
  {
    label: "Pass evidence",
    meta: "manifest and logs",
    tone: "validation",
  },
];

const evidenceItems = [
  {
    label: "Changed files",
    meta: "final diff",
    tone: "neutral",
  },
  {
    label: "QA results",
    meta: "commands and logs",
    tone: "validation",
  },
  {
    label: "Issue completion review",
    meta: "risk trigger",
    tone: "operator",
  },
  {
    label: "Review package",
    meta: "offline HTML",
    tone: "branch",
  },
];

const integrationLanes = [
  {
    label: "Gitflow",
    flag: "delivery-gitflow",
    tone: "branch",
    steps: [
      "Issue branch",
      "Local integration",
      "dev",
      "agent-integrated",
    ],
  },
  {
    label: "Trunk",
    flag: "delivery-trunk",
    tone: "validation",
    steps: ["Issue branch", "Local integration", "main", "agent-merged"],
  },
  {
    label: "Exploratory",
    flag: "delivery-exploratory",
    tone: "operator",
    steps: [
      "Issue branch",
      "Exploratory branch",
      "agent-reviewing",
      "Open issue",
    ],
  },
];

const failureSteps = [
  {
    label: "QA or review fails",
    meta: "attempt stops",
    tone: "failure",
  },
  {
    label: "agent-failed",
    meta: "issue evidence",
    tone: "failure",
  },
  {
    label: "Logs preserved",
    meta: "manifest and worktree",
    tone: "operator",
  },
  {
    label: "Target unchanged",
    meta: "no push boundary",
    tone: "validation",
  },
];

const trustPoints = [
  {
    label: "Queue control",
    meta: "ready-for-agent gates entry",
    tone: "operator",
  },
  {
    label: "Validation control",
    meta: "Test lane before publication",
    tone: "validation",
  },
  {
    label: "Review control",
    meta: "Review package and dev review",
    tone: "branch",
  },
  {
    label: "Failure control",
    meta: "logs kept, target unchanged",
    tone: "failure",
  },
];

export const slides = [
  {
    id: "ralph-loop",
    eyebrow: "Operator workflow",
    title: "Ralph Loop",
    lede: "Follow one issue from GitHub queue to release evidence.",
    layout: "hero",
    stage: "map",
    visual: {
      type: "path",
      steps: mainPath,
      columns: 7,
    },
    notes: ["GitHub Issues", "Delivery mode", "Test lane", "Local integration"],
  },
  {
    id: "control-system",
    eyebrow: "Ralph primer",
    title: "Ralph Turns A Task List Into Commits",
    lede:
      "Give Ralph scoped work. It takes one task, checks it, records progress, and repeats.",
    layout: "loop",
    stage: "map",
    visual: {
      type: "loop",
      center: {
        label: "One-task loop",
        primary: "You set scope and review progress.",
        secondary: "Ralph repeats the smallest safe unit.",
      },
      steps: mentalModelLoop,
    },
    notes: [
      "Operator workflow",
      "GitHub Issues",
      "Test lane",
      "Integration target",
    ],
  },
  {
    id: "operator-start",
    eyebrow: "Control surface",
    title: "The Operator Starts Here",
    lede: "You shape work and review dev. Ralph runs QA and publishes.",
    layout: "split",
    stage: "queue",
    visual: {
      type: "commands",
      commands: [
        "$shape-issues",
        "$ralph-triage",
        "$ralph-loop drain",
        "review dev",
        "$ralph-loop promote",
      ],
    },
    callouts: [
      {
        label: "Human judgment",
        meta: "shape, triage, dev review",
        tone: "operator",
      },
      {
        label: "Ralph ownership",
        meta: "QA, evidence, publication",
        tone: "branch",
      },
    ],
  },
  {
    id: "queue",
    eyebrow: "GitHub Issues",
    title: "GitHub Issues Are The Queue",
    lede: "One state label opens the queue. One Delivery mode chooses the path.",
    layout: "matrix",
    stage: "queue",
    visual: {
      type: "labels",
      groups: labelGroups,
    },
    issue: {
      number: "124",
      title: "Add review evidence",
      state: "ready-for-agent",
      delivery: "delivery-gitflow",
    },
  },
  {
    id: "delivery-mode",
    eyebrow: "Delivery mode",
    title: "Mode Sets The Path",
    lede: "Gitflow lands on dev. Trunk closes on main. Exploratory waits for review.",
    layout: "lanes",
    stage: "mode",
    visual: {
      type: "lanes",
      lanes: deliveryLanes,
    },
  },
  {
    id: "drain",
    eyebrow: "Drain",
    title: "Ralph Claims The Issue",
    lede: "Ralph swaps ready-for-agent for agent-running.",
    layout: "split",
    stage: "run",
    visual: {
      type: "state",
      before: {
        label: "Ready issue",
        chips: ["ready-for-agent", "delivery-gitflow", "enhancement"],
      },
      after: {
        label: "Running attempt",
        chips: ["agent-running", "delivery-gitflow"],
      },
    },
    callouts: [
      {
        label: "Codex implements",
        meta: "inside Ralph worktree",
        tone: "branch",
      },
      {
        label: "Ralph owns publication",
        meta: "no agent push",
        tone: "operator",
      },
    ],
  },
  {
    id: "local-qa",
    eyebrow: "Test lane",
    title: "QA Before Branch Moves",
    lede: "Ralph validates the changed Subproject before it updates a target.",
    layout: "diagram",
    stage: "run",
    visual: {
      type: "path",
      steps: qaSteps,
      columns: 5,
    },
    notes: ["Fast check", "Commit check", "Push check"],
  },
  {
    id: "review-package",
    eyebrow: "Evidence gate",
    title: "Review Package",
    lede: "Ralph writes the local evidence page before publication.",
    layout: "stack",
    stage: "evidence",
    visual: {
      type: "evidence",
      items: evidenceItems,
    },
    callouts: [
      {
        label: "Risk work gets review",
        meta: "Issue completion review",
        tone: "operator",
      },
      {
        label: "Evidence stays local",
        meta: "offline review-package.html",
        tone: "branch",
      },
    ],
  },
  {
    id: "local-integration",
    eyebrow: "Integration target",
    title: "Local Integration",
    lede: "Ralph lands validated work without a pull request.",
    layout: "lanes",
    stage: "release",
    visual: {
      type: "lanes",
      lanes: integrationLanes,
    },
  },
  {
    id: "promotion",
    eyebrow: "Gitflow release",
    title: "Promotion Closes Gitflow Issues",
    lede: "The Operator reviews dev before Ralph promotes to main.",
    layout: "diagram",
    stage: "release",
    visual: {
      type: "path",
      columns: 5,
      steps: [
        {
          label: "dev reviewed",
          meta: "human checkpoint",
          tone: "operator",
        },
        {
          label: "Promotion",
          meta: "dev to main",
          tone: "branch",
        },
        {
          label: "main updated",
          meta: "verified range",
          tone: "validation",
        },
        {
          label: "agent-merged",
          meta: "runtime label",
          tone: "validation",
        },
        {
          label: "Issue closed",
          meta: "Promotion evidence",
          tone: "operator",
        },
      ],
    },
    notes: ["Gitflow default", "main receives reviewed dev"],
  },
  {
    id: "failure",
    eyebrow: "Contained failure",
    title: "Ralph Contains Failure",
    lede: "A failed attempt leaves evidence and preserves branch targets.",
    layout: "diagram",
    stage: "contain",
    visual: {
      type: "path",
      steps: failureSteps,
      columns: 4,
    },
    callouts: [
      {
        label: "No Integration target update",
        meta: "dev and main stay put",
        tone: "validation",
      },
      {
        label: "Operator gets logs",
        meta: "safe recovery path",
        tone: "operator",
      },
    ],
  },
  {
    id: "demo-path",
    eyebrow: "Demo path",
    title: "One Issue End To End",
    lede: "Start with the default Gitflow path.",
    layout: "runway",
    stage: "map",
    visual: {
      type: "path",
      steps: [
        {
          label: "Issue shaped",
          meta: "source context",
          tone: "operator",
        },
        {
          label: "ready-for-agent",
          meta: "queue entry",
          tone: "operator",
        },
        {
          label: "agent-running",
          meta: "Ralph claim",
          tone: "branch",
        },
        {
          label: "QA passes",
          meta: "Test lane",
          tone: "validation",
        },
        {
          label: "Package ready",
          meta: "Review package",
          tone: "validation",
        },
        {
          label: "dev updated",
          meta: "Local integration",
          tone: "branch",
        },
        {
          label: "dev reviewed",
          meta: "human checkpoint",
          tone: "operator",
        },
        {
          label: "main updated",
          meta: "Promotion",
          tone: "validation",
        },
      ],
      columns: 4,
    },
  },
  {
    id: "trust-points",
    eyebrow: "Stakeholder view",
    title: "Trust Points",
    lede: "Humans keep judgment. Ralph keeps evidence.",
    layout: "stack",
    stage: "evidence",
    visual: {
      type: "trust",
      items: trustPoints,
    },
    callouts: [
      {
        label: "Ready issue refresh",
        meta: "keeps the queue current",
        tone: "branch",
      },
      {
        label: "Review moments",
        meta: "triage, dev review, exploratory decision",
        tone: "operator",
      },
    ],
  },
];
