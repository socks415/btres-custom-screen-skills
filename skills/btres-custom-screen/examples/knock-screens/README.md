# Knock screens (example)

3D-engine screens with per-cylinder knock correction and ignition-timing callouts, plus boost, fuel pumps and lambda: one for a 6/7/8 series V8 and one for an RS3 / TT RS 5-cylinder, each in S-series (1920x480) and M1 / X1 (800x480) layouts. They are examples of a large, WebGL-based custom screen; they are not the skill itself.

Build any of the four:

```
python3 scripts/build.py --car v8|rs3 --unit s|m1x1 --out ./out
```

`GUIDE.md` explains how they are built and how to rebuild or adapt them, `REFERENCE.md` documents their behaviour (alert levels, last-pull rules, firing-order mapping, layout geometry). Python 3 only. They were checked in headless Chrome and by a V8 owner in a car, not on every unit type.
