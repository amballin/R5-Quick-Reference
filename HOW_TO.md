# Photography Reference System How-To

For governing rules and authority, see [`PROJECT_RULES.md`](PROJECT_RULES.md). For normative architecture, profile, card, appendix, asset, and build requirements, see [`00 Master/specifications/`](00%20Master/specifications/). This guide contains operational procedures rather than duplicate governance.

## Build Locally

```bash
python3 "80 Build/build.py"
```

This regenerates the card outputs, guide pages, installable web app, and GitHub Pages folder without changing the published version or timestamp. It does not commit, push, or deploy. Development and test threads must use this command and must never run the publishing script.

Responsive HTML is the primary and default published phone card. PNG remains an opt-in fixed-size export. Both resolve from `00 Master/baseline.yaml` plus profile overrides—there is no separate content source.

Generated or refreshed:

- `../<repository folder name> Local/Build Output/cards/`
- `../<repository folder name> Local/Build Output/field-guide/`
- `../<repository folder name> Local/Build Output/merged-build/`
- `docs/`
- `../<repository folder name> Local/Build Output/reports/BUILD_REPORT.md`

The default build also removes stale generated PNGs and PDFs:

- `../<repository folder name> Local/Build Output/cards/png/`
- `../<repository folder name> Local/Build Output/cards/phone-png/`

- `../<repository folder name> Local/Build Output/cards/pdf/`
- `../<repository folder name> Local/Build Output/field-guide/pdf/`

## Optional PDFs

PDFs are off by default. To generate fresh card and guide PDFs:

```bash
python3 "80 Build/build.py" --pdf
```

PDF outputs are written to:

- `../<repository folder name> Local/Build Output/cards/pdf/`
- `../<repository folder name> Local/Build Output/field-guide/pdf/`

## Optional PNG Cards

PNG cards are off by default. To generate them and include secondary PNG actions in the local site:

```bash
python3 "80 Build/build.py" --png
```

They are written to `Build Output/cards/png/` and `Build Output/cards/phone-png/`.

## Current Folder Structure

| Folder | Purpose | Edit by hand? |
| --- | --- | --- |
| `00 Master/` | Baseline camera settings, schema, layout rules, and decision log. | Yes |
| `10 Profiles/` | Subject/profile YAML files such as Wildlife, Sports, Landscape. | Yes |
| `20 Templates/` | `card.html` controls responsive HTML card layout and styling. | Yes, carefully |
| `40 Assets/` | Legacy colors and fonts only; old Canon icon cheatsheet images moved to `60 Assets/icons/cheatsheet/`. | Rarely |
| `50 Field Guide/Appendices/` | Editable field-guide source pages. | Yes |
| `50 Field Guide/Setting Deep Dives/` | Editable focused guides for individual settings or tightly scoped features. | Yes |
| `60 Assets/` | Source visual assets used by cards and guides: active card icons in `icons/card_icons/`, official Canon R5 icons in `icons/canon_r5_official/`, cheatsheet reference pages in `icons/cheatsheet/`, and retained photography icons in `Photography Icons/`. | Yes |
| `60 Reference Tables/` | Empty placeholder. Remove later if no reference-table data is planned. | No |
| `70 Canon Guides/` | Canon guide source/extraction material. | Yes |
| `80 Build/` | Build, validation, PWA, iOS wrapper, extraction code, and fixed PNG presentation in `render_card_outputs.js`. | Yes, for tooling |
| `90 Testing/` | Test material and checks. | Yes, for tests |
| `data/` | Support data for the reference system. | Yes, carefully |
| `docs/` | Generated GitHub Pages publish folder. GitHub serves this. | No |
| `ios/` | Optional native Xcode wrapper project. Not required for Pages/browser/iPhone install. | Yes, if keeping native wrapper |
| `../<repository folder name> Local/Build Output/` | All disposable card, guide, PWA, website, PDF, and report output. | No |
| `../<repository folder name> Local/Backups/` | Timestamped pre-change recovery snapshots. | No |
| `../<repository folder name> Local/Native Wrapper/` | Generated website resources consumed by the optional Xcode wrapper. | No |

Everything under local `Build Output/` is rebuilt and safe to discard. The sibling local workspace is the default; set `PRS_LOCAL_WORKSPACE` when a different machine-local path is needed.

## Generated Site Flow

```text
../<repository folder name> Local/Build Output/merged-build/
        -> docs/        # GitHub Pages publishing copy
        -> ../<repository folder name> Local/Build Output/website/
              -> ../<repository folder name> Local/Native Wrapper/Website/
                    -> ios/Resources/Website symlink for Xcode
```

The normal build refreshes local `merged-build/` and repository `docs/`. The website and iOS targets create their disposable outputs in the local workspace.

Generated responsive cards are in `Build Output/cards/html/`. An explicit `--png` build adds fixed PNGs in `Build Output/cards/png/` and `Build Output/cards/phone-png/` and mirrors released PNGs into `docs/Cards/`. Generated icon copies are under `docs/web-assets/`. Source Canon icons remain in `60 Assets/icons/canon_r5_official/`, with SVG preferred and PNG used only when no SVG mapping is available.

## Control Field Guide and Setting Deep Dive Order

The published sections are controlled by each entry in `50 Field Guide/required_appendices.yaml`:

```yaml
- id: example_guide
  title: "Example Guide"
  file: "Appendices/Example Guide.md"
  content_type: field_guide
  release: true
  display_order: 20
```

- Use `content_type: field_guide` for the published **Field Guides** section and store the source under `50 Field Guide/Appendices/`.
- Use `content_type: setting_deep_dive` for the published **Deep Dive** section and store the source under `50 Field Guide/Setting Deep Dives/`.
- Use `release: true` to list the entry on the published index.
- Use `display_order` to control its position within its own section. Lower numbers appear first, equal numbers sort alphabetically, and an omitted value defaults to `100`.
- Leave gaps such as `10`, `20`, and `30` so another entry can be inserted later without renumbering the entire section.

After changing classification or order, run the validator and normal build, then review both published sections in `docs/index.html`.

## Control Card Category and Order

Use `display_category` and `display_order` in a profile YAML file to control index placement without changing how the card inherits or renders settings:

```yaml
display_category: reference
display_order: 20
```

- `display_category: subject` places the card under **Subjects**.
- `display_category: reference` places the card under **Reference Cards**.
- Lower `display_order` values appear first within the category; equal values sort alphabetically; omitted values default to `100`.
- Category affects index placement only. Keep `card_type: reference` for explicitly authored permanent references, and keep baseline-driven cards as normal profile cards.

## Work Safely on Two Macs

Each Mac has its own clone, dependencies, Git credentials, and sibling `<repository folder name> Local/` workspace. Git transfers repository files between Macs; disposable `Build Output/`, local backups, and native-wrapper output are rebuilt separately on each computer.

### Authenticate GitHub on Each Mac

The configured remote uses HTTPS. Enable the macOS Keychain credential helper once on each Mac:

```bash
git config --global credential.helper osxkeychain
```

At the first authenticated fetch or push, enter the GitHub username `amballin`. At the password prompt, enter a GitHub personal access token with access to `R5-Quick-Reference`, not the GitHub account password. Never paste a token into project files, a remote URL, documentation, or chat. A valid existing token may be reused if its repository access and expiration are appropriate.

### Before Starting Work

From the repository root, run:

```bash
./80\ Build/scripts/preflight-git.sh
```

The preflight script fetches `origin` with pruning, verifies that the branch is `main` with an upstream, compares local and remote history, and reports working-tree changes. Its outcomes are:

- **Clean and synchronized:** safe to begin.
- **Local changes:** continue only after confirming they belong to the work already in progress on this Mac.
- **Ahead:** local commits still need to be pushed before switching Macs.
- **Behind:** with a clean working tree, run `git pull --ff-only`, then rerun preflight.
- **Diverged or safety check failed:** stop for manual review; the scripts do not merge automatically.

For a status-only check at any time, run:

```bash
./80\ Build/scripts/git-status-report.sh
```

This report refreshes the remote comparison but does not pull, merge, commit, push, switch branches, or alter project files.

### Before Switching Macs

Run the interactive finish workflow:

```bash
./80\ Build/scripts/finish-day.sh
```

Depending on repository state, it offers to:

1. Run the documented validator, normal development build, and post-build validator.
2. Back up regenerated `docs/` and restore them to `HEAD`, with confirmation, so Pages is not changed by the handoff.
3. Stage every remaining source change shown by `git status`.
4. Commit the staged source changes with a message you provide.
5. Push `main` to its configured upstream, provided no outgoing commit changes `docs/`.
6. Verify that the branch is clean and synchronized.

Read every prompt and review the complete file list before answering yes. The normal development build refreshes tracked `docs/`, but a handoff is not publication. With confirmation, `finish-day.sh` archives the full current `docs/` tree plus Git status and binary patches under the machine-local `Backups/` folder, restores tracked `docs/` to the current commit, removes only archived untracked generated files under `docs/`, and verifies that no Pages changes remain before staging source files. It refuses to push an existing unpushed commit containing `docs/` changes because correcting that safely requires manual commit-history review.

Do not switch Macs until `finish-day.sh` prints `FINISHED FOR TODAY: Safe to switch Macs.` On the other Mac, run `preflight-git.sh`; if it reports that the clean clone is behind, run `git pull --ff-only` and rerun preflight before editing.

Publishing is not required for a computer handoff. Run the publishing command only when intentionally updating the live Pages site, version, and timestamp.

## Why `docs/` Is Still Top Level

GitHub Pages branch publishing is configured as `main / docs`. That setting looks for a folder named `docs` at the repository root. Moving it under another folder would break the Pages setting unless GitHub Pages is reconfigured to a custom workflow.

The normal build creates `docs/` automatically for local review, but that does not authorize publication. Because Pages watches `main / docs`, any pushed commit that changes `docs/` may update the live site. Ordinary development and handoff commits must leave `docs/` unchanged.

## Pages Is The Primary Path

GitHub Pages is the simplest useful output because it works in:

- iPhone Safari
- iPad Safari
- desktop browsers
- Add to Home Screen installs

The Xcode wrapper is optional. It only adds a native app shell around the same web content. It is not needed for the Pages site or the Safari-installed app.

## Publish To GitHub Pages

1. Make sure the GitHub repo settings are:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

2. From the repository root, run the single official publishing command:

```bash
./80\ Build/scripts/publish.sh
```

This runs a fresh publish-mode build, increments the minor version, updates the timestamp, regenerates and validates `docs`, commits only `docs` and finalized publish metadata through a temporary Git index, and pushes the commit to the current branch.

This default publish omits PNG cards. To deliberately publish the optional PNG downloads, use:

```bash
./80\ Build/scripts/publish.sh --png
```

`./80 Build/scripts/publish.sh` is the only supported website publishing command. Do not run the internal `build.py --publish` mode directly. Development and test threads must never run the publishing script.

This is the publication control boundary: run the script only after explicitly deciding to update the live site. It performs the publish-mode build, validates generated output, updates version and timestamp metadata, commits only the approved Pages output and finalized publish metadata through a temporary Git index, and pushes that publication commit. A normal build, `finish-day.sh`, or an ordinary `git push` is not an authorized substitute.

Do not install or use the GitHub CLI (`gh`) for this project. Authorized commits and pushes use the existing local `git` workflow; authorized website publication uses the publishing script above.

3. Open:

```text
https://amballin.github.io/R5-Quick-Reference/
```

## Build One Profile

```bash
python3 "80 Build/build.py" "Camera Defaults"
python3 "80 Build/build.py" Wildlife
python3 "80 Build/build.py" "Birds in Flight"
```

Single-profile builds update HTML only by default. Add `--png` to update that card's PNG outputs. Run the full build before publishing.

## Build Website Only

For hosts that publish a selected output folder, such as Cloudflare Pages or Netlify:

```bash
python3 "80 Build/build.py" build website
```

Publish the optional website staging folder:

The generated folder is:

```text
../<repository folder name> Local/Build Output/website/
```

## Build Optional Native iOS Wrapper

Only use this if you decide to keep the native Xcode app shell:

```bash
python3 "80 Build/build.py" build ios
```

That command refreshes:

- `../<repository folder name> Local/Build Output/website/`
- `../<repository folder name> Local/Native Wrapper/Website/`
- the ignored `ios/Resources/Website` symlink used by Xcode

Normal Pages builds do not keep `ios/Resources/Website/` populated, so the top-level project does not carry another duplicate copy of the same site.

## Build GitHub Pages Folder Only

```bash
python3 "80 Build/build.py" build pages
```

This rebuilds the site and refreshes `docs/`.

## Install On iPhone

Open the live URL in Safari and tap a profile name for the responsive HTML version. If the site was deliberately published with `--png`, a smaller PNG action is also shown. To install the site, use Safari's Share button, choose **Add to Home Screen**, keep the `Camera Settings` name, and tap Add.

The first online visit registers the service worker and caches the generated cards, guide pages, icons, and supporting web assets. After that, the app can open without a network connection.

## Validate Project Integrity

```bash
python3 "80 Build/validator.py"
```

The validator checks project structure, YAML syntax, profile inheritance, baseline/override compatibility, icon assets, Canon guide YAML, links, and generated outputs.

## Extract Canon Guide Candidates

Use the guide extractor to convert a Canon guide into a draft profile candidate:

```bash
python3 "80 Build/extract_guide.py" --source "70 Canon Guides/Details/Some Guide.yaml" --name "Guide Name"
```

For a web page:

```bash
python3 "80 Build/extract_guide.py" --url "https://example.com/canon-guide" --name "Guide Name"
```

If you are refreshing an existing extraction folder, add `--force`:

```bash
python3 "80 Build/extract_guide.py" --source "70 Canon Guides/Details/Canon Fireworks.yaml" --name "Fireworks" --force
```

Extractor output is written under:

```text
70 Canon Guides/Extracted/<Guide Name>/
```

Each extraction folder should contain:

- `guide_summary.md`
- `guide_metadata.yaml`
- `profile_candidate.yaml`
- `extraction_report.md`
- `comparison_to_baseline.md`

## Firmware Changes

When camera firmware changes settings, menus, terminology, or behavior:

1. Update `00 Master/baseline.yaml` only after confirming the new setting should be part of the normal baseline.
2. Do not duplicate new baseline settings inside profiles.
3. Review every profile in `10 Profiles/` for overrides that may now be outdated.
4. Update `60 Assets/icon-map.yaml` only if setting names or icons changed.
5. Run `python3 "80 Build/validator.py"`.
6. Run `python3 "80 Build/build.py"`.
7. Review generated HTML cards. Add `--png` or `--pdf` only when those fixed outputs need to be refreshed.
8. Record the firmware-related decision in `00 Master/decision-log.md`.

Mark the entry `Proposed`, `Accepted`, `Superseded`, or `Rejected`; only `Accepted` decisions are binding. Follow the rule-change process in `PROJECT_RULES.md` when the firmware change affects architecture or permanent rules.
