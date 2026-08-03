#!/usr/bin/env python3
"""
LocalRestoreHub — Programmatic SEO Engine (Phase 2, v2)
========================================================
CA Water Damage only. Generates:
  - src/data/cities.json                                     (master data for homepage)
  - src/pages/water-damage-repair-<city>-ca.astro            (local landing pages)

URL pattern : /water-damage-repair-<city>-ca/
STRICT RULE : ZERO "mold/moisissure" in texts, metadata, or URLs.
              Any seed containing forbidden terms is REJECTED at generation.

v2 CHANGES (visual credibility, ultra-light):
  - Local Hero section: blue gradient background, centered white H1 + call button
  - Inline SVG icons (phone / shield / truck / clock) — no external requests
  - White, minimal content area below the hero
  - Body CTAs rendered as real UI buttons, not underlined text links
  - HOURS variable at the top of this script — change it in one place only

USAGE
-----
Add new cities to scripts/cities-seed.json (append to the array), then:
    python3 scripts/gen_ca_pages.py
Idempotent: the seed file is the single source of truth. Stale generated
pages (old .md or removed cities) are cleaned automatically.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES_DIR = os.path.join(ROOT, "src", "pages")
DATA_PATH = os.path.join(ROOT, "src", "data", "cities.json")
SEED_PATH = os.path.join(ROOT, "scripts", "cities-seed.json")

# =====================================================================
#  CONFIG — edit these values only when the network confirms them
# =====================================================================
PHONE_DISPLAY = "+1 (844) 833-10-48"          # tracking number shown to visitors
PHONE_TEL     = "tel:+18448331048"            # clickable phone link
HOURS         = "Daily 10:00 AM - 2:00 AM"    # Marketcall offer #12330: Mon-Sun 10am-2am EST
# =====================================================================

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

# =====================================================================
#  PAGE TEMPLATE (Astro) — the ONLY place the page structure lives.
#  __PLACEHOLDERS__ are replaced per city. Astro braces are untouched.
# =====================================================================
PAGE_TEMPLATE = """---
import Layout from "../layouts/Layout.astro";

const PHONE_DISPLAY = "__PHONE_DISPLAY__";
const PHONE_TEL = "__PHONE_TEL__";
const HOURS = "__HOURS__";

const CITY = "__CITY__";
const ZIP = "__ZIP__";
const COUNTY = "__COUNTY__";
const KEYWORD = "__KEYWORD__";
const INTRO = __INTRO__;
const CONTEXT = __CONTEXT__;
const STEPS = __STEPS__;
const NEARBY = __NEARBY__;

const TITLE = `${KEYWORD} ${CITY}, CA ${ZIP} - 24/7 Emergency Response`;
const DESC = `Need ${KEYWORD.toLowerCase()} in ${CITY}, CA ${ZIP}? Call our ${HOURS} local dispatch at ${PHONE_DISPLAY} for immediate professional help.`;
---

<Layout title={TITLE} description={DESC}>
  <!-- ============ HERO LOCAL ============ -->
  <section class="bg-gradient-to-br from-primary via-primary-light to-primary text-white">
    <div class="max-w-5xl mx-auto px-4 py-16 md:py-24 text-center">
      <h1 class="text-3xl md:text-5xl font-extrabold leading-tight mb-4">
        {KEYWORD} in {CITY}, CA {ZIP}
      </h1>
      <p class="text-lg md:text-xl text-gray-200 max-w-3xl mx-auto mb-8 leading-relaxed">
        {INTRO}
      </p>

      <!-- Call button (inline SVG phone icon) -->
      <a href={PHONE_TEL}
         class="inline-flex items-center gap-3 bg-accent hover:bg-accent-hover text-white font-bold text-lg px-8 py-4 rounded-lg shadow-lg transition transform hover:scale-105">
        <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
        </svg>
        Call {PHONE_DISPLAY}
      </a>

      <!-- Reassurance badges (inline SVG shield / truck / clock) -->
      <div class="flex flex-wrap justify-center gap-x-8 gap-y-3 mt-10 text-sm font-semibold text-gray-100">
        <span class="inline-flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
          Verified Local Providers
        </span>
        <span class="inline-flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8.25 18.75a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 01-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 01-3 0m3 0a1.5 1.5 0 00-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 00-3.213-9.193 2.056 2.056 0 00-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 00-10.026 0 1.106 1.106 0 00-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12"/>
          </svg>
          Fast Response
        </span>
        <span class="inline-flex items-center gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          Open {HOURS}
        </span>
      </div>
    </div>
  </section>

  <!-- ============ CONTENU BLANC ============ -->
  <section class="bg-white py-12 md:py-16">
    <div class="max-w-4xl mx-auto px-4">
      <h2 class="text-2xl md:text-3xl font-bold text-primary mb-6">Why Water Damage Is Common in {CITY}</h2>
      <p class="text-gray-700 leading-relaxed mb-10">{CONTEXT}</p>

      <h2 class="text-2xl md:text-3xl font-bold text-primary mb-6">Immediate Steps to Take</h2>
      <ul class="space-y-3 mb-10">
        {STEPS.map((s, i) => (
          <li class="flex items-start gap-3 bg-bg-light border border-gray-100 rounded-lg p-4">
            <span class="flex-shrink-0 w-7 h-7 bg-accent/10 text-accent rounded-full flex items-center justify-center text-sm font-bold">{i + 1}</span>
            <span class="text-gray-600">{s}</span>
          </li>
        ))}
      </ul>

      <!-- CTA principal corps de page — vrai bouton UI -->
      <div class="bg-bg-light border border-gray-200 rounded-xl p-8 text-center mb-10">
        <p class="text-xl font-bold text-primary mb-4">Need immediate help in {CITY}?</p>
        <a href={PHONE_TEL}
           class="inline-flex items-center gap-3 bg-accent hover:bg-accent-hover text-white font-bold text-lg px-8 py-4 rounded-lg shadow transition">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
          </svg>
          Call {PHONE_DISPLAY}
        </a>
        <p class="text-xs text-gray-500 mt-4">Our {HOURS} local dispatch is standing by to connect you with verified water damage professionals serving {COUNTY} and the {CITY} area. By calling this number, you consent to being connected with a third-party service provider and to the recording of your call for quality assurance and compliance purposes. Read our <a href="/privacy-policy" class="underline">Privacy Policy</a> for full TCPA &amp; CCPA disclosures.</p>
      </div>

      <h2 class="text-2xl md:text-3xl font-bold text-primary mb-6">Nearby Service Areas</h2>
      <ul class="grid md:grid-cols-2 gap-3">
        {NEARBY.map((n) => (
          <li>
            <a href={`/${n.slug}/`} class="block bg-bg-light hover:bg-gray-soft border border-gray-200 rounded-lg px-4 py-3 text-primary font-semibold transition">
              💧 Water Damage Help in {n.city}, CA
            </a>
          </li>
        ))}
      </ul>
    </div>
  </section>
</Layout>
"""


# ---- Phase-1 cities (safe default if seed file missing) ----
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

        for term in FORBIDDEN:
            if term in lowered:
                errors.append(f"[{city}] forbidden term '{term}' in content")

        if not re.fullmatch(r"water-damage-repair-[a-z-]+-ca", slug):
            errors.append(f"[{city}] bad slug '{slug}' — must be water-damage-repair-<city>-ca")

        if city.lower() in EXCLUDED_CITIES:
            errors.append(f"[{city}] city is on the excluded-metro list")

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


def clean_stale_pages(current_slugs):
    """
    Remove previously generated pages that are no longer needed.
    - .md pages: legacy format from v1 — always removed (superseded by .astro)
    - .astro pages: removed only when their slug is no longer in the seed
    """
    removed = 0
    for fname in os.listdir(PAGES_DIR):
        if not fname.startswith("water-damage-repair-"):
            continue
        if fname.endswith(".md"):
            os.remove(os.path.join(PAGES_DIR, fname))
            print(f"🗑️  removed legacy {fname}")
            removed += 1
        elif fname.endswith(".astro"):
            slug = fname[: -len(".astro")]
            if slug not in current_slugs:
                os.remove(os.path.join(PAGES_DIR, fname))
                print(f"🗑️  removed stale {fname}")
                removed += 1
    return removed


def build_page(city, all_cities):
    """Render the Astro page template for one city."""
    others = [x for x in all_cities if x["url_slug"] != city["url_slug"]]
    nearby = [{"slug": x["url_slug"], "city": x["city"]} for x in others]

    page = (PAGE_TEMPLATE
            .replace("__PHONE_DISPLAY__", PHONE_DISPLAY)
            .replace("__PHONE_TEL__", PHONE_TEL)
            .replace("__HOURS__", HOURS)
            .replace("__CITY__", city["city"])
            .replace("__ZIP__", city["zip"])
            .replace("__COUNTY__", city["county"])
            .replace("__KEYWORD__", city["keyword"])
            .replace("__INTRO__", json.dumps(city["intro"], ensure_ascii=False))
            .replace("__CONTEXT__", json.dumps(city["context"], ensure_ascii=False))
            .replace("__STEPS__", json.dumps(city["steps"], ensure_ascii=False))
            .replace("__NEARBY__", json.dumps(nearby, ensure_ascii=False)))
    return page


def verify(generated):
    """Check generated files for forbidden terms."""
    violations = []
    for slug in generated:
        fpath = os.path.join(PAGES_DIR, f"{slug}.astro")
        text = open(fpath, encoding="utf-8").read().lower()
        for term in FORBIDDEN:
            if term in text:
                violations.append(f"{slug}.astro contains '{term}'")
    if violations:
        print("❌ VERIFICATION FAILED:")
        for v in violations:
            print(f"   • {v}")
        sys.exit(1)
    print(f"✅ Verification: 0 forbidden terms across {len(generated)} pages")


def main():
    cities = check_seed(load_seed())

    for i, c in enumerate(cities):
        if not c.get("keyword"):
            c["keyword"] = KEYWORDS[i % len(KEYWORDS)]

    # ---- cities.json (homepage data) ----
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

    # ---- generate .astro pages ----
    generated = []
    for c in cities:
        fpath = os.path.join(PAGES_DIR, f"{c['url_slug']}.astro")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(build_page(c, cities))
        generated.append(c["url_slug"])
        print(f"✅ {c['url_slug']}.astro")

    # ---- cleanup stale pages ----
    clean_stale_pages(set(generated))

    # ---- post-generation verification ----
    verify(generated)
    print(f"\n🎉 Generation complete — {len(generated)} pages")


if __name__ == "__main__":
    main()
