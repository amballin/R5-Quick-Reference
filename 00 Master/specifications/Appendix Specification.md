# Appendix Specification

## Scope and Purpose

This specification governs Field Guides and Setting Deep Dives. Both are core explanatory content generated during builds; they prevent educational material from being duplicated in profiles.

## Manifest and Required Content

- Required appendices are declared in `50 Field Guide/required_appendices.yaml` and are not optional.
- Every manifest entry must have a unique `id`, title, and source file. Its referenced profiles and related appendix IDs must exist.
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
- `release: true` controls whether an entry is shown in the published GitHub Pages/offline index. Released `field_guide` entries appear under **Field Guide**; released `setting_deep_dive` entries appear under **Setting Deep Dives**.
- Optional integer `display_order` controls position independently within the published Field Guide or Setting Deep Dives section. Lower numbers appear first; entries with the same number are ordered alphabetically. Entries without the field default to `100`. Changing `content_type` moves an entry between sections; its source file must also be stored in the matching folder.
- Entries without `release: true` remain generated and linkable from released documentation, but are not listed in either published index section.
- Preserve existing appendix sources, manifest compatibility, rendering, and output locations unless explicitly approved.
- Standalone published appendices and Setting Deep Dives use the same Camera Settings header and inherited baseline `card.icons.header` as profile cards. The centered title always links to the main index. Back returns to the originating profile card when a valid generated card return target is supplied; otherwise it returns to the main index. Navigation must remain inside the generated reference system and must not depend on browser history.

## Enforcement and Evidence

- `50 Field Guide/required_appendices.yaml` is the machine-readable appendix inventory, relationship map, required-section list, topic metadata, exceptions, and release selection.
- `80 Build/validators/appendix_validator.py` checks manifest shape, unique IDs, files, headings, profile references, related appendix references, and strict topics.
- `80 Build/appendix_renderer.py` implements appendix rendering.
- `80 Build/validators/output_validator.py`, `pwa_validator.py`, and relevant build validation check generated/offline integration.
