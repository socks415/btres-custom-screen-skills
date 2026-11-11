# bTres Knock Screen skill

An AI-agent skill that builds bTres gauge-unit "Knock Screens" (3D engine with per-cylinder knock and ignition callouts, boost, fuel pumps, lambda). It asks which car (6/7/8 series V8 or RS3 / TT RS 5-cylinder) and which unit (S-series 1920x480 or M1 / X1 800x480) and writes the matching screen JSON plus a ZIP ready to install.

Also included, as ready-to-install S-series (1920x480) examples: **Pull Lab** and **Live Dyno** in `assets/examples/`.

## Install
- **Claude Code:** unzip so the folder `btres-knock-screen/` sits in `~/.claude/skills/` (all projects) or `<project>/.claude/skills/`. Then ask: "build me a bTres knock screen" or run `/btres-knock-screen`.
- **Claude.ai / Claude desktop:** upload the ZIP under Settings > Capabilities > Skills (the ZIP must contain the `btres-knock-screen/` folder with `SKILL.md` at its top). Menu names change; check the current Skills help page.
- **Other AI tools:** `SKILL.md` is plain Markdown. Give it (and the folder) to any agent that can run Python 3 and ask you questions, and tell it to follow `SKILL.md`.

Requirements: Python 3 (standard library only). No network access needed.

## Use without an AI
`python3 scripts/build.py --car v8|rs3 --unit s|m1x1 --out ./out`

## Not tested on every setup
Screens were checked in headless Chrome renders, and the V8 screen by an owner in a car. Check on your own unit before relying on any alert.

Not affiliated with Audi, Volkswagen or Better Than, Inc.
