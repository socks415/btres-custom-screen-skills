# Design guidelines for bTres screens

Observed in screens the bTres community has shared (a read of about 130 photos, November 2026) and from building screens for the units. Treat the numbers as starting points, not rules. Test on a real unit in the car's light.

- **Glanceable**: a driver reads it for a second. Cap a screen near **12 readouts** (the median was 10; screens with 22-48 were read as unreadable). Put the rest on a second screen.
- **Text size**: the smallest text should be at least about **3% of the screen height** (1.5% text was flagged as illegible): roughly 15 px on 480 high, 24 design px on M1 / X1 (it is scaled by 0.7). Main readouts much larger (150-210 px in the boost screens made for the units).
- **One unit system per block**: don't mix bar, MPa, ms and degrees in one cluster. Follow the unit's settings (`units.md`).
- **Readable names**: show "Boost target", not `psrs_w`; no raw ECU names in labels or alerts.
- **Colour**: red text on black or maroon was the top legibility complaint. Pair red with a light fill, or keep red for large values. Never use colour alone for ahead/behind or good/bad: add words (AHEAD / BEHIND) or signs. A colour language that worked: amber = cold / not ready, green = go, gold = target, outlined pill with a red dot = recording.
- **Selectors** (map buttons and similar): label every button and show the active one with a lamp or fill, not colour alone; identical-looking toggles hide the active map.
- **Min / max captions** under ring gauges are standard but usually tiny: print them at label size or larger.
- **Boost dial pattern** (from a dial that reused the unit's own dial face): draw the peak (MAX) and target (TGT) marks after the dial's translucent fill, draw scale numbers after every ring, don't make a needle thin or place it inside a bar, and make the target mark a separate element rotated to the target on the dial's scale. A hit-target flash that blinks green for a couple of seconds then stays green read well.
- **Footer**: with the footer bar on, keep content above about y 420 (S-series) / about y 620 design px (M1 / X1); with it off the whole height is free but the footer's readouts are gone.
- **Don't leave seed values** (your own best times and similar) in a screen you share.

Adapted from notes by Jim (the group-photo observations are his, one reader's judgement).
