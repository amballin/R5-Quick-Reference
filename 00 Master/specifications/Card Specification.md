# Card Specification

## Scope

This specification governs generated quick-reference card content and conditional rendering.

## Required Quick-Reference Settings

Cards use `card_type: profile` by default. Profile cards inherit the baseline and render merged camera settings. Permanent reference cards use `card_type: reference`, do not inherit the baseline or define overrides, and render their `reference_settings` entries as a two-column **Settings** table.

Each `reference_settings` entry contains a non-empty `control` and `assignment`. Reference-card checklists contain concise recommendations or verification steps rather than repeating the Settings table.

Cards may define `appendix_links` as a list of manifest appendix IDs with optional display labels. Renderers resolve these IDs for each output context; profile YAML must not contain generated-output paths.

Cards render required settings from fully merged baseline + profile data, including inherited values:

- `exposure.mode`
- `autofocus.operation`
- `autofocus.subject_detection`
- `autofocus.eye_detection`
- `autofocus.method`
- `drive.mode`
- `shutter.target`
- `lens.aperture.target`
- `stabilization.image_stabilization.mode`
- `exposure.iso.mode`
- `exposure.auto_iso.maximum`

If a required merged value is unset, render the row with `—` rather than omitting it or inventing a camera setting.

`00 Master/card_layout.yaml` may define additional always-shown settings; those remain part of current card behavior.

## Rendering Requirements

- Render ISO as one quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays the fixed value. Do not collapse the underlying fields.
- When both are shown, render IBIS and Lens IS as one `IBIS/Lens IS` quick-reference row. Do not collapse the underlying fields.
- When AF Operation is `Manual Focus`, omit AF Method, Subject Detection, and Eye Detection.
- When AF Method is `Not Used`, omit Subject Detection and Eye Detection.
- Preserve existing card formats, filenames, proportions/behavior, output locations, and backward compatibility unless explicitly approved.
- Card styling and conditional presentation are renderer concerns, not profile-data concerns.

## Release Requirement

Only profiles with `metadata.release: true` are included as cards in the offline iPhone/PWA bundle. Other generated development outputs may still exist.

Released profile cards appear under **Subject Cards**. Released permanent reference cards appear under **Reference Cards**.

## Enforcement and Evidence

- `00 Master/card_layout.yaml` is the machine-readable list of always-shown card rows and labels.
- `00 Master/baseline.yaml` and profile YAML supply merged values.
- Card renderers and templates under `80 Build/` and `20 Templates/` implement formatting and conditional rows.
- `80 Build/validators/output_validator.py` checks expected generated card artifacts.
- `80 Build/validators/pwa_validator.py` checks the merged offline bundle.
- Profile validation checks that every `appendix_links` ID exists in the appendix manifest.

Not every conditional rendering rule has a dedicated validator; visual/generated-output review remains required after relevant changes.
