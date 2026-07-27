# Project To-Do

This file records approved follow-up work and analysis candidates that should not be lost. It is repository planning material, not published Field Guide content and not a source of binding architecture. Promote a decision through the normal approval process before implementing any architectural item.

## Control Architecture Follow-Up

- Run and record the non-published [EOS R5 On-Camera Verification Checklist](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Checklist.md); promote only completed, unambiguous results to owner-confirmed status.
- Physically configure and verify AF-ON with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to Face + Tracking.
- Physically configure and verify AE Lock with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to 1-Point AF.
- Verify that C1's present registration matches the Wildlife profile; register and verify C2 as Birds in Flight / Action and C3 as Landscape.
- Verify that the DOF button changes One-Shot AF ↔ Servo AF and that both AF-start buttons respect the resulting state.
- Physically test the joystick straight press with Face + Tracking, including face/eye selection, tracking release, the single- and double-border displays, and the Face Select: Off indication; do not make the behavior definitive until verified.
- Decide whether Spot AF needs another immediate control for serious macro work.

## Exposure and Shutter Follow-Up

- Physically verify the approved EFCS baseline on the owner’s EOS R5: compare tripod sharpness at approximately 1/8–1/60 sec.; inspect EF 50mm f/1.4 bokeh at 1/1000–1/8000 sec.; test indoor LED lighting at Sports shutter speeds; confirm High and High Speed Continuous+ burst behavior; and verify the Mechanical 1/200-sec. Pluto/manual-flash Waterdrops setup. Keep the documentation classified as an approved target pending physical verification until these checks are complete.

## Architecture and Validation Improvements

- Generate duplicate control tables from one authoritative machine-readable control source.
- Add validation that rejects the deprecated registered-AF workflow terminology.

## Macro Refinement

- Refine the Macro profile and guidance as a separately approved content change.
- Review Spot AF, 1-Point AF, manual focus, magnification, peaking, and the role of AF-ON versus AE Lock at macro distances.
- Review stabilization at macro distances for handheld, tripod, and controlled-support workflows.
- Refine focus-bracketing starting points by magnification, subject depth, aperture, increment, and shot count.
- Expand flash-versus-ambient guidance, working-distance considerations, diffraction tradeoffs, and support recommendations.
- Review whether the Canon EF 100mm f/2.8L Macro IS USM needs more explicit lens-specific operating guidance without duplicating the Lens Capabilities appendix.
- Keep advanced high-magnification, MP-E 65mm, automated rail, StackShot, vibration-control, and stacking workflow work as a later phase.
