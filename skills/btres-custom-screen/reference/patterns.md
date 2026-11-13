# Patterns and gotchas from the example screens

Notes taken from the example screens that ship in `examples/` (**Pull Lab**: pull verdict, boost/lambda/fuel graphs and per-cylinder knock; **Live Dyno**: estimated whp/torque curve with pull comparison), plus an image-based artwork dial screen that is not included. The knock screens in `examples/knock-screens/` use the same screen format.

## Screen structure they share
- `settings.showFooterBar:false`, then `elements:[ one big "text" element 1920x480 at x=0,y=0, one "textData" element ]`.
- The text element's `text` is HTML (absolutely-positioned divs, canvases, optional inline SVG, images as `data:` URIs). Its logic rides along in a hidden `<img src="data:," onerror="...">` that `eval`s the screen code once, guarded by a window flag (`window.xyz||(window.xyz=1,eval("..."))`) so re-rendering the HTML does not start a second copy.
- The `textData` element (`monitorType:"custom"`) carries the **same code** in its `monitor` string, again behind the same guard, with `color:"rgba(0,0,0,0)"`, tiny `width/height`, `minMax:"none"` and a `minMaxThreshold` such as `"[wped_w]>80"`. That makes the unit evaluate it, so the screen still starts if the `onerror` path is blocked. Keep both copies identical.
- Logic is a `setInterval(...,100)` (10 Hz) that reads values, updates text with a `T(id,text)` helper that only writes on change, and redraws canvases every other tick.
- Older screens skip drawing when off-screen with `hideScreen(id)`: `e.closest('.customGaugeScreen').id !== window.activeSection`. The knock screens use the app's newer `window.btScreenVisible` / `.bt-offscreen` mechanism instead.

## Helper conventions
- `G(k)`: `window.gaugeVars[k].v` parsed to a number, `null` when missing/empty. Always null-check; a missing channel must show `--`, never a made-up number.
- Boost psi = `(psrg_w - pu_w) * 0.0145038` (both absolute, hPa-like units); target = `psrs_w` (V8) or `pvds_w` (RS3) the same way.
- Lambda: wideband can read ~16 when not ready; cap or hide above ~2.

## Extra variables seen (see also variables.md)
`nmot_w` rpm, `gangi` gear, `zwist` actual ignition (average), `miist_w` ECU torque, `Com_aLng` longitudinal accel, `vfzg_w` and `VehV_vWhlFrtL/FrtR/RrL/RrR` speeds, `tvldste_w` WGDC %, `toel` oil temp (C), `tans` intake temp (C), `ethanolpercent`, `mapswitch`, `wped_w` pedal, `rl_w` load, `customresult5` (NOS %), `customresult10`, `customresult14` (user-defined channels; meaning is up to the user's setup), `btScreen.settings.carWeight` (lb; older screens read the app's internals for this, which new screens must not), `window._ecuDA` (density altitude).

## Pull rules used elsewhere
- Pull Lab / Live Dyno start a pull at pedal >= 90 % and load >= 120 for 0.5 s and end it 0.5 s after pedal < 50 %; a pull must last >= 1.5 s to count. The knock screens use a simpler pedal >= 80 % rule (see `examples/knock-screens/REFERENCE.md`). Pick one per screen and say which.
- Pull Lab judges on values held for a moment (3 samples fuel/lambda, 10 samples boost) and only while pedal >= 90 and load >= 200, so spool-up and lift-off don't count.

## Things to watch
- These screens count cylinders by **variable number** (`wkrv_2` = "cylinder 2"). Variables are firing-order numbered, so on a V8 `wkrv_2` is physical cylinder 5. If a screen labels cylinders, map them (`variables.md`).
- Fuel pressure: `pbkist_w`/`pbksoll_w` are kPa (low-pressure limit around 580), `prroh_w`/`prroh2_w`/`prsoll_w` are MPa.
- The "S8 Digilog" artwork screen is a ~6 MB image-based JSON (SVG + embedded PNG glyphs). Check the unit/app upload limit before building anything that size; the knock screens stay under 1.00 MB.
- The two examples are **1920x480 only** (S-series). They are provided as finished, installable screens and as references; no 800x480 versions exist, so don't offer them to M1 / X1 users without designing a new layout (see the 1143x686 design size in `layouts.md`).
- Artwork that uses another company's logo or trademark should not be bundled into a public build.
