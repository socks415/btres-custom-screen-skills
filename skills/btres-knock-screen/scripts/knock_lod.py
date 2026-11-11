"""Shared patches for the knock screens' 3D engine code (decoded JS text), used by patch_v8_glhide.py and
make_rs3_knock_screen.py (whose engine comes from a different prototype, so it needs the same patches applied).

lod():   slightly coarser geometry / a smaller shadow map: fewer vertices to build at load and to draw every frame,
         hardly visible at the size the engine is shown.
loading(): the engine is built a moment after the screen appears: until its first frame has been drawn the callout
         lines point at the middle of the engine area and a "LOADING ENGINE" note sits there.
"""


def _rep(js, old, new, name):
    assert js.count(old) >= 1, "knock_lod: %s target missing: %r" % (name, old[:70])
    return js.replace(old, new)


def lod(js):
    js = _rep(js, "key.shadow.mapSize.set(2048,2048)", "key.shadow.mapSize.set(1024,1024)", "shadow map")
    js = _rep(js, "bevelSegments:3,curveSegments:6", "bevelSegments:2,curveSegments:4", "extrude")
    js = _rep(js, "seg||40", "seg||28", "cylinders")
    js = _rep(js, "TorusGeometry(R,t,14,48,", "TorusGeometry(R,t,10,32,", "torus")
    js = _rep(js, "Math.max(24,pts.length*14),r,10,", "Math.max(20,pts.length*10),r,8,", "tubes")
    js = _rep(js, "SphereGeometry(20,48,24)", "SphereGeometry(20,32,16)", "env sphere")
    return js


def loading(js):
    js = _rep(js, "cylObjs=[],focusLight,glOK=true;", "cylObjs=[],focusLight,glOK=true,glReady=false;", "flag")
    js = _rep(js, "function project(obj,local){",
              "function project(obj,local){if(!glReady)return {x:GL.x+GL.w/2,y:GL.y+GL.h/2};", "project")
    js = _rep(js, "const o=cylObjs[i];const p=project(o.g,new THREE.Vector3(0,0.42,0));",
              "const o=cylObjs[i];const p=glReady?project(o.g,new THREE.Vector3(0,0.42,0)):project();", "anchor")
    js = _rep(js, "renderer.render(scene,camera);\n}", "renderer.render(scene,camera);glReady=true;\n}", "ready")
    js = _rep(js, "  if(f){const cy=cyl[f.c],yb=",
              '  if(glOK&&!glReady){c.save();const mx=GL.x+GL.w/2,my=GL.y+GL.h/2,lt="LOADING ENGINE\\u2026";c.font=F(26,800);const bw=c.measureText(lt).width+36,bh=46;c.fillStyle="#000";c.beginPath();c.roundRect?c.roundRect(mx-bw/2,my-bh/2,bw,bh,10):c.rect(mx-bw/2,my-bh/2,bw,bh);c.fill();c.globalAlpha=0.6+0.35*Math.sin(sim.t*4);txt(c,lt,mx,my,F(26,800),"#fff");c.restore()}\n'
              "  if(f){const cy=cyl[f.c],yb=", "loading text")
    # build the engine a moment after the first frame, so the loading note is on screen while it builds
    js = _rep(js, "renderer=null;cylObjs=[];glOK=true;\n    layout();try{initGL()}catch(e){glOK=false}layout();bindLogos();bindDrag(glc)}",
              "renderer=null;cylObjs=[];glOK=true;glReady=false;\n    layout();setTimeout(()=>{try{initGL()}catch(e){glOK=false}layout()},60);bindLogos();bindDrag(glc)}", "deferred init")
    return js
