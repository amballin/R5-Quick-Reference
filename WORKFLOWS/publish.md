# Publish the Website

Publishing intentionally updates the live GitHub Pages site, version, date, and publication commit. It is separate from Finish Day and ordinary Git pushes.

The supported publisher runs only from `main`. A prototype branch may be committed and pushed to its matching prototype upstream through Finish Day, but that is a Git handoff—not publication. Integrate approved prototype work into `main` before starting this workflow.

## Before publishing

- Source changes are validated, committed, and pushed.
- `main` is checked out, clean, and synchronized with `origin/main`.
- If spreadsheet inputs changed, rebuild their release workbooks first.
- Add concise reader-facing highlights for the upcoming version to `00 Master/release_notes.yaml`.
- Confirm that updating the live website is intentional.

## Choose the version first

To start a new major series, replace `N` with an integer greater than the current major version:

```bash
./80\ Build/scripts/publish.sh --major-version N
```

If both spreadsheet families must also be replaced:

```bash
./80\ Build/scripts/publish.sh --major-version N --spreadsheet-downloads
```

A major release publishes `N.00`. Later ordinary publications continue with minor increments in that major series. Spreadsheet revisions remain independent.

Otherwise, publish the next minor version with unchanged spreadsheet downloads:

```bash
./80\ Build/scripts/publish.sh
```

Or publish the next minor version while replacing both spreadsheet families:

```bash
./80\ Build/scripts/publish.sh --spreadsheet-downloads
```

Publication automatically stops before building or pushing if the selected version has no curated entry in `00 Master/release_notes.yaml`.

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

## Generate reader-facing release notes

After publication succeeds and is verified, summarize it against the preceding publication:

```bash
python3 "80 Build/release_notes.py"
```

The command prints curated Markdown without writing or publishing a file. For an older comparison, use `--from VERSION`, `--to VERSION`, or both; the default needs no version arguments.
