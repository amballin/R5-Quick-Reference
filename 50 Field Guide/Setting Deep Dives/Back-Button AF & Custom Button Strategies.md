# Custom Controls, Back-Button AF & Dial Strategies

## Purpose

Document the owner-confirmed Canon EOS R5 button and dial layout used across the baseline and all subject profiles. Keep Canon capabilities, the current configuration, operating recommendations, and unresolved controls visibly separate.

## What it Does

Back-button AF separates autofocus activation from the shutter release. **AF-ON** starts autofocus with the camera's current AF settings. **AE Lock** starts autofocus with a precise 1-Point AF override. Choose one AF-start button at a time, then press the shutter to take the picture.

The physical controls stay consistent across subjects. The baseline and profile overrides continue to own AF Method, Subject Detection, Eye Detection, exposure, drive, and other subject-specific settings.

## Owner-Confirmed Current Layout

These settings were directly confirmed by the project owner on 2026-07-23. They are current configuration, not deductions from the retired screenshots.

| Physical control | Assignment | INFO details or operation |
|---|---|---|
| **Shutter half-press** | **Metering start** | Does not start autofocus. |
| **AF-ON** | **Metering and AF start** | AF Operation: **Maintain current setting**; AF Method: **Maintain current setting**; Servo AF characteristics: **Maintain current setting**. |
| **AE Lock** | **Metering and AF start** | AF Operation: **Maintain current setting**; AF Method: **1-Point AF**; Servo AF characteristics: **Maintain current setting**. |
| **AF Point Selection** | **AF point selection** | Use the **Main Dial** to change the selection. |
| **Lens AF button** | **AF Off** | Stops AF while the lens button is used. |
| **DOF button** | **One-Shot AF ↔ Servo AF** | Changes AF Operation. |
| **SET** | **Set AF point to center** | Recenters the selected AF point. |
| **Joystick** | **Direct AF point selection** | Moves the selected AF point or starting position. |
| **Main Dial** | **Shutter Speed** | Direct exposure control. |
| **Rear Wheel** | **Aperture** | Direct exposure control. |
| **Top Rear Dial** | **ISO Speed** | Direct exposure control. |
| **Control Ring** | **Exposure Compensation** | In Manual exposure, compensation requires Auto ISO. |
| **Movie Record button** | **Leave default** | No custom assignment in this architecture. |
| **MODE button** | **Leave default** | No custom assignment in this architecture. |
| **LCD panel illumination button** | **Leave default** | No custom assignment in this architecture. |
| **M-Fn** | **Unresolved — review later** | Do not change it as part of this architecture. |

C1, C2, and C3 are also unresolved. If adopted later, each should represent a complete shooting configuration resolved from the baseline plus one profile, not an independent AF-only preset.

## How it Works

### AF-ON: normal autofocus

Assign **Metering and AF start**, press **INFO**, and set all three details to **Maintain current setting**:

| AF-ON INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | Maintain current setting |
| Servo AF characteristics | Maintain current setting |

AF-ON therefore uses the AF configuration currently set on the camera from the applicable merged card. It does not read or activate a YAML profile automatically.

### AE Lock: precise alternate autofocus

Assign **Metering and AF start**, press **INFO**, and override only AF Method:

| AE Lock INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | 1-Point AF |
| Servo AF characteristics | Maintain current setting |

AE Lock starts autofocus itself. It retains the current One-Shot/Servo choice and Servo response while using 1-Point AF. Do not hold AF-ON and AE Lock together.

Subject Detection and Eye Detection menu values do not need to be changed for the AE Lock override. They remain configured on the camera, but 1-Point AF provides deliberate point placement instead of Face + Tracking behavior.

### Other AF methods

The AE Lock shortcut remains 1-Point AF for consistency. When a profile calls for Spot AF or Expand AF Area, use **AF Point Selection** and the **Main Dial** to select it manually.

## Advantages

- Separates autofocus activation from image capture.
- Keeps the normal subject configuration and a precise alternate immediately available.
- Requires only one rear AF-start button at a time.
- Preserves current One-Shot/Servo and Servo-response choices on both AF-start buttons.
- Provides direct AF-point movement, recentering, and AF-operation switching.
- Keeps shutter speed, aperture, ISO speed, and exposure compensation on separate physical controls.
- Uses the same physical layout across every subject profile.

## Disadvantages

- Half-pressing the shutter no longer starts autofocus.
- The photographer must deliberately choose AF-ON or AE Lock.
- AE Lock is no longer available for its original exposure-lock role.
- The DOF button is no longer available for depth-of-field preview.
- A customized camera can be confusing to another photographer unless the layout is documented.

## Recommended Uses

The following are operating recommendations, not additional camera assignments:

- Use **AF-ON** for the normal AF configuration selected from the subject card.
- Use **AE Lock** when deliberate 1-Point placement is more reliable than tracking.
- Use **AF Point Selection + Main Dial** when Spot AF or Expand AF Area is more appropriate.
- Use **SET** to recover quickly when the AF point has moved away from the desired starting position.
- Use the **Joystick** for direct AF-point placement.

## When Not to Use

- Do not press AF-ON and AE Lock together.
- Do not expect shutter half-press to refocus.
- Do not use back-button AF without practicing before an important shoot.
- Do not change M-Fn while its role remains unresolved.
- Do not rely on Control Ring exposure compensation in Manual exposure with fixed ISO.
- Do not treat C1-C3 as AF-only controls.

## Decision Guide

| Situation | Control | Action |
|---|---|---|
| Start AF with the current subject configuration | **AF-ON** | Press or hold; all INFO details maintain current settings. |
| Start AF with precise point placement | **AE Lock** | Press or hold; only AF Method changes to 1-Point AF. |
| Select Spot, Expand, or another AF method manually | **AF Point Selection** | Press it and use the Main Dial. |
| Move the active AF point | **Joystick** | Move the point or starting position directly. |
| Return the AF point to center | **SET** | Press once. |
| Change between One-Shot and Servo | **DOF button** | Use One-Shot AF ↔ Servo AF. |
| Temporarily stop lens AF | **Lens AF button** | Use AF Off. |
| Change shutter speed | **Main Dial** | Rotate the dial. |
| Change aperture | **Rear Wheel** | Rotate the wheel. |
| Change ISO speed | **Top Rear Dial** | Rotate the dial. |
| Apply exposure compensation | **Control Ring** | Rotate the ring; use Auto ISO when working in Manual exposure. |

## Recommended Settings by Profile

| Profile | AF-ON behavior from current camera settings | AE Lock or manual alternative |
|---|---|---|
| **Birds in Flight** | Face + Tracking, Animals, Servo AF | AE Lock for 1-Point AF; select Expand AF Area manually when movement is difficult to hold under one point. |
| **Birds Perched** | Face + Tracking, Animals, Eye Detection | AE Lock for 1-Point AF through branches; select Spot AF manually for finer placement. |
| **Wildlife** | Face + Tracking, Animals, Eye Detection | AE Lock for 1-Point AF through grass or brush; select Expand AF Area manually for movement. |
| **Sports** | Face + Tracking, People, Servo AF | AE Lock for 1-Point AF when the wrong player is selected; choose Expand AF Area manually when appropriate. |
| **People** | Face + Tracking, People, Eye Detection | AE Lock for deliberate 1-Point placement when the wrong face is selected. |
| **Macro** | One-Shot AF and Spot AF when autofocus is useful | AE Lock changes the method to 1-Point; use AF-ON when the profile's Spot AF is preferred. |
| **Landscape** | One-Shot AF with deliberate point placement | AF-ON follows the current settings; AE Lock may be redundant when the current method is already 1-Point. |
| **Travel** | Baseline AF unless a subject-specific configuration is selected | Use AF-ON normally; AE Lock supplies consistent 1-Point AF. |
| **Fireworks / Waterdrops** | Manual Focus | Rear AF-start buttons do not replace the manual-focus workflow. |

These recommendations describe operation only. Subject settings remain owned by the baseline and profile overrides.

## Canon-Specific Notes

Verified Canon capabilities:

- The original EOS R5 supports separate custom-button assignments for still-photo and movie use.
- Supported rear buttons can be assigned **Metering and AF start** and can expose advanced AF details through **INFO**.
- The camera provides 1-Point AF, Spot AF, Expand AF Area, Face + Tracking, and the other documented AF methods.
- The Control Ring may be on an RF lens or an EF-EOS R control ring adapter.

Project configuration:

- The table in **Owner-Confirmed Current Layout** is the project owner's confirmed physical setup.
- Historical screenshots are not current-state evidence.
- Plain physical names are used so the layout is readable in the field.

## Tips

- Practice AF-ON first, then practice moving to AE Lock without pressing both.
- Test the 1-Point override on a high-contrast stationary subject.
- Confirm AF-ON still follows Face + Tracking after selecting a bird, wildlife, sports, or people configuration.
- Confirm AF-ON follows One-Shot or Spot AF after selecting Landscape or Macro settings.
- Photograph the finished control pages after the architecture is stable.
- Recheck assignments after a reset or firmware-related settings reset.

## Common Mistakes

- Expecting shutter half-press to autofocus.
- Pressing AF-ON and AE Lock together.
- Overriding AF Operation or Servo AF characteristics accidentally in the AE Lock INFO details.
- Expecting Eye Detection behavior while the 1-Point override is active.
- Assuming AF-ON activates a project profile automatically.
- Changing M-Fn before its separate review.
- Expecting exposure compensation to change Manual exposure with fixed ISO.

## Cross References

- Card: Camera Buttons.
- Profiles: Birds in Flight, Birds Perched, Wildlife, Sports, People, Macro, Landscape, Travel, Fireworks, Waterdrops.
- Related guides:
  - [AF Cases & Tracking Behavior](appendix:af_cases_tracking)
  - [R5 Quick Reference](appendix:r5_quick_reference)
