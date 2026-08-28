# Preflight: Before Starting Work

Run preflight before editing on any Mac:

```bash
./80\ Build/scripts/preflight-git.sh
```

## Continue when

- **Clean and synchronized:** safe to begin.
- **Intentional local changes:** review the listed files and continue only if they belong to the current work.
- **Ahead:** you may continue on this Mac, but its commits must be pushed before switching Macs.
- **Prototype branch:** routine work is allowed when the branch tracks the same-named branch on `origin`. A prototype branch is not the live GitHub Pages source.

## Stop when

- **Behind:** if the working tree is clean, run `git pull --ff-only`, then rerun preflight.
- **Diverged:** stop for manual review. Do not pull, merge, or reset automatically.
- **Explicitly requested branch mismatch, no upstream, mismatched upstream, or fetch failure:** resolve that condition before editing. The current branch must track its exact same-named branch on `origin`.
- **Stale derived artifacts:** run `./80\ Build/scripts/build-all-spreadsheet-downloads.sh`; if the verification tracker contains manual edits, import them first as directed.
- **Baseline source differs from the review base:** run `python3 "80 Build/baseline_impact_check.py" --base-ref REF` with the applicable Git ref. A semantic change requires the guarded Profile Editor migration workflow.

## What preflight does

It treats the checked-out branch as the intended work branch unless an explicit expected branch is supplied, requires its exact same-named upstream on `origin`, refreshes the remote comparison, reports whether this Mac is ahead or behind, and diagnoses verification, Matrix/settings, and Setup derived-artifact freshness. This permits both `main` and deliberate prototype worktrees without weakening synchronization checks.

Preflight does not refresh derived artifacts, modify source files, pull changes, merge branches, build the project, or publish the website.

## Next

- If safe, begin routine work in [Profile Editor](profile-editor.html). Use [Local Build](local-build.html) for equivalent terminal commands, troubleshooting, or changes outside the editor's scope.
- If this is a different Mac, also read [Continue on Another Mac](other-mac.html).
