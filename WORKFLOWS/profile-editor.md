# Profile Editor

Profile Editor 1.0 is the project's main local interface for routine work and deliberate releases: a Start → Work → Finish daily path, shooting profiles, persisted My Menu organization and card colors, Camera Buttons assignments, reviewed Camera Lab evidence, baseline setup, session review, local builds, guarded Finish Day handoff, optional guarded branch integration, Terminal-free publication, and camera reference. It provides a Canon-sourced EOS R5 still-photo settings dictionary, runs the existing preflight as a quiet opening check, loads and saves the reviewed My Menu and Camera Buttons sources, renders isolated shooting and reference-card previews, can create, duplicate, or update shooting-profile YAML, can apply a complete reviewed baseline migration, can run the guarded normal local build after every browser draft is resolved, and keeps Git integration and live publication in separately confirmed workspaces.

Use the specialized workflow pages linked from the editor for manual spreadsheet preparation or recovery, testing-status import, physical-camera verification, publication, and detailed handoff reference. The **Today** workspace can run and display preflight but never pulls, merges, commits, pushes, or publishes; source commit and branch push exist only in **Finish Day**, while main integration exists only in **Integrate Branch**. The editor's confirmed local build automatically refreshes safely stale spreadsheet-derived artifacts.

The first header row orders **User guide**, **Open in Camera Lab**, and **Stop Profile Editor**. The second row contains the active profile-pack selector. A dedicated third row displays `Editor Major.Minor.Incremental · Main/Prototype`, right-aligned with the buttons above; expand it to see the exact Git branch and deterministic source hash. The redundant yellow checkout badge is no longer shown. The silver camera logo remains in its own adjacent column and is centered across all three rows. If two open editor windows show different context or versions, stop and use the application associated with the intended worktree before reviewing changes.

Permanent reference-card profile YAML remains read-only. Camera Buttons and My Menu instead use dedicated structured editors for their canonical sources. The editor cannot rename profiles, remove released cards, or permanently delete cards. It may move an unreleased editable card into recoverable Deleted Cards only through the dependency-checked, reviewed transaction described below. The shared baseline changes only through the guarded multi-file migration described below. **Review & Build** may promote exact physical Camera Lab evidence, import a closed verification workbook, and refresh generated local output and tracked `docs/` only after all session drafts are resolved and the applicable review or readiness checks pass. **Finish Day**, **Integrate Branch**, and **Release & Publish** retain their separate confirmations and authority.

## Start the editor

For routine use, double-click **R5 Profile Editor.app** in the machine-local `Applications` folder. The app starts Profile Editor in the background without opening Terminal and opens Google Chrome automatically. The main project uses `http://127.0.0.1:8765/`; a development worktree uses `http://127.0.0.1:8766/`, so the main reference and prototype can run together. Their application wrappers also have distinct macOS identities. Confirm the Main/Prototype version indicator and active profile-pack name before editing.

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

The editor is available only on this Mac while that diagnostic command is running. Use **Stop Profile Editor** in the page header; **Control-C** remains a fallback only for a server deliberately started from Terminal. It listens only on the local loopback address.

### Select and edit a profile pack (Step 4C)

The compact **Profile Pack:** label sits directly beside the selector. The selector shows **Embedded Canon EOS R5 sources** and every remembered compatible private pack by the user-friendly `pack_name` stored in that pack's `profile-pack.yaml`. It never displays the private filesystem path. Choose **Choose another profile pack…** to enter one exact pack-root path. The editor validates that root before remembering or opening it; it never scans sibling folders.

**Setup & Sharing** remains available with either source mode. With an external pack active, **New Profile Pack** explains why creation is paused and provides **Switch to embedded sources**. With embedded sources active, enter a friendly name and choose **Choose with Finder…**. The native macOS window provides normal folder navigation and New Folder support and returns the exact destination; the path field is not typed manually. Resolve all browser drafts, review the generated manifest, UUID, destination, source inventory, and Git boundary, then confirm separately. The editor stages and validates the complete pack, adds a root `.gitignore` excluding `.DS_Store`, initializes local Git without a commit or remote, atomically installs it, registers it, selects it, and reloads. Pack fingerprinting, review, and staging also omit Finder metadata for older packs. It never overwrites an existing destination, and embedded sources remain unchanged.

With an external pack active, Setup & Sharing is a four-step state-driven flow: create or select, save locally, connect GitHub, and push and verify. Only the current required action is expanded. A new pack's source-bound one-use commit review must include its repository-owned `AGENTS.md`; the later compact confirmation changes only the pack and does not push. The connection step instructs the owner to create an empty private GitHub repository without README, `.gitignore`, or license, recommends HTTPS on macOS, explains the SSH-key prerequisite, and prohibits credentials in the URL. Reviewing a new exact URL can replace an unreachable old origin without contacting it first.

Exact credential-free origin configuration uses another review and confirmation. Push uses a third confirmation, targets only the current pack branch's same-named `origin` branch, runs without interactive credential prompts, and stops on remote-only or divergent history. Configuration and push run as reconnectable jobs with stage, elapsed time, bounded progress details, and 20-second remote checks. A persistent completion receipt records the friendly pack, branch, commit, remote, time, verified result, and next step. Reopen and refresh reconcile it with the current live head so synchronized status replaces stale setup advice. It never creates, switches, or force-pushes a branch.

Combined handoff is read-only and becomes ready only when both repositories are clean and each local head equals the live head of its exact matching origin branch. The two repository diagnostics are optional detail below the guided flow. Checking the application remote does not fetch or mutate application Git. Application changes continue through normal Finish Day; the external-pack workflow cannot commit or push them.

Switching requires every browser draft to be saved or discarded and a separate confirmation. The editor loads and validates the complete replacement context before changing the machine-local saved selection, then reloads the page. The normal `R5 Profile Editor.app`, `Start Profile Editor.command`, and `npm run ui` launches use that saved selection. Choose embedded sources in the selector to clear the active external selection while keeping valid packs available for later switching.

An explicit one-launch override remains available from the application repository root:

```bash
python3 -B "80 Build/profile_editor.py" --profile-pack "/absolute/path/to/private-profile-pack"
```

This command does not save a selection and does not change the normal application launcher. The header identifies the application checkout and selected pack separately, and a gold banner marks the session **guarded editing**. You may preview and use exact reviewed saves for Profiles and lens choices, C1–C3 assignments and card routes, My Menu, Camera Buttons, and baseline migrations. You may also remove eligible unreleased cards to the pack's recoverable Deleted Cards area and restore them.

Every canonical write is confined to a manifest-owned pack source; application source and its legacy control mirror are never external write targets. Previews, backups, and Deleted Cards are isolated under the selected pack ID in the machine-local workspace. A save still requires an exact review, checks current source fingerprints, validates the combined application-plus-pack source set, and rolls back every written file on failure. C1–C3 assignment saves also reconcile affected verification-status fingerprints. The editor accepts its own successfully validated pack revision, but an independent source change requires a restart.

Steps 5A–5B permit **Open in Camera Lab** for the active external pack. Camera Lab can connect, scan, compare, rehearse guarded simulator application, and use its separately confirmed physical-camera write mode. Local journals, qualifications, evidence, confirmations, and checklist state are isolated by pack ID. Step 5C exposes **Evidence Review** in Profile Editor for deliberate promotion of exact completed physical-camera evidence into that pack's verification status. Camera Lab itself cannot write pack source. Step 6B permits only the reviewed private-pack Git and combined-handoff surface described above. Equipment editing, independent verification editing, spreadsheets, builds, cleanup, application Finish Day/Git, branch integration, main-editor launch, and publication remain disabled and are rejected by the server. A moved, replaced, incompatible, identity-changed, or independently changed pack is also rejected. If a saved pack becomes unavailable and the normal launcher cannot start, use `python3 -B "80 Build/profile_editor.py" --embedded`, then choose embedded or another valid pack in the header. That separately confirmed choice safely repairs invalid machine-local selection state.

## Open the current profile in Camera Lab

Select a saved Subject/Profile Card and choose **Open in Camera Lab** in the header. Profile Editor starts the independent Camera Lab if needed, or reuses an existing Lab only when it has the same pack ID, then opens it with that saved profile preselected. Camera Lab receives the exact resolved pack context and reloads the current saved profile and C1–C3 assignments itself.

Save or discard ordinary profile edits first. The button is unavailable for a new or unsaved profile draft and for permanent reference cards. Opening the Lab does not connect the camera, scan it, compare it, or change a setting; use the Lab controls when ready. Stopping Profile Editor does not stop Camera Lab, and stopping Camera Lab does not stop Profile Editor. The header keeps **User guide**, **Open in Camera Lab**, and **Stop Profile Editor** on the first row, the profile-pack selector on the second row, and the right-aligned expandable Main/Prototype version on a dedicated third row; the silver camera logo stays in its own adjacent column.

Camera Lab never updates the Setup & Verification Tracker automatically. With embedded sources, **Review & Build** can open **Camera Lab evidence**; with an external pack, the same protected surface is presented as **Evidence Review** without build controls. It lists exact unmigrated setting evidence from completed physical-camera sessions, and nothing is checked automatically. The importer can mark only the matching current C1–C3 setting as configured; it does not mark read-back, registration, operational testing, backups, Canon capability, or owner-confirmed project evidence. It excludes simulator, incomplete, legacy-without-pack-identity, and other-pack sessions, records journal provenance, blocks when the active pack's workbook has unimported edits, and requires an exact YAML review plus separate confirmation. External promotion writes only pack-owned verification status and does not generate a spreadsheet.

## Follow the workspace order

The sidebar separates routine work, profile setup, and occasional procedures. **Today** provides the short Start → Work → Finish path. **Profiles** remains embedded in Profile Editor, while **Camera Lab** opens the separate application. **Review & Build** collects every profile, Cx Foundation, My Menu, Camera Buttons, and baseline draft in one list and contains the physical-evidence review. Profile setup includes Cx Foundation, Deleted Cards, My Menu, Camera Buttons, and Baseline Setup. **Finish Day**, **Integrate Branch**, and the occasional workspaces retain their existing positions and safeguards.

Numbered badges identify pending browser drafts. Moving to another profile or workspace preserves drafts in this browser session instead of silently discarding them. Moving from Profiles to Cx Foundation carries the selected saved shooting profile into **Profile to evaluate**. Refreshing or closing the page still clears session drafts, so the browser warns before leaving while any remain.

### Use Today

**Start** runs `preflight-git.sh` automatically and classifies the result as ready, review, or blocked. The checked-out branch is the expected work branch and must track its exact same-named branch on `origin`, so both `main` and a deliberate prototype worktree can pass. The compact ready state avoids unnecessary Git and multi-Mac detail for ordinary single-Mac use; exact output remains available when review is useful. A blocker shows its safest in-editor next action. A clean branch that is only behind may request a separately confirmed fast-forward-only update; local changes, divergence, conflicts, unexpected tracking, and branch decisions remain non-automatic. Stale spreadsheet or verification state routes to Review & Build instead of relying on a terminal command.

**Work** opens the existing Profiles and Review & Build views or launches the independent Camera Lab. It does not duplicate those workspaces or their safeguards.

**Finish** shows the current browser-draft count and opens the guarded in-app Finish Day workspace. The optional other-Mac checkbox reveals the additional handoff requirement only when another computer will take over. The same clean, synchronized Finish Day endpoint applies to single- and multi-Mac use. On a prototype branch, Finish Day may push only to its matching prototype upstream and does not update the live site.

### Use Finish Day

The in-app workspace and `finish-day.sh` share `80 Build/finish_day.py`; neither is a second implementation of the workflow. **Check** verifies zero browser drafts, safely classifies verification and release-workbook state, checks the current branch and exact same-named `origin` upstream, and refreshes ahead/behind state. A safely stale workbook family adds a separate preparation checkbox naming the refresh and warning that Apple Numbers will run temporarily in the background; possible unimported tracker edits instead route to the confirmed Review & Build importer. **Prepare** requires confirmation before starting a reconnectable background job that conditionally refreshes the stale artifacts, then shows the current command, elapsed time, completed steps, and expandable output while running source validation, the normal build, full validation, and backed-up removal of generated `docs/` changes from the handoff. If Numbers is already open, save and close it and choose **Resume after closing Numbers**; the workflow repeats its safety checks and continues through the same preparation. Refreshing the page reconnects to a running preparation. **Commit** requires the exact source list, a content-sensitive one-use review, a message, and separate confirmation. **Push** requires another confirmation, refuses outgoing `docs/` changes, pushes only the reviewed current branch to its matching upstream, and verifies the final clean synchronized state.

### Integrate a finished branch

Use **Integrate Branch** only after Finish Day reports that the current non-main branch is clean and synchronized. **Check** refreshes `origin`, requires the branch's exact same-named upstream, and targets only `origin/main`. **Review** starts a reconnectable background job with the same visible command progress as Finish Day, creates the proposed merge in a disposable worktree, stops cleanly on conflicts, and rejects `docs/` changes. It diagnoses spreadsheet state against that exact merged candidate. If stale artifacts are safe to regenerate, the stopped panel offers a separately confirmed retry that rebuilds only those artifacts inside a fresh disposable candidate and warns that Apple Numbers will run temporarily in the background; rebuilding in the original checkout would not repair the candidate. If Numbers is already open, the same retry control remains available after it is saved and closed. It then runs source validation, the normal build, and full validation, restores generated website files, and shows the exact commits and files.

The remaining changes have independent authority. **Merge Main** applies the exact reviewed tree to a clean local `main` worktree but does not push. **Push Main** synchronizes `origin/main` but does not call the website publisher or create a release. **Resync** fast-forwards the current working branch to the integrated main commit and pushes only its exact same-named upstream. It then compares the persistent Main project's installed Profile Editor and Camera Lab wrappers with deterministic integrated candidates and rebuilds only missing or stale wrappers. The completion receipt distinguishes current, rebuilt, unavailable, and failed app-refresh states. Ordinary merged source changes do not require rebuilding these thin launcher bundles, but runtime changes require restarting any running apps; the editor reports that requirement without stopping drafts or a camera session. The workflow never rebases or rewrites shared history. If `main` is not already checked out, the editor uses a temporary worktree, does not create an app that points to that disposable path, and never switches the active Profile Editor checkout.

For a fork, `origin` must be the fork owner's repository. Integrate Branch therefore updates that fork's `origin/main`, not another owner's repository. Receiving later improvements from a separate upstream repository remains a distinct workflow and is not inferred here.

### Review optional cleanup

After Finish Day or branch integration completes, **Cleanup Review** may list exact recognized disposable items. It always protects the newest successful recovery backup of each workflow type and each profile operation/target, lists only older superseded recognized backups, applies no age threshold, ignores manually named or unrecognized backups, and may also list exact `.DS_Store` metadata inside the repository. Each item shows its full path, date, size, and reason. Nothing is selected automatically.

Permanent deletion requires checking each exact item and then checking a separate irreversible-deletion confirmation. The editor recomputes the inventory before deletion and stops if anything changed. Canonical source, current deliverables, private profile data, protected newest backups, and temporary integration worktrees are never candidates.

Refresh or prepare again whenever source changes after review. Workflow blockers provide a direct editor destination, confirmed safe action, or explicit manual-review explanation; terminal commands remain optional expert details. Integrate Branch never pulls, switches branches, changes website version metadata, or publishes.

**Release & Publish** is separate because publication is not an everyday action. Approved prototype work must be integrated into `main`; the prototype workspace can then open the Main project editor without a Terminal step. In Main, the workspace checks clean synchronization, prepares an exact minor or major release, reviews and backs up missing reader-facing highlights, and sends that source change through Finish Day. When the notes are synchronized, **Automatic (recommended)** preserves current spreadsheet bytes or rebuilds only diagnosed stale families. A separate force choice regenerates and republishes both families even when current; deliberate removal remains available. The final review binds that action, both visible spreadsheet build IDs, and the current main commit. A separate live-site confirmation starts reconnectable progress through the existing publisher, and completion requires both the publication receipt and a clean synchronized Git report.

**Setup & Sharing** keeps fork and computer guidance out of the daily path. Step 4C allows the ordinary editor launcher to use a private machine-local saved pack, Steps 5A–5B pass that exact pack to Camera Lab for comparison and guarded camera operation, Step 5C permits reviewed evidence promotion, Step 6A provides guarded New Profile Pack creation from embedded sources, and Step 6B provides separately reviewed pack Git and read-only combined handoff status. The embedded source remains authoritative. Direct Camera Lab pack-source writes, source-migration activation, and external-pack publication remain future work.

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

The released **My Menu** and **Camera Buttons** cards remain generated and read-only in the Profiles view. Choose either and select **Render reference preview**. Edit My Menu through its dedicated layout workspace.

In **Camera Buttons**, each control uses the same Canon physical-control icon that precedes its name on the generated card. Every fixed control shows its documented Canon default and a short explanation. **Assignment** identifies the camera function; **Operation** describes what happens when the control is used; separately named **INFO** dropdowns represent the advanced choices shown after pressing INFO for compatible assignments; **Notes** is project explanation in free text; and **Evidence** says whether the row is physically confirmed, pending verification, a Canon capability, a recommendation, or unresolved. Use **Other / exact camera label** when the needed camera wording is not yet in the curated list rather than choosing an approximate value. **Card detail** shows the exact combined paragraph that will appear beneath the assignment and updates immediately as its contributing fields change.

Unchanged/default Movie Record, MODE, and LCD panel illumination stay off the concise card. If the assignment, operation, or INFO behavior of one of those buttons is customized, the editor includes it automatically; no separate inclusion choice is needed.

Choose **Preview Camera Buttons card** in the sticky preview header to render the complete unsaved draft through the same renderer used by the released card. After a draft edit, the same fixed action becomes **Refresh Camera Buttons preview**. The preview writes no canonical source and is marked stale after another edit. **Review Camera Buttons changes** still preserves every physical row and the C1–C3 mappings, validates the synchronized candidates, and presents the exact two-file YAML diff. Changing confirmed assignment, operation, or INFO behavior automatically returns that row to pending camera verification; changing Notes alone does not erase evidence.

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
8. For a Subject card, edit **Lens Choices** above the camera settings. Add or remove owned lens/accessory combinations, use the arrow buttons to set card order, and select exactly one **Primary** role; remaining entries may be **Alternative** or **Specialist**. Each choice requires concise **When to use** and **Field check** text. The editor limits accessories to compatible lenses, permits at most three choices, and automatically recomputes Compatibility in the next preview. A Camera Setup & Controls card has no lens choices.
9. Use **Use baseline** for one setting or **Use baseline for section** for an additional-settings group. Open **Profile actions** and choose **Restore saved profile** to abandon unsaved browser edits—including lens choices—and reload the selected profile's saved source values. Selecting an enabled Profile action closes the menu.
10. Choose **Render preview** in the right-hand panel. On a desktop-width window, the settings and preview scroll independently so the card remains visible while settings are reviewed. On a narrower window, use the **Settings** and **Preview** pane controls.
11. After an edit, treat the retained preview as out of date until **Refresh preview** completes.
12. Choose **Review changes** in the persistent action bar only when the draft is ready to save. The review lists each effective setting change as its saved value and latest draft value before one exact YAML diff. A lens-only edit changes only `00 Master/profile_lens_guidance.yaml`; a combined edit may include that file and the selected profile. The guarded transaction fingerprints, backs up, validates, writes, and rolls back both sources together. It also synchronizes the candidate's visible My Menu cues with the persisted global layout when profile fields changed, so you do not need to visit My Menu unless that global configuration itself is changing. When a customization is removed, the resulting inherited baseline value is named explicitly, such as **Aperture: Blank → Auto (inherited from baseline)**. For every setting, recognized text choices are case-insensitive and return to their canonical spelling before comparison, so `AUto` is treated as `Auto`; unrecognized custom values such as `f/8` remain unchanged.

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
- Reference-card profile YAML cannot be duplicated or edited. My Menu and Camera Buttons change only through their dedicated structured workspaces.

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

Unsaved profile, My Menu, Camera Buttons, and baseline draft values live only in the open browser page. A reviewed My Menu save persists its tab layout in `00 Master/my_menu.yaml` and matching colors in `00 Master/my_menu_colors.yaml`. A reviewed Camera Buttons save updates `controls.yaml` and its synchronized current-evidence record together.

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

Open **Review & Build** to validate an embedded editing session before generation. With an external pack, open **Evidence Review**; draft-summary, spreadsheet, and build controls are hidden. Save each intended draft through its guarded review or choose **Discard** and confirm before evidence promotion. For Camera Lab evidence, refresh the list, check only the exact items to retain, review the canonical status diff, acknowledge the narrow evidence boundary, and import. Embedded mode rebuilds the safely synchronized working tracker; external mode updates only pack-owned verification status and creates no spreadsheet. When an embedded manually edited verification workbook contains results to retain, save and close Numbers or Excel, choose **Import verification tracker**, and confirm. Neither path imports automatically. Then run a fresh readiness check before an embedded local build.

The guarded build runs source-only validation, conditionally refreshes only safely stale spreadsheet-derived artifacts, then runs the normal development build and full validation. While it runs, Review & Build shows the numbered current stage, elapsed time, exact safe command, and an expandable **Watch command log**; **Show status details** retains readiness and final step output. The job is reconnectable after refreshing the page. It stops on the first failure and shows its output. If the verification working copy may contain unimported edits, readiness blocks before the build; import those edits through the testing workflow first. The build does not run Git, publish, or change website version metadata.

## Boundaries

The editor intentionally provides no released-profile removal, permanent card or source deletion, existing-profile rename, direct baseline edit, raw reference-card YAML editing, or arbitrary control creation. Unreleased editable profiles use the guarded Deleted Cards transaction. Baseline writes require a complete reviewed migration. My Menu and Camera Buttons use only their dedicated exact-diff transactions. Review & Build offers reviewed Camera Lab evidence promotion, the existing closed-workbook importer, and the guarded local build sequence. Finish Day, Integrate Branch, Release & Publish, and Cleanup Review retain their separate authority and confirmations.

## Quick readiness check

To confirm that the editor can load all current profiles without starting the web interface, run:

```bash
python3 "80 Build/profile_editor.py" --check
```
