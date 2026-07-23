# Architecture

## Scope

This specification defines the system boundaries and ownership of data, content, rendering, and generated artifacts. Governance and precedence are defined in [`PROJECT_RULES.md`](../../PROJECT_RULES.md).

## Requirements

- Preserve the established baseline + overrides architecture and existing YAML structure.
- Distinguish four evidence classes in camera-control documentation: verified Canon capability, owner-confirmed current configuration, project recommendation, and unresolved item.
- Do not treat historical screenshots, inferred icon meanings, or recommendations as proof of the current camera configuration.
- Explain the rationale and obtain explicit project-owner approval before changing an established architecture.
- Present proposed changes and affected files for review before modifying the reference.
- Shared behavior and shared camera settings belong in `00 Master/baseline.yaml`.
- Subject profiles inherit the baseline and contain only necessary overrides.
- The build resolves baseline and profile data before rendering.
- Presentation and rendering decisions belong in build code and templates, not profile YAML.
- Explanatory and educational content belongs in field-guide appendices; profiles reference it rather than duplicate it.
- Permanent reference cards remain separate from shooting profiles.
- The physical button and dial layout is shared across subject profiles. Subject-specific AF, exposure, drive, and stabilization settings remain owned by the baseline and profile overrides.
- Preserve the established build workflow, output locations, release behavior, rendering behavior, and backward compatibility unless an explicitly Accepted decision changes them.

## System Flow

```text
baseline.yaml + profile overrides
        -> merged profile data
        -> machine-local cards / guide / web-PWA outputs
        -> docs (GitHub Pages mirror)
        -> optional machine-local website staging -> optional iOS wrapper resources
```

## Enforcement and Evidence

- `00 Master/baseline.yaml` is the shared-default source.
- `00 Master/schema.yaml` documents the intended YAML fields and value shapes.
- `80 Build/validators/baseline_validator.py` checks baseline shape.
- `80 Build/validators/profile_validator.py` checks inheritance, override paths, and compatible types.
- `80 Build/validators/structure.py` checks required architectural files and folders.
- `80 Build/validators/yaml_validator.py` checks parseability and top-level YAML shape.
- `build.py` and files under `80 Build/` implement merging, rendering, and output flow.

The Markdown specification is authoritative for intent; the listed configuration and validators are executable enforcement. A discrepancy is a defect to resolve, not permission to silently change behavior.
