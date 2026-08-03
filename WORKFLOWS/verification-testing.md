# On-Camera Verification Testing

Use this workflow for EOS R5 setup checks, C1–C3 registration and read-back, physical-control behavior, shutter tests, and the final promotion of supported results. The detailed test requirements remain in the [EOS R5 On-Camera Verification Checklist](../90%20Testing/EOS%20R5%20On-Camera%20Verification%20Checklist.md).

## Open the correct working tracker

The preferred command safely creates the machine-local tracker only when no working copy exists, reports whether it matches the last YAML import, and opens the newest Numbers or Excel copy:

```bash
./80\ Build/scripts/open-verification-working-copy.sh
```

With the default local-workspace location, use either direct link:

- [Open the Numbers testing tracker](../../Canon%20Camera%20Reference%20Local/Verification/EOS%20R5%20On-Camera%20Verification%20Tracker.numbers)
- [Open the Excel testing tracker](../../Canon%20Camera%20Reference%20Local/Verification/EOS%20R5%20On-Camera%20Verification%20Tracker.xlsx)

If the direct link is missing or `PRS_LOCAL_WORKSPACE` points elsewhere, use the helper. Never record test progress in the blank publishable Setup master.

## Prepare the camera and session record

Work in Checklist Sequence order and use one Session ID for each camera session. Record the date, tester, firmware, battery, card, lenses, flash or trigger, evidence location, and notes in Sessions.

Before changing the camera:

1. Record anything currently stored in C1, C2, and C3.
2. Save the complete starting camera configuration to the card and record its filename.
3. Work from a normal shooting mode rather than C1, C2, or C3.
4. Set Auto update set. to Disable.

## Complete setup and registration in order

1. Configure My Menu: SWITCH and My Menu: AF Case, the complete C1-aligned operational baseline shown by Camera Defaults and Camera Setup Essentials, and the physical controls.
2. Save the first checkpoint and mark that Checklist row Backup-Settings.
3. In a normal mode, read back the complete C1-aligned default state, register it to C1, leave it, recall it, and read back every target setting again.
4. Repeat the complete configure, register, and read-back cycle for C2 Birds in Flight.
5. Do not begin C3 until C1 and C2 both recall correctly. Then complete C3 Landscape.
6. Save the second Backup-Settings checkpoint after all three registrations have been read back.
7. Perform the operational control, transition, joystick, shutter, burst, lighting, bokeh, and flash or trigger tests required by the Checklist.
8. Complete the final C1–C3 and control read-back, confirm Auto update remains disabled, and save the verified final camera configuration to the card.

Do not register a custom mode until every setting in that mode's complete target column has been checked. C1–C3 registration rows require separate Configure and Read Back results; both must pass against the current target.

## Record results and evidence

For each Checklist row, update Status, Test Date, Session ID, Evidence Files, Observation, Next Action, Evidence Class, and Updated in Project as applicable.

Use the status that describes the observed result:

- Verified only when the camera produced the exact Expected Result and the observation is complete and unambiguous.
- Failed—needs correction when the observed behavior clearly differs from the requirement.
- Inconclusive—needs retest when the evidence cannot support a clear pass or fail.
- Blocked when the required test cannot presently be performed.
- Backup-Settings only for the two prescribed checkpoint saves.

Evidence files remain machine-local or in an owner-controlled evidence location; the tracker and YAML store filenames or references. Preserve the completed tracker and supporting images until applicable project evidence states have been updated.

The importer validates allowed statuses and current definition fingerprints, but it cannot judge whether an observation is genuinely sufficient. Selecting Verified is the tester's confirmation that the current Expected Result passed. If a test definition or C1–C3 target later changes, its earlier pass is preserved in history and changed to Inconclusive—needs retest or Needs retest.

## Understand completion and project updates

The Dashboard counts Verified rows plus the two prescribed Backup-Settings rows toward phase completion. There is no separate Complete Checklist status.

A camera result may become owner-confirmed project state only when its row has Project Update? = Yes, Status = Verified, and complete unambiguous evidence. Update the named project files only after that review, then set Updated in Project to Yes. Approved targets remain pending physical verification until this promotion is complete.

## Close and import after testing

Save and close Numbers or Excel before importing:

```bash
./80\ Build/scripts/import-verification-status.sh
```

The importer chooses the most recently modified local Numbers or Excel tracker, matches stable Test IDs and registration settings, records history, and updates `90 Testing/eos_r5_verification_status.yaml`. Finish Day stops if a local tracker changed after its last successful import.

## Continue on the other Mac

On the first Mac:

1. Close the tracker and import its status.
2. Use Finish Day and do not switch until the repository is clean and synchronized.

On the second Mac:

1. Run Preflight.
2. If the clean clone is behind, run `git pull --ff-only`, then rerun Preflight.
3. Run the open helper; it creates that Mac's tracker from the synchronized YAML when needed.

Do not copy the active tracker through iCloud as the normal handoff. Git-tracked YAML is authoritative and prevents an older workbook from replacing newer status. iCloud may carry evidence photographs and other supporting files.

## Recover from an interrupted handoff

If unimported workbook changes remain on the first Mac, return to that Mac, close the tracker, import it, and complete Finish Day before working on the second Mac. Do not rebuild a tracker over unimported changes and do not choose a workbook solely because its timestamp appears newer.
