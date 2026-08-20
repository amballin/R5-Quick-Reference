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
- **Stale derived artifacts:** run `./80\ Build/scripts/build-all-spreadsheet-downloads.sh`; if the verification tracker contains manual edits, import them first as directed.
- **Baseline source differs from the review base:** run `python3 "80 Build/baseline_impact_check.py" --base-ref REF` with the applicable Git ref. A semantic change requires the guarded Profile Editor migration workflow.

## What preflight does

It refreshes the remote comparison, checks the branch and upstream, reports whether this Mac is ahead or behind, and diagnoses verification, Matrix/settings, and Setup derived-artifact freshness. It distinguishes unimported edits, safely rebuildable generated state, and current state.

Preflight does not refresh derived artifacts, modify source files, pull changes, merge branches, build the project, or publish the website.

## Next

- If safe, begin work and use [Local Build](local-build.html) when the change requires it.
- If this is a different Mac, also read [Continue on Another Mac](other-mac.html).
