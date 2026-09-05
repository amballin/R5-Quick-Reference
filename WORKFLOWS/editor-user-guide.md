# Profile Editor User Guide

Profile Editor 1.0 is the main local interface for routine work and deliberate releases: starting with a quiet preflight, creating and updating shooting profiles, previewing cards, organizing My Menu, planning shared baseline changes, reviewing session drafts, validating and building, completing the guarded Finish Day handoff, optionally integrating a finished branch into `main`, publishing from the Main project, and looking up camera settings. Its confirmed local build refreshes safely stale spreadsheet-derived artifacts automatically.

## Start the editor

For routine use, double-click **R5 Profile Editor.app** in the machine-local `Applications` folder. It starts in the background without opening Terminal and opens Google Chrome automatically. The main project uses port 8765 and a development prototype uses port 8766, so both can run at the same time. Their Main/Prototype version indicators and macOS application identities remain distinct.

If an editor is running without a visible Chrome window, open that checkout's **R5 Profile Editor.app** again to recover the window. Use **Stop Profile Editor** in the header when finished; it warns before discarding unsaved browser drafts and stops only the editor server. If the window cannot be recovered, double-click **Stop Profile Editor.command** in that repository. It clears stale process records, recognizes one verified pre-upgrade prototype left on port 8765, and stops only a server verified as belonging to that exact checkout.

The self-contained app is the normal launch method; no npm command is required for routine use. For Profile Editor development or diagnostics only, from the project root run:

```bash
npm run ui
```

Open the local address shown in Terminal. Keep that Terminal window open while using this diagnostic method. Use **Stop Profile Editor** in the page header; **Control-C** is only the fallback for this diagnostic launch method.

The editor runs only on this Mac. Routine source commit and branch push are available only inside **Finish Day**. Merge to main, main push, and branch resynchronization are available only inside **Integrate Branch**. Live publication is available only inside **Release & Publish** in the Main project editor, after a separate exact review and confirmation.

Before editing, confirm the expandable editor-version indicator. **Main** means the app is running from the authoritative `main` worktree; **Prototype** means it is running from a development worktree. Expand it for the exact branch and source hash. If the context does not match the work you intend to do, stop that app and open the correct project-specific app instead.

### Select and edit a private profile pack

Use the selector beside the compact **Profile Pack:** label to move among embedded sources and remembered private packs. Available external choices display the friendly name from that pack's `profile-pack.yaml`, never its folder name or filesystem path. Choose **Choose another profile pack…** and enter an exact root path to add a pack. The editor does not search the Mac for packs.

Save or discard every browser draft first. Switching requires confirmation, validates and loads the complete new pack before saving the selection, and then reloads the editor. Future launches through **R5 Profile Editor.app** use that selection. Selecting embedded sources clears the active external choice but keeps valid remembered packs in the list.

### Create a new private profile pack

Open **Profile Packs** and use **New Profile Pack**. If an external pack is active, use **Switch to embedded sources** first. The baseline, editable C1 Wildlife/C2 Birds in Flight/C3 Landscape starters, and the Camera Buttons, Camera Defaults, Camera Setup Essentials, and My Menu reference cards are always included. Check only the additional optional subject cards wanted in this pack. Enter a friendly name, choose **Choose with Finder…**, and use the macOS window—including its New Folder control when useful—to select an exact new sibling destination. Never place one profile pack inside another. Save or discard every browser draft, then choose **Review new profile pack**. Review the generated UUID manifest, exact destination, required and selected cards, exact source inventory, and local-Git boundary before checking the compact confirmation and choosing **Create and select profile pack**. New-pack camera verification and control evidence begins pending rather than inheriting another owner's physical-session results.

To add an official profile later, select the private pack, open **Profile Packs**, and use **Add Profiles from Catalog**. Select one or more profiles, review the exact new YAML files and any matching lens-guidance additions, check the compact confirmation, and add them. The editor refuses an existing filename or card identity, never overwrites an existing profile, creates a recovery backup, validates the combined source, and rolls back on failure. The addition remains a local pack change until it is saved and shared through the steps below.

The editor stages the new pack from the reviewed starter selection, trims pack-owned lens guidance to those active subject cards, resets camera verification history, and marks control evidence pending verification. It adds the private-pack working instructions and a `.gitignore` that excludes Finder's `.DS_Store`, initializes local Git, validates the combined application and pack sources, then atomically installs, registers, selects, and reloads the pack. Finder metadata is also excluded defensively from pack review and commits. It refuses an existing destination and removes an incomplete new destination after failure. Creation makes no commit, remote, push, build, spreadsheet, handoff, or publication. When an external pack is active, switch to embedded sources before creating another pack.

### Save and hand off a private profile pack

With the external pack selected, open **Profile Packs**. On the **Profile Packs & Sharing** page, follow its four numbered steps: **Create or select**, **Save locally**, **Connect GitHub**, and **Push & verify**. Only the action needed next is open. For a new pack, review the exact pack files, confirm that `AGENTS.md` is included, enter the message, check the compact confirmation, and commit. Nothing is pushed and application Git is untouched.

Before **Connect GitHub**, create an empty repository on GitHub: choose **New repository**, set it to **Private**, and do not add a README, `.gitignore`, or license. Copy its HTTPS URL; HTTPS is recommended on this Mac because credentials remain in the system credential manager. SSH is supported only when an SSH key is already configured. Never put a password or token in the URL. Review the exact URL and confirm the connection separately. If an old origin is unreachable, review the replacement URL here; the editor does not require the old origin to respond first.

Push remains a third separate approval. Verify the displayed current branch and exact same-named `origin` target, check the confirmation, and choose **Push private pack**. Connection and push show their stage and elapsed time, can reconnect after page navigation or reload, and stop a nonresponsive remote check after 20 seconds. When either finishes, a receipt remains with the pack, branch, commit, remote, time, verified result, and next step. Reopening the page reconciles that receipt with live status, so a synchronized pack shows its verified commit instead of stale instructions from an earlier commit step. On a timeout, refresh status before retrying. The workflow never creates, switches, or force-pushes a branch.

**Setup complete** appears only after both the application and private pack are clean and their current commits match the live heads of their respective matching `origin` branches. Open **How the application and private pack stay separate** for the two repository status details. A result for one repository never substitutes for the other. Resolve application Git work through its normal Finish Day workflow; external-pack Profile Packs & Sharing never commits or pushes the application.

For a one-launch override that does not change the saved choice, run from the application repository root:

```bash
python3 -B "80 Build/profile_editor.py" --profile-pack "/absolute/path/to/private-profile-pack"
```

The header shows the application checkout and selected pack independently, without displaying the private filesystem path. A gold **External profile pack · guarded editing** banner identifies the boundary. Profiles and lens choices, Cx Foundation, My Menu, Camera Buttons, Baseline Setup, Deleted Cards, and Camera Reference are available; previews, reviews, and saves use only manifest-owned pack sources and pack-ID-namespaced machine-local state. Each save retains the normal one-use review, fingerprint, backup, validation, atomic-write, and rollback safeguards.

Steps 5A–5B allow **Open in Camera Lab** for connection, scan, comparison, equipment context, C1–C3 labels, setup routes, guarded simulation, and explicitly enabled physical-camera operation from the selected external pack. Camera Lab displays the manifest name, refuses to reuse a Lab running another pack, and keeps local journals, qualifications, evidence, confirmations, and checklist state isolated by pack ID. Step 5C adds **Evidence Review** for deliberately promoting exact completed physical-camera evidence into the selected pack's verification status. Camera Lab cannot write pack source itself. Step 6B permits only the reviewed private-pack Git and combined-handoff workflow described above. Equipment editing, independent verification editing, spreadsheets, builds, cleanup, application Finish Day/Git, integration, main-editor launch, and publication remain disabled and server-rejected for an external pack. Restart after changing pack source outside the editor.

If a saved pack is missing, moved, or invalid and the ordinary launcher stops, use this recovery launch and then select embedded sources or another valid pack. The separately confirmed choice repairs invalid machine-local selection state:

```bash
python3 -B "80 Build/profile_editor.py" --embedded
```

## Understand the working model

On desktop, the left navigation has its own scrollbar sized to the space actually visible below the header. You can reach every navigation item without scrolling the content workspace on the right. At narrow responsive widths, navigation returns to ordinary page flow.

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

**Daily work**

- **Today** — Follow the short Start → Work → Finish path. It runs the existing preflight, points to the embedded workspaces, and opens the guarded Finish Day workspace.
- **Profiles** — Preview, create, duplicate, or update shooting profiles inside Profile Editor.
- **Camera Lab** — Launch the independent Camera Lab application with the selected saved profile. This is an application action, not an embedded workspace.
- **Review & Build** — Resolve all browser drafts, review exact Camera Lab evidence, validate source, and run the guarded local build.
- **Finish Day** — Check repository state, validate and prepare source, review and commit the exact source list, then separately approve a push to the matching upstream. It never publishes.

**Profile setup**

- **Cx Foundation** — Assign C1–C3 profiles, compare foundation fit, and make the final card-route selection.
- **My Menu** — Arrange saved tabs, shortcuts, and card colors.
- **Camera Buttons** — Review Canon defaults, choose assignments and advanced options from explained dropdowns, see the exact live card-detail text, let customized optional buttons appear automatically, refresh the preview from its fixed header, and save through a synchronized review.
- **Baseline Setup** — Test a proposed shared change and review its effect across profiles.
- **Deleted Cards** — Review and restore unreleased cards removed from active source.

**Occasional**

- **Integrate Branch** — Validate a finished branch against current `main`, review the exact result, then separately approve the local-main merge, main push, and branch resynchronization. It never publishes.
- **Release & Publish** — Prepare reader-facing highlights, select a minor or major version, choose how spreadsheet downloads are handled, review the exact live release, publish through the established main-only publisher, and require a verified clean result. A prototype workspace can open the Main project editor after integration.
- **Cleanup Review** — Optionally review exact superseded workflow backups and disposable metadata. Nothing is selected automatically.
- **Profile Packs** — Create, select, extend, save, and share an independently owned profile pack.
- **Camera Reference** — Find and review setup records and their source links.

On narrower windows, the sidebar becomes a compact navigation row above the workspace.

Moving to another tab does not save work, but the sidebar badges and Review & Build list preserve and identify pending profile, Cx Foundation, My Menu, Camera Buttons, and baseline work for this browser session. When you move from Profiles to Cx Foundation, the selected saved shooting profile is carried into **Profile to evaluate** automatically.

## Follow the daily path

Open **Today** when beginning or ending routine work:

1. **Start** runs the existing preflight automatically. It accepts either `main` or the checked-out prototype branch when that branch tracks its exact same-named upstream. A clean result stays compact; notices and blockers expose the exact output. Preflight refreshes the remote comparison but never pulls, merges, builds, commits, or publishes.
2. **Work** opens the embedded Profiles or Review & Build workspace, or launches Camera Lab as a separate application. The draft count follows the existing browser-session ledger.
3. **Finish** identifies unresolved browser drafts and opens the in-app Finish Day workspace. Select the additional other-Mac reminder only when another computer will take over.

The ordinary stopping point is the same on one Mac or two: Finish Day must leave the current branch clean and synchronized with its matching upstream. On a prototype branch, that means the prototype Git branch only; it does not publish GitHub Pages. Live publication is optional, remains in the separate **Release & Publish** workspace, and requires approved work to be integrated into `main` first.

## Finish the day in the editor

Open **Finish Day** only after every browser draft has been saved or discarded. The workspace uses four guarded stages:

1. **Check** refreshes remote-tracking state and verifies the current branch, exact matching upstream, browser drafts, verification status, and ahead/behind state. It never pulls or merges.
2. **Prepare** requires confirmation, then immediately opens an in-page progress panel showing the current command, elapsed time, completed steps, and an expandable command log while source validation, the normal development build, and full validation run. Refreshing the page reconnects to the same running preparation. If the build changes `docs/`, it creates a machine-local recovery archive and restores those generated files before source review.
3. **Commit** displays the exact eligible source list. Enter a concise message, check the exact-review confirmation, and commit. A content-sensitive one-use review expires if any tracked diff or untracked file changes after preparation. Nothing is pushed at this stage.
4. **Push** requires a new confirmation. It pushes only the current branch to its exact same-named upstream on `origin`, refuses any outgoing `docs/` change, and verifies the final clean synchronized state.

The existing `finish-day.sh` command remains available and uses the same underlying engine and safeguards. Neither interface switches branches, merges, or publishes the website.

## Integrate a finished branch

After Finish Day reports a clean synchronized non-main branch, open **Integrate Branch**. This is optional; finishing the day does not require integration.

1. **Check** refreshes `origin`, confirms the current branch tracks its exact same-named upstream, and requires no local or browser changes.
2. **Review** starts the same reconnectable in-page command progress, creates a disposable worktree from current `origin/main`, attempts the merge there, rejects conflicts and `docs/` changes, runs source validation, the development build, and full validation, restores generated website files, and displays every proposed commit and file. If the protected application profile catalog, its policy, or its lens guidance changes, review the separate exact protected YAML diff and explicitly approve it as the application owner.
3. **Merge Main** requires confirmation and applies the exact validated tree to a clean local `main`. A protected catalog candidate remains blocked until its separate owner approval is bound to that exact candidate and the same reviewed heads. Nothing is pushed.
4. **Push Main** requires a separate confirmation and updates `origin/main`. It does not call the publisher, change website version metadata, or create a release.
5. **Resync** requires another confirmation, fast-forwards the working branch to the integrated main commit, and pushes only its exact same-named `origin` branch. It then checks the persistent Main project's installed Profile Editor and Camera Lab wrappers and rebuilds only a missing or stale wrapper. It never rebases or rewrites shared history.

If a conflict, dirty main worktree, changed remote ref, or different candidate tree appears, the editor stops and reports it. When `main` is not already checked out, the workflow uses a temporary worktree rather than switching the active editor branch. For a fork, `origin/main` is the fork owner's main branch; updates from a separate upstream project remain a different workflow.

The completion panel reports whether the Main apps were already current, rebuilt automatically, unavailable because Main was temporary, or could not be refreshed. The apps are thin launchers, so most source merges need a restart rather than a wrapper rebuild. When runtime inputs changed, stop and reopen any running Profile Editor or Camera Lab after saving drafts and ending the camera session; integration never stops either app automatically.

## Publish without Terminal

Open **Release & Publish** only when you intend to update the live website.

1. From a prototype editor, complete Finish Day and Integrate Branch, then choose **Open Main project editor**. Publication never runs from the prototype branch.
2. In Main, refresh readiness. The workspace requires no browser drafts, clean synchronized `main`, and exact `origin/main` tracking.
3. If the upcoming version has no curated notes, choose the next minor release or a new major series, enter one reader-facing highlight per line, review the exact YAML addition, and save it. The editor creates a recovery backup and runs source validation.
4. Open **Finish Day** to review, commit, and push that release-note source change. Return to **Release & Publish** after Main is clean and synchronized.
5. Choose how spreadsheet downloads are handled. **Automatic (recommended)** preserves exact verified files when current and rebuilds only stale families. **Force rebuild and republish both** regenerates both families even when current. Deliberate removal remains separate. Review the Matrix and Setup build IDs shown in the status and exact publication review.
6. Review the exact version, highlights, spreadsheet action, and current main commit. Check the separate live-site confirmation only when those details are correct.
7. Choose **Publish live website**. The page shows the current stage, elapsed time, safe command label, and expandable log; refreshing reconnects to the same publication.
8. Treat the release as complete only when the editor states that the selected version is published and verified and that Main is clean and synchronized.

The editor calls the existing supported publisher and does not create another deployment path. A failed run says **Publication stopped — not completed or verified**, preserves the actual error in its diagnostic log, stops the running indicator, and never displays the successful receipt or a next-command placeholder.

## Review optional cleanup

After Finish Day or Integrate Branch completes, choose **Review optional cleanup**, or open **Cleanup Review** directly. The editor lists only exact `.DS_Store` metadata and recognized timestamped workflow backups that have been superseded by a newer successful backup of the same type and profile operation/target. The newest successful recovery backup is always protected. There is no age requirement, and manually named or unrecognized backups are ignored.

Nothing is checked automatically. Review each full path, date, size, and reason. To delete, check the exact items, then separately confirm permanent deletion. The editor checks the candidates again immediately before deletion and stops if one changed. Source files, private profile data, current deliverables, protected backups, and automatic integration worktrees are never offered.

**Profile Packs & Sharing** documents the private profile-pack architecture for an independent fork owner. Step 4C supports saved guarded editor selection, Steps 5A–5B let the selected external pack open in Camera Lab for comparison and guarded camera operation, Step 5C adds reviewed evidence promotion, Step 6A creates a validated starter pack from embedded sources, Step 7A defines its minimum and optional starter content, Step 7B adds missing official application-catalog profiles later without overwrite, Step 7C presents and verifies that action as **Add Profiles from Catalog**, and Step 6B provides independent pack Git plus combined handoff checks. Embedded source remains authoritative. Direct Camera Lab pack-source writes, source-migration activation, external-pack publication, and other activation work remain future work.

When a saved Subject/Profile Card is selected with no unsaved ordinary profile edits, choose **Open in Camera Lab** in the header to start or reuse the independent Lab with that profile preselected. The editor passes the exact active pack context and saved profile name; Camera Lab reloads the current profile and C1–C3 assignments from that pack. It does not connect, scan, compare, or change a setting automatically. After connecting and completing the first comparison, selecting another profile automatically refreshes its comparison and card-specific lens menu. The ordinary Canon EDSDK Lab starts read-only with embedded or external sources; choose **Enable camera changes** and confirm the safe restart before **Apply this profile to camera** becomes available. Apply defaults Lens to the attached lens (or the card's Primary), Flash to **None**, and Cards to **CFexpress & SD**, with controlled menus for the other supported contexts. If Camera Setup Essentials is already set, its optional readiness confirmation clears only matching Set & Forget targets that Camera Lab cannot verify directly. Camera Lab checks readiness and shows every proposed change, but removes already-correct and non-action rows from the work queue. Simulator-safe changes run and verify after the one final confirmation; remaining manual work is grouped by camera route with one rescan per group. The stationary **Do this now** card contains every exact target, and the complete list stays out of the active workspace. Completed manual groups immediately update Rapid setup and may follow an identical setting and target to another card only during the same unchanged connected-camera session. Camera Lab gives an explicit successful-or-not-fully-applied receipt. External-pack journals remain machine-local and Step 5C allows exact eligible evidence to be promoted through Profile Editor's guarded **Evidence Review**. Each app's Stop button closes only that app.

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
3. For a Subject card, review **Lens Choices**. Every Subject card requires one to three authored lens or lens-and-accessory choices and exactly one **Primary** choice. Use **Alternative** or **Specialist** for the others, explain when to use each, add its field check, and use the arrow controls to set display order. Only compatible accessories are offered for the selected lens.
4. Work through **Shown on this card** in the exact order used by the generated card. A single card row can be backed by more than one camera control, such as ISO mode and Auto ISO maximum.
5. Expand **Additional profile settings** only when you need a control that is not currently rendered on the card.
6. Use the state beside each field to see whether the value is inherited or customized.
7. Change only the fields needed for this profile.
8. Use **Use baseline** for a field or section when the profile should inherit the shared value again. Clearing any editable field has the same result and immediately redisplays the baseline value. C1/C2/C3 foundations remain starting and comparison references rather than inheritance sources.
9. Use **Render preview** in the right-hand preview panel. The panel remains visible while the settings column scrolls independently.
10. Choose **Review changes** from the persistent action bar when the draft is ready.
11. Save only after the effective before-and-after settings and both exact YAML reviews match the intended result. A lens edit is stored with the shared lens-guidance source in the same guarded transaction as the profile. When a customization is removed, the review names the resulting inherited baseline value explicitly instead of showing only the YAML deletion. Recognized text choices use their standard capitalization across every setting, so a case-only variation such as `AUto` is treated as `Auto`, while a genuine custom value such as `f/8` is preserved.

The saved Lens Choices are operational data, not just card copy. Camera Lab selects a matching attached lens automatically, otherwise starts from the card's Primary choice, and offers only the authored choices for that card. Selecting another choice creates a planning context; a physical apply is blocked until the attached equipment agrees. Supported lens IS modes and equipment-interaction notes are derived from the saved lens and accessory definitions.

After a setting changes, the existing preview remains available but is labeled as out of date. Choose **Refresh preview** before relying on it. On narrower windows, use the **Settings** and **Preview** controls to switch between the two panes.

Open **Profile actions** and choose **Restore saved profile** to abandon unsaved browser edits and return the selected profile to its saved source state. Choosing an enabled Profile action closes the menu.

For a saved card that is still unreleased, **Profile actions → Move to Deleted Cards** provides a recoverable removal workflow. When disabled, the menu explains exactly what must be saved, restored, or unreferenced first. The editor checks UUID-based C1–C3 assignments, other card foundations, appendix associations, and every other registered structured reference. Any dependency blocks removal. Narrative document mentions appear separately as warnings for review. Confirming preserves the exact source and an integrity manifest in machine-local Deleted Cards, removes the active source, and validates the project; any failure restores active source automatically.

Open **Deleted Cards** to see the complete removal sequence and review inactive held cards. A saved card must first be unchecked for release, reviewed, and saved; then use **Profile actions → Move to Deleted Cards**. Never-saved browser drafts are discarded through Review & Build instead and never enter this holding area. Structured references block removal until resolved, and permanent reference cards are never eligible. **Review restore** shows the exact YAML addition. Restore is blocked if the original filename or immutable card identity is already active, and a successful reviewed restore returns the exact held bytes to active source and removes the holding entry. The normal editor provides no permanent purge action.

On cards with a declared C1–C3 foundation, `Δ` identifies a value that differs from that saved foundation—not from the baseline. Choosing **Use baseline** clears `Δ` only when the baseline value also matches the saved foundation. On editable profile cards without a Cx foundation, every visible settings row uses `Δ` as a reminder to verify or set the target on the camera. My Menu colors identify where to find a setting and do not depend on a Cx foundation.

### Create or duplicate a profile

Use **New from baseline** for a profile that should begin with shared values and no custom fields. Open **Profile actions** and choose **Duplicate profile** when a new profile should begin from an existing editable profile.

For **New from baseline**, the proposed YAML filename follows the card title automatically. Edit the filename directly when a different name is needed; further title edits then leave that custom filename unchanged. Provide a unique filename and complete the same preview, review, and save process. The editor checks for an existing filename during review and checks again immediately before saving. New and duplicated profiles begin as unreleased drafts so they can be reviewed before release.

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

1. Review every pending profile, Cx Foundation, My Menu, Camera Buttons, and baseline draft.
2. Open each draft and save it through its exact-diff review, or choose **Discard** and confirm that decision.
3. For completed physical Camera Lab sessions, refresh **Camera Lab evidence**, check only exact items to retain, review the YAML, and separately confirm the import. It can mark only the mapped C1–C3 setting as configured; it never claims read-back, registration, operational testing, backups, or Canon verification.
4. If the verification workbook has edits to bring into the project, save and close Numbers or Excel, then choose **Import verification tracker** and confirm. Neither import path runs automatically.
5. When the pending list is empty, choose **Validate readiness**. It reports whether verification, Matrix/settings, or Setup spreadsheet-derived artifacts need refresh.
6. After readiness passes, choose **Run local build**, read the final warning—including whether Apple Numbers will run temporarily in the background—and confirm. Follow the numbered stage, elapsed time, and current command; expand **Watch command log** for live step output or **Show status details** for readiness and final results. Refreshing the page reconnects to the running build. If Numbers was already open, save and close it, then choose **Resume after closing Numbers**; the workflow rechecks safety and continues with only the spreadsheet artifacts that still need attention.
7. Review the generated result, then open **Finish Day** when you are ready to commit and synchronize the completed source work.
8. Use **Stop Profile Editor** in the header when finished.

For an external pack, this workspace is named **Evidence Review**. Refresh the evidence, select only the intended completed physical-camera items, review the exact verification-status YAML diff, acknowledge the narrow evidence boundary, and confirm. The transaction writes only the selected pack's verification-status source, creates a pack-scoped recovery backup, validates the combined source context, and does not create a spreadsheet or run a build.

The guarded Review & Build action for embedded sources runs source-only validation, refreshes only safely stale spreadsheet-derived artifacts when needed, then runs the normal development build and full validation. For an external pack this workspace becomes **Evidence Review**, hides build controls, and may update only pack-owned verification status. If the active verification tracker may contain unimported edits, evidence promotion stops. Permanent reference-card profile YAML remains read-only; My Menu and Camera Buttons change only through their dedicated structured editors. Neither surface renames profiles, permanently deletes cards, commits, pushes, publishes, or changes website version metadata.

## Get more help

For detailed safeguards, recovery behavior, and advanced baseline or My Menu behavior, open the [Profile Editor workflow reference](profile-editor.html). For physical-camera comparison and guarded application, open the [Camera Lab User Guide](camera-lab-user-guide.html). For camera-field meaning and recommendations, use the linked Canon and project reference materials.
