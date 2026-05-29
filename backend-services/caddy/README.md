# Caddy Portfolio And Reverse Proxy

This Subproject builds the public Caddy image used by the local compose stack
and the deployed AWS edge host. The image serves a static Astro portfolio at
the root URL and keeps the existing Caddy reverse-proxy routes for Dagster,
auth, and Marimo.

## Table of contents

- [What it does](#what-it-does)
- [Astro portfolio](#astro-portfolio)
- [Local usage](#local-usage)
- [Review package media](#review-package-media)
- [Validation](#validation)
- [Related docs](#related-docs)

## What it does

- [Caddyfile](Caddyfile) keeps Caddy as the public entrypoint.
- [Dockerfile](Dockerfile) builds the Astro app, copies `dist/` into
  `/var/www/html`, and then runs the Caddy runtime image.
- The generated root page links to the guest Dagster UI, protected Dagster
  admin UI, and protected Marimo dashboard.
- The generated `/marimo` page is served by Caddy after the existing Marimo
  auth check, then fetches `/marimo/dashboard-registry.json` from the Marimo
  service at runtime. Marimo continues to own the registry JSON endpoint and
  `/marimo/<notebook>/` notebook routes.
- The generated `/theme.css` asset is served from Caddy's static root so Marimo
  pages can keep using the same palette.

## Astro portfolio

The portfolio source lives under [src/](src/):

- [src/pages/index.astro](src/pages/index.astro) composes the page.
- [src/pages/marimo.astro](src/pages/marimo.astro) renders the protected
  portfolio-story dashboard listing shell and loads dashboard registry records
  from Marimo at runtime.
- [src/components/HeroArchitectureFlow.tsx](src/components/HeroArchitectureFlow.tsx)
  owns the invisible first-view controller and deployed runtime detail modal.
  [src/components/HeroArchitectureFallback.astro](src/components/HeroArchitectureFallback.astro)
  renders the visible first-view card so reloads do not swap the architecture
  preview during client hydration.
- [src/components/AutomationWorkflowFlow.tsx](src/components/AutomationWorkflowFlow.tsx)
  renders the stable HTML/SVG preview for human decisions and AI execution,
  with a master-detail selector for goal setting, build/check work,
  **Documentation sync**, **Test lane** evidence, and human approval. Each
  selector opens a focused React Flow detail modal with overview and deep dive
  tabs, including links to repo-local **Agent skills**, Operator docs,
  maintained-doc policy, QA policy docs, and **Delivery mode** context for
  approval.
- [src/components/InfrastructureDiagram.astro](src/components/InfrastructureDiagram.astro)
  renders the recruiter-facing tech stack section grouped by capability area.
- [public/theme.css](public/theme.css) is copied to `/theme.css` during the
  Astro build for the portfolio and Marimo notebook pages.

## Local usage

Install dependencies once from this Subproject directory:

```bash
npm install
```

Run the Astro development server:

```bash
npm run dev
```

Build the static files that the Caddy image serves:

```bash
npm run build
```

The local backend-services compose stack builds this image from
`backend-services/caddy` and serves the generated portfolio at
`https://localhost/`.

## Review package media

Ralph owns the Caddy portfolio and dashboard-listing Review package video
recipe. When an issue changes one of this README's `sync.sources` portfolio or
static-serving inputs, Ralph maps that change to the generated root route `/`,
runs `npm run build` from this Subproject, serves the built `dist/` directory
from the issue worktree, and records desktop and narrow `.webm` videos before
**Local integration**, Trunk push, or Exploratory handoff. When the changed
branch's built Astro output also contains the Caddy-served `/marimo` dashboard
listing route, Ralph records desktop and narrow videos for `/marimo` as sibling
Review package media as well.

The Caddy Subproject does not need a separate browser-review helper. Ralph uses
its generic Review package media helper from `tools/ralph-loop` and stores the
recorded videos next to the Review package in the issue run directory. Build,
serve, missing-route, or capture failures block publication. This is separate
from Marimo notebook media capture for `/marimo/<notebook>/` routes, which
remains owned by the Marimo Review package media recipe.

## Validation

For portfolio-only edits, run:

```bash
npm run build
```

For root docs or cross-Subproject changes, run the relevant repo **Commit
check** surface from the changed Subproject or root, as described in
[AGENTS.md](../../AGENTS.md).

## Related docs

- [Local backend-services stack](../README.md)
- [Marimo notebook services](../marimo/README.md)
- [AWS edge and access docs](../../infrastructure/aws-pulumi/docs/edge-and-access.md)
- [Repository architecture](../../docs/repository/architecture.md)

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `backend-services/caddy/Caddyfile`
  - `backend-services/caddy/Dockerfile`
  - `backend-services/caddy/package.json`
  - `backend-services/caddy/astro.config.mjs`
  - `backend-services/caddy/tsconfig.json`
  - `backend-services/caddy/public/theme.css`
  - `backend-services/caddy/src/pages/index.astro`
  - `backend-services/caddy/src/pages/marimo.astro`
  - `backend-services/caddy/src/components/AutomationWorkflowFlow.tsx`
  - `backend-services/caddy/src/components/HeroArchitectureFallback.astro`
  - `backend-services/caddy/src/components/HeroArchitectureFlow.tsx`
  - `backend-services/caddy/src/components/InfrastructureDiagram.astro`
  - `backend-services/caddy/src/components/ServiceLinks.astro`
  - `backend-services/caddy/src/layouts/PortfolioLayout.astro`
  - `backend-services/caddy/src/styles/site.css`
  - `tools/ralph-loop/src/ralph_loop/cli.py`
  - `tools/ralph-loop/src/ralph_loop/review_package_media.py`
  - `tools/ralph-loop/src/ralph_loop/workflow.py`
- `sync.scope`: `interface, deployment`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" README.md docs backend-services infrastructure tools`
  - `npm run build` from `backend-services/caddy`
  - `verify links, diagrams, commands, paths, ports, env vars, and names`
