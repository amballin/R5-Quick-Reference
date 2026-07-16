# Photography Reference System Rules

This is the concise governing entry point for the repository. Detailed requirements live in the linked specifications; stable context lives in project memory; decisions live in the decision log.

## Authority and Precedence

When sources disagree, apply this order:

1. Explicit instructions approved by the project owner for the current change.
2. This file (`PROJECT_RULES.md`), including the non-negotiable rules and rule-change process.
3. The applicable document under [`00 Master/specifications/`](00%20Master/specifications/).
4. [`00 Master/decision-log.md`](00%20Master/decision-log.md), but only entries marked **Accepted**. A later Accepted decision supersedes an earlier one when stated explicitly.
5. Machine-readable configuration and validators identified by the applicable specification.
6. [`00 Master/project_memory.md`](00%20Master/project_memory.md), for stable context, intent, rationale, terminology, and architectural history.
7. `README.md`, `HOW_TO.md`, and other explanatory documentation.

Proposed, Rejected, and Superseded decisions are non-binding. Conversation history is not a permanent authority. If two binding sources still conflict, stop, preserve current behavior, and ask the project owner to resolve the conflict.

## Non-Negotiable Working Rules

- Preserve the existing repository structure and improve it incrementally; do not redesign architecture, YAML structure, naming, or workflow without explicit approval.
- Use the baseline + overrides architecture. Profiles inherit from the baseline, contain only differences from it, and never duplicate baseline settings.
- Keep rendering decisions in the build system, not profile YAML. Keep educational material in appendices rather than profiles.
- Preserve backward compatibility whenever practical. Identify conflicts instead of silently replacing established constraints.
- Keep generated files only in documented repository or machine-local output locations and source assets only in asset locations. Reuse existing assets whenever practical.
- Make the smallest change that satisfies the request. Do not modify unrelated work.
- Before changing project files, create a timestamped backup under the sibling local workspace's `Backups/` folder sufficient to restore the affected state.
- Validate relevant YAML, documentation references, project structure, and generated behavior before publishing.
- Publishing, committing, and pushing are separate explicit actions; do not perform them without authorization.
- Finish work on the computer where it began. Before continuing on another computer, validate, commit all intentional source changes, push the current branch, and leave the working tree clean. A computer handoff does not require publishing.

## Rule-Change Process

Architectural or permanent rule changes require explicit project-owner approval. For an approved change:

1. Create the required backup and preserve unrelated work.
2. Record the decision in the decision log as **Accepted** (or update an existing entry and mark any replaced decision **Superseded**).
3. Update this file if authority, precedence, or a non-negotiable rule changed.
4. Update exactly one applicable specification for each normative detail; update machine-readable configuration and validators when enforcement changes.
5. Update project memory only for stable context, intent, rationale, terminology, or architectural history—not duplicated requirements.
6. Update operational and overview links, run validation, and check for stale or contradictory statements.

## Specifications

- [Architecture](00%20Master/specifications/Architecture.md)
- [Profile Specification](00%20Master/specifications/Profile%20Specification.md)
- [Card Specification](00%20Master/specifications/Card%20Specification.md)
- [Appendix Specification](00%20Master/specifications/Appendix%20Specification.md)
- [Asset Specification](00%20Master/specifications/Asset%20Specification.md)
- [Build and Validation Specification](00%20Master/specifications/Build%20and%20Validation%20Specification.md)

See also [project memory](00%20Master/project_memory.md) and the [decision log](00%20Master/decision-log.md).
