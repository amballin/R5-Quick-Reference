# Profile Specification

## Scope

This specification governs subject/profile YAML under `10 Profiles/`.

## Requirements

- Every profile inherits `baseline`.
- Every profile and permanent reference card requires one immutable canonical `card_id` UUID. Existing cards are migrated deterministically; create and duplicate operations generate a new UUID. Titles and filenames remain human-facing labels rather than machine identity.
- A profile contains only values that differ from `00 Master/baseline.yaml`; it must not repeat baseline values.
- Overrides must use paths present in `baseline.defaults` and compatible value types.
- Profile data retains camera concepts as separate fields, including ISO mode, fixed ISO value, Auto ISO maximum, Servo AF Case, Tracking Sensitivity, Accel./Decel. tracking, Switching tracked subjects, stabilization mode, IBIS, Lens IS, and High speed display.
- Profiles contain shooting settings and concise field-use content, not duplicated educational explanations. Reference applicable appendices instead.
- Preserve existing profile filenames, titles, YAML structure, data, and backward compatibility unless explicitly approved.
- `metadata.release: true` selects the profile/card for the offline iPhone/PWA bundle. Absence or false does not select it, but changing this flag never removes active profile source or moves it to Deleted Cards.

## Baseline Impact and Guarded Migration

The local editor may load the current baseline into a session-only draft and analyze proposed value changes against every inheriting profile. Analysis remains available when the baseline draft is unchanged so current or draft My Menu coverage can be evaluated independently. This analysis must use the repository-owned baseline impact engine and report inherited effective-value changes, values protected by existing overrides, overrides made redundant by the proposed baseline, removed override paths, incompatible override types, and current My Menu route coverage.

The repository must also provide a read-only command-line baseline-impact check for changes reviewed outside the UI. It compares the worktree `baseline.defaults` with the baseline at `HEAD` by default or another explicit `--base-ref`, loads the current authored profiles, and calls the same repository-owned impact engine as the editor. Metadata-only and YAML-formatting changes are not baseline-setting changes. No semantic change returns status 0; one or more semantic baseline-default changes print their per-profile classifications and return status 1; invalid input or an unreadable comparison returns status 2. The CLI must not write a migration, and a reported semantic change must be handled through the guarded editor workflow below.

The draft may change values only for existing baseline setting paths. The server must reject missing paths, additional paths, and values incompatible with the current baseline type. Reloading the browser discards the draft. Baseline impact analysis does not create a review token and must not write the baseline, profiles, generated output, or any other project file.

The editor may turn an analyzed draft into a read-only migration plan. The migration-plan action must be available both above the impact report and after its setting-preference controls so the user does not need to scroll back to the first action. Every inherited profile-setting change requires an explicit `follow_baseline` or `preserve_previous` choice. A preserve choice proposes a new override equal to that profile's previous effective value; a follow choice proposes no override. Newly redundant overrides are proposed for removal, and protected overrides are retained. Missing choices and invalid overrides keep the plan incomplete and must remain visible as unresolved items.

The server must recompute the impact from the complete draft and current session My Menu configuration and validate every submitted choice against it. It must reject stale, duplicate, invalid, ambiguous, and inapplicable choices. Bulk choices may fill only unresolved inherited changes. Every displayed configured My Menu setting on an editable profile card that lacks a card cue must be included automatically as a planned profile change when its item resolves to one unique configured tab. This includes authored C1–C3 routes, subject cards without a Cx foundation, and profile-based reference cards; permanent reference cards remain excluded. Each authored card cue whose named tab is absent from the current draft, or whose supported setting identity is no longer present in that named tab, must be included automatically as a planned removal even when the setting is hidden by card rules. A tab rename or shortcut move therefore plans removal from the old tab and addition to the uniquely resolved new tab. Each planned change names the profile, setting path, tab, reason, and target `card.field_setup.my_menus` location. The plan must explain that cue additions and removals change only card access labeling and color, not settings displayed on cards or items in the camera's My Menu. An incomplete plan remains session-only and cannot create a review token or write source.

A complete plan may be reviewed and applied only after the user explicitly acknowledges both the C1–C3 impact report and the My Menu route report. The server must build the exact candidate bytes for every source that actually changes, validate those candidates in an isolated source layout, and show one exact multi-file YAML diff. Include `00 Master/baseline.yaml` only when the proposed baseline differs from the current baseline; a profile-only My Menu cue addition, removal, or move must contain only affected profile candidates. The review token must be short-lived, one-use, and bound to both the candidate bytes and the fingerprint of every source file. A plan with no source changes must expose no write action.

The applied migration must set the proposed baseline values, add overrides selected to preserve previous effective values, remove newly redundant overrides, retain protected overrides, remove planned obsolete My Menu cues, and append planned missing cues to existing profile rows. Removals occur before additions so a tab rename or shortcut move produces one deterministic candidate. Removing a cue must preserve unrelated settings and tabs, delete an empty tab block, and remove empty migration-created `access_only` and `field_setup` scaffolding when the final cue is gone. The migration may create `card.field_setup.my_menus` when an eligible profile has no prior route, but it must not invent a C1–C3 start or source profile. A profile-based reference card created by this migration uses `access_only: true`; a subject card simply omits Cx metadata. The migration must leave C1–C3 registrations, existing starting-mode declarations, existing source-profile declarations, unresolved My Menu identities, unrelated routes, and the session My Menu configuration unchanged. Immediately before writing, the server must reconfirm every fingerprint, back up prior and candidate source bytes, replace each file atomically, run source validation, and restore every written file if any write or validation step fails.

### C1–C3 Impact Warnings

Baseline impact analysis must also calculate effective before-and-after values for the three currently assigned C1–C3 registrations defined by the synchronized control mappings and `90 Testing/eos_r5_verification_tracker.yaml`. The report must identify each slot with its current assigned profile, include every proposed baseline setting path for all three modes, and distinguish values that change with the baseline from values protected by an explicit registration entry.

For each registered mode whose effective value changes, the report must warn about every shooting profile whose `card.field_setup.start` declares that C-mode. Each warning identifies the profile, declared source profile, and affected settings. The migration may apply separately planned baseline/profile changes, but it must not modify C1–C3 registration definitions, profile starting-mode metadata, source-profile declarations, or My Menu routes in response to these warnings.

### My Menu Card-Coverage Warnings

Baseline impact analysis must inspect the fully merged rows displayed by each profile card against the current session-only My Menu draft. The profile editor's Canon options catalog must provide an explicit, unique setting-path identity for each supported My Menu item; label matching is not sufficient.

My Menu is a stable fast-access configuration, not a transition recipe. Matching a C1–C3 starting value must not make a shortcut unnecessary. For both the current and proposed baseline, the engine must use the card renderer's conditional visibility rules to determine whether each declared route setting is displayed. The report must show whether its identified Canon item is available in the named configured tab and whether a displayed configured shortcut lacks a card cue. A cue gap introduced because a conditional row becomes visible after the proposal must be identified as newly visible.

The report must include access-only profile cards and exclude permanent reference cards. A card tab assignment with no displayed settings is informational and is omitted from that rendered card; hidden status alone is not a recommendation to remove the shortcut from My Menu. A configured shortcut whose setting is not displayed on any card remains only a possible camera-configuration removal candidate. By contrast, an authored card cue is obsolete when its named tab is absent, or when its known setting identity is absent from that named tab, and must be listed as a planned profile-cue removal. A declaration whose setting identity is unknown remains an unresolved warning unless its entire named tab is absent. Findings must not mutate the browser's My Menu draft, C1–C3 registrations, or profile routes. A complete reviewed migration may synchronize multiple existing cards; an ordinary guarded profile review synchronizes its one candidate against the persisted global My Menu layout. Editing or restoring the session My Menu draft invalidates an existing coverage report and review token and requires a new analysis.

## Guarded Local Editor Transactions

Profile Editor 1.0 is the primary local interface for routine profile, Cx Foundation, My Menu, baseline, camera-reference, readiness, and local-build work. Workflow documentation must lead with this interface for those tasks and reserve terminal-first instructions for startup, troubleshooting, Git/handoff, spreadsheets, testing import, recovery, and publication.

The normal Profile Editor runtime must use loopback port 8765 in the authoritative `main` worktree and 8766 in a development worktree, while retaining an explicit diagnostic port override. The development application wrapper must use a distinct macOS bundle identifier so it can run beside the main application. The wrapper must hand launch supervision to a detached background process and exit immediately, allowing every Finder click to execute the verified start-or-reuse path instead of activating a waiting non-interactive shell. Each checkout must keep its runtime PID only in its own machine-local workspace. Reopening an application may reuse and reopen a responsive existing instance only after verifying its exact editor program, repository working directory, expected port, and editor endpoint. Launch must discard stale PID records, preserve prior diagnostic log content, and refuse to stop or reuse an unrecognized port listener. A separate recovery stop command must enforce the same ownership checks before signaling a hidden editor process.

The local loopback profile editor may perform only these writes under `10 Profiles/`:

- update the title, optional subtitle, metadata status, release flag, baseline overrides, and saved-My-Menu card cues of an existing shooting profile without renaming its file;
- create a new baseline-derived shooting profile; or
- duplicate an existing shooting profile into a new file;
- restore an exact held shooting-profile source from the machine-local Deleted Cards area after reviewed conflict checks; or
- move a saved editable unreleased shooting profile to Deleted Cards after proving it has no structured inbound references.

Reference cards and permanent deletion remain read-only. The shared baseline is writable only as part of a complete guarded migration. `00 Master/my_menu.yaml` and `00 Master/my_menu_colors.yaml` are writable only together through the dedicated guarded My Menu review transaction. The dedicated Cx Foundation transaction may update `controls.yaml`, its synchronized current-control record, C1–C3 registration headings and matching workflow labels, and the `card.field_setup.start`/`source_card_id` declarations needed to keep routes aligned. New and duplicated profiles must begin as `Draft` with `metadata.release: false` and a new `card_id`.

Every editor save must follow one guarded transaction:

1. Validate structured input, remove overrides equal to the baseline, and deterministically synchronize the candidate's visible card cues with the persisted global My Menu layout.
2. Confirm the source fingerprint and target-name availability.
3. Build and validate the complete candidate in an isolated temporary source layout.
4. Show the exact YAML diff and bind those candidate bytes to a short-lived one-time review token.
5. Reconfirm source and target state immediately before saving.
6. Create a timestamped recovery backup under the designated machine-local `Backups/` directory.
7. Replace the profile atomically and run source validation.
8. Restore the prior source state automatically if post-save validation fails.

The editor does not commit, push, publish, change website version metadata, rename, or permanently delete. It may move an eligible unreleased card into recoverable Deleted Cards and restore it through the dedicated guarded transactions. It may run the guarded local validation/build sequence defined in the Build and Validation Specification; Git and publication remain separate operator-authorized workflows.

The workspace order is **Profiles**, **Cx Foundation**, **Deleted Cards**, **My Menu**, **Baseline Setup**, **Review & Build**, then **Camera Reference**. Profile drafts must survive profile and workspace navigation in browser memory. The currently selected saved editable profile is the active profile context and must become the Profile to evaluate when the owner moves from Profiles into Cx Foundation. The sidebar shows pending badges for profile, Cx Foundation, My Menu, and baseline work, while Review & Build lists every pending item with actions to open it or discard it after confirmation. Closing or refreshing the page while any draft remains invokes the browser leave warning. A local build remains locked until every pending item is saved or explicitly discarded and a fresh readiness check passes.

Profile actions closes after any enabled submenu action is selected. **Restore saved profile** discards only unsaved browser edits and reloads active source. **Move to Deleted Cards** remains visible for every saved card; when disabled, the menu must state the actionable reason, including release state, unsaved changes, structured inbound references, or permanent-reference status. The Deleted Cards page must summarize the unrelease-save-move sequence, distinguish never-saved browser drafts from saved active cards, and state that structured references and permanent reference-card status block removal.

The Cx Foundation workspace provides two explicitly separate decisions. **C1–C3 assignments** selects three distinct editable shooting profiles, one per slot. **Cx Foundation Fit** selects one editable card, compares its effective values with all three candidate foundations simultaneously, and counts differences by rendered visible card row using the same combined-row semantics as the card change markers. Every lowest-count foundation is marked Recommended, but the editor must never select or save it automatically. The owner may explicitly select any C1–C3 slot or No Cx. Fit uses an unsaved browser profile draft when one exists, but saving that card's foundation remains blocked until the ordinary profile draft is saved or discarded.

An assignment review must synchronize both control mappings, registration headings and matching workflow labels, and every card route using an affected slot. It must not alter concrete C1–C3 registration row values; those remain deliberate matrix/tracker inputs because profile fields may contain ranges or guidance rather than one camera-ready value. A card-foundation review changes only that card's `start` and assigned `source_card_id`, or removes both for No Cx, while preserving My Menu routes. Both operations require exact multi-file diff review, byte-bound one-use tokens, concurrent-source checks, a machine-local recovery backup, atomic writes, source validation, and complete rollback.

The editable settings panel presents card-visible controls first in renderer order and keeps other controls in a collapsed secondary group. Its independently scrolling preview remains visible beside desktop settings. The preview must state that `Δ` compares with the saved C1/C2/C3 foundation rather than the baseline, so removing an override does not imply that the indicator will clear.

The My Menu page loads the persisted used tabs and ordered item identities from `00 Master/my_menu.yaml` and the curated palette/current named-tab assignments from `00 Master/my_menu_colors.yaml`. It is required only when changing the global camera tab layout, shortcuts, names, or colors. Ordinary profile create, duplicate, and update review derives that one candidate's visible `card.field_setup.my_menus` cues automatically from this persisted configuration and includes cue changes in the exact profile diff. The page supports up to five tabs and six ordered items per tab, omits unused tabs when saving, requires every used tab to have a name and at least one unique catalog item, and requires a distinct palette choice for each used tab. Light Red and Coral must remain visually distinguishable, with Light Red reading as red and Coral as orange-red.

The My Menu page must provide **Analyze profile impact** whenever baseline data is loaded. It submits the complete current My Menu draft with an unchanged or edited baseline draft to the same impact endpoint used by Baseline Impact, switches to that view, and focuses the My Menu coverage result. Saving My Menu remains a separate guarded transaction and does not silently rewrite profiles; the analysis and optional reviewed profile-only migration handle resulting missing and obsolete card cues.

Coverage uses stable `setting_path` identities on supported My Menu catalog items, not membership in the recommended tabs. Saved AF Operation, Eye Detection, and ISO speed settings entries therefore map to the corresponding profile rows even when they appear in a newly created tab. A catalog item without a supported profile-setting identity may be preserved in the saved camera reference, but it must be reported as unrepresented rather than guessed onto a card row.

A My Menu save must validate both complete candidates, show one exact two-file YAML diff, bind every candidate byte and source fingerprint to a short-lived one-use token, create a recovery backup containing prior and candidate files, replace only reviewed changed files atomically, run source validation, and roll back every written file on failure. Saved colors apply globally to matching named-tab tokens, values, change markers, PDFs, and field-guide access tokens. The persisted layout drives the dynamic read-only My Menu reference card. Reference previews are permitted without overrides or source writes, and every displayed card preview must provide a Return to top action in the editor.

The editor provides one global Return to top control rather than a preview-local action. It is a fixed circular up arrow available in Profiles, Cx Foundation, My Menu, Baseline Setup, Review & Build, and Camera Reference, appears only after meaningful vertical scrolling, respects lower-right safe-area insets, carries an accessible text label, and is hidden for print.

The editor header must display its semantic editor version and a short deterministic build identifier followed immediately by the established silver camera logo used by card navigation. The server derives the build identifier from the relevant editor, renderer, Cx-comparison, and card-template source bytes; it must not use a timestamp that changes without a source change.

Baseline migrations use the same safety principles across multiple files: isolated candidate validation, explicit warning acknowledgements, exact diff review, byte and fingerprint binding, a recovery backup containing every affected source, atomic per-file replacement, post-write source validation, and all-file rollback.

## Expected Structure

Profiles use the existing keys documented by `00 Master/schema.yaml`, including `metadata`, `title`, optional `subtitle`, `inherits`, `overrides`, and optional list content such as `checklist`, `watch_for`, `common_mistakes`, and `notes`.

## Enforcement and Evidence

- `00 Master/baseline.yaml` defines valid shared default paths and their effective types.
- `00 Master/schema.yaml` documents profile field structure.
- `80 Build/validators/profile_validator.py` enforces required keys, `inherits: baseline`, override paths/types, title uniqueness, and list shapes.
- `80 Build/validators/yaml_validator.py` rejects malformed or duplicate-key YAML.
- `80 Build/validators/profile_editor_validator.py` verifies editor readiness, source fingerprints, read-only reference-card behavior, unreleased-draft defaults, and complete My Menu setting identities for declared routes.
- `80 Build/my_menu_colors.py` validates the curated palette and named-tab assignments used by both renderers and guarded editor saves.
- `80 Build/my_menu.py` validates persisted tab names and ordered Canon item identities; `80 Build/my_menu_reference.py` derives the read-only reference-card rows.
- `80 Build/cx_route_analysis.py` owns both selected-foundation change markers and simultaneous C1–C3 visible-row fit counts.
- `80 Build/test_profile_editor.py` exercises guarded update, create, duplicate, Cx assignment and selection transactions, foundation-fit recommendations, baseline migration, one-use review, conflict, all-file rollback, acknowledgement, reference-card boundaries, session My Menu availability analysis, draft-ledger UI, Cx-foundation change-indicator semantics, and local-build gating in temporary repositories.
- `80 Build/baseline_impact.py` provides deterministic, read-only profile comparison, C1–C3 registration and starting-route warnings, My Menu card-coverage analysis, and validated migration planning for current and proposed baseline values.
- `80 Build/test_baseline_impact.py` covers inherited choices, protected and redundant overrides, C1–C3 effective values, visible-card My Menu coverage and availability, newly visible cue gaps, obsolete cues from removed tabs and shortcuts, tab moves, globally unreferenced configured shortcuts, invalid paths and types, stale-decision rejection, reference-card exclusion, and input immutability.
- `80 Build/baseline_migration.py` converts a complete plan into deterministic baseline/profile candidate bytes without mutating its inputs.
- `80 Build/test_baseline_migration.py` covers candidate override addition/removal, My Menu cue addition/removal/moves, empty route cleanup, metadata updates, incomplete-plan rejection, and input immutability.
- Build and PWA code under `80 Build/` implements merging and release filtering; generated-output and PWA validators provide integration evidence.

The profile validator rejects an override when its value equals the baseline, enforcing the baseline-plus-overrides no-duplication rule.
