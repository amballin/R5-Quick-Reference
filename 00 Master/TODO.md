# Project To-Do

This file records approved follow-up work and analysis candidates that should not be lost. It is repository planning material, not published Field Guide content and not a source of binding architecture. Promote a decision through the normal approval process before implementing any architectural item.

## Control Architecture Follow-Up

- Run the non-published [EOS R5 On-Camera Verification Checklist](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Checklist.md), record progress and evidence in its [Excel tracker](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Tracker.xlsx), and promote only completed, unambiguous results to owner-confirmed status.
- Physically configure and verify AF-ON with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to Face + Tracking.
- Physically configure and verify AE Lock with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to 1-Point AF.
- Verify that C1's present registration matches the Wildlife profile; register and verify C2 as Birds in Flight / Action and C3 as Landscape.
- Verify that the DOF button changes One-Shot AF ↔ Servo AF and that both AF-start buttons respect the resulting state.
- Physically test the joystick straight press with Face + Tracking, including face/eye selection, tracking release, the single- and double-border displays, and the Face Select: Off indication; do not make the behavior definitive until verified.
- Decide whether Spot AF needs another immediate control for serious macro work.

### My Menu Transition Verification and Expansion

Verify the approved starting workflow from the registered C1-C3 profiles to People, Macro, and Waterdrops, then evaluate whether another green-star My Menu item or tab is warranted.

| Target | Best starting mode | Already close | Remaining changes | Strong My Menu candidates |
|---|---|---|---|---|
| People | C1 Wildlife | Fv, Auto ISO, Servo AF, Face + Tracking, Eye Detection, Mode 1 | Animals to People, High to Low Speed Continuous, EFCS to Mechanical, portrait shutter/aperture targets | Subject to detect; Shutter mode |
| Macro | C3 Landscape | Av, One-Shot AF, Single Shot, EFCS, Mode 1, suitable aperture range | ISO 100 to Auto, 1-Point to Spot AF, enable Focus Bracketing, set f/8 | Focus bracketing |
| Waterdrops | C3 Landscape | ISO 100, Single Shot, aperture near f/8-f/11 | Av to Manual, 1/200 sec., Mechanical, Manual Focus, stabilization Off | Shutter mode; IS (Image Stabilizer) mode |

Test these transitions on the camera with **Auto update set.: Disable**. Record whether the mode-specific exposure values and broader settings retain, revert, or carry across, including exposure compensation and any temporary 1.6× crop. Confirm that recalling C1 or C3 supplies the expected starting state and that subsequent changes do not rewrite the registered mode.

Verify the approved starting My Menu tab named **SWITCH**:

1. Subject to detect
2. Shutter mode
3. Focus bracketing
4. IS (Image Stabilizer) mode
5. Cropping/aspect ratio

Leave the sixth position open until the physical transition test identifies another menu-only need. My Menu only shortens navigation to the real setting; it does not apply a complete People, Macro, or Waterdrops configuration. Keep Drive Mode, ISO, shutter speed, aperture, and AF Method on Q, the dials, or the AF-point controls when those remain faster, and keep lens AF/MF and IS switches as physical checks. After verifying SWITCH, evaluate other My Menu tabs separately by field frequency, menu depth, risk of leaving a temporary setting active, and whether Q, a dial, a button, or a physical lens control is already faster.

## Exposure and Shutter Follow-Up

- Physically verify the approved EFCS baseline on the owner’s EOS R5: compare tripod sharpness at approximately 1/8–1/60 sec.; inspect EF 50mm f/1.4 bokeh at 1/1000–1/8000 sec.; test indoor LED lighting at Sports shutter speeds; confirm High and High Speed Continuous+ burst behavior; and verify the Mechanical 1/200-sec. Pluto/manual-flash Waterdrops setup. Keep the documentation classified as an approved target pending physical verification until these checks are complete.

## Architecture and Validation Improvements

- Generate duplicate control tables from one authoritative machine-readable control source.
- Add validation that rejects the deprecated registered-AF workflow terminology.

### Feature Interaction Rules

Create a structured way to capture and surface important Canon feature interactions and conditional menu behavior.

Examples include:

- A setting disappearing or changing when a particular lens is attached.
- Lens switches overriding or replacing camera-menu controls.
- Lens optical IS coordinating with camera IBIS.
- Flash restrictions.
- Electronic-shutter restrictions.
- Drive-mode restrictions.
- Focus-bracketing compatibility.
- HDR-related compatibility.

## Macro Refinement

- Refine the Macro profile and guidance as a separately approved content change.
- Review Spot AF, 1-Point AF, manual focus, magnification, peaking, and the role of AF-ON versus AE Lock at macro distances.
- Review stabilization at macro distances for handheld, tripod, and controlled-support workflows.
- Refine focus-bracketing starting points by magnification, subject depth, aperture, increment, and shot count.
- Expand flash-versus-ambient guidance, working-distance considerations, diffraction tradeoffs, and support recommendations.
- Review whether the Canon EF 100mm f/2.8L Macro IS USM needs more explicit lens-specific operating guidance without duplicating the Lens Capabilities appendix.
- Keep advanced high-magnification, MP-E 65mm, automated rail, StackShot, vibration-control, and stacking workflow work as a later phase.
