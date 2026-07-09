# Decision Log

## Future Enhancement: Lens Stabilization Guidance

Status: Reminder
Date: 2026-07-05

The current profile structure should keep stabilization concepts separate:

- `stabilization.image_stabilization.mode` records the stabilization mode or behavior to use for the shooting situation.
- `stabilization.ibis` records body image stabilization on/off.
- `stabilization.lens_is` records lens optical stabilization on/off.

Do not combine IBIS and Lens IS into one field without an explicit architecture decision. Different lenses expose different stabilization controls, and some lenses have Mode 1 / Mode 2 / Mode 3 behavior while others do not.

Future work should add lens-specific guidance, likely as reference documentation rather than repeated profile overrides. The lens guide should explain:

- Lens IS switch behavior for specific lenses.
- Image Stabilization mode reminders.
- When to use Mode 1, Mode 2, or Mode 3.
- Tripod behavior and when stabilization should be turned off.
- Macro, panning, wildlife, and long-exposure considerations.
- How profile cards should reference lens guidance without duplicating lens-specific details.

## Future Enhancement: Phase 4 - User Experience

Status: Reminder
Date: 2026-07-05

Future build-system improvements should focus on making the project easier to inspect and operate from the command line while preserving the current project structure, YAML format, baseline + overrides architecture, and existing build workflow.

Search:

```bash
python build.py --search ISO
```

Expected result should list profiles that reference or inherit relevant ISO settings, for example:

```text
Wildlife
Sports
Fireworks
Macro
```

Compare:

```bash
python build.py --compare Wildlife Sports
```

Expected result should show only the differences between the two fully resolved profiles.

Build one profile:

```bash
python build.py Fireworks
```

This behavior already exists and should be preserved.

Build changed profiles only:

Add a future mode that builds only profiles whose source YAML, baseline, dependent assets, or build inputs changed. This would be a significant time saver, especially once the profile set grows.

## Future Enhancement: Phase 5 - Documentation

Status: Reminder
Date: 2026-07-05

Create permanent project documentation with Codex assistance after the architecture stabilizes. The documentation set should include:

- `PROJECT_RULES.md`
- `Architecture.md`
- `Profile Specification.md`
- `Asset Specification.md`
- `Build Specification.md`

These should become the permanent reference documents for future development and should document the current architecture rather than redesign it.

## Future Enhancement: Card Visual Format

Status: Reminder
Date: 2026-07-05

Future card-rendering work should move generated cards closer to the original reference-card format while preserving the existing output locations, filenames, profile YAML structure, and build workflow.

Desired direction:

- Keep the main content area of each card white for readability.
- Use colored headers or section bars to carry profile identity and visual hierarchy.
- Allow profile-specific header color choices in the future, after deciding the YAML structure.
- Add an icon or icons near the top of each card, especially for PNG and PDF outputs.
- Preserve the existing pale-blue setting icons unless a broader visual refresh is explicitly approved.
- Match the original card proportions and layout more closely where practical.

Do not implement this as an ad hoc renderer change. Decide the card styling model first, then update the renderer and documentation together.

## Future Enhancement: Macro Guidance Expansion

Status: Reminder
Date: 2026-07-05

Future profile/content work should flesh out the Macro section in stages.

Phase 1 should cover Canon EOS R5 built-in macro-relevant capabilities, including:

- Focus bracketing / focus stacking workflow.
- Manual focus and magnified view.
- Focus peaking.
- Stabilization considerations at macro distances.
- Flash and ambient-light considerations.
- Tripod, rail, and handheld tradeoffs.
- Depth-of-field limitations and diffraction cautions.

Phase 2 should add specialized macro guidance for:

- Canon MP-E 65mm macro lens usage.
- StackShot / automated rail workflow.
- High-magnification setup, lighting, vibration control, and stacking notes.

Keep this as guidance and profile content work unless a later decision explicitly changes the YAML structure or build behavior.
