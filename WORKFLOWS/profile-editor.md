# Profile Editor Prototype

This Stage 1 prototype is a safe way to work through camera setup, My Menu organization, and existing camera profiles. It provides a Canon-sourced EOS R5 still-photo settings dictionary, keeps a temporary My Menu draft, lets you make temporary profile choices, and renders an isolated card preview with the existing card renderer.

It cannot create, update, or delete profile YAML. It does not run the normal website build, change `docs/`, publish, commit, push, or merge anything.

## Start the prototype

Use the Project Terminal panel on the [Workflow Index](index.html) to open the prototype worktree in Terminal. Then run:

```bash
python3 "80 Build/profile_editor.py"
```

Open the local address shown in Terminal, normally:

```text
http://127.0.0.1:8765
```

The editor is available only on this Mac while that command is running. Press **Control-C** in Terminal to stop it.

## Work through camera setup

The prototype opens on **Camera setup**. Search the Shooting, AF, Playback, Wireless, Set-up, and Custom Functions dictionary or filter it by **Set Once**, **Situational**, **Ignore**, **Avoid**, or **Unresolved**. Every record identifies its direct camera-menu location, reset-default reference, project recommendation, whether it should be revisited, and the applicable Canon manual source.

The dictionary separates Canon reference facts from project recommendations. Menu names and locations are grounded in Canon's menu overviews. A reset default remains a working reference unless the linked Canon page states it explicitly. Neither the recommendation nor the temporary UI state proves the current physical camera setting.

**Touch & Drag AF** is represented by its three separate controls:

- Touch & Drag AF: Enable
- Positioning method: Relative
- Active touch area: Right

All three are project **Set Once** recommendations. The active touch area should be revisited if handedness, grip, or unintended face contact makes another area more reliable.

## Configure My Menu

Open **Configure My Menu** after reviewing setup. The temporary configurator follows the EOS R5 limit of five tabs with six items per tab. Choose **Load recommended tabs** to start with the approved **SWITCH** and **AF Case** layouts, or build a different session-only arrangement.

The dictionary shows a **Configured shortcut** only after an item is selected in this configurator. This keeps the direct Canon menu location authoritative and prevents the UI from claiming a My Menu path that was never configured in the draft.

The My Menu draft is explicitly unverified and exists only in the current browser session. It does not save to project YAML and does not prove the physical camera matches the draft.

## Try a profile

1. Open **Profiles**.
2. Choose an existing profile.
3. Review the grouped camera settings.
4. Look for the **Inherited** or **Customized** label beside each setting.
5. Try the available dropdowns and text fields.
6. Use **Use baseline** for one setting, **Use baseline for section** for a group, or **Discard draft & reload profile** to restore the selected profile's saved source values.
7. Choose **Preview card** to render the temporary draft with the established card renderer.

Exposure, Autofocus, and Drive controls use the prototype's Canon EOS R5 options catalog. Each cataloged setting links to the applicable Canon manual page and uses the same approved setting/value icon system as the subject cards. The catalog is scoped to still photos on EOS R5 firmware 2.2.0 or later.

Canon choices, conditional Canon choices, and project compatibility values are labeled separately. For example, Canon defines One-Shot AF and Servo AF as AF Operation choices; this project retains Manual Focus in that field only for compatibility with existing profile data.

Some fields allow both Canon choices and custom profile targets. ISO and exposure compensation profiles may contain a descriptive range or field instruction rather than one camera value, so those controls provide Canon suggestions without discarding the existing free-form behavior.

## Where the preview goes

The one disposable preview file is written under the prototype worktree's separate machine-local workspace:

```text
Canon Camera Reference UI Prototype Local/Build Output/cards/html/_Profile Editor Preview.html
```

Each preview replaces the prior disposable preview. No file under `10 Profiles/` or `docs/` is changed.

## Discard draft changes

Profile and My Menu draft values live only in the open browser page.

- **Use baseline** removes the temporary override for one setting.
- **Use baseline for section** removes all temporary overrides in that section.
- **Discard draft & reload profile** restores the selected profile's original saved overrides. This may bring back customized values that differ from the baseline.
- Selecting another profile discards the current draft and loads the selected profile. Returning to the first profile loads its original saved overrides again.
- Reloading the page clears the My Menu draft. Use **Load recommended tabs** to restore the project recommendation.
- Refreshing the page, closing the tab, or stopping the server discards all browser drafts.

Restarting the server is not required to discard a draft. It is required only when profile or catalog source files were changed externally while the server was already running, because source data is loaded when the server starts.

Stage 1 intentionally has no **Save** button. Safe profile creation and updating, backups, change review, validation, and automatic recovery belong to a separately reviewed later stage.

## Quick readiness check

To confirm that the prototype can load all current profiles without starting the web interface, run:

```bash
python3 "80 Build/profile_editor.py" --check
```
