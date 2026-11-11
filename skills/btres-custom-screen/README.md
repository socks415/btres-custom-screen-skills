# bTres custom screen skill

An AI-agent skill for designing and building **custom data screens for bTres gauge units**. Tell it which unit you have (S-series 1920x480 or M1 / X1 800x480), which car, and what you want to see - any DS1 monitor, default or custom - and it writes the screen, packages it as an installable JSON / ZIP, and previews it.

## Install
- **Claude Code:** copy this folder (`btres-custom-screen/`) into `~/.claude/skills/` (all projects) or `<project>/.claude/skills/`, then ask: "make me a bTres screen that shows ..." or run `/btres-custom-screen`.
- **Claude.ai / Claude desktop:** zip this folder (the `btres-custom-screen/` folder itself at the top of the zip) and upload it under Settings > Capabilities > Skills. Menu names change; check the current Skills help page.
- **Other AI tools:** give the agent `SKILL.md` and this folder, and tell it to follow `SKILL.md`.

Requirements: Python 3 (standard library only); Google Chrome or Chromium for previews.

## Use the tools without an AI
```
python3 scripts/make_screen.py --name "My Screen" --html screen.html --js screen.js --unit s --out ./out
python3 scripts/preview.py ./out/My-Screen.json shot.png --unit s --vars '{"psrg_w":2400,"pu_w":1000}'
```
Try it with `examples/hello-boost/`.

## What's inside
`SKILL.md` (the workflow), `reference/` (JSON format, DS1 variables and the full 6/7/8 series and RS3 / TT RS monitor lists, unit layouts, patterns), `scripts/` (packager, preview, monitor lookup), `examples/` (a minimal screen, Pull Lab, Live Dyno, and the 3D knock screens).

Screens are checked in headless renders; always test on your own unit. Licensed GPL-3.0-or-later (see the repo `LICENSE`).
