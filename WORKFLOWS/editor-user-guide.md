# Profile Editor User Guide

Profile Editor 1.0 is the main local interface for routine work: creating and updating shooting profiles, previewing cards, organizing My Menu, planning shared baseline changes, reviewing session drafts, validating and building, and looking up camera settings. Its confirmed local build refreshes safely stale spreadsheet-derived artifacts automatically. Use the specialized workflow pages for Git handoff, manual spreadsheet preparation or recovery, physical-camera testing and status import, and publication.

## Start the editor

From the project root, run:

```bash
npm run ui
```

Open the local address shown in Terminal. Keep that Terminal window open while using the editor. Press **Control-C** in Terminal when you are finished.

The editor runs only on this Mac. It does not publish the website or make Git changes.

## Understand the working model

The editor separates temporary work from saved source:

- Changes begin as a browser draft.
- A preview shows the result without saving it.
- A review step shows the exact source changes.
- A save is available only for the version that was reviewed.
- Profile drafts remain available while you move among profiles and workspaces in the same browser session.
- Refreshing or closing the page discards unsaved drafts, so the browser warns before leaving while changes remain.

If source files change outside the editor, restart the editor before continuing. If the editor detects that a reviewed source changed, it blocks the save so you can reload and review again.

## Move around the editor

Use the workspace sidebar:

- **Profiles** — Preview, create, duplicate, or update shooting profiles.
- **Cx Foundation** — Assign C1–C3 profiles, compare foundation fit, and make the final card-route selection.
- **Deleted Cards** — Review and restore unreleased cards removed from active source.
- **My Menu** — Arrange saved tabs, shortcuts, and card colors.
- **Baseline Setup** — Test a proposed shared change and review its effect across profiles.
- **Review & Build** — Resolve all browser drafts, validate source, and run the guarded local build.
- **Camera Reference** — Find and review setup records and their source links.

On narrower windows, the sidebar becomes a compact navigation row above the workspace.

Moving to another tab does not save work, but the sidebar badges and Review & Build list preserve and identify pending work for this browser session. When you move from Profiles to Cx Foundation, the selected saved shooting profile is carried into **Profile to evaluate** automatically.

## Choose a Cx foundation

Open **Cx Foundation** when the C1–C3 arrangement or a card's starting route needs deliberate review. This workspace is separate from Profiles because these decisions should change less often than ordinary card settings.

Under **C1–C3 assignments**, select three different editable shooting profiles. Choosing a profile already assigned to another slot swaps the two assignments, so all three remain distinct. The assignment describes the approved profile target for each camera slot; it does not prove that the physical camera has been updated or verified. Reviewing an assignment change shows every synchronized control record, registration heading, workflow label, and affected card route. Concrete C1–C3 setting values are intentionally left unchanged—use the Subject Settings Matrix and registration tracker to decide and finalize those values.

Under **Cx Foundation Fit**, use the prominent **Profile to evaluate** selector. Every saved editable card, including a newly created profile, is available immediately after it is saved. C1, C2, and C3 are compared simultaneously using the card's effective visible rows. Combined rows count as one field change when any represented setting differs. The lowest count is marked **Recommended**; ties remain equally recommended. The editor never makes the selection for you. Choose C1, C2, C3, or **No Cx**, then review and save that explicit choice.

If an unsaved Profiles draft exists for the selected card, the recommendation reflects that draft. Save or discard the Profiles draft before saving the card's foundation so the two reviewed changes cannot conflict. Cx Foundation drafts appear in **Review & Build** and keep the local build locked until saved or discarded.

## Review the camera reference

Use the search box to find a record by name or related wording. Use the classification filter to narrow the list by how the record is used in the project.

Each record provides its menu location, project guidance, status, and reference link. Treat the editor as an organized view of the source material; consult the linked references for field-level detail.

This section is for review and navigation. It does not write settings to the camera or prove the camera's current physical configuration.

## Configure My Menu

Open **My Menu** only when you intend to change the saved global camera navigation layout, its shortcuts, tab names, or colors. Ordinary profile review/save automatically maps that card's visible rows to the persisted My Menu layout and includes any cue changes in the exact profile diff.

- Edit a tab name, select its ordered shortcuts, and choose its card color.
- Keep each used tab valid and each selected shortcut unique where the editor requires it.
- Use **Reload saved layout** to discard browser edits and return to the saved version.
- Use **Restore recommended tabs** to create a recommended draft without saving it.
- Choose **Review My Menu changes** when the complete layout is ready.

The review shows the exact changes. Read the review, then use the save action only if it matches your intent. A successful save updates the project source; it does not update the physical camera.

### Remove a tab or shortcut from cards

To remove a complete tab, clear all of its shortcut slots and its tab name. To remove one shortcut, clear only that shortcut slot. Review and save the My Menu changes, then choose **Analyze profile impact**.

The coverage report lists every stored card cue that no longer matches the saved tab layout under **Card cues to remove**. Build the migration plan, confirm the **Obsolete My Menu card cues to remove** list, review the exact profile YAML, and apply the migration. A renamed tab or moved shortcut is shown as removal from the old tab and addition to the new one. The migration changes the cards' access labels and colors; it does not remove setting rows from the cards or make another change to the camera's My Menu.

## Work with profiles

Open **Profiles**, then select a profile from the menu. Reference cards can be previewed but not edited.

For an editable profile:

1. Follow the profile workflow shown above the workspace: choose, edit, preview, then review and save.
2. Review the profile title, release information, and **Card section**. Choose **Subjects** or **Camera Setup & Controls** to control where the released card appears in the index. Unchecking release excludes the card from the bundle after review/save; it does not remove active source.
3. Work through **Shown on this card** in the exact order used by the generated card. A single card row can be backed by more than one camera control, such as ISO mode and Auto ISO maximum.
4. Expand **Additional profile settings** only when you need a control that is not currently rendered on the card.
5. Use the state beside each field to see whether the value is inherited or customized.
6. Change only the fields needed for this profile.
7. Use **Use baseline** for a field or section when the profile should inherit the shared value again. Clearing any editable field has the same result and immediately redisplays the baseline value. C1/C2/C3 foundations remain starting and comparison references rather than inheritance sources.
8. Use **Render preview** in the right-hand preview panel. The panel remains visible while the settings column scrolls independently.
9. Choose **Review changes** from the persistent action bar when the draft is ready.
10. Save only after the effective before-and-after settings and the exact YAML review match the intended result. When a customization is removed, the review names the resulting inherited baseline value explicitly instead of showing only the YAML deletion. Recognized text choices use their standard capitalization across every setting, so a case-only variation such as `AUto` is treated as `Auto`, while a genuine custom value such as `f/8` is preserved.

After a setting changes, the existing preview remains available but is labeled as out of date. Choose **Refresh preview** before relying on it. On narrower windows, use the **Settings** and **Preview** controls to switch between the two panes.

Open **Profile actions** and choose **Restore saved profile** to abandon unsaved browser edits and return the selected profile to its saved source state. Choosing an enabled Profile action closes the menu.

For a saved card that is still unreleased, **Profile actions → Move to Deleted Cards** provides a recoverable removal workflow. When disabled, the menu explains exactly what must be saved, restored, or unreferenced first. The editor checks UUID-based C1–C3 assignments, other card foundations, appendix associations, and every other registered structured reference. Any dependency blocks removal. Narrative document mentions appear separately as warnings for review. Confirming preserves the exact source and an integrity manifest in machine-local Deleted Cards, removes the active source, and validates the project; any failure restores active source automatically.

Open **Deleted Cards** to see the complete removal sequence and review inactive held cards. A saved card must first be unchecked for release, reviewed, and saved; then use **Profile actions → Move to Deleted Cards**. Never-saved browser drafts are discarded through Review & Build instead and never enter this holding area. Structured references block removal until resolved, and permanent reference cards are never eligible. **Review restore** shows the exact YAML addition. Restore is blocked if the original filename or immutable card identity is already active, and a successful reviewed restore returns the exact held bytes to active source and removes the holding entry. The normal editor provides no permanent purge action.

On cards with a declared C1–C3 foundation, `Δ` identifies a value that differs from that saved foundation—not from the baseline. Choosing **Use baseline** clears `Δ` only when the baseline value also matches the saved foundation. On editable profile cards without a Cx foundation, every visible settings row uses `Δ` as a reminder to verify or set the target on the camera. My Menu colors identify where to find a setting and do not depend on a Cx foundation.

### Create or duplicate a profile

Use **New from baseline** for a profile that should begin with shared values and no custom fields. Open **Profile actions** and choose **Duplicate profile** when a new profile should begin from an existing editable profile.

Provide a unique filename and complete the same preview, review, and save process. New and duplicated profiles begin as unreleased drafts so they can be reviewed before release.

The **Shooting Mode** field describes the exposure program used inside the profile, such as Fv, Tv, Av, M, or Bulb. C1, C2, and C3 are saved recall slots and are assigned separately in **Cx Foundation**.

## Evaluate Baseline Setup

Use **Baseline Setup** when considering a change to a shared value. This area is a planning workspace, not a quick-edit form.

1. Change one or more draft values.
2. Choose **Analyze draft**.
3. Review which profiles would follow the proposal and which are protected by existing customization.
4. For each affected inherited value, choose whether the profile should follow the proposed baseline or preserve its previous value as a customization.
5. Build the migration plan and review all warnings and route effects.
6. Review the exact multi-file changes only when the plan is complete.
7. Apply the migration only when every listed change matches the intended result.

Use **Discard baseline draft** to abandon the proposal. Refreshing the page also clears an unapplied analysis and its decisions.

## Preview, review, and save safely

A preview is disposable and may replace the previous editor preview. It does not change profile source or the released website.

A review is tied to the exact draft and source state shown. If you edit the draft after reviewing it, review again before saving. When a save succeeds, the editor creates a recovery backup and validates the source.

If validation or a concurrent-change check fails, stop and read the message. Reload the affected source rather than trying to force the prior review through.

## Review the session and build locally

Open **Review & Build** before finishing:

1. Review every pending profile, Cx Foundation, My Menu, and baseline draft.
2. Open each draft and save it through its exact-diff review, or choose **Discard** and confirm that decision.
3. If the verification workbook has edits to bring into the project, save and close Numbers or Excel, then choose **Import verification tracker** and confirm. The editor uses the existing importer and displays its result; it never imports automatically.
4. When the pending list is empty, choose **Validate readiness**. It reports whether verification, Matrix/settings, or Setup spreadsheet-derived artifacts need refresh.
5. After readiness passes, choose **Run local build**, read the final warning—including whether Apple Numbers may launch—and confirm.
6. Review the generated result, then follow the established Finish Day or publishing workflow separately when appropriate.
7. Stop the editor with **Control-C** in its Terminal window.

The guarded action runs source-only validation, refreshes only safely stale spreadsheet-derived artifacts when needed, then runs the normal development build and full validation. If the verification tracker may contain unimported edits, readiness stops and directs you to import them first. The action may refresh local output and tracked documentation, but it does not rename profiles, edit permanent reference cards, permanently delete cards, commit, push, publish, or change website version metadata. Recoverable unreleased-card removal is available only through the separate reviewed Deleted Cards action described above.

## Get more help

For detailed safeguards, recovery behavior, and advanced baseline or My Menu behavior, open the [Profile Editor workflow reference](profile-editor.html). For camera-field meaning and recommendations, use the linked Canon and project reference materials.
