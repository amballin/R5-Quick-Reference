# Photography Reference System — Project Memory

## Purpose and Authority

This file preserves stable project context, intent, rationale, terminology, and architectural history. It is not a duplicate rulebook. Governance and precedence are defined in [`PROJECT_RULES.md`](../PROJECT_RULES.md); normative details are defined in [`specifications/`](specifications/).

The repository is the permanent source of truth; conversation history is not. When permanent context changes, update this file in the same change, but place new binding requirements in the governing rules, an applicable specification, or an Accepted decision.

## Project Intent

The Photography Reference System produces Canon EOS R5 subject-setting cards, field-guide appendices, an installable web app, GitHub Pages output, and an optional native iOS wrapper. Cards are concise, field-ready quick references; appendices contain explanation and education.

The project is intentionally evolutionary. Consistency, minimal changes, reuse, and backward compatibility are preferred over theoretical elegance. Research normally happens outside the repository, while a feature conversation owns a deliverable from idea through implementation. The Master Planner maintains roadmap and priorities and protects architectural consistency.

## Architectural History and Rationale

The established design is **Baseline + Overrides**. Shared defaults live once in the baseline; profiles describe subject-specific differences. The build merges both sources before rendering, which prevents drift and lets cards show inherited settings without copying them into profile files.

Rendering is separated from profile data so presentation can evolve without restructuring shooting data. Educational content is separated into appendices so profiles remain concise and explanations have a single home. Permanent reference cards remain distinct from shooting profiles.

The generated site uses the machine-local workspace's `Build Output/merged-build/` as its canonical web/PWA bundle. It is mirrored to top-level `docs/` because GitHub Pages is configured for `main / docs`; `Build Output/website/` is optional machine-local staging and feeds `Native Wrapper/Website/`, exposed through `ios/Resources/Website`, only for the native wrapper workflow. PDF generation is intentionally opt-in.

## Domain Context and Terminology

- Use Canon terminology and prefer official Canon names, icons, and descriptions.
- The primary camera context is the Canon EOS R5; firmware context is recorded in the baseline.
- Stabilization mode, in-body image stabilization (IBIS), and lens optical stabilization (Lens IS) are distinct camera/lens concepts even when a card combines their presentation.
- “Profile” means a subject or shooting-situation YAML override that inherits from the baseline.
- “Card” means a generated quick-reference view of fully merged settings.
- “Appendix” means explanatory field-guide source content declared by the appendix manifest.
- “Release” means inclusion in the offline iPhone/PWA bundle, controlled independently for profiles and appendices.

## Stable Workflow Context

```text
Research (outside the project)
    -> Feature conversation (one deliverable)
    -> Repository implementation
    -> Rules/specification/decision/context updates when warranted
```

Firmware changes are treated cautiously: confirm new camera behavior, decide whether it changes shared defaults, review profile overrides, assets, rendered results, and record significant decisions.

## Governing References

- [`PROJECT_RULES.md`](../PROJECT_RULES.md)
- [`00 Master/specifications/`](specifications/)
- [`00 Master/decision-log.md`](decision-log.md)
- [`00 Master/baseline.yaml`](baseline.yaml)
- [`00 Master/schema.yaml`](schema.yaml)
- [`00 Master/card_layout.yaml`](card_layout.yaml)
- [`50 Field Guide/required_appendices.yaml`](../50%20Field%20Guide/required_appendices.yaml)
