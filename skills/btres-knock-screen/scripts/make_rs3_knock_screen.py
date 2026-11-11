"""Builds the bTres 2.5 TFSI (RS3 / TT RS five-cylinder) Knock Screens: the 1920x480 screen and the 800x480-unit
screen (designed on 1143 x 686, the 0.7-scaled layout).

  python3 screens/make_rs3_knock_screen.py "<V8 1920 build .json>" "<bTres 2.5 TFSI Knock Screen.html>" "<out dir>"

Both screens are derived from the finished V8 Knock Screen build, which already carries the alert levels, frame-rate
budget, off-screen pause, last-pull data and so on. What changes for the five-cylinder car:
  - the 3D engine is the inline five from the 2.5 TFSI prototype (single bank, one set of pumps and one lambda);
  - knock / ignition come from wkrv..wkrv_5 and zwcalcar..zwcalcar_5;
  - HPFP B2, lambda B2 and the "B1" in the labels are gone;
  - the boost target comes from pvds_w, oil temp from toelk_w when toel is not logged.
The 800 version shows only the engine and its callouts (no footer bar, no logo buttons).
"""
import base64
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import knock_lod

src, proto, outdir = sys.argv[1:4]
OLD_VER = "v8k-19"
VER_1920, VER_800 = "r3k-2", "r3w-2"

t = open(src).read()
doc = json.loads(t)
m = max(re.finditer(r"[A-Za-z0-9+/=]{100000,}", t), key=lambda x: len(x.group(0)))
raw = base64.b64decode(m.group(0)).decode()
k = raw.index("if(window.bt8v!==")
three, core = raw[:k], raw[k:]
assert OLD_VER in core

ph = open(proto, encoding="utf-8").read()
ps = ph.index("function makeTex(")
pe = ph.index("let _halo=null;")
engine = ph[ps:pe]
engine = engine.replace('document.getElementById("glerr").style.display="block";', "")
assert "glerr" not in engine


def rep(text, old, new, count=1):
    assert text.count(old) == count, "patch target missing or not unique: %r (%d)" % (old[:90], text.count(old))
    return text.replace(old, new)


# ======================================================================== 1920 x 480 (five cylinders)
js = core

# ---- the inline-five engine (everything from makeTex up to the halo/number sprites)
a = js.index("function makeTex(")
b = js.index("let _halo=null;")
js = js[:a] + engine + js[b:]
js = rep(js, "pivot.rotation.y=yaw;pivot.rotation.x=pitch;", "pivot.rotation.y=yaw;pivot.rotation.x=pitch;pivot.rotation.z=-yaw*1.4;")
js = rep(js, "zoom=0.71,pitch=0;", "zoom=0.76,pitch=0;")
js = rep(js, "zoom+=((f?0.77:0.71)-zoom)", "zoom+=((f?0.82:0.76)-zoom)")

# ---- five cylinders: wkrv..wkrv_5 and zwcalcar..zwcalcar_5
# (the V8 build lists its variables in cylinder order for the firing order; this car's five are simply 1 to 5)
# The variables are numbered in firing order 1-2-4-5-3 (wkrv = cyl 1, wkrv_2 = cyl 2, wkrv_3 = cyl 4, wkrv_4 = cyl 5,
# wkrv_5 = cyl 3), so entry i here (physical cylinder i+1) reads the variable that belongs to that cylinder.
js, n1 = re.subn(r'const KN=\[[^\]]*\];', 'const KN=["wkrv","wkrv_2","wkrv_5","wkrv_3","wkrv_4"];', js)
js, n2 = re.subn(r'const IG=\[[^\]]*\];', 'const IG=["zwcalcar","zwcalcar_2","zwcalcar_5","zwcalcar_3","zwcalcar_4"];', js)
assert n1 == 1 and n2 == 1

# ---- callouts: the prototype's staggered layout (C1, C3, C5 on the left, C2, C4 on the right)
POS_1920 = "const POS=[{l:1,y:328},{l:0,y:262},{l:1,y:196},{l:0,y:130},{l:1,y:64}];"
js = rep(js, "const LAB=[[1171,64],[1171,152],[1171,240],[1171,328]];\nconst LABR=[[1720,64],[1720,152],[1720,240],[1720,328]];",
         "const LABX=1171,LABRX=1720;\n" + POS_1920)
js = rep(js, "const left=i<4,slot=left?3-i:7-i,[x,y]=(left?LAB:LABR)[slot],isF=",
         "const left=!!POS[i].l,x=left?LABX:LABRX,y=POS[i].y,isF=")

# ---- data: boost target is the pre-throttle target (pvds_w); oil temp is toelk_w on this ECU
js = rep(js, 'pt=GV("psrs_w")', 'pt=GV("pvds_w")')
js = rep(js, '["tans","toel","tmot","Gbx_tOilConv"].forEach', '["tans",GV("toel")!==null?"toel":"toelk_w","tmot","Gbx_tOilConv"].forEach')

# ---- one fuel-pump pair (LPFP, HPFP) and one lambda block, re-centred between the boost gauge and the engine
# legend: drawn on the overlay canvas (the base canvas sits under the engine, which hid the start of the text)
LEGEND_1920 = 'txt(c,"K: KNOCK  \\u00b7  IGN: TIMING",1171,403,F(18,700),WHITE,"left");'
js = rep(js, 'txt(c,"K: KNOCK CORR.  \\u00b7  IGN: TIMING",1898,400,F(18,700),WHITE,"right");', "")
js = rep(js, "c.clearRect(0,0,1920,480);", "c.clearRect(0,0,1920,480);" + LEGEND_1920)
js = rep(js, 'drawPump(c,612,"LPFP",sim.lp,sim.lpT,sim.lastLp,6,1);', 'drawPump(c,720,"LPFP",sim.lp,sim.lpT,sim.lastLp,6,1);')
js = rep(js, 'drawPump(c,828,"HPFP B1",', 'drawPump(c,940,"HPFP",')
js = rep(js, '  drawPump(c,1045,"HPFP B2",sim.hp[1],sim.hpT[1],sim.lastHp[1],20,1," MPa");\n', "")
a = js.index("function drawLambda(c){")
b = js.index("function unitVal(")
LAMBDA = r'''function drawLambda(c){
  txt(c,"LAMBDA",780,258,F(22,800));txt(c,sim.lam[0].toFixed(2),780,296,F(50,900));txt(c,`L ${sim.lastLam[0].toFixed(2)}`,780,334,F(24,800),CYAN);
  const g={e:900,dir:-1};
  {const top=220,bot=412,tw=28,bw=56;const p=[[g.e,top],[g.e+g.dir*tw,top],[g.e+g.dir*bw,bot],[g.e,bot]];
    c.save();c.beginPath();p.forEach((q,k)=>k?c.lineTo(q[0],q[1]):c.moveTo(q[0],q[1]));c.closePath();c.fillStyle="#0b0b0b";c.fill();c.clip();
    const y=LY(sim.lam[0]);const gr=c.createLinearGradient(0,y,0,bot);gr.addColorStop(0,"#ff2a1a");gr.addColorStop(1,"#7a0905");c.fillStyle=gr;c.fillRect(g.e-80,y,160,bot-y);
    c.restore();
    c.beginPath();p.forEach((q,k)=>k?c.lineTo(q[0],q[1]):c.moveTo(q[0],q[1]));c.closePath();c.lineWidth=2;c.strokeStyle=WHITE;c.stroke();
    for(let v=0.7;v<=1.1001;v+=0.05){const yy=LY(v);c.beginPath();c.moveTo(g.e,yy);c.lineTo(g.e+g.dir*(Math.abs((v*100)%10)<1e-6||Math.abs((v*100)%10-10)<1e-6?14:8),yy);c.lineWidth=2;c.strokeStyle="#d8d8d8";c.stroke()}
    const my=LY(sim.lam[0]);c.beginPath();c.moveTo(g.e-g.dir*2,my);c.lineTo(g.e-g.dir*14,my-7);c.lineTo(g.e-g.dir*14,my+7);c.closePath();c.fillStyle=WHITE;c.fill()}
  [1.1,1.0,0.9,0.8,0.7].forEach(v=>txt(c,v.toFixed(2),942,LY(v),F(20,800)));
}
'''
js = js[:a] + LAMBDA + js[b:]
js = knock_lod.lod(js)   # the prototype engine replaced the V8 one above: coarsen it too (the loading-engine state is already in the V8 base)
js = js.replace(OLD_VER, VER_1920)


def pack(jscode, ver_old, ver_new, html_doc, name, html_patch=None):
    jscode = jscode.encode("ascii", "backslashreplace").decode()
    assert jscode.isascii()
    payload = base64.b64encode((three + jscode).encode()).decode()
    d = json.loads(json.dumps(html_doc))
    h = d["elements"][0]["text"].replace(m.group(0), payload)
    h = h.replace(OLD_VER, ver_new)
    if html_patch:
        h = html_patch(h)
        d["elements"][0]["width"] = W800
        d["elements"][0]["height"] = H800
    d["elements"][0]["text"] = h
    for el in d["elements"][1:]:
        if "monitor" in el:
            el["monitor"] = el["monitor"].replace(OLD_VER, ver_new)
    d["settings"] = {"showFooterBar": False}
    data = json.dumps(d, ensure_ascii=True, separators=(",", ":")).encode()
    assert OLD_VER.encode() not in data
    p = os.path.join(outdir, name)
    open(p, "wb").write(data)
    print("wrote %s: %d bytes (%.2f MB of the 1.00 MB JSON limit)" % (p, len(data), len(data) / 1048576))


# ======================================================================== 800 x 480 unit (1143 x 686 design)
W800, H800 = 1143, 686
GLX, GLY, GLW, GLH = 260, -15, 620, 650
RX = 1125
LAB_X = 18
POS_800 = "const POS=[{l:1,y:520},{l:0,y:415},{l:1,y:310},{l:0,y:205},{l:1,y:100}];"

j8 = js
j8 = rep(j8, "c.width=1920*RES;c.height=480*RES", "c.width=%d*RES;c.height=%d*RES" % (W800, H800))
j8 = rep(j8, "const GL={x:1305,y:0,w:460,h:425};", "const GL={x:%d,y:%d,w:%d,h:%d};" % (GLX, GLY, GLW, GLH))
j8 = rep(j8, "c.clearRect(0,0,1920,480);" + LEGEND_1920,
         'c.clearRect(0,0,%d,%d);txt(c,"K: KNOCK CORR.  \\u00b7  IGN: TIMING",%d,673,F(20,700),WHITE);' % (W800, H800, W800 // 2))
# only the engine and its callouts: no boost / pumps / lambda / footer bar / logo buttons
j8 = rep(j8, "drawBase();updateGL(dt);drawOver()", "updateGL(dt);drawOver()")
j8 = rep(j8, "bindLogos();bindDrag(glc)", "bindDrag(glc)")
j8 = rep(j8, "zoom=0.76,pitch=0;", "zoom=0.74,pitch=0;")
j8 = rep(j8, "zoom+=((f?0.82:0.76)-zoom)", "zoom+=((f?0.82:0.74)-zoom)")
j8 = rep(j8, "const LABX=1171,LABRX=1720;\n" + POS_1920, "const LABX=%d,LABRX=%d;\n%s" % (LAB_X, RX, POS_800))
j8 = rep(j8, 'const tx=left?x:x,align="left";', 'const tx=left?x:x-w,align="left";')
j8 = rep(j8, "c.font=F(18,800);const w=Math.max(", "c.font=F(22,800);const w=Math.max(")
j8 = rep(j8, "const bx=tx-10,by=y-26,bw=w+20,bh=78;", "const bx=tx-12,by=y-34,bw=w+24,bh=100;")
j8 = rep(j8, 'txt(c,"C"+(i+1),tx,y-10,F(26,900),', 'txt(c,"C"+(i+1),tx,y-12,F(32,900),')
j8 = rep(j8, "txt(c,l2,tx,y+16,F(18,800),", "txt(c,l2,tx,y+22,F(22,800),")
j8 = rep(j8, "txt(c,l3,tx,y+38,F(18,800),", "txt(c,l3,tx,y+52,F(22,800),")
j8 = rep(j8, "ay=y+16,bx=left?ax+18:ax-18;", "ay=y+22,bx=left?ax+18:ax-18;")
j8 = rep(j8, "c.font=F(19,900);const w=c.measureText(msg).width+36,x=1540-w/2,y=8;",
         "c.font=F(24,900);const w=c.measureText(msg).width+44,x=%d-w/2,y=8;" % (W800 // 2))
j8 = rep(j8, "c.roundRect?c.roundRect(x,y,w,30,15):c.rect(x,y,w,30)", "c.roundRect?c.roundRect(x,y,w,38,19):c.rect(x,y,w,38)")
j8 = rep(j8, "txt(c,msg,1540,y+15,F(19,900),", "txt(c,msg,%d,y+19,F(24,900)," % (W800 // 2))
j8 = j8.replace(VER_1920, VER_800)


def html800(h):
    h = rep(h, "#bt8{position:relative;isolation:isolate;width:1920px;height:480px;",
            "#bt8{position:relative;isolation:isolate;width:%dpx;height:%dpx;" % (W800, H800))
    h = rep(h, "#bt8base,#bt8over{left:0;top:0;width:1920px;height:480px}",
            "#bt8base,#bt8over{left:0;top:0;width:%dpx;height:%dpx}" % (W800, H800))
    h = rep(h, "#bt8gl{left:1305px;top:0;width:460px;height:425px}",
            "#bt8gl{left:%dpx;top:%dpx;width:%dpx;height:%dpx}" % (GLX, GLY, GLW, GLH))
    h = rep(h, '<canvas id="bt8base" width="1920" height="480">', '<canvas id="bt8base" width="%d" height="%d">' % (W800, H800))
    h = rep(h, '<canvas id="bt8gl" width="460" height="425">', '<canvas id="bt8gl" width="%d" height="%d">' % (GLW, GLH))
    h = rep(h, '<canvas id="bt8over" width="1920" height="480">', '<canvas id="bt8over" width="%d" height="%d">' % (W800, H800))
    h, n = re.subn(r'<div id="btLogo"[^>]*>.*?</div><div id="ds1Logo"[^>]*>.*?</div>', "", h, flags=re.S)
    assert n == 1
    return h


pack(js, OLD_VER, VER_1920, doc, "bTres-RS3-Knock-Screen.json")
pack(j8, OLD_VER, VER_800, doc, "bTres-RS3-Knock-Screen-800.json", html800)
