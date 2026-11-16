#!/usr/bin/env python3
"""Round 6 SEO boost - inject 24h section + local FAQ before 'Nearby Service Areas'.
Idempotent: skips pages that already contain a 24-Hour block.
Only edits the 9 pages of round 6. Never touches TITLE/DESC/INTRO/CONTEXT.
"""
import re
import sys
from pathlib import Path

PAGES = Path(__file__).resolve().parent.parent / "src" / "pages"
ANCHOR = '<h2 class="text-2xl md:text-3xl font-bold text-primary mb-6">Nearby Service Areas</h2>'

H2 = '<h2 class="text-2xl md:text-3xl font-bold text-primary mb-6">{t}</h2>'
P_OPEN = '<p class="text-gray-700 leading-relaxed mb-10">'
QA_DIV = '<div class="space-y-4 mb-10">'
Q_BOX = '<div class="bg-bg-light border border-gray-100 rounded-lg p-5">'
H3 = '<h3 class="font-bold text-primary mb-2">{q}</h3>'
A_P = '<p class="text-gray-600 text-sm leading-relaxed">{a}</p>'

# 9 unique angles, every number/fact taken from each page's CONTEXT
DATA = {
    "camarillo": {
        "h2a": "24-Hour Flood Cleanup in Camarillo",
        "body": (
            "Camarillo still reads as a farming valley in places, and that shapes how water behaves here. "
            "On the outlying parcels a house can sit at the end of a long private service run or draw from "
            "its own well, so a failed line or a worn irrigation main can soak the ground for days before "
            "anything shows indoors. Calleguas Creek and its tributaries carry the valley's runoff, and in a "
            "wet winter the water table under Pleasant Valley rises quickly, pushing moisture up through "
            "slabs and low additions. Crews covering 93010 answer calls daily from 10:00 AM to 2:00 AM."
        ),
        "h2b": "Camarillo Water Damage FAQ",
        "faq": [
            ("Where does water usually start on Camarillo's rural parcels?",
             "Most often underground and far from the house. Long service runs cross open ground, wells and "
             "pressure tanks sit apart from the structure, and irrigation mains feed hedges and nursery rows. "
             "A break in any of them can saturate soil for weeks; the tell is usually a patch of ground that "
             "never dries or a pump that runs when no fixture is open."),
            ("Why does the water table matter in Pleasant Valley?",
             "The valley is a low farming plain ringed by the Camarillo Hills and the Santa Monica Mountains, "
             "and Calleguas Creek drains it from end to end. After sustained winter rain the groundwater sits "
             "high enough that slab edges, garages, and low-floor additions wick moisture upward even with no "
             "leak at all, which is why drying has to include the slab and not just the visible wall."),
            ("What tends to fail in the 1960s subdivisions?",
             "The neighborhoods that filled in around the wartime hospital and airfield are now well past sixty "
             "years. Supply piping, water heater connections, hose bibs, and the original drain runs were "
             "installed together and tend to fail in the same decade, so a first repair often turns up a second "
             "weak point close behind it."),
        ],
    },
    "duarte": {
        "h2a": "24-Hour Flood Cleanup in Duarte",
        "body": (
            "Duarte takes water from two directions, and each arrives differently. When a winter storm hits the "
            "steep, sometimes burned slopes of the San Gabriel range, Fish Canyon and the Duarte Wash push "
            "debris-laden runoff and sheet flow straight down onto the terraced streets above Foothill "
            "Boulevard, where retaining walls can hold it against a foundation before it ever reaches a gutter. "
            "In the older bungalows below, original drain lines under the floors are eighty to a hundred years "
            "old. Lines for 91009 stay open daily, 10:00 AM to 2:00 AM."
        ),
        "h2b": "Duarte Water Damage FAQ",
        "faq": [
            ("How quickly can canyon runoff reach a Duarte house?",
             "Minutes, not hours. The city sits across the mouths of Fish Canyon and the Duarte Wash where the "
             "range drops sharply to the valley floor, so a burst of rain upslope becomes sheet flow on the "
             "terrace streets almost immediately. On hillside lots the water usually arrives at the uphill wall "
             "or the garage door first, which is where diversion has to start."),
            ("What should be checked first in an old Route 66 bungalow?",
             "The drain lines under the floor. Houses lining Foothill Boulevard from the citrus era still carry "
             "original cast drain runs and supply piping installed long before modern pressure standards, and "
             "they fail slowly — a cracked joint seeps into the subfloor for months before it reaches a room. "
             "Moisture readings at the baseboards and around the bathroom tell you more than looking for a puddle."),
            ("Do hillside properties need different equipment?",
             "Yes. Terraced lots with retaining walls create pockets where water stands against the structure, "
             "and access is usually a slope, a stair, or a narrow side yard rather than a driveway. Extraction "
             "there starts at the lowest terrace and works upward with portable units, because truck-mounted hose "
             "runs cannot always reach the water."),
        ],
    },
    "covina": {
        "h2a": "24-Hour Water Damage Restoration in Covina",
        "body": (
            "Covina was built on irrigation, and some of that old orchard network is still down there. The "
            "sprinkler mains and lateral lines that replaced the citrus-era ditches share the same ground as "
            "clay sewer laterals laid decades ago, and the mature trees along the older blocks push roots "
            "straight into the joints. A hairline crack that would stay harmless in sandy soil widens under root "
            "pressure until a slab in a postwar tract, or an apartment court off Foothill Boulevard, turns wet. "
            "Dispatch for 91722 runs every day from 10:00 AM to 2:00 AM."
        ),
        "h2b": "Covina Water Damage FAQ",
        "faq": [
            ("Why do tree roots keep finding Covina's sewer laterals?",
             "Because the laterals are clay and old. The groves that defined the town were plowed under after "
             "the war, but the trees planted along the streets and in back yards stayed, and their roots seek "
             "the moisture escaping at every joint. Once inside, roots widen the gap and catch paper and grease, "
             "so the line backs up before it shows any sign of damage on the surface."),
            ("What do the San Gabriel River spreading grounds mean for my property?",
             "They sit west of town and are designed to let river water sink into the basin on purpose, which "
             "keeps shallow groundwater higher on that side of the city during wet years. For a house with a "
             "slab on grade, that means more moisture available to wick upward, and it is a good reason to check "
             "the base of exterior walls after a wet winter rather than only after a visible leak."),
            ("Covina's postwar tracts are about seventy years old — what fails first?",
             "Supply lines and drain runs, usually within a few years of each other. The ranch tracts and small "
             "apartment courts put in after the war used materials with a similar service life, so a pinhole in "
             "a copper run or a leaking water heater connection is often the first of several failures on the "
             "same property."),
        ],
    },
    "azusa": {
        "h2a": "24-Hour Flood Cleanup in Azusa",
        "body": (
            "Azusa's water rarely stays where it started. North of the main corridor the ground climbs toward "
            "the mouth of the San Gabriel Canyon, and a storm sends runoff off steep canyon ground onto small "
            "hillside lots within minutes. Below that, the valley portion rests on deep alluvial soil the river "
            "left behind, and that material carries a leak sideways through sand and gravel with very little "
            "resistance — a broken service line near the curb can surface in a garage or under a bedroom floor "
            "twenty feet away. For 91702, crews are reachable daily from 10:00 AM to 2:00 AM."
        ),
        "h2b": "Azusa Water Damage FAQ",
        "faq": [
            ("Why does a leak in Azusa show up far from the break?",
             "The alluvial soil under the valley portion is loose sand and gravel laid down by the river, and "
             "water moves through it almost freely. A failure at a service connection or under a walkway will "
             "follow the path of least resistance and appear wherever the slab or the footing gives it an "
             "opening, which is why locating it means mapping moisture across the whole floor."),
            ("How should canyon-side properties get ready for winter?",
             "Before the first big storm, clear the swales and area drains on the uphill side, check that the "
             "dirt grade still slopes away from the foundation, and keep sandbags where the water historically "
             "crosses the property line. On the small lots near the canyon mouth there is very little room to "
             "store runoff, so it needs somewhere to go before it reaches a wall."),
            ("What is typical of Azusa's small-lot tract housing?",
             "Modest houses on tight parcels, often with a later addition or a converted garage, and a handful "
             "of apartment buildings along the main corridors. Side yards are narrow enough that hose runs and "
             "equipment have to be staged in front, and in the apartments a leak above is usually discovered by "
             "the unit below."),
        ],
    },
    "santa-ana": {
        "h2a": "24-Hour Flood Cleanup in Santa Ana",
        "body": (
            "In Santa Ana the water almost always travels before it shows. The downtown blocks were laid out "
            "when storm drainage meant a gutter and a ditch, and the dense mix of bungalows, Spanish Colonial "
            "fourplexes and apartment buildings means a failed supply line can run beneath pavement, cross a "
            "shared wall, and reach the next unit before anyone thinks to call. Rear alleys and mature street "
            "trees hide the route it took. Help for 92701 is available every day, 10:00 AM to 2:00 AM, "
            "including upper-floor units."
        ),
        "h2b": "Santa Ana Water Damage FAQ",
        "faq": [
            ("My neighbor's ceiling is wet but my unit looks fine — where do I start?",
             "Assume the water is between you and treat both sides. In a fourplex or an attached bungalow the "
             "supply risers and drain stacks run in the shared wall, so shutting off your own unit proves "
             "nothing. Read moisture on both sides of the wall, look at the base of the shared stack, and bring "
             "the owner or manager in early because the failed run may be common property."),
            ("Why does the Santa Ana River matter to flooding downtown?",
             "It forms the western boundary of the city, and the older grid near it was platted long before "
             "modern storm drainage existed. The river channel moves regional water, but the streets behind it "
             "were never designed for the volume a hard winter storm drops in an hour, so ponding at the low "
             "corners of the old grid is a drainage story, not a plumbing one."),
            ("Can a hidden leak under pavement really reach my unit?",
             "Yes, and it is common on these blocks. Service lines run under sidewalks and rear alleys, and a "
             "slow break there saturates the base material until water finds the path of least resistance — a "
             "crack in a wall, a joint at the foundation, or the floor of the unit nearest the street. That is "
             "why the search starts outside the building rather than in the room that looks wet."),
        ],
    },
    "midway-city": {
        "h2a": "24-Hour Water Damage Restoration in Midway City",
        "body": (
            "Midway City has almost no fall to work with. The community sits on drained bean-field ground so "
            "flat and so fully paved that the storm drains and sewer laterals have only inches of gradient, and "
            "the water table under the Bolsa Avenue corridor stays close to the surface all year. In a heavy "
            "winter storm the street system backs up instead of carrying water away, and it comes up first in "
            "whatever was built lowest — garages, carports, converted porches and the low-floor additions tacked "
            "onto post-war houses. Call takers for 92655 work daily from 10:00 AM to 2:00 AM."
        ),
        "h2b": "Midway City Water Damage FAQ",
        "faq": [
            ("Why does water come up through the floor instead of draining away?",
             "Because there is nowhere lower for it to go. With a high water table and very little fall in the "
             "pipes, a storm that overwhelms the street inlets pushes water back through the lowest openings — "
             "floor drains, toilet bases, shower curbs — rather than letting it run off. Extracting fast matters, "
             "but stopping the inflow at the source matters more."),
            ("How do you trace plumbing in a house that keeps getting added onto?",
             "Room by room, with the meter. Post-war houses here were extended repeatedly, and additions often "
             "left old exterior hose bibs and capped stubs buried in new walls. Shutting every fixture and "
             "watching the meter separates a supply leak from a drain problem, and a moisture scan across the "
             "additions shows which phase of construction the water is hiding in."),
            ("Does the East Garden Grove-Wintersburg Channel protect the community?",
             "It carries regional drainage past the neighborhood, but it does not change the local picture: the "
             "ground here is low, the tidal wetlands of Bolsa Chica sit just to the south, and the internal "
             "street drains still depend on gravity that this terrain barely provides. Water can pond on a block "
             "even when the channel itself is running well below capacity."),
        ],
    },
    "artesia": {
        "h2a": "24-Hour Water Damage Restoration in Artesia",
        "body": (
            "Artesia packs a lot of plumbing under very old concrete. The dairy-era lots along Artesia Boulevard "
            "were laid out long and narrow, with detached garages, rear sheds and patios poured decades before "
            "today's codes, and the water service and sewer lateral for the house frequently run directly "
            "beneath those slabs. A slow underground failure therefore has no visible outlet: the first evidence "
            "is usually a damp patch at a back wall, a soft spot in a patio, or a bill that climbs for no "
            "reason. Scheduling for 90702 covers all seven days, 10:00 AM to 2:00 AM."
        ),
        "h2b": "Artesia Water Damage FAQ",
        "faq": [
            ("How do you find a leak under a patio or a detached garage slab?",
             "By isolating first and scanning second. Close the main and watch the meter to confirm the loss is "
             "on the supply side, then use moisture and thermal readings to follow the wet trail from the house "
             "outward. On these deep lots the lateral often crosses more than one slab, so the wettest point is "
             "not always the break."),
            ("Why did Artesia's dairy-era lots end up shaped this way?",
             "The town was built to supply milk to the region, and a working dairy parcel needed depth — a house "
             "in front, yards and outbuildings behind, and vehicle access down the side. That pattern survived "
             "long after the dairies left, which is why so many properties here have structures sitting on "
             "concrete that was poured for animals, carts and trucks rather than for modern drainage."),
            ("Is a rising water bill a reliable warning sign?",
             "It is one of the best ones available on a lot like this. A failing lateral or a seeping service "
             "line can lose hundreds of gallons before anything surfaces, and the meter registers all of it. "
             "Rule out the easy causes first — a running toilet, an irrigation cycle — then treat a bill that "
             "stays high with everything off as a buried leak until it is proven otherwise."),
        ],
    },
    "arcadia": {
        "h2a": "24-Hour Flood Cleanup in Arcadia",
        "body": (
            "Arcadia's north side drains a mountain. The Santa Anita Wash and the foothill debris basins above "
            "the city are built to catch rock, silt and storm water coming off the San Gabriel range, and when a "
            "storm exceeds what that system can hold, the overflow takes the streets that climb into the "
            "foothills first. Lower down, the 1920s to 1950s houses in the central blocks still have original "
            "drain lines running under hardwood floors, so a cracked or backed-up line lifts boards instead of "
            "leaving a puddle. Requests for 91006 are handled daily from 10:00 AM to 2:00 AM."
        ),
        "h2b": "Arcadia Water Damage FAQ",
        "faq": [
            ("What are the debris basins above Arcadia actually doing?",
             "They slow the mountain. A storm on bare or burned slopes above the city arrives loaded with rock, "
             "sand and branches, and the basins are there to drop that material before it reaches the concrete "
             "channel of the Santa Anita Wash. Once a basin fills, water carries the load straight down, which "
             "is when foothill streets and driveways take the hit."),
            ("Why do hardwood floors buckle before water is visible?",
             "Because the line failing is underneath them. The older central blocks still have original drain "
             "runs beneath the subfloor, and a joint that seeps there wets the wood from below. Cupping and "
             "springy boards appear long before a stain on the ceiling below, and by the time the floor moves "
             "the subfloor has usually been wet for a while."),
            ("Do Arcadia's mature oaks cause plumbing trouble?",
             "They contribute. The tree-lined streets are the city's signature, and the same roots that lift "
             "sidewalks work into the clay laterals and older irrigation lines that run out to the curb. Root "
             "intrusion narrows a drain gradually, so repeated slow backups in the same fixture are worth "
             "camera-inspecting rather than augering again."),
        ],
    },
    "lawndale": {
        "h2a": "24-Hour Emergency Water Extraction in Lawndale",
        "body": (
            "Lawndale gets roughly 12.82 inches of rain across 35.7 wet days, and nearly all of it arrives in a "
            "few winter storms over a city that is completely built out. The ground is sandy loam, which drains "
            "unevenly — quickly on one block, hardly at all on the next — so street ponding during a downpour is "
            "ordinary, and it pushes water toward the lowest house on the block. Inside, a median construction "
            "year of 1963 means most supply lines and laterals have now been in service for six decades. Crews "
            "serving 90260 are on call daily, 10:00 AM to 2:00 AM."
        ),
        "h2b": "Lawndale Water Damage FAQ",
        "faq": [
            ("Why does one Lawndale block flood while the next stays dry?",
             "Sandy loam is not uniform, and neither is the grading. A lot that was regraded for a later addition "
             "or a new driveway can sit an inch or two lower than its neighbors, and on flat ground that is "
             "enough to collect the whole block's runoff. Add patched pavement that redirects the sheet flow and "
             "you get a repeat flooding address."),
            ("What fails first in a 1963-era Lawndale house?",
             "Usually the supply side. Water heaters, hose bibs and the original interior runs were installed "
             "together in the middle of the last century and reach the end of their life at about the same time, "
             "and drain lines under a slab give no warning until a room stays damp. When one component goes, "
             "expect the rest to follow within a few years."),
            ("Zone X shows minimal flood hazard — does that mean no risk?",
             "It means the property sits outside the mapped one-percent annual chance floodplain, which is a "
             "statement about riverine and coastal flooding, not about a broken lateral or a storm drain that "
             "backs up in a downpour. Plumbing failures here ignore the map, and street ponding can still reach "
             "a low garage."),
        ],
    },
}


def build_block(d):
    parts = [
        H2.format(t=d["h2a"]),
        P_OPEN + d["body"] + "</p>",
        "",
        H2.format(t=d["h2b"]),
        QA_DIV,
    ]
    for q, a in d["faq"]:
        parts.append("  " + Q_BOX)
        parts.append("    " + H3.format(q=q))
        parts.append("    " + A_P.format(a=a))
        parts.append("  </div>")
    parts.append("</div>")
    return "\n".join(parts)


def main():
    changed = []
    for slug, d in DATA.items():
        path = PAGES / f"water-damage-repair-{slug}-ca.astro"
        src = path.read_text()
        if not path.exists():
            print(f"MISSING FILE: {path}")
            return 1
        if "Water Damage FAQ" in src:
            print(f"SKIP (already boosted): {slug}")
            continue
        if src.count(ANCHOR) != 1:
            print(f"ABORT {slug}: anchor count = {src.count(ANCHOR)}")
            return 1
        block = build_block(d)
        new = src.replace(ANCHOR, block + "\n\n      " + ANCHOR, 1)
        # sanity: TITLE/DESC lines must be byte-identical (they are template literals)
        for var in ("TITLE", "DESC"):
            old_line = next((l for l in src.splitlines() if l.startswith(f"const {var} =")), None)
            new_line = next((l for l in new.splitlines() if l.startswith(f"const {var} =")), None)
            assert old_line is not None and old_line == new_line, f"{slug}: {var} changed!"
        path.write_text(new)
        changed.append(slug)
    print("MODIFIED:", ", ".join(changed) if changed else "(none)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
