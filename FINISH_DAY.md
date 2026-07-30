# Finish Day: Sync, Spreadsheets, Publish

Use these steps in order when you want to finish the source work, synchronize Git, prepare both spreadsheet downloads, and publish the complete website.

## 0. Import testing status when the working tracker changed

If you updated the local Excel or Numbers verification tracker, close it and run:

```bash
./80\ Build/scripts/import-verification-status.sh
```

This transfers approved mutable fields into the non-published, Git-tracked YAML status. `finish-day.sh` will stop if the local tracker changed after its last successful import.

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

The command is successful only when it prints `PUBLICATION COMPLETE AND VERIFIED`. It also records a timestamped diagnostic log under the machine-local `Logs/` folder. If publication stops, it prints `PUBLICATION DID NOT COMPLETE` and the exact log location.

Later plain `publish.sh` releases preserve these exact workbook downloads while their recorded source fingerprints remain current. If relevant workbook inputs changed, plain publication stops and requires a rebuild or explicit removal.

## 4. Verify the final Git state

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

Both `PUBLICATION VERIFIED` and `STATUS: CLEAN AND SYNCHRONIZED` are required. If either result does not appear, use the publish log reported by Step 3 and do not treat the website as published.

## Optional: also publish PNG downloads

Use this publishing command instead of the command in Step 3:

```bash
./80\ Build/scripts/publish.sh --png --spreadsheet-downloads
```

Only include `--png` when fixed PNG card downloads are intentionally wanted on the live site.

## Optional: start a new major website version

To make this publication Version 2.00, use this command instead of Step 3:

```bash
./80\ Build/scripts/publish.sh --major-version 2 --spreadsheet-downloads
```

The requested major number must be greater than the current one. Later ordinary publications continue with 2.01, 2.02, and so on. Spreadsheet revisions remain independent.
