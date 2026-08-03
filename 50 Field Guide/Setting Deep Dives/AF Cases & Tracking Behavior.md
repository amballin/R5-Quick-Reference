# AF Cases & Tracking Behavior

## Purpose

Explain how Canon EOS R5 Servo AF tracking controls change camera response, and provide a repeatable way to correct tracking problems without changing several interacting settings at once.

## What it Does

Servo AF continuously updates focus while autofocus is active. AF Cases tune how the camera responds when subject distance, speed, direction, or visibility changes. They have no active effect in One-Shot AF or Manual Focus.

These controls work alongside AF Method, Subject Detection, Eye Detection, the selected AF area, and Switching tracked subjects. They do not replace initial subject acquisition or accurate framing.

## How it Works

| Servo AF Case parameter | Lower / locked-on behavior | Higher / responsive behavior |
|---|---|---|
| Tracking Sensitivity | Stays with the current subject through brief obstacles | Transfers focus more quickly when a new target enters the active area |
| Accel./Decel. Tracking | Assumes steadier motion | Responds more strongly to abrupt starts, stops, and speed changes |

Canon AF Cases combine starting values for those two parameters:

| Case | Canon purpose | Default parameters | Practical meaning |
|---|---|---|---|
| **Case 1** | Versatile multi-purpose setting | Tracking Sensitivity **0**; Accel./Decel. **0** | Neutral behavior for general, predictable movement |
| **Case 2** | Continue tracking while ignoring possible obstacles | Tracking Sensitivity **–1**; Accel./Decel. **0** | Holds the current subject longer through branches, players, or brief framing errors |
| **Case 3** | Instantly focus on subjects entering the AF points | Tracking Sensitivity **+1**; Accel./Decel. **+1** | Quickly accepts a new or closer subject; useful for intentional target succession, but more likely to leave the original subject |
| **Case 4** | Subjects that accelerate or decelerate quickly | Tracking Sensitivity **0**; Accel./Decel. **+1** | Follows abrupt starts, stops, and speed changes without deliberately favoring a new subject |
| **Case A (Auto)** | Automatically adapt to subject movement | Both parameters controlled automatically | Broad starting point for varied or dynamic movement when no repeatable failure calls for a specialized Case |

Cases 1–4 may be tuned manually. Case A controls both parameters automatically. Treat every Case as a starting behavior, then diagnose the observed failure before adjusting an individual parameter or choosing a specialized Case.

Subject Detection identifies People, Animals, or Vehicles. Eye Detection can refine priority to an eye when the subject and AF method support it. The AF area still controls where the camera can begin or continue looking.

**Switching tracked subjects is separate from the AF Case.** It controls whether compatible subject-aware AF methods retain the initially chosen subject or transfer detection priority to another recognized subject. Changing it does not change Tracking Sensitivity or Accel./Decel. Tracking.

## Advantages

- A locked-on response can hold focus through branches, players, or momentary obstructions.
- A responsive setting can make intentional target changes faster.
- Increased Accel./Decel. Tracking can help with erratic or rapidly changing motion.
- Subject and Eye Detection can reduce the need to keep a small AF point precisely on a face or eye.

## Disadvantages

- Over-responsive settings can jump to backgrounds, foreground obstacles, or another subject.
- Overly locked-on settings can cling to the wrong subject after an intentional change.
- Aggressive acceleration response may make steady, predictable subjects less consistent.
- Detection can fail when subjects are small, blocked, low contrast, or outside the useful AF area.
- Changing several controls together makes it difficult to identify which change helped.

## Recommended Uses

Use Servo AF for subjects moving toward, away from, or across the camera. Enable the appropriate subject type when recognition is reliable. Use Face + Tracking when the camera should follow a recognized subject across the frame; use a smaller or expanded area when you need more control over initial acquisition.

Start with the profile's documented Case. Leave its parameters at the Canon defaults until a repeatable failure appears. Tune the failure, not the subject label alone.

### Quick Field Access

- The fastest normal route is to recall the complete registered profile: **C1 Wildlife uses Case A**, **C2 Birds in Flight uses Case 4**, and **C3 Landscape stores Case A but does not actively use it while C3 remains in One-Shot AF**.
- For a temporary change, open **My Menu: AF Case > Servo AF**, select the Case, and press SET. The direct route remains **AF3 > Servo AF characteristics**.
- **My Menu: AF Case** contains **Servo AF**, **Tracking Sensitivity**, and **Accel./Decel. tracking** in that order. Here, Servo AF opens the Case selector; it does not change AF Operation.
- Use Tracking Sensitivity or Accel./Decel. tracking only to correct a repeatable response problem. Change one parameter at a time and restore the profile's starting Case if the experiment does not help.
- Keep **Auto update set.: Disable** so a temporary Case change inside C1–C3 does not silently rewrite the registered starting profile.

## When Not to Use

Use One-Shot AF or Manual Focus for static subjects when focus should not continue updating. When the camera repeatedly chooses the wrong object, use Spot AF, 1-Point AF, or Expand AF Area for more deliberate acquisition; Subject to Detect: None removes category priority but does not disable automatic main-subject selection. Do not use a highly responsive configuration merely because the subject is fast; speed changes and target switching are separate problems.

## Decision Guide

| Observed problem | First adjustment | Also check |
|---|---|---|
| Focus jumps to a branch, player, or foreground obstacle | Try Case 2 or move Tracking Sensitivity toward locked-on | AF area may be too broad |
| Camera is slow to accept an intentional new subject | Try Case 3 or move Tracking Sensitivity toward responsive | Release and reacquire AF if needed |
| Focus lags abrupt starts, stops, or speed changes | Try Case 4 or increase Accel./Decel. Tracking one step | Shutter speed and initial AF acquisition |
| Camera abandons the intended detected subject | Reduce subject switching | Confirm correct subject type and AF area |
| Camera will not transfer to a new recognized subject | Increase subject switching cautiously | Confirm the new subject is recognizable |
| Eye Detection chooses the wrong person or animal | Reduce switching or use a controlled AF area | Initial point placement and subject size |
| Background is selected before the subject | Start with 1-Point or Expand AF Area | Reacquire on visible subject detail |

After each adjustment, test the same kind of pass or movement again. If the result does not improve, return that control to its prior value before changing another.

## Recommended Settings by Profile

| Profile | Recommended Case | Adjustment trigger |
|---|---|---|
| Wildlife / C1 | **Case A (Auto)** | Try Case 2 through vegetation; Case 4 for repeatable abrupt movement |
| Birds Perched | **Case A (Auto)** | Try Case 2 when branches or brief framing errors steal focus |
| Birds in Flight / C2 | **Case 4** | Try Case 2 with obstructions; Case 3 only when intentionally acquiring successive birds at different distances |
| People | **Case A (Auto)** | Try Case 2 through crossings; when the camera changes faces, adjust Switching tracked subjects rather than blaming the Case alone |
| Sports | **Case 4** | Try Case 2 through player crossings; Case 3 when deliberately transferring among successive players or vehicles |
| Travel | **Inactive in the One-Shot starting profile** | Use Case A if Travel is temporarily changed to Servo AF |
| Landscape, Macro, Fireworks, Waterdrops | **Inactive** | Retain the documented One-Shot AF or Manual Focus approach |

## Canon-Specific Notes

- AF Cases and subject detection affect different parts of the focusing decision: Cases tune response over time; detection helps identify what to prioritize.
- Canon calls the automatic option **Case A** and displays **AUTO** for it; this guide labels it **Case A (Auto)** for clarity.
- Cases 1–4 combine editable Tracking Sensitivity and Accel./Decel. Tracking values. Case A sets both automatically.
- On the original EOS R5, Subject to Detect takes effect with Face + Tracking, Zone AF, and Large Zone AF. Spot AF, 1-Point AF, and Expand AF Area use deliberately positioned AF points instead.
- Face + Tracking gives detection broad freedom. 1-Point and Expand AF Area provide more control over where acquisition begins.
- Eye Detection requires Face + Tracking and works best when the eye is large and distinct enough to recognize.
- Back-button AF can make it easier to stop tracking immediately without changing AF Operation.
- Menu wording and available controls can vary with firmware and shooting context; confirm the displayed R5 options before relying on a saved configuration.
- Canon reference: [EOS R5 Servo AF Characteristics](https://cam.start.canon/en/C003/manual/html/UG-04_AF-Drive_0100.html).
- Canon reference: [EOS R5 Customizing AF Functions](https://cam.start.canon/en/C003/manual/html/UG-04_AF-Drive_0110.html).

## Tips

- Begin with defaults and change one parameter at a time.
- Test against the real background, not only against a clean wall or sky.
- Separate an acquisition failure from a tracking failure: first get focus onto the intended subject, then judge whether Servo AF stays with it.
- Use short, repeatable trials and inspect sequences at useful magnification.
- Save a proven action configuration to an appropriate custom shooting mode only after it is reliable.
- Photograph or record the original Case before a field experiment, and restore the profile's starting Case afterward.

## Common Mistakes

- Treating an AF Case as a complete replacement for AF Method and subject selection.
- Treating Switching tracked subjects as a third AF Case parameter.
- Increasing every response control for fast action.
- Blaming tracking behavior when shutter speed caused motion blur.
- Expecting Eye Detection to recover a subject that was never acquired.
- Testing multiple changes at once.
- Leaving a specialized configuration active for unrelated subjects.

## Cross References

- Profiles: Birds Perched, Birds in Flight, People, Sports, Wildlife.
- Settings: Servo AF, AF Method, Tracking Sensitivity, Accel./Decel. Tracking, Subject Detection, Eye Detection, subject switching.
- Related guides:
  - [R5 Quick Reference](appendix:r5_quick_reference)
  - [Custom Controls & Menus, Back-Button AF & Dial Strategies](appendix:back_button_af_custom_button_strategies)
