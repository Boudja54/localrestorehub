#!/usr/bin/env python3
"""Fix doorway pages: réécrit INTRO + CONTEXT uniques par ville."""
import os, re

FIXES = {
    "Bell": {
        "intro": "A sudden water emergency in Bell can happen at any time. Whether it's a burst pipe in an older post-war home or flooding after heavy rain, the damage spreads fast in this dense urban city.",
        "context": "Bell is one of the most densely populated cities in Los Angeles County, part of the Gateway Cities corridor east of downtown. Much of its housing stock dates from the 1940s-1960s, when galvanized steel plumbing was standard — pipes that are now at the end of their lifespan. The flat, heavily paved terrain leaves little room for stormwater absorption, so intense rain can overwhelm the city's drainage system quickly.",
    },
    "Bell Gardens": {
        "intro": "When water breaks through in Bell Gardens, the damage spreads faster than most homeowners expect. Aging infrastructure and dense urban layout make every minute count.",
        "context": "Bell Gardens sits in the Gateway Cities region of southeast Los Angeles County, bordered by the Rio Hondo channel. The city's flat, low-lying terrain — much of it former agricultural land converted in the 1950s — drains slowly, and its aging sewer and water lines are a common source of sudden indoor flooding. Heavy winter storms can also push the Rio Hondo toward its banks.",
    },
    "Compton": {
        "intro": "Water damage doesn't wait — and in Compton, the combination of aging infrastructure and flat urban terrain creates real risks. Every minute of delay increases the damage.",
        "context": "Compton is a flat, fully urbanized city in the southern portion of Los Angeles County. Built out largely in the 1940s and 1950s, much of its housing still runs on original galvanized plumbing, a frequent source of catastrophic leaks. The city's low elevation and dense paving mean that during major rain events, street flooding can back up into homes before residents have time to react.",
    },
    "Downey": {
        "intro": "In Downey, water emergencies often arrive without warning. A failing water heater or a sewer backup can turn a quiet evening into a flooding event in minutes.",
        "context": "Downey lies in the flat Gateway Cities corridor, roughly bounded by the San Gabriel River. The city's mid-century housing boom left a legacy of aging cast-iron and galvanized pipes, and homes near the river corridor face periodic groundwater pressure issues. Downey's mostly clay soils hold water, which can mean slow-draining yards and higher flood risk around older slab foundations.",
    },
    "El Segundo": {
        "intro": "Water damage in El Segundo can strike without warning — a burst pipe, a failed water heater, or coastal humidity taking a toll on older systems.",
        "context": "El Segundo is a coastal city wedged between the Pacific Ocean and LAX. Salt air and ocean mist accelerate corrosion in metal plumbing, and the city's post-war housing stock is a prime candidate for hidden pipe failures. As a beachside community, El Segundo also faces occasional street flooding when heavy winter storms push inland from the ocean.",
    },
    "Gardena": {
        "intro": "A sudden water emergency in Gardena can happen at any time. Whether it's a water heater failure or a slab leak, the damage compounds quickly.",
        "context": "Gardena sits in the South Bay area of Los Angeles County, on former agricultural land that was subdivided in the 1950s. Many of its single-story homes still have the original plumbing and concrete slab foundations — where a hidden slab leak can silently soak a home for weeks before surfacing. The city's flat terrain and aging water mains make unexpected line failures a recurring issue.",
    },
    "Hawthorne": {
        "intro": "Water damage in Hawthorne can strike without warning — a burst pipe under the slab or an aging water main in the street sending water into your home.",
        "context": "Hawthorne is a flat, densely built South Bay city whose housing was largely constructed in the 1940s and 1950s. Slab-on-grade foundations and original copper or galvanized plumbing are common, and hidden slab leaks are a frequent cause of damage. Its proximity to the LAX flight path and heavy street paving means drainage is a recurring concern during intense rain.",
    },
    "Hermosa Beach": {
        "intro": "In Hermosa Beach, water emergencies often arrive without warning — coastal weather, aging pipes, or a hillside home fighting gravity and moisture.",
        "context": "Hermosa Beach is a compact beach city on the Pacific coast, with some of the oldest housing stock in the South Bay. Ocean proximity means corrosive salt air attacks metal plumbing and water heaters, and the city's narrow, sandy-soil lots have limited drainage. Homes close to the strand also contend with groundwater and the occasional high-tide or storm-surge flooding.",
    },
    "Lawndale": {
        "intro": "Water damage in Lawndale can strike without warning — a burst pipe, a failing water heater, or drainage overwhelmed by a heavy downpour.",
        "context": "Lawndale is a small, fully built-out South Bay city dominated by mid-century single-family homes. Its flat terrain and sandy-loam soil drain inconsistently, and much of the housing still carries original plumbing nearing the end of its useful life. During big winter storms, the city's older street drainage can be quickly overwhelmed, pushing water toward low-lying homes.",
    },
    "Lynwood": {
        "intro": "A sudden water emergency in Lynwood can happen at any time. Whether it's an aging main line or a roof failure during a storm, the damage spreads fast.",
        "context": "Lynwood sits in the flat, urbanized southern corridor of Los Angeles County, threaded by the 105 and 710 freeways. Built out primarily in the 1950s, the city's housing stock relies heavily on original plumbing systems, and its low elevation with extensive paving leaves stormwater few places to go. Heavy rain frequently turns intersections into shallow lakes that can back up into homes.",
    },
    "Malibu": {
        "intro": "Water damage in Malibu carries its own risks — from winter storms on the coast to canyon homes facing runoff and erosion. Fast response is essential.",
        "context": "Malibu stretches 21 miles along the Pacific Coast Highway, where the Santa Monica Mountains meet the ocean. This is NOT the South Bay — it's a uniquely exposed coastal corridor. Homes in the canyons face hillside runoff, debris flows, and damaged drainage after heavy rain, while beachfront properties contend with high tides and storm surge. The mix of ocean exposure, steep terrain, and long distances between services makes professional water extraction particularly time-critical here.",
    },
    "Manhattan Beach": {
        "intro": "When water breaks through in Manhattan Beach, the damage spreads quickly — ocean air, aging systems, and a hillside location all play a role.",
        "context": "Manhattan Beach is an upscale coastal city with both beachfront properties and hillside homes overlooking the Pacific. Salt air aggressively corrodes metal plumbing and water heaters throughout the city, while hillside homes face unique runoff and foundation drainage challenges. The beachside flatlands, built on sandy soils, can see groundwater intrusion and storm-driven flooding during winter swells.",
    },
    "Maywood": {
        "intro": "Water damage in Maywood can strike without warning — a burst pipe in a dense neighborhood or street flooding after heavy rain.",
        "context": "Maywood is one of the smallest and most densely populated cities in Los Angeles County, a fully urbanized Gateway Cities community. Its compact lots and older housing stock mean plumbing failures affect neighbors quickly, and there is little open ground to absorb stormwater. During heavy rain, the city's aging storm drains can be overwhelmed, pushing water into low-lying single-family homes.",
    },
    "Redondo Beach": {
        "intro": "A sudden water emergency in Redondo Beach can happen at any time — ocean weather, a slab leak, or an aging water heater can flood a home fast.",
        "context": "Redondo Beach spans both coastal flatlands and steep hillside neighborhoods above the Pacific. Salt air is hard on plumbing and water heaters across the city, while hillside homes face runoff and drainage problems during winter storms. The coastal lowlands, including the harbor district, contend with high groundwater and occasional storm-surge flooding that can affect even well-maintained homes.",
    },
}

base_dir = "/root/localrestorehub/src/pages"
fixed = 0
for fname in os.listdir(base_dir):
    if not fname.startswith("water-damage-repair-") or not fname.endswith(".astro"):
        continue
    fpath = os.path.join(base_dir, fname)
    with open(fpath) as f:
        content = f.read()

    city_match = re.search(r'const CITY = "([^"]+)"', content)
    if not city_match:
        continue
    city = city_match.group(1)

    if city not in FIXES:
        continue

    fix = FIXES[city]
    content = re.sub(
        r'const INTRO = "[^"]*"',
        'const INTRO = "' + fix["intro"] + '"',
        content, count=1
    )
    content = re.sub(
        r'const CONTEXT = "[^"]*"',
        'const CONTEXT = "' + fix["context"] + '"',
        content, count=1
    )

    with open(fpath, "w") as f:
        f.write(content)
    fixed += 1
    print(f"✅ {city} — réécrit")

print(f"\n🎉 {fixed} pages corrigées")
