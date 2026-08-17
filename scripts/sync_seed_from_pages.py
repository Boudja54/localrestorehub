#!/usr/bin/env python3
"""
sync_seed_from_pages.py — Restore hand-crafted unique CONTEXT/INTRO into the seed.

Root cause of weekly blockage:
  - Hand-crafted unique CONTEXT/INTRO blocks live ONLY in committed .astro pages
    (anti-doorway work was done directly on pages).
  - cities-seed.json still holds generic template contexts.
  - Each weekly run regenerates every page from the seed, wiping the uniqueness,
    so the anti-doorway gate blocks the push.

This script copies the CONTEXT/INTRO from the committed (HEAD) pages back into
the seed for existing cities, and injects hand-crafted unique CONTEXT/INTRO for
new cities (provided via NEW_CONTEXTS below). Idempotent.
"""
import json
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED_PATH = os.path.join(ROOT, "scripts", "cities-seed.json")

# Hand-crafted UNIQUE CONTEXT/INTRO for cities not yet committed at HEAD.
# Factual, local, no fabricated statistics, no forbidden terms.
NEW_CONTEXTS = {
    "South Gate": {
        "intro": "A burst pipe in a post-war tract home or runoff backing up from the streets can turn a quiet South Gate neighborhood into a water emergency in minutes. Local crews respond fast to protect your floors, walls, and foundation.",
        "context": "South Gate is a densely built city in the Gateway Cities corridor southeast of downtown Los Angeles, where rows of post-war tract homes from the 1940s and 1950s sit on small lots with limited open ground. The city's flat, heavily paved terrain and aging municipal water lines make sudden pipe failures and stormwater buildup a recurring concern, and the nearby Los Angeles River and Rio Hondo corridors concentrate runoff during heavy winter rains. Much of the local housing stock still relies on original galvanized steel supply lines that are now decades past their expected lifespan, leaving homeowners vulnerable to leaks and pressure surges without warning.",
    },
    "Inglewood": {
        "intro": "From aging supply lines in older residential blocks to stormwater pressure during heavy rain, water emergencies in Inglewood demand a fast local response. One call connects you to a nearby crew ready to act.",
        "context": "Inglewood sits in the South Bay area west of downtown Los Angeles, a city in transition where older neighborhoods from the 1920s through the 1950s sit alongside the new stadium district around SoFi Stadium and the Kia Forum. Much of its housing stock features aging cast-iron and galvanized plumbing, and the flat, low-lying terrain between the Baldwin Hills and the coast leaves the city's drainage system straining during heavy winter storms. Redevelopment projects have modernized parts of the city, but many residential blocks still depend on water lines installed decades ago that are prone to sudden failure.",
    },
}


def head_pages():
    """Extract city -> (CONTEXT, INTRO) from committed pages via git archive."""
    tmp = tempfile.mkdtemp(prefix="lrh_head_")
    subprocess.run(["git", "archive", "HEAD", "src/pages"], cwd=ROOT,
                   check=True, capture_output=True)
    # simpler: read from git show per file
    pages = {}
    seed = json.load(open(SEED_PATH, encoding="utf-8"))
    for entry in seed:
        slug = entry["url_slug"]
        if not slug.startswith("water-damage-repair-"):
            continue
        r = subprocess.run(["git", "show", f"HEAD:src/pages/{slug}.astro"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            continue  # new page, not in HEAD yet
        src = r.stdout
        m_ctx = re.search(r'const CONTEXT = "((?:[^"\\]|\\.)*)"', src, re.DOTALL)
        m_intro = re.search(r'const INTRO = "((?:[^"\\]|\\.)*)"', src, re.DOTALL)
        if not m_ctx or not m_intro:
            print(f"  !! {slug}: CONTEXT/INTRO not found in HEAD")
            continue
        pages[entry["city"]] = {
            "context": m_ctx.group(1),
            "intro": m_intro.group(1),
        }
    return pages


def main():
    head = head_pages()
    print(f"Extracted {len(head)} unique CONTEXT/INTRO from HEAD pages.")

    with open(SEED_PATH, encoding="utf-8") as f:
        seed = json.load(f)

    updated = 0
    for entry in seed:
        city = entry["city"]
        if city in head:
            if entry.get("context") != head[city]["context"] or entry.get("intro") != head[city]["intro"]:
                entry["context"] = head[city]["context"]
                entry["intro"] = head[city]["intro"]
                updated += 1
                print(f"  ~ {city}: CONTEXT/INTRO synced from HEAD")
        elif city in NEW_CONTEXTS:
            nc = NEW_CONTEXTS[city]
            if entry.get("context") != nc["context"] or entry.get("intro") != nc["intro"]:
                entry["context"] = nc["context"]
                entry["intro"] = nc["intro"]
                updated += 1
                print(f"  + {city}: hand-crafted CONTEXT/INTRO injected")

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(seed, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\n{updated} seed entries updated.")


if __name__ == "__main__":
    main()
