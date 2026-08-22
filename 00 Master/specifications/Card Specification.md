# Card Specification

## Scope

This specification governs generated quick-reference card content and conditional rendering.

## Required Quick-Reference Settings

Cards use `card_type: profile` by default. Profile cards inherit the baseline and render merged camera settings. Permanent reference cards use `card_type: reference`, do not inherit the baseline or define overrides, and normally render their `reference_settings` entries as a two-column **Settings** table. The My Menu reference card instead declares `reference_source: my_menu`; it must not author `reference_settings` because its tab sections and ordered items are derived from the persisted My Menu configuration.

Index placement is independent of rendering behavior. Optional `display_category` is `subject` or `reference`; when omitted, it defaults to `subject` for profile cards and `reference` for permanent reference cards. Optional integer `display_order` defaults to `100`; lower values appear first within a category and ties sort alphabetically. This allows a baseline-driven profile card to appear with operational references without duplicating baseline settings.

Each `reference_settings` entry contains a non-empty `control` and `assignment`. Reference-card checklists contain concise recommendations or verification steps rather than repeating the Settings table.

Cards may define `appendix_links` as a list of manifest appendix IDs with optional display labels. Renderers resolve these IDs for each output context; profile YAML must not contain generated-output paths.

Card icon configuration has three independent positions under `card.icons`: `header` controls the right side of the shared Camera Settings header, `left` controls the left side of the card-title row, and `right` controls the right side of the card-title row. All positions inherit baseline defaults and may be overridden by a card. The baseline `header` is the Silver logo; baseline `left` and `right` are empty. An empty card-title position remains reserved so the title stays centered.

Profile cards may define `card.field_setup` to identify My Menu tabs that provide fast access to listed settings, with or without an intended C1–C3 starting configuration. `start` is `C1`, `C2`, or `C3`; `source_card_id` is the immutable UUID of the profile represented by that registered mode; when used, both are required together. Renderers resolve the current source title from that UUID. Optional `my_menus` contains at most five named tabs, each with a non-empty list of unique card-setting paths. A card may omit `start` and `source_card_id` while retaining My Menu access metadata. A baseline-driven profile displayed in the reference category may additionally set `access_only: true` to identify a route that does not imply a registered C-mode. Access-only routes require at least one authored My Menu tab. A setting may belong to only one displayed My Menu tab on a card.

Cards render required settings from fully merged baseline + profile data, including inherited values:

- `exposure.mode`
- `shutter.target`
- `shutter.type`
- `lens.aperture.target`
- `exposure.iso.mode`
- `exposure.auto_iso.maximum`
- `autofocus.operation`
- `autofocus.servo_af_case`
- `autofocus.tracking_sensitivity`
- `autofocus.accel_decel_tracking`
- `autofocus.switching_tracked_subjects`
- `autofocus.method`
- `autofocus.subject_detection`
- `autofocus.eye_detection`
- `drive.mode`
- `display.high_speed_display`
- `stabilization.image_stabilization.mode`

If a required merged value is unset, render the row with `—` rather than omitting it or inventing a camera setting.

`00 Master/card_layout.yaml` may define additional always-shown settings; those remain part of current card behavior.

The Camera Setup Essentials card also renders `shutter.type` as **Shutter Type**, `image.cropping_aspect_ratio` as **Crop / Aspect**, and the three shared Touch & Drag AF controls as separate rows: `autofocus.touch_drag_af`, `autofocus.touch_drag_positioning_method`, and `autofocus.touch_drag_active_area`. The shared shutter and Touch & Drag AF baseline values and any explicit profile overrides remain visible without duplicating them in profile YAML. The shared cropping baseline is **Full-frame**; subject cards inherit it, and a temporary 1.6× field change does not require a permanent profile override.

## Rendering Requirements

- Render ISO as one quick-reference row. Auto ISO displays as `Auto - maximum`; fixed ISO displays the fixed value. Do not collapse the underlying fields.
- When both are shown, render IBIS and Lens IS as one `IBIS/Lens IS` quick-reference row. Do not collapse the underlying fields.
- When AF Operation is `Manual Focus`, omit AF Method, Subject Detection, and Eye Detection.
- Show **Servo AF Case** immediately after **AF Operation** when AF Operation is `Servo AF`; omit it when AF Operation is One-Shot AF or Manual Focus because the stored Case is inactive.
- When the effective Servo AF Case is Case 1–4, combine the merged Tracking Sensitivity and Accel./Decel. tracking values into one compact **Track / Accel** row immediately below Servo AF Case. Show inherited values as well as explicit overrides. Omit the row for Case A and whenever Servo AF Case is inactive.
- Show **Switching Tracked Subjects** when the effective AF Method is Face + Tracking, Zone AF, or Large Zone AF. Omit it for AF methods that do not support subject switching. Its value remains separate from the Servo AF Case parameters.
- Show **High Speed Display** on Camera Defaults, Camera Setup Essentials, and profile cards whose effective starting configuration uses regular High Speed Continuous or Electronic shutter. Omit it for High Speed Continuous+, Low Speed Continuous, Single Shot, and other starting configurations where the selectable setting is inactive.
- When AF Method is `Not Used`, omit Subject Detection and Eye Detection.
- Preserve existing card formats, filenames, proportions/behavior, output locations, and backward compatibility unless explicitly approved.
- Card styling and conditional presentation are renderer concerns, not profile-data concerns.
- When `card.field_setup` is present, render a compact route beneath the title containing the starting Cx, when applicable, followed by each named My Menu tab with at least one assigned setting represented by a visible merged card row. Omit a tab from that card when none of its assigned settings are visible; do not interpret that omission as a recommendation to remove the shortcut from the camera's My Menu. An access-only route renders visible My Menu tokens without a Cx token and renders no route or generated access note when no assigned settings are visible. Keep the Cx token and non-My-Menu values in the normal white text color. Color each visible My Menu value to match its labeled route token whether or not that value differs from the selected Cx foundation. Resolve named-tab colors from `00 Master/my_menu_colors.yaml`, use distinct assignments, and fall back through its curated palette for a valid authored tab that has no saved assignment. Do not store raw access colors in profile YAML or rely on color without the visible tab name.
- Reserve a fixed rightmost change-indicator column on every editable profile card. With a starting Cx, compare each visible merged row with the effective values of the exact profile identified by `card.field_setup.source_card_id`; leave the indicator blank when all represented settings match and otherwise show `Δ`. Without a Cx foundation, show `Δ` on every visible settings row because project data cannot prove the physical camera already contains the target value. Use the row's displayed setting color for each marker, including the normal card text color for non-My-Menu rows. For combined Track / Accel, IBIS/Lens IS, and ISO rows, one marker represents every underlying setting in that row. Keep My Menu coloring independent from the change calculation. The visible legend and accessible label identify either the selected Cx foundation or **Verify/set — no Cx foundation**. Permanent reference cards do not render the change column. Change markers are derived rendering state and must not be authored in profile YAML.
- On applicable cards, associate the displayed Servo AF Case, Track / Accel, and Switching Tracked Subjects values with **My Menu: AF Case** when their underlying setting paths are assigned to that tab. The tab contains **Servo AF**, **Tracking Sensitivity**, **Accel./Decel. tracking**, and **Switching tracked subjects** in that order. Switching tracked subjects remains separate in camera behavior even though the shared tab provides fast access.
- Prepend a generated Notes item explaining the full starting profile, the need to verify its Cx registration when applicable, and that My Menu colors identify access regardless of whether a change is required. For a Cx route, explain that a same-colored `Δ` identifies a value that differs from the starting foundation. For a non-Cx or access-only profile card, explain that every `Δ` directs the user to verify or set the target because no foundation comparison is available. Support multiple My Menu tabs without requiring them on current cards.
- Normal profile-card rows follow `card_layout.display_order`, which mirrors the conceptual sequence of the R5 Quick Reference. Reference-card rows retain the explicit order of their authored `reference_settings` list.
- Camera Buttons reference rows use stable control-name keys to display the corresponding official Canon physical-control SVG when one is mapped. Keep the authored project control name as text, preserve the existing row order, and do not substitute an assignment icon or fabricate a control icon. If an official SVG contains an opaque background that conflicts with the card's standard monochrome treatment, a geometry-preserving card derivative may remove only that background fill; preserve the official source asset for the icon reference and apply the normal card icon color to the derivative.
- The My Menu reference card renders one visibly separated section for each used persisted tab, in saved tab order. Each section shows its `MY MENU1`–`MY MENU5` position, saved tab name in the assigned tab color, and its item labels in saved order. The source camera-menu location may appear as subordinate detail. Empty tabs and slots are omitted. The card remains an approved-layout reminder pending comparison with the physical camera.
- Responsive HTML is the primary published phone format. It uses the full phone width, a centered maximum width on larger screens, safe-area padding, and browser-rendered text without horizontal scrolling or pinch-to-zoom.
- In responsive HTML, keep every card's identity region sticky beneath the shared Camera Settings navigation while card content scrolls. The identity region contains the card title and any existing subtitle or field-setup route; do not add a duplicate title, route, legend, or other persistent content. Give a displayed field-setup route 8 px of breathing room before the identity divider without changing reference-card spacing. Disable sticky positioning for print output.
- Fixed card PNG exports are not generated or published. Responsive HTML presentation is controlled by `20 Templates/card.html`; optional card PDF presentation is controlled by `80 Build/render_card_pdf.js`.
- Published HTML copies required card icons into the generated site and uses relative URLs so local files and repository-subdirectory GitHub Pages hosting remain portable. SVG is preferred when available and PNG is the fallback.
- Every published HTML card uses the shared Camera Settings header and inherited `card.icons.header`. Its Back control and centered title both use real internal relative links to the main index so navigation works in an iPhone Home Screen installation without browser controls.

## Release Requirement

Only profiles with `metadata.release: true` are included as cards in the published iPhone/PWA bundle. Their responsive HTML card is the index action. During a normal full build, every profile whose release flag is not `true` is instead listed in the separate machine-local `Build Output/Card Candidates/` review mini-site. Candidate cards must not enter the publishable bundle, `docs/`, or website staging.

Released cards with `display_category: subject` appear under **Subjects**. Cards with `display_category: reference` appear under **Camera Setup & Controls**, regardless of whether their rendering behavior is profile-based or permanent-reference-based.

## Enforcement and Evidence

- `00 Master/card_layout.yaml` is the machine-readable display order and list of always-shown card rows and labels.
- `00 Master/baseline.yaml` and profile YAML supply merged values.
- `80 Build/cx_route_analysis.py` derives visible setting differences from each card's selected Cx foundation without mutating source data.
- `00 Master/my_menu_colors.yaml` and `80 Build/my_menu_colors.py` define, validate, and resolve the shared named-tab palette and assignments.
- `00 Master/my_menu.yaml`, `80 Build/my_menu.py`, and `80 Build/my_menu_reference.py` define, validate, and materialize the dynamic My Menu reference-card sections.
- Card renderers and templates under `80 Build/` and `20 Templates/` implement formatting and conditional rows.
- `80 Build/validators/output_validator.py` checks expected generated card artifacts.
- Candidate validation checks that all and only unreleased profiles appear in the machine-local Card Candidates review set and that their local navigation resolves.
- `80 Build/validators/pwa_validator.py` checks the merged offline bundle.
- `80 Build/validators/profile_validator.py` checks field-setup structure, starting modes, source-profile references, My Menu count and names, displayed setting paths, and duplicate setting assignments.
- Profile validation checks that every `appendix_links` ID exists in the appendix manifest.

Not every conditional rendering rule has a dedicated validator; visual/generated-output review remains required after relevant changes.
