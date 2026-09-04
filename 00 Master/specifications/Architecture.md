# Architecture

## Scope

This specification defines the system boundaries and ownership of data, content, rendering, and generated artifacts. Governance and precedence are defined in [`PROJECT_RULES.md`](../../PROJECT_RULES.md).

## Requirements

- The Git root is the only authoritative source root for a task. Resolve it at runtime; do not select another repository or sibling copy automatically.
- `00 Master/project_identity.yaml` identifies this repository as the authoritative Canon EOS R5 source project. Its camera identity must agree with `00 Master/baseline.yaml`.
- Reject roots or parent folders marked as old, backup, archive, build output, generated output, or native wrapper locations. Reject incomplete or generated-only roots and stop for project-owner direction rather than searching for a substitute.
- Required source components, Git-root identity, current-working-directory containment, prohibited path markers, and camera identity are source-validation requirements.
- Preserve the established baseline + overrides architecture and existing YAML structure.
- The accepted target architecture separates reusable application source, an owner's application fork, and an independently owned private profile pack. [`Profile Pack Specification.md`](Profile%20Pack%20Specification.md) is authoritative for pack identity, ownership, compatibility, selection, privacy, publication, and migration requirements.
- The application repository's `origin` is the owner's repository and remains the only ordinary application push destination. A separately configured shared upstream is an explicit inbound source of selected reusable improvements; no workflow may infer permission to push to it.
- The target private pack is a separate private Git repository, not a Git submodule. It is composed with the application at build and runtime through one validated source resolver.
- Until source migration activation and broader external-pack workflows are separately approved, the current Git root remains the application authority and embedded compatibility sources remain available. The development build and general validator may compose one explicitly selected external pack for isolated parity review. Profile Editor Step 4C may use either an explicit or machine-local saved pack, switch among remembered packs and embedded sources after draft/confirmation checks, and perform guarded reviewed transactions only against the active pack's manifest-owned sources. Steps 5A–5B pass that exact context into Camera Lab for scan, comparison, guarded simulation, and explicitly enabled physical-camera operation. Step 5C lets Profile Editor deliberately promote exact completed physical-camera evidence into the pack-owned verification status. Step 6A may create, validate, register, and select a new external pack containing a migrated copy of the unchanged embedded owner sources. Step 6B permits only separately reviewed Git actions in that pack and read-only combined handoff checks across the application and pack. Camera Lab direct pack-source writes, editor-initiated build, cleanup, application Git mutation from the external session, spreadsheet-generation, main-editor launch, and publication workflows remain unavailable.
- Every profile and permanent reference card has an immutable canonical `card_id` UUID. Structured card relationships store UUIDs rather than mutable titles; editors and renderers resolve the current title for display. Existing cards use the documented deterministic migration and new or duplicated cards receive new UUIDs.
- Distinguish five evidence classes in camera-control documentation: verified Canon capability, owner-confirmed current configuration, approved target pending physical verification, project recommendation, and unresolved item.
- Do not treat approved targets, historical screenshots, inferred icon meanings, or recommendations as proof of the current camera configuration.
- Explain the rationale and obtain explicit project-owner approval before changing an established architecture.
- Present proposed changes and affected files for review before modifying the reference.
- For each new change task, present a clear recommendation, rationale, and affected files, then request approval as a separate explicit question. Once approved, treat that recommended scope as authorized without requiring the project owner to repeat it. Read-only questions and status checks do not require change approval.
- Shared behavior and shared camera settings belong in `00 Master/baseline.yaml`.
- Baseline/profile impact classification belongs to the shared repository module `80 Build/baseline_impact.py`, not exclusively to the local browser UI. Both guided and command-line review paths must call that engine rather than reimplement its rules.
- `80 Build/baseline_impact_check.py` is the read-only repository boundary for detecting semantic worktree baseline-default changes relative to `HEAD` or another explicit Git ref. It reports impact and directs semantic changes to the guarded Profile Editor migration; it must not write source, generated output, Git state, or publication state.
- The operational baseline and Camera Defaults card are the general-purpose starting state: Fv with shutter and aperture on Auto, Servo AF with Case A (Auto), Tracking Sensitivity and Accel./Decel. tracking on Auto, Switching tracked subjects set to On subject, Face + Tracking, Animals, Eye Detection enabled, High Speed Continuous, High speed display enabled, EFCS, and Mode 1 stabilization. Registered C1 Wildlife intentionally overrides only its specialized Servo Case values; neutral, deliberate-point, static, manual-focus, or other specialized profiles express their differences as overrides.
- Subject profiles inherit the baseline and contain only necessary overrides.
- The build resolves baseline and profile data before rendering.
- Presentation and rendering decisions belong in build code and templates, not profile YAML.
- `00 Master/my_menu_colors.yaml` owns the curated card-color palette and named My Menu tab assignments. These project presentation settings are global and must not be duplicated in profiles or treated as proof of the physical camera's tab configuration.
- `00 Master/my_menu.yaml` owns the approved EOS R5 My Menu tab names and ordered item identities. It is separate from presentation colors and from proof of the physical camera's current state.
- `00 Master/feature_interactions.yaml` is the canonical source for reviewed Canon feature interactions and conditional menu behavior. Each rule records explicit setting conditions, effects, evidence classification, user-facing guidance, surfaces, and Canon sources. Equipment-dependent rules declare required context and remain unmatched when that context is absent; consumers must never infer attached-lens, flash, or other physical state.
- `data/stabilization_reference.yaml` is the canonical owned-lens, control-ring adapter, extender, and stabilization-capability catalog. `00 Master/profile_lens_guidance.yaml` maps subject cards to one primary and up to two realistic alternative or specialist choices by immutable card and equipment IDs. These are field recommendations, not evidence of the attached lens. Renderers resolve display names and compatibility from the catalogs rather than duplicating lens guidance in profile YAML.
- Explanatory and educational content belongs in field-guide appendices; profiles reference it rather than duplicate it.
- Permanent reference cards remain separate from shooting profiles.
- A permanent reference card may declare `reference_source: my_menu`; its rows are derived from `00 Master/my_menu.yaml` and the Canon settings catalog at render time so persisted My Menu content is not duplicated in profile YAML.
- The physical button and dial layout is shared across subject profiles.
- Subject profiles define complete shooting environments. C1, C2, and C3 are camera-side implementations of the canonical `Wildlife`, `Birds in Flight`, and `Landscape` profiles rather than independent AF presets. Field labels such as **General Wildlife** and **Birds in Flight / Action** may describe use, while machine-readable mappings retain immutable card UUIDs and resolve current titles for display.
- Active profiles, control records, Field Guides, workflows, and verification material must not describe the retired **Switch to registered AF function**, registered-AF behavior/override, AF-preset, or Register/Recall Shooting Function workflow. Use the current constant-control model: AF-ON temporarily selects Face + Tracking, AE Lock temporarily selects 1-Point AF, both maintain the current AF Operation and Servo AF characteristics, and C1-C3 are complete registered shooting environments. Governance/history and literal official-Canon reference material may retain those terms when clearly non-operational.
- The selected profile owns the initial AF Operation, Subject Detection, Eye Detection, exposure, drive, stabilization, and other subject-specific settings.
- AF-ON and AE Lock keep constant focusing roles across profiles. AF-ON temporarily selects Face + Tracking for intelligent acquisition; AE Lock temporarily selects 1-Point AF for precise placement. Both maintain the current AF Operation and Servo AF characteristics.
- The DOF button remains the One-Shot AF ↔ Servo AF control. AF-ON and AE Lock must not force an AF Operation that would defeat the selected profile state or a DOF-button change.
- Subject Detection belongs to the profile, not to either AF-start button. A deliberate-point AF method may make Subject Detection or Eye Detection inapplicable without changing their stored profile values.
- Servo AF Case, Tracking Sensitivity, and Accel./Decel. tracking belong to the shooting profile. Case A (Auto) with both parameters on Auto is the shared baseline. Case 1 is configured once as the project preset at Tracking Sensitivity -1 and Accel./Decel. tracking +1; Wildlife, Birds Perched, and Sports select it. This is not Canon's factory Case 1 default of 0 / 0. Birds in Flight uses Case 4 at 0 / +1. The stored Case and parameters are inactive in One-Shot AF and Manual Focus.
- Switching tracked subjects is a separate profile-owned subject-selection setting. On subject is the shared baseline. It is meaningful with Face + Tracking, Zone AF, and Large Zone AF and is omitted from cards whose effective AF Method does not support it.
- High speed display is a shared set-and-forget display preference. Enable is the approved baseline target; cards show it only when the effective starting configuration uses regular High Speed Continuous or Electronic shutter.
- Preserve the established build workflow, output locations, release behavior, rendering behavior, and backward compatibility unless an explicitly Accepted decision changes them.

## System Flow

Current active flow:

```text
baseline.yaml + profile overrides
        -> merged profile data
        -> machine-local cards / guide / web-PWA outputs
        -> docs (GitHub Pages mirror)
        -> optional machine-local website staging
```

Explicit Step 3A/3B development-review flow:

```text
owner's application checkout + explicitly selected external profile pack
                              -> combined source validation
                              -> validated resolved source set
                              -> pack-ID-namespaced machine-local cards / guide / web-PWA
                              -> isolated machine-local Pages review
                              -> combined generated-output validation
```

Step 4C guarded-editor selection flow:

```text
owner's application checkout + explicit or machine-local saved profile pack
                              -> centralized identity and compatibility resolution
                              -> live manifest-name chooser and confirmed switching
                              -> pack-namespaced previews and exact reviews
                              -> guarded writes to manifest-owned pack sources only
                              -> combined validation or complete rollback
                              -> Camera Lab governed separately by Steps 5A–5B
                              -> Step 5C reviewed evidence promotion to pack verification status
                              -> Step 6B separately reviewed pack Git and combined handoff
                              -> no direct Camera Lab pack-source writes, build, application Git, cleanup, or publication boundary
```

Steps 5A–5B Camera Lab flow:

```text
active Profile Editor pack context + saved Subject/Profile Card
                              -> exact pack-ID handoff or same-pack Lab reuse
                              -> centralized pack resolution and fingerprint check
                              -> physical or simulated capability scan
                              -> pack profile/baseline/My Menu/equipment comparison
                              -> guarded simulator or explicitly enabled physical-camera operation
                              -> pack-ID-namespaced journals, qualifications, evidence, confirmations, and checklist
                              -> no profile-pack source write or canonical evidence promotion
```

Step 5C evidence-promotion flow:

```text
active external pack + pack-ID-namespaced completed physical journal
                              -> matching pack identity and eligible C1-C3 evidence inventory
                              -> explicit item selection and exact verification-status diff
                              -> one-use review token and separate confirmation
                              -> journal/source recheck, pack-namespaced backup, atomic pack-only write
                              -> combined source validation or complete rollback
                              -> no spreadsheet generation, build, Git, handoff, or publication
```

Step 6B independent pack-Git and combined-handoff flow:

```text
active external pack + zero browser drafts
                              -> separate application and pack Git inspection
                              -> exact source-bound pack commit review (initial commit includes AGENTS.md)
                              -> separate pack-only commit confirmation
                              -> exact credential-free origin review and separate configuration confirmation
                              -> separate non-force push to the same-named pack branch
                              -> live remote-head equality for both independent repositories
                              -> combined handoff ready, without application Git mutation
```

Accepted target flow after external-pack activation:

```text
shared upstream --selected reusable updates--> owner's application fork (origin)
                                                   +
                                          selected private profile pack
                                                   |
                                      validated resolved source set
                                                   |
                         cards / guide / spreadsheets / web-PWA outputs
```

The application and pack remain separate Git authorities. Combined output records both exact source revisions and the deterministic pack fingerprint; it does not make either repository authoritative for the other.

## Enforcement and Evidence

- `00 Master/project_identity.yaml` is the machine-readable repository identity.
- `00 Master/specifications/Profile Pack Specification.md` defines the accepted external-pack contract, limited Step 3A build, Step 3B validation, Step 4C saved selection and guarded editor support, Steps 5A–5B Camera Lab support, Step 5C reviewed evidence promotion, Step 6A New Profile Pack creation from embedded sources, Step 6B independent pack Git and combined handoff, and the still-inactive source-migration activation state.
- `80 Build/profile_pack.py` implements embedded compatibility, strict external-manifest parsing, application/pack identity checks, source containment, deterministic pack fingerprints, and path-free combined-build provenance. `80 Build/profile_pack_selection.py` owns the machine-local editor registry and selection. `80 Build/asset_manager.py` exposes the central resolved context while isolating external output by pack ID. `python3 "80 Build/build.py" --profile-pack PATH` and `python3 "80 Build/validator.py" --profile-pack PATH` remain explicit external development-review commands.
- `80 Build/card_identity.py`, `80 Build/migrate_card_ids.py`, and `80 Build/validators/card_identity_validator.py` own identity resolution, legacy migration, UUID uniqueness, and referential-integrity enforcement.
- `80 Build/validators/project_identity_validator.py` checks the Git root, current working directory, prohibited path markers, required authoritative components, identity fields, and baseline camera agreement.
- `00 Master/baseline.yaml` is the shared-default source.
- `00 Master/schema.yaml` documents the intended YAML fields and value shapes.
- `00 Master/my_menu_colors.yaml` defines reusable named-tab card colors; `80 Build/my_menu_colors.py` validates and resolves them for renderers and the editor.
- `00 Master/my_menu.yaml` and `80 Build/my_menu.py` define and validate the persisted My Menu layout; `80 Build/my_menu_reference.py` materializes that layout for HTML, PDF, and editor reference previews.
- `00 Master/feature_interactions.yaml`, `80 Build/feature_interactions.py`, and `80 Build/validators/feature_interaction_validator.py` define, evaluate, and validate shared feature-interaction rules for cards, Profile Editor previews, and future Camera Lab context.
- `00 Master/profile_lens_guidance.yaml`, `data/stabilization_reference.yaml`, `80 Build/lens_guidance.py`, and `80 Build/validators/lens_guidance_validator.py` define and validate subject-card lens choices, owned equipment relationships, and per-choice compatibility contexts.
- `80 Build/validators/baseline_validator.py` checks baseline shape.
- `80 Build/validators/profile_validator.py` checks inheritance, override paths, and compatible types.
- `80 Build/baseline_impact.py` owns baseline/profile impact classification; `80 Build/baseline_impact_check.py` exposes that same analysis for command-line review outside the UI.
- `80 Build/validators/structure.py` checks required architectural files and folders.
- `80 Build/validators/yaml_validator.py` checks parseability and top-level YAML shape.
- `build.py` and files under `80 Build/` implement merging, rendering, and output flow.

The Markdown specification is authoritative for intent; the listed configuration and validators are executable enforcement. A discrepancy is a defect to resolve, not permission to silently change behavior.
