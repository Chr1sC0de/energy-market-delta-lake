# Caddy Portfolio And Reverse Proxy

This Subproject builds the public Caddy image used by the local compose stack
and the deployed AWS edge host. The image serves a static Vite + React Router
portfolio at the root URL and keeps the existing Caddy reverse-proxy routes for
Dagster, auth, and Marimo.

## Table of contents

- [What it does](#what-it-does)
- [React Router portfolio](#react-router-portfolio)
- [Local usage](#local-usage)
- [Review package media](#review-package-media)
- [Validation](#validation)
- [Related docs](#related-docs)

## What it does

- [Caddyfile](Caddyfile) keeps Caddy as the public entrypoint.
- [Dockerfile](Dockerfile) builds the Vite app, copies `dist/` into
  `/var/www/html`, and then runs the Caddy runtime image.
- The generated public workspace provides React Router routes for `/` and
  `/login`, with direct root links ordered as public Dagster source map, private
  Dagster admin tools, and restricted dashboards.
  Unknown public portfolio paths redirect back to `/`.
- `/login` posts credentials only to `POST /auth/login`, passes the optional
  `next` query value as the requested return path, and follows only the
  API-returned `redirect_to` path.
- The generated `/theme.css` asset is served from Caddy's static root so Marimo
  pages can use the shared light, readability-safe palette.
- [Caddyfile](Caddyfile) uses a static SPA fallback for public portfolio routes
  while excluding `/marimo*`, `/dagster-webserver*`, `/oauth2*`, `/auth*`,
  `/logout*`, `/_next*`, `/graphql*`, Dagster favicon paths, and manifest paths
  from that fallback.
- [Caddyfile](Caddyfile) proxies the custom FastAPI auth API at `/auth*` and
  `POST /logout` to `DAGSTER_AUTHSERVER` alongside the hosted-OIDC routes used
  by `forward_auth`.
- Failed Dagster admin `forward_auth` checks redirect to the shared custom
  login route at `/login?next=/dagster-webserver/admin`.

## React Router portfolio

The portfolio source lives under [src/](src/):

- [index.html](index.html), [vite.config.ts](vite.config.ts), and
  [src/main.tsx](src/main.tsx) form the Vite + React Router entrypoint.
- [src/App.tsx](src/App.tsx) owns the public workspace, login page, route cards,
  and reactive preview panel for public source map, private admin tools, and
  restricted dashboards.
- [src/data.ts](src/data.ts) keeps legacy public labels and dashboard story
  summaries available for future route expansion.
- [src/styles/site.css](src/styles/site.css) owns the bold single-page visual
  system, responsive spacing, hover/focus states, and reduced-motion fallbacks.
- [src/components/HeroArchitectureFlow.tsx](src/components/HeroArchitectureFlow.tsx)
  and [src/components/AutomationWorkflowFlow.tsx](src/components/AutomationWorkflowFlow.tsx)
  remain available component assets for future richer diagrams; the current
  public workspace uses the route preview in [src/App.tsx](src/App.tsx).
- [public/theme.css](public/theme.css) is copied to `/theme.css` during the
  Vite build for the portfolio and Marimo notebook pages. The shared theme stays
  light-only because Marimo's generated notebook shell owns its own dark-mode
  styling.

## Local usage

Install dependencies once from this Subproject directory:

```bash
npm install
```

Run the Vite development server:

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
branch's built Vite output also contains the Caddy-served `/marimo` dashboard
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

For login-route edits, run the Caddy frontend build check and Playwright login
smoke:

```bash
npm run build
npm run login-smoke
```

When a Ralph issue requires this login-route check, declare it as
`- QA: npm run build && npm run login-smoke`. Ralph then runs the command from
this Subproject during formal QA and persists the command, cwd, status, and log
path in the issue run manifest and Review package evidence. Manual smoke
commands run only inside the implementation pass remain Codex implementation
logs.

Ralph treats this declaration as required before `ready-for-agent` for issue
contracts that change `Caddyfile` redirects to `/login?next=...`, shared
`/login` route behavior, or `/auth/login` proxy/login form behavior.
Portfolio-only Caddy edits can still declare and run only `npm run build`.

For screenshot-based browser review, this Subproject includes Playwright as a
development dependency. Install the Chromium browser once, then review the local
Vite preview route:

```bash
npx playwright install chromium
npm run preview -- --host 127.0.0.1 --port 4173
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
  - `backend-services/caddy/index.html`
  - `backend-services/caddy/vite.config.ts`
  - `backend-services/caddy/tsconfig.json`
  - `backend-services/caddy/scripts/login-smoke.mjs`
  - `backend-services/caddy/public/theme.css`
  - `backend-services/caddy/src/App.tsx`
  - `backend-services/caddy/src/data.ts`
  - `backend-services/caddy/src/main.tsx`
  - `backend-services/caddy/src/components/AutomationWorkflowFlow.tsx`
  - `backend-services/caddy/src/components/HeroArchitectureFlow.tsx`
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
