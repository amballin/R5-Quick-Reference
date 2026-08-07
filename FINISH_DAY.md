# Finish Day: Release Notes, Sync, Spreadsheets, Publish

Choose one path:

- **Finish for the day or switch Macs:** complete Step 0 when applicable, then Step 2, and stop.
- **Publish the complete website:** complete Step 0 when applicable, then Steps 1–5 in order. Prepare the release notes before the single `finish-day.sh` run so all source work is synchronized together.

## 0. Import testing status when the working tracker changed

If you updated the local Excel or Numbers verification tracker, close it and run:

```bash
./80\ Build/scripts/import-verification-status.sh
```

This transfers approved mutable fields into the non-published, Git-tracked YAML status. `finish-day.sh` stops if the local tracker changed after its last successful import, if its definitions are stale, or if canonical YAML changed without rebuilding the tracker. When the unchanged tracker is merely stale, run the open-tracker helper to refresh it safely.

## 1. Prepare the release notes when publishing

Skip this step when you are only finishing for the day or switching Macs.

Ask Codex to prepare curated release notes for the upcoming website version. Codex should review the reader-facing changes since the previous publication, propose concise highlights for your approval, create the required backup, add the approved entry to `00 Master/release_notes.yaml`, and validate it.

For an ordinary release, the upcoming version keeps the current major number from `80 Build/publish_metadata.yaml` and adds one to its minor number. For a new major series, the upcoming version is `N.00`, where `N` is greater than the current major version. Do not edit the publish metadata manually.

Review and approve the highlights as reader-facing release notes. Do not continue until the exact upcoming version exists in `00 Master/release_notes.yaml`.

## 2. Finish the source work and synchronize Git

From the repository root, run:

```bash
./80\ Build/scripts/finish-day.sh
```

The script first runs source validation, the normal development build, and full validation; these checks are mandatory and cannot be postponed while continuing to a commit. Then, at the prompts:

1. Review the complete source-file list.
2. Approve staging every listed source change.
3. Approve the commit and enter a clear commit message.
4. Approve the push.

Do not continue until the script prints:

```text
FINISHED FOR TODAY: Safe to switch Macs.
```

This commit and push synchronize all editable project source, including the release notes when publishing. The script excludes regenerated `docs/`, so this Git handoff does not publish the website.

> If you are only finishing for the day or switching Macs, stop here. If publishing, continue directly to Step 3; do not run `finish-day.sh` again.

## 3. Build and verify both spreadsheet families

Run:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

This prepares and verifies the Subject Settings Matrix and the EOS R5 Setup & Verification Tracker in both Excel and Apple Numbers formats. The workbook files are machine-local release artifacts; they are not committed to Git.

## 4. Choose the website version and publish

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
