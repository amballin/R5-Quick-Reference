# USB Camera Configuration

Use this workflow only with the authoritative Canon EOS R5 project and a physical EOS R5 connected by USB. The current Phase 0 probe is read-only. It opens a camera session, reads available identity and health information, optionally watches for a disconnect, and closes the session. It has no camera-setting write API.

## Develop in Camera Lab

Camera Lab is the fast standalone interface used before USB controls are integrated into the Profile Editor. It serves direct local files and does not rebuild cards, appendices, spreadsheets, the PWA, or `docs`.

For normal physical-camera work, double-click **Start Camera Lab.command** in the repository's top-level folder. A Terminal window opens, Camera Lab starts with the physical-camera connection, and Google Chrome opens the interface automatically.

Keep that Terminal window open while using Camera Lab. Press **Control-C** there to stop Camera Lab cleanly. If startup fails, the window remains open so the error can be read. If port 8770 is already occupied, stop the existing Camera Lab before trying again.

The equivalent Terminal command remains available for development and diagnostics:

```bash
./80\ Build/scripts/start-camera-lab.sh
```

Both launch methods use the cached machine-local Canon EDSDK helper and wait for Camera Lab to respond before opening `http://127.0.0.1:8770/` in Google Chrome.

To open the simulator instead:

```bash
./80\ Build/scripts/start-camera-lab.sh --simulated
```

The underlying simulated-server command remains available for diagnostics:

```bash
python3 -B "80 Build/camera_control/dev_server.py"
```

Open the displayed `http://127.0.0.1:8770/` address. HTML, CSS, and JavaScript changes need only a browser refresh. Python changes need only a Camera Lab restart.

### Fast validation loop

While work remains isolated to Camera Lab, its camera-control tests, the capability catalog, and these USB documents, validate with:

```bash
python3 -m unittest \
  "80 Build/test_camera_control_connect.py" \
  "80 Build/test_camera_control_lab.py" && \
python3 "80 Build/validator.py" --source-only
```

Also exercise the affected simulated state in Camera Lab and use the physical EOS R5 when the change depends on real SDK behavior. Do not run the card/PWA build merely to test an isolated Camera Lab iteration.

Run the complete source-validation, development-build, and full-validation sequence when USB work enters the shared Profile Editor, touches baseline/profile/shared-build or published inputs, reaches an explicit integration checkpoint, or is about to be committed, pushed, handed to another computer, finished for the day, or published.

The simulation provides ready, no-camera, multiple-camera, wrong-model, missing-property, busy, and disconnect conditions. It never loads Canon EDSDK.

On the first physical-camera run, point Camera Lab at the Canon-provided framework:

```bash
python3 -B "80 Build/camera_control/dev_server.py" \
  --backend edsdk \
  --sdk-path "/path/to/EDSDK.framework"
```

Camera Lab binds only to local loopback, rejects non-local Host headers, requires a per-process request token for actions, and disables camera-setting writes. Stop it with Control-C.

On macOS, that first run builds and ad-hoc signs a minimal machine-local `EDSDKHelper.app`, embeds a local framework copy, and stores the verified app under the sibling `Local/SDK` workspace outside Git. Later runs may point `--sdk-path` directly at that cached app:

```bash
python3 -B "80 Build/camera_control/dev_server.py" \
  --backend edsdk \
  --sdk-path "/path/to/project Local/SDK/EDSDKHelper.app"
```

Only the helper has the narrowly scoped library-validation entitlement. Python, Camera Lab, and macOS security settings are not modified.

## Scan core capabilities

After Camera Lab shows **EOS R5 connected**, select **Scan capabilities**. The read-only scan checks the reviewed properties defined in `00 Master/camera_capabilities.yaml` and reports current raw values, data types, Canon descriptor access, descriptor forms, and allowed raw values. When a Subject/Profile Card is already selected, the scan automatically refreshes that profile comparison too. The current 22-property set includes the original core 15 plus aspect ratio, continuous AF, eye detection, AF method, IBIS high-resolution shot, subject-detection discovery, and image-metadata noise-reduction discovery.

Camera Lab acquires Canon property-change events during its regular connection checks and again immediately before every scan. This ensures a setting changed directly on the camera is reread instead of leaving the prior comparison value displayed.

If the camera slept or its session stopped responding, Camera Lab closes the stale session, reconnects once, reconfirms the EOS R5 identity, and retries the scan automatically. If that recovery fails, follow the popup instructions to wake or power-cycle the camera, close EOS Utility, reconnect USB, and retry. Restart Camera Lab if the guided retry still fails.

Some Canon properties require a documented activation request before the camera session opens. Camera Lab performs that request only to expose the property for reading; it does not change the camera-menu setting, and activation does not count as write verification.

The verified EOS R5 firmware 2.2.1 scan reads 20 of the 22 reviewed properties. Subject detection remains manual or SDK-unmapped because the original EOS R5 did not return a readable value in the tested context. The noise-reduction discovery row is expected to be unreadable from the camera because Canon defines that identifier on image metadata.

Interpret the results conservatively:

- **Readable** means the current value was returned by the connected camera in this session.
- **Descriptor available** means Canon returned metadata or allowed raw values for the current camera context.
- **Unverified** in the write column means Camera Lab did not attempt a write. A read/write descriptor alone is not proof that the project can set the property safely.
- **Unavailable** may be mode-, lens-, card-, or equipment-dependent. Record the context before classifying it as unsupported.

Camera Lab shows Canon’s human-readable label and the original raw SDK value together. Labels come from the installed Canon SDK headers and supplied sample tables. `Raw N` means the project has preserved the evidence but has not yet approved a human-readable interpretation.

The coverage section separates baseline settings into:

- **SDK-readable profile settings** with a direct reviewed property mapping;
- **Conditional comparison** where a value depends on mode, lens, a target range, or situational profile guidance; and
- **Manual or SDK-unmapped** settings that require later property discovery or a manual checklist.

The silver camera logo displayed by Camera Lab is served directly from the canonical `60 Assets/Card Logos/png/Silver Logo.png` asset; it is not a duplicate Camera Lab image.

The tracked catalog must not contain a camera body identifier. Physical observations must record EOS R5 firmware, EDSDK version, date, camera mode and relevant equipment context before they are accepted as capability evidence.

## Compare a Subject/Profile Card

After connecting, select one Subject/Profile Card and choose **Scan & compare**. This control always performs a fresh capability scan before comparing, so a camera-side change is reread without scrolling back to the connection controls. Permanent reference cards such as Camera Buttons and My Menu are not offered because they are not complete camera-state targets.

The profile choice names the intended registered-mode foundation. For example, **C1 – Wildlife** means set the camera to C1 and compare it with the Wildlife card. A derived choice such as **C1 – Wildlife → People** means begin from the C1 Wildlife registration, then compare against the People target.

The first findings section follows the exact visible setting-row order used by the selected card. Combined card rows retain their grouped presentation and show their underlying setting findings. **Additional settings** then lists every remaining resolved baseline/profile setting in canonical card-layout order.

Each finding is shown in four columns: **Card Expected**, **Camera**, **Status**, and **Optimal Access Path**. Card Expected shows both the setting and its expected value, using the same My Menu-derived value color as the card editor. Access methods are listed in fastest practical order: assigned physical button, dial, switch, or direct control; Q screen; the selected card's My Menu route; then the fastest standard menu path. My Menu is not placed first when a faster direct control exists.

Every camera setting includes a reviewed way to reach it. Focus Bracketing uses **My Menu: SWITCH** before its Shooting 5 menu route. Image Quality, White Balance, and Picture Style identify the **Q screen** as their quickest route. Rows that contain authored notes, strategy, or verification status are explicitly identified as reference guidance rather than camera settings.

Status is **Match**, **Different**, **Equivalent**, **Unreadable**, **Conditional**, **Manual**, or **Not applicable**. The comparison reads the existing capability scan and never changes a camera setting. Manual checklist actions and guided correction remain later Phase 1 work.

Use **Order** to switch among Setup route, the card's original row order, and status order. Status order places Different, Unreadable, Conditional, Manual, Equivalent, Match, and Not applicable findings in that sequence. Manual findings are then grouped by buttons and direct controls, My Menu tabs in the saved tab order (for example SWITCH and AF Case), standard menu, and items without a reviewed route. The floating up arrow returns to the top of Camera Lab after scrolling.

**Setup route** is the default when configuring the camera. It combines card rows and additional settings into one working sequence: physical controls, Q screen, each saved My Menu tab in item order, then each Canon menu family and page. Actionable findings appear first, with status priority inside each route group, so each tab or page needs to be visited only once. Equivalent, matching, and not-applicable findings follow under clearly labeled no-change groups. Switch back to **Card order** when you need the card's presentation or **Status** when you need a discrepancy review.

## Before connecting

1. Use a known-good data-capable USB cable.
2. Turn the camera on and place it in still-photo mode.
3. Close EOS Utility and every other application that may own the camera session.
4. Ensure the battery is adequately charged or use supported external power.
5. Keep the camera awake while testing.

## Locate Canon EDSDK

The repository does not contain or redistribute Canon SDK files. Point the probe at the EDSDK framework binary or framework directory supplied by Canon:

```bash
export CANON_EDSDK_FRAMEWORK="/path/to/EDSDK.framework"
```

You may instead pass the location for one run with `--sdk-path`. Do not place a personal absolute path in repository source or documentation.

## Connect and inspect

From the repository root:

```bash
python3 "80 Build/camera_control/connect_probe.py"
```

For structured diagnostic output:

```bash
python3 "80 Build/camera_control/connect_probe.py" --json
```

When more than one Canon camera is connected, the command stops and prints the available indexes. Rerun with the intended index:

```bash
python3 "80 Build/camera_control/connect_probe.py" --camera-index 0
```

To keep the session open briefly and detect an unplug or camera shutdown:

```bash
python3 "80 Build/camera_control/connect_probe.py" --watch-seconds 15
```

The probe accepts the EOS R5 names returned by the SDK (`EOS R5` and `Canon EOS R5`) after whitespace normalization. It rejects another Canon model rather than assuming compatibility.

## Expected result

A successful run reports:

- EOS R5 product identity;
- body or serial identifier when the camera exposes it;
- firmware version when available;
- raw battery value when available;
- EDSDK binary path and framework version when available; and
- confirmation that the camera session closed cleanly.

Unavailable optional properties are displayed as unavailable. They do not become inferred values.

## Troubleshooting

- **SDK not found:** set `CANON_EDSDK_FRAMEWORK` or use `--sdk-path` with the Canon-provided framework.
- **No camera found:** check cable capability, camera power, sleep state, and USB connection.
- **Camera session could not open:** close EOS Utility and other tethering applications, then reconnect the camera.
- **More than one camera:** rerun with the reported `--camera-index`.
- **Wrong model:** stop. This project must not configure a different camera.
- **Disconnected while watching:** restore the physical connection and rerun from the beginning; do not infer that the previous session remains valid.
- **Scan fails after camera sleep or timeout:** Camera Lab retries one clean reconnection automatically. If the recovery popup appears, follow its steps and choose **Reconnect and scan**.

Phase 1 readback comparison and later guarded writes remain unavailable until their capability mapping and physical-camera tests are complete.
