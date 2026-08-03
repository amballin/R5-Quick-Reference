## Card Theme Direction

Current card rendering should keep the existing dark card layout, with setting icons rendered in pale blue so they remain visible against the dark background.

Profile cards with field-access metadata place a compact Cx/My Menu route immediately below the title. SWITCH is consistently green because it is the primary transition tab. AF Case and any later My Menu tabs receive distinct renderer-managed colors in authored order. Matching setting values use the same colors; ordinary Quick Control, dial, and button values remain white. Visible tab names accompany every color so the cue does not depend on color alone.

Preferred future direction:

- Keep camera settings and profile overrides focused on camera behavior, not visual styling.
- Avoid putting raw color values directly into profile YAML.
- If profiles need visual variation, add renderer-level theme support first.
- A good future card structure would use a colored header for profile identity and a light text area for readability.
- Icons should not require a white background unless testing shows contrast still fails.
- If per-profile colors are added later, prefer profile theme names over arbitrary profile-defined colors.
- In responsive HTML cards, use the inherited `card.icons.header` in the general Camera Settings navigation header; it defaults to the shared Silver logo. Align the card title between the independently configurable `card.icons.left` and `card.icons.right` positions below it. Empty title-row positions remain reserved so the title stays centered.
- Fixed PNG and PDF outputs may retain their existing header treatment because they do not use the responsive HTML navigation header.
