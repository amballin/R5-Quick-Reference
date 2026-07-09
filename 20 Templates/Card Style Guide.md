## Card Theme Direction

Current card rendering should keep the existing dark card layout, with setting icons rendered in pale blue so they remain visible against the dark background.

Preferred future direction:

- Keep camera settings and profile overrides focused on camera behavior, not visual styling.
- Avoid putting raw color values directly into profile YAML.
- If profiles need visual variation, add renderer-level theme support first.
- A good future card structure would use a colored header for profile identity and a light text area for readability.
- Icons should not require a white background unless testing shows contrast still fails.
- If per-profile colors are added later, prefer profile theme names over arbitrary profile-defined colors.
- A future header treatment may place a small icon on each side of the dynamic island, especially for PNG and PDF card outputs.
