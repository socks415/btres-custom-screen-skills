#!/usr/bin/env python3
"""Builds a bTres knock screen for one car + one unit size.

  python3 build.py --car v8|rs3 --unit s|m1x1 --out <dir>

  --car   v8  = 6/7/8 series (V8, 8 cylinders)      rs3 = RS3 / TT RS (2.5 TFSI, 5 cylinders)
  --unit  s   = S-series, 1920x480                   m1x1 = M1 / X1, 800x480 (designed on 1143x686, shown at 0.7)

Writes <out>/<name>.json and <out>/<name>.json.zip (the zip is what the gallery / "install from file" takes).
Python 3 standard library only. The base screen and the 5-cylinder engine prototype are in ../assets.
"""
import argparse, json, os, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "..", "assets")
BASE = os.path.join(ASSETS, "bTres-V8-Knock-Screen.base.json")
PROTO = os.path.join(ASSETS, "bTres-2.5-TFSI-engine-prototype.html")
NAMES = {("v8", "s"): "bTres-V8-Knock-Screen", ("v8", "m1x1"): "bTres-V8-Knock-Screen-800",
         ("rs3", "s"): "bTres-RS3-Knock-Screen", ("rs3", "m1x1"): "bTres-RS3-Knock-Screen-800"}

ap = argparse.ArgumentParser()
ap.add_argument("--car", required=True, choices=["v8", "rs3"])
ap.add_argument("--unit", required=True, choices=["s", "m1x1"])
ap.add_argument("--out", required=True)
a = ap.parse_args()

name = NAMES[(a.car, a.unit)]
os.makedirs(a.out, exist_ok=True)
dest = os.path.join(a.out, name + ".json")
with tempfile.TemporaryDirectory() as tmp:
    if a.car == "v8" and a.unit == "s":
        shutil.copy(BASE, dest)                       # the base build is the V8 1920 screen
    elif a.car == "v8":
        subprocess.run([sys.executable, os.path.join(HERE, "make_v8_knock_screen_800.py"), BASE, dest], check=True)
    else:
        subprocess.run([sys.executable, os.path.join(HERE, "make_rs3_knock_screen.py"), BASE, PROTO, tmp], check=True)
        shutil.copy(os.path.join(tmp, name + ".json"), dest)

data = open(dest, "rb").read()
json.loads(data)
assert len(data) < 1048576, "over the 1.00 MB screen JSON limit"
with zipfile.ZipFile(dest + ".zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(dest, name + ".json")
print("built %s (%.2f MB of the 1.00 MB limit)\n  %s\n  %s.zip" % (name, len(data) / 1048576, dest, dest))
