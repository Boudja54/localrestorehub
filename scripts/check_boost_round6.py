#!/usr/bin/env python3
"""Doorway gate for boost rounds.

Extracts each page's injected block (first '24-Hour' H2 → 'Nearby Service Areas'),
normalises it (city name + 'california' stripped, lowercase, words > 3 chars) and
compares ALL pairs by Jaccard.

FAIL (exit 1) on any pair > THRESHOLD that involves a page of the target round.
Non-target pairs (legacy rounds 1-5) are reported as warnings only.

Usage: python3 scripts/check_boost_round6.py [city ...]
"""
import glob
import itertools
import re
import sys

THRESHOLD = 0.30
DIR = "src/pages"
ROUND6 = ["Camarillo", "Duarte", "Covina", "Azusa", "Santa Ana",
          "Midway City", "Artesia", "Arcadia", "Lawndale"]


def words(text, city):
    t = text.lower().replace(city.lower(), " ").replace("california", " ")
    return {w for w in re.sub(r"[^a-z ]", " ", t).split() if len(w) > 3}


blocks = {}
for f in sorted(glob.glob(f"{DIR}/water-damage-repair-*.astro")):
    src = open(f).read()
    city = re.search(r'const CITY = "([^"]*)"', src)
    start, end = src.find("24-Hour"), src.find("Nearby Service Areas")
    if city and start != -1 < end:
        blocks[city.group(1)] = words(src[start:end], city.group(1))

targets = set(sys.argv[1:] or ROUND6)
pairs = list(itertools.combinations(sorted(blocks), 2))
scored = sorted(((len(blocks[a].intersection(blocks[b])) / len(blocks[a].union(blocks[b])), a, b)
                 for a, b in pairs), reverse=True)

fails = [x for x in scored if x[0] > THRESHOLD and (x[1] in targets or x[2] in targets)]
legacy = [x for x in scored if x[0] > THRESHOLD and x not in fails]

print(f"blocks={len(blocks)} pairs={len(pairs)} threshold={THRESHOLD}")
print(f"max pair involving target round: {max((x for x in scored if x[1] in targets or x[2] in targets))[0]:.2f}")
if legacy:
    print(f"legacy warnings ({len(legacy)}) — rounds 1-5, out of scope:")
    for j, a, b in legacy:
        print(f"  {j:.2f}  {a} vs {b}")
if fails:
    print("RISK in target round:")
    for j, a, b in fails:
        print(f"  {j:.2f}  {a} vs {b}")
    sys.exit(1)
print("RESULT: doorway check PASSED")
