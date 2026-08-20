# Profile Editor

This Stage 2 local editor is a safe way to work through camera setup, persisted My Menu organization and card colors, baseline impact, and shooting profiles. It provides a Canon-sourced EOS R5 still-photo settings dictionary, loads and saves the reviewed My Menu layout, renders isolated shooting and reference-card previews, can create, duplicate, or update shooting-profile YAML, and can apply a complete reviewed baseline migration.

The header shows the editor version and a deterministic short build identifier. If two open editor windows show different build identifiers, use the window connected to the current server and reload it before reviewing changes.

It cannot edit permanent reference cards, rename or delete profiles, or run the normal website build, change `docs/`, commit, push, merge, or publish anything. The shared baseline changes only through the guarded multi-file migration described below. My Menu tab names/items and their named-tab colors save together through their own guarded two-file transaction.

## Start the editor

Use the Project Terminal panel on the [Workflow Index](index.html) to open the prototype worktree in Terminal. Then run:

```bash
npm run ui
```

Run the command from the repository root. It starts the guarded Stage 2 editor without building or publishing the website.

Open the local address shown in Terminal, normally:

```text
http://127.0.0.1:8765
```

The editor is available only on this Mac while that command is running. Press **Control-C** in Terminal to stop it. It listens only on the local loopback address.

## Work through camera setup

The prototype opens on **Camera setup**. Search the Shooting, AF, Playback, Wireless, Set-up, and Custom Functions dictionary or filter it by **Set Once**, **Situational**, **Ignore**, **Avoid**, or **Unresolved**. Every record identifies its direct camera-menu location, reset-default reference, project recommendation, whether it should be revisited, and the applicable Canon manual source.

The dictionary separates Canon reference facts from project recommendations. Menu names and locations are grounded in Canon's menu overviews. A reset default remains a working reference unless the linked Canon page states it explicitly. Neither the recommendation nor the temporary UI state proves the current physical camera setting.

**Touch & Drag AF** is represented by its three separate controls:

- Touch & Drag AF: Enable
- Positioning method: Relative
- Active touch area: Right

All three are project **Set Once** recommendations. The active touch area should be revisited if handedness, grip, or unintended face contact makes another area more reliable.

## Configure My Menu

Open **Configure My Menu** after reviewing setup. The configurator follows the EOS R5 limit of five tabs with six items per tab and starts from the saved layout in `00 Master/my_menu.yaml`. **Reload saved layout** discards browser edits. **Restore recommended tabs** creates a draft of the approved **SWITCH** and **AF Case** recommendation without saving it.

Each used tab requires a name, one to six unique ordered items, and a distinct **Card color** from the curated palette. Light Red is visibly red; Coral is more orange. Choose **Review My Menu changes** to validate the complete layout and inspect the exact diffs for `00 Master/my_menu.yaml` and `00 Master/my_menu_colors.yaml`. **Save reviewed My Menu** creates a machine-local recovery backup, checks both source fingerprints, writes only the reviewed changed bytes, runs source validation, and restores every written file automatically if validation fails. Saved colors apply consistently to matching card route tokens, setting values, `Δ` indicators, PDF cards, field-guide My Menu tokens, and My Menu reference-card section headings.

Choose **Analyze profile impact** at any time to evaluate the current browser My Menu draft before or after saving it. The editor opens Baseline Impact and focuses the shared My Menu coverage report. The analysis is read-only and remains available when no baseline setting changed. It identifies old tab names that profiles can no longer find and displayed configured shortcuts that need a profile-card cue.

Supported shortcuts are matched by setting identity, not by whether they came from **Restore recommended tabs**. For example, AF Operation, Eye Detection, and ISO speed settings in a newly created tab are checked against their corresponding profile card rows. A saved shortcut that has no supported card-setting identity remains visible as an unrepresented configured item instead of being assigned by guesswork.

The dictionary shows a **Configured shortcut** only after an item is selected in this configurator. This keeps the direct Canon menu location authoritative and prevents the UI from claiming a My Menu path that was never configured in the draft.

The saved layout is the approved project reference, not proof that the physical camera currently matches it. Compare the generated My Menu card with the camera after a reset, firmware update, or deliberate on-camera menu change.

## Use the My Menu reference card

The released **My Menu** card appears under **Camera Setup & Controls** beside **Camera Buttons** and is read-only in the Profiles view. Choose it and select **Preview reference card** to see the current field reminder without saving anything. Each used saved tab becomes a separate section in `MY MENU1`–`MY MENU5` order, followed by its saved shortcuts in item order. Adding, renaming, reordering, or removing a used tab through **Configure My Menu** changes the next preview and normal build automatically.

After scrolling down in any editor tab, use the floating circular **↑** control at the lower right to return to the top. It is available in Camera setup, Configure My Menu, Profiles, and Baseline Impact and disappears near the top.

## Preview baseline impact

Open **Baseline impact** to test how proposed baseline values would affect the authored profiles or to inspect My Menu coverage without changing the baseline. **Analyze draft** remains enabled after the baseline loads. The report separates inherited changes from profiles protected by existing overrides, identifies overrides that would become redundant, and always includes current My Menu route coverage.

For every inherited profile change, deliberately choose one result:

- **Follow proposed baseline** changes that profile's effective value and adds no override.
- **Preserve previous value as override** keeps that profile's prior effective value by proposing a new override.

The bulk buttons above the report fill unresolved choices across the complete proposal. Each changed-setting panel also provides **Follow baseline for this setting** and **Preserve previous for this setting** to fill unresolved profiles for that setting only. Neither form of bulk action replaces choices already made individually. Choose **Build migration plan** above the report or use the matching action after the setting-preference results. Both validate the same current choices on the server. The plan lists profiles following the baseline, overrides to add, redundant overrides to remove, protected overrides to retain, existing card rows to color-code with their My Menu access, and unresolved items. Each My Menu suggestion applies to a setting already shown on the card: the setting uses the color of the My Menu tab where it can be found, and that tab's name appears at the top of the card. Nothing new is added to the card or to the camera's My Menu. A plan is complete only when every inherited change has a choice and no invalid override remains.

The analysis also includes a **C1–C3 effective impact** report. For each proposed baseline setting, it shows the effective before-and-after value in **C1 Wildlife**, **C2 Birds in Flight**, and **C3 Landscape**. **Changes with baseline** means that registered mode inherits the affected value. **Protected by C1/C2/C3 registration** means an explicit registration value keeps the effective mode unchanged.

The starting-mode warning list identifies profiles whose declared `C1`, `C2`, or `C3` starting route would be affected, together with the route's declared source profile and affected settings. Treat these as review warnings only. This increment does not rewrite C1–C3 registrations, profile routes, source-profile declarations, or My Menu assignments.

The **My Menu card coverage** report uses the My Menu arrangement currently shown in the browser and the fully merged settings actually listed on each card. My Menu remains a stable fast path to buried settings; matching a C1–C3 starting value does not make a shortcut unnecessary. Expand a profile to see which declared settings are shown on its card and whether the corresponding Canon item is available in the named tab.

The renderer shows a My Menu tab on a card whenever at least one setting assigned to that tab is visible. If conditional card rules hide every assigned setting, the tab is omitted from that card without changing My Menu or recommending removal. The report separately lists displayed configured shortcuts without a card cue; **Newly visible** means a baseline proposal caused that conditional row to appear. Camera Defaults is included as an access-only card.

The global **Configured shortcuts not referenced by any card** note is the only removal-oriented finding. It lists shortcuts whose setting is not displayed on any card and describes them only as possible removal candidates; the editor never changes My Menu automatically. Conversely, each displayed configured shortcut without an authored card cue on an existing C1–C3 route is automatically included in the migration plan as an existing card row to color-code for its target tab. This adds no card field and no camera My Menu item. The cue is written only if the complete migration is reviewed and applied.

Changing a My Menu tab name or item, or restoring the recommended tabs, clears an existing impact report and migration review; choose **Analyze draft** again to evaluate the new session arrangement. Coverage findings do not modify the My Menu draft, saved profile routes, or registrations. Unavailable, unnecessary, and unresolved routes remain warnings and are not rewritten by migration.

The view cannot add, remove, or rename baseline setting paths. An incomplete plan remains session-only. When the plan is complete, acknowledge both the C1–C3 and My Menu warning reports, then choose **Review exact migration YAML**. The editor validates the proposed baseline and every affected profile together and shows one exact multi-file diff. **Apply reviewed migration** writes only those reviewed bytes.

The migration updates the baseline, adds selected preservation overrides, removes newly redundant overrides, retains protected overrides, and adds the planned My Menu card cues. It does not rewrite C1–C3 registrations, starting routes, source-profile declarations, unused routes, unavailable routes, or the camera/My Menu draft. Before writing, it verifies that every source still matches the review, creates a recovery backup with all prior and candidate files, writes each file atomically, and runs source validation. If any write or validation fails, every file already written is restored. A successful migration reloads the baseline and profile data in the editor.

When the baseline is unchanged and the plan contains only missing My Menu card cues, the reviewed migration contains only the affected profile files. It does not touch the baseline merely to permit the profile update. If analysis finds no baseline or profile source change, the plan says no migration is required and offers no save action.

The draft, decisions, and unapplied plan exist only in browser memory; refreshing the page, closing the tab, or stopping the server discards them. The analysis reads the baseline and profiles loaded when the editor server started, so restart the server after external source changes.

## Edit or preview a profile

1. Open **Profiles**.
2. Choose an existing profile.
3. Review the grouped camera settings.
4. Look for the **Inherited** or **Customized** label beside each setting.
5. Edit the title, optional subtitle, status, release state, and available setting controls.
6. Use **Use baseline** for one setting, **Use baseline for section** for a group, or **Discard draft & reload profile** to restore the selected profile's saved source values.
7. Choose **Preview card** to render the temporary draft with the established card renderer.
8. Choose **Review YAML changes** only when the draft is ready to save.

On a preview or generated profile card, the C1/C2/C3 token remains white. My Menu-colored values keep their saved tab color whether or not they already match the selected foundation. A fixed rightmost column shows `Δ` in the same color as the setting value only when that row differs from the effective profile named as the Cx foundation. A blank indicator cell means no field change is required for that row. The legend below Settings names the foundation used for the comparison.

Exposure, Autofocus, and Drive controls use the prototype's Canon EOS R5 options catalog. Each cataloged setting links to the applicable Canon manual page and uses the same approved setting/value icon system as the subject cards. The catalog is scoped to still photos on EOS R5 firmware 2.2.0 or later.

Canon choices, conditional Canon choices, and project compatibility values are labeled separately. For example, Canon defines One-Shot AF and Servo AF as AF Operation choices; this project retains Manual Focus in that field only for compatibility with existing profile data.

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
- Enter a new YAML filename without the `.yaml` suffix.
- New and duplicated profiles always begin as **Draft** and **not released**. Save once, then deliberately change those fields in a later update if appropriate.
- Reference cards cannot be duplicated or edited.

## Review and save

Every save requires **Review YAML changes**. The editor validates the complete candidate in an isolated temporary source layout and shows the exact YAML diff. **Save reviewed YAML** can write only those reviewed bytes.

Immediately before writing, the editor confirms that the loaded source did not change and that a new filename is still available. It then:

1. Creates a timestamped recovery backup under `Canon Camera Reference UI Prototype Local/Backups/`.
2. Replaces the target profile atomically.
3. Runs project source validation.
4. Automatically restores the prior source state if validation fails.

If another process changes the profile after it was loaded or reviewed, the editor blocks the save. Reload the profile, reapply the intended change, and review the new diff. A successful editor save changes source only; run the normal local build separately when you want refreshed cards or website output.

## Discard draft changes

Unsaved profile, My Menu, and baseline-impact draft values live only in the open browser page. A reviewed My Menu save persists its tab layout in `00 Master/my_menu.yaml` and matching colors in `00 Master/my_menu_colors.yaml`.

- **Use baseline** removes the temporary override for one setting.
- **Use baseline for section** removes all temporary overrides in that section.
- **Discard draft & reload profile** restores the selected profile's title, metadata, and saved overrides. This may bring back customized values that differ from the baseline.
- Selecting another profile discards the current draft and loads the selected profile. Returning to the first profile loads its original saved overrides again.
- Reloading the page clears unsaved My Menu edits and reloads the persisted layout.
- **Discard baseline draft** restores every temporary baseline value to the currently loaded source baseline.
- Refreshing the page, closing the tab, or stopping the server discards all browser drafts.

Restarting the server is not required to discard a draft. A successful editor save reloads the in-memory profile list automatically. Restart the server when profile or catalog source files were changed by another tool while the editor was running.

## Boundaries

The editor intentionally provides no profile deletion, existing-profile rename, direct baseline edit, reference-card edit, build, commit, push, merge, or publish action. Baseline writes are available only through a complete reviewed migration. My Menu layout and colors are available only through their exact-diff guarded transaction. Use the established project workflows for validation, Git checkpoints, and publication.

## Quick readiness check

To confirm that the editor can load all current profiles without starting the web interface, run:

```bash
python3 "80 Build/profile_editor.py" --check
```
