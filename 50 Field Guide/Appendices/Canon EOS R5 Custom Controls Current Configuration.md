# Canon EOS R5 Custom Controls — Owner-Confirmed Configuration

## Purpose

This appendix records the owner-confirmed physical layout and separately identifies approved target settings that still require physical camera verification.

The previous custom-control screenshots (`IMG_6335`–`IMG_6340`) are retired historical material. The camera settings changed after capture, so those images are not reliable current-state evidence.

## Owner-Confirmed Buttons and Controls

<!-- CONTROL_REFERENCE_TABLE: controls -->

## Owner-Confirmed Dials and Control Ring

<!-- CONTROL_REFERENCE_TABLE: dials -->

The project uses these plain-language control names. Numbered quick-dial terminology is intentionally avoided.

## AF-ON and AE Lock Behavior

AF-ON is the intelligent-acquisition AF-start button. Its owner-confirmed INFO details maintain the active profile or DOF-selected AF Operation, temporarily select Face + Tracking, and maintain Servo AF characteristics. It honors the stored Eye detection state, including a state changed with SET.

SET toggles Eye detection when the active AF method supports it. The selected Eye detection state persists when switching between 1-Point AF and Face + Tracking, and AF-ON uses that state when it invokes Face + Tracking. SET has no effect while 1-Point AF or Spot AF is active because those methods cannot use Eye detection.

AE Lock is the precision AF-start button. It maintains the active profile's AF Operation and Servo AF characteristics but temporarily uses 1-Point AF. It remembers the last 1-Point position rather than automatically recentering it. Move the point with the joystick and press the joystick straight in when recentering is needed.

This arrangement preserves the baseline-plus-overrides architecture: the profile determines the shooting environment and initial AF Operation and Eye detection states, SET provides a situational Eye detection toggle, and the two rear buttons consistently select tracking or precision.

## C1–C3

The approved target registrations are:

| Custom mode | Canonical profile | Field label | Verification status |
|---|---|---|---|
| C1 | Wildlife | General Wildlife | Registered and camera-body verified; lens Mode 1 pending |
| C2 | Birds in Flight | Birds in Flight / Action | Registered and camera-body verified; lens Mode 3 pending |
| C3 | Landscape | Landscape | Registered and camera-body verified; lens Mode 1 pending |

They are complete shooting environments, not independent AF-setting controls. The camera-body registrations were recalled and cross-checked in physical session 3; only the lens-dependent stabilization modes remain unresolved.

## Evidence and Recommendation Rules

- A verified Canon capability states what the camera can do; it does not prove which assignment is currently selected.
- An owner-confirmed setting records the chosen current setup.
- An approved target records the chosen architecture but remains distinct from current state until physically verified on the camera.
- A recommendation must be labeled as advice and does not become a current setting without owner confirmation.
- An unresolved item remains unresolved; do not guess from historical screenshots. M-Fn is no longer unresolved: its custom-mode switching assignment has been physically tested.

See [Custom Controls & Menus, Back-Button AF & Dial Strategies](../Setting%20Deep%20Dives/Custom%20Controls%20%26%20Menus%2C%20Back-Button%20AF%20%26%20Dial%20Strategies.md) for the readable control table, exact AF-ON and AE Lock setup details, rationale, and profile behavior.
