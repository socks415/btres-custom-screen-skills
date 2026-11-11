#!/usr/bin/env python3
"""Package a custom bTres screen (your HTML + your JavaScript) into an installable screen JSON and ZIP.

  python3 make_screen.py --name "My Screen" --html screen.html --js screen.js --unit s|m1x1 --out ./out
                         [--footer] [--trigger "[wped_w]>80"] [--key myscreen]

  --html     the screen's markup (a fragment: divs, canvases, inline SVG, <style>). No <html>/<body>, no <script>.
  --js       the screen's logic (optional). Runs once when the screen appears, and again as a monitor, behind a
             guard so it never runs twice. Read values with window.gaugeVars[name].v.
  --unit     s    = S-series, 1920 x 480 design size
             m1x1 = M1 / X1, 800 x 480 unit: design on 1143 x 686 (the app scales the screen by 0.7)
  --footer   keep the app's footer bar (default: hidden, the screen uses the full height)
  --trigger  the textData monitor's minMaxThreshold expression (default "[wped_w]>80"), harmless for most screens
  --key      guard name; default is derived from the JS so changed code always re-runs on the unit

Writes <out>/<Name>.json and <out>/<Name>.json.zip. Python 3 standard library only.
"""
import argparse, base64, hashlib, json, os, re, sys, zipfile

SIZES = {"s": (1920, 480), "m1x1": (1143, 686)}
LIMIT = 1048576

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--html", required=True)
ap.add_argument("--js", default=None)
ap.add_argument("--unit", required=True, choices=SIZES)
ap.add_argument("--out", required=True)
ap.add_argument("--footer", action="store_true")
ap.add_argument("--trigger", default="[wped_w]>80")
ap.add_argument("--key", default=None)
a = ap.parse_args()

W, H = SIZES[a.unit]
html = open(a.html, encoding="utf-8").read()
js = open(a.js, encoding="utf-8").read() if a.js else ""
for bad in ("<script", "<html", "<body"):
    if bad in html.lower():
        sys.exit("html must be a fragment: remove %s (put logic in --js)" % bad)

if js:
    # atob() returns Latin-1: keep the code ASCII, escaping anything else as \uXXXX (fine in strings, regexes, comments)
    js = js.encode("ascii", "backslashreplace").decode()
    key = a.key or "bt_" + hashlib.sha1(js.encode()).hexdigest()[:8]
    key = re.sub(r"[^A-Za-z0-9_]", "_", key)
    b64 = base64.b64encode(js.encode()).decode()
    run = "(window.%s||(window.%s=1,eval(atob('%s'))))" % (key, key, b64)
    html = html + '<img src="data:," style="display:none" onerror="%s">' % run.replace('"', "&quot;")
    monitor = run
else:
    monitor = ""

doc = {
    "settings": {"showFooterBar": bool(a.footer)},
    "elements": [
        {"type": "text", "text": html, "fontSize": 24, "fontWeight": 400, "color": "rgba(160,190,160,1)",
         "width": W, "height": H, "x": 0, "y": 0, "align": "left"},
    ],
}
if monitor:
    doc["elements"].append(
        {"type": "textData", "monitorType": "custom", "monitor": monitor, "decimals": 0, "preText": "", "preFontSize": 24,
         "preFontWeight": 400, "preFontColor": "rgba(160,190,160,1)", "postText": "", "postFontSize": 24,
         "postFontWeight": 400, "postFontColor": "rgba(160,190,160,1)", "fontSize": 8, "fontWeight": 700,
         "color": "rgba(0,0,0,0)", "width": 10, "height": 35, "x": 0, "y": 0, "align": "left", "minMax": "none",
         "minMaxThreshold": a.trigger})

data = json.dumps(doc, ensure_ascii=True, separators=(",", ":")).encode()
os.makedirs(a.out, exist_ok=True)
base = re.sub(r"[^A-Za-z0-9._-]+", "-", a.name).strip("-")
path = os.path.join(a.out, base + ".json")
open(path, "wb").write(data)
with zipfile.ZipFile(path + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(path, base + ".json")
print("wrote %s: %d bytes (%.2f MB of the 1.00 MB limit), design size %dx%d" % (path, len(data), len(data) / LIMIT, W, H))
if len(data) >= LIMIT:
    print("WARNING: over the 1.00 MB screen JSON limit - shrink images / code", file=sys.stderr)
