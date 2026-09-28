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
    "Buena Park": {
        "intro": "Water damage in Buena Park rarely stays in one room — a failed line under a slab or a backed-up drain spreads through flooring and walls quickly. Local crews can start extraction the same day you call.",
        "context": "Buena Park began as a late-nineteenth-century farming community of berry fields and dairies, and its layout still reflects that past: a compact older core near Beach Boulevard and California Avenue, ringed by the large tract subdivisions built after the Second World War. Coyote Creek traces part of the city's western edge, and the flat, fully developed ground in between leaves stormwater almost nowhere to collect. Houses from the post-war boom run on supply lines and drain laterals installed when the tracts went in, and with so much slab-on-grade construction, a break often surfaces well away from where it actually started.",
    },
    "Bellflower": {
        "intro": "In a flat, densely built city like Bellflower, water from a failed line has nowhere to drain and spreads under the floors instead. A fast local response limits how far it reaches.",
        "context": "Bellflower was laid out in 1906 as a dairy colony on the level ground between the Los Angeles and San Gabriel river corridors, and it grew into a small farm town along the road that still carries its name. The wartime and post-war years replaced the dairies with dense tracts of stucco houses on narrow lots, most of them built with galvanized supply lines and cast-iron drains that are now well past their original service life. Because the city is almost entirely paved and sits on flat ground, stormwater and escaped water depend on the same street drainage, so an indoor break can stay hidden until a water bill jumps or a damp patch appears in a rear alley or garage.",
    },
    "Arcadia": {
        "intro": "With the San Gabriel Mountains rising directly above Arcadia, water arrives both as storm runoff from the hills and as plumbing failures hidden inside older walls. Quick extraction protects the structure and the lot.",
        "context": "Arcadia occupies the mouth of the Santa Anita Wash at the base of the San Gabriel Mountains, a former rancho subdivided into tree-lined residential streets in the early twentieth century and still known for its rows of mature oaks. The northern edge of the city climbs into the foothills, where debris basins and concrete channels carry mountain runoff down toward the valley floor, while the older central blocks keep 1920s to 1950s houses with original drain lines beneath hardwood floors. Runoff arriving from above and aging supply lines working below is a pairing that lets a single storm or one failed fitting put water where it should never be.",
    },
    "Santa Clarita": {
        "intro": "Hard clay ground, long dry spells, and then heavy winter storms make Santa Clarita plumbing fail with little warning. Local crews handle both storm flooding and sudden pipe breaks.",
        "context": "Santa Clarita spreads along the Santa Clara River through the valley between the San Gabriel and Santa Susana ranges, where an old railroad and oil town grew into a patchwork of master-planned Valencia neighborhoods and older Saugus and Newhall blocks. Much of the ground beneath the valley is dense clay and hardpan that sheds water rather than absorbing it, so winter storms arrive fast and concentrate in washes and streets. Homes built during the valley's growth decades depend on irrigation lines, pool plumbing, and supply runs sized for a dry climate, and the first heavy rain of the season is when buried leaks and pressure failures tend to announce themselves.",
    },
    "Azusa": {
        "intro": "Azusa sits where the San Gabriel Canyon opens onto the valley, so canyon runoff and aging plumbing are both part of everyday life here. Fast local extraction keeps a small failure from becoming a flooded home.",
        "context": "Azusa sits at the mouth of the San Gabriel Canyon, where the river leaves the mountains and the valley floor begins. The city started as a citrus and agricultural stop along the foothill highway, and the old ranch land was gradually converted after the war into modest tract housing on small lots, with apartment blocks added along the main corridors. Hillside properties on the north side take drainage straight off steep canyon ground, while the deep alluvial soil under the valley portion holds water well enough that an underground leak can travel a surprising distance before it surfaces indoors.",
    },
    "Huntington Beach": {
        "intro": "Salt air, a high water table, and plumbing installed during the post-war boom are a difficult combination in Huntington Beach. When water gets in, quick extraction is what protects the flooring.",
        "context": "Huntington Beach runs along the Orange County coastline from the Santa Ana River mouth to the Bolsa Chica wetlands, a stretch that began the twentieth century as a small beach town and changed completely once oil was struck in the 1920s. Rows of later tract houses and low-rise apartments now stand on the old oil field and on the low ground behind the bluffs, where the water table sits close enough to the surface that drainage has little room to work. Marine air accelerates corrosion on exposed and under-slab lines, and winter storm surf combined with high groundwater can push water up into garages and ground-floor rooms from below rather than from above.",
    },
    "Cowan Heights": {
        "intro": "On the canyon-edge lots of Cowan Heights, a hidden leak can drain away underground for weeks before it ever shows indoors. Professional extraction and drying limit how much of the house is affected.",
        "context": "Cowan Heights is an unincorporated hillside community in the Santa Ana foothills above Tustin, built out as large custom lots stepping along canyon rims rather than as a uniform grid. Most of the houses date from the 1950s into the 1970s, when these parcels were graded and served by the long private water and drain runs that hillside building requires, and several streets still sit beside open canyon ground near Peter's Canyon. Steep driveways, retaining walls, and terraced landscaping shed stormwater toward the structures below them, while porous hillside soil lets an underground break disappear long before anyone notices it indoors.",
    },
    "Brea": {
        "intro": "Brea's hillside streets and older downtown blocks both move water quickly once a line or a drain lets go. A nearby crew can begin extracting the same day.",
        "context": "Brea sits on the northern edge of Orange County where the flat valley gives way to the rolling hills and canyons around Carbon Canyon. The city's oil history began before the turn of the twentieth century, and the working field left behind a town of small older houses near the original downtown, now restored along Birch Street, with suburban tracts filling in the ground between. Streets here climb and bend with the terrain, so runoff from higher blocks crosses lower lots, and the heavy clay soil common throughout the area holds water against foundations instead of letting it drain away.",
    },
    "Camarillo": {
        "intro": "Camarillo's mix of ranch parcels, orchards, and post-war neighborhoods means a water problem can come from a buried line, a well, or a storm all at once. Local crews respond quickly.",
        "context": "Camarillo occupies the Pleasant Valley in Ventura County, a farming plain ringed by the Camarillo Hills and the Santa Monica Mountains that stayed orchards and ranch land well into the twentieth century and still grows strawberries and nursery stock along its edges. The military hospital and airfield established during the Second World War shaped a good part of the town, and surrounding subdivisions filled in from the 1960s onward. Calleguas Creek carries drainage from the valley and its tributaries, so heavy winter rain raises groundwater quickly, while outlying parcels often rely on private wells, long service runs, and irrigation systems that can fail far out of sight.",
    },
    "Lancaster": {
        "intro": "In the high desert, water damage in Lancaster usually arrives all at once — a flash flood or a line failing in a house built for dry heat. Fast extraction protects what the climate normally does not.",
        "context": "Lancaster sits on the floor of the Antelope Valley in the western Mojave, a high desert plain where surrounding mountains drain into dry washes, playas, and alkaline lake beds. The town was a small agricultural stop on the railroad until the aerospace build-out of the 1950s and 1960s filled the valley with tract houses, and those construction methods were aimed at heat and dryness rather than at water. Soil here is often cemented hardpan that absorbs almost nothing, so a summer cloudburst or a winter storm runs off in sheets, and supply lines, cooler feeds, and irrigation runs that sit unused for months are the parts most likely to let go when the season turns.",
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
