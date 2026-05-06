# Ralph Keeps Exploratory Branches Outside Automatic Promotion

Ralph publishes **Exploratory delivery** work to a durable **Exploratory
branch** instead of integrating it to `dev` or `main` immediately. The branch is
created from `origin/main`, named `agent/exploratory/issue-N-slug` by default,
pushed to origin after QA, and recorded on the issue with `agent-reviewing`.
The issue remains open until a human review accepts or rejects the work.

Automatic **Promotion** does not merge **Exploratory branches**. Accepted
Exploratory work enters **Promotion** only after a human merges the reviewed
branch to `dev`, comments acceptance evidence that starts with
`Ralph exploratory acceptance completed.`, records the accepted `dev` commit,
removes `agent-reviewing`, and adds `agent-integrated`. Rejected Exploratory
work stays open, removes `agent-reviewing`, adds `ready-for-human`, and records
the review result without adding `agent-integrated`.

## Considered options

- Promote every published **Exploratory branch** automatically: keeps the drain
  moving, but turns exploratory work into unreviewed `main` changes and removes
  the human judgment requested by `## Review focus`.
- Open GitHub draft PRs for Exploratory work: preserves familiar review UI, but
  adds a second queue object while Ralph already uses GitHub Issues as the board
  and **Delivery mode** labels as the routing contract.
- Keep **Exploratory branches** outside automatic **Promotion** until accepted:
  preserves durable review evidence, keeps issue state as the workflow source
  of truth, and lets **Promotion** close only verified work already reachable
  from `dev`.

## Consequences

Exploratory review is an explicit human state transition, not a Ralph drain
state. Ralph may publish the **Exploratory branch**, add `agent-reviewing`,
leave the issue open, and run **Ready issue refresh** for the next queue items,
but it does not decide acceptance or rejection. The `## Review focus` section
is therefore required before a ready `delivery-exploratory` issue can run.

**Promotion** can verify accepted Exploratory work with the same branch-range
evidence model it uses for Gitflow work. The accepted `dev` commit must appear
in the promoted `origin/main..origin/dev` range before Ralph comments Promotion
evidence, replaces `agent-integrated` with `agent-merged`, and closes the issue.
If the acceptance comment is missing or unparseable, **Promotion** warns instead
of silently closing the issue.

Keeping rejected Exploratory work out of `agent-integrated` prevents accidental
closure. Rejection leaves the issue open with `ready-for-human` and a review
comment explaining the next action. Operators can later reshape, re-triage, or
close the issue with normal issue evidence.

## Sync metadata

- `sync.owner`: `agents`
- `sync.sources`:
  - `scripts/ralph.py`
  - `CONTEXT.md`
  - `OPERATOR.md`
  - `docs/agents/ralph-loop.md`
  - `docs/agents/triage-labels.md`
  - `docs/agents/issue-tracker.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure`
  - `python3 -m unittest discover -s tests`
  - `verify decision text matches Exploratory delivery labels, review states, and Promotion evidence`
