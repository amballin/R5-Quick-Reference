# Asset Specification

## Scope

This specification governs source visual assets and their use by cards, appendices, guides, and generated web outputs.

## Requirements

- Source assets belong only in established asset locations, principally `60 Assets/`; generated copies belong only in documented output locations.
- Reuse existing assets whenever practical. Do not create duplicate authoritative asset sources.
- Use Canon terminology and prefer official Canon names, icons, and descriptions when available.
- Keep active card icons, official Canon EOS R5 icons, retained cheatsheet references, and other photography assets in their existing documented subfolders.
- Preserve existing asset paths and mappings for backward compatibility unless an explicitly approved migration updates every consumer.
- Update `60 Assets/icon-map.yaml` when an approved setting/icon mapping changes.

## Enforcement and Evidence

- `60 Assets/icon-map.yaml` maps setting concepts to active assets.
- `60 Assets/icons/canon_r5_official/modes.yaml` and `data/canon_r5_icons.yaml` describe official Canon icon assets.
- `80 Build/validators/icon_validator.py` checks mapped assets, duplicates, metadata, required official icons, SVG validity, and unreferenced assets.
- `80 Build/validators/validate_canon_r5_icons.py` performs the dedicated Canon R5 icon-reference validation.
- `80 Build/validators/yaml_validator.py` checks the machine-readable asset manifests.

Generated HTML/PWA copies are verified as build outputs; they are not new source assets.
