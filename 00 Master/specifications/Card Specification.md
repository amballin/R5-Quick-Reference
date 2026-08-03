# Card Specification

## Scope

This specification governs generated quick-reference card content and conditional rendering.

## Required Quick-Reference Settings

Cards use `card_type: profile` by default. Profile cards inherit the baseline and render merged camera settings. Permanent reference cards use `card_type: reference`, do not inherit the baseline or define overrides, and render their `reference_settings` entries as a two-column **Settings** table.

Index placement is independent of rendering behavior. Optional `display_category` is `subject` or `reference`; when omitted, it defaults to `subject` for profile cards and `reference` for permanent reference cards. Optional integer `display_order` defaults to `100`; lower values appear first within a category and ties sort alphabetically. This allows a baseline-driven profile card to appear with operational references without duplicating baseline settings.

Each `reference_settings` entry contains a non-empty `control` and `assignment`. Reference-card checklists contain concise recommendations or verification steps rather than repeating the Settings table.

Cards may define `appendix_links` as a list of manifest appendix IDs with optional display labels. Renderers resolve these IDs for each output context; profile YAML must not contain generated-output paths.

Card icon configuration has three independent positions under `card.icons`: `header` controls the right side of the shared Camera Settings header, `left` controls the left side of the card-title row, and `right` controls the right side of the card-title row. All positions inherit baseline defaults and may be overridden by a card. The baseline `header` is the Silver logo; baseline `left` and `right` are empty. An empty card-title position remains reserved so the title stays centered.

Profile cards may define `card.field_setup` to identify an intended C1–C3 starting configuration and the My Menu tabs used for field changes. `start` is `C1`, `C2`, or `C3`; `source_profile` is the exact profile title represented by that registered mode; optional `my_menus` contains at most five named tabs, each with a non-empty list of unique card-setting paths. A setting may belong to only one displayed My Menu tab on a card.

Cards render required settings from fully merged baseline + profile data, including inherited values:

- `exposure.mode`
- `shutter.target`
- `shutter.type`
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

The Camera Setup Essentials card also renders `shutter.type` as **Shutter Type** and `image.cropping_aspect_ratio` as **Crop / Aspect**. The shared shutter baseline and any explicit profile override remain visible without duplicating them in profile YAML. The shared cropping baseline is **Full-frame**; subject cards inherit it, and a temporary 1.6× field change does not require a permanent profile override.

## Rendering Requirements

- Render ISO as one quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays the fixed value. Do not collapse the underlying fields.
- When both are shown, render IBIS and Lens IS as one `IBIS/Lens IS` quick-reference row. Do not collapse the underlying fields.
- When AF Operation is `Manual Focus`, omit AF Method, Subject Detection, and Eye Detection.
- When AF Method is `Not Used`, omit Subject Detection and Eye Detection.
- Preserve existing card formats, filenames, proportions/behavior, output locations, and backward compatibility unless explicitly approved.
- Card styling and conditional presentation are renderer concerns, not profile-data concerns.
- When `card.field_setup` is present, render a compact route beneath the title containing the starting Cx followed by every named My Menu tab. Keep non-My-Menu values in the normal text color and color each My Menu value to match its labeled route token. `SWITCH` always uses the renderer-managed green treatment; other tabs use distinct renderer-managed colors in authored order. Do not store raw access colors in profile YAML or rely on color without the visible tab name.
- Prepend a generated Notes item explaining the full starting profile, the need to verify its Cx registration, and the distinction between colored My Menu values and white Quick Control, dial, or button values. Support multiple My Menu tabs without requiring them on current cards.
- Normal profile-card rows follow `card_layout.display_order`, which mirrors the conceptual sequence of the R5 Quick Reference. Reference-card rows retain the explicit order of their authored `reference_settings` list.
- Camera Buttons reference rows use stable control-name keys to display the corresponding official Canon physical-control SVG when one is mapped. Keep the authored project control name as text, preserve the existing row order, and do not substitute an assignment icon or fabricate a control icon. If an official SVG contains an opaque background that conflicts with the card's standard monochrome treatment, a geometry-preserving card derivative may remove only that background fill; preserve the official source asset for the icon reference and apply the normal card icon color to the derivative.
- Responsive HTML is the primary published phone format. It uses the full phone width, a centered maximum width on larger screens, safe-area padding, and browser-rendered text without horizontal scrolling or pinch-to-zoom.
- In responsive HTML, keep every card's identity region sticky beneath the shared Camera Settings navigation while card content scrolls. The identity region contains the card title and any existing subtitle or field-setup route; do not add a duplicate title, route, legend, or other persistent content. Give a displayed field-setup route 8 px of breathing room before the identity divider without changing reference-card spacing. Disable sticky positioning for print output.
- Fixed card PNG exports are not generated or published. Responsive HTML presentation is controlled by `20 Templates/card.html`; optional card PDF presentation is controlled by `80 Build/render_card_pdf.js`.
- Published HTML copies required card icons into the generated site and uses relative URLs so local files and repository-subdirectory GitHub Pages hosting remain portable. SVG is preferred when available and PNG is the fallback.
- Every published HTML card uses the shared Camera Settings header and inherited `card.icons.header`. Its Back control and centered title both use real internal relative links to the main index so navigation works in an iPhone Home Screen installation without browser controls.

## Release Requirement

Only profiles with `metadata.release: true` are included as cards in the published iPhone/PWA bundle. Their responsive HTML card is the index action. Other generated development outputs may still exist.

Released cards with `display_category: subject` appear under **Subjects**. Cards with `display_category: reference` appear under **Camera Setup & Controls**, regardless of whether their rendering behavior is profile-based or permanent-reference-based.

## Enforcement and Evidence

- `00 Master/card_layout.yaml` is the machine-readable display order and list of always-shown card rows and labels.
- `00 Master/baseline.yaml` and profile YAML supply merged values.
- Card renderers and templates under `80 Build/` and `20 Templates/` implement formatting and conditional rows.
- `80 Build/validators/output_validator.py` checks expected generated card artifacts.
- `80 Build/validators/pwa_validator.py` checks the merged offline bundle.
- `80 Build/validators/profile_validator.py` checks field-setup structure, starting modes, source-profile references, My Menu count and names, displayed setting paths, and duplicate setting assignments.
- Profile validation checks that every `appendix_links` ID exists in the appendix manifest.

Not every conditional rendering rule has a dedicated validator; visual/generated-output review remains required after relevant changes.
