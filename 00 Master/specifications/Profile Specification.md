# Profile Specification

## Scope

This specification governs subject/profile YAML under `10 Profiles/`.

## Requirements

- Every profile inherits `baseline`.
- A profile contains only values that differ from `00 Master/baseline.yaml`; it must not repeat baseline values.
- Overrides must use paths present in `baseline.defaults` and compatible value types.
- Profile data retains camera concepts as separate fields, including ISO mode, fixed ISO value, Auto ISO maximum, Servo AF Case, Tracking Sensitivity, Accel./Decel. tracking, Switching tracked subjects, stabilization mode, IBIS, Lens IS, and High speed display.
- Profiles contain shooting settings and concise field-use content, not duplicated educational explanations. Reference applicable appendices instead.
- Preserve existing profile filenames, titles, YAML structure, data, and backward compatibility unless explicitly approved.
- `metadata.release: true` selects the profile/card for the offline iPhone/PWA bundle. Absence or false does not select it.

## Read-Only Baseline Impact Draft

The local editor may load the current baseline into a session-only draft and analyze proposed value changes against every inheriting profile. This analysis must use the repository-owned baseline impact engine and report inherited effective-value changes, values protected by existing overrides, overrides made redundant by the proposed baseline, removed override paths, and incompatible override types.

The draft may change values only for existing baseline setting paths. The server must reject missing paths, additional paths, and values incompatible with the current baseline type. Reloading the browser discards the draft. Baseline impact analysis does not create a review token and must not write the baseline, profiles, generated output, or any other project file.

The editor may turn an analyzed draft into a read-only migration plan. The migration-plan action must be available both above the impact report and after its setting-preference controls so the user does not need to scroll back to the first action. Every inherited profile-setting change requires an explicit `follow_baseline` or `preserve_previous` choice. A preserve choice proposes a new override equal to that profile's previous effective value; a follow choice proposes no override. Newly redundant overrides are proposed for removal, and protected overrides are retained. Missing choices and invalid overrides keep the plan incomplete and must remain visible as unresolved items.

The server must recompute the impact from the complete draft and current session My Menu configuration and validate every submitted choice against it. It must reject stale, duplicate, invalid, ambiguous, and inapplicable choices. Bulk choices may fill only unresolved inherited changes. Every displayed configured My Menu setting that lacks an authored card cue must be included automatically as a planned profile change naming the profile, setting path, unique configured tab, and target `card.field_setup.my_menus` location. The plan must describe these as color-coding existing card rows for My Menu access and state that they add neither setting rows to cards nor items to the camera's My Menu. Migration planning remains session-only and read-only: it produces no YAML diff, review token, save token, or write endpoint.

### C1–C3 Impact Warnings

Baseline impact analysis must also calculate effective before-and-after values for the canonical **C1 Wildlife**, **C2 Birds in Flight**, and **C3 Landscape** registrations defined in `90 Testing/eos_r5_verification_tracker.yaml`. The report must include every proposed baseline setting path for all three modes and distinguish values that change with the baseline from values protected by an explicit registration entry.

For each registered mode whose effective value changes, the report must warn about every shooting profile whose `card.field_setup.start` declares that C-mode. Each warning identifies the profile, declared source profile, and affected settings. This stage is advisory only and must not modify C1–C3 registration definitions, profile starting-mode metadata, source-profile declarations, My Menu routes, baseline values, or profile overrides.

### My Menu Card-Coverage Warnings

Baseline impact analysis must inspect the fully merged rows displayed by each profile card against the current session-only My Menu draft. The profile editor's Canon options catalog must provide an explicit, unique setting-path identity for each supported My Menu item; label matching is not sufficient.

My Menu is a stable fast-access configuration, not a transition recipe. Matching a C1–C3 starting value must not make a shortcut unnecessary. For both the current and proposed baseline, the engine must use the card renderer's conditional visibility rules to determine whether each declared route setting is displayed. The report must show whether its identified Canon item is available in the named configured tab and whether a displayed configured shortcut lacks a card cue. A cue gap introduced because a conditional row becomes visible after the proposal must be identified as newly visible.

The report must include access-only profile cards and exclude permanent reference cards. A card tab assignment with no displayed settings is informational and is omitted from that rendered card; it is not a recommendation to remove the shortcut from My Menu. The only possible removal candidates are configured shortcuts whose setting is not displayed on any card. Findings are warnings only and must not mutate the browser's My Menu draft, C1–C3 registrations, baseline data, profile routes, or profile YAML. Editing or restoring the session My Menu draft invalidates an existing coverage report and requires a new analysis.

## Guarded Local Editor Transactions

The local loopback profile editor may perform only these writes under `10 Profiles/`:

- update the title, optional subtitle, metadata status, release flag, and baseline overrides of an existing shooting profile without renaming its file;
- create a new baseline-derived shooting profile; or
- duplicate an existing shooting profile into a new file.

Reference cards, the shared baseline, My Menu persistence, profile deletion, and every non-profile source remain read-only. New and duplicated profiles must begin as `Draft` with `metadata.release: false`.

Every editor save must follow one guarded transaction:

1. Validate structured input and remove overrides equal to the baseline.
2. Confirm the source fingerprint and target-name availability.
3. Build and validate the complete candidate in an isolated temporary source layout.
4. Show the exact YAML diff and bind those candidate bytes to a short-lived one-time review token.
5. Reconfirm source and target state immediately before saving.
6. Create a timestamped recovery backup under the designated machine-local `Backups/` directory.
7. Replace the profile atomically and run source validation.
8. Restore the prior source state automatically if post-save validation fails.

The editor does not build, commit, push, publish, rename, or delete. Those remain separate operator-authorized workflows.

## Expected Structure

Profiles use the existing keys documented by `00 Master/schema.yaml`, including `metadata`, `title`, optional `subtitle`, `inherits`, `overrides`, and optional list content such as `checklist`, `watch_for`, `common_mistakes`, and `notes`.

## Enforcement and Evidence

- `00 Master/baseline.yaml` defines valid shared default paths and their effective types.
- `00 Master/schema.yaml` documents profile field structure.
- `80 Build/validators/profile_validator.py` enforces required keys, `inherits: baseline`, override paths/types, title uniqueness, and list shapes.
- `80 Build/validators/yaml_validator.py` rejects malformed or duplicate-key YAML.
- `80 Build/validators/profile_editor_validator.py` verifies editor readiness, source fingerprints, read-only reference-card behavior, unreleased-draft defaults, and complete My Menu setting identities for declared routes.
- `80 Build/test_profile_editor.py` exercises guarded update, create, duplicate, conflict, rollback, reference-card boundaries, and session My Menu availability analysis in temporary repositories.
- `80 Build/baseline_impact.py` provides deterministic, read-only profile comparison, C1–C3 registration and starting-route warnings, My Menu card-coverage analysis, and validated migration planning for current and proposed baseline values.
- `80 Build/test_baseline_impact.py` covers inherited choices, protected and redundant overrides, C1–C3 effective values, visible-card My Menu coverage and availability, newly visible cue gaps, globally unreferenced configured shortcuts, invalid paths and types, stale-decision rejection, reference-card exclusion, and input immutability.
- Build and PWA code under `80 Build/` implements merging and release filtering; generated-output and PWA validators provide integration evidence.

The profile validator rejects an override when its value equals the baseline, enforcing the baseline-plus-overrides no-duplication rule.
