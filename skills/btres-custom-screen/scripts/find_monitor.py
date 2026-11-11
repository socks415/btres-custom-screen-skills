#!/usr/bin/env python3
"""Look up DS1 monitors (variable name, description, unit) in the bundled lists.

  python3 find_monitor.py --car v8|rs3 [keyword ...]      # words are ANDed, matched against name + description
  python3 find_monitor.py --car v8 --exact nmot_w psrg_w  # check that variable names exist for that car

  --car   v8  = 6/7/8 series Audi (reference/ds1-monitors/6-7-8-series.json)
          rs3 = RS3 / TT RS     (reference/ds1-monitors/rs3-ttrs.json)
With no keywords it prints the whole list. Use it before using a variable in a screen: if a name is not found, do not
use it; ask the user.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {"v8": "6-7-8-series.json", "rs3": "rs3-ttrs.json"}
ap = argparse.ArgumentParser()
ap.add_argument("--car", required=True, choices=FILES)
ap.add_argument("--exact", action="store_true", help="arguments are exact variable names to check")
ap.add_argument("words", nargs="*")
a = ap.parse_args()
rows = json.load(open(os.path.join(HERE, "..", "reference", "ds1-monitors", FILES[a.car])))
by = {r["var"]: r for r in rows}

def show(r):
    sc = "" if r["scale"] == 1 and r["offset"] == 0 else "  (x%g%+g)" % (r["scale"], r["offset"]) if r["offset"] else "  (x%g)" % r["scale"]
    print("%-28s %-12s %s%s" % (r["var"], r["unit"] or "-", r["desc"], sc))

if a.exact:
    bad = 0
    for w in a.words:
        if w in by:
            show(by[w])
        else:
            bad += 1
            print("%-28s NOT FOUND for this car" % w)
    sys.exit(1 if bad else 0)
ws = [w.lower() for w in a.words]
n = 0
for r in rows:
    h = (r["var"] + " " + r["desc"]).lower()
    if all(w in h for w in ws):
        show(r); n += 1
print("-- %d match(es) in %s" % (n, FILES[a.car]), file=sys.stderr)
