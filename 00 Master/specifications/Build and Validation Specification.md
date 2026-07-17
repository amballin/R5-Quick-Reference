# Build and Validation Specification

## Build Workflow

- `python3 "80 Build/build.py"` is the normal full development build. It regenerates responsive HTML cards, field-guide HTML, the canonical merged web/PWA bundle, `docs/`, and reports; stale PNG and PDF folders are removed because both fixed formats are off by default. It does not change publish metadata, commit, push, or deploy.
- `./80 Build/scripts/publish.sh` is the only supported website publishing command. It runs an authorized publish-mode build, increments the minor version once, generates one timestamp, commits only `docs/` and finalized publish metadata through a temporary Git index, and pushes to the current branch.
- Development and test threads must never run the publishing script.
- `python3 "80 Build/build.py" --png` additionally creates fixed PNG cards and includes PNG actions in the generated site. `./80 Build/scripts/publish.sh --png` explicitly publishes them; the normal publish command omits them.
- `python3 "80 Build/build.py" --pdf` additionally creates current card and appendix PDFs.
- `python3 "80 Build/build.py" <profile>` preserves the existing single-profile workflow; run a full build before publishing.
- `python3 "80 Build/build.py" build website`, `build pages`, and `build ios` preserve their existing staging, Pages, and optional wrapper behaviors.
- Do not place rendering decisions in profile YAML or change build logic as a side effect of documentation/content work.

## Output and Release Behavior

- Disposable generated artifacts belong in the machine-local workspace's `Build Output/` folder. The default workspace is the sibling folder `<repository name> Local/`; `PRS_LOCAL_WORKSPACE` may set a different absolute or user-relative location.
- `Build Output/merged-build/` is the canonical generated web/PWA bundle. It contains released responsive cards under `Cards/*.html`, optional secondary PNGs under `Cards/*.png` only for a `--png` build, and copied card assets under `web-assets/`.
- `docs/` is an exact publishing mirror for GitHub Pages configured as `main / docs`.
- `Build Output/website/` is optional staging. The iOS target copies it into `Native Wrapper/Website/` in the local workspace and exposes that folder to Xcode through the ignored `ios/Resources/Website` symlink.
- Timestamped pre-change recovery backups belong under the local workspace's `Backups/` folder, not in the repository.
- Card and field-guide PDFs are opt-in.
- Profile and appendix release flags independently control inclusion in the offline bundle as defined by their specifications.
- Validate generated output before publishing. Publishing remains a manual, explicitly authorized Git operation.

## Computer Handoff

- Complete a unit of work on the computer where it began before continuing it elsewhere.
- Run relevant validation, commit every intentional source change, push the current branch, and verify a clean working tree before handoff.
- If a development build changed tracked `docs/` but publication is not intended, restore `docs/` to the current commit before the final clean-tree check. Disposable local output does not transfer through Git and is rebuilt on the next computer.
- Do not run the publishing workflow merely to move work between computers. Publish only when intentionally updating the live site, version, and timestamp.

## Validation Requirements

Run `python3 "80 Build/validator.py"` after relevant changes. It orchestrates validators for:

- project structure (`validators/structure.py`);
- YAML parseability and duplicate keys (`yaml_validator.py`);
- baseline shape (`baseline_validator.py`);
- card-layout structure and required-setting alignment (`card_layout_validator.py`);
- governing-document presence, local links, stale retired references, and decision statuses (`governance_validator.py`);
- appendix manifest/content relationships (`appendix_validator.py`);
- profile inheritance and overrides (`profile_validator.py`);
- assets/icons (`icon_validator.py`);
- Canon guide YAML (`canon_guides_validator.py`);
- generated artifacts (`output_validator.py`);
- merged PWA integrity (`pwa_validator.py`);
- supported links (`link_validator.py`).

Generated-output validation also checks responsive viewport metadata, local path portability, referenced HTML assets, released index/card correspondence, duplicate HTML IDs, and unresolved template text. PNG output counts are checked during an explicit `--png` build.

Run the dedicated `validators/validate_canon_r5_icons.py` when Canon icon reference data/assets change. For documentation consolidation, also search Markdown/YAML/code for stale paths and contradictory normative statements; the project validator does not validate documentation links or rule uniqueness comprehensively.

## Machine-Readable Sources and Enforcement Map

| File | Governs | Primary enforcement |
| --- | --- | --- |
| `00 Master/baseline.yaml` | Shared defaults and camera/workflow context | `baseline_validator.py`, `profile_validator.py`, `yaml_validator.py` |
| `00 Master/schema.yaml` | Intended profile/YAML field structure | `yaml_validator.py`; parts are enforced directly by `profile_validator.py` |
| `00 Master/card_layout.yaml` | Card-row display order plus always-shown rows and labels | `card_layout_validator.py`, `yaml_validator.py`; consumed by rendering/build code, with output review |
| `50 Field Guide/required_appendices.yaml` | Required appendices, sections, relationships, topics, exceptions, release flags | `appendix_validator.py`, rendering/build and PWA validation |

`80 Build/validator.py` is the validation entry point. A passing validator means its implemented checks passed; it does not replace visual card review, documentation-reference review, or review of requirements not yet encoded as checks.
