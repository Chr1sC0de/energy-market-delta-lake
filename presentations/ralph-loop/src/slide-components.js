const toneClass = (tone = "neutral") => `tone-${tone}`;

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

const renderChip = (label, tone = "neutral") =>
  `<span class="chip ${toneClass(tone)}">${escapeHtml(label)}</span>`;

const renderSlideHeader = (slide) => `
  <header class="slide-header">
    <p class="eyebrow">${escapeHtml(slide.eyebrow)}</p>
    <h1>${escapeHtml(slide.title)}</h1>
    <p class="lede">${escapeHtml(slide.lede)}</p>
  </header>
`;

const controlStages = [
  {
    id: "queue",
    label: "Queue",
  },
  {
    id: "mode",
    label: "Mode",
  },
  {
    id: "run",
    label: "Run",
  },
  {
    id: "evidence",
    label: "Evidence",
  },
  {
    id: "release",
    label: "Release",
  },
  {
    id: "contain",
    label: "Contain",
  },
];

const renderControlRail = (stage = "map") => `
  <div class="control-rail" aria-label="Operator flow position">
    <span class="control-title">${stage === "map" ? "Flow map" : "Control point"}</span>
    <ol>
      ${controlStages
        .map(
          (item, index) => `
            <li class="${item.id === stage ? "is-active" : ""}">
              <span>${String(index + 1).padStart(2, "0")}</span>
              ${escapeHtml(item.label)}
            </li>
          `,
        )
        .join("")}
    </ol>
  </div>
`;

const renderCallouts = (items = []) => {
  if (items.length === 0) {
    return "";
  }

  return `
    <aside class="callout-strip" aria-label="Key points">
      ${items
        .map(
          (item, index) => `
            <div class="callout fragment ${toneClass(item.tone)}" data-fragment-index="${index + 1}">
              <strong>${escapeHtml(item.label)}</strong>
              <span>${escapeHtml(item.meta)}</span>
            </div>
          `,
        )
        .join("")}
    </aside>
  `;
};

const renderNotes = (notes = []) => {
  if (notes.length === 0) {
    return "";
  }

  return `
    <div class="note-row" aria-label="Canonical terms">
      ${notes.map((note) => renderChip(note, "neutral")).join("")}
    </div>
  `;
};

const renderPath = ({ columns, steps }) => `
  <ol class="flow-path" style="--columns: ${columns ?? steps.length}">
    ${steps
      .map(
        (step, index) => `
          <li class="flow-node fragment ${toneClass(step.tone)}" data-fragment-index="${index + 1}">
            <span class="node-index">${String(index + 1).padStart(2, "0")}</span>
            <strong>${escapeHtml(step.label)}</strong>
            <small>${escapeHtml(step.meta)}</small>
          </li>
        `,
      )
      .join("")}
  </ol>
`;

const renderLoopRing = () => `
  <svg class="loop-ring" viewBox="0 0 1000 360" aria-hidden="true" focusable="false">
    <defs>
      <marker
        id="loop-arrow"
        markerHeight="18"
        markerUnits="userSpaceOnUse"
        markerWidth="18"
        orient="auto"
        refX="16"
        refY="9"
        viewBox="0 0 18 18"
      >
        <path d="M 0 0 L 18 9 L 0 18 z"></path>
      </marker>
    </defs>
    <path class="loop-ring-path loop-ring-top" d="M 110 18 H 890"></path>
    <path class="loop-ring-path loop-ring-right" d="M 982 82 V 278"></path>
    <path class="loop-ring-path loop-ring-bottom" d="M 890 342 H 110"></path>
    <path class="loop-ring-path loop-ring-left" d="M 18 278 V 82"></path>
  </svg>
`;

const renderLoop = ({ center, steps }) => `
  <div class="loop-visual" aria-label="Ralph one-task loop">
    ${renderLoopRing()}
    <div class="loop-core">
      <strong>${escapeHtml(center.label)}</strong>
      <span>${escapeHtml(center.primary)}</span>
      <span>${escapeHtml(center.secondary)}</span>
    </div>
    <ol class="loop-steps">
      ${steps
        .map(
          (step, index) => `
            <li class="loop-step fragment ${toneClass(step.tone)}" data-fragment-index="${index + 1}">
              <span class="loop-index">${String(index + 1).padStart(2, "0")}</span>
              <span class="loop-owner">${escapeHtml(step.owner)}</span>
              <strong>${escapeHtml(step.label)}</strong>
              <small>${escapeHtml(step.meta)}</small>
            </li>
          `,
        )
        .join("")}
    </ol>
  </div>
`;

const renderCommandStack = ({ commands }) => `
  <div class="command-panel" aria-label="Operator commands">
    ${commands
      .map(
        (command, index) => `
          <div class="command-line fragment" data-fragment-index="${index + 1}">
            <span class="prompt">&gt;</span>
            <code>${escapeHtml(command)}</code>
          </div>
        `,
      )
      .join("")}
  </div>
`;

const renderLabels = ({ groups }, issue) => `
  <div class="queue-layout">
    <div class="issue-ticket fragment" data-fragment-index="1">
      <span class="ticket-number">#${escapeHtml(issue.number)}</span>
      <strong>${escapeHtml(issue.title)}</strong>
      <div class="ticket-chips">
        ${renderChip(issue.state, "operator")}
        ${renderChip(issue.delivery, "branch")}
      </div>
    </div>
    <div class="label-grid" aria-label="Label roles">
      ${groups
        .map(
          (group, index) => `
            <div class="label-group fragment ${toneClass(group.tone)}" data-fragment-index="${index + 2}">
              <div>
                <strong>${escapeHtml(group.role)}</strong>
                <span>${escapeHtml(group.purpose)}</span>
              </div>
              <div class="label-chip-list">
                ${group.labels.map((label) => renderChip(label, group.tone)).join("")}
              </div>
            </div>
          `,
        )
        .join("")}
    </div>
  </div>
`;

const renderLanes = ({ lanes }) => `
  <div class="lane-board" aria-label="Delivery mode lanes">
    ${lanes
      .map(
        (lane, laneIndex) => `
          <div class="lane-row fragment ${toneClass(lane.tone)}" data-fragment-index="${laneIndex + 1}">
            <header>
              <span>${escapeHtml(lane.flag)}</span>
              <strong>${escapeHtml(lane.label)}</strong>
            </header>
            <ol style="--lane-columns: ${lane.steps.length}">
              ${lane.steps
                .map(
                  (step, stepIndex) => `
                    <li>
                      <span>${String(stepIndex + 1).padStart(2, "0")}</span>
                      ${escapeHtml(step)}
                    </li>
                  `,
                )
                .join("")}
            </ol>
          </div>
        `,
      )
      .join("")}
  </div>
`;

const renderStateTransition = ({ after, before }) => `
  <div class="state-transition" aria-label="Issue claim transition">
    ${renderIssueState(before, "1")}
    <div class="transition-arrow fragment" data-fragment-index="2">
      <span>Ralph claim</span>
    </div>
    ${renderIssueState(after, "3")}
  </div>
`;

const renderIssueState = (state, fragmentIndex) => `
  <div class="state-card fragment" data-fragment-index="${fragmentIndex}">
    <strong>${escapeHtml(state.label)}</strong>
    <div class="ticket-chips">
      ${state.chips.map((chip) => renderChip(chip, chip.startsWith("delivery") ? "branch" : "operator")).join("")}
    </div>
  </div>
`;

const renderEvidence = ({ items }) => `
  <div class="evidence-stack" aria-label="Review package evidence">
    ${items
      .map(
        (item, index) => `
          <div class="evidence-item fragment ${toneClass(item.tone)}" data-fragment-index="${index + 1}">
            <span class="evidence-rule"></span>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.meta)}</small>
          </div>
        `,
      )
      .join("")}
  </div>
`;

const renderTrust = ({ items }) => `
  <div class="trust-grid" aria-label="Stakeholder trust points">
    ${items
      .map(
        (item, index) => `
          <div class="trust-tile fragment ${toneClass(item.tone)}" data-fragment-index="${index + 1}">
            <span class="trust-marker">${String(index + 1).padStart(2, "0")}</span>
            <strong>${escapeHtml(item.label)}</strong>
            <small>${escapeHtml(item.meta)}</small>
          </div>
        `,
      )
      .join("")}
  </div>
`;

const renderVisual = (slide) => {
  const visual = slide.visual;

  switch (visual.type) {
    case "commands":
      return renderCommandStack(visual);
    case "evidence":
      return renderEvidence(visual);
    case "labels":
      return renderLabels(visual, slide.issue);
    case "lanes":
      return renderLanes(visual);
    case "loop":
      return renderLoop(visual);
    case "path":
      return renderPath(visual);
    case "state":
      return renderStateTransition(visual);
    case "trust":
      return renderTrust(visual);
    default:
      return "";
  }
};

export const renderSlide = (slide) => `
  <section class="slide slide-${escapeHtml(slide.layout)}" id="${escapeHtml(slide.id)}">
    <div class="slide-frame">
      ${renderControlRail(slide.stage)}
      ${renderSlideHeader(slide)}
      <main class="slide-body">
        ${renderVisual(slide)}
        ${renderCallouts(slide.callouts)}
      </main>
      ${renderNotes(slide.notes)}
    </div>
  </section>
`;
