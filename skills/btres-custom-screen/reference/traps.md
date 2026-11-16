# Traps and facts that have bitten before

Each item says how to avoid it. (Adapted from notes by Jim, checked against the unit's code where marked; the car data is from one 2014 S6 4.0T unless noted.)

## Data
- `gaugeVars` **keeps the last value** when a log cell is empty; a variable that has never arrived has no `.v`. Treat a missing value as missing (`--`), and test with an evaluator that holds the last value (a checker that doesn't made the sparse `pu_w` look like 0 and produced a false "+14 psi" theory once).
- `pu_w` (ambient) is logged about 1 row in 9; the unit holds the last value.
- **Engine off**: the ECU reports a fixed `psrg_w` of 1013 hPa: force boost, target and max to 0 when `nmot_w < 300` (see `units.md`).
- **Target pressure**: `psrs_w` first; `pvds_w` caps near 26 psi on the 4.0T and sits at -3 psi at idle.
- `ignadj` ("Ign adj ALS") was never nonzero in about 83,700 rows: don't build indicators on it.
- Oil level percent as `(Oil_lvl - 30) / 35` clamped 0..100 is **uncalibrated** (30 mm = 0 %, 65 mm = 100 %; settled engine-off readings were 55-78 mm): say so on the screen or in the notes.
- "Use the stock variable" is a starting point: check it against real logs before keeping it.
- **Gear (`gangi`)**: 0 is park **and** neutral, 1-6 forward, 7 is reverse; the default stream has no selector-lever column. With the four wheel speeds (`VehV_vWhl*`): `gangi` 0 and all wheels under 3 km/h = P, `gangi` 0 and moving = N, `gangi` 7 under 30 km/h = R, otherwise the digit. (An 8-speed needs its own log; on the 4.0T `gangi` never exceeded 6.)
- **Browser storage doesn't persist on the unit**: `localStorage`, `sessionStorage` and IndexedDB are lost on restart. Use `btScreen.store()` (`app-api.md`) for anything that must survive.
- A variable the screen needs that never shows up in `gaugeVars` on the unit is probably not in the DS1's logged set: see `ds1-logging.md`. Say so in the hand-off.

## Layout
- The unit's footer is **60 px** and hidden only while `settings.showFooterBar` is false. With it on, keep content above y 420 (S-series) / about 620 design px (M1 / X1). Don't move the footer's own buttons or readouts with CSS: units use different footer layouts (`.disableBar`); set `showFooterBar` false instead.
- Screens are `#screen_<position>`; the position changes when screens are reordered. Don't use `screen_N` ids for anything. Give your own elements unique ids (two screens with the same ids collide). The app remaps ids of screens authored at another position, but unique prefixes are safer.
- Editing and re-uploading a **hand-uploaded** screen adds a duplicate on the unit: delete the old copy first (community report, 2025). Installing from the gallery replaces the same screen in place.

## Touch
- **The unit has its own virtual keyboard** (the app's, opened by tapping a text field; see `app-api.md`). There is no browser or system keyboard on the unit, so don't count on one, and you don't need to draw your own keys: the app's keyboard works inside custom screens.
- Vertical swipes that **start within 60 px of the top or bottom screen edge** open the unit's top or bottom menu (a swipe of at least 30 px, within 600 ms, mostly vertical). Horizontal swipes move between screens (scroll-snap). So: keep drag controls out of those edge strips, reject taps that move more than about 24 px, and for a control that must be dragged (a rotating model, a slider), call `stopPropagation()` on its touch events and use `touch-action:none`. (The knock screens' engine rotation does exactly this.)
- Real-unit touch behaviour of new controls is easy to get wrong in a preview: test on the unit, and give any value the driver must enter a sensible default.

## Start-up and recovery (a screen that stays black)
The knock screens were reported black on some units, only the DS1 / bTres logos showing, "randomly". Reproduced in headless Chrome and fixed (`examples/knock-screens/scripts/harden_knock.py`). The causes apply to any screen with code:
- **Your code starts inside `try/catch{}`.** The app evaluates the loader monitor in `personalize()`, which swallows every exception, so a throw during setup is invisible (no log, no message). Don't rely on it failing loudly: test the failure.
- **Set the "already started" flag LAST.** A flag set first (`if(window.X!=='v'){window.X='v'; ...setup...}` or `window.KEY=1,eval(..)`) means that if setup throws once, nothing ever retries. Set it after the last setup statement. Retry a failed start a few times (`make_screen.py` does 3), then give up and **show a message on the screen** ("Engine failed to start, restart your bTres") instead of black. Because a retry re-runs your setup, keep it idempotent (cancel the old `requestAnimationFrame` / remove the old listener before adding the new one, don't stack `setInterval`s).
- **Never commit "attached" before the work that makes it true.** `if(el!==cur){cur=el; ctx=el.getContext('2d'); ...}` leaves `cur` set when `getContext` returned `null` (canvas memory pressure or a lost context on a small unit); every later frame then throws on the null context and nothing retries. Get every context first, `return false` (try again next frame) if one is missing, and assign state only after all of them exist.
- **Isolate the parts of a frame.** One `try/catch` per part (data step, 3D render, 2D draw): a failing WebGL render ran *before* the 2D overlay and blanked the whole screen. A render failure should only turn the 3D off (`glOK=false`). After about a second of failing frames, detach and attach from scratch (new contexts, new renderer), but cap how often (3 times) - rebuilding a WebGL renderer every few frames is worse than a black screen.
- **No square brackets in the loader monitor** (the app's `personalize()` treats `[name]` in monitor text as a variable reference and rewrites it). Build any message element with `createElement` + `textContent` rather than an HTML string, and index with `.item()` / `.at()` or keep that code in the screen's own script.
- **Test the failure, not just the happy path.** The harness for these fixes loads the screen's HTML the way the app does, evals the monitor in a try/catch, and injects: `getContext("2d")` returning `null` for the first calls, an exception during the first setup, WebGL unavailable, setup that always throws. Check the canvases have non-black pixels afterwards and that the old build (control) fails the same test. A test only counts if the control fails.

## Testing
- A test only counts if its control fails: add a wrong version that must be caught (`scripts/test_units.js` and `lint_screen.py --selftest` do). Abort if a checker matches fewer items than expected.
- A plain HTML harness doesn't draw everything the unit does; the preview here is a layout and logic check, not the app.
- Photos lose EXIF; the newest log on a log server can lag.
- For a design pass, have several independent reviews (glanceability, layout, colour/contrast, labels) and apply what two or more agree on.

## Sharing
- No personal seed values (your own best times) in screens you share.
- Say plainly what was and wasn't verified (renderer vs a real unit, which car's logs).
