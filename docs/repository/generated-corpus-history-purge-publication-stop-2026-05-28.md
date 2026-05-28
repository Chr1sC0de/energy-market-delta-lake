# Generated Corpus History Purge Publication Stop Evidence

This note records the GitHub issue #282 publication preflight attempted on
2026-05-28 from the issue worktree. No remote refs were pushed, no fresh clone
verification was run, and no GitHub Issue metadata was edited because the
approved force-push leases from the rehearsal report no longer matched the
remote inventory.

The controlling rehearsal report is
`docs/repository/generated-corpus-history-purge-rehearsal-2026-05-28.md`.

## Stop Decision

The publication stopped before any destructive remote operation. The current
remote inventory differs from the rehearsal report's approved inventory for
`refs/heads/dev` and `refs/heads/main`.

Approved rehearsal inventory:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
b9ef78d07d8d3a16dc6ef65026309fb06f2976ad refs/heads/dev
c38e20c6cd22d881d6262b8902279c71329ec342 refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/tags/0.1.0
```

Observed remote inventory:

```text
0a1e29c7ddc7254a306402bc8dba3f68ef65bbdb refs/heads/agent/exploratory/issue-259-reorganize-aemo-etl-asset-groups-for-lineage-readability
0a69918a55a0d2f1c8c40e6030c338e01498b30f refs/heads/dev
5548755ebafe45274496be8297f1aaa5f419aa43 refs/heads/main
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/heads/releases/0.1.0
556abcac9b5d16c0778f7c322ad73d1c04dea240 refs/tags/0.1.0
```

The rewritten commits from the rehearsal report are therefore stale for the
current `dev` and `main` tips. Reusing the old force-push commands would discard
later **Local integration** and **Promotion** work.

Pushed refs:

```text
none
```

## Preflight Evidence

Source branch:

```text
agent/issue-282-force-push-generated-corpus-purge-and-verify-fresh-clone
```

Source HEAD:

```text
0a69918a55a0d2f1c8c40e6030c338e01498b30f
```

Source checkout cleanliness:

```bash
git status --short
```

Output was empty before this evidence file was added.

Current-tree generated corpus tracking check:

```bash
git ls-files tools/gas-market-knowledge-base/generated
```

Output was empty.

Source object database baseline:

```text
warning: garbage found: /home/cmamon/GitHub/energy-market-delta-lake/.git/worktrees/agent-issue-282-force-push-generated-corpus-purge-and-verify-fresh-clone/refs
count: 2639
size: 18.61 MiB
in-pack: 32502
packs: 4
size-pack: 42.73 MiB
prune-packable: 0
garbage: 1
size-garbage: 4.00 KiB
```

The warning matches the rehearsal report's existing linked-worktree `refs`
garbage warning class.

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
```

Remote identity:

```bash
git remote -v
```

Observed evidence:

```text
origin git@github.com:Chr1sC0de/energy-market-delta-lake.git (fetch)
origin git@github.com:Chr1sC0de/energy-market-delta-lake.git (push)
```

External corpus root:

```text
ENERGY_MARKET_CORPUS_ROOT unset
```

External artifact copy:

```text
source files: 14632
copy files: 14632
source size: 144M /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market
copy size: 144M /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
diff -qr output: none
aemo-major-publications absent as expected
```

## Fresh Clone Verification

Fresh clone verification was intentionally not run. The approved publication
was blocked before any push, so a fresh clone would only verify the unrewritten
remote history and would not satisfy the issue's publication acceptance
criteria.

## Reset Guidance

No collaborator or Ralph worktree reset is required from this stopped attempt
because no remote refs changed.

Before a future force-push attempt, regenerate the rewrite from the current
remote inventory and produce a new force-push plan whose
`--force-with-lease` object IDs match the then-current remote refs exactly. The
future plan must include reset guidance for collaborators and Ralph worktrees
using the new rewritten `dev`, `main`, and exploratory branch object IDs.

## QA Evidence

Commands run for this stopped publication attempt:

```text
git status --short
git diff --name-only
git branch --show-current
git rev-parse HEAD
git remote -v
git ls-files tools/gas-market-knowledge-base/generated
git count-objects -vH
git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
sha256sum /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle
git ls-remote --heads --tags origin
printenv ENERGY_MARKET_CORPUS_ROOT
rsync -a --delete /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market/ /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market/
find /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market -type f | wc -l
find /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market -type f | wc -l
du -sh /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market
du -sh /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
diff -qr /home/cmamon/energy-market-delta-lake-artifacts/corpora/gas-market /tmp/energy-market-delta-lake-history-rehearsals/issue-281-20260528T103812Z/external-corpus-copy/gas-market
test -d /home/cmamon/energy-market-delta-lake-artifacts/corpora/aemo-major-publications
```

## Sync metadata

- `sync.owner`: `docs`
- `sync.sources`:
  - `docs/repository/generated-corpus-history-purge-rehearsal-2026-05-28.md`
- `sync.scope`: `operations`
- `sync.qa`:
  - `git diff --name-only`
  - `rg -n "docs/repository/generated-corpus-history-purge-rehearsal-2026-05-28.md" README.md docs backend-services infrastructure tools`
  - `git status --short`
  - `git ls-files tools/gas-market-knowledge-base/generated`
  - `git count-objects -vH`
  - `git bundle verify /tmp/energy-market-delta-lake-history-backups/issue-280-20260528T061714Z/energy-market-delta-lake-all-refs-before-generated-corpus-purge.bundle`
  - `verify stopped publication evidence, remote ref drift, no pushed refs, and no fresh-clone claim`
