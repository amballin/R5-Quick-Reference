# Project Workflow Index

Follow this order during a typical project day. Spreadsheet testing status and spreadsheet release files have separate places in the sequence.

## 1. Preflight before editing

Open [Preflight](preflight.html) to confirm this Mac has the current source and is safe to use.

## 2. Develop, build, and test

Make the intended source changes. Open [Local Build](local-build.html) to validate before generation, build the complete local result, and validate the generated result. For routine review, open the completed website at `Canon Camera Reference Local/Build Output/merged-build/index.html`, not the intermediate card files or the Git-tracked `docs/` publication mirror.

## 3. Record spreadsheet testing status

If you updated the machine-local verification workbook, open [Spreadsheet Workflows](spreadsheets.html), close the workbook, and import its testing status into Git-tracked YAML. Do this before Finish Day so the status is included in the source commit.

If the testing workbook did not change, continue directly to Step 4.

## 4. Finish source work for the day

Open [Finish Day](../FINISH_DAY.html) and complete its source-synchronization step. It validates, builds, commits, and pushes the source work.

For an ordinary day, stop here after Finish Day reports that the repository is clean and synchronized.

## 5. Build spreadsheet release files

When the next publication must replace the Matrix, Setup workbook, or both, open [Spreadsheet Workflows](spreadsheets.html) and build the required release families now. These verified Excel and Numbers files are machine-local release artifacts; they are not part of the source commit.

If spreadsheet downloads are unchanged and their source fingerprints are still current, continue to Step 6 without rebuilding them.

## 6. Publish the website

Open [Publish the Website](publish.html) only when you intentionally want to update GitHub Pages. Use ordinary publication when spreadsheet downloads remain current, or spreadsheet replacement publication after Step 5.

## 7. Verify the publication and final Git state

Complete both publication verification and the final clean-and-synchronized Git check described on [Publish the Website](publish.html). A clean Git report alone does not prove that publication succeeded.

## Continue on another Mac

Complete Steps 1–4 on the first Mac. Then open [Continue on Another Mac](other-mac.html) before resuming the project elsewhere.

## Recovery and troubleshooting

Open [Recovery and Troubleshooting](recovery.html) at the first failed safety check. Stop rather than guessing when Git is behind, diverged, a build fails, spreadsheet preparation fails, or publication is not verified.
