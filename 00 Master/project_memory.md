# Photography Reference System — Project Memory

## Purpose and Authority

This file preserves stable project context, intent, rationale, terminology, and architectural history. It is not a duplicate rulebook. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md); normative details are defined in [`specifications/`](specifications/).

The repository is the permanent source of truth; conversation history is not. When permanent context changes, update this file in the same change, but place new binding requirements in the governing rules, an applicable specification, or an Accepted decision.

## Project Intent

The Photography Reference System produces Canon EOS R5 subject-setting cards, field-guide appendices, an installable web app, and GitHub Pages output. Cards are concise, field-ready quick references; appendices contain explanation and education.

The project is intentionally evolutionary. Consistency, minimal changes, reuse, and backward compatibility are preferred over theoretical elegance. Research normally happens outside the repository, while a feature conversation owns a deliverable from idea through implementation. The Master Planner maintains roadmap and priorities and protects architectural consistency.

## Architectural History and Rationale

The established design is **Baseline + Overrides**. Shared defaults live once in the baseline; profiles describe subject-specific differences. The build merges both sources before rendering, which prevents drift and lets cards show inherited settings without copying them into profile files.

The accepted long-term sharing model preserves Baseline + Overrides while separating ownership. Reusable application logic and Canon knowledge can flow selectively from a shared upstream into an owner's application fork, while the operational baseline, profiles, My Menu, owner controls, equipment selection, and verification state live together in a separately owned private profile pack. A combined build records both source revisions. This makes application improvements shareable without making private source part of the shared upstream, but it does not make released profile output private. Step 4C lets Profile Editor remember a private machine-local selection, display each pack's live manifest name, and switch safely among remembered packs and embedded compatibility sources before using the guarded Profile/lens, baseline, C1-C3, My Menu, Camera Buttons, preview, removal, and restore workflows. Steps 5A and 5B pass that selected context into Camera Lab for path-private scan, comparison, guarded simulation, and explicitly enabled physical-camera operation. Step 5C lets Profile Editor deliberately promote exact completed physical-camera evidence from the active pack's machine-local journal namespace into that pack's verification status after exact review, separate confirmation, backup, validation, and rollback protection. Local journals, qualifications, write evidence, confirmations, and browser checklist state are pack-ID-namespaced; Camera Lab itself still cannot modify pack source. Canonical editor writes remain manifest-contained; backups, Deleted Cards, and previews remain pack-ID-namespaced. Editor-initiated builds, spreadsheets, cleanup, Git, handoff, integration, main-editor launch, and publication remain closed for external packs. A guided New Profile Pack wizard is a deferred, separately approved creation/migration capability.

The repository carries a machine-readable project identity that distinguishes the authoritative Canon EOS R5 source from similarly named backups, archives, wrappers, and generated outputs. Runtime root checks intentionally stop for owner direction instead of searching sibling locations or selecting a substitute repository automatically.

The operational baseline and Camera Defaults reset state are the general-purpose target, including explicit Auto shutter and aperture values, Servo AF Case A (Auto) with automatic Case parameters, Switching tracked subjects set to On subject, Face + Tracking, Animals, Eye Detection enabled, High Speed Continuous, and High speed display enabled. Case 1 is configured once as a project preset at Tracking Sensitivity -1 and Accel./Decel. tracking +1; this differs from Canon's factory 0 / 0 Case 1. Wildlife, Birds Perched, and Sports select the custom preset, while Birds in Flight uses Case 4 at 0 / +1 and People remains Case A. One-Shot and Manual Focus profiles retain a stored Case but do not actively use or display it. These are approved targets pending physical verification and do not establish that the camera currently matches them.

Rendering is separated from profile data so presentation can evolve without restructuring shooting data. Educational content is separated into appendices so profiles remain concise and explanations have a single home. Permanent reference cards remain distinct from shooting profiles.

Profile Editor navigation follows the operator's normal sequence: Daily work first, ordered Profile setup second, and Occasional integration, publication, maintenance, sharing, and reference tools last. The Camera Buttons workspace mirrors the generated card visually through the same physical-control icon mapping and uses a Canon-grounded option catalog to explain defaults, choices, INFO settings, and evidence states. Its preview is a production-rendered view of the unsaved in-memory draft; saving still requires the guarded synchronized-source transaction.

Every shooting profile and permanent reference card has an immutable UUID. C1–C3 assignments, card foundations, and appendix associations use that identity rather than the mutable title; interfaces resolve the current title for display. Unreleased editable cards can leave active source only through the recoverable machine-local Deleted Cards holding area after structured dependency checks. The ordinary editor has restore but no permanent purge action. Permanent reference-card profile YAML remains read-only; Camera Buttons and My Menu instead use dedicated structured editors for their canonical sources.

Applicable profile cards carry compact field-access metadata for any intended starting C1–C3 mode and for My Menu tabs used to reach displayed settings. My Menu access does not require a Cx foundation: its color answers where a setting can be found. A shared curated palette assigns colors by named My Menu tab and colors matching setting values and their change indicators, while Quick Control, dial, and button values remain white. With a Cx foundation, `Δ` identifies a derived difference; without one, every displayed row carries `Δ` as a conservative instruction to verify or set the target. SWITCH starts green and AF Case starts gold but both may be deliberately reassigned through the guarded My Menu review. The persisted tab names and ordered shortcuts also generate a read-only My Menu reference card for field use; the card follows every saved used tab without duplicating its contents in profile YAML. Light Red is intentionally redder than the orange-red Coral choice. The full explanation remains in generated Notes so the top-of-card route stays field-ready.

Camera Defaults uses the same color language as an access-only route: SWITCH and AF Case appear without a C1–C3 token because the general baseline is not a registered-mode target. Shutter Type, Subject Detection, and Image Stabilization use SWITCH; Servo AF Case and Switching Tracked Subjects use AF Case. Other values remain white for Q, dial, button, or normal-menu access.

Servo AF cards show the effective Servo AF Case directly after AF Operation. Registered C1 Wildlife supplies Case 1 (Custom) at -1 / +1, registered C2 Birds in Flight supplies Case 4 at 0 / +1, and C3 stores Case A without using it in its One-Shot starting state. People remains Case A and therefore changes C1's selected Case through My Menu: AF Case when starting from C1. Non-Auto Cases show the two effective Case parameters in one compact Track / Accel row. Switching tracked subjects is separate from the Case, uses On subject as the shared starting point, and appears only with compatible Face + Tracking, Zone AF, or Large Zone AF methods. My Menu: AF Case contains Servo AF, Tracking Sensitivity, Accel./Decel. tracking, and Switching tracked subjects; Servo AF opens the Case selector. Wildlife, Birds in Flight, Birds Perched, People, and Sports associate their applicable displayed values with that tab. AF3 remains the direct Case route and AF4 remains the direct subject-switching route.

High speed display is enabled as a shared set-and-forget target. It appears on Camera Defaults, Camera Setup Essentials, and cards whose starting configuration uses regular High Speed Continuous or Electronic shutter. It is not a My Menu transition setting and is omitted where High Speed Continuous+, Low Speed Continuous, or Single Shot makes the selectable setting inactive.

EFCS is the owner-approved EOS R5 shutter baseline pending physical verification. Mechanical overrides remain for People, Birds in Flight, Sports, and Waterdrops because fast, wide-aperture bokeh or third-party flash/trigger reliability matters more in those profiles. Fully Electronic shutter remains situational rather than a profile default.

The EOS R5 uses one physical button and dial layout across subject profiles. C1, C2, and C3 provide fast camera-side implementations of the canonical Wildlife, Birds in Flight, and Landscape profiles, with General Wildlife and Birds in Flight / Action retained only as field labels. M-Fn is owner-confirmed as **Switch to Custom shooting mode**, and repeated presses were physically verified to switch among C1, C2, and C3. In physical session 3, C1 Wildlife, C2 Birds in Flight, and C3 Landscape were registered, recalled, and cross-checked against their camera-body targets; `C123_CFG.CSD` is the completed recovery checkpoint. Exact lens stabilization Mode 1/3 remains unresolved because the attached lens exposed only IS On/Off. The selected profile establishes the shooting environment and initial One-Shot/Servo and Eye Detection states. AF-ON consistently supplies Face + Tracking for intelligent subject acquisition, while AE Lock consistently supplies the 1-Point AF precision alternative; both maintain the current AF Operation so the DOF-button switch remains effective. SET toggles the stored Eye Detection state when the active AF method supports it, and AF-ON honors that state. AE Lock remembers the last 1-Point position, the joystick moves the point, and pressing the joystick straight in recenters it. Subject Detection belongs to the profile. Detailed setup and operating rationale belong in the custom-controls deep dive, while the Camera Buttons card remains concise. Historical control screenshots are not treated as current-state evidence, and future registration-target changes remain pending until physically reverified.

The generated site uses the machine-local workspace's `Build Output/merged-build/` as its canonical web/PWA bundle. It is mirrored to top-level `docs/` because GitHub Pages is configured for `main / docs`; `Build Output/website/` remains optional machine-local staging for other web hosts. PDF generation is intentionally opt-in. Fixed card PNG exports were retired as unused; this does not affect PNG source assets, app icons, spreadsheet previews, or PDF assembly. The former native iOS wrapper was retired after the installable HTML/PWA became the sufficient phone experience.

Concise task guidance is maintained as Markdown plus automatically generated, Git-tracked local HTML pages. The workflow index covers preflight, local builds, spreadsheet creation/publication/status, publishing, computer handoff, and recovery. These pages travel between computers through Git but are excluded from `docs/` and the public site.

Local validation is intentionally two-phase: source-only validation runs before generation, then full validation checks generated output after the normal build. This prevents legitimate stale generated artifacts from blocking the build that refreshes them.

Spreadsheet structure is source-driven: shared and workbook-specific layout lives in `00 Master/spreadsheet_layouts.yaml`, while Setup verification content and its Menu access lookups live in `90 Testing/eos_r5_verification_tracker.yaml`. The publishable Setup workbook is always a blank master. Mutable testing state is canonical in the non-published, Git-tracked `90 Testing/eos_r5_verification_status.yaml`; Excel/Numbers is the machine-local working interface, and workbook changes are imported back into YAML. Definition fingerprints invalidate affected prior passes when requirements change. Published spreadsheet releases carry independent revisions, source fingerprints, and file hashes so ordinary site publication can preserve compatible workbook bytes without silently retaining stale content.
Each spreadsheet family has a deterministic visible build ID derived from its workbook revision and current source fingerprint. Profile Editor publication preserves current workbook bytes automatically, refreshes only stale families, and offers a separate true force rebuild for both families; spreadsheet build identity remains independent from website versioning.
Website publications increment the minor version by default. An intentional major release uses `publish.sh --major-version N`, requires a value greater than the current major version, publishes as `N.00`, and leaves spreadsheet revisions independent.
Publication completion is independently auditable: each run writes a machine-local log, and the latest release must pass version-transition, published-index, upstream-commit, and requested spreadsheet-hash verification. A clean Git report by itself does not prove that publication occurred.
Profile Editor and Camera Lab share a separate local-application version from `00 Master/application_version.yaml`. Major is owner-controlled, Minor follows Git commits from the recorded anchor, and Incremental records completed development updates between commits. Their headers show the shared version plus Main or Prototype; the full branch and source hash remain inside expandable version diagnostics instead of a duplicate header badge.
Camera Lab can replace its active physical-camera backend with the deterministic simulator, and return to Canon EDSDK, from a confirmed in-page action. The authenticated restart closes the current session and replaces the same supervised loopback server process; it never runs both backends or two port-8770 servers together. Completed physical EDSDK journals can be reviewed in Profile Editor and promoted only into exact matching C1–C3 configured fields, with provenance and deduplication; simulator evidence and broader verification claims remain ineligible.

## Domain Context and Terminology

- Use Canon terminology and prefer official Canon names, icons, and descriptions.
- The primary camera context is the Canon EOS R5; firmware context is recorded in the baseline.
- Stabilization mode, in-body image stabilization (IBIS), and lens optical stabilization (Lens IS) are distinct camera/lens concepts even when a card combines their presentation.
- “Profile” means a subject or shooting-situation YAML override that inherits from the baseline.
- “Card” means a generated quick-reference view of fully merged settings.
- “Appendix” means explanatory field-guide source content declared by the appendix manifest.
- “Release” means inclusion in the offline iPhone/PWA bundle, controlled independently for profiles and appendices.
- “Owner-confirmed” means the project owner directly verified or set the camera control after the earlier screenshot evidence became unreliable.

## Stable Workflow Context

```text
Research (outside the project)
    -> Feature conversation (one deliverable)
    -> Repository implementation
    -> Rules/specification/decision/context updates when warranted
```

Firmware changes are treated cautiously: confirm new camera behavior, decide whether it changes shared defaults, review profile overrides, assets, rendered results, and record significant decisions.

## Governing References

- [`PROJECT_RULES.md`](../PROJECT_RULES.md)
- [`00 Master/specifications/`](specifications/)
- [`00 Master/decision-log.md`](decision-log.md)
- [`00 Master/baseline.yaml`](baseline.yaml)
- [`00 Master/schema.yaml`](schema.yaml)
- [`00 Master/card_layout.yaml`](card_layout.yaml)
- [`50 Field Guide/required_appendices.yaml`](../50%20Field%20Guide/required_appendices.yaml)
