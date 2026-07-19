# Focus Bracketing & In-Camera Depth Compositing

## Purpose

Focus Bracketing captures a sequence of photographs while the camera automatically moves focus from near to far. It is used when one photograph cannot hold enough depth of field.

Depth Compositing is the process of combining those bracketed photographs into one image where more of the subject appears sharp. Focus Bracketing creates the source frames. Depth Compositing creates the final stacked image.

Multiple focused images often produce better results than stopping down to very small apertures. At f/16, f/22, or smaller, diffraction can soften fine detail even though depth of field increases. A stack shot around f/5.6-f/11 often keeps sharper detail and creates deeper apparent focus.

Use this appendix as a field guide for estimating Focus Bracketing settings with minimal trial and error.

Table of contents:

- [Camera Requirements](#camera-requirements)
- [Every Camera Setting Explained](#every-camera-setting-explained)
- [Number of Shots](#number-of-shots)
- [Focus Increment](#focus-increment)
- [Exposure Smoothing](#exposure-smoothing)
- [Depth Compositing](#depth-compositing)
- [How to Choose Settings](#how-to-choose-settings)
- [Starting Point Tables](#starting-point-tables)
- [Lens x Magnification x Aperture Quick Reference](#lens-x-magnification-x-aperture-quick-reference)
- [Lens Considerations](#lens-considerations)
- [Common Problems](#common-problems)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Decision Trees](#decision-trees)
- [Profile Recommendations](#profile-recommendations)

## What it Does

Focus Bracketing takes multiple frames focused at different distances. The camera begins at the focus point you choose, then steps focus farther away for each frame.

Depth Compositing uses the sharp regions from those frames to create a deeper-focus image. The composite can be made in camera when supported, or later in software such as Canon Digital Photo Professional, Photoshop, Helicon Focus, or Zerene Stacker.

### Camera Requirements

- Compatible lenses: Use Canon AF lenses that support electronic focus control. RF lenses generally work best. Many adapted EF lenses work well, but focus step behavior varies by lens.
- RAW/JPEG behavior: Keep the source images for maximum quality. In-camera depth compositing may create a processed composite file, while external software can use the original RAW frames.
- Tripod recommendations: Use a tripod for macro, product, landscape, architecture, and any stack where framing must stay fixed.
- Handheld limitations: Handheld bracketing can work for casual close-ups, but framing shifts and subject movement increase stacking errors.
- Flash compatibility: Flash can work, but recycle time must keep up with the bracket sequence. Manual flash with consistent power is usually better than variable automatic flash.
- Electronic shutter considerations: Electronic shutter can reduce vibration, but watch for banding under artificial light. Mechanical shutter may be safer when flash is required.
- Image Stabilization considerations: Use IS for handheld stacks. Turn IS off on a solid tripod for static subjects unless the lens/body combination handles tripod detection cleanly.

## How it Works

The camera needs a starting focus point, a focus increment, and a number of shots.

Start focus on the nearest important detail. The sequence moves focus farther away from that point. If you start too deep into the subject, the near edge will never be sharp.

The key relationships are:

- Higher magnification gives shallower depth of field.
- Closer subject distance gives shallower depth of field.
- Wider aperture gives shallower depth of field.
- Smaller focus increments increase overlap between slices.
- More shots increase total depth coverage.

## Advantages

- Creates deeper apparent focus without relying on very small apertures.
- Preserves fine detail by avoiding diffraction-heavy settings.
- Excellent for macro, product photography, flowers, food, small collectibles, and landscapes with close foregrounds.
- Lets the photographer choose sharpness and depth separately.
- External stacking software can produce high-quality results from RAW source frames.

## Disadvantages

- Requires static subjects or very little movement.
- Wind can ruin flowers, insects, and foreground landscape elements.
- Flash recycle time can interrupt the sequence.
- Focus breathing can change framing between frames.
- Too few images leave gaps; too many images waste storage and time.
- In-camera compositing is convenient but less controllable than external software.

## Recommended Uses

Use Focus Bracketing when the subject is static and depth of field is not enough in one frame.

Recommended:

- Macro subjects.
- Water drops.
- Flowers.
- Coins.
- Jewelry.
- Watches.
- Food.
- Electronics.
- Product photography.
- Architecture details.
- Landscapes with close foreground elements.

## When Not to Use

Avoid Focus Bracketing when the subject is moving, the camera cannot be held steady, wind is moving important details, or the flash cannot recycle fast enough.

Avoid it for portraits unless there is a specific static setup. Eye and face movement usually make stacking unnecessary or unreliable.

Avoid using very small apertures and stacking at the same time unless there is a deliberate reason. Diffraction can soften every frame in the stack.

## Every Camera Setting Explained

Canon Focus Bracketing settings control how far the camera travels through the subject and how reliable the overlap is between frames.

### Number of Shots

What it controls: the maximum number of frames the camera will capture in the bracket.

Effect of increasing the value: more depth coverage and less chance that the sequence stops before the far edge is sharp.

Effect of decreasing the value: less time, less storage, and faster processing.

Typical values:

| Subject | Typical Number of Shots |
| --- | --- |
| Very shallow macro | 100-300+ |
| Flowers | 30-80 |
| Products | 20-60 |
| Landscape | 3-20 |
| Architecture | 5-15 |
| Portrait | Rarely needed |

Common mistakes:

- Too few shots leave the far edge soft.
- Too many shots waste time and storage.
- Using one shot count for every subject.

Recommended starting point: choose more shots than you think you need for the first test stack, then reduce after reviewing the last useful sharp frame.

### Focus Increment

What it controls: how far the focus plane moves between frames.

Focus Increment is the most important setting. It does not represent a fixed distance in inches or millimeters. Its real-world effect changes with aperture, magnification, subject distance, and lens behavior.

Relationship to depth of field:

- Wider aperture: shallower depth of field, smaller increment needed.
- Smaller aperture: deeper depth of field, larger increment possible.
- Higher magnification: shallower depth of field, smaller increment needed.
- Closer subject: shallower depth of field, smaller increment needed.
- Greater subject distance: deeper depth of field, larger increment possible.

Small increment:

- More overlap.
- Better stacking reliability.
- More images.
- Slower workflow.

Large increment:

- Fewer images.
- Faster capture.
- Less storage.
- Greater chance of focus gaps.

Practical starting points:

| Subject | Suggested Increment |
| --- | --- |
| 1:1 Macro | 1-2 |
| Insects | 2-3 |
| Flowers | 3-5 |
| Product Photography | 3-5 |
| Food | 4-6 |
| Landscape | 5-8 |
| Architecture | 5-10 |

These are starting points, not fixed rules. If the stack shows bands of softness, reduce the increment. If every frame is nearly identical, increase the increment.

Common mistakes:

- Using a large increment for 1:1 macro.
- Assuming the increment means the same thing with every lens.
- Changing aperture without adjusting increment.
- Starting focus in the middle of the subject instead of the nearest important detail.

Recommended starting point: increment 1-2 for true macro, 3-5 for close product work, and 5-8 for landscape.

### Exposure Smoothing

What it controls: whether the camera attempts to reduce visible exposure jumps across the bracket.

Effect of enabling it: helps make frames more consistent when natural light shifts during the sequence.

Effect of disabling it: keeps controlled studio lighting untouched and avoids unnecessary camera intervention.

Typical values:

- On for changing natural light.
- Usually Off for controlled studio lighting.

Common mistakes:

- Leaving it Off outdoors when clouds are moving quickly.
- Turning it On in a controlled flash setup and expecting it to fix inconsistent flash recycle.

Recommended starting point: On outdoors, Off in studio.

### Depth Compositing

What it controls: whether the camera creates a stacked composite from the bracketed images.

How it works: the camera analyzes sharp areas from each frame, aligns the stack where possible, and blends the sharp regions into one composite.

Advantages:

- Fast review in the field.
- Useful for simple subjects.
- Good for quick documentation.

Limitations:

- Less control over halos and alignment.
- Less retouching flexibility.
- Can struggle with movement and focus breathing.
- External software usually produces better results for serious macro, product, and landscape work.

Common mistakes:

- Treating the in-camera composite as the only file worth keeping.
- Expecting it to fix movement, wind, or poor overlap.

Recommended starting point: use in-camera compositing for quick checks; keep source frames for final stacking.

## Decision Guide

How much depth needs to be covered?

- Small depth: use fewer shots.
- Large depth: use more shots.

How large is the subject?

- Tiny macro subject: small increment and many shots.
- Larger product or landscape: larger increment and fewer shots.

How close am I?

- Very close: smaller increment.
- Farther away: larger increment.

What aperture am I using?

- f/5.6-f/8 macro: small increment.
- f/8-f/11 product or landscape: moderate increment.
- f/16 or smaller: watch for diffraction; stacking may be better at a wider aperture.

Choose Focus Increment.

Estimate Number of Shots.

Review the first stack.

Adjust.

## How to Choose Settings

Use this field process:

1. Decide how much physical depth must be sharp.
2. Check how close you are to the subject.
3. Estimate magnification. The closer the lens is to macro range, the smaller the increment should be.
4. Choose an aperture that balances sharpness and depth. f/8 is a strong starting point for many macro and product stacks.
5. Choose Focus Increment.
6. Choose Number of Shots.
7. Run a test stack.
8. Review the first and last frames.
9. Adjust increment or shot count.

Worked examples:

- Water drops at f/8 with a 100 mm macro lens: start at increment 1 and 150 shots. If the rear edge is still soft, increase shots. If many final frames add no detail, reduce shots.
- Flower at f/8: start at increment 4 and 50 shots. If petal edges show focus gaps, reduce increment to 3 or increase shots.
- Product watch at f/8: start at increment 3 and 80 shots. Use tripod and controlled light. If bracelet links show gaps, reduce increment.
- Landscape with close foreground flowers at f/8: start at increment 5 and 15 shots. If the background is already sharp by frame 8, reduce shots next time.
- Architecture detail at f/8: start at increment 7 and 8 shots. Use more shots only if close foreground detail is included.

## Recommended Settings by Profile

| Profile / Subject | Aperture | Focus Increment | Number of Shots | Notes |
| --- | --- | --- | --- | --- |
| Macro | f/8 | 1-3 | 80-200 | Use tripod when possible |
| Water Drops | f/8 | 1 | 150 | Flash recycle and timing matter |
| Landscape close foreground | f/8 | 5-8 | 5-20 | Start near foreground detail |
| Product | f/8 | 3-5 | 20-80 | Controlled light and tripod |
| Flowers | f/8 | 3-5 | 30-80 | Watch wind |
| Insects | f/8 | 2-3 | 100-200 | Subject movement is the main risk |
| Architecture | f/8 | 5-10 | 5-15 | Usually fewer frames than macro |

## Canon-Specific Notes

Canon R5 Focus Bracketing starts from the current focus position and moves focus farther away. Focus carefully on the nearest important detail before starting the sequence.

If using in-camera Depth Compositing, keep expectations practical. It is useful for fast review and simple stacks, but external software usually provides better alignment, retouching, and artifact control.

Some Canon lenses change framing noticeably as focus shifts. This focus breathing can make stacks harder to align, especially with product and macro subjects.

## Tips

- Start with the nearest important detail.
- Use a tripod for serious stacks.
- Use f/8 as a practical first aperture for many macro/product stacks.
- Review the first and last frame to confirm the full depth range was covered.
- If there are focus gaps, lower the increment or increase shot count.
- If many frames are redundant, raise the increment or reduce shot count.
- Use controlled lighting when possible.
- Protect the subject from wind.
- Leave extra room around the subject for alignment and cropping.

## Common Mistakes

- Starting focus too far into the subject.
- Using too few shots.
- Using an increment that is too large for macro.
- Using f/22 and getting diffraction-soft source frames.
- Letting flash recycle time lag behind the bracket sequence.
- Ignoring subject movement.
- Forgetting focus breathing.
- Keeping hundreds of unnecessary frames.

## Starting Point Tables

### 100 mm Macro Lens

| Subject | Aperture | Increment | Shots |
| --- | --- | --- | --- |
| Water Drops | f/8 | 1 | 150 |
| Insects | f/8 | 2 | 120 |
| Flowers | f/8 | 4 | 50 |
| Coins | f/8 | 3 | 60 |

### Landscape

| Subject | Aperture | Increment | Shots |
| --- | --- | --- | --- |
| Foreground flowers | f/8 | 5 | 15 |
| Mountains | f/8 | 6 | 8 |
| Scenic overlook | f/8 | 7 | 5 |

### Product Photography

| Subject | Aperture | Increment | Shots |
| --- | --- | --- | --- |
| Watches | f/8 | 3 | 80 |
| Jewelry | f/8 | 2 | 100 |
| Electronics | f/8 | 4 | 40 |
| Small collectibles | f/8 | 4 | 50 |

### Lens x Magnification x Aperture Quick Reference

| Lens | Magnification | Aperture | Increment | Starting Shots |
| --- | --- | --- | --- | --- |
| RF 100 Macro | 1:1 | f/8 | 1 | 150 |
| RF 100 Macro | 1:2 | f/8 | 2 | 80 |
| RF 100 Macro | 1:4 | f/8 | 4 | 40 |
| EF 100 Macro | 1:1 | f/8 | 1-2 | 150 |
| EF 100 Macro | 1:2 | f/8 | 2-3 | 80 |
| EF 100-400 @ 400mm | Close focus | f/8 | 3 | 30 |
| RF 24-105 @ 24mm | Landscape | f/8 | 6 | 8 |

## Lens Considerations

RF 100 mm Macro: excellent for high-magnification stacking. At 1:1 or higher, use very small increments and many shots.

EF 100 mm Macro: similar field logic to the RF macro, though focus behavior and breathing may differ when adapted.

EF 100-400L: useful for close telephoto detail, flowers, compressed landscape details, and larger products. Use moderate increments because magnification is lower than true macro but depth can still be shallow at close focus.

Wide-angle lenses: landscapes often need fewer frames. Use Focus Bracketing when the foreground is close and important, not for every scenic view.

Working distance and magnification matter more than lens name. The closer and larger the subject appears, the smaller the increment should be.

## Common Problems

- Missing focus slices: usually caused by an increment that is too large.
- Halo artifacts: usually caused by movement, focus breathing, or difficult high-contrast edges.
- Subject movement: common with insects, flowers, water, and outdoor foregrounds.
- Wind: the main outdoor stacking problem for flowers and foreground landscape elements.
- Flash recycle issues: missed or underexposed frames appear when flash cannot recharge between shots.
- Focus breathing: framing changes as focus moves, especially at close distances.
- Too many images: slows sorting, stacking, storage, and backup.
- Too few images: leaves gaps or stops before the far edge is sharp.
- Diffraction: very small apertures soften every frame before stacking starts.

## Troubleshooting Guide

| Problem | Likely Cause | Recommended Solution |
| --- | --- | --- |
| Missing focus slices | Increment too large | Lower increment and reshoot |
| Far edge still soft | Too few shots | Increase shot count |
| Near edge soft | Started focus too far away | Start on nearest important detail |
| Halo artifacts | Blend struggled with edges | Use external software and retouch |
| Subject movement | Wind or living subject moved | Shield subject, wait, or abandon stack |
| Flash misses frames | Recycle too slow | Lower flash power, raise ISO, or slow sequence |
| Framing changes | Focus breathing | Leave extra crop room and use external software |
| Too many images | Shot count too high | Reduce shots after test stack |
| Diffraction softness | Aperture too small | Use wider aperture and stack more frames |

## Decision Trees

Tripod?

- No: use only for casual stacks; keep shots low and expect alignment issues.
- Yes: continue.

Macro?

- Yes: start increment 1-3 and 80-200 shots.
- No: continue.

Product or flower?

- Yes: start increment 3-5 and 30-80 shots.
- No: continue.

Landscape?

- Foreground close: start increment 5-8 and 5-20 shots.
- No close foreground: Focus Bracketing may not be needed.

Landscape decision tree:

Landscape?

- No: use the subject-specific table.
- Yes: continue.

Foreground close?

- No: single frame may be enough.
- Yes: continue.

Need foreground and background critically sharp?

- No: stop down moderately and shoot one frame.
- Yes: use Focus Bracketing at f/8, increment 5-8, 5-20 shots.

Flash decision tree:

Using flash?

- No: continue normally.
- Yes: test recycle time.

Flash keeps up with every frame?

- Yes: continue.
- No: lower flash power, raise ISO, slow the sequence, or reduce the number of frames.

## Profile Recommendations

| Profile | Recommended Starting Point |
| --- | --- |
| Macro | f/8, increment 1-3, 80-200 shots |
| Water Drops | f/8, increment 1, 150 shots, controlled flash |
| Landscape | f/8, increment 5-8, 5-20 shots when foreground is close |
| Product | f/8, increment 3-5, 20-80 shots |
| Flowers | f/8, increment 3-5, 30-80 shots |
| Insects | f/8, increment 2-3, 100-200 shots |
| Architecture | f/8, increment 5-10, 5-15 shots |

## Cross References

- Profiles: Landscape, Macro, Water Drops, Product, Flowers, Insects, Architecture.
- Settings: focus bracketing, number of shots, focus increment, exposure smoothing, depth compositing, aperture, shutter mode, flash mode.
- Related appendices:
  - [Long Exposure & Night Photography](appendix:long_exposure_night_photography)
  - [Flash Photography](appendix:flash_photography)
  - [R5 Quick Reference](appendix:r5_quick_reference)
