# Card Specification

## Scope

This specification governs generated quick-reference card content and conditional rendering.

## Required Quick-Reference Settings

Cards use `card_type: profile` by default. Profile cards inherit the baseline and render merged camera settings. Permanent reference cards use `card_type: reference`, do not inherit the baseline or define overrides, and render their `reference_settings` entries as a two-column **Settings** table.

Each `reference_settings` entry contains a non-empty `control` and `assignment`. Reference-card checklists contain concise recommendations or verification steps rather than repeating the Settings table.

Cards may define `appendix_links` as a list of manifest appendix IDs with optional display labels. Renderers resolve these IDs for each output context; profile YAML must not contain generated-output paths.

Card icon configuration has three independent positions under `card.icons`: `header` controls the right side of the shared Camera Settings header, `left` controls the left side of the card-title row, and `right` controls the right side of the card-title row. All positions inherit baseline defaults and may be overridden by a card. The baseline `header` is the Silver logo; baseline `left` and `right` are empty. An empty card-title position remains reserved so the title stays centered.

Cards render required settings from fully merged baseline + profile data, including inherited values:

- `exposure.mode`
- `shutter.target`
- `lens.aperture.target`
- `exposure.iso.mode`
- `exposure.auto_iso.maximum`
- `autofocus.operation`
- `autofocus.method`
- `autofocus.subject_detection`
- `autofocus.eye_detection`
- `drive.mode`
- `stabilization.image_stabilization.mode`

If a required merged value is unset, render the row with `—` rather than omitting it or inventing a camera setting.

`00 Master/card_layout.yaml` may define additional always-shown settings; those remain part of current card behavior.

## Rendering Requirements

- Render ISO as one quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays the fixed value. Do not collapse the underlying fields.
- When both are shown, render IBIS and Lens IS as one `IBIS/Lens IS` quick-reference row. Do not collapse the underlying fields.
- When AF Operation is `Manual Focus`, omit AF Method, Subject Detection, and Eye Detection.
- When AF Method is `Not Used`, omit Subject Detection and Eye Detection.
- Preserve existing card formats, filenames, proportions/behavior, output locations, and backward compatibility unless explicitly approved.
- Card styling and conditional presentation are renderer concerns, not profile-data concerns.
- Normal profile-card rows follow `card_layout.display_order`, which mirrors the conceptual sequence of the R5 Quick Reference. Reference-card rows retain the explicit order of their authored `reference_settings` list.
- Responsive HTML is the primary published phone format. It uses the full phone width, a centered maximum width on larger screens, safe-area padding, and browser-rendered text without horizontal scrolling or pinch-to-zoom.
- PNG remains an optional secondary fixed-size export generated with `--png` from the same merged data. Responsive HTML presentation is controlled by `20 Templates/card.html`; fixed PNG presentation is controlled by `80 Build/render_card_outputs.js`.
- Published HTML copies required card icons into the generated site and uses relative URLs so local files and repository-subdirectory GitHub Pages hosting remain portable. SVG is preferred when available and PNG is the fallback.
- Every published HTML card uses the shared Camera Settings header and inherited `card.icons.header`. Its Back control and centered title both use real internal relative links to the main index so navigation works in an iPhone Home Screen installation without browser controls.

## Release Requirement

Only profiles with `metadata.release: true` are included as cards in the published iPhone/PWA bundle. Their responsive HTML card is the primary index action. A PNG secondary action appears only when the build or publish is explicitly run with `--png`. Other generated development outputs may still exist.

Released profile cards appear under **Subject Cards**. Released permanent reference cards appear under **Reference Cards**.

## Enforcement and Evidence

- `00 Master/card_layout.yaml` is the machine-readable display order and list of always-shown card rows and labels.
- `00 Master/baseline.yaml` and profile YAML supply merged values.
- Card renderers and templates under `80 Build/` and `20 Templates/` implement formatting and conditional rows.
- `80 Build/validators/output_validator.py` checks expected generated card artifacts.
- `80 Build/validators/pwa_validator.py` checks the merged offline bundle.
- Profile validation checks that every `appendix_links` ID exists in the appendix manifest.

Not every conditional rendering rule has a dedicated validator; visual/generated-output review remains required after relevant changes.
