"""Hardens a finished knock screen (V8 / RS3, 1920 or 800) so it can't be left black.

  python3 screens/harden_knock.py "<finished screen.json>" "<out.json>"

Field reports: some units show the screen entirely black except the DS1 / bTres logos, "randomly". The engine starts from a
hidden monitor that evals the base64 script inside the app's personalize() (which swallows every exception), and the script
had several single points of failure. This patch removes them:

 1. The "already loaded" flag (window.bt8v) was set BEFORE the setup code ran, so any exception during setup meant it was
    never retried. It is now set only after setup succeeded; the monitor retries a failed start (max 4 times, so a script that
    can never start doesn't re-parse 700 KB forever) and then writes an "Engine failed to start" note on the screen.
 2. attach() stored the canvas as "attached" before its 2D contexts existed. If getContext("2d") returned null (canvas memory
    pressure / lost context) every later frame threw on the null context and nothing retried. It now only attaches once both
    contexts exist, and otherwise tries again next frame.
 3. frameLoop had no error handling: one throw in step(), updateGL() or drawOver() repeated every frame and, since updateGL
    runs before drawOver, a failing 3D render blanked the 2D layer too. Each part is now isolated; after about a second of failures the
    screen detaches and attaches again from scratch (new contexts, new 3D renderer), at most 3 times.

The screen's version token changes (v8w-2 -> v8w-3, ...) so the flag/guard of an older build can never mask the new one.
"""
import base64, json, os, re, sys

NEXT = {"v8k-19": "v8k-20", "v8w-2": "v8w-3", "r3k-2": "r3k-3", "r3w-2": "r3w-3"}


def rep(text, old, new, name):
    assert text.count(old) == 1, "harden_knock: %s target found %d times: %r" % (name, text.count(old), old[:80])
    return text.replace(old, new)


def harden_js(js, ver):
    # 1. flag only once setup has run to the end (the loop is the last thing the setup does)
    js = rep(js, "if(window.bt8v!=='%s'){window.bt8v='%s';" % (ver, ver), "if(window.bt8v!=='%s'){" % ver, "flag head")
    js = rep(js, "window.bt8raf=requestAnimationFrame(frameLoop);\n/*DEBUG*/",
             "window.bt8raf=requestAnimationFrame(frameLoop);\nwindow.bt8v='%s';\n/*DEBUG*/" % ver, "flag tail")

    # 2. attach only once both 2D contexts exist
    js = rep(js,
             'if(b!==base){base=b;over=document.getElementById("bt8over");glc=document.getElementById("bt8gl");\n'
             '    bctx=base.getContext("2d");octx=over.getContext("2d");\n',
             'if(b!==base){const o=document.getElementById("bt8over"),bc=b.getContext("2d"),oc=o&&o.getContext("2d");\n'
             '    if(!bc||!oc)return false;                       // no canvas yet (memory pressure / lost context): try again next frame\n'
             '    base=b;over=o;glc=document.getElementById("bt8gl");bctx=bc;octx=oc;\n', "attach")

    # 3. isolate each part of a frame; recover after repeated failures
    js = rep(js, "function frameLoop(now){window.bt8raf=requestAnimationFrame(frameLoop);if(!attach())return;",
             "let fails=0,reattach=0;\n"
             "function frameLoop(now){window.bt8raf=requestAnimationFrame(frameLoop);\n"
             "  try{frameBody(now);fails=0}catch(e){\n"
             "    if(++fails===1&&window.console)console.error('knock screen frame error',e);\n"
             "    if(fails>=30&&reattach++<3){fails=0;base=null}   // ~1 s of failures: detach, the next frame attaches again from scratch (3 times at most)\n"
             "  }}\n"
             "function frameBody(now){if(!attach())return;", "frameLoop")
    base_call = "drawBase();" if "if(!hidden){drawBase();updateGL(dt);drawOver()}" in js else ""   # the 1920 builds draw their base layer here
    js = rep(js, "const dt=Math.min(0.15,gap/1000);last=now;sim.t=now/1000;step(dt);\n  if(!hidden){" + base_call + "updateGL(dt);drawOver()}",
             "const dt=Math.min(0.15,gap/1000);last=now;sim.t=now/1000;\n"
             "  let bad=0;\n"
             "  try{step(dt)}catch(e){bad=e}\n"
             "  if(!hidden){\n"
             + ("    try{drawBase()}catch(e){bad=bad||e}\n" if base_call else "") +
             "    try{updateGL(dt)}catch(e){glOK=false;bad=bad||e}   // a failing 3D render must not blank the 2D layers\n"
             "    try{drawOver()}catch(e){bad=bad||e}\n"
             "  }\n"
             "  wasHidden=hidden;\n"
             "  if(bad)throw bad;", "frame body")
    return js


def monitor(ver):
    # the app runs this through personalize() (brackets are special there, so none are used)
    return ("((window.bt8v==='%s'||(function(){var s=document.getElementById('bt8src');"
            "if(s){if((window.bt8n=(window.bt8n||0)+1)>4){var b=document.getElementById('bt8');"
            "if(b&&!document.getElementById('bt8err')){var e=document.createElement('div');e.id='bt8err';"
            "e.style.cssText='position:absolute;left:0;right:0;top:44%%;text-align:center;color:#fff;font:700 26px sans-serif;z-index:5';"
            "e.textContent='Engine failed to start. Please restart your bTres.';b.appendChild(e)}}"
            "else (0,eval)(atob(s.textContent))}})())&&'​')") % ver


def main(src, out):
    t = open(src).read()
    d = json.loads(t)
    old_mon = d["elements"][1]["monitor"]
    ver = next(v for v in NEXT if "window.bt8v==='%s'" % v in old_mon)
    new = NEXT[ver]
    assert old_mon == ("((window.bt8v==='%s'||(function(){var s=document.getElementById('bt8src');if(s)(0,eval)(atob(s.textContent))})())&&'​')" % ver), \
        "unexpected monitor: %r" % old_mon

    m = max(re.finditer(r"[A-Za-z0-9+/=]{100000,}", d["elements"][0]["text"]), key=lambda x: len(x.group(0)))
    js = base64.b64decode(m.group(0)).decode()
    assert ("window.bt8v!=='%s'" % ver) in js
    js = harden_js(js, ver).replace(ver, new)
    assert js.isascii()
    d["elements"][0]["text"] = d["elements"][0]["text"].replace(m.group(0), base64.b64encode(js.encode()).decode()).replace(ver, new)
    d["elements"][1]["monitor"] = monitor(new)
    assert "[" not in d["elements"][1]["monitor"] and "<" not in d["elements"][1]["monitor"]
    data = json.dumps(d, ensure_ascii=True, separators=(",", ":")).encode()
    assert ver.encode() not in data
    open(out, "wb").write(data)
    print("wrote %s (%s -> %s): %d bytes" % (out, ver, new, len(data)))


if __name__ == "__main__":
    main(*sys.argv[1:3])
