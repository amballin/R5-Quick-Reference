# Spreadsheet Workflows

Choose the outcome you need. Release workbooks and the testing working copy serve different purposes.

## Build both local release workbook families

Use this after spreadsheet definitions, layout, or generator code changes, or before publishing replacement spreadsheet downloads:

```bash
./80\ Build/scripts/build-all-spreadsheet-downloads.sh
```

It prepares and verifies Matrix and Setup workbooks in Excel and Apple Numbers. These files are machine-local and are not committed.

## Build one release workbook family

- Matrix only:

```bash
./80\ Build/scripts/build-matrix-downloads.sh
```

- Blank Setup master only:

```bash
./80\ Build/scripts/build-setup-downloads.sh
```

The `prepare-*` scripts are manual conversion fallbacks. Use them only when automatic Numbers conversion fails.

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

First build both release families, then follow [Publish the Website](publish.html) with:

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

This is a complete website publication, not a spreadsheet-only upload. An ordinary minor release is the default; a major-version option is never required.

## Verify published spreadsheet status

```bash
python3 "80 Build/verify_publication.py" --require-target matrix --require-target setup
```

Success requires `PUBLICATION VERIFIED` and matching Matrix and Setup hashes.
