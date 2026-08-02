# Photography Reference System — Project Memory

## Purpose and Authority

This file preserves stable project context, intent, rationale, terminology, and architectural history. It is not a duplicate rulebook. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md); normative details are defined in [`specifications/`](specifications/).

The repository is the permanent source of truth; conversation history is not. When permanent context changes, update this file in the same change, but place new binding requirements in the governing rules, an applicable specification, or an Accepted decision.

## Project Intent

The Photography Reference System produces Canon EOS R5 subject-setting cards, field-guide appendices, an installable web app, and GitHub Pages output. Cards are concise, field-ready quick references; appendices contain explanation and education.

The project is intentionally evolutionary. Consistency, minimal changes, reuse, and backward compatibility are preferred over theoretical elegance. Research normally happens outside the repository, while a feature conversation owns a deliverable from idea through implementation. The Master Planner maintains roadmap and priorities and protects architectural consistency.

## Architectural History and Rationale

The established design is **Baseline + Overrides**. Shared defaults live once in the baseline; profiles describe subject-specific differences. The build merges both sources before rendering, which prevents drift and lets cards show inherited settings without copying them into profile files.

The operational baseline and Camera Defaults reset state intentionally match the approved C1 Wildlife target, including explicit Auto shutter and aperture values, Face + Tracking, Animals, Eye Detection enabled, and High Speed Continuous. Profiles for deliberate-point, static, or manual-focus work override those inherited choices. This alignment is an approved target pending physical verification and does not establish that the camera currently matches it.

Rendering is separated from profile data so presentation can evolve without restructuring shooting data. Educational content is separated into appendices so profiles remain concise and explanations have a single home. Permanent reference cards remain distinct from shooting profiles.

Applicable subject cards carry compact field-access metadata for the intended starting C1–C3 mode and any My Menu tabs used for remaining changes. The responsive card renderer keeps SWITCH green, assigns renderer-managed colors to later tabs, colors matching setting values, and leaves Quick Control, dial, and button values white. The full explanation remains in generated Notes so the top-of-card route stays field-ready.

EFCS is the owner-approved EOS R5 shutter baseline pending physical verification. Mechanical overrides remain for People, Birds in Flight, Sports, and Waterdrops because fast, wide-aperture bokeh or third-party flash/trigger reliability matters more in those profiles. Fully Electronic shutter remains situational rather than a profile default.

The EOS R5 uses one physical button and dial layout across subject profiles. C1, C2, and C3 provide fast camera-side implementations of the canonical Wildlife, Birds in Flight, and Landscape profiles, with General Wildlife and Birds in Flight / Action retained only as field labels. M-Fn is owner-confirmed as **Switch to Custom shooting mode**, and repeated presses were physically verified to switch among C1, C2, and C3. C1 currently contains registered settings but still requires verification against the complete Wildlife profile; C2 and C3 are not yet registered. The selected profile establishes the shooting environment and initial One-Shot/Servo and Eye Detection states. AF-ON consistently supplies Face + Tracking for intelligent subject acquisition, while AE Lock consistently supplies the 1-Point AF precision alternative; both maintain the current AF Operation so the DOF-button switch remains effective. SET toggles the stored Eye Detection state when the active AF method supports it, and AF-ON honors that state. AE Lock remembers the last 1-Point position, the joystick moves the point, and pressing the joystick straight in recenters it. Subject Detection belongs to the profile. Detailed setup and operating rationale belong in the custom-controls deep dive, while the Camera Buttons card remains concise. Historical control screenshots are not treated as current-state evidence, and approved target settings remain distinct from settings physically confirmed on the camera.

The generated site uses the machine-local workspace's `Build Output/merged-build/` as its canonical web/PWA bundle. It is mirrored to top-level `docs/` because GitHub Pages is configured for `main / docs`; `Build Output/website/` remains optional machine-local staging for other web hosts. PDF generation is intentionally opt-in. Fixed card PNG exports were retired as unused; this does not affect PNG source assets, app icons, spreadsheet previews, or PDF assembly. The former native iOS wrapper was retired after the installable HTML/PWA became the sufficient phone experience.

Concise task guidance is maintained as Markdown plus automatically generated, Git-tracked local HTML pages. The workflow index covers preflight, local builds, spreadsheet creation/publication/status, publishing, computer handoff, and recovery. These pages travel between computers through Git but are excluded from `docs/` and the public site.

Local validation is intentionally two-phase: source-only validation runs before generation, then full validation checks generated output after the normal build. This prevents legitimate stale generated artifacts from blocking the build that refreshes them.

Spreadsheet structure is source-driven: shared and workbook-specific layout lives in `00 Master/spreadsheet_layouts.yaml`, while Setup verification content and its Menu access lookups live in `90 Testing/eos_r5_verification_tracker.yaml`. The publishable Setup workbook is always a blank master. Mutable testing state is canonical in the non-published, Git-tracked `90 Testing/eos_r5_verification_status.yaml`; Excel/Numbers is the machine-local working interface, and workbook changes are imported back into YAML. Definition fingerprints invalidate affected prior passes when requirements change. Published spreadsheet releases carry independent revisions, source fingerprints, and file hashes so ordinary site publication can preserve compatible workbook bytes without silently retaining stale content.
Website publications increment the minor version by default. An intentional major release uses `publish.sh --major-version N`, requires a value greater than the current major version, publishes as `N.00`, and leaves spreadsheet revisions independent.
Publication completion is independently auditable: each run writes a machine-local log, and the latest release must pass version-transition, published-index, upstream-commit, and requested spreadsheet-hash verification. A clean Git report by itself does not prove that publication occurred.

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
