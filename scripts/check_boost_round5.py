#!/usr/bin/env python3
"""SEO boost round 5 verification: duplicate FAQ H3s, Jaccard on injected blocks, forbidden terms."""
import glob, re, sys, itertools

PAGES = sorted(glob.glob('src/pages/water-damage-repair-*.astro'))
BOOST = ['san-marino', 'oxnard', 'moorpark', 'fullerton', 'cerritos']

# ---- 1. duplicate FAQ question strings across ALL pages
h3 = []
for f in PAGES:
    h3 += re.findall(r'mb-2">([^<]*)', open(f).read())
dups = {q for q in h3 if h3.count(q) > 1}
print(f'FAQ questions total: {len(h3)} | duplicates: {len(dups)}')
for d in dups:
    print('  DUP:', d)

# ---- 2. Jaccard on the INJECTED blocks only (24-Hour -> Nearby Service Areas)
blocks, names = {}, {}
for f in PAGES:
    src = open(f).read()
    if '24-Hour' not in src:
        continue
    city = re.search(r'const CITY = "([^"]*)"', src).group(1)
    a = src.index('24-Hour')
    b = src.index('Nearby Service Areas')
    txt = src[a:b]
    norm = txt.lower().replace(city.lower(), ' ')
    norm = re.sub(r'[^a-z ]', ' ', norm)
    blocks[city] = {w for w in norm.split() if len(w) > 3}
    names[city] = f

print(f'\nPages with boost blocks: {len(blocks)}')
worst = 0.0
risky = []
for x, y in itertools.combinations(sorted(blocks), 2):
    s = len(blocks[x] & blocks[y]) / len(blocks[x] | blocks[y])
    worst = max(worst, s)
    if s > 0.30:
        risky.append((x, y, s))
for x, y, s in risky:
    print(f'  RISK {x} vs {y} -> {s:.2f}')
print(f'Max Jaccard pair: {worst:.2f} (threshold 0.30) | pairs over threshold: {len(risky)}')

# ---- 3. round-5 pairwise detail
r5 = [re.search(r'const CITY = "([^"]*)"', open(f'src/pages/water-damage-repair-{s}-ca.astro').read()).group(1) for s in BOOST]
print('\nRound 5 pairwise:')
for x, y in itertools.combinations(r5, 2):
    if x in blocks and y in blocks:
        s = len(blocks[x] & blocks[y]) / len(blocks[x] | blocks[y])
        print(f'  {x:12s} vs {y:12s} {s:.2f}')

# ---- 4. forbidden terms in the injected blocks + presence of tel link / hours / zip
forbidden = ['mold', 'moisissure', 'sewage', 'sewer']
print('\nForbidden-term check on round-5 blocks:')
for slug in BOOST:
    src = open(f'src/pages/water-damage-repair-{slug}-ca.astro').read()
    a, b = src.index('24-Hour'), src.index('Nearby Service Areas')
    chunk = src[a:b].lower()
    hits = [t for t in forbidden if t in chunk]
    tel = src.count('PHONE_TEL')
    hours = '10:00 AM to 2:00 AM' in src[a:b]
    zipv = re.search(r'const ZIP = "([^"]*)"', src).group(1)
    zipok = zipv in src[a:b]
    print(f'  {slug:12s} forbidden={hits or "none"} tel_refs={tel} hours={hours} zip({zipv})={zipok}')

sys.exit(1 if (dups or risky) else 0)
