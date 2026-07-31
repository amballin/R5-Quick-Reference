# Publish the Website

Publishing intentionally updates the live GitHub Pages site, version, date, and publication commit. It is separate from Finish Day and ordinary Git pushes.

## Before publishing

- Source changes are validated, committed, and pushed.
- The branch is clean and synchronized.
- If spreadsheet inputs changed, rebuild their release workbooks first.
- Confirm that updating the live website is intentional.

## Ordinary publication

Use the ordinary command when spreadsheet downloads are unchanged:

```bash
./80\ Build/scripts/publish.sh
```

This increments the minor website version.

## Publication with replacement spreadsheets

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

This replaces both published workbook families and increments the minor website version. It does not require a major-version bump.

## Optional major release

Only when intentionally starting a new major series:

```bash
./80\ Build/scripts/publish.sh --major-version N --spreadsheet-downloads
```

Replace `N` with an integer greater than the current major version. A major release is never required for ordinary site or spreadsheet changes.

## Required success result

Do not consider the site published unless the command ends with:

```text
PUBLICATION COMPLETE AND VERIFIED.
```

Every run writes a timestamped log under the machine-local `Logs/` folder.

For spreadsheet publication, independently verify:

```bash
python3 "80 Build/verify_publication.py" --require-target matrix --require-target setup
```

Then verify the final Git state:

```bash
./80\ Build/scripts/git-status-report.sh
```

Success requires both `PUBLICATION VERIFIED` and `STATUS: CLEAN AND SYNCHRONIZED`. See [Recovery](recovery.html) if either check fails.
