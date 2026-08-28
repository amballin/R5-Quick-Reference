# Finish Day: Release Notes, Sync, Spreadsheets, Publish

Choose one path:

- **Finish for the day or switch Macs:** complete Step 0 when applicable, then Step 2, and stop.
- **Integrate a finished working branch:** complete Step 0 when applicable, Step 2, then Step 2A. Integration remains optional and does not publish.
- **Publish the complete website:** complete Step 0 when applicable, then Steps 1–5 in order, including Step 2A when starting from a working branch. Prepare the release notes before the single `finish-day.sh` run so all source work is synchronized together.

## 0. Import testing status when the working tracker changed

If you updated the local Excel or Numbers verification tracker, close it and run:

```bash
./80\ Build/scripts/import-verification-status.sh
```

This transfers approved mutable fields into the non-published, Git-tracked YAML status. `finish-day.sh` stops if the local tracker changed after its last successful import, if its definitions are stale, or if canonical YAML changed without rebuilding the tracker. When the unchanged tracker is merely stale, run the consolidated recovery command:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

The command diagnoses every spreadsheet-derived artifact first and will not overwrite unimported tracker edits.

## 1. Prepare the release notes when publishing

Skip this step when you are only finishing for the day or switching Macs.

Ask Codex to prepare curated release notes for the upcoming website version. Codex should review the reader-facing changes since the previous publication, propose concise highlights for your approval, create the required backup, add the approved entry to `00 Master/release_notes.yaml`, confirm that it uses the next publication version, and run source-only validation. A release-note-only change does not require a development build; the full sequence runs once in Step 2.

For an ordinary release, the upcoming version keeps the current major number from `80 Build/publish_metadata.yaml` and adds one to its minor number. For a new major series, the upcoming version is `N.00`, where `N` is greater than the current major version. Do not edit the publish metadata manually.

Review and approve the highlights as reader-facing release notes. Do not continue until the exact upcoming version exists in `00 Master/release_notes.yaml`.

## 2. Finish the source work and synchronize Git

In Profile Editor, open **Finish Day**. It guides the same workflow through four separately guarded stages: **Check**, **Prepare**, **Commit**, and **Push**. Review every displayed source file, enter the commit message, and approve commit and push separately. Do not continue until the workspace reports that the branch is clean and synchronized.

The terminal interface remains available from the repository root and uses the same shared implementation:

```bash
./80\ Build/scripts/finish-day.sh
```

After preparation approval, both interfaces run source validation, the normal development build, and full validation; these checks are mandatory and cannot be postponed while continuing to a commit. Then:

1. Review the complete source-file list.
2. Approve staging every listed source change.
3. Approve the commit and enter a clear commit message.
4. Approve the push.

Do not continue until the UI reports a clean synchronized branch or the terminal command prints:

```text
FINISHED FOR TODAY: Safe to switch Macs.
```

This commit and push synchronize all editable project source, including the release notes when publishing. The shared Finish Day engine backs up and excludes regenerated `docs/`, so this Git handoff does not publish the website.

Finish Day uses the current checked-out branch and requires its exact same-named upstream on `origin`. On a prototype worktree, it may therefore commit and push only that prototype branch. It never redirects the push to `main`, and because GitHub Pages watches `main / docs`, the prototype handoff does not update the live site.

> If you are only finishing for the day or switching Macs, stop here. If this is a prototype branch, also stop here and integrate the approved work into `main` separately before publication. If already on `main` and publishing, continue directly to Step 3; do not run `finish-day.sh` again.

## 2A. Integrate a finished working branch when needed

Skip this step when you are stopping for the day or are already working on `main`.

In Profile Editor, open **Integrate Branch** only after Finish Day reports that the current non-main branch is clean and synchronized. The workspace uses five separately guarded stages:

1. **Check** refreshes `origin`, verifies the clean current branch and its exact same-named upstream, and targets only `origin/main`.
2. **Review** creates the proposed merge in a disposable worktree based on current `origin/main`. It stops without changing either real branch on conflicts, rejects proposed `docs/` changes, runs source validation, the normal development build, and full validation, restores generated website files, and displays the exact commits and files.
3. **Merge Main** requires confirmation and applies the exact reviewed tree to a clean local `main`. Nothing is pushed.
4. **Push Main** requires a separate confirmation and updates only `origin/main`. It does not call `publish.sh`, change release metadata, or publish the website.
5. **Resync** requires another confirmation, fast-forwards the working branch to the integrated main commit, and pushes only its exact same-named upstream. It never rebases or rewrites shared history.

If `main` is already checked out elsewhere on this Mac, that worktree must be clean and synchronized. If it is not checked out, the workflow uses a temporary worktree rather than switching the active branch. For a fork, `origin/main` means the fork owner's main branch; receiving enhancements from a separate upstream repository remains a distinct operation.

Do not continue to publication until Integrate Branch reports that `main` and the working branch are synchronized.

## 3. Build and verify both spreadsheet families

Run:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

This diagnoses the local verification working copy plus both release families, safely refreshes only stale artifacts in dependency order, and verifies the Subject Settings Matrix and EOS R5 Setup & Verification Tracker in Excel and Apple Numbers. Numbers launches automatically. The workbook files are machine-local and are not committed to Git.

## 4. Choose the website version and publish

Confirm that the current branch is `main`. The publisher stops before building or changing files on every other branch.

To start a new major website version, replace `N` with an integer greater than the current major version:

```bash
./80\ Build/scripts/publish.sh --major-version N --spreadsheet-downloads
```

Otherwise, publish the next minor website version:

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

This performs the release build, includes both verified spreadsheet families, increments the site version, updates the publication date, creates the publication commit, and pushes it.

The selected version must exactly match the curated highlights prepared in Step 1 and synchronized in Step 2. Major website versions do not change spreadsheet revisions, and later ordinary publications continue with minor increments in the selected major series.

The command is successful only when it prints `PUBLICATION COMPLETE AND VERIFIED`. It also records a timestamped diagnostic log under the machine-local `Logs/` folder. If publication stops, it prints `PUBLICATION DID NOT COMPLETE` and the exact log location.

Later plain `publish.sh` releases preserve these exact workbook downloads while their recorded source fingerprints remain current. If relevant workbook inputs changed, plain publication stops and requires a rebuild or explicit removal.

## 5. Verify the final Git state

First verify the publication itself:

```bash
python3 "80 Build/verify_publication.py" --require-target matrix --require-target setup
```

The required result begins with:

```text
PUBLICATION VERIFIED
```

Then run:

```bash
./80\ Build/scripts/git-status-report.sh
```

Both `PUBLICATION VERIFIED` and `STATUS: CLEAN AND SYNCHRONIZED` are required. If either result does not appear, use the publish log reported by Step 4 and do not treat the website as published.
