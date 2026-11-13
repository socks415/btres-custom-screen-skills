# DS1 logging, custom monitors and safety

Notes for screens that need a variable the DS1 doesn't send by default, and the rules an AI agent must follow around the unit and the DS1. (Adapted from notes by Jim, read from the unit's and the DS1 editor's code, a 4.0T's logs and the bTres community; items from the community are reports, not verified by this skill.)

## Hard safety rules for an AI agent
1. Never call the unit's `/updates/check/<branch>` (it **switches branch**), `/updates/pull`, `/restart`, or any delete / upload / install endpoint without the owner's explicit yes for that action. Reading the screen list, images and alerts is fine.
2. Never send DS1 `run<path>` for "Clear fault codes", `factory`, `del`, `pass`/`pasr`, `RTperm`, or any ECU write. A clear-faults button on a screen must be PIN-gated and pressed by the owner.
3. No raw CAN/UDS frames, no development-mode requests to a transmission controller, nothing that writes to the car.
4. Back up the unit's screens before any upload; nothing goes on a unit unseen, and the owner confirms.
5. Don't hunt for credentials.
6. Anything shared with other owners is built clean: no personal seed values.

## Getting a variable onto the bTres (community method)
A screen can only read what the DS1 streams. The default stream is log mask 3 (groups 1 and 2). To log another monitor:
1. Make a **renamed copy** of `monitors.csv` and set that row's **Log mask** to **1** (change only that field, keep the line endings, diff against the original so exactly the rows you meant changed; never hand-edit addresses).
2. Upload the copy in the DS1 **File** tab, then type the exact file name **with `.csv`** (e.g. `monitors2.csv`) in DS1 Settings > Custom logging. Leave the default mask at 3. Check the saved file for stray spaces if you used Excel (a plain-text editor is safer).
3. Put extra rows at the **end** of the file on **raster 2**, not raster 1: 100 Hz rasters are scarce (about 2000 CAN frames/s) and too many items make ECU logging misbehave.
4. Some channels read wrong until corrected (cam timing read about 40 degrees off: fix with Metric Offset). SABRE boost rows read 0 unless the SABRE loop is enabled in the tune.

**Hand-off rule:** if a screen needs a variable outside the default stream, the **first line** of the hand-off says so in capitals ("NEEDS A MONITORS.CSV CHANGE ON THE DS1"), names the variables, and says the DS1 change is the owner's step. Until it is made those readouts are blank or 0. Prefer screens that need no change, and tell users how to check (does the variable appear in `gaugeVars` on their unit?).

## How the mask works
- The mask is a bit-OR of groups; each monitor row is in exactly one group. Default 3 = groups 1 + 2; ECU extras 9 = 1 + 8; transmission 5 = 1 + 4; custom boost 131 = 1 + 2 + 128; 4115 adds 4096 (custom results).
- On the 4.0T file, group 128 is the ten SABRE boost rows, 8 is ECU extras (ASR, cams, misfires, knock ratio), 4 is the transmission, 0 is never logged. Mask 3 sent 189 rows.
- The stream (websocket on port 9997) is a JSON monitor list then binary raster frames.

## DS1 and unit facts that bite
- The DS1 is the Wi-Fi OBD dongle (its own page at 192.168.4.1 or `ds1.local`); the bTres unit is the display (its own access point 192.168.220.1, web app on port 5000). A laptop on the unit's access point never sees DS1 traffic.
- Any ECU-tab command (`run`) stops DS2 logging: gauges go blank until logging restarts. "Read DS1 log" erases the log. One browser per DS1: a phone can't use the DS1 page while the bTres holds it.
- Fault reading and clearing is done by the vendor app by friendly name ('Read fault codes', 'Clear fault codes'); `getDS1Worm` returns "" when a name doesn't match exactly, which sends a bare `run`, so any button needs an exact-name allowlist that refuses "".
- Stock unit functions a screen can call: `checkFaults()`, `clearFaults()`, `setMap(n)` (PIN-gated, but the gate does nothing when no PIN is set), `launchAppWindow('faults'|'alerts'|'eCalc')`. Prefer not to; the editor never opens the DS1 socket, so test DS1-dependent features in the car.
- Unit endpoints that are read-only: screen list, images, alerts, log list. Unsafe from a script: anything under `/updates/*`, `/restart`, `/support/*`, and delete/upload routes.
