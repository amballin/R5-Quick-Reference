# Agent Entry Point

Before analyzing, building, or changing this repository, read and follow
[`PROJECT_RULES.md`](PROJECT_RULES.md). It defines governing authority,
required backups, validation, and publishing restrictions.

Treat the Git repository root discovered at runtime as the project root. Do
not depend on an absolute filesystem path or an older checkout location.

Choose validation in proportion to the affected surface. For a narrow source
change that cannot affect generated behavior, use the relevant targeted check
or source-only validation. Release-note-only changes require source-only
validation, not a development build.

When a change can affect generated cards, guides, downloads, the PWA, or build
behavior—or at an integration, handoff, or Finish Day checkpoint—run this
sequence from the repository root:

```bash
python3 "80 Build/validator.py" --source-only &&
python3 "80 Build/build.py" &&
python3 "80 Build/validator.py"
```

Do not repeat an unchanged full build unless inputs changed, a previous check
failed, or the task specifically tests deterministic/reproducible generation.
Publication uses the supported publish-mode build and verification; it does not
require an additional unchanged development build immediately beforehand.

Never publish, commit, or push unless the project owner explicitly requests
that separate action.
