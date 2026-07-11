# Decision Log

Only entries marked **Accepted** are binding. **Proposed** entries are non-binding possibilities; **Superseded** and **Rejected** entries are historical only. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md).

## Documentation Governance Consolidation

**Status:** Accepted
**Date:** 2026-07-11

Use `PROJECT_RULES.md` as the concise governing entry point; separate detailed architecture, profile, card, appendix, asset, and build/validation requirements under `00 Master/specifications/`; retain project memory for stable context; and use this status-based decision log. This decision supersedes the former combined-specification arrangement.

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
