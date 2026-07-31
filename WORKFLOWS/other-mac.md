# Continue Work on Another Mac

## Before leaving the first Mac

Use [Finish Day](../FINISH_DAY.html). Do not switch computers until it reports that the source is clean and synchronized.

If you edited the testing workbook, import its status before finishing:

```bash
./80\ Build/scripts/import-verification-status.sh
```

Then complete Finish Day so the updated YAML status is committed and pushed. The workbook itself does not need to move between Macs.

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

To recreate and open the verification tracker from the synchronized YAML status:

```bash
./80\ Build/scripts/open-verification-working-copy.sh
```

## Recreate local artifacts only when needed

- Use [Local Build](local-build.html) when you need to review the site locally.
- Use [Spreadsheet Workflows](spreadsheets.html) when you need local release Excel or Numbers files.
- Use [On-Camera Verification Testing](verification-testing.html) when continuing camera testing.

Never copy an older machine-local workbook over newer Git-tracked status.

## iCloud and evidence files

Do not edit one live verification workbook from both Macs and do not use iCloud as the authoritative status store. iCloud may carry test photographs, screenshots, and other evidence files. Record stable filenames or folder references in the tracker, while keeping the mutable testing status in Git-tracked YAML.

If an exceptional interrupted session leaves unimported workbook changes on the first Mac, finish that import on the first Mac before resuming on the second. This preserves definition fingerprints and avoids choosing between competing workbook versions.
