# Decision Log

Only entries marked **Accepted** are binding. **Proposed** entries are non-binding possibilities; **Superseded** and **Rejected** entries are historical only. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md).

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
