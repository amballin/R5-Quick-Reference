# Custom Controls & Menus, Back-Button AF & Dial Strategies

## Purpose

Explain why the Canon EOS R5 is configured around complete subject profiles, constant physical controls, and two distinct focusing choices. The architecture is intended to reduce cognitive load in the field: choose the shooting environment, then use the same buttons for tracking or precision.

## Index

- [Approved Control Layout](#approved-control-layout)
- [Recommended Field Flow](#recommended-field-flow)
- [What it Does](#what-it-does)
- [How It Works](#how-it-works)
  - [M-Fn: custom-mode switching](#m-fn-custom-mode-switching)
  - [AF-ON: intelligent acquisition](#af-on-intelligent-acquisition)
  - [AE Lock: precision focus](#ae-lock-precision-focus)
  - [SET: eye-priority toggle](#set-eye-priority-toggle)
  - [Why AF Operation remains current](#why-af-operation-remains-current)
  - [DOF: One-Shot and Servo switching](#dof-one-shot-and-servo-switching)
  - [Joystick: position and recenter](#joystick-position-and-recenter)
    - [Physical test: joystick straight press](#physical-test-joystick-straight-press)
  - [Multi-function Lock: when controls stop responding](#multi-function-lock-when-controls-stop-responding)
  - [AF Point Selection: exception methods](#af-point-selection-exception-methods)
- [Design Philosophy](#design-philosophy)
- [Subject Detection Workflow](#subject-detection-workflow)
- [C1-C3 Registration Reference](#c1-c3-registration-reference)
  - [Registration sequence](#registration-sequence)
  - [C1 — General Wildlife](#c1-general-wildlife)
  - [C2 — Birds in Flight / Action](#c2-birds-in-flight-action)
  - [What C1 and C2 should normally keep the same](#what-c1-and-c2-should-normally-keep-the-same)
  - [C3 — Landscape](#c3-landscape)
  - [My Menu: SWITCH](#my-menu-switch)
  - [My Menu: AF Case](#my-menu-af-case)
    - [Other My Menu tabs to consider](#other-my-menu-tabs-to-consider)
  - [Protect the registered modes: disable Auto update](#protect-the-registered-modes-disable-auto-update)
  - [Save alternate complete configurations to a card](#save-alternate-complete-configurations-to-a-card)
- [Other AF Methods](#other-af-methods)
- [Advantages](#advantages)
- [Disadvantages](#disadvantages)
- [Recommended Uses](#recommended-uses)
- [When Not to Use](#when-not-to-use)
- [Decision Guide](#decision-guide)
- [Recommended Settings by Profile](#recommended-settings-by-profile)
- [Canon-Specific Notes](#canon-specific-notes)
- [Tips](#tips)
- [Common Mistakes](#common-mistakes)
- [Cross References](#cross-references)

## Approved Control Layout

The physical layout is shared across the baseline and all subject profiles. The button and dial assignments below are owner-confirmed on the camera. M-Fn switching among C1-C3 has been physically tested. Physical session 3 registered, recalled, and camera-body verified C1 Wildlife, C2 Birds in Flight, and C3 Landscape; exact lens stabilization Mode 1/3 remains equipment-dependent.

### Controls

| Physical control | Assignment | INFO details or operation |
|---|---|---|
| **Shutter half-press** | **Metering start** | Does not start autofocus. |
| **AF-ON** | **Metering and AF start** | AF Operation: **Maintain current setting**; AF Method: **Face + Tracking**; Servo AF characteristics: **Maintain current setting**. |
| **AE Lock** | **Metering and AF start** | AF Operation: **Maintain current setting**; AF Method: **1-Point AF**; Servo AF characteristics: **Maintain current setting**; uses the last 1-Point position. |
| **AF Point Selection** | **AF point selection** | Use the **Main Dial** to change the selection; with Face + Tracking active, INFO toggles Eye detection. |
| **Lens AF button** | **AF Off** | Stops AF while the lens button is used. |
| **DOF button** | **One-Shot AF ↔ Servo AF** | Changes AF Operation. |
| **SET** | **Eye detection** | Toggles the stored state when the active AF method supports Eye detection; no effect with 1-Point AF or Spot AF. |
| **Joystick** | **Direct AF point selection** | Moves the AF point or starting position; during Face + Tracking adjustment, selects among detected faces or eyes. Straight press centers in Canon's documented AF-point workflow; additional observed Face Select behavior is pending the physical test. |
| **Movie Record button** | **Leave default** | No custom assignment in this architecture. |
| **MODE button** | **Leave default** | No custom assignment in this architecture. |
| **LCD panel illumination button** | **Leave default** | No custom assignment in this architecture. |
| **M-Fn** | **Switch to Custom shooting mode** | Press repeatedly to switch among C1, C2, and C3. |

### Dials and Control Ring

| Physical control | Assignment | Operation |
|---|---|---|
| **Main Dial** | **Shutter Speed** | Direct exposure control. |
| **Rear Wheel** | **Aperture** | Direct exposure control. |
| **Top Rear Dial** | **ISO Speed** | Direct exposure control. |
| **Control Ring** | **Exposure Compensation** | In Manual exposure, compensation requires Auto ISO. |

## Recommended Field Flow

1. **Choose the shooting environment.** Press M-Fn to recall the appropriate registered C1, C2, or C3 profile, or select the applicable subject profile.
2. **Confirm still versus moving focus.** Start with the profile's AF Operation and press the DOF button only when the subject needs the other One-Shot/Servo behavior.
3. **Choose eye priority when available.** Use SET to enable or disable the stored Eye Detection state before starting autofocus.
4. **Choose the focusing behavior.** Hold AF-ON for Face + Tracking acquisition or AE Lock for precise 1-Point AF; use one AF-start button at a time.
5. **Place or recenter the focus point.** Move the joystick for deliberate positioning and use its straight press for the documented recentering workflow, subject to the Face Select test below.
6. **Set exposure directly.** Use the Main Dial for shutter speed, Rear Wheel for aperture, Top Rear Dial for ISO, and Control Ring for exposure compensation.
7. **Use exception controls only when needed.** Press AF Point Selection and turn the Main Dial for Spot AF, Expand AF Area, or another justified AF method.

## What it Does

Back-button AF separates autofocus activation from the shutter release. **AF-ON** starts subject-aware autofocus with Face + Tracking. **AE Lock** starts autofocus with a precise 1-Point AF override. Choose one AF-start button at a time, then press the shutter to take the picture.

Both AF-start buttons maintain the current AF Operation. A profile may start in Servo AF or One-Shot AF, and the DOF button may switch that state. AF-ON and AE Lock respect the resulting choice instead of secretly forcing Servo AF.

The practical operating model is:

| Question | Control |
|---|---|
| What am I photographing? | Select the applicable profile or C1-C3 mode. |
| Should the camera find and follow the subject? | Use AF-ON. |
| Should Face + Tracking prioritize an eye? | Use SET while a compatible AF method is active. |
| Do I need to place focus exactly here? | Use AE Lock. |
| Is the subject still or moving? | Start with the profile's AF Operation; use the DOF button if it needs to change. |

The objective is constant muscle memory: M-Fn selects the registered shooting environment, SET chooses eye priority when supported, AF-ON provides intelligent acquisition, AE Lock provides precise placement, and the joystick positions or recenters the deliberate AF point. Both AF-start buttons respect the profile-selected or DOF-selected AF Operation.

## How it Works

The selected profile or C mode loads the shooting environment. SET can change the stored Eye Detection state when the active AF method supports it. AF-ON and AE Lock then temporarily choose tracking or precision without replacing the active One-Shot/Servo state. The DOF button changes only that AF Operation state.

### M-Fn: custom-mode switching

M-Fn is the direct entry point to the registered subject configurations. Press it repeatedly to switch among C1, C2, and C3 without changing the button assignments described above. The switching behavior and all three current camera-body registrations were physically verified in session 3; exact lens stabilization Mode 1/3 remains equipment-dependent.

### AF-ON: intelligent acquisition

AF-ON is for speed. Assign **Metering and AF start**, press **INFO**, and use:

| AF-ON INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | Face + Tracking |
| Servo AF characteristics | Maintain current setting |

AF-ON always selects the subject-aware tracking method and uses the profile's Subject Detection choice and the stored Eye Detection state. The profile establishes the initial Eye Detection state, and SET may change it situationally. With Servo AF active, focus continues updating as the subject moves. With One-Shot AF active, Face + Tracking can identify and acquire the subject, but it does not provide continuous Servo tracking.

### AE Lock: precision focus

AE Lock is for precision. Assign **Metering and AF start**, press **INFO**, and use:

| AE Lock INFO item | Setting |
|---|---|
| AF Operation | Maintain current setting |
| AF Method | 1-Point AF |
| Servo AF characteristics | Maintain current setting |

AE Lock gives exact point placement and avoids automatic subject switching. Subject Detection and Eye Detection remain stored, but they are not used by the 1-Point AF precision method. AE Lock uses the last 1-Point position rather than automatically recentering it. Use the joystick to move the point and press the joystick straight in to recenter. Do not describe AE Lock as changing the Subject Detection or Eye Detection menu values to OFF.

### SET: eye-priority toggle

SET is the direct eye-priority control. Assign **Eye detection** to SET. When Face + Tracking is active, pressing SET toggles the stored Eye Detection state between Enable and Disable. The state persists when switching between Face + Tracking and 1-Point AF, and AF-ON honors it when AF-ON invokes Face + Tracking.

SET has no effect while 1-Point AF or Spot AF is active because those methods cannot use Eye Detection. This is a persistent menu-state toggle, not the separate momentary **Eye Detection AF** custom-button function. As a slower alternative, press **AF Point Selection** and then **INFO** to toggle Eye detection when Face + Tracking is active.

### Why AF Operation remains current

AF Method and AF Operation answer different questions:

- **AF Method:** should the camera find the subject, or should the photographer place one point?
- **AF Operation:** should focus lock once, or continue updating?

The profile supplies the normal One-Shot/Servo starting point. The DOF button changes that state when the subject behaves differently than expected. Because both AF-start buttons maintain AF Operation, either button respects the profile and the DOF-button change.

### DOF: One-Shot and Servo switching

The DOF button changes AF Operation between **One-Shot AF** and **Servo AF** without changing AF Method, Subject Detection, or Eye Detection. Use it when the subject's movement differs from the profile's expected starting behavior. Both AF-ON and AE Lock honor the resulting AF Operation.

### Joystick: position and recenter

The joystick directly moves the selected AF point or Face + Tracking starting position. During Face + Tracking subject adjustment, move the joystick to choose among detected faces or eyes. A manually chosen face or animal can become the subject the camera locks onto and tracks. This selection does not change Subject Detection or Eye Detection; SET remains assigned to toggle the stored Eye Detection state.

> **CAUTION — PROVISIONAL, NOT DEFINITIVE: USE WITH CAUTION; PHYSICAL TESTING IS REQUIRED.** Canon documents pressing the joystick straight in as centering the AF point or initial Face + Tracking Servo position. The owner has also observed a Face Select change from a straight press under the current control configuration, but the meanings of the single border, double border, and **Face Select: Off** display have not been physically established. Do not rely on straight press as a Face Select or tracking-release toggle until the test below proves the behavior.

AE Lock remembers the last 1-Point position, so the confirmed centering behavior remains important when the previous precision-point position is no longer useful.

#### Physical test: joystick straight press

**Status:** Pending owner verification on the camera.

Use still-photo mode with **Servo AF**, **Face + Tracking**, **Subject Detection: People**, **Eye Detection: Enable**, the joystick assigned to **Direct AF point selection**, and SET assigned to **Eye detection**. Frame two clearly separated faces in good light.

| Step | Action | Record |
|---|---|---|
| 1 | Without pressing AF-ON, observe both detected faces. | Which face or eye is initially active and what frame/icon identifies it? |
| 2 | Move the joystick left and right without first pressing it straight in. | Does selection move directly among faces or eyes, or is another selection state required? |
| 3 | Press the joystick straight in once. | Does it center an initial AF position, display or enable Face Select, release a selected subject, or perform more than one action? |
| 4 | Move the joystick left and right again. | Does it now cycle among detected faces or eyes differently from step 2? |
| 5 | Select one face, hold AF-ON, and recompose while both faces remain visible. | Does the camera stay locked to the manually selected subject? |
| 6 | Release AF-ON, then press it again without changing composition. | Does the manual subject selection persist between AF starts? |
| 7 | Press the joystick straight in a second time. | Does it exit Face Select, release tracking, center the starting position, or leave the selected subject unchanged? |
| 8 | Press SET once. | Confirm that Eye Detection toggles. Also record whether the selected-subject lock changes; do not assume SET retains Canon's default tracking-release behavior after customization. |
| 9 | If the subject remains locked, test the on-screen **Subject tracking release** control and the AF Point Selection button separately. | Identify the reliable release method that does not change the SET Eye Detection assignment. |

Repeat steps 1–9 with **Subject Detection: Animals** and two detectable animal faces if practical. Record the observed screen labels or photograph the displays so the final documentation can distinguish owner-confirmed behavior from Canon's general instructions.

### Multi-function Lock: when controls stop responding

The Multi-function Lock button toggles whichever physical controls are checked under **Set-up > Multi function lock**. It does not lock individual settings or preserve everything except the last-adjusted value. Depending on the configured checkmarks, it can disable direct use of the Main Dial, Rear Wheel, Top Rear Dial, joystick, control ring, and/or touchscreen.

If **LOCK** appears or the joystick or exposure dials stop responding, press the Multi-function Lock button once and try again. This applies across camera functions and shooting modes, not only Fv. Lock the controls again after setup when protection from accidental movement is more important than immediate adjustment.

### AF Point Selection: exception methods

Press **AF Point Selection**, then use the **Main Dial** when Spot AF, Expand AF Area, or another method is demonstrably better than the standard AF-ON or AE Lock choices. With Face + Tracking active, INFO provides the slower alternative for changing Eye Detection.

## Design Philosophy

1. **Keep button behavior constant.** Muscle memory should not change when the subject changes.
2. **Profiles define the shooting environment.** A profile establishes exposure, drive, stabilization, initial AF Operation, Subject Detection, Eye Detection, and other subject-specific settings.
3. **Subject Detection belongs to the profile—not the buttons.** Wildlife prioritizes Animals; a people setup prioritizes People; a motorsports setup may prioritize Vehicles.
4. **Use overrides only when they provide a measurable operational advantage.** The tracking and precision buttons cover the two common focusing decisions. Spot AF or Expand AF Area remains available when a specific situation justifies another method.
5. **Preserve muscle memory whenever possible.** C1-C3 change the environment; AF-ON and AE Lock keep the same jobs.

## Subject Detection Workflow

Subject Detection is part of the shooting profile. It is not part of the tracking-versus-precision button choice.

| Subject environment | Subject Detection |
|---|---|
| Wildlife | Animals |
| Family / people | People |
| Motorsports | Vehicles |
| Landscape | None |

Changing Subject Detection changes what AF-ON prioritizes while its physical behavior remains constant. AE Lock continues to provide deliberate 1-Point placement regardless of the selected subject category.

The profile also supplies the initial Eye Detection state. SET can change that stored state situationally when the active AF method supports Eye Detection, and AF-ON honors the resulting state when it invokes Face + Tracking.

Changing from the complete Wildlife card to the complete People card involves more than Subject Detection: the current project cards also differ in drive, shutter target, and aperture strategy. Changing only Subject Detection is appropriate when the existing exposure and drive environment is already suitable.

## C1-C3 Registration Reference

C1-C3 are not alternate AF buttons or AF-only presets. Each recalls a complete shooting environment derived from an established subject card. The cards remain concise field references; this matrix is the single registration reference for the profile-defining settings. Shared Set & Forget settings remain on Camera Setup Essentials and are intentionally not repeated here.

Camera Defaults and the shared operational baseline provide the general-purpose Case A (Auto) state. C1 Wildlife intentionally differs by selecting **Case 1 (Custom)**, configured once at Tracking Sensitivity -1 and Accel./Decel. tracking +1. Canon's factory Case 1 is 0 / 0, so verify the custom values in addition to the shared setup, controls, Auto update setting, and every registered C mode after a reset or recovery operation.

The exact starting values below convert card ranges and situational guidance into reproducible registrations. Settings not governed by this project remain unchanged and must not be guessed. The **Lens IS switch** is a physical pre-shoot check rather than a camera-registered menu value.

| Setting | C1 — Wildlife | C2 — Birds in Flight | C3 — Landscape |
|---|---|---|---|
| **Mode** | Fv | Tv | Av |
| **Metering** | Evaluative | Evaluative | Evaluative |
| **Exposure Compensation** | 0 | 0 starting point; adjust for background in the field | 0 |
| **Shutter Speed** | Auto | **1/2500 sec** | Auto |
| **Aperture** | Auto | Auto | **f/9** |
| **ISO** | Auto | Auto | 100 |
| **Auto ISO Maximum** | 12800 | 12800 | 12800; inactive while ISO 100 is fixed |
| **AF Operation** | Servo AF | Servo AF | One-Shot AF |
| **Servo AF Case** | **Case 1 (Custom)** | **Case 4** | Case A (Auto); inactive in One-Shot AF |
| **Tracking / Accel.-Decel.** | **-1 / +1** | **0 / +1** | Auto / Auto; inactive in One-Shot AF |
| **Switching tracked subjects** | On subject | On subject | On subject; inactive with 1-Point AF |
| **AF Method** | Face + Tracking | Face + Tracking | 1-Point AF |
| **Subject Detection** | Animals | Animals | None |
| **Eye Detection** | Enable | Enable | Disable |
| **Drive Mode** | High Speed Continuous | High Speed Continuous+ | Single Shot |
| **High speed display** | Enable | Enable; stored but inactive with High Speed Continuous+ | Enable; stored but inactive with Single Shot |
| **Shutter Type** | EFCS | Mechanical | EFCS |
| **Image Stabilizer Mode** | Mode 1 | Mode 3 | Mode 1 |
| **IBIS** | On | On | On |
| **Lens IS switch** | On; physical check | On; physical check | On for the registered handheld starting state; turn off for tripod use |
| **Focus Bracketing** | Disable | Disable | Disable; enable situationally for near-to-far depth of field |
| **Current verification state** | Camera-body verified; lens Mode 1 pending | Camera-body verified; lens Mode 3 pending | Camera-body verified; lens Mode 1 pending |

The C2 starting shutter is **1/2500 sec**: fast enough for normal birds-in-flight action while giving the camera more opportunity to retain useful aperture and depth of field than a 1/4000-sec default. Raise it toward 1/3200–1/4000 when wing speed or subject motion requires it. The C3 starting aperture is **f/9**, the practical middle of the card's f/8–f/11 range.

### Registration sequence

1. Confirm the approved shared button and dial layout.
2. Set **Custom shooting mode (C1-C3) > Auto update set.** to **Disable**.
3. Configure every row in the applicable matrix column. Confirm physical lens controls separately.
4. Use **Set-up > Custom shooting mode (C1-C3) > Register settings** and select the intended C1, C2, or C3 slot.
5. Leave the mode, recall it with M-Fn, and verify the complete matrix column rather than assuming registration succeeded.
6. Record the verification state and save a named camera-settings file after all three modes are confirmed.

### C1 — General Wildlife

C1 implements the Wildlife card for animals that are stationary, moderately active, or moving unpredictably without requiring the full action setup. It selects the project-customized Case 1 preset at -1 / +1 so brief foreground obstacles are less likely to steal focus while Servo AF remains responsive to abrupt speed changes. This is not Canon's factory 0 / 0 Case 1.

Examples include perched birds, deer, herons, eagles on a perch, and ducks on the water. Its priorities are deliberate composition, useful image quality, Animal Detection, Eye Detection, and a continuous drive appropriate for wildlife behavior.

The operating idea is: **the animal is already there**.

- Use AF-ON for fast animal/eye acquisition.
- Use AE Lock for precise focus through grass, branches, or other obstructions.
- Select Spot AF or Expand AF Area manually only when it provides a measurable advantage over the two standard buttons.

### C2 — Birds in Flight / Action

C2 implements the Birds in Flight card for fast-moving wildlife: birds in flight, osprey diving, ducks taking off, swallows, or running animals.

It retains the same button layout, Animal Detection, Eye Detection, metering philosophy, and tracking-versus-precision choice as C1. Its primary differences are the shooting environment: a 1/2500-sec registered starting shutter, High Speed Continuous+, Tv exposure, Servo AF Case 4 for abrupt speed changes, and Mode 3 stabilization.

The operating idea is: **the animal is moving fast**.

- Use AF-ON as the primary tracking control.
- Use AE Lock when automatic selection repeatedly chooses the wrong subject.
- Use Expand AF Area manually when subject size, obstruction, or background makes it measurably more reliable.
- Raise the shutter speed when necessary for faster action, but do not use 1/4000 sec by default when the resulting wide aperture would reduce needed depth of field.

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
- f/9 registered starting aperture
- One-Shot AF
- Single Shot
- Mode 1 and stabilization on as the handheld starting state
- Tripod, stabilization, and near-to-far sharpness checks

Use AE Lock for normal deliberate 1-Point placement. AF-ON remains available when subject-aware acquisition is useful, and it still maintains C3's One-Shot AF unless the DOF button changes the operation.

For tripod work, turn off stabilization after recalling C3. For a scene that needs greater near-to-far depth of field, enable Focus Bracketing situationally rather than treating a very small aperture as the permanent registration.

In the normal `C3LANDSC` configuration, People does not use a C-mode slot. For an occasional people or family shoot, start with **C1**, because it already provides Fv, Auto ISO, Servo AF, Eye Detection, and general handheld stabilization. If people photography will dominate the session, load the alternate `C3PEOPLE` complete configuration described above instead. Otherwise, make these changes from C1:

| Setting | Change for people |
|---|---|
| Servo AF Case | Change Case 1 (Custom) to Case A (Auto) through My Menu: AF Case |
| Subject Detection | Change Animals to People |
| Drive | Change High Speed Continuous to Low Speed Continuous |
| Shutter target | Use 1/200-1/320 for portraits or 1/500+ for active people |
| Aperture target | Use f/1.8-f/4 for one person or f/4-f/8 for a group |

Keep AF-ON for face/eye acquisition and AE Lock for exact 1-Point placement. Do not start from C3 for people while the normal `C3LANDSC` configuration is loaded; in that set, C3 recalls the Landscape settings—ISO 100, One-Shot AF, Single Shot, and f/9.

### My Menu: SWITCH

Use one My Menu tab named **SWITCH** as the starting menu for transitions from the registered C1-C3 profiles to People, Macro, and Waterdrops. The interface keeps its established green treatment as a visual cue. My Menu items are shortcuts to the camera's real settings; selecting an item opens that setting, and it does not apply a complete profile automatically.

| Target | Best starting mode | Already close | Remaining changes | SWITCH items used |
|---|---|---|---|---|
| **People** | **C1 Wildlife** | Fv, Auto ISO, Servo AF, Face + Tracking, Eye Detection, Mode 1 | Case 1 (Custom) to Case A, Animals to People, High to Low Speed Continuous, EFCS to Mechanical, portrait shutter/aperture targets | Subject to detect; Shutter mode; use AF Case separately |
| **Macro** | **C3 Landscape** | Av, One-Shot AF, Single Shot, EFCS, Mode 1, suitable aperture range | ISO 100 to Auto, 1-Point to Spot AF, enable Focus Bracketing, set f/8 | Focus bracketing |
| **Waterdrops** | **C3 Landscape** | ISO 100, Single Shot, aperture near f/8-f/11 | Av to Manual, 1/200 sec., Mechanical, Manual Focus, stabilization Off | Shutter mode; IS (Image Stabilizer) mode |

Configure the **SWITCH** tab in this starting order:

1. **Subject to detect**
2. **Shutter mode**
3. **Focus bracketing**
4. **IS (Image Stabilizer) mode**
5. **Cropping/aspect ratio**

Leave the sixth position open until field testing identifies another menu-only need. Cropping/aspect ratio provides a fast way to find and clear a temporary 1.6× crop after wildlife or distant-subject work.

Use Q, the dials, or the AF-point controls for Drive Mode, ISO, shutter speed, aperture, and AF Method when those controls are faster. Keep lens AF/MF and IS switches as physical checks. With **Auto update set.: Disable**, these transition changes must not rewrite the registered C1-C3 starting environments.

### My Menu: AF Case

Use a separate My Menu tab named **AF Case** for Servo AF tracking behavior. Configure it in this order:

1. **Servo AF**
2. **Tracking Sensitivity**
3. **Accel./Decel. tracking**
4. **Switching tracked subjects**

On the EOS R5, **Servo AF** in this tab is the shortcut to the Case selector; it is not the AF Operation setting. Continue to use Q or the DOF button to change AF Operation between One-Shot AF and Servo AF.

The Wildlife, Birds in Flight, Birds Perched, People, and Sports cards show **AF Case** in their field routes because they use its applicable controls. The colored **Servo AF Case** value identifies the Case shortcut. Case 1 (Custom) and Case 4 cards also show the effective Tracking Sensitivity and Accel./Decel. tracking values together on one **Track / Accel** row. Compatible Face + Tracking, Zone AF, and Large Zone AF cards show **Switching Tracked Subjects** separately because it changes recognized-subject selection rather than Servo response.

Keep **Auto update set.: Disable** before making a temporary Case or parameter change inside C1–C3. Restore the profile's approved Case after testing unless the change is deliberately re-registered.

#### Other My Menu tabs to consider

The EOS R5 can hold up to five My Menu tabs. Beyond the approved **SWITCH** and **AF Case** tabs, create another tab only when repeated field use justifies it. The following are evaluation categories, not approved camera configurations:

| Candidate tab | Purpose | Items to consider |
|---|---|---|
| **FOCUS** | Macro, focus stacking, and deliberate manual focus | Focus bracketing; MF peaking settings; Focus guide; IS (Image Stabilizer) mode |
| **FLASH** | Waterdrops, macro flash, and people flash | External Speedlite control; Shutter mode; Expo. simulation; Image review |
| **LONG** | Landscape, fireworks, and night work | Bulb timer; Interval timer; Long exp. noise reduction; IS (Image Stabilizer) mode; Shutter mode |
| **FIELD** | Temporary capture conditions that are easy to leave active | Anti-flicker shoot.; Cropping/aspect ratio; Expo. simulation; Image review |
| **TRANSFER** | In-camera selection and phone or network transfer | Wi-Fi/Bluetooth connection; Protect images; Rating images; Image search conditions |

Consider these cautions before creating another tab:

- Do not fill all five tabs merely because they are available. More tabs increase navigation and make the important SWITCH and AF Case tabs less immediate.
- Do not duplicate SWITCH or AF Case items on another tab unless repeated use within that workflow clearly saves time.
- Prefer Q, a dial, a customized button, the AF-point controls, or a physical lens switch whenever it is faster than opening My Menu.
- Treat conditional items carefully. A menu item may move, disappear, or behave differently with another shooting mode, lens, flash, trigger, or firmware version.
- Keep destructive or recovery operations such as **Format card**, **Reset camera**, **Clear settings**, and bulk-delete commands out of frequently used field tabs.
- Use **Menu display: Display from My Menu tab** rather than **Display only My Menu tab** so the full camera menus remain available.
- Remember that a My Menu shortcut opens the real setting. It does not store a preferred value, apply several changes together, or replace a C1-C3 registration.
- Recheck the tabs after a firmware update, camera reset, or loading a saved camera-settings file.

### Protect the registered modes: disable Auto update

**Strong recommendation: set `Custom shooting mode (C1-C3) > Auto update set.` to `Disable` and leave it disabled.**

With Auto update enabled, a temporary field change made while using C1, C2, or C3 can be written back into that registered mode. The custom mode may then stop matching its documented subject card without an obvious warning. That defeats the purpose of using C1-C3 as reliable, repeatable starting environments.

With Auto update disabled, temporary changes remain temporary. Make an intentional change to a registered mode by configuring the camera as desired and using **Register settings** again—not by allowing field adjustments to accumulate automatically.

Check this setting after a reset, after loading a camera-settings file, and after any firmware-related settings reset.

### Save alternate complete configurations to a card

After C1-C3 are registered and verified, use **Set-up 5 > Save/load cam settings on card > Save to card** to preserve the complete camera configuration. Canon describes these files as saving current shooting, menu, and Custom Function settings. A card can hold up to ten files, and each file can be given an eight-character name with the INFO button before saving.

This makes it practical to keep multiple named sets when the best use of a C-mode slot changes. For example:

| Settings file | C1 | C2 | C3 | Use |
|---|---|---|---|---|
| `C3LANDSC` | Wildlife | Birds in Flight | Landscape | Normal wildlife and landscape set |
| `C3PEOPLE` | Wildlife | Birds in Flight | People | Event, family, or portrait set |

Loading one of these files restores the **complete saved camera configuration**, not only C3. Confirm the loaded C1-C3 registrations, button assignments, and **Auto update set.: Disable** before the shoot. Save a fresh backup after any intentional configuration change.

Keep settings files with the camera and copy them elsewhere for recovery. A file from another camera model cannot be loaded, and a file saved under a different firmware version may not load, so create a new verified backup after firmware changes.

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
- Press M-Fn repeatedly to move among C1, C2, and C3.
- Use AF-ON when the camera should identify and follow the subject.
- Use AE Lock when exact placement is more important than automatic recognition.
- Use the DOF button only when the profile's starting One-Shot/Servo state no longer matches subject movement.
- Use AF Point Selection + Main Dial for a justified Spot AF or Expand AF Area exception.
- Press the joystick straight in to recover quickly when the AF point has moved away from the desired starting position.

## When Not to Use

- Do not press AF-ON and AE Lock together.
- Do not expect shutter half-press to refocus.
- Do not describe AF-ON as continuous tracking when One-Shot AF is active.
- Do not describe AE Lock as turning profile Subject Detection or Eye Detection settings OFF.
- Do not force Servo AF from either AF-start button; doing so would defeat the DOF-button workflow.
- Do not assume a selected C mode contains its documented profile until that registration has been verified.
- Do not treat C1-C3 as AF-only controls.

## Decision Guide

| Situation | Control | Action |
|---|---|---|
| Load general wildlife environment | **C1** | Recall the Wildlife card. |
| Load birds-in-flight/action environment | **C2** | Recall the Birds in Flight card. |
| Load landscape environment | **C3** | Recall the Landscape card. |
| Let the camera find the subject | **AF-ON** | Use Face + Tracking with the current AF Operation. |
| Toggle eye priority for Face + Tracking | **SET** | Toggle the stored Eye Detection state while a compatible AF method is active. |
| Focus exactly at one point | **AE Lock** | Use 1-Point AF with the current AF Operation. |
| Change between still and moving focus behavior | **DOF button** | Switch One-Shot AF ↔ Servo AF. |
| Select Spot, Expand, or another AF method manually | **AF Point Selection** | Press it and use the Main Dial. |
| Move the active AF point | **Joystick** | Move the point or starting position directly. |
| Choose among detected faces or eyes | **Joystick** | During Face + Tracking subject adjustment, move the joystick toward the intended face or eye. |
| Return the AF point to center | **Joystick** | Press straight in. |
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
- Eye detection can be assigned to SET as a persistent Enable/Disable toggle; it is distinct from the momentary Eye Detection AF function.
- The camera provides Face + Tracking, 1-Point AF, Spot AF, Expand AF Area, and other documented AF methods.
- Subject to Detect applies to compatible subject-aware methods. It does not need to be changed when a deliberate-point method is used.
- The Control Ring may be on an RF lens or an EF-EOS R control ring adapter.

Project configuration:

- The physical control layout is the project owner's confirmed layout.
- Face + Tracking on AF-ON and the SET Eye detection assignment are owner-confirmed on the camera.
- C1 Wildlife, C2 Birds in Flight, and C3 Landscape were registered, recalled, and camera-body verified in physical session 3. Exact lens stabilization Mode 1/3 remains equipment-dependent.
- Historical screenshots are not current-state evidence.
- Plain physical names are used so the layout is readable in the field.

## Tips

- Practice the field model: select the profile, set eye priority when needed, choose AF-ON or AE Lock, then use DOF only if motion behavior changes.
- Keep **Auto update set.** disabled so field adjustments cannot silently rewrite C1-C3.
- Save named camera-settings files after registering and verifying C1-C3, and create a fresh file after firmware changes.
- Test AF-ON and AE Lock in both Servo AF and One-Shot AF to confirm that neither button forces AF Operation.
- Confirm SET changes Eye Detection when Face + Tracking is active and expect no effect with 1-Point AF or Spot AF.
- Remember that AE Lock returns to the last 1-Point position; press the joystick straight in when a centered point is needed.
- With multiple detected faces or eyes, use joystick movement to choose the intended subject; complete the straight-press test before relying on it as a Face Select or release toggle.
- Verify C1, C2, and C3 after registration by checking exposure, drive, AF Operation, Subject Detection, and stabilization.
- Test the 1-Point override on a high-contrast stationary subject and through foreground clutter.
- Photograph the finished control and custom-mode pages after physical verification.
- Recheck assignments after a reset or firmware-related settings reset.

## Common Mistakes

- Treating C1-C3 as AF-only presets instead of complete subject cards.
- Enabling Auto update and unintentionally teaching a C mode temporary field settings.
- Assuming a saved camera-settings file changes only one C mode; loading it restores the complete saved configuration.
- Expecting AF-ON to force Servo AF.
- Expecting continuous tracking while One-Shot AF is active.
- Expecting Eye Detection behavior while the 1-Point override is active.
- Expecting SET to toggle Eye Detection while 1-Point AF or Spot AF is active.
- Assuming AE Lock changes Subject Detection or Eye Detection menu values.
- Assuming AE Lock automatically recenters its 1-Point position.
- Assuming joystick face/eye selection changes the stored Subject Detection or Eye Detection setting.
- Pressing AF-ON and AE Lock together.
- Confusing an approved target assignment with a setting already verified on the camera.
- Assuming C1's present registration matches the complete Wildlife card without verification, or expecting C2/C3 to be populated before registration.

## Cross References

- Card: Camera Buttons.
- Custom modes: C1 Wildlife (General Wildlife field label), C2 Birds in Flight (Birds in Flight / Action field label), C3 Landscape.
- Profiles: Wildlife, Birds in Flight, Landscape, Birds Perched, People, Sports, Macro, Travel, Fireworks, Waterdrops.
- Related guides:
  - [AF Cases & Tracking Behavior](appendix:af_cases_tracking)
  - [R5 Quick Reference](appendix:r5_quick_reference)
