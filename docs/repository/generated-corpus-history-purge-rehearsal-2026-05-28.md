# Generated Corpus History Purge Rehearsal

This report records the local generated-corpus history rewrite rehearsal for
GitHub issue #281. The rehearsal used the preflight evidence from
`docs/repository/generated-corpus-history-purge-preflight-2026-05-28.md`,
rewrote only a disposable local clone under `/tmp`, and did not push or mutate
any remote refs.

Rehearsal timestamp: `2026-05-28T10:38:12Z`

Source worktree:
`/home/cmamon/GitHub/energy-market-delta-lake__worktrees/agent-issue-281-run-local-generated-corpus-history-rewrite-rehearsal`

Source branch:
`agent/issue-281-run-local-generated-corpus-history-rewrite-rehearsal`

Source HEAD:
`b9ef78d07d8d3a16dc6ef65026309fb06f2976ad`

Disposable run root:
`/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z`

## Summary

- The pre-rewrite gates passed for the backup bundle, remote identity, source
  checkout cleanliness, current-tree generated-path check, expected
  post-preflight remote ref advances, and external artifact copy.
- The default external corpus root was used because `ENERGY_MARKET_CORPUS_ROOT`
  was unset:
  `/home/cmamon/energy-market-delta-lake-artifacts/corpora`.
- The Gas market corpus was copied to
  `/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market`.
  The copy matched the source file count and size. The AEMO major publications
  corpus remained absent, as recorded by the preflight.
- The rewrite used a disposable bare clone containing only the intended
  published remote heads and tags. `refs/pull/*` and local-only source refs
  were not part of the final force-push surface.
- Before rewrite, the disposable clone had `14668` historical generated corpus
  paths and `size-pack: 32.97 MiB`.
- After rewrite, the disposable clone had `0` historical generated corpus
  paths and `size-pack: 15.39 MiB`.
- The final publication plan updates only the three rewritten published heads:
  the exploratory branch, `dev`, and `main`. The release branch and `0.1.0`
  tag are listed explicitly below and require no update because their object
  IDs did not change.

## Pre-Rewrite Gates

Source checkout cleanliness:

```bash
git status --short
```

Output was empty.

Current-tree generated corpus tracking check:

```bash
git ls-files tools/gas-market-knowledge-base/generated
```

Output was empty.

Source object database baseline:

```text
warning: garbage found: /home/cmamon/GitHub/energy-market-delta-lake/.git/worktrees/agent-issue-281-run-local-generated-corpus-history-rewrite-rehearsal/refs
count: 2556
size: 17.97 MiB
in-pack: 32502
packs: 4
size-pack: 42.73 MiB
prune-packable: 0
garbage: 1
size-garbage: 4.00 KiB
```

The warning matches the preflight's existing linked-worktree `refs` garbage
warning class. No new warning class was observed before the disposable rewrite.

Backup bundle verification:

```bash
git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
sha256sum /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
```

Observed evidence:

```text
/tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle is okay
The bundle records a complete history.
The bundle uses this hash algorithm: sha1
8392cb6dfbc7871428baebaa75d789ac92cf12ada11c10870461b2c2d8c2c3f5  /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
-rw-rw-r-- 1 cmamon cmamon 37M May 28 16:17 /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
```

Remote identity:

```bash
git remote -v
```

Observed evidence:

```text
origin	git@github.com:Chr1sC0de/energy-market-delta-lake.git (fetch)
origin	git@github.com:Chr1sC0de/energy-market-delta-lake.git (push)
```

Remote heads and tags:

```bash
git ls-remote --heads --tags origin
```

Observed evidence:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb	refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
b9ef78d07d8d3a16dc6ef65026309fb06f2976ad	refs/heads/dev
c38e20c6cd22d881d6262b8902279c71329ec342	refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240	refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240	refs/tags/0.1.0
```

The remote ref set still contains only the heads and tag recorded by the
preflight. The changed object IDs are expected post-preflight advances:

- `refs/heads/dev` advanced from preflight
  `b54011023e3e8b41e5ede5ebaad4563ba8e45570` to
  `b9ef78d07d8d3a16dc6ef65026309fb06f2976ad` through the later Gitflow
  **Local integration** and **Promotion** range named in the refreshed issue
  context.
- `refs/heads/main` advanced from preflight
  `743d569a7a7ef370fbb397640b20474e1ab4e24f` to
  `c38e20c6cd22d881d6262b8902279c71329ec342` through the verified
  **Promotion** range named in the refreshed issue context.
- The exploratory branch, release branch, and tag still match the preflight
  object IDs.

Ancestry checks confirmed the expected advances:

```text
b540_to_b9ef=0
743_to_c38=0
c38_to_b9ef=0
```

External artifact copy:

```bash
rsync -a --delete \
  /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/ \
  /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market/
diff -qr \
  /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market \
  /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
```

Observed evidence:

```text
source files: 14632
copy files: 14632
144M	/home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market
144M	/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
aemo-major-publications absent as expected
```

`diff -qr` produced no differences.

## Disposable Rewrite

The rehearsal used a bare clone populated by explicit heads and tags refspecs
so the rewrite surface matched the remote publication inventory:

```bash
git init --bare \
  /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git
git --git-dir=/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git \
  fetch --prune git@github.com:Chr1sC0de/energy-market-delta-lake.git \
  '+refs/heads/*:refs/heads/*' \
  '+refs/tags/*:refs/tags/*'
git --git-dir=/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git \
  config remote.origin.url git@github.com:Chr1sC0de/energy-market-delta-lake.git
```

Published refs before rewrite:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
b9ef78d07d8d3a16dc6ef65026309fb06f2976ad refs/heads/dev
c38e20c6cd22d881d6262b8902279c71329ec342 refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/tags/0.1.0
```

Object-size baseline before rewrite:

```text
count: 0
size: 0 bytes
in-pack: 25910
packs: 1
size-pack: 32.97 MiB
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
```

Generated-path verification before rewrite:

```bash
git --git-dir=/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git \
  log --all --name-only --format='' -- tools/gas-market-knowledge-base/generated |
  sed '/^$/d' |
  sort -u |
  wc -l
```

Observed output:

```text
14668
```

Per-ref generated-path counts before rewrite:

```text
refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability 56
refs/heads/dev 14668
refs/heads/main 14668
refs/heads/releases/0.1.0 0
refs/tags/0.1.0 0
```

Rewrite command:

```bash
UV_TOOL_DIR=/tmp/codex-uv-tools \
UV_CACHE_DIR=/tmp/codex-uv-cache \
uvx --from git-filter-repo git-filter-repo \
  --path tools/gas-market-knowledge-base/generated \
  --invert-paths \
  --force
```

The command was run from:

```text
/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git
```

Observed output:

```text
NOTICE: Removing 'origin' remote; see 'Why is my origin removed?'
        in the manual if you want to push back there.
        (was git@github.com:Chr1sC0de/energy-market-delta-lake.git)
Parsed 441 commits
Parsed 484 commits
New history written in 0.22 seconds; now repacking/cleaning...
Repacking your repo and cleaning out old unneeded objects
Completely finished after 0.83 seconds.
```

Published refs after rewrite:

```text
83f81ac66fcbacb9e0f24c74b9a4caf5b0a7dbec refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
7f27a9982fb8e53c44dd2317e9e5a08c270b2db0 refs/heads/dev
4dbd44fdda0e6bc214fe942b896de80846971d03 refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/tags/0.1.0
```

Object-size baseline after rewrite:

```text
count: 0
size: 0 bytes
in-pack: 11018
packs: 1
size-pack: 15.39 MiB
prune-packable: 0
garbage: 0
size-garbage: 0 bytes
```

Generated-path verification after rewrite:

```text
refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability 0
refs/heads/dev 0
refs/heads/main 0
refs/heads/releases/0.1.0 0
refs/tags/0.1.0 0
```

The all-ref generated path count after rewrite was `0`, and this command
produced no output:

```bash
git --git-dir=/tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git \
  rev-list --objects --all |
  rg 'tools/gas-market-knowledge-base/generated'
```

## Final Force-Push Plan

This is the exact remote publication plan for a later execution issue. It was
not run during this rehearsal.

Before any command below, rerun the preflight gates from this report and stop
if the backup bundle, remote identity, remote ref inventory, source checkout
cleanliness, external artifact copy, or generated-path verification differs.

`git filter-repo` removes the `origin` remote in the disposable clone. Re-add
the remote in the final execution clone before publication:

```bash
git remote add origin git@github.com:Chr1sC0de/energy-market-delta-lake.git
git ls-remote --heads --tags origin
```

Expected remote inventory immediately before publication:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb	refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
b9ef78d07d8d3a16dc6ef65026309fb06f2976ad	refs/heads/dev
c38e20c6cd22d881d6262b8902279c71329ec342	refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240	refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240	refs/tags/0.1.0
```

Force-push commands for rewritten refs:

```bash
git push \
  --force-with-lease=refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability:0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb \
  origin \
  83f81ac66fcbacb9e0f24c74b9a4caf5b0a7dbec:refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability

git push \
  --force-with-lease=refs/heads/dev:b9ef78d07d8d3a16dc6ef65026309fb06f2976ad \
  origin \
  7f27a9982fb8e53c44dd2317e9e5a08c270b2db0:refs/heads/dev

git push \
  --force-with-lease=refs/heads/main:c38e20c6cd22d881d6262b8902279c71329ec342 \
  origin \
  4dbd44fdda0e6bc214fe942b896de80846971d03:refs/heads/main
```

Refs explicitly verified as unchanged and not needing publication:

```text
refs/heads/releases/0.1.0 556abcac9b5d16c0778f7c322ad73d1c04dea240
refs/tags/0.1.0 556abcac9b5d16c0778f7c322ad73d1c04dea240
```

After publication, the final issue should run a fresh clone verification and
confirm all published refs report `0` generated corpus paths under
`tools/gas-market-knowledge-base/generated`.

## Stop Conditions for the Final Issue

Stop before any destructive remote operation if any of these values differ:

- backup bundle path, `git bundle verify`, or SHA-256
- `origin` remote identity
- current remote heads/tags inventory, except for explicitly approved new
  Operator evidence
- source checkout cleanliness
- current-tree `git ls-files tools/gas-market-knowledge-base/generated`
  output
- external corpus root or Gas market artifact copy result
- unexpected creation of
  `/home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications`
- generated-path count after the local rewrite

The final issue must also stop if it expects AEMO major publications fixture
artifacts to exist or to be built under the default external corpus root.

## QA Evidence

Commands run for this rehearsal:

```text
git diff --name-only
git status --short
git ls-files tools/gas-market-knowledge-base/generated
git count-objects -vH
git remote -v
git ls-remote --heads --tags origin
git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
sha256sum /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
rsync -a --delete /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/ /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market/
diff -qr /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
git init --bare /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/energy-market-delta-lake-rewrite-rehearsal-published-refs.git
git fetch '+refs/heads/*:refs/heads/*' '+refs/tags/*:refs/tags/*'
uvx --from git-filter-repo git-filter-repo --path tools/gas-market-knowledge-base/generated --invert-paths --force
git count-objects -vH
git log --all --name-only --format='' -- tools/gas-market-knowledge-base/generated
git rev-list --objects --all
```

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `.gitignore`
  - `docs/adr/0010-gas-market-knowledge-base.md`
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/repository/generated-corpus-history-purge-preflight-2026-05-28.md`
  - `tools/gas-market-knowledge-base/README.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "<changed-file-path>" OPERATOR.md README.md docs backend-services infrastructure tools`
  - `python3 -m unittest discover -s tests`
  - `git status --short`
  - `git ls-files tools/gas-market-knowledge-base/generated`
  - `git count-objects -vH`
  - `git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle`
  - `verify recorded remote refs, rewritten refs, backup path, artifact copy, generated-path checks, and no-push force-push plan`
