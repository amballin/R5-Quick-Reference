# Architecture

## Scope

This specification defines the system boundaries and ownership of data, content, rendering, and generated artifacts. Governance and precedence are defined in [`PROJECT_RULES.md`](../../PROJECT_RULES.md).

## Requirements

- Preserve the established baseline + overrides architecture and existing YAML structure.
- Distinguish five evidence classes in camera-control documentation: verified Canon capability, owner-confirmed current configuration, approved target pending physical verification, project recommendation, and unresolved item.
- Do not treat approved targets, historical screenshots, inferred icon meanings, or recommendations as proof of the current camera configuration.
- Explain the rationale and obtain explicit project-owner approval before changing an established architecture.
- Present proposed changes and affected files for review before modifying the reference.
- For each new change task, present a clear recommendation, rationale, and affected files, then request approval as a separate explicit question. Once approved, treat that recommended scope as authorized without requiring the project owner to repeat it. Read-only questions and status checks do not require change approval.
- Shared behavior and shared camera settings belong in `00 Master/baseline.yaml`.
- Subject profiles inherit the baseline and contain only necessary overrides.
- The build resolves baseline and profile data before rendering.
- Presentation and rendering decisions belong in build code and templates, not profile YAML.
- Explanatory and educational content belongs in field-guide appendices; profiles reference it rather than duplicate it.
- Permanent reference cards remain separate from shooting profiles.
- The physical button and dial layout is shared across subject profiles.
- Subject profiles define complete shooting environments. C1, C2, and C3 are camera-side implementations of the canonical `Wildlife`, `Birds in Flight`, and `Landscape` profiles rather than independent AF presets. Field labels such as **General Wildlife** and **Birds in Flight / Action** may describe use, but machine-readable mappings retain the exact canonical profile title.
- The selected profile owns the initial AF Operation, Subject Detection, Eye Detection, exposure, drive, stabilization, and other subject-specific settings.
- AF-ON and AE Lock keep constant focusing roles across profiles. AF-ON temporarily selects Face + Tracking for intelligent acquisition; AE Lock temporarily selects 1-Point AF for precise placement. Both maintain the current AF Operation and Servo AF characteristics.
- The DOF button remains the One-Shot AF ↔ Servo AF control. AF-ON and AE Lock must not force an AF Operation that would defeat the selected profile state or a DOF-button change.
- Subject Detection belongs to the profile, not to either AF-start button. A deliberate-point AF method may make Subject Detection or Eye Detection inapplicable without changing their stored profile values.
- Preserve the established build workflow, output locations, release behavior, rendering behavior, and backward compatibility unless an explicitly Accepted decision changes them.

## System Flow

```text
baseline.yaml + profile overrides
        -> merged profile data
        -> machine-local cards / guide / web-PWA outputs
        -> docs (GitHub Pages mirror)
        -> optional machine-local website staging
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
