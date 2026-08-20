# Project Workflow Index

Follow this order during a typical project day. Spreadsheet testing status and spreadsheet release files have separate places in the sequence.

Use the **Project Terminal** panel at the top of the generated HTML guide to copy the displayed `cd` command, then paste it into an open Terminal session.

## 1. Preflight before editing

Open [Preflight](preflight.html) to confirm this Mac has the current source and is safe to use.

## 2. Develop, build, and test

Open [Profile Editor](profile-editor.html) as the main interface for routine profile, My Menu, baseline, camera-reference, session-review, validation, and local-build work. Its guarded saves require exact YAML review, recovery backup, concurrent-change checks, and validation. **Review & Build** inventories pending drafts and can run the normal local sequence only after every draft is saved or discarded and readiness passes.

Open [Local Build](local-build.html) for the equivalent terminal commands, troubleshooting, or project changes outside the editor's scope. For routine generated-result review, open `Canon Camera Reference Local/Build Output/merged-build/index.html`, not intermediate card files or the Git-tracked `docs/` publication mirror. Git actions and publishing remain separate workflows.

## 3. Record spreadsheet testing status

For camera setup and physical testing, open [On-Camera Verification Testing](verification-testing.html). It opens or creates the correct machine-local tracker, explains the required test order and evidence rules, and covers the complete import and two-Mac handoff cycle.

If you updated the machine-local verification workbook, close it and import its testing status into Git-tracked YAML. Do this before Finish Day so the status is included in the source commit.

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

For camera testing specifically, follow the two-Mac procedure in [On-Camera Verification Testing](verification-testing.html). Transfer status through Git-tracked YAML rather than copying the active tracker between Macs.

## Recovery and troubleshooting

Open [Recovery and Troubleshooting](recovery.html) at the first failed safety check. Stop rather than guessing when Git is behind, diverged, a build fails, spreadsheet preparation fails, or publication is not verified.
