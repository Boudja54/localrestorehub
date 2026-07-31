#!/usr/bin/env python3
"""
LocalRestoreHub — Programmatic SEO Engine (Phase 2)
====================================================
CA Water Damage only. Generates:
  - src/data/cities.json        (master city data for homepage)
  - src/pages/water-damage-repair-<city>-ca.md   (local landing pages)

URL pattern : /water-damage-repair-<city>-ca/
STRICT RULE : ZERO "mold/moisissure" in texts, metadata, or URLs.
              Any seed containing forbidden terms is REJECTED at generation.

USAGE
-----
Add new cities to scripts/cities-seed.json (append to the array), then:
    python3 scripts/gen_ca_pages.py
The generator is idempotent: it regenerates all pages from the seed,
so the seed file is the single source of truth.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "src", "pages")
DATA_PATH = os.path.join(ROOT, "src", "data", "cities.json")
SEED_PATH = os.path.join(ROOT, "scripts", "cities-seed.json")

PHONE_DISPLAY = "+1 (844) 833-10-48"
PHONE_TEL = "tel:+18448331048"

# Strict water keywords — rotated across cities
KEYWORDS = [
    "Water Damage Restoration",
    "Flood Cleanup",
    "Emergency Water Extraction",
]

# Hard-blocked terms (compliance). Seed is rejected if any appear.
FORBIDDEN = ["mold", "moisissure", "mould", "sewage", "flooding risk"]

# Metro areas we deliberately do NOT target (ultra-competitive).
EXCLUDED_CITIES = [
    "los angeles", "beverly hills", "santa monica", "long beach",
    "irvine", "anaheim", "san diego", "san francisco", "sacramento",
    "san jose", "oakland", "fresno", "bakersfield",
]


def check_seed(cities):
    """Reject seed entries that violate compliance rules."""
    errors = []
    seen = set()
    for c in cities:
        slug = c.get("url_slug", "")
        city = c.get("city", "")
        text = " ".join(str(c.get(k, "")) for k in
                        ["city", "county", "region", "keyword", "context", "intro"])
        text += " " + " ".join(c.get("steps", []))
        lowered = text.lower()

        # 1. forbidden terms
        for term in FORBIDDEN:
            if term in lowered:
                errors.append(f"[{city}] forbidden term '{term}' in content")

        # 2. slug must match pattern
        if not re.fullmatch(r"water-damage-repair-[a-z-]+-ca", slug):
            errors.append(f"[{city}] bad slug '{slug}' — must be water-damage-repair-<city>-ca")

        # 3. excluded metros
        if city.lower() in EXCLUDED_CITIES:
            errors.append(f"[{city}] city is on the excluded-metro list")

        # 4. duplicates
        if slug in seen:
            errors.append(f"[{city}] duplicate slug '{slug}'")
        seen.add(slug)

    if errors:
        print("❌ SEED REJECTED — compliance errors:")
        for e in errors:
            print(f"   • {e}")
        sys.exit(1)
    return cities


def load_seed():
    """Load seed file, or fall back to built-in Phase-1 cities."""
    if os.path.exists(SEED_PATH):
        with open(SEED_PATH, encoding="utf-8") as f:
            return json.load(f)
    print(f"⚠️  {SEED_PATH} not found — using built-in Phase-1 cities")
    return BUILTIN_CITIES


# ---- Phase-1 cities (keep as safe default if seed file missing) ----
BUILTIN_CITIES = [
    {"url_slug": "water-damage-repair-bardsdale-ca", "city": "Bardsdale", "state": "CA", "zip": "93015",
     "county": "Ventura County", "region": "the Santa Clara River Valley", "keyword": "Water Damage Restoration",
     "context": "Bardsdale sits in Ventura County's Santa Clara River Valley, where seasonal winter storms can quickly turn the river into a flood threat. The area's older farmhouse plumbing and well systems are especially vulnerable to pressure surges and pipe failures during heavy rain.",
     "intro": "When water breaks through in Bardsdale, the damage spreads fast. Between the Santa Clara River's flood potential and aging rural plumbing, homeowners here face real water emergencies every winter — and fast action is the difference between a quick fix and a major repair.",
     "steps": ["Shut off the main water supply immediately if the source is a burst pipe or plumbing failure.", "Document all damage with photos and notes for your insurance claim before any cleanup begins.", "Move valuable items, electronics, and important documents to a dry, safe area if it is safe to do so."]},
    {"url_slug": "water-damage-repair-somis-ca", "city": "Somis", "state": "CA", "zip": "93066",
     "county": "Ventura County", "region": "the Las Posas Valley", "keyword": "Flood Cleanup",
     "context": "Somis is a rural community in the Las Posas Valley, where heavy winter rain produces rapid runoff from surrounding hillsides. Many homes rely on older well pumps and septic systems that can fail without warning, sending water into living spaces.",
     "intro": "A sudden water emergency in Somis can strike during any winter storm. Hillside runoff, aging well equipment, and isolated rural roads mean homeowners often need help fast — and a quick, professional response protects your floors, walls, and belongings.",
     "steps": ["Turn off the main water valve and, if safe, the electricity in affected rooms at the breaker panel.", "Photograph and video the damage for your insurance records before touching anything.", "Lift furniture off wet flooring and remove rugs, boxes, and valuables from the affected area."]},
    {"url_slug": "water-damage-repair-piru-ca", "city": "Piru", "state": "CA", "zip": "93040",
     "county": "Ventura County", "region": "the Piru Creek watershed", "keyword": "Emergency Water Extraction",
     "context": "Piru lies along the Piru Creek watershed at the edge of the Los Padres National Forest. Flash flooding after heavy rain is a recurring seasonal risk, and the town's older infrastructure makes sudden pipe and water line failures a genuine concern for local homeowners.",
     "intro": "In Piru, water emergencies often arrive without warning — a creek that jumps its banks, a failing water line, or a storm that overwhelms the drainage. When it happens, standing water inside your home needs to be extracted quickly to protect your property.",
     "steps": ["Stay out of standing water and keep children and pets away from the affected area.", "Shut off water at the main valve and electricity at the breaker if flooding is present.", "Call for professional extraction as soon as it is safe — every hour of standing water increases the damage."]},
    {"url_slug": "water-damage-repair-littlerock-ca", "city": "Littlerock", "state": "CA", "zip": "93543",
     "county": "Los Angeles County", "region": "the Antelope Valley", "keyword": "Water Damage Restoration",
     "context": "Littlerock sits in the high desert of the Antelope Valley, where summer monsoon storms and winter cloudbursts can drop heavy rain on dry ground, causing sudden flash flooding. Desert homes with older plumbing and well systems face unique water damage risks.",
     "intro": "Water damage in Littlerock can come from a sudden desert storm or a failing well line. Because the high desert drains fast and hard, flooding here is often sudden and severe — which is why having a local water damage response line matters.",
     "steps": ["Move vehicles and valuables to higher ground if flooding is approaching.", "Shut off the main water supply and electrical breakers if water has entered the home.", "Document everything with photos and call for professional water extraction right away."]},
    {"url_slug": "water-damage-repair-acton-ca", "city": "Acton", "state": "CA", "zip": "93510",
     "county": "Los Angeles County", "region": "the high desert foothills", "keyword": "Flood Cleanup",
     "context": "Acton is a semi-rural high desert community at the base of the San Gabriel Mountains. Sudden thunderstorms send runoff down the foothills, and many homes on acreage rely on private wells and septic systems prone to sudden failure.",
     "intro": "Between foothill runoff and aging well systems, Acton homeowners face real water emergencies. A flooded garage, a failed pressure tank, or a storm-swollen wash can leave you needing cleanup help in a hurry.",
     "steps": ["Shut off water at the well or main valve first — protect your water system from contamination.", "Turn off power to any rooms with standing water.", "Photograph damage for insurance and call for flood cleanup support immediately."]},
    {"url_slug": "water-damage-repair-valyermo-ca", "city": "Valyermo", "state": "CA", "zip": "93563",
     "county": "Los Angeles County", "region": "the high desert along Big Rock Creek", "keyword": "Emergency Water Extraction",
     "context": "Valyermo is a remote high desert community along Big Rock Creek below the San Gabriel Mountains. Sudden creek surges during storms and isolated well systems create real water emergencies for the homes scattered across this rugged terrain.",
     "intro": "Living in Valyermo means living with the desert's extremes — including sudden water events. When a creek surge or a failed well line puts water in your home, remote locations make fast local help essential.",
     "steps": ["Keep everyone away from fast-moving water and flooded washes — never attempt to cross them.", "Shut off the main water valve and electrical breakers if water is inside the home.", "Document the damage and call for emergency water extraction without delay."]},
]


def main():
    cities = check_seed(load_seed())

    # rotate keywords if seed entry lacks one
    for i, c in enumerate(cities):
        if not c.get("keyword"):
            c["keyword"] = KEYWORDS[i % len(KEYWORDS)]

    # ---- write cities.json ----
    json_data = []
    for c in cities:
        json_data.append({
            "slug": c["url_slug"],
            "city": c["city"],
            "state": c.get("state", "CA"),
            "zip": c["zip"],
            "county": c["county"],
            "emergency": c["keyword"],
            "context": c["context"],
            "intro": c["intro"],
            "steps": c["steps"],
            "phone": PHONE_DISPLAY,
        })
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"✅ cities.json: {len(json_data)} CA cities")

    # ---- generate markdown pages ----
    generated = []
    for c in cities:
        others = [x for x in cities if x["url_slug"] != c["url_slug"]]
        link_items = "\n".join(
            f"- [Water Damage Help in {x['city']}, CA](/{x['url_slug']}/)"
            for x in others
        )
        md = f"""---
title: "{c['keyword']} {c['city']}, CA {c['zip']} - 24/7 Emergency Response"
description: "Need {c['keyword'].lower()} in {c['city']}, CA {c['zip']}? Call our 24/7 local dispatch at {PHONE_DISPLAY} for immediate professional help."
layout: ../layouts/Layout.astro
---

## {c['keyword']} in {c['city']}, CA {c['zip']} - 24/7 Emergency Response

{c['intro']}

## Why Water Damage Is Common in {c['city']}

{c['context']}

## Immediate Steps to Take

- **{c['steps'][0]}**
- **{c['steps'][1]}**
- **{c['steps'][2]}**

## The Solution: Call Your Local Dispatch

> **Need immediate help in {c['city']}? Call our 24/7 local dispatch now: [{PHONE_DISPLAY}]({PHONE_TEL})**

*By calling this number, you consent to being connected with a third-party service provider and to the recording of your call for quality assurance and compliance purposes. Read our [Privacy Policy](/privacy-policy) for full TCPA &amp; CCPA disclosures.*

Our operators are standing by 24/7 to connect you with verified water damage professionals serving {c['county']} and the {c['city']} area. Fast response minimizes structural damage and protects your property.

## Nearby Service Areas

{link_items}

*Local Restore Hub is a free directory service connecting you with independent local contractors. Call {PHONE_DISPLAY} for 24/7 emergency assistance.*
"""
        fpath = os.path.join(PAGES_DIR, f"{c['url_slug']}.md")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(md)
        generated.append(c["url_slug"])
        print(f"✅ {c['url_slug']}.md")

    # ---- post-generation verification ----
    verify(generated)
    print(f"\n🎉 Generation complete — {len(generated)} pages")


def verify(generated):
    """Check generated files for forbidden terms."""
    violations = []
    for slug in generated:
        fpath = os.path.join(PAGES_DIR, f"{slug}.md")
        text = open(fpath, encoding="utf-8").read().lower()
        for term in FORBIDDEN:
            if term in text:
                violations.append(f"{slug}.md contains '{term}'")
    if violations:
        print("❌ VERIFICATION FAILED:")
        for v in violations:
            print(f"   • {v}")
        sys.exit(1)
    print(f"✅ Verification: 0 forbidden terms across {len(generated)} pages")


if __name__ == "__main__":
    main()
