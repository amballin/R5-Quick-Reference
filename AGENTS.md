# Agent Entry Point

Before analyzing, building, or changing this repository, read and follow
[`PROJECT_RULES.md`](PROJECT_RULES.md). It defines governing authority,
required backups, validation, and publishing restrictions.

Treat the Git repository root discovered at runtime as the project root. Do
not depend on an absolute filesystem path or an older checkout location.

For ordinary local validation and builds, run commands from that repository
root:

```bash
python3 "80 Build/validator.py"
python3 "80 Build/build.py"
```

Never publish, commit, or push unless the project owner explicitly requests
that separate action.
