# Photography Reference System How-To

## Build Everything

```bash
python3 build.py
```

This regenerates the card outputs, guide pages, installable web app, and GitHub Pages folder.

Generated or refreshed:

- `output/cards/`
- `output/field-guide/`
- `output/merged-build/`
- `docs/`
- `output/reports/BUILD_REPORT.md`

The default build also removes stale generated PDFs:

- `output/cards/pdf/`
- `output/field-guide/pdf/`

## Optional PDFs

PDFs are off by default. To generate fresh card and guide PDFs:

```bash
python3 build.py --pdf
```

PDF outputs are written to:

- `output/cards/pdf/`
- `output/field-guide/pdf/`

## Current Folder Structure

| Folder | Purpose | Edit by hand? |
| --- | --- | --- |
| `00 Master/` | Baseline camera settings, schema, layout rules, and decision log. | Yes |
| `10 Profiles/` | Subject/profile YAML files such as Wildlife, Sports, Landscape. | Yes |
| `20 Templates/` | Card HTML/style templates used by the renderer. | Yes, carefully |
| `40 Assets/` | Older static Canon icon reference images. Keep until confirmed unused. | Rarely |
| `50 Field Guide/Appendices/` | Editable field-guide source pages. | Yes |
| `60 Assets/` | Source visual assets used by cards and guides, including `60 Assets/icons/`. | Yes |
| `60 Reference Tables/` | Empty placeholder. Remove later if no reference-table data is planned. | No |
| `70 Canon Guides/` | Canon guide source/extraction material. | Yes |
| `80 Build/` | Build, validation, PWA, iOS wrapper, and extraction code. | Yes, for tooling |
| `90 Testing/` | Test material and checks. | Yes, for tests |
| `data/` | Support data for the reference system. | Yes, carefully |
| `docs/` | Generated GitHub Pages publish folder. GitHub serves this. | No |
| `ios/` | Optional native Xcode wrapper project. Not required for Pages/browser/iPhone install. | Yes, if keeping native wrapper |
| `output/cards/` | Generated card artifacts. Disposable. | No |
| `output/field-guide/` | Generated guide HTML, search index, and optional PDFs. Disposable. | No |
| `output/merged-build/` | Canonical generated web/PWA bundle. Disposable. | No |
| `output/reports/` | Generated build, validation, and cleanup reports. | No |
| `output/website/` | Optional generated staging copy for non-GitHub hosts and native iOS wrapping. Disposable. | No |

Everything under `output/` is rebuilt and safe to discard.

## Generated Site Flow

```text
output/merged-build/   # canonical generated web/PWA bundle
        -> docs/        # GitHub Pages publishing copy
        -> output/website/
              -> ios/Resources/Website/ when building the native iOS wrapper
```

The normal build refreshes `output/merged-build/` and `docs/`. The `build website` target also creates `output/website/`. The `build ios` target copies `output/website/` into `ios/Resources/Website/` for Xcode.

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

## Why Publish Is Manual

The local build can safely create the exact files GitHub Pages needs, but pushing to GitHub changes the public website and requires your GitHub authentication. Keeping that last step manual prevents accidental public updates.

## Publish To GitHub Pages

1. Make sure the GitHub repo settings are:

```text
Source: Deploy from a branch
Branch: main
Folder: /docs
```

2. Build the local project:

```bash
python3 build.py
```

3. Copy or sync the generated `docs/` folder into the GitHub repo if the build project and GitHub repo are separate folders.

4. From the GitHub repo folder, publish:

```bash
git status
git add docs
git commit -m "Update published reference"
git push origin main
```

5. Open:

```text
https://amballin.github.io/R5-Quick-Reference/
```

## Build One Profile

```bash
python3 build.py "Camera Defaults"
python3 build.py Wildlife
python3 build.py "Birds in Flight"
```

Single-profile builds update that card's HTML/PNG outputs. Run the full build before publishing.

## Build Website Only

For hosts that publish a selected output folder, such as Cloudflare Pages or Netlify:

```bash
python3 build.py build website
```

Publish the optional website staging folder:

The generated folder is:

```text
output/website/
```

## Build Optional Native iOS Wrapper

Only use this if you decide to keep the native Xcode app shell:

```bash
python3 build.py build ios
```

That command refreshes:

- `output/website/`
- `ios/Resources/Website/`

Normal Pages builds do not keep `ios/Resources/Website/` populated, so the top-level project does not carry another duplicate copy of the same site.

## Build GitHub Pages Folder Only

```bash
python3 build.py build pages
```

This rebuilds the site and refreshes `docs/`.

## Install On iPhone

Open the live URL in Safari, then use Share -> Add to Home Screen. The installed app is labeled `Settings by Subject`.

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
6. Run `python3 build.py`.
7. Review generated HTML/PNG cards. Add `--pdf` only if PDFs need to be refreshed.
8. Record the firmware-related decision in `00 Master/decision-log.md`.
