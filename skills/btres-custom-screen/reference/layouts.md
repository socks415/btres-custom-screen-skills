# Units, canvases and app behaviours

| unit | screen | design canvas | notes |
|---|---|---|---|
| S-series | 1920 x 480 | **1920 x 480** | `window.innerWidth > 1910` |
| M1 / X1 | 800 x 480 | **1143 x 686** | the app scales the screen by 0.7 (`#sliders{transform:scale(.7);width:1142.86px}`), so a 1143x686 canvas fills 800x480 |

- Pass `--unit s` or `--unit m1x1` to `make_screen.py` / `preview.py`; they set the canvas size. A design for one unit is not automatically right for the other: lay out each separately (the 800 unit has far less room per element; use larger text, fewer panels).
- **Footer bar**: `settings.showFooterBar:false` hides it per screen. The app waits until a screen is fully settled before hiding/showing the footer, so it doesn't flash while swiping.
- **Touch**: elements are not clickable unless they set `pointer-events:all`. A two-finger tap resets the app's min/max; a screen can listen for `touchstart` with `e.touches.length>1` to clear its own data. Swipes move between screens: if a control needs to be dragged (e.g. rotating a model), stop propagation on its touch/mouse events.
- **Frame rate**: the app caps `requestAnimationFrame` globally (`window.bT.maxFps`, default 30). Don't expect 60 fps.
- **Off-screen**: the app marks custom screens that are completely out of view with class `bt-offscreen` (CSS skips their layout/paint and pauses CSS animations) and keeps `window.btScreenVisible[screenId]` (true/false) plus a bubbling `btscreenvisible` event (`detail:{id,visible}`). JS timers and data keep running, so logging and tracking continue. A screen should skip *drawing* when `btScreenVisible[id]===false` but keep its data logic running. (Older screens do the same with `window.activeSection`.)
- **Fully-in-view** (newer app builds): the screen element gets class `bt-full` once >= 98 % in view for 100 ms, and `window.btFullTracking` is true. Heavy parts (e.g. a WebGL canvas) can be hidden with CSS until then (`.customGaugeScreen:not(.bt-full) #myCanvas{visibility:hidden}`) and their drawing skipped (check `window.btFullTracking` first so older apps still draw).
- **Version display / branch**, PIN pad and other app UI sit outside the screen; don't draw over the top strip if the footer is visible.
