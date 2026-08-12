#!/usr/bin/env python3
"""Rewrite CONTEXT for city pairs flagged as doorway-risk (Jaccard > 0.30).
Keeps TRUE local facts (NOAA precip, FEMA zones, housing age) but gives each
city a distinct angle, sentence structure, and detail set.
"""
import re, glob

NEW = {
"commerce": "Commerce grew up as an industrial hub east of downtown Los Angeles, a grid of warehouses, rail yards, and mid-century homes squeezed between the Santa Ana and Los Angeles rivers. The Los Angeles River, running channelized along the city's edge, carries winter storm runoff past industrial parcels before it reaches the harbor. Decades of pavement mean rain has nowhere to soak in, and aging supply lines under commercial slabs are a common source of indoor flooding. Commerce sees roughly 15.32 inches of rain a year across about 24.4 wet days, with FEMA mapping most of the city in Low-risk Zone X.",

"vernon": "Vernon is one of California's most unusual municipalities - a tiny industrial city, barely five square miles, home to packing plants, metal shops, and warehouses but only a small residential population. Much of the housing dates to 1953 or earlier, and the city's flat, former river-bottom ground along the channelized Los Angeles River floods only when drainage backs up during heavy rain. With about 12.82 inches of annual rainfall spread over 35.7 wet days, most storms arrive in winter, when saturated ground and old sewer laterals combine to send water into low-lying buildings.",

"lynwood": "Lynwood's grid of 1950s tract homes sits on the flat coastal plain between the 105 and 710 freeways, ground that was strawberry and dairy farmland until mid-century. The low elevation and heavy paving leave stormwater few outlets, and winter storms can turn intersections into shallow lakes that creep toward front doors. Original galvanized plumbing in many postwar homes is past its useful life, making pipe bursts a familiar emergency. Lynwood averages 12.26 inches of rain over 35.2 wet days a year; FEMA maps the city mostly as Low-risk Zone X.",

"manhattan-beach": "Manhattan Beach is a compact beach city where the strand's sand-side cottages and the hilltop homes above Sepulveda Boulevard face opposite problems. Down by the water, salt-laden fog corrodes water heaters and copper lines within a decade, while the hillside streets channel winter runoff straight down to the flats. The pier and downtown sit on sandy fill that drains quickly, but groundwater intrusion troubles the lowest beachfront lots during high winter swells. Annual rainfall is modest at 12.82 inches over 35.7 wet days, and FEMA puts Zone VE along the shoreline with most of the city in Low-risk Zone X.",

"redondo-beach": "Redondo Beach wraps around a crescent bay where King Harbor, the pier, and the beachfront flatlands meet steep hillside neighborhoods to the south and west. The harbor district sits on fill over the old lagoon, where high groundwater and storm surge can push water into ground-level garages and shops. Hillside homes above the harbor deal with the opposite hazard: runoff cutting across sloped yards and seeping into foundations. Winter storms bring about 13.76 inches of rain over 35.1 wet days, and FEMA maps the harbor shoreline as Zone VE while most inland parcels sit in Low-risk Zone X.",

"bardsdale": "Bardsdale is a quiet unincorporated farming community on the north bank of the Santa Clara River between Fillmore and Santa Paula. Citrus orchards and pre-war farmhouses sit on bench land that rises gently from the river, and many homes still depend on private wells and aging galvanized pipes. When winter storms stall over Ventura County, the river can jump its channel and threaten the low fields closest to the water. The community receives about 17.38 inches of rain across 28.9 wet days a year, with FEMA mapping the river corridor as Zone AE and the townsite as Zone X.",

"fillmore": "Fillmore's historic downtown - a Main Street of brick storefronts that has hosted Hollywood film crews - anchors a farm town where the Santa Clara River bends around the city's south side. The 1969 and 2005 floods reshaped how residents think about the river: water that normally stays in its banks can spread across low farmland in a big winter season. Many of the town's older homes carry original cast-iron plumbing, and cold snaps bring their share of burst pipes. Fillmore sees about 17.38 inches of rain a year over 28.9 wet days; FEMA zones most of the river corridor Moderate (AE) with the city core in Zone X.",

"castaic": "Castaic hugs the hills around the lake that bears its name, a recreation and commuter community straddling the Interstate 5 corridor at the north end of Los Angeles County. Winter storms pile rain on the surrounding chaparral slopes, sending runoff down steep streets and into the creeks that feed the lake. Homes built into hillsides contend with drainage that flows toward foundations, while older subdivisions near the lake face aging supply lines. The area averages 18.63 inches of rain over 43.8 wet days a year, and FEMA maps much of Castaic as shaded Zone X (0.2% annual chance).",

"piru": "Piru is a small valley town tucked where Piru Creek comes out of the Los Padres National Forest and crosses the Santa Clara Valley floor. The creek, dammed upstream at Lake Piru, can still run bank-full after long winter rains, and flash-flooding along the corridor is part of the area's history. The town's housing stock, much of it built around 2003, is a mix of ranch homes and newer tracts on former orchard land. Piru gets about 18.63 inches of rain over 31.9 wet days a year; FEMA maps the creek corridor as Zone AE and the town core as Zone X.",

"littlerock": "Littlerock sits along the Pearblossom Highway in the high desert of the Antelope Valley, where the Mojave's dry washes flash with water only a few times a year. Summer monsoon cells and winter cloudbursts drop rain faster than the sandy desert ground can absorb it, turning washes and low-water crossings into sudden torrents. Homes here often run on private wells with long supply lines exposed to freezing nights. With just 6.73 inches of annual rainfall across 20.5 wet days - among the driest on this site - one intense storm can do more damage than a wet season elsewhere. FEMA maps much of the area as shaded Zone X (0.2% annual chance).",

"moorpark": "Moorpark grew from an apricot-farming town into one of Ventura County's fastest-growing suburbs, with most of its housing built during the 1980s and 1990s boom. The city spreads across the floor and lower slopes of the Simi Valley, where winter storms run off the hills and fill the drainage channels that crisscross new subdivisions. Newer homes have modern plumbing, but the 1980s tracts are reaching the age where water heaters and supply lines fail. Rainfall averages about 17.4 inches a year, and FEMA places most of Moorpark in shaded Zone X (0.2% annual chance).",

"bell-gardens": "Bell Gardens packs nearly 40,000 people into under three square miles, making it one of the densest cities in Los Angeles County. The Rio Hondo channel forms part of its eastern border, and the city's flat, former ranch land - developed mainly in the 1950s - drains slowly when storms hit. Older sewer and water lines under the tight street grid are a frequent source of sudden indoor flooding, and heavy rain can push the channel toward its banks. The city sees about 12.26 inches of rain across 35.2 wet days a year, with most of its housing dating to 1957 and FEMA mapping it as Low-risk Zone X.",
}

changed = []
for f in glob.glob("src/pages/water-damage-repair-*.astro"):
    city = re.search(r"const CITY = \"([^\"]*)\"", open(f).read())
    if not city: continue
    slug = re.search(r"water-damage-repair-([a-z-]+)-ca", f).group(1)
    if slug not in NEW: continue
    src = open(f).read()
    m = re.search(r'const CONTEXT = "[^"]*"', src)
    if not m: continue
    new_src = src.replace(m.group(0), f'const CONTEXT = "{NEW[slug]}"')
    open(f, "w").write(new_src)
    changed.append(slug)

print(f"Reécrit : {len(changed)} pages -> {', '.join(sorted(changed))}")
