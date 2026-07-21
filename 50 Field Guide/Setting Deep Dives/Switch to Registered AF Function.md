# Switch to Registered AF Function

## Purpose

Explain what **Switch to registered AF function** does on the original Canon EOS R5, why it initially sounds more useful than it may be in the field, and how it compares with two related custom-control strategies:

- a second **Metering and AF start** button with its own detailed AF settings; and
- **Register/recall shooting function**, which can recall a broader temporary shooting state.

This document is intentionally standalone and not yet linked from the project manifest, profiles, or quick reference. It preserves the research and open questions for later testing and enhancement.

## What it Does

**Switch to registered AF function** temporarily changes selected autofocus behavior while its assigned button is held. Releasing the button returns the camera to its normal AF behavior.

A typical idea is:

| Normal AF behavior | Temporary registered behavior |
|---|---|
| Face + Tracking | Spot AF or 1-Point AF |
| Servo AF | Servo AF |
| Normal Servo response | Different Tracking Sensitivity or Accel./Decel. Tracking |

This can help when subject or eye tracking selects branches, grass, another player, or the background instead of the intended subject.

The important limitation is ergonomic: **Switch to registered AF function changes AF behavior, but it is not itself the normal AF-start command**.

With the project's currently recommended control pattern:

- **AF-ON** starts autofocus;
- **AE Lock** holds the registered AF override; and
- the shutter takes the picture.

That can require the photographer to operate **AF-ON, AE Lock, and the shutter at the same time**. Because AF-ON and AE Lock are adjacent thumb controls, this is awkward and may be unreliable during fast action.

## How it Works

### Normal and temporary states

The camera normally follows the active AF settings. For example:

- Servo AF
- Face + Tracking
- Subject to Detect: Animals
- Eye Detection: Enable
- Case 2

While the assigned override button is held, the camera applies the AF items selected in that button's detailed configuration. A useful temporary state might be:

- Spot AF for a stationary bird behind branches; or
- 1-Point AF or Expand AF Area for a moving subject behind grass.

Release the button and the normal state returns immediately.

### Setup path

1. Open **MENU > Custom Functions > C.Fn3 > Customize buttons**.
2. Select the desired physical button.
3. Assign **Switch to registered AF func.**
4. Press **INFO** when the detail option is shown.
5. Select only the AF properties that should be overridden.
6. Configure the temporary values and confirm the assignment.
7. Test the function while looking through the viewfinder.

Canon's EOS R5 manual confirms that functions marked with the INFO symbol have advanced settings, but it does not explain the registered-AF workflow in enough detail to remove the need for an on-camera test.

### What it should not be confused with

**Switch to registered AF function** is not:

- a Custom Shooting Mode such as C1, C2, or C3;
- a registered AF-point position;
- **Eye Detection AF** assigned directly to a button; or
- **Register/recall shooting function**.

These features solve different problems and have different button behavior.

### Subject Detection and Eye Detection

Do not assume this function literally switches **Subject to Detect** or **Eye Detection** off on the original R5 unless those items are visible and selected in the camera's detail screen.

Choosing Spot AF, 1-Point AF, or Expand AF Area can still produce the desired practical result because those methods do not use subject and eye tracking in the same way as Face + Tracking. The underlying Subject Detection and Eye Detection menu values may remain unchanged.

On the original R5, **Subject to Detect: None** is not an off switch. It removes People, Animals, or Vehicles priority while the camera still determines a main subject automatically from detected subject information. Subject to Detect does not apply when the AF method is Spot AF, 1-Point AF, or Expand AF Area.

This distinction should be verified from the camera before the project publishes a definitive list of registerable items.

### The three-control problem

Using the existing proposed layout would require:

1. Hold **AE Lock** to invoke the registered AF behavior.
2. Hold **AF-ON** to start and continue autofocus.
3. Press the shutter to take the picture.

This is possible, but it is not a naturally comfortable field action. Both rear controls compete for the right thumb, and the combination becomes harder while panning, supporting a long lens, or reacting quickly.

Moving the override to the depth-of-field preview button can distribute the work across different fingers, but it still requires three simultaneous controls. It improves reach, not conceptual simplicity.

## Register/Recall Shooting Function

### What it is

**Register/recall shooting function** is a separate, broader custom-button assignment. Instead of recalling only a limited AF behavior, it is intended to recall a selected temporary shooting state while the assigned button is used.

Depending on the items offered by the original R5's INFO detail screen, that state may include a combination of exposure, drive, metering, and AF-related choices. The photographer selects which items participate rather than blindly replacing every camera setting.

The EOS R5 manual confirms that **Register/recall shooting func.** is available as a still-photo custom-button assignment and that INFO opens advanced settings. However, Canon's original-R5 manual does not document the detailed item list or activation behavior clearly enough.

### Why it may be more practical

On Canon implementations where the recall button also activates the registered AF operation, the workflow becomes:

1. Hold the recall button to apply the alternate state and focus.
2. Press the shutter to take the picture.
3. Release the recall button to return to normal.

That is a two-control workflow, not the three-control workflow created by pairing **Switch to registered AF function** with a separate AF-ON button.

Canon's current AF-setting guidance demonstrates this pattern on newer EOS bodies: normal AF is started with AF-ON, while a button assigned to **Register/recall shooting function** starts AF with the recalled behavior. This is useful evidence about Canon's design intent, but it is not proof that every detail behaves identically on the original EOS R5.

### What must be verified on the original R5

Before recommending Register/Recall for this project, test and record:

- Whether pressing the assigned button starts metering and autofocus.
- Whether the recalled settings apply only while the button is held.
- Whether releasing the button restores every participating setting.
- Which settings appear in the INFO detail screen.
- Whether AF Operation, AF Method, Tracking Sensitivity, and Accel./Decel. Tracking are available.
- Whether Subject to Detect and Eye Detection are available.
- Whether shutter speed, aperture, ISO, metering mode, and drive mode are available.
- Whether the registered AF-point position can participate.
- Which physical buttons can accept the assignment.
- Whether behavior changes by exposure mode, AF operation, or firmware version.

### Suggested verification procedure

1. Photograph every page of the original R5's **Register/recall shooting function** INFO detail screen.
2. Register an unmistakable test state, such as Spot AF plus a visibly different shutter speed.
3. Keep shutter-button half-press assigned to **Metering start** so AF activation can be identified unambiguously.
4. Hold only the recall button and observe whether the lens focuses.
5. While holding it, take a picture and inspect the recorded exposure and AF behavior.
6. Release it and confirm that the camera returns to the previous settings.
7. Repeat after powering the camera off and on.
8. Repeat in the exposure and AF modes used by Birds in Flight, Birds Perched, Wildlife, and Sports.

Until this test is completed, Register/Recall should be described as **promising but not yet verified on the project's camera**.

## A More Practical Alternative: Dual Back-Button AF

For the specific goal of switching temporarily from tracking to a precise AF area, the simplest R5 solution may not be either registered function.

Instead, assign a second rear button to **Metering and AF start**, then use its INFO detail screen to give that button a different AF behavior.

Example:

| Control | Behavior |
|---|---|
| **AF-ON** | Metering and AF start with normal Face + Tracking behavior |
| **AE Lock** | Metering and AF start with Servo AF plus Spot AF, 1-Point AF, or Expand AF Area |
| **Shutter** | Metering and capture, without autofocus |

Field operation becomes:

- Hold **AF-ON** and press the shutter for normal tracking; or
- hold **AE Lock** and press the shutter for the precise alternate AF behavior.

Only one rear AF button is pressed at a time. Each AF button both selects its behavior and starts autofocus.

This is the most promising workflow for birds, wildlife, and sports because it preserves back-button AF without requiring AF-ON and AE Lock simultaneously.

It should be tested on the camera before replacing the current recommendation, but Canon's custom-button design and published back-button AF guidance support this general approach.

## Advantages

### Switch to registered AF function

- Temporarily changes several supported AF properties together.
- Returns automatically when the button is released.
- Leaves the normal AF setup untouched.
- Can provide quick access to a more precise AF area.

### Register/Recall Shooting Function

- Potentially recalls a broader combination of AF and shooting settings.
- May provide a more ergonomic two-control workflow if the assigned button starts AF.
- Can be useful when the temporary situation also needs a different shutter speed, drive mode, or exposure behavior.

### Dual back-button AF

- Each rear button starts autofocus directly.
- Requires only one thumb button at a time.
- Is easier to learn and operate while following action.
- Keeps normal tracking and precision AF immediately available.

## Disadvantages

### Switch to registered AF function

- Can require three simultaneous controls with back-button AF.
- Competes for the same thumb used by AF-ON.
- Does not automatically mean that Subject Detection or Eye Detection has been disabled.
- A small AF area may be hard to keep on fast subjects.

### Register/Recall Shooting Function

- Is poorly explained in the original EOS R5 manual.
- Can change more settings than intended if configured carelessly.
- Requires documentation and testing so the photographer remembers what is recalled.
- Original-R5 activation behavior and available items still need camera verification.

### Dual back-button AF

- Uses the AE Lock button for autofocus instead of exposure lock.
- Requires remembering which rear button invokes which AF behavior.
- May offer fewer non-AF overrides than Register/Recall.

## Recommended Uses

- A perched bird partly hidden by branches.
- Wildlife moving behind grass, reeds, or brush.
- A player surrounded by other people.
- A subject that Face + Tracking repeatedly fails to select.
- Rapid movement between a normal tracking view and a deliberately placed AF area.

For these uses, test **dual back-button AF first**. Consider Register/Recall when the alternate situation also requires exposure or drive changes. Reserve **Switch to registered AF function** for a button position and grip that make its hold behavior genuinely comfortable.

## When Not to Use

- Do not adopt a three-control combination merely because the feature sounds powerful.
- Do not change the Camera Buttons recommendation until the physical workflow has been tested with the intended lens.
- Do not register numerous settings before documenting which ones are active.
- Do not use Spot AF for erratic motion that cannot be held under a very small point.
- Do not assume behavior from an EOS R5 Mark II or EOS R1 is identical to the original EOS R5.
- Do not use a critical shoot as the first test.

## Decision Guide

| Need | Best starting approach | Reason |
|---|---|---|
| Normal tracking plus a second precise AF method | Dual back-button AF | The selected rear button also starts AF. |
| Temporary AF-response change only | Switch to registered AF function, if ergonomically reachable | Narrower scope, but may require a separate AF-start control. |
| Temporary AF plus exposure or drive changes | Register/Recall Shooting Function, after verification | Broader recalled state may consolidate several changes. |
| Completely different persistent shooting setup | C1, C2, or C3 | Better for a full mode change that should remain active. |
| Temporarily invoke eye-detection autofocus | Dedicated Eye Detection AF assignment | More direct than recalling unrelated settings; it is not a persistent menu toggle. |

## Recommended Settings by Profile

These are test candidates, not approved project settings.

| Profile | Normal AF button | Alternate AF button or recall candidate |
|---|---|---|
| **Birds in Flight** | Face + Tracking, Animals, Servo AF | Expand AF Area with Servo AF |
| **Birds Perched** | Face + Tracking, Animals, Servo AF | Spot AF or 1-Point AF for branches |
| **Wildlife** | Face + Tracking, Animals, Servo AF | 1-Point AF or Expand AF Area for grass and brush |
| **Sports** | Face + Tracking, People, Servo AF | 1-Point AF for crowded scenes |
| **People** | Face + Tracking, People | 1-Point AF when the wrong face is selected |

For an alternate Case 4-like response, Canon defines Case 4 as Tracking Sensitivity 0 and Accel./Decel. Tracking +1. Register or override the underlying values only if those controls appear in the selected button's detail screen.

## Canon-Specific Notes

- The original EOS R5 uses the AF-method name **Face + Tracking**. **Whole Area AF** is terminology used on newer bodies.
- Canon's R5 manual lists both **Switch to registered AF func.** and **Register/recall shooting func.** under Customize buttons.
- The R5 manual says to press INFO for functions that offer advanced settings.
- The manual confirms availability, but it does not adequately document the detailed registered items or field operation.
- Canon's newer AF guides are useful for understanding design intent, but model-specific behavior must be verified on the original R5.
- The camera's firmware version should be recorded with all verification screenshots.

## Tips

- Evaluate the physical button combination with the actual long lens before evaluating the feature in theory.
- Start with one obvious alternate AF method and leave all other override items unchanged.
- Use Spot AF mainly for stationary or predictable subjects behind small obstructions.
- Use 1-Point AF or Expand AF Area for subjects that are moving.
- If two buttons provide Metering and AF start, make their roles simple: tracking versus precision.
- Photograph every detail screen so the configuration can be reproduced after a reset.
- Recheck all registered behaviors after firmware updates or clearing customized controls.

## Common Mistakes

- Confusing **Switch to registered AF function** with **Register/recall shooting function**.
- Assuming the registered-AF button starts autofocus.
- Expecting one thumb to hold AF-ON and AE Lock comfortably during fast action.
- Assuming Subject Detection and Eye Detection are explicitly switched off.
- Calling Face + Tracking "Whole Area AF" on the original R5.
- Treating a named Servo Case as though the name itself is necessarily recalled.
- Registering too many settings and forgetting which ones change.
- Copying an R5 Mark II workflow without testing it on the original R5.

## Cross References

No internal project links have been added yet.

Official source material retained for later verification:

- [Canon EOS R5: Custom Function Setting Items](https://cam.start.canon/en/C003/manual/html/UG-08_Custom_0030.html)
- [Canon EOS R5: Servo AF Characteristics](https://cam.start.canon/en/C003/manual/html/UG-04_AF-Drive_0100.html)
- [Canon USA: Back-Button Autofocus Explained](https://www.usa.canon.com/learning/training-articles/training-articles-list//back-button-autofocus-explained)
- [Canon EOS R1 AF Setting Guide: Shooting Through a Net](https://cam.start.canon/en/C018/guide/html/AF-05_CaseStudy_0130.html) - useful for design intent only; not evidence of identical original-R5 behavior.

## Verification Status

Confirmed from Canon's original EOS R5 documentation:

- Both custom-button assignments exist.
- Both are still-photo functions.
- INFO opens advanced settings for supported assignments.
- Switch to registered AF function is available on a limited set of controls.
- Case 4 uses Tracking Sensitivity 0 and Accel./Decel. Tracking +1.

Not yet confirmed directly on the project's EOS R5:

- The complete selectable-item list for each registered function.
- Whether Register/Recall starts AF on the original R5.
- Whether Register/Recall is hold-to-recall and release-to-restore in every configuration.
- Whether Subject Detection and Eye Detection can participate.
- The most comfortable physical button assignment with the owner's lenses and grip.
