# Profile Editor User Guide

The Profile Editor is a local workspace for reviewing camera setup information, organizing My Menu, creating or updating shooting profiles, previewing cards, and evaluating shared baseline changes. This guide explains how to operate the editor. Use the camera reference materials when you need the meaning or recommended value of a particular field.

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
- Refreshing or closing the page discards unsaved drafts.

If source files change outside the editor, restart the editor before continuing. If the editor detects that a reviewed source changed, it blocks the save so you can reload and review again.

## Move around the editor

Use the four numbered tabs across the top:

1. **Camera setup** — Find and review setup records and their source links.
2. **Configure My Menu** — Arrange saved tabs, shortcuts, and card colors.
3. **Profiles** — Preview, create, duplicate, or update shooting profiles.
4. **Baseline impact** — Test a proposed shared change and review its effect across profiles.

Moving to another tab does not save work. Complete or deliberately discard a draft before switching tasks.

## Review camera setup

Use the search box to find a record by name or related wording. Use the classification filter to narrow the list by how the record is used in the project.

Each record provides its menu location, project guidance, status, and reference link. Treat the editor as an organized view of the source material; consult the linked references for field-level detail.

This section is for review and navigation. It does not write settings to the camera or prove the camera's current physical configuration.

## Configure My Menu

Open **Configure My Menu** to work with the saved navigation layout.

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

1. Review the profile title, release information, and grouped fields.
2. Use the state beside each field to see whether the value is inherited or customized.
3. Change only the fields needed for this profile.
4. Use **Use baseline** for a field or section when the profile should inherit the shared value again.
5. Choose **Preview card** and inspect the temporary card.
6. Choose **Review YAML changes** when the draft is ready.
7. Save only after the exact review matches the intended result.

Use **Discard draft & reload profile** to return the selected profile to its saved state.

On cards with a declared C1–C3 foundation, `Δ` identifies a value that differs from that foundation. On editable profile cards without a Cx foundation, every visible settings row uses `Δ` as a reminder to verify or set the target on the camera. My Menu colors identify where to find a setting and do not depend on a Cx foundation.

### Create or duplicate a profile

Use **New from baseline** for a profile that should begin with shared values and no custom fields. Use **Duplicate profile** when a new profile should begin from an existing editable profile.

Provide a unique filename and complete the same preview, review, and save process. New and duplicated profiles begin as unreleased drafts so they can be reviewed before release.

## Evaluate baseline impact

Use **Baseline impact** when considering a change to a shared value. This area is a planning workspace, not a quick-edit form.

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

## Finish the editing session

After the intended source changes are saved:

1. Run the project's normal local validation and build workflow separately.
2. Review the generated result.
3. Follow the established Finish Day or publishing workflow when appropriate.
4. Stop the editor with **Control-C** in its Terminal window.

The editor does not delete or rename existing profiles, edit permanent reference cards, run the normal build, commit, push, or publish.

## Get more help

For detailed safeguards, recovery behavior, and advanced baseline or My Menu behavior, open the [Profile Editor workflow reference](profile-editor.html). For camera-field meaning and recommendations, use the linked Canon and project reference materials.
