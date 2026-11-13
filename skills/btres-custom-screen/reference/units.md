# Units: follow the device's settings

**Rule: build one screen that follows the unit's own settings**, not separate metric and imperial files. The unit has two unit settings and its stock gauges obey both. Screens read them from `btScreen.settings` (see `app-api.md`):

| setting | `true` | `false` |
|---|---|---|
| `mapBoost` ("Swap Map to Boost") | show **BOOST in psi**, gauge pressure (above ambient) | show **MAP in bar**, absolute |
| `ctoF` ("Switch C to F") | degrees **F** (and mph) | degrees **C** (and km/h) |

There is no speed setting: follow `ctoF` (F = mph, C = km/h). Fuel pressures have no stock setting: follow `mapBoost` (psi vs bar) and label them. Why not two files: owners flip these settings and expect screens to follow, two files double the building and testing, and a screen that disagrees with the unit's own footer looks broken.

`reference/units-snippet.js` has the tested helpers (`btUnits.boost()`, `target()`, `temp(col)`, `speed(col)`, `kpa(col)`, `labels.*`, `pressureMax()`); copy what you need into `screen.js`. `scripts/test_units.js` tests them in all four modes with hand-worked values and controls that must fail.

## Rules
- **Internals stay metric** (hPa, kPa, deg C, km/h); convert only at the display edge.
- **Labels follow the setting too**: never hard-code `psi`, a degree-F sign, `mph` or `bar` in static text. `scripts/lint_screen.py` warns about it.
- **Scale ranges follow the unit**: a boost bar that runs 0..30 in psi mode must run 0..3 in bar mode (the stock gauges use `30` or `3`). Needle maximums, peak arcs, redlines and colour thresholds too. Compare thresholds in the internal unit (Celsius, hPa) so they don't move when the setting flips.
- Test **all four modes** (psi/bar x F/C), and the empty state.
- Constants: 1 bar = 14.5037738 psi; hPa x 0.0145037738 = psi; hPa / 1000 = bar; kPa x 0.145037738 = psi; kPa / 100 = bar; F = C x 9/5 + 32; mph = km/h / 1.609344.

## Boost math
- **psi mode**: `(absolute - ambient) x 0.0145037738`, **floored at 0**. Idle shows about -10 psi of real vacuum; the stock gauge clamps to 0, so floor the readout, target, max, needle and peak arc too.
- **bar mode**: **absolute** `absolute / 1000` (about 0.3 at idle, 1.0 engine off, about 3.0 at 29 psi). Not "gauge bar" (psi / 14.5): that reads about 1 bar low next to every stock screen.
- **Columns**: boost is `psrg_w` (else `psr_w` on cars that send that instead); target is `psrs_w` first (it reached 28-30 psi in the V8 test pulls), `pvds_w` second (it caps near 26 psi on that car and sits at -3 psi at idle). The RS3 / TT RS list has only `pvds_w` for the target. Ambient is `pu_w`, logged only about 1 row in 9 (the unit holds the last value), else 1013.25.
- **Engine off**: the ECU reports a fixed `psrg_w` of 1013 hPa, which is about +0.6 psi against a real ambient of 971 hPa. When `nmot_w` is below 300, treat the reading as ambient so boost, target and max read 0. Skip that rule if the car sends no `nmot_w`.
- Most US owners run psi (`mapBoost` on), but the bar path ships and must be tested.

## Where this comes from
Adapted from notes shared by Jim (read from the unit's own code and 4.0T logs of a 2014 S6). The constants and the `mapBoost` / `ctoF` behaviour match the unit's code. The column choices were checked on one V8 car only; other cars (R8 5.2, RS3) were not checked on real logs.
