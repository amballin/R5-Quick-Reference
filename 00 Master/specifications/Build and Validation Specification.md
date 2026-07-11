# Build and Validation Specification

## Build Workflow

- `python3 build.py` is the normal full build. It regenerates cards, field-guide HTML, the canonical merged web/PWA bundle, `docs/`, and reports; stale PDF folders are removed because PDFs are off by default.
- `python3 build.py --pdf` additionally creates current card and appendix PDFs.
- `python3 build.py <profile>` preserves the existing single-profile workflow; run a full build before publishing.
- `python3 build.py build website`, `build pages`, and `build ios` preserve their existing staging, Pages, and optional wrapper behaviors.
- Do not place rendering decisions in profile YAML or change build logic as a side effect of documentation/content work.

## Output and Release Behavior

- Generated artifacts belong under `output/` or `docs/`, except the optional generated native-wrapper copy at `ios/Resources/Website/`.
- `output/merged-build/` is the canonical generated web/PWA bundle.
- `docs/` is an exact publishing mirror for GitHub Pages configured as `main / docs`.
- `output/website/` is optional staging and is copied into `ios/Resources/Website/` by the iOS build target.
- Card and field-guide PDFs are opt-in.
- Profile and appendix release flags independently control inclusion in the offline bundle as defined by their specifications.
- Validate generated output before publishing. Publishing remains a manual, explicitly authorized Git operation.

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

Run the dedicated `validators/validate_canon_r5_icons.py` when Canon icon reference data/assets change. For documentation consolidation, also search Markdown/YAML/code for stale paths and contradictory normative statements; the project validator does not validate documentation links or rule uniqueness comprehensively.

## Machine-Readable Sources and Enforcement Map

| File | Governs | Primary enforcement |
| --- | --- | --- |
| `00 Master/baseline.yaml` | Shared defaults and camera/workflow context | `baseline_validator.py`, `profile_validator.py`, `yaml_validator.py` |
| `00 Master/schema.yaml` | Intended profile/YAML field structure | `yaml_validator.py`; parts are enforced directly by `profile_validator.py` |
| `00 Master/card_layout.yaml` | Always-shown card rows and labels | `card_layout_validator.py`, `yaml_validator.py`; consumed by rendering/build code, with output review |
| `50 Field Guide/required_appendices.yaml` | Required appendices, sections, relationships, topics, exceptions, release flags | `appendix_validator.py`, rendering/build and PWA validation |

`80 Build/validator.py` is the validation entry point. A passing validator means its implemented checks passed; it does not replace visual card review, documentation-reference review, or review of requirements not yet encoded as checks.
