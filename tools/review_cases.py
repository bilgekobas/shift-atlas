"""Build reviewed case data, a complete audit trail, and the evidence pilot.

Inputs: the archived pre-review corpus. Output JS is generated from reviewed JSON.
No numerical performance claim is accepted solely from a bibliography entry.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'data/audit/original-cases-2026-10-20.json'
PILOT = {4, 5, 6, 7, 12, 34, 37, 38, 40, 42, 53, 57}
DATE = '2026-10-20'

# Replacement effects remove unsupported quantities, causal attribution and absolutes.
# These are explicitly labelled editorial physical interpretations unless documented below.
EFFECTS = {
1: 'Solar access may reduce heating demand, depending on orientation, glazing, shading and occupancy.|Animal heat can contribute to the building heat balance; separation, ventilation, hygiene and fire safety remain necessary.|Eaves can intercept high-angle sun; effectiveness depends on orientation and geometry.|Roof form affects snow accumulation and loading; safe performance requires local structural assessment.',
2: 'Infill and timber jointly affect heat and moisture transfer; insulation and airtightness depend on the actual wall assembly.|Opening area and orientation affect solar gain, daylight and heat loss.|Enclosure can shelter streets from wind, while also reducing ventilation and winter solar access.',
3: 'Orientation and surrounding shelter can reduce wind exposure, subject to site conditions.|Thatch can resist heat transfer when its thickness, moisture condition and construction are suitable.|Shared enclosure can retain internal gains; air quality and hygiene constrain livestock integration.',
4: 'Shade, vegetation and water may modify courtyard air and radiant conditions; their separate contributions require measurement.|Courtyard geometry can reduce direct solar exposure; reflected radiation and seasonal sun access also matter.|Masonry can delay heat transfer; benefit depends on night-time heat rejection, internal gains and operation.',
5: 'Masonry can attenuate and delay temperature fluctuations; this is not equivalent to thermal insulation.|Limewashed surfaces can reduce solar absorption where maintained; exposed stone roof portions need separate assessment.|Stored heat must be discharged to a cooler sink if buffering is to persist over successive hot days.|Corbelled stone construction can reduce structural dependence on timber, with local craft and structural constraints.|Roof collection and cisterns can store rainwater where present; yield and water quality require assessment.',
6: 'Ground contact and rock mass can damp temperature variation; depth, ventilation and geology determine the result.|Ground shelter can reduce directly exposed surfaces; openings and courtyards still receive solar radiation.|Cisterns and channels can collect rainfall where documented, subject to water quality and maintenance.|Drainage, ventilation and sanitation are necessary to manage damp and contamination risks.',
7: 'Wind pressure and buoyancy can drive airflow through a tower and connected openings; performance depends on wind direction and flow resistance.|Ground contact and water may provide additional cooling where connected to the air path; the tower alone does not guarantee below-ambient air.|Inward planning and shaded openings can reduce solar exposure; façade configuration varies between buildings.',
8: 'Adobe can store and release heat, with performance dependent on wall assembly, solar access and daily temperature variation.|Stepped volumes can shade some surfaces and occupied areas, depending on solar angle.|Solar gain can contribute to heating where openings, orientation and storage are coordinated; auxiliary heat may still be necessary.',
9: 'Palm canopy provides shade; air-temperature effects depend on irrigation, vegetation and ventilation.|Covered passages reduce direct solar exposure on pedestrian routes; coverage varies within the settlement.|Continuous enclosure can provide wind shelter while requiring deliberate ventilation paths.',
10: 'Raised floors can permit air movement and separate occupied spaces from wet ground; this does not establish moisture or comfort performance by itself.|Overhangs and roof drainage can reduce rain exposure, subject to wind direction and detailing.|Elevation can reduce exposure to some floods; flood level, scour, debris and structural stability remain limits.',
11: 'Shaded verandas can reduce radiant exposure and enable air movement where a pressure difference exists.|Ridge openings can exhaust warm air where inlet area, buoyancy and wind conditions support flow.|Raised floors can separate occupied space from wet ground and some flood conditions; protection is not unlimited.',
12: 'Courtyard-connected openings can support ventilation; direction and rate depend on wind, buoyancy and opening configuration.|Pitched roofs and overhangs can shed rain and protect openings; drainage and wind-driven rain detailing remain necessary.|Screens can shade openings while allowing some air and daylight to pass; geometry controls the trade-off.',
13: 'Large roof overhangs can shed rain and shade walls; aerodynamic or storm-resistance claims require structural evidence.|Bamboo exchanges moisture with surrounding air; room-scale humidity buffering depends on exposed material, coatings and ventilation.|Raised floors may permit under-floor air movement and reduce contact with wet ground.',
14: 'Turf and other roof or wall layers affect heat transfer; moisture, thickness and construction must be specified.|Low form and ground contact can reduce exposure, while drainage and ground moisture remain critical.|An enclosed entrance passage can buffer direct air exchange if doors and use support that function.',
15: 'Compact geometry can reduce exposed area for a given volume; no universal advantage over other forms is quantified here.|Covering layers can reduce heat transfer; hide, textile and turf variants must be distinguished.|Some goahti variants are portable; permanent turf-covered structures require separate documentation.|Topography and vegetation may provide wind shelter; snow accumulation can also create loading and moisture risks.',
16: 'Curved enclosure changes wind loading; resistance depends on anchoring, frame and cover construction.|Felt layers resist heat transfer; performance depends on density, moisture, thickness and air leakage.|The crown opening can support ventilation or smoke exhaust depending on configuration; heating and indoor air quality require separate assessment.',
17: 'Cliff position can shade parts of a settlement at particular times; solar access varies by aspect and season.|Rock mass can damp local temperature variation but does not guarantee cooling of occupied rooms.|Enclosed earthen walls can reduce direct wind exposure; joints and openings determine air leakage.|Earthen walls can delay heat transfer; indoor temperatures require case-specific evidence.',
18: 'Earthen walls can store and release heat; the balance depends on material moisture, thickness and boundary conditions.|Projecting timber members can support access for recurring maintenance, as documented for particular buildings.|Roof occupation may exploit cooler night conditions; use and safety require local documentation.',
19: 'Shaded planting and water can modify radiant and air conditions; water use and humidity limit evaporative benefit.|Inward-facing rooms can reduce some street exposure; opening patterns vary.|Courtyard proportions and orientation affect seasonal sun access; enclosure cannot exclude direct sun at all angles.',
20: 'Narrow lanes can reduce direct solar exposure, with seasonal and orientation-dependent effects.|Timber lattices can shade openings and admit air; stone-screen results cannot be assigned to timber screens without qualification.|Party walls reduce exposed envelope area; thermal storage depends on their material and thickness.',
21: 'Masonry can store solar heat and release it later; cold-night performance also depends on insulation and infiltration.|Grass thatch can resist heat transfer when its construction and moisture condition are suitable.|Orientation changes the timing of solar gain; local slope, shading and seasonal occupation must be documented.|Terraces can modify drainage and local exposure; frost protection and cold-air movement need site-specific evidence.',
22: 'Ground coupling and rock mass can damp temperature fluctuations; indoor conditions vary with depth, occupancy and ventilation.|Embedding reduces exposed envelope area, while entrances and excavated façades still receive solar gain.|Protected openings can limit wind exposure; adequate ventilation and moisture control remain necessary.',
23: 'Log joints and sealing affect infiltration; airtightness requires measurement of the actual building.|Vegetated roofs can retain and delay rainfall runoff; performance depends on substrate, antecedent moisture and rainfall.|Outbuildings may shelter occupied areas where layout and wind direction support it.|Orientation and enclosure can improve solar access and wind shelter; the result is site-specific.',
24: 'Earthen shell mass can buffer temperature variation; structural efficiency and thermal performance require separate evaluation.|External ribs support maintenance access and alter runoff paths; erosion and repair remain important.|A high opening can enable warm-air exhaust where replacement air and driving pressure are available.',
25: 'Thick earth walls can damp heat transfer; measured performance of one tulou is not a universal value for the type.|Courtyard-facing openings allow air exchange, but continuous cross-ventilation is not guaranteed.|Roof and courtyard drainage can manage rain where maintained and adequately sized.|Overhangs and galleries can shade inward façades, depending on orientation and solar angle.',
26: 'Courtyard openings can support ventilation under suitable wind and buoyancy conditions.|Pitched roofs and overhangs can shed rain and protect openings, subject to detailing.|Screens can reduce direct sun while permitting some air and daylight to pass.|Water and planting can modify local conditions; evaporative cooling potential decreases with humidity.',
27: 'Layered thatch and an air space can reduce heat transfer and provide shade; construction details require documentation.|Inward-draining roof geometry can collect rainfall; storage capacity, overflow and water quality are constraints.|Earth can store heat and exchange moisture; benefit depends on assembly and ventilation.|Multiple openings can enable cross-flow where pressure differences exist.',
28: 'Floor elevation can reduce exposure to some floods; design flood level and structural hazards must be established.|Building spacing and openings influence wind-driven ventilation; no universal opening ratio is prescribed here.|Roof form and overhangs can shed rain and shade occupied spaces, subject to wind-driven rain exposure.|Elevating the floor separates it from wet ground; direct thermal coupling to the ground is consequently limited.',
29: 'Air wells provide an exchange path; airflow depends on geometry, temperature differences and wind pressure.|Covered arcades can shade circulation and shelter entrances from rain.|Operable louvres permit adjustment of view, shade and airflow, with coupled trade-offs.',
30: 'Courtyards can provide sheltered daylight and ventilation paths; room performance requires case-specific assessment.|Openable screens and openings can support airflow, depending on the actual enclosure and use.|Layered shading can reduce direct solar exposure; coverage changes with sun angle and maintenance.',
31: 'Distributed courtyards can provide multiple air paths; actual airflow depends on openings and pressure differences.|Overhangs, verandas and vegetation can reduce direct solar exposure, with seasonal variation.|A pool may modify local humidity and radiation; cooling magnitude requires measurement and depends on air conditions.',
32: 'Private forecourts provide semi-outdoor space and potential ventilation paths; dimensions and use should be verified from drawings.|Orientation and open façades affect wind exposure; local wind and surrounding buildings determine performance.|Projecting courts and galleries can shade lower surfaces, depending on sun angle.',
33: 'Distributed voids can provide air paths; porosity alone does not establish ventilation rate or comfort.|Orientation affects exposure to prevailing winds; local obstructions and opening configuration remain important.|Opening geometry mediates solar gain, privacy and airflow; each requires separate evaluation.',
34: 'The mantle can shade the body and reduce direct wind exposure, depending on posture and use.|Wool layers can resist heat transfer; wetting, compression and openings change performance.|Carrying shelter permits protection to move with the worker; mobility and effort are part of its use.|Felt can resist intermittent wetting; water resistance and drying require material and use documentation.',
35: 'The curved cover can shed rain away from covered body areas; protection depends on fit, posture and wind.|A back-mounted cover leaves the hands available for work; ergonomic performance requires user observation.|The cover can reduce direct solar exposure on covered body areas.|Local fibres can support repairable construction; durability, harvesting and labour must be documented.',
36: 'Fabric and adjustable sides can provide shade and permit air movement.|Moisture can alter fibre and weave behaviour; waterproofing depends on the actual fabric, tension and condition.|Modular fabric and poles allow relocation; transport, assembly and livelihood requirements shape use.|Adjustable sides can mediate wind and dust exposure, with ventilation trade-offs.',
37: 'Lattice depth and aperture geometry can reduce direct solar penetration.|Apertures modify daylight distribution and contrast; glare reduction requires a specified viewing condition.|A permeable opening allows some airflow but adds resistance; net ventilation depends on the full air path.|Filtered visibility can support privacy, depending on light levels, viewing angle and local use.',
38: 'Deep apertures can intercept direct sun depending on orientation and solar angle.|The pattern modifies daylight distribution; glare performance depends on the room and view.|Air can pass through apertures where a driving pressure exists; perforation does not itself create ventilation.|Patterned openings can mediate views; privacy varies with geometry and lighting.',
39: 'Paper can transmit and scatter daylight; transmittance depends on paper, ageing and construction.|Translucent infill can obscure direct views while admitting light.|Sliding panels permit spatial and seasonal adjustment; ventilation depends on whether an air path is actually opened.',
40: 'Shell infill can transmit and scatter daylight; visible and infrared properties require measured spectra for the actual shell assembly.|Operable timber panels can adjust exposure and air exchange, subject to rain and wind.|Translucent shell infill can obscure views while admitting daylight; effectiveness depends on lighting and material.',
41: 'A roofed threshold can shade adjacent rooms and occupation zones, depending on depth and solar angle.|The intermediate zone can shelter openings from some rain; wind-driven rain remains a limit.|Sliding boundaries can adjust enclosure and occupation, depending on the documented house and season.',
42: 'A shaded platform can reduce direct solar and radiant exposure; air temperature, surface temperature and mean radiant temperature are distinct outcomes.|A semi-public threshold can support relocation of activities to a sheltered edge, subject to access and social practice.|The covered entry can shelter occupants and openings from some rainfall.|Shared shade can support public resting and interaction where access and use permit.',
43: 'Covered routes reduce direct solar exposure; their effect on thermal comfort and pedestrian behaviour needs local evidence.|Roofed circulation can maintain shelter during rainfall, subject to drainage and wind exposure.|Continuity can support sheltered movement through the city; accessibility and network gaps matter.',
44: 'South-facing openings can admit winter solar gains, subject to obstruction, geometry and use.|A gallery can shade summer sun while admitting lower-angle winter sun where orientation and geometry support it.|Masonry can store solar heat and release it later; insulation and infiltration determine night-time heat loss.',
45: 'Excavation can provide self-shading and ground coupling; temperatures measured in Mediterranean caves are not measurements of this Henan case.|Surrounding ground can damp external temperature variation; depth, moisture and ventilation matter.|A below-grade courtyard can reduce direct wind exposure while requiring drainage and ventilation.',
46: 'Walls and galleries can reduce direct radiant exposure, depending on courtyard proportions and orientation.|Masonry can delay heat transfer; effectiveness requires suitable heat-rejection conditions.|Courtyard-connected openings may support air exchange where wind or buoyancy supplies a driving pressure.|Relocating activities can change exposure; actual use requires observation or a traceable account.',
47: 'South-oriented rooms can receive winter solar gains where courtyard geometry and obstructions allow.|Courtyard proportions and roof edges can shade surfaces during part of the day.|Enclosure can reduce direct wind exposure, with possible ventilation and daylight trade-offs.|Rooms with different exposures permit seasonal use patterns where documented.',
48: 'Enclosure can reduce wind exposure locally; the effect depends on height, porosity and surrounding terrain.|Earth walls can store heat; winter benefit also requires solar access, insulation and control of air leakage.',
49: 'A vine canopy can intercept solar radiation when leaf cover is sufficient.|Plant transpiration can modify local air conditions where irrigation and atmospheric demand permit.|Deciduous vegetation can change shading seasonally; timing depends on species, health and climate.|Enclosure can provide some shelter from street exposure while requiring ventilation and dust management.',
50: 'Walls, arcades and plants can intercept direct sun; shade varies by hour and season.|Water and vegetation may produce local evaporative effects; magnitude depends on water supply, humidity and air movement.|An inward courtyard can provide sheltered outdoor space; enclosure may also retain heat.|Watering, shade operation and maintenance shape environmental performance and resource use.',
51: 'Walls and galleries can intercept sun and mediate glare, depending on geometry.|Planting and water may modify local conditions; Casablanca cannot be assumed to have the same evaporative potential as an inland arid site.|Inward openings can mediate privacy and exposure; actual use and access vary.|Night-time air exchange can remove heat only when outdoor conditions and airflow are favourable.',
52: 'Massive walls can delay heat transfer; material properties, thickness and night cooling need documentation.|The courtyard can organise domestic and agricultural activity in sheltered space; actual seasonal use needs local evidence.',
53: 'A temporary dry organic layer can add thermal resistance; thickness, moisture, fire and pest risks require assessment.|Seasonal removal may permit reuse; actual material handling and reuse routes require documentation.',
54: 'Stone mass can delay heat transfer; sustained cooling depends on heat rejection and internal gains.|Compact enclosure and controlled openings can reduce direct wind exposure; ventilation remains necessary.|A maintained light roof finish can reduce solar absorption.|Roof drainage can collect rainwater where connected to suitable storage; reliability depends on rainfall, demand and water quality.',
55: 'Limewash can reduce solar absorption; reflectance, ageing and pedestrian radiation trade-offs need assessment.|Mass and ground contact can delay temperature changes; indoor outcomes depend on construction and operation.|Narrow passages can shade occupants during part of the day; orientation and season determine coverage.|Compact construction can reduce exposed area; resource demand and indoor conditions require separate evidence.',
56: 'A water film can support evaporative heat exchange where air is unsaturated and water-air contact is sufficient.|Shading can reduce solar heating of water, surfaces and occupants.|Surrounding masonry can store heat; mass does not itself remove heat from the system.|Evaporation potential decreases as air approaches saturation; water, hygiene and maintenance constrain use.',
57: 'Shading and vegetation form part of the contemporary public-space adaptation project.|The project combines water cycles and cooling technologies; it is not a purely gravity-fed historic water channel.|Photovoltaics and hybrid systems are part of the documented design; auxiliary energy and operation must be included.|The public-space demonstrator includes participation and governance; comfort and use require evaluation.',
58: 'A tower can use wind pressure and buoyancy to move air through connected spaces.|Water contact may add evaporative cooling under suitable air conditions; verify the actual air path.|Masonry can delay heat transfer and interact with ventilation, subject to night cooling and use.|Selective operation may mediate hot wind and dust; filtration and maintenance require documentation.'}

NARRATIVES = {
1:'The Schwarzwaldhaus brings domestic rooms, agricultural storage and livestock spaces under a large roof. The atlas interprets this integration through shared enclosure, internal gains and seasonal operation. Construction, orientation and social arrangements vary; historical intent and building performance require evidence for a particular farm.',
2:'Half-timbered buildings combine a load-bearing timber frame with infill and finishes. Their environmental behaviour depends on the full assembly and later alterations. Street enclosure, craft and social history are relevant context; exposed framing alone does not establish thermal performance or social status.',
3:'The Niederdeutsches Hallenhaus integrates domestic and agricultural functions within a large hall-house arrangement. Shared enclosure and internal gains are plausible environmental mechanisms, alongside the requirements of work and storage. Regional construction history, ventilation and hygiene need specific documentation.',
7:'Badgir are windcatcher systems associated with buildings in Yazd and other regions. Towers operate as part of a connected airflow system, sometimes coupled to water or underground spaces. This regional type includes different geometries and operating modes. Climatic interpretation should be separated from claims about civic organisation, status and historical design intent.',
8:'Pueblo settlements combine earthen construction, compact aggregation and culturally specific forms of occupation. This entry is a regional overview represented near Taos, rather than a measured model of one dwelling. Thermal interpretations require wall, opening and operating information. Social and ceremonial meanings should be documented through locally grounded sources.',
9:'Ghadamès is an oasis settlement with connected buildings, covered passages and roof spaces. These arrangements can provide shade and sheltered circulation. Historical accounts of gendered use, commerce and domestic space require attention to period and variation; they are not universal operating rules for the present settlement.',
10:'Rumah panggung denotes raised-house forms across parts of Indonesia. This entry represents a broad type, not a single longhouse or cultural group. Elevation, roof shelter and permeable construction may address wet ground, rain and heat; ownership, community organisation and actual flood protection vary.',
11:'Vernacular housing in the Mekong Delta includes raised floors, verandas and lightweight construction associated with water-oriented livelihoods. Ventilation, rain shelter and adaptability are relevant mechanisms. Relocation, tenure and seasonal occupation require specific local documentation rather than inference from construction alone.',
13:'Tongkonan are culturally specific Toraja houses associated with kinship, ceremony and craft. Raised construction and large roofs can modify rain and solar exposure. Environmental mechanisms, structural behaviour and social meanings should be supported separately; neither climatic optimisation nor storm resistance follows from roof form alone.',
14:'Icelandic turf houses combine timber, stone, turf and other layers in regionally and historically variable assemblies. Limited access to construction materials influenced building practice, but timber was not wholly absent. Thermal and moisture behaviour depend on roof and wall construction, heating, occupancy and maintenance.',
15:'Goahti includes several Sámi dwelling constructions, including portable and turf-covered forms. Their materials, seasonal use and mobility differ. This overview must not assign one covering, insulation value or interior social order to every variant. Community-grounded documentation is needed alongside environmental interpretation.',
17:'Settlements around the Bandiagara escarpment combine earthen construction, topography and culturally specific spatial practices. Shading and wind shelter depend on cliff aspect and settlement position. Historical explanations involving defence, cosmology and burial practices require specific sources and should not be inferred from the map point.',
19:'Riad courtyard houses combine inward-facing rooms with a central open space, sometimes planted or watered. Shade, enclosure and occupation can shape local exposure. Privacy, symbolism and household organisation vary by building, period and community; a single environmental or cultural explanation is insufficient.',
20:'Ahmedabad pols are neighbourhood clusters containing houses, lanes and shared infrastructure. Compactness and screens may modify solar and wind exposure. Social organisation, craft and access are important, but claims about caste, ownership and governance require historical and local sources for the particular pol.',
21:'Andean dwellings include stone and earth walls, grass roofs and varied settlement arrangements. Altitude, slope, solar exposure, cold nights and livelihood shape their use. This entry represents a broad regional type. Claims about orientation, material selection and frost protection require site evidence; solar and thermal interpretations must account for the Southern Hemisphere.',
22:'Cappadocian rock-cut dwellings use excavated volcanic formations in varied historical contexts. Ground contact and rock mass can damp temperature variation, while openings, depth and ventilation produce different indoor conditions. Defensive and religious histories should be documented for specific sites rather than assigned to every dwelling.',
23:'Norwegian farmsteads include log buildings, storage structures and varied roof assemblies. Craft, layout and maintenance influence exposure and heat transfer. This entry does not establish a universal farm orientation, courtyard geometry or airtightness level. Dwelling and storehouse functions need separate documentation.',
24:'Musgum earthen houses use tall curved shells with prominent external ribs. Environmental interpretation concerns earth mass, shade and high-level openings; structural form and rib functions need technical and local documentation. Precise geometric optimality and cooling magnitudes are not established by visual resemblance.',
25:'Fujian tulou are large communal earthen compounds with courtyards and regionally varied plans. Walls, galleries and openings interact with seasonal climate and occupation. Population, kinship and defensive history should refer to specific compounds; measured performance cannot be generalized to the entire type.',
27:'Casamance impluvium houses include inward-draining roofs and central open or collection spaces. Their construction and household organisation vary. This entry interprets roof shelter, water collection and air paths; it does not establish a universal compound-growth pattern or measured cooling effect.',
30:'Geoffrey Bawa’s 33rd Lane house is a contemporary architectural work drawing on courtyards and transitional spaces. The atlas examines its relationship to regional environmental practices. Room enclosure, ventilation and solar performance require drawings, operating information and measurements of this house.',
31:'The Ena de Silva House is a contemporary courtyard house by Geoffrey Bawa that was subsequently relocated. Its courtyards and transitional spaces offer a case for studying reinterpretation of regional practices. The original and relocated sites must be distinguished when interpreting climate, materials and use.',
32:'Bedok Court is a contemporary housing development in Singapore with semi-outdoor private forecourts. It provides a case for studying the translation of courtyard and threshold ideas to collective housing. Density, ownership, dimensions, occupation and environmental effects require project-specific documentation.',
33:'Space Block is a contemporary housing project in Hanoi using voids and openings within a dense arrangement. It can support research on reinterpretation of regional air-well and threshold strategies. Claimed porosity ratios, wind speeds and post-occupancy criticisms need traceable project evidence.',
39:'Shōji are translucent sliding screens used in Japanese buildings. Paper, frame, layering and operation affect daylight, enclosure and heat transfer. A single-layer screen and a double-layer insulated retrofit are different assemblies. This entry avoids treating one material transmittance or seasonal preference as universal.',
40:'Capiz windows use translucent shell infill in timber frames, notably in Philippine bahay na bato architecture. They mediate light, views and operable enclosure. Shell thickness, visible transmittance and infrared properties require measurements of specified assemblies. Historical origin and craft practices require dedicated sources.',
43:'Bologna’s porticoes form an extensive network of covered urban thresholds. The entry considers solar and rain shelter alongside public circulation and access. Regional climate modelling provides background exposure information; it does not directly measure the cooling effect of a portico or establish pedestrian behaviour.',
44:'Traditional Lhasa houses combine masonry, courtyards, galleries and roof spaces in a high-altitude setting. Solar exposure, enclosure and seasonal occupation are relevant research topics. Temperature ranges, surface conditions, maintenance rituals and actual room use need building-specific evidence.',
57:'Cartuja Qanat is a contemporary public-space adaptation demonstrator in Seville. Project documentation combines traditional inspiration with shading, vegetation, water-based cooling, photovoltaics and hybrid systems. It must be distinguished from historic gravity-fed qanat infrastructure. Operating energy, water demand, maintenance and measured comfort are central to its evaluation.'}

# Exact bibliographic corrections checked against publisher/institutional records.
CORRECTIONS = [
('Energy and microclimatic performance of restored hypogeous buildings', 'Cardinale, N., Rospi, G. & Stazi, A. (2010). Energy and microclimatic performance of restored hypogeous buildings in south Italy: The “Sassi” district of Matera. Building and Environment, 45, 94–106. https://doi.org/10.1016/j.buildenv.2009.05.017', 'https://api.crossref.org/works/10.1016/j.buildenv.2009.05.017', 'metadata_verified'),
('The relation between outdoor microclimate and people flow', 'Boeri, A., Longo, D., Fabbri, K., Roversi, R. & Boulanger, S. (2023). The Relation between Outdoor Microclimate and People Flow in Historic City Context the Case Study of Bologna within the ROCK Project. Sustainability, 15(9), 7527. https://doi.org/10.3390/su15097527', 'https://www.unibo.it/sitoweb/kristian.fabbri/publications?page=2', 'metadata_verified'),
('Kabre, C. (2022). Jaali:', 'Prasad, R., Tandon, R., Verma, A., Sharma, M. & Ajmera, N. (2022). Jaali a tool of sustainable architectural practice: Understanding the feasibility and usage. Materials Today: Proceedings, 60, 513–525. https://doi.org/10.1016/j.matpr.2022.01.424', 'https://api.crossref.org/works/10.1016/j.matpr.2022.01.424', 'metadata_verified'),
('Seasonal analysis of thermal comfort in Mediterranean social courtyards', 'Diz-Mellado, E., López-Cabeza, V. P., Rivera-Gómez, C. & Galán-Marín, C. (2023). Seasonal analysis of thermal comfort in Mediterranean social courtyards: A comparative study. Journal of Building Engineering, 78, 107756. https://doi.org/10.1016/j.jobe.2023.107756', 'https://doi.org/10.1016/j.jobe.2023.107756', 'metadata_verified'),
('Energy and Environmental Performance of Trullo Stone Building', 'Stefanizzi, P., Fato, I. & Di Turi, S. (2016). Energy and Environmental Performance of Trullo Stone Building. An Experimental and Numerical Survey. International Journal of Heat and Technology, 34(S2), S396–S402. https://doi.org/10.18280/ijht.34S229', 'https://www.iieta.org/journals/ijht/paper/10.18280/ijht.34S229', 'full_text_reviewed'),
('Evaluation of heat insulation performance of the fitting combined taiko-shoji', 'Nakazono, M., Yoshiura, A., Mizunuma, M. & Koganei, M. (2012). Evaluation of heat insulation performance of the fitting combined Taiko-Shoji and wooden pair glass sash for traditional wooden house renovation. Journal of Environmental Engineering (Transactions of AIJ), 77(674), 241–249. https://doi.org/10.3130/aije.77.241', 'https://petit.lib.yamaguchi-u.ac.jp/19757', 'metadata_verified'),
('Analysis of urban thermal structures in different scenarios of hot weather', 'Possega, M., Brattich, E., Cintolesi, C., Ruggieri, P. & Di Sabatino, S. (2026). Analysis of urban thermal structures in different scenarios of hot weather: The Bologna case study. Urban Climate, 65, 102779. https://doi.org/10.1016/j.uclim.2026.102779', 'https://www.unibo.it/sitoweb/silvana.disabatino/publications', 'metadata_verified')]

def infer(row):
    s = (row['s'] + ' ' + row['e']).lower()
    if any(x in s for x in ['collect rain', 'cistern', 'collect rainfall']): return 'Collect / store water', 'Water-harvesting system'
    if any(x in s for x in ['evaporat', 'transpir']): return 'Evaporate', 'Water or vegetation cooling'
    if any(x in s for x in ['ground contact', 'ground coupling', 'embedding', 'excavat']): return 'Earth-couple', 'Ground-coupled enclosure'
    if any(x in s for x in ['reflectance', 'solar absorption', 'limewash']): return 'Reflect', 'Reflective surface'
    if any(x in s for x in ['rain', 'runoff', 'wetting']): return 'Shed / manage water', 'Rain-protective enclosure'
    if any(x in s for x in ['flood', 'wet ground']): return 'Elevate', 'Raised floor'
    if any(x in s for x in ['resist heat', 'insulat', 'felt layers', 'thatch']): return 'Resist heat transfer', 'Layered envelope'
    if any(x in s for x in ['store heat', 'store and release', 'delay heat', 'damp heat', 'thermal storage', 'masonry can', 'earth can store']): return 'Store / release heat', 'Thermal mass enclosure'
    if any(x in s for x in ['airflow', 'air movement', 'ventilation', 'air paths', 'air exchange', 'air wells', 'air path']): return 'Ventilate', 'Managed air path'
    if any(x in s for x in ['shade', 'shading', 'solar exposure', 'direct sun']): return 'Shade', 'Solar-control arrangement'
    if any(x in s for x in ['light', 'translucent', 'daylight']): return 'Transmit / scatter light', 'Translucent boundary'
    if any(x in s for x in ['wind exposure', 'wind shelter']): return 'Reduce wind exposure', 'Sheltered enclosure'
    return 'Modify exposure / use', 'Adaptive spatial or operational arrangement'

def main():
    prior_path = ROOT / 'data/reference-audit.json'
    prior = {r['id']: r for r in json.loads(prior_path.read_text()).get('references', [])} if prior_path.exists() else {}
    cases = json.loads(ARCHIVE.read_text())
    references, ref_index, logs = [], {}, []
    for c in cases:
        original = json.loads(json.dumps(c))
        c['referenceRecords'] = []
        for citation in c.get('refs', []):
            key = citation.strip()
            if key not in ref_index:
                record = {'id': 'REF-' + hashlib.sha256(key.encode()).hexdigest()[:10],
                          'original_citation': key, 'citation': key,
                          'status': 'verification_pending', 'case_ids': [],
                          'claim_support': 'Not established by bibliographic presence.'}
                for needle, replacement, url, status in CORRECTIONS:
                    if needle.lower() in key.lower():
                        record.update(citation=replacement, status=status, verification_url=url,
                                      correction_note='Original authors/year/locator corrected against primary metadata.')
                ref_index[key] = record
                for field in ('candidates', 'lookup_note'):
                    if field in prior.get(record['id'], {}):
                        record[field] = prior[record['id']][field]
                references.append(record)
            r = ref_index[key]
            r['case_ids'].append(c['id'])
            c['referenceRecords'].append(r)
        c['refs'] = [r['citation'] for r in c['referenceRecords']]
        if c['id'] in NARRATIVES:
            c['cult'] = NARRATIVES[c['id']]
        effects = EFFECTS[c['id']].split('|')
        assert len(effects) == len(c['re']), (c['id'], len(effects), len(c['re']))
        for i, (row, effect) in enumerate(zip(c['re'], effects)):
            row['e'] = effect
            if c['id'] in (12,26) and '3000' in row['c']:
                row['c'] = 'Monsoon rainfall'
            # Remove unverified quantitative geometry from the strategy label.
            row['s'] = re.sub(r'\b\d+(?:[.,–×°−-]\d+)*\s*(?:%|cm|mm|m|°)?\s*(?:\+\s*)?', '', row['s']).strip()
            row['s'] = re.sub(r'\s+', ' ', row['s']).replace('Superinsulation', 'Insulation').replace('superinsulation', 'insulation')
            row['mechanism'], row['strategyFamily'] = infer(row)
            row['claimId'] = f'SHIFT-{c["id"]:03d}-R{i+1:02d}'
            row['evidence'] = {
                'type': 'mechanism_inference', 'status': 'qualitative_interpretation',
                'site_relation': 'regional_type_or_case_interpretation',
                'source_ids': [], 'locator': None, 'outcome': 'Qualitative environmental consequence',
                'value': None, 'unit': None, 'comparator': None,
                'conditions': 'Depends on the actual geometry, material, weather, operation and occupancy.',
                'limitations': 'No case-specific effect size established. Bibliography entries are not claim validation.',
                'reviewed_at': DATE}
        c['evidencePilot'] = c['id'] in PILOT
        c['review'] = {'date': DATE, 'status': 'claims_screened', 'historical_claims': 'source_verification_pending',
            'mapping_basis': 'Representative point unless a specific building is explicitly documented; precision not independently verified.',
            'scope': 'Qualitative editorial interpretation; no blanket performance grade.'}
        c.get('tax', {}).pop('evidence', None)
        logs.append({'case_id': c['id'], 'name': c['name'], 'date': DATE,
            'actions': ['Screened all matrix claims and reference strings.',
                        'Replaced unsupported performance quantities and absolutes with conditional interpretation.',
                        'Removed uncalibrated whole-case evidence grade.',
                        'Retained original corpus for claim-by-claim comparison.'],
            'original_response_rows': original['re'],
            'original_narrative': original['cult'],
            'remaining_work': ['Verify primary full texts and page-level locators.',
                               'Verify location, geometry, historical and community-specific interpretation.'],
            'pilot': c['evidencePilot']})
    # Pilot-specific conditions, outcomes and source relationships.
    conditions = {
4:('Courtyard air and radiant conditions','Orientation, height-to-width ratio, water, vegetation, seasonal operation.','Separate shade, evaporation and heat storage; Mediterranean evidence is not universal.'),
5:('Indoor temperature buffering','Unoccupied Fasano trullo monitored March–November 2013; simulations extend conditions.','Comparable trullo, not the mapped Alberobello building; no isolated mechanism effect size.'),
6:('Ground-coupled temperature and moisture','Depth, geology, outdoor exposure, drainage, ventilation and occupancy.','Healthy conditions cannot be inferred from stable temperature alone.'),
7:('Airflow and coupled cooling','Tower geometry, wind direction, pressure differences and connected openings or water.','Separate wind-driven ventilation from evaporation and ground coupling.'),
12:('Ventilation and rain protection','Courtyard and inlet geometry, wind, humidity, overhangs and drainage.','Courtyard form does not demonstrate sufficient airflow or dehumidification.'),
34:('Body exposure and heat exchange','Felt thickness, wetting, posture, clothing, activity and duration.','No physiological benefit or insulation value has been measured for this record.'),
37:('Solar exposure, daylight, airflow and privacy','Aperture ratio, depth, orientation, pressure difference and indoor/outdoor light levels.','Enhanced mashrabiya devices are not evidence for a plain traditional screen.'),
38:('Solar exposure, daylight and air resistance','Screen depth, aperture geometry, orientation and wind pressure.','Local jet velocity is not equivalent to increased room ventilation.'),
40:('Transmitted light and views','Shell species, thickness, assembly, ageing and lighting.','Spectral selectivity and optical magnitudes remain unverified.'),
42:('Radiant exposure and use','Roof depth, solar angle, local airflow, access and observed occupation.','Surface temperature, air temperature and mean radiant temperature are different variables.'),
53:('Envelope heat transfer and seasonal maintenance','Organic layer thickness, moisture, installation, fire protection, pests and reuse.','A physical insulation principle does not verify the historical practice at the mapped point.'),
57:('Public-space cooling and operation','Actual hybrid equipment, water cycle, shading, energy, weather and public use.','Project design documentation is not measured comfort or energy performance.')}
    for c in cases:
        if c['id'] not in PILOT:
            continue
        outcome, cond, lim = conditions[c['id']]
        for row in c['re']:
            row['evidence'].update(outcome=outcome, conditions=cond, limitations=lim)
        # A retrieved sourcebook is a lead until pages/figures are checked, not claim-level support.
        c['review']['pilot_note'] = 'Each response has an explicit evidence type, relationship, conditions and limitation. Empty source links mean verification is still required.'
    trullo = next(c for c in cases if c['id'] == 5)
    src = next(r for r in trullo['referenceRecords'] if 'ijht.34S229' in r['citation'])
    trullo['re'][0]['e'] = 'A monitored, unoccupied trullo in Selva di Fasano showed indoor temperature buffering. The authors also found winter conditions too cold without heating. This comparable building does not establish performance of every trullo.'
    trullo['re'][0]['evidence'].update(type='measured', status='full_text_reviewed', source_ids=[src['id']],
        site_relation='comparable_building_same_regional_type', locator='Sections 2, 4 and 7; monitoring March–November 2013',
        comparator='Indoor versus outdoor conditions in the monitored building; no matched control.',
        outcome='Indoor temperature variation; seasonal heating limitation')
    qanat = next(c for c in cases if c['id'] == 57)
    qref = {'id':'REF-cartuja-uia-2022','original_citation':None,
        'citation':'Urban Innovative Actions (2022). Cartuja Qanat – Seville. Project case study. https://uia.urban-initiative.eu/en/thematic-knowledge/building-resilient-cities-adapting-climate/cartuja-qanat-seville',
        'status':'full_text_reviewed', 'verification_url':'https://uia.urban-initiative.eu/en/thematic-knowledge/building-resilient-cities-adapting-climate/cartuja-qanat-seville',
        'case_ids':[57], 'claim_support':'Project components and purpose only, not measured thermal performance.'}
    references.append(qref);qanat['referenceRecords'].append(qref);qanat['refs'].append(qref['citation'])
    qanat['typology'] = 'Contemporary public-space cooling demonstrator'
    qanat['period'] = 'Contemporary project; UIA project period 2018–2021'
    qanat['lesson'] = 'Evaluate traditional inspiration together with contemporary equipment, water, energy, maintenance and public use. Do not treat this demonstrator as a purely passive historic qanat.'
    for row in qanat['re']:
        row['evidence'].update(type='documented_design', status='full_text_reviewed', source_ids=[qref['id']],
            locator='Project description, Identity and Recovering life on the street sections',
            site_relation='same_project_design_documentation', outcome='Documented project components; performance unquantified')
    for row, label in zip(qanat['re'], ['Shade and vegetation','Water-based cooling systems','Hybrid energy and operation','Public-space use and governance']):
        row['s'] = label
    out = ROOT / 'data/cases-reviewed.json'
    out.write_text(json.dumps(cases, ensure_ascii=False, indent=2))
    (ROOT / 'data/cases-reviewed.js').write_text('// Generated by tools/review_cases.py; edit the review inputs, then rebuild.\nwindow.ATLAS_CASES=' + json.dumps(cases, ensure_ascii=False, separators=(',', ':')) + ';\n')
    (ROOT / 'data/case-audit.json').write_text(json.dumps({'review_date':DATE,'scope':'All 58 matrix and narrative records screened; bibliography candidates are not full-text verification.','cases':logs}, ensure_ascii=False, indent=2))
    (ROOT / 'data/reference-audit.json').write_text(json.dumps({'review_date':DATE,'method':'Original strings screened, primary corrections recorded, other references remain pending. Crossref candidates do not validate identity or claim support.','references':references}, ensure_ascii=False, indent=2))
    (ROOT / 'data/evidence-pilot.json').write_text(json.dumps({'schema_version':'shift-evidence-v1','case_ids':sorted(PILOT),'cases':[{'case_id':c['id'],'name':c['name'],'claims':c['re']} for c in cases if c['id'] in PILOT]},ensure_ascii=False,indent=2))
    print(len(cases), 'cases;', len(references), 'distinct reference strings;', sum(len(c['re']) for c in cases), 'claims;', sum(len(c['re']) for c in cases if c['id'] in PILOT), 'pilot claims')

if __name__ == '__main__':
    main()
