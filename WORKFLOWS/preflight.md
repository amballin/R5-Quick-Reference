# Preflight: Before Starting Work

Run preflight before editing on any Mac:

```bash
./80\ Build/scripts/preflight-git.sh
```

## Continue when

- **Clean and synchronized:** safe to begin.
- **Intentional local changes:** review the listed files and continue only if they belong to the current work.
- **Ahead:** you may continue on this Mac, but its commits must be pushed before switching Macs.

## Stop when

- **Behind:** if the working tree is clean, run `git pull --ff-only`, then rerun preflight.
- **Diverged:** stop for manual review. Do not pull, merge, or reset automatically.
- **Wrong branch, no upstream, or fetch failure:** resolve that condition before editing.
- **Stale verification tracker:** use the open helper to rebuild an unchanged copy, or import its edits before rebuilding when both the workbook and its definitions changed.

## What preflight does

It refreshes the remote comparison, checks the branch and upstream, reports whether this Mac is ahead or behind, and checks whether the local verification tracker matches its synchronized file hashes, YAML-status hash, workbook revision, and source fingerprint. It distinguishes unimported edits, a safely rebuildable stale tracker, and a stale tracker whose edits must be imported before rebuilding.

Preflight does not modify source files, pull changes, merge branches, build the project, or publish the website.

## Next

- If safe, begin work and use [Local Build](local-build.html) when the change requires it.
- If this is a different Mac, also read [Continue on Another Mac](other-mac.html).
