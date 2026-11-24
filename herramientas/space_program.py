# Stages 2 and 3 of the space programme: projects, missions, goals, staff, private sector, debris, AI, solar system and colonies.
# Everything comes from the tables below. Used by make_space_gui.py, which writes the windows.
# Requirements: t:tech, a:action done, h:headquarters level, s:launch bases, n:astronauts.

# Effects: variables of the dynamic modifier mdr_space_program_modifier, plus "prestige" and "debris".
# id, category, Spanish name, English name, Spanish effect, English effect, science, money (billions), weeks, requirements, effects, script when finished
PROJECTS = [
 ("engine_test", 1, "Banco de motores", "Engine Test Stand", "Lanzamientos más fiables y más ciencia.", "More reliable launches and more science.", 34, 0.7, 12, ["t:launcher"], {"olv_r": 0.018, "science": 0.02}, ""),
 ("launch_auto", 1, "Cuenta regresiva automatizada", "Automated Countdown", "Lanzadores más rápidos y presupuesto más barato.", "Faster launchers and a cheaper budget.", 41, 0.8, 12, ["t:launcher", "a:engine_test"], {"olv_s": 0.04, "budget": -0.012}, ""),
 ("upper_stage", 1, "Etapa superior reencendible", "Restartable Upper Stage", "Más fiabilidad y satélites más rápidos.", "More reliability and faster satellites.", 47, 0.9, 14, ["t:cryogenic"], {"olv_r": 0.024, "sat": 0.02}, ""),
 ("heavy_booster", 1, "Propulsor lateral pesado", "Heavy Side Booster", "Lanzadores más rápidos y más ciencia por cosmódromo.", "Faster launchers and more science per spaceport.", 58, 1.6, 20, ["t:heavy"], {"olv_s": 0.05, "site": 0.1}, ""),
 ("reuse_trial", 1, "Ensayo de recuperación", "Recovery Trial", "Lanzadores mucho más baratos.", "Far cheaper launchers.", 62, 1.4, 18, ["t:reusable"], {"olv_c": -0.06}, ""),
 ("super_pad", 1, "Plataforma superpesada", "Super-Heavy Pad", "Cada cosmódromo da bastante más ciencia.", "Each spaceport gives far more science.", 96, 3.4, 30, ["t:superheavy"], {"site": 0.24, "olv_s": 0.06}, ""),
 ("eva_suit", 2, "Trajes espaciales propios", "Own Spacesuits", "Más ciencia y 2 astronautas.", "More science and 2 astronauts.", 38, 0.6, 10, ["t:crewed"], {"science": 0.018}, "add_to_variable = { mdr_space_astronauts = 2 }"),
 ("astro_corps", 2, "Cuerpo de astronautas", "Astronaut Corps", "6 astronautas y más poder político.", "6 astronauts and more political power.", 44, 0.9, 12, ["t:crewed"], {"pp": 0.006}, "add_to_variable = { mdr_space_astronauts = 6 }"),
 ("crew_capsule", 2, "Cápsula tripulada propia", "Own Crew Capsule", "Más ciencia, estabilidad y apoyo a la guerra.", "More science, stability and war support.", 66, 1.8, 24, ["t:crewed"], {"science": 0.03, "stability": 0.003, "war": 0.006, "prestige": 3}, ""),
 ("space_medicine", 2, "Medicina espacial", "Space Medicine", "Investigación y estabilidad.", "Research and stability.", 49, 0.7, 14, ["t:longstay"], {"research": 0.003, "stability": 0.002}, ""),
 ("rad_shelter", 2, "Refugios contra la radiación", "Radiation Shelters", "Más ciencia y más fiabilidad.", "More science and reliability.", 58, 1.1, 18, ["t:radiation"], {"science": 0.022, "olv_r": 0.009}, ""),
 ("life_loop", 2, "Ciclo cerrado de soporte vital", "Closed Life Loop", "Más ciencia y presupuesto más barato.", "More science and a cheaper budget.", 72, 1.4, 22, ["t:lifesupport"], {"science": 0.026, "budget": -0.01}, ""),
 ("solar_sat", 3, "Satélite solar de prueba", "Solar Test Satellite", "Más energía en todo el país.", "More energy across the country.", 57, 1.3, 20, ["t:powerarrays"], {"energy": 0.012}, ""),
 ("rtg_program", 3, "Programa de radioisótopos", "Radioisotope Programme", "Más ciencia y energía.", "More science and energy.", 61, 1.2, 18, ["t:rtg"], {"science": 0.024, "energy": 0.004}, ""),
 ("isru_test", 3, "Uso de recursos in situ", "In-Situ Resource Use", "Presupuesto más barato.", "A cheaper budget.", 69, 1.5, 20, ["t:lunarice"], {"budget": -0.016}, ""),
 ("fuel_depot", 3, "Tecnología de depósitos", "Depot Technology", "Lanzadores más baratos y más rápidos.", "Cheaper and faster launchers.", 74, 1.9, 22, ["t:refuel"], {"olv_c": -0.04, "olv_s": 0.03}, ""),
 ("lunar_reactor", 3, "Reactor para la superficie", "Surface Reactor Design", "Más ciencia por cosmódromo y energía.", "More science per spaceport and energy.", 88, 2.6, 26, ["t:fission"], {"site": 0.12, "energy": 0.01}, ""),
 ("power_beam", 3, "Ensayo de energía transmitida", "Power Beaming Trial", "Mucha más energía en todo el país.", "Much more energy across the country.", 104, 3.1, 30, ["t:powerbeam"], {"energy": 0.026}, ""),
 ("debris_radar", 4, "Radar de basura espacial", "Debris Radar", "Baja la basura orbital en 3 y da inteligencia.", "Lowers orbital debris by 3 and gives intelligence.", 36, 0.6, 10, ["t:debris"], {"intel": 0.012, "debris": -3}, ""),
 ("asat_test", 4, "Ensayo antisatélite", "Anti-Satellite Test", "Apoyo a la guerra e inteligencia, pero suma 9 de basura orbital para todos.", "War support and intelligence, but adds 9 orbital debris for everyone.", 46, 1.1, 8, ["t:spacecommand"], {"war": 0.01, "intel": 0.01, "debris": 9}, ""),
 ("sat_hardening", 4, "Satélites protegidos", "Protected Satellites", "Satélites más rápidos.", "Faster satellites.", 53, 1.0, 14, ["t:hardening"], {"sat": 0.024}, ""),
 ("warning_sat", 4, "Satélites de alerta", "Warning Satellites", "Inteligencia y satélites más rápidos.", "Intelligence and faster satellites.", 59, 1.5, 16, ["t:awareness"], {"intel": 0.018, "sat": 0.012}, ""),
 ("planet_watch", 4, "Vigilancia planetaria", "Planetary Watch", "Estabilidad y más ciencia.", "Stability and more science.", 64, 1.3, 20, ["t:planetary"], {"stability": 0.004, "science": 0.016}, ""),
 ("debris_cleanup", 4, "Misión de limpieza", "Cleanup Mission", "Saca 18 de basura orbital, para todos.", "Removes 18 orbital debris, for everyone.", 82, 2.4, 24, ["t:cleanup"], {"debris": -18, "prestige": 2}, ""),
 ("sat_bus", 5, "Plataforma común de satélites", "Common Satellite Bus", "Satélites más rápidos.", "Faster satellites.", 33, 0.5, 10, ["t:smallsat"], {"sat": 0.03}, ""),
 ("cubesat_fab", 5, "Fábrica de nanosatélites", "Nanosatellite Plant", "Satélites más rápidos y presupuesto más barato.", "Faster satellites and a cheaper budget.", 37, 0.6, 10, ["t:smallsat", "a:sat_bus"], {"sat": 0.02, "budget": -0.008}, ""),
 ("micro_lab", 5, "Laboratorio de microgravedad", "Microgravity Laboratory", "Investigación.", "Research.", 42, 0.8, 12, ["t:microgravity"], {"research": 0.004}, ""),
 ("export_program", 5, "Programa de exportación", "Export Programme", "Presupuesto bastante más barato y poder político.", "A far cheaper budget and political power.", 55, 0.9, 16, ["t:commercialsat"], {"budget": -0.03, "pp": 0.005}, ""),
 ("space_print", 5, "Impresión 3D de piezas", "3D Part Printing", "Construcción más rápida en todo el país.", "Faster construction across the country.", 63, 1.4, 18, ["t:printing"], {"build": 0.01}, ""),
 ("orbital_plant", 5, "Planta orbital piloto", "Pilot Orbital Plant", "Más producción de las fábricas militares.", "More military factory output.", 99, 3.2, 30, ["t:manufacturing"], {"factory": 0.012}, ""),
]

# Same columns. Those of categories 1, 3 and 4 are launches: they can fail.
MISSIONS = [
 ("probe_moon", 1, "Sonda a la Luna", "Lunar Probe", "Más ciencia y prestigio.", "More science and prestige.", 28, 0.7, 16, ["t:launcher", "t:navigation"], {"science": 0.016, "prestige": 3}, ""),
 ("probe_mercury", 1, "Sonda a Mercurio", "Mercury Probe", "Más ciencia y prestigio.", "More science and prestige.", 58, 1.5, 34, ["t:gravityassist", "a:probe_venus"], {"science": 0.02, "prestige": 3}, ""),
 ("probe_venus", 1, "Sonda a Venus", "Venus Probe", "Más ciencia y prestigio.", "More science and prestige.", 44, 1.1, 26, ["t:gravityassist", "a:probe_moon"], {"science": 0.018, "prestige": 3}, ""),
 ("probe_mars", 1, "Sonda a Marte", "Mars Probe", "Más ciencia y prestigio.", "More science and prestige.", 52, 1.4, 30, ["t:heavy", "t:gravityassist", "a:probe_moon"], {"science": 0.024, "prestige": 4}, ""),
 ("probe_asteroid", 1, "Sonda a un asteroide", "Asteroid Probe", "Más ciencia y prestigio.", "More science and prestige.", 66, 1.6, 36, ["t:deepnet", "a:probe_mars"], {"science": 0.022, "prestige": 4}, ""),
 ("probe_jupiter", 1, "Sonda a Júpiter", "Jupiter Probe", "Mucha más ciencia y prestigio.", "Much more science and prestige.", 92, 2.9, 52, ["t:deepnet", "t:rtg", "a:probe_mars"], {"science": 0.034, "prestige": 6}, ""),
 ("probe_saturn", 1, "Sonda a Saturno", "Saturn Probe", "Mucha más ciencia y prestigio.", "Much more science and prestige.", 118, 3.8, 64, ["a:probe_jupiter"], {"science": 0.042, "prestige": 8}, ""),
 ("own_station", 2, "Estación orbital propia", "Own Orbital Station", "Un proyecto más a la vez, y más ciencia.", "One more project at a time, and more science.", 86, 4.2, 40, ["t:station", "h:2"], {"science": 0.05, "prestige": 8}, "add_to_variable = { mdr_space_extra_slots = 1 }"),
 ("station_lab", 2, "Módulo de laboratorio", "Laboratory Module", "Ciencia e investigación.", "Science and research.", 62, 2.1, 24, ["a:own_station"], {"science": 0.03, "research": 0.003}, ""),
 ("space_tug", 2, "Remolcador orbital", "Orbital Tug", "Lanzadores más rápidos.", "Faster launchers.", 58, 1.7, 20, ["t:refuel"], {"olv_s": 0.04}, ""),
 ("space_telescope", 2, "Telescopio espacial", "Space Telescope", "Más ciencia e inteligencia.", "More science and intelligence.", 73, 2.2, 30, ["t:tracking"], {"science": 0.036, "intel": 0.008, "prestige": 4}, ""),
 ("orbital_depot", 2, "Depósito orbital", "Orbital Depot", "Lanzadores más baratos.", "Cheaper launchers.", 77, 2.6, 26, ["a:fuel_depot"], {"olv_c": -0.05}, ""),
 ("orbital_yard", 2, "Astillero orbital", "Orbital Yard", "Más fábricas y lanzadores más rápidos.", "More factories and faster launchers.", 140, 6.8, 48, ["t:shipyard"], {"factory": 0.01, "olv_s": 0.07, "prestige": 6}, ""),
 ("crew_moon", 3, "Misión tripulada a la Luna", "Crewed Moon Mission", "Gran prestigio: hay que tener 6 astronautas.", "Great prestige: 6 astronauts are needed.", 112, 7.4, 40, ["t:crewed", "t:heavy", "t:translunar", "a:probe_moon", "n:6"], {"prestige": 18, "stability": 0.005}, ""),
 ("moon_base", 3, "Base lunar", "Lunar Base", "Funda la colonia de la Luna.", "Founds the Moon colony.", 168, 14.6, 60, ["t:habitat", "t:precisionland", "a:crew_moon"], {"prestige": 22}, "mdr_col_moon_found = yes mdr_moon_start = yes"),
 ("moon_expand", 3, "Ampliar la base lunar", "Expand the Lunar Base", "20 colonos más de capacidad.", "Room for 20 more colonists.", 96, 6.1, 36, ["a:moon_base"], {"prestige": 4}, "add_to_variable = { mdr_col_moon_cap = 20 }"),
 ("moon_ice", 3, "Minas de hielo lunar", "Lunar Ice Mines", "Lanzadores más baratos y energía.", "Cheaper launchers and energy.", 71, 3.8, 26, ["t:lunarice", "a:moon_base"], {"olv_c": -0.03, "energy": 0.006}, ""),
 ("moon_regolith", 3, "Minería de regolito", "Regolith Mining", "12 de aluminio y 8 de acero en la capital.", "12 aluminium and 8 steel in the capital.", 84, 4.7, 30, ["t:regolith", "a:moon_base"], {"factory": 0.004}, "capital_scope = { add_resource = { type = aluminium amount = 12 } add_resource = { type = steel amount = 8 } }"),
 ("moon_observatory", 3, "Observatorio lunar", "Lunar Observatory", "Mucha más ciencia.", "Much more science.", 88, 4.4, 32, ["a:moon_base"], {"science": 0.05, "prestige": 4}, ""),
 ("mars_lander", 4, "Módulo de descenso en Marte", "Mars Lander", "Más ciencia y prestigio.", "More science and prestige.", 94, 4.8, 48, ["t:aerobrake", "t:precisionland", "a:probe_mars"], {"science": 0.03, "prestige": 6}, ""),
 ("mars_flyby", 4, "Sobrevuelo tripulado de Marte", "Crewed Mars Flyby", "Gran prestigio: hay que tener 12 astronautas.", "Great prestige: 12 astronauts are needed.", 138, 11.2, 70, ["t:transithab", "a:mars_lander", "n:12"], {"prestige": 14}, ""),
 ("crew_mars", 4, "Misión tripulada a Marte", "Crewed Mars Mission", "El mayor prestigio posible.", "The greatest prestige there is.", 240, 26.4, 104, ["t:marslanding", "t:marstransfer", "a:mars_flyby", "n:12"], {"prestige": 40, "stability": 0.01, "pp": 0.01}, ""),
 ("mars_base", 4, "Base marciana", "Martian Base", "Funda la colonia de Marte.", "Founds the Mars colony.", 280, 34.8, 120, ["t:habitat", "a:crew_mars"], {"prestige": 30}, "mdr_col_mars_found = yes mdr_mars_start = yes"),
 ("mars_fuel", 4, "Planta de combustible marciano", "Martian Fuel Plant", "Lanzadores más baratos.", "Cheaper launchers.", 110, 8.2, 48, ["t:marsfuel", "a:mars_base"], {"olv_c": -0.04}, ""),
 ("mars_dome", 4, "Gran domo marciano", "Great Martian Dome", "Estabilidad, ciencia y 30 colonos más de capacidad.", "Stability, science and room for 30 more colonists.", 134, 9.6, 56, ["t:biosphere", "a:mars_base"], {"stability": 0.004, "science": 0.05}, "add_to_variable = { mdr_col_mars_cap = 30 }"),
 ("venus_station", 6, "Estación flotante en Venus", "Venus Floating Station", "Mucha más ciencia y gran prestigio.", "Much more science and great prestige.", 190, 16.4, 72, ["t:venusfloat", "a:probe_venus", "n:12"], {"science": 0.06, "prestige": 14}, "mdr_col_venus_found = yes mdr_venus_start = yes"),
 ("mercury_mine", 6, "Estación solar en Mercurio", "Mercury Solar Station", "Mucha más energía y prestigio.", "Much more energy and prestige.", 210, 18.2, 80, ["t:powerbeam", "a:probe_mercury"], {"energy": 0.04, "prestige": 12}, "mdr_col_mercury_found = yes mdr_mercury_start = yes"),
 ("asteroid_outpost", 6, "Puesto en los asteroides", "Asteroid Outpost", "20 de acero y 14 de cromo en la capital, y más fábricas.", "20 steel and 14 chromium in the capital, and more factories.", 220, 19.6, 84, ["t:asteroidnav", "t:asteroidmining", "a:probe_asteroid"], {"factory": 0.014, "prestige": 14}, "capital_scope = { add_resource = { type = steel amount = 20 } add_resource = { type = chromium amount = 14 } } mdr_col_asteroids_found = yes mdr_asteroids_start = yes"),
 ("callisto_base", 6, "Base en Calisto (Júpiter)", "Callisto Base (Jupiter)", "Enorme ciencia y prestigio.", "Huge science and prestige.", 320, 38.4, 130, ["t:outerprop", "a:probe_jupiter", "a:mars_base"], {"science": 0.09, "prestige": 28}, "mdr_col_callisto_found = yes mdr_callisto_start = yes"),
 ("titan_base", 6, "Base en Titán (Saturno)", "Titan Base (Saturn)", "Combustible, enorme ciencia y prestigio.", "Fuel, huge science and prestige.", 380, 46.2, 150, ["t:titanentry", "a:probe_saturn", "a:callisto_base"], {"science": 0.11, "prestige": 34, "olv_c": -0.05}, "mdr_col_titan_found = yes mdr_titan_start = yes"),
 ("join_iss", 5, "Sumarse a la estación internacional", "Join the International Station", "Más ciencia, y astronautas propios en órbita.", "More science, and our own astronauts in orbit.", 22, 1.1, 8, ["h:1"], {"science": 0.028}, "add_to_variable = { mdr_space_astronauts = 2 }"),
 ("space_treaty", 5, "Tratado del Espacio Exterior", "Outer Space Treaty", "Poder político y estabilidad.", "Political power and stability.", 12, 0.2, 6, ["h:1"], {"pp": 0.004, "stability": 0.002}, ""),
 ("sell_launch", 5, "Vender lanzamientos", "Sell Launches", "Presupuesto más barato.", "A cheaper budget.", 18, 0.4, 10, ["t:launcher"], {"budget": -0.024}, ""),
 ("share_science", 5, "Compartir datos científicos", "Share Scientific Data", "Investigación.", "Research.", 30, 0.5, 12, ["h:2"], {"research": 0.003}, ""),
 ("debris_accord", 5, "Acuerdo sobre basura espacial", "Debris Accord", "Saca 12 de basura orbital, para todos.", "Removes 12 orbital debris, for everyone.", 40, 0.8, 16, ["t:debris"], {"debris": -12, "pp": 0.003}, ""),
 ("joint_mars", 5, "Programa conjunto a Marte", "Joint Mars Programme", "Presupuesto más barato y prestigio.", "A cheaper budget and prestige.", 90, 5.6, 40, ["a:probe_mars"], {"budget": -0.02, "prestige": 5}, ""),
]

CATS_P = [("programme", "Cohetes", "Rockets"), ("staff", "Vida", "Life"), ("solar", "Energía", "Energy"), ("goals", "Defensa", "Defence"), ("projects", "Industria", "Industry")]
# Shortcuts at the bottom of the summary: picture, page, and an extra effect when clicked.
# Solar system page: the map on the left (SOLAR_W x SOLAR_H), the Sun just outside its left edge, and where each body sits.
SOLAR_W, SOLAR_H, SOLAR_SUN = 486, 576, (-40, 288)
SOLAR_POS = {"mercury": (82, 250), "venus": (126, 340), "earth": (178, 214), "moon": (212, 182), "mars": (236, 352),
             "asteroids": (300, 150), "jupiter": (344, 430), "saturn": (424, 236)}
# A picture of Millennium Dawn for each goal card, in GOALS order.
GOAL_ART = ["nasa_launch_mars", "astronauts", "nasa_orion_space_capsule", "moonbase_construction", "moonbase", "mars_mission", "manned_mission_mars", "mars_colony_1"]
# Banners of the two colonies.
COLONY_ART = ["moonbase", "mars_colony_1"]
CARDS = [
 ("astronauts", 4, "", "Agencia y personal", "Agency and Staff"),
 ("news_nasa_launch_mars", 3, "", "Proyectos", "Projects"),
 ("moonbase", 6, "set_variable = { mdr_space_body = 4 }", "Base lunar", "Lunar Base"),
 ("mars_mission", 7, "set_variable = { mdr_space_cat_d = 4 }", "Misión a Marte", "Mars Mission"),
 ("nasa", 2, "", "Objetivos", "Goals"),
]
CAT_ART_P = ["news_nasa_launch_mars", "astronauts", "news_moonbase_construction", "space_debris", "news_spacex_announcement"]
CAT_ART_D = ["news_spacex_mars", "nasa_orion_space_capsule", "news_moonbase", "news_manned_mission_mars", "nasa", "news_asteroid"]
CATS_D = [("summary", "Misiones", "Missions"), ("projects", "Órbita", "Orbit"), ("colonies", "Luna", "Moon"), ("goals", "Marte", "Mars"), ("decisions", "Cooperación", "Cooperation"), ("solar", "Exterior", "Outer System")]

# id, Spanish, English, Spanish text, English text, requirements, prestige
GOALS = [
 ("orbit", "Acceso a la órbita", "Access to Orbit", "Un lanzador y un cosmódromo propios.", "A launcher and a spaceport of our own.", ["t:launcher", "s:1"], 5),
 ("crew", "Vuelo tripulado", "Crewed Flight", "Un cuerpo de astronautas y vuelo tripulado.", "An astronaut corps and crewed flight.", ["t:crewed", "a:astro_corps"], 8),
 ("station", "Estación propia", "Own Station", "Una estación orbital propia.", "An orbital station of our own.", ["a:own_station"], 10),
 ("moon_return", "Regreso a la Luna", "Return to the Moon", "Una misión tripulada a la Luna.", "A crewed mission to the Moon.", ["a:crew_moon"], 14),
 ("moon_colony", "Base lunar", "Lunar Base", "Una colonia en la Luna.", "A colony on the Moon.", ["a:moon_base"], 16),
 ("mars_robot", "Robots en Marte", "Robots on Mars", "Una sonda y un módulo de descenso en Marte.", "A probe and a lander on Mars.", ["a:probe_mars", "a:mars_lander"], 8),
 ("mars_crew", "Personas en Marte", "People on Mars", "Una misión tripulada a Marte.", "A crewed mission to Mars.", ["a:crew_mars"], 24),
 ("mars_colony", "Colonia marciana", "Martian Colony", "Una colonia en Marte.", "A colony on Mars.", ["a:mars_base"], 30),
]

# id, x, y, size on the map, names, text, mission that reaches it, picture, the road there
BODIES = [
 ("mercury", 112, 96, 26, "Mercurio", "Mercury", "Metales y sol sin límite, a un costo enorme. Solo una estación solar.", "Metals and limitless sun, at an enormous cost. Only a solar station.", "probe_mercury", "GFX_mars_colony_10", ["t:navigation", "t:gravityassist", "a:probe_venus", "a:probe_mercury", "t:powerbeam", "a:mercury_mine"]),
 ("venus", 186, 204, 38, "Venus", "Venus", "Atmósfera ácida y aplastante. Se vive flotando, a 50 km de altura.", "A crushing, acidic atmosphere. People live afloat, 50 km up.", "probe_venus", "GFX_mars_colony_5", ["t:navigation", "t:gravityassist", "a:probe_venus", "t:venusfloat", "a:venus_station"]),
 ("earth", 276, 110, 44, "Tierra", "Earth", "Nuestra base: cosmódromos, satélites y estaciones.", "Our base: spaceports, satellites and stations.", None, "GFX_astronauts", []),
 ("moon", 326, 62, 22, "Luna", "Moon", "Hielo, regolito y helio-3, a tres días de viaje. Se puede colonizar.", "Ice, regolith and helium-3, three days away. It can be colonised.", "moon_base", "GFX_moonbase", ["t:navigation", "a:probe_moon", "t:translunar", "t:crewed", "a:crew_moon", "t:habitat", "t:precisionland", "a:moon_base"]),
 ("mars", 388, 216, 36, "Marte", "Mars", "Agua, CO2 y gravedad útil. El gran destino: se puede colonizar.", "Water, CO2 and useful gravity. The great goal: it can be colonised.", "mars_base", "GFX_mars_colony_1", ["t:gravityassist", "a:probe_mars", "t:aerobrake", "a:mars_lander", "t:transithab", "a:mars_flyby", "t:marstransfer", "t:marslanding", "a:crew_mars", "t:habitat", "a:mars_base"]),
 ("asteroids", 488, 92, 46, "Asteroides", "Asteroids", "Metales raros y agua en cuerpos cercanos. Un puesto minero.", "Rare metals and water in nearby bodies. A mining outpost.", "probe_asteroid", "GFX_asteroid", ["t:deepnet", "a:probe_asteroid", "t:asteroidnav", "t:asteroidmining", "a:asteroid_outpost"]),
 ("jupiter", 586, 202, 74, "Júpiter", "Jupiter", "Sin superficie. Se llega a su luna Calisto, lejos de la radiación.", "No surface. People reach its moon Callisto, far from the radiation.", "probe_jupiter", "GFX_mars_colony_20", ["t:deepnet", "t:rtg", "a:probe_jupiter", "t:outerprop", "a:callisto_base"]),
 ("saturn", 694, 92, 66, "Saturno", "Saturn", "Sin superficie. Se llega a Titán, con sus lagos de metano.", "No surface. People reach Titan, with its methane lakes.", "probe_saturn", "GFX_mars_colony_6", ["a:probe_jupiter", "a:probe_saturn", "t:titanentry", "a:titan_base"]),
]

# Private sector: real companies, one contract per service at a time. A company can be hired while its country exists and is
# not at war with us, from the year it began selling that service and, if it stopped, until then.
SERVICES = [
 ("launch", "Lanzamientos", "Launches"),
 ("sat", "Satélites", "Satellites"),
 ("crew", "Tripulación y carga", "Crew and Cargo"),
 ("data", "Datos e imágenes", "Data and Imagery"),
]
# id, service, country, from, until (0 = still working), name, what it is (es, en), cost a week ($B), effects.
COMPANIES = [
 ("arianespace", "launch", "FRA", 1980, 0, "Arianespace", "Ariane 4 y 5 desde Kourou: la mitad del mercado comercial en 2000.", "Ariane 4 and 5 from Kourou: half of the commercial market in 2000.", 0.043, {"olv_c": -0.07, "olv_r": 0.012}),
 ("ils", "launch", "USA", 1995, 2022, "International Launch Services", "Protones rusos vendidos por Lockheed. Cerró con las sanciones de 2022.", "Russian Protons sold by Lockheed. It closed with the 2022 sanctions.", 0.038, {"olv_c": -0.09}),
 ("great_wall", "launch", "CHI", 1980, 0, "China Great Wall Industry", "Larga Marcha a bajo precio, con fallas en los noventa.", "Low-priced Long March, with failures in the nineties.", 0.027, {"olv_c": -0.11, "olv_r": -0.008}),
 ("antrix", "launch", "RAJ", 1992, 0, "Antrix", "El brazo comercial de la ISRO: viajes compartidos en el PSLV.", "ISRO's commercial arm: rideshares on the PSLV.", 0.021, {"olv_c": -0.06, "sat": 0.017}),
 ("mhi", "launch", "JAP", 2007, 0, "Mitsubishi Heavy Industries", "Opera el H-IIA desde 2007: caro y muy fiable.", "Runs the H-IIA since 2007: expensive and very reliable.", 0.052, {"olv_c": -0.04, "olv_r": 0.024}),
 ("spacex", "launch", "USA", 2010, 0, "SpaceX", "Falcon 9 desde 2010, reutilizable desde 2017. Rompió los precios.", "Falcon 9 since 2010, reusable since 2017. It broke the prices.", 0.047, {"olv_c": -0.16, "olv_s": 0.037}),
 ("rocket_lab", "launch", "NZL", 2018, 0, "Rocket Lab", "Electron desde Mahia: lanzamientos dedicados para satélites chicos.", "Electron from Mahia: dedicated launches for small satellites.", 0.019, {"sat": 0.043, "olv_c": -0.03}),
 ("loral", "sat", "USA", 1990, 2012, "Space Systems/Loral", "Satélites de comunicaciones en serie, en Palo Alto.", "Communication satellites in series, in Palo Alto.", 0.034, {"sat": 0.046}),
 ("astrium", "sat", "FRA", 2000, 2014, "Astrium", "La rama espacial de EADS: satélites, sondas y la parte europea de la estación.", "EADS's space arm: satellites, probes and Europe's share of the station.", 0.041, {"sat": 0.038, "science": 0.012}),
 ("sstl", "sat", "ENG", 1985, 0, "Surrey Satellite Technology", "Satélites chicos y baratos, nacidos en una universidad.", "Small, cheap satellites, born in a university.", 0.016, {"sat": 0.027, "budget": -0.011}),
 ("thales_alenia", "sat", "FRA", 2007, 0, "Thales Alenia Space", "Franco-italiana: satélites, módulos presurizados y Galileo.", "French-Italian: satellites, pressurised modules and Galileo.", 0.044, {"sat": 0.052, "science": 0.008}),
 ("oneweb", "sat", "ENG", 2019, 0, "OneWeb", "Constelación de internet en órbita baja, rescatada por el Reino Unido en 2020.", "Low-orbit internet constellation, rescued by the United Kingdom in 2020.", 0.036, {"sat": 0.061}),
 ("spacehab", "crew", "USA", 1984, 2011, "Spacehab", "Módulos de carga y laboratorio para el transbordador.", "Cargo and laboratory modules for the Shuttle.", 0.031, {"science": 0.034}),
 ("glavkosmos", "crew", "SOV", 1985, 0, "Glavkosmos", "Vende asientos en la Soyuz y tiempo en estaciones rusas.", "Sells Soyuz seats and time on Russian stations.", 0.048, {"science": 0.046}),
 ("space_adventures", "crew", "USA", 2001, 0, "Space Adventures", "Turismo espacial: Dennis Tito en 2001, en una Soyuz.", "Space tourism: Dennis Tito in 2001, on a Soyuz.", 0.022, {"science": 0.018, "budget": -0.014}),
 ("spacex_dragon", "crew", "USA", 2020, 0, "SpaceX Dragon", "Cápsula tripulada y de carga a la estación desde 2020.", "Crewed and cargo capsule to the station since 2020.", 0.067, {"science": 0.071, "olv_s": 0.012}),
 ("axiom", "crew", "USA", 2022, 0, "Axiom Space", "Misiones privadas a la estación con astronautas de otros países.", "Private missions to the station with astronauts from other countries.", 0.039, {"science": 0.052}),
 ("spot_image", "data", "FRA", 1982, 2014, "Spot Image", "Vende las imágenes de los satélites SPOT a gobiernos y empresas.", "Sells SPOT satellite imagery to governments and companies.", 0.018, {"budget": -0.027, "intel": 0.008}),
 ("iridium", "data", "USA", 2000, 0, "Iridium", "Telefonía satelital, rescatada de la quiebra en diciembre de 2000.", "Satellite telephony, rescued from bankruptcy in December 2000.", 0.024, {"budget": -0.019, "intel": 0.006}),
 ("digitalglobe", "data", "USA", 2001, 0, "DigitalGlobe", "Imágenes de alta resolución desde QuickBird, en 2001.", "High-resolution imagery from QuickBird, in 2001.", 0.029, {"budget": -0.033, "intel": 0.014}),
 ("planet", "data", "USA", 2014, 0, "Planet Labs", "Fotografía toda la Tierra cada día con cientos de satélites chicos.", "Photographs the whole Earth every day with hundreds of small satellites.", 0.026, {"budget": -0.031, "intel": 0.019}),
]
COMPANY_BY_ID = {c[0]: c for c in COMPANIES}
PC_KEYS = ["olv_c", "olv_s", "olv_r", "sat", "science", "budget", "intel"]
# What each effect changes, grouped by subject so a line fits: "launchers -16% cost and +3.7% speed".
PC_TEXT = {
 "olv_c": (("lanzadores", "costo"), ("launchers", "cost")),
 "olv_s": (("lanzadores", "velocidad"), ("launchers", "speed")),
 "olv_r": (("lanzadores", "fiabilidad"), ("launchers", "reliability")),
 "sat": (("satélites", "velocidad"), ("satellites", "speed")),
 "science": (("ciencia", ""), ("science", "")),
 "budget": (("presupuesto", ""), ("budget", "")),
 "intel": (("inteligencia", ""), ("intelligence", "")),
}


def companies_of(service):
    return [c for c in COMPANIES if c[1] == service]


def company_effects_text(c, lang):
    idx = 0 if lang == "spanish" else 1
    groups = {}
    for k, v in c[9].items():
        subject, measure = PC_TEXT[k][idx]
        amount = ("+" if v > 0 else "-") + number(round(abs(v) * 100, 1), lang) + "%"
        groups.setdefault(subject, []).append(f"{amount} {measure}".strip())
    joiner = " y " if idx == 0 else " and "
    return ", ".join(f"{subject} {joiner.join(items)}" for subject, items in groups.items())


def company_open(c):
    until = f" date < {c[4]}.1.1" if c[4] else ""
    return f"date > {c[3] - 1}.12.31{until} country_exists = {c[2]} NOT = {{ has_war_with = {c[2]} }}"

FX_VARS = ["research", "stability", "pp", "olv_s", "olv_c", "olv_r", "sat", "science", "budget", "site", "energy", "factory", "build", "intel", "war"]
import re

ACTIONS = [(a, "p") for a in PROJECTS] + [(a, "m") for a in MISSIONS]
ROLLED = (1, 3, 4, 6)  # mission categories that can fail


def tid(t):
    return "mdr_sp_" + t


def req_trigger(r):
    kind, value = r.split(":")
    if kind == "t":
        return f"has_tech = {tid(value)}"
    if kind == "a":
        return f"has_country_flag = mdr_sa_{value}_done"
    limit = {"h": "mdr_space_hq", "s": "mdr_space_sites", "n": "mdr_space_astronauts"}[kind]
    return f"check_variable = {{ {limit} > {int(value) - 1} }}"


def tech_names(lang):
    names = {}
    for line in open(f"localisation/{lang}/mdr_space_techs_l_{lang}.yml", encoding="utf-8-sig"):
        m = re.match(r' (mdr_sp_\w+):\d* "(.*)"', line)
        if m:
            names[m.group(1)] = m.group(2)
    return names


ACTION_BY_ID = {a[0]: a for a, _ in ACTIONS}


def req_loc(r, lang):
    kind, value = r.split(":")
    es = lang == "spanish"
    if kind == "t":
        return tech_names(lang)[tid(value)]
    if kind == "a":
        return ACTION_BY_ID[value][2 if es else 3]
    return {"h": ("sede nivel ", "headquarters level "), "s": ("cosmódromos: ", "spaceports: "), "n": ("astronautas: ", "astronauts: ")}[kind][0 if es else 1] + value


def req_key(r):
    return "MDR_RQ_" + r.replace(":", "_").upper()


def all_reqs():
    seen = {}
    for a, _ in ACTIONS:
        for r in a[9]:
            seen[r] = 1
    for g in GOALS:
        for r in g[5]:
            seen[r] = 1
    for b in BODIES:
        for r in b[10]:
            seen[r] = 1
    return list(seen)


def number(v, lang):
    s = f"{v:g}"
    return s.replace(".", ",") if lang == "spanish" else s


def write_files():
    write_triggers()
    write_effects()
    write_loc()
    write_events()


def write_triggers():
    s = "# Generated by herramientas/space_program.py.\n"
    s += "mdr_space_any_goal_ready = {\n\tOR = {\n" + "".join(f"\t\tAND = {{ mdr_sg_{g[0]}_met = yes NOT = {{ has_country_flag = mdr_sg_{g[0]}_claimed }} }}\n" for g in GOALS) + "\t}\n}\n\n"
    for a, _ in ACTIONS:
        name, sci, money, reqs = a[0], a[6], a[7], a[9]
        s += f"mdr_sa_{name}_reqs = {{\n" + "".join(f"\t{req_trigger(r)}\n" for r in reqs) + "}\n\n"
        s += f"mdr_sa_{name}_can = {{\n\tNOT = {{ has_country_flag = mdr_sa_{name}_done has_country_flag = mdr_sa_{name}_run }}\n\tmdr_sa_{name}_reqs = yes\n\tcheck_variable = {{ mdr_space_science > {sci - 1} }}\n\tcheck_variable = {{ treasury > {money} }}\n}}\n\n"
    for g in GOALS:
        s += f"mdr_sg_{g[0]}_met = {{\n" + "".join(f"\t{req_trigger(r)}\n" for r in g[5]) + "}\n\n"
    # Private companies: whether one can be hired now, and whether the one shown for a service can.
    for c in COMPANIES:
        s += f"mdr_pco_{c[0]}_open = {{\n\t{company_open(c)}\n}}\n\n"
    for key, _, _ in SERVICES:
        s += f"mdr_pc_{key}_view_open = {{\n\tOR = {{\n" + "".join(f"\t\tAND = {{ check_variable = {{ mdr_pc_{key}_view = {i + 1} }} mdr_pco_{c[0]}_open = yes }}\n" for i, c in enumerate(companies_of(key))) + "\t}\n}\n\n"
    with open("common/scripted_triggers/mdr_space_program_triggers.txt", "wb") as f:
        f.write(s.encode("utf-8"))


def finish_lines(a):
    fx, script = a[10], a[11]
    s = ""
    for k, v in fx.items():
        if k == "prestige":
            s += f"\tadd_to_variable = {{ mdr_space_prestige = {v} }}\n"
        elif k == "debris":
            s += f"\tadd_to_variable = {{ global.mdr_space_debris = {v} }}\n"
        else:
            s += f"\tadd_to_variable = {{ mdr_sm_{k} = {v} }}\n"
    if script:
        s += f"\t{script}\n"
    return s


CHART_YEARS = 5


def spend_effects():
    # Spending by year for the Finance chart. mdr_space_spend_0 is the year running, 1 to 4 the years before. Every payment
    # of the programme adds to it: the weekly cost here, and what is paid from the treasury where it is paid.
    k = range(CHART_YEARS)
    s = "# Weekly, before mdr_space_refresh: closes the year when it changes and adds this week's cost.\nmdr_space_spend_track = {\n"
    s += "\tif = { limit = { has_variable = mdr_space_spend_year NOT = { check_variable = { var = mdr_space_spend_year compare = equals value = global.year } } }\n"
    s += "\t\tset_temp_variable = { mdr_space_spend_gap = global.year }\n\t\tsubtract_from_temp_variable = { mdr_space_spend_gap = mdr_space_spend_year }\n"
    s += "".join(f"\t\tset_variable = {{ mdr_space_spend_{i} = mdr_space_spend_{i - 1} }}\n" for i in range(CHART_YEARS - 1, 0, -1))
    # More than a year without counting (no agency in between): those years cost nothing.
    s += "\t\tif = { limit = { check_variable = { mdr_space_spend_gap > 1 } }\n" + "".join(f"\t\t\tset_variable = {{ mdr_space_spend_{i} = 0 }}\n" for i in range(1, CHART_YEARS)) + "\t\t}\n"
    s += "\t\tset_variable = { mdr_space_spend_0 = 0 }\n\t\tset_variable = { mdr_space_spend_year = global.year }\n\t}\n"
    s += "\tadd_to_variable = { mdr_space_spend_0 = mdr_space_week_cost }\n}\n\n"
    s += "# From mdr_space_refresh: the height of each bar against the highest year, and the year under it.\nmdr_space_spend_chart = {\n"
    # Agencies of 2000 had budgets before: as an estimate, the same as now.
    s += "\tif = { limit = { NOT = { has_variable = mdr_space_spend_year } }\n\t\tset_variable = { mdr_space_spend_year = global.year }\n\t\tif = { limit = { date < 2000.6.1 }\n\t\t\tset_variable = { mdr_space_spend_1 = mdr_space_week_cost }\n\t\t\tmultiply_variable = { mdr_space_spend_1 = 52 }\n"
    s += "".join(f"\t\t\tset_variable = {{ mdr_space_spend_{i} = mdr_space_spend_1 }}\n" for i in range(2, CHART_YEARS))
    s += "\t\t}\n\t}\n\tset_variable = { mdr_space_spend_max = 0.01 }\n"
    s += "".join(f"\tif = {{ limit = {{ check_variable = {{ var = mdr_space_spend_{i} compare = greater_than value = mdr_space_spend_max }} }} set_variable = {{ mdr_space_spend_max = mdr_space_spend_{i} }} }}\n" for i in k)
    for i in k:
        s += f"\tset_variable = {{ mdr_space_spend_frame_{i} = mdr_space_spend_{i} }}\n\tmultiply_variable = {{ mdr_space_spend_frame_{i} = 50 }}\n\tdivide_variable = {{ mdr_space_spend_frame_{i} = mdr_space_spend_max }}\n\tround_variable = mdr_space_spend_frame_{i}\n\tadd_to_variable = {{ mdr_space_spend_frame_{i} = 1 }}\n"
        s += f"\tset_variable = {{ mdr_space_spend_y{i} = mdr_space_spend_year }}\n" + (f"\tsubtract_from_variable = {{ mdr_space_spend_y{i} = {i} }}\n" if i else "")
    return s + "}\n\n"


PAID = "\tmodify_treasury_effect = yes\n"
# Counts a payment from the treasury (treasury_change, negative) in this year's spending.
PAID_COUNTED = "\tsubtract_from_variable = { mdr_space_spend_0 = treasury_change }\n" + PAID


def write_effects():
    s = "# Generated by herramientas/space_program.py. Projects and missions: mdr_sa_<id>_run, _left (weeks) and _done.\n\n"
    for n, (a, kind) in enumerate(ACTIONS):
        name, sci, money, weeks = a[0], a[6], a[7], a[8]
        s += f"mdr_sa_{name}_begin = {{\n\tclr_country_flag = mdr_sa_{name}_queued\n\tset_country_flag = mdr_sa_{name}_run\n\tset_variable = {{ mdr_sa_{name}_left = {weeks} }}\n\tadd_to_variable = {{ mdr_space_active = 1 }}\n\tadd_to_variable = {{ mdr_space_science = -{sci} }}\n\tset_temp_variable = {{ treasury_change = -{money} }}\n\tmodify_treasury_effect = yes\n\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n}}\n\n"
        s += f"mdr_sa_{name}_finish = {{\n\tclr_country_flag = mdr_sa_{name}_run\n\tset_country_flag = mdr_sa_{name}_done\n\tadd_to_variable = {{ mdr_space_active = -1 }}\n{finish_lines(a)}\tset_variable = {{ mdr_space_last_action = {n + 1} }}\n\tif = {{ limit = {{ is_ai = no NOT = {{ has_country_flag = mdr_space_auto_quiet }} }} country_event = {{ id = mdr_space.1 }} }}\n}}\n\n"
    # Weekly countdown. Launches can fail: the mission must be started again.
    s += "mdr_space_actions_weekly = {\n\tset_temp_variable = { mdr_space_speed = mdr_space_engineers }\n\tdivide_temp_variable = { mdr_space_speed = 2000 }\n\tadd_to_temp_variable = { mdr_space_speed = 1 }\n"
    for n, (a, kind) in enumerate(ACTIONS):
        name = a[0]
        s += f"\tif = {{ limit = {{ has_country_flag = mdr_sa_{name}_run }}\n\t\tsubtract_from_variable = {{ mdr_sa_{name}_left = mdr_space_speed }}\n\t\tif = {{ limit = {{ check_variable = {{ mdr_sa_{name}_left < 0.01 }} }}\n"
        if kind == "m" and a[1] in ROLLED:
            s += f"\t\t\tmdr_space_roll = yes\n\t\t\tif = {{ limit = {{ check_variable = {{ mdr_space_roll_failed = 1 }} }}\n\t\t\t\tclr_country_flag = mdr_sa_{name}_run\n\t\t\t\tadd_to_variable = {{ mdr_space_active = -1 }}\n\t\t\t\tadd_to_variable = {{ mdr_space_prestige = -1 }}\n\t\t\t\tset_variable = {{ mdr_space_last_action = {n + 1} }}\n\t\t\t\tif = {{ limit = {{ is_ai = no }} country_event = {{ id = mdr_space.2 }} }}\n\t\t\t}}\n\t\t\telse = {{ mdr_sa_{name}_finish = yes }}\n"
        else:
            s += f"\t\t\tmdr_sa_{name}_finish = yes\n"
        s += "\t\t}\n\t}\n"
    s += "}\n\n"
    # Queue: what fits and can be paid starts by itself.
    s += "mdr_space_queue_weekly = {\n"
    for a, _ in ACTIONS:
        name = a[0]
        s += f"\tif = {{ limit = {{ has_country_flag = mdr_sa_{name}_queued mdr_sa_{name}_can = yes check_variable = {{ var = mdr_space_active compare = less_than value = mdr_space_slots }} }} mdr_sa_{name}_begin = yes }}\n"
    s += "}\n\n"
    # AI: limited. Takes the first thing it can pay for; only rich powers go past orbit.
    s += "mdr_space_ai_projects = {\n"
    for i, (a, kind) in enumerate(ACTIONS):
        name, cat = a[0], a[1]
        word = "if" if i == 0 else "else_if"
        extra = ""
        if kind == "m" and cat in (3, 4):
            extra = " check_variable = { mdr_space_tier > 2 } check_variable = { gdp_total > 2400 }"
        s += f"\t{word} = {{ limit = {{ mdr_sa_{name}_can = yes check_variable = {{ treasury > {a[7] * 3:.2f} }}{extra} }} mdr_sa_{name}_begin = yes }}\n"
    s += "}\n\n"
    s += spend_effects()
    # What was already done in 2000.
    s += '''mdr_space_program_start = {
	set_variable = { mdr_space_cat_p = 1 }
	set_variable = { mdr_space_cat_d = 1 }
	set_variable = { mdr_space_body = 3 }
	set_variable = { mdr_space_colony_view = 1 }
	set_variable = { mdr_space_hq = mdr_space_tier }
	if = { limit = { check_variable = { mdr_space_hq < 1 } } set_variable = { mdr_space_hq = 1 } }
	if = { limit = { check_variable = { mdr_space_tier = 3 } }
		set_variable = { mdr_space_scientists = 1240 }
		set_variable = { mdr_space_engineers = 3800 }
	}
	else_if = { limit = { check_variable = { mdr_space_tier = 2 } }
		set_variable = { mdr_space_scientists = 420 }
		set_variable = { mdr_space_engineers = 1300 }
	}
	else_if = { limit = { check_variable = { mdr_space_tier = 1 } }
		set_variable = { mdr_space_scientists = 120 }
		set_variable = { mdr_space_engineers = 360 }
	}
	if = { limit = { original_tag = USA }
		set_variable = { mdr_space_astronauts = 146 }
		set_variable = { mdr_space_prestige = 40 }
		set_country_flag = mdr_sa_astro_corps_done
		set_country_flag = mdr_sa_crew_capsule_done
		set_country_flag = mdr_sa_eva_suit_done
		set_country_flag = mdr_sa_engine_test_done
		set_country_flag = mdr_sa_probe_moon_done
		set_country_flag = mdr_sa_probe_venus_done
		set_country_flag = mdr_sa_probe_mars_done
		set_country_flag = mdr_sa_probe_jupiter_done
		set_country_flag = mdr_sa_probe_saturn_done
		set_country_flag = mdr_sa_crew_moon_done
		set_country_flag = mdr_sa_space_telescope_done
		set_country_flag = mdr_sa_join_iss_done
		set_country_flag = mdr_sa_space_treaty_done
	}
	else_if = { limit = { original_tag = SOV }
		set_variable = { mdr_space_astronauts = 40 }
		set_variable = { mdr_space_prestige = 28 }
		set_country_flag = mdr_sa_astro_corps_done
		set_country_flag = mdr_sa_crew_capsule_done
		set_country_flag = mdr_sa_eva_suit_done
		set_country_flag = mdr_sa_engine_test_done
		set_country_flag = mdr_sa_probe_moon_done
		set_country_flag = mdr_sa_probe_venus_done
		set_country_flag = mdr_sa_probe_mars_done
		set_country_flag = mdr_sa_own_station_done
		set_country_flag = mdr_sa_join_iss_done
		set_country_flag = mdr_sa_space_treaty_done
		add_to_variable = { mdr_space_extra_slots = 1 }
	}
	else_if = { limit = { check_variable = { mdr_space_tier = 2 } }
		set_variable = { mdr_space_astronauts = 6 }
		set_variable = { mdr_space_prestige = 6 }
		set_country_flag = mdr_sa_engine_test_done
	}
	else_if = { limit = { check_variable = { mdr_space_tier = 1 } }
		set_variable = { mdr_space_prestige = 1 }
	}
	if = { limit = { NOT = { has_dynamic_modifier = { modifier = mdr_space_program_modifier } } } add_dynamic_modifier = { modifier = mdr_space_program_modifier } }
	if = { limit = { NOT = { has_dynamic_modifier = { modifier = mdr_space_standing_modifier } } } add_dynamic_modifier = { modifier = mdr_space_standing_modifier } }
}

# Country init, after the first refresh: goals reached before 2000 count as claimed, without their reward again.
mdr_space_claim_past_goals = {
''' + "".join(f"\tif = {{ limit = {{ mdr_sg_{g[0]}_met = yes }} set_country_flag = mdr_sg_{g[0]}_claimed }}\n" for g in GOALS) + '''}

# A launch: 84% plus the launcher reliability, up to 97%. Output: mdr_space_roll_failed.
mdr_space_roll = {
	set_temp_variable = { mdr_space_chance = modifier@olv_launch_reliability_modifier }
	add_to_temp_variable = { mdr_space_chance = 0.84 }
	if = { limit = { check_variable = { mdr_space_chance > 0.97 } } set_temp_variable = { mdr_space_chance = 0.97 } }
	set_temp_variable = { mdr_space_dice = random }
	if = { limit = { check_variable = { var = mdr_space_dice compare = greater_than value = mdr_space_chance } } set_variable = { mdr_space_roll_failed = 1 } }
	else = { set_variable = { mdr_space_roll_failed = 0 } }
}

# Country scope, weekly: everything that moves in an agency.
mdr_space_program_weekly = {
	# Scientists: 0.4 science a week per hundred.
	set_temp_variable = { mdr_space_staff_science = mdr_space_scientists }
	multiply_temp_variable = { mdr_space_staff_science = 0.004 }
	add_to_variable = { mdr_space_science = mdr_space_staff_science }
	if = { limit = { check_variable = { mdr_space_active > 0 } } mdr_space_actions_weekly = yes }
	mdr_space_queue_weekly = yes
''' + "".join(f"\tif = {{ limit = {{ has_country_flag = mdr_col_{c[0]} }} mdr_col_{c[0]}_weekly = yes mdr_{c[0]}_weekly = yes }}\n" for c in COLONY_KEYS) + '''	mdr_space_standing_update = yes
	# The player's automatic mode (herramientas/space_auto.py).
	if = { limit = { is_ai = no has_country_flag = mdr_space_auto } mdr_space_auto_weekly = yes }
	if = { limit = { is_ai = yes }
		if = { limit = { check_variable = { var = mdr_space_active compare = less_than value = mdr_space_slots } }
			random_list = {
				12 = { mdr_space_ai_projects = yes }
				88 = { }
			}
		}
		# Its Mars colony grows by itself (herramientas/space_colony.py).
''' + "".join(f"\t\tif = {{ limit = {{ has_country_flag = mdr_col_{c[0]} check_variable = {{ treasury > 12 }} }}\n\t\t\trandom_list = {{\n\t\t\t\t14 = {{ mdr_{c[0]}_auto = yes }}\n\t\t\t\t86 = {{ }}\n\t\t\t}}\n\t\t}}\n" for c in COLONY_KEYS) + '''		# One service a year or so, while the treasury has room.
		if = { limit = { check_variable = { treasury > 15 } }
			random_list = {
				2 = { mdr_space_ai_contracts = yes }
				98 = { }
			}
		}
		# It keeps a budget according to its level, and grows if it is rich.
		if = { limit = { check_variable = { mdr_space_budget < 12 } check_variable = { treasury > 20 } check_variable = { gdp_total > 600 } } set_variable = { mdr_space_budget = 12 } }
	}
}

# Slots, prestige, colonies and debris as modifiers.
mdr_space_standing_update = {
	set_variable = { mdr_space_slots = 1 }
	if = { limit = { check_variable = { mdr_space_hq > 2 } } add_to_variable = { mdr_space_slots = 1 } }
	if = { limit = { check_variable = { mdr_space_hq > 4 } } add_to_variable = { mdr_space_slots = 1 } }
	add_to_variable = { mdr_space_slots = mdr_space_extra_slots }
	# Prestige: 0.04% stability and 0.03% political power per point. Failed launches cannot take it below zero.
	if = { limit = { check_variable = { mdr_space_prestige < 0 } } set_variable = { mdr_space_prestige = 0 } }
	set_variable = { mdr_st_stability = mdr_space_prestige }
	multiply_variable = { mdr_st_stability = 0.0004 }
	set_variable = { mdr_st_pp = mdr_space_prestige }
	multiply_variable = { mdr_st_pp = 0.0003 }
	# Debris: up to -9% launch reliability and +12% launcher cost at 100.
	set_variable = { mdr_st_debris_r = global.mdr_space_debris }
	multiply_variable = { mdr_st_debris_r = -0.0009 }
	set_variable = { mdr_st_debris_c = global.mdr_space_debris }
	multiply_variable = { mdr_st_debris_c = 0.0012 }
	# Colonies: research per settler, factories per workshop.
	set_variable = { mdr_st_col_research = 0 }
''' + "".join(f"\tadd_to_variable = {{ mdr_st_col_research = mdr_col_{c[0]}_pop }}\n" for c in COLONY_KEYS) + '''	multiply_variable = { mdr_st_col_research = 0.00008 }
	set_variable = { mdr_st_col_factory = 0 }
''' + "".join(f"\tadd_to_variable = {{ mdr_st_col_factory = mdr_col_{c[0]}_workshop }}\n" for c in COLONY_KEYS) + '''	multiply_variable = { mdr_st_col_factory = 0.003 }
	# Payroll and supply routes, paid with the budget (mdr_space_refresh adds them to the expense).
	set_variable = { mdr_space_payroll = mdr_space_scientists }
	add_to_variable = { mdr_space_payroll = mdr_space_engineers }
	multiply_variable = { mdr_space_payroll = 0.00002 }
	set_temp_variable = { mdr_space_astro_pay = mdr_space_astronauts }
	multiply_temp_variable = { mdr_space_astro_pay = 0.0004 }
	add_to_variable = { mdr_space_payroll = mdr_space_astro_pay }
''' + "".join(f"\tif = {{ limit = {{ has_country_flag = mdr_col_{c[0]}_route }} add_to_variable = {{ mdr_space_payroll = {c[3]} }} }}\n" for c in COLONY_KEYS) + '''	set_variable = { mdr_space_contract_cost = 0 }
'''
    s += "\t# Private companies: one per service. A contract ends by itself if the company can no longer be hired.\n"
    s += "".join(f"\tset_variable = {{ mdr_pc_{k} = 0 }}\n" for k in PC_KEYS)
    for key, _, _ in SERVICES:
        s += f"\tif = {{ limit = {{ check_variable = {{ mdr_pc_{key}_view < 1 }} }} set_variable = {{ mdr_pc_{key}_view = 1 }} }}\n"
        for i, c in enumerate(companies_of(key)):
            s += f"\tif = {{ limit = {{ check_variable = {{ mdr_pc_{key}_signed = {i + 1} }} }}\n\t\tif = {{ limit = {{ NOT = {{ mdr_pco_{c[0]}_open = yes }} }} set_variable = {{ mdr_pc_{key}_signed = 0 }} }}\n\t\telse = {{\n\t\t\tadd_to_variable = {{ mdr_space_payroll = {c[8]} }}\n\t\t\tadd_to_variable = {{ mdr_space_contract_cost = {c[8]} }}\n"
            s += "".join(f"\t\t\tadd_to_variable = {{ mdr_pc_{k} = {v} }}\n" for k, v in c[9].items())
            s += "\t\t}\n\t}\n"
    s += "\tadd_to_variable = { mdr_st_debris_r = mdr_pc_olv_r }\n"
    s += "}\n\n"
    # AI: hires the first company it can for a service it lacks, if it has money to spare.
    s += "mdr_space_ai_contracts = {\n"
    for n, (key, _, _) in enumerate(SERVICES):
        any_open = " ".join(f"mdr_pco_{c[0]}_open = yes" for c in companies_of(key))
        s += f"\t{'if' if n == 0 else 'else_if'} = {{ limit = {{ check_variable = {{ mdr_pc_{key}_signed < 1 }} OR = {{ {any_open} }} }}\n"
        for i, c in enumerate(companies_of(key)):
            s += f"\t\t{'if' if i == 0 else 'else_if'} = {{ limit = {{ mdr_pco_{c[0]}_open = yes }} set_variable = {{ mdr_pc_{key}_signed = {i + 1} }} set_variable = {{ mdr_pc_{key}_view = {i + 1} }} }}\n"
        s += "\t}\n"
    s += "}\n\nmdr_space_upgrade_hq = {\n\tset_temp_variable = { mdr_space_hq_money = mdr_space_hq }\n\tmultiply_temp_variable = { mdr_space_hq_money = -1.2 }\n\tset_temp_variable = { treasury_change = mdr_space_hq_money }\n\tmodify_treasury_effect = yes\n\tset_temp_variable = { mdr_space_hq_science = mdr_space_hq }\n\tmultiply_temp_variable = { mdr_space_hq_science = -40 }\n\tadd_to_variable = { mdr_space_science = mdr_space_hq_science }\n\tadd_to_variable = { mdr_space_hq = 1 }\n\tmdr_space_refresh = yes\n}\n\n"
    # Orbital debris of the whole world.
    s += '''# World, weekly: every launch leaves something behind.
mdr_space_debris_weekly = {
	if = { limit = { NOT = { has_global_flag = mdr_space_debris_started } }
		set_global_flag = mdr_space_debris_started
		set_variable = { global.mdr_space_debris = 8 }
	}
	add_to_variable = { global.mdr_space_debris = 0.021 }
	if = { limit = { check_variable = { global.mdr_space_debris < 0 } } set_variable = { global.mdr_space_debris = 0 } }
	if = { limit = { check_variable = { global.mdr_space_debris > 100 } } set_variable = { global.mdr_space_debris = 100 } }
	if = { limit = { check_variable = { global.mdr_space_debris > 70 } NOT = { has_global_flag = mdr_space_kessler_warned } }
		set_global_flag = mdr_space_kessler_warned
		every_country = { limit = { is_ai = no check_variable = { mdr_space_tier > 0 } } country_event = { id = mdr_space.3 } }
	}
}

'''
    for b, cap, money, _, _, _ in COLONY_KEYS:
        s += colony_effects(b, cap, money)
    s = s.replace(PAID, PAID_COUNTED)
    with open("common/scripted_effects/mdr_space_program.txt", "wb") as f:
        f.write(s.encode("utf-8"))


SUPPLIES = ["water", "food", "energy", "oxygen"]
# Colonies: key, settlers they can hold when founded, cost of sending 4 settlers and of the cargo route a week ($B),
# body number in the solar map, and the mission that founds them. The plans are in space_colony.py.
COLONY_KEYS = [("moon", 40, 0.4, 0.09, 4, "moon_base"), ("mars", 24, 1.4, 0.34, 5, "mars_base"), ("venus", 16, 1.6, 0.41, 2, "venus_station"),
               ("mercury", 12, 1.9, 0.52, 1, "mercury_mine"), ("asteroids", 14, 1.3, 0.38, 6, "asteroid_outpost"), ("callisto", 18, 2.6, 0.74, 7, "callisto_base"),
               ("titan", 18, 3.1, 0.88, 8, "titan_base")]
MODULES = [("greenhouse", "food", 0.9), ("mine", "water", 0.8), ("reactor", "energy", 1.1), ("workshop", None, 0)]


def colony_effects(b, cap, money):
    p = f"mdr_col_{b}"
    s = f"{p}_found = {{\n\tset_country_flag = {p}\n\tset_variable = {{ {p}_pop = 12 }}\n\tset_variable = {{ {p}_cap = {cap} }}\n\tset_variable = {{ {p}_morale = 70 }}\n"
    for x in SUPPLIES:
        s += f"\tset_variable = {{ {p}_{x} = 60 }}\n"
    s += f"\t{p}_frames = yes\n}}\n\n"
    s += f"{p}_frames = {{\n\tset_temp_variable = {{ mdr_col_use = {p}_pop }}\n\tmultiply_temp_variable = {{ mdr_col_use = -0.05 }}\n\tif = {{ limit = {{ has_country_flag = {p}_route }} add_to_temp_variable = {{ mdr_col_use = 6 }} }}\n"
    for x, m, k in (("water", "mine", 0.8), ("food", "greenhouse", 0.9), ("energy", "reactor", 1.1), ("oxygen", "mine", 0.8)):
        s += f"\tset_variable = {{ {p}_{x}_net = {p}_{m} }}\n\tmultiply_variable = {{ {p}_{x}_net = {k} }}\n\tadd_to_variable = {{ {p}_{x}_net = mdr_col_use }}\n"
    for x in SUPPLIES:
        s += f"\tset_variable = {{ {p}_{x}_frame = {p}_{x} }}\n\tdivide_variable = {{ {p}_{x}_frame = 2 }}\n\tround_variable = {p}_{x}_frame\n\tadd_to_variable = {{ {p}_{x}_frame = 1 }}\n"
    s += "}\n\n"
    s += f"# Each settler uses supplies; modules make them, and the route brings 6 of each a week.\n{p}_weekly = {{\n\tset_temp_variable = {{ mdr_col_use = {p}_pop }}\n\tmultiply_temp_variable = {{ mdr_col_use = 0.05 }}\n"
    for x in SUPPLIES:
        s += f"\tsubtract_from_variable = {{ {p}_{x} = mdr_col_use }}\n"
    for m, x, k in MODULES:
        if x:
            s += f"\tset_temp_variable = {{ mdr_col_made = {p}_{m} }}\n\tmultiply_temp_variable = {{ mdr_col_made = {k} }}\n\tadd_to_variable = {{ {p}_{x} = mdr_col_made }}\n"
            if x == "water":
                s += f"\tadd_to_variable = {{ {p}_oxygen = mdr_col_made }}\n"
    s += f"\tif = {{ limit = {{ has_country_flag = {p}_route }}\n"
    for x in SUPPLIES:
        s += f"\t\tadd_to_variable = {{ {p}_{x} = 6 }}\n"
    s += "\t}\n"
    for x in SUPPLIES:
        s += f"\tif = {{ limit = {{ check_variable = {{ {p}_{x} < 0 }} }} set_variable = {{ {p}_{x} = 0 }} }}\n\tif = {{ limit = {{ check_variable = {{ {p}_{x} > 100 }} }} set_variable = {{ {p}_{x} = 100 }} }}\n"
    low = " ".join(f"check_variable = {{ {p}_{x} < 15 }}" for x in SUPPLIES)
    s += f"\tif = {{ limit = {{ OR = {{ {low} }} }}\n\t\tadd_to_variable = {{ {p}_morale = -3 }}\n\t\tif = {{ limit = {{ check_variable = {{ {p}_morale < 25 }} check_variable = {{ {p}_pop > 0 }} }} add_to_variable = {{ {p}_pop = -1 }} }}\n\t\tif = {{ limit = {{ is_ai = no NOT = {{ has_country_flag = {p}_warned }} }} set_country_flag = {p}_warned country_event = {{ id = mdr_space.4 }} }}\n\t}}\n"
    s += f"\telse = {{\n\t\tclr_country_flag = {p}_warned\n\t\tif = {{ limit = {{ check_variable = {{ {p}_morale < 100 }} }} add_to_variable = {{ {p}_morale = 1 }} }}\n\t}}\n\tif = {{ limit = {{ check_variable = {{ {p}_morale < 0 }} }} set_variable = {{ {p}_morale = 0 }} }}\n"
    s += f"\t# Science of the colony.\n\tset_temp_variable = {{ mdr_col_science = {p}_pop }}\n\tmultiply_temp_variable = {{ mdr_col_science = 0.09 }}\n\tadd_to_variable = {{ mdr_space_science = mdr_col_science }}\n\t{p}_frames = yes\n}}\n\n"
    s += f"{p}_send = {{\n\tadd_to_variable = {{ {p}_pop = 4 }}\n\tif = {{ limit = {{ check_variable = {{ var = {p}_pop compare = greater_than value = {p}_cap }} }} set_variable = {{ {p}_pop = {p}_cap }} }}\n\tset_temp_variable = {{ treasury_change = -{money} }}\n\tmodify_treasury_effect = yes\n\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n}}\n\n"
    return s


def write_events():
    s = '''add_namespace = mdr_space
# Generated by herramientas/space_program.py.

country_event = {
	id = mdr_space.1
	title = mdr_space.1.t
	desc = mdr_space.1.d
	picture = GFX_nasa_launch_mars
	is_triggered_only = yes

	option = {
		name = mdr_space.1.a
	}
}

country_event = {
	id = mdr_space.2
	title = mdr_space.2.t
	desc = mdr_space.2.d
	picture = GFX_space_debris
	is_triggered_only = yes

	option = {
		name = mdr_space.2.a
	}
}

country_event = {
	id = mdr_space.3
	title = mdr_space.3.t
	desc = mdr_space.3.d
	picture = GFX_space_debris
	is_triggered_only = yes

	option = {
		name = mdr_space.3.a
	}
}

country_event = {
	id = mdr_space.4
	title = mdr_space.4.t
	desc = mdr_space.4.d
	picture = GFX_moonbase
	is_triggered_only = yes

	option = {
		name = mdr_space.4.a
	}
}
'''
    with open("events/mdr_space_events.txt", "wb") as f:
        f.write(s.encode("utf-8"))
    # Name of the last project or mission, for those events.
    d = "# Generated by herramientas/space_program.py.\ndefined_text = {\n\tname = mdr_space_last_name\n"
    for n, (a, _) in enumerate(ACTIONS):
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_last_action = {n + 1} }} }}\n\t\tlocalization_key = MDR_SA_{a[0].upper()}\n\t}}\n"
    d += "}\n\n"
    for key, rows in (("name", 5), ("text", 7)):
        d += f"defined_text = {{\n\tname = mdr_space_body_{key}\n"
        for i, b in enumerate(BODIES):
            d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_body = {i + 1} }} }}\n\t\tlocalization_key = MDR_SPACE_BODY_{b[0].upper()}{'' if key == 'name' else '_TEXT'}\n\t}}\n"
        d += "}\n\n"
    for a, _ in ACTIONS:
        name, N = a[0], a[0].upper()
        d += f"defined_text = {{\n\tname = mdr_sa_{name}_status\n\ttext = {{\n\t\ttrigger = {{ has_country_flag = mdr_sa_{name}_done }}\n\t\tlocalization_key = MDR_SPACE_ST_DONE\n\t}}\n\ttext = {{\n\t\ttrigger = {{ has_country_flag = mdr_sa_{name}_run }}\n\t\tlocalization_key = MDR_SA_{N}_LEFT\n\t}}\n\ttext = {{\n\t\ttrigger = {{ has_country_flag = mdr_sa_{name}_queued }}\n\t\tlocalization_key = MDR_SPACE_ST_QUEUED\n\t}}\n"
        for r in a[9]:
            d += f"\ttext = {{\n\t\ttrigger = {{ NOT = {{ {req_trigger(r)} }} }}\n\t\tlocalization_key = {req_key(r)}\n\t}}\n"
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_science < {a[6]} }} }}\n\t\tlocalization_key = MDR_SPACE_ST_NO_SCIENCE\n\t}}\n\ttext = {{\n\t\ttrigger = {{ NOT = {{ check_variable = {{ treasury > {a[7]} }} }} }}\n\t\tlocalization_key = MDR_SPACE_ST_NO_MONEY\n\t}}\n\ttext = {{\n\t\tlocalization_key = MDR_SPACE_ST_READY\n\t}}\n}}\n\n"
    for g in GOALS:
        name = g[0]
        d += f"defined_text = {{\n\tname = mdr_sg_{name}_status\n\ttext = {{\n\t\ttrigger = {{ has_country_flag = mdr_sg_{name}_claimed }}\n\t\tlocalization_key = MDR_SPACE_GOAL_DONE\n\t}}\n"
        for r in g[5]:
            d += f"\ttext = {{\n\t\ttrigger = {{ NOT = {{ {req_trigger(r)} }} }}\n\t\tlocalization_key = {req_key(r)}\n\t}}\n"
        d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_GOAL_READY\n\t}\n}\n\n"
    # The next step towards the selected body.
    d += "defined_text = {\n\tname = mdr_space_body_step\n"
    for i, b in enumerate(BODIES):
        for r in b[10]:
            d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_body = {i + 1} }} NOT = {{ {req_trigger(r)} }} }}\n\t\tlocalization_key = {req_key(r)}\n\t}}\n"
    d += "\ttext = {\n\t\ttrigger = { check_variable = { mdr_space_body = 3 } }\n\t\tlocalization_key = MDR_SPACE_BODY_HOME\n\t}\n\ttext = {\n\t\tlocalization_key = MDR_SPACE_BODY_ALL_DONE\n\t}\n}\n\n"
    # Private companies: the one shown for each service on the Agency page, and the one hired, for Finance.
    def by_index(name, var, key_of, fallback):
        t = f"defined_text = {{\n\tname = {name}\n"
        for i, c in enumerate(companies_of(service)):
            t += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ {var} = {i + 1} }} }}\n\t\tlocalization_key = {key_of(c)}\n\t}}\n"
        return t + f"\ttext = {{\n\t\tlocalization_key = {fallback}\n\t}}\n}}\n\n"
    for service, _, _ in SERVICES:
        view, signed = f"mdr_pc_{service}_view", f"mdr_pc_{service}_signed"
        first = f"MDR_PCO_{companies_of(service)[0][0].upper()}"
        d += by_index(f"mdr_pc_{service}_view_name", view, lambda c: f"MDR_PCO_{c[0].upper()}", first)
        d += by_index(f"mdr_pc_{service}_view_info", view, lambda c: f"MDR_PCO_{c[0].upper()}_INFO", first + "_INFO")
        d += by_index(f"mdr_pc_{service}_view_tt", view, lambda c: f"MDR_PCO_{c[0].upper()}_TT", first + "_TT")
        d += by_index(f"mdr_pc_{service}_signed_name", signed, lambda c: f"MDR_PCO_{c[0].upper()}", "MDR_PC_NONE")
        d += by_index(f"mdr_pc_{service}_signed_cost", signed, lambda c: f"MDR_PCO_{c[0].upper()}_COST", "MDR_SPACE_EMPTY")
        d += f"defined_text = {{\n\tname = mdr_pc_{service}_view_state\n"
        for i, c in enumerate(companies_of(service)):
            N, at = c[0].upper(), f"check_variable = {{ {view} = {i + 1} }}"
            d += f"\ttext = {{\n\t\ttrigger = {{ {at} check_variable = {{ {signed} = {i + 1} }} }}\n\t\tlocalization_key = MDR_PCO_{N}_ON\n\t}}\n"
            d += f"\ttext = {{\n\t\ttrigger = {{ {at} mdr_pco_{c[0]}_open = yes }}\n\t\tlocalization_key = MDR_PCO_{N}_FREE\n\t}}\n"
            d += f"\ttext = {{\n\t\ttrigger = {{ {at} date < {c[3]}.1.1 }}\n\t\tlocalization_key = MDR_PCO_{N}_SOON\n\t}}\n"
            if c[4]:
                d += f"\ttext = {{\n\t\ttrigger = {{ {at} date > {c[4] - 1}.12.31 }}\n\t\tlocalization_key = MDR_PC_STATE_CLOSED\n\t}}\n"
            d += f"\ttext = {{\n\t\ttrigger = {{ {at} country_exists = {c[2]} has_war_with = {c[2]} }}\n\t\tlocalization_key = MDR_PC_STATE_WAR\n\t}}\n"
        d += "\ttext = {\n\t\tlocalization_key = MDR_PC_STATE_LOCKED\n\t}\n}\n\n"
    # A requirement, in green or red.
    for r in all_reqs():
        name = req_key(r).lower()
        d += f"defined_text = {{\n\tname = {name}\n\ttext = {{\n\t\ttrigger = {{ {req_trigger(r)} }}\n\t\tlocalization_key = {req_key(r).replace('MDR_RQ', 'MDR_RK')}\n\t}}\n\ttext = {{\n\t\tlocalization_key = {req_key(r)}\n\t}}\n}}\n\n"
    # The first thing that can be started.
    d += "defined_text = {\n\tname = mdr_space_suggest\n"
    for a, _ in ACTIONS:
        d += f"\ttext = {{\n\t\ttrigger = {{ mdr_sa_{a[0]}_can = yes }}\n\t\tlocalization_key = MDR_SA_{a[0].upper()}\n\t}}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_SUGGEST_NONE\n\t}\n}\n\n"
    # The first goal not claimed.
    for var, suffix in (("mdr_space_goal_now", ""), ("mdr_space_goal_now_status", "_STATUS")):
        d += f"defined_text = {{\n\tname = {var}\n"
        for g in GOALS:
            d += f"\ttext = {{\n\t\ttrigger = {{ NOT = {{ has_country_flag = mdr_sg_{g[0]}_claimed }} }}\n\t\tlocalization_key = MDR_SG_{g[0].upper()}{suffix}\n\t}}\n"
        d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_GOALS_ALL_DONE\n\t}\n}\n\n"
    # The road to each colony.
    for b in BODIES:
        if b[0] in ("moon", "mars"):
            d += f"defined_text = {{\n\tname = mdr_col_{b[0]}_step\n"
            for r in b[10]:
                d += f"\ttext = {{\n\t\ttrigger = {{ NOT = {{ {req_trigger(r)} }} }}\n\t\tlocalization_key = {req_key(r)}\n\t}}\n"
            d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_BODY_ALL_DONE\n\t}\n}\n\n"
    # What to do now, on the summary.
    ready = " ".join(f"AND = {{ mdr_sg_{g[0]}_met = yes NOT = {{ has_country_flag = mdr_sg_{g[0]}_claimed }} }}" for g in GOALS)
    steps = [("check_variable = { mdr_space_sites < 1 }", "SITE"), ("check_variable = { mdr_space_budget < 1 }", "BUDGET"), (f"OR = {{ {ready} }}", "GOAL"), ("check_variable = { mdr_space_active < 1 }", "IDLE"), ("check_variable = { var = mdr_space_active compare = less_than value = mdr_space_slots }", "ROOM")]
    d += "defined_text = {\n\tname = mdr_space_next_step\n"
    for trigger, key in steps:
        d += f"\ttext = {{\n\t\ttrigger = {{ {trigger} }}\n\t\tlocalization_key = MDR_SPACE_STEP_{key}\n\t}}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_STEP_WAIT\n\t}\n}\n\n"
    d += "defined_text = {\n\tname = mdr_space_body_state\n"
    for i, b in enumerate(BODIES):
        if b[8]:
            d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ mdr_space_body = {i + 1} }} has_country_flag = mdr_sa_{b[8]}_done }}\n\t\tlocalization_key = MDR_SPACE_BODY_REACHED\n\t}}\n"
    d += "\ttext = {\n\t\ttrigger = { check_variable = { mdr_space_body = 3 } }\n\t\tlocalization_key = MDR_SPACE_BODY_HOME\n\t}\n\ttext = {\n\t\tlocalization_key = MDR_SPACE_BODY_UNREACHED\n\t}\n}\n"
    with open("common/scripted_localisation/mdr_space_program_loc.txt", "wb") as f:
        f.write(d.encode("utf-8"))


STATIC = {
 **{f"MDR_SPACE_CARD_{i}": (c[3], c[4]) for i, c in enumerate(CARDS)},
 **{f"MDR_SPACE_CAT_COUNT_OPEN_{n}": (f"{n} · abierta  -", f"{n} · open  -") for n in range(1, 9)},
 **{f"MDR_SPACE_CAT_COUNT_SHUT_{n}": (f"{n}  +", f"{n}  +") for n in range(1, 9)},
 # Frame of the big menu: figures on top, groups of the side bar, bottom bar.
 "MDR_SPACE_TOP_TREASURY": ("TESORO", "TREASURY"), "MDR_SPACE_TOP_TREASURY_V": ("§Y$$[?treasury|1]B§!", "§Y$$[?treasury|1]B§!"),
 "MDR_SPACE_TOP_TREASURY_TT": ("Dinero del país. Paga proyectos, misiones, sede y obras en colonias.", "The country's money. It pays for projects, missions, headquarters and colony works."),
 "MDR_SPACE_TOP_UPKEEP": ("GASTO SEMANAL", "WEEKLY UPKEEP"), "MDR_SPACE_TOP_UPKEEP_V": ("§R$$[?mdr_space_week_cost|3]B§!", "§R$$[?mdr_space_week_cost|3]B§!"),
 "MDR_SPACE_TOP_UPKEEP_TT": ("Presupuesto, sueldos, rutas de carga y empresas contratadas, cada semana. Figura en Economía.", "Budget, wages, cargo routes and hired companies, every week. It shows in Economy."),
 "MDR_SPACE_TOP_SCIENCE": ("CIENCIA", "SCIENCE"), "MDR_SPACE_TOP_SCIENCE_V": ("§G[?mdr_space_science|0]§! (+[?mdr_space_science_week|1])", "§G[?mdr_space_science|0]§! (+[?mdr_space_science_week|1])"),
 "MDR_SPACE_TOP_SCIENCE_TT": ("Ciencia juntada y lo que entra por semana. Paga proyectos y misiones.", "Science gathered and what comes in each week. It pays for projects and missions."),
 "MDR_SPACE_TOP_PRESTIGE": ("PRESTIGIO", "PRESTIGE"), "MDR_SPACE_TOP_PRESTIGE_V": ("§Y[?mdr_space_prestige|0]§!", "§Y[?mdr_space_prestige|0]§!"),
 "MDR_SPACE_TOP_PRESTIGE_TT": ("Sube con objetivos y grandes misiones; baja con fallas. Da estabilidad y poder político.", "It rises with goals and great missions and falls with failures. It gives stability and political power."),
 "MDR_SPACE_GROUP_PROGRAMME": ("PROGRAMA", "PROGRAMME"), "MDR_SPACE_GROUP_EXPLORATION": ("EXPLORACIÓN", "EXPLORATION"),
 "MDR_SPACE_GROUP_OPERATIONS": ("OPERACIONES", "OPERATIONS"), "MDR_SPACE_GROUP_HELP": ("AYUDA", "HELP"),
 "MDR_SPACE_TAB_9": ("Guía", "Guide"), "MDR_MARS_LINK_TEXT": ("Cada colonia tiene su propio plano: casillas, módulos y obras. Se abre en una ventana grande.", "Each colony has its own plan: slots, modules and works. It opens in a large window."), "MDR_SPACE_NAV_9": ("§YGuía§!: cómo funciona, paso a paso.", "§YGuide§!: how it works, step by step."),
 "MDR_SPACE_BAR_TITLE": ("PRÓXIMO PASO", "NEXT STEP"),
 "MDR_SPACE_CHART_TITLE": ("GASTO POR AÑO", "SPENDING BY YEAR"),
 "MDR_SPACE_CHART_TT": ("Todo lo que costó el programa cada año: presupuesto, sueldos, rutas, contratos, proyectos, misiones, sede y obras en colonias. La última barra es el año en curso. Cada barra se mide contra el año más caro.", "Everything the programme cost each year: budget, wages, routes, contracts, projects, missions, headquarters and colony works. The last bar is the year running. Each bar is measured against the most expensive year."),
 **{f"MDR_SPACE_CHART_V{i}": (f"$$[?mdr_space_spend_{i}|1]B", f"$$[?mdr_space_spend_{i}|1]B") for i in range(CHART_YEARS)},
 **{f"MDR_SPACE_CHART_Y{i}": (f"[?mdr_space_spend_y{i}|0]", f"[?mdr_space_spend_y{i}|0]") for i in range(CHART_YEARS)},
 "MDR_SPACE_CONTRACTS_TITLE": ("EMPRESAS: $$[?mdr_space_contract_cost|3]B/SEM", "COMPANIES: $$[?mdr_space_contract_cost|3]B/WK"),
 "MDR_SPACE_CONTRACTS_GO_TT": ("Las empresas se eligen, contratan y cortan en la página Agencia: una por servicio.", "Companies are chosen, hired and dropped on the Agency page: one per service."),
 "MDR_PC_STATE_LOCKED": ("§gSu país no existe§!", "§gIts country is gone§!"),
 "MDR_PC_STATE_CLOSED": ("§gYa no opera§!", "§gNo longer working§!"),
 "MDR_PC_STATE_WAR": ("§REn guerra con su país§!", "§RAt war with its country§!"),
 "MDR_PC_NONE": ("§gNinguna§!", "§gNone§!"),
 "MDR_PC_PREV_TT": ("Empresa anterior de este servicio.", "Previous company for this service."),
 "MDR_PC_NEXT_TT": ("Empresa siguiente de este servicio.", "Next company for this service."),
 "MDR_PC_SIGN_TT": ("Contrata a esta empresa. Solo una por servicio: reemplaza a la anterior.", "Hires this company. Only one per service: it replaces the previous one."),
 "MDR_SPACE_SPEND_WHERE": ("Figura en §YEconomía§!, en Gastos adicionales.", "It shows in §YEconomy§!, under Additional expenses."),
 "MDR_SPACE_NAV_2": ("§YObjetivos§!", "§YGoals§!"), "MDR_SPACE_NAV_3": ("§YProyectos§!", "§YProjects§!"), "MDR_SPACE_NAV_4": ("§YAgencia y personal§!", "§YAgency and Staff§!"),
 "MDR_SPACE_NAV_6": ("§YSistema solar§!", "§YSolar System§!"), "MDR_SPACE_NAV_7": ("§YDecisiones§!", "§YDecisions§!"), "MDR_SPACE_NAV_8": ("§YColonias y carga§!", "§YColonies and Cargo§!"),
 "MDR_SPACE_BTN_START": ("Iniciar", "Start"), "MDR_SPACE_BTN_QUEUE": ("A la cola", "Queue"), "MDR_SPACE_BTN_UNQUEUE": ("Quitar", "Remove"), "MDR_SPACE_BTN_CLAIM": ("Reclamar", "Claim"),
 "MDR_SPACE_ST_DONE": ("§GHecho§!", "§GDone§!"), "MDR_SPACE_ST_QUEUED": ("§YEn cola§!: empieza cuando haya lugar y alcance", "§YQueued§!: starts when there is room and it can be paid"), "MDR_SPACE_ST_NO_SCIENCE": ("§RFalta ciencia§!", "§RNot enough science§!"), "MDR_SPACE_ST_NO_MONEY": ("§RFalta dinero§!", "§RNot enough money§!"), "MDR_SPACE_ST_READY": ("§GListo para iniciar§!", "§GReady to start§!"),
 "MDR_SPACE_GOAL_READY": ("§GCumplido: reclamá el premio§!", "§GAchieved: claim the reward§!"), "MDR_SPACE_BODY_ALL_DONE": ("§GYa hicimos todo lo posible acá.§!", "§GWe have done everything possible here.§!"), "MDR_SPACE_BODY_STEP_TITLE": ("§YPróximo paso:§!", "§YNext step:§!"), "MDR_SPACE_BODY_STEP": ("[mdr_space_body_step]", "[mdr_space_body_step]"),
 "MDR_SPACE_NEXT_STEP_TITLE": ("QUÉ HACER AHORA", "WHAT TO DO NOW"), "MDR_SPACE_NEXT_STEP": ("[mdr_space_next_step]", "[mdr_space_next_step]"),
 "MDR_SPACE_STEP_SITE": ("§RNo tenés cosmódromo.§! Construí uno en la pantalla de construcción, en Edificios estatales.", "§RYou have no spaceport.§! Build one from the construction screen, under state buildings."),
 "MDR_SPACE_STEP_BUDGET": ("§RPresupuesto en cero.§! Subilo en la página Finanzas: sin presupuesto no hay ciencia.", "§RThe budget is zero.§! Raise it on the Finance page: no budget, no science."),
 "MDR_SPACE_STEP_GOAL": ("§GHay un objetivo cumplido.§! Andá a Objetivos y reclamá el premio.", "§GA goal is achieved.§! Go to Goals and claim the reward."),
 "MDR_SPACE_STEP_IDLE": ("§YNada en marcha.§! Podés iniciar: §G[mdr_space_suggest]§!", "§YNothing running.§! You can start: §G[mdr_space_suggest]§!"),
 "MDR_SPACE_STEP_ROOM": ("§YQueda lugar§! para algo más a la vez. Podés iniciar: §G[mdr_space_suggest]§!", "§YThere is room§! for one more at a time. You can start: §G[mdr_space_suggest]§!"),
 "MDR_SPACE_SUGGEST_NONE": ("nada todavía: juntá ciencia o investigá en la pestaña Programa espacial", "nothing yet: gather science or research in the Space Programme tab"),
 "MDR_SPACE_GOALS_ALL_DONE": ("§GTodas las metas cumplidas§!", "§GAll goals achieved§!"),
 "MDR_SPACE_GOAL_TITLE": ("PRÓXIMA META", "NEXT GOAL"), "MDR_SPACE_GOAL_NAME": ("§Y[mdr_space_goal_now]§!", "§Y[mdr_space_goal_now]§!"), "MDR_SPACE_GOAL_STATUS": ("[mdr_space_goal_now_status]", "[mdr_space_goal_now_status]"),
 "MDR_SPACE_GO": ("Ir", "Go"), "MDR_SPACE_GO_TT": ("Te lleva a la página donde se hace esto.", "Takes you to the page where this is done."),
 "MDR_SPACE_GUIDE": ("Guía", "Guide"), "MDR_SPACE_GUIDE_TT": ("Cómo funciona el programa espacial, paso a paso.", "How the space programme works, step by step."),
 "MDR_SPACE_CHANCE": ("Éxito de lanzamiento: §Y[?mdr_space_chance_pct|0]%§!", "Launch success: §Y[?mdr_space_chance_pct|0]%§!"),
 "MDR_SPACE_GUIDE_INTRO": ("CÓMO FUNCIONA, EN 7 PASOS", "HOW IT WORKS, IN 7 STEPS"),
 "MDR_SPACE_G1": ("1. Poné presupuesto", "1. Set a budget"), "MDR_SPACE_G1_T": ("Sale de la economía cada semana y genera §Gciencia§!, la moneda del programa. En 2000 casi todos ponían entre 0,01% y 0,15% del PBI; arriba de 0,5% es una apuesta fuerte.", "It leaves the economy every week and makes §Gscience§!, the programme's currency. In 2000 almost everyone put between 0.01% and 0.15% of GDP; above 0.5% is a big bet."),
 "MDR_SPACE_G2": ("2. Construí cosmódromos", "2. Build spaceports"), "MDR_SPACE_G2_T": ("En la pantalla de construcción, Edificios estatales. Cada nivel da ciencia y mejora los lanzadores.", "In the construction screen, under state buildings. Each level gives science and improves launchers."),
 "MDR_SPACE_G3": ("3. Investigá", "3. Research"), "MDR_SPACE_G3_T": ("En la pantalla de investigación, pestaña Programa espacial. Cada investigación dice qué abre. Viajes espaciales abre los destinos.", "In the research screen, Space Programme tab. Each research says what it opens. Space Travel opens the destinations."),
 "MDR_SPACE_G4": ("4. Hacé proyectos", "4. Run projects"), "MDR_SPACE_G4_T": ("Mejoras permanentes que se pagan con ciencia y dinero. Solo se hacen unos pocos a la vez: el resto espera en la cola.", "Permanent upgrades paid with science and money. Only a few run at a time: the rest wait in the queue."),
 "MDR_SPACE_G5": ("5. Lanzá misiones", "5. Launch missions"), "MDR_SPACE_G5_T": ("Sondas, viajes tripulados y bases, en Decisiones. Pueden fallar. Primero sonda, después tripulación, después base.", "Probes, crewed journeys and bases, in Decisions. They can fail. First a probe, then a crew, then a base."),
 "MDR_SPACE_G6": ("6. Reclamá objetivos", "6. Claim goals"), "MDR_SPACE_G6_T": ("Al cumplir una meta, reclamala en Objetivos. El prestigio da estabilidad y poder político.", "When a goal is met, claim it in Goals. Prestige gives stability and political power."),
 "MDR_SPACE_G7": ("7. Cuidá las colonias", "7. Look after colonies"), "MDR_SPACE_G7_T": ("Las bases en la Luna y Marte abren colonias. Si faltan suministros, cae la moral y se pierden colonos.", "Bases on the Moon and Mars open colonies. If supplies run out, morale falls and settlers are lost."),
 "MDR_COL_NONE_MOON": ("§YLuna:§! [mdr_col_moon_step]", "§YMoon:§! [mdr_col_moon_step]"), "MDR_COL_NONE_MARS": ("§YMarte:§! [mdr_col_mars_step]", "§YMars:§! [mdr_col_mars_step]"),
 "MDR_SPACE_TIP_TECHS": ("Investigaciones terminadas de la pestaña Programa espacial. Se investigan en la pantalla de investigación.", "Researches finished in the Space Programme tab. They are done in the research screen."),
 "MDR_SPACE_TIP_SITES": ("Estados con cosmódromo. Se construyen en la pantalla de construcción, Edificios estatales, hasta 3 niveles por estado.", "States with a spaceport. They are built in the construction screen, under state buildings, up to 3 levels per state."),
 "MDR_SPACE_TIP_PCT": ("Parte del PBI que va al programa cada año. Se cambia en Finanzas.", "Share of GDP going to the programme each year. It is changed in Finance."),
 "MDR_SPACE_TIP_SCIENCE": ("Ciencia juntada. Paga los proyectos y las misiones. Sube cada semana por el presupuesto, los científicos, los cosmódromos y las colonias.", "Science gathered. It pays for projects and missions. It rises each week from the budget, scientists, spaceports and colonies."),
 "MDR_SPACE_TIP_BONUS": ("Velocidad de investigación que da el presupuesto, para todo el país.", "Research speed given by the budget, for the whole country."),
 "MDR_SPACE_TIP_PRESTIGE": ("Sube con objetivos y grandes misiones. Da estabilidad y poder político.", "It rises with goals and great missions. It gives stability and political power."),
 "MDR_SPACE_TIP_SCIENTISTS": ("Cada 50 científicos dan 0,2 de ciencia por semana y cobran $$0,001B.", "Every 50 scientists give 0.2 science a week and cost $$0.001B."),
 "MDR_SPACE_TIP_ENGINEERS": ("Cada 100 ingenieros acortan 5% los proyectos y misiones, y cobran $$0,002B por semana.", "Every 100 engineers shorten projects and missions by 5%, and cost $$0.002B a week."),
 "MDR_SPACE_TIP_ASTRONAUTS": ("Las misiones tripuladas piden un mínimo. Cada 2 astronautas cobran $$0,0008B por semana.", "Crewed missions need a minimum. Every 2 astronauts cost $$0.0008B a week."),
 "MDR_COL_TIP_POP": ("Cada colono da ciencia e investigación, y gasta suministros. Se envían con el botón de abajo.", "Each settler gives science and research, and uses supplies. They are sent with the button below."),
 "MDR_COL_TIP_MORALE": ("Baja si un suministro cae por debajo de 15. Por debajo de 25% se pierden colonos.", "It falls if a supply drops below 15. Below 25% settlers are lost."),
 "MDR_COL_GREENHOUSE_TT": ("§YInvernadero:§! 0,9 de comida por semana. Cuesta $$0,8B en la Luna y $$2,6B en Marte.", "§YGreenhouse:§! 0.9 food a week. Costs $$0.8B on the Moon and $$2.6B on Mars."),
 "MDR_COL_MINE_TT": ("§YMina de hielo:§! 0,8 de agua y de oxígeno por semana. Cuesta $$0,8B en la Luna y $$2,6B en Marte.", "§YIce mine:§! 0.8 water and oxygen a week. Costs $$0.8B on the Moon and $$2.6B on Mars."),
 "MDR_COL_REACTOR_TT": ("§YReactor:§! 1,1 de energía por semana. Cuesta $$0,8B en la Luna y $$2,6B en Marte.", "§YReactor:§! 1.1 energy a week. Costs $$0.8B on the Moon and $$2.6B on Mars."),
 "MDR_COL_WORKSHOP_TT": ("§YTaller:§! +0,3% de producción de fábricas militares. Cuesta $$0,8B en la Luna y $$2,6B en Marte.", "§YWorkshop:§! +0.3% military factory output. Costs $$0.8B on the Moon and $$2.6B on Mars."),
 "MDR_SPACE_TIP_FIELD": ("Escribí con tu teclado. Con las flechas moviste el cursor. Retroceso y Suprimir borran.", "Type on your keyboard. The arrows move the cursor. Backspace and Delete erase."),
 "MDR_SPACE_STEP_WAIT": ("§GTodo en marcha.§! Esperá a que terminen, o poné más en la cola.", "§GEverything is running.§! Wait for them to finish, or queue more."),
 "MDR_SPACE_TAB_1": ("Resumen", "Summary"), "MDR_SPACE_TAB_2": ("Objetivos", "Goals"), "MDR_SPACE_TAB_3": ("Proyectos", "Projects"), "MDR_SPACE_TAB_4": ("Agencia", "Agency"), "MDR_SPACE_TAB_5": ("Finanzas", "Finance"), "MDR_SPACE_TAB_6": ("Sistema solar", "Solar System"), "MDR_SPACE_TAB_7": ("Decisiones", "Decisions"), "MDR_SPACE_TAB_8": ("Colonias", "Colonies"),
 "MDR_SPACE_HELP_P": ("Mejoras permanentes: cuestan ciencia y dinero, y tardan semanas.", "Upgrades of the agency. They cost science and money, take weeks, and their effects stay for good."),
 "MDR_SPACE_HELP_D": ("Viajes y acuerdos. Los lanzamientos pueden fallar: §Y[?mdr_space_chance_pct|0]%§! de éxito.", "Journeys and accords. Launches can fail, and each row says what it still needs."),
 "MDR_SPACE_HELP_G": ("Metas nacionales. Se cumplen solas al lograr lo que piden: entonces reclamás el prestigio, que da estabilidad y poder político.", "National goals. They are met by achieving what they ask: then you claim the prestige, which gives stability and political power."),
 "MDR_SPACE_HELP_S": ("Hacé clic en un planeta para ver qué falta para llegar.", "Click a planet to see what is needed to get there."),
 "MDR_SPACE_HELP_C": ("Cada colono gasta suministros y da ciencia. Mantené las barras arriba con módulos o con una ruta de carga.", "Each settler uses supplies and gives science. Keep the bars up with modules or a cargo route."),
 "MDR_SPACE_HELP_A": ("Más personal da más ciencia y acorta los proyectos, pero cobra sueldo cada semana.", "More staff gives more science and shortens projects, but it is paid every week."), "MDR_SPACE_SLOTS": ("En curso: §Y[?mdr_space_active|0]/[?mdr_space_slots|0]§!", "Running: §Y[?mdr_space_active|0]/[?mdr_space_slots|0]§!"),
 "MDR_SPACE_SCIENCE_STOCK": ("Ciencia: §G[?mdr_space_science|0]§!", "Science: §G[?mdr_space_science|0]§!"),
 "MDR_SPACE_GOAL_PENDING": ("En curso", "In progress"), "MDR_SPACE_GOAL_DONE": ("§GCumplido§!", "§GAchieved§!"),
 "MDR_SPACE_HQ_TITLE": ("SEDE DE LA AGENCIA", "AGENCY HEADQUARTERS"), "MDR_SPACE_HQ_LEVEL": ("Nivel §Y[?mdr_space_hq|0]§! de 5", "Level §Y[?mdr_space_hq|0]§! of 5"),
 "MDR_SPACE_HQ_TEXT": ("Da proyectos a la vez en los niveles 3 y 5, y permite los más grandes.", "Gives more projects at a time at levels 3 and 5, and allows the largest ones."),
 "MDR_SPACE_HQ_UP": ("Ampliar sede", "Expand"), "MDR_SPACE_HQ_UP_TT": ("Cuesta §Y40§! de ciencia y §Y$$1,2B§! por cada nivel actual.", "Costs §Y40§! science and §Y$$1.2B§! per current level."),
 "MDR_SPACE_LBL_SCIENTISTS": ("Científicos", "Scientists"), "MDR_SPACE_LBL_ENGINEERS": ("Ingenieros", "Engineers"), "MDR_SPACE_LBL_ASTRONAUTS": ("Astronautas", "Astronauts"),
 "MDR_SPACE_VAL_SCIENTISTS": ("§Y[?mdr_space_scientists|0]§!", "§Y[?mdr_space_scientists|0]§!"), "MDR_SPACE_VAL_ENGINEERS": ("§Y[?mdr_space_engineers|0]§!", "§Y[?mdr_space_engineers|0]§!"), "MDR_SPACE_VAL_ASTRONAUTS": ("§Y[?mdr_space_astronauts|0]§!", "§Y[?mdr_space_astronauts|0]§!"),
 "MDR_SPACE_STAFF_TT": ("Científicos: dan ciencia por semana. Ingenieros: acortan los proyectos. Astronautas: los piden las misiones tripuladas. Todos cobran sueldo, que se suma al gasto del programa.", "Scientists give science each week. Engineers shorten projects. Astronauts are needed for crewed missions. All are paid, and that adds to the programme's expense."),
 "MDR_SPACE_SITES_TITLE": ("COSMÓDROMOS", "SPACEPORTS"), "MDR_SPACE_SITE_ENTRY": ("[THIS.GetName]: nivel §Y[?THIS.building_level@mdr_spaceport|0]§!", "[THIS.GetName]: level §Y[?THIS.building_level@mdr_spaceport|0]§!"),
 "MDR_SPACE_PRIVATE_TITLE": ("SECTOR PRIVADO", "PRIVATE SECTOR"), "MDR_SPACE_SIGN": ("Firmar", "Sign"), "MDR_SPACE_CANCEL": ("Cortar", "End"),
 "MDR_SPACE_DEBRIS": ("Basura orbital: §Y[?global.mdr_space_debris|0]§!/100", "Orbital debris: §Y[?global.mdr_space_debris|0]§!/100"),
 "MDR_SPACE_DEBRIS_TT": ("Afecta a todos: baja la fiabilidad y encarece los lanzadores. Crece sola, y sube mucho con los ensayos antisatélite. Se limpia con proyectos y acuerdos.", "It affects everyone: lowers reliability and makes launchers dearer. It grows by itself, and much more with anti-satellite tests. Projects and accords clean it."),
 "MDR_SPACE_SOLAR_NOTE": ("Esquema, no a escala.", "Schematic, not to scale."), "MDR_SPACE_BODY_NAME": ("[mdr_space_body_name]", "[mdr_space_body_name]"), "MDR_SPACE_BODY_TEXT": ("[mdr_space_body_text]", "[mdr_space_body_text]"), "MDR_SPACE_BODY_STATE": ("[mdr_space_body_state]", "[mdr_space_body_state]"),
 "MDR_SPACE_BODY_REACHED": ("§GYa llegamos.§!", "§GWe have reached it.§!"), "MDR_SPACE_BODY_HOME": ("§GNuestro hogar.§!", "§GOur home.§!"), "MDR_SPACE_BODY_UNREACHED": ("§RTodavía no llegamos.§!", "§RNot reached yet.§!"),
 "MDR_SPACE_GO_MISSIONS": ("Ver misiones", "Missions"), "MDR_SPACE_GO_COLONIES": ("Ver colonias", "Colonies"),
 "MDR_COL_MOON": ("Luna", "Moon"), "MDR_COL_MARS": ("Marte", "Mars"), "MDR_COL_NONE_TITLE": ("Todavía no hay colonias", "No colonies yet"), "MDR_COL_NONE_TEXT": ("Se fundan con la Base lunar y la Base marciana, en Decisiones. Primero hay que llegar con misiones tripuladas.", "They are founded with the Lunar Base and the Martian Base, in Decisions. Crewed missions must get there first."),
 "MDR_COL_POP": ("Colonos", "Settlers"), "MDR_COL_MORALE": ("Moral", "Morale"), "MDR_COL_SUPPLIES": ("SUMINISTROS", "SUPPLIES"), "MDR_COL_MODULES": ("MÓDULOS", "MODULES"), "MDR_COL_ROUTE": ("RUTA DE CARGA", "CARGO ROUTE"),
 "MDR_COL_WATER": ("Agua", "Water"), "MDR_COL_FOOD": ("Comida", "Food"), "MDR_COL_ENERGY": ("Energía", "Energy"), "MDR_COL_OXYGEN": ("Oxígeno", "Oxygen"),
 "MDR_COL_GREENHOUSE": ("Invernadero", "Greenhouse"), "MDR_COL_MINE": ("Minas de hielo", "Ice Mines"), "MDR_COL_REACTOR": ("Reactor", "Reactor"), "MDR_COL_WORKSHOP": ("Taller", "Workshop"),
 "MDR_COL_BUILD": ("Construir", "Build"), "MDR_COL_SEND": ("Enviar colonos", "Send Settlers"), "MDR_COL_ROUTE_ON": ("Abrir ruta", "Open Route"), "MDR_COL_ROUTE_OFF": ("Cerrar ruta", "Close Route"),
 "MDR_COL_BUILD_TT": ("Cuesta §Y$$0,8B§! en la Luna y §Y$$2,6B§! en Marte. Invernadero: comida. Minas: agua y oxígeno. Reactor: energía. Taller: más fábricas militares.", "Costs §Y$$0.8B§! on the Moon and §Y$$2.6B§! on Mars. Greenhouse: food. Mines: water and oxygen. Reactor: energy. Workshop: more military factories."),
 "MDR_COL_SEND_TT": ("4 colonos más: §Y$$0,4B§! a la Luna y §Y$$1,4B§! a Marte. Cada uno consume suministros y da ciencia e investigación.", "4 more settlers: §Y$$0.4B§! to the Moon and §Y$$1.4B§! to Mars. Each uses supplies and gives science and research."),
 "MDR_COL_ROUTE_TT": ("Lleva 6 de cada suministro por semana. Cuesta §Y$$0,09B§! por semana a la Luna y §Y$$0,34B§! a Marte.", "Carries 6 of each supply a week. Costs §Y$$0.09B§! a week to the Moon and §Y$$0.34B§! to Mars."),
 "MDR_SPACE_SITE_MAPICON_TT": ("§YCosmódromo§! en [FROM.GetName]\\nNivel: §Y[?FROM.building_level@mdr_spaceport|0]§!", "§YSpaceport§! in [FROM.GetName]\\nLevel: §Y[?FROM.building_level@mdr_spaceport|0]§!"),
 "mdr_space_program_modifier": ("Programa espacial: proyectos", "Space Programme: Projects"), "mdr_space_standing_modifier": ("Programa espacial: prestigio y colonias", "Space Programme: Prestige and Colonies"),
 "mdr_space.1.t": ("Misión cumplida: [mdr_space_last_name]", "Mission Accomplished: [mdr_space_last_name]"), "mdr_space.1.d": ("La agencia terminó [mdr_space_last_name]. Sus efectos ya rigen, y el programa puede seguir adelante.", "The agency has finished [mdr_space_last_name]. Its effects now apply, and the programme can move on."), "mdr_space.1.a": ("Seguimos adelante.", "Onward."),
 "mdr_space.2.t": ("Falla en el lanzamiento", "Launch Failure"), "mdr_space.2.d": ("El lanzamiento de [mdr_space_last_name] falló y se perdió lo invertido. Se puede volver a intentar.", "The launch of [mdr_space_last_name] failed and the investment was lost. It can be tried again."), "mdr_space.2.a": ("Volveremos a intentarlo.", "We will try again."),
 "mdr_space.3.t": ("La órbita baja se llena de basura", "Low Orbit Fills with Debris"), "mdr_space.3.d": ("Los choques entre restos ya amenazan a todos los satélites. Lanzar sale más caro y es más riesgoso, hasta que alguien limpie.", "Collisions between debris now threaten every satellite. Launching costs more and is riskier, until someone cleans it up."), "mdr_space.3.a": ("Habrá que hacer algo.", "Something must be done."),
 "mdr_space.4.t": ("Faltan suministros en la colonia", "Colony Short of Supplies"), "mdr_space.4.d": ("Una de nuestras colonias se está quedando sin suministros. Si no llegan pronto, la moral caerá y perderemos colonos.", "One of our colonies is running out of supplies. If they do not arrive soon, morale will fall and we will lose settlers."), "mdr_space.4.a": ("Hay que enviar ayuda.", "Help must be sent."),
}


def write_loc():
    for idx, lang in enumerate(("spanish", "english")):
        y = f"l_{lang}:\n"
        for key, values in STATIC.items():
            y += f' {key}: "{values[idx]}"\n'
        for r in all_reqs():
            y += f' {req_key(r)}: "§R{"Falta" if idx == 0 else "Missing"}:§! {req_loc(r, lang)}"\n'
            y += f' {req_key(r).replace("MDR_RQ", "MDR_RK")}: "§G{"Listo" if idx == 0 else "Done"}:§! {req_loc(r, lang)}"\n'
        for a, _ in ACTIONS:
            n = a[0].upper()
            reqs = ", ".join(req_loc(r, lang) for r in a[9])
            sci_word, wk = ("ciencia", "sem.") if idx == 0 else ("science", "wk.")
            y += f' MDR_SA_{n}: "{a[2 + idx]}"\n MDR_SA_{n}_DESC: "{a[4 + idx]}"\n'
            y += f' MDR_SA_{n}_COST: "§G{a[6]}§! {sci_word} · §Y$${number(a[7], lang)}B§!\\n{a[8]} {wk}"\n'
            lines = "\\n".join(f"[{req_key(r).lower()}]" for r in a[9])
            roll = ""
            if _ == "m" and a[1] in ROLLED:
                roll = "\\n\\n" + ("§YEs un lanzamiento:§! puede fallar. Éxito actual: §Y[?mdr_space_chance_pct|0]%§!. Si falla, se pierde lo pagado." if idx == 0 else "§YIt is a launch:§! it can fail. Current success: §Y[?mdr_space_chance_pct|0]%§!. If it fails, what was paid is lost.")
            y += f' MDR_SA_{n}_TT: "{a[4 + idx]}\\n\\n§Y{"Costo" if idx == 0 else "Cost"}:§! {a[6]} {sci_word}, $${number(a[7], lang)}B, {a[8]} {"semanas" if idx == 0 else "weeks"}.\\n§Y{"Tenés" if idx == 0 else "You have"}:§! [?mdr_space_science|0] {sci_word}, $$[?treasury|1]B.\\n\\n§Y{"Requisitos" if idx == 0 else "Requirements"}:§!\\n{lines}{roll}"\n'
        for g in GOALS:
            n = g[0].upper()
            y += f' MDR_SG_{n}: "{g[1 + idx]}"\n MDR_SG_{n}_DESC: "{g[3 + idx]}"\n MDR_SG_{n}_REWARD: "{"Prestigio" if idx == 0 else "Prestige"} §G+{g[6]}§!"\n'
        for i, c in enumerate(CATS_P):
            y += f' MDR_SPACE_CAT_P{i + 1}: "{c[1 + idx]}"\n'
        for i, c in enumerate(CATS_D):
            y += f' MDR_SPACE_CAT_D{i + 1}: "{c[1 + idx]}"\n'
        for b in BODIES:
            n = b[0].upper()
            y += f' MDR_SPACE_BODY_{n}: "{b[4 + idx]}"\n MDR_SPACE_BODY_{n}_TEXT: "{b[6 + idx]}"\n'
        es = idx == 0
        week = "sem" if es else "wk"
        for key, label_es, label_en in SERVICES:
            K = key.upper()
            y += f' MDR_PC_SERVICE_{K}: "{(label_es if es else label_en).upper()}"\n'
            for part in ("view_name", "view_info", "view_tt", "view_state", "signed_name", "signed_cost"):
                y += f' MDR_PC_{K}_{part.upper()}: "[mdr_pc_{key}_{part}]"\n'
        for c in COMPANIES:
            N, cost = c[0].upper(), number(c[8], lang)
            since = f"{c[3]}-{c[4]}" if c[4] else str(c[3])
            effects = company_effects_text(c, lang)
            y += f' MDR_PCO_{N}: "{c[5]}"\n'
            y += f' MDR_PCO_{N}_INFO: "[{c[2]}.GetName], {since}: §G{effects}§!"\n'
            y += f' MDR_PCO_{N}_TT: "§Y{c[5]}§! ([{c[2]}.GetName], {since})\\n{c[6 + idx]}\\n\\n§G{effects[0].upper() + effects[1:]}.§!\\n{"Cuesta" if es else "Costs"} §Y$${cost}B§! {"por semana" if es else "a week"}. {"Se corta solo si entramos en guerra con" if es else "It ends by itself if we go to war with"} [{c[2]}.GetName]."\n'
            y += f' MDR_PCO_{N}_ON: "{"§GFirmado§!" if es else "§GSigned§!"}: §R$${cost}B§!/{week}"\n'
            y += f' MDR_PCO_{N}_FREE: "{"§YDisponible§!" if es else "§YAvailable§!"}: $${cost}B/{week}"\n'
            y += f' MDR_PCO_{N}_SOON: "§g{"Desde" if es else "From"} {c[3]}§!"\n'
            y += f' MDR_PCO_{N}_COST: "§R$${cost}B§!/{week}"\n'
        with open(f"localisation/{lang}/mdr_space_program_l_{lang}.yml", "wb") as f:
            f.write(b"\xef\xbb\xbf" + y.encode("utf-8"))


# ---- Windows. The helpers come from make_space_gui.py.
def goto(page_var, value):
    return f"set_variable = {{ {page_var} = {value} }}\n\t\t\t\tmdr_space_refresh = yes"


def action_rows(rows, text, panel, button, picture=None, icon=None, row_h=54, top=212):
    c, eff, trig = "", "", ""
    for i, a in enumerate(rows):
        name, N = a[0], a[0].upper()
        y = top + i * row_h
        c += panel(f"mdr_sa_{name}_row", 16, y, 748, row_h - 4)
        if picture and icon:
            c += picture(f"mdr_sa_{name}_icon", f"GFX_mdr_space_icon_{icon}", 26, y + 11)
        c += text(f"mdr_sa_{name}_name", 62, y + 6, 400, 18, "hoi_18mbs", f"MDR_SA_{N}", "left", f"MDR_SA_{N}_TT") + text(f"mdr_sa_{name}_status", 62, y + 27, 440, 18, "hoi_16mbs", f"MDR_SA_{N}_STATUS", "left", f"MDR_SA_{N}_TT")
        c += text(f"mdr_sa_{name}_cost", 470, y + 8, 192, 36, "hoi_16mbs", f"MDR_SA_{N}_COST", "right")
        for kind, key in (("start", "MDR_SPACE_BTN_START"), ("queue", "MDR_SPACE_BTN_QUEUE"), ("unqueue", "MDR_SPACE_BTN_UNQUEUE")):
            c += button(f"mdr_sa_{name}_{kind}", 672, y + 12, "GFX_mdr_space_btn_71x26", key, f"MDR_SA_{N}_TT")
        eff += f"\t\t\tmdr_sa_{name}_start_click = {{\n\t\t\t\tmdr_sa_{name}_begin = yes\n\t\t\t}}\n"
        eff += f"\t\t\tmdr_sa_{name}_queue_click = {{\n\t\t\t\tset_country_flag = mdr_sa_{name}_queued\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n"
        eff += f"\t\t\tmdr_sa_{name}_unqueue_click = {{\n\t\t\t\tclr_country_flag = mdr_sa_{name}_queued\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n"
        idle = f"NOT = {{ has_country_flag = mdr_sa_{name}_done has_country_flag = mdr_sa_{name}_run has_country_flag = mdr_sa_{name}_queued }}"
        free = "check_variable = { var = mdr_space_active compare = less_than value = mdr_space_slots }"
        trig += f"\t\t\tmdr_sa_{name}_start_visible = {{ {idle} {free} }}\n\t\t\tmdr_sa_{name}_start_click_enabled = {{ mdr_sa_{name}_can = yes }}\n"
        trig += f"\t\t\tmdr_sa_{name}_queue_visible = {{ {idle} NOT = {{ {free} }} }}\n\t\t\tmdr_sa_{name}_queue_click_enabled = {{ mdr_sa_{name}_reqs = yes }}\n"
        trig += f"\t\t\tmdr_sa_{name}_unqueue_visible = {{ has_country_flag = mdr_sa_{name}_queued }}\n"
    return c, eff, trig


def pages(text, panel, picture, button, section, tile, carrier):
    """Name of each window: (content, effects, triggers, visible)."""
    out = {}
    # Projects and missions, a window per category.
    for short, table, cats, var, page, help_key in (("p", PROJECTS, CATS_P, "mdr_space_cat_p", 3, "MDR_SPACE_HELP_P"), ("d", MISSIONS, CATS_D, "mdr_space_cat_d", 7, "MDR_SPACE_HELP_D")):
        for k in range(1, len(cats) + 1):
            c, eff, trig = text("mdr_space_help", 18, 124, 520, 20, "hoi_16mbs", help_key), "", ""
            c += text("mdr_space_slots", 550, 124, 214, 18, "hoi_16mbs", "MDR_SPACE_SLOTS", "right")
            y = 148
            for j, cat in enumerate(cats):
                count = len([a for a in table if a[1] == j + 1])
                c += f'\t\tbuttonType = {{ name = "mdr_space_cat_{j + 1}" position = {{ x = 16 y = {y} }} quadTextureSprite = "GFX_mdr_space_banner_{short}{j + 1}" pdx_tooltip = "MDR_SPACE_CAT_{short.upper()}{j + 1}" clicksound = click_checkbox }}\n'
                if j + 1 == k:
                    c += picture(f"mdr_space_cat_sel", "GFX_mdr_space_banner_sel", 16, y)
                c += text(f"mdr_space_cat_label_{j + 1}", 30, y + 8, 300, 20, "hoi_18mbs", f"MDR_SPACE_CAT_{short.upper()}{j + 1}")
                c += text(f"mdr_space_cat_count_{j + 1}", 560, y + 9, 190, 18, "hoi_16mbs", f"MDR_SPACE_CAT_COUNT_{'OPEN' if j + 1 == k else 'SHUT'}_{count}", "right")
                eff += f"\t\t\tmdr_space_cat_{j + 1}_click = {{\n\t\t\t\t{goto(var, j + 1)}\n\t\t\t}}\n"
                y += 38
                if j + 1 == k:
                    rows = [a for a in table if a[1] == k]
                    rc, re_, rt = action_rows(rows, text, panel, button, picture, cat[0], top=y)
                    c, eff, trig = c + rc, eff + re_, trig + rt
                    y += len(rows) * 54 + 4
            out[f"{short}{k}"] = (c, eff, trig, f"check_variable = {{ mdr_space_tier > 0 }} check_variable = {{ mdr_space_page = {page} }} check_variable = {{ {var} = {k} }}")
    # Goals.
    c, eff, trig = text("mdr_space_help", 18, 124, 744, 36, "hoi_16mbs", "MDR_SPACE_HELP_G"), "", ""
    # Cards in two columns: picture, name, what it asks, its state, the reward and the claim button.
    for i, g in enumerate(GOALS):
        name, N = g[0], g[0].upper()
        x, y = 16 + i % 2 * 378, 164 + i // 2 * 132
        c += panel(f"mdr_sg_{name}_row", x, y, 370, 128) + picture(f"mdr_sg_{name}_picture", f"GFX_mdr_space_goal_{i}", x + 8, y + 8)
        c += text(f"mdr_sg_{name}_name", x + 150, y + 10, 210, 20, "hoi_18mbs", f"MDR_SG_{N}") + text(f"mdr_sg_{name}_desc", x + 150, y + 34, 210, 36, "hoi_16mbs", f"MDR_SG_{N}_DESC") + text(f"mdr_sg_{name}_status", x + 150, y + 72, 210, 18, "hoi_16mbs", f"MDR_SG_{N}_STATUS")
        c += text(f"mdr_sg_{name}_reward", x + 150, y + 100, 120, 18, "hoi_16mbs", f"MDR_SG_{N}_REWARD")
        c += button(f"mdr_sg_{name}_claim", x + 290, y + 94, "GFX_mdr_space_btn_71x26", "MDR_SPACE_BTN_CLAIM")
        eff += f"\t\t\tmdr_sg_{name}_claim_click = {{\n\t\t\t\tset_country_flag = mdr_sg_{name}_claimed\n\t\t\t\tadd_to_variable = {{ mdr_space_prestige = {g[6]} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}}\n"
        trig += f"\t\t\tmdr_sg_{name}_claim_visible = {{ mdr_sg_{name}_met = yes NOT = {{ has_country_flag = mdr_sg_{name}_claimed }} }}\n"
    out["goals"] = (c, eff, trig, "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 2 }")
    # Agency and staff.
    c = picture("mdr_space_hero", "GFX_mdr_space_hero", 16, 124)
    c += text("mdr_space_hq_title", 32, 140, 480, 20, "hoi_16mbs", "MDR_SPACE_HQ_TITLE") + text("mdr_space_hq_level", 32, 164, 480, 30, "hoi_24header", "MDR_SPACE_HQ_LEVEL") + text("mdr_space_hq_text", 32, 202, 520, 40, "hoi_16mbs", "MDR_SPACE_HQ_TEXT")
    c += button("mdr_space_hq_up", 610, 172, "GFX_mdr_space_btn_123x34", "MDR_SPACE_HQ_UP", "MDR_SPACE_HQ_UP_TT")
    eff = "\t\t\tmdr_space_hq_up_click = {\n\t\t\t\tmdr_space_upgrade_hq = yes\n\t\t\t}\n"
    trig = "\t\t\tmdr_space_hq_up_click_enabled = {\n\t\t\t\tcheck_variable = { mdr_space_hq < 5 }\n\t\t\t\tcheck_variable = { var = mdr_space_science compare = greater_than_or_equals value = mdr_space_hq_science_cost }\n\t\t\t\tcheck_variable = { var = treasury compare = greater_than value = mdr_space_hq_money_cost }\n\t\t\t}\n"
    c += text("mdr_space_help", 18, 262, 744, 20, "hoi_16mbs", "MDR_SPACE_HELP_A")
    for i, (key, var, step, icon) in enumerate((("SCIENTISTS", "mdr_space_scientists", 50, "atom"), ("ENGINEERS", "mdr_space_engineers", 100, "projects"), ("ASTRONAUTS", "mdr_space_astronauts", 2, "staff"))):
        x = 16 + i * 251
        c += tile(f"mdr_space_staff_{i}", x, 286, 246, icon, f"MDR_SPACE_LBL_{key}", f"MDR_SPACE_VAL_{key}", f"MDR_SPACE_TIP_{key}")
        c += button(f"mdr_space_staff_{i}_less", x + 44, 318, "GFX_small_minus_button", "MDR_SPACE_EMPTY", f"MDR_SPACE_TIP_{key}") + button(f"mdr_space_staff_{i}_more", x + 182, 318, "GFX_small_plus_button", "MDR_SPACE_EMPTY", f"MDR_SPACE_TIP_{key}")
        eff += f"\t\t\tmdr_space_staff_{i}_more_click = {{\n\t\t\t\tadd_to_variable = {{ {var} = {step} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n"
        eff += f"\t\t\tmdr_space_staff_{i}_less_click = {{\n\t\t\t\tadd_to_variable = {{ {var} = -{step} }}\n\t\t\t\tif = {{ limit = {{ check_variable = {{ {var} < 0 }} }} set_variable = {{ {var} = 0 }} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n"
    c += panel("mdr_space_sites_panel", 16, 378, 300, 322) + section("mdr_space_sites_title", 30, 388, "MDR_SPACE_SITES_TITLE")
    c += '\t\tgridboxtype = {\n\t\t\tname = "mdr_space_site_list"\n\t\t\tposition = { x = 30 y = 418 }\n\t\t\tsize = { width = 272 height = 230 }\n\t\t\tslotsize = { width = 272 height = 22 }\n\t\t\tmax_slots_horizontal = 1\n\t\t\tformat = "UPPER_LEFT"\n\t\t}\n'
    c += text("mdr_space_debris", 30, 668, 272, 20, "hoi_16mbs", "MDR_SPACE_DEBRIS", "left")
    c += panel("mdr_space_private_panel", 322, 378, 442, 322) + section("mdr_space_private_title", 336, 388, "MDR_SPACE_PRIVATE_TITLE")
    # One row per service: arrows to go through its companies, and the one shown can be hired.
    for i, (n, _, _) in enumerate(SERVICES):
        N, count, y = n.upper(), len(companies_of(n)), 418 + i * 68
        view, signed = f"mdr_pc_{n}_view", f"mdr_pc_{n}_signed"
        c += text(f"mdr_pc_{n}_service", 336, y, 200, 18, "hoi_16mbs", f"MDR_PC_SERVICE_{N}") + text(f"mdr_pc_{n}_state", 500, y, 250, 18, "hoi_16mbs", f"MDR_PC_{N}_VIEW_STATE", "right")
        c += f'\t\tbuttonType = {{ name = "mdr_pc_{n}_prev" position = {{ x = 336 y = {y + 20} }} quadTextureSprite = "GFX_mdr_space_arrow_left" pdx_tooltip = "MDR_PC_PREV_TT" clicksound = click_default }}\n'
        c += text(f"mdr_pc_{n}_name", 364, y + 22, 280, 20, "hoi_18mbs", f"MDR_PC_{N}_VIEW_NAME", "left", f"MDR_PC_{N}_VIEW_TT")
        c += f'\t\tbuttonType = {{ name = "mdr_pc_{n}_next" position = {{ x = 646 y = {y + 20} }} quadTextureSprite = "GFX_mdr_space_arrow_right" pdx_tooltip = "MDR_PC_NEXT_TT" clicksound = click_default }}\n'
        c += button(f"mdr_pc_{n}_on", 680, y + 18, "GFX_mdr_space_btn_71x26", "MDR_SPACE_SIGN", "MDR_PC_SIGN_TT") + button(f"mdr_pc_{n}_off", 680, y + 18, "GFX_mdr_space_btn_71x26", "MDR_SPACE_CANCEL")
        c += text(f"mdr_pc_{n}_info", 336, y + 44, 414, 18, "hoi_16mbs", f"MDR_PC_{N}_VIEW_INFO", "left", f"MDR_PC_{N}_VIEW_TT")
        redraw = "\t\t\t\tadd_to_variable = { global.international_systems_updated = 1 }\n"
        eff += f"\t\t\tmdr_pc_{n}_prev_click = {{\n\t\t\t\tadd_to_variable = {{ {view} = -1 }}\n\t\t\t\tif = {{ limit = {{ check_variable = {{ {view} < 1 }} }} set_variable = {{ {view} = {count} }} }}\n{redraw}\t\t\t}}\n"
        eff += f"\t\t\tmdr_pc_{n}_next_click = {{\n\t\t\t\tadd_to_variable = {{ {view} = 1 }}\n\t\t\t\tif = {{ limit = {{ check_variable = {{ {view} > {count} }} }} set_variable = {{ {view} = 1 }} }}\n{redraw}\t\t\t}}\n"
        eff += f"\t\t\tmdr_pc_{n}_on_click = {{\n\t\t\t\tset_variable = {{ {signed} = {view} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n\t\t\tmdr_pc_{n}_off_click = {{\n\t\t\t\tset_variable = {{ {signed} = 0 }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n"
        same = f"check_variable = {{ var = {signed} compare = equals value = {view} }}"
        trig += f"\t\t\tmdr_pc_{n}_on_visible = {{ NOT = {{ {same} }} }}\n\t\t\tmdr_pc_{n}_on_click_enabled = {{ mdr_pc_{n}_view_open = yes }}\n\t\t\tmdr_pc_{n}_off_visible = {{ {same} check_variable = {{ {signed} > 0 }} }}\n"
    out["agency"] = (c, eff, trig, "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 4 }")
    # Solar system.
    # Map on the left, the chosen body's card on the right.
    c = picture("mdr_space_solar_map", "GFX_mdr_space_solar_map", 16, 124) + panel("mdr_space_body_panel", 510, 124, 254, 576)
    eff, trig = "", ""
    for i, b in enumerate(BODIES):
        n, size = b[0], b[3]
        x, y = SOLAR_POS[n]
        c += f'\t\tbuttonType = {{ name = "mdr_space_body_{i + 1}" position = {{ x = {16 + x - size // 2} y = {124 + y - size // 2} }} quadTextureSprite = "GFX_mdr_space_planet_{n}" pdx_tooltip = "MDR_SPACE_BODY_{n.upper()}" clicksound = click_default }}\n'
        c += f'\t\ticonType = {{ name = "mdr_space_body_ring_{i + 1}" spriteType = "GFX_mdr_space_ring_{size + 10}" position = {{ x = {16 + x - (size + 10) // 2} y = {124 + y - (size + 10) // 2} }} alwaystransparent = yes }}\n'
        c += text(f"mdr_space_body_label_{i + 1}", 16 + x - 45, 124 + y + size // 2 + 4, 90, 18, "hoi_16mbs", f"MDR_SPACE_BODY_{n.upper()}", "center")
        c += picture(f"mdr_space_body_photo_{i + 1}", b[9], 528, 140)
        eff += f"\t\t\tmdr_space_body_{i + 1}_click = {{\n\t\t\t\tset_variable = {{ mdr_space_body = {i + 1} }}\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n"
        trig += f"\t\t\tmdr_space_body_ring_{i + 1}_visible = {{ check_variable = {{ mdr_space_body = {i + 1} }} }}\n\t\t\tmdr_space_body_photo_{i + 1}_visible = {{ check_variable = {{ mdr_space_body = {i + 1} }} }}\n"
    c += text("mdr_space_help", 30, 132, 440, 18, "hoi_16mbs", "MDR_SPACE_HELP_S") + text("mdr_space_solar_note", 290, 676, 200, 18, "hoi_16mbs", "MDR_SPACE_SOLAR_NOTE", "right")
    c += text("mdr_space_body_name", 528, 316, 220, 30, "hoi_24header", "MDR_SPACE_BODY_NAME") + text("mdr_space_body_text", 528, 352, 220, 76, "hoi_16mbs", "MDR_SPACE_BODY_TEXT") + text("mdr_space_body_state", 528, 434, 220, 40, "hoi_16mbs", "MDR_SPACE_BODY_STATE")
    c += section("mdr_space_body_step_title", 528, 484, "MDR_SPACE_BODY_STEP_TITLE") + text("mdr_space_body_step", 528, 512, 220, 60, "hoi_16mbs", "MDR_SPACE_BODY_STEP")
    c += button("mdr_space_go_missions", 528, 600, "GFX_mdr_space_btn_123x34", "MDR_SPACE_GO_MISSIONS") + button("mdr_space_go_colonies", 528, 642, "GFX_mdr_space_btn_123x34", "MDR_SPACE_GO_COLONIES")
    eff += "\t\t\tmdr_space_go_missions_click = {\n\t\t\t\tset_variable = { mdr_space_page = 7 }\n\t\t\t\tset_variable = { mdr_space_cat_d = 1 }\n\t\t\t\tif = { limit = { check_variable = { mdr_space_body = 4 } } set_variable = { mdr_space_cat_d = 3 } }\n\t\t\t\tif = { limit = { check_variable = { mdr_space_body = 5 } } set_variable = { mdr_space_cat_d = 4 } }\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}\n"
    eff += "\t\t\tmdr_space_go_colonies_click = {\n\t\t\t\tset_variable = { mdr_space_page = 8 }\n\t\t\t\tif = { limit = { check_variable = { mdr_space_body = 5 } } set_variable = { mdr_space_colony_view = 2 } }\n\t\t\t\telse = { set_variable = { mdr_space_colony_view = 1 } }\n" + "".join(f"\t\t\t\tif = {{ limit = {{ check_variable = {{ mdr_space_body = {c[4]} }} has_country_flag = mdr_col_{c[0]} }} set_country_flag = mdr_{c[0]}_open }}\n" for c in COLONY_KEYS) + "\t\t\t\tmdr_space_refresh = yes\n\t\t\t}\n"
    trig += "\t\t\tmdr_space_go_colonies_visible = { OR = { " + " ".join(f"AND = {{ check_variable = {{ mdr_space_body = {c[4]} }} has_country_flag = mdr_col_{c[0]} }}" for c in COLONY_KEYS) + " } }\n"
    out["solar"] = (c, eff, trig, "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 6 }")
    # Colonies.
    for view, b, build, N in ((1, "moon", 0.8, "MOON"), (2, "mars", 2.6, "MARS")):
        p = f"mdr_col_{b}"
        tabs, eff = text("mdr_space_help", 18, 124, 744, 20, "hoi_16mbs", "MDR_SPACE_HELP_C"), ""
        # Moon and Mars as two picture banners side by side, like the categories of Projects.
        for j, nm in enumerate(("MOON", "MARS")):
            x = 16 + j * 378
            tabs += f'\t\tbuttonType = {{ name = "mdr_col_tab_{j + 1}" position = {{ x = {x} y = 146 }} quadTextureSprite = "GFX_mdr_space_banner_col{j + 1}" pdx_tooltip = "MDR_COL_{nm}" clicksound = click_checkbox }}\n'
            if j + 1 == view:
                tabs += picture("mdr_col_tab_sel", "GFX_mdr_space_banner_col_sel", x, 146)
            tabs += text(f"mdr_col_tab_label_{j + 1}", x + 16, 164, 200, 22, "hoi_24header", f"MDR_COL_{nm}")
            extra = f"\t\t\t\tif = {{ limit = {{ has_country_flag = mdr_col_{nm.lower()} }} set_country_flag = mdr_{nm.lower()}_open }}\n"
            eff += f"\t\t\tmdr_col_tab_{j + 1}_click = {{\n{extra}\t\t\t\t{goto('mdr_space_colony_view', j + 1)}\n\t\t\t}}\n"
        c = tabs
        if b in ("moon", "mars"):
            # The Martian colony lives in its own window (herramientas/space_colony.py); this page opens it.
            c += panel("mdr_col_mars_link_panel", 16, 212, 748, 160) + text("mdr_col_mars_link_text", 32, 228, 716, 60, "hoi_18mbs", "MDR_MARS_LINK_TEXT")
            c += button("mdr_col_mars_link", 32, 310, "GFX_mdr_space_btn_123x34", f"MDR_{b.upper()}_OPEN", f"MDR_{b.upper()}_OPEN_TT")
            eff += f"\t\t\tmdr_col_mars_link_click = {{\n\t\t\t\tset_country_flag = mdr_{b}_open\n\t\t\t\tadd_to_variable = {{ global.international_systems_updated = 1 }}\n\t\t\t}}\n"
            out[f"colony_{b}"] = (c, eff, "", f"check_variable = {{ mdr_space_tier > 0 }} check_variable = {{ mdr_space_page = 8 }} check_variable = {{ mdr_space_colony_view = {view} }} has_country_flag = {p}")
            continue
        c += tile("mdr_col_pop_t", 16, 212, 370, "staff", "MDR_COL_POP", f"MDR_COL_{N}_POP", "MDR_COL_TIP_POP") + tile("mdr_col_morale_t", 394, 212, 370, "goals", "MDR_COL_MORALE", f"MDR_COL_{N}_MORALE", "MDR_COL_TIP_MORALE")
        c += panel("mdr_col_sup_panel", 16, 304, 370, 210) + section("mdr_col_sup_title", 30, 314, "MDR_COL_SUPPLIES")
        properties = ""
        for i, (x_, key) in enumerate(zip(SUPPLIES, ("WATER", "FOOD", "ENERGY", "OXYGEN"))):
            y = 350 + i * 38
            c += text(f"mdr_col_{x_}_label", 30, y, 90, 18, "hoi_16mbs", f"MDR_COL_{key}") + picture(f"mdr_col_{x_}_bar", "GFX_mdr_space_meter", 128, y + 2) + text(f"mdr_col_{x_}_value", 298, y, 70, 18, "hoi_16mbs", f"MDR_COL_{N}_{key}_V", "right")
            properties += f"\t\t\tmdr_col_{x_}_bar = {{\n\t\t\t\tframe = {p}_{x_}_frame\n\t\t\t}}\n"
        trig_build = ""
        c += panel("mdr_col_mod_panel", 394, 304, 370, 210) + section("mdr_col_mod_title", 408, 314, "MDR_COL_MODULES")
        for i, (m, key) in enumerate(zip(("greenhouse", "mine", "reactor", "workshop"), ("GREENHOUSE", "MINE", "REACTOR", "WORKSHOP"))):
            y = 346 + i * 40
            c += text(f"mdr_col_{m}_label", 408, y + 4, 260, 18, "hoi_16mbs", f"MDR_COL_{N}_{key}") + button(f"mdr_col_{m}_build", 680, y, "GFX_mdr_space_btn_71x26", "MDR_COL_BUILD", f"MDR_COL_{key}_TT")
            trig_build = trig_build + f"\t\t\tmdr_col_{m}_build_click_enabled = {{ check_variable = {{ treasury > {build} }} }}\n"
            eff += f"\t\t\tmdr_col_{m}_build_click = {{\n\t\t\t\tadd_to_variable = {{ {p}_{m} = 1 }}\n\t\t\t\tset_temp_variable = {{ treasury_change = -{build} }}\n\t\t\t\tsubtract_from_variable = {{ mdr_space_spend_0 = treasury_change }}\n\t\t\t\tmodify_treasury_effect = yes\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}}\n"
        c += panel("mdr_col_route_panel", 16, 520, 748, 180) + section("mdr_col_route_title", 30, 530, "MDR_COL_ROUTE")
        c += text("mdr_col_route_state", 30, 562, 716, 40, "hoi_16mbs", "MDR_COL_ROUTE_TT")
        c += button("mdr_col_route_on", 30, 620, "GFX_mdr_space_btn_123x34", "MDR_COL_ROUTE_ON", "MDR_COL_ROUTE_TT") + button("mdr_col_route_off", 30, 620, "GFX_mdr_space_btn_123x34", "MDR_COL_ROUTE_OFF", "MDR_COL_ROUTE_TT") + button("mdr_col_send", 170, 620, "GFX_mdr_space_btn_123x34", "MDR_COL_SEND", "MDR_COL_SEND_TT")
        eff += f"\t\t\tmdr_col_route_on_click = {{\n\t\t\t\tset_country_flag = {p}_route\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n\t\t\tmdr_col_route_off_click = {{\n\t\t\t\tclr_country_flag = {p}_route\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t\tingame_update_setup = yes\n\t\t\t}}\n\t\t\tmdr_col_send_click = {{\n\t\t\t\t{p}_send = yes\n\t\t\t}}\n"
        trig = f"\t\t\tmdr_col_route_on_visible = {{ NOT = {{ has_country_flag = {p}_route }} }}\n\t\t\tmdr_col_route_off_visible = {{ has_country_flag = {p}_route }}\n\t\t\tmdr_col_send_click_enabled = {{ check_variable = {{ var = {p}_pop compare = less_than value = {p}_cap }} }}\n" + trig_build
        out[f"colony_{b}"] = (c, eff, trig, f"check_variable = {{ mdr_space_tier > 0 }} check_variable = {{ mdr_space_page = 8 }} check_variable = {{ mdr_space_colony_view = {view} }} has_country_flag = {p}", properties)
    c = panel("mdr_col_none_panel", 16, 124, 748, 200) + text("mdr_col_none_title", 32, 142, 700, 30, "hoi_24header", "MDR_COL_NONE_TITLE") + text("mdr_col_none_text", 32, 182, 700, 44, "hoi_18mbs", "MDR_COL_NONE_TEXT")
    c += text("mdr_col_none_moon", 32, 240, 700, 24, "hoi_18mbs", "MDR_COL_NONE_MOON") + text("mdr_col_none_mars", 32, 272, 700, 24, "hoi_18mbs", "MDR_COL_NONE_MARS")
    out["colony_none"] = (c, "", "", "check_variable = { mdr_space_tier > 0 } check_variable = { mdr_space_page = 8 } NOT = { AND = { check_variable = { mdr_space_colony_view = 1 } has_country_flag = mdr_col_moon } AND = { check_variable = { mdr_space_colony_view = 2 } has_country_flag = mdr_col_mars } }")
    # Guide: the seven steps, each with a shortcut.
    c = panel("mdr_space_guide_panel", 16, 124, 748, 576) + section("mdr_space_guide_title", 30, 134, "MDR_SPACE_GUIDE_INTRO")
    eff, trig = "", ""
    for i, (icon, page) in enumerate((("finance", 5), ("programme", 0), ("atom", 0), ("projects", 3), ("summary", 7), ("goals", 2), ("colonies", 8))):
        y = 166 + i * 76
        c += picture(f"mdr_space_guide_icon_{i + 1}", f"GFX_mdr_space_icon_{icon}", 30, y + 8)
        c += text(f"mdr_space_guide_name_{i + 1}", 72, y, 580, 20, "hoi_18mbs", f"MDR_SPACE_G{i + 1}") + text(f"mdr_space_guide_text_{i + 1}", 72, y + 24, 580, 40, "hoi_16mbs", f"MDR_SPACE_G{i + 1}_T")
        if page:
            c += button(f"mdr_space_guide_go_{i + 1}", 672, y + 14, "GFX_mdr_space_btn_71x26", "MDR_SPACE_GO", "MDR_SPACE_GO_TT")
            eff += f"\t\t\tmdr_space_guide_go_{i + 1}_click = {{\n\t\t\t\tset_variable = {{ mdr_space_page = {page} }}\n\t\t\t\tmdr_space_refresh = yes\n\t\t\t}}\n"
            trig += f"\t\t\tmdr_space_guide_go_{i + 1}_click_enabled = {{ check_variable = {{ mdr_space_tier > 0 }} }}\n"
    out["guide"] = (c, eff, trig, "check_variable = { mdr_space_page = 9 }")
    return out


def colony_static():
    for b, N in (("moon", "MOON"), ("mars", "MARS")):
        p = f"mdr_col_{b}"
        STATIC[f"MDR_COL_{N}_POP"] = (f"§Y[?{p}_pop|0]§!/[?{p}_cap|0]", f"§Y[?{p}_pop|0]§!/[?{p}_cap|0]")
        STATIC[f"MDR_COL_{N}_MORALE"] = (f"§Y[?{p}_morale|0]%§!", f"§Y[?{p}_morale|0]%§!")
        for m, key, es, en in (("greenhouse", "GREENHOUSE", "Invernaderos", "Greenhouses"), ("mine", "MINE", "Minas de hielo", "Ice mines"), ("reactor", "REACTOR", "Reactores", "Reactors"), ("workshop", "WORKSHOP", "Talleres", "Workshops")):
            STATIC[f"MDR_COL_{N}_{key}"] = (f"{es}: §Y[?{p}_{m}|0]§!", f"{en}: §Y[?{p}_{m}|0]§!")
        for key, supply in (("WATER", "water"), ("FOOD", "food"), ("ENERGY", "energy"), ("OXYGEN", "oxygen")):
            STATIC[f"MDR_COL_{N}_{key}_V"] = (f"§Y[?{p}_{supply}|0]§! ([?{p}_{supply}_net|+1])", f"§Y[?{p}_{supply}|0]§! ([?{p}_{supply}_net|+1])")
        STATIC[f"MDR_COL_{N}_ROUTE_STATE"] = (f"Tierra a {'Luna' if b == 'moon' else 'Marte'}. Agua §Y[?{p}_water|0]§!, comida §Y[?{p}_food|0]§!, energía §Y[?{p}_energy|0]§!, oxígeno §Y[?{p}_oxygen|0]§!", f"Earth to {'Moon' if b == 'moon' else 'Mars'}. Water §Y[?{p}_water|0]§!, food §Y[?{p}_food|0]§!, energy §Y[?{p}_energy|0]§!, oxygen §Y[?{p}_oxygen|0]§!")
    STATIC["MDR_SPACE_EMPTY"] = ("", "")
    for a, _ in ACTIONS:
        key = f"mdr_sa_{a[0]}_left"
        STATIC[f"MDR_SA_{a[0].upper()}_LEFT"] = (f"§YEn curso:§! quedan §Y[?{key}|0]§! semanas", f"§YRunning:§! §Y[?{key}|0]§! weeks left")
        STATIC[f"MDR_SA_{a[0].upper()}_STATUS"] = (f"[mdr_sa_{a[0]}_status]", f"[mdr_sa_{a[0]}_status]")
    for g in GOALS:
        STATIC[f"MDR_SG_{g[0].upper()}_STATUS"] = (f"[mdr_sg_{g[0]}_status]", f"[mdr_sg_{g[0]}_status]")


colony_static()
