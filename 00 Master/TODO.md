# Project To-Do

This file records approved follow-up work and analysis candidates that should not be lost. It is repository planning material, not published Field Guide content and not a source of binding architecture. Promote a decision through the normal approval process before implementing any architectural item.

## Control Architecture Follow-Up

- Run the non-published [EOS R5 On-Camera Verification Checklist](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Checklist.md), record progress and evidence in its [Excel tracker](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Tracker.xlsx), and promote only completed, unambiguous results to owner-confirmed status.
- Physically configure and verify AF-ON with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to Face + Tracking.
- Physically configure and verify AE Lock with AF Operation and Servo AF characteristics set to Maintain current setting and AF Method set to 1-Point AF.
- Configure Case 1 as the project -1 / +1 preset, verify that C1 recalls Wildlife with that custom Case, register and verify C2 as Birds in Flight / Action, and retain C3 as Landscape.
- Verify that the DOF button changes One-Shot AF ↔ Servo AF and that both AF-start buttons respect the resulting state.
- Physically test the joystick straight press with Face + Tracking, including face/eye selection, tracking release, the single- and double-border displays, and the Face Select: Off indication; do not make the behavior definitive until verified.
- Decide whether Spot AF needs another immediate control for serious macro work.

### My Menu Transition Verification and Expansion

Verify the approved starting workflow from the registered C1-C3 profiles to every derived subject card, then evaluate whether another My Menu item or tab is warranted.

| Target | Best starting mode | Already close | Remaining changes | Strong My Menu candidates |
|---|---|---|---|---|
| People | C1 Wildlife | Fv, Auto ISO, Servo AF, Face + Tracking, Eye Detection, Mode 1 | Custom Case 1 to Case A, Animals to People, High to Low Speed Continuous, EFCS to Mechanical, portrait shutter/aperture targets | AF Case; Subject to detect; Shutter mode |
| Birds Perched | C1 Wildlife | Fv, Auto ISO, Servo AF, Face + Tracking, Animals, Eye Detection, High Speed Continuous, EFCS, Mode 1 | Set perched-bird shutter/aperture targets and exposure compensation | None; use dials |
| Sports | C2 Birds in Flight | Tv, Auto ISO, Servo AF, Face + Tracking, Eye Detection, High Speed Continuous+, Mechanical, Mode 3 | Case 4 to project-customized Case 1, Animals to People, sports shutter target, reset exposure compensation | AF Case; Subject to detect |
| Travel | C3 Landscape | 1-Point AF, no subject detection, Eye Detection disabled, Single Shot, EFCS, Mode 1 | Av to Fv, ISO 100 to Auto, One-Shot to Servo AF, clear the landscape aperture target | None; use MODE, Q, DOF button, and dials |
| Macro | C3 Landscape | Av, One-Shot AF, Single Shot, EFCS, Mode 1, suitable aperture range | ISO 100 to Auto, 1-Point to Spot AF, enable Focus Bracketing, set f/8 | Focus bracketing |
| Waterdrops | C3 Landscape | ISO 100, Single Shot, aperture near f/8-f/11 | Av to Manual, 1/200 sec., Mechanical, Manual Focus, stabilization Off | Shutter mode; IS (Image Stabilizer) mode |
| Fireworks | C3 Landscape | ISO 100, Single Shot, EFCS, f/8-f/11 | Av to Manual, 2-6 sec., Manual Focus, stabilization Off | IS (Image Stabilizer) mode |

Test these transitions on the camera with **Auto update set.: Disable**. Record whether the mode-specific exposure values and broader settings retain, revert, or carry across, including exposure compensation and any temporary 1.6× crop. Confirm that recalling C1 or C3 supplies the expected starting state and that subsequent changes do not rewrite the registered mode.

Verify the approved starting My Menu tab named **SWITCH**:

1. Subject to detect
2. Shutter mode
3. Focus bracketing
4. IS (Image Stabilizer) mode
5. Cropping/aspect ratio

Leave the sixth position open until physical transition testing identifies another menu-only need. My Menu only shortens navigation to the real setting; it does not apply a complete derived subject configuration. Keep Drive Mode, ISO, shutter speed, aperture, and AF Method on Q, the dials, or the AF-point controls when those remain faster, and keep lens AF/MF and IS switches as physical checks. After verifying SWITCH and AF Case, evaluate other My Menu tabs separately by field frequency, menu depth, risk of leaving a temporary setting active, and whether Q, a dial, a button, or a physical lens control is already faster.

Verify the approved My Menu tab named **AF Case**:

1. Servo AF
2. Tracking Sensitivity
3. Accel./Decel. tracking
4. Switching tracked subjects

Confirm that Servo AF opens the complete Case 1–4 / Case A selector and does not change AF Operation. Configure Case 1 to the project -1 / +1 values and verify that selecting Case A does not erase them; separately confirm what the camera's Case reset command restores. Confirm that Switching tracked subjects opens the AF4 control with Initial priority, On subject, and Switch subject. Verify the AF Case field route on Wildlife, Birds in Flight, Birds Perched, People, and Sports, including the combined Track / Accel row on custom Case 1 and Case 4 cards and the separate Switching Tracked Subjects value on compatible AF-method cards.

## Exposure and Shutter Follow-Up

- Physically verify the approved EFCS baseline on the owner’s EOS R5: compare tripod sharpness at approximately 1/8–1/60 sec.; inspect EF 50mm f/1.4 bokeh at 1/1000–1/8000 sec.; test indoor LED lighting at Sports shutter speeds; confirm High and High Speed Continuous+ burst behavior; confirm High speed display is enabled and improves regular High Speed Continuous subject-following under supported conditions; and verify the Mechanical 1/200-sec. Pluto/manual-flash Waterdrops setup. Keep the documentation classified as an approved target pending physical verification until these checks are complete.

## Architecture and Validation Improvements

- Generate duplicate control tables from one authoritative machine-readable control source.
- Add validation that rejects the deprecated registered-AF workflow terminology.

### Profile Editor Terminal-free Application

Update **R5 Profile Editor.app** later so it owns the local Profile Editor server without opening Terminal, matching the Camera Lab application lifecycle. Add a clear authenticated **Stop Profile Editor** action that shuts down the server and ends the background app process, show startup or unexpected-stop failures in a macOS alert, retain diagnostic output in the machine-local `Logs/` folder, and preserve **Start Profile Editor.command** as the Terminal-based diagnostic and recovery path.

### Profile Editor Camera Lab Launcher

Add a later launcher-only integration from Profile Editor to the standalone Camera Lab. Preserve Camera Lab as the owner of the Canon EDSDK process, camera session, read-only comparison workflow, checklist state, and future camera-operation safeguards rather than embedding or duplicating those capabilities inside Profile Editor.

The launcher should:

- start Camera Lab only when its loopback service is not already running;
- pass the currently selected **saved** profile so Camera Lab can preselect it, while never sending an unsaved browser draft to the camera workflow;
- open Camera Lab in a separate browser tab and preserve Profile Editor independently;
- detect and report startup, port-conflict, missing-helper, and already-running states clearly;
- depend on Camera Lab's authenticated graceful-stop action so the camera session, EDSDK helper, and local server have one explicit owner and shutdown path; and
- retain Terminal Control-C as the recovery fallback rather than treating browser tab closure as reliable process control.

Do not add deeper Profile Editor embedding unless a later approved requirement needs shared unsaved-draft comparison, a unified camera-write journal, or coordinated backup/write transactions. Because this launcher crosses the isolated Camera Lab/Profile Editor boundary, implement and validate it as an integration checkpoint with the normal source-validation, development-build, and full-validation sequence.

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

### Portable Tracker and Status Migration

Consider a repository-independent way for another photographer to use a released Setup & Verification Tracker on their own computer and carry their local progress into a later tracker revision. Treat this as a demand-dependent enhancement rather than committed work: its value may be limited if the other photographer configures the camera differently enough that the project's checklist requirements, C1-C3 targets, or evidence model are not useful to them.

If pursued, build a small local **Tracker Upgrader**, not a portable copy of the project's Git/YAML synchronization workflow. The user's workbook should remain their sole source of truth. The upgrader must not require this repository, Git, GitHub access, a project clone, or knowledge of the machine-local project workspace.

#### Recommended first release

- Distribute a ZIP containing the current blank `.xlsx` tracker, a local migration utility, and concise instructions.
- Accept an earlier tracker in `.xlsx` format and either bundle the current blank tracker or let the user select it.
- Write a new migrated `.xlsx` file beside a user-selected destination. Never overwrite the earlier tracker or the blank master.
- Keep all processing local and offline; do not upload workbook data or evidence references.
- Support the defined EOS R5 tracker family only. Do not imply that the utility can translate arbitrary camera configurations or independently customized workbook structures.
- For Apple Numbers users, initially require exporting the earlier tracker to `.xlsx`; the migrated `.xlsx` can then be opened in Numbers. Native `.numbers` input/output, automatic conversion, and Mac-only Apple automation are optional later additions.

#### Migration contract

Carry forward only mutable user state:

- Checklist: Status, Test Date, Session ID, Evidence Files, Observation, Next Action, Evidence Class, and Updated in Project.
- C1-C3 Registration: Configured, Read-back, and Notes for each custom mode.
- Sessions: all nonblank session rows and their twelve defined fields.

Match Checklist rows by stable **Test ID**, registration rows by stable **Setting** name, and session fields by their headings. Never match progress by row number. Preserve current definitions, formulas, validations, formatting, menu locations, targets, and dashboard logic from the new blank tracker rather than copying those elements from the old workbook.

Use the hidden Metadata sheet's per-test and per-registration definition fingerprints when available:

- Preserve a completed result only when its recorded definition fingerprint matches the current definition.
- Change an old `Verified` checklist result to `Inconclusive—needs retest` when the definition is missing, older, or different, while preserving its evidence and observation.
- Change affected C1-C3 `Pass` results to `Needs retest` when the registration target fingerprint is missing or different.
- Leave tests newly introduced by the current tracker at their current default state.
- Do not silently discard removed Test IDs or registration settings; list them in the migration report as retired/unmatched items.
- Reject unsupported status or evidence values rather than writing an internally inconsistent workbook.

After migration, show or save a summary containing the source and destination filenames, workbook revisions/fingerprints, counts migrated, new, retired/unmatched, reset, and requiring retest, plus any warnings. A successful run must also confirm that the earlier workbook and blank master were left unchanged.

#### Implementation starting point

Existing project behavior can inform the implementation, but should be extracted or reimplemented without repository dependencies:

- `80 Build/render_camera_setup_tracker.mjs` already reads mutable Checklist, C1-C3 Registration, and Sessions values using stable identifiers.
- `80 Build/verification_status.py` already defines validation, definition-fingerprint comparison, history-preserving retest behavior, and default states.
- `80 Build/spreadsheet_revisions.py` defines the current fingerprint semantics.
- `80 Build/spreadsheet_ooxml.py` demonstrates targeted OOXML changes that preserve the workbook package.

Do not distribute the current `migrate-setup-tracker.sh` workflow unchanged. It writes to the repository's canonical YAML status, rebuilds from repository source files, depends on the bundled `@oai/artifact-tool` runtime, and uses Apple Numbers automation. The direct migration reader in the renderer also needs the fingerprint/retest safeguards before it is safe as an independent upgrader.

Prefer a small, testable migration core with a thin double-clickable wrapper. For maximum workbook fidelity, either make targeted OOXML updates to a copy of the new template or prove through fixture tests that the selected spreadsheet library preserves formulas, tables, validations, hidden metadata, images, styles, freeze panes, and conditional formatting. Packaging and code signing for polished Mac and Windows applications are separate distribution work; begin with one supported platform only if there is demonstrated demand.

#### Acceptance criteria

- Migration works without the repository, Git, GitHub, project YAML files, or private Codex runtime paths.
- A fixture from the immediately preceding tracker revision migrates every supported mutable field correctly.
- Changed definitions invalidate affected passes while retaining evidence and observations.
- New and removed tests are reported correctly, and duplicate or missing stable identifiers stop migration with a useful error.
- The migrated workbook opens without repair warnings and retains formulas, tables, validations, formatting, frozen panes, hidden metadata, and dashboard behavior.
- The tool never overwrites either input and produces a deterministic, reviewable migration report.
- Instructions clearly state that migration preserves recorded progress; it does not adapt project targets to another photographer's preferred camera configuration.

## Macro Refinement

- Refine the Macro profile and guidance as a separately approved content change.
- Review Spot AF, 1-Point AF, manual focus, magnification, peaking, and the role of AF-ON versus AE Lock at macro distances.
- Review stabilization at macro distances for handheld, tripod, and controlled-support workflows.
- Refine focus-bracketing starting points by magnification, subject depth, aperture, increment, and shot count.
- Expand flash-versus-ambient guidance, working-distance considerations, diffraction tradeoffs, and support recommendations.
- Review whether the Canon EF 100mm f/2.8L Macro IS USM needs more explicit lens-specific operating guidance without duplicating the Lens Capabilities appendix.
- Keep advanced high-magnification, MP-E 65mm, automated rail, StackShot, vibration-control, and stacking workflow work as a later phase.
