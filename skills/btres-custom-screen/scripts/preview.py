#!/usr/bin/env python3
"""Render a screen JSON to a PNG in headless Chrome with fake data, to check the layout before installing.

  python3 preview.py screen.json out.png [--unit s|m1x1] [--vars '{"nmot_w":5200,"psrg_w":2400,"pu_w":1000}'] [--wait 3]

  --vars   JSON object of fake values; each becomes window.gaugeVars[name] = {v: value}
  --wait   seconds to let the screen run before the screenshot (WebGL screens in software need 10 s or more)

Needs Google Chrome (or Chromium). It is a layout / logic check only: no app, no footer, no real unit scaling,
and not a substitute for testing on the device.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile

SIZES = {"s": (1920, 480), "m1x1": (1143, 686)}
ap = argparse.ArgumentParser()
ap.add_argument("json")
ap.add_argument("png")
ap.add_argument("--unit", default=None, choices=SIZES)
ap.add_argument("--vars", default="{}")
ap.add_argument("--wait", type=float, default=3)
a = ap.parse_args()

doc = json.load(open(a.json))
el = doc["elements"][0]
W, H = SIZES[a.unit] if a.unit else (el.get("width", 1920), el.get("height", 480))
chrome = next((p for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome"),
                           shutil.which("chromium"), shutil.which("chromium-browser"), shutil.which("chrome")]
               if p and os.path.exists(p)), None)
if not chrome:
    sys.exit("Chrome/Chromium not found")
page = """<!doctype html><html><body style="margin:0;background:#222"><div id="screen_1" class="customGaugeScreen" style="width:%dpx;height:%dpx;position:relative;background:#000;overflow:hidden"></div>
<script>window.addEventListener("error",function(e){var d=document.createElement("pre");d.style.cssText="position:fixed;left:0;top:0;color:#0f0;font:14px monospace;z-index:99;background:#000";d.textContent="JS ERROR: "+e.message+" @"+e.lineno;document.body.appendChild(d)});
window.gaugeVars={};var v=%s;for(var k in v)gaugeVars[k]={v:v[k]};window.btScreenVisible={};
document.getElementById('screen_1').innerHTML=%s;</script></body></html>""" % (W, H, a.vars, json.dumps(el["text"]))
with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, "page.html")
    open(p, "w").write(page)
    subprocess.run([chrome, "--headless=new", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                    "--allow-file-access-from-files", "--window-size=%d,%d" % (W, H),
                    "--virtual-time-budget=%d" % int(a.wait * 1000), "--screenshot=" + os.path.abspath(a.png), "file://" + p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("wrote", a.png, "(%dx%d)" % (W, H))
