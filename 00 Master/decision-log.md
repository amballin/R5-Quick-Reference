# Decision Log

Only entries marked **Accepted** are binding. **Proposed** entries are non-binding possibilities; **Superseded** and **Rejected** entries are historical only. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md).

## Owner-Confirmed EOS R5 Button and Dial Architecture

**Status:** Accepted
**Date:** 2026-07-23

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
