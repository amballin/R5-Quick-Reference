# R5 Quick Reference

## Overview

Use this quick reference when a card setting is not obvious, especially AF Operation, AF tracking behavior, Subject Detection, Eye Detection, AF Method, Focus Mode, Drive Mode, Metering Mode, Shutter Speed, Cropping/aspect ratio, Image Stabilization Mode, IBIS, Lens IS, Shutter Type, flash behavior, Focus Bracketing, or Long Exposure Noise Reduction. Basic exposure terms such as Mode, Aperture, ISO, and Auto ISO Max are intentionally kept out of the main quick reference.

## Topic Index

- [LOCK Displayed or Controls Will Not Change](#lock-displayed-or-controls-will-not-change)
- [Exposure and Shutter](#exposure-and-shutter)
  - [Shooting Modes](#shooting-modes)
  - [Metering Mode](#metering-mode)
  - [Shutter Speed](#shutter-speed)
  - [Shutter Type](#shutter-type)
- [Autofocus and Manual Focus](#autofocus-and-manual-focus)
  - [Focus Mode](#focus-mode)
  - [AF Operation](#af-operation)
  - [AF Method](#af-method)
  - [Subject Detection](#subject-detection)
  - [Eye Detection](#eye-detection)
  - [Subject Detection and AF Method Combinations](#subject-detection-and-af-method-combinations)
  - [AF Tracking Behavior](#af-tracking-behavior)
- [Capture and Timing](#capture-and-timing)
  - [Cropping / Aspect Ratio](#cropping-aspect-ratio)
  - [Drive Mode](#drive-mode)
- [Flash](#flash)
  - [Flash Modes and Compatibility](#flash-modes-and-compatibility)
- [Stabilization](#stabilization)
  - [Image Stabilization](#image-stabilization-mode)
- [Specialized Focus and Long-Exposure Tools](#specialized-focus-and-long-exposure-tools)
  - [Focus Features](#focus-features)
  - [Focus Bracketing](#focus-bracketing)
  - [Long Exposure Noise Reduction](#long-exposure-noise-reduction)

## Decision Guide

### LOCK Displayed or Controls Will Not Change

Press the **Multi-function Lock button** once to unlock the controls, then retry the adjustment. The button toggles the physical controls selected under **Set-up > Multi function lock**, which may include the Main Dial, Rear Wheel, Top Rear Dial, joystick, control ring, and touchscreen. It does not lock individual settings.

This can affect any shooting mode. In Fv it may prevent the Top Rear Dial from selecting an exposure parameter or the Main Dial from changing its value. After making the adjustment, lock the controls again only when preventing accidental changes is worth giving up immediate access.

### Exposure and Shutter

#### Shooting Modes

Canon EOS R5 shooting modes define how exposure decisions are divided between the photographer and the camera.

##### Choosing Shooting Mode: P vs Fv vs Av/Tv/M

Use P for simple Program AE when you want low-friction general shooting and are happy for the camera to choose shutter speed and aperture.

Use Fv as the flexible R5 general-purpose mode. It can behave like P, but lets you quickly take control of shutter speed, aperture, ISO, or exposure compensation without changing modes. In this project, consider both P and Fv for general shooting; Fv is often better for an experienced R5 user because it gives selective control while staying fast. For full setup guidance, see [Fv (Flexible Priority)](appendix:fv_flexible_priority).

In Fv, turn the **Top Rear Dial (Quick Control Dial 2)** to select an exposure parameter and the **Main Dial** to change it. Press the **Erase (trash-can) button** to return shutter speed, aperture, or ISO to AUTO, or exposure compensation to ±0. If **LOCK** appears, press the Multi-function Lock button first.

Use Av when aperture and depth of field are the main decision, such as landscapes, portraits, perched birds, natural-light macro, and tripod/still scenes.

Use Tv when shutter speed is the main decision, such as birds in flight, sports, active wildlife, and fast action.

Use M when controlled or repeatable exposure matters more than camera automation, such as waterdrops, flash macro, studio flash, and repeatable night setups.

Use Bulb only for long manual exposures where you directly control how long the shutter stays open.

| Icon | Setting | Canon Name | What it Does |
|---|---|---|---|
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **A+** | Scene Intelligent Auto | Camera analyzes the scene and sets optimum settings automatically. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **Fv** | Flexible-priority AE | Allows shutter speed, aperture, ISO, and exposure compensation to be manual or automatic. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **P** | Program AE | Camera automatically sets shutter speed and aperture for subject brightness. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **Tv** | Shutter-priority AE | You set shutter speed; the camera sets aperture for standard exposure. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **Av** | Aperture-priority AE | You set aperture; the camera sets shutter speed for standard exposure. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **M** | Manual exposure | You set shutter speed and aperture and judge exposure from the exposure indicator. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **BULB** | Bulb | Shutter remains open while the shutter button is held for long exposures. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **C1** | Custom shooting mode 1 | Recalls registered camera settings. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **C2** | Custom shooting mode 2 | Recalls registered camera settings. |
| ![Mode selector](../../60 Assets/icons/canon_r5_official/mode-select.svg) | **C3** | Custom shooting mode 3 | Recalls registered camera settings. |

**Camera Menu:** MODE button, then Main dial. Custom modes are registered under Set-up > Custom shooting mode (C1-C3). The owner-confirmed M-Fn assignment switches among C1, C2, and C3; C1 currently contains registered settings, while C2 and C3 are not yet registered.

**Quick Menu:** Exposure mode is normally changed with the MODE button, not the Q screen.

#### Metering Mode

Use Evaluative as the general default, including for backlit subjects. For bright sky, snow, dark backgrounds, and other difficult scenes, normally keep Evaluative and adjust exposure compensation while checking the RGB histogram and highlight alert.

Partial and Spot meter only the center of the EOS R5 screen; Spot does not follow the active AF point. Use them only when you deliberately place the tone to measure under the center metering area. Partial is the more forgiving choice when a centered subject is surrounded by much brighter light. Spot is for precise measurement of a specific tone and may require compensation when that tone is lighter or darker than a middle tone. Center-weighted is most useful when the important subject stays near the center and you want the rest of the frame to retain some influence.

| Icon | Setting | What it Does |
|---|---|---|
| ![Evaluative metering](../../60 Assets/icons/canon_r5_official/evaluative_metering.svg) | Evaluative | Reads the whole scene; best general default across the documented profiles. |
| ![Partial metering](../../60 Assets/icons/canon_r5_official/partial_metering.svg) | Partial | Meters approximately 6.1% at the screen center when a much brighter background should have less influence. |
| ![Spot metering](../../60 Assets/icons/canon_r5_official/spot_metering.svg) | Spot | Meters approximately 3.1% at the screen center for deliberate measurement of a specific tone. |
| ![Center-weighted average metering](../../60 Assets/icons/canon_r5_official/center_weighted_average_metering.svg) | Center-weighted | Averages the whole screen while weighting its center more heavily. |

**Camera Menu:** Shooting menu > Metering mode.

**Quick Menu:** Q screen. M-Fn is reserved for switching among C1-C3.

#### Shutter Speed

Shutter speed controls motion. Action profiles use fast shutter speeds; long exposure profiles use slow shutter speeds.

| Setting | What it Does |
|---|---|
| Fast shutter speed | Freezes motion for action, wildlife, or sports. |
| Slow shutter speed | Allows long exposures for fireworks, night work, or blur effects. |
| Camera-selected shutter speed | Lets the camera choose shutter speed from the exposure mode. |

**Camera Menu:** Tv or Manual exposure shutter speed control; Av/P/Fv allow the camera to choose shutter speed.

**Quick Menu:** Top dial / Q screen depending on exposure mode.

#### Shutter Type

EFCS is the approved EOS R5 baseline pending physical verification. It starts the exposure electronically and ends it with the mechanical second curtain, which removes first-curtain shutter shock without taking on the major motion-distortion and flash restrictions of fully Electronic shutter. It is not silent.

| Setting | What it Does |
|---|---|
| Mechanical | Use for fast shutter speeds near maximum aperture and conservative third-party flash/trigger compatibility. |
| EFCS | General baseline; reduces vibration, retains broad motion and flash compatibility, and normally minimizes artificial-light banding. |
| Electronic | Silent and up to approximately 20 fps, but watch for rolling shutter, banding, and flash restrictions. |

Use Mechanical for People, Birds in Flight, Sports, and Waterdrops. These profiles prioritize clean wide-aperture bokeh at fast shutter speeds or a conservative third-party flash/trigger workflow. Use EFCS for general shooting, Travel, Wildlife, Birds Perched, Landscape, ambient-light or focus-bracketed Macro, and Fireworks. The R5 automatically uses EFCS for Bulb exposures.

Canon warns that EFCS can render defocused highlights incompletely when the lens is near maximum aperture at high shutter speeds. Lower the shutter speed, stop down, or switch to Mechanical when background highlights look clipped. Mechanical and EFCS avoid the major fast-subject distortion associated with fully Electronic shutter and normally handle flickering artificial light much more reliably, but test the actual lighting and use Anti-flicker shooting when needed.

On the R5, Mechanical and EFCS both reach approximately 12 fps in High Speed Continuous+. In regular High Speed Continuous, Canon specifies approximately 6 fps with Mechanical and 8 fps with EFCS. Normal flash sync is up to 1/200 sec. with Mechanical and 1/250 sec. with EFCS; attached flashes, triggers, and other conditions may impose lower limits.

For Canon's fuller explanation and example use cases, see [A Look at the Shutter Modes in Canon EOS Cameras](https://www.usa.canon.com/learning/training-articles/training-articles-list/a-look-at-the-shutter-modes-in-canon-eos-cameras).

**Camera Menu:** Shooting 6 > Shutter mode.

**Quick Menu:** Menu only.

### Autofocus and Manual Focus

#### Focus Mode

AF lets the camera drive focus. MF leaves focus under manual control from the lens or camera setting. When Focus Mode is MF, AF Method, Subject Detection, and Eye Detection do not help focusing.

| Icon | Setting | What it Does |
|---|---|---|
| ![AF](../../60 Assets/icons/canon_r5_official/lens_af.svg) | AF | Lets the camera or lens drive focus. |
| ![MF](../../60 Assets/icons/canon_r5_official/lens_mf.svg) | MF | Leaves focus under manual control from the lens or camera setting. |

**Camera Menu:** Lens AF/MF switch; AF1 > Focus mode when shown.

**Quick Menu:** Lens switch; usually not a Q item.

#### AF Operation

Use Servo AF for movement, One-Shot AF for static subjects, and Manual Focus when focus must stay locked or autofocus would hunt.

| Icon | Setting | What it Does |
|---|---|---|
| ![AF](../../60 Assets/icons/canon_r5_official/lens_af.svg) | Servo AF | Continuously updates focus for moving subjects. |
| ![AF](../../60 Assets/icons/canon_r5_official/lens_af.svg) | One-Shot AF | Locks focus for static or slow subjects. |
| ![MF](../../60 Assets/icons/canon_r5_official/lens_mf.svg) | Manual Focus | Stops autofocus hunting and keeps focus under manual control. |

**Camera Menu:** AF1 > AF operation; for Manual Focus use the lens AF/MF switch or AF1 > Focus mode when shown.

**Quick Menu:** Q screen for AF Operation. Manual Focus is usually the lens switch, not Q; M-Fn is reserved for switching among C1-C3.

#### AF Method

Face + Tracking is for subject-aware tracking. 1-Point AF is precise and predictable. Spot AF is smaller and more exact. Expand AF Area helps with action when tracking may lose the subject.

| Icon | Setting | What it Does |
|---|---|---|
| ![Face+Tracking](../../60 Assets/icons/canon_r5_official/face_tracking.svg) | Face + Tracking | Tracks recognized subjects across the frame. |
| ![1-point AF](../../60 Assets/icons/canon_r5_official/one_point_af.svg) | 1-Point AF | Gives predictable focus control on one selected point. |
| ![Spot AF](../../60 Assets/icons/canon_r5_official/spot_af.svg) | Spot AF | Uses a smaller point for very precise placement. |
| ![Expand AF area](../../60 Assets/icons/canon_r5_official/expand_af_area.svg) | Expand AF Area | Starts from one point but uses surrounding points to help with action. |
| screen-only | Not Used | AF method does not matter because autofocus is not controlling focus. |

**Camera Menu:** AF1 > AF method.

**Quick Menu:** AF point selection button, then Main Dial; the Q screen is the alternative. M-Fn is reserved for switching among C1-C3.

#### Subject Detection

Use People, Animals, or Vehicles when one category should receive priority. Use None when no category should receive priority; it does not disable automatic main-subject selection. AF Method, not Subject to Detect, determines whether a smaller manually positioned AF area controls focus.

| Icon | Setting | What it Does |
|---|---|---|
| ![People](../../60 Assets/icons/canon_r5_official/subject_to_detect_people.png) | People | Prioritizes human faces, heads, and eyes. |
| ![Animals](../../60 Assets/icons/canon_r5_official/subject_to_detect_animals.png) | Animals | Prioritizes animals and birds when recognized. |
| ![Vehicles](../../60 Assets/icons/canon_r5_official/subject_to_detect_vehicles.png) | Vehicles | Prioritizes racing cars and motorcycles when recognized. |
| ![None](../../60 Assets/icons/canon_r5_official/subject_to_detect_none.png) | None | Applies no People, Animals, or Vehicles priority; the camera still determines a main subject automatically from detected subject information. |

**Camera Menu:** AF1 > Subject to detect.

**Quick Menu:** Menu only.

#### Eye Detection

Enable it when Face + Tracking and subject detection are useful. It is not useful when AF is manual or when the selected AF method cannot use eye tracking.

| Icon | Setting | What it Does |
|---|---|---|
| ![Eye detection](../../60 Assets/icons/canon_r5_official/eye_detection.svg) | Enable | Lets compatible AF methods prioritize the subject's eye. |
| ![Eye detection](../../60 Assets/icons/canon_r5_official/eye_detection.svg) | Disable | Prevents eye priority when the AF area or subject choice should stay simpler. |
| ![Eye detection](../../60 Assets/icons/canon_r5_official/eye_detection.svg) | Not shown | Usually means AF is manual or the AF method cannot use eye tracking. |

**Camera Menu:** AF1 > Eye detection.

**Quick Menu:** With Face + Tracking active, press the AF point selection button and then INFO to toggle Eye detection. This shortcut is unavailable when the active AF method cannot use Eye detection.

Assigning **Eye Detection AF** to a custom button provides direct eye-detection autofocus while that button is used. It is not the same as persistently toggling the **Eye detection: Enable/Disable** menu setting.

In the owner-confirmed control layout, **SET** is assigned to **Eye detection**. It toggles the stored Enable/Disable state when the active AF method supports Eye detection and has no effect with 1-Point AF or Spot AF. The state persists when switching AF methods, and AF-ON honors it when AF-ON temporarily selects Face + Tracking.

#### Subject Detection and AF Method Combinations

Subject to Detect takes effect with Face + Tracking, Zone AF, and Large Zone AF on the original EOS R5. Spot AF, 1-Point AF, and Expand AF Area use deliberately positioned AF points instead, so changing Subject to Detect to None is unnecessary when switching to those methods. Eye Detection requires Face + Tracking. Manual Focus makes all AF settings irrelevant.

| Icon | Setting | What it Does |
|---|---|---|
| ![Face+Tracking](../../60 Assets/icons/canon_r5_official/face_tracking.svg) | Face + Tracking + subject detection | Best when the camera should identify and follow the subject. |
| ![Expand AF area](../../60 Assets/icons/canon_r5_official/expand_af_area.svg) | Spot, 1-Point, or Expand AF Area | Provides deliberate AF-point placement without requiring a Subject to Detect change. |
| screen-only | Zone or Large Zone AF + subject detection | Uses subject information within a controlled zone while retaining more automatic selection than Expand AF Area. |
| ![MF](../../60 Assets/icons/canon_r5_official/lens_mf.svg) | Manual Focus | Makes Subject Detection, Eye Detection, and AF Method irrelevant on the card. |

**Camera Menu:** AF1 > AF method; AF1 > Subject to detect; lens AF/MF switch or AF1 > Focus mode when shown.

**Quick Menu:** AF method via the AF point selection button and Main Dial. Subject Detection is menu only. Manual Focus is usually the lens switch. M-Fn is reserved for switching among C1-C3.

#### AF Tracking Behavior

Start with Canon's default Servo AF tracking behavior and change only the response that is causing a problem. These controls tune how Servo AF reacts; they do not replace AF Method, subject detection, or good subject acquisition.

| Control | What it Changes | Field Use |
|---|---|---|
| Tracking Sensitivity | How readily focus leaves the tracked subject when an obstacle or another subject enters the AF area | Move toward locked-on when brief obstructions steal focus; move toward responsive when intentional target changes feel slow. |
| Accel./Decel. Tracking | How strongly Servo AF anticipates abrupt speed changes | Increase for subjects that start, stop, or change speed unpredictably; leave near default for steady motion. |
| Subject switching | How readily subject detection transfers priority to another recognized subject | Reduce when the camera abandons the intended subject; increase when rapid handoffs are intentional. |

Change one control at a time and test it against the actual background and subject motion. For scenarios and troubleshooting, see [AF Cases & Tracking Behavior](appendix:af_cases_tracking).

**Camera Menu:** AF menu > Servo AF characteristics / Case settings and subject-tracking options.

**Quick Menu:** Menu only.

### Capture and Timing

#### Cropping / Aspect Ratio

Keep **Full-frame** as the Set & Forget starting point. Select **1.6× (crop)** temporarily when a distant bird, animal, or field-sports subject will remain predictably inside the smaller capture area and the enlarged view makes framing easier. Return to Full-frame after the session. This is a framing and file-workflow choice, not extra optical reach.

| Setting | Recorded pixels | Field use |
|---|---:|---|
| Full-frame | Approx. 44.8 MP (8192×5464) | Maximum resolution and maximum room to follow, crop, or recompose. |
| 1.6× (crop) | Approx. 17.3 MP (5088×3392) | Tighter displayed view and generally smaller files when the final image would clearly use only the sensor center. |

The camera records only the center area in 1.6× mode, including for RAW and cRAW, so the excluded area cannot be recovered later. The lower pixel count generally reduces file size, but actual size varies with image quality and subject content. Use Full-frame for erratic birds, rapidly approaching action, uncertain composition, or whenever maximum resolution and reframing room matter.

With **RF-S or adapted EF-S lenses**, the R5 automatically selects 1.6× crop and no Full-frame option is available while the lens is attached. RF and adapted EF lenses do not force crop mode.

**Temporary override process:** begin with Full-frame, select 1.6× only for the specific distant-subject situation, and restore Full-frame afterward. When working in C1-C3, keep **Auto update: Disable** so a temporary crop choice does not silently replace the registered subject setup.

**Camera Menu:** Shooting 1 > Cropping/aspect ratio.

**Quick Menu:** Menu only.

See Canon's [Still Photo Cropping/Aspect Ratio](https://cam.start.canon/en/C003/manual/html/UG-03_Shooting-1_0050.html) instructions and [EOS R5 recorded pixel counts](https://cam.start.canon/en/C003/manual/html/UG-09_Reference_0100.html).

#### Drive Mode

Single Shot is deliberate. Low or High Speed Continuous helps with expression, motion, and timing. High Speed Continuous+ maximizes capture rate but creates more files.

| Icon | Setting | What it Does |
|---|---|---|
| ![Single shooting](../../60 Assets/icons/canon_r5_official/single_shooting.svg) | Single Shot | Takes one frame per shutter press for deliberate work. |
| ![Low-speed continuous shooting](../../60 Assets/icons/canon_r5_official/low_speed_continuous_shooting.svg) | Low Speed Continuous | Captures short bursts without creating too many files. |
| ![High-speed continuous shooting](../../60 Assets/icons/canon_r5_official/high_speed_continuous_shooting.svg) | High Speed Continuous | Increases capture rate for movement and changing expressions. |
| ![High-speed continuous shooting plus](../../60 Assets/icons/canon_r5_official/high_speed_continuous_shooting_plus.svg) | High Speed Continuous+ | Maximizes capture rate for fast action, with more files to sort later. |
| ![10 sec. self-timer](../../60 Assets/icons/canon_r5_official/self_timer_10_sec_remote_control.svg) | Self-timer: 10 sec. | Delays capture for tripod work, group frames, or remote release timing. |
| ![2 sec. self-timer](../../60 Assets/icons/canon_r5_official/self_timer_2_sec_remote_control.svg) | Self-timer: 2 sec. | Delays capture briefly to let tripod shake settle after pressing the shutter. |

**Camera Menu:** Shooting menu > Drive mode.

**Quick Menu:** Q screen. M-Fn is reserved for switching among C1-C3.

Burst rate is conditional: shutter type, shutter speed, aperture, battery state, card speed, buffer state, flash recycle, and other camera conditions can prevent the advertised maximum rate. Silent capture uses Electronic shutter behavior, so its rolling-shutter, banding, and flash limitations still apply.

### Flash

#### Flash Modes and Compatibility

Use E-TTL when subject distance or ambient light changes; use Manual flash when repeatable output matters. Flash Exposure Compensation adjusts automatic flash brightness without changing ambient exposure. High Speed Sync permits shutter speeds above normal sync but reduces effective flash power.

| Setting | What it Does |
|---|---|
| E-TTL | Uses a metering preflash to set flash output automatically. |
| Manual flash | Holds a chosen power level for repeatable lighting. |
| Flash Exposure Compensation | Makes E-TTL flash brighter or darker while leaving its automatic calculation active. |
| High Speed Sync | Allows faster shutter speeds and wider apertures in bright light, with reduced range and power. |
| Rear-curtain sync | Fires near the end of the exposure so motion trails appear behind a moving subject. |

EFCS supports normal flash synchronization up to 1/250 sec. on the R5, while Mechanical supports up to 1/200 sec. Use Mechanical as the conservative starting point for unverified third-party flashes or triggers, including the documented Waterdrops setup, and test the complete combination before critical work. Flash is useful for nearby subjects; it will not illuminate distant fireworks or distant scenery. For lighting setups, wireless control, macro, and trigger guidance, see [Flash Photography](appendix:flash_photography).

**Camera Menu:** Shooting menu > External Speedlite control; compatible Speedlite or trigger controls may also set flash behavior.

**Quick Menu:** Flash Exposure Compensation may be available through Q or an assigned control; other choices depend on the attached flash.

### Stabilization

#### Image Stabilization Mode

This is the normal shake-reduction control, not IBIS High Resolution Shot. Stabilization reduces camera shake; it does not freeze subject movement.

**Camera setting**

`MENU → Shooting menu → IS (Image Stabilizer) mode`

Use this for normal body stabilization when the option is available, especially with a lens that has no optical IS switch. The Shooting-menu page number can change with shooting mode, attached lens, firmware, and other camera conditions, so find the exact Canon label rather than a fixed tab number.

**Lens control**

If the attached lens has an Image Stabilizer On/Off switch, use the lens switch. The camera's IS On/Off choice may be unavailable or behave differently while that lens is attached.

**IS Mode 1 / 2 / 3**

Select these with the physical Image Stabilizer mode selector on lenses that provide one:

- **1 — General:** general-purpose stabilization.
- **2 — Panning:** stabilization for deliberate panning.
- **3 — Erratic action:** stabilization applied primarily during exposure, when supported.

These lens modes are not normally selected from the EOS R5 camera menu. A lens without a mode switch does not gain Mode 1 / 2 / 3 choices in the camera menu.

**Interaction**

With a compatible lens switched On, lens optical IS and the R5's in-body stabilization coordinate automatically. Treat them as one coordinated system rather than two independent controls. For lens-specific switches, modes, and exceptions, see [Lens Capabilities](appendix:lens_settings).

**Solid tripod:** Follow the selected profile and lens-specific Canon guidance; turn stabilization Off for locked tripod or Bulb work when directed.

### Specialized Focus and Long-Exposure Tools

#### Focus Features

These features support manual focus precision and depth-of-field workflows. Keep the detailed setup in the focus appendix; cards should only show the setting when it matters.

| Icon | Setting | Canon Name | What it Does |
|---|---|---|---|
| ![Focus Bracketing](../../60 Assets/icons/canon_r5_official/focus-bracketing.svg) | Focus Bracketing | Focus Bracketing | Captures a sequence while automatically shifting focus after each shot. |
| ![Focus Guide](../../60 Assets/icons/canon_r5_official/focus-guide.svg) | Focus Guide | Focus Guide | Displays a guide frame showing direction and amount of manual focus adjustment. |
| ![MF Peaking](../../60 Assets/icons/canon_r5_official/focus-mf-peaking.svg) | MF Peaking | MF Peaking (Outline Emphasis) | Displays in-focus edges in color to make manual focusing easier. |

**Camera Menu:** Shooting menu > Focus bracketing; AF menu > Focus guide; AF menu > MF peaking settings.

**Quick Menu:** Menu only.

**Recommended MF Peaking setup:** **On**, **Level: Low**, **Color: Red**. Leave it enabled as a Set & Forget manual-focus aid. Peaking is not recorded in the image and does not change autofocus behavior. It is not shown during magnified viewing, and highlighted contrast edges do not guarantee exact focus, so use magnification as the final check for critical macro or landscape focus. See Canon's [Manual Focus](https://cam.start.canon/en/C003/manual/html/UG-04_AF-Drive_0090.html) instructions.

#### Focus Bracketing

Focus Bracketing captures a sequence while shifting focus through the subject. Use it when one frame cannot hold enough depth of field. For full setup guidance, see [Focus Bracketing & In-Camera Depth Compositing](appendix:focus_bracketing_depth_compositing).

| Setting | What it Does |
|---|---|
| Enable | Turns on focus-bracket capture for near-to-far focus stacks. |
| Disable | Returns the camera to normal single-focus capture. |
| Number of shots | Controls how many frames the bracket sequence captures. |
| Focus increment | Controls how far focus moves between frames. |

Recommended: create a new folder for each subject or stack so bracket sequences stay organized.

**Camera Menu:** Shooting 5 > Focus bracketing.

**Quick Menu:** Menu only.

#### Long Exposure Noise Reduction

LENR takes a dark frame after a long exposure. It can clean hot pixels but doubles wait time and is usually poor for repeated captures, stacking, or fireworks sequences.

| Setting | What it Does |
|---|---|
| Off | Avoids delay between frames and is best for sequences or stacking. |
| Auto | Lets the camera decide when dark-frame cleanup is useful. |
| On | Takes a dark frame after long exposures to reduce hot pixels, but doubles wait time. |

**Camera Menu:** Shooting 4 > Long exp. noise reduction.

**Quick Menu:** Menu only.

## Recommended Settings by Profile

- Birds in Flight: Mechanical; Servo AF, Animals, Eye Detection, Face + Tracking, High Speed Continuous+. If tracking repeatedly selects the wrong target, use Expand AF Area without changing Subject to Detect. Stay Full-frame for erratic flight; consider 1.6× only when a distant bird remains predictably framed.
- Birds Perched: EFCS; Servo AF, Animals, Eye Detection, Face + Tracking, High Speed Continuous. Use Spot AF or 1-Point AF through branches; use Expand AF Area when movement is difficult to follow. Consider 1.6× for a distant, relatively stationary bird when the final image would clearly be cropped.
- Fireworks: EFCS; Manual Focus, Single Shot, tripod stabilization off, long shutter target.
- Landscape: EFCS; One-Shot AF, 1-Point AF, handheld stabilization by default, ISO 100 unless handheld shutter speed needs help.
- Macro: EFCS for ambient light and focus bracketing; One-Shot AF or Manual Focus depending on subject, Spot AF when autofocus is useful. Use Mechanical for a separate, non-bracketed third-party flash setup until verified.
- People: Mechanical; Servo AF, People, Eye Detection, Face + Tracking.
- Sports: Mechanical; Servo AF, People, Eye Detection, Face + Tracking, High Speed Continuous+, fast shutter target. For vehicle-based sports, change Subject Detection situationally from People to Vehicles. Use Expand AF Area if detection is unreliable. Consider 1.6× for distant field action; keep Full-frame when action approaches quickly or framing is uncertain.
- Travel: EFCS baseline unless the subject demands a specialized profile; use Mechanical for fast, wide-open EF 50mm f/1.4 work.
- Waterdrops: Mechanical; Manual Focus, Single Shot, fixed ISO, flash/trigger workflow.
- Wildlife: EFCS; Servo AF, Animals, Eye Detection, Face + Tracking, continuous drive. Use 1-Point AF through grass or brush when deliberate acquisition is more reliable. Consider 1.6× for distant, predictably moving animals; keep Full-frame when movement or composition may change quickly.

## Canon-Specific Notes

Canon R5 Eye Detection is tied to subject-aware AF behavior. It is most meaningful with Face + Tracking and a suitable subject type. Manual Focus bypasses AF selection behavior, so AF Method, Subject Detection, and Eye Detection are hidden from cards when AF Operation is Manual Focus.

For Canon's official setting names and the icons used throughout this reference system, open the [Canon EOS R5 Official Icon Reference](appendix:canon_r5_official_icon_reference). It remains available as a supporting field reference without occupying a separate entry on the main Field Guides index.

## Tips

- Change one behavior at a time when troubleshooting focus.
- Restore Full-frame after a temporary 1.6× crop session.
- If the camera jumps to the wrong subject, use Spot AF, 1-Point AF, or Expand AF Area for deliberate acquisition. Subject to Detect: None removes category priority but does not disable automatic main-subject detection.
- For handheld landscape, raise ISO before accepting camera shake.
- For tripod work, remember to review stabilization and Long Exposure Noise Reduction.

## Common Mistakes

- Leaving action drive mode on for deliberate static work.
- Leaving 1.6× crop enabled and losing resolution or framing room on the next subject.
- Expecting 1.6× crop to add optical reach or capture more subject detail than a later crop from the same full-frame exposure.
- Expecting Eye Detection to work when AF Method or Manual Focus prevents it.
- Using Electronic shutter under lights without checking for banding.
- Leaving stabilization on for solid tripod long exposures.
- Using LENR during sequences where the delay causes missed shots.

## Cross References

- Profiles: Birds in Flight, Birds Perched, Camera Defaults, Fireworks, Landscape, Macro, People, Sports, Travel, Waterdrops, Wildlife.
- Settings: AF Operation, Subject Detection, Eye Detection, AF Method, Focus Mode, Drive Mode, Metering Mode, Shutter Speed, Cropping/aspect ratio, Image Stabilization Mode, IBIS, Lens IS, Shutter Type, Focus Bracketing, Long Exposure Noise Reduction.
- Related guides: AF Cases & Tracking Behavior; Custom Controls, Back-Button AF & Dial Strategies; Flash Photography; Focus Bracketing & In-Camera Depth Compositing; Lens Capabilities; Long Exposure & Night Photography.

## Included Appendix

### Purpose

Explain the card settings whose choices are easy to misread in the field.

### What it Does

This quick reference turns compact card labels into short practical meaning. It focuses on Canon R5 behavior that affects focusing, capture area, stabilization, drive behavior, shutter behavior, and long exposure workflow.

### How it Works

The cards show merged baseline and profile settings. Some settings are always shown because they define the profile; others appear only when a profile changes them from the baseline. Card display may combine related settings, such as IBIS and Lens IS, to save space.

### Advantages

- Helps explain why a card chooses one focusing or stabilization behavior.
- Keeps quick-reference cards compact without hiding the meaning of important choices.
- Clarifies when the camera ignores a setting, such as AF Method during Manual Focus.

### Disadvantages

- It is a quick reference, not a full camera manual.
- Some subjects still require judgment when conditions change.
- Menu names can vary slightly by firmware or shooting context.

### When Not to Use

Do not use this quick reference to decide basic exposure values. For aperture, ISO, and Auto ISO Max, use the card value and normal photographic judgment.
