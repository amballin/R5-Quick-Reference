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
- Phase 2A guarded planning and execution remains available in the deterministic simulator. Canon EDSDK stays strictly read-only by default. Phase 2B may expose physical qualification and guarded execution only when the server and native helper were both launched with the explicit physical-write gate, and only under the evidence and confirmation rules below. The existing reviewed limited-property activation and property-event registration remain separate discovery operations.
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

### Reviewed promotion into verification status

Camera Lab journals and manual-confirmation records remain machine-local evidence. Profile Editor may inventory only completed physical-camera EDSDK guarded-run journals and present exact unmigrated setting evidence for deliberate promotion. The first importer maps a journal profile to its current UUID-backed C1–C3 assignment, maps a journal setting path to one defined registration row, and may set only that slot's configured result to `Pass`. It must preserve evidence method, journal identity and hash, profile, setting path, target, and completion time in verification history; deduplicate by stable session/slot/setting identity; select nothing automatically; and exclude simulator, incomplete, ambiguous, non-registration, and already promoted evidence. A promotion never establishes read-back, slot registration, operational performance, backup completion, Canon capability, or owner-confirmed project state.

Promotion must be blocked while the machine-local verification workbook has unimported edits. The reviewed canonical status change and safely rebuilt working tracker use the guarded transaction requirements in the Build and Validation Specification. Camera Lab itself continues to write no repository source or tracker status.

## Phase 0 — Connection and Capability Discovery

### Camera Lab development interface

Develop USB behavior in a standalone machine-local Camera Lab before mounting it in the Profile Editor. Camera Lab must reuse the production camera-control service and API contracts, serve direct static HTML/CSS/JavaScript without invoking the card/PWA build, bind only to `127.0.0.1`, reject non-loopback Host headers, require a per-process token for every POST request, and send no-store and restrictive browser security headers.

Camera Lab must support a deterministic simulated backend for routine UI development and an explicit EDSDK backend for physical-camera testing. Simulated states include no camera, one EOS R5, multiple cameras, wrong model, missing optional properties, busy session, and disconnect after connection. Simulation controls must be absent or disabled in EDSDK mode. The standalone interface and the future Profile Editor workspace must consume the same service operations rather than reimplementing camera selection, identity enforcement, session ownership, cleanup, or event reporting.

The running Lab must offer **Use Simulator** in EDSDK mode and **Use Camera** in simulated mode. Before either switch, show an explicit confirmation naming the destination, stating that the current camera or simulated session plus scan/comparison state will close, and reiterating that no camera settings will be written. Only the confirmation action may call the authenticated backend-restart endpoint. The server must close the current session, release its loopback listener, and replace the same supervised process in the requested mode; it must never start a competing server. Returning to EDSDK requires the machine-local helper. Reload the existing page only after the replacement server reports the requested backend.

Camera Lab and Profile Editor must share the repository-owned local-application version in `00 Master/application_version.yaml` and display `Major.Minor.Incremental · Main/Prototype` on a dedicated third header row, right-aligned with the control-button column above it. Major is manually controlled. Minor advances for every commit after the recorded anchor. Incremental advances once through `80 Build/scripts/complete-development-update.sh` for each completed development update against the same commit and displays as zero after Minor advances. Each app's full checkout badge remains prominent on the second row. Camera Lab places **No setting writes** to the left of that checkout badge in default Canon EDSDK mode, **Camera changes enabled** in gated Phase 2B mode, or **Simulator changes only** in simulated mode; its first row contains the active backend, matching **Use Simulator/Use Camera** action, **Enable camera changes/Return to read-only** in EDSDK mode, and **Stop Camera Lab**. Profile Editor's first row orders **User guide**, **Open in Camera Lab**, and **Stop Profile Editor**. Each app's deterministic source hash must remain available by expanding the third-row version rather than in the primary header text. The silver camera logo must remain isolated in its adjacent grid column and vertically centered across all three rows.

Both local applications must show a persistent checkout-context badge in the second header row. The badge must derive from the active Git worktree rather than a hardcoded folder name: **Main project** for branch `main`, **Prototype · &lt;branch&gt;** for another named branch, and **Project context unavailable** when the worktree cannot be identified. This indicator is operational guidance only and does not change repository authority.

Reopening a responsive Profile Editor or Camera Lab application must recover its Chrome window instead of attempting a duplicate server. Camera Lab reuse requires a successful loopback status response that identifies the running service as a read-only Camera Lab. A listener that does not pass that check remains an unrecognized port conflict and must not be stopped or reused automatically.

Profile Editor integration is a launcher boundary, not an embedded camera workspace. **Open in Camera Lab** must accept only the currently selected saved Subject/Profile Card, start Camera Lab if it is not running, reuse it if it is, and open a loopback URL whose `profile` query parameter contains only that canonical saved profile name. Camera Lab must validate the requested name against its freshly loaded profile catalog and preselect it without automatically connecting, scanning, comparing, or writing. Unsaved, new, and reference-card selections must not be passed. Camera Lab remains independently owned: Stop Profile Editor stops only the editor server, and Stop Camera Lab stops only the camera session and Lab server.

The Phase 0 API boundary is:

- `GET /api/camera-control/status`;
- `GET /api/camera-control/cameras`;
- `GET /api/camera-control/camera`;
- `GET /api/camera-control/events`;
- `GET /api/camera-control/capabilities`;
- `POST /api/camera-control/connect`;
- `POST /api/camera-control/disconnect`;
- `POST /api/camera-control/restart-backend`;
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
- For the conditional Exposure Compensation, Aperture, and Shutter targets, evaluate exact values and simple single-context ranges when both the authored target and SDK readback can be interpreted safely. Report an exact value as `match`, an in-range or numerically equivalent representation as `equivalent`, and an interpretable out-of-range value as `difference`. When one authored target contains distinct alternatives by subject, lighting, or grouping, Camera Lab must ask which authored context applies, select only that clause after an explicit choice, and then report `match`, `equivalent`, or `difference` when interpretation is safe. It must never infer the missing choice. Keep the finding `conditional` when no choice has been made, the choice is invalid, a bracketing or lens instruction does not define distinct comparable targets, the authored guidance lacks a numeric target, or the selected target and readback still cannot be interpreted safely.
- Compare expected and actual values as `match`, `difference`, `equivalent`, `unreadable`, `manual_confirmation_needed`, `not_applicable`, or `blocked`.
- Display the comparison in columns for **Card Expected**, **Camera**, **Status**, and **Optimal Access Path**. Card Expected contains the setting name and expected value using the same My Menu-derived value color as the shared card/editor presentation. Order reviewed access methods by practical speed: assigned physical button, dial, switch, or direct control first; Q screen next; the selected card's My Menu route next; and the fastest standard menu path last. Do not assume My Menu is fastest when a direct control exists.
- Retain the actual value, raw SDK value when available, result, evidence method, camera context, and any prerequisite.
- Generate manual checklist items for camera-only settings, physical controls, unreadable values, and conditional equipment settings.
- Resolve the selected profile's authored lens choices through `00 Master/profile_lens_guidance.yaml` and the owned-equipment capabilities in `data/stabilization_reference.yaml`. In physical-camera mode, match Canon's camera-reported lens name to the canonical lens identity and use that attached lens by default. In simulator or planning contexts without a recognized attached lens, use the card's Primary lens by default. Offer only that card's authored lens/accessory choices as deliberate planning alternatives. A planning choice that differs from a recognized attached lens must be labeled as an override and must not enter physical guarded execution until the matching lens is attached and rescanned.
- Derive stabilization controls from the selected lens capability. A lens with a physical Mode 1 / 2 / 3 selector offers only its catalogued modes and defaults to the selected profile's merged stabilization target when supported; the operator may deliberately override that target only with another supported mode for the current comparison. A lens with IS On/Off but no mode selector shows automatic stabilization behavior and makes a profile Mode 1 / 2 / 3 target not applicable. A lens without optical IS retains the EOS R5 body stabilization route. Never expose an unsupported lens mode.
- Evaluate every matching `camera_lab` rule from `00 Master/feature_interactions.yaml` against the merged profile plus the resolved lens/accessory context. Attach the rule's behavior and message to every affected finding. An `inactive` effect makes the affected setting `not_applicable`; an equipment `overridden` effect is recorded as automatically controlled by that equipment. `restricted`, `replaced`, `coordinated`, `available`, and `automatic` effects retain the applicable comparison or manual action while explaining the changed availability, route, limitation, or coordination. The comparison must cover the catalogued AF dependencies, High Speed Display context, Focus Bracketing flash restriction, stabilization behavior, adapted-lens control ring, extender tradeoffs, macro limitations, MP-E limitations, and EF-S forced crop without guessing absent context.

## Phase 2A — Simulated Guarded-Run Planning

After a Subject/Profile Card comparison completes, **Apply this profile to camera** is available in simulated mode. Default Canon EDSDK mode exposes neither this action nor any guarded-run API. Phase 2A does not establish physical write support, change the tracked real-camera write classifications, automate C1–C3 registration, or transfer a camera-settings file. Phase 2B may expose the same operator action only after camera changes are explicitly enabled.

Before a simulated run can be planned, Camera Lab must:

1. confirm and record simulated EOS R5 product identity, body identifier when available, and firmware;
2. record battery or external-power evidence plus still/movie context, lens, flash, cards, and current mode when available;
3. require explicit confirmation that EOS Utility and every other camera-control application are closed;
4. take and journal a fresh pre-change readback snapshot; and
5. require explicit confirmation of a recoverable camera-side card backup and record its `.CSD` filename.

Readiness must present controlled equipment choices rather than open-ended descriptions: lens defaults to the camera-reported attached lens when available and otherwise to the selected card's Primary lens, while offering only that card's authored lens choices; flash offers **None**, **Flash Attached**, and **Trigger**, defaulting to **None**; and cards offers **CFexpress & SD**, **CFexpress**, and **SD**. A non-attached authored lens remains a planning choice and is subject to the physical guarded-execution lens check.

Readiness must also ask whether the operator has already confirmed the matching **Camera Setup Essentials** Set & Forget targets. This confirmation is optional and records `manual_user_confirmed` evidence only for exact selected-profile targets that appear on Camera Setup Essentials, match its effective target, and lack contradictory camera readback. It must not clear a readable difference, unresolved contextual target, blocked item, or profile-specific override.

The review must always reflect the currently displayed readiness choices. Changing a readiness choice while the run is still planned must rebuild the complete review before execution can begin. After execution is confirmed, readiness controls must display and lock to the values recorded in that immutable run; a later on-screen edit must never imply that the active plan inherited new equipment or Camera Setup Essentials evidence. Changing those values requires stopping the attempt and preparing a new review.

The preview must list the entire proposed run before execution and classify every step as **Already matching and skipped**, **Simulator-automatic**, **Manual**, or **Blocked or unsupported**. Conditional guidance with an explicit authored choice remains blocked until the choice is supplied; field- or equipment-dependent guidance without a safely encodable target remains manual. A target without one unambiguous reviewed simulator encoding remains manual. A missing prerequisite or simulator-reported unsupported value is blocked.

The following authenticated routes exist only while the deterministic simulator is active and must return not-found in Canon EDSDK mode:

- `GET /api/camera-control/guarded-run?session_id=ID`;
- `POST /api/camera-control/guarded-run/prepare`;
- `POST /api/camera-control/guarded-run/confirm`;
- `POST /api/camera-control/guarded-run/next`;
- `POST /api/camera-control/guarded-run/resume`; and
- `POST /api/camera-control/guarded-run/abort`.

Execution requires a separate explicit confirmation after preview. Each call to the next-step route may process only the one displayed step. For a simulator-automatic step it must read the current value, skip an existing match, otherwise simulate exactly one write, immediately read the value back, and advance only after equality is verified. A manual step advances only after explicit manual confirmation. A blocked step cannot execute. The run stops immediately on readback mismatch, unsupported value, missing or changed prerequisite, camera-busy state, disconnect, or changed camera identity. A partial, failed, blocked, or aborted run must never be labeled complete.

The deterministic scenarios are successful write and readback, readback mismatch, unsupported value, missing prerequisite, camera busy, disconnect, and changed camera identity. A second plan after a successful run must propose zero automatic writes for settings already matching.

Every prepared run is stored as an atomic JSON journal under the machine-local `Camera Lab/Guarded Runs/` directory. The journal records the selected profile, safe camera and preflight context, pre-change snapshot, complete plan, per-setting reads/writes/readbacks or manual confirmation, operator work groups, progress, failure, deliberate resume, abort, and final status. It must not store request tokens, credentials, secrets, or enter Git. Resume is deliberate and must re-confirm the recorded camera identity; abort preserves the journal.

The complete audit plan and operator work queue are distinct. Already-correct, equivalent, not-applicable, and reference-only rows are finalized from the fresh snapshot and never consume an operator action; exact readable matches are automatically rechecked at confirmation and again before completion. The interface separately reports automatic work, operator actions, and no-action rows. A changed previously matching value invalidates the reviewed plan and stops the attempt.

In simulator mode, the single post-preview confirmation authorizes Camera Lab to process all simulator-automatic settings without additional clicks. Each remains an independent journaled transaction: validate identity and prerequisites, read, skip a fresh match or simulate exactly one write, immediately read back, save progress, and stop before any later automatic setting on failure. Physical mode retains one deliberate action per actual camera write.

Manual settings are grouped by practical camera route without losing their individual targets or journal records. The active card lists every setting and target in the group. One explicit group-completion action triggers one capability rescan, camera-verifies every exact readable match together, and records explicit manual confirmation for remaining unreadable or non-exact items. The active workspace remains stationary and focused between actions. Preflight fields may persist only in browser session storage and only under the exact unchanged camera product, body, firmware, and lens identity.

Manual-group completion must also update Rapid setup through the machine-local `Camera Lab/Manual Confirmations.json` ledger. The selected card refreshes immediately: exact SDK-readable matches use camera-verification evidence, while unreadable or non-exact items use clearly labelled manual-confirmation evidence. Cross-card reuse is permitted only during the same uninterrupted connection session and only when camera product, body identifier, firmware, camera-reported lens, selected canonical lens/accessory, selected lens IS mode, current exposure mode, still/movie context, flash, cards, setting path, and normalized target all match. A different target, disconnect, server restart, camera or equipment identity change, mode change, explicit clearing, or contradictory readback must prevent reuse. Browser-local checklist confirmation is scoped by the same selected canonical equipment and mode context. The ledger stores no token, credential, or secret and remains outside Git.

## Phase 2B — Qualified Physical Guarded Writes

Canon EDSDK remains read-only unless Camera Lab is launched with `--enable-physical-writes`. That flag must also be passed to the native helper; the default helper process must reject every setting-write command. Backend switching and ordinary app launch must not silently enable the flag. Ordinary EDSDK mode must provide a deliberate **Enable camera changes** action that explains the consequences and, only after confirmation, closes the current session and replaces the same server process with the explicit flag. Gated mode must provide **Return to read-only** through the same confirmed session-closing restart. Neither transition may perform a camera-setting write.

Before normal physical guarded execution, Camera Lab must qualify each exact raw value on the connected body. Qualification is limited to tracked `write_qualification_candidate` properties and a target present in the descriptor read during the current session. It requires the Phase 2A preflight, a readable body identifier, firmware, EDSDK version, fresh original readback, complete reversible preview, and separate explicit confirmation. One qualification transaction may perform at most two setting writes: write the temporary target and immediately verify it, then restore the original value and immediately verify restoration. A failed target verification must still make the bounded restoration attempt. If restoration cannot be verified, stop, label the session incomplete, and show the exact manual restoration action; never create write evidence.

Successful qualification records `sdk_written_and_verified` evidence only in the machine-local `Camera Lab/Physical Write Evidence.json` file. Evidence is scoped to exact product, body identifier, firmware, EDSDK framework version, property, and raw value. It contains no token, credential, or secret and must not enter Git. Descriptor access alone, another body or firmware, a merely successful setter return, simulator evidence, or manual confirmation never enables a physical value.

The native helper accepts only the nine conservative qualification candidates declared in the tracked capability catalog and duplicated as a defensive compiled allowlist: white balance, picture style, drive mode, metering mode, AF operation, AF method, cropping/aspect ratio, continuous AF, and eye detection. It validates a 32-bit integer data type and current descriptor membership before the single guarded `EdsSetPropertyData` call. Exposure mode, ISO, aperture, shutter, exposure compensation, image quality, C1–C3 registration, and CSD transfer remain outside the physical write surface.

Guarded preflight must read the attached lens through Canon's documented `kEdsPropID_LensName` when available, display it as the default lens choice, and store that camera readback instead of accepting contradictory text. The lens selector may also list only the selected card's authored choices for planning. When no lens name is returned, default to the card's Primary lens and label the selected authored lens as manual context. Display **Switching tracked subjects** as **Initial priority (0)**, **On subject (1)**, or **Switch subject (2)** wherever the operator selects or reviews it. Because the installed EDSDK exposes no documented property ID for that camera control, it remains manual and outside the qualification allowlist.

Physical guarded planning must preserve the exact equipment choice and resolved stabilization mode from the reviewed comparison. Reject a planning lens that differs from the camera-reported attached lens, and reject a camera-reported lens that cannot be matched to the canonical owned-equipment catalog. The lens identity remains part of the guarded-run stop boundary. A manually selected accessory is operator-confirmed context; it does not become camera-read evidence.

After a comparison, physical planning classifies an exact qualified target as **EOS R5 automatic**. Every unqualified, out-of-descriptor, or non-allowlisted target is **Blocked or unsupported**. The full plan and a separate execution confirmation are required. Each next-step request handles only the visible setting: revalidate identity, read current value, skip a match, otherwise perform exactly one allowlisted write, immediately read it back, and advance only on equality. Busy state, disconnect, changed identity, changed prerequisite, setter failure, or mismatch stops the run immediately; a partial physical run is never complete. Manual C1–C3 registration and camera-settings-file transfer remain unavailable.

The operator interface must call this workflow **Apply this profile to camera** and organize it as readiness, review, one visible action at a time, and result. Translate internal classifications into **Already correct**, **Camera Lab will change**, **You will change**, and **Needs attention first**. The review must state that nothing has changed, prevent start while any item needs attention, and give an actionable resolution for every such item. Reversible value qualification must be collapsed under **Advanced setup** and described as a safety test rather than placed in the main path.

The result must say **Profile applied successfully** only after every step is final and successful, then list settings verified automatically, confirmed manually, and left unchanged because they were already correct. A failure, blocked state, disconnect, identity or prerequisite change, or user stop must instead say **Profile not fully applied**, show completed versus total steps, identify the stopping point and completed settings, and retain the deliberate continue-or-stop options. Progress alone is never proof of success. Internal API and journal names may retain `guarded_run` without exposing that terminology as the primary operator model.

Phase 2B adds authenticated qualification candidate/read, prepare, confirm, and execute routes only in explicitly enabled EDSDK mode. Default EDSDK mode returns not-found for qualification and guarded-run routes. Automated tests must use a no-SDK physical backend double and may never perform a real-camera write. A live qualification or guarded execution is a separate owner-approved physical session.

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

Present one actionable setting or same-route manual group at a time while retaining visible automatic and operator progress. Never put an already-correct or non-action row into the operator queue. A later step must not silently bypass an incomplete safety, prerequisite, or verification step.

## Profile and C1–C3 Selection

- Offer `Apply for current use` for one active profile.
- Offer `Build and register C1–C3` when multiple profiles are selected.
- Multiple selected profiles require an explicit destination slot and are processed sequentially because only one ordinary shooting state can be active at a time.
- Build each C-mode target from a normal shooting mode rather than from a recalled C1, C2, or C3 state.
- Keep custom-mode Auto Update disabled throughout configuration and verification.
- After registration, leave the setup state, recall the slot, read back every supported value, correct differences, and recheck previously completed slots before proceeding.
- Registration remains a guided manual action until physical SDK testing proves safe support on the original EOS R5.
- During the read-only phase, Camera Lab must provide a separate C1–C3 Maintenance & Validation section before profile comparison. Keep it collapsed by default because it is an infrequent maintenance workflow, while retaining an explicit expand/collapse summary in its first-in-process position. It must state that the current camera-body registrations were verified in physical session 3, show the current saved foundation assigned to each slot, and support routine recalled-state validation without implying that registration is unfinished. For an assignment change, reset, restore, or deliberate re-registration, it must require an independent pre-configuration backup, direct setup from a normal shooting mode, open the assigned profile checklist without writing to the camera, state the manual Canon registration route, require recalled-state rescans and cross-slot rechecks, and finish with an independent post-configuration backup.
- C1–C3 labels must be resolved from the current saved profile sources whenever Camera Lab loads its profile catalog. A saved Profile Editor reassignment such as C1 to Macro must therefore appear as C1 – Macro after Camera Lab reloads; Camera Lab must not hardcode current foundation titles or maintain a separate assignment source.

## Manual Checklist

Every manual item must show the setting, expected value, actual value when readable, exact menu or physical-control route, reason automation is unavailable, and verification method. A user checkbox records `manual_user_confirmed`; it does not create SDK evidence. Camera Lab may retain these confirmations in browser-local storage keyed by profile and connected-camera context; it must explain that the record is machine-local, allow deliberate clearing, and invalidate the association when the profile target or camera context changes. A conditional finding with unresolved authored context must require that contextual choice before manual confirmation is offered. During the read-only Phase 1 slice, provide an explicit full-camera rescan after changes and require that rescan, rather than a manual checkbox, to complete a directly readable difference. A later write-capable phase may add focused per-property readback without weakening this evidence boundary.

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
- Selecting a different profile after a camera is connected must perform a fresh capability scan, refresh the displayed comparison, and expose that card's lens choices without requiring a second comparison command. If the camera session stopped responding, Camera Lab may close the stale read-only session, reconnect once, reconfirm EOS R5 identity, and retry the scan. After that single bounded retry fails, stop automatic recovery and show explicit camera wake, competing-application, USB reconnection, retry, and Camera Lab restart instructions.
- The comparison control must perform a fresh capability scan before rendering the selected profile, so it remains usable without returning to the connection controls. Comparison findings must support original card order and status order. Status order is Different, Unreadable, Conditional, Manual, Equivalent, Match, then Not applicable; manual findings are subgrouped by direct buttons and controls, My Menu tabs in saved tab order, standard menu, and entries without a reviewed route. After scrolling, the floating up-arrow control must return to the **Compare a Subject/Profile Card** section rather than the page header.
- Profile choices and comparison headings must identify the intended registered-mode foundation by C1–C3 and its base card title. In the selector, list the three currently saved registered bases first in slot order as `Cx (Base)`. List every remaining profile alphabetically as `Profile ← Cx (Base)`, for example `Sports ← C2 (Birds in Flight)`; use `Profile ← No Cx` when no foundation is assigned. Comparison headings retain the base-first form `Cx – Base` for a registered base and `Cx – Base → Profile` for a derived card so the camera starting position and selected comparison target remain distinct. Current saved assignments may be C1 Wildlife, C2 Birds in Flight, and C3 Landscape, but all labels and guided Cx cards are dynamic.
- Keep the profile comparison and setup checklist before the capability inventory in page order. The capability scan still runs first as the comparison's data source, but its detailed property and coverage results are secondary reference material displayed after the primary profile workflow and collapsed by default behind an explicit **Camera capabilities** summary.
- Every camera-setting finding must show at least one reviewed physical control, Q screen, configured My Menu tab, or Canon menu route. Camera Lab must retain configured My Menu routes for settings outside the compact card rows, including Focus Bracketing on SWITCH. Authored notes, strategy, and verification-status fields must be labeled as reference guidance rather than incorrectly reported as camera settings without a route.
- Comparison ordering must provide Card order, Status, and Setup route. Setup route is the default configuration workflow and combines card and additional findings into one sequence so access groups are not revisited across sections. It lists actionable findings first, grouped by physical controls, Q screen, each saved My Menu tab and item order, then exact Canon menu family and page; status priority applies within each route group. Equivalent, matching, and not-applicable findings follow in the same route order as a no-change section.
- The native console helper must regularly acquire Canon events with `EdsGetEvent` while a camera session is open and must acquire pending events immediately before a capability scan so physical camera changes are reflected in fresh property reads.

## Validation

- Unit-test selection, wrong-model rejection, optional-property handling, cleanup after every failure boundary, JSON serialization, and disconnect detection with a deterministic fake SDK backend.
- Unit-test all Phase 2A simulator success and failure scenarios, explicit confirmation, idempotent re-planning, manual-step confirmation, atomic machine-local journaling, deliberate resume, abort, and the rule that partial runs never become complete. Unit-test Phase 2B with a no-SDK physical double: default-mode route rejection, explicit launch gating, allowlist and descriptor enforcement, confirmation, successful target/readback/restore/readback, evidence scoping, restoration failure, unqualified blocking, one-setting physical execution, mismatch, disconnect, and identity change. Static validation must prove the helper has only the reviewed activation and guarded setting setter call sites and no CSD write.
- Keep real-camera tests explicit and machine-local. They must record SDK version, camera firmware, cable/connection method, and observed property support.
- Prove idempotence before enabling writes: a second complete run against an already matching camera must propose zero writes.
- An isolated Camera Lab iteration is limited to `80 Build/camera_control/`, its three `80 Build/test_camera_control_*.py` test modules, the Camera Lab safety validator, `00 Master/camera_capabilities.yaml`, and the USB specification or workflow documents that govern those files. It must not change the baseline, profiles, shared Profile Editor, shared renderer or build behavior, spreadsheet sources, published output, or another subsystem.
- Validate every isolated iteration with the three camera-control test modules, source-only validation, and the relevant simulated-browser or physical-camera check. Browser-only HTML, CSS, and JavaScript changes need a refresh; Python changes need a Camera Lab restart. The normal card/PWA development build and full validator are deliberately skipped during this fast loop.
- End the fast loop and run source-only validation, the normal development build, and full validation when a change falls outside the isolated file boundary, when Camera Lab is mounted in or changes the shared Profile Editor, when shared profile or build inputs change, when an integration check is explicitly requested, and before any commit, push, computer handoff, Finish Day, or publication.
- USB tests remain independent and must not become prerequisites for unrelated project builds.

## Implementation Status

- Phase 0 connection probe: implemented and physically verified against an EOS R5 on firmware 2.2.1 with EDSDK framework 13.20.20.0; five bounded identity polls and clean session shutdown verified.
- Phase 0 Camera Lab: implemented as a standalone loopback development interface and physically verified against the same EOS R5 connection.
- Confirmed backend switching: implemented for replacing the running EDSDK Lab with the deterministic simulator and returning to the physical-camera backend without a competing loopback server.
- Phase 0 physical property capability catalog: the 22-property read-only scanner is verified on EOS R5 firmware 2.2.1 with EDSDK 13.20.20.0. Twenty properties were readable and all 22 returned descriptors. The second batch verified aspect ratio, continuous AF, eye detection, AF method, and IBIS high-resolution shot for profile readback. Subject detection was unreadable on the original EOS R5 in the tested context, and Canon documents the noise-reduction identifier as image metadata rather than a camera property. Write classifications remain unverified.
- Phase 1 read-only profile comparison and checklist: implemented as the first complete read-only slice. Camera Lab lists the 12 baseline-inheriting Subject/Profile Cards, resolves one selected profile through the shared baseline merge, and displays expected-versus-actual findings in card, status, or rapid setup-route order. Manual, conditional, and unreadable findings accept explicitly labeled `manual_user_confirmed` completion stored only in the browser for that profile and camera context; readable differences require a full rescan. The summary separates camera-verified, manually confirmed, unresolved, and blocked findings. Exact and simple-range contextual comparison is implemented for Exposure Compensation, Aperture, and Shutter. Multi-target People and Sports guidance asks for the missing authored subject, grouping, or lighting context and compares only the selected authored clause; guidance without distinct comparable targets remains explicitly conditional. Camera Lab also resolves the camera-reported or planned card lens through the owned-equipment catalog, offers only supported physical IS modes with a profile-derived default, and applies every matching structured Canon feature-interaction rule to affected findings. Broader physical validation and the remaining manual SDK capability gaps remain pending.
- Phase 2A simulated guarded-run planning and execution: implemented. A completed comparison can collect the full preflight and pre-change snapshot, preview all four step classifications, require explicit confirmation, process one simulator setting at a time with immediate readback, stop on every deterministic failure scenario, and persist an atomic machine-local journal for deliberate resume or abort. Default Canon EDSDK remains read-only and exposes no guarded-run action or route; explicitly gated physical behavior is governed only by Phase 2B.
- Phase 2B qualified physical guarded writes: implemented and read-only by default. The ordinary Lab can deliberately restart into or out of camera-change mode without a Terminal workflow. Its operator path is **Apply this profile to camera**, with plain readiness, review, one-action, and explicit success-or-stopped results; reversible qualification is collapsed under **Advanced setup**. Physical session 4 reversibly qualified Picture Style Neutral and Standard on EOS R5 body `032021000338`, firmware 2.2.1, EDSDK 13.20.20.0; the final readback restored Neutral and the evidence remains machine-local. Other exact values remain blocked until separately qualified. The connected lens is camera-read and authoritative in preflight. Switching tracked subjects displays Canon's numeric choices but remains manual because no documented EDSDK property ID is available.
- Phase 1 guided C1–C3 maintenance and recalled-state validation: implemented as a read-only workflow driven by the current saved slot foundations. Physical session 3 manually registered and camera-body verified C1 Wildlife, C2 Birds in Flight, and C3 Landscape, with `C123_CFG.CSD` saved as the recovery checkpoint; exact lens stabilization Mode 1/3 remains equipment-dependent. Camera Lab opens the appropriate comparison checklist but performs no registration or setting writes. Guarded or automated C1–C3 writes remain pending.
- Profile Editor launcher integration: implemented as an independent-app handoff. The standalone editor runs without a Terminal window, has its own authenticated stop action, and can start or reuse Camera Lab with the current saved Subject/Profile Card preselected. The Lab reloads current profile and C1–C3 sources and does not synchronize lifecycle or unsaved editor state.
- Reviewed tracker promotion: implemented in Profile Editor for completed physical EDSDK guarded-run journals. It selects nothing automatically and promotes only exact mapped setting evidence into the currently assigned C1–C3 slot's configured result, with journal provenance and deduplication. Simulator results and incomplete runs are excluded, and read-back, registration completion, operational tests, backups, Canon capability claims, and owner-confirmed project evidence remain separate.
- Automated camera-settings-data transfer: physically tested and unavailable on the original EOS R5 firmware 2.2.1. `EdsGetCsdFileData` returned `EDS_ERR_INVALID_PARAMETER`; `EdsSetCsdFileData` was not called. Continue using camera-side card backups.
