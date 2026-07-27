# Decision Log

Only entries marked **Accepted** are binding. **Proposed** entries are non-binding possibilities; **Superseded** and **Rejected** entries are historical only. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md).

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

Keep the concise Camera Buttons card limited to assignments and a link to the detailed guide. Put AF-ON and AE Lock INFO details, operating explanation, and subject-profile examples in **Custom Controls, Back-Button AF & Dial Strategies**, not R5 Quick Reference. Use the plain physical labels **Main Dial**, **Rear Wheel**, **Top Rear Dial**, and **Control Ring**. Leave Movie Record, MODE, and LCD panel illumination at their defaults. M-Fn and the contents of C1-C3 remain unresolved for later review.

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

Promote AF Cases & Tracking Behavior, Flash Photography, and Long Exposure & Night Photography to released Setting Deep Dives. Consolidate general custom-control guidance into **Custom Controls, Back-Button AF & Dial Strategies**. Preserve the incomplete Canon EOS R5 Custom Controls Current Configuration source without deciding its eventual disposition. Keep the Canon EOS R5 Official Icon Reference generated and available offline as an unreleased supporting reference linked directly from R5 Quick Reference, rather than listing it as a primary Field Guide.

## Independent Card Display Categories

**Status:** Accepted
**Date:** 2026-07-18

Separate index placement from card rendering behavior. Profiles may use `display_category: subject|reference` and integer `display_order`; category defaults from `card_type`, order defaults to `100`, lower values appear first, and ties sort alphabetically. This allows baseline-driven operational cards to appear under **Reference Cards** without converting them to permanent reference-card data. Label the published sections **Subjects**, **Reference Cards**, **Field Guides**, and **Deep Dive**.

This decision supersedes the index-placement restriction in **Permanent Reference-Card Type** and the published section labels in **Setting Deep Dives**; their remaining requirements stay binding.

## Opt-In PNG Card Exports

**Status:** Accepted
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

Publish released camera cards as responsive standalone HTML pages optimized for iPhone safe areas and readable browser text. Make each HTML card the primary action on the Camera Settings index while retaining fixed PNG cards as secondary exports. Generate both presentations from the same merged baseline-plus-overrides data. Keep responsive styling in `20 Templates/card.html`, fixed PNG styling in `80 Build/render_card_outputs.js`, and publish required card icons through generated relative asset paths.

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

**Status:** Proposed (non-binding)
**Date:** 2026-07-05

Future work could add lens-specific reference guidance covering lens IS switches, Mode 1/2/3, tripod behavior, macro, panning, wildlife, and long exposure. It should avoid repeating lens-specific explanations in profiles.

The current separation of stabilization mode, IBIS, and Lens IS is binding through the Profile Specification; this proposal does not itself authorize a data-model change.

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
