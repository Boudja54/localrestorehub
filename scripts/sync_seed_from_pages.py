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
        "Whittier": {
            "intro": "A burst supply line or a storm-driven backup in Whittier can reach flooring, walls, and hillside foundations long before it becomes visible. Local crews are ready to begin extraction immediately.",
            "context": "Whittier grew up around a Quaker colony planted in the 1880s, and its Uptown district still shows that history in Victorian storefronts and Craftsman bungalows set behind mature pepper and oak trees. From there the city fans outward: hillside streets climb toward Turnbull Canyon and Friendly Hills, while the southern flats sit close to the Rio Hondo and San Gabriel River channels. Because so much of the housing dates from the 1920s through the 1950s, cast-iron drains and galvanized supply lines remain common behind plaster walls, and homes on the slopes also have to contend with drainage running down toward them."
        },
        "Artesia": {
            "intro": "In a city of narrow lots and older buildings like Artesia, a hidden pipe failure can soak a foundation without anyone noticing. Fast extraction and drying are what limit the damage.",
            "context": "Artesia is one of the smallest cities in Los Angeles County, a compact grid of narrow lots strung along Artesia Boulevard that once supplied much of the region with milk. The Dutch dairy heritage is still visible in the annual parade and in the older farm-style buildings along the main street, and many parcels keep small rear outbuildings, detached garages, and concrete pads poured decades before modern plumbing codes. Sewer laterals and water service lines from that era run beneath those slabs and patios, so a slow underground failure often announces itself first as a damp patch or an unexplained jump in the water bill."
        },
        "Altadena": {
            "intro": "With mountain runoff above and century-old plumbing below, Altadena homes face water emergencies from both directions at once. A quick local response protects the structure.",
            "context": "Altadena is an unincorporated community pressed against the San Gabriel Mountains, where the street grid gives way to deep lots, towering deodars, and an unusual concentration of historic Craftsman and Spanish Revival houses. Elevation climbs steadily from the valley floor up into the foothills, and the washes and debris basins that channel mountain runoff sit directly above residential blocks. That terrain produces two very different kinds of trouble: storm flows and hillside seepage arriving from above, and decades-old copper, galvanized, or even clay lines working beneath the floors of houses that are now a hundred years old."
        },
        "San Marino": {
            "intro": "Long driveways and dense estate landscaping can hide a failing line in San Marino for weeks. When water finally surfaces, speed matters more than anything else.",
            "context": "San Marino is a small, largely residential city at the western edge of the San Gabriel Valley, laid out in the early twentieth century around broad, median-divided streets and estate-sized parcels. The Huntington Library and its gardens occupy much of the eastern side of town, and the surrounding blocks are dominated by large architecturally significant houses surrounded by mature landscaping and extensive irrigation. Deep lots, long private driveways, and original subterranean plumbing mean a leak can travel a considerable distance underground before any sign of it appears indoors."
        },
        "Newhall": {
            "intro": "Hard soil and decades-old lines in Newhall mean a small leak can quietly turn into a flooded crawlspace or garage floor. Professional extraction stops the spread quickly.",
            "context": "Newhall is the historic core of the Santa Clarita Valley, a former railroad and oil town whose older blocks still line the original highway alignment between the San Gabriel and Santa Susana ranges. Suburban growth has since filled the surrounding valley with tracts of stucco houses put up from the 1960s onward, but the original Newhall grid keeps small, close-set homes on modest lots. Summer heat combined with hard, clay-heavy ground works against buried pipes here, and long dry spells followed by intense winter downpours put stress on both foundations and outdoor irrigation."
        },
        "Toluca Lake": {
            "intro": "Renovated houses in Toluca Lake often conceal plumbing from several different eras. When one of those older lines lets go, fast water removal protects flooring and cabinetry.",
            "context": "Toluca Lake is a compact, leafy neighborhood in the southeastern San Fernando Valley, arranged around the small lake and the village shops along Riverside Drive. The housing stock mixes 1920s and 1930s period homes with later additions, many of them enlarged over the decades with rear extensions, converted garages, and pool houses. Those layered renovations frequently leave old supply and drain lines buried beneath new slabs and decking, and the flat valley terrain means water from a concealed leak spreads sideways into adjoining rooms instead of draining away."
        },
        "Alta Loma": {
            "intro": "Sandy foothill ground in Alta Loma lets a hidden leak drain away unseen until the damage is well advanced. Emergency extraction and drying limit how far it travels.",
            "context": "Alta Loma occupies the gently rising alluvial fan at the foot of the Cucamonga foothills in the Rancho Cucamonga area, where residential blocks step upward toward the mountains. Lots tend to be generous, often with swimming pools, citrus trees, and long driveway runs, and much of the housing was built during the 1970s and 1980s construction boom. Because the soil is sandy and drains quickly, small underground leaks can go unnoticed for months, and properties set against the hills also collect runoff arriving from the slopes above them."
        },
        "Alhambra": {
            "intro": "In Alhambra's tightly packed blocks, water from one unit quickly reaches the next. A fast response keeps a single pipe failure from turning into a building-wide problem.",
            "context": "Alhambra is a densely built city just east of Los Angeles, where Main Street marks the old commercial spine and residential blocks run north toward the South Pasadena border. Much of the housing went up between the 1920s and the 1940s, with bungalows, duplexes, and small courtyard apartment buildings sharing narrow lots and rear alley access. Original cast-iron drains, bathrooms added decades after construction, and constant tenant turnover make undetected leaks a regular occurrence, and the flat terrain gives escaping groundwater nowhere to go once a line begins to fail."
        },
        "Costa Mesa": {
            "intro": "Between a high water table and plumbing that has aged well past its prime, Costa Mesa homes can take on water fast. Local crews start extracting the same day you call.",
            "context": "Costa Mesa occupies the mesas and lowlands of central Orange County, between the Santa Ana River channel and the Upper Newport Bay. The older westside neighborhoods mix small post-war houses with light industrial yards, while the eastside has been rebuilt with townhomes and mid-rise buildings. Near the bay the water table sits high enough that drainage backs up quickly during winter storms, and marine air combined with original galvanized service lines shortens the working life of plumbing installed in the middle of the last century."
        },
        "Santa Ana": {
            "intro": "In a dense historic city like Santa Ana, water finds its way under pavement and through shared walls. Getting extraction started early is what protects the property.",
            "context": "Santa Ana is the seat of Orange County and its most densely populated city, with a historic downtown of early twentieth-century commercial buildings ringed by neighborhoods of bungalows, Spanish Colonial fourplexes, and later apartment blocks. The Santa Ana River forms the western boundary, and the older street grid was laid out long before modern storm drainage existed. Narrow lots, rear alleys, and mature street trees make it common for a break in a service line or a lateral drain to be discovered only after water has travelled beneath pavement or through a shared wall into a neighboring unit."
        },
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
