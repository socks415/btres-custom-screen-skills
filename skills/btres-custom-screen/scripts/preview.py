#!/usr/bin/env python3
"""Render a screen JSON to a PNG in headless Chrome with fake data, to check the layout before installing.

  python3 preview.py screen.json out.png [--unit s|m1x1] [--vars '{"nmot_w":5200,"psrg_w":2400,"pu_w":1000}'] [--wait 3]

  --vars   JSON object of fake values; each becomes window.gaugeVars[name] = {v: value}
  --settings  JSON object that overrides the mock btScreen.settings (e.g. '{"ctoF":true,"carModel":"RS3"}')
  --data      JSON object that seeds the mock btScreen.store() for the screen (the saved values at start-up)
  --raw    M1/X1 only: render the unscaled 1143x686 design canvas instead of the real 800x480 view
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
ap.add_argument("--raw", action="store_true")
ap.add_argument("--settings", default="{}")
ap.add_argument("--data", default="{}")
ap.add_argument("--wait", type=float, default=3)
a = ap.parse_args()

doc = json.load(open(a.json))
el = doc["elements"][0]
W, H = SIZES[a.unit] if a.unit else (el.get("width", 1920), el.get("height", 480))
fit = (W, H) == SIZES["m1x1"] and not a.raw      # M1 / X1: show what the unit shows, the design canvas scaled by 0.7 into 800x480
VW, VH = (800, 480) if fit else (W, H)
chrome = next((p for p in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome"),
                           shutil.which("chromium"), shutil.which("chromium-browser"), shutil.which("chrome")]
               if p and os.path.exists(p)), None)
if not chrome:
    sys.exit("Chrome/Chromium not found")
page = """<!doctype html><html><body style="margin:0;background:#222"><div style="width:%dpx;height:%dpx;overflow:hidden;position:relative"><div id="screen_1" class="customGaugeScreen" data-screen-key="preview" style="width:%dpx;height:%dpx;position:relative;background:#000;overflow:hidden;transform-origin:0 0;transform:scale(%s)"></div></div>
<script>window.addEventListener("error",function(e){var d=document.createElement("pre");d.style.cssText="position:fixed;left:0;top:0;color:#0f0;font:14px monospace;z-index:99;background:#000";d.textContent="JS ERROR: "+e.message+" @"+e.lineno;document.body.appendChild(d)});
window.gaugeVars={};var v=%s;
/* the app page has jQuery; the preview only stands in for the bit screens use for the on-screen keyboard: $(sel).on(event, fn) */
if(!window.jQuery){window.$=window.jQuery=function(s){var l=typeof s==="string"?Array.prototype.slice.call(document.querySelectorAll(s)):[s&&s.nodeType?s:document];return{on:function(e,f){l.forEach(function(n){n.addEventListener(e,f)});return this},length:l.length}}}
/* mock of the app's btScreen API (settings, ready, store): in memory only, same limits as the app */
window.btScreen=(function(){var S=Object.assign({loaded:true,ctoF:false,mapBoost:false,ds1Url:"ds1.local",map1:"",map2:"",map3:"",map4:"",map5:"",map6:"",map7:"",map8:"",map9:"",launchBoost:null,carModel:"S8",carWeight:4870,tireWidth:275,tireRatio:35,tireRim:21},%s);var D=%s,KEY=/^[A-Za-z0-9_.-]{1,64}$/;
var cp=function(x){return x===undefined?undefined:JSON.parse(JSON.stringify(x))};
return {version:1,settings:Object.freeze(S),ready:function(f){Promise.resolve().then(f)},store:function(el){
 return {available:true,get:function(k,d){return Object.prototype.hasOwnProperty.call(D,k)?cp(D[k]):d},all:function(){return cp(D)},
  set:function(k,v){if(!KEY.test(k)){console.warn("bad key");return false}if(v===undefined){delete D[k];return true}var n=cp(D);n[k]=cp(v);
   if(Object.keys(n).length>200||unescape(encodeURIComponent(JSON.stringify(n))).length>102400){console.warn("store limit");return false}D=n;return true},
  remove:function(k){delete D[k];return true},clear:function(){D={};return true}}}}})();for(var k in v)gaugeVars[k]={v:v[k]};window.btScreenVisible={};
document.getElementById('screen_1').innerHTML=%s;</script></body></html>""" % (VW, VH, W, H, "0.7" if fit else "1", a.vars, a.settings, a.data, json.dumps(el["text"]))
with tempfile.TemporaryDirectory() as t:
    p = os.path.join(t, "page.html")
    open(p, "w").write(page)
    subprocess.run([chrome, "--headless=new", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                    "--allow-file-access-from-files", "--window-size=%d,%d" % (VW, VH),
                    "--virtual-time-budget=%d" % int(a.wait * 1000), "--screenshot=" + os.path.abspath(a.png), "file://" + p],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("wrote", a.png, "(%dx%d%s)" % (VW, VH, ", scaled 0.7 like the unit" if fit else ""))
