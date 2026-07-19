# Long Exposure & Night Photography

## Purpose

Explain the Canon R5 choices that matter for long exposures, night photography, fireworks, waterfalls, light painting, Milky Way images, and other tripod-based low-light work.

This appendix is the single source of truth for Long Exposure Noise Reduction (LENR). Profiles should reference this appendix rather than duplicating LENR explanations.

Table of contents:

- [Long Exposure Noise Reduction (LENR)](#long-exposure-noise-reduction-lenr)
- [Processing Time](#processing-time)
- [AUTO Setting](#auto-setting)
- [Decision Guide](#decision-guide)
- [Recommended Settings by Profile](#recommended-settings-by-profile)
- [Cross References](#cross-references)

## What it Does

Long exposure settings control how the R5 handles multi-second captures, sensor heat, tripod stability, shutter behavior, stabilization, and processing delays.

### Long Exposure Noise Reduction (LENR)

Long Exposure Noise Reduction performs a second exposure, called a dark frame, immediately after the original exposure with the shutter closed.

The camera compares the dark frame with the original exposure and removes or reduces:

- Hot pixels.
- Thermal noise.
- Amp glow.
- Fixed-pattern sensor noise.

LENR is different from High ISO Noise Reduction. High ISO Noise Reduction targets high-sensitivity noise; LENR targets artifacts created or revealed by longer exposure times.

## How it Works

The camera uses dark frame subtraction. If the original exposure is 30 seconds, the R5 records the main image, then spends roughly another 30 seconds recording a dark frame. The dark frame contains sensor noise patterns but no scene detail, allowing the camera to subtract those artifacts.

During the dark-frame exposure, the camera cannot take another photograph.

### Processing Time

LENR effectively doubles capture time.

| Exposure | Camera Busy Time |
| --- | --- |
| 5 sec | 10 sec |
| 15 sec | 30 sec |
| 30 sec | 60 sec |
| 1 minute | 2 minutes |
| 5 minutes | 10 minutes |

The camera may display `BUSY` while the dark frame is being captured or processed.

## Advantages

- Reduces hot pixels.
- Reduces thermal noise.
- Reduces fixed-pattern sensor noise.
- Helps control amp glow.
- Improves single long exposures.
- Is especially useful on warm nights.
- Produces cleaner night photographs directly from the camera.

## Disadvantages

- Doubles shooting time.
- Makes the camera unavailable during processing.
- Increases battery usage.
- Can cause missed opportunities.
- Is not efficient for image stacking workflows.
- Can interrupt fireworks, lightning, time-lapse, and changing-light sequences.

## Recommended Uses

Turn LENR On for important one-off long exposures where maximum single-frame image quality is more important than speed.

Recommended On:

- Single night landscapes.
- Single cityscapes.
- Single waterfall exposures.
- Single light-painting images.
- Single fireworks exposures.
- Single Milky Way exposures.
- Any important one-off long exposure where maximum image quality is desired.

For exposures under a few seconds, the benefit is usually minimal. LENR becomes more valuable as exposure duration and sensor heat increase.

## When Not to Use

Turn LENR Off for workflows where many images will be captured or combined later.

Recommended Off:

- Focus bracketing.
- Exposure bracketing.
- Time-lapse.
- Astrophotography stacking.
- Star trails.
- Multiple waterfall exposures.
- Burst long exposures.
- Waterdrop flash work.
- Any workflow where many images will be combined later.

Post-processing software generally provides better results for stacked images than applying LENR to every frame in camera. If shooting many long exposures, disable LENR and remove hot pixels during post-processing or with a planned dark-frame workflow.

### AUTO Setting

AUTO lets the camera decide when to apply Long Exposure Noise Reduction.

AUTO is suitable for general photography and travel, but the user may experience unexpected processing delays. If timing matters, choose On or Off deliberately instead of leaving the decision to the camera.

## Decision Guide

Long exposure?

- No: Off or Auto.
- Yes: continue.

More than one exposure?

- Yes: Off.
- No: continue.

Maximum single-frame image quality required?

- Yes: On.
- No: Auto.

If timing matters more than maximum single-frame cleanup, choose Off.

## Recommended Settings by Profile

| Photography Type | Recommended Setting |
| --- | --- |
| Normal | Auto |
| Travel | Auto |
| Landscape (single exposure) | On |
| Landscape (multiple exposures) | Off |
| Night Landscape | On |
| Milky Way (single image) | On |
| Milky Way (stacking) | Off |
| Star Trails | Off |
| Waterfalls | Off |
| Light Painting | On |
| Fireworks (single exposure) | On |
| Fireworks (sequence) | Off |
| Focus Bracketing | Off |
| Wildlife | Off |
| Birds in Flight | Off |
| Sports | Off |
| Waterdrops | Off |

## Canon-Specific Notes

On the Canon EOS R5, Long Exposure Noise Reduction can affect RAW and JPEG workflows because the correction is applied by the camera, not merely stored as a post-processing suggestion.

The project baseline should avoid forcing LENR On. Use Auto for general/travel workflows when convenience matters, On for single critical long exposures, and Off for stacked or repeated-capture workflows.

LENR is separate from High ISO Noise Reduction. Do not use LENR as a general high-ISO cleanup tool.

## Tips

- For exposures under a few seconds, the benefit is usually minimal.
- LENR is most valuable for long exposures where sensor heating becomes significant.
- If shooting many long exposures, disable LENR and remove hot pixels during post-processing.
- Expect the camera to display `BUSY` while capturing the dark frame.
- Decide before the sequence starts; changing mid-shoot can make files inconsistent.
- Watch battery life during long exposure sessions.

## Common Mistakes

- Leaving LENR On after a night shoot.
- Using LENR for waterdrop flash work.
- Confusing LENR with High ISO Noise Reduction.
- Missing fireworks or lightning because the camera is busy processing.
- Applying LENR to every frame in a stacking workflow.
- Forgetting that processing delay scales with exposure length.

## Cross References

- Profiles: Camera Defaults, Fireworks, Landscape, Macro, Travel, Waterdrops.
- Settings: `image.long_exposure_noise_reduction.value`, shutter speed, drive mode, ISO, flash mode.
- Related appendices:
  - [Focus Bracketing & In-Camera Depth Compositing](appendix:focus_bracketing_depth_compositing)
  - [Flash Photography](appendix:flash_photography)
  - [R5 Quick Reference](appendix:r5_quick_reference)
