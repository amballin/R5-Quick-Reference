# Camera Lab User Guide

Camera Lab compares the current Canon EOS R5 with a saved Subject/Profile Card, organizes the work into efficient camera routes, and verifies the result. It starts read-only. Camera changes remain unavailable until you deliberately enable them and approve a reviewed apply plan.

Use the **User Guide** button in the Camera Lab header to reopen this page at any time. For SDK installation, development, physical-write qualification, and detailed evidence rules, use the [USB Camera Configuration advanced reference](usb-camera-configuration.html).

## Start Camera Lab

For routine use, double-click **R5 Camera Lab.app** in the machine-local `Applications` folder. It runs in the background without opening Terminal and opens Google Chrome automatically.

You can also select a saved, unchanged Subject/Profile Card in Profile Editor and choose **Open in Camera Lab**. Camera Lab opens or reuses its window with that profile selected. It still waits for you to connect and scan; the handoff does not change the camera.

Check the header before working:

- **Main** or **Prototype** identifies the checkout supplying the profiles and C1–C3 assignments.
- **Read-only** means Camera Lab can inspect but cannot write camera settings.
- **Simulator** identifies a rehearsal. It cannot change a physical EOS R5.
- The version badge expands to show a diagnostic source hash.

Reopen the app if its Chrome window is missing. Choose **Stop Camera Lab** when finished; it closes the camera session and only the Camera Lab server.

## Choose physical camera or simulator

The ordinary app starts with Canon EDSDK for a physical EOS R5. Use this mode for actual readback, comparison, manual setup, and verified guarded changes.

Choose **Use Simulator** to rehearse without a camera. Confirming the switch ends the current session and restarts the same Camera Lab in simulated mode. Choose **Use Physical Camera** to return to Canon EDSDK. Switching modes clears the current scan and comparison.

Camera Lab never runs the simulator and physical-camera backend at the same time.

## Connect and scan

Before connecting a physical camera:

1. Close EOS Utility and every other application that may control the camera.
2. Connect only the intended EOS R5 with a known-good data-capable USB cable.
3. Turn the camera on in still-photo mode and keep it awake.
4. Use adequate battery power or supported external power.

Choose **Discover cameras**, select the intended EOS R5 if asked, and choose **Connect**. Camera Lab confirms the model, body identifier, firmware, power status, attached lens, EDSDK version, and access mode.

Choose **Scan capabilities** for an initial inventory, or go directly to **Scan & compare** after selecting a profile. **Scan & compare** always performs a fresh scan first. If the camera slept or stopped responding, Camera Lab attempts one clean reconnection and then shows recovery steps if that fails.

## Compare a Subject/Profile Card

Select a **Subject/Profile Card** and choose **Scan & compare**. Saved C1–C3 foundations appear first, followed by the remaining profiles. A label such as **Sports ← C2 (Birds in Flight)** means that Sports starts from the saved C2 foundation.

After the first comparison, selecting another profile automatically rescans and compares it. Permanent reference cards are not offered because they are not complete camera-state targets.

### Choose the equipment context

Camera Lab selects the recognized attached lens when it matches a lens authored for the card. Otherwise it starts with the card's **Primary** lens.

Use **Lens for this comparison** to plan with another authored lens or accessory combination. A selection that differs from the physically attached lens is clearly marked as a planning override. Attach the selected lens and rescan before applying the profile.

When the selected lens has a Mode 1, 2, or 3 switch, **Lens IS mode** offers only supported modes. **Profile default** follows the card target. Read **What this equipment or setting combination changes** because a lens, accessory, IS mode, flash, card, or other dependency can make a setting unavailable, automatic, coordinated, or unnecessary.

### Read the findings

Each setting shows the card target, camera value, status, quickest reviewed access path, and checklist state. Common statuses are:

- **Match** — the readable camera value equals the target.
- **Equivalent** — the value safely satisfies an authored range or equivalent condition.
- **Different** — change the setting and rescan.
- **Manual** or **Unreadable** — the SDK cannot verify the completed action; review it on the camera.
- **Conditional** — choose the requested shooting context before evaluation, or apply the authored guidance manually.
- **Not applicable** — the current equipment or setting context requires no action.

Use **Setup route** for efficient camera setup, **Card order** to follow the card presentation, or **Status** to group discrepancies. Setup route visits physical controls, the Q screen, My Menu tabs, and Canon menu pages in practical order.

The collapsed **Camera capabilities** panel is supporting diagnostic detail. It is not required for an ordinary comparison.

## Complete a read-only setup

The **Setup checklist** can complete a profile without enabling camera writes:

1. For a readable **Different** item, use its displayed access route to change the camera, then choose **Rescan camera**. Only a matching readback completes it as camera-verified.
2. For an eligible Manual, Conditional, or Unreadable item, review or set it on the camera and select **Reviewed/set manually**.
3. Answer any requested shooting-context choice before confirming that finding.
4. Continue until **Unresolved** and **Blocked** both show zero.

Manual confirmations are browser-session evidence for the selected profile, expected target, and connected-camera context. They do not become camera verification or update project source. Choose **Clear manual confirmations** when deliberately starting a new review.

## Maintain or revalidate C1–C3

Expand **C1–C3 Maintenance & Validation** only after an assignment change, reset, restore, or deliberate re-registration. Routine profile comparison does not require this section.

Camera Lab guides this process but does not register C1, C2, or C3 automatically:

1. Disconnect USB and save an independent pre-configuration camera-settings backup to a card.
2. Reconnect and begin from a normal shooting mode, not a recalled C1–C3 state.
3. Keep **Custom shooting mode Auto update** disabled.
4. Choose **Open Cx checklist** for the displayed assignment and complete its comparison.
5. Register the state manually through **Set-up 5 → Custom shooting mode (C1-C3) → Register settings → Cx**.
6. Recall that slot, rescan it, and recheck earlier slots after each later registration.
7. Confirm Auto update is still disabled and save a separate post-configuration backup to a card.

The original EOS R5 does not provide a supported Camera Lab computer-backup button. Pre- and post-configuration backups remain camera-side card operations.

## Rehearse an apply in the simulator

Use the simulator before a physical apply when you want to learn the flow or test stop conditions.

1. Choose **Use Simulator**, connect, select a profile, and choose **Scan & compare**.
2. Choose **Apply this profile to camera**.
3. Confirm the planned lens, flash, cards, recovery information, and optional Camera Setup Essentials evidence.
4. Choose **Review what will change** and read all four groups: **Already correct**, **Camera Lab will change**, **You will change**, and **Needs attention first**.
5. Choose **Start simulator test** only when the plan says it is ready.
6. Follow the stationary **Do this now** card for each remaining manual route group.

The simulator performs and verifies simulator-safe automatic steps, stops at the first problem, and ends with **Profile applied successfully** or **Profile not fully applied**. It cannot change the physical camera.

## Apply a profile to the physical camera

Physical camera changes are a separate, deliberately enabled mode.

1. Start in physical-camera read-only mode and choose **Enable camera changes**.
2. Read the warning and confirm the safe restart. Enabling changes does not itself change a setting.
3. Reconnect, scan, and compare the intended profile.
4. Choose **Apply this profile to camera**.
5. Verify the camera identity, power, attached equipment, lens, flash, cards, and the required recovery-backup filename. A planning lens override must be resolved before apply.
6. Optionally confirm **Camera Setup Essentials is already set** only when that is true. This clears matching Set & Forget targets that Camera Lab cannot read directly; it never overrides contradictory readback.
7. Choose **Review what will change**. Nothing changes during review.
8. Resolve every **Needs attention first** item. Start only when the plan says **Ready to apply**.
9. Approve the separate final confirmation and follow the stationary **Do this now** card.

Already-correct and no-action rows are removed from the work queue. A setting is changed automatically only when exact physical-write evidence authorizes that property and value for the connected body, firmware, and EDSDK context. All remaining work stays manual and is grouped by camera route with one rescan per group.

Do not use **Advanced setup — safely enable additional automatic settings** during routine operation. It is a reversible physical-write qualification workflow for deliberately expanding verified automatic support and requires its own review, approval, test, readback, and restoration.

When finished, read the receipt. **Profile applied successfully** means the reviewed plan completed and verified under its recorded evidence rules. **Profile not fully applied** identifies the stopping point and does not imply completion. Save the required independent post-configuration camera-settings backup, then choose **Return to read-only**.

## Recover from a stop or connection problem

- **Camera slept or timed out:** wake it and use **Reconnect and scan** when prompted.
- **EOS Utility owns the camera:** close EOS Utility and other camera-control software, reconnect, and retry.
- **Equipment or identity changed:** stop the apply attempt, restore the reviewed equipment context, and create a new review.
- **Apply stopped:** read the exact stopping reason. **Continue stopped attempt** first rechecks the recorded identity and context; otherwise stop and plan again.
- **Camera Lab window is missing:** reopen **R5 Camera Lab.app** to recover it.
- **Camera Lab is unresponsive:** stop it, disconnect the camera if needed, and reopen the app. Never force a prior reviewed plan through a changed session.

Camera Lab keeps guarded-run records and manual confirmations machine-locally. It does not commit, push, publish, edit profile source, or update the verification tracker itself. In Profile Editor's **Review & Build** workspace, **Camera Lab evidence** can deliberately promote exact evidence from a completed physical EDSDK session only into the matching current C1–C3 setting's configured result. Simulator and incomplete sessions are excluded, nothing is selected automatically, and read-back, registration, operational-test, backup, Canon-capability, and owner-confirmed evidence remain unchanged.

## Get more help

Use the [USB Camera Configuration advanced reference](usb-camera-configuration.html) for Canon EDSDK location, development commands, capability details, physical-write evidence, safety qualification, and troubleshooting depth. Use the [Profile Editor User Guide](editor-user-guide.html) to change profile targets, lens choices, C1–C3 foundations, My Menu, and shared baseline settings.
