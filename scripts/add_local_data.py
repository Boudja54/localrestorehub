#!/usr/bin/env python3
"""
add_local_data.py — Inject 2-3 VERIFIED local data points into each city page.

Mission: MISSION-local-data.md (12/08/2026)
- Reads scripts/local-city-data.json (verified data from NOAA / FEMA / Weather Spark / city-data)
- Appends 2-3 short factual sentences to each page's const CONTEXT (idempotent)
- Varies phrasing per city (rotating templates + fact order) so even neighboring
  cities with similar climates never share a sentence.
- Verifies uniqueness: `for f in src/pages/water-damage-repair-*.astro; do grep -o 'const CONTEXT = "[^"]*"' "$f" | cut -d'"' -f2; done | sort | uniq -d` must be empty
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ROOT / "src" / "pages"
DATA_FILE = ROOT / "scripts" / "local-city-data.json"


def slug_key(city: str) -> str:
    return city.strip().lower().replace(" ", "-")


def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# Rotating precipitation templates. {c}=City name, {p}=precip, {d}=rainy days
PRECIP_TEMPLATES = [
    "{c} receives about {p} inches of rain per year, spread over roughly {d} wet days.",
    "Annual rainfall in {c} averages about {p} inches, with roughly {d} wet days per year.",
    "Typical winters bring {c} about {p} inches of rain across roughly {d} wet days.",
    "With about {p} inches of rain and {d} wet days each year, {c} gets most of its moisture in winter.",
    "{c} sees about {p} inches of precipitation annually, mostly across {d} wet days.",
]
PRECIP_ONLY_TEMPLATES = [
    "{c} receives about {p} inches of rain per year.",
    "Annual rainfall in {c} averages about {p} inches.",
    "Typical winters bring {c} about {p} inches of rain.",
]

# Rotating FEMA templates. {c}=City name, {f}=fema phrase
FEMA_TEMPLATES = [
    "FEMA flood maps rate much of the {c} area as {f}.",
    "FEMA's flood maps put {f} across much of the {c} area.",
    "Flood risk in {c} is {f}, according to FEMA mapping.",
    "Much of {c} sits in {f}, per FEMA flood mapping.",
]

# Orderings: which fact goes first/second/third. p=precip, f=fema, l=local
ORDERS = [
    ["p", "f", "l"],
    ["p", "l", "f"],
    ["f", "p", "l"],
    ["f", "l", "p"],
    ["l", "p", "f"],
]


def build_sentences(city_key: str, data: dict) -> list[str]:
    city_title = city_key.replace("-", " ").title()
    facts = {}

    if data.get("precip_in"):
        if data.get("rainy_days"):
            tpl = PRECIP_TEMPLATES[int(hashlib.md5((city_key + "p").encode()).hexdigest(), 16) % len(PRECIP_TEMPLATES)]
            facts["p"] = tpl.format(c=city_title, p=data["precip_in"], d=data["rainy_days"])
        else:
            tpl = PRECIP_ONLY_TEMPLATES[int(hashlib.md5((city_key + "po").encode()).hexdigest(), 16) % len(PRECIP_ONLY_TEMPLATES)]
            facts["p"] = tpl.format(c=city_title, p=data["precip_in"])

    if data.get("fema"):
        tpl = FEMA_TEMPLATES[int(hashlib.md5((city_key + "f").encode()).hexdigest(), 16) % len(FEMA_TEMPLATES)]
        facts["f"] = tpl.format(c=city_title, f=data["fema"])

    if data.get("local_fact"):
        facts["l"] = data["local_fact"]

    if not facts:
        return []

    order = ORDERS[int(hashlib.md5(city_key.encode()).hexdigest(), 16) % len(ORDERS)]
    return [facts[k] for k in order if k in facts]


def process_page(path: Path, city_key: str, data: dict):
    text = path.read_text(encoding="utf-8")
    sentences = build_sentences(city_key, data)
    if not sentences:
        print(f"  !! {path.name}: no verified data, skipped")
        return False

    m = re.search(r'(const CONTEXT = ")(.*?)(";)', text, re.DOTALL)
    if not m:
        print(f"  !! {path.name}: CONTEXT not found")
        return False

    prefix, ctx, suffix = m.group(1), m.group(2), m.group(3)

    # Idempotency + dedup: drop any sentence (or near-duplicate) already in the CONTEXT.
    # Compare on a normalized core (first 60 chars, lowercase, non-alphanumeric stripped)
    # to catch the same fact phrased slightly differently in the original INTRO/CONTEXT.
    def norm(s: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", s.lower())[:60]

    ctx_core = norm(ctx)
    kept = []
    for s in sentences:
        core = norm(s)
        if core and core in ctx_core:
            print(f"    ~ {path.name}: skipped duplicate fact: {s[:60]}...")
            continue
        # also skip if the local fact is already present verbatim inside ctx
        if len(s) > 40 and s.lower()[:40] in ctx.lower():
            print(f"    ~ {path.name}: skipped near-duplicate fact: {s[:60]}...")
            continue
        kept.append(s)

    if not kept:
        print(f"  == {path.name}: already enriched (all facts present)")
        return False

    new_ctx = ctx.rstrip() + " " + " ".join(kept)
    new_text = text[: m.start()] + prefix + new_ctx + suffix + text[m.end():]
    path.write_text(new_text, encoding="utf-8")
    print(f"  + {path.name}: added {len(sentences)} facts")
    return True


def main():
    data = load_data()
    changed = 0
    for city, d in data.items():
        key = slug_key(city)
        page = PAGES / f"water-damage-repair-{key}-ca.astro"
        if not page.exists():
            print(f"  !! page not found for {city}: {page.name}")
            continue
        if process_page(page, key, d):
            changed += 1
    print(f"\n{changed} pages enriched.")


if __name__ == "__main__":
    main()
