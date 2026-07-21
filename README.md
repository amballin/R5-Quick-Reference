# Photography Reference System

Responsive HTML is the primary and default published phone format. Each released profile opens as a crisp, width-responsive card from the Camera Settings page. Fixed PNG cards remain optional exports for Photos, sharing, wallpaper, and offline files; use `--png` when they are wanted. Both formats use the same baseline-plus-overrides YAML data.

This project builds Canon R5 subject-setting cards, guide pages, an installable web app, and the `docs/` folder served by GitHub Pages.

The primary delivery path is GitHub Pages. That works in phone, iPad, and desktop browsers, and can be installed from Safari with Add to Home Screen.

## Set Up on Another Computer

Install Git, Python 3, Node.js, and npm, then clone the repository and install its JavaScript dependencies:

```bash
git clone https://github.com/amballin/R5-Quick-Reference.git
cd R5-Quick-Reference
npm install
python3 "80 Build/validator.py"
python3 "80 Build/build.py"
```

The repository contains the editable profiles, reference cards, appendices, templates, build code, assets, and published `docs/` site. Disposable build output, backups, reports, and native-wrapper resources live in the sibling `<repository folder name> Local/` workspace and can be recreated or managed independently.

Each Mac needs its own GitHub authentication. For this HTTPS remote, configure the macOS Keychain helper with `git config --global credential.helper osxkeychain`. When Git first prompts, use the GitHub username `amballin` and a personal access token as the password; never store the token in the repository.

Use the repository's handoff scripts from the project root:

```bash
./80\ Build/scripts/preflight-git.sh       # before starting work on a Mac
./80\ Build/scripts/git-status-report.sh  # inspect local and remote state
./80\ Build/scripts/finish-day.sh         # finish before switching Macs
```

`preflight-git.sh` refreshes `origin` and blocks work when the clone is behind or diverged. `finish-day.sh` is interactive and can validate, build, separate generated `docs/`, stage source changes, commit, and push only after confirmation. It backs up changed `docs/` in the machine-local workspace and restores them to `HEAD` so the handoff commit cannot publish Pages. It also refuses to push an older unpushed commit containing `docs/` changes. Review its complete change list before approving staging. Do not switch Macs until the final report says the working tree is clean and synchronized. See [`HOW_TO.md`](HOW_TO.md) for the full workflow.

Project governance starts in [`PROJECT_RULES.md`](PROJECT_RULES.md). Detailed technical requirements are under [`00 Master/specifications/`](00%20Master/specifications/), while operational procedures are in [`HOW_TO.md`](HOW_TO.md).

## Build locally

```bash
python3 "80 Build/build.py"
```

This rebuilds local outputs without changing the published version or timestamp. It does not commit, push, or deploy. Development and test threads must use this command and must never run the publishing script.

The default build omits and removes stale fixed PNG and PDF output. Both are off by default.

To create fixed PNG cards and include their secondary index links:

```bash
python3 "80 Build/build.py" --png
```

To create fresh PDFs only when you actually need them:

```bash
python3 "80 Build/build.py" --pdf
```

## Publish the website

```bash
./80\ Build/scripts/publish.sh
```

This runs a fresh publish build, increments the minor version, updates the publish timestamp, regenerates `docs`, commits the release, and pushes it to the current branch on GitHub.

The normal publish contains responsive HTML only. Use `./80\ Build/scripts/publish.sh --png` only when PNG downloads should also be published.

The version/publish footer appears only on the main Camera Settings index in the form `Format v1.xx • yyyy/mm/dd hh:mm AM/PM`; individual HTML and PNG cards do not include it.

`./80 Build/scripts/publish.sh` is the only supported publishing command. The internal `build.py --publish` mode cannot be run directly.

GitHub Pages watches `main / docs`. Consequently, any push to `main` that changes `docs/` can update the live site, regardless of which Git command created the commit. Keep `docs/` out of ordinary development and computer-handoff commits. The supported publish script is the deliberate control point: it performs the publish-mode build, validates the output, updates publish metadata, commits the approved Pages files, and pushes them. Run it only when you explicitly intend to publish.

GitHub Pages must be configured to publish from:

```text
main / docs
```

Live URL:

```text
https://amballin.github.io/R5-Quick-Reference/
```

Standalone field-guide pages get their `← Back` button from the shared site navigation.
Links from cards and between generated appendix pages carry a validated internal return target;
pages opened directly fall back to the repository's `index.html` without a hardcoded GitHub Pages URL.
Set `navigation: false` on an entry in `50 Field Guide/required_appendices.yaml` to disable the
button for that page. The button is omitted from embedded index content and hidden for print and
output-mode rendering.

## Folder Map

Source folders:

- `00 Master/`: baseline camera settings, schema, layout rules, and decision log.
- `10 Profiles/`: editable subject/profile YAML files such as Wildlife, Sports, Landscape.
- `20 Templates/`: editable card HTML/style templates.
- `50 Field Guide/Appendices/`: editable guide source pages.
- `60 Assets/`: source visual assets used by cards and guides, including `60 Assets/icons/`.
- `70 Canon Guides/`: Canon guide source and extraction material.
- `80 Build/`: build, validation, PWA, iOS wrapper, and extraction code.
- `ios/`: native Xcode wrapper project.

Generated folders:

- `../<repository folder name> Local/Build Output/cards/html/`: generated responsive HTML for every profile.
- `../<repository folder name> Local/Build Output/cards/png/` and `cards/phone-png/`: optional fixed PNG exports from a `--png` build.
- `../<repository folder name> Local/Build Output/field-guide/`: generated guide HTML, search index, and optional PDFs.
- `../<repository folder name> Local/Build Output/merged-build/`: canonical generated web/PWA bundle.
- `../<repository folder name> Local/Build Output/website/`: optional staging copy for non-GitHub hosts and the native iOS wrapper.
- `../<repository folder name> Local/Build Output/reports/`: generated build and validation reports.
- `../<repository folder name> Local/Backups/`: timestamped pre-change recovery snapshots.
- `docs/`: generated GitHub Pages publish folder. GitHub serves this folder.

`20 Templates/card.html` controls responsive HTML presentation. `80 Build/render_card_outputs.js` independently controls fixed PNG rendering, so responsive layout changes do not change the PNG canvas. Canon icons remain authoritative in `60 Assets/icons/canon_r5_official/`; icon selection prefers SVG and falls back to PNG. The build copies only required published assets into `docs/web-assets/` with relative paths.

Everything under `Build Output/` is disposable and can be regenerated by a full build. Set `PRS_LOCAL_WORKSPACE` to override the default sibling workspace location.

Generated site flow:

```text
../<repository folder name> Local/Build Output/merged-build/
        -> docs/        # GitHub Pages publishing copy
        -> ../<repository folder name> Local/Build Output/website/
              -> ../<repository folder name> Local/Native Wrapper/Website/
                    -> ios/Resources/Website symlink for Xcode
```

The normal build refreshes the local `merged-build/` and repository `docs/`. The `build website` target also creates local website staging. The `build ios` target creates local native-wrapper resources and an ignored repository symlink for Xcode.

Asset support folders:

- `60 Assets/icons/card_icons/`: active card setting icons used by generated cards and quick references.
- `60 Assets/icons/canon_r5_official/`: official Canon EOS R5 icons extracted from Canon manual assets.
- `60 Assets/icons/cheatsheet/`: static Canon icon reference/cheatsheet pages preserved from the older asset set.
- `60 Assets/Photography Icons/`: retained photography icon collection; not the active card icon source.
- `60 Reference Tables/`: currently empty; keep only if reference-table source data is added.
- `data/`: support data used by the reference system.

## iPhone Install

Open the live URL in Safari, select a profile to open its responsive HTML card, then use Share -> Add to Home Screen. The installed site is labeled `Camera Settings`. PNG links appear only when the site was explicitly published with `--png`.

The first online visit caches the cards, guide pages, icons, and supporting assets for offline use.

## Optional Native iOS Wrapper

The Xcode wrapper in `ios/` is not required for GitHub Pages, Safari, iPhone, iPad, or desktop browser use. Keep it only if you later want an actual native iOS app shell around the same web content.

To refresh and build that optional wrapper:

```bash
python3 "80 Build/build.py" build ios
```
