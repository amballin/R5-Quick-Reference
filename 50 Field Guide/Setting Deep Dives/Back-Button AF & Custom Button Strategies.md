# Custom Controls, Back-Button AF & Dial Strategies

## Purpose

Explain why the Canon EOS R5 is configured around complete subject profiles, constant physical controls, and two distinct focusing choices. The architecture is intended to reduce cognitive load in the field: choose the shooting environment, then use the same buttons for tracking or precision.

## Index

- [Design Philosophy](#design-philosophy)
- [Approved Layout](#approved-layout)
- [How It Works](#how-it-works)
- [Back-Button Philosophy](#back-button-philosophy)
  - [AF-ON: intelligent acquisition](#af-on-intelligent-acquisition)
  - [AE Lock: precision focus](#ae-lock-precision-focus)
  - [Why AF Operation remains current](#why-af-operation-remains-current)
- [Subject Detection Workflow](#subject-detection-workflow)
- [C1-C3: Fast Implementations of Subject Cards](#c1-c3-fast-implementations-of-subject-cards)
  - [C1 — General Wildlife](#c1-general-wildlife)
  - [C2 — Birds in Flight / Action](#c2-birds-in-flight-action)
  - [C3 — Landscape](#c3-landscape)
- [Other AF Methods](#other-af-methods)
- [Advantages and Disadvantages](#advantages)
- [Recommended Uses and When Not to Use](#recommended-uses)
- [Decision Guide](#decision-guide)
- [Recommended Settings by Profile](#recommended-settings-by-profile)
- [Canon-Specific Notes](#canon-specific-notes)
- [Tips and Common Mistakes](#tips)
- [Operating Principle](#operating-principle)
- [Cross References](#cross-references)

## Design Philosophy

1. **Keep button behavior constant.** Muscle memory should not change when the subject changes.
2. **Profiles define the shooting environment.** A profile establishes exposure, drive, stabilization, initial AF Operation, Subject Detection, Eye Detection, and other subject-specific settings.
3. **Subject Detection belongs to the profile—not the buttons.** Wildlife prioritizes Animals; a people setup prioritizes People; a motorsports setup may prioritize Vehicles.
4. **Use overrides only when they provide a measurable operational advantage.** The tracking and precision buttons cover the two common focusing decisions. Spot AF or Expand AF Area remains available when a specific situation justifies another method.
5. **Preserve muscle memory whenever possible.** C1-C3 change the environment; AF-ON and AE Lock keep the same jobs.

The practical model is:

| Question | Control |
|---|---|
| What am I photographing? | Select the applicable profile or C1-C3 mode. |
| Should the camera find and follow the subject? | Use AF-ON. |
| Do I need to place focus exactly here? | Use AE Lock. |
| Is the subject still or moving? | Start with the profile's AF Operation; use the DOF button if it needs to change. |

## What it Does

Back-button AF separates autofocus activation from the shutter release. **AF-ON** starts subject-aware autofocus with Face + Tracking. **AE Lock** starts autofocus with a precise 1-Point AF override. Choose one AF-start button at a time, then press the shutter to take the picture.

Both AF-start buttons maintain the current AF Operation. A profile may start in Servo AF or One-Shot AF, and the DOF button may switch that state. AF-ON and AE Lock respect the resulting choice instead of secretly forcing Servo AF.

## Approved Layout

The physical layout is shared across the baseline and all subject profiles. Settings already confirmed on the camera remain current; the new AF-ON detail and C1-C3 registrations are approved targets pending physical verification.

| Physical control | Assignment | INFO details or operation |
|---|---|---|
| **Shutter half-press** | **Metering start** | Does not start autofocus. |
| **AF-ON** | **Metering and AF start** | AF Operation: **Maintain current setting**; AF Method: **Face + Tracking**; Servo AF characteristics: **Maintain current setting**. Approved target pending camera verification. |
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

## How it Works

The selected profile or C mode loads the shooting environment. AF-ON and AE Lock then temporarily choose tracking or precision without replacing the active One-Shot/Servo state. The DOF button changes only that AF Operation state.

## Back-Button Philosophy

### AF-ON: intelligent acquisition

AF-ON is for speed. Assign **Metering and AF start**, press **INFO**, and use:

| AF-ON INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | Face + Tracking |
| Servo AF characteristics | Maintain current setting |

AF-ON always selects the subject-aware tracking method and uses the profile's Subject Detection and Eye Detection choices. With Servo AF active, focus continues updating as the subject moves. With One-Shot AF active, Face + Tracking can identify and acquire the subject, but it does not provide continuous Servo tracking.

### AE Lock: precision focus

AE Lock is for precision. Assign **Metering and AF start**, press **INFO**, and use:

| AE Lock INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | 1-Point AF |
| Servo AF characteristics | Maintain current setting |

AE Lock gives exact point placement and avoids automatic subject switching. Subject Detection and Eye Detection remain stored in the active profile, but they are not used by the 1-Point AF precision method. Do not describe the button as changing those profile menu values to OFF.

### Why AF Operation remains current

AF Method and AF Operation answer different questions:

- **AF Method:** should the camera find the subject, or should the photographer place one point?
- **AF Operation:** should focus lock once, or continue updating?

The profile supplies the normal One-Shot/Servo starting point. The DOF button changes that state when the subject behaves differently than expected. Because both AF-start buttons maintain AF Operation, either button respects the profile and the DOF-button change.

## Subject Detection Workflow

Subject Detection is part of the shooting profile. It is not part of the tracking-versus-precision button choice.

| Subject environment | Subject Detection |
|---|---|
| Wildlife | Animals |
| Family / people | People |
| Motorsports | Vehicles |
| Landscape | None |

Changing Subject Detection changes what AF-ON prioritizes while its physical behavior remains constant. AE Lock continues to provide deliberate 1-Point placement regardless of the selected subject category.

Changing from the complete Wildlife card to the complete People card involves more than Subject Detection: the current project cards also differ in drive, shutter target, and aperture strategy. Changing only Subject Detection is appropriate when the existing exposure and drive environment is already suitable.

## C1-C3: Fast Implementations of Subject Cards

C1-C3 are not alternate AF buttons or AF-only presets. Each recalls a complete shooting environment derived from an established subject card.

### C1 — General Wildlife

C1 implements the Wildlife card for animals that are stationary, moderately active, or moving unpredictably without requiring the full action setup.

Examples include perched birds, deer, herons, eagles on a perch, and ducks on the water. Its priorities are deliberate composition, useful image quality, Animal Detection, Eye Detection, and a continuous drive appropriate for wildlife behavior.

The operating idea is: **the animal is already there**.

- Use AF-ON for fast animal/eye acquisition.
- Use AE Lock for precise focus through grass, branches, or other obstructions.
- Select Spot AF or Expand AF Area manually only when it provides a measurable advantage over the two standard buttons.

### C2 — Birds in Flight / Action

C2 implements the Birds in Flight card for fast-moving wildlife: birds in flight, osprey diving, ducks taking off, swallows, or running animals.

It retains the same button layout, Animal Detection, Eye Detection, metering philosophy, and tracking-versus-precision choice as C1. Its primary differences are the shooting environment: much faster shutter targets, High Speed Continuous+, action-oriented exposure, and action stabilization.

The operating idea is: **the animal is moving fast**.

- Use AF-ON as the primary tracking control.
- Use AE Lock when automatic selection repeatedly chooses the wrong subject.
- Use Expand AF Area manually when subject size, obstruction, or background makes it measurably more reliable.

### What C1 and C2 should normally keep the same

- Button assignments
- Tracking-versus-precision AF philosophy
- Subject Detection: Animals
- Eye Detection
- Metering philosophy
- Physical control layout

Exposure targets, drive behavior, and stabilization are what primarily distinguish C1 from C2.

### C3 — Landscape

C3 implements the Landscape card. Landscape deserves the third instant-recall position because it changes the complete operating state rather than only the detected subject:

- Av exposure
- Fixed ISO 100
- One-Shot AF
- Single Shot
- f/8-f/11 aperture strategy
- Tripod, stabilization, and near-to-far sharpness considerations

Use AE Lock for normal deliberate 1-Point placement. AF-ON remains available when subject-aware acquisition is useful, and it still maintains C3's One-Shot AF unless the DOF button changes the operation.

People does not use a C-mode slot. For a normal people or family shoot, start with **C1**, because it already provides Fv, Auto ISO, Servo AF, Eye Detection, and general handheld stabilization. Then make these changes:

| Setting | Change for people |
|---|---|
| Subject Detection | Change Animals to People |
| Drive | Change High Speed Continuous to Low Speed Continuous |
| Shutter target | Use 1/200-1/320 for portraits or 1/500+ for active people |
| Aperture target | Use f/1.8-f/4 for one person or f/4-f/8 for a group |

Keep AF-ON for face/eye acquisition and AE Lock for exact 1-Point placement. Do not start from C3 for people; C3 loads the Landscape settings—ISO 100, One-Shot AF, Single Shot, and f/8-f/11.

## Other AF Methods

The two rear buttons cover the normal tracking and precision decisions. When Spot AF or Expand AF Area is demonstrably better, use **AF Point Selection** and the **Main Dial** to select it manually.

This is an exception workflow, not a reason to change the constant button assignments.

## Advantages

- Reduces field decisions to subject profile, tracking versus precision, and still versus moving.
- Keeps the physical controls consistent across every subject.
- Preserves the profile's One-Shot/Servo choice and any DOF-button change.
- Keeps Subject Detection with the profile that defines the subject environment.
- Provides intelligent acquisition and deliberate point placement without menu diving.
- Makes C1-C3 useful as complete shooting setups rather than AF-only presets.

## Disadvantages

- Half-pressing the shutter no longer starts autofocus.
- AE Lock is no longer available for its original exposure-lock role.
- AF-ON temporarily overrides a profile's displayed AF Method with Face + Tracking.
- AE Lock provides 1-Point AF, not the smaller Spot AF used in some macro work.
- The photographer must deliberately choose AF-ON or AE Lock and avoid pressing both together.
- A customized camera can be confusing to another photographer unless the layout is documented.

## Recommended Uses

- Select C1 for general wildlife, C2 for birds in flight or fast animal action, and C3 for landscape.
- Use AF-ON when the camera should identify and follow the subject.
- Use AE Lock when exact placement is more important than automatic recognition.
- Use the DOF button only when the profile's starting One-Shot/Servo state no longer matches subject movement.
- Use AF Point Selection + Main Dial for a justified Spot AF or Expand AF Area exception.
- Use SET to recover quickly when the AF point has moved away from the desired starting position.

## When Not to Use

- Do not press AF-ON and AE Lock together.
- Do not expect shutter half-press to refocus.
- Do not describe AF-ON as continuous tracking when One-Shot AF is active.
- Do not describe AE Lock as turning profile Subject Detection or Eye Detection settings OFF.
- Do not force Servo AF from either AF-start button; doing so would defeat the DOF-button workflow.
- Do not change M-Fn while its role remains unresolved.
- Do not treat C1-C3 as AF-only controls.

## Decision Guide

| Situation | Control | Action |
|---|---|---|
| Load general wildlife environment | **C1** | Recall the Wildlife card. |
| Load birds-in-flight/action environment | **C2** | Recall the Birds in Flight card. |
| Load landscape environment | **C3** | Recall the Landscape card. |
| Let the camera find the subject | **AF-ON** | Use Face + Tracking with the current AF Operation. |
| Focus exactly at one point | **AE Lock** | Use 1-Point AF with the current AF Operation. |
| Change between still and moving focus behavior | **DOF button** | Switch One-Shot AF ↔ Servo AF. |
| Select Spot, Expand, or another AF method manually | **AF Point Selection** | Press it and use the Main Dial. |
| Move the active AF point | **Joystick** | Move the point or starting position directly. |
| Return the AF point to center | **SET** | Press once. |
| Temporarily stop lens AF | **Lens AF button** | Use AF Off. |

## Recommended Settings by Profile

| Profile | Initial environment | AF-ON | AE Lock |
|---|---|---|---|
| **Wildlife / C1** | Servo AF, Animals, Eye Detection, continuous drive | Face + Tracking | 1-Point AF through vegetation or clutter |
| **Birds in Flight / C2** | Servo AF, Animals, Eye Detection, fast shutter, High Speed Continuous+ | Face + Tracking | 1-Point AF when automatic selection fails |
| **Landscape / C3** | One-Shot AF, None, ISO 100, Single Shot | Face + Tracking while maintaining One-Shot | Normal deliberate 1-Point placement |
| **Birds Perched** | Servo AF, Animals, Eye Detection | Face + Tracking | 1-Point AF through branches |
| **People** | Servo AF, People, Eye Detection, Low Speed Continuous | Face + Tracking | 1-Point AF when the wrong face is selected |
| **Sports** | Servo AF, People, fast drive; change to Vehicles situationally for vehicle-based sports | Face + Tracking | 1-Point AF when automatic selection fails |
| **Macro** | One-Shot AF and Spot AF when autofocus is useful | Face + Tracking override | 1-Point AF; select Spot AF manually when needed |
| **Travel** | General starting environment | Face + Tracking | 1-Point AF |
| **Fireworks / Waterdrops** | Manual Focus | Rear AF-start buttons do not replace the manual-focus workflow | Rear AF-start buttons do not replace the manual-focus workflow |

## Canon-Specific Notes

Verified Canon capabilities:

- The original EOS R5 supports separate custom-button assignments for still-photo and movie use.
- Supported rear buttons can be assigned **Metering and AF start** and expose AF details through **INFO**.
- The camera provides Face + Tracking, 1-Point AF, Spot AF, Expand AF Area, and other documented AF methods.
- Subject to Detect applies to compatible subject-aware methods. It does not need to be changed when a deliberate-point method is used.
- The Control Ring may be on an RF lens or an EF-EOS R control ring adapter.

Project configuration:

- The physical control layout is the project owner's confirmed layout.
- Face + Tracking on AF-ON and the C1-C3 registrations are approved target settings pending physical camera verification.
- Historical screenshots are not current-state evidence.
- Plain physical names are used so the layout is readable in the field.

## Tips

- Practice the three-step model: select profile, choose AF-ON or AE Lock, then use DOF only if motion behavior changes.
- Test AF-ON and AE Lock in both Servo AF and One-Shot AF to confirm that neither button forces AF Operation.
- Verify C1, C2, and C3 after registration by checking exposure, drive, AF Operation, Subject Detection, and stabilization.
- Test the 1-Point override on a high-contrast stationary subject and through foreground clutter.
- Photograph the finished control and custom-mode pages after physical verification.
- Recheck assignments after a reset or firmware-related settings reset.

## Common Mistakes

- Treating C1-C3 as AF-only presets instead of complete subject cards.
- Expecting AF-ON to force Servo AF.
- Expecting continuous tracking while One-Shot AF is active.
- Expecting Eye Detection behavior while the 1-Point override is active.
- Assuming AE Lock changes Subject Detection or Eye Detection menu values.
- Pressing AF-ON and AE Lock together.
- Confusing an approved target assignment with a setting already verified on the camera.
- Changing M-Fn before its separate review.

## Operating Principle

The objective of this architecture is to keep muscle memory constant. C1-C3 recall the shooting environment. AF-ON consistently provides intelligent subject acquisition, AE Lock consistently provides precise point placement, and both respect the profile or DOF-selected AF Operation.

## Cross References

- Card: Camera Buttons.
- Custom modes: C1 Wildlife (General Wildlife field label), C2 Birds in Flight (Birds in Flight / Action field label), C3 Landscape.
- Profiles: Wildlife, Birds in Flight, Landscape, Birds Perched, People, Sports, Macro, Travel, Fireworks, Waterdrops.
- Related guides:
  - [AF Cases & Tracking Behavior](appendix:af_cases_tracking)
  - [R5 Quick Reference](appendix:r5_quick_reference)
