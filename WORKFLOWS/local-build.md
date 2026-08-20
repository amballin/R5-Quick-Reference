# Local Build: When and Why

The normal local build is:

```bash
python3 "80 Build/validator.py" --source-only &&
python3 "80 Build/build.py" &&
python3 "80 Build/validator.py"
```

You may copy and run the complete block. The `&&` connections stop the sequence at the first error, so a failed check cannot be hidden by a later command. You may also run the three commands one at a time when troubleshooting.

The Profile Editor provides the same sequence under **Review & Build**. It first requires every browser draft to be saved or explicitly discarded, then requires a fresh readiness check and a final confirmation. This is convenient after profile, My Menu, or baseline work; the command block remains available for troubleshooting and other project changes.

## Why three commands

- The source-only validator checks editable source without treating expected stale generated files as errors.
- The build regenerates the local HTML/PWA, workflow HTML, `docs/` review copy, and reports. It automatically includes valid prepared workbook families and preserves compatible committed spreadsheet downloads for the rest, including the main index's **Downloads** section, without regenerating workbooks or opening Apple Numbers.
- The final validator checks the generated result.

Stop when any command reports an error. Read the first error, correct it, and rerun the sequence. None of these commands publishes, commits, or pushes.

## Baseline impact before the build

When `00 Master/baseline.yaml` changed outside a reviewed Profile Editor migration, run:

```bash
python3 "80 Build/baseline_impact_check.py"
```

The command compares worktree defaults with `HEAD`. Use `--base-ref origin/main` when reviewing a branch for integration. Status 1 is a review result, not a migration: open the Profile Editor and complete the guarded Baseline Setup workflow before continuing. Metadata-only and formatting-only baseline differences return status 0.

If spreadsheet definitions or layout changed and no valid prepared replacement exists, the normal build stops rather than preserve stale downloads. Use the affected workbook family's dedicated command in [Spreadsheet Workflows](spreadsheets.html), then rerun the same normal local build; it detects and includes the verified replacement automatically. The dedicated commands are only needed when workbook inputs change or replacement workbook files are wanted.

## Which website copy to open

- For routine local review, open `Canon Camera Reference Local/Build Output/merged-build/index.html`. This is the complete disposable local website, and its version line begins with **Pre-Release •** so it is easy to distinguish from published output.
- To review cards that are not released, open `Canon Camera Reference Local/Build Output/Card Candidates/index.html`. The normal full build refreshes this separate candidate list; these cards never enter `docs/` or the publishable PWA.
- Use `Canon Camera Reference/docs/index.html` only to inspect the Git-tracked GitHub Pages mirror. Its version line does not show the local indicator. Changes under `docs/` can reach the live website if committed and pushed.
- Do not open `Build Output/cards/html/` for normal review. Those card pages are intermediate build files, so their links are written for later assembly into the complete website.

A normal build may refresh both the local website and `docs/`, but it does not authorize publication.

## Build when

- Card, profile, baseline, control, appendix, navigation, template, or website content changed.
- Build or rendering code changed.
- Finish Day or workflow Markdown changed; the build automatically refreshes its tracked HTML copy.
- You want to review the complete local website.
- Before committing a substantial source change.
- A validator specifically requests regenerated output.

## A full build is usually unnecessary when

- You only inspected files or answered a question.
- You changed only machine-local testing observations and are importing them into YAML; validate after import.
- You are preparing spreadsheets only; use their dedicated build commands.

## After pulling on another Mac

Build if you need local output or if pulled changes affect generated content. Machine-local output is deliberately not synchronized through Git.

## Important

The normal build may change tracked `docs/`, but that is local generated output—not publication authorization. Finish Day separates those changes from ordinary source commits. Only the supported publish command updates the live site.
