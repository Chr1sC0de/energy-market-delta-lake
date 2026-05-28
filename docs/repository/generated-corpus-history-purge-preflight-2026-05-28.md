# Generated Corpus History Purge Preflight

This report is the non-destructive preflight for GitHub issue #280,
`all-ref generated-corpus purge preflight`. It prepares evidence for a later
purge execution issue and does not rewrite history, delete refs, run `git gc`,
or force-push `origin`.

Preflight timestamp: `2026-05-28T06:17:14Z`

Worktree:
`/home/cmamon/GitHub/energy-market-delta-lake__worktrees/agent-issue-280-prepare-generated-corpus-history-purge-preflight-and-bac`

Current branch:
`agent/issue-280-prepare-generated-corpus-history-purge-preflight-and-bac`

Current HEAD:
`b54011023e3e8b41e5ede5ebaad4563ba8e45570`

## Summary

- Current-tree generated corpus tracking check passed:
  `git ls-files tools/gas-market-knowledge-base/generated` returned no files.
- The default external corpus root is
  `/home/cmamon/energy-market-delta-lake-artifacts/corpora` because
  `ENERGY_MARKET_CORPUS_ROOT` was unset in this preflight shell.
- Existing Gas market generated corpus artifacts are present under the default
  external root.
- AEMO major publications fixture artifacts are not present under the default
  external root. The current tree does not track any AEMO generated corpus
  files to copy from `tools/gas-market-knowledge-base/generated`, and a
  sandboxed attempt to build those fixture artifacts into the default root
  failed because the default external root was read-only from this worktree.
- A `git bundle --all` backup exists outside the repo at
  `/tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle`.
  The bundle verified successfully and records complete history.
- The remote intended for the purge execution issue is `origin`.
- This preflight records the local and remote refs observed before purge. The
  later purge execution issue must stop if these refs differ unexpectedly.

## Current-Tree Check

Commands from the repo root:

```bash
git status --short
git ls-files tools/gas-market-knowledge-base/generated
git ls-tree -r --name-only HEAD tools/gas-market-knowledge-base/generated
```

Observed output was empty for all three commands. The current tree no longer
tracks generated corpus artifact files under
`tools/gas-market-knowledge-base/generated`.

Historical generated corpus paths still exist in git history. This command
found `16667` unique paths across all refs:

```bash
git log --all --name-only --format='' -- tools/gas-market-knowledge-base/generated |
  sed '/^$/d' |
  sort -u |
  wc -l
```

Sample historical paths:

```text
tools/gas-market-knowledge-base/generated/bronze/.gitkeep
tools/gas-market-knowledge-base/generated/bronze/source_manifest.jsonl
tools/gas-market-knowledge-base/generated/gold/README.md
tools/gas-market-knowledge-base/generated/gold/glossary/README.md
tools/gas-market-knowledge-base/generated/gold/glossary/allocation.md
tools/gas-market-knowledge-base/generated/gold/glossary/bid-offer.md
tools/gas-market-knowledge-base/generated/gold/glossary/capacity.md
tools/gas-market-knowledge-base/generated/gold/glossary/connection-point.md
tools/gas-market-knowledge-base/generated/gold/glossary/facility.md
tools/gas-market-knowledge-base/generated/gold/glossary/flow.md
tools/gas-market-knowledge-base/generated/gold/glossary/gas-day.md
tools/gas-market-knowledge-base/generated/gold/glossary/hub-zone.md
tools/gas-market-knowledge-base/generated/gold/glossary/linepack.md
tools/gas-market-knowledge-base/generated/gold/glossary/mos.md
tools/gas-market-knowledge-base/generated/gold/glossary/participant.md
tools/gas-market-knowledge-base/generated/gold/glossary/schedule.md
tools/gas-market-knowledge-base/generated/gold/glossary/settlement.md
tools/gas-market-knowledge-base/generated/silver/.gitkeep
```

## External Corpus Artifacts

`ENERGY_MARKET_CORPUS_ROOT` was unset. The documented default root therefore
applies:

```text
/home/cmamon/energy-market-delta-lake-artifacts/corpora
```

Artifact presence under the default root:

```text
present files=2 size=132K /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/bronze
present files=47 size=13M /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/silver/documents
present files=14565 size=94M /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/silver/chunks
present files=1 size=38M /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/silver/index/chunks.jsonl
present files=16 size=72K /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/gold
missing /home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications/bronze
missing /home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications/silver
missing /home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications/gold
```

The AEMO major publications fixture command was checked through the Subproject
**Unit test** lane:

```text
make aemo-publications-unit-test
6 passed in 0.13s
```

An attempted default-root fixture build failed because the sandbox could not
write under `/home/cmamon/energy-market-delta-lake-artifacts/corpora`:

```text
uv run aemo-publications-corpus build-fixture
OSError: [Errno 30] Read-only file system:
'/home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications'
```

There is no AEMO major publications artifact set to preserve under the default
external root in this preflight. The purge execution issue must stop if the
Operator expects those fixture artifacts to exist before purge, if
`$ENERGY_MARKET_CORPUS_ROOT/aemo-major-publications` appears before execution
and is not backed up, or if the external root is not writable when the
execution issue needs to build or copy artifacts before rewriting refs.

Additional corpus validation note:

```text
uv run gas-market-kb validate
summary: manifest_rows=49 index_rows=14565 chunk_files=14565 gold_pages=15
gold_glossary_pages=13 errors=29325
```

The failing validation output references missing
`tools/gas-market-knowledge-base/generated/...` targets after the current-tree
cleanup. This report treats the external Gas market files as present for purge
preservation, but the later execution issue should not treat this as a clean
corpus validation result.

## Backup Bundle

The backup bundle was created with:

```bash
git bundle create \
  /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle \
  --all
git bundle verify \
  /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
sha256sum \
  /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
```

Bundle evidence:

```text
/tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle is okay
The bundle contains 41 refs, including the local refs listed below plus linked
worktree HEAD pseudo-refs.
The bundle records a complete history.
The bundle uses this hash algorithm: sha1
8392cb6dfbc7871428baebaa75d789ac92cf12ada11c10870461b2c2d8c2c3f5  /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
-rw-rw-r-- 1 cmamon cmamon 37M May 28 16:17 /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
```

An attempt to create the backup under the repo-independent artifact directory
`/home/cmamon/energy-market-delta-lake-artifacts/git-backups` failed because
that path was read-only from this sandbox. The `/tmp` bundle is outside the
repo and verified, but purge execution must re-check that the bundle still
exists and should copy it to durable Operator-owned storage if execution is not
immediate.

## Object-Size Baseline

Command:

```bash
git count-objects -vH
```

Output before purge:

```text
warning: garbage found: /home/cmamon/GitHub/energy-market-delta-lake/.git/worktrees/agent-issue-280-prepare-generated-corpus-history-purge-preflight-and-bac/refs
count: 2453
size: 17.13 MiB
in-pack: 32502
packs: 4
size-pack: 42.73 MiB
prune-packable: 0
garbage: 1
size-garbage: 4.00 KiB
```

The existing `garbage found` warning is part of this baseline. The purge
execution issue must stop if new object-database warnings appear before the
rewrite.

## Local Refs

Command:

```bash
git for-each-ref --format='%(refname) %(objectname) %(upstream:short)'
```

Observed local refs:

```text
refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability 0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb origin/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
refs/heads/agent/issue-175-add-ralph-operator-smoke-hook-for-credentialed-explorato 1993c1a88a59b07fee0137ee8401d87f2bd161df origin/dev
refs/heads/agent/issue-176-record-gas-market-knowledge-base-language-and-architectu 697a3d14929850e13e306854a7df7aba00ca3a07 origin/main
refs/heads/agent/issue-177-scaffold-the-gas-market-knowledge-base-subproject 14447f8d8e66033edf632c46b3a4d63320e45038 origin/dev
refs/heads/agent/issue-242-clean-rerun-live-archive-pdfs-through-docling-corpus-gen f67bb1cdf4244c6dc8cfea85ccab8bf65a3b1b08 origin/dev
refs/heads/agent/issue-252-promote-integrated-backlog-before-claiming-more-ready-wo 18a624ca96def7c85591fdb91d68d9a3318dc0ab origin/dev
refs/heads/agent/issue-279-stop-tracking-generated-corpus-files-in-the-current-tree 0b0a6b460017f55105d5edd8cf35fe5671003a5f origin/dev
refs/heads/agent/issue-280-prepare-generated-corpus-history-purge-preflight-and-bac b54011023e3e8b41e5ede5ebaad4563ba8e45570 origin/dev
refs/heads/agent/issue-284-compute-ratio-fields-in-shape-issue-gate 7b9f51c2fa22042187d4c4d3545ca69e4e275f47 origin/dev
refs/heads/backup/issue-180-repair-20260517T0408Z 94afb0cccb2451a3ccb257aa7447ed16ecb42cc8 origin/dev
refs/heads/backup/issue-182-failed-20260517T070408Z 1cd64b3da8f61cf0d2524933c969dcaa489d970d origin/dev
refs/heads/backup/issue-183-failed-20260517T093448Z 8f837fdaa3418040d2d4d8da1a1927205a04fe5e origin/dev
refs/heads/dev 743d569a7a7ef370fbb397640b20474e1ab4e24f origin/dev
refs/heads/main 743d569a7a7ef370fbb397640b20474e1ab4e24f origin/main
refs/ralph/manual-backup/issue-251-20260521T142318Z ca91cd573f01f40ecc832fcdb423b6a184e85bdf
refs/ralph/manual-backup/issue-259-20260521T142318Z 080d2f45b1392b3b6474ae6ec5036e6124eb8834
refs/ralph/manual-backup/issue-259-pre-requeue 3dc7d2fad73833b6b9c9e3721d32516f20525e2e
refs/ralph/recovery/issue-242-stale-running-20260525 538b05bfc6ca4456fb3e9956d89a2666e646a55f
refs/ralph/recovery/issue-242-stale-worktree-20260522 911eb0630562e75215552b284e5139c7c8eace13
refs/ralph/requeue/issue-239-20260521t212259z c2eb6cf7dfebf48319f03920b661536e640b80ed
refs/remotes/origin/HEAD 743d569a7a7ef370fbb397640b20474e1ab4e24f
refs/remotes/origin/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability 0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb
refs/remotes/origin/dev b54011023e3e8b41e5ede5ebaad4563ba8e45570
refs/remotes/origin/main 743d569a7a7ef370fbb397640b20474e1ab4e24f
refs/remotes/origin/releases/0.1.0 556abcac9b5d16c0778f7c322ad73d1c04dea240
refs/stash 911eb0630562e75215552b284e5139c7c8eace13
refs/tags/0.1.0 556abcac9b5d16c0778f7c322ad73d1c04dea240
```

Local branches and tags are intended local purge refs for an all-ref local
history rewrite. Local `refs/ralph/*` refs and `refs/stash` are also present
and were included in the backup bundle. The purge execution issue must choose
explicitly whether those local-only refs are rewritten, retained from backup,
or deleted after Operator review.

## Remote Refs

Remote:

```text
origin git@github.com:Chr1sC0de/energy-market-delta-lake.git
```

Command:

```bash
git ls-remote --heads --tags origin
```

Observed remote refs intended for remote purge update:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
b54011023e3e8b41e5ede5ebaad4563ba8e45570 refs/heads/dev
743d569a7a7ef370fbb397640b20474e1ab4e24f refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/tags/0.1.0
```

No force-push credential preflight was run in this issue. The purge execution
issue must verify force-push and protected-branch permissions before rewriting
remote refs.

## Hard Stop Conditions

The purge execution issue must stop before any history rewrite or force-push if
any condition below is true:

- `git status --short` is non-empty in the purge worktree.
- `git ls-files tools/gas-market-knowledge-base/generated` returns any path.
- The backup bundle above is missing, fails `git bundle verify`, or has a
  SHA-256 other than
  `8392cb6dfbc7871428baebaa75d789ac92cf12ada11c10870461b2c2d8c2c3f5`.
- `origin` does not resolve to
  `git@github.com:Chr1sC0de/energy-market-delta-lake.git`.
- `git ls-remote --heads --tags origin` differs from the remote refs recorded
  in this report, unless the Operator explicitly approves the changed ref set.
- `git for-each-ref` differs from the local refs recorded in this report in a
  way the purge plan has not explicitly accounted for.
- The purge plan omits any branch or tag recorded in this report.
- `git count-objects -vH` reports object-database warnings beyond the existing
  `garbage found: .../worktrees/.../refs` baseline warning.
- The external corpus root differs from
  `/home/cmamon/energy-market-delta-lake-artifacts/corpora` without Operator
  approval.
- The existing Gas market corpus roots recorded above are missing before purge.
- `$ENERGY_MARKET_CORPUS_ROOT/aemo-major-publications` exists before purge but
  is not backed up or intentionally excluded by the Operator.
- The execution issue expects AEMO major publications fixture artifacts to be
  built under the default external corpus root, but that root is unavailable or
  read-only.
- Force-push credentials, protected-branch permissions, or tag-update
  permissions for `origin` are unavailable.
- The execution plan includes `git filter-repo`, BFG, ref deletion, `git gc`,
  `git prune`, or `git push --force-with-lease` steps that are not covered by a
  fresh backup and ref preflight.

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `.gitignore`
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `tools/gas-market-knowledge-base/README.md`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/corpus_paths.py`
  - `tools/gas-market-knowledge-base/src/gas_market_knowledge_base/aemo_publications/corpus_paths.py`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `git status --short`
  - `git ls-files tools/gas-market-knowledge-base/generated`
  - `git count-objects -vH`
  - `git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle`
  - `verify recorded local refs, remote refs, backup path, artifact root, and stop conditions`
