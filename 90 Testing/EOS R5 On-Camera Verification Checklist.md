# EOS R5 On-Camera Verification Checklist

**Status:** Test plan — not yet performed  
**Publication:** Non-published repository test material  
**Evidence rule:** A target becomes owner-confirmed only after the applicable test passes and the result is recorded.

The structured checklist source is [`eos_r5_verification_tracker.yaml`](eos_r5_verification_tracker.yaml). Generate a blank publishable master with `./80 Build/scripts/build-setup-downloads.sh`; keep test progress in a separately migrated machine-local working copy. The earlier [EOS R5 On-Camera Verification Tracker](EOS%20R5%20On-Camera%20Verification%20Tracker.xlsx) is retained as a migration source, not as the current blank master.

Use this checklist for one deliberate camera-setup session. Complete the steps in order. Do not register C1, C2, or C3 until every setting for that mode has been checked.

## Session Record

- Date:
- Tester:
- EOS R5 firmware:
- Battery model and charge:
- Memory card:
- Lens or lenses:
- Flash and trigger:
- Test-image folder or filename range:
- Notes:

## 1. Prepare and Set Up the Camera

### Protect the starting state

- [ ] Insert a formatted card with enough free space.
- [ ] Photograph or write down any current C1, C2, and C3 contents that may need to be preserved.
- [ ] Use **Set-up 5 > Save/load cam settings on card > Save to card** to save the current complete camera configuration before changing it.
- [ ] Record the saved filename:
- [ ] Confirm the camera is in a normal shooting mode, not C1, C2, or C3, before building the first registration.
- [ ] Set **Custom shooting mode (C1-C3) > Auto update set. > Disable**.

### Confirm shared Camera Setup Essentials

- [ ] Configure the approved **SWITCH** My Menu tab with Subject to detect, Shutter mode, Focus bracketing, IS (Image Stabilizer) mode, and Cropping/aspect ratio in that order; leave position 6 open.

- [ ] Image quality: cRAW.
- [ ] Cropping/aspect ratio: Full-frame.
- [ ] Metering: Evaluative.
- [ ] Auto ISO maximum: 12800.
- [ ] RGB histogram: enabled.
- [ ] Highlight alert: enabled.
- [ ] High ISO Noise Reduction: Off.
- [ ] Long Exposure Noise Reduction: Off.
- [ ] Continuous AF: Off.
- [ ] Electronic full-time MF: Off.
- [ ] IBIS High Resolution Shot: Off.
- [ ] MF Peaking: On, Low, Red.

### Configure the shared physical controls

- [ ] Shutter half-press: Metering start; it does not start AF.
- [ ] AF-ON: Metering and AF start.
  - [ ] AF Operation: Maintain current setting.
  - [ ] AF Method: Face + Tracking.
  - [ ] Servo AF characteristics: Maintain current setting.
- [ ] AE Lock: Metering and AF start.
  - [ ] AF Operation: Maintain current setting.
  - [ ] AF Method: 1-Point AF.
  - [ ] Servo AF characteristics: Maintain current setting.
- [ ] AF Point Selection: AF point selection; Main Dial changes the AF method.
- [ ] Lens AF button: AF Off.
- [ ] DOF button: One-Shot AF ↔ Servo AF.
- [ ] SET: Eye detection.
- [ ] Joystick: Direct AF point selection.
- [ ] Main Dial: Shutter Speed.
- [ ] Rear Wheel: Aperture.
- [ ] Top Rear Dial: ISO Speed.
- [ ] Control Ring: Exposure Compensation.
- [ ] M-Fn: Switch to Custom shooting mode.

Do not continue to C1 registration until the shared setup and control assignments above are correct.

### Save the shared-setup checkpoint

- [ ] Use **Set-up 5 > Save/load cam settings on card > Save to card** after SWITCH, shared settings, and physical controls are complete.
- [ ] Record the checkpoint in the Sessions sheet and set its Checklist status to **Backup-Settings**.

## 2. Configure, Validate, and Register C1 — Wildlife

Remain in a normal shooting mode while configuring these settings.

| Setting | Required C1 value | Checked |
|---|---|---|
| Mode | Fv | [ ] |
| Metering | Evaluative | [ ] |
| Exposure Compensation | 0 | [ ] |
| Shutter Speed | Auto | [ ] |
| Aperture | Auto | [ ] |
| ISO | Auto | [ ] |
| Auto ISO Maximum | 12800 | [ ] |
| AF Operation | Servo AF | [ ] |
| AF Method | Face + Tracking | [ ] |
| Subject Detection | Animals | [ ] |
| Eye Detection | Enable | [ ] |
| Drive Mode | High Speed Continuous | [ ] |
| Shutter Type | EFCS | [ ] |
| Image Stabilizer Mode | Mode 1 | [ ] |
| IBIS | On | [ ] |
| Focus Bracketing | Disable | [ ] |
| Lens IS switch | On; physical check | [ ] |

### Register and read back C1

- [ ] Review the complete C1 table again before registration.
- [ ] Use **Set-up > Custom shooting mode (C1-C3) > Register settings > C1**.
- [ ] Leave the setup state.
- [ ] Recall C1 with M-Fn.
- [ ] Read back every C1 table value from the camera.
- [ ] Confirm temporary changes do not rewrite C1 because Auto update remains disabled.
- [ ] Record discrepancies:
- [ ] C1 result: Pass / Fail / Needs retest.

Do not begin C2 until C1 has been registered and read back successfully.

## 3. Modify the Normal Shooting State, Validate, and Register C2 — Birds in Flight

Return to a normal shooting mode rather than modifying the recalled C1 slot. Configure the complete C2 environment. Compared with C1, the principal changes are Tv mode, 1/2500 sec., High Speed Continuous+, Mechanical shutter, and Image Stabilizer Mode 3.

| Setting | Required C2 value | Checked |
|---|---|---|
| Mode | Tv | [ ] |
| Metering | Evaluative | [ ] |
| Exposure Compensation | 0 starting point | [ ] |
| Shutter Speed | 1/2500 sec. | [ ] |
| Aperture | Auto | [ ] |
| ISO | Auto | [ ] |
| Auto ISO Maximum | 12800 | [ ] |
| AF Operation | Servo AF | [ ] |
| AF Method | Face + Tracking | [ ] |
| Subject Detection | Animals | [ ] |
| Eye Detection | Enable | [ ] |
| Drive Mode | High Speed Continuous+ | [ ] |
| Shutter Type | Mechanical | [ ] |
| Image Stabilizer Mode | Mode 3 | [ ] |
| IBIS | On | [ ] |
| Focus Bracketing | Disable | [ ] |
| Lens IS switch | On; physical check | [ ] |

### Register and read back C2

- [ ] Review the complete C2 table again before registration.
- [ ] Use **Set-up > Custom shooting mode (C1-C3) > Register settings > C2**.
- [ ] Leave the setup state.
- [ ] Recall C2 with M-Fn.
- [ ] Read back every C2 table value from the camera.
- [ ] Recall C1 again and confirm C1 was not altered while C2 was created.
- [ ] Record discrepancies:
- [ ] C2 result: Pass / Fail / Needs retest.

Do not begin C3 until both C1 and C2 recall their complete intended configurations.

## 4. Modify the Normal Shooting State, Validate, and Register C3 — Landscape

Return to a normal shooting mode rather than modifying C1 or C2. Configure the complete C3 environment.

| Setting | Required C3 value | Checked |
|---|---|---|
| Mode | Av | [ ] |
| Metering | Evaluative | [ ] |
| Exposure Compensation | 0 | [ ] |
| Shutter Speed | Auto | [ ] |
| Aperture | f/9 | [ ] |
| ISO | 100 | [ ] |
| Auto ISO Maximum | 12800; inactive while ISO 100 is fixed | [ ] |
| AF Operation | One-Shot AF | [ ] |
| AF Method | 1-Point AF | [ ] |
| Subject Detection | None | [ ] |
| Eye Detection | Disable | [ ] |
| Drive Mode | Single Shot | [ ] |
| Shutter Type | EFCS | [ ] |
| Image Stabilizer Mode | Mode 1 | [ ] |
| IBIS | On | [ ] |
| Focus Bracketing | Disable; enable only when needed | [ ] |
| Lens IS switch | On for the registered handheld starting state | [ ] |

### Register and read back C3

- [ ] Review the complete C3 table again before registration.
- [ ] Use **Set-up > Custom shooting mode (C1-C3) > Register settings > C3**.
- [ ] Leave the setup state.
- [ ] Recall C3 with M-Fn.
- [ ] Read back every C3 table value from the camera.
- [ ] Recall C1, C2, and C3 in sequence and confirm all three remain correct.
- [ ] Confirm Auto update is still disabled.
- [ ] Record discrepancies:
- [ ] C3 result: Pass / Fail / Needs retest.

### Save the registered-modes checkpoint

- [ ] After C1, C2, and C3 have all been registered and read back, save another complete camera configuration to the card.
- [ ] Record the checkpoint in the Sessions sheet and set its Checklist status to **Backup-Settings**.

## 5. Verify the Shared AF Controls

Run these tests in both C1 or C2 Servo AF and C3 One-Shot AF.

### AF-ON

- [ ] AF-ON invokes Face + Tracking.
- [ ] In C1/C2, AF-ON maintains Servo AF.
- [ ] In C3, AF-ON maintains One-Shot AF.
- [ ] AF-ON honors the stored Eye Detection state.
- [ ] Result and observations:

### AE Lock

- [ ] AE Lock invokes 1-Point AF.
- [ ] In C1/C2, AE Lock maintains Servo AF.
- [ ] In C3, AE Lock maintains One-Shot AF.
- [ ] AE Lock uses the last 1-Point position.
- [ ] Result and observations:

### DOF AF-operation switch

- [ ] In C3, press DOF and confirm One-Shot changes to Servo.
- [ ] AF-ON maintains the changed Servo state.
- [ ] AE Lock maintains the changed Servo state.
- [ ] Press DOF again and confirm the camera returns to One-Shot.
- [ ] Repeat from C1 or C2 to confirm Servo changes to One-Shot and back.
- [ ] Result and observations:

### SET and joystick

- [ ] With Face + Tracking active, SET toggles Eye Detection.
- [ ] With 1-Point AF or Spot AF active, SET does not incorrectly imply active Eye Detection.
- [ ] Joystick movement selects or moves the expected AF point or subject.
- [ ] Straight joystick press recenters the AF point in the documented AF-point workflow.
- [ ] With Face + Tracking, record the single-border, double-border, tracking-release, and Face Select: Off behavior actually observed.
- [ ] Result and observations:

## 6. Verify EFCS and Mechanical Shutter Choices

Keep exposure, focus, support, framing, and lighting constant within each comparison. Record filenames for every series.

### Tripod sharpness and shutter shock

- [ ] Use a detailed static target, solid tripod, stabilization Off, remote release or 2-second timer.
- [ ] Compare EFCS and Mechanical at approximately 1/8, 1/15, 1/30, and 1/60 sec.
- [ ] Capture at least five frames per mode and shutter speed.
- [ ] Compare identical detailed areas at useful magnification.
- [ ] Evidence filenames:
- [ ] Result and observations:

### Fast-shutter bokeh with EF 50mm f/1.4

- [ ] Use the EF 50mm f/1.4 near maximum aperture with distinct out-of-focus highlights.
- [ ] Compare EFCS and Mechanical at 1/1000, 1/2000, 1/4000, and 1/8000 sec. as light permits.
- [ ] Keep composition, focus distance, aperture, and exposure equivalent.
- [ ] Inspect highlight shape and lower-edge clipping.
- [ ] Evidence filenames:
- [ ] Result and observations:

### Indoor LED or fluorescent lighting

- [ ] Use representative Sports shutter speeds under the actual artificial lighting.
- [ ] Compare EFCS and Mechanical with Anti-flicker Off and On.
- [ ] Check exposure and color consistency across short bursts.
- [ ] Evidence filenames:
- [ ] Result and observations:

### Burst behavior

- [ ] Compare EFCS and Mechanical in High Speed Continuous.
- [ ] Compare EFCS and Mechanical in High Speed Continuous+.
- [ ] Record battery, lens, shutter speed, aperture, card, and Anti-flicker state.
- [ ] Confirm subject tracking and viewfinder behavior remain usable.
- [ ] Evidence filenames:
- [ ] Result and observations:

### Pluto and Waterdrops flash workflow

- [ ] Select Mechanical shutter.
- [ ] Confirm 1/200 sec., Manual exposure, ISO 100, and the intended f/8–f/11 aperture.
- [ ] Confirm manual flash starts around 1/16–1/64 power.
- [ ] Verify Pluto connection, delay timing, flash synchronization, exposure consistency, and recycle behavior.
- [ ] Do not substitute EFCS for this documented workflow until separately tested and approved.
- [ ] Evidence filenames:
- [ ] Result and observations:

## 7. Final Read-Back and Save

- [ ] Recall C1 and confirm Wildlife.
- [ ] Recall C2 and confirm Birds in Flight.
- [ ] Recall C3 and confirm Landscape.
- [ ] Confirm AF-ON, AE Lock, DOF, SET, joystick, and M-Fn assignments remain correct.
- [ ] Confirm Auto update remains disabled.
- [ ] Save the verified complete camera configuration to the card.
- [ ] Assign and record the final settings filename:
- [ ] Preserve test images and this completed checklist until the reference-system evidence states are updated.

## Verification Summary

| Area | Result | Evidence / notes |
|---|---|---|
| Shared camera setup | Not tested | |
| C1 Wildlife | Not tested | |
| C2 Birds in Flight | Not tested | |
| C3 Landscape | Not tested | |
| AF-ON | Not tested | |
| AE Lock | Not tested | |
| DOF switch | Not tested | |
| SET / Eye Detection | Not tested | |
| Joystick | Not tested | |
| EFCS tripod sharpness | Not tested | |
| EFCS fast-shutter bokeh | Not tested | |
| Artificial lighting | Not tested | |
| Burst behavior | Not tested | |
| Pluto / Waterdrops | Not tested | |

After the session, update only the items that actually passed. Failed, ambiguous, or unperformed items remain approved targets pending physical verification or unresolved.
