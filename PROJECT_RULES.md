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

## Project Identity and Workspace Safety

Before reading project source beyond the governing and identity files, creating a backup, running a build, or modifying any file:

1. Resolve the current Git repository root with `git rev-parse --show-toplevel`. Treat that resolved path as the only project root for the task.
2. Display the resolved project root to the project owner before editing.
3. Confirm the current working directory is inside that Git root.
4. Do not locate, select, or switch to another repository automatically.
5. Do not search sibling directories to find a better, newer, or similarly named copy.
6. Reject the repository if its root or any parent folder is named or clearly marked `OLD`, `Backup`, `Backups`, `Archive`, `Archives`, `Build Output`, `Generated`, `Generated Output`, or `Native Wrapper`.
7. Confirm `00 Master/project_identity.yaml` identifies the project as **Canon EOS R5 Camera Reference**, with repository role **authoritative-source** and artifact type **source-repository**.
8. Confirm these authoritative components exist inside the resolved root: `PROJECT_RULES.md`, `00 Master/baseline.yaml`, `00 Master/schema.yaml`, `00 Master/card_layout.yaml`, `00 Master/setting_access.yaml`, `10 Profiles/`, `20 Templates/`, `50 Field Guide/required_appendices.yaml`, `50 Field Guide/Appendices/R5 Quick Reference.md`, `80 Build/build.py`, and `80 Build/validator.py`.
9. Confirm the baseline camera manufacturer and model are Canon and EOS R5 and agree with the project identity file.
10. Reject a repository that is empty, incomplete, generated-only, ambiguously identified, or missing any required authoritative component.
11. If any identity or authority check fails, stop and ask the project owner to open or identify the correct project. Never choose another project automatically.
12. After verification passes, restrict all source inspection and modification to the resolved Git root.
13. Inspect generated previews only in the output location derived by this repository's build system. Never treat generated output as source.
14. The only permitted write outside the source root is an in-scope machine-local artifact in a location required by this repository, including a recovery backup in the designated local-workspace `Backups/` directory.
15. Repeat project-identity verification whenever the working directory, repository, computer, worktree, or task context changes.

Before editing, report the resolved Git project root, project identity, camera model, prohibited-name result, authoritative-source result, and required-component result. No source file may be modified until every check passes.

## Non-Negotiable Working Rules

- Preserve the existing repository structure and improve it incrementally; do not redesign or change established architecture, YAML structure, naming, or workflow without first explaining the rationale and receiving explicit project-owner approval.
- Use the baseline + overrides architecture. Profiles inherit from the baseline, contain only differences from it, and never duplicate baseline settings.
- Clearly separate verified Canon capabilities, owner-confirmed current configuration, approved targets pending physical verification, project recommendations, and unresolved items. Never present an approved target, recommendation, or historical screenshot as verified current state.
- Present proposed reference or architectural changes, affected files, and intended changes for project-owner review before creating backups or modifying project files.
- Before modifying project files for each new change task, provide a clear recommendation with rationale and affected files, then ask a separate explicit approval question. Approval authorizes the recommended scope; the project owner does not need to restate it. Read-only questions and status checks do not require change approval.
- When a change affects an established command, workflow, or operator-facing procedure, review the relevant `WORKFLOWS` Markdown and `FINISH_DAY.md`. Before editing, identify whether those guides need updating and include the affected guide files in the proposed change scope; if no update is appropriate, state why.
- Keep rendering decisions in the build system, not profile YAML. Keep educational material in appendices rather than profiles.
- Preserve backward compatibility whenever practical. Identify conflicts instead of silently replacing established constraints.
- Keep generated files only in documented repository or machine-local output locations and source assets only in asset locations. Reuse existing assets whenever practical.
- Make the smallest change that satisfies the request. Do not modify unrelated work.
- Before changing project files, create a timestamped backup under the sibling local workspace's `Backups/` folder sufficient to restore the affected state.
- Validate relevant YAML, documentation references, project structure, and generated behavior before publishing.
- Publishing, committing, and pushing are separate explicit actions; do not perform them without authorization.
- Do not install or use the GitHub CLI (`gh`) for this project. Use the established local `git` commands for version control and `80 Build/scripts/publish.sh` for explicitly authorized website publishing. Do not introduce a replacement GitHub workflow or dependency without explicit project-owner approval.
- Before creating or switching to a new Git branch, explain why the branch may be useful, the risks and additional workflow steps it creates, and whether working directly on `main` is appropriate. Obtain explicit project-owner approval before creating or switching branches.
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
