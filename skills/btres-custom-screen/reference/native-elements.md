# The unit's built-in element types (`textData`, `radialNeedle`, `meter`, `text`)

This skill builds screens whose logic is JavaScript (`make_screen.py`). Screens made with the editor's built-in elements work differently, and you may need to read or change one. How the unit evaluates them (checked against `personalize()` in the unit's `betterThan.js`):

- A screen is `{settings, elements}`. Elements are drawn in file order (z order = file order). Keep element indexes stable: blank an element instead of deleting it.
- **`textData` / `radialNeedle` / `meter`** have a `monitor` formula. Every `[var]` is replaced with `gaugeVars[var].v`. If the resulting text contains any of `+ - * \ ( )` it is run through `eval`; a numeric result is rounded with `toFixed(decimals)`, a string stays as is.
  - So a monitor with none of `+ - * \ ( )` is **never evaluated**: wrap it, e.g. `(calcBoost?'psi':'bar')`.
  - A numeric-looking *label* gets re-rounded (a tick label `'1.5'` showed `2`): end labels that must keep their text/decimals with U+200B (zero-width space) so the result is not a number.
  - **min/max elements** (`minMax: min|max` plus a threshold expression): the monitor **must return a number**. A string (or a U+200B ending) gives NaN that sticks. A two-finger tap resets min/max.
  - `[var]` for a column the car never sends stays raw and breaks the whole formula: read `gaugeVars` directly with a fallback instead: `gaugeVars.x ? gaugeVars.x.v : fallback`. The formula runs in page scope (`gaugeVars`, `window`, `calcBoost`, `switchF` are globals).
  - `preText` / `postText` must be strings (empty is fine) or the unit prints `undefined`.
- **`text`** elements get a width but **no height**: size what you draw inside them with their own CSS/SVG. Use pixel sizes, not percentages.
- **`gaugeVars` keeps the last value** when a log cell is empty. A variable that has never arrived has no `.v`.
- **Geometry** (`x`, `y`, `width`, `height`) must be **numbers**. Strings (`"14"`) are ignored by the unit and the element draws at 0,0. `scripts/lint_screen.py` checks this.
- The built-in elements run from the unit's monitor loop (about every 100-200 ms) only for the screen that is showing, so long-running code should start from the hidden `<img onerror>` that `make_screen.py` writes, not from a monitor.
- Element ids are `element_<position>_<n>` inside `#screen_<position>`. Screens authored at another position are remapped by the app on load, but ids can still collide between screens: give your own elements unique id prefixes.

Adapted from notes by Jim; verified against the unit's evaluation code, not on a unit.
