# bTres custom screen skills

AI-agent skills for building custom data screens for bTres gauge units. Each skill is a folder under `skills/` with a `SKILL.md` (plain Markdown, works with Claude and any agent that can follow it and run Python 3).

| skill | what it does |
|---|---|
| [`btres-knock-screen`](skills/btres-knock-screen/) | Builds the 3D-engine Knock Screen (per-cylinder knock and ignition callouts) for a 6/7/8 series V8 or RS3 / TT RS, in S-series (1920x480) or M1 / X1 (800x480) layout. Also ships Pull Lab and Live Dyno example screens (S-series only). |

## Install a skill
- **Claude Code:** copy the skill folder (e.g. `skills/btres-knock-screen`) into `~/.claude/skills/` or `<project>/.claude/skills/`.
- **Claude.ai / desktop:** zip the skill folder (the folder itself at the top of the zip) and upload it under Settings > Capabilities > Skills.
- **Other AI tools:** point the agent at the skill's `SKILL.md`.

See each skill's own README for details.

Not affiliated with Audi, Volkswagen or Better Than, Inc.

## License
GPL-3.0-or-later (see [LICENSE](LICENSE)): you may use and modify these skills and screens, but if you distribute a modified version you must share it under the same license, with its source. Bundled third-party code is listed in [THIRD_PARTY.md](THIRD_PARTY.md). The bTres and DS1 logos embedded in the screens belong to their owners and are not covered by this license.
