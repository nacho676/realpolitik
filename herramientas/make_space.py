# Generates the "Programa espacial" technology tab from Millennium Dawn's files: common/technologies/mdr_space.txt,
# common/technology_tags/00_technology.txt (copy of MD's with the folder and category), interface/mdr_space_techs.gfx, the folder, tab and
# item templates in interface/countrytechtreeview.gui, common/scripted_effects/mdr_space_techs.txt,
# common/scripted_localisation/mdr_space_techs_loc.txt and localisation/*/mdr_space_techs_l_*.yml.
# Run from the mod folder: python herramientas/make_space.py
# Run it again after each Millennium Dawn update (after copying its new countrytechtreeview.gui).
import colorsys, os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import space_program
import numpy as np
from PIL import Image, ImageDraw

MD = "../Millennium-Dawn-2.0.0"
FOLDER = "mdr_space_program_folder"
CATEGORY = "CAT_mdr_space"
OUT = "gfx/interface/mdr/space/"
PHOTO = "gfx/event_pictures/generic/space_stuff/"
SCI = "gfx/interface/goals/00_science/"

COLUMNS = [("LANZAMIENTO", "LAUNCH"), ("VIDA Y SEGURIDAD", "LIFE AND SAFETY"), ("RECURSOS Y ENERGÍA", "RESOURCES AND ENERGY"), ("DEFENSA ORBITAL", "ORBITAL DEFENSE"), ("INDUSTRIA ORBITAL", "ORBITAL INDUSTRY"), ("VIAJES ESPACIALES", "SPACE TRAVEL")]
SITE, RADAR, GREEN, RESEARCH, STABLE = "production_speed_mdr_spaceport_factor", "production_speed_radar_station_factor", "renewable_energy_gain_multiplier", "research_speed_factor", "stability_factor"

# Which technologies have an icon (the drawings come from make_space_tech_icons.py; these MD pictures were the old ones).
ICON = {
 "foundations": (PHOTO + "nasa.dds", .5), "launcher": (PHOTO + "mars_colony_2.dds", .5), "heavy": (PHOTO + "nasa_launch_mars.dds", .5), "cryogenic": (PHOTO + "nasa_launch_pad_mars.dds", .5),
 "smalllauncher": (SCI + "focus_rocketry.dds", None), "reusable": (PHOTO + "spacex_mars.dds", .5), "rapidreuse": (PHOTO + "mars_colony_19.dds", .3), "superheavy": (PHOTO + "mars_colony_13.dds", .5),
 "refuel": (PHOTO + "spacex_super_heavy.dds", .6), "nuclear": (SCI + "stellarator_reactor.dds", None), "electric": (SCI + "tokamak_reactor.dds", None), "fullflow": (SCI + "rocketry.dds", None),
 "massdriver": (PHOTO + "kinetic_bombardment.dds", .7), "cruiser": (PHOTO + "mars_colony_3.dds", .55),
 "crewed": (PHOTO + "astronauts.dds", .5), "station": (SCI + "international_space_station.dds", None), "longstay": ("gfx/event_pictures/americas/north_america/canada - CAN/CAN_space_expedition_35.dds", .5),
 "commercialcrew": ("gfx/event_pictures/americas/north_america/united_states - USA/USA_shuttle_launch.dds", .4), "lifesupport": (PHOTO + "mars_colony_10.dds", .5), "radiation": (PHOTO + "nasa_orion_space_capsule.dds", .5),
 "habitat": (PHOTO + "moonbase.dds", .5), "surface": (PHOTO + "mars_mission.dds", .5), "deepmission": (PHOTO + "manned_mission_mars.dds", .5), "marslanding": (PHOTO + "mars_colony_1.dds", .5),
 "gravity": ("gfx/event_pictures/americas/north_america/united_states - USA/USA_shuttle_funding.dds", .5), "torpor": (PHOTO + "mars_colony_9.dds", .5), "biosphere": (PHOTO + "mars_colony_17.dds", .5),
 "tracking": (SCI + "radar2.dds", None), "powerarrays": ("gfx/interface/goals/00_energy_resources/generic_solar.dds", None), "rtg": ("gfx/interface/goals/00_energy_resources/mining.dds", None), "prospecting": (SCI + "land_on_moon.dds", None),
 "solar": ("gfx/interface/ideas/economy/solar_energy.dds", None), "lunarice": (SCI + "moon_relax.dds", None), "fission": (PHOTO + "mars_colony_16.dds", .5), "regolith": (PHOTO + "moonbase_construction.dds", .5),
 "marsfuel": (PHOTO + "mars_colony_8.dds", .5), "asteroidsurvey": (PHOTO + "asteroid.dds", .5), "asteroidmining": (SCI + "asteroid_mining.dds", None), "powerbeam": ("gfx/event_pictures/europe/italy - ITA/report_event_Italy_From_Space.dds", .5), "helium": (SCI + "orbit_moon.dds", None),
 "debris": (PHOTO + "space_debris.dds", .5), "awareness": (SCI + "radar.dds", None), "hardening": (SCI + "weaponized_satellites.dds", None), "spacecommand": ("gfx/interface/goals/00_army/army_radar.dds", None),
 "avoidance": (SCI + "generic_space.dds", None), "cleanup": ("gfx/event_pictures/asia/turkmenistan - TRK/turkmen_spaceprogramm.dds", .78), "patrol": (PHOTO + "mars_colony_15.dds", .5), "planetary": (PHOTO + "asteroid_in_orbit.dds", .5),
 "deflection": ("gfx/event_pictures/europe/italy - ITA/report_event_Asteroid_Rosetta.dds", .5), "cislunar": (SCI + "lunar_launch.dds", None), "baseguard": (PHOTO + "mars_colony_11.dds", .5),
 "microgravity": (SCI + "mars.dds", None), "smallsat": (PHOTO + "mars_colony_12.dds", .5), "commercialsat": (PHOTO + "spacex_announcement.dds", .55), "constellation": ("gfx/event_pictures/europe/italy - ITA/report_event_Italy_From_Space_1.dds", .5),
 "servicing": ("gfx/interface/goals/00_economy/economic_robots.dds", None), "manufacturing": ("gfx/interface/goals/mining_research.dds", None), "printing": (PHOTO + "mars_colony_4.dds", .5), "assembly": (PHOTO + "mars_colony_14.dds", .5),
 "navigation": (SCI + "radar2.dds", None), "gravityassist": (PHOTO + "asteroid_in_orbit.dds", .5), "translunar": (SCI + "lunar_launch.dds", None), "deepnet": (SCI + "radio_communications.dds", None), "precisionland": (SCI + "land_on_moon.dds", None), "aerobrake": (SCI + "land_on_mars.dds", None),
 "transithab": (PHOTO + "manned_mission_mars.dds", .3), "marstransfer": (PHOTO + "nasa_launch_mars.dds", .3), "venusfloat": (PHOTO + "mars_colony_5.dds", .5), "asteroidnav": (PHOTO + "asteroid.dds", .3), "outerprop": (SCI + "fusion_science.dds", None), "titanentry": (PHOTO + "mars_colony_6.dds", .3), "solarnet": (SCI + "mars_base.dds", None),
 "lunarfactory": (PHOTO + "mars_colony_7.dds", .5), "shipyard": (PHOTO + "mars_colony_6.dds", .5), "platform": (PHOTO + "mars_colony_20.dds", .5), "elevator": (PHOTO + "mars_colony_18.dds", .5),
}

# What each technology really does: the agency first (science, budget, bases), then launchers and satellites, then what it brings home.
OLV_S, OLV_C, OLV_R = "olv_production_speed_modifier", "olv_production_cost_modifier", "olv_launch_reliability_modifier"
SCIENCE, BUDGET, PERBASE = "mdr_space_science_factor", "mdr_space_budget_cost_factor", "mdr_space_site_science"
G_S, G_C = "gnss_production_speed_modifier", "gnss_production_cost_modifier"
C_S, C_C = "comsat_production_speed_modifier", "comsat_production_cost_modifier"
S_S, S_C = "spysat_production_speed_modifier", "spysat_production_cost_modifier"
K_S, K_C = "killsat_production_speed_modifier", "killsat_production_cost_modifier"
PP, BUILD, FUEL, ORE = "political_power_factor", "production_speed_buildings_factor", "fuel_gain_factor", "local_resources_factor"
REACTOR, ENERGY, NUKE, INFLUENCE = "nuclear_reactor_fuel_production_factor", "energy_gain_multiplier", "nuclear_energy_generation_modifier", "foreign_influence_modifier"
GOODS, CYBER, CRYPTO, INTEL = "consumer_goods_factor", "cyber_defense_rating_modifier", "encryption_factor", "civilian_intel_factor"
EFFICIENCY, FACTORY, DOCKYARD = "production_factory_max_efficiency_factor", "industrial_capacity_factory", "industrial_capacity_dockyard"
MODS = {
 "foundations": {SCIENCE: 0.053, BUDGET: -0.012, "research_speed_factor": 0.003},
 "launcher": {OLV_S: 0.072, SITE: 0.048, "air_detection": 0.02},
 "heavy": {OLV_C: -0.046, PERBASE: 0.12, "production_speed_buildings_factor": 0.004},
 "cryogenic": {OLV_R: 0.027, FUEL: 0.008, "supply_factor": 0.004},
 "smalllauncher": {OLV_C: -0.043, C_S: 0.051, BUDGET: -0.014},
 "reusable": {OLV_C: -0.128, OLV_S: 0.064, BUDGET: -0.027},
 "rapidreuse": {OLV_S: 0.113, OLV_R: 0.018, "air_mission_efficiency": 0.01},
 "superheavy": {SITE: 0.074, PERBASE: 0.27, FACTORY: 0.004},
 "refuel": {OLV_R: 0.029, OLV_C: -0.036, FUEL: 0.012},
 "nuclear": {OLV_S: 0.057, REACTOR: 0.046, "nuclear_production_factor": 0.03},
 "electric": {SCIENCE: 0.037, "energy_gain_multiplier": 0.006, RESEARCH: 0.003},
 "fullflow": {OLV_C: -0.087, BUDGET: -0.021, "air_superiority_efficiency": 0.008},
 "massdriver": {OLV_C: -0.074, SITE: 0.043, ORE: 0.017},
 "cruiser": {SCIENCE: 0.062, INFLUENCE: 0.028, "trade_opinion_factor": 0.03},
 "crewed": {SCIENCE: 0.031, "war_support_factor": 0.012, PP: 0.006},
 "station": {SCIENCE: 0.058, "experience_gain_factor": 0.01, RESEARCH: 0.004},
 "longstay": {"monthly_population": 0.006, BUDGET: -0.009, RESEARCH: 0.002},
 "commercialcrew": {BUDGET: -0.034, OLV_S: 0.047, "political_power_gain": 0.03},
 "lifesupport": {SCIENCE: 0.024, GOODS: -0.004, "attrition": -0.006},
 "radiation": {SCIENCE: 0.022, "nuclear_production_factor": 0.02, STABLE: 0.002},
 "habitat": {SCIENCE: 0.044, PERBASE: 0.16, "local_building_slots_factor": 0.004},
 "surface": {BUILD: 0.008, ORE: 0.009, "army_org_factor": 0.004},
 "deepmission": {SCIENCE: 0.039, PP: 0.011, "conscription_factor": 0.004},
 "marslanding": {SCIENCE: 0.074, PP: 0.019, STABLE: 0.006, "war_support_factor": 0.012},
 "gravity": {"monthly_population": 0.008, OLV_R: 0.013, RESEARCH: 0.003},
 "torpor": {SCIENCE: 0.024, BUDGET: -0.017, GOODS: -0.003},
 "biosphere": {SCIENCE: 0.047, GOODS: -0.009, "monthly_population": 0.01},
 "tracking": {G_S: 0.074, "planning_speed": 0.03, RADAR: 0.028},
 "powerarrays": {C_S: 0.036, GREEN: 0.019, "energy_gain_multiplier": 0.004},
 "rtg": {SCIENCE: 0.029, OLV_R: 0.012, REACTOR: 0.028},
 "prospecting": {SCIENCE: 0.033, PERBASE: 0.09, ORE: 0.008},
 "solar": {BUDGET: -0.008, GREEN: 0.027, "energy_gain_multiplier": 0.008},
 "lunarice": {SCIENCE: 0.026, FUEL: 0.011, OLV_C: -0.014},
 "fission": {PERBASE: 0.11, NUKE: 0.018, REACTOR: 0.022},
 "regolith": {OLV_C: -0.027, BUILD: 0.006, ORE: 0.017},
 "marsfuel": {OLV_C: -0.034, FUEL: 0.019, "supply_factor": 0.006},
 "asteroidsurvey": {SCIENCE: 0.038, "max_planning": 0.02, RESEARCH: 0.002},
 "asteroidmining": {BUDGET: -0.023, ORE: 0.026, EFFICIENCY: 0.006},
 "powerbeam": {GREEN: 0.046, "energy_gain_multiplier": 0.011, "air_night_penalty": -0.01},
 "helium": {SCIENCE: 0.034, "energy_gain_multiplier": 0.018, NUKE: 0.012},
 "debris": {G_C: -0.043, OLV_R: 0.016, "naval_detection": 0.02},
 "awareness": {S_S: 0.071, INTEL: 0.018, "air_detection": 0.03},
 "hardening": {K_C: -0.034, S_C: -0.027, CYBER: 1, "decryption_factor": 0.02},
 "spacecommand": {K_S: 0.092, S_S: 0.037, "air_intercept_efficiency": 0.012},
 "avoidance": {C_C: -0.047, G_C: -0.024, "air_accidents_factor": -0.04},
 "cleanup": {BUDGET: -0.012, G_C: -0.041, C_C: -0.028},
 "patrol": {S_C: -0.087, K_S: 0.044, "navy_intel_factor": 0.04},
 "planetary": {SCIENCE: 0.027, STABLE: 0.003, INFLUENCE: 0.011},
 "deflection": {K_C: -0.031, PP: 0.006, "drift_defence_factor": 0.03},
 "cislunar": {C_S: 0.087, SITE: 0.021, "naval_speed_factor": 0.004},
 "baseguard": {PERBASE: 0.08, K_S: 0.039, CRYPTO: 0.027},
 "microgravity": {SCIENCE: 0.038, EFFICIENCY: 0.004, "monthly_population": 0.004},
 "smallsat": {C_S: 0.072, G_S: 0.042, "land_night_attack": 0.012},
 "commercialsat": {BUDGET: -0.029, C_C: -0.071, "trade_opinion_factor": 0.02},
 "constellation": {C_S: 0.054, INTEL: 0.044, "army_intel_factor": 0.05},
 "servicing": {K_C: -0.047, S_C: -0.033, "airforce_intel_factor": 0.04},
 "manufacturing": {SCIENCE: 0.026, BUDGET: -0.018, EFFICIENCY: 0.009},
 "printing": {SITE: 0.026, OLV_C: -0.024, BUILD: 0.009},
 "assembly": {SITE: 0.046, PERBASE: 0.13, "production_factory_efficiency_gain_factor": 0.012},
 "lunarfactory": {SCIENCE: 0.029, OLV_C: -0.031, FACTORY: 0.009},
 "shipyard": {BUDGET: -0.016, OLV_S: 0.048, DOCKYARD: 0.018},
 "platform": {SCIENCE: 0.053, PERBASE: 0.18, "global_building_slots_factor": 0.004},
 "elevator": {BUDGET: -0.038, OLV_C: -0.168, OLV_S: 0.091},
 "navigation": {SCIENCE: 0.024, OLV_R: 0.012, "planning_speed": 0.02},
 "gravityassist": {SCIENCE: 0.031, BUDGET: -0.009, FUEL: 0.006},
 "translunar": {OLV_S: 0.044, PERBASE: 0.08, "war_support_factor": 0.006},
 "deepnet": {SCIENCE: 0.042, INTEL: 0.012, RADAR: 0.018},
 "precisionland": {OLV_R: 0.021, "air_accidents_factor": -0.03, RESEARCH: 0.002},
 "aerobrake": {OLV_C: -0.032, OLV_R: 0.016, SCIENCE: 0.019},
 "transithab": {SCIENCE: 0.036, GOODS: -0.004, STABLE: 0.002},
 "marstransfer": {OLV_S: 0.058, BUDGET: -0.014, PP: 0.008},
 "venusfloat": {SCIENCE: 0.044, GREEN: 0.012, RESEARCH: 0.002},
 "asteroidnav": {OLV_C: -0.029, ORE: 0.012, SCIENCE: 0.026},
 "outerprop": {OLV_S: 0.067, REACTOR: 0.031, NUKE: 0.011},
 "titanentry": {SCIENCE: 0.052, FUEL: 0.014, PERBASE: 0.1},
 "solarnet": {SCIENCE: 0.071, INFLUENCE: 0.021, BUDGET: -0.024},
}

# Plain words for ONCE, shown in the technology.
ONCE_TEXT = {
 "crewed": ("86 de poder político, estabilidad, 6 de prestigio y 4 astronautas.", "86 political power, stability, 6 prestige and 4 astronauts."),
 "station": ("Un proyecto o misión más a la vez.", "One more project or mission at a time."),
 "reusable": ("42 de ciencia y un proyecto o misión más a la vez.", "42 science and one more project or mission at a time."),
 "superheavy": ("8 de prestigio.", "8 prestige."),
 "commercialcrew": ("6 astronautas y 54 de poder político.", "6 astronauts and 54 political power."),
 "marslanding": ("12 de prestigio, estabilidad y apoyo a la guerra.", "12 prestige, stability and war support."),
 "microgravity": ("36 de ciencia.", "36 science."),
 "constellation": ("Bono para las próximas 2 investigaciones de esta pestaña.", "A bonus for the next 2 researches of this tab."),
 "manufacturing": ("2 fábricas militares en la capital.", "2 military factories in the capital."),
 "lunarfactory": ("3 fábricas civiles en la capital.", "3 civilian factories in the capital."),
 "asteroidsurvey": ("64 de ciencia.", "64 science."),
 "asteroidmining": ("16 de acero, 12 de cromo y 8 de tungsteno en la capital.", "16 steel, 12 chromium and 8 tungsten in the capital."),
 "regolith": ("10 de aluminio en la capital.", "10 aluminium in the capital."),
 "lunarice": ("38 de ciencia.", "38 science."),
 "cleanup": ("Saca 11 de basura orbital, para todos.", "Removes 11 orbital debris, for everyone."),
 "debris": ("Saca 2 de basura orbital, para todos.", "Removes 2 orbital debris, for everyone."),
 "planetary": ("Estabilidad.", "Stability."),
 "deflection": ("5 de prestigio y estabilidad.", "5 prestige and stability."),
 "powerbeam": ("Un espacio de edificio en la capital.", "One building slot in the capital."),
 "platform": ("Un proyecto o misión más a la vez, y 8 de prestigio.", "One more project or mission at a time, and 8 prestige."),
 "translunar": ("4 de prestigio.", "4 prestige."),
 "marstransfer": ("8 de prestigio y 64 de poder político.", "8 prestige and 64 political power."),
 "solarnet": ("Un proyecto o misión más a la vez, y 12 de prestigio.", "One more project or mission at a time, and 12 prestige."),
 "elevator": ("30 de prestigio, 180 de poder político, estabilidad y un proyecto o misión más a la vez.", "30 prestige, 180 political power, stability and one more project or mission at a time."),
}

# Notable things that happen once, when the research is finished. All in country scope.
ONCE = {
 "crewed": "add_political_power = 86\n\t\t\tadd_stability = 0.018\n\t\t\tadd_to_variable = { mdr_space_prestige = 6 }\n\t\t\tadd_to_variable = { mdr_space_astronauts = 4 }",
 "station": "add_to_variable = { mdr_space_extra_slots = 1 }",
 "reusable": "add_to_variable = { mdr_space_science = 42 }\n\t\t\tadd_to_variable = { mdr_space_extra_slots = 1 }",
 "superheavy": "add_to_variable = { mdr_space_prestige = 8 }",
 "commercialcrew": "add_to_variable = { mdr_space_astronauts = 6 }\n\t\t\tadd_political_power = 54",
 "marslanding": "add_to_variable = { mdr_space_prestige = 12 }\n\t\t\tadd_stability = 0.024\n\t\t\tadd_war_support = 0.018",
 "microgravity": "add_to_variable = { mdr_space_science = 36 }",
 "constellation": "add_tech_bonus = { name = mdr_space_constellation_bonus bonus = 1 uses = 2 category = CAT_mdr_space }",
 "manufacturing": "capital_scope = { add_extra_state_shared_building_slots = 2 add_building_construction = { type = arms_factory level = 2 instant_build = yes } }",
 "lunarfactory": "capital_scope = { add_extra_state_shared_building_slots = 3 add_building_construction = { type = industrial_complex level = 3 instant_build = yes } }",
 "asteroidsurvey": "add_to_variable = { mdr_space_science = 64 }",
 "asteroidmining": "capital_scope = { add_resource = { type = steel amount = 16 } add_resource = { type = chromium amount = 12 } add_resource = { type = tungsten amount = 8 } }",
 "regolith": "capital_scope = { add_resource = { type = aluminium amount = 10 } }",
 "lunarice": "add_to_variable = { mdr_space_science = 38 }",
 "cleanup": "add_to_variable = { global.mdr_space_debris = -11 }",
 "debris": "add_to_variable = { global.mdr_space_debris = -2 }",
 "planetary": "add_stability = 0.012",
 "deflection": "add_to_variable = { mdr_space_prestige = 5 }\n\t\t\tadd_stability = 0.01",
 "powerbeam": "capital_scope = { add_extra_state_shared_building_slots = 1 }",
 "platform": "add_to_variable = { mdr_space_extra_slots = 1 }\n\t\t\tadd_to_variable = { mdr_space_prestige = 8 }",
 "translunar": "add_to_variable = { mdr_space_prestige = 4 }",
 "marstransfer": "add_to_variable = { mdr_space_prestige = 8 }\n\t\t\tadd_political_power = 64",
 "solarnet": "add_to_variable = { mdr_space_extra_slots = 1 }\n\t\t\tadd_to_variable = { mdr_space_prestige = 12 }",
 "elevator": "add_to_variable = { mdr_space_prestige = 30 }\n\t\t\tadd_political_power = 180\n\t\t\tadd_stability = 0.03\n\t\t\tadd_to_variable = { mdr_space_extra_slots = 1 }",
}

# Each column is a chain, oldest first: id, year, modifiers, Spanish name and text, English name and text.
ROOT = ("foundations", 1985, {RESEARCH: 0.003}, "Fundamentos del programa espacial", "Formar ingenieros, estudiar la órbita y sentar las bases de un programa. Permite fundar una agencia espacial.", "Space Programme Foundations", "Training engineers, studying orbits and laying the groundwork for a programme. Allows founding a space agency.")
CHAINS = [
[
("launcher", 1990, {SITE: 0.04}, "Lanzador orbital", "Un cohete propio capaz de poner una carga en órbita baja.", "Orbital Launcher", "A rocket of our own that can put a payload into low orbit."),
("heavy", 2000, {SITE: 0.04}, "Lanzador pesado", "Más de 20 toneladas en órbita baja: estaciones, sondas y satélites grandes.", "Heavy Launcher", "Over 20 tonnes in low orbit: stations, probes and large satellites."),
("cryogenic", 2005, {SITE: 0.02}, "Etapa criogénica", "Hidrógeno y oxígeno líquidos para llegar más lejos con la misma masa.", "Cryogenic Upper Stage", "Liquid hydrogen and oxygen to go further with the same mass."),
("smalllauncher", 2010, {SITE: 0.02}, "Lanzador ligero comercial", "Cohetes chicos y baratos para satélites pequeños.", "Commercial Light Launcher", "Small, cheap rockets for small satellites."),
("reusable", 2015, {SITE: 0.05}, "Primera etapa reutilizable", "La primera etapa vuelve y aterriza: cada lanzamiento cuesta mucho menos.", "Reusable First Stage", "The first stage comes back and lands: each launch costs far less."),
("rapidreuse", 2020, {SITE: 0.03}, "Reutilización rápida", "Volver a volar el mismo cohete en días, no en meses.", "Rapid Reuse", "Flying the same rocket again in days, not months."),
("superheavy", 2025, {SITE: 0.05}, "Lanzador superpesado", "Más de 100 toneladas en órbita baja: lo necesario para ir a la Luna y a Marte.", "Super-Heavy Launcher", "Over 100 tonnes in low orbit: what it takes to reach the Moon and Mars."),
("refuel", 2030, {SITE: 0.02}, "Reabastecimiento en órbita", "Cargar combustible en órbita multiplica lo que se puede enviar lejos.", "Orbital Refuelling", "Taking on fuel in orbit multiplies what can be sent far away."),
("nuclear", 2040, {RESEARCH: 0.003}, "Propulsión nuclear térmica", "Un reactor calienta el propelente y acorta a la mitad los viajes a Marte.", "Nuclear Thermal Propulsion", "A reactor heats the propellant and halves the journey to Mars."),
("electric", 2045, {}, "Propulsión eléctrica de alta potencia", "Motores iónicos de megavatios para cargas pesadas entre planetas.", "High-Power Electric Propulsion", "Megawatt ion engines for heavy cargo between planets."),
("fullflow", 2055, {SITE: 0.03}, "Motores de ciclo completo", "El límite práctico de los motores químicos: más empuje y menos costo.", "Full-Flow Engines", "The practical limit of chemical engines: more thrust, lower cost."),
("massdriver", 2065, {}, "Catapulta electromagnética lunar", "Lanzar carga desde la Luna sin cohetes, aprovechando su baja gravedad.", "Lunar Mass Driver", "Launching cargo from the Moon without rockets, thanks to its low gravity."),
("cruiser", 2075, {}, "Nave de transporte interplanetario", "Una nave de uso permanente entre la Tierra y Marte.", "Interplanetary Transport Ship", "A permanent ship between Earth and Mars."),
],
[
("crewed", 1990, {STABLE: 0.003}, "Vuelo tripulado", "Cápsulas y entrenamiento para llevar personas a la órbita y traerlas de vuelta.", "Crewed Spaceflight", "Capsules and training to take people to orbit and bring them back."),
("station", 1995, {RESEARCH: 0.003}, "Estación orbital", "Un laboratorio habitado de forma permanente en órbita.", "Orbital Station", "A permanently crewed laboratory in orbit."),
("longstay", 2005, {}, "Estadías prolongadas", "Medicina y rutinas para pasar un año entero en órbita.", "Extended Stays", "Medicine and routines to spend a whole year in orbit."),
("commercialcrew", 2015, {SITE: 0.02}, "Tripulación comercial", "Empresas privadas que llevan astronautas por contrato.", "Commercial Crew", "Private companies carrying astronauts under contract."),
("lifesupport", 2020, {}, "Soporte vital cerrado", "Reciclar el agua y el aire casi por completo para misiones largas.", "Closed Life Support", "Recycling almost all water and air for long missions."),
("radiation", 2025, {}, "Protección contra la radiación", "Blindajes y refugios para vivir lejos del campo magnético terrestre.", "Radiation Shielding", "Shielding and shelters for living beyond Earth's magnetic field."),
("habitat", 2030, {RESEARCH: 0.003}, "Hábitat lunar", "Módulos que protegen a una tripulación del frío y de la radiación de la Luna.", "Lunar Habitat", "Modules that shield a crew from the Moon's cold and radiation."),
("surface", 2035, {}, "Operaciones de superficie", "Trajes y vehículos para trabajar semanas fuera de la base.", "Surface Operations", "Suits and vehicles for working weeks away from base."),
("deepmission", 2040, {STABLE: 0.003}, "Misiones de larga duración", "Tripulaciones que pasan años lejos de la Tierra, rumbo a Marte.", "Long-Duration Missions", "Crews spending years far from Earth, on the way to Mars."),
("marslanding", 2045, {STABLE: 0.004}, "Descenso tripulado en Marte", "Posar decenas de toneladas en Marte y volver a despegar.", "Crewed Mars Landing", "Landing dozens of tonnes on Mars and taking off again."),
("gravity", 2055, {}, "Gravedad artificial", "Naves que giran para proteger los huesos y el corazón.", "Artificial Gravity", "Rotating ships that protect bones and hearts."),
("torpor", 2065, {}, "Letargo médico", "Reducir el metabolismo para bajar comida, agua y radiación en el viaje.", "Medical Torpor", "Lowering metabolism to cut food, water and radiation on the journey."),
("biosphere", 2075, {RESEARCH: 0.003}, "Biosfera cerrada", "Una colonia que produce casi todo lo que come y respira.", "Closed Biosphere", "A colony that makes almost everything it eats and breathes."),
],
[
("tracking", 1995, {RADAR: 0.03}, "Red de seguimiento", "Antenas y radares terrestres para seguir y controlar lo que está en órbita.", "Tracking Network", "Ground antennas and radars to track and control what is in orbit."),
("powerarrays", 2005, {GREEN: 0.02}, "Paneles solares de alto rendimiento", "Células de varias capas nacidas de los satélites.", "High-Efficiency Solar Arrays", "Multi-layer cells born from satellites."),
("rtg", 2010, {}, "Generadores de radioisótopos", "Energía durante décadas para sondas lejos del Sol.", "Radioisotope Generators", "Decades of power for probes far from the Sun."),
("prospecting", 2015, {}, "Prospección lunar", "Sondas que cartografían el hielo y los minerales de la Luna.", "Lunar Prospecting", "Probes mapping the Moon's ice and minerals."),
("solar", 2020, {GREEN: 0.03}, "Energía solar orbital", "Paneles más livianos y primeros ensayos de enviar energía desde la órbita.", "Orbital Solar Power", "Lighter panels and first trials of sending power from orbit."),
("lunarice", 2025, {}, "Extracción de hielo lunar", "Sacar agua de los cráteres polares para beber y hacer combustible.", "Lunar Ice Extraction", "Getting water from polar craters to drink and make fuel."),
("fission", 2030, {}, "Reactor de superficie", "Un reactor pequeño que da energía durante la noche lunar.", "Surface Reactor", "A small reactor giving power through the lunar night."),
("regolith", 2035, {}, "Minería de regolito", "Sacar oxígeno y metales del suelo lunar para no llevarlos desde la Tierra.", "Regolith Mining", "Getting oxygen and metals from lunar soil instead of hauling them from Earth."),
("marsfuel", 2040, {}, "Combustible marciano", "Fabricar metano y oxígeno con la atmósfera de Marte para volver.", "Martian Fuel", "Making methane and oxygen from Mars's air for the way back."),
("asteroidsurvey", 2045, {}, "Catálogo de asteroides", "Conocer la composición de los asteroides cercanos.", "Asteroid Survey", "Learning what nearby asteroids are made of."),
("asteroidmining", 2055, {RESEARCH: 0.002}, "Minería de asteroides", "Traer metales y agua de un asteroide cercano.", "Asteroid Mining", "Bringing metals and water from a nearby asteroid."),
("powerbeam", 2065, {GREEN: 0.05}, "Transmisión de energía desde la órbita", "Grandes plantas solares que envían energía a la Tierra.", "Space-Based Power Transmission", "Large solar plants beaming power to Earth."),
("helium", 2075, {}, "Estudio del helio-3", "Evaluar si el helio-3 lunar serviría para la fusión.", "Helium-3 Study", "Assessing whether lunar helium-3 could serve fusion."),
],
[
("debris", 2000, {RADAR: 0.02}, "Rastreo de basura espacial", "Catalogar los restos en órbita para que los satélites puedan esquivarlos.", "Space Debris Tracking", "Cataloguing debris in orbit so satellites can dodge it."),
("awareness", 2005, {RADAR: 0.02}, "Vigilancia del espacio", "Saber qué hace cada objeto en órbita y de quién es.", "Space Domain Awareness", "Knowing what each object in orbit is doing and whose it is."),
("hardening", 2010, {}, "Satélites endurecidos", "Protección contra interferencias, láseres y explosiones.", "Hardened Satellites", "Protection against jamming, lasers and blasts."),
("spacecommand", 2015, {}, "Mando espacial", "Una rama militar dedicada a la órbita.", "Space Command", "A military branch devoted to orbit."),
("avoidance", 2020, {}, "Maniobras automáticas", "Satélites que esquivan los choques por su cuenta.", "Automatic Avoidance", "Satellites that dodge collisions on their own."),
("cleanup", 2025, {}, "Limpieza orbital", "Naves que capturan restos y los sacan de órbita.", "Orbital Cleanup", "Spacecraft that capture debris and take it out of orbit."),
("patrol", 2030, {}, "Patrulla orbital", "Naves que inspeccionan satélites ajenos de cerca.", "Orbital Patrol", "Craft inspecting other countries' satellites up close."),
("planetary", 2035, {STABLE: 0.002}, "Defensa planetaria", "Detectar asteroides peligrosos a tiempo.", "Planetary Defense", "Spotting dangerous asteroids in time."),
("deflection", 2045, {}, "Desvío de asteroides", "Impactos que cambian el rumbo de un asteroide.", "Asteroid Deflection", "Impacts that change an asteroid's course."),
("cislunar", 2055, {}, "Control del tráfico lunar", "Reglas y radares para el espacio entre la Tierra y la Luna.", "Cislunar Traffic Control", "Rules and radars for the space between Earth and Moon."),
("baseguard", 2065, {}, "Protección de bases", "Defender colonias de impactos, tormentas solares y sabotajes.", "Base Protection", "Guarding colonies from impacts, solar storms and sabotage."),
],
[
("microgravity", 2000, {RESEARCH: 0.002}, "Experimentos en microgravedad", "Materiales y medicamentos que solo se pueden hacer sin gravedad.", "Microgravity Experiments", "Materials and medicines that can only be made without gravity."),
("smallsat", 2005, {}, "Plataformas de satélites", "Un mismo diseño base para muchos satélites.", "Satellite Buses", "One base design for many satellites."),
("commercialsat", 2010, {}, "Mercado de satélites", "Empresas que venden imágenes, datos y comunicaciones.", "Satellite Market", "Companies selling images, data and communications."),
("constellation", 2015, {}, "Megaconstelaciones", "Miles de satélites baratos en órbita baja.", "Megaconstellations", "Thousands of cheap satellites in low orbit."),
("servicing", 2020, {}, "Reparación en órbita", "Naves que reparan y recargan satélites.", "On-Orbit Servicing", "Craft that repair and refuel satellites."),
("manufacturing", 2025, {RESEARCH: 0.003}, "Fabricación orbital", "Talleres automáticos que producen lo que vale más que su transporte.", "Orbital Manufacturing", "Automatic workshops making what is worth more than its transport."),
("printing", 2030, {}, "Impresión 3D en el espacio", "Fabricar piezas y estructuras donde se necesitan.", "3D Printing in Space", "Making parts and structures where they are needed."),
("assembly", 2035, {}, "Ensamblaje orbital", "Armar en órbita naves demasiado grandes para cualquier cohete.", "Orbital Assembly", "Assembling in orbit ships too big for any rocket."),
("lunarfactory", 2045, {RESEARCH: 0.002}, "Fábrica lunar", "Producir en la Luna con materiales de la Luna.", "Lunar Factory", "Making things on the Moon from lunar materials."),
("shipyard", 2055, {}, "Astillero orbital", "Construir y reparar naves interplanetarias en órbita.", "Orbital Shipyard", "Building and repairing interplanetary ships in orbit."),
("platform", 2065, {}, "Plataforma orbital gigante", "Una estructura de kilómetros, habitada y productiva.", "Giant Orbital Platform", "A kilometre-long structure, inhabited and productive."),
("elevator", 2075, {}, "Estudio del ascensor espacial", "Materiales y cálculos para un cable hasta la órbita. Es la investigación final de esta era.", "Space Elevator Study", "Materials and sums for a cable to orbit. It is the final research of this era."),
],
[
("navigation", 1990, {}, "Navegación interplanetaria", "Calcular rumbos entre planetas. Sin esto no sale ninguna sonda hacia la Luna ni más lejos.", "Interplanetary Navigation", "Working out courses between planets. Without it no probe leaves for the Moon or beyond."),
("gravityassist", 1995, {}, "Asistencia gravitatoria", "Usar la gravedad de los planetas para llegar más lejos. Abre Venus, Mercurio y Marte.", "Gravity Assist", "Using the planets' gravity to go further. Opens Venus, Mercury and Mars."),
("translunar", 2000, {}, "Inyección translunar", "Mandar una tripulación a la Luna y traerla de vuelta. Obligatoria para la misión tripulada.", "Translunar Injection", "Sending a crew to the Moon and bringing it back. Required for the crewed mission."),
("deepnet", 2005, {}, "Red de espacio profundo", "Antenas para hablar con naves muy lejanas. Obligatoria para Júpiter, Saturno y los asteroides.", "Deep Space Network", "Antennas to talk to very distant craft. Required for Jupiter, Saturn and the asteroids."),
("precisionland", 2010, {}, "Descenso de precisión", "Posarse a metros del lugar elegido. Obligatorio para las bases.", "Precision Landing", "Landing metres from the chosen spot. Required for bases."),
("aerobrake", 2015, {}, "Aerofrenado", "Frenar con la atmósfera en lugar de combustible. Obligatorio para bajar en Marte.", "Aerobraking", "Braking with the atmosphere instead of fuel. Required to land on Mars."),
("transithab", 2025, {}, "Hábitat de tránsito", "Vivir meses en el viaje. Obligatorio para los vuelos tripulados a Marte.", "Transit Habitat", "Living for months on the way. Required for crewed flights to Mars."),
("marstransfer", 2035, {}, "Ventana de transferencia a Marte", "Una tripulación que llega a Marte y vuelve. Obligatoria para pisar Marte.", "Mars Transfer Window", "A crew that reaches Mars and returns. Required to set foot on Mars."),
("venusfloat", 2040, {}, "Plataformas flotantes", "Globos en la atmósfera de Venus, a 50 km de altura. Abre la estación en Venus.", "Floating Platforms", "Balloons in Venus's atmosphere, 50 km up. Opens the Venus station."),
("asteroidnav", 2045, {}, "Encuentro con asteroides", "Acercarse y anclarse a un cuerpo diminuto. Abre el puesto en los asteroides.", "Asteroid Rendezvous", "Approaching and anchoring to a tiny body. Opens the asteroid outpost."),
("outerprop", 2055, {}, "Propulsión al sistema exterior", "Motores para llevar personas hasta las lunas de Júpiter. Abre Calisto.", "Outer System Propulsion", "Engines to take people to Jupiter's moons. Opens Callisto."),
("titanentry", 2065, {}, "Entrada en Titán", "Descender entre nieblas y lagos de metano. Abre la base en Titán.", "Titan Entry", "Descending through haze and methane lakes. Opens the Titan base."),
("solarnet", 2075, {}, "Red del sistema solar", "Comunicaciones y rutas entre todos los puestos humanos. Es el final de los viajes de esta era.", "Solar System Network", "Communications and routes between every human outpost. The end of this era's travel."),
],
]

def tid(t): return "mdr_sp_" + t
def spew(path, text, bom=False):
    d = os.path.dirname(path)
    if d: os.makedirs(d, exist_ok=True)
    with open(path, "wb") as f:
        f.write((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
def slurp(path):
    with open(path, "rb") as f:
        return f.read().decode("utf-8-sig")
def row(year): return (year - 1985) // 5 * 2

def cost(year): return round(1.25 + (year - 1985) * 0.03, 2)

# Flatten: id, year, x, parent list, children list, modifiers, icon, names.
children, position = {}, {}
position[ROOT[0]] = (6, row(ROOT[1]))
children[ROOT[0]] = []
for c, chain in enumerate(CHAINS):
    prev = None
    for i, t in enumerate(chain):
        position[t[0]] = (c * 3, row(t[1]))
        children.setdefault(t[0], [])
        if prev:
            children[prev].append(t[0])
        elif c == 3:
            children["tracking"].append(t[0])  # debris tracking grows from the tracking network
        else:
            children[ROOT[0]].append(t[0])
        prev = t[0]
ALL = [ROOT] + [t for chain in CHAINS for t in chain]
for t in ALL:
    if t[0] not in ICON or not MODS.get(t[0]):
        sys.exit("no icon or effect for " + t[0])


def save_dds(img, path):
    a = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w = a.shape[:2]
    head = struct.pack("<4s7I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1) + b"\0" * 44
    head += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000) + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(head + a[:, :, [2, 1, 0, 3]].tobytes())


# Icons: drawn by herramientas/make_space_tech_icons.py (one scene per technology); this script only checks they exist.
os.makedirs(OUT, exist_ok=True)
missing = [name for name in ICON if not os.path.exists(f"{OUT}tech_{name}.dds")]
if missing:
    sys.exit("run herramientas/make_space_tech_icons.py first; missing icons: " + ", ".join(missing))

# Background: Millennium Dawn's Earth and satellite picture, which it draws almost transparent: made stronger so it can be seen.
bg = Image.open(os.path.join(MD, "gfx/interface/techtree/network_centric_techtree_bg.dds")).convert("RGBA").resize((1190, 1075), Image.LANCZOS)
arr = np.array(bg, dtype=float)
arr[:, :, 3] = np.clip(arr[:, :, 3] * 3.4, 0, 135)
save_dds(Image.fromarray(arr.astype(np.uint8)), OUT + "mdr_space_techtree_bg.dds")

# Logos of the menu, Millennium Dawn's own: the real agency where it has one, and space ones anyone can pick.
LOGOS = {
    "usa": "gfx/interface/goals/united_states/nasa.dds",
    "sov": "gfx/interface/goals/00_economy/companies/roscosmos.dds",
    "chi": "gfx/interface/goals/china/space_combat_support_force.dds",
    "fra": "gfx/interface/goals/france/french_space_efforts.dds",
    "eng": "gfx/interface/goals/united_kingdom/British_Space.dds",
    "raj": "gfx/interface/goals/india/indian_rocket.dds",
    "isr": "gfx/interface/goals/israel_palestine/Jews_In_Space.dds",
    "any": SCI + "international_space_station.dds",
    "space": SCI + "generic_space.dds",
    "rocketry": SCI + "rocketry.dds",
    "orbit": SCI + "orbit_moon.dds",
    "moon": SCI + "land_on_moon.dds",
    "landmars": SCI + "land_on_mars.dds",
    "marsbase": SCI + "mars_base.dds",
    "mars": SCI + "mars.dds",
    "asteroid": SCI + "asteroid_mining.dds",
}
for name, src in LOGOS.items():
    logo = Image.open(os.path.join(MD, src)).convert("RGBA")
    logo = logo.crop(logo.getbbox())
    logo.thumbnail((100, 88), Image.LANCZOS)
    tile = Image.new("RGBA", (100, 88), (0, 0, 0, 0))
    tile.alpha_composite(logo, ((100 - logo.width) // 2, (88 - logo.height) // 2))
    save_dds(tile, f"{OUT}mdr_space_logo_{name}.dds")

# Tab: Millennium Dawn's missile tab, recoloured from purple to blue.
tab = np.array(Image.open(os.path.join(MD, "gfx/interface/techtree/ballistic_missile.dds")).convert("RGBA"), dtype=float) / 255
for y in range(tab.shape[0]):
    for x in range(tab.shape[1]):
        h, s, v = colorsys.rgb_to_hsv(*tab[y, x, :3])
        if s > 0.22 and 0.6 < h < 0.95:
            tab[y, x, :3] = colorsys.hsv_to_rgb(0.58, s * 0.8, min(v * 1.2, 1))
save_dds(Image.fromarray((tab * 255).astype(np.uint8), "RGBA"), OUT + "mdr_space_tab.dds")

out = "# Generated by herramientas/make_space.py. Tab \"Programa espacial\": everyone can research the foundations; the rest needs a space agency.\ntechnologies = {\n"
for t in ALL:
    name, year, mods = t[0], t[1], MODS[t[0]]
    x, y = position[name]
    out += f"\t{tid(name)} = {{\n\t\tresearch_cost = {cost(year)}\n\t\tstart_year = {year}\n\n"
    for k, v in mods.items():
        out += f"\t\t{k} = {v}\n"
    if name in ONCE:
        # Not for the technologies given at the start (mdr_space_start sets mdr_space_ready after them), in case set_technology runs this.
        out += f"\n\t\ton_research_complete = {{\n\t\t\tcustom_effect_tooltip = {tid(name)}_once\n\t\t\thidden_effect = {{\n\t\t\tif = {{ limit = {{ has_country_flag = mdr_space_ready }}\n\t\t\t" + ONCE[name] + "\n\t\t\t}\n\t\t\t}\n\t\t}\n"
    if name == ROOT[0]:
        out += "\n\t\tenable_building = {\n\t\t\tbuilding = mdr_spaceport\n\t\t\tlevel = 3\n\t\t}\n"
    if name != ROOT[0]:
        out += "\n\t\tallow = {\n\t\t\tcustom_trigger_tooltip = {\n\t\t\t\ttooltip = mdr_space_need_agency_tt\n\t\t\t\tcheck_variable = { mdr_space_tier > 0 }\n\t\t\t}\n\t\t}\n"
    for child in children[name]:
        out += f"\n\t\tpath = {{\n\t\t\tleads_to_tech = {tid(child)}\n\t\t\tresearch_cost_coeff = 1\n\t\t}}\n"
    out += f"\n\t\tfolder = {{\n\t\t\tname = {FOLDER}\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t}}\n\n\t\tcategories = {{\n\t\t\t{CATEGORY}\n\t\t}}\n"
    if name == ROOT[0]:
        out += "\n\t\tai_will_do = {\n\t\t\tfactor = 1\n\t\t\tmodifier = { factor = 0 check_variable = { gdp_total < 48 } }\n\t\t}\n\t}\n\n"
    else:
        out += "\n\t\tai_will_do = {\n\t\t\tfactor = 1\n\t\t\tmodifier = { factor = 0 check_variable = { mdr_space_tier < 1 } }\n\t\t\tmodifier = { factor = 0.5 check_variable = { mdr_space_tier < 2 } }\n\t\t}\n\t}\n\n"
out += "}\n"
spew("common/technologies/mdr_space.txt", out)

# Folder and category in a copy of Millennium Dawn's tags.
tags = slurp(f"{MD}/common/technology_tags/00_technology.txt")
tags, n1 = re.subn(r"(\n\tCAT_gnss\n)", rf"\1\t{CATEGORY}\n", tags, count=1)
tags, n2 = re.subn(r"(\n\tspace_folder = \{\s*\n\s*\}\n)", rf"\1\t{FOLDER} = {{\n\n\t}}\n", tags, count=1)
if n1 != 1 or n2 != 1:
    sys.exit("technology_tags changed")
spew("common/technology_tags/00_technology.txt", tags)


def block_at(text, start):
    """The balanced { } block that starts at the first brace after start."""
    i = text.index("{", start) + 1
    depth = 1
    while depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i]


# Sprites: the same frames as MD's space tab, and icons from MD's own files.
gfx_src = slurp(f"{MD}/interface/countrytechtreeview.gfx")
blocks = []
for m in re.finditer(r"(?i)(?:frameAnimatedSpriteType|spriteType)\s*=\s*\{", gfx_src):
    block = block_at(gfx_src, m.start())
    if "GFX_technology_space_folder_" in block:
        blocks.append(block.replace("GFX_technology_space_folder_", f"GFX_technology_{FOLDER}_"))
if len(blocks) < 8:
    sys.exit("space folder sprites not found")
gfx = "# Generated by herramientas/make_space.py.\nspriteTypes = {\n\tspriteType = {\n\t\tname = \"GFX_mdr_space_tab\"\n\t\ttextureFile = \"gfx/interface/mdr/space/mdr_space_tab.dds\"\n\t\tnoOfFrames = 2\n\t}\n\tspriteType = {\n\t\tname = \"GFX_mdr_space_techtree_bg\"\n\t\ttextureFile = \"gfx/interface/mdr/space/mdr_space_techtree_bg.dds\"\n\t\talwaystransparent = yes\n\t}\n"
for name in LOGOS:
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_logo_{name}"\n\t\ttextureFile = "gfx/interface/mdr/space/mdr_space_logo_{name}.dds"\n\t}}\n'
gfx += "".join("\t" + b + "\n" for b in blocks)
gfx += "".join(f"\tspriteType = {{ name = \"GFX_{tid(t[0])}_medium\" texturefile = \"gfx/interface/mdr/space/tech_{t[0]}.dds\" }}\n" for t in ALL)
gfx += "}\n"
spew("interface/mdr_space_techs.gfx", gfx)

# The tab in the research screen.
GUI = "interface/countrytechtreeview.gui"
g = slurp(GUI)
crlf = "\r\n" in g
g = g.replace("\r\n", "\n")
marks = [("\t\t# Realpolitik: space programme tab (herramientas/make_space.py).\n", "\t\t# Realpolitik: end of the space programme tab.\n"),
         ("\t\t\t# Realpolitik: space programme tab button.\n", "\t\t\t# Realpolitik: end of the tab button.\n"),
         ("\t# Realpolitik: space programme technology items.\n", "\t# Realpolitik: end of the space programme technology items.\n")]
for a, b in marks:
    g = re.sub(re.escape(a) + r".*?" + re.escape(b), "", g, flags=re.S)
TOP = 90
HEIGHT = TOP + (row(2075) + 2) * 70
blk = marks[0][0] + f"\t\tcontainerWindowType = {{\n\t\t\tname = \"{FOLDER}\"\n\t\t\tposition = {{ x = 0 y = 47 }}\n\t\t\tsize = {{ width = 100%% height = 100%% }}\n\t\t\tmargin = {{ top = 13 left = 13 bottom = 24 right = 25 }}\n\t\t\tdrag_scroll = {{ left middle }}\n\t\t\tverticalScrollbar = \"right_vertical_slider\"\n\t\t\thorizontalScrollbar = \"bottom_horizontal_slider\"\n\n\t\t\tbackground = {{\n\t\t\t\tname = \"Background\"\n\t\t\t\tquadTextureSprite =\"GFX_tiled_window_2b_border\"\n\t\t\t}}\n"
blk += f"\t\t\tcontainerWindowType = {{\n\t\t\t\tname = \"techtree_stripes\"\n\t\t\t\tposition = {{ x = 0 y = 0 }}\n\t\t\t\tsize = {{\n\t\t\t\t\twidth = 1400 height = {HEIGHT}\n\t\t\t\t\tmin = {{ width = 100%% height = 100%% }}\n\t\t\t\t}}\n\t\t\t\tclipping = no\n\t\t\t\ticonType = {{\n\t\t\t\t\tname = \"mdr_space_techtree_bg\"\n\t\t\t\t\tspriteType = \"GFX_mdr_space_techtree_bg\"\n\t\t\t\t\tposition = {{ x = 0 y = 0 }}\n\t\t\t\t}}\n\t\t\t}}\n"
for y in range(1985, 2080, 5):
    blk += f"\t\t\tinstantTextBoxType = {{\n\t\t\t\tname = \"mdr_space_year_{y}\"\n\t\t\t\tposition = {{ x = 40 y = {TOP + row(y) * 70 + 16} }}\n\t\t\t\tfont = \"hoi_36header\"\n\t\t\t\tborderSize = {{ x = 0 y = 4 }}\n\t\t\t\ttext = \"{y}\"\n\t\t\t\tmaxWidth = 110\n\t\t\t\tmaxHeight = 32\n\t\t\t\tformat = left\n\t\t\t\tOrientation = \"UPPER_LEFT\"\n\t\t\t}}\n"
for i in range(len(COLUMNS)):
    blk += f"\t\t\tinstantTextBoxType = {{\n\t\t\t\tname = \"mdr_space_column_{i}\"\n\t\t\t\tposition = {{ x = {150 + i * 210 + 35 - 102} y = 6 }}\n\n\t\t\t\tfont = \"hoi_33\"\n\t\t\t\tborderSize = {{ x = 0 y = 4 }}\n\t\t\t\ttext = \"MDR_SPACE_COLUMN_{i}\"\n\t\t\t\tmaxWidth = 205\n\t\t\t\tmaxHeight = 74\n\t\t\t\tformat = center\n\t\t\t\tOrientation = \"UPPER_LEFT\"\n\t\t\t}}\n"
# A grid centres its content in its width, so it is exactly one slot wide and the slots count from its position.
blk += f"\t\t\tgridboxtype = {{\n\t\t\t\tname = \"{tid(ROOT[0])}_tree\"\n\t\t\t\tposition = {{ x = 150 y = {TOP} }}\n\t\t\t\tsize = {{ width = 70 height = {HEIGHT} }}\n\t\t\t\tslotsize = {{ width = 70 height = 70 }}\n\t\t\t\tformat = \"UP\"\n\t\t\t}}\n\t\t}}\n" + marks[0][1]
anchor = "\t\tcontainerWindowType = {\n\t\t\tname = \"cruise_missiles_folder\""
if anchor not in g:
    sys.exit("anchor cruise_missiles_folder not found")
g = g.replace(anchor, blk + anchor, 1)
tab = marks[1][0] + f"\t\t\tbuttonType = {{\n\t\t\t\tname = \"{FOLDER}_tab\"\n\t\t\t\tposition = {{ x = 1025 y = 0 }}\n\t\t\t\tquadTextureSprite = \"GFX_mdr_space_tab\"\n\t\t\t\tframe = 1\n\t\t\t\tclicksound = ui_research_tab_engineering\n\t\t\t}}\n" + marks[1][1]
anchor2 = "\t\t\t#These need to be here for dumb tutorial reasons\n"
if anchor2 not in g:
    sys.exit("tab anchor not found")
g = g.replace(anchor2, tab + "\n" + anchor2, 1)
# The game draws each technology with techtree_<folder>_item and _small_item: copies of the space folder's.
items = ""
for suffix in ("small_item", "item"):
    m = re.search(r"\tcontainerWindowType = \{\s*\n\s*name = \"techtree_space_folder_" + suffix + "\"", g)
    if not m:
        sys.exit("item template not found: " + suffix)
    items += "\t" + block_at(g, m.start() + 1).replace("techtree_space_folder_", f"techtree_{FOLDER}_") + "\n"
m = re.search(r"\tcontainerWindowType = \{\s*\n\s*name = \"techtree_space_folder_small_item\"", g)
g = g[:m.start()] + marks[2][0] + items + marks[2][1] + g[m.start():]
spew(GUI, g.replace("\n", "\r\n") if crlf else g)

# Effects and texts that follow the list.
e = "# Generated by herramientas/make_space.py. Country scope. Output: variable mdr_space_techs, technologies researched in the tab.\nmdr_space_count_techs = {\n\tset_variable = { mdr_space_techs = 0 }\n"
e += "".join(f"\tif = {{ limit = {{ has_tech = {tid(t[0])} }} add_to_variable = {{ mdr_space_techs = 1 }} }}\n" for t in ALL)
e += "}\n"
spew("common/scripted_effects/mdr_space_techs.txt", e)
order = sorted(ALL, key=lambda t: t[1])
sl = "# Generated by herramientas/make_space.py. The next technology of the tab, oldest first.\ndefined_text = {\n\tname = mdr_space_next_tech\n"
sl += "".join(f"\ttext = {{\n\t\ttrigger = {{ NOT = {{ has_tech = {tid(t[0])} }} }}\n\t\tlocalization_key = {tid(t[0])}\n\t}}\n" for t in order)
sl += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_ALL_TECHS\n\t}\n}\n"
spew("common/scripted_localisation/mdr_space_techs_loc.txt", sl)
for lang, ni, ti, fname, fdesc, ci in (
    ("spanish", 3, 4, "Programa espacial", "Lanzadores, vuelo tripulado, industria y defensa en órbita. Los satélites siguen en su propia pestaña.", 0),
    ("english", 5, 6, "Space Programme", "Launchers, crewed flight, orbital industry and defense. Satellites keep their own tab.", 1)):
    y = f"l_{lang}:\n {FOLDER}: \"{fname}\"\n {FOLDER}_desc: \"{fdesc}\"\n {CATEGORY}: \"{fname}\"\n {CATEGORY}_research: \"{fname}\"\n MDR_SPACE_TECH_TOTAL: \"{len(ALL)}\"\n"
    for i, c in enumerate(COLUMNS):
        y += f" MDR_SPACE_COLUMN_{i}: \"{c[ci]}\"\n"
    es = lang == "spanish"
    for t in ALL:
        need = f"t:{t[0]}"
        opened = [a[2 if es else 3] for a, _ in space_program.ACTIONS if need in a[9]]
        extra = ""
        if t[0] == ROOT[0]:
            extra = "\\n\\n§Y" + ("Abre:§! crear la agencia espacial y construir cosmódromos." if es else "Opens:§! creating the space agency and building spaceports.")
        if opened:
            extra += "\\n\\n§Y" + ("Abre en el menú del programa:§! " if es else "Opens in the programme menu:§! ") + ", ".join(opened) + "."
        y += f" {tid(t[0])}: \"{t[ni]}\"\n {tid(t[0])}_desc: \"{t[ti]}{extra}\"\n"
        if t[0] in ONCE_TEXT:
            y += f" {tid(t[0])}_once: \"§G{'Al terminarla, una vez' if es else 'When finished, once'}:§! {ONCE_TEXT[t[0]][0 if es else 1]}\"\n"
    spew(f"localisation/{lang}/mdr_space_techs_l_{lang}.yml", y, bom=True)
print("ok", len(ALL), "technologies,", len(blocks), "sprites copied")
