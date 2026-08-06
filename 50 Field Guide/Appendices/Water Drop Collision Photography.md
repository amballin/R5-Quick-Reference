# Water Drop Collision Photography

## Purpose

Provide a repeatable method for photographing water-drop collisions with the Pluto Trigger, including measured drop sizes, useful timing calculations, multiple-flash placement, reflection control, and manual focus when a soap bubble crosses the optical path.

This guide separates values that can be calculated from values that must be measured. The calculations are starting estimates. Real collisions remain sensitive to valve behavior, liquid pressure, viscosity, surface tension, temperature, pool depth, and small alignment changes.

## What it Does

The working setup uses the Pluto Trigger to control the valve-open duration and the timing between drops. In the owner's current connection, Pluto fires the camera and the camera fires the flashes. The short flash burst, rather than the 1/200-second shutter speed by itself, freezes the collision.

Pluto also documents a dark-room arrangement in which it opens the camera exposure by infrared, releases two drops, and fires a flash directly through its camera/flash port. That arrangement normally uses an exposure around 1–2 seconds. These two connection methods are not interchangeable timing models: camera shutter latency matters much more when the camera must open at the collision instant.

## How it Works

### Measurements and symbols

Use one unit system throughout a calculation.

| Symbol | Meaning |
| --- | --- |
| `H` | Vertical distance from the detached drop to the undisturbed pool surface |
| `D` | Pool depth |
| `P1`, `P2`, `P3` | Valve-open command for drops 1, 2, and 3, in milliseconds |
| `V1`, `V2`, `V3` | Measured volume of drops 1, 2, and 3 |
| `L1`, `L2`, `L3` | Delay between a valve command and actual drop detachment |
| `g` | Gravitational acceleration, approximately `9.81 m/s²` |
| `u` | Effective upward speed of the first rebound jet or column |
| `y` | Height above the undisturbed pool surface |
| `t` | Time measured from the first valve command |

Measure `H` to the liquid surface, not to the bottom of the tray. Keep the valve height, nozzle, liquid level, temperature, camera position, and pool fill constant while calibrating.

### Free-fall estimate

Ignoring air resistance, a detached drop released from height `H` reaches the surface after:

`t_fall = sqrt(2H / g)`

Its estimated impact speed is:

`v_impact = sqrt(2gH)`

Example: with `H = 0.50 m`, `t_fall` is about `0.319 s` and impact speed is about `3.13 m/s`. Add the measured valve-to-detachment delay `L1` when comparing this with a Pluto command or flash delay.

### Peak rebound height

Pool depth, pool width, drop size, and fall distance do **not** uniquely determine the maximum rebound height. Energy is lost to the crater, crown, waves, satellite drops, viscosity, and air. Surface tension and the shape of the collapsing cavity redirect only part of the impact energy upward. A shallow bottom or nearby wall can also alter that collapse.

The dependable measurement is a timing sweep or a calibrated scale placed in the collision plane:

1. Disable drops 2 and 3.
2. Keep drop 1 size fixed.
3. Sweep the flash delay in 5 ms steps until the rising column nears its top.
4. Repeat that range in 1 ms steps.
5. Read peak height from a ruler or grid placed at the collision plane, correcting for image magnification if the ruler is offset from that plane.

If the first-drop impact time and peak time have been measured, a simple ballistic approximation can estimate height. Let `tau` be the time from impact to the top of the rebound:

`u ≈ g × tau`

`y_max ≈ 0.5 × g × tau²`

This treats the top of the jet like a freely moving particle. It is useful for planning but is not a fluid-dynamics prediction. The jet continues changing shape and may pinch off, so direct measurement from the image is more trustworthy.

Test pool depth empirically. Increase `D` while holding everything else fixed; once peak height and shape stop changing meaningfully, the bottom is no longer an important variable for that setup. Do the same with tray width if reflected waves or wall proximity may be influencing the crown.

### Calibrating drop size for drops 1, 2, and 3

Valve-open milliseconds are a control setting, not a volume. Flow may be nonlinear near the valve's opening threshold, and pressure changes with liquid level. Calibrate each requested pulse width.

1. Prime the valve and establish the normal working liquid level and pressure.
2. Put a tared cup on a scale with at least 0.01 g resolution.
3. Release `N` identical drops at one pulse width; use 50–100 drops when practical.
4. Weigh the collected liquid.
5. Repeat at least three times and record the mean and range.

For collected mass `m`, liquid density `rho`, and `N` drops:

`V_drop = m / (rho × N)`

For water near room temperature, `rho` is close to `1.00 g/mL`, so grams collected are approximately milliliters collected. For a water/glycerin or soap mixture, measure or look up the mixture density rather than assuming pure water.

To express the measured volume as an equivalent spherical diameter:

`d = cube_root(6V / pi)`

Use `V` in cubic millimeters to obtain `d` in millimeters. One microliter equals one cubic millimeter.

Example: 50 drops with a total mass of 2.00 g give approximately `0.040 mL`, `40 microliters`, or `40 mm³` per drop. The equivalent spherical diameter is about `4.24 mm`.

Build a calibration table for each liquid:

| Command | Drop role | Repeats | Mean mass per drop | Volume | Equivalent diameter | Range/notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `P1` | Drop 1 |  |  |  |  |  |
| `P2` | Drop 2 |  |  |  |  |  |
| `P3` | Drop 3 |  |  |  |  |  |

Calibrate drop 1, drop 2, and drop 3 settings independently by disabling the other drops when the controller permits. Then run the complete sequence and weigh its total output as a consistency check. Closely spaced commands can behave differently from isolated commands because the valve and fluid column have not completely settled.

The current official Pluto Droplet guide documents two drops. If the installed app, firmware, or a separate valve controller offers a third drop, apply the same measurement method to it and verify how that controller defines the third delay—absolute from drop 1 or relative to drop 2.

### Calculating the delay for a collision

The following model provides a first estimate. It does not replace a timing sweep.

The first drop detaches at `L1` and impacts at approximately:

`t_impact1 = L1 + sqrt(2H / g)`

After impact, approximate the rising first column as:

`y1(t) = u(t - t_impact1) - 0.5g(t - t_impact1)²`

For a chosen collision height `y_c` below the measured `y_max`, the time on the rising branch is:

`t_collision = t_impact1 + [u - sqrt(u² - 2g y_c)] / g`

A later falling drop needs approximately this much time to travel from the nozzle to `y_c`:

`t_flight_to_y = sqrt[2(H - y_c) / g]`

Therefore the starting command delay for drop 2 is:

`Delay2 ≈ t_collision - L2 - t_flight_to_y`

For a third drop intended to reach a chosen later collision at time `t_collision3` and height `y_c3`:

`Delay3_absolute ≈ t_collision3 - L3 - sqrt[2(H - y_c3) / g]`

If the controller defines the third setting as an interval after drop 2 rather than an absolute delay from drop 1:

`Delay3_relative = Delay3_absolute - Delay2`

The square root in the rebound equation requires `u² ≥ 2g y_c`; otherwise the selected height exceeds the estimated peak. In practice, use the measured first-drop peak and choose a collision slightly below it, where the rising column has enough width and repeatability.

### Practical Pluto calibration sequence

1. Stabilize valve pressure, liquid temperature, nozzle height, pool depth, and framing.
2. Enable only drop 1 and choose its measured volume.
3. Find first impact and peak rebound with Pluto's flash-delay calibration. The official guide suggests beginning with 5 ms increments and then refining.
4. Estimate drop 2 delay with the equations or begin near the observed peak timing.
5. Sweep drop 2 delay in 2–5 ms steps; after a collision appears, refine in 1 ms steps.
6. Change only one variable at a time. A change to drop volume changes impact energy and usually changes the correct delay.
7. Add drop 3 only after the drop 1/drop 2 collision is stable. Decide whether it should thicken the column, strike the umbrella, or create a later secondary collision, then sweep its delay separately.
8. Calibrate the final flash delay last, because the desired photographed shape may occur after the physical collision begins.

Record successful trials rather than relying on app values alone:

| Trial | Liquid/temperature | `H` / `D` | `P1` / `P2` / `P3` | Delays | Flash delay | Flash powers | Result |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  |

## Advantages

- Measured drop volumes make different pulse widths and liquids comparable.
- A calculated delay narrows the search range before fine calibration.
- Low-power manual flashes provide short, repeatable bursts and fast recycling.
- A fixed manual-focus plane avoids autofocus latency and focus hunting.
- A separate candidate card and detailed guide keep field instructions concise.

## Disadvantages

- The rebound is a fluid interaction, so a simple ballistic model cannot predict its complete shape.
- Valve detachment latency and drop volume can change with pressure, temperature, liquid level, and viscosity.
- Multiple flashes add reflections, radio/optical synchronization issues, and exposure variables.
- A curved soap film is a variable optical element and can make the collision appear shifted or distorted.
- Very small timing changes can produce substantially different shapes.

## Recommended Uses

- Repeatable two-drop crowns, columns, mushrooms, and umbrellas.
- Three-drop experiments when the installed controller explicitly supports a third timed release.
- Comparison of liquid recipes after each recipe has its own volume and timing calibration.
- Multiple-light setups where key, rim, and background illumination need independent placement.

## When Not to Use

Do not rely on the equations alone when the valve is sputtering, the reservoir pressure is changing, the tray is visibly affected by earlier waves, or the soap bubble shape changes between frames. Do not use autofocus during the sequence. Do not use a long camera-controlled shutter exposure in a bright room where ambient light will record unwanted motion or background detail.

## Decision Guide

| Observation | Best next action |
| --- | --- |
| First rebound height varies | Stabilize valve pressure and pool; verify drop 1 mass before changing timing |
| Column is repeatable but drop 2 misses | Sweep only drop 2 delay, first coarsely and then in 1 ms steps |
| Collision occurs too low | Release drop 2 slightly earlier, or reduce the intended collision height calculation |
| Collision occurs after the column collapses | Release drop 2 earlier; confirm drop 1 peak timing again |
| Frame is sharp without a bubble but soft through it | Treat the bubble as the cause; reform it, refocus after forming it, or remove it from the optical path |
| Reflections show the flash head or diffuser | Move the reflected angle away from the lens and flag the source; do not begin by reducing exposure |
| Motion has a bright trail | Reduce ambient light or shorten the effective flash duration with lower manual power |
| Image is dark at low flash power | Move lights closer, improve diffusion efficiency, add a flash, open toward f/8, then raise ISO modestly |

## Recommended Settings by Profile

| Profile | Starting values | Notes |
| --- | --- | --- |
| Waterdrops | Manual, 1/200, f/8–f/11, ISO 100, Mechanical shutter, Manual Focus, Single Shot, stabilization Off | Use when Pluto fires the camera and the camera fires synchronized flashes |
| Waterdrops—direct-flash dark-room method | Manual exposure around 1–2 seconds, low ambient light, Manual Focus | Pluto opens the exposure and directly fires the flash; confirm EOS R5 remote compatibility and exact wiring |

Begin each flash around 1/32 power when using two or three nearby flashes. Adjust distance and modifier efficiency first. Use 1/16 when more exposure is needed; use 1/64 when shorter duration or faster recycle matters more. These are project starting recommendations, not verified duration specifications for every flash model.

## Canon-Specific Notes

- The current Waterdrops profile uses Mechanical shutter at 1/200 as a conservative camera-triggered flash-sync starting point.
- Disable High Speed Sync for this setup unless a separately tested connection requires it; ordinary manual flash is more power-efficient.
- Manual Focus, Single Shot, and disabled stabilization remove avoidable timing and framing variation on a fixed support.
- At close distances, f/22 increases depth of field but also adds diffraction. ISO 3200 adds noise and reduces highlight headroom. Start near f/8–f/11 and ISO 100, then solve exposure with flash distance, diffusion efficiency, the number of flashes, and modest ISO increases.
- Confirm that every flash fires after the shutter is fully open. A dark band indicates a sync or timing problem, not a drop-delay problem.

## Tips

### Multiple-flash placement

- Use manual power on every flash so output does not change with framing or liquid highlights.
- Start with a diffused key light 30–45 degrees behind and to one side of the collision.
- Put a weaker fill on the opposite side, or use a white reflector before adding another powered light.
- Light a translucent background from behind with a separate flash when a clean colored field is wanted.
- Keep all flashes at power levels that recycle completely before the next Pluto sequence.
- Trigger secondary flashes with a tested radio receiver or manual optical slave. Confirm that no E-TTL preflash fires a slave early.

### Avoiding reflections

Water and soap films are specular: they reflect the source at the mirror angle. Move the light or diffuser until that reflected angle misses the lens. A larger diffuser makes a broader, smoother highlight but does not remove it.

Use black flags beside and above the set to block views of flash heads, room lights, bright walls, and the camera. Keep the lens shaded. Place flashes behind side diffusion panels rather than aiming bare heads toward the water. Small controlled highlights often help define the curved drop; the goal is to shape them, not necessarily eliminate every highlight.

A circular polarizer on the lens may reduce some glare but cannot remove reflections from every curved surface orientation. For stronger control, place linear polarizing film over every flash in the same orientation and rotate the lens polarizer toward cross-polarization. Expect substantial light loss and test for uneven color or stress patterns in plastic trays and acrylic panels.

### Focus through a soap bubble

A soap film is thin, but a curved bubble behaves as a changing lens. If the lens focus ring has not moved but the collision looks shifted after the bubble is formed, the apparent focus change is refraction through the bubble, not autofocus.

For the most repeatable result:

1. Mount the camera and lock composition.
2. Form the bubble in its final position and shape.
3. Put a thin rod, needle tip, printed edge, or spare drop exactly at the intended collision plane inside or behind the bubble.
4. Use magnified Live View to focus on that target.
5. Switch the lens to manual focus if needed and tape the focus ring.
6. Remove the target without touching the camera, tray, bubble support, or focus ring.
7. Recheck after every re-formed bubble because its curvature may differ.

Depth of field can hide a small apparent shift, but f/22 is not the first solution. Increase working distance or reduce magnification slightly, keep the sensor plane parallel to the desired collision plane, and begin near f/8–f/11. If the changing bubble must remain between lens and subject, perfect repeatability is not physically guaranteed; reform and refocus, or redesign the angle so the collision is not photographed through the curved film.

## Common Mistakes

- Assuming `10 ms` produces a known or universally repeatable drop volume.
- Measuring nozzle height to the tray bottom instead of the liquid surface.
- Changing several variables between trials.
- Calculating rebound height as if all impact energy becomes vertical motion.
- Ignoring valve-to-detachment latency.
- Confusing an absolute third-drop delay with an interval measured from drop 2.
- Letting earlier waves remain in the tray before the next sequence.
- Using E-TTL or a preflash that triggers optical slaves prematurely.
- Pointing bare flashes toward the camera-facing side of the water.
- Focusing before forming a curved soap bubble, then expecting the apparent plane to stay fixed.
- Using f/22 and ISO 3200 when flash placement, power, and working distance have not been optimized.

## Cross References

- Profile: Waterdrops.
- Related guides:
  - [Flash Photography](appendix:flash_photography)
  - [R5 Quick Reference](appendix:r5_quick_reference)
- Authoritative Pluto references:
  - [Pluto Trigger manual—Droplet mode](https://plutotrigger.com/pages/manuals)
  - [Pluto Valve user guide](https://plutotrigger.com/pages/valve-guide)
