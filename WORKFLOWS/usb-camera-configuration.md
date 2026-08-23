# USB Camera Configuration

Use this workflow only with the authoritative Canon EOS R5 project and a physical EOS R5 connected by USB. Camera Lab's implemented Phase 0 connection/capability scan and Phase 1 profile checklist are strictly read-only. They open one camera session, verify the EOS R5 identity, inspect reviewed settings, compare a selected profile, guide manual review, and close the session without exposing a camera-setting write API.

## Develop in Camera Lab

Camera Lab is the fast standalone interface used before USB controls are integrated into the Profile Editor. It serves direct local files and does not rebuild cards, appendices, spreadsheets, the PWA, or `docs`.

For normal physical-camera work, double-click **R5 Camera Lab.app** in the machine-local `Applications` folder. Camera Lab starts with the physical-camera connection without opening Terminal, and Google Chrome opens the interface automatically.

Build or refresh both local application wrappers from the repository root with:

```bash
./80\ Build/scripts/build-app-wrappers.sh
```

The wrappers are written to `Canon Camera Reference UI Prototype Local/Applications/` and retain a deliberate link to this authoritative project folder. Rebuild them after moving or renaming the project, or on another Mac. The existing **Start Camera Lab.command** launcher remains available in the repository's top-level folder.

Use **Stop Camera Lab** in the page header to close the EOS R5 session, stop the local server, and end the background app process. The page closes its tab when browser policy permits; if the tab remains open, close it after the stopped confirmation appears. Closing or refreshing the browser tab alone is not a dependable server-shutdown signal. If startup fails or the server stops unexpectedly, the app shows a macOS alert and records details in the machine-local `Logs/R5 Camera Lab.log` file. If port 8770 is already occupied, stop the existing Camera Lab before trying again.

The direct Terminal command remains available for development, diagnostics, and Control-C recovery:

```bash
./80\ Build/scripts/start-camera-lab.sh
```

Both launch methods use the cached machine-local Canon EDSDK helper and wait for Camera Lab to respond before opening `http://127.0.0.1:8770/` in Google Chrome.

Profile Editor can also start or reuse Camera Lab through **Open in Camera Lab**. It passes only the current saved Subject/Profile Card name. Camera Lab validates that name against its freshly loaded catalog and preselects the profile; it does not connect, scan, compare, or write automatically. The two apps remain independent, so each Stop button closes only its own server and Camera Lab alone owns the camera session.

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

Camera Lab binds only to local loopback, rejects non-local Host headers, requires a per-process request token for actions, and disables camera-setting writes. Use the authenticated **Stop Camera Lab** action for normal shutdown or Control-C as the fallback.

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

## Set up and validate C1–C3

Use **C1–C3 Setup & Validation** before the profile-comparison section when the camera's custom modes have not yet been configured. The three cards are generated from the current saved profile foundations each time Camera Lab loads them; they are not fixed to particular subjects. If Profile Editor saves C1 as Macro, reload Camera Lab and the first card and profile selector will identify **C1 – Macro** automatically.

Camera Lab guides this work but remains read-only. **Open Cx checklist** selects the assigned profile and moves to comparison; it does not change a camera setting or register a custom mode.

1. Disconnect USB, save an independent pre-configuration camera-settings backup through the camera's card menu, then reconnect Camera Lab.
2. Start from a normal still-photo shooting mode such as Fv, P, Tv, Av, or M, never from a recalled C1, C2, or C3 state.
3. Keep Custom shooting mode Auto update disabled. Configure the shared controls, My Menu entries, and baseline values before the slot-specific target.
4. For the displayed Cx assignment, choose **Open Cx checklist**, connect and scan if needed, and resolve or confirm the assigned profile's findings.
5. Register the completed state manually on the camera through **Set-up 5 → Custom shooting mode (C1-C3) → Register settings → Cx**. Camera Lab does not press this command or write the camera.
6. Leave the setup state, recall that Cx slot, and choose **Scan & compare** again. Resolve readable differences with another rescan; use manual confirmation only where the checklist identifies manual, conditional, or unreadable evidence.
7. After each later slot, recall and recheck the slots already completed so a shared change has not altered their intended state.
8. When all three recalled states pass review, confirm Auto update is still disabled, disconnect USB, and save a separate final camera-settings backup through the camera's card menu. Preserve the original pre-configuration backup.

## Camera-settings backups remain card-based

Use **Set-up 5 → Save/load cam settings on card → Save to card** on the EOS R5 for both the independent pre-configuration and post-configuration backups. Stop Camera Lab or disconnect the camera's USB cable before using this camera menu, then reconnect after the CSD file is saved.

The installed SDK declares `EdsGetCsdFileData`, but a physical read-only test on the original EOS R5 with firmware 2.2.1 and EDSDK 13.20.20.0 returned Canon error `0x00000060` (`INVALID_PARAMETER`). No file was produced and no camera setting changed. Canon documents PC camera-settings save/load support for selected newer bodies, not the original EOS R5, so Camera Lab does not show a computer-backup button.

`EdsSetCsdFileData` was not called and remains unavailable. Loading a CSD file would overwrite camera configuration and must not be inferred safe from the presence of the SDK symbol.

## Compare a Subject/Profile Card

After connecting, select one Subject/Profile Card and choose **Scan & compare**. This control always performs a fresh capability scan before comparing, so a camera-side change is reread without scrolling back to the connection controls. Permanent reference cards such as Camera Buttons and My Menu are not offered because they are not complete camera-state targets.

The selector lists the current saved registered bases first in C1–C3 slot order. Every remaining profile follows alphabetically with its starting foundation after a left arrow, for example **Sports ← C2 (Birds in Flight)**. A profile without a registered-mode foundation is labeled **Profile ← No Cx**. Comparison headings remain base-first: **C1 – Wildlife → People** means begin from the currently saved C1 Wildlife registration, then compare against the People target. The names are read from saved profile data rather than hardcoded, so a saved foundation change appears after Camera Lab reloads.

The detailed **Camera capabilities** inventory appears after the comparison and checklist because it is supporting reference material. Camera Lab still performs that read-only scan first internally; moving the displayed results does not change the data source, freshness, or safety behavior.

The first findings section follows the exact visible setting-row order used by the selected card. Combined card rows retain their grouped presentation and show their underlying setting findings. **Additional settings** then lists every remaining resolved baseline/profile setting in canonical card-layout order.

Each finding is shown in five columns: **Card Expected**, **Camera**, **Status**, **Optimal Access Path**, and **Checklist**. Card Expected shows both the setting and its expected value, using the same My Menu-derived value color as the card editor. Access methods are listed in fastest practical order: assigned physical button, dial, switch, or direct control; Q screen; the selected card's My Menu route; then the fastest standard menu path. My Menu is not placed first when a faster direct control exists. Checklist shows whether the finding is camera-verified, requires a change and rescan, needs manual confirmation, is blocked, or needs no action.

Every camera setting includes a reviewed way to reach it. Focus Bracketing uses **My Menu: SWITCH** before its Shooting 5 menu route. Image Quality, White Balance, and Picture Style identify the **Q screen** as their quickest route. Rows that contain authored notes, strategy, or verification status are explicitly identified as reference guidance rather than camera settings.

Status is **Match**, **Different**, **Equivalent**, **Unreadable**, **Conditional**, **Manual**, or **Not applicable**. The comparison reads the existing capability scan and never changes a camera setting.

Exposure Compensation, Aperture, and Shutter targets receive contextual comparison when the meaning is unambiguous. Exact values can match, simple ranges accept a camera value inside the range as equivalent, and an interpretable value outside the range is different. Instructions that depend on subject, lighting, grouping, bracketing, lens, or another field choice remain Conditional and explain which context Camera Lab cannot choose. For example, `1/2000–1/4000` can be evaluated directly, while separate outdoor and indoor targets remain Conditional.

Use **Order** to switch among Setup route, the card's original row order, and status order. Status order places Different, Unreadable, Conditional, Manual, Equivalent, Match, and Not applicable findings in that sequence. Manual findings are then grouped by buttons and direct controls, My Menu tabs in the saved tab order (for example SWITCH and AF Case), standard menu, and items without a reviewed route. The floating up arrow returns to the top of Camera Lab after scrolling.

**Setup route** is the default when configuring the camera. It combines card rows and additional settings into one working sequence: physical controls, Q screen, each saved My Menu tab in item order, then each Canon menu family and page. Actionable findings appear first, with status priority inside each route group, so each tab or page needs to be visited only once. Equivalent, matching, and not-applicable findings follow under clearly labeled no-change groups. Switch back to **Card order** when you need the card's presentation or **Status** when you need a discrepancy review.

### Complete the read-only checklist

The existing Setup route is also the checklist order. **Different** means change the readable setting and then choose **Rescan camera**; only a subsequent camera read can complete that item. **Manual**, **Conditional**, and **Unreadable** findings provide **Reviewed/set manually** because their completion depends on camera context, a physical control, or a value the SDK cannot verify. That checkbox records `manual_user_confirmed`; it never becomes camera verification.

Camera Lab retains manual confirmations in this browser for the selected profile and connected-camera context. The expected target is part of each saved checklist identity, so a changed profile target does not inherit an older confirmation. Use **Clear manual confirmations** to begin a new manual review deliberately.

The checklist summary reports **Camera verified**, **Manually confirmed**, **Unresolved**, and **Blocked** counts. Review is complete only when no unresolved or blocked findings remain. The last full-scan time is displayed beside the summary. This browser-local record is working-session evidence, not a change to project YAML, the verification tracker, or the physical camera.

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

The Phase 1 read-only comparison, manual checklist, and guided C1–C3 setup and recalled-state validation are implemented. Richer contextual equivalence and broader physical validation remain. Guarded camera-setting writes, automated C1–C3 registration, and automated camera-settings-data transfer remain unavailable; EOS R5 backups remain card-based.
