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
    # --- batch 2026-10-19 (weekly expansion: bespoke CONTEXT for the 9 picked cities) ---
    'La Habra': {
        "intro": "La Habra's oldest houses were plumbed long before modern codes, and the creek that crosses town carries storm runoff straight past them. A fast local response is what keeps one failed line from becoming a gutted ground floor.",
        "context": 'La Habra began in the 1890s as an avocado and citrus colony straddling the line between Los Angeles and Orange counties, and its main street still shows the shape of that farming town: short blocks of storefronts, small pre-war homes, and packing sheds turned into shops. Oil wells were drilled across the hillsides north of downtown during the boom years, and the land under the older neighborhoods was disturbed by decades of that work. The city fills the flat ground where Coyote Creek and La Canada Verde come together, so runoff from the surrounding slopes funnels through the middle of town. Many homes were built before copper replaced galvanized steel, leaving narrow supply runs buried beneath driveways that were widened long afterwards.',
    },
    'Carson': {
        "intro": 'Almost all of Carson went up inside one building boom, so the same joints are aging together across entire tracts. When one gives out, a nearby crew can be extracting the same day.',
        "context": 'Carson was assembled during the 1960s and 1970s from a patchwork of dairy pasture, oil property, and the old Dominguez rancho, and it only incorporated in 1968, which makes it unusual for the Harbor corridor in having almost no pre-war housing at all. Ranch homes and apartment courts rose within a handful of years beside the freeway, the refinery belt, and the university campus on Dominguez Hills, so roof lines, slabs, and original piping repeat from street to street. The terrain is level and heavily paved, with the Dominguez Channel carrying runoff to the port, and shallow groundwater plus irrigation seep into the very soils that hold buried supply piping. Long stretches of rail-side industry add warehouses and shops with plumbing of their own vintage.',
    },
    'Sierra Madre': {
        "intro": 'Canyon runoff above town and eighty-year-old pipework below it are both ordinary hazards in Sierra Madre. Local crews start extraction the same day you call.',
        "context": 'Sierra Madre is a small foothill settlement laid out in the 1880s at the mouth of a canyon in the San Gabriel range, first reached from the valley by a mule-drawn railway and later connected by the trail that still climbs toward Mount Wilson. Its grid of streets simply stops where the mountainside begins, and the debris basin and flood-control dam above town exist because winter weather drives mud, rock, and fast current down those slopes onto the streets beneath. Buildings date mostly from the 1900s through the 1940s, shingled bungalows, cabins, and later ranch homes on deep terraced lots shaded by oaks and cedars; plenty of them still keep original drain runs, cellar rooms, and crawl areas never sized for the volume a modern washer or drip system pushes through.',
    },
    'San Fernando': {
        "intro": "San Fernando's housing covers more than a century and the piping inside it covers nearly as much. When a line gives out, prompt local extraction is what saves the floors.",
        "context": 'San Fernando is the oldest incorporated municipality in the San Fernando Valley and among the oldest in the region, platted in 1874 around the mission that gave the valley its name. For generations it stayed a small agricultural service town ringed by citrus and walnut orchards and later by warehouses along the rail line, and its building stock reflects that long slow growth: mission-influenced early structures, 1920s bungalows, dense post-war stucco tracts, and apartment courts crowded onto narrow parcels. The Pacoima Wash and its concrete channel cut along the edge of town to move mountain runoff toward the river, and the level valley floor leaves escaping water almost no fall, so a break below a slab creeps under adjoining rooms and garages rather than draining off.',
    },
    'Chino Hills': {
        "intro": 'Graded hillside lots and heavy landscaping mean a break in Chino Hills can travel a long way before it surfaces indoors. A local crew can start extraction right away.',
        "context": "Chino Hills covers the rolling, oak-covered foothills at the southwestern corner of San Bernardino County, where the Chino Valley meets the ridgeline that separates it from Orange County. For most of its history the area was cattle range and dairy pasture; the city only incorporated in the 1990s after a long fight over growth, and much of its housing is therefore recent, from large planned subdivisions and cul-de-sacs to hillside homes on graded benches above Carbon and Soquel canyons. Elevation shifts constantly within the city limits, so one parcel often sits above a neighbour's roof or below the street, and storms breaking over the higher ridges push water down canyon roads and across lower pads. Automatic irrigation, pool equipment, and very long private utility runs cross all of it.",
    },
    'Newport Beach': {
        "intro": 'Salt air, harbour tides, and a large stock of small older cottages make Newport Beach unforgiving when a pipe fails. Local crews respond the same day you call.',
        "context": "Newport Beach stretches across a harbour, a sand spit, and a set of bluffs above the Pacific, and open water sits close to nearly every part of it. Balboa Island and the peninsula keep some of the county's earliest small homes, tightly packed cottages on narrow parcels whose crawl areas sit barely above the tide line, while Corona del Mar and the bay-front streets mix mid-century houses with rebuilds on the same shallow substrate. Salt-laden air eats through exposed copper, brass, and the fittings on heaters and pool gear faster than inland conditions do, and tidal movement keeps groundwater shifting beneath island blocks. Because so many properties sit at or near sea level, a leak below a floor often announces itself as damp framing and lifting tile.",
    },
    'Tustin': {
        "intro": "From Old Town's century-old service runs to the newest townhomes, Tustin's plumbing spans several eras. Fast extraction is what keeps a single failure contained.",
        "context": 'Tustin grew up as a citrus town on the Santa Ana plain, laid out in the 1880s along a road lined with eucalyptus windbreaks planted to shelter the orchards. Old Town still holds brick storefronts and Victorian-era homes, but most of the city arrived far later: 1950s and 1960s tracts first, then the huge planned villages that filled the decommissioned Marine air station after its twin wooden hangars went quiet, and finally apartment and townhome blocks near the freeway. The terrain is almost perfectly flat and drains through channels toward the Santa Ana River. Three distinct generations of plumbing, built to three different sets of standards, can therefore sit on a single block, and additions have repeatedly buried older routes.',
    },
    'Orange': {
        "intro": 'Orange pairs a Victorian-era core with mid-century tracts, and the pipework beneath both is old. A nearby crew can begin extraction immediately.',
        "context": 'Orange calls itself the Plaza City for the traffic circle at its centre, a square laid out in the 1880s and still ringed by brick buildings that once held hardware merchants and citrus packing houses. Around it stand some of the oldest residential blocks in Orange County, Victorian and Craftsman homes under mature trees, while the remainder of the city filled in with post-war tracts, the streets around Chapman University, and industrial parks near the river channel. The Santa Ana River and Santiago Creek bracket the city and the plain between them drains slowly. Houses here have been re-plumbed, re-roofed, and re-landscaped repeatedly, and additions poured over former patios frequently bury the original drain route where a slow leak can run for weeks.',
    },
    'Santa Susana': {
        "intro": 'Large rural parcels and very long private runs mean a leak in Santa Susana can go unnoticed for a long time. Local crews can start extraction the same day.',
        "context": 'Santa Susana is a small unincorporated settlement in Ventura County pressed against the Santa Susana Pass, where two ranges pinch together and the old stage road and railroad climbed through the gap toward the valley. It grew as a rural stop with a store, a schoolhouse, and scattered ranch homes, and much of the surrounding acreage later went to film ranches and to the rocket-testing laboratory on the heights above. Housing is sparse, varied, and frequently old, on generous parcels served by private wells, septic fields, and long supply runs crossing unincorporated ground. Slopes are steep, rocky, and brush-covered, so a storm following a burn scar sends debris-laden flow down the same draws that drain the community.',
    },
    # --- pending batch 2026-10-12 (weekly expansion that tripped the doorway gate) ---
    "Chino": {
        "intro": "Chino was dairy country for most of a century, and the ground those farms left behind is flat, fine-grained, and slow to shed water. A failed line or a heavy storm can put water inside a house fast, so local crews start extracting the same day you call.",
        "context": "Chino occupies the western end of the Chino Valley in San Bernardino County, a broad, nearly level basin that spent most of the twentieth century as one of the largest dairy districts in the country before the herds moved east and the land was converted into warehouses, business parks, and large subdivisions. Chino Creek and its tributaries run across the valley toward the Prado flood-control basin at the city's southern edge, and the soil between them is fine-grained and compacted, so once land is graded and paved it sheds water quickly instead of soaking it in. The older blocks near the historic downtown still hold small farm-era houses from the early 1900s, but most of the housing here went up after the 1970s on graded pads, with long service runs buried under driveways and landscaping where a slow break can stay invisible for weeks.",
    },
    "Cypress": {
        "intro": "Cypress filled in over a short stretch of post-war years, so the pipework in one house is usually the same age as the pipework next door — and it tends to let go on the same schedule. A nearby crew can begin extraction the same day.",
        "context": "Cypress lies in northwestern Orange County on level ground between the San Gabriel River channel and Coyote Creek, a stretch of former dairy and bean fields that was still largely agricultural into the 1950s. The city then built out quickly in one continuous wave: compact single-story tracts, small apartment courts, and the commercial frontage along Lincoln Avenue and Valley View Street, with the college campus and the Los Alamitos base holding the largest open parcels. Practically every neighborhood was graded and drained at the same time, and the terrain is flat enough that escaped water and stormwater share the same street system, which is why a break beneath a slab or a blocked lateral often announces itself first as soft pavement, a waterlogged planter bed, or a meter that keeps turning when nothing is running.",
    },
    "Fountain Valley": {
        "intro": "Fountain Valley was planned down to the street wall, which means uniform lots, uniform slabs, and plumbing that reaches retirement age block by block. When a line fails, fast extraction is what keeps the loss inside one room.",
        "context": "Fountain Valley is a purpose-built community in coastal Orange County, incorporated in the 1950s on farmland between the Santa Ana River to the west and the upper end of the Talbert Valley channel system, and it was among the first California cities to require the block walls and greenbelts that still shape its neighborhoods. Mile Square Regional Park fills the middle of town, and the housing around it is overwhelmingly low, level, and built within a narrow window of years, so original supply lines and drain laterals across whole blocks are aging at the same rate. The water table sits shallow here and the terrain is almost perfectly flat, leaving escaping water very little fall to work with; it tends to pool beneath foundations, driveways, and patio slabs rather than running off.",
    },
    "Garden Grove": {
        "intro": "With a shallow water table beneath dense mid-century blocks, Garden Grove homes can take on water from below as easily as from a burst pipe. Local crews respond the same day you call.",
        "context": "Garden Grove started as a late-nineteenth-century farming colony planted with fruit and nut groves along the road that still carries its name, and it stayed agricultural until the war years, when tight grids of small houses and garden apartments replaced the orchards almost block by block. It is now one of the most densely populated cities in Orange County, with the Little Saigon commercial core running along Bolsa Avenue and older residential streets packed in behind it on narrow lots with rear alleys. The city sits on low, flat ground where the water table stays close and drainage moves through concrete channels toward the Santa Ana River, so a winter downpour and a failed service line both push water into carports, garages, and low-floor rooms instead of away from them.",
    },
    "Monrovia": {
        "intro": "Monrovia's upper streets take runoff straight off the San Gabriel range, while its historic downtown blocks hide very old lines behind plaster. Either way, a quick local response is what limits the loss.",
        "context": "Monrovia is a foothill town in the San Gabriel Valley, laid out in the 1880s along Myrtle Avenue and Huntington Drive where citrus and avocado ranches met the first electric railway heading toward Pasadena. It kept a compact historic commercial center of Craftsman houses and later bungalow courts, while its northern streets climb abruptly into steep canyons of the San Gabriel Mountains, where winter storms deliver runoff, debris, and post-fire silt at high speed. Homes at those elevations often still carry original drain lines under floors that were repoured and extended over the decades, and their long private service runs cross grades steep enough that a break can travel a long way downhill before anyone notices it from the street.",
    },
    "Newport Coast": {
        "intro": "Newport Coast was carved into ocean-facing slopes in the 1990s, so its large homes, pool equipment, and irrigation lines all sit on graded ground above the Pacific. A buried failure can travel a long way before it surfaces.",
        "context": "Newport Coast is a master-planned hillside community on the ridgeline above Crystal Cove in Newport Beach, built out from the early 1990s onward on slopes that fall steeply toward the coast highway and the ocean. Nearly all of its housing is recent, large, and heavily landscaped, with pool systems, drip irrigation, and long private utility runs crossing graded benches and terraced lots, and marine air keeps exposed metal and the ground damp through much of the year. Because the terrain sheds toward lower pads and structures, a small break in an irrigation or supply run can move along a slope and appear far from its source — often as a damp patch, a settled walkway, or a crack in a retaining wall rather than an obvious indoor puddle.",
    },
    "Paramount": {
        "intro": "Paramount was built tight and flat, so water from a failed line has nowhere to go but sideways under floors and into neighboring yards. A local crew can start extraction right away.",
        "context": "Paramount began as Clearwater, a dairy town named for the artesian wells that once fed its pastures, and it took its present name in the 1930s as the farms gave way to dense working-class tracts on very small lots. It is now among the most tightly packed cities in the Gateway Cities corridor, with post-war houses, apartment courts, and light industrial yards pressed together between Compton, Bellflower, and the Los Angeles River channel that forms part of its eastern edge. Artesian groundwater is still a local reality, and the terrain is perfectly level and almost entirely paved, so a break in an old service line or a blocked lateral has no natural path away from the structure: it simply creeps sideways beneath slabs, driveways, and lot-line fences.",
    },
    "Porter Ranch": {
        "intro": "Porter Ranch was graded and built in phases across the north valley floor and its slopes, so hillside lots, irrigation, and newer pipework all meet hard, dry ground. When something lets go, water moves quickly and quietly.",
        "context": "Porter Ranch occupies the northwestern corner of the San Fernando Valley against the Santa Susana Mountains, a planned community that grew in phases from the 1970s onward on former ranch and orchard land regraded into benches and terraced streets. The neighborhoods mix gated hillside developments of large newer houses with older ranch-style blocks closer to the valley floor, and nearly all of them were landscaped for a dry climate, with extensive irrigation, pool equipment, and long private runs crossing graded pads. Soil on the slopes is largely clay and compacted fill that holds moisture against foundations instead of draining it, and because so many homes sit above or below a neighbor's lot, a concealed break can soak a retaining wall, a lower pad, or a slope-facing room long before anything shows from the street.",
    },
    "Simi Valley": {
        "intro": "Simi Valley sits in a basin between two mountain ranges, with a concrete arroyo carrying stormwater through the middle of it and most of its housing built during the boom decades. When a line fails, quick extraction protects the structure.",
        "context": "Simi Valley fills the broad basin of the same name in Ventura County, a former apricot and citrus valley walled off by the Santa Susana Mountains to the north and the Simi Hills to the south, with the Arroyo Simi running the length of the city to carry runoff out toward the Santa Clara River. Development arrived in waves from the 1960s through the 1980s, replacing groves with tracts and condominiums and later with master-planned villages along the western and southern edges. The 1994 earthquake damaged a large share of the local housing stock and left many homes with repaired or partly replaced supply lines, and the valley's position between two ranges means winter storms concentrate runoff in the arroyo and in the streets that feed it.",
    },
    "Cerritos": {
        "intro": "In Cerritos, most homes sit on slab foundations built during the tract era, so a hidden leak under the floor can spread through the whole house before it shows. Local crews start extraction the same day you call.",
        "context": "Cerritos occupies a stretch of the Los Angeles coastal plain between the San Gabriel River channel and the 605 corridor, land that was open dairy pasture under the name Dairy Valley well into the 1960s. When the dairies gave way, the city rebuilt itself almost entirely at once: planned tracts of one- and two-story homes, townhome villages, and the commercial spine along South Street and the Artesia Freeway. Because nearly every house went up on a concrete slab in the same two decades, slab-on-grade plumbing is the norm here rather than the exception, and the ground beneath is flat, heavily paved, and slow to drain. A break in a supply line or a backed-up lateral has nowhere to go but sideways under the floor, which is why the first sign is often a warm spot, a warped plank, or a water bill that jumps for no clear reason.",
    },
    "Lakewood": {
        "intro": "Lakewood's 1950s tract houses were built fast and built alike, which means one failed supply line can look exactly like the neighbors' problem. Fast, local response contains it before it spreads between rooms.",
        "context": "Lakewood is the prototype of the post-war American suburb, laid out in the early 1950s on former Bixby sugar-beet and dairy land as one of the largest planned tracts ever built at the time, and it pioneered the contract-city arrangement that still supplies many of its services from the county. The result is a very even city: block after block of single-story ranch houses on compact lots, most of them built within a few years of each other with original galvanized supply lines and cast-iron drains. Streets are wide and flat, drainage runs to the same storm system everywhere, and there is little open ground to absorb a surge. Houses here also tend to have been added onto over the decades, with patios, family-room extensions, and converted garages that bury older plumbing beneath new slabs, so a leak frequently surfaces somewhere the owner never expected.",
    },
    "Duarte": {
        "intro": "Duarte sits right against the San Gabriel Mountains, so water arrives two ways here: storm runoff off the slopes above and failures in very old plumbing below. Local crews handle both.",
        "context": "Duarte is a narrow foothill city along historic Route 66, spread across the mouths of Fish Canyon and the Duarte Wash where the San Gabriel Mountains drop sharply to the valley floor. The town grew out of a ranch settlement and stayed small, with older bungalows and citrus-era houses lining Foothill Boulevard and steeper streets climbing the terraces above it, now mixed with medical campus buildings and mid-century tracts. That position against the range brings two distinct water problems: debris-laden runoff and sheet flow off burned or steep slopes during winter storms, and the plumbing inside houses that are now eighty to a hundred years old, with original drain lines under floors and service connections installed long before modern pressure standards. Hillside lots add retaining walls, terraces, and long private runs that can fail out of sight.",
    },
    "Northridge": {
        "intro": "Northridge homes sit on ground that has been shaken, repaired, and rebuilt — and on plumbing that often dates to the original tract. When a line goes, water spreads under the slab fast.",
        "context": "Northridge occupies the northern San Fernando Valley, a former citrus-growing district that was renamed for its position north of the valley floor and then filled in with ranch-style tracts during the suburban boom of the 1950s and 1960s. The neighborhood is famous for the 1994 earthquake, whose ground movement ruptured water mains and snapped service lines across the area, and a good deal of the housing stock still carries patched or partially replaced plumbing from that period. The ground here is largely hardpan and compacted alluvium that sheds water rather than absorbing it, and the summer heat is hard on exterior pipe runs and irrigation. Add the hillside streets along the northern edge, where runoff crosses lower lots, and it is easy for water to end up somewhere it was never meant to reach.",
    },
    "Irwindale": {
        "intro": "Between quarry pits, industrial yards, and a small residential core, Irwindale is an unusual place for a water emergency — but when a line lets go, a fast local response is what protects the property.",
        "context": "Irwindale is one of the smallest and least conventional cities in the San Gabriel Valley, a mostly industrial municipality at the foot of the San Gabriel Mountains built around the gravel and rock quarries that have been worked here for generations. Residential blocks are few and older, clustered near the remaining neighborhoods and along the valley-side streets, while much of the land is taken up by below-grade mine pits, processing yards, and warehouse space along the 210 corridor. Because so much of the ground has been excavated, graded, or filled, surface drainage follows manufactured contours rather than natural ones, and heavy canyon rain drains off the mountain front through the Santa Fe Dam basin and the San Gabriel River channel just to the west. Buildings here mix very old plumbing with industrial water and irrigation systems, so failures are rarely simple.",
    },
    "Midway City": {
        "intro": "Midway City sits on low ground between two larger cities, where the water table is close and drainage has few places to go. When a line fails or a storm backs up the street, quick extraction matters.",
        "context": "Midway City is an unincorporated community in coastal Orange County, sitting exactly where its name suggests — on the flat ground between Westminster and Huntington Beach, along the Bolsa Avenue corridor that forms the heart of the area's Vietnamese commercial district. The land was drained farmland and bean fields before it was built out, and it remains low, level, and almost fully paved, hemmed in by the East Garden Grove-Wintersburg Channel and the tidal wetlands of Bolsa Chica to the south. The water table sits high enough that storm drains and sewer laterals have little fall to work with, so heavy winter rain can push water back into garages, carports, and low-floor additions. Much of the housing dates from the post-war decades and has been added onto repeatedly, leaving plumbing that is hard to trace.",
    },
    "Santa Ana Heights": {
        "intro": "Set on a mesa just above the bay and next to an active airport, Santa Ana Heights homes face damp air, high groundwater nearby, and plumbing from the mid-century. Local crews respond the same day.",
        "context": "Santa Ana Heights is an unincorporated pocket of coastal Orange County perched on the mesa above the Upper Newport Bay, wedged between Newport Beach, Costa Mesa, and John Wayne Airport. The neighborhood developed from the 1950s through the 1970s as larger lots with ranch and mid-century houses, several of them on streets that dead-end into the bluffs overlooking the bay's wetlands and the San Diego Creek channel. Marine air and fog keep the ground and structures damp through much of the year, and the bay-side terrain means the water table is never far below the surface on the lower edges of the community. Because properties here were often built with long private drain runs, pool plumbing, and extensive landscape irrigation, a leak can travel a long way under driveways and planting before it finally shows up indoors.",
    },
    "Fullerton": {
        "intro": "Fullerton has railroad-era blocks, orange-grove tracts, and oil-boom houses all in one city — and a hundred years of plumbing underneath them. When water gets loose, speed is what limits the damage.",
        "context": "Fullerton is one of Orange County's oldest cities, founded in the 1880s as a Santa Fe railroad stop and named for the men who laid out the townsite. Its economy then ran on Valencia oranges and, from the 1890s onward, on oil from the field that spread across the northern part of the city, and both left a mark on the layout: a dense walkable downtown of brick storefronts and Craftsman bungalows, grove-era houses on the surrounding grid, and later tracts filling the ground toward the hills. Coyote Creek and the Fullerton Creek channel carry drainage through the city, and the water table responds quickly to winter storms. With housing from so many eras sitting side by side, it is common to find modern supply lines feeding original cast-iron drains, or a decades-old service lateral running under a driveway that was poured long after the house was built.",
    },
    "Oxnard": {
        "intro": "On the Oxnard Plain, irrigation keeps the ground wet and the air off the ocean keeps it corrosive — a hard combination for plumbing in older neighborhoods. When something fails, local crews respond fast.",
        "context": "Oxnard sits on the broad agricultural plain of Ventura County, a city that began as a company town around the sugar beet factory built at the turn of the twentieth century and has stayed tied to farming ever since, with strawberry and vegetable fields pressing right up against its edges. The older neighborhoods near the historic downtown and south of the highway hold small houses from the 1900s through the 1950s, while later tracts spread east and north toward the naval base and the harbor. Because the plain is intensively irrigated, groundwater stays close to the surface across much of the city, and marine air off the Channel Islands accelerates corrosion on exposed and buried metal. That pairing means a pinhole leak in an old service line can stay undiscovered until paving lifts or a foundation footing stays wet for weeks.",
    },
    "Palmdale": {
        "intro": "In Palmdale, water damage does not arrive gradually — a burst line behind a wall or a wash running through the neighborhood after a storm can put water inside a house within the hour. Local crews can start extracting the same day you call.",
        "context": "Palmdale spreads across the floor of the Antelope Valley, a Mojave basin framed by the Sierra Pelona and the mountains to the south, with the San Andreas fault running along their base. The city grew twice: first as a rural stop on the railroad, then again from the 1950s onward, when flight testing at the aerospace plant north of downtown and later the Antelope Valley Freeway turned it into a commuter city for the Los Angeles basin. The housing that followed was designed around triple-digit heat, single-digit humidity, and long stretches without rain, so water is the least expected problem a Palmdale house can have. Thin desert soils and caliche layers shed whatever falls instead of soaking it in, and one cloudburst can push sheet flow down streets and through yards. Evaporative cooler feeds, landscape drip lines, pool equipment, and service laterals that sit idle through the dry season are the components most likely to fail once the weather finally changes.",

    },
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
    # --- batch 2026-10-26 (weekly expansion: bespoke CONTEXT for the 6 picked cities) ---
    "La Mirada": {
        "intro": "La Mirada was laid out as one planned community in a single building push, so the same slab foundations and the same supply runs repeat from block to block. When one lets go, a nearby crew can be extracting the same day.",
        "context": "La Mirada takes its name from the old McNally family estate, whose Spanish name referred to the open view across the plain toward the Coast Range, and the city only incorporated in 1960 after the ranch land at the southeast corner of Los Angeles County was carved into a fully planned subdivision. Because a single development company put up whole tracts within a few years, ranch and two-story models repeat along curving interior streets on nearly level parcels, with patios, carports, and rear additions poured later over runs that were never meant to be reached again. The ground here borders the Coyote Creek and San Gabriel River drainage on the county line, and it is flat, heavily paved, and slow to shed a spill, so a failed fitting below a floor tends to creep sideways into the next room rather than reaching the yard.",
    },
    "South Pasadena": {
        "intro": "Plenty of South Pasadena houses were standing before the First World War, and the pipework inside them has been patched ever since. A quick local response is what keeps an old line failure from ruining historic floors.",
        "context": "South Pasadena incorporated in 1888 and grew up along the Arroyo Seco as a streetcar suburb of its larger neighbour, with narrow tree-shaded blocks of Craftsman bungalows, Spanish Revival courts, and shingled houses that are now well over a century old. Raymond Hill and the streets climbing off Mission Street sit at noticeably different elevations within a few hundred yards of one another, so drainage follows the slope past whatever happens to lie below. Inside those homes, original galvanised supplies have been spliced so many times that tracing a single run is guesswork, and the clay beneath the older lots keeps a slow leak pressed against a footing long after the plaster above it has begun to stain.",
    },
    "North Hills": {
        "intro": "North Hills filled in during a handful of post-war years, and the ground under it has been shaken and repaired since. A failed line beneath a slab here can run a long way before anyone notices.",
        "context": "North Hills occupies the north-central floor of the San Fernando Valley, land that was still walnut and citrus orchard when the first tracts went up in the 1950s under the older name Sepulveda. Nearly every block was finished within the same decade on concrete slabs, which means the copper and galvanised lines inside those houses are letting go on roughly the same schedule today, and the 1994 earthquake centred nearby split service connections across the neighbourhood and left a large number of patched joints behind. The soil is hardpan and compacted alluvium that refuses to absorb a spill, so water from a break travels under flooring, along the trench of an old utility run, and into the garage next door rather than soaking away where it started.",
    },
    "Claremont": {
        "intro": "Claremont's grove-era houses and its college streets both carry plumbing older than most of the people living in them. When a line fails, fast extraction is what protects the original woodwork.",
        "context": "Claremont began as a Santa Fe railroad settlement in 1887 and grew around the cluster of colleges that gave the town its character, a grid of wide, canopied streets where pepper trees and olive groves once separated the campus quadrangles from the surrounding citrus ranches. The village core and the blocks near the colleges still hold bungalows, Tudor cottages, and Spanish Colonial houses from the 1900s through the 1930s, many with cellars or raised foundations that let water collect unseen beneath living space. North of Foothill Boulevard the ground begins to tilt up toward the San Gabriel range, so storm water arriving from the washes above crosses the lower streets, and the decomposed granite of the foothill lots drains quickly enough that a buried break can empty itself into the subsoil for weeks.",
    },
    "Westminster": {
        "intro": "Westminster was farmland far longer than it has been a city, and much of it sits low enough that escaped water has nowhere to run. Local crews start extracting the same day you call.",
        "context": "Westminster was founded in 1870 as a Presbyterian temperance colony and stayed a barley and bean farming town for generations, with a small grid of storefronts on the main road and fields stretching out to the county line. After the war those fields were divided into dense tracts and garden apartments, and the arrival of families from Vietnam in the 1970s turned Bolsa Avenue into the commercial heart of Little Saigon, filling the blocks behind it with shops, restaurants, and crowded rental units. The city rests on a low coastal plain where the water table stays near the surface and runoff moves through open concrete channels, and because so many parcels have been rebuilt or extended, the pipework inside them mixes decades and standards in ways that are hard to read from the street.",
    },
    "Placentia": {
        "intro": "Placentia grew up around citrus packing houses, and the older homes near the tracks still sit on plumbing from that era. A quick response keeps a small break from taking the flooring with it.",
        "context": "Placentia took its Latin name, a pleasant place, from the Santa Fe station that anchored the townsite in the 1870s, and for decades the surrounding plain was one of the densest orange-growing districts in the county, with packing houses and spur lines running through the middle of town. The historic core keeps small houses and commercial buildings from the early 1900s, while later subdivisions spread north toward the bluffs and east along the boulevards, mixing mid-century tracts with newer infill. Parts of the city sit on the flats below the Santa Ana River levees and the Prado reservoir releases, and the older streets were laid out before modern storm drains existed, so heavy rain and an underground failure compete for the same crowded space beneath the pavement.",
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
