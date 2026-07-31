# Recovery and Troubleshooting

Stop at the first failed safety check. Do not compensate with an improvised pull, merge, reset, commit, or publish.

## Preflight says behind

If the working tree is clean:

```bash
git pull --ff-only &&
./80\ Build/scripts/preflight-git.sh
```

The second command runs only if the pull succeeds.

If local changes also exist, preserve and review them before pulling.

## Preflight says diverged

Stop for manual history review. Do not merge or rebase automatically.

## Validation or local build fails

Read the first reported error, correct the source issue, then rerun the validator and build. Do not publish merely to test a development change.

## Spreadsheet build fails

The automatic build may fail if Numbers is unavailable or a workbook remains open. Close the workbook and retry. Use the matching `prepare-*` script only as the documented manual conversion fallback.

## Finish Day blocks on testing status

Close the testing workbook and run:

```bash
./80\ Build/scripts/import-verification-status.sh
```

Then rerun Finish Day.

## Publication fails

The final output states `PUBLICATION DID NOT COMPLETE` and gives the exact log location. Read that log before retrying.

Do not rely only on a clean Git report. Run the publication verifier appropriate to the release. For both spreadsheets:

```bash
python3 "80 Build/verify_publication.py" --require-target matrix --require-target setup
```

## Unsure what to do

Return to the [Workflow Index](index.html) and choose the intended outcome. Keep source synchronization, local generation, and live publication as separate actions.
