---
name: btres-custom-screen
description: Design and build custom data screens for bTres gauge units (S-series 1920x480 and M1 / X1 800x480) that show any DS1 monitor, default or custom - gauges, bars, graphs, readouts, alerts, pull tracking, 3D, artwork. Asks which bTres unit and car, which data the user wants and how it should look, then writes the screen, packages it as an installable screen JSON / ZIP and previews it. Use when the user wants to make, change or port a bTres custom screen.
argument-hint: [what the screen should show]
---

# bTres custom screen builder

Request: $ARGUMENTS

Builds a bTres **custom data screen**: a JSON file the user installs from the bTres screen gallery or "upload custom screen". The screen is HTML (divs, canvases, SVG) plus JavaScript that reads live values from `window.gaugeVars`. Everything needed is in this folder; the tools use only Python 3's standard library. This file is plain Markdown: any AI agent that can write files, run Python and ask the user a question can follow it.

## Steps

1. **Find out what to build.** Ask only what you don't already know (multiple choice if you have a question tool):
   - **Which bTres unit?** S-series (1920x480 screen) or M1 / X1 (800x480 screen). This sets the design size (see `reference/layouts.md`; 800 units are designed on 1143x686).
   - **Which car?** It decides which DS1 variable names, cylinder count and firing order apply. If it is not a car covered in `reference/variables.md`, ask the user for the variable names instead of guessing.
   - **What data, and which monitors?** Default DS1 monitors or custom ones (user-defined channels such as `customresult5`). Look each variable up with `scripts/find_monitor.py` (bundled full monitor lists for the 6/7/8 series and the RS3 / TT RS, `reference/variables.md`); for another car or a custom channel, ask the user for the exact name and what it means, and the units / scale they want.
   - **What should it look like and do?** Gauges, bars, graphs, numbers, colors, alerts and thresholds, pull / last-run tracking, whether the footer bar stays, any touch actions.
2. **Start from the closest example** in `examples/` (see `examples/README.md`): a minimal screen, a pull verdict screen, a dyno screen, or the 3D-engine knock screens. Reuse their patterns; adapt rather than reinvent. Tell the user when you are adapting one.
3. **Write the screen** as two files in a scratch folder: `screen.html` (a fragment, sized to the design canvas, absolutely positioned) and `screen.js` (logic). Follow the rules below and `reference/patterns.md`.
4. **Package it:**
   ```
   python3 <this skill>/scripts/make_screen.py --name "My Screen" --html screen.html --js screen.js --unit s|m1x1 --out <dir>
   ```
   It writes `<name>.json` and `<name>.json.zip` and warns if the file is over the 1.00 MB limit.
5. **Preview it** with fake values, look at the PNG, fix, repeat:
   ```
   python3 <this skill>/scripts/preview.py <name>.json out.png --unit s|m1x1 --vars '{"nmot_w":5200,"psrg_w":2400,"pu_w":1000}'
   ```
   Test the empty state too (no `--vars`: every value should show `--`, nothing should throw). Checks every threshold / alert state you built by feeding values on each side of it.
6. **Hand over** the file path(s) and say plainly: how to install it (upload the `.json` or the `.zip` on the unit), that a unit with an older copy of the same screen needs it removed first, and that previews are headless-Chrome renders - **not tested on a real unit** unless the user tells you otherwise.

## Rules

- **Never invent variables or values.** Read with `window.gaugeVars[name].v`; a missing / empty value shows `--`, never a made-up number or `0`. Only use names that exist in the bundled monitor list for the user's car (`find_monitor.py --exact`) or that the user gave you. Density altitude comes from `window._ecuDA`. If a custom channel's meaning is unclear, ask.
- State units and scales on the screen and in your handover; convert explicitly (psi, bar, kPa, MPa, C/F).
- Keep it light: draw at most ~10-30 times a second, write text only when it changed, skip drawing work when the screen is off-screen (`reference/layouts.md`). The unit's CPU is small.
- Variables numbered per cylinder (`wkrv_2` ...) follow the **firing order**, not cylinder order. Map them to physical cylinders before labelling a cylinder (`reference/variables.md`).
- No external network resources: all fonts, images and code are embedded (data URIs). Keep the JSON under 1.00 MB; compress images, avoid huge base64 assets.
- Don't bundle another company's logo or trademark into something meant for sharing.
- Safety: this is a display. Don't present estimates (power, torque, anything derived) as ECU or measured truth without labelling them as estimates.

## Files
- `reference/screen-format.md` - the JSON format, the two-element pattern, how code is started, limits.
- `reference/variables.md` - how to read the DS1 monitor lists, V8 vs RS3 name differences, density altitude (`window._ecuDA`), custom channels, per-cylinder numbering and firing orders.
- `reference/ds1-monitors/` - the full DS1 monitor lists (variable, description, metric unit, scaling) for the 6/7/8 series and the RS3 / TT RS.
- `reference/layouts.md` - unit sizes and design canvases, footer, app behaviours screens can use (frame cap, off-screen state, touch).
- `reference/patterns.md` - patterns and gotchas from the example screens.
- `scripts/make_screen.py`, `scripts/preview.py`, `scripts/find_monitor.py` - the packager, the preview renderer and the monitor lookup.
- `examples/` - finished screens and their sources.
