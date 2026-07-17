# Photography Reference System How-To

For governing rules and authority, see [`PROJECT_RULES.md`](PROJECT_RULES.md). For normative architecture, profile, card, appendix, asset, and build requirements, see [`00 Master/specifications/`](00%20Master/specifications/). This guide contains operational procedures rather than duplicate governance.

## Build Locally

```bash
python3 "80 Build/build.py"
```

This regenerates the card outputs, guide pages, installable web app, and GitHub Pages folder without changing the published version or timestamp. It does not commit, push, or deploy. Development and test threads must use this command and must never run the publishing script.

Responsive HTML is the primary and default published phone card. PNG remains an opt-in fixed-size export. Both resolve from `00 Master/baseline.yaml` plus profile overrides—there is no separate content source.

Generated or refreshed:

- `../Photography Reference System Local/Build Output/cards/`
- `../Photography Reference System Local/Build Output/field-guide/`
- `../Photography Reference System Local/Build Output/merged-build/`
- `docs/`
- `../Photography Reference System Local/Build Output/reports/BUILD_REPORT.md`

The default build also removes stale generated PNGs and PDFs:

- `../Photography Reference System Local/Build Output/cards/png/`
- `../Photography Reference System Local/Build Output/cards/phone-png/`

- `../Photography Reference System Local/Build Output/cards/pdf/`
- `../Photography Reference System Local/Build Output/field-guide/pdf/`

## Optional PDFs

PDFs are off by default. To generate fresh card and guide PDFs:

```bash
python3 "80 Build/build.py" --pdf
```

PDF outputs are written to:

- `../Photography Reference System Local/Build Output/cards/pdf/`
- `../Photography Reference System Local/Build Output/field-guide/pdf/`

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
| `../Photography Reference System Local/Build Output/` | All disposable card, guide, PWA, website, PDF, and report output. | No |
| `../Photography Reference System Local/Backups/` | Timestamped pre-change recovery snapshots. | No |
| `../Photography Reference System Local/Native Wrapper/` | Generated website resources consumed by the optional Xcode wrapper. | No |

Everything under local `Build Output/` is rebuilt and safe to discard. The sibling local workspace is the default; set `PRS_LOCAL_WORKSPACE` when a different machine-local path is needed.

## Generated Site Flow

```text
../Photography Reference System Local/Build Output/merged-build/
        -> docs/        # GitHub Pages publishing copy
        -> ../Photography Reference System Local/Build Output/website/
              -> ../Photography Reference System Local/Native Wrapper/Website/
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

- Use `content_type: field_guide` for the **Field Guide** section and store the source under `50 Field Guide/Appendices/`.
- Use `content_type: setting_deep_dive` for the **Setting Deep Dives** section and store the source under `50 Field Guide/Setting Deep Dives/`.
- Use `release: true` to list the entry on the published index.
- Use `display_order` to control its position within its own section. Lower numbers appear first, equal numbers sort alphabetically, and an omitted value defaults to `100`.
- Leave gaps such as `10`, `20`, and `30` so another entry can be inserted later without renumbering the entire section.

After changing classification or order, run the validator and normal build, then review both published sections in `docs/index.html`.

## Continue Work on Another Computer

Finish the current unit of work before changing computers:

1. Run `python3 "80 Build/validator.py"`.
2. If this was only a development build, restore generated `docs/` changes with `git restore docs` so they are not mistaken for a release.
3. Commit all intentional source changes.
4. Push the current branch.
5. Confirm `git status --short` produces no output.

Publishing is not required for a computer handoff. Run the publishing command only when you intentionally want to update the live Pages site, version, and timestamp. Local build output is rebuilt on the next computer rather than transferred through Git.

## Why `docs/` Is Still Top Level

GitHub Pages branch publishing is configured as `main / docs`. That setting looks for a folder named `docs` at the repository root. Moving it under another folder would break the Pages setting unless GitHub Pages is reconfigured to a custom workflow.

The build already creates `docs/` automatically. The only manual part is publishing that folder to GitHub.

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
../Photography Reference System Local/Build Output/website/
```

## Build Optional Native iOS Wrapper

Only use this if you decide to keep the native Xcode app shell:

```bash
python3 "80 Build/build.py" build ios
```

That command refreshes:

- `../Photography Reference System Local/Build Output/website/`
- `../Photography Reference System Local/Native Wrapper/Website/`
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
