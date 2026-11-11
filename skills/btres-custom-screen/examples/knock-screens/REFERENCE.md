# Knock Screen reference

## What the screens do
- Per cylinder: **K** = live knock correction in degrees (<= 0, negative = timing pulled), **IGN** = that cylinder's ignition timing. A second line **L** shows the *last pull's* worst knock and its peak timing under load.
- Alert levels (knock correction): **yellow at -2 deg or lower, red at -3 deg or lower**. A cylinder alert draws a box round its callout, an animated line to the cylinder and a top banner; outside a pull it clears itself after 10 s; a new pull clears it.
- A pull = pedal (`wped_w`) >= 80 %; it ends when the pedal has been below 80 % for 0.3 s, which is when "last" values are saved. Knock events count when a cylinder goes below -0.5 deg during a pull.
- "Last IGN" = the **peak timing while under load** (`rl_w` >= 150) during the pull, falling back to the last in-pull timing if the car was never loaded. (Lift-off pulls timing and would otherwise give negative values.)
- Two-finger tap on the screen clears last-pull data and knock alerts (the app also resets min/max).
- Tap/drag the engine to rotate it. Tapping the bTres / DS1 logos (1920 screens only) opens the app's usual overlays.

## Variables (`window.gaugeVars[name].v`)

| purpose | name(s) | notes |
|---|---|---|
| knock per cylinder | `wkrv`, `wkrv_2` ... `wkrv_8` (V8) / `wkrv_5` (2.5 TFSI) | **firing-order numbered**, see below |
| ignition per cylinder | `zwcalcar`, `zwcalcar_2` ... | same numbering |
| pedal | `wped_w` | pull detection |
| load | `rl_w` | peak-timing rule |
| boost | `psrg_w` (actual), `pu_w` (ambient), target `psrs_w` (V8) / `pvds_w` (RS3) | psi over ambient = (kPa diff) x 0.0145038 |
| LPFP | `pbkist_w`, `pbksoll_w` | /100 -> bar |
| HPFP | `prroh_w` / `prsoll_w` (B1), `prroh2_w` / `prsoll2_w` (B2, V8 only) | MPa |
| lambda | `lamsoni_w` (B1), `lamsoni2_w` (B2, V8 only) | capped at 1.99 like the main lambda gauge (unready sensors read ~16) |
| temps | `tans` (intake), `toel` (oil; RS3 falls back to `toelk_w`), `tmot` (coolant), `Gbx_tOilConv` (trans) | degrees C |
| other | `ethanolpercent`, `ubsq` (volts), `mapswitch`, `window._ecuDA` (density altitude) | footer bar of the 1920 screens |

### Firing-order mapping
Variable index k belongs to physical cylinder FO[k]:
- **V8**: FO = 1-5-4-8-6-3-7-2, so `wkrv`=cyl 1, `wkrv_2`=5, `wkrv_3`=4, `wkrv_4`=8, `wkrv_5`=6, `wkrv_6`=3, `wkrv_7`=7, `wkrv_8`=2. The screen's per-cylinder arrays are `KN=["wkrv","wkrv_8","wkrv_6","wkrv_3","wkrv_2","wkrv_5","wkrv_7","wkrv_4"]` (cyl 1..8) and the same for `zwcalcar`.
- **2.5 TFSI**: FO = 1-2-4-5-3, so `wkrv_3`=cyl 4, `wkrv_4`=cyl 5, `wkrv_5`=cyl 3: `KN=["wkrv","wkrv_2","wkrv_5","wkrv_3","wkrv_4"]`.

## Layout
- 1920 screen: 1920x480 canvas set; engine WebGL canvas at (1305,0) 460x425; callout columns at x=1171 (left) and x=1720 (right, right-aligned in the 800 build).
- 800x480 unit: the app scales `#sliders` by 0.7 (`width:1142.86px`), so the screen is designed on **1143x686**. Engine canvas (260,-15) 620x650, callout slots at y = 84/234/384/534 (V8, 4 per side) or staggered (RS3), 22 px text, legend at y=673. 
- Three canvases: `bt8base` (gauges, under), `bt8gl` (three.js engine), `bt8over` (callouts and lines, on top). Element ids are `bt8*`.

## Screen JSON format
`{"settings":{"showFooterBar":false},"elements":[ <text element>, <textData loader monitor> ]}`. The text element holds the HTML and a base64 payload (three.js r128 + the screen JS) that an `<img onerror=eval(atob(...))>` loads; a version-tag guard (`window.bt8v!==VER`) re-initialises when the code changes. 1.00 MB JSON limit. All four builds set `showFooterBar:false`: the app hides its native footer bar on these screens (the 1920 screens draw their own temps/ethanol/volts bar).

## Behaviours that depend on the bTres app
- The app caps `requestAnimationFrame` globally (`bT.maxFps`, 30) and sets `.bt-offscreen` on custom screens that are fully out of view (`window.btScreenVisible[id]`). The screen then runs only its data logic.
- The engine canvas is hidden (`visibility:hidden` on `#bt8gl`) until its screen is >= 98 % in view plus 100 ms (`.bt-full`, `window.btFullTracking`), and `updateGL()` skips drawing meanwhile. Older apps without the flag draw normally.
- Before the first engine frame the callout lines point at the engine area's centre under a black "LOADING ENGINE" box. The engine is built ~60 ms after attach so that note is visible.
- Coarser 3D detail (shadow map 1024, 28-segment cylinders, 10x32 tori, 8-sided tubes, 2/4 extrude bevel/curve segments) in `scripts/knock_lod.py`.

## Customising (edit the scripts, then rebuild)
- `scripts/make_v8_knock_screen_800.py` : 800 layout constants at the top (GL canvas, RX, LAB_X, SLOTS) and asserted replacements. It patches the **base build** (`assets/bTres-V8-Knock-Screen.base.json`).
- `scripts/make_rs3_knock_screen.py` : 5-cylinder changes (`KN`/`IG`, POS_1920 / POS_800 staggered callouts, zoom, lambda block); the engine comes from `assets/bTres-2.5-TFSI-engine-prototype.html`.
- `scripts/knock_lod.py` : shared 3D detail and loading-state patches.
- Alert thresholds: `threshold=-2,THR2=-3` in the screen JS (in the base). Because the base is a finished build, change such things with an added asserted replacement in the relevant script (decode -> replace -> re-encode, see how `make_v8_knock_screen_800.py` does it) and bump the version tag.

## Testing without a car
Open the screen HTML in headless Chrome inside a div with class `customGaugeScreen`, define `window.gaugeVars={wped_w:{v:95},rl_w:{v:210},wkrv_3:{v:-3.4},...}`, and screenshot after >= 10 s (software WebGL). For the app's real slider/footer behaviour you need an actual unit.
