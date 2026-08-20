# Decision Log

Only entries marked **Accepted** are binding. **Proposed** entries are non-binding possibilities; **Superseded** and **Rejected** entries are historical only. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md).

## Profile Editor as the Main Local Interface

**Status:** Accepted
**Date:** 2026-08-20

Treat Profile Editor 1.0 as the main day-to-day interface for profile editing and previews, persisted My Menu work, baseline analysis and guarded migration, camera-reference lookup, session-change review, source readiness, and the normal local validation/build sequence. Lead routine workflow documentation with the editor rather than presenting it as an optional prototype or secondary authoring tool.

Keep specialized workflows outside the editor where their scope or authorization differs: Git preflight and handoff, spreadsheet preparation and testing-status import, on-camera verification, recovery, committing and pushing, and publication. The editor remains local and loopback-only and does not expand its existing Git, publication, deletion, rename, or version-metadata authority.

## Guarded Session Review and Local Build

**Status:** Accepted
**Date:** 2026-08-20

Order the Profile Editor workspace as **Profiles**, **My Menu**, **Baseline Setup**, **Review & Build**, and **Camera Reference**. Preserve unsaved profile drafts when the user selects another profile or workspace, show per-workspace and total pending-change badges, and collect every unsaved profile, My Menu, and baseline draft in **Review & Build**. Require explicit confirmation before discarding a draft, and use the browser's leave warning while any session draft remains.

Keep the card preview beside the independently scrolling settings panel. Order **Shown on this card** by the renderer's card rows, followed by collapsed additional settings. Explain beside the preview that `Δ` compares the current card with its saved C1/C2/C3 foundation, not with the baseline; using a baseline value clears `Δ` only when that value also matches the saved foundation.

Permit **Review & Build** to run the documented local sequence only after every browser draft has been saved or explicitly discarded, a fresh source-readiness check passes, and the user confirms that generated local output and tracked documentation may change. The server must serialize build requests and run source-only validation, the normal development build, and full validation in that order, stopping at the first failure. It must not commit, push, publish, change website version metadata, rename, or delete. This decision supersedes only the prior prohibition on editor-initiated local builds in **Guarded Local Profile Authoring**; all guarded-save, Git, and publication boundaries remain in force.

## Main-Owned Baseline Impact Invariant

**Status:** Accepted
**Date:** 2026-08-20

Keep baseline/profile impact analysis in the shared repository module `80 Build/baseline_impact.py`. The Profile Editor remains the guided interface for proposing values, choosing per-profile outcomes, reviewing exact source changes, and applying a guarded migration, but the invariant does not belong exclusively to the browser application.

Provide `80 Build/baseline_impact_check.py` as a read-only command-line check for baseline changes made or reviewed outside the UI. By default it compares the worktree baseline defaults with `HEAD`; `--base-ref REF` selects another Git baseline such as `origin/main`. It must load the current authored profiles, call the same shared impact engine as the UI, ignore metadata-only or YAML-formatting differences, print every semantic baseline-setting change and its profile classifications, return success when no semantic baseline-default change exists, return status 1 when review is required, and return status 2 when the comparison cannot be completed. It must never modify baseline, profile, generated, Git, or publication state.

Use the CLI as a review boundary, not as an alternate migration writer. A semantic change reported by the command still belongs in the guarded Profile Editor migration workflow. Main owns the shared engine, CLI, tests, and specifications; the UI owns the guided transaction.

## Cx Foundation Change Indicators

**Status:** Accepted
**Date:** 2026-08-19

On every profile card with an authored C1–C3 route, derive whether each visible field value differs from the effective profile named by `card.field_setup.source_profile`. Reserve a fixed rightmost table column and place a `Δ` in that column only when the row requires a change from the selected foundation; leave the cell blank when it already matches. Combined rows require the marker when any represented underlying setting differs. Keep the C1/C2/C3 route token white.

Keep My Menu value colors independent from whether a change is required. Every visible setting assigned to a named My Menu tab retains that tab's color whether or not it matches the Cx foundation. The color answers where the setting is available; the rightmost `Δ` answers whether it must change. Render each `Δ` in the same color as its setting value, including the normal card text color for non-My-Menu rows. Include an accessible, print-safe legend and change description. Derive this presentation during rendering rather than storing duplicated change flags in profile YAML.

Display the local profile editor's semantic version and a short deterministic build identifier in its header. Calculate the build identifier from the relevant editor, renderer, comparison-engine, and card-template source bytes rather than a timestamp so the same sources produce the same identifier.

## Field Setup Without a Cx Foundation

**Status:** Accepted
**Date:** 2026-08-20

Permit every editable profile card to carry named My Menu setting cues without requiring a C1–C3 starting route. My Menu color answers where a displayed setting can be found and therefore remains useful independently of any registered-mode foundation. Automatically plan a missing cue for every displayed setting whose configured My Menu item resolves to one unique tab, including subject cards without a Cx route and profile-based reference cards. Permanent reference cards remain read-only and excluded.

Keep derived Cx comparisons when both `card.field_setup.start` and `source_profile` identify a valid foundation. When an editable profile card has no Cx foundation, reserve the same change-indicator column and mark every visible settings row with `Δ` because the current camera state cannot be proven from project data; the marker directs the user to verify or set the target value. Use a legend and accessible label that state **Verify/set — no Cx foundation** rather than claiming a calculated difference. This decision supersedes only the authored-Cx limitation on planned My Menu cues and the prior omission of change indicators from access-only or other non-Cx profile cards. My Menu colors remain independent from change indicators.

## Guarded Removal of Obsolete My Menu Card Cues

**Status:** Accepted
**Date:** 2026-08-20

When the current My Menu draft removes a named tab or removes a supported shortcut from its declared tab, identify every matching profile-card cue as obsolete and include its removal automatically in the guarded migration plan. This applies whether or not the setting is currently visible on that card because the authored access route is no longer true. A tab rename or shortcut move is represented explicitly as removal from the old tab plus addition to the uniquely resolved new tab.

Remove only the reviewed setting cue. Delete its tab block when no settings remain, and clean up empty migration-created access-only routing scaffolding when the last cue is removed. Keep C1–C3 registrations, starting modes, source profiles, unrelated card cues, the session My Menu draft, and declarations without enough setting identity to prove obsolescence unchanged. Require the existing analysis, acknowledgement, exact multi-file diff, source fingerprints, recovery backup, validation, atomic replacement, and rollback safeguards.

This decision supersedes the warnings-only treatment of known unavailable My Menu routes in **Always-Available My Menu Profile Impact and Global Return Control** and **Guarded Local Profile Authoring**. Advisory treatment remains in force for unresolved identities and for configured shortcuts not displayed on any card.

## Guarded My Menu Card Colors

**Status:** Accepted
**Date:** 2026-08-20

Store the reusable named-tab card palette and assignments in `00 Master/my_menu_colors.yaml`, never in individual profiles. Allow the My Menu page to select one distinct curated palette color for each named tab. Tab names and camera menu items remain session-only, but a color assignment may be persisted only through an exact YAML diff, one-use review token, concurrent-change check, machine-local recovery backup, atomic replacement, source validation, and automatic rollback.

Use the saved named-tab color consistently for route tokens, setting values, matching change indicators, PDF cards, and field-guide My Menu access tokens. Keep a visible tab label so color is never the sole access cue. This decision supersedes the fixed requirement that SWITCH must always remain green and the earlier amber-only change-marker treatment; the initial assignments retain green for SWITCH and gold for AF Case until deliberately changed through the guarded editor action.

## Persisted My Menu Layout and Field Reference Card

**Status:** Accepted
**Date:** 2026-08-20

Persist the approved EOS R5 My Menu tab names and ordered item identities in `00 Master/my_menu.yaml`. The Profile Editor's My Menu page is the only guided editor for this source. Save the layout and matching named-tab color assignments as one reviewed two-file transaction with exact diffs, one-use token, concurrent-change checks, a machine-local recovery backup, atomic replacement, source validation, and all-file rollback.

Create a released, read-only **My Menu** reference card beside **Camera Buttons**. Its displayed sections and ordered items are derived at render time from the saved My Menu configuration rather than duplicated in profile YAML. Every used tab becomes one section; adding, renaming, reordering, or removing a saved tab changes the next reference-card preview and build. The card records the approved project layout as a field reminder and does not claim that the physical camera has been verified. Reference-card edits remain unavailable; changes go through **Configure My Menu**. Permit reference-card previews in the editor and provide a Return to top action after any preview.

Rename the former Pink palette choice to **Light Red** and use a visibly red tone distinct from the more orange **Coral** choice. This decision supersedes earlier session-only/no-persistence My Menu editor requirements and the color-only save boundary, but retains guarded persistence and the separation between approved project configuration and verified physical-camera state.

## Always-Available My Menu Profile Impact and Global Return Control

**Status:** Accepted
**Date:** 2026-08-20

Keep Baseline Impact analysis available after the baseline loads even when no baseline setting has changed. Add **Analyze profile impact** to Configure My Menu; it runs the same read-only server analysis against the complete current My Menu draft, switches to Baseline Impact, and focuses the My Menu coverage report. A separately saved My Menu remains structurally valid, while unavailable old tab names and missing profile-card cues remain visible warnings rather than silent profile rewrites.

Give each supported configured shortcut a stable profile-setting identity independent of whether it belongs to the recommended tabs. In particular, the saved AF Operation, Eye Detection, and ISO speed settings shortcuts resolve to `autofocus.operation`, `autofocus.eye_detection`, and the combined ISO card row rooted at `exposure.iso.mode`. This lets newly added used tabs participate in coverage analysis rather than limiting analysis to the initial recommendation.

Permit a complete migration plan containing only planned My Menu card cues to produce and review profile candidates without manufacturing an unrelated baseline change. Omit `00 Master/baseline.yaml` from that transaction when the proposed baseline equals the current baseline. Keep the usual acknowledgements, exact diff, source fingerprints, recovery backup, atomic writes, validation, and rollback for the affected profile files. If neither baseline nor profile source needs a change, show that no migration is required and provide no write action.

Replace the preview-local Return to top button with one global, fixed circular up-arrow control available across all four editor views. Show it only after meaningful scrolling, place it within the lower-right safe area, give it an accessible Return to top label, and hide it for print. Match the established Reference Guide floating-return treatment.

## Guarded Local Profile Authoring

**Status:** Accepted
**Date:** 2026-08-17

Allow the loopback-only profile editor to update an existing shooting profile, create a baseline-derived shooting profile, or duplicate an existing shooting profile. Keep permanent reference cards, camera My Menu persistence, and profile deletion outside the ordinary profile-editing scope; named-tab card colors are the only separately guarded My Menu-related source write. New and duplicated profiles must begin with `metadata.status: Draft` and `metadata.release: false`.

Require an exact YAML diff before every save. Bind the reviewed candidate bytes to a short-lived one-time token so the browser cannot save different content from what was reviewed. Before writing, confirm the loaded source fingerprint still matches and that a new target name remains available. Validate the complete candidate profile in an isolated temporary source layout, create a timestamped machine-local recovery backup, replace the target atomically, and run source validation after the write. Automatically restore the prior source state when post-save validation fails.

Allow a session-only **Baseline impact** workspace to propose value changes for existing baseline setting paths and calculate their effect on every inheriting profile. Keep the draft in browser memory and reject added or removed paths and incompatible values at the server boundary. Classify inherited effective-value changes, protected overrides, newly redundant overrides, removed paths, and incompatible override types through one repository-owned read-only impact engine.

Allow that workspace to build a migration plan. Require an explicit per-profile choice for each inherited effective-value change: follow the proposed baseline or preserve the previous effective value as a proposed override. Permit deliberate bulk choices across the complete proposal or within one changed setting, but apply them only to unresolved inherited changes and never replace an existing individual choice. Automatically include newly redundant overrides as proposed removals, retain protected overrides, and keep missing choices or invalid overrides visibly unresolved. Also include each displayed configured My Menu setting on an authored C1–C3 route that lacks a card cue as an explicit planned profile change, resolved to its unique configured tab. Describe those changes as color-coding existing card rows for My Menu access, and state visibly that they add neither setting rows to cards nor items to the camera's My Menu. Provide the same migration-plan action above and below the preference report. Recompute and validate the proposal, choices, and current session My Menu draft on the server; reject stale, duplicate, invalid, ambiguous, or inapplicable input.

Permit a complete plan to become one guarded baseline-migration transaction. Require explicit acknowledgement of the C1–C3 and My Menu warning reports, validate all candidate sources in isolation, and show one exact multi-file YAML diff. Bind the candidate bytes and every original source fingerprint to a short-lived one-use review token. Before writing, reconfirm every fingerprint, create a timestamped backup containing the prior and candidate baseline/profile sources, atomically replace each source, and run source validation. On any write or validation failure, restore every file already written. Apply the proposed baseline, add preservation overrides, remove newly redundant overrides, retain protected overrides, and add only planned My Menu card cues. Do not rewrite C1–C3 registrations, starting routes, source-profile declarations, unavailable routes, unnecessary routes, or the session My Menu configuration.

Extend baseline impact analysis to the canonical C1–C3 registration definitions. For every proposed baseline setting change, show the effective value before and after in **C1 Wildlife**, **C2 Birds in Flight**, and **C3 Landscape**, including when an explicit registration value protects a mode from the baseline change. Warn for every shooting profile whose declared `card.field_setup.start` uses an affected registered mode, and identify its declared source profile and affected settings. These are warnings only: analysis must not rewrite registrations, starting-mode routes, source-profile declarations, My Menu routes, or profile YAML.

Extend that report with read-only My Menu card-coverage analysis. Treat My Menu as a stable fast-access configuration rather than a transition recipe: a declared shortcut does not become unnecessary merely because a profile value matches its C1–C3 starting environment. Evaluate the fully merged rows that each profile card actually displays, including access-only cards. Show a named My Menu tab on a card whenever at least one setting assigned to that tab is displayed, and omit that tab from the card only when none of its assigned settings are displayed. Report displayed settings whose Canon item is unavailable in the named tab and displayed configured shortcuts that lack a card cue. Identify a configured shortcut as a possible removal candidate only when no card displays its setting. These findings are advisory and must not rewrite profile routing or My Menu configuration.

Initialize the session-only My Menu configurator with the approved **SWITCH** and **AF Case** recommended tabs after the settings dictionary loads. Leave the remaining tabs and slots empty. Users may modify the browser draft, and **Restore recommended tabs** replaces it with the approved recommendation. Refreshing or reopening the editor starts from the recommendation again. This initial camera-layout draft remains unverified, does not claim the physical camera matches it, and creates no tab-name or menu-item persistence; the separately guarded named-tab card-color transaction is the only My Menu-related write endpoint.

The editor must not run builds, commit, push, publish, rename existing profiles, delete profiles, or persist the camera My Menu configuration. Its only non-profile writes are `00 Master/baseline.yaml` through the guarded migration transaction and `00 Master/my_menu_colors.yaml` through the guarded color transaction. Git and publication remain separate operator-authorized workflows.

## Consolidated Spreadsheet-Derived Artifact Recovery

**Status:** Accepted
**Date:** 2026-08-08

Use `build-all-spreadsheet-downloads.sh` as the single non-publishing recovery command for stale verification, Matrix/settings, and Setup spreadsheet-derived artifacts. Diagnose all three states before rebuilding, stop without modifying files when the verification tracker may contain unimported edits, rebuild a safely stale verification copy before release workbook families, and skip artifacts that are already current. Preflight remains diagnostic and must never invoke the refresh automatically.

Centralize Apple Numbers automation behind both supported bundle IDs. Explicitly launch and wait for the selected application before open, conversion, finalization, or export operations; preserve actionable per-candidate errors when neither application can complete the operation. Machine-local runtime fallbacks must derive from the current user's home directory rather than a username-specific absolute path.

## Machine-Verifiable Authoritative Project Identity

**Status:** Accepted
**Date:** 2026-08-07

Identify this repository with `00 Master/project_identity.yaml` as the authoritative Canon EOS R5 source project. Before edits, resolve and report the Git root, require the working directory to remain inside it, reject old, backup, archive, generated-output, build-output, and native-wrapper locations, and confirm the required source components and baseline camera identity.

Do not search sibling directories or select another repository automatically when identity checks fail. Stop for project-owner direction instead. Enforce the same checks at the start of source-only and full validation so prose rules and machine behavior cannot silently diverge.

## Camera Defaults My Menu Access Route

**Status:** Accepted
**Date:** 2026-08-06

Give Camera Defaults an access-only field route containing **SWITCH** and **AF Case**, without a C1–C3 token because Camera Defaults is not a registered-mode target. Color Shutter Type, Subject Detection, and Image Stabilization with SWITCH; color Servo AF Case and Switching Tracked Subjects with AF Case. Keep values reached fastest through Q, dials, buttons, or ordinary menu navigation white. Render a visible token for every color and explain the access-only meaning in the generated Notes.

Permit baseline-driven profile cards displayed in the reference category to declare an access-only My Menu route without a starting C-mode. Keep permanent authored reference cards ineligible for `card.field_setup`.

## Project-Customized Case 1 Preset

**Status:** Accepted
**Date:** 2026-08-06

Keep **Case A (Auto)** with automatic parameters as the general operational baseline, Camera Defaults state, and People target. Configure **Case 1** once as the project preset with **Tracking Sensitivity -1** and **Accel./Decel. tracking +1**. Label it **Case 1 (Custom)** and state wherever the values are taught that Canon's factory Case 1 is 0 / 0. Selecting or resetting Canon's Case 1 defaults can therefore remove the project customization.

Use the custom Case 1 preset for Wildlife, Birds Perched, and Sports. Keep Birds in Flight on Case 4 at 0 / +1. Register C1 Wildlife with the custom Case 1 preset, retain C2 Birds in Flight and C3 Landscape, and explicitly include the Case 1 to Case A change in the People-from-C1 field transition. Treat the values and registrations as approved targets pending physical verification.

This decision supersedes **AF Subject Switching, Case Parameters, and High Speed Display**, **Servo AF Cases in Profiles and Cards**, and **C1-Aligned Operational Baseline** only where they assign Case A to C1 Wildlife, assign Case 4 to Sports, or require Camera Defaults to match every C1 setting. Baseline-plus-overrides remains authoritative.

## AF Subject Switching, Case Parameters, and High Speed Display

**Status:** Accepted
**Date:** 2026-08-06

Use **On subject** as the shared approved target for **Switching tracked subjects**. Treat it as a separate subject-selection control that applies with Face + Tracking, Zone AF, and Large Zone AF, not as a third Servo AF Case parameter. Add it as the fourth shortcut in **My Menu: AF Case**, after Servo AF, Tracking Sensitivity, and Accel./Decel. tracking. Show the merged value on Camera Defaults and cards whose effective AF Method supports it, including inherited baseline matches.

Store Tracking Sensitivity and Accel./Decel. tracking as separate profile settings. Case A uses Auto for both. Birds in Flight uses the Canon Case 4 starting values of Tracking Sensitivity 0 and Accel./Decel. tracking +1; the later **Project-Customized Case 1 Preset** decision governs Wildlife, Birds Perched, and Sports. When the effective Servo AF Case is 1–4, show both values in one compact **Track / Accel** row immediately below Servo AF Case; omit that row for Case A and when Servo AF is inactive.

Use **High speed display: Enable** as a shared approved target pending physical verification. Show it on Camera Defaults, Camera Setup Essentials, and subject cards where the effective starting configuration uses regular High Speed Continuous or Electronic shutter. Omit it when the starting configuration cannot use the selectable setting, including High Speed Continuous+, Low Speed Continuous, and Single Shot. Keep it out of My Menu because it is a set-and-forget display preference rather than a routine field transition.

This decision supersedes **My Menu: AF Case** where that entry specifies only three shortcuts or excludes Case parameters from cards, and **Servo AF Cases in Profiles and Cards** where that entry requires cards to show only the selected Case.

## Machine-Local Unreleased Card Candidates

**Status:** Accepted
**Date:** 2026-08-04

Generate a disposable machine-local review mini-site at `Build Output/Card Candidates/` during every normal full build. Its index contains each card profile whose `metadata.release` is not `true`, with working card navigation and links to locally generated appendices. Keep these candidates out of `Build Output/merged-build/`, `docs/`, and every publishable PWA or website mirror. Continue generating intermediate HTML for all profiles as before.

Validate that every unreleased profile has exactly one candidate card, that released or stale cards are absent from the candidate set, and that the candidate index and card links resolve. Single-profile builds preserve their existing behavior and do not regenerate the complete candidate index; use the normal full build for candidate review.

## Local Pre-Release Version Indicator

**Status:** Accepted
**Date:** 2026-08-03

Prepend **Pre-Release •** to the version line only when the generated index is opened from the documented machine-local `Build Output/merged-build/` review location. Keep the generated site identical between the canonical merged build and `docs/`; determine the local-review context at runtime. The same index opened from `docs/` or served by GitHub Pages must retain the published version and date without the indicator.

## Definition-Aware Verification Tracker Integrity

**Status:** Accepted
**Date:** 2026-08-03

Treat a machine-local verification tracker as current only when its file hashes, canonical YAML-status hash, workbook revision, and source fingerprint all match its synchronization marker and the current project definitions. A tracker whose definitions or YAML status changed but whose workbook files remain unchanged may be rebuilt automatically from canonical YAML. If the workbook also contains unimported edits, block rebuilding and opening through the helper until those edits are imported; preserve evidence and mark changed definitions for retest through the existing fingerprint-aware importer.

Enforce this state in the open-tracker helper, Preflight, source validation, and Finish Day. Finish Day must run source validation, the normal development build, and full validation before staging; it may not continue to a commit after validation is declined or postponed. Keep working Excel and Numbers files exclusively in the machine-local Verification folder, reject them under `90 Testing`, and retain Git-tracked YAML as the portable canonical record.

Represent **My Menu: SWITCH** and **My Menu: AF Case** as distinct checklist tests with independent status and evidence. Require SWITCH at sequence 4 and AF Case immediately afterward, including the approved shortcut order and confirmation that Servo AF opens the complete Case selector.

## My Menu: AF Case

**Status:** Accepted
**Date:** 2026-08-03

Create a separate EOS R5 My Menu tab named **AF Case** with **Servo AF**, **Tracking Sensitivity**, and **Accel./Decel. tracking** in that order. In this tab, Servo AF is the Case-selection shortcut and does not replace the Q/DOF workflow for changing AF Operation.

Add AF Case to the field routes for Wildlife, Birds in Flight, Birds Perched, People, and Sports, whose approved starting profiles use Servo AF. Associate the colored route with the existing **Servo AF Case** row. Keep Tracking Sensitivity and Accel./Decel. tracking as deep-dive troubleshooting controls rather than separate profile or card settings.

This decision supersedes the temporary-access paragraph in **Servo AF Cases in Profiles and Cards** and the earlier approved-route list in **Compact Cx and My Menu Field Cues** only where those entries deferred an AF Case My Menu or omitted it from Servo AF card routes. It does not change the approved five-item **SWITCH** tab.

## Servo AF Cases in Profiles and Cards

**Status:** Accepted
**Date:** 2026-08-03

Treat Servo AF Case as a profile-owned camera setting under the baseline-plus-overrides architecture. Use **Case A (Auto)** as the shared C1 Wildlife baseline and use **Case 4** overrides for Birds in Flight and Sports. The Case remains stored but inactive when AF Operation is One-Shot AF or Manual Focus.

Show **Servo AF Case** immediately after **AF Operation** on every merged card whose effective AF Operation is Servo AF. Omit it from One-Shot AF and Manual Focus cards. Keep only the selected Case on the concise card; keep Case definitions, parameters, subject recommendations, and troubleshooting in **AF Cases & Tracking Behavior**.

Use registered C1-C3 profiles as the fastest normal field access and **AF3 > Servo AF characteristics** for a temporary change. Do not alter the approved five-item SWITCH My Menu configuration until physical testing confirms whether one registered item opens the complete Case selector. Retain the open sixth SWITCH position during that evaluation.

## Sticky Card Identity During Scrolling

**Status:** Accepted
**Date:** 2026-08-03

Keep the existing identity region visible beneath the shared Camera Settings navigation while responsive HTML card content scrolls. Apply this consistently to subject and reference cards: subject cards retain the title and existing Cx / My Menu route, while reference cards retain the title and any existing subtitle. Reuse the existing content without adding a duplicate title, route, or legend. Give a displayed Cx / My Menu route 8 px of breathing room before the identity divider without changing reference-card spacing, and disable the sticky treatment for print output.

## C1-Aligned Operational Baseline

**Status:** Accepted
**Date:** 2026-08-02

Use the approved C1 Wildlife registration target as the shared operational baseline and the Camera Defaults reset state. In addition to the existing matching values, set **Shutter Speed: Auto**, **Aperture: Auto**, **AF Method: Face + Tracking**, **Subject Detection: Animals**, **Eye Detection: Enable**, and **Drive Mode: High Speed Continuous** in `baseline.yaml`. This keeps Default Settings, C1 Wildlife, profile cards, and generated spreadsheet comparisons aligned instead of treating unset shutter or aperture targets as equivalent to the explicit C1 Auto values.

Keep baseline-plus-overrides behavior intact. Wildlife becomes baseline-derived; profiles that require deliberate-point AF, no subject priority, Eye Detection disabled, Single Shot, or another drive mode retain those differences explicitly. C1, C2, and C3 remain complete target configurations, and their verification states do not change merely because the project baseline now matches C1.

Classify this baseline as an approved target pending physical verification, not as owner-confirmed current camera state. After a camera reset or saved-configuration load, verify the shared defaults, controls, Auto update setting, and C1–C3 registrations before relying on them.

## Compact Cx and My Menu Field Cues

**Status:** Accepted
**Date:** 2026-08-02

Put a compact field-access route beneath the title of applicable iPhone cards: the intended starting C1–C3 mode followed by the abbreviated names of any My Menu tabs used to reach displayed changes. Keep ordinary Quick Control, dial, and button values white. Color My Menu setting values to match the visibly named tab token, with **SWITCH permanently green** because it is expected to be the primary transition tab. Support as many as five named tabs and distinct renderer-managed colors without putting raw styling values in profile YAML or relying on color alone.

Configure the approved routes now: C1 Wildlife, C2 Birds in Flight, C3 Landscape, Birds Perched from C1 Wildlife, People from C1 Wildlife through SWITCH, Sports from C2 Birds in Flight through SWITCH, Travel from C3 Landscape, and Macro, Waterdrops, or Fireworks from C3 Landscape through SWITCH. These are field-start recommendations pending physical transition verification. Add a generated Notes explanation that names the complete starting profile, requires registration verification before reliance, and explains the white-versus-colored access cue. Do not add hypothetical My Menu tabs merely to exercise the multi-tab support.

This decision implements the field-access portion of the earlier non-binding **Card Visual Format** direction without adopting its proposed light-body or profile-theme redesign.

## Workflow Documentation Review for Procedural Changes

**Status:** Accepted
**Date:** 2026-08-01

When a change affects an established command, workflow, or operator-facing procedure, review the relevant `WORKFLOWS` Markdown and `FINISH_DAY.md`. Before editing, identify whether those guides need updating and include the affected guide files in the proposed change scope; if no update is appropriate, state why. Keep Markdown authoritative and regenerate tracked workflow HTML through the established build rather than editing generated HTML directly.

## Curated Reader-Facing Release Notes

**Status:** Accepted
**Date:** 2026-08-01

Maintain concise reader-facing publication highlights in `00 Master/release_notes.yaml`. Generate summaries with `80 Build/release_notes.py`, using committed publish metadata and valid version transitions as the authority for publication boundaries and dates. With no version options, compare the two most recent publications. Permit optional `--from` and `--to` selection for historical ranges, using the latest matching publication when historical version reuse makes a label ambiguous. Keep prose curated rather than inferred from commit messages or file counts, and stop with an actionable error when any included publication lacks notes. Print Markdown to standard output by default; do not publish, commit, or write a generated artifact as a side effect.

Before a supported publication builds, commits, or pushes, calculate its candidate version and require a matching curated entry in `00 Master/release_notes.yaml`. Block publication with an actionable error when the entry is absent. This gate automates coverage enforcement only; it must not generate or infer the highlight prose.

## Automatic Spreadsheet Row Heights

**Status:** Accepted
**Date:** 2026-07-31

Use wrapped text and automatic row heights for every content-bearing table row in the Subject Settings Matrix and in the Setup workbook's Menu, Checklist, C1–C3 Registration, and Sessions sheets. Auto-fit those rows during generation so previews and initial output show all current content, then remove fixed custom-height metadata from the Excel export so rows continue to expand or contract when a user edits notes or other wrapped cells. Preserve deliberate fixed heights only for structural banner and spacer rows. Keep merged title and instruction areas deliberately sized because Excel and Apple Numbers do not reliably auto-fit merged cells.

## Preserve Spreadsheet Downloads in Normal Local Builds

**Status:** Accepted
**Date:** 2026-07-31

Make the normal local website build automatically include each complete, current, machine-local prepared workbook family and preserve exact compatible spreadsheet downloads from the committed release manifest for any remaining family. Reuse the existing revision, source-fingerprint, filename, and content-hash safeguards; do not regenerate Excel workbooks or invoke Apple Numbers as part of the normal build. If a committed workbook family is stale relative to its current inputs and no valid prepared replacement exists, stop the build with an actionable requirement to rebuild that family rather than silently retaining stale files or removing the Downloads section. Explicit spreadsheet build scripts remain the preparation workflow for new replacement workbook bytes, and website publication remains a separate authorized action.

## Source-Only Pre-Build Validation

**Status:** Accepted
**Date:** 2026-07-31

Separate editable-source checks from generated-output freshness checks. Provide `validator.py --source-only` for the pre-build stage, excluding prepared and published spreadsheet freshness, generated workflow-guide agreement, generated build output, and merged-PWA checks that are expected to become stale after legitimate source edits. Use the reliable local sequence source-only validation, normal build, then full validation, joined with `&&` to stop at the first error. Finish Day and Preflight guidance use the same sequence.

## Local Task-Oriented Workflow Guides

**Status:** Accepted
**Date:** 2026-07-31

Maintain a concise local workflow index with separate pages for Preflight, continuing on another Mac, local builds and build timing, spreadsheet creation/publication/status updates, on-camera verification testing, website publication, and recovery. The verification-testing page links to the machine-local working tracker, incorporates the operational sequence and evidence rules from the repository Checklist, and uses Git-tracked YAML rather than a shared live workbook for two-Mac handoff. Keep Markdown as the editable source and automatically regenerate readable HTML during normal builds and Finish Day. Track both formats in Git so the guidance follows the repository between computers, but exclude all workflow pages from `docs/` and the public website. Keep `FINISH_DAY.html` as the concise end-of-day recipe and link it with the workflow index.

## Retire Fixed Card PNG Exports

**Status:** Accepted
**Date:** 2026-07-31

Remove fixed downloadable card PNG generation, publication options, index links, and output folders because this export is not used. Keep responsive HTML as the published card format and PDF as an independent opt-in local output. Retain source/fallback PNG assets, PWA icons, spreadsheet preview images, and temporary in-memory rasterization required to assemble PDFs. This decision supersedes **Opt-In PNG Card Exports** and the fixed-PNG clauses in **Responsive HTML as Primary Published Card Format**.

## Auditable Publication Completion

**Status:** Accepted
**Date:** 2026-07-30

Do not treat a clean, synchronized Git repository as evidence that website publication occurred. Every supported publication must write a timestamped machine-local log and end with an unmistakable completed or failed result. After the push, verify that the latest commit advanced the website version correctly, the published index displays that version, the commit matches its upstream, and every requested spreadsheet download matches its prepared content hash. The Finish Day procedure must require this publication verification before its final Git synchronization check.

## Explicit Major Website Version Bumps

**Status:** Accepted
**Date:** 2026-07-30

Keep ordinary website publications on the existing automatic minor-version increment. Permit an intentional major-version release only through the supported publication command with `--major-version N`. Require `N` to be an integer greater than the currently published major version, set that release to `N.00`, and resume ordinary minor increments from the new major version. Do not permit a major-version request through an ordinary development build or by using a negative minor-number workaround.

## Preserved Spreadsheet Releases and Git-Tracked Verification Status

**Status:** Accepted
**Date:** 2026-07-30

Preserve compatible spreadsheet downloads during an ordinary website publication instead of removing them. Record a published release manifest containing each workbook family’s revision, source fingerprint, stable filenames, and content hashes. A plain `publish.sh` preserves the exact previously published workbook bytes only when their recorded source fingerprint still matches the current inputs. If relevant Matrix or Setup inputs changed, publication must stop until that family is rebuilt or spreadsheet downloads are explicitly removed. `--matrix-downloads`, `--setup-downloads`, and `--spreadsheet-downloads` deliberately replace selected families; `--remove-spreadsheet-downloads` deliberately removes all workbook downloads. Workbook preparation remains separate from publication.

Show an independent workbook revision, shortened source fingerprint, and generation date inside both workbook families. Do not use the website version as the workbook revision because unrelated website changes increment it. On C1–C3 Registration, apply a three-point project-blue outer border to the complete column ranges `A:A`, `B:E`, `F:I`, and `J:M`.

Keep `90 Testing/eos_r5_verification_status.yaml` as the canonical, non-published, Git-tracked record of mutable testing status. Generate the machine-local Excel/Numbers working tracker from the current definitions plus that status, and import approved mutable workbook fields back into YAML by stable Test ID and registration setting. Keep evidence binaries local; store only their references in YAML. Record definition fingerprints in the working workbook and against verified results. When a test requirement or C1–C3 target changes, preserve prior history and evidence but invalidate affected passes as needing retest. New tests begin unverified, removed tests are archived, and finish-day must refuse to complete while a local working tracker differs from its last YAML synchronization.

This decision supersedes the normal-publish omission/removal behavior in **Opt-In Subject Settings Workbook Downloads** and the machine-local-only status-record portion of **External Spreadsheet Specifications and Setup Master**. The published Setup workbook remains a blank master and must never contain the owner’s testing status.

## External Spreadsheet Specifications and Setup Master

**Status:** Accepted
**Date:** 2026-07-30

Keep reusable spreadsheet presentation and behavior in `00 Master/spreadsheet_layouts.yaml`, not buried in the builders. Keep Setup checklist content, menu access lookups, status lists, and C1–C3 targets in `90 Testing/eos_r5_verification_tracker.yaml`. Both the Subject Settings Matrix and Setup Tracker builders consume these external sources.

Generate a blank Setup master in Excel and Apple Numbers for optional publication. Its Checklist uses the same removable three-band banner pattern as the Matrix, freezes its table header and column A, and keeps Menu Location bold and centered. The Menu sheet is the authoritative workbook lookup for Best Access, Menu Location, and Menu Detail. Configure the approved SWITCH My Menu tab by sequence 4, before shared settings, controls, and C1–C3 registration.

Open the Setup master on Dashboard when the workbook application honors saved active-sheet state. Preserve the Dashboard's formula-driven green Verified, amber pending, and red attention cues; center populated Dashboard columns B–E and H. Center Checklist Status, freeze C1–C3 Registration column A in both formats, and explicitly align the Checklist banner and table left edges. Use `Backup-Settings` as the completed state for checkpoint saves after shared setup/controls and after C1–C3 registration/read-back, in addition to the initial and final configuration saves.

Apply screenshot-matched Completion highlighting in Dashboard column E: 100% uses green text, values above 0% and below 100% use bold black text on pale yellow, and 0% uses italic text. In C1–C3 Registration, right-align column A and center target columns B, F, and J.

Keep any migrated Setup workbook as a separate machine-local working copy and never publish it. Migrate mutable verification state by stable identifiers while regenerating requirements and layout from current sources. Use uniquely named Matrix and Setup scripts, plus a driver for both; retain prior Settings script and flag names only as Matrix compatibility aliases. This decision extends and supersedes the command/file-naming portions of **Opt-In Subject Settings Workbook Downloads**; its publication authorization and readiness safeguards remain binding.

## Recommendation-First Change Approval

**Status:** Accepted
**Date:** 2026-07-28

For every new task that would modify project files, first give the project owner a clear recommendation with its rationale and affected files. Ask for approval as a separate explicit question. The owner's approval authorizes the recommended scope, so the owner does not need to restate the recommendation. Read-only questions and status checks do not require change approval.

## Opt-In Subject Settings Workbook Downloads

**Status:** Accepted
**Date:** 2026-07-29

Provide the complete subject-settings summary in both Excel and Apple Numbers formats as optional website downloads. Keep preparation distinct from publication. The dedicated on-demand spreadsheet script generates the Excel workbook, converts and finalizes the Numbers companion, and verifies both exact files with a machine-local content-hash manifest without running the website build; the interactive preparation script remains as a manual fallback. Only then may the authorized publish workflow use `--settings-downloads`. A publish requested with that option must refuse missing, stale, or changed workbook files. Normal publishing remains unchanged and omits both downloads.

For reliable Excel-to-Numbers transfer, render the title, sorting instructions, and legend as one composite drawing object containing three visual bands. This preserves the three-part presentation while making the entire banner removable with one selection after import. During Numbers verification, remove the import-only rows from the table, position the banner above it, assign and freeze one native header row, and assign and freeze A:C as native header columns. Use 85-point, 80-point, and 80-point widths for columns A, B, and C respectively. Keep A normal and left-aligned, B bold and centered, C bold and right-aligned, and the complete table header row bold. Preserve the sortable Card Order and Rapid Setup Order columns and the frozen row/column settings supported by each format.

Publish stable download filenames under `downloads/` and show separate Excel and Apple Numbers links on the generated index only when the opt-in download flag is used. These files are generated release artifacts, not editable project sources, and publication remains subject to the existing explicit authorization, validation, commit, and push boundary.

## My Menu: SWITCH Starting Tab

**Status:** Accepted
**Date:** 2026-07-28

Use one EOS R5 My Menu tab named **SWITCH** as the approved starting recommendation for transitions from the registered C1-C3 profiles to People, Macro, and Waterdrops. Its formal project name is **My Menu: SWITCH**; the renderer keeps its established green treatment as a visual cue. Register these five shortcuts in order: **Subject to detect**, **Shutter mode**, **Focus bracketing**, **IS (Image Stabilizer) mode**, and **Cropping/aspect ratio**. Leave the sixth position open until physical transition testing identifies another menu-only need.

My Menu provides shortcuts to the camera's real menu settings; it does not store or apply a complete subject profile. Start People from C1 Wildlife, and start Macro or Waterdrops from C3 Landscape, then make the remaining changes through SWITCH, Q, dials, AF-point controls, or physical lens switches as appropriate. Keep **Auto update set.: Disable** so field changes do not rewrite the registered C1-C3 starting environments.

Keep the Camera Buttons card concise with a reference to SWITCH and the linked guide. Put the complete configuration, transition table, and operating rationale in **Custom Controls & Menus, Back-Button AF & Dial Strategies**. Retain on-camera verification and evaluation of any sixth item or additional My Menu tabs as TODO work.

## Screen Information Displays on Camera Setup Essentials

**Status:** Accepted
**Date:** 2026-07-27

Keep **Shooting 7 > Shooting info. disp. > Screen info. settings** modes **1–5 enabled** as the owner-confirmed EOS R5 configuration. Mode 5 provides the full Quick Control screen for quickly reviewing and changing camera settings with **Q**, while **INFO** cycles through the enabled displays.

Show **Screen Info: Modes 1–5 enabled** as a visible Set & Forget setting on Camera Setup Essentials and include the menu path and operating purpose in its notes. Keep this concise setup guidance on the Essentials card rather than creating a separate appendix.

## External Authoritative Reference Links

**Status:** Accepted
**Date:** 2026-07-26

Preserve explicitly authored HTTPS links to authoritative external references in standalone guides, the published site, and the offline/PWA bundle. Open them separately with safe external-link attributes so the installed reference system remains available. Internal Back, Camera Settings, card, appendix, and index navigation must continue to use validated destinations inside the reference system.

This decision supersedes **Shared Internal Web Navigation** only to permit authored HTTPS content references to open an external source. Its internal-navigation, validated-return-target, and browser-history requirements remain binding.

## EFCS Baseline with Mechanical Profile Overrides

**Status:** Accepted
**Date:** 2026-07-26

Use **Electronic 1st-curtain shutter (EFCS)** as the shared EOS R5 shutter baseline. EFCS removes first-curtain mechanical movement, reduces the risk of shutter-shock softness, avoids the major rolling-shutter distortion of fully Electronic shutter, and normally minimizes artificial-light banding while retaining a mechanical second curtain. It is the approved starting point for Camera Defaults, Camera Setup Essentials, Travel, Wildlife, Birds Perched, Landscape, ambient-light or focus-bracketed Macro, and Fireworks. The EOS R5 automatically uses EFCS for Bulb exposures.

Use explicit **Mechanical** shutter overrides for **People**, **Birds in Flight**, **Sports**, and **Waterdrops**. People, Birds in Flight, and Sports frequently combine fast shutter speeds with lenses at or near maximum aperture, where Canon warns that EFCS may render defocused highlights incompletely. Waterdrops retains Mechanical at 1/200 sec. as the conservative starting point for the third-party Pluto trigger and manual-flash workflow. Use Mechanical situationally for other unverified third-party flash/trigger setups and for non-bracketed flash macro. Canon EOS R5 focus bracketing does not support flash.

Canon documents a maximum normal flash synchronization speed of 1/250 sec. with EFCS and 1/200 sec. with Mechanical shutter. Mechanical and EFCS both support approximately 12 fps High Speed Continuous+; in regular High Speed Continuous, Canon specifies approximately 6 fps with Mechanical and 8 fps with EFCS. Fully Electronic shutter remains situational for silence or 20 fps because of rolling-shutter, flicker/banding, and flash restrictions.

This is an owner-approved target and project recommendation based on Canon-documented EOS R5 behavior and the project’s profiles and owned lenses. It is not an owner-confirmed current camera configuration or a completed physical comparison. Retain the physical verification task for shutter shock, EF 50mm f/1.4 fast-shutter bokeh, artificial lighting, burst behavior, and the Pluto/manual-flash setup.

Show **Shutter Type** on every merged profile-based camera-settings card, including Camera Setup Essentials, so the inherited EFCS baseline and Mechanical profile exceptions remain visible in the field. Do not add it to permanent reference cards such as Camera Buttons, and do not duplicate the baseline value in profile YAML.

## Retire Native iOS Wrapper

**Status:** Accepted
**Date:** 2026-07-26

Retire the native iOS wrapper and its Xcode/Swift project, Python wrapper automation, XCTest harness, native-resource staging path, `build ios` target, and supporting documentation. The responsive HTML/PWA and GitHub Pages output provide the required iPhone experience, including Add to Home Screen and offline caching, without maintaining a second native application shell.

Keep `build website` as independent optional staging for other web hosts. This decision does not uninstall system-wide Apple Command Line Tools or Swift because they are machine-level developer tools and are not dependencies of the remaining reference-system build.

## Full-Frame Crop Baseline and Situational 1.6× Override

**Status:** Accepted
**Date:** 2026-07-26

Keep **Cropping/aspect ratio: Full-frame** as the shared baseline and show it on Camera Setup Essentials as a Set & Forget setting. Do not make 1.6× crop a permanent override in any subject profile. Use it temporarily for distant birds, wildlife, or sports only when the subject will predictably remain within the smaller capture area and tighter viewfinder framing provides a practical advantage. Restore Full-frame after the session. With C1-C3 Auto update disabled, retain this as a temporary field change rather than silently replacing a registered subject setup.

On the EOS R5, Full-frame records approximately 44.8 megapixels at 8192×5464, while 1.6× crop records approximately 17.3 megapixels at 5088×3392. The reduced pixel count generally produces smaller files, although actual file size varies with image quality and subject content. Crop mode does not add optical magnification or capture more subject detail than cropping the same full-frame image later, and the excluded area is not recoverable from a RAW file.

RF-S and adapted EF-S lenses force 1.6× crop automatically and do not offer Full-frame while attached. RF and adapted EF lenses do not force crop mode. This behavior and the recorded pixel counts are verified Canon capabilities; using Full-frame as the project baseline and 1.6× as a situational override is a project recommendation, not an owner-confirmed physical camera setting.

## Evaluative Metering Baseline and Situational Alternatives

**Status:** Accepted
**Date:** 2026-07-25

Keep **Evaluative metering** as the shared baseline. No documented subject profile requires a metering override.

Evaluative is the most reliable starting point across general photography, people, wildlife, birds, sports, travel, landscape, and ambient-light macro because subjects may be off-center and backgrounds or lighting may change. For bright sky, snow, dark backgrounds, backlighting, and other difficult scenes, retain Evaluative and use exposure compensation, the RGB histogram, the highlight alert, or bracketing as appropriate.

Keep **Partial** and **Spot** as deliberate situational tools. On the EOS R5 they meter approximately 6.1% and 3.1% of the screen center, respectively; Spot metering does not follow the active AF point. Partial can reduce the influence of a much brighter background when the important subject is deliberately placed under the center metering area. Spot is for intentional measurement of a specific tone and normally requires compensation when that tone is not a middle tone. **Center-weighted average** remains available for a consistently centered composition but offers no repeatable profile-wide advantage over Evaluative for the documented subjects.

In Fireworks and Waterdrops, the inherited metering selection does not determine capture exposure because those profiles use Manual exposure with fixed ISO; use the documented histogram, highlight, flash-power, and test-frame guidance instead.

This is a project recommendation based on Canon-documented EOS R5 behavior and review of the documented profiles and representative lighting conditions. It is not an owner-confirmed physical camera test.

## Five-Class Evidence Model and Canonical Camera Terminology

**Status:** Accepted
**Date:** 2026-07-24

Use five explicit evidence classes in camera-control records: **verified Canon capability**, **owner-confirmed current configuration**, **approved target pending physical verification**, **project recommendation**, and **unresolved item**. An approved target is an owner-approved setup instruction but must not be described as physically current until it is verified on the camera. Any record-level current-state label applies only to entries explicitly marked owner-confirmed, not to approved targets in the same file.

Use **One-Shot AF** and **Single Shot** as the canonical project values. C1, C2, and C3 machine-readable mappings identify their source cards by exact canonical profile title: `Wildlife`, `Birds in Flight`, and `Landscape`. Optional field labels may remain **General Wildlife**, **Birds in Flight / Action**, and **Landscape**. Validate the duplicated control records against each other and verify that every mapped profile exists.

The Sports profile starts with People detection. Vehicles is a situational change for vehicle-based sports, not a separate profile.

## Official Canon Physical-Control Icons on Camera Buttons

**Status:** Accepted
**Date:** 2026-07-25

Display the official Canon EOS R5 physical-control icon beside each control name on the Camera Buttons reference card. Use Canon's documented button and dial SVGs for Shutter half-press, AF-ON, AE Lock, AF Point Selection, Lens AF, SET, DOF, Joystick, Main Dial, Rear Wheel, Top Rear Dial, Control Ring, and M-Fn. Map the project's plain physical names to Canon's corresponding controls: Rear Wheel is Quick Control Dial 1, Top Rear Dial is Quick Control Dial 2, and Joystick is the Multi-controller.

Icons identify the physical control, not the assigned function. Keep the authored control text and row order, use stable control-name renderer keys, and do not fabricate fallbacks. This styling applies to the Camera Buttons reference card without changing other card content or control assignments.

## Transparent AF Point Button Card Treatment

**Status:** Accepted
**Date:** 2026-07-25

The official Canon AF point button SVG contains an opaque white button face that does not survive the card's standard monochrome color treatment cleanly. Preserve that official SVG unchanged in the Canon icon reference. For the Camera Buttons card, use a geometry-preserving derivative that removes only the opaque background fill and retains Canon's button outline and AF-point marks. Apply the same standard card icon color used by the other physical controls, with no special black background or one-off color.

This decision supersedes **Official Canon Physical-Control Icons on Camera Buttons** only for the AF point button's card presentation; the official Canon geometry, physical-control meaning, and source-reference requirements remain in force.

## Owner-Confirmed M-Fn Custom-Mode Switching

**Status:** Accepted
**Date:** 2026-07-25

Assign **M-Fn** to Canon's **Switch to Custom shooting mode** function. The project owner physically tested the assignment and confirmed that repeated presses switch among C1, C2, and C3.

The switching function is owner-confirmed, but the registered mode contents retain separate evidence states. C1 contains registered settings, although its match to the complete Wildlife profile remains pending verification. C2 and C3 do not yet contain their target registrations. Do not describe all three profile implementations as current merely because M-Fn can select their mode positions.

This decision supersedes the unresolved M-Fn portions of **Owner-Confirmed Eye Priority and AF-Point Position Controls**, **Subject-Profile Custom Modes and Tracking/Precision AF Buttons**, and **Owner-Confirmed EOS R5 Button and Dial Architecture**.

## Owner-Confirmed Eye Priority and AF-Point Position Controls

**Status:** Accepted
**Date:** 2026-07-25

The project owner physically configured and verified **AF-ON** as Metering and AF start with AF Operation set to Maintain current setting, AF Method set to Face + Tracking, and Servo AF characteristics set to Maintain current setting. AF-ON honors the stored Eye Detection state.

Assign **SET** to **Eye detection**. SET toggles the stored Eye Detection Enable/Disable state when the active AF method supports Eye Detection. The state persists when switching between Face + Tracking and deliberate-point AF methods, and AF-ON uses the stored state when it invokes Face + Tracking. SET has no effect while 1-Point AF or Spot AF is active because those methods cannot use Eye Detection. The AF Point Selection button followed by INFO remains a slower context-sensitive Eye Detection toggle when Face + Tracking is active.

**AE Lock** remains Metering and AF start with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to 1-Point AF. Its 1-Point position is the last position used; AE Lock does not automatically recenter it. The joystick directly moves the AF point or starting position, and pressing the joystick straight in recenters it.

This decision confirms the AF-ON target in **Subject-Profile Custom Modes and Tracking/Precision AF Buttons** and supersedes the SET and joystick assignments in **Owner-Confirmed EOS R5 Button and Dial Architecture**. C1-C3 remain approved targets pending physical verification, and M-Fn remains unresolved.

## Appendix Index Return Navigation

**Status:** Accepted
**Date:** 2026-07-24

Appendices with a front **Index**, **Topic Index**, or **Table of Contents** provide a persistent **Return to index** control both on standalone generated pages and inside their expanded panel on the main index. Keep the control out of print/output rendering. Embedded appendix heading IDs and internal fragment links are namespaced per appendix so links cannot land in a different expanded guide with the same heading ID. Anchor destinations must include enough scroll offset for the sticky Camera Settings header so the destination heading remains visible rather than being covered by the header.

## Subject-Profile Custom Modes and Tracking/Precision AF Buttons

**Status:** Accepted
**Date:** 2026-07-24

Use C1, C2, and C3 as fast camera-side implementations of complete subject cards:

- **C1 — Wildlife** (field label: General Wildlife)
- **C2 — Birds in Flight** (field label: Birds in Flight / Action)
- **C3 — Landscape**

The selected profile or custom mode establishes the shooting environment, including its initial AF Operation, Subject Detection, Eye Detection, exposure, drive, and other subject-specific settings. Subject Detection belongs to the profile, not to a physical focusing button.

Keep the two rear AF-start buttons constant across profiles. **AF-ON** starts metering and AF while maintaining the current AF Operation and Servo AF characteristics and temporarily selecting **Face + Tracking** for intelligent subject acquisition. **AE Lock** starts metering and AF while maintaining the current AF Operation and Servo AF characteristics and temporarily selecting **1-Point AF** for precise point placement. The **DOF button** remains the One-Shot AF ↔ Servo AF control; because both AF-start buttons maintain AF Operation, they respect the profile state and any DOF-button change.

AF-ON always selects the subject-aware tracking method, but continuous focus updating occurs only when the current AF Operation is Servo AF. Subject Detection and Eye Detection menu values remain profile settings; they are not used by the 1-Point AF precision override. Spot AF and Expand AF Area remain deliberate situational alternatives selected manually when they provide a measurable advantage.

The Deep Dive is the primary explanation of this operating philosophy. The Camera Buttons card remains concise. Owner-confirmed-current records must distinguish settings physically verified on the camera from this approved target configuration until the new AF-ON detail and C1-C3 registrations are confirmed on the camera.

This decision supersedes the AF-ON AF Method and unresolved C1-C3 portions of **Owner-Confirmed EOS R5 Button and Dial Architecture** (2026-07-23). Its remaining physical layout, dial assignments, evidence boundaries, default-button choices, M-Fn status, and documentation placement remain in force.

## Owner-Confirmed EOS R5 Button and Dial Architecture

**Status:** Accepted
**Date:** 2026-07-23
**Superseded in part by:** Subject-Profile Custom Modes and Tracking/Precision AF Buttons (2026-07-24), for AF-ON AF Method and C1-C3 only

Use one owner-confirmed physical button and dial layout across the baseline and all subject profiles. AF-ON starts metering and AF with AF Operation, AF Method, and Servo AF characteristics set to Maintain current setting. AE Lock starts metering and AF while overriding only AF Method to 1-Point AF. This gives one normal AF-start button and one precise AF-start button.

Keep the concise Camera Buttons card limited to assignments and a link to the detailed guide. Put AF-ON and AE Lock INFO details, operating explanation, and subject-profile examples in **Custom Controls & Menus, Back-Button AF & Dial Strategies**, not R5 Quick Reference. Use the plain physical labels **Main Dial**, **Rear Wheel**, **Top Rear Dial**, and **Control Ring**. Leave Movie Record, MODE, and LCD panel illumination at their defaults. M-Fn and the contents of C1-C3 remain unresolved for later review.

This decision supersedes prior screenshot-derived claims about the current control configuration. Historical screenshots are not current-state evidence.

## Frequency-Oriented Index Sections

**Status:** Accepted
**Date:** 2026-07-22

Order the published index sections by expected frequency of use: **Subjects**, **Field Guides**, **Camera Setup & Controls**, then **Deep Dive**. Rename the user-facing **Reference Cards** section to **Camera Setup & Controls** so its label describes Camera Buttons, Camera Defaults, and Camera Setup Essentials while remaining distinct from the R5 Quick Reference Field Guide.

This decision supersedes the published section label and ordering portions of **Independent Card Display Categories**, the user-facing section label in **Permanent Reference-Card Type**, and the prior published section ordering implied by **Setting Deep Dives**. The `display_category: reference` value and reference-card data/rendering behavior remain unchanged.

## Date-Only Version Header

**Status:** Accepted
**Date:** 2026-07-19

Display the published version and publication date in the shared header without the publication time. Preserve the full timezone-aware publication timestamp in metadata for publishing and cache behavior; only the user-facing header format changes.

## Appendix Consolidation and Deep-Dive Promotion

**Status:** Accepted
**Date:** 2026-07-19

Use **R5 Quick Reference** as the single concise reference for metering modes, drive modes, shutter types, general stabilization, basic flash choices, and AF tracking terminology. Remove the separate Metering Modes, Drive Modes, Electronic vs EFCS vs Mechanical Shutter, Image Stabilization, and Custom Controls manifest entries after preserving their useful guidance in R5 Quick Reference, Lens Capabilities, or the expanded custom-controls guide.

Promote AF Cases & Tracking Behavior, Flash Photography, and Long Exposure & Night Photography to released Setting Deep Dives. Consolidate general custom-control guidance into **Custom Controls & Menus, Back-Button AF & Dial Strategies**. Preserve the incomplete Canon EOS R5 Custom Controls Current Configuration source without deciding its eventual disposition. Keep the Canon EOS R5 Official Icon Reference generated and available offline as an unreleased supporting reference linked directly from R5 Quick Reference, rather than listing it as a primary Field Guide.

## Independent Card Display Categories

**Status:** Accepted
**Date:** 2026-07-18

Separate index placement from card rendering behavior. Profiles may use `display_category: subject|reference` and integer `display_order`; category defaults from `card_type`, order defaults to `100`, lower values appear first, and ties sort alphabetically. This allows baseline-driven operational cards to appear under **Reference Cards** without converting them to permanent reference-card data. Label the published sections **Subjects**, **Reference Cards**, **Field Guides**, and **Deep Dive**.

This decision supersedes the index-placement restriction in **Permanent Reference-Card Type** and the published section labels in **Setting Deep Dives**; their remaining requirements stay binding.

## Opt-In PNG Card Exports

**Status:** Superseded
**Date:** 2026-07-17

Responsive HTML is the default and primary card output. Fixed PNG cards remain available from the same merged baseline-plus-overrides data, but generation and publication are opt-in with `--png`. A normal build or publish omits PNG cards and PNG index actions. PDF generation remains independently opt-in and may use the fixed renderer internally without retaining PNG files.

## Shared Internal Web Navigation

**Status:** Accepted
**Date:** 2026-07-17

Use one safe-area-aware Camera Settings header on the published index, responsive cards, Field Guide appendices, Setting Deep Dives, and generated reference pages. Standalone content pages provide a real internal Back destination and a centered Camera Settings link to the index. Appendix links from cards and links between generated appendix pages supply a validated internal return target; invalid or absent targets fall back to the index. Do not depend on browser history or navigate outside the reference system.

## No GitHub CLI

**Status:** Accepted
**Date:** 2026-07-17

Do not install or use the GitHub CLI (`gh`) for this project. Preserve the established workflow: use local `git` commands for authorized staging, commits, and pushes, and use `80 Build/scripts/publish.sh` only when website publishing is explicitly authorized. Introducing another GitHub workflow or dependency requires separate project-owner approval.

## Responsive HTML as Primary Published Card Format

**Status:** Accepted
**Date:** 2026-07-17

Publish released camera cards as responsive standalone HTML pages optimized for iPhone safe areas and readable browser text. Make each HTML card the primary action on the Camera Settings index and publish required card icons through generated relative asset paths. The later **Retire Fixed Card PNG Exports** decision supersedes this entry's former fixed-PNG clauses; the responsive HTML requirements remain accepted.

## Explicit Approval Before Git Branch Changes

**Status:** Accepted
**Date:** 2026-07-16

Before creating or switching to a Git branch, explain its purpose, risks, additional workflow and cleanup steps, and whether direct work on `main` is appropriate for the approved change. Obtain explicit project-owner approval before creating or switching branches. Do not introduce a separate branch automatically merely because it is a common precaution.

## External Machine-Local Workspace and Computer Handoffs

**Status:** Accepted
**Date:** 2026-07-16

Keep disposable build output, build reports, native-wrapper generated resources, and pre-change recovery backups in a sibling machine-local workspace rather than in the Git repository. Keep `docs/` in the repository because GitHub Pages publishes from `main / docs`. Allow `PRS_LOCAL_WORKSPACE` to override the default sibling location when necessary.

Work started on one computer must reach a clean pushed Git checkpoint before it continues on another computer: validate, commit all intentional source changes, push the current branch, and verify the working tree is clean. This handoff is not a release and does not require running the publishing workflow. Publishing remains a separate, explicit action that updates the live site, version, and timestamp.

## Manifest-ID Internal Links

**Status:** Accepted
**Date:** 2026-07-16

Reference Field Guide content by stable IDs from `50 Field Guide/required_appendices.yaml`. Profiles use `appendix_links`; Markdown sources use the `appendix:` link scheme. Build renderers resolve IDs into context-appropriate paths, and validators reject missing IDs. Generated-output locations must not be stored in source content.

## Permanent Reference-Card Type

**Status:** Accepted
**Date:** 2026-07-16

Represent permanent operational references with `card_type: reference`. Reference cards remain in the card source collection but do not inherit the shooting baseline, define overrides, or render a Settings section. Released reference cards appear in a separate **Reference Cards** section rather than among subject profiles. Existing cards default to `card_type: profile` for backward compatibility.

## Documentation Governance Consolidation

**Status:** Accepted
**Date:** 2026-07-11

Use `PROJECT_RULES.md` as the concise governing entry point; separate detailed architecture, profile, card, appendix, asset, and build/validation requirements under `00 Master/specifications/`; retain project memory for stable context; and use this status-based decision log. This decision supersedes the former combined-specification arrangement.

## Setting Deep Dives

**Status:** Accepted
**Date:** 2026-07-12

Add Setting Deep Dives as a first-class Field Guide content type for focused guidance about individual camera settings and tightly scoped features. Store these sources under `50 Field Guide/Setting Deep Dives/` and identify them with `content_type: setting_deep_dive` in the appendix manifest. Existing entries default to `field_guide` for backward compatibility.

Generate all manifest entries so draft content remains linkable from released documentation. Use `release: true` only to control whether an entry appears in the published index: released Field Guides appear under **Field Guide**, and released Setting Deep Dives appear under **Setting Deep Dives**.

## Lens Stabilization Guidance

**Status:** Accepted
**Date:** 2026-07-27

Keep normal EOS R5 stabilization guidance in R5 Quick Reference and lens-specific physical-control guidance in Lens Capabilities. Store verified camera and lens stabilization capabilities in `data/stabilization_reference.yaml`, and generate each lens's stabilization-control table from that structured source.

Document optical IS presence, physical Image Stabilizer On/Off and mode switches, only the modes supported by the specific lens, Canon's purpose for each supported mode, the controlling device, automatic lens/body coordination, and Canon-stated exceptions. Retain the exact `IS (Image Stabilizer) mode` camera-menu label because the Shooting-menu page number and availability are conditional.

This structured appendix data does not change the profile schema. The existing separation of stabilization mode, IBIS, and Lens IS remains binding through the Profile Specification, and IBIS High Resolution Shot remains outside this lens-control guidance.

## Phase 4 — User Experience

**Status:** Proposed (non-binding)
**Date:** 2026-07-05

Potential command-line improvements:

- `python build.py --search ISO` to list profiles that reference or inherit matching settings.
- `python build.py --compare Wildlife Sports` to show differences between resolved profiles.
- A changed-profiles-only build based on profile, baseline, asset, and build-input dependencies.

The existing `python build.py Fireworks` single-profile behavior remains documented in the Build and Validation Specification; this proposal does not authorize the other features.

## Phase 5 — Documentation

**Status:** Superseded
**Date:** 2026-07-05
**Superseded by:** Documentation Governance Consolidation (2026-07-11)

The proposal anticipated permanent architecture, profile, asset, and build documentation. The accepted consolidation implements and expands that documentation set.

## Card Visual Format

**Status:** Proposed (non-binding)
**Date:** 2026-07-05

Future card design could move closer to the original reference-card format: white main content, colored headers/section bars, possible profile-specific header colors after deciding the data model, top icons, retained pale-blue setting icons, and closer original proportions.

Any implementation requires a separately Accepted styling decision and coordinated renderer/documentation changes. Existing formats, paths, filenames, YAML, and workflow remain unchanged meanwhile.

## Macro Guidance Expansion

**Status:** Proposed (non-binding)
**Date:** 2026-07-05

Potential staged content work:

- Phase 1: EOS R5 focus bracketing/stacking, manual focus and magnification, peaking, stabilization at macro distances, flash/ambient light, support tradeoffs, depth of field, and diffraction.
- Phase 2: Canon MP-E 65mm, StackShot/automated rail workflow, high magnification, lighting, vibration control, and stacking.

This is guidance/profile content work only unless a later Accepted decision changes YAML or build behavior.
