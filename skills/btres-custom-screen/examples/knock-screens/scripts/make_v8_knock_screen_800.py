"""Builds the 800x480 unit version of the bTres V8 Knock Screen: the 3D engine with per-cylinder knock / ignition
callouts and nothing else (no boost, fuel, lambda or footer bar).

  python3 screens/make_v8_knock_screen_800.py "<bTres-V8-Knock-Screen.json (the 1920 build)>" "<out.json>"

The 800x480 units apply a 0.7 scale to everything, so the screen is designed on a 1143 x 686 canvas (800/0.7 x 480/0.7).
It is derived from the finished 1920 screen: its code is patched with the changes below rather than maintained twice.
"""
import base64
import json
import re
import sys

src, out = sys.argv[1:3]
OLD_VER, VER = "v8k-19", "v8w-2"          # own version tag, so it never collides with the 1920 screen's code
W, H = 1143, 686
GLX, GLY, GLW, GLH = 260, -15, 620, 650    # the engine's WebGL canvas
RX = 1125                                 # right edge of the right-hand callout column
LAB_X = 18
SLOTS = [84, 234, 384, 534]               # top y of the four callouts in each column

doc = json.load(open(src))
t = open(src).read()
m = max(re.finditer(r"[A-Za-z0-9+/=]{100000,}", t), key=lambda x: len(x.group(0)))
js = base64.b64decode(m.group(0)).decode()
assert OLD_VER in js


def rep(text, old, new):
    assert text.count(old) == 1, "patch target missing or not unique: %r (%d)" % (old[:80], text.count(old))
    return text.replace(old, new)


# ---- canvas / layout
js = rep(js, "c.width=1920*RES;c.height=480*RES", "c.width=%d*RES;c.height=%d*RES" % (W, H))
js = rep(js, "const GL={x:1305,y:0,w:460,h:425};", "const GL={x:%d,y:%d,w:%d,h:%d};" % (GLX, GLY, GLW, GLH))
js = rep(js, "c.clearRect(0,0,1920,480);",
         'c.clearRect(0,0,%d,%d);txt(c,"K: KNOCK CORR.  \\u00b7  IGN: TIMING",%d,673,F(20,700),WHITE);' % (W, H, W // 2))

# ---- nothing but the engine and its callouts: no boost / pumps / lambda / footer bar / logo buttons.
# bindLogos() looks the logos up by id: without ours it would grab the native footer's logos and double-bind them.
js = rep(js, "bindLogos();bindDrag(glc)", "bindDrag(glc)")
js = rep(js, "drawBase();updateGL(dt);drawOver()", "updateGL(dt);drawOver()")

# ---- bigger engine
js = rep(js, "zoom+=((f?0.77:0.71)-zoom)", "zoom+=((f?0.94:0.86)-zoom)")
js = rep(js, "let yaw=YAW_A,zoom=0.71,pitch=0;", "let yaw=YAW_A,zoom=0.86,pitch=0;")

# ---- callouts: four per side, larger text; the right column is right-aligned to RX
js = rep(js, "const LAB=[[1171,64],[1171,152],[1171,240],[1171,328]];",
         "const LAB=[%s];" % ",".join("[%d,%d]" % (LAB_X, y) for y in SLOTS))
js = rep(js, "const LABR=[[1720,64],[1720,152],[1720,240],[1720,328]];",
         "const LABR=[%s];" % ",".join("[%d,%d]" % (RX, y) for y in SLOTS))
js = rep(js, 'const tx=left?x:x,align="left";', 'const tx=left?x:x-w,align="left";')
js = rep(js, "c.font=F(18,800);const w=Math.max(", "c.font=F(22,800);const w=Math.max(")
js = rep(js, "const bx=tx-10,by=y-26,bw=w+20,bh=78;", "const bx=tx-12,by=y-34,bw=w+24,bh=100;")
js = rep(js, 'txt(c,"C"+(i+1),tx,y-10,F(26,900),', 'txt(c,"C"+(i+1),tx,y-12,F(32,900),')
js = rep(js, "txt(c,l2,tx,y+16,F(18,800),", "txt(c,l2,tx,y+22,F(22,800),")
js = rep(js, "txt(c,l3,tx,y+38,F(18,800),", "txt(c,l3,tx,y+52,F(22,800),")
js = rep(js, "ay=y+16,bx=left?ax+18:ax-18;", "ay=y+22,bx=left?ax+18:ax-18;")

# ---- top banner, centred over the engine
js = rep(js, "c.font=F(19,900);const w=c.measureText(msg).width+36,x=1540-w/2,y=8;",
         "c.font=F(24,900);const w=c.measureText(msg).width+44,x=%d-w/2,y=8;" % (W // 2))
js = rep(js, "c.roundRect?c.roundRect(x,y,w,30,15):c.rect(x,y,w,30)", "c.roundRect?c.roundRect(x,y,w,38,19):c.rect(x,y,w,38)")
js = rep(js, "txt(c,msg,1540,y+15,F(19,900),", "txt(c,msg,%d,y+19,F(24,900)," % (W // 2))

js = js.replace(OLD_VER, VER)
assert js.isascii()
payload = base64.b64encode(js.encode()).decode()

# ---- HTML element: canvas sizes, engine canvas position; the bTres / DS1 logo buttons are removed
html = doc["elements"][0]["text"].replace(m.group(0), payload)
html = rep(html, "#bt8{position:relative;isolation:isolate;width:1920px;height:480px;",
           "#bt8{position:relative;isolation:isolate;width:%dpx;height:%dpx;" % (W, H))
html = rep(html, "#bt8base,#bt8over{left:0;top:0;width:1920px;height:480px}",
           "#bt8base,#bt8over{left:0;top:0;width:%dpx;height:%dpx}" % (W, H))
html = rep(html, "#bt8gl{left:1305px;top:0;width:460px;height:425px}",
           "#bt8gl{left:%dpx;top:%dpx;width:%dpx;height:%dpx}" % (GLX, GLY, GLW, GLH))
html = rep(html, '<canvas id="bt8base" width="1920" height="480">', '<canvas id="bt8base" width="%d" height="%d">' % (W, H))
html = rep(html, '<canvas id="bt8gl" width="460" height="425">', '<canvas id="bt8gl" width="%d" height="%d">' % (GLW, GLH))
html = rep(html, '<canvas id="bt8over" width="1920" height="480">', '<canvas id="bt8over" width="%d" height="%d">' % (W, H))
html, n_logos = re.subn(r'<div id="btLogo"[^>]*>.*?</div><div id="ds1Logo"[^>]*>.*?</div>', "", html, flags=re.S)
assert n_logos == 1
html = html.replace(OLD_VER, VER)
doc["elements"][0]["text"] = html
doc["elements"][0]["width"] = W
doc["elements"][0]["height"] = H

# the loader monitor carries the version tag too
for el in doc["elements"][1:]:
    if "monitor" in el:
        el["monitor"] = el["monitor"].replace(OLD_VER, VER)

doc["settings"] = {"showFooterBar": False}
data = json.dumps(doc, ensure_ascii=True, separators=(",", ":")).encode()
assert OLD_VER.encode() not in data
open(out, "wb").write(data)
print("wrote %s: %d bytes (%.2f MB of the 1.00 MB JSON limit)" % (out, len(data), len(data) / 1048576))
