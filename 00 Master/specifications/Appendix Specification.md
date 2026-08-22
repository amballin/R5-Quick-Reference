# Appendix Specification

## Scope and Purpose

This specification governs Field Guides and Setting Deep Dives. Both are core explanatory content generated during builds; they prevent educational material from being duplicated in profiles.

## Manifest and Required Content

- Required appendices are declared in `50 Field Guide/required_appendices.yaml` and are not optional.
- Every manifest entry must have a unique `id`, title, and source file. Its `profile_ids` must resolve to active immutable card UUIDs, and its related appendix IDs must exist.
- A missing required appendix or an unparseable/invalid manifest fails validation.
- Filenames and titles do not need numbers. Legacy appendix numbers may remain as manifest metadata for continuity.
- Appendices should cross-reference relevant profiles, camera settings, lens notes, and related appendices. Profiles should reference appendices instead of duplicating their explanations.
- Internal Markdown links to another manifest entry use `(appendix:manifest_id)`. The renderer resolves the ID to the correct generated filename, and validation rejects missing IDs.
- Sources with `content_type: field_guide`, or with no `content_type` for backward compatibility, live under `50 Field Guide/Appendices/`.
- Sources with `content_type: setting_deep_dive` live under `50 Field Guide/Setting Deep Dives/` and provide focused guidance for an individual camera setting or tightly scoped feature.

## Standard Section Order

Unless an appendix manifest entry explicitly lists a section in `skip_required_sections`, use this order:

1. Purpose
2. What it Does
3. How it Works
4. Advantages
5. Disadvantages
6. Recommended Uses
7. When Not to Use
8. Decision Guide
9. Recommended Settings by Profile
10. Canon-Specific Notes
11. Tips
12. Common Mistakes
13. Cross References

Manifest `required_topics` describe expected subject coverage. Topics are validator-enforced only when the entry enables `strict_topics`.

## Build and Release Requirements

- Builds generate all manifest entries in applicable HTML and search outputs. PDF remains optional.
- `release: true` controls whether an entry is shown in the published GitHub Pages/offline index. Released `field_guide` entries appear under **Field Guides**; released `setting_deep_dive` entries appear under **Deep Dive**.
- Optional integer `display_order` controls position independently within the published Field Guide or Setting Deep Dives section. Lower numbers appear first; entries with the same number are ordered alphabetically. Entries without the field default to `100`. Changing `content_type` moves an entry between sections; its source file must also be stored in the matching folder.
- Entries without `release: true` remain generated and linkable from released documentation, but are not listed in either published index section.
- Preserve existing appendix sources, manifest compatibility, rendering, and output locations unless explicitly approved.
- Standalone published appendices and Setting Deep Dives use the same Camera Settings header and inherited baseline `card.icons.header` as profile cards. The centered title always links to the main index. Back returns to the originating profile card when a valid generated card return target is supplied; otherwise it returns to the main index. Navigation must remain inside the generated reference system and must not depend on browser history.
- An appendix with a front `Index`, `Topic Index`, or `Table of Contents` heading provides a persistent internal **Return to index** control both on its standalone page and inside its expanded panel on the main index. Print/output rendering omits this control.
- Embedded appendix heading IDs and internal fragment links are namespaced per appendix so duplicate source heading IDs cannot send a link into a different expanded guide.
- Internal heading targets use sufficient scroll offset to remain visible below the sticky Camera Settings header.
- Preserve explicitly authored HTTPS links to authoritative external references in standalone appendix HTML, the published index, and the offline/PWA bundle. Open them separately with `target="_blank"` and `rel="noopener noreferrer"`; do not treat them as internal Back or return destinations.

## Structured Stabilization Reference

- `data/stabilization_reference.yaml` is the structured source for normal EOS R5 stabilization control and per-lens stabilization capabilities used by the Lens Capabilities appendix.
- Lens records distinguish optical IS presence, physical Image Stabilizer On/Off and mode switches, supported modes and their Canon-stated purposes, control location, camera interaction, lens-specific exceptions, and Canon sources.
- Fields that do not apply remain absent where practical. In particular, a lens without a physical mode selector does not carry an `is_modes` list.
- Lens Capabilities Markdown uses a stable lens ID marker where the appendix renderer inserts the corresponding generated stabilization table. Rendering shows only modes supported by that lens.
- Camera guidance retains Canon's exact `IS (Image Stabilizer) mode` label and treats the Shooting-menu page number as conditional rather than fixed.
- Structured stabilization facts remain explanatory appendix data. They do not alter the baseline-plus-overrides profile schema or collapse the separate profile concepts of stabilization mode, IBIS, and Lens IS.

## Enforcement and Evidence

- `50 Field Guide/required_appendices.yaml` is the machine-readable appendix inventory, relationship map, required-section list, topic metadata, exceptions, and release selection.
- `data/stabilization_reference.yaml` is the machine-readable source for generated lens stabilization controls and normal EOS R5 IS menu behavior.
- `80 Build/validators/appendix_validator.py` checks manifest shape, unique IDs, files, headings, profile references, related appendix references, and strict topics.
- `80 Build/validators/stabilization_validator.py` checks conditional stabilization fields, lens marker coverage, Canon-source presence, exact camera-menu terminology, and contradictory switch/mode claims.
- `80 Build/appendix_renderer.py` implements appendix rendering.
- `80 Build/validators/output_validator.py`, `pwa_validator.py`, and relevant build validation check generated/offline integration.
