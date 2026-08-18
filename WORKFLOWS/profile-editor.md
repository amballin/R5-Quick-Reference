# Profile Editor

This Stage 2 local editor is a safe way to work through camera setup, My Menu organization, baseline impact, and shooting profiles. It provides a Canon-sourced EOS R5 still-photo settings dictionary, keeps temporary My Menu and baseline-impact drafts, renders isolated card previews, and can create, duplicate, or update shooting-profile YAML through a guarded review-and-save transaction.

It cannot edit permanent reference cards, the shared baseline, or saved My Menu configuration. It cannot rename or delete profiles and does not run the normal website build, change `docs/`, commit, push, merge, or publish anything.

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

Open **Configure My Menu** after reviewing setup. The temporary configurator follows the EOS R5 limit of five tabs with six items per tab and starts with the approved **SWITCH** and **AF Case** layouts. The remaining tabs and slots start empty. Modify that session-only arrangement as needed, or choose **Restore recommended tabs** to replace it with the approved recommendation.

The dictionary shows a **Configured shortcut** only after an item is selected in this configurator. This keeps the direct Canon menu location authoritative and prevents the UI from claiming a My Menu path that was never configured in the draft.

The My Menu draft is explicitly unverified and exists only in the current browser session. It does not save to project YAML and does not prove the physical camera matches the draft.

## Preview baseline impact

Open **Baseline impact** to test how proposed baseline values would affect the authored profiles. Change one or more existing values, then choose **Analyze draft**. The report separates inherited changes from profiles protected by existing overrides and identifies overrides that would become redundant.

For every inherited profile change, deliberately choose one result:

- **Follow proposed baseline** changes that profile's effective value and adds no override.
- **Preserve previous value as override** keeps that profile's prior effective value by proposing a new override.

The bulk buttons above the report fill unresolved choices across the complete proposal. Each changed-setting panel also provides **Follow baseline for this setting** and **Preserve previous for this setting** to fill unresolved profiles for that setting only. Neither form of bulk action replaces choices already made individually. Choose **Build migration plan** at any time to validate the current choices on the server. The plan lists profiles following the baseline, overrides to add, redundant overrides to remove, protected overrides to retain, and unresolved items. A plan is complete only when every inherited change has a choice and no invalid override remains.

The analysis also includes a **C1–C3 effective impact** report. For each proposed baseline setting, it shows the effective before-and-after value in **C1 Wildlife**, **C2 Birds in Flight**, and **C3 Landscape**. **Changes with baseline** means that registered mode inherits the affected value. **Protected by C1/C2/C3 registration** means an explicit registration value keeps the effective mode unchanged.

The starting-mode warning list identifies profiles whose declared `C1`, `C2`, or `C3` starting route would be affected, together with the route's declared source profile and affected settings. Treat these as review warnings only. This increment does not rewrite C1–C3 registrations, profile routes, source-profile declarations, or My Menu assignments.

This is a planning view only. It cannot add, remove, or rename baseline settings, and it provides no YAML diff, review token, baseline save, or profile save action. The complete draft, decisions, and plan exist only in browser memory; refreshing the page, closing the tab, or stopping the server discards them. The analysis reads the baseline and profiles loaded when the editor server started, so restart the server after external source changes.

## Edit or preview a profile

1. Open **Profiles**.
2. Choose an existing profile.
3. Review the grouped camera settings.
4. Look for the **Inherited** or **Customized** label beside each setting.
5. Edit the title, optional subtitle, status, release state, and available setting controls.
6. Use **Use baseline** for one setting, **Use baseline for section** for a group, or **Discard draft & reload profile** to restore the selected profile's saved source values.
7. Choose **Preview card** to render the temporary draft with the established card renderer.
8. Choose **Review YAML changes** only when the draft is ready to save.

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

Profile, My Menu, and baseline-impact draft values live only in the open browser page.

- **Use baseline** removes the temporary override for one setting.
- **Use baseline for section** removes all temporary overrides in that section.
- **Discard draft & reload profile** restores the selected profile's title, metadata, and saved overrides. This may bring back customized values that differ from the baseline.
- Selecting another profile discards the current draft and loads the selected profile. Returning to the first profile loads its original saved overrides again.
- Reloading the page clears My Menu edits and starts a new draft from the approved **SWITCH** and **AF Case** recommendation.
- **Discard baseline draft** restores every temporary baseline value to the currently loaded source baseline.
- Refreshing the page, closing the tab, or stopping the server discards all browser drafts.

Restarting the server is not required to discard a draft. A successful editor save reloads the in-memory profile list automatically. Restart the server when profile or catalog source files were changed by another tool while the editor was running.

## Boundaries

The editor intentionally provides no profile deletion, existing-profile rename, baseline write, persistent My Menu save, build, commit, push, merge, or publish action. Use the established project workflows for validation, Git checkpoints, and publication.

## Quick readiness check

To confirm that the editor can load all current profiles without starting the web interface, run:

```bash
python3 "80 Build/profile_editor.py" --check
```
