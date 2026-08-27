# USB Camera Configuration

Use this workflow only with the authoritative Canon EOS R5 project. Camera Lab's ordinary physical Canon EDSDK connection, capability scan, and profile comparison remain strictly read-only. The simulator can rehearse applying a profile. Physical camera changes are available only after the operator deliberately chooses **Enable camera changes** and only for values that passed the required reversible safety test.

## Develop in Camera Lab

Camera Lab is the fast standalone interface used before USB controls are integrated into the Profile Editor. It serves direct local files and does not rebuild cards, appendices, spreadsheets, the PWA, or `docs`.

For normal physical-camera work, double-click **R5 Camera Lab.app** in the machine-local `Applications` folder. Camera Lab starts with the physical-camera connection without opening Terminal, and Google Chrome opens the interface automatically. If that Lab is already running, opening the app again verifies the existing Lab and recovers its Chrome window instead of reporting a duplicate-server error.

Build or refresh both local application wrappers from the repository root with:

```bash
./80\ Build/scripts/build-app-wrappers.sh
```

The wrappers are written to `Canon Camera Reference UI Prototype Local/Applications/` and retain a deliberate link to this authoritative project folder. Rebuild them after moving or renaming the project, or on another Mac. The existing **Start Camera Lab.command** launcher remains available in the repository's top-level folder.

The first Camera Lab header row shows the active **Canon EDSDK/Simulated camera** backend, **Use Simulator/Use Camera**, **Enable camera changes/Return to read-only** in EDSDK mode, and **Stop Camera Lab**. The second row shows **No setting writes** in ordinary EDSDK mode, **Camera changes enabled** in Phase 2B mode, or **Simulator changes only** in simulated mode, followed by the full **Main project** or **Prototype · branch-name** checkout badge. A dedicated third row right-aligns `Camera Lab Major.Minor.Incremental · Main/Prototype` with the buttons above; expand it to see the diagnostic source hash. The silver camera logo remains in its own adjacent column. Confirm both the checkout badge and change-state badge before physical-camera work.

Use **Stop Camera Lab** in the page header to close the EOS R5 session, stop the local server, and end the background app process. The page closes its tab when browser policy permits; if the tab remains open, close it after the stopped confirmation appears. Closing or refreshing the browser tab alone is not a dependable server-shutdown signal. If startup fails or the server stops unexpectedly, the app shows a macOS alert and records details in the machine-local `Logs/R5 Camera Lab.log` file. A verified running Camera Lab on port 8770 is reused; an unrecognized process on that port is rejected and left untouched.

The direct Terminal command remains available for development, diagnostics, and Control-C recovery:

```bash
./80\ Build/scripts/start-camera-lab.sh
```

Both launch methods use the cached machine-local Canon EDSDK helper and wait for Camera Lab to respond before opening `http://127.0.0.1:8770/` in Google Chrome.

To work without the physical camera, choose **Use Simulator** in the Camera Lab header. Review the confirmation carefully: continuing closes any active EOS R5 session, clears the current scan/comparison state, and restarts the same Lab in simulated mode. The switch itself writes nothing. The header changes to **Simulated camera**, and the development scenario controls become available. Choose **Use Camera** and confirm to close the simulation and restart through the machine-local Canon EDSDK helper. The switch replaces the existing server; it never launches a second Lab on port 8770. A machine-local guarded-run journal remains available for deliberate review, resume, or abort after a restart.

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
  "80 Build/test_camera_control_guarded_run.py" \
  "80 Build/test_camera_control_lab.py" && \
python3 "80 Build/validator.py" --source-only
```

Also exercise the affected simulated state in Camera Lab and use the physical EOS R5 when the change depends on real SDK behavior. Do not run the card/PWA build merely to test an isolated Camera Lab iteration.

Run the complete source-validation, development-build, and full-validation sequence when USB work enters the shared Profile Editor, touches baseline/profile/shared-build or published inputs, reaches an explicit integration checkpoint, or is about to be committed, pushed, handed to another computer, finished for the day, or published.

The simulation provides ready, no-camera, multiple-camera, wrong-model, missing-property, busy, and disconnect connection conditions. Phase 2A additionally provides successful write/readback, readback mismatch, unsupported value, missing prerequisite, guarded camera busy, guarded disconnect, and changed-identity scenarios. Simulated mode never loads Canon EDSDK.

On the first physical-camera run, point Camera Lab at the Canon-provided framework:

```bash
python3 -B "80 Build/camera_control/dev_server.py" \
  --backend edsdk \
  --sdk-path "/path/to/EDSDK.framework"
```

Camera Lab binds only to local loopback, rejects non-local Host headers, and requires a per-process request token for actions. Ordinary Canon EDSDK mode exposes no qualification or guarded-run write route. Use the authenticated **Stop Camera Lab** action for normal shutdown or Control-C as the fallback.

On macOS, that first run builds and ad-hoc signs a minimal machine-local `EDSDKHelper.app`, embeds a local framework copy, and stores the verified app under the sibling `Local/SDK` workspace outside Git. Later runs may point `--sdk-path` directly at that cached app:

```bash
python3 -B "80 Build/camera_control/dev_server.py" \
  --backend edsdk \
  --sdk-path "/path/to/project Local/SDK/EDSDKHelper.app"
```

Only the helper has the narrowly scoped library-validation entitlement. Python, Camera Lab, and macOS security settings are not modified.

## Qualify and use a physical setting write

Do not use this section for ordinary read-only comparison. A live qualification changes the EOS R5 temporarily and requires explicit confirmation with `C123_CFG.CSD` or another confirmed recoverable card backup.

Close EOS Utility and every other camera-control application, connect only the intended EOS R5, and open the ordinary Camera Lab app. Choose **Enable camera changes**, review the warning, and confirm the safe restart. This closes the current session; enabling changes does not itself change a camera setting. After the page returns, the header must say **Camera changes enabled**. Reconnect, scan capabilities, compare the intended Subject/Profile Card, and select **Apply this profile to camera**.

The application flow is intentionally plain:

1. **Check that the camera is ready.** Confirm identity, power, camera-reported lens, flash, cards, competing applications, and recovery backup.
2. **Review every change.** Nothing has changed yet. The summary separates **Already correct**, **Camera Lab will change**, **You will change**, and **Needs attention first**.
3. Resolve every needs-attention item. The message tells you whether to choose missing comparison context, change the value on-camera and rescan, or open collapsed **Advanced setup** to run a reversible safety test.
4. Choose **Start applying profile** only when the review says **Ready to apply**. Already-correct and non-action rows require no clicks. In simulator mode, Camera Lab immediately processes and independently verifies all safe automatic changes, stopping at the first problem.
5. Follow the single stationary **Do this now** card. A single-setting action includes the exact target. Same-route manual settings appear together—for example, the four **My Menu — AF Case** settings—and require one completion action instead of four. Camera Lab then performs one rescan and verifies every exact readable match in that group together.
6. Return to Rapid setup at any time. Completed group items immediately appear as **Camera verified** when the rescan found an exact match, or **Previously manually confirmed in this connected-camera session** when no exact readback exists. Switching cards reuses that manual evidence only for the same exact setting and target under the unchanged camera, mode, lens, flash, and card context. A different target remains unresolved.
7. Finish only when the receipt says **Profile applied successfully** and lists what was verified, manually confirmed, and already correct. If it says **Profile not fully applied**, treat the camera as partial and review the stated stopping point.

The `--enable-physical-writes` command-line flag remains a diagnostic fallback, not the normal operator workflow.

For one candidate:

1. preview the exact original and temporary values;
2. confirm the reversible transaction in the separate physical-write dialog;
3. choose **Write, verify & restore** once;
4. confirm that Camera Lab verified the temporary value and then verified restoration of the original value; and
5. stop if any failure or manual-restoration warning appears.

A success records exact `sdk_written_and_verified` evidence in the machine-local `Camera Lab/Physical Write Evidence.json` file. It is valid only for the recorded EOS R5 body identifier, firmware, EDSDK version, property, and raw values. It is not committed to Git and cannot authorize another body, firmware, SDK, property, or value.

Review the profile again after an Advanced setup safety test. A review containing **Needs attention first** cannot start. For a ready review, confirm it separately and process only the displayed step. Each automatic step rereads the current value, leaves an existing match unchanged, otherwise changes it once, immediately verifies the readback, and stops on any mismatch, busy state, disconnect, identity change, or unexpected prerequisite.

When the receipt says **Profile applied successfully**, choose **Return to read-only**, confirm the restart, and reconnect only if more read-only work is needed. **Switching tracked subjects** is shown as **Initial priority (0)**, **On subject (1)**, or **Switch subject (2)** and remains a manual step because Canon's installed EDSDK does not expose a documented property ID for it.

Physical execution does not register C1–C3 and does not transfer `.CSD` files. Those actions remain manual. Use **Return to read-only** before ending the guarded-write session.

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

Use **C1–C3 Setup & Validation** before the profile-comparison section when the camera's custom modes have not yet been configured. This first-in-process section is collapsed by default because it is not part of most Camera Lab sessions; expand it when registering or revalidating C1–C3. The three cards are generated from the current saved profile foundations each time Camera Lab loads them; they are not fixed to particular subjects. If Profile Editor saves C1 as Macro, reload Camera Lab and the first card and profile selector will identify **C1 – Macro** automatically.

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

The detailed **Camera capabilities** inventory appears after the comparison and checklist because it is supporting reference material. It remains collapsed until you choose to expand it after a scan. Camera Lab still performs that read-only scan first internally; collapsing the displayed results does not change the data source, freshness, or safety behavior.

The first findings section follows the exact visible setting-row order used by the selected card. Combined card rows retain their grouped presentation and show their underlying setting findings. **Additional settings** then lists every remaining resolved baseline/profile setting in canonical card-layout order.

Each finding is shown in five columns: **Card Expected**, **Camera**, **Status**, **Optimal Access Path**, and **Checklist**. Card Expected shows both the setting and its expected value, using the same My Menu-derived value color as the card editor. Access methods are listed in fastest practical order: assigned physical button, dial, switch, or direct control; Q screen; the selected card's My Menu route; then the fastest standard menu path. My Menu is not placed first when a faster direct control exists. Checklist shows whether the finding is camera-verified, requires a change and rescan, needs manual confirmation, is blocked, or needs no action.

Every camera setting includes a reviewed way to reach it. Focus Bracketing uses **My Menu: SWITCH** before its Shooting 5 menu route. Image Quality, White Balance, and Picture Style identify the **Q screen** as their quickest route. Rows that contain authored notes, strategy, or verification status are explicitly identified as reference guidance rather than camera settings.

Status is **Match**, **Different**, **Equivalent**, **Unreadable**, **Conditional**, **Manual**, or **Not applicable**. The comparison reads the existing capability scan and never changes a camera setting.

Exposure Compensation, Aperture, and Shutter targets receive contextual comparison when the meaning is unambiguous. Exact values can match, simple ranges accept a camera value inside the range as equivalent, and an interpretable value outside the range is different. When the card authors distinct targets for different situations, Camera Lab asks for the missing context in the finding itself. For example, Sports asks **Outdoor** or **Indoor**, while People asks for the applicable portrait/action or single/group condition. After you choose, Camera Lab evaluates only that authored clause and reports Match, Equivalent, or Different when safe; changing the choice recomputes the comparison without rescanning or changing the camera. Camera Lab never chooses for you. Guidance such as **Adjust for background** or **bracket before f/16** remains Conditional when the card does not supply distinct numeric targets that make comparison safe.

Use **Order** to switch among Setup route, the card's original row order, and status order. Status order places Different, Unreadable, Conditional, Manual, Equivalent, Match, and Not applicable findings in that sequence. Manual findings are then grouped by buttons and direct controls, My Menu tabs in the saved tab order (for example SWITCH and AF Case), standard menu, and items without a reviewed route. After scrolling, the floating up arrow returns directly to **Compare a Subject/Profile Card**.

**Setup route** is the default when configuring the camera. It combines card rows and additional settings into one working sequence: physical controls, Q screen, each saved My Menu tab in item order, then each Canon menu family and page. Actionable findings appear first, with status priority inside each route group, so each tab or page needs to be visited only once. Equivalent, matching, and not-applicable findings follow under clearly labeled no-change groups. Switch back to **Card order** when you need the card's presentation or **Status** when you need a discrepancy review.

### Complete the read-only checklist

The existing Setup route is also the checklist order. **Different** means change the readable setting and then choose **Rescan camera**; only a subsequent camera read can complete that item. A Conditional finding with authored context choices must be answered before it can be evaluated or manually confirmed. Other **Manual**, **Conditional**, and **Unreadable** findings provide **Reviewed/set manually** because their completion depends on camera context, a physical control, or a value the SDK cannot verify. That checkbox records `manual_user_confirmed`; it never becomes camera verification.

Camera Lab retains manual confirmations in this browser for the selected profile and connected-camera context. The expected target is part of each saved checklist identity, so a changed profile target does not inherit an older confirmation. Use **Clear manual confirmations** to begin a new manual review deliberately.

The checklist summary reports **Camera verified**, **Manually confirmed**, **Unresolved**, and **Blocked** counts. Review is complete only when no unresolved or blocked findings remain. The last full-scan time is displayed beside the summary. This browser-local record is working-session evidence, not a change to project YAML, the verification tracker, or the physical camera.

## Rehearse applying a profile in the simulator

After **Scan & compare** completes in simulated mode, choose **Apply this profile to camera**. Complete the same readiness and review flow. The page clearly identifies simulator mode and cannot change the physical EOS R5.

Choose **Review what will change**. Camera Lab takes a fresh pre-change readback snapshot and displays the entire proposed attempt before execution. Review all four classifications:

- **Already correct** requires no change.
- **Camera Lab will change** can be simulated and verified automatically.
- **You will change** requires the displayed camera route and your confirmation.
- **Needs attention first** must be resolved before the attempt can start.

Choose **Start simulator test** only after reviewing the complete plan. This is a second, separate confirmation. Camera Lab automatically clears no-action rows and processes all simulator-safe settings, independently reading and verifying each and stopping at the first failure. It then presents one stationary **Do this now** card for each remaining manual route group while retaining separate automatic and operator progress. The complete list is hidden during processing and returns afterward. One group completion performs one rescan; exact readable matches become camera-verified and other group members retain explicit manual-confirmation evidence.

Those manual confirmations feed the Rapid setup checklist immediately and may follow the same exact setting and target to another card during the same uninterrupted connected-camera session. They never cross a different target, disconnect, restart, camera/firmware/lens/mode/flash/card-context change, or explicit clear. Shared confirmation remains labelled manual and is not camera verification.

A mismatch, unsupported value, missing or changed prerequisite, busy state, disconnect, or changed identity stops immediately. The result says **Profile not fully applied**, identifies the stopping point, and never implies completion. **Continue stopped attempt** rechecks the recorded identity before retrying the current step. **Stop applying** preserves the internal record. Machine-local records contain no request token or credential and never enter Git.

Use the Phase 2A scenarios to test every stop boundary. A second plan after a successful run must show zero simulator-automatic writes for settings already matching. C1–C3 registration and camera-settings-file transfer remain manual; the simulator does not add either operation.

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
- **Simulator application stops:** Read the displayed failure and stopping point. Resolve or change the deterministic scenario, reconnect the same simulator identity, then choose **Continue stopped attempt**; otherwise choose **Stop applying** and prepare a fresh review. Never interpret **Profile not fully applied** as complete.
- **Qualification restoration is not verified:** stop SDK execution and use the displayed camera controls to restore the exact recorded original value. Rescan before doing anything else. No write evidence is created.
- **Physical target remains blocked:** qualify that exact raw value on this body/firmware/SDK context, or complete it manually. Descriptor membership alone is insufficient.

The Phase 1 read-only comparison, manual checklist, guided C1–C3 maintenance and recalled-state validation, simulator rehearsal, and evidence-gated physical camera-change workflow are implemented. The ordinary Lab provides **Enable camera changes**, **Apply this profile to camera**, a plain readiness and review flow, one visible action at a time, an explicit completion receipt, and **Return to read-only**. Physical session 4 qualified Picture Style Neutral and Standard for the tested EOS R5 body/firmware/EDSDK context and restored Neutral; every other exact value remains unavailable for automatic change until it passes the safety test. Physical session 3 manually registered and camera-body verified C1 Wildlife, C2 Birds in Flight, and C3 Landscape, with `C123_CFG.CSD` saved as the recovery checkpoint. Automated C1–C3 registration and camera-settings-data transfer remain unavailable; EOS R5 backups remain card-based.
