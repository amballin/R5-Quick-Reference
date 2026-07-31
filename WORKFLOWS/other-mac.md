# Continue Work on Another Mac

## Before leaving the first Mac

Use [Finish Day](../FINISH_DAY.html). Do not switch computers until it reports that the source is clean and synchronized.

If you edited the testing workbook, import its status before finishing:

```bash
./80\ Build/scripts/import-verification-status.sh
```

Machine-local spreadsheets, reports, backups, and build output do not travel through Git.

## On the other Mac

Run:

```bash
./80\ Build/scripts/preflight-git.sh
```

If the clean clone is behind:

```bash
git pull --ff-only
```

Then rerun preflight. Begin work only when the result is clean and synchronized.

## Recreate local artifacts only when needed

- Use [Local Build](local-build.html) when you need to review the site locally.
- Use [Spreadsheet Workflows](spreadsheets.html) when you need local Excel or Numbers files.
- Generate the verification working copy from Git-tracked YAML before continuing camera testing.

Never copy an older machine-local workbook over newer Git-tracked status.
