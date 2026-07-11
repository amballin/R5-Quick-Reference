# Appendix Specification

## Scope and Purpose

This specification governs field-guide appendices. Appendices are core explanatory content generated during builds; they prevent educational material from being duplicated in profiles.

## Manifest and Required Content

- Required appendices are declared in `50 Field Guide/required_appendices.yaml` and are not optional.
- Every manifest entry must have a unique `id`, title, and source file. Its referenced profiles and related appendix IDs must exist.
- A missing required appendix or an unparseable/invalid manifest fails validation.
- Filenames and titles do not need numbers. Legacy appendix numbers may remain as manifest metadata for continuity.
- Appendices should cross-reference relevant profiles, camera settings, lens notes, and related appendices. Profiles should reference appendices instead of duplicating their explanations.

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

- Builds include required appendices in applicable HTML, optional PDF, navigation, search, icon/index, and offline outputs.
- `release: true` on an appendix manifest entry selects it for the offline iPhone/PWA bundle. Absence or false does not select it.
- Preserve existing appendix sources, manifest compatibility, rendering, and output locations unless explicitly approved.

## Enforcement and Evidence

- `50 Field Guide/required_appendices.yaml` is the machine-readable appendix inventory, relationship map, required-section list, topic metadata, exceptions, and release selection.
- `80 Build/validators/appendix_validator.py` checks manifest shape, unique IDs, files, headings, profile references, related appendix references, and strict topics.
- `80 Build/appendix_renderer.py` implements appendix rendering.
- `80 Build/validators/output_validator.py`, `pwa_validator.py`, and relevant build validation check generated/offline integration.
