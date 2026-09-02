# Spreadsheet Workflows

Choose the outcome you need. Release workbooks and the testing working copy serve different purposes.

Routine local website builds include valid workbook families already prepared on this Mac and preserve compatible committed spreadsheet downloads for the rest. You do not need an extra website-build flag to keep the **Downloads** section on the local main index. Use the release-workbook commands below only when workbook inputs changed or you intentionally want replacement files; the next normal local build detects and includes them automatically.

## Refresh stale spreadsheet-derived artifacts

This is the normal recovery command after spreadsheet definitions, layout, generator code, or canonical verification status changes:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

It first reports the verification working copy, Matrix/settings, and Setup states. If the verification copy may contain unimported edits, it stops before changing anything and directs you to import them. Otherwise it rebuilds only stale artifacts in the safe order and skips current files. It does not publish, commit, or push.

Leave Numbers closed before starting. The workflow launches it quietly in the background, closes each generated workbook, and quits the Numbers process it launched. If Numbers is already open, the workflow stops without touching that session. Save and close Numbers, then choose **Resume after closing Numbers** in Profile Editor or rerun the same command; the fresh diagnosis skips spreadsheet artifacts that are already current.

To deliberately regenerate both release workbook families even when they are current:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh --force-release-workbooks
```

The same diagnosis and unimported-edit safeguards run first. Each regenerated workbook shows its deterministic spreadsheet build ID in the banner; the Setup Metadata sheet records the same ID.

## Build one release workbook family

- Matrix only:

```bash
./80\ Build/scripts/build-matrix-downloads.sh
```

- Blank Setup master only:

```bash
./80\ Build/scripts/build-setup-downloads.sh
```

The `prepare-*` scripts are manual conversion fallbacks. Use them only if the automatic workflow reports that neither supported Numbers application can complete the operation.

## Create the testing working copy

The testing workbook contains private working status and is never published. Follow [On-Camera Verification Testing](verification-testing.html) for opening the correct workbook, recording evidence, importing results, and changing Macs safely.

The preferred helper creates the tracker only when neither local format exists, reports its synchronization state, and opens the newest Numbers or Excel copy:

```bash
./80\ Build/scripts/open-verification-working-copy.sh
```

With the default local-workspace location, these direct links open the existing file:

- [Open the Numbers testing tracker](../../Canon%20Camera%20Reference%20Local/Verification/EOS%20R5%20On-Camera%20Verification%20Tracker.numbers)
- [Open the Excel testing tracker](../../Canon%20Camera%20Reference%20Local/Verification/EOS%20R5%20On-Camera%20Verification%20Tracker.xlsx)

If `PRS_LOCAL_WORKSPACE` points somewhere else, use the helper rather than the direct links.

To rebuild the testing workbook deliberately from Git-tracked status:

```bash
./80\ Build/scripts/build-verification-working-copy.sh
```

It combines current definitions with Git-tracked testing status. Do not run this rebuild over a tracker containing unimported changes.

## Record testing-status updates

After editing and closing the local testing workbook:

```bash
./80\ Build/scripts/import-verification-status.sh
```

This imports approved mutable fields into `90 Testing/eos_r5_verification_status.yaml`. Run it before Finish Day or changing computers.

If definitions changed without a workbook import:

```bash
./80\ Build/scripts/reconcile-verification-status.sh
```

Changed requirements preserve history but mark affected prior passes for retesting.

## Publish replacement spreadsheets

Profile Editor's **Automatic (recommended)** publication option rebuilds only diagnosed stale families and preserves current families. To force new files for both families, use its **Force rebuild and republish both** option.

For the equivalent Terminal recovery path, first run the force command above, then follow [Publish the Website](publish.html) with:

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

This is a complete website publication, not a spreadsheet-only upload. An ordinary minor release is the default; a major-version option is never required.

## Verify published spreadsheet status

```bash
python3 "80 Build/verify_publication.py" --require-target matrix --require-target setup
```

Success requires `PUBLICATION VERIFIED` and matching Matrix and Setup hashes.
The website Downloads section, published manifest, workbook banner, and publication receipt must also agree on each family’s spreadsheet build ID.
