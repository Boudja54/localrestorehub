#!/usr/bin/env python3
"""
LocalRestoreHub — Weekly Expansion Engine (Phase 3)
====================================================
Automatically adds a batch of NEW California cities each run, drawing ONLY
from the official Marketcall zip list (scripts/marketcall-zips.json).

Batch size : BATCH_SIZE (default 10) — one batch per week via cron.
Source of truth : scripts/marketcall-zips.json (official offer #12330 zips)
Already-live cities (in cities-seed.json) are skipped. Excluded metros are skipped.

RUN
---
    python3 scripts/expand_weekly.py
    (dry-run: python3 scripts/expand_weekly.py --dry-run)

The engine then calls gen_ca_pages.py (generates .astro pages + cities.json),
runs the Astro build, commits, and pushes to origin/main so Cloudflare deploys
the new batch with zero human intervention.
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(ROOT, "scripts", "cities-seed.json")
ZIPS_PATH = os.path.join(ROOT, "scripts", "marketcall-zips.json")
GEN_PATH = os.path.join(ROOT, "scripts", "gen_ca_pages.py")

BATCH_SIZE = 10  # new cities per run (one batch per week)

# Ultra-competitive metros to exclude (original campaign brief) + LA core neighborhoods.
# ALL other cities in marketcall-zips.json are fair game — the official list is the source of truth.
EXCLUDED_CITIES = [
    # The 6 metros named in the original campaign brief
    "los angeles", "beverly hills", "santa monica", "long beach",
    "irvine", "anaheim",
    # Other major metros (would be hyper-competitive)
    "san diego", "san francisco", "sacramento", "san jose", "oakland",
    "fresno", "bakersfield",
    # LA city core / neighborhoods (duplicate of "los angeles")
    "hollywood", "west hollywood", "east los angeles", "venice",
    "north hollywood", "van nuys", "reseda", "canoga park", "sylmar",
    "san pedro", "huntington park", "boyle heights", "pacoima",
    "arleta", "sun valley", "panorama city", "tarzana", "studio city",
    "valley village", "universal city", "sherman oaks", "encino",
    "woodland hills", "west hills", "winnetka", "chatsworth",
    "pasadena", "glendale", "burbank", "culver city",
    # OCR noise / micro-neighborhoods / non-municipalities
    "rosewood", "la fresa", "los nietos", "naylor place", "belmont shore",
    "naval air station point mugu", "brandeis", "hazard", "lennox",
    "marina del rey", "playa del rey", "topanga", "oak park", "stanton",
    "rossmoor", "seal beach", "wilmington", "bradbury", "pacific palisades",
    "pacific palisade", "cudahy", "la habra heights", "santa fe springs",
    "los alamitos", "calabasas", "thousand oaks", "newbury park",
    "rolling hills estates", "rancho palos verdes", "rancho palos ve",
    "rancho palos verde", "rolling hills", "la cañada flintri",
    "flintridge", "mount wilson", "sunset beach", "surfside",
    "hawaiian garden", "hawaiian gardens", "rancho dominguez",
    "east rancho dominguez", "la crescenta", "montrose", "sunland",
    "tujunga", "avalon", "harbor city", "signal hill", "lomita",
    "city of industry", "la puente", "hacienda heights",
]

# Keywords rotated across new cities (must stay strictly water-related)
KEYWORDS = [
    "Water Damage Restoration",
    "Flood Cleanup",
    "Emergency Water Extraction",
]

# Regional context templates — keyed by zip prefix; filled with city/county
REGION_CONTEXTS = {
    "900": ("Los Angeles County", "the Los Angeles basin",
            "Los Angeles County's dense urban plumbing networks and frequent winter storms put older homes at real risk of sudden water failures. Aging supply lines and storm drainage systems can fail without warning, leaving homeowners facing serious water damage."),
    "902": ("Los Angeles County", "the coastal South Bay",
            "the coastal South Bay area of Los Angeles County, where ocean proximity, older infrastructure, and heavy winter rain create real water damage risks for homes and businesses alike."),
    "903": ("Los Angeles County", "the South Bay",
            "the South Bay, where dense older neighborhoods and aging plumbing make sudden pipe and water line failures a genuine concern for local homeowners."),
    "904": ("Los Angeles County", "the beach cities",
            "the beach cities, where salt air corrodes older pipes and winter storms bring heavy runoff — a combination that makes water emergencies all too common."),
    "905": ("Los Angeles County", "the South Bay",
            "the South Bay, where decades-old supply lines and storm-driven runoff put many homes at risk of sudden water damage during heavy rain."),
    "906": ("Los Angeles County", "the Gateway Cities",
            "the Gateway Cities area, where dense older neighborhoods and aging water infrastructure make pipe failures and storm flooding a recurring concern."),
    "907": ("Los Angeles County", "the Harbor Area",
            "the Harbor Area, where older homes, coastal moisture, and heavy winter storms combine to create frequent water damage emergencies."),
    "908": ("Los Angeles County", "the Long Beach area",
            "the Long Beach area, where aging coastal plumbing and seasonal storms leave many homes vulnerable to sudden water damage."),
    "910": ("Los Angeles County", "the foothill communities",
            "the foothill communities, where hillside runoff during winter storms and older supply lines create real water damage risks for homeowners."),
    "911": ("Los Angeles County", "the San Gabriel Valley",
            "the San Gabriel Valley, where older homes and aging municipal water lines make sudden pipe failures and water emergencies a real concern."),
    "912": ("Los Angeles County", "the Glendale area",
            "the Glendale area, where dense neighborhoods and older plumbing infrastructure put homes at risk of sudden water damage during storms and cold snaps."),
    "913": ("Los Angeles County", "the San Fernando Valley",
            "the San Fernando Valley, where hillside runoff, aging pipes, and winter storms combine to create real water damage risks for local homeowners."),
    "914": ("Los Angeles County", "the San Fernando Valley",
            "the San Fernando Valley, where older neighborhoods and storm-driven runoff make water emergencies a recurring seasonal problem."),
    "915": ("Los Angeles County", "the San Fernando Valley",
            "the San Fernando Valley, where dense older housing and aging water lines mean sudden leaks and storm flooding can strike without warning."),
    "916": ("Los Angeles County", "the San Fernando Valley",
            "the San Fernando Valley, where a mix of hillside homes and older plumbing creates genuine water damage risks during heavy rain."),
    "917": ("Los Angeles County", "the San Gabriel Valley",
            "the San Gabriel Valley, where aging infrastructure and seasonal storms leave many homes vulnerable to sudden water damage and flooding."),
    "918": ("Los Angeles County", "the San Gabriel Valley",
            "the San Gabriel Valley, where older neighborhoods and outdated supply lines make water emergencies a real and recurring concern."),
    "926": ("Orange County", "Orange County",
            "Orange County, where coastal weather and older residential plumbing combine to create real water damage risks for homeowners."),
    "927": ("Orange County", "Orange County",
            "Orange County, where aging homes and winter rain events put many residents at risk of sudden water damage emergencies."),
    "928": ("Orange County", "Orange County",
            "Orange County, where a mix of older neighborhoods and heavy seasonal rain makes pipe failures and water damage a genuine concern."),
    "930": ("Ventura County", "Ventura County",
            "Ventura County, where winter storms bring heavy rain and river flooding, and older farmhouse plumbing is especially prone to sudden failures."),
    "935": ("Los Angeles County", "the Antelope Valley high desert",
            "the Antelope Valley high desert, where sudden monsoon storms and winter cloudbursts can drop heavy rain on dry ground, causing flash flooding and water emergencies."),
}

# Opening sentences rotated per city for local flavor
INTRO_TEMPLATES = [
    "Water damage in {city} can strike without warning — a burst pipe, a failing water heater, or a storm that overwhelms the drainage. Fast, professional help protects your home and your family.",
    "When water breaks through in {city}, the damage spreads fast. Between seasonal storms and aging plumbing, homeowners here face real water emergencies — and quick action makes all the difference.",
    "A sudden water emergency in {city} can happen at any time. Whether it's a storm-driven leak or a failing supply line, professional water damage response protects your floors, walls, and belongings.",
    "Water damage doesn't wait — and in {city}, the combination of local weather patterns and older home plumbing creates serious risks. Every minute of delay increases the damage.",
    "In {city}, water emergencies often arrive without warning. A failing pipe, a storm surge, or an appliance leak can leave you needing professional help in a hurry.",
]

# Safety steps — rotated but always water-focused, never mentioning mold
STEPS_POOL = [
    ["Shut off the main water supply immediately if the source is a burst pipe or plumbing failure.",
     "Document all damage with photos and notes for your insurance claim before any cleanup begins.",
     "Move valuable items, electronics, and important documents to a dry, safe area if it is safe to do so."],
    ["Turn off the main water valve and, if safe, the electricity in affected rooms at the breaker panel.",
     "Photograph and video the damage for your insurance records before touching anything.",
     "Lift furniture off wet flooring and remove rugs, boxes, and valuables from the affected area."],
    ["Stay out of standing water and keep children and pets away from the affected area.",
     "Shut off water at the main valve and electricity at the breaker if flooding is present.",
     "Call for professional extraction as soon as it is safe — every hour of standing water increases the damage."],
    ["Move vehicles and valuables to higher ground if flooding is approaching.",
     "Shut off the main water supply and electrical breakers if water has entered the home.",
     "Document everything with photos and call for professional water extraction right away."],
    ["Shut off water at the main valve or well first — protect your water system from contamination.",
     "Turn off power to any rooms with standing water.",
     "Photograph damage for insurance and call for professional help immediately."],
]


def slugify(city):
    return city.lower().replace(" ", "-").replace(".", "").replace("'", "")


def make_slug(city):
    return f"water-damage-repair-{slugify(city)}-ca"


def pick_batch():
    """Choose the next BATCH_SIZE cities not yet deployed and not excluded.
    One entry per unique city (a city may span several zips — we keep the first)."""
    with open(SEED_PATH, encoding="utf-8") as f:
        seed = json.load(f)
    deployed_zips = {c["zip"] for c in seed}

    with open(ZIPS_PATH, encoding="utf-8") as f:
        zips = json.load(f)

    candidates = []
    seen_cities = set()
    for z in sorted(zips):
        city = zips[z]
        if z in deployed_zips:
            continue
        if city.lower() in EXCLUDED_CITIES:
            continue
        if not city.strip():
            continue
        # dedupe by city name — first (lowest) zip wins
        key = city.lower()
        if key in seen_cities:
            continue
        seen_cities.add(key)
        candidates.append((z, city))

    batch = candidates[:BATCH_SIZE]
    return batch, len(candidates)


def build_city_entry(zipcode, city):
    """Generate a full seed entry for one city with local, compliant content."""
    prefix = zipcode[:3]
    county, region, context = REGION_CONTEXTS.get(
        prefix, ("Los Angeles County", "California",
                 "California's seasonal storms and aging home plumbing create real water damage risks for homeowners across the region."))

    intro_tpl = INTRO_TEMPLATES[int(zipcode) % len(INTRO_TEMPLATES)]
    steps = STEPS_POOL[int(zipcode) % len(STEPS_POOL)]
    keyword = KEYWORDS[int(zipcode) % len(KEYWORDS)]

    return {
        "url_slug": make_slug(city),
        "city": city,
        "state": "CA",
        "zip": zipcode,
        "county": county,
        "region": region,
        "keyword": keyword,
        "context": f"{city} sits in {region} of {county}. {context}",
        "intro": intro_tpl.format(city=city),
        "steps": steps,
    }


def run(cmd, cwd=ROOT):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"❌ {' '.join(cmd)} failed:\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    return r.stdout


def check_doorway_risk(threshold=0.30):
    """Anti-doorway gate: compute normalized Jaccard similarity between all
    city-page CONTEXT blocks (city name stripped). If ANY pair exceeds the
    threshold, abort the push — the batch would recreate doorway pages."""
    pages_dir = os.path.join(ROOT, "src", "pages")
    pages = {}
    for f in sorted(os.listdir(pages_dir)):
        if not f.startswith("water-damage-repair-") or not f.endswith(".astro"):
            continue
        path = os.path.join(pages_dir, f)
        src = open(path, encoding="utf-8").read()
        m_city = re.search(r'const CITY = "([^"]*)"', src)
        m_ctx = re.search(r'const CONTEXT = "([^"]*)"', src)
        if not m_city or not m_ctx:
            continue
        city, text = m_city.group(1), m_ctx.group(1)
        norm = text.lower().replace(city.lower(), " ").replace("california", " ")
        norm = re.sub(r"[^a-z ]", " ", norm)
        words = {w for w in norm.split() if len(w) > 3}
        pages[city] = words

    cities = list(pages.keys())
    bad = []
    for i in range(len(cities)):
        for j in range(i + 1, len(cities)):
            a, b = pages[cities[i]], pages[cities[j]]
            inter = len(a & b)
            union = len(a | b)
            jac = inter / union if union else 0
            if jac > threshold:
                bad.append((cities[i], cities[j], round(jac, 2)))
    return bad


def main():
    dry_run = "--dry-run" in sys.argv
    batch, remaining = pick_batch()

    if not batch:
        print("✅ Aucune nouvelle ville disponible — tout le pool est déployé.")
        return

    print(f"Lot de {len(batch)} villes (reste {remaining} candidats)")

    with open(SEED_PATH, encoding="utf-8") as f:
        seed = json.load(f)

    existing_slugs = {c["url_slug"] for c in seed}
    added = 0
    for zipcode, city in batch:
        slug = make_slug(city)
        if slug in existing_slugs:
            continue
        seed.append(build_city_entry(zipcode, city))
        existing_slugs.add(slug)
        added += 1
        print(f"➕ {city} ({zipcode})")

    if added == 0:
        print("✅ Aucune ville ajoutée (déjà toutes présentes).")
        return

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)
        f.write("\n")

    if dry_run:
        print(f"\n🔍 Dry-run: {added} villes prêtes (seed mis à jour, pas de build/push).")
        return

    # 1. Generate pages + cities.json
    print("\n--- Génération des pages ---")
    run(["python3", GEN_PATH])

    # 1a. Enrich new pages with verified local data (NOAA/FEMA) if available
    print("\n--- Enrichissement données locales (NOAA/FEMA) ---")
    run(["python3", os.path.join(ROOT, "scripts", "add_local_data.py")])

    # 1b. Anti-doorway gate: abort push if any pair of pages is too similar
    print("\n--- Check anti-doorway (similarité CONTEXT) ---")
    bad_pairs = check_doorway_risk()
    if bad_pairs:
        print("❌ BLOCAGE : paires de pages trop similaires (risque doorway) :")
        for c1, c2, jac in bad_pairs:
            print(f"   {c1} vs {c2} -> {jac}")
        print("Aucun commit/push effectué. Corrigez les CONTEXT puis relancez.")
        sys.exit(2)

    # 1c. Regenerate the direct sitemap.xml (single file, no index)
    run(["python3", os.path.join(ROOT, "scripts", "gen_sitemap.py")])

    # 2. Astro build
    print("--- Build Astro ---")
    out = run(["npm", "run", "build"])
    for line in out.splitlines():
        if "page(s) built" in line:
            print(line)

    # 3. Commit + push
    print("--- Commit + Push ---")
    run(["git", "add", "-A"])
    run(["git", "commit", "-m", f"Phase 3: +{added} CA cities (weekly expansion batch)"])
    run(["git", "push", "origin", "main"])

    print(f"\n🎉 {added} villes ajoutées, déployées et poussées. Cloudflare va rebuild automatiquement.")


if __name__ == "__main__":
    main()
