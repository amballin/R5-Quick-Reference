# AF Cases & Tracking Behavior

## Purpose

Explain how Canon EOS R5 Servo AF tracking controls change camera response, and provide a repeatable way to correct tracking problems without changing several interacting settings at once.

## What it Does

Servo AF continuously updates focus while autofocus is active. AF Cases and their parameters tune how the camera responds when subject distance, speed, direction, visibility, or priority changes.

These controls work alongside AF Method, Subject Detection, Eye Detection, and the selected AF area. They do not replace initial subject acquisition or accurate framing.

## How it Works

| Control | Lower / locked-on behavior | Higher / responsive behavior |
|---|---|---|
| Tracking Sensitivity | Stays with the current subject through brief obstacles | Transfers focus more quickly when a new target enters the active area |
| Accel./Decel. Tracking | Assumes steadier motion | Responds more strongly to abrupt starts, stops, and speed changes |
| Subject switching | Resists transferring detection priority | Moves priority more readily to another recognized subject |

Canon AF Cases combine starting values for tracking behavior. Treat a Case as a starting point, then diagnose the observed failure before adjusting an individual parameter.

Subject Detection identifies People, Animals, or Vehicles. Eye Detection can refine priority to an eye when the subject and AF method support it. The AF area still controls where the camera can begin or continue looking.

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

Leave tracking behavior near its default until a repeatable failure appears. Tune the failure, not the subject label alone.

## When Not to Use

Use One-Shot AF or Manual Focus for static subjects when focus should not continue updating. When the camera repeatedly chooses the wrong object, use Spot AF, 1-Point AF, or Expand AF Area for more deliberate acquisition; Subject to Detect: None removes category priority but does not disable automatic main-subject selection. Do not use a highly responsive configuration merely because the subject is fast; speed changes and target switching are separate problems.

## Decision Guide

| Observed problem | First adjustment | Also check |
|---|---|---|
| Focus jumps to a branch, player, or foreground obstacle | Move Tracking Sensitivity toward locked-on | AF area may be too broad |
| Camera is slow to accept an intentional new subject | Move Tracking Sensitivity toward responsive | Release and reacquire AF if needed |
| Focus lags abrupt starts, stops, or direction changes | Increase Accel./Decel. Tracking one step | Shutter speed and AF acquisition |
| Camera abandons the intended detected subject | Reduce subject switching | Confirm correct subject type and AF area |
| Camera will not transfer to a new recognized subject | Increase subject switching cautiously | Confirm the new subject is recognizable |
| Eye Detection chooses the wrong person or animal | Reduce switching or use a controlled AF area | Initial point placement and subject size |
| Background is selected before the subject | Start with 1-Point or Expand AF Area | Reacquire on visible subject detail |

After each adjustment, test the same kind of pass or movement again. If the result does not improve, return that control to its prior value before changing another.

## Recommended Settings by Profile

| Profile | Starting behavior | Adjustment trigger |
|---|---|---|
| Birds in Flight | Servo AF, Animals, Eye Detection when reliable; default tracking response | Lock on more through branches; raise Accel./Decel. for abrupt flight changes |
| People | Servo AF for movement, People and Eye Detection; default response | Reduce subject switching in groups when the camera changes faces |
| Sports | Servo AF, appropriate people/vehicle detection; default response | Lock on through players crossing; raise Accel./Decel. for stop-start action |
| Wildlife | Servo AF, Animals and Eye Detection when reliable; default response | Lock on through vegetation; use a smaller area when detection chooses the background |

## Canon-Specific Notes

- AF Cases and subject detection affect different parts of the focusing decision: Cases tune response over time; detection helps identify what to prioritize.
- On the original EOS R5, Subject to Detect takes effect with Face + Tracking, Zone AF, and Large Zone AF. Spot AF, 1-Point AF, and Expand AF Area use deliberately positioned AF points instead.
- Face + Tracking gives detection broad freedom. 1-Point and Expand AF Area provide more control over where acquisition begins.
- Eye Detection requires Face + Tracking and works best when the eye is large and distinct enough to recognize.
- Back-button AF can make it easier to stop tracking immediately without changing AF Operation.
- Menu wording and available controls can vary with firmware and shooting context; confirm the displayed R5 options before relying on a saved configuration.

## Tips

- Begin with defaults and change one parameter at a time.
- Test against the real background, not only against a clean wall or sky.
- Separate an acquisition failure from a tracking failure: first get focus onto the intended subject, then judge whether Servo AF stays with it.
- Use short, repeatable trials and inspect sequences at useful magnification.
- Save a proven action configuration to an appropriate custom shooting mode only after it is reliable.

## Common Mistakes

- Treating an AF Case as a complete replacement for AF Method and subject selection.
- Increasing every response control for fast action.
- Blaming tracking behavior when shutter speed caused motion blur.
- Expecting Eye Detection to recover a subject that was never acquired.
- Testing multiple changes at once.
- Leaving a specialized configuration active for unrelated subjects.

## Cross References

- Profiles: Birds in Flight, People, Sports, Wildlife.
- Settings: Servo AF, AF Method, Tracking Sensitivity, Accel./Decel. Tracking, Subject Detection, Eye Detection, subject switching.
- Related guides:
  - [R5 Quick Reference](appendix:r5_quick_reference)
  - [Custom Controls, Back-Button AF & Dial Strategies](appendix:back_button_af_custom_button_strategies)
