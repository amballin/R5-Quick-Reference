# USB Camera Configuration Specification

## Scope

This specification governs machine-local USB connection, configuration, readback, comparison, manual-completion guidance, C1–C3 orchestration, and camera-settings backup for the Canon EOS R5. Governance and precedence are defined in [`PROJECT_RULES.md`](../../PROJECT_RULES.md).

The canonical camera targets remain `00 Master/baseline.yaml`, profile overrides under `10 Profiles/`, synchronized C1–C3 mappings, My Menu sources, controls sources, and the verification tracker. USB integration consumes those sources; it does not create an alternate profile format or treat observed camera state as authored project source.

## System Boundary

- Use Canon EDSDK for USB communication with a physically connected camera.
- Keep EDSDK libraries, headers, samples, licenses, credentials, and machine-specific installation paths outside Git.
- Keep native camera access machine-local. The published website and offline PWA remain reference-only and must not load or expose the native SDK bridge.
- On macOS, isolate EDSDK in a minimal native helper process when the project Python runtime cannot load Canon's framework under library-validation policy. The helper may expose only the read-only Phase 0 operations defined here and communicate through a private parent-process pipe. Build it as a machine-local app bundle from tracked source plus the external Canon headers and framework, embed a machine-local copy of the framework, and cache the verified bundle outside Git. When required by macOS, the ad-hoc-signed helper alone may carry `com.apple.security.cs.disable-library-validation`; its compiled rpath must resolve only the framework embedded in its app bundle. Do not add the entitlement to Python, the browser-facing server, or another project executable, disable global security controls, or modify the system Python installation.
- Load the SDK only when a USB operation is explicitly requested. Ordinary validation, builds, profile editing, and publication must not require a camera or EDSDK installation.
- Bind any future browser-to-native bridge to loopback only and protect mutating requests with the same explicit review and session safeguards used by other guarded local actions.

## Evidence Classes

Every observed setting result must identify its evidence method:

- `sdk_verified`: the value was read successfully from the connected camera in the recorded context;
- `sdk_written_and_verified`: the value was written and then read back successfully;
- `manual_user_confirmed`: the user confirmed a camera-only or physical control;
- `unreadable`: the SDK did not expose a usable value;
- `not_applicable`: the value does not apply in the recorded mode, lens, flash, card, or other equipment context;
- `unresolved`: the result cannot yet be classified safely.

An approved target, successful SDK return code, historical observation, or user confirmation must not be relabeled as SDK-verified current state.

## Phase 0 — Connection and Capability Discovery

### Camera Lab development interface

Develop USB behavior in a standalone machine-local Camera Lab before mounting it in the Profile Editor. Camera Lab must reuse the production camera-control service and API contracts, serve direct static HTML/CSS/JavaScript without invoking the card/PWA build, bind only to `127.0.0.1`, reject non-loopback Host headers, require a per-process token for every POST request, and send no-store and restrictive browser security headers.

Camera Lab must support a deterministic simulated backend for routine UI development and an explicit EDSDK backend for physical-camera testing. Simulated states include no camera, one EOS R5, multiple cameras, wrong model, missing optional properties, busy session, and disconnect after connection. Simulation controls must be absent or disabled in EDSDK mode. The standalone interface and the future Profile Editor workspace must consume the same service operations rather than reimplementing camera selection, identity enforcement, session ownership, cleanup, or event reporting.

Camera Lab and Profile Editor header version/build information must occupy the row below their action controls, with its right edge aligned to the rightmost Stop button's right edge. The silver camera logo must be vertically centered across both rows.

Profile Editor integration is a launcher boundary, not an embedded camera workspace. **Open in Camera Lab** must accept only the currently selected saved Subject/Profile Card, start Camera Lab if it is not running, reuse it if it is, and open a loopback URL whose `profile` query parameter contains only that canonical saved profile name. Camera Lab must validate the requested name against its freshly loaded profile catalog and preselect it without automatically connecting, scanning, comparing, or writing. Unsaved, new, and reference-card selections must not be passed. Camera Lab remains independently owned: Stop Profile Editor stops only the editor server, and Stop Camera Lab stops only the camera session and Lab server.

The Phase 0 API boundary is:

- `GET /api/camera-control/status`;
- `GET /api/camera-control/cameras`;
- `GET /api/camera-control/camera`;
- `GET /api/camera-control/events`;
- `GET /api/camera-control/capabilities`;
- `POST /api/camera-control/connect`;
- `POST /api/camera-control/disconnect`;
- `POST /api/camera-control/shutdown`;
- simulated-mode-only scenario and disconnect controls.

No Phase 0 endpoint may write a camera setting.

### Connection probe

The first implementation is read-only and must:

1. Initialize EDSDK only after an explicit command.
2. discover connected Canon cameras;
3. stop when no camera is connected;
4. require an explicit index when more than one camera is connected;
5. open exactly one camera session;
6. require the normalized connected product name to be exactly `EOS R5` or Canon's SDK-reported `Canon EOS R5` form;
7. report the SDK path and version plus every available product name, body/serial identifier, firmware version, and battery value;
8. permit a bounded watch interval that detects a failed identity poll as a disconnect;
9. close the camera session, release all SDK references, and terminate EDSDK on success, failure, interruption, or disconnect; and
10. expose no camera-setting write operation.

The probe must provide stable human-readable output and structured JSON output. Missing optional identity properties are reported as unavailable rather than causing a false connection failure. SDK load errors, no-camera state, ambiguous selection, wrong model, session errors, and disconnects must have distinct actionable messages and non-zero exit status.

### Capability discovery

Before any write-capable phase, physically enumerate the EOS R5 properties and descriptors exposed by the approved SDK and camera firmware. Record read/write/manual/unavailable classifications, allowed values, prerequisites, mode dependencies, equipment dependencies, and readback behavior in a reviewed machine-readable capability catalog. Do not infer support from property names or support on another Canon model.

The initial catalog is `00 Master/camera_capabilities.yaml`. It defines the reviewed core property scan set and stores only physical observations that identify their EOS R5 firmware, EDSDK version, date, and camera context. Do not store a camera body identifier in the tracked catalog. A successful `EdsGetPropertyDesc` result records descriptor evidence and allowed raw values; it does not establish safe write support. Every property remains `write_classification: unverified` until a separate guarded write and readback test produces `sdk_written_and_verified` evidence.

Each catalog definition must also identify zero or more canonical profile paths, a capability classification (`sdk_readable`, `conditional`, or `context_only`), and known dependencies. Human-readable decoding must be sourced from the installed Canon SDK headers, Canon's supplied API reference, or supplied sample application tables, retain the original raw value, and fall back visibly to the raw value when no reviewed label exists. Coverage is measured against leaf paths in the authored baseline: exact SDK-readable paths, conditional paths requiring context or target interpretation, and manual or SDK-unmapped paths. Coverage reporting does not convert an unmapped path into an unsupported-camera claim.

Canon limited properties may require a documented pre-session activation call using Canon's private activation property and key. That call only requests SDK exposure of the named property; it does not set the property's camera-menu value, is not exposed as a Camera Lab operation, and does not constitute write-support evidence. Activation failure is non-fatal and the property remains visibly unreadable.

## Phase 1 — Read-Only Profile Comparison

The initial Phase 1 API adds:

- `GET /api/camera-control/profiles` to list baseline-inheriting Subject/Profile Cards; and
- `GET /api/camera-control/comparison?profile=NAME` to compare one selected card with the cached read-only capability scan.

- Resolve the selected profile by merging the authored baseline with its overrides through the shared project engine.
- List only baseline-inheriting Subject/Profile Cards for selection; permanent reference cards are not camera-state targets.
- Order the primary review with the shared card renderer's visible setting rows, including its combined rows. List every remaining resolved profile setting in canonical card-layout order under **Additional settings**.
- Read every supported camera property without changing the camera.
- Normalize only explicitly documented equivalent representations.
- For the conditional Exposure Compensation, Aperture, and Shutter targets, evaluate exact values and simple single-context ranges when both the authored target and SDK readback can be interpreted safely. Report an exact value as `match`, an in-range or numerically equivalent representation as `equivalent`, and an interpretable out-of-range value as `difference`. Keep multi-context instructions—such as different targets by subject, lighting, grouping, bracketing, lens, or field condition—as `conditional` with a specific explanation; never choose the missing context automatically.
- Compare expected and actual values as `match`, `difference`, `equivalent`, `unreadable`, `manual_confirmation_needed`, `not_applicable`, or `blocked`.
- Display the comparison in columns for **Card Expected**, **Camera**, **Status**, and **Optimal Access Path**. Card Expected contains the setting name and expected value using the same My Menu-derived value color as the shared card/editor presentation. Order reviewed access methods by practical speed: assigned physical button, dial, switch, or direct control first; Q screen next; the selected card's My Menu route next; and the fastest standard menu path last. Do not assume My Menu is fastest when a direct control exists.
- Retain the actual value, raw SDK value when available, result, evidence method, camera context, and any prerequisite.
- Generate manual checklist items for camera-only settings, physical controls, unreadable values, and conditional equipment settings.

## Phase 2 — Guarded One-at-a-Time Writes

Before the first write-capable run:

1. confirm EOS R5 identity and firmware;
2. record battery/power, still/movie context, lens, flash, cards, and current mode where available;
3. require EOS Utility and other camera-control applications to be closed;
4. take a pre-change SDK readback snapshot; and
5. require and record a recoverable camera-side card backup.

The application must preview the complete proposed run, identify automatic and manual steps, and require explicit confirmation. Each automatic setting is processed independently: read current value, skip an existing match, write once, read back immediately, and stop on an unresolved failure. Never continue blindly after disconnect, camera-busy state, changed identity, or an unexpected prerequisite. Maintain a machine-local session journal sufficient to resume deliberately without representing a partial run as complete.

## Preferred Execution Order

The default plan is:

1. connection, identity, power, storage, and safety checks;
2. pre-change card backup and readback snapshot;
3. camera setup menus;
4. My Menu tabs;
5. shared physical controls and baseline settings;
6. the selected profile;
7. immediate and phase-boundary readback comparison;
8. manual completion checklist;
9. optional C1–C3 registration and recalled-state verification;
10. final cross-slot readback; and
11. independent post-configuration card backup.

Present one actionable step at a time while retaining visible overall progress. A later step must not silently bypass an incomplete safety, prerequisite, or verification step.

## Profile and C1–C3 Selection

- Offer `Apply for current use` for one active profile.
- Offer `Build and register C1–C3` when multiple profiles are selected.
- Multiple selected profiles require an explicit destination slot and are processed sequentially because only one ordinary shooting state can be active at a time.
- Build each C-mode target from a normal shooting mode rather than from a recalled C1, C2, or C3 state.
- Keep custom-mode Auto Update disabled throughout configuration and verification.
- After registration, leave the setup state, recall the slot, read back every supported value, correct differences, and recheck previously completed slots before proceeding.
- Registration remains a guided manual action until physical SDK testing proves safe support on the original EOS R5.
- During the read-only phase, Camera Lab must provide a separate C1–C3 Setup & Validation section before profile comparison. It must show the current saved foundation assigned to each slot, require an independent pre-configuration backup, direct setup from a normal shooting mode, open the assigned profile checklist without writing to the camera, state the manual Canon registration route, require recalled-state rescans and cross-slot rechecks, and finish with an independent post-configuration backup.
- C1–C3 labels must be resolved from the current saved profile sources whenever Camera Lab loads its profile catalog. A saved Profile Editor reassignment such as C1 to Macro must therefore appear as C1 – Macro after Camera Lab reloads; Camera Lab must not hardcode current foundation titles or maintain a separate assignment source.

## Manual Checklist

Every manual item must show the setting, expected value, actual value when readable, exact menu or physical-control route, reason automation is unavailable, and verification method. A user checkbox records `manual_user_confirmed`; it does not create SDK evidence. Camera Lab may retain these confirmations in browser-local storage keyed by profile and connected-camera context; it must explain that the record is machine-local, allow deliberate clearing, and invalidate the association when the profile target or camera context changes. During the read-only Phase 1 slice, provide an explicit full-camera rescan after changes and require that rescan, rather than a manual checkbox, to complete a directly readable difference. A later write-capable phase may add focused per-property readback without weakening this evidence boundary.

## Card Backup

- Treat pre-change and post-configuration backups as independent steps.
- Record the camera model, body identifier when available, firmware, backup filename, selected profiles, C1–C3 assignments, and verification summary in the machine-local session record.
- Respect the EOS R5 limit and compatibility rules documented by Canon, including the ten-file camera display limit and possible firmware incompatibility.
- Use the camera-guided `Save/load cam settings on card` operation for the original EOS R5. Disconnect USB before entering the camera menu, save the CSD file to the card, and reconnect only after the menu operation is complete.
- `EdsGetCsdFileData` was tested read-only on August 23, 2026 with the original EOS R5, firmware 2.2.1, EDSDK 13.20.20.0, direct USB, and external power. Canon returned `EDS_ERR_INVALID_PARAMETER` (`0x00000060`) for the documented host file stream; no CSD file was created and no camera setting changed. [Canon's EDSDK 13.20.11 release notes](https://personal.canon.jp/product/camera/software/api-package/info/detail-260527) identify PC camera-settings save/load support for EOS R10, EOS R100, and EOS R50 V, not the original EOS R5. Camera Lab must not expose this unavailable transfer as an operator backup action.
- `EdsSetCsdFileData` remains unavailable and must not be tested on the original EOS R5 merely because the SDK exports the symbol. It is a camera mutation and would additionally require guarded-write safeguards, compatibility checks, a fresh pre-restore backup, explicit owner confirmation, and model-specific physical support evidence.

## Failure and Recovery

- No camera mutation may occur during connection or read-only comparison phases.
- Camera Lab must provide an explicit authenticated **Stop Camera Lab** action that closes the active camera session and SDK helper before shutting down the loopback server. After confirmation, the page may attempt to close its tab but must also state clearly when browser policy requires the user to close it manually. Browser tab closure is not a reliable shutdown signal and must not replace this action; Terminal Control-C remains the fallback.
- Close every opened session and release every SDK reference in reverse ownership order.
- Preserve the last verified camera state, journal, and card backup reference after failure.
- Do not attempt speculative rollback writes. Direct the user to the verified pre-change card backup when restoration is required.
- A disconnected, busy, sleeping, recording, mode-incompatible, or unexpectedly changed camera blocks progress until the condition is resolved and identity is reconfirmed.
- A capability rescan must automatically refresh the displayed profile comparison when a profile is selected. If the camera session stopped responding, Camera Lab may close the stale read-only session, reconnect once, reconfirm EOS R5 identity, and retry the scan. After that single bounded retry fails, stop automatic recovery and show explicit camera wake, competing-application, USB reconnection, retry, and Camera Lab restart instructions.
- The comparison control must perform a fresh capability scan before rendering the selected profile, so it remains usable without returning to the connection controls. Comparison findings must support original card order and status order. Status order is Different, Unreadable, Conditional, Manual, Equivalent, Match, then Not applicable; manual findings are subgrouped by direct buttons and controls, My Menu tabs in saved tab order, standard menu, and entries without a reviewed route. A floating return-to-top control must remain available after scrolling.
- Profile choices and comparison headings must identify the intended registered-mode foundation by C1–C3 and its base card title. In the selector, list the three currently saved registered bases first in slot order as `Cx (Base)`. List every remaining profile alphabetically as `Profile ← Cx (Base)`, for example `Sports ← C2 (Birds in Flight)`; use `Profile ← No Cx` when no foundation is assigned. Comparison headings retain the base-first form `Cx – Base` for a registered base and `Cx – Base → Profile` for a derived card so the camera starting position and selected comparison target remain distinct. Current saved assignments may be C1 Wildlife, C2 Birds in Flight, and C3 Landscape, but all labels and guided Cx cards are dynamic.
- Keep the profile comparison and setup checklist before the expanded capability inventory in page order. The capability scan still runs first as the comparison's data source, but its detailed property and coverage results are secondary reference material displayed after the primary profile workflow.
- Every camera-setting finding must show at least one reviewed physical control, Q screen, configured My Menu tab, or Canon menu route. Camera Lab must retain configured My Menu routes for settings outside the compact card rows, including Focus Bracketing on SWITCH. Authored notes, strategy, and verification-status fields must be labeled as reference guidance rather than incorrectly reported as camera settings without a route.
- Comparison ordering must provide Card order, Status, and Setup route. Setup route is the default configuration workflow and combines card and additional findings into one sequence so access groups are not revisited across sections. It lists actionable findings first, grouped by physical controls, Q screen, each saved My Menu tab and item order, then exact Canon menu family and page; status priority applies within each route group. Equivalent, matching, and not-applicable findings follow in the same route order as a no-change section.
- The native console helper must regularly acquire Canon events with `EdsGetEvent` while a camera session is open and must acquire pending events immediately before a capability scan so physical camera changes are reflected in fresh property reads.

## Validation

- Unit-test selection, wrong-model rejection, optional-property handling, cleanup after every failure boundary, JSON serialization, and disconnect detection with a deterministic fake SDK backend.
- Keep real-camera tests explicit and machine-local. They must record SDK version, camera firmware, cable/connection method, and observed property support.
- Prove idempotence before enabling writes: a second complete run against an already matching camera must propose zero writes.
- An isolated Camera Lab iteration is limited to `80 Build/camera_control/`, its two `80 Build/test_camera_control_*.py` test modules, `00 Master/camera_capabilities.yaml`, and the USB specification or workflow documents that govern those files. It must not change the baseline, profiles, shared Profile Editor, shared renderer or build behavior, spreadsheet sources, published output, or another subsystem.
- Validate every isolated iteration with the two camera-control test modules, source-only validation, and the relevant simulated-browser or physical-camera check. Browser-only HTML, CSS, and JavaScript changes need a refresh; Python changes need a Camera Lab restart. The normal card/PWA development build and full validator are deliberately skipped during this fast loop.
- End the fast loop and run source-only validation, the normal development build, and full validation when a change falls outside the isolated file boundary, when Camera Lab is mounted in or changes the shared Profile Editor, when shared profile or build inputs change, when an integration check is explicitly requested, and before any commit, push, computer handoff, Finish Day, or publication.
- USB tests remain independent and must not become prerequisites for unrelated project builds.

## Implementation Status

- Phase 0 connection probe: implemented and physically verified against an EOS R5 on firmware 2.2.1 with EDSDK framework 13.20.20.0; five bounded identity polls and clean session shutdown verified.
- Phase 0 Camera Lab: implemented as a standalone loopback development interface and physically verified against the same EOS R5 connection.
- Phase 0 physical property capability catalog: the 22-property read-only scanner is verified on EOS R5 firmware 2.2.1 with EDSDK 13.20.20.0. Twenty properties were readable and all 22 returned descriptors. The second batch verified aspect ratio, continuous AF, eye detection, AF method, and IBIS high-resolution shot for profile readback. Subject detection was unreadable on the original EOS R5 in the tested context, and Canon documents the noise-reduction identifier as image metadata rather than a camera property. Write classifications remain unverified.
- Phase 1 read-only profile comparison and checklist: implemented as the first complete read-only slice. Camera Lab lists the 12 baseline-inheriting Subject/Profile Cards, resolves one selected profile through the shared baseline merge, and displays expected-versus-actual findings in card, status, or rapid setup-route order. Manual, conditional, and unreadable findings accept explicitly labeled `manual_user_confirmed` completion stored only in the browser for that profile and camera context; readable differences require a full rescan. The summary separates camera-verified, manually confirmed, unresolved, and blocked findings. Exact and simple-range contextual comparison is implemented for Exposure Compensation, Aperture, and Shutter; multi-context guidance remains explicitly conditional. Broader physical validation and the remaining manual capability gaps remain pending.
- Phase 2 guarded writes: pending.
- Phase 1 guided C1–C3 setup and recalled-state validation: implemented as a read-only workflow driven by the current saved slot foundations. Camera Lab opens the appropriate comparison checklist but performs no registration or setting writes. Guarded or automated C1–C3 writes remain pending.
- Profile Editor launcher integration: implemented as an independent-app handoff. The standalone editor runs without a Terminal window, has its own authenticated stop action, and can start or reuse Camera Lab with the current saved Subject/Profile Card preselected. The Lab reloads current profile and C1–C3 sources and does not synchronize lifecycle or unsaved editor state.
- Automated camera-settings-data transfer: physically tested and unavailable on the original EOS R5 firmware 2.2.1. `EdsGetCsdFileData` returned `EDS_ERR_INVALID_PARAMETER`; `EdsSetCsdFileData` was not called. Continue using camera-side card backups.
