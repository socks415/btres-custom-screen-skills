# Screen JSON format

What follows is what the known-working screens in `examples/` use and what `scripts/make_screen.py` writes. If the user's bTres app version supports other element types, check a screen exported from their unit before relying on them.

```json
{
  "settings": { "showFooterBar": false },
  "elements": [
    { "type": "text", "text": "<HTML fragment>", "fontSize": 24, "fontWeight": 400,
      "color": "rgba(160,190,160,1)", "width": 1920, "height": 480, "x": 0, "y": 0, "align": "left" },
    { "type": "textData", "monitorType": "custom", "monitor": "<JavaScript expression>",
      "decimals": 0, "preText": "", "postText": "", "fontSize": 8, "fontWeight": 700,
      "color": "rgba(0,0,0,0)", "width": 10, "height": 35, "x": 0, "y": 0, "align": "left",
      "minMax": "none", "minMaxThreshold": "[wped_w]>80" }
  ]
}
```

- **`settings.showFooterBar`**: `false` hides the app's bottom bar on this screen (the screen gets the full height). `true` keeps it, so design for less height.
- **text element**: the whole screen is one HTML fragment sized to the design canvas (1920x480 for S-series; 1143x686 for M1/X1, see `layouts.md`). Use absolutely positioned divs, `<canvas>`, inline SVG, `<style>`, images as `data:` URIs.
- **How code starts**: a `<script>` tag inside the fragment does not run. Instead the fragment contains a hidden `<img src="data:," style="display:none" onerror="...">` whose handler evaluates the code. `make_screen.py` embeds the JS as a JSON-escaped string literal (`eval("...")`), HTML-escaped inside the attribute, so quoting is handled. Don't use base64 / `atob` or build code at run time: the gallery's upload scanner flags that as high risk (see `gallery.md`).
- **Guard**: the handler is `(window.KEY||(window.KEY=1,eval(...)))` so the code runs once even if the HTML is re-rendered. Change `KEY` when the code changes, or a unit that already ran the old code keeps running it (`make_screen.py` derives KEY from the code's hash).
- **textData monitor**: a second, invisible element carrying the *same guarded code* as its `monitor`. The unit evaluates monitors itself, so the screen still starts if the `onerror` route is blocked. Keep the two copies identical. `minMaxThreshold` is an expression over variables in square brackets that the app evaluates for min/max tracking; `"[wped_w]>80"` is harmless filler.
- **Reading data**: `window.gaugeVars[name].v` (string or number; parse it; may be missing / empty). Values update continuously; poll with `setInterval(...,100)` or `requestAnimationFrame`.
- **Size limit**: the gallery accepts a screen JSON of up to 1 MB (a ZIP up to 20 MB for screens that bundle images); keep each screen JSON under 1.00 MB. One large image-based screen (~6 MB) existed; its acceptance on a unit was never verified.
- **Installing**: upload the `.json` (or the `.zip` of it) on the unit's custom-screen page, or install it from the gallery at https://gallery.betterthan.shop (see `gallery.md`). Replacing an installed screen with changed code: uninstall the old one first.
- Non-ASCII characters in the JS are escaped as `\uXXXX` by the packager.
