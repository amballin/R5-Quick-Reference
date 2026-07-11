# Profile Specification

## Scope

This specification governs subject/profile YAML under `10 Profiles/`.

## Requirements

- Every profile inherits `baseline`.
- A profile contains only values that differ from `00 Master/baseline.yaml`; it must not repeat baseline values.
- Overrides must use paths present in `baseline.defaults` and compatible value types.
- Profile data retains camera concepts as separate fields, including ISO mode, fixed ISO value, Auto ISO maximum, stabilization mode, IBIS, and Lens IS.
- Profiles contain shooting settings and concise field-use content, not duplicated educational explanations. Reference applicable appendices instead.
- Preserve existing profile filenames, titles, YAML structure, data, and backward compatibility unless explicitly approved.
- `metadata.release: true` selects the profile/card for the offline iPhone/PWA bundle. Absence or false does not select it.

## Expected Structure

Profiles use the existing keys documented by `00 Master/schema.yaml`, including `metadata`, `title`, optional `subtitle`, `inherits`, `overrides`, and optional list content such as `checklist`, `watch_for`, `common_mistakes`, and `notes`.

## Enforcement and Evidence

- `00 Master/baseline.yaml` defines valid shared default paths and their effective types.
- `00 Master/schema.yaml` documents profile field structure.
- `80 Build/validators/profile_validator.py` enforces required keys, `inherits: baseline`, override paths/types, title uniqueness, and list shapes.
- `80 Build/validators/yaml_validator.py` rejects malformed or duplicate-key YAML.
- Build and PWA code under `80 Build/` implements merging and release filtering; generated-output and PWA validators provide integration evidence.

The current validator checks that overrides are valid but does not reject an override merely because its value equals the baseline. The no-duplication rule therefore also requires review until a dedicated check exists.
