# Profile Editor

Profile Editor 1.0 is the project's main local interface for routine work: shooting profiles, persisted My Menu organization and card colors, baseline setup, session review, local builds, and camera reference. It provides a Canon-sourced EOS R5 still-photo settings dictionary, loads and saves the reviewed My Menu layout, renders isolated shooting and reference-card previews, can create, duplicate, or update shooting-profile YAML, can apply a complete reviewed baseline migration, and can run the guarded normal local build after every browser draft is resolved.

Use the specialized workflow pages—not the editor—for Git preflight and handoff, manual spreadsheet preparation or recovery, testing-status import, physical-camera verification, commits and pushes, and publication. The editor's confirmed local build automatically refreshes safely stale spreadsheet-derived artifacts.

The header shows the current checkout context, editor version, and deterministic short build identifier. **Main project** identifies the authoritative `main` worktree; **Prototype · branch-name** identifies a development worktree. The build identifier sits below the action row with its right edge aligned to **Stop Profile Editor**, and the silver camera logo is centered across both rows. If two open editor windows show different context or build identifiers, stop and use the application associated with the intended worktree before reviewing changes.

It cannot edit permanent reference cards, rename profiles, remove released cards, permanently delete cards, commit, push, merge, publish, or change website version metadata. It may move an unreleased editable card into recoverable Deleted Cards only through the dependency-checked, reviewed transaction described below. The shared baseline changes only through the guarded multi-file migration described below. My Menu tab names/items and their named-tab colors save together through their own guarded two-file transaction. **Review & Build** may refresh generated local output and tracked `docs/` only after all session drafts are resolved, readiness validation passes, and the user confirms the build.

## Start the editor

For routine use, double-click **R5 Profile Editor.app** in the machine-local `Applications` folder. The app starts Profile Editor in the background without opening Terminal and opens Google Chrome automatically. The main project uses `http://127.0.0.1:8765/`; a development worktree uses `http://127.0.0.1:8766/`, so the main reference and prototype can run together. Their application wrappers also have distinct macOS identities. Confirm the header badge before editing.

If that checkout's editor is already running but its Chrome window is missing, open **R5 Profile Editor.app** again. The launcher verifies and reopens the existing instance instead of starting a duplicate. Use **Stop Profile Editor** in the page header to stop its local server. The page closes its tab when browser policy permits; if it remains open, close it after the stopped confirmation appears. Unsaved browser drafts are identified in the confirmation before shutdown.

Build or refresh both local application wrappers from the repository root with:

```bash
./80\ Build/scripts/build-app-wrappers.sh
```

The wrappers are written to `Canon Camera Reference UI Prototype Local/Applications/` and retain a deliberate link to this authoritative project folder. Rebuild them after moving or renaming the project, or on another Mac. Startup and relaunch diagnostics are appended to the machine-local `Logs/R5 Profile Editor.log` file. The existing **Start Profile Editor.command** launcher remains available as a Terminal-based diagnostic fallback in the repository's top-level folder.

If no editor window is visible and reopening the app does not recover it, double-click **Stop Profile Editor.command** in the repository's top-level folder. It stops only a process that matches this checkout's exact editor program, working directory, and expected port. It also recognizes a verified prototype left on the former shared port 8765 so that one legacy instance can be cleared after upgrading. It removes stale process records automatically and refuses to stop an unrecognized service.

For development or diagnostics, use the Project Terminal panel on the [Workflow Index](index.html) to open the project worktree in Terminal. Then run:

```bash
npm run ui
```

Run the command from the repository root. It starts Profile Editor 1.0 without building or publishing the website.

Open the local address shown in Terminal. The normal addresses are:

```text
Main project: http://127.0.0.1:8765
Prototype:    http://127.0.0.1:8766
```

The editor is available only on this Mac while that command is running. Press **Control-C** in Terminal to stop it. It listens only on the local loopback address.

## Open the current profile in Camera Lab

Select a saved Subject/Profile Card and choose **Open in Camera Lab** in the header. Profile Editor starts the independent Camera Lab if needed, or reuses the existing Lab, then opens it with that saved profile preselected. Camera Lab reloads the current saved profile and C1–C3 assignments itself; the editor passes only the canonical profile name.

Save or discard ordinary profile edits first. The button is unavailable for a new or unsaved profile draft and for permanent reference cards. Opening the Lab does not connect the camera, scan it, compare it, or change a setting; use the Lab controls when ready. Stopping Profile Editor does not stop Camera Lab, and stopping Camera Lab does not stop Profile Editor.

## Follow the workspace order

The sidebar follows the normal editing flow: **Profiles**, **Cx Foundation**, **Deleted Cards**, **My Menu**, **Baseline Setup**, **Review & Build**, then **Camera Reference**. Numbered badges identify pending browser drafts. Moving to another profile or workspace preserves drafts in this browser session instead of silently discarding them. Moving from Profiles to Cx Foundation carries the selected saved shooting profile into **Profile to evaluate**. Review & Build collects every profile, Cx Foundation, My Menu, and baseline draft in one list. Refreshing or closing the page still clears session drafts, so the browser warns before leaving while any remain.

## Choose Cx foundations

Open **Cx Foundation** for the occasional decision about which complete shooting profile C1, C2, and C3 represent, or which slot a particular card should start from. Under **C1–C3 assignments**, choose three distinct editable profiles. Choosing a profile already used by another slot swaps the two assignments. Assignment changes remain approved targets pending physical camera verification; they do not claim that the camera has been reconfigured.

Under **Cx Foundation Fit**, use the full-width **Profile to evaluate** selector. A newly saved editable profile is added to this selector immediately. The editor compares its effective visible card rows with all three assignments simultaneously. Each result shows the number of field changes; combined card rows count once when any represented camera setting differs. Every lowest-count result is marked **Recommended**, but the editor never selects it automatically. Deliberately select C1, C2, C3, or **No Cx** as the final card route.

If the selected card has an unsaved Profiles draft, the fit uses those draft values, but save or discard that ordinary profile draft before saving its foundation choice. **Review assignment changes** synchronizes the two control mappings, registration headings and matching workflow labels, and affected card routes. It does not rewrite concrete C1–C3 registration values; use the Subject Settings Matrix and registration tracker to finalize those values. **Review foundation selection** changes only the selected card's Cx route and preserves its My Menu cues. Both actions show an exact diff and use the normal backup, concurrent-change, validation, and rollback safeguards.

## Work through camera reference

Open **Camera Reference**. Search the Shooting, AF, Playback, Wireless, Set-up, and Custom Functions dictionary or filter it by **Set Once**, **Situational**, **Ignore**, **Avoid**, or **Unresolved**. Every record identifies its direct camera-menu location, reset-default reference, project recommendation, whether it should be revisited, and the applicable Canon manual source.

The dictionary separates Canon reference facts from project recommendations. Menu names and locations are grounded in Canon's menu overviews. A reset default remains a working reference unless the linked Canon page states it explicitly. Neither the recommendation nor the temporary UI state proves the current physical camera setting.

**Touch & Drag AF** is represented by its three separate controls:

- Touch & Drag AF: Enable
- Positioning method: Relative
- Active touch area: Right

All three are project **Set Once** recommendations. The active touch area should be revisited if handedness, grip, or unintended face contact makes another area more reliable.

## Configure My Menu

Open **My Menu** only when changing the global camera tabs, shortcuts, names, or colors. Ordinary profile review/save automatically synchronizes that card's visible My Menu cues with the persisted layout and includes any cue changes in the exact profile YAML diff. The configurator follows the EOS R5 limit of five tabs with six items per tab and starts from the saved layout in `00 Master/my_menu.yaml`. **Reload saved layout** discards browser edits. **Restore recommended tabs** creates a draft of the approved **SWITCH** and **AF Case** recommendation without saving it.

Each used tab requires a name, one to six unique ordered items, and a distinct **Card color** from the curated palette. Light Red is visibly red; Coral is more orange. Choose **Review My Menu changes** to validate the complete layout and inspect the exact diffs for `00 Master/my_menu.yaml` and `00 Master/my_menu_colors.yaml`. **Save reviewed My Menu** creates a machine-local recovery backup, checks both source fingerprints, writes only the reviewed changed bytes, runs source validation, and restores every written file automatically if validation fails. Saved colors apply consistently to matching card route tokens, setting values, `Δ` indicators, PDF cards, field-guide My Menu tokens, and My Menu reference-card section headings.

Choose **Analyze profile impact** at any time to evaluate the current browser My Menu draft before or after saving it. The editor opens **Baseline Setup** and focuses the shared My Menu coverage report. The analysis is read-only and remains available when no baseline setting changed. It identifies card cues whose tab or shortcut has been removed and displayed configured shortcuts that need a profile-card cue.

Supported shortcuts are matched by setting identity, not by whether they came from **Restore recommended tabs**. For example, AF Operation, Eye Detection, and ISO speed settings in a newly created tab are checked against their corresponding profile card rows. A saved shortcut that has no supported card-setting identity remains visible as an unrepresented configured item instead of being assigned by guesswork.

The dictionary shows a **Configured shortcut** only after an item is selected in this configurator. This keeps the direct Canon menu location authoritative and prevents the UI from claiming a My Menu path that was never configured in the draft.

The saved layout is the approved project reference, not proof that the physical camera currently matches it. Compare the generated My Menu card with the camera after a reset, firmware update, or deliberate on-camera menu change.

## Use the My Menu reference card

The released **My Menu** card appears under **Camera Setup & Controls** beside **Camera Buttons** and is read-only in the Profiles view. Choose it and select **Render reference preview** to see the current field reminder without saving anything. Each used saved tab becomes a separate section in `MY MENU1`–`MY MENU5` order, followed by its saved shortcuts in item order. Adding, renaming, reordering, or removing a used tab through **My Menu** changes the next preview and normal build automatically.

After scrolling down in any editor tab, use the floating circular **↑** control at the lower right to return to the top. It is available throughout Profiles, Cx Foundation, My Menu, Baseline Setup, Review & Build, and Camera Reference and disappears near the top.

## Use Baseline Setup

Open **Baseline Setup** to test how proposed baseline values would affect the authored profiles or to inspect My Menu coverage without changing the baseline. **Analyze draft** remains enabled after the baseline loads. The report separates inherited changes from profiles protected by existing overrides, identifies overrides that would become redundant, and always includes current My Menu route coverage.

For every inherited profile change, deliberately choose one result:

- **Follow proposed baseline** changes that profile's effective value and adds no override.
- **Preserve previous value as override** keeps that profile's prior effective value by proposing a new override.

The bulk buttons above the report fill unresolved choices across the complete proposal. Each changed-setting panel also provides **Follow baseline for this setting** and **Preserve previous for this setting** to fill unresolved profiles for that setting only. Neither form of bulk action replaces choices already made individually. Choose **Build migration plan** above the report or use the matching action after the setting-preference results. Both validate the same current choices on the server. The plan lists profiles following the baseline, overrides to add, redundant overrides to remove, protected overrides to retain, existing card rows to color-code with their My Menu access, and unresolved items. Each My Menu suggestion applies to a setting already shown on the card: the setting uses the color of the My Menu tab where it can be found, and that tab's name appears at the top of the card. Nothing new is added to the card or to the camera's My Menu. A plan is complete only when every inherited change has a choice and no invalid override remains.

The analysis also includes a **C1–C3 effective impact** report. For each proposed baseline setting, it shows the effective before-and-after value in **C1 Wildlife**, **C2 Birds in Flight**, and **C3 Landscape**. **Changes with baseline** means that registered mode inherits the affected value. **Protected by C1/C2/C3 registration** means an explicit registration value keeps the effective mode unchanged.

The starting-mode warning list identifies profiles whose declared `C1`, `C2`, or `C3` starting route would be affected, together with the route's declared source profile and affected settings. Treat these as review warnings only. This increment does not rewrite C1–C3 registrations, profile routes, source-profile declarations, or My Menu assignments.

The **My Menu card coverage** report uses the My Menu arrangement currently shown in the browser and the fully merged settings actually listed on each card. My Menu remains a stable fast path to buried settings; matching a C1–C3 starting value does not make a shortcut unnecessary. Expand a profile to see which declared settings are shown on its card and whether the corresponding Canon item is available in the named tab.

The renderer shows a My Menu tab on a card whenever at least one setting assigned to that tab is visible. If conditional card rules hide every assigned setting, the tab is omitted from that card without changing My Menu or recommending removal. The report separately lists displayed configured shortcuts without a card cue; **Newly visible** means a baseline proposal caused that conditional row to appear. Camera Defaults is included as an access-only card.

The global **Configured shortcuts not referenced by any card** note identifies possible shortcuts to remove from the camera configuration; the editor never changes My Menu automatically. Card-cue cleanup is different: when the current draft removes a tab or removes a supported shortcut from its named tab, every matching card cue is listed under **Card cues to remove** and included automatically in the migration plan. This applies even when a conditional card rule currently hides the setting because the stored access route is no longer true. A renamed tab or moved shortcut produces a removal from the old tab and an addition to the new tab.

Conversely, each displayed configured shortcut without an authored card cue on an editable profile card is automatically included in the migration plan as an existing card row to color-code for its target tab. This applies to C1–C3 routes, subject cards without a Cx foundation, and profile-based reference cards. Cue additions and removals change only route labels and colors; they add or remove neither setting rows on cards nor items in the camera's My Menu. They are written only if the complete migration is reviewed and applied.

Changing a My Menu tab name or item, or restoring the recommended tabs, clears an existing impact report and migration review; choose **Analyze draft** again to evaluate the new session arrangement. Coverage findings do not modify the My Menu draft, saved profile routes, or registrations. Known obsolete cues are rewritten only through the reviewed migration; unresolved identities remain warnings.

The view cannot add, remove, or rename baseline setting paths. An incomplete plan remains session-only. When the plan is complete, acknowledge both the C1–C3 and My Menu warning reports, then choose **Review exact migration YAML**. The editor validates the proposed baseline and every affected profile together and shows one exact multi-file diff. **Apply reviewed migration** writes only those reviewed bytes.

The migration updates the baseline, adds selected preservation overrides, removes newly redundant overrides, retains protected overrides, removes obsolete My Menu card cues, and adds missing cues. Empty cue tabs are removed; empty migration-created access-only routing is cleaned up when its last cue is gone. It does not rewrite C1–C3 registrations, starting routes, source-profile declarations, unresolved identities, or the camera/My Menu draft. Before writing, it verifies that every source still matches the review, creates a recovery backup with all prior and candidate files, writes each file atomically, and runs source validation. If any write or validation fails, every file already written is restored. A successful migration reloads the baseline and profile data in the editor.

When the baseline is unchanged and the plan contains only My Menu card-cue additions or removals, the reviewed migration contains only the affected profile files. It does not touch the baseline merely to permit the profile update. If analysis finds no baseline or profile source change, the plan says no migration is required and offers no save action.

The draft, decisions, and unapplied plan exist only in browser memory; refreshing the page, closing the tab, or stopping the server discards them. The analysis reads the baseline and profiles loaded when the editor server started, so restart the server after external source changes.

### Check baseline impact outside the editor

The shared impact rules also have a read-only command-line check. To compare an uncommitted worktree baseline with `HEAD`, run:

```bash
python3 "80 Build/baseline_impact_check.py"
```

For branch integration, select the baseline branch explicitly:

```bash
python3 "80 Build/baseline_impact_check.py" --base-ref origin/main
```

Status 0 means there is no semantic baseline-default change. Status 1 prints the changed settings and affected profile classifications and requires review through the Baseline Setup workflow above. Status 2 means the comparison could not be completed. The command ignores metadata-only and YAML-formatting differences and never writes a migration.

## Edit or preview a profile

1. Open **Profiles**.
2. Choose an existing profile.
3. Follow the workflow strip from **Choose profile** through **Review & save**.
4. Review **Shown on this card** first. Its controls use the renderer's actual visible-setting rules and the same path order as `00 Master/card_layout.yaml`. Combined card rows, including ISO and tracking/acceleration, expose each underlying camera control together in that order.
5. Expand **Additional profile settings** for controls that are not currently rendered on the card. They remain grouped by camera-setting category.
6. Look for the **Inherited** or **Customized** label beside each setting.
7. Edit the title, optional subtitle, status, release state, **Card section**, and available setting controls. Card section chooses **Subjects** or **Camera Setup & Controls** index placement. Clearing any editable setting restores and immediately redisplays its inherited baseline value; an empty string is not stored as a profile override. C1/C2/C3 foundations remain comparison and field-start references, not inheritance sources.
8. Use **Use baseline** for one setting or **Use baseline for section** for an additional-settings group. Open **Profile actions** and choose **Restore saved profile** to abandon unsaved browser edits and reload the selected profile's saved source values. Selecting an enabled Profile action closes the menu.
9. Choose **Render preview** in the right-hand panel. On a desktop-width window, the settings and preview scroll independently so the card remains visible while settings are reviewed. On a narrower window, use the **Settings** and **Preview** pane controls.
10. After an edit, treat the retained preview as out of date until **Refresh preview** completes.
11. Choose **Review changes** in the persistent action bar only when the draft is ready to save. The review lists each effective setting change as its saved value and latest draft value before the exact YAML diff. It also synchronizes the candidate's visible My Menu cues with the persisted global layout, so you do not need to visit My Menu unless that global configuration itself is changing. When a customization is removed, the resulting inherited baseline value is named explicitly, such as **Aperture: Blank → Auto (inherited from baseline)**. For every setting, recognized text choices are case-insensitive and return to their canonical spelling before comparison, so `AUto` is treated as `Auto`; unrecognized custom values such as `f/8` remain unchanged.

On a preview or generated profile card, the C1/C2/C3 token remains white. My Menu-colored values keep their saved tab color whether or not they already match the selected foundation. A fixed rightmost column shows `Δ` in the same color as the setting value. With a Cx foundation, `Δ` compares the draft with the effective saved foundation profile—not with the baseline—and appears only when that row differs. Therefore **Use baseline** clears `Δ` only when the baseline value also matches the saved foundation. Without a Cx foundation, every visible settings row shows `Δ` because the project cannot prove the camera's current state; the legend says **Verify/set — no Cx foundation**. Permanent reference cards do not render the indicator column.

Exposure, Autofocus, and Drive controls use the editor's Canon EOS R5 options catalog. Each cataloged setting links to the applicable Canon manual page and uses the same approved setting/value icon system as the subject cards. The catalog is scoped to still photos on EOS R5 firmware 2.2.0 or later.

Canon choices, conditional Canon choices, and project compatibility values are labeled separately. For example, Canon defines One-Shot AF and Servo AF as AF Operation choices; this project retains Manual Focus in that field only for compatibility with existing profile data.

**Shooting Mode** is the exposure program used inside the profile. C1–C3 are registered recall slots, so they are intentionally selected in **Cx Foundation** rather than offered as Shooting Mode values.

Some fields allow both Canon choices and custom profile targets. ISO and exposure compensation profiles may contain a descriptive range or field instruction rather than one camera value, so those controls provide Canon suggestions without discarding the existing free-form behavior.

## Where the preview goes

The one disposable preview file is written under the prototype worktree's separate machine-local workspace:

```text
Canon Camera Reference UI Prototype Local/Build Output/cards/html/_Profile Editor Preview.html
```

Each preview replaces the prior disposable preview. No file under `10 Profiles/` or `docs/` is changed.

## Create or duplicate a profile

- Choose **New from baseline** to begin with no overrides.
- Choose **Duplicate profile** to copy the selected shooting profile's authored content and current overrides.
- For **New from baseline**, the YAML filename follows the card title automatically. Editing the filename directly stops that automatic link so a custom filename is preserved. Enter filenames without the `.yaml` suffix.
- The editor rejects an existing filename during review and checks again immediately before saving; matching is case-insensitive.
- New and duplicated profiles always begin as **Draft** and **not released**. Save once, then deliberately change those fields in a later update if appropriate.
- Reference cards cannot be duplicated or edited.

### Move and restore a saved unreleased card

Open **Profile actions → Move to Deleted Cards** only after unchecking release and saving that change, and after saving or restoring any other browser edits for that card. The action remains visible while disabled and its inline reason states what must be resolved. The editor checks immutable UUID relationships and blocks removal when the card is assigned to C1–C3, used as another card's Cx foundation, associated with an appendix, or named by any other registered structured reference. Narrative mentions are shown separately as review warnings. After dependency checks pass, the exact active-source removal is shown. **Move reviewed card** creates a recovery backup, writes the exact YAML and integrity manifest into machine-local Deleted Cards, removes active source, runs source validation, and restores active source automatically on failure.

Open **Deleted Cards** to review the on-page removal instructions or restore a held card. Never-saved browser drafts are discarded from Review & Build and do not enter Deleted Cards. Structured references must be removed before a saved card is eligible, and permanent reference cards are never eligible. Restore shows an exact YAML addition and requires a new one-use review. Filename or UUID conflicts block it. A successful restore validates active source before removing the holding entry. The editor provides no permanent purge action.

## Review and save

Every save requires **Review YAML changes**. The editor validates the complete candidate in an isolated temporary source layout and shows the exact YAML diff. **Save reviewed YAML** can write only those reviewed bytes.

Immediately before writing, the editor confirms that the loaded source did not change and that a new filename is still available. It then:

1. Creates a timestamped recovery backup under `Canon Camera Reference UI Prototype Local/Backups/`.
2. Replaces the target profile atomically.
3. Runs project source validation.
4. Automatically restores the prior source state if validation fails.

If another process changes the profile after it was loaded or reviewed, the editor blocks the save. Reload the profile, reapply the intended change, and review the new diff. A successful editor save changes source only; use **Review & Build** when you want refreshed cards or website output.

## Discard draft changes

Unsaved profile, My Menu, and baseline draft values live only in the open browser page. A reviewed My Menu save persists its tab layout in `00 Master/my_menu.yaml` and matching colors in `00 Master/my_menu_colors.yaml`.

- **Use baseline** removes the temporary override for one setting.
- **Use baseline for section** removes all temporary overrides in that section.
- **Restore saved profile** restores the selected profile's title, metadata, and saved overrides. This may bring back customized values that differ from the baseline.
- Selecting another profile preserves the current draft in the session ledger. Returning to that profile restores the draft.
- Reloading the page clears unsaved My Menu edits and reloads the persisted layout.
- **Discard baseline draft** restores every temporary baseline value to the currently loaded source baseline.
- Review & Build offers a confirmed **Discard** action for each pending item.
- Refreshing the page, closing the tab, or stopping the server discards all browser drafts; the browser warns before leaving when drafts remain.

Restarting the server is not required to discard a draft. A successful editor save reloads the in-memory profile list automatically. Restart the server when profile or catalog source files were changed by another tool while the editor was running.

## Review and build locally

Open **Review & Build** to validate the editing session before generation. Save each intended draft through its guarded review or choose **Discard** and confirm. The local build remains locked while the pending list is nonempty. When the verification working tracker contains results to retain, save and close Numbers or Excel, choose **Import verification tracker**, and confirm the deliberate import into canonical YAML status. The editor never imports workbook edits automatically. When the list is clear, choose **Validate readiness**. Readiness reports any stale verification, Matrix/settings, or Setup artifacts detected from their source fingerprints. Then choose **Run local build** and confirm that Apple Numbers may launch and generated local output and tracked documentation may change.

The guarded build runs source-only validation, conditionally refreshes only safely stale spreadsheet-derived artifacts, then runs the normal development build and full validation. It stops on the first failure and shows its output. If the verification working copy may contain unimported edits, readiness blocks before the build; import those edits through the testing workflow first. The build does not run Git, publish, or change website version metadata.

## Boundaries

The editor intentionally provides no released-profile removal, permanent deletion, existing-profile rename, direct baseline edit, reference-card edit, commit, push, merge, publish, or website-version action. Unreleased editable profiles may be moved only through the UUID dependency-checked, exact-diff, backed-up Deleted Cards transaction and restored through its matching guarded review. Baseline writes are available only through a complete reviewed migration. My Menu layout and colors are available only through their exact-diff guarded transaction. Review & Build offers the existing guarded tracker importer plus the guarded local build sequence; Git checkpoints and publication remain separate established workflows.

## Quick readiness check

To confirm that the editor can load all current profiles without starting the web interface, run:

```bash
python3 "80 Build/profile_editor.py" --check
```
