# Architecture

## Scope

This specification defines the system boundaries and ownership of data, content, rendering, and generated artifacts. Governance and precedence are defined in [`PROJECT_RULES.md`](../../PROJECT_RULES.md).

## Requirements

- The Git root is the only authoritative source root for a task. Resolve it at runtime; do not select another repository or sibling copy automatically.
- `00 Master/project_identity.yaml` identifies this repository as the authoritative Canon EOS R5 source project. Its camera identity must agree with `00 Master/baseline.yaml`.
- Reject roots or parent folders marked as old, backup, archive, build output, generated output, or native wrapper locations. Reject incomplete or generated-only roots and stop for project-owner direction rather than searching for a substitute.
- Required source components, Git-root identity, current-working-directory containment, prohibited path markers, and camera identity are source-validation requirements.
- Preserve the established baseline + overrides architecture and existing YAML structure.
- Distinguish five evidence classes in camera-control documentation: verified Canon capability, owner-confirmed current configuration, approved target pending physical verification, project recommendation, and unresolved item.
- Do not treat approved targets, historical screenshots, inferred icon meanings, or recommendations as proof of the current camera configuration.
- Explain the rationale and obtain explicit project-owner approval before changing an established architecture.
- Present proposed changes and affected files for review before modifying the reference.
- For each new change task, present a clear recommendation, rationale, and affected files, then request approval as a separate explicit question. Once approved, treat that recommended scope as authorized without requiring the project owner to repeat it. Read-only questions and status checks do not require change approval.
- Shared behavior and shared camera settings belong in `00 Master/baseline.yaml`.
- The operational baseline and Camera Defaults card are the general-purpose starting state: Fv with shutter and aperture on Auto, Servo AF with Case A (Auto), Tracking Sensitivity and Accel./Decel. tracking on Auto, Switching tracked subjects set to On subject, Face + Tracking, Animals, Eye Detection enabled, High Speed Continuous, High speed display enabled, EFCS, and Mode 1 stabilization. Registered C1 Wildlife intentionally overrides only its specialized Servo Case values; neutral, deliberate-point, static, manual-focus, or other specialized profiles express their differences as overrides.
- Subject profiles inherit the baseline and contain only necessary overrides.
- The build resolves baseline and profile data before rendering.
- Presentation and rendering decisions belong in build code and templates, not profile YAML.
- `00 Master/my_menu_colors.yaml` owns the curated card-color palette and named My Menu tab assignments. These project presentation settings are global and must not be duplicated in profiles or treated as proof of the physical camera's tab configuration.
- `00 Master/my_menu.yaml` owns the approved EOS R5 My Menu tab names and ordered item identities. It is separate from presentation colors and from proof of the physical camera's current state.
- Explanatory and educational content belongs in field-guide appendices; profiles reference it rather than duplicate it.
- Permanent reference cards remain separate from shooting profiles.
- A permanent reference card may declare `reference_source: my_menu`; its rows are derived from `00 Master/my_menu.yaml` and the Canon settings catalog at render time so persisted My Menu content is not duplicated in profile YAML.
- The physical button and dial layout is shared across subject profiles.
- Subject profiles define complete shooting environments. C1, C2, and C3 are camera-side implementations of the canonical `Wildlife`, `Birds in Flight`, and `Landscape` profiles rather than independent AF presets. Field labels such as **General Wildlife** and **Birds in Flight / Action** may describe use, but machine-readable mappings retain the exact canonical profile title.
- The selected profile owns the initial AF Operation, Subject Detection, Eye Detection, exposure, drive, stabilization, and other subject-specific settings.
- AF-ON and AE Lock keep constant focusing roles across profiles. AF-ON temporarily selects Face + Tracking for intelligent acquisition; AE Lock temporarily selects 1-Point AF for precise placement. Both maintain the current AF Operation and Servo AF characteristics.
- The DOF button remains the One-Shot AF ↔ Servo AF control. AF-ON and AE Lock must not force an AF Operation that would defeat the selected profile state or a DOF-button change.
- Subject Detection belongs to the profile, not to either AF-start button. A deliberate-point AF method may make Subject Detection or Eye Detection inapplicable without changing their stored profile values.
- Servo AF Case, Tracking Sensitivity, and Accel./Decel. tracking belong to the shooting profile. Case A (Auto) with both parameters on Auto is the shared baseline. Case 1 is configured once as the project preset at Tracking Sensitivity -1 and Accel./Decel. tracking +1; Wildlife, Birds Perched, and Sports select it. This is not Canon's factory Case 1 default of 0 / 0. Birds in Flight uses Case 4 at 0 / +1. The stored Case and parameters are inactive in One-Shot AF and Manual Focus.
- Switching tracked subjects is a separate profile-owned subject-selection setting. On subject is the shared baseline. It is meaningful with Face + Tracking, Zone AF, and Large Zone AF and is omitted from cards whose effective AF Method does not support it.
- High speed display is a shared set-and-forget display preference. Enable is the approved baseline target; cards show it only when the effective starting configuration uses regular High Speed Continuous or Electronic shutter.
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

- `00 Master/project_identity.yaml` is the machine-readable repository identity.
- `80 Build/validators/project_identity_validator.py` checks the Git root, current working directory, prohibited path markers, required authoritative components, identity fields, and baseline camera agreement.
- `00 Master/baseline.yaml` is the shared-default source.
- `00 Master/schema.yaml` documents the intended YAML fields and value shapes.
- `00 Master/my_menu_colors.yaml` defines reusable named-tab card colors; `80 Build/my_menu_colors.py` validates and resolves them for renderers and the editor.
- `00 Master/my_menu.yaml` and `80 Build/my_menu.py` define and validate the persisted My Menu layout; `80 Build/my_menu_reference.py` materializes that layout for HTML, PDF, and editor reference previews.
- `80 Build/validators/baseline_validator.py` checks baseline shape.
- `80 Build/validators/profile_validator.py` checks inheritance, override paths, and compatible types.
- `80 Build/validators/structure.py` checks required architectural files and folders.
- `80 Build/validators/yaml_validator.py` checks parseability and top-level YAML shape.
- `build.py` and files under `80 Build/` implement merging, rendering, and output flow.

The Markdown specification is authoritative for intent; the listed configuration and validators are executable enforcement. A discrepancy is a defect to resolve, not permission to silently change behavior.
