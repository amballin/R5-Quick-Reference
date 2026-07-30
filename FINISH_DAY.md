# Finish Day: Sync, Spreadsheets, Publish

Use these steps in order when you want to finish the source work, synchronize Git, prepare both spreadsheet downloads, and publish the complete website.

## 1. Finish the source work and synchronize Git

From the repository root, run:

```bash
./80\ Build/scripts/finish-day.sh
```

At the prompts:

1. Approve the validator and normal development build.
2. Review the complete source-file list.
3. Approve staging every listed source change.
4. Approve the commit and enter a clear commit message.
5. Approve the push.

Do not continue until the script prints:

```text
FINISHED FOR TODAY: Safe to switch Macs.
```

This first commit and push synchronize the editable project source. The script excludes regenerated `docs/`, so this Git handoff does not publish the website.

## 2. Build and verify both spreadsheet families

Run:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

This prepares and verifies the Subject Settings Matrix and the EOS R5 Setup & Verification Tracker in both Excel and Apple Numbers formats. The workbook files are machine-local release artifacts; they are not committed to Git.

## 3. Publish the website with the spreadsheets

Run:

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

This performs the release build, includes both verified spreadsheet families, increments the site version, updates the publication date, creates the publication commit, and pushes it.

> Do not run plain `publish.sh` afterward. A plain publish omits the spreadsheet downloads and would remove them from the published site.

## 4. Verify the final Git state

Run:

```bash
./80\ Build/scripts/git-status-report.sh
```

The required final result is:

```text
STATUS: CLEAN AND SYNCHRONIZED
```

If that result does not appear, stop and resolve the reported Git state before switching computers.

## Optional: also publish PNG downloads

Use this publishing command instead of the command in Step 3:

```bash
./80\ Build/scripts/publish.sh --png --spreadsheet-downloads
```

Only include `--png` when fixed PNG card downloads are intentionally wanted on the live site.
