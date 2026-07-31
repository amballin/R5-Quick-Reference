# Local Build: When and Why

The normal local build is:

```bash
python3 "80 Build/validator.py" --source-only &&
python3 "80 Build/build.py" &&
python3 "80 Build/validator.py"
```

You may copy and run the complete block. The `&&` connections stop the sequence at the first error, so a failed check cannot be hidden by a later command. You may also run the three commands one at a time when troubleshooting.

## Why three commands

- The source-only validator checks editable source without treating expected stale generated files as errors.
- The build regenerates the local HTML/PWA, workflow HTML, `docs/` review copy, and reports.
- The final validator checks the generated result.

Stop when any command reports an error. Read the first error, correct it, and rerun the sequence. None of these commands publishes, commits, or pushes.

## Which website copy to open

- For routine local review, open `Canon Camera Reference Local/Build Output/merged-build/index.html`. This is the complete disposable local website.
- Use `Canon Camera Reference/docs/index.html` only to inspect the Git-tracked GitHub Pages mirror. Changes under `docs/` can reach the live website if committed and pushed.
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
