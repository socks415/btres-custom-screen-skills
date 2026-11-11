---
name: btres-knock-screen
description: Build a bTres gauge-unit "Knock Screen" - a 3D engine with per-cylinder knock correction and ignition-timing callouts, plus boost, fuel pumps and lambda - as an installable screen JSON. Asks which car (6/7/8 series V8 or RS3 / TT RS 5-cylinder) and which bTres unit (S-series 1920x480 or M1 / X1 800x480), then builds the matching file. Use when the user wants a knock / ignition / per-cylinder data screen for a bTres unit, or wants to customise or extend these screens.
argument-hint: [v8|rs3] [s|m1x1]
---

# bTres Knock Screen builder

Arguments: $ARGUMENTS

Output is a bTres custom data-screen JSON (and a `.zip` of it) that the user installs from the bTres screen gallery or "install from file". Everything needed is in this folder; the build uses only Python 3's standard library. This file is plain Markdown: any AI agent that can run Python and ask the user a question can follow it.

## Steps

1. **Ask the two questions** (skip any already answered in the arguments or the conversation). Use a multiple-choice question tool if you have one, otherwise ask in chat.
   - **Which car?** `v8` = 6 / 7 / 8 series (V8, 8 cylinders, two banks) or `rs3` = RS3 / TT RS (2.5 TFSI, 5-cylinder inline).
   - **Which bTres unit?** `s` = S-series (1920x480 screen) or `m1x1` = M1 / X1 (800x480 screen).
   If the user is unsure of the unit: S-series is the wide one. A unit's screen is 800 px wide when `window.innerWidth <= 1910`.
2. **Build it.** The car sets which engine data is used, the unit sets the layout:

   ```
   python3 <this skill>/scripts/build.py --car <v8|rs3> --unit <s|m1x1> --out <output dir>
   ```

   | car | unit | file | what you get |
   |---|---|---|---|
   | v8 | s | `bTres-V8-Knock-Screen.json` | boost gauge, LPFP + HPFP B1/B2, lambda B1/B2, temps bar, 3D V8 with 8 callouts |
   | v8 | m1x1 | `bTres-V8-Knock-Screen-800.json` | engine + 8 callouts only (4 per side), footer bar hidden |
   | rs3 | s | `bTres-RS3-Knock-Screen.json` | boost, LPFP + HPFP, one lambda, 3D inline-5 with 5 callouts |
   | rs3 | m1x1 | `bTres-RS3-Knock-Screen-800.json` | engine + 5 callouts only, footer bar hidden |

   The build prints the size (the hard limit is 1.00 MB) and writes `<name>.json` and `<name>.json.zip`.
3. **Check the result** if you can: the screens render in headless Chrome (software WebGL is slow, give the engine 10 s or more to appear; before it appears the screen shows a "LOADING ENGINE" note). Fake `window.gaugeVars` values from `reference.md` to see knock alerts.
4. **Hand over** the file path(s) and tell the user, plainly:
   - install the `.zip` (or the `.json`) on the unit; the screen hides the native footer bar itself;
   - a unit that already has the same version tag (`v8k-19`, `v8w-2`, `r3k-2`, `r3w-2`) keeps its cached code, so uninstall the old one first;
   - these screens have been checked in headless renders and by a V8 owner in a car, not on every unit type - say so rather than claiming they are proven on the user's car.

## Rules

- **Never invent variables.** Every value comes from `window.gaugeVars[name].v`. Only use names from `reference.md`; if the user asks for data that is not there, ask them for the exact variable name from their ECU's list.
- The knock / ignition variables are numbered in **firing order**, not cylinder order. The builds already map them to physical cylinders (V8 1-5-4-8-6-3-7-2, 2.5 TFSI 1-2-4-5-3). Do not "fix" this back to straight numbering.
- Do not hand-edit the base64 payload in the JSON. Change the Python build scripts (they patch the decoded JavaScript with asserted string replacements, so a missed target fails loudly) and rebuild. `reference.md` says where each thing lives.
- Keep every output under 1.00 MB and keep the version tag unique per layout when the code changes, or units will keep running the old code.
- Don't claim hardware performance numbers. The coarser 3D detail and hide-until-in-view behaviour are reasoned, not measured on a unit.

Two more finished screens ship in `assets/examples/` (both S-series 1920x480 only): `bTres-Pull-Lab-1920.json` (pull verdict + graphs + per-cylinder knock) and `bTres-Live-Dyno-1920.json` (estimated whp / torque with pull comparison). If an S-series user asks for a dyno or pull-lab style screen, hand them the matching file as is, and say there is no M1 / X1 version. See `other-screen-patterns.md` for how they work and as a base for new screens.
See `reference.md` for the data map, behaviour rules (alert levels, last-pull data, pull detection), layout geometry, the screen JSON format, and how to customise.
