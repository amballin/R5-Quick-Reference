# Local Validation and Build: When and Why

Choose the smallest validation that proves the affected surface is correct. A narrow metadata or documentation-source change may need only a targeted check or source-only validation. Run the complete local build when generated output or build behavior can change, or when work reaches an integration checkpoint.

The complete local sequence is:

```bash
python3 "80 Build/validator.py" --source-only &&
python3 "80 Build/build.py" &&
python3 "80 Build/validator.py"
```

You may copy and run the complete block. The `&&` connections stop the sequence at the first error, so a failed check cannot be hidden by a later command. You may also run the three commands one at a time when troubleshooting. One successful sequence is enough while its inputs remain unchanged.

The Profile Editor provides the same sequence under **Review & Build**. It first requires every browser draft to be saved or explicitly discarded, then requires a fresh readiness check and a final confirmation. This is convenient after profile, My Menu, or baseline work; the command block remains available for troubleshooting and other project changes.

## Why three commands

- The source-only validator checks editable source without treating expected stale generated files as errors.
- The build regenerates the local HTML/PWA, workflow HTML, `docs/` review copy, and reports. It automatically includes valid prepared workbook families and preserves compatible committed spreadsheet downloads for the rest, including the main index's **Downloads** section, without regenerating workbooks or opening Apple Numbers.
- The final validator checks the generated result.

Stop when any command reports an error. Read the first error, correct it, and rerun the sequence. None of these commands publishes, commits, or pushes.

## Use targeted or source-only validation when

- Release notes are the only changed source: confirm the next version, run source-only validation, and review the diff. The publishing workflow checks the exact candidate again.
- A decision-log, project-memory, TODO, or other non-generated metadata/documentation change cannot affect rendered output or build behavior.
- A subsystem documents its own focused test loop, such as isolated Camera Lab development.
- A machine-local testing-status import changes only canonical YAML status; run the relevant import checks and source-only validation.

Targeted validation is not permission to skip a later integration checkpoint. Accumulate related source work, then run the complete sequence once when it reaches that boundary.

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
- At integration, computer handoff, or Finish Day checkpoints. Publication runs its own supported publish-mode build and verification instead of requiring another unchanged development build immediately beforehand.
- Before committing a substantial change that has not already passed the complete sequence on the same inputs.
- A validator specifically requests regenerated output.

## A full build is usually unnecessary when

- You only inspected files or answered a question.
- You changed only machine-local testing observations and are importing them into YAML; validate after import.
- You are preparing spreadsheets only; use their dedicated build commands.
- You changed only release notes or non-generated project metadata and source-only validation passed.

## Repeat a full build only when

- Inputs changed after the previous successful sequence.
- A previous build or validation failed and the cause was corrected.
- Build, rendering, template, spreadsheet-generation, or reproducibility behavior changed and a clean repeat is needed to test determinism.
- There is evidence of hidden state or nondeterministic output.

Do not run a second unchanged full build merely because an artifact is maintained or expected to be regenerated later.

## After pulling on another Mac

Build if you need local output or if pulled changes affect generated content. Machine-local output is deliberately not synchronized through Git.

## Important

The normal build may change tracked `docs/`, but that is local generated output—not publication authorization. Finish Day separates those changes from ordinary source commits. Only the supported publish command updates the live site.
