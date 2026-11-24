# Colony view, built like Millennium Dawn's Antarctic station: a blueprint with slots of four shapes. A slot is chosen
# on the plan, a module picked with the arrows on the right, and sent to be built; it takes weeks and then shows on its
# slot. Each colony (Moon, Mars, Venus, Mercury, the asteroids, Callisto and Titan) has its own plan colour, module names,
# costs and sunlight. The code below is written for Mars (mdr_mars, MDR_MARS); emit() renames it for each colony.
# Uses MD's Antarctic art (plan, slots, module frame, module pictures), coloured and resized here.
# Writes: common/scripted_effects/mdr_space_colony.txt, common/scripted_triggers/mdr_space_colony_triggers.txt,
# common/scripted_guis/mdr_space_colony_gui.txt, interface/mdr_space_colony.gui and .gfx,
# common/scripted_localisation/mdr_space_colony_loc.txt, localisation/*/mdr_space_colony_l_*.yml and gfx/interface/mdr/space/colony/.
# Run from the mod folder: python herramientas/space_colony.py (make_space_gui.py runs it too).
import os
import sys

sys.path.insert(0, "herramientas")
import numpy as np
from PIL import Image, ImageDraw
import space_program as sp
import space_theme as theme

T = "\t"
ART = "../Millennium-Dawn-2.0.3/gfx/interface/scripted_gui/antarctica/"
PHOTO = "../Millennium-Dawn-2.0.3/gfx/event_pictures/generic/space_stuff/"
OUT = "gfx/interface/mdr/space/colony/"
P = "mdr_col_mars"
V = "mdr_mars"
# Window: centred, draggable.
W, H = 1240, 720
PLAN_X, PLAN_Y, SCALE = 290, 60, 0.7

# Slots of MD's station: id, shape (1 hexagon, 2 diamond, 3 square, 4 turned square) and place, as in MD_countrymissilesview.gui
# (plan at x 296, y 5); then what opens it (None: open from the start).
SLOTS = [
    (1, 1, 459, 352, None), (2, 2, 531, 282, None), (5, 1, 678, 350, None), (7, 1, 570, 161, None), (13, 4, 860, 283, None),
    (6, 1, 569, 539, "h:3"), (8, 1, 788, 160, "h:3"), (11, 3, 710, 203, "p:20"), (14, 4, 532, 475, "p:20"),
    (9, 1, 788, 539, "h:4"), (10, 1, 897, 350, "h:4"), (4, 2, 859, 471, "t:surface"), (12, 3, 711, 582, "t:printing"),
]
LARGE_SHAPES = (1,)
# Modules of Mars: id, size (L: hexagons, S: the small ones), Spanish, English, what it is (es, en), cost $B, weeks,
# requirement, effect (counter it adds to), MD picture (in station_modules/), and what it gives (es, en).
BASE_MODULES = [
    ("hab", "L", "Hábitat presurizado", "Pressurised Habitat", "Módulos enterrados bajo regolito contra la radiación.", "Modules buried under regolith against radiation.", 1.8, 20, None, "hab", "modular_and_container_buildings", "+8 colonos de capacidad", "+8 settler capacity"),
    ("greenhouse", "L", "Invernadero", "Greenhouse", "Cultivos con luz artificial y agua reciclada.", "Crops under artificial light with recycled water.", 2.6, 26, "t:lifesupport", "greenhouse", "greenhouse", "+0,9 de comida por semana", "+0.9 food a week"),
    ("drill", "L", "Perforadora de hielo", "Ice Drill", "Saca hielo del subsuelo: agua para beber y oxígeno.", "Mines subsurface ice: water to drink and oxygen.", 2.2, 22, None, "mine", "ice_core_deep_drilling_rig", "+0,8 de agua y de oxígeno por semana", "+0.8 water and oxygen a week"),
    ("lab", "L", "Laboratorio de radiación", "Radiation Laboratory", "Estudia el suelo, el clima y la radiación del lugar.", "Studies the place's soil, weather and radiation.", 3.1, 28, "t:radiation", "lab", "radiation_laboratory", "+0,6 de ciencia por semana", "+0.6 science a week"),
    ("workshop", "L", "Taller de fabricación", "Fabrication Workshop", "Imprime piezas y herramientas con material local.", "Prints parts and tools from local material.", 3.4, 30, "t:printing", "workshop", "elevated_buildings", "+0,3% de producción de fábricas", "+0.3% factory output"),
    ("medical", "L", "Centro médico", "Medical Centre", "Cirugía, rehabilitación y salud mental lejos de casa.", "Surgery, rehabilitation and mental health far from home.", 2.4, 24, "t:deepmission", "medical", "extreme_environment_medical_center", "+1,5 de moral por semana", "+1.5 morale a week"),
    ("quarters", "L", "Viviendas amplias", "Spacious Quarters", "Lugar para familias, con ventanas y espacio común.", "Room for families, with windows and common space.", 3.8, 32, "t:surface", "quarters", "premium_living_quarters", "+12 colonos de capacidad y +0,5 de moral", "+12 settler capacity and +0.5 morale"),
    ("solar", "S", "Paneles solares", "Solar Arrays", "Paneles finos que se limpian del polvo solos.", "Thin arrays that shake off the dust.", 1.2, 12, None, "solar", "kyocera_kc130ght_2", "+0,6 de energía por semana", "+0.6 energy a week"),
    ("reactor", "S", "Reactor de superficie", "Surface Reactor", "Un reactor de fisión chico: energía en tormentas de polvo.", "A small fission reactor: power through dust storms.", 2.9, 24, "t:fission", "reactor", "caterpillar_3512B", "+1,1 de energía por semana", "+1.1 energy a week"),
    ("moxie", "S", "Planta de oxígeno", "Oxygen Plant", "Saca oxígeno de lo que haya a mano: aire, suelo o hielo.", "Makes oxygen from whatever is at hand: air, soil or ice.", 1.9, 18, "t:regolith", "moxie", "extra_heat_recovery_system", "+1 de oxígeno por semana", "+1 oxygen a week"),
    ("fuel", "S", "Planta de combustible", "Propellant Plant", "Metano y oxígeno líquidos para el viaje de vuelta.", "Liquid methane and oxygen for the trip home.", 3.6, 30, "t:marsfuel", "fuel", "large_fuel_tank_farm", "-3% de costo de lanzadores", "-3% launcher cost"),
]
# Short names for the list of modules installed.
SHORT = {"hab": ("Hábitats", "Habitats"), "greenhouse": ("Invernaderos", "Greenhouses"), "drill": ("Perforadoras", "Drills"), "lab": ("Laboratorios", "Laboratories"),
         "workshop": ("Talleres", "Workshops"), "medical": ("Centros médicos", "Medical centres"), "quarters": ("Viviendas", "Quarters"),
         "solar": ("Paneles", "Arrays"), "reactor": ("Reactores", "Reactors"), "moxie": ("Oxígeno", "Oxygen plants"), "fuel": ("Combustible", "Propellant")}
# Weekly production of the counters that are new (the old ones, greenhouse, mine and reactor, are in space_program.py).
NEW_COUNTERS = {"solar": ("energy", 0.6), "moxie": ("oxygen", 1.0)}

# Colonies: key, Spanish and English name (for titles), MD picture for the card, plan colours (dark, light) and glow,
# settlers when founded, settler trip cost, cargo route cost a week ($B), cost and time factors (far is dearer and slower),
# sunlight on the arrays (1 = the Moon), planet sprite, body number in the solar map, and per-module changes:
# id -> (Spanish name, English name, Spanish text, English text, requirement or None to keep it).
COLONIES = [
    ("moon", "Luna", "Moon", "moonbase", (54, 56, 62), (226, 228, 234), (0.9, 0.95, 1.05), 40, 0.4, 0.09, 0.45, 0.7, 1.0, "moon", 4, {
        "drill": ("Extracción de hielo polar", "Polar Ice Extraction", "Hielo de los cráteres en sombra eterna del polo sur.", "Ice from the permanently shadowed craters of the south pole.", "t:lunarice"),
        "lab": ("Observatorio lunar", "Lunar Observatory", "Radiotelescopios en la cara oculta, lejos del ruido de la Tierra.", "Radio telescopes on the far side, away from Earth's noise.", None),
        "moxie": ("Planta de oxígeno del regolito", "Regolith Oxygen Plant", "Calienta el suelo lunar para soltar su oxígeno.", "Heats lunar soil to release its oxygen.", None),
        "fuel": ("Catapulta electromagnética", "Mass Driver", "Lanza carga desde la Luna sin cohetes.", "Throws cargo off the Moon without rockets.", "t:massdriver"),
    }),
    ("mars", "Marte", "Mars", "mars_colony_1", (92, 42, 28), (250, 214, 186), (1.3, 0.72, 0.52), 24, 1.4, 0.34, 1.0, 1.0, 0.6, "mars", 5, {}),
    ("venus", "Venus", "Venus", "mars_colony_5", (96, 74, 30), (250, 232, 168), (1.25, 1.05, 0.55), 16, 1.6, 0.41, 1.15, 1.05, 1.6, "venus", 2, {
        "hab": ("Góndola habitable", "Habitable Gondola", "Flota a 50 km de altura, con presión y temperatura de la Tierra.", "Floats 50 km up, at Earth's pressure and temperature.", None),
        "greenhouse": ("Invernadero de nubes", "Cloud Greenhouse", "Cultivos colgados bajo el globo, con luz de sobra.", "Crops hung under the balloon, with light to spare.", None),
        "drill": ("Extractor de agua del aire", "Atmospheric Water Extractor", "Saca agua de las nubes de ácido sulfúrico.", "Pulls water out of the sulphuric acid clouds.", "t:venusfloat"),
        "moxie": ("Planta de oxígeno del CO2", "CO2 Oxygen Plant", "La atmósfera es casi todo dióxido de carbono.", "The atmosphere is nearly all carbon dioxide.", None),
        "fuel": ("Planta de propelente", "Propellant Plant", "Combustible hecho con el aire para volver a la órbita.", "Fuel made from the air to climb back to orbit.", None),
    }),
    ("mercury", "Mercurio", "Mercury", "mars_colony_14", (60, 52, 46), (232, 216, 196), (1.15, 0.95, 0.75), 12, 1.9, 0.52, 1.3, 1.15, 2.2, "mercury", 1, {
        "drill": ("Mina de hielo polar", "Polar Ice Mine", "Hielo en cráteres del polo que nunca ven el Sol.", "Ice in polar craters that never see the Sun.", None),
        "workshop": ("Fundición de metales", "Metal Foundry", "Funde el suelo rico en metales con la luz del Sol.", "Melts the metal-rich soil with sunlight.", None),
        "solar": ("Campo solar", "Solar Field", "Cerca del Sol, cada panel rinde más del doble.", "Close to the Sun, each array yields more than twice.", None),
    }),
    ("asteroids", "Asteroides", "Asteroids", "asteroid", (50, 54, 60), (214, 220, 230), (0.85, 0.92, 1.1), 14, 1.3, 0.38, 1.05, 1.0, 0.4, "asteroids", 6, {
        "drill": ("Minería de agua", "Water Mining", "Saca agua y volátiles de un asteroide carbonáceo.", "Takes water and volatiles from a carbonaceous asteroid.", "t:asteroidmining"),
        "workshop": ("Refinería de metales", "Metal Refinery", "Hierro, níquel y metales del grupo del platino.", "Iron, nickel and platinum-group metals.", None),
        "quarters": ("Anillo giratorio", "Spinning Ring", "Gravedad artificial para vivir años sin perder hueso.", "Artificial gravity to live for years without bone loss.", "t:gravity"),
    }),
    ("callisto", "Calisto", "Callisto", "mars_colony_20", (40, 50, 64), (200, 214, 234), (0.75, 0.88, 1.2), 18, 2.6, 0.74, 1.7, 1.35, 0.15, "jupiter", 7, {
        "drill": ("Perforadora de hielo de Calisto", "Callisto Ice Drill", "La luna es mitad hielo: agua y oxígeno de sobra.", "The moon is half ice: water and oxygen to spare.", None),
        "lab": ("Observatorio de Júpiter", "Jupiter Observatory", "Estudia Júpiter y sus lunas desde fuera de su radiación.", "Studies Jupiter and its moons from outside its radiation.", None),
        "solar": ("Paneles de gran superficie", "Large Arrays", "A esta distancia el Sol da 4% de lo que da en la Tierra.", "At this distance the Sun gives 4% of what it gives at Earth.", None),
    }),
    ("titan", "Titán", "Titan", "mars_colony_6", (90, 58, 26), (246, 206, 140), (1.3, 0.9, 0.5), 18, 3.1, 0.88, 1.95, 1.5, 0.05, "saturn", 8, {
        "drill": ("Bomba de hielo y metano", "Ice and Methane Pump", "Hielo de agua bajo lagos de metano líquido.", "Water ice under lakes of liquid methane.", None),
        "fuel": ("Planta de metano de Titán", "Titan Methane Plant", "Combustible tomado directo de los lagos.", "Fuel taken straight from the lakes.", None),
        "solar": ("Paneles bajo la niebla", "Arrays under the Haze", "Casi no llega luz: mejor un reactor.", "Hardly any light gets through: better a reactor.", None),
    }),
]
COLONY = None
# "de la Luna", "de los asteroides": the colony's name after "de" in Spanish, and in English with "the" where it goes.
OF = {"moon": ("la Luna", "the Moon"), "asteroids": ("los asteroides", "the asteroid")}


def of(colony, idx):
    return OF.get(colony[0], (colony[1], colony[2]))[idx]


def setup(colony):
    # Points the module-level names at one colony: its modules with their own names, costs, times and sunlight.
    global COLONY, P, MODULES, NEW_COUNTERS
    COLONY = colony
    key, _, _, _, _, _, _, _, _, _, cost_k, weeks_k, sun, _, _, changes = colony
    P = f"mdr_col_{key}"
    MODULES = []
    for m in BASE_MODULES:
        m = list(m)
        if m[0] in changes:
            es, en, des, den, r = changes[m[0]]
            m[2], m[3], m[4], m[5] = es, en, des, den
            if r:
                m[8] = r
        m[6] = round(m[6] * cost_k, 1)
        m[7] = max(6, round(m[7] * weeks_k))
        if m[0] == "solar":
            out = round(sun, 2)
            m[11], m[12] = f"+{sp.number(out, 'spanish')} de energía por semana", f"+{sp.number(out, 'english')} energy a week"
        MODULES.append(tuple(m))
    NEW_COUNTERS = {"solar": ("energy", round(sun, 2)), "moxie": ("oxygen", 1.0)}


BUF = {}


def emit(path, text):
    # Collects every colony's output in one file per path, renaming the Mars code for the current colony.
    key = COLONY[0]
    text = text.replace("mdr_mars", f"mdr_{key}").replace("MDR_MARS", f"MDR_{key.upper()}").replace("plan_mars", f"plan_{key}").replace("card_mars", f"card_{key}")
    text = text.replace("MDRX_", "mdr_")
    BUF.setdefault(path, []).append(text)


def mid(m):
    return MODULES.index(m) + 1


def by_size(size):
    return [m for m in MODULES if m[1] == size]


def size_of(shape):
    return "L" if shape in LARGE_SHAPES else "S"


def req(r):
    if r is None:
        return "always = yes"
    kind, value = r.split(":")
    if kind == "p":
        return f"check_variable = {{ {P}_pop > {int(value) - 1} }}"
    return sp.req_trigger(r)


def req_text(r, lang):
    es = lang == "spanish"
    kind, value = r.split(":")
    if kind == "p":
        return f"{value} {'colonos' if es else 'settlers'}"
    return sp.req_loc(r, lang)


# ---- Logic.
def logic():
    s = "# Generated by herramientas/space_colony.py. Mars colony: mdr_mars_s<slot> is the module built there (0: none),\n# mdr_mars_s<slot>_job the one being built and mdr_mars_s<slot>_left its weeks. mdr_mars_n_<module> counts them.\n\n"
    s += f"# When the Martian base is founded: the first habitat already stands on slot 1.\n{V}_start = {{\n\tset_variable = {{ {V}_s1 = {mid(MODULES[0])} }}\n\tset_variable = {{ {V}_n_hab = 1 }}\n\tset_variable = {{ {V}_sel = 1 }}\n\tset_variable = {{ {V}_view = 1 }}\n}}\n\n"
    # Start building the chosen module on the chosen slot.
    s += f"{V}_build = {{\n"
    for slot in SLOTS:
        n = slot[0]
        for m in MODULES:
            s += f"\tif = {{ limit = {{ check_variable = {{ {V}_sel = {n} }} check_variable = {{ {V}_view = {mid(m)} }} }}\n\t\tset_variable = {{ {V}_s{n}_job = {mid(m)} }}\n\t\tset_variable = {{ {V}_s{n}_left = {m[7]} }}\n"
            s += f"\t\tset_temp_variable = {{ treasury_change = -{m[6]} }}\n\t\tsubtract_from_variable = {{ mdr_space_spend_0 = treasury_change }}\n\t\tmodify_treasury_effect = yes\n\t}}\n"
    s += "\tadd_to_variable = { global.international_systems_updated = 1 }\n}\n\n"
    # What a module gives when it is finished.
    s += f"# Temp variable {V}_done: the module just finished.\n{V}_apply = {{\n"
    for m in MODULES:
        eff = m[9]
        s += f"\tif = {{ limit = {{ check_variable = {{ {V}_done = {mid(m)} }} }}\n\t\tadd_to_variable = {{ {V}_n_{m[0]} = 1 }}\n"
        if eff == "hab":
            s += f"\t\tadd_to_variable = {{ {P}_cap = 8 }}\n"
        elif eff == "quarters":
            s += f"\t\tadd_to_variable = {{ {P}_cap = 12 }}\n"
        elif eff in ("greenhouse", "mine", "reactor", "workshop"):
            s += f"\t\tadd_to_variable = {{ {P}_{eff} = 1 }}\n"
        elif eff == "fuel":
            s += "\t\tadd_to_variable = { mdr_sm_olv_c = -0.03 }\n"
        s += "\t}\n"
    s += "}\n\n"
    # Weekly: works go on with the engineers' speed; the new modules produce.
    s += f"# Country scope, weekly, with a Mars colony.\n{V}_weekly = {{\n\tset_temp_variable = {{ {V}_speed = mdr_space_engineers }}\n\tdivide_temp_variable = {{ {V}_speed = 2000 }}\n\tadd_to_temp_variable = {{ {V}_speed = 1 }}\n\tset_variable = {{ {V}_jobs = 0 }}\n"
    for slot in SLOTS:
        n = slot[0]
        s += f"\tif = {{ limit = {{ check_variable = {{ {V}_s{n}_job > 0 }} }}\n\t\tadd_to_variable = {{ {V}_jobs = 1 }}\n\t\tsubtract_from_variable = {{ {V}_s{n}_left = {V}_speed }}\n"
        s += f"\t\tif = {{ limit = {{ check_variable = {{ {V}_s{n}_left < 0.01 }} }}\n\t\t\tset_variable = {{ {V}_s{n} = {V}_s{n}_job }}\n\t\t\tset_temp_variable = {{ {V}_done = {V}_s{n}_job }}\n\t\t\tset_variable = {{ {V}_s{n}_job = 0 }}\n\t\t\t{V}_apply = yes\n\t\t}}\n\t}}\n"
    for counter, (supply, k) in NEW_COUNTERS.items():
        s += f"\tset_temp_variable = {{ {V}_made = {V}_n_{counter} }}\n\tmultiply_temp_variable = {{ {V}_made = {k} }}\n\tadd_to_variable = {{ {P}_{supply} = {V}_made }}\n"
    s += f"\tset_variable = {{ {V}_science = {V}_n_lab }}\n\tmultiply_variable = {{ {V}_science = 0.6 }}\n\tadd_to_variable = {{ mdr_space_science = {V}_science }}\n"
    s += f"\tset_temp_variable = {{ {V}_cheer = {V}_n_medical }}\n\tmultiply_temp_variable = {{ {V}_cheer = 1.5 }}\n\tset_temp_variable = {{ {V}_cheer2 = {V}_n_quarters }}\n\tmultiply_temp_variable = {{ {V}_cheer2 = 0.5 }}\n\tadd_to_temp_variable = {{ {V}_cheer = {V}_cheer2 }}\n"
    s += f"\tadd_to_variable = {{ {P}_morale = {V}_cheer }}\n\tif = {{ limit = {{ check_variable = {{ {P}_morale > 100 }} }} set_variable = {{ {P}_morale = 100 }} }}\n"
    s += f"\t{V}_figures = yes\n}}\n\n"
    # Figures for the window.
    s += f"{V}_figures = {{\n\tset_variable = {{ {V}_built = 0 }}\n"
    for m in MODULES:
        s += f"\tadd_to_variable = {{ {V}_built = {V}_n_{m[0]} }}\n"
    s += f"\tset_variable = {{ {V}_science_total = {P}_pop }}\n\tmultiply_variable = {{ {V}_science_total = 0.09 }}\n\tset_temp_variable = {{ {V}_lab_science = {V}_n_lab }}\n\tmultiply_temp_variable = {{ {V}_lab_science = 0.6 }}\n\tadd_to_variable = {{ {V}_science_total = {V}_lab_science }}\n"
    for counter, (supply, k) in NEW_COUNTERS.items():
        s += f"\tset_temp_variable = {{ {V}_made = {V}_n_{counter} }}\n\tmultiply_temp_variable = {{ {V}_made = {k} }}\n\tadd_to_variable = {{ {P}_{supply}_net = {V}_made }}\n"
    s += "\tadd_to_variable = { global.international_systems_updated = 1 }\n}\n\n"
    # Choosing a slot shows its module, or the first one that fits it.
    s += f"{V}_select = {{\n"
    for slot in SLOTS:
        n, first = slot[0], mid(by_size(size_of(slot[1]))[0])
        s += f"\tif = {{ limit = {{ check_variable = {{ {V}_sel = {n} }} }}\n\t\tset_variable = {{ {V}_view = {first} }}\n\t\tif = {{ limit = {{ check_variable = {{ {V}_s{n} > 0 }} }} set_variable = {{ {V}_view = {V}_s{n} }} }}\n\t\tif = {{ limit = {{ check_variable = {{ {V}_s{n}_job > 0 }} }} set_variable = {{ {V}_view = {V}_s{n}_job }} }}\n\t}}\n"
    s += "\tadd_to_variable = { global.international_systems_updated = 1 }\n}\n\n"
    # Arrows: the next or previous module of the same size.
    for name, step in (("next", 1), ("prev", -1)):
        s += f"{V}_{name} = {{\n"
        first = True
        for size in ("L", "S"):
            group = by_size(size)
            for i, m in enumerate(group):
                to = group[(i + step) % len(group)]
                s += f"\t{'if' if first else 'else_if'} = {{ limit = {{ check_variable = {{ {V}_view = {mid(m)} }} }} set_variable = {{ {V}_view = {mid(to)} }} }}\n"
                first = False
        s += "\tadd_to_variable = { global.international_systems_updated = 1 }\n}\n\n"
    # Automatic mode and AI: one work at a time, the module the colony needs most, on the first free slot that fits.
    s += f"# Automatic mode and AI: builds what the colony lacks most, one work at a time, keeping the reserve.\n{V}_auto = {{\n\tif = {{ limit = {{ check_variable = {{ {V}_jobs < 1 }} }}\n"
    s += f"\t\tset_temp_variable = {{ {V}_want_l = {mid(MODULES[3])} }}\n"
    wants_l = [(f"check_variable = {{ var = {P}_pop compare = greater_than_or_equals value = {V}_room }}", "hab"), (f"check_variable = {{ {P}_morale < 50 }}", "medical"), (f"check_variable = {{ {P}_water < 40 }}", "drill"), (f"check_variable = {{ {P}_food < 40 }}", "greenhouse")]
    s += f"\t\tset_temp_variable = {{ {V}_room = {P}_cap }}\n\t\tadd_to_temp_variable = {{ {V}_room = -4 }}\n"
    for cond, mod in reversed(wants_l):
        m = next(x for x in MODULES if x[0] == mod)
        s += f"\t\tif = {{ limit = {{ {cond} {req(m[8])} }} set_temp_variable = {{ {V}_want_l = {mid(m)} }} }}\n"
    s += f"\t\tset_temp_variable = {{ {V}_want_s = {mid(next(x for x in MODULES if x[0] == 'solar'))} }}\n"
    for cond, mod in ((f"check_variable = {{ {P}_oxygen < 40 }}", "moxie"), (f"check_variable = {{ {P}_energy < 40 }}", "reactor")):
        m = next(x for x in MODULES if x[0] == mod)
        s += f"\t\tif = {{ limit = {{ {cond} {req(m[8])} }} set_temp_variable = {{ {V}_want_s = {mid(m)} }} }}\n"
    s += f"\t\tset_temp_variable = {{ {V}_started = 0 }}\n"
    for slot in SLOTS:
        n, size = slot[0], size_of(slot[1])
        want = f"{V}_want_{size.lower()}"
        s += f"\t\tif = {{ limit = {{ check_variable = {{ {V}_started = 0 }} {V}_slot_{n}_free = yes }}\n\t\t\tset_variable = {{ {V}_sel = {n} }}\n\t\t\tset_variable = {{ {V}_view = {want} }}\n"
        s += f"\t\t\tif = {{ limit = {{ {V}_can_build = yes }} {V}_build = yes set_temp_variable = {{ {V}_started = 1 }} }}\n\t\t}}\n"
    s += "\t}\n}\n"
    emit("common/scripted_effects/mdr_space_colony.txt", s)

    # Triggers.
    t = "# Generated by herramientas/space_colony.py.\n"
    for slot in SLOTS:
        n = slot[0]
        t += f"{V}_slot_{n}_open = {{\n\t{req(slot[4])}\n}}\n\n"
        t += f"{V}_slot_{n}_free = {{\n\t{V}_slot_{n}_open = yes\n\tNOT = {{ check_variable = {{ {V}_s{n} > 0 }} }}\n\tNOT = {{ check_variable = {{ {V}_s{n}_job > 0 }} }}\n}}\n\n"
    for m in MODULES:
        t += f"{V}_module_{m[0]}_ready = {{\n\t{req(m[8])}\n}}\n\n"
    # The chosen module fits the chosen slot, is researched, and can be paid keeping a little money.
    t += f"{V}_can_build = {{\n\tOR = {{\n"
    for slot in SLOTS:
        n = slot[0]
        mods = " ".join(f"AND = {{ check_variable = {{ {V}_view = {mid(m)} }} {V}_module_{m[0]}_ready = yes check_variable = {{ treasury > {m[6]} }} }}" for m in by_size(size_of(slot[1])))
        t += f"\t\tAND = {{ check_variable = {{ {V}_sel = {n} }} {V}_slot_{n}_free = yes OR = {{ {mods} }} }}\n"
    t += "\t}\n}\n"
    emit("common/scripted_triggers/mdr_space_colony_triggers.txt", t)


# ---- Art.
def save(img, name):
    from make_space_icons import save_dds
    save_dds(img, OUT + name + ".dds")


def tint_plan():
    # MD's blueprint in the colony's colours: its lines and grid lighten, its blue takes the ground's colour.
    a = np.array(Image.open(ART + "antarctic_station_bp.dds").convert("RGBA"), dtype=float)
    lum = a[:, :, :3].mean(axis=2, keepdims=True) / 255
    dark, light = np.array(COLONY[4], dtype=float), np.array(COLONY[5], dtype=float)
    a[:, :, :3] = dark + (light - dark) * np.clip((lum - 0.25) * 1.6, 0, 1)
    plan = Image.fromarray(a.astype(np.uint8))
    size = (round(plan.width * SCALE), round(plan.height * SCALE))
    glow = Image.open(ART + "antarctic_station_glow.dds").convert("RGBA").resize((round(926 * SCALE), round(926 * SCALE)), Image.LANCZOS)
    g = np.array(glow, dtype=float)
    g[:, :, :3] *= np.array(COLONY[6])
    out = Image.new("RGBA", (size[0] + 20, size[1] + 20), (0, 0, 0, 0))
    out.alpha_composite(Image.fromarray(np.clip(g, 0, 255).astype(np.uint8)).crop((0, 0, size[0] + 20, size[1] + 20)), (0, 0))
    out.alpha_composite(plan.resize(size, Image.LANCZOS), (8, 8))
    return out


def slot_art(shape, kind):
    src = Image.open(ART + f"antarctic_station_module_slot_{shape}.dds").convert("RGBA")
    img = src.resize((round(src.width * SCALE), round(src.height * SCALE)), Image.LANCZOS)
    a = np.array(img, dtype=float)
    if kind == "locked":
        a[:, :, :3] = a[:, :, :3].mean(axis=2, keepdims=True) * 0.32
    elif kind == "built":
        a[:, :, :3] = a[:, :, :3] * np.array([0.78, 0.62, 0.5])
    elif kind == "work":
        # Building site: the slot with yellow and black stripes.
        yy, xx = np.mgrid[0:a.shape[0], 0:a.shape[1]]
        stripe = ((xx + yy) // 7) % 2 == 0
        a[:, :, :3] = np.where(stripe[:, :, None], np.array([226, 182, 52.0]), np.array([46, 40, 34.0])) * 0.85 + a[:, :, :3] * 0.15
    elif kind == "ring":
        alpha = a[:, :, 3] > 40
        edge = alpha & ~(np.roll(alpha, 3, 0) & np.roll(alpha, -3, 0) & np.roll(alpha, 3, 1) & np.roll(alpha, -3, 1))
        a[:, :, :3] = theme.ACCENT
        a[:, :, 3] = np.where(edge, 255, 0)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def module_art(m, size):
    if size == "frame":
        img = Image.open(ART + f"station_modules/station_module_{m[10]}.dds").convert("RGBA")
        scale = min(206 / img.width, 92 / img.height)
    else:
        folder, suffix = ("station_modules_large_slot", "large") if m[1] == "L" else ("station_modules_small_slot", "small")
        img = Image.open(ART + f"station_modules/{folder}/station_module_{m[10]}_{suffix}.dds").convert("RGBA")
        box = (88, 98) if m[1] == "L" else (52, 52)
        scale = min(box[0] / img.width, box[1] / img.height)
    return img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)


def build_button(w=254, h=44):
    shape = theme._rounded(w, h, 6, (0, 0, 0, 255))
    img = theme._masked(theme._vertical(w, h, (74, 150, 104), (40, 96, 64)), shape)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=6, outline=(150, 220, 170, 255), width=2)
    d.line([(6, 2), (w - 7, 2)], fill=(190, 240, 200, 150), width=1)
    return img


def art():
    os.makedirs(OUT, exist_ok=True)
    gfx = ""

    def sprite(name, file, frames=1, button=False):
        nonlocal gfx
        extra = '\t\teffectFile = "gfx/FX/buttonstate.lua"\n' if button else ""
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_{name}"\n\t\ttextureFile = "{OUT}{file}.dds"\n\t\tnoOfFrames = {frames}\n{extra}\t}}\n'

    save(tint_plan(), f"plan_{COLONY[0]}")
    sprite("mdr_mars_plan", "plan_mars")
    for shape in (1, 2, 3, 4):
        for kind in ("open", "locked", "built", "work", "ring"):
            save(slot_art(shape, kind), f"slot_{shape}_{kind}")
            sprite(f"mdr_colony_slot_{shape}_{kind}", f"slot_{shape}_{kind}", button=kind in ("open", "built", "work", "locked"))
    for m in MODULES:
        save(module_art(m, "slot"), f"mod_{m[0]}_slot")
        sprite(f"mdr_mars_mod_{m[0]}_slot", f"mod_{m[0]}_slot")
        save(module_art(m, "frame"), f"mod_{m[0]}_frame")
        sprite(f"mdr_mars_mod_{m[0]}_frame", f"mod_{m[0]}_frame")
    frame = Image.open(ART + "antarctic_station_module_bg.dds").convert("RGBA").resize((262, 113), Image.LANCZOS)
    save(frame, "module_frame")
    sprite("mdr_colony_module_frame", "module_frame")
    arrow = Image.open(ART + "antarctic_map_desc_button_scroll_two.dds").convert("RGBA").resize((24, 56), Image.LANCZOS)
    save(arrow, "arrow_left")
    save(arrow.transpose(Image.FLIP_LEFT_RIGHT), "arrow_right")
    sprite("mdr_colony_arrow_left", "arrow_left", button=True)
    sprite("mdr_colony_arrow_right", "arrow_right", button=True)
    label = theme._rounded(66, 22, 6, (18, 24, 28, 225), (226, 182, 52, 255), 1)
    save(label, "work_label")
    sprite("mdr_colony_work_label", "work_label")
    save(build_button(), "build_btn")
    sprite("mdr_colony_build_btn", "build_btn", button=True)
    photo = Image.open(PHOTO + COLONY[3] + ".dds").convert("RGBA")
    card = theme.card(photo, 92, 70)
    save(card, f"card_{COLONY[0]}")
    sprite("mdr_mars_card", "card_mars")
    emit("interface/mdr_space_colony.gfx", gfx)


# ---- Window.
def text(name, x, y, w, key, font="hoi_16mbs", tip=None, fmt="left", h=20):
    end = f'pdx_tooltip = "{tip}"' if tip else "alwaystransparent = yes"
    return f'{T * 2}instantTextboxType = {{ name = "{name}" position = {{ x = {x} y = {y} }} font = "{font}" borderSize = {{ x = 0 y = 0 }} text = "{key}" maxWidth = {w} maxHeight = {h} format = {fmt} {end} }}\n'


def panel(name, x, y, w, h):
    return f'{T * 2}containerWindowType = {{\n{T * 3}name = "{name}"\n{T * 3}position = {{ x = {x} y = {y} }}\n{T * 3}size = {{ width = {w} height = {h} }}\n{T * 3}alwaystransparent = yes\n{T * 3}background = {{\n{T * 4}name = "Background"\n{T * 4}quadTextureSprite = "GFX_mdr_space_panel"\n{T * 3}}}\n{T * 2}}}\n'


def icon(name, sprite, x, y):
    return f'{T * 2}iconType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x = {x} y = {y} }} alwaystransparent = yes }}\n'


def button(name, sprite, x, y, key=None, tip=None, font="hoi_16mbs"):
    label = f' buttonText = "{key}" buttonFont = "{font}"' if key else ""
    tooltip = f' pdx_tooltip = "{tip}"' if tip else ""
    return f'{T * 2}buttonType = {{ name = "{name}" position = {{ x = {x} y = {y} }} quadTextureSprite = "{sprite}"{label}{tooltip} clicksound = click_default }}\n'


def slot_pos(slot):
    return round(PLAN_X + 8 + (slot[2] - 296) * SCALE), round(PLAN_Y + 8 + (slot[3] - 5) * SCALE)


def slot_size(shape):
    src = Image.open(ART + f"antarctic_station_module_slot_{shape}.dds")
    return round(src.width * SCALE), round(src.height * SCALE)


def window():
    g = ""
    g += f'{T}containerWindowType = {{\n{T * 2}name = "mdr_mars_window"\n{T * 2}position = {{ x = {-W // 2} y = {-H // 2} }}\n{T * 2}size = {{ width = {W} height = {H} }}\n{T * 2}Orientation = center\n{T * 2}moveable = yes\n\n'
    g += f'{T * 2}background = {{\n{T * 3}name = "Background"\n{T * 3}quadTextureSprite = "GFX_mdr_space_window"\n{T * 2}}}\n'
    # Header.
    g += text("mdr_mars_title", 20, 12, 520, "MDR_MARS_TITLE", "hoi_24header", h=30) + text("mdr_mars_subtitle", 20, 40, 520, "MDR_MARS_SUBTITLE")
    for n, key in enumerate(("POP", "MORALE", "SCIENCE", "ROUTE")):
        x = 560 + n * 150
        g += panel(f"mdr_mars_chip_{n}", x, 8, 144, 44) + text(f"mdr_mars_chip_label_{n}", x + 10, 12, 130, f"MDR_MARS_CHIP_{key}", tip=f"MDR_MARS_CHIP_{key}_TT") + text(f"mdr_mars_chip_value_{n}", x + 10, 28, 130, f"MDR_MARS_CHIP_{key}_V", "hoi_18mbs", tip=f"MDR_MARS_CHIP_{key}_TT")
    g += f'{T * 2}buttonType = {{ name = "mdr_mars_close" position = {{ x = {W - 42} y = 12 }} quadTextureSprite = "GFX_closebutton" shortcut = "ESCAPE" clicksound = click_close pdx_tooltip = "CLOSE" }}\n'
    # Left: colony card, supplies, production, modules.
    g += panel("mdr_mars_card_panel", 12, 64, 268, 168) + icon("mdr_mars_card", "GFX_mdr_mars_card", 24, 76)
    g += text("mdr_mars_card_name", 126, 76, 150, "MDR_MARS_CARD_NAME", "hoi_18mbs") + text("mdr_mars_card_level", 126, 98, 150, "MDR_MARS_CARD_LEVEL") + text("mdr_mars_card_works", 126, 118, 150, "MDR_MARS_CARD_WORKS")
    g += button("mdr_mars_route_on", "GFX_mdr_space_btn_123x34", 24, 154, "MDR_COL_ROUTE_ON", "MDR_COL_ROUTE_TT") + button("mdr_mars_route_off", "GFX_mdr_space_btn_123x34", 24, 154, "MDR_COL_ROUTE_OFF", "MDR_COL_ROUTE_TT")
    g += button("mdr_mars_send", "GFX_mdr_space_btn_123x34", 150, 154, "MDR_COL_SEND", "MDR_COL_SEND_TT")
    for n_, other in enumerate(COLONIES):
        g += f'{T * 2}buttonType = {{ name = "mdr_mars_go_{other[0]}" position = {{ x = {24 + n_ * 36} y = 196 }} quadTextureSprite = "GFX_mdr_colony_go_{other[0]}" pdx_tooltip = "MDR_COLONY_GO_{other[0].upper()}" clicksound = click_default }}\n'
    g += icon("mdr_mars_go_ring", "GFX_mdr_colony_go_ring", 24 + COLONIES.index(COLONY) * 36 - 2, 194)
    g += panel("mdr_mars_supply_panel", 12, 240, 268, 150) + text("mdr_mars_supply_title", 24, 248, 240, "MDR_MARS_SUPPLIES")
    for i, (x_, key) in enumerate(zip(sp.SUPPLIES, ("WATER", "FOOD", "ENERGY", "OXYGEN"))):
        y = 274 + i * 28
        g += text(f"mdr_mars_{x_}_label", 24, y, 70, f"MDR_COL_{key}") + icon(f"mdr_mars_{x_}_bar", "GFX_mdr_space_meter", 92, y + 3)
        g += text(f"mdr_mars_{x_}_value", 210, y, 64, f"MDR_MARS_{key}_V", fmt="right", tip="MDR_MARS_SUPPLY_TT")
    g += panel("mdr_mars_mods_panel", 12, 398, 268, 194) + text("mdr_mars_mods_title", 24, 406, 240, "MDR_MARS_INSTALLED")
    for i, m in enumerate(MODULES):
        x, y = 24 + i % 2 * 128, 430 + i // 2 * 26
        g += text(f"mdr_mars_count_{m[0]}", x, y, 124, f"MDR_MARS_COUNT_{m[0].upper()}", tip=f"MDR_MARS_MOD_{m[0].upper()}_TT")
    # Centre: the plan and its slots.
    g += icon("mdr_mars_plan", "GFX_mdr_mars_plan", PLAN_X, PLAN_Y)
    for slot in SLOTS:
        n, shape = slot[0], slot[1]
        x, y = slot_pos(slot)
        w, h = slot_size(shape)
        for kind in ("open", "locked", "built", "work"):
            g += button(f"mdr_mars_slot_{n}_{kind}", f"GFX_mdr_colony_slot_{shape}_{kind}", x, y, tip=f"MDR_MARS_SLOT_{n}_TT")
        for m in by_size(size_of(shape)):
            g += icon(f"mdr_mars_slot_{n}_mod_{m[0]}", f"GFX_mdr_mars_mod_{m[0]}_slot", x + (w - module_art(m, "slot").width) // 2, y + (h - module_art(m, "slot").height) // 2)
        g += text(f"mdr_mars_slot_{n}_plus", x, y + h // 2 - 12, w, "MDR_MARS_PLUS", "hoi_24header", fmt="center", h=26)
        g += icon(f"mdr_mars_slot_{n}_weeksbg", "GFX_mdr_colony_work_label", x + (w - 66) // 2, y + h // 2 - 11)
        g += text(f"mdr_mars_slot_{n}_weeks", x, y + h // 2 - 9, w, f"MDR_MARS_SLOT_{n}_WEEKS", "hoi_16mbs", fmt="center")
        g += icon(f"mdr_mars_slot_{n}_ring", f"GFX_mdr_colony_slot_{shape}_ring", x, y)
    # Right: the chosen slot.
    RX = W - 288
    g += panel("mdr_mars_side", RX, 64, 276, 528)
    g += text("mdr_mars_sel_title", RX + 12, 74, 252, "MDR_MARS_SEL_TITLE") + text("mdr_mars_sel_hint", RX + 12, 94, 252, "MDR_MARS_SEL_HINT", h=36)
    g += icon("mdr_mars_frame", "GFX_mdr_colony_module_frame", RX + 7, 134)
    for m in MODULES:
        art_ = module_art(m, "frame")
        g += icon(f"mdr_mars_view_{m[0]}", f"GFX_mdr_mars_mod_{m[0]}_frame", RX + 7 + (262 - art_.width) // 2, 134 + (113 - art_.height) // 2)
    g += button("mdr_mars_prev", "GFX_mdr_colony_arrow_left", RX + 10, 162, tip="MDR_MARS_ARROW_TT") + button("mdr_mars_next", "GFX_mdr_colony_arrow_right", RX + 242, 162, tip="MDR_MARS_ARROW_TT")
    g += text("mdr_mars_view_name", RX + 12, 256, 252, "MDR_MARS_VIEW_NAME", "hoi_18mbs")
    g += text("mdr_mars_view_desc", RX + 12, 280, 252, "MDR_MARS_VIEW_DESC", h=40)
    for i, key in enumerate(("COST", "WEEKS", "GIVES")):
        g += text(f"mdr_mars_view_{key.lower()}_l", RX + 12, 326 + i * 24, 110, f"MDR_MARS_L_{key}") + text(f"mdr_mars_view_{key.lower()}", RX + 100, 326 + i * 24, 164, f"MDR_MARS_VIEW_{key}", fmt="right")
    g += text("mdr_mars_view_req", RX + 12, 404, 252, "MDR_MARS_VIEW_REQ", h=40)
    g += text("mdr_mars_view_state", RX + 12, 452, 252, "MDR_MARS_VIEW_STATE", h=40)
    g += button("mdr_mars_build", "GFX_mdr_colony_build_btn", RX + 11, 536, "MDR_MARS_BUILD", "MDR_MARS_BUILD_TT", "hoi_18mbs")
    # Bottom: works and locked slots.
    g += panel("mdr_mars_bottom", 12, 600, W - 24, 108)
    g += text("mdr_mars_works_title", 26, 610, 300, "MDR_MARS_WORKS_TITLE") + text("mdr_mars_works", 26, 632, 420, "MDR_MARS_WORKS", h=64)
    g += text("mdr_mars_locks_title", 470, 610, 400, "MDR_MARS_LOCKS_TITLE")
    for i, key in enumerate(("H3", "H4", "P20", "TECH")):
        g += text(f"mdr_mars_lock_{i}", 470 + i % 2 * 370, 632 + i // 2 * 22, 360, f"MDR_MARS_LOCK_{key}")
    g += text("mdr_mars_footer", 470, 684, 740, "MDR_MARS_FOOTER")
    g += f"{T}}}\n"
    emit("interface/mdr_space_colony.gui", g)


def scripted_gui():
    redraw = f"{T * 4}add_to_variable = {{ global.international_systems_updated = 1 }}\n"
    g = ""
    g += f'{T}mdr_mars_gui = {{\n{T * 2}context_type = player_context\n{T * 2}window_name = "mdr_mars_window"\n{T * 2}dirty = global.international_systems_updated\n\n'
    g += f"{T * 2}visible = {{ has_country_flag = mdr_mars_open has_country_flag = {P} }}\n\n"
    g += f"{T * 2}properties = {{\n" + "".join(f"{T * 3}mdr_mars_{x}_bar = {{\n{T * 4}frame = {P}_{x}_frame\n{T * 3}}}\n" for x in sp.SUPPLIES) + f"{T * 2}}}\n\n"
    g += f"{T * 2}effects = {{\n{T * 3}mdr_mars_close_click = {{\n{T * 4}clr_country_flag = mdr_mars_open\n{redraw}{T * 3}}}\n"
    g += f"{T * 3}mdr_mars_prev_click = {{\n{T * 4}{V}_prev = yes\n{T * 3}}}\n{T * 3}mdr_mars_next_click = {{\n{T * 4}{V}_next = yes\n{T * 3}}}\n"
    g += f"{T * 3}mdr_mars_build_click = {{\n{T * 4}{V}_build = yes\n{T * 4}{V}_figures = yes\n{T * 3}}}\n"
    g += f"{T * 3}mdr_mars_route_on_click = {{\n{T * 4}set_country_flag = {P}_route\n{T * 4}mdr_space_refresh = yes\n{T * 4}ingame_update_setup = yes\n{T * 3}}}\n"
    g += f"{T * 3}mdr_mars_route_off_click = {{\n{T * 4}clr_country_flag = {P}_route\n{T * 4}mdr_space_refresh = yes\n{T * 4}ingame_update_setup = yes\n{T * 3}}}\n"
    g += f"{T * 3}mdr_mars_send_click = {{\n{T * 4}{P}_send = yes\n{T * 4}{V}_figures = yes\n{T * 3}}}\n"
    for other in COLONIES:
        closes = "".join(f"{T * 4}clr_country_flag = MDRX_{o[0]}_open\n" for o in COLONIES)
        g += f"{T * 3}mdr_mars_go_{other[0]}_click = {{\n{closes}{T * 4}set_country_flag = MDRX_{other[0]}_open\n{T * 4}add_to_variable = {{ global.international_systems_updated = 1 }}\n{T * 3}}}\n"
    for slot in SLOTS:
        n = slot[0]
        for kind in ("open", "locked", "built", "work"):
            g += f"{T * 3}mdr_mars_slot_{n}_{kind}_click = {{\n{T * 4}set_variable = {{ {V}_sel = {n} }}\n{T * 4}{V}_select = yes\n{T * 3}}}\n"
    g += f"{T * 2}}}\n\n{T * 2}triggers = {{\n"
    g += f"{T * 3}mdr_mars_build_click_enabled = {{ {V}_can_build = yes }}\n"
    for other in COLONIES:
        g += f"{T * 3}mdr_mars_go_{other[0]}_visible = {{ has_country_flag = MDRX_col_{other[0]} }}\n"
    g += f"{T * 3}mdr_mars_route_on_visible = {{ NOT = {{ has_country_flag = {P}_route }} }}\n{T * 3}mdr_mars_route_off_visible = {{ has_country_flag = {P}_route }}\n"
    g += f"{T * 3}mdr_mars_send_click_enabled = {{ check_variable = {{ var = {P}_pop compare = less_than value = {P}_cap }} check_variable = {{ treasury > {COLONY[8]} }} }}\n"
    for slot in SLOTS:
        n, shape = slot[0], slot[1]
        built, job = f"check_variable = {{ {V}_s{n} > 0 }}", f"check_variable = {{ {V}_s{n}_job > 0 }}"
        g += f"{T * 3}mdr_mars_slot_{n}_locked_visible = {{ NOT = {{ {V}_slot_{n}_open = yes }} }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_open_visible = {{ {V}_slot_{n}_free = yes }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_built_visible = {{ {built} NOT = {{ {job} }} }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_work_visible = {{ {job} }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_plus_visible = {{ {V}_slot_{n}_free = yes }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_weeks_visible = {{ {job} }}\n{T * 3}mdr_mars_slot_{n}_weeksbg_visible = {{ {job} }}\n"
        g += f"{T * 3}mdr_mars_slot_{n}_ring_visible = {{ check_variable = {{ {V}_sel = {n} }} }}\n"
        for m in by_size(size_of(shape)):
            g += f"{T * 3}mdr_mars_slot_{n}_mod_{m[0]}_visible = {{ check_variable = {{ {V}_s{n} = {mid(m)} }} NOT = {{ {job} }} }}\n"
    for m in MODULES:
        g += f"{T * 3}mdr_mars_view_{m[0]}_visible = {{ check_variable = {{ {V}_view = {mid(m)} }} }}\n"
    g += f"{T * 2}}}\n\n{T * 2}ai_enabled = {{ always = no }}\n{T}}}\n"
    emit("common/scripted_guis/mdr_space_colony_gui.txt", g)


# ---- Texts.
def pick(name, var, keys, fallback):
    d = f"defined_text = {{\n\tname = {name}\n"
    for value, key in keys:
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ {var} = {value} }} }}\n\t\tlocalization_key = {key}\n\t}}\n"
    return d + f"\ttext = {{\n\t\tlocalization_key = {fallback}\n\t}}\n}}\n\n"


def texts():
    d = "# Generated by herramientas/space_colony.py.\n"
    for part in ("NAME", "DESC", "COST", "WEEKS", "GIVES"):
        d += pick(f"mdr_mars_view_{part.lower()}", f"{V}_view", [(mid(m), f"MDR_MARS_MOD_{m[0].upper()}_{part}") for m in MODULES], "MDR_SPACE_EMPTY")
    # Requirement of the shown module.
    d += "defined_text = {\n\tname = mdr_mars_view_req\n"
    for m in MODULES:
        key = f"MDR_MARS_MOD_{m[0].upper()}"
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ {V}_view = {mid(m)} }} {V}_module_{m[0]}_ready = yes }}\n\t\tlocalization_key = {key}_REQ_OK\n\t}}\n"
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ {V}_view = {mid(m)} }} }}\n\t\tlocalization_key = {key}_REQ_NO\n\t}}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_EMPTY\n\t}\n}\n\n"
    # State of the chosen slot.
    d += "defined_text = {\n\tname = mdr_mars_sel_state\n"
    for slot in SLOTS:
        n = slot[0]
        at = f"check_variable = {{ {V}_sel = {n} }}"
        d += f"\ttext = {{\n\t\ttrigger = {{ {at} NOT = {{ {V}_slot_{n}_open = yes }} }}\n\t\tlocalization_key = MDR_MARS_SLOT_{n}_LOCKED\n\t}}\n"
        d += f"\ttext = {{\n\t\ttrigger = {{ {at} check_variable = {{ {V}_s{n}_job > 0 }} }}\n\t\tlocalization_key = MDR_MARS_SEL_WORK_{n}\n\t}}\n"
        d += f"\ttext = {{\n\t\ttrigger = {{ {at} check_variable = {{ {V}_s{n} > 0 }} }}\n\t\tlocalization_key = MDR_MARS_SEL_BUILT\n\t}}\n"
    d += "\ttext = {\n\t\ttrigger = { mdr_mars_can_build = yes }\n\t\tlocalization_key = MDR_MARS_SEL_READY\n\t}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_MARS_SEL_CANT\n\t}\n}\n\n"
    d += "defined_text = {\n\tname = mdr_mars_sel_title\n"
    for slot in SLOTS:
        n = slot[0]
        at = f"check_variable = {{ {V}_sel = {n} }}"
        for cond, key in ((f"NOT = {{ {V}_slot_{n}_open = yes }}", "LOCKED"), (f"check_variable = {{ {V}_s{n}_job > 0 }}", "WORK"), (f"check_variable = {{ {V}_s{n} > 0 }}", "BUILT"), ("always = yes", "FREE")):
            d += f"\ttext = {{\n\t\ttrigger = {{ {at} {cond} }}\n\t\tlocalization_key = MDR_MARS_T_{n}_{key}\n\t}}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_SPACE_EMPTY\n\t}\n}\n\n"
    # First work going on.
    d += "defined_text = {\n\tname = mdr_mars_works\n"
    for slot in SLOTS:
        n = slot[0]
        d += f"\ttext = {{\n\t\ttrigger = {{ check_variable = {{ {V}_s{n}_job > 0 }} }}\n\t\tlocalization_key = MDR_MARS_WORK_{n}\n\t}}\n"
    d += "\ttext = {\n\t\tlocalization_key = MDR_MARS_NO_WORKS\n\t}\n}\n\n"
    for slot in SLOTS:
        n = slot[0]
        d += pick(f"mdr_mars_job_name_{n}", f"{V}_s{n}_job", [(mid(m), f"MDR_MARS_MOD_{m[0].upper()}_NAME") for m in MODULES], "MDR_SPACE_EMPTY")
        d += pick(f"mdr_mars_built_name_{n}", f"{V}_s{n}", [(mid(m), f"MDR_MARS_MOD_{m[0].upper()}_NAME") for m in MODULES], "MDR_SPACE_EMPTY")
    # Locked slots summary, green when open.
    for key, cond in (("H3", "check_variable = { mdr_space_hq > 2 }"), ("H4", "check_variable = { mdr_space_hq > 3 }"), ("P20", f"check_variable = {{ {P}_pop > 19 }}"), ("TECH", "has_tech = mdr_sp_surface has_tech = mdr_sp_printing")):
        d += f"defined_text = {{\n\tname = mdr_mars_lock_{key.lower()}\n\ttext = {{\n\t\ttrigger = {{ {cond} }}\n\t\tlocalization_key = MDR_MARS_LOCK_{key}_OK\n\t}}\n\ttext = {{\n\t\tlocalization_key = MDR_MARS_LOCK_{key}_NO\n\t}}\n}}\n\n"
    emit("common/scripted_localisation/mdr_space_colony_loc.txt", d)

    for idx, lang in enumerate(("spanish", "english")):
        es = idx == 0
        num = lambda v: sp.number(v, lang)
        w = {
            "MDR_MARS_TITLE": (f"{COLONY[1].upper()}  ·  COLONIA", f"{COLONY[2].upper()}  ·  COLONY"),
            "MDR_MARS_SUBTITLE": ("[?mdr_mars_built|0] módulos construidos · [?mdr_mars_jobs|0] en obra", "[?mdr_mars_built|0] modules built · [?mdr_mars_jobs|0] under construction"),
            "MDR_MARS_CHIP_POP": ("COLONOS", "SETTLERS"), "MDR_MARS_CHIP_POP_V": (f"§Y[?{P}_pop|0] / [?{P}_cap|0]§!", f"§Y[?{P}_pop|0] / [?{P}_cap|0]§!"),
            "MDR_MARS_CHIP_POP_TT": ("Colonos y capacidad. Los hábitats y las viviendas suben la capacidad.", "Settlers and capacity. Habitats and quarters raise the capacity."),
            "MDR_MARS_CHIP_MORALE": ("MORAL", "MORALE"), "MDR_MARS_CHIP_MORALE_V": (f"§G[?{P}_morale|0]%§!", f"§G[?{P}_morale|0]%§!"),
            "MDR_MARS_CHIP_MORALE_TT": ("Baja si falta un suministro; por debajo de 25% se pierden colonos. El centro médico y las viviendas la suben.", "Falls if a supply runs short; below 25% settlers are lost. The medical centre and quarters raise it."),
            "MDR_MARS_CHIP_SCIENCE": ("CIENCIA", "SCIENCE"), "MDR_MARS_CHIP_SCIENCE_V": ("§G+[?mdr_mars_science_total|1] / sem§!", "§G+[?mdr_mars_science_total|1] / wk§!"),
            "MDR_MARS_CHIP_SCIENCE_TT": ("Ciencia por semana: 0,09 por colono más los laboratorios.", "Science a week: 0.09 per settler plus the laboratories."),
            "MDR_MARS_CHIP_ROUTE": ("RUTA DE CARGA", "CARGO ROUTE"), "MDR_MARS_CHIP_ROUTE_V": ("[mdr_mars_route_state]", "[mdr_mars_route_state]"),
            "MDR_MARS_CHIP_ROUTE_TT": (f"Trae 6 de cada suministro por semana y cuesta $${num(COLONY[9])}B por semana.", f"Brings 6 of each supply a week and costs $${num(COLONY[9])}B a week."),
            "MDR_MARS_ROUTE_ON_V": (f"§YAbierta§! · $${num(COLONY[9])}B", f"§YOpen§! · $${num(COLONY[9])}B"), "MDR_MARS_ROUTE_OFF_V": ("§gCerrada§!", "§gClosed§!"),
            "MDR_MARS_CARD_NAME": (f"§YColonia de {of(COLONY, 0)}§!", f"§Y{of(COLONY, 1)[0].upper() + of(COLONY, 1)[1:]} colony§!"), "MDR_MARS_CARD_LEVEL": ("Módulos: [?mdr_mars_built|0] de 13", "Modules: [?mdr_mars_built|0] of 13"),
            "MDR_MARS_CARD_WORKS": ("En obra: [?mdr_mars_jobs|0]", "Under construction: [?mdr_mars_jobs|0]"),
            "MDR_MARS_BACK_HINT": ("§gCerrá con la X para volver al programa.§!", "§gClose with the X to go back to the programme.§!"),
            "MDR_MARS_SUPPLIES": ("SUMINISTROS", "SUPPLIES"),
            "MDR_MARS_SUPPLY_TT": ("Nivel actual y cambio por semana: lo que hacen los módulos menos lo que gastan los colonos, más la ruta.", "Current level and weekly change: what modules make minus what settlers use, plus the route."),
            "MDR_MARS_INSTALLED": ("MÓDULOS INSTALADOS", "MODULES INSTALLED"), "MDR_MARS_PLUS": ("+", "+"),
            "MDR_MARS_SEL_TITLE": ("[mdr_mars_sel_title]", "[mdr_mars_sel_title]"), "MDR_MARS_SEL_HINT": ("[mdr_mars_sel_state]", "[mdr_mars_sel_state]"),
            "MDR_MARS_SEL_BUILT": ("§GConstruido.§! Elegí una casilla libre para seguir.", "§GBuilt.§! Pick a free slot to go on."),
            "MDR_MARS_SEL_READY": ("Elegí un módulo con las flechas y mandalo a construir.", "Pick a module with the arrows and send it to be built."),
            "MDR_MARS_SEL_CANT": ("§RNo se puede construir este módulo acá todavía:§! mirá su requisito y el dinero.", "§RThis module cannot be built here yet:§! check its requirement and the money."),
            "MDR_MARS_ARROW_TT": ("Módulo anterior o siguiente de los que entran en esta casilla.", "Previous or next module that fits this slot."),
            "MDR_MARS_VIEW_NAME": ("§Y[mdr_mars_view_name]§!", "§Y[mdr_mars_view_name]§!"), "MDR_MARS_VIEW_DESC": ("[mdr_mars_view_desc]", "[mdr_mars_view_desc]"),
            "MDR_MARS_L_COST": ("Costo", "Cost"), "MDR_MARS_L_WEEKS": ("Obra", "Work"), "MDR_MARS_L_GIVES": ("Da", "Gives"),
            "MDR_MARS_VIEW_COST": ("[mdr_mars_view_cost]", "[mdr_mars_view_cost]"), "MDR_MARS_VIEW_WEEKS": ("[mdr_mars_view_weeks]", "[mdr_mars_view_weeks]"), "MDR_MARS_VIEW_GIVES": ("[mdr_mars_view_gives]", "[mdr_mars_view_gives]"),
            "MDR_MARS_VIEW_REQ": ("[mdr_mars_view_req]", "[mdr_mars_view_req]"), "MDR_MARS_VIEW_STATE": ("", ""),
            "MDR_MARS_BUILD": ("Enviar a construir", "Send to build"),
            "MDR_MARS_BUILD_TT": ("Paga el módulo y empieza la obra en la casilla elegida. Los ingenieros la acortan.", "Pays for the module and starts the work on the chosen slot. Engineers shorten it."),
            "MDR_MARS_WORKS_TITLE": ("EN OBRA", "UNDER CONSTRUCTION"), "MDR_MARS_WORKS": ("[mdr_mars_works]", "[mdr_mars_works]"),
            "MDR_MARS_NO_WORKS": ("§gNada en obra. Elegí una casilla libre en el plano.§!", "§gNothing under construction. Pick a free slot on the plan.§!"),
            "MDR_MARS_LOCKS_TITLE": ("CASILLAS QUE SE ABREN", "SLOTS THAT OPEN"),
            "MDR_MARS_LOCK_H3": ("[mdr_mars_lock_h3]", "[mdr_mars_lock_h3]"), "MDR_MARS_LOCK_H4": ("[mdr_mars_lock_h4]", "[mdr_mars_lock_h4]"),
            "MDR_MARS_LOCK_P20": ("[mdr_mars_lock_p20]", "[mdr_mars_lock_p20]"), "MDR_MARS_LOCK_TECH": ("[mdr_mars_lock_tech]", "[mdr_mars_lock_tech]"),
            "MDR_MARS_LOCK_H3_OK": ("§G· Casillas 6 y 8: sede nivel 3§!", "§G· Slots 6 and 8: headquarters level 3§!"), "MDR_MARS_LOCK_H3_NO": ("· Casillas 6 y 8: §Rsede nivel 3§!", "· Slots 6 and 8: §Rheadquarters level 3§!"),
            "MDR_MARS_LOCK_H4_OK": ("§G· Casillas 9 y 10: sede nivel 4§!", "§G· Slots 9 and 10: headquarters level 4§!"), "MDR_MARS_LOCK_H4_NO": ("· Casillas 9 y 10: §Rsede nivel 4§!", "· Slots 9 and 10: §Rheadquarters level 4§!"),
            "MDR_MARS_LOCK_P20_OK": ("§G· Casillas 11 y 14: 20 colonos§!", "§G· Slots 11 and 14: 20 settlers§!"), "MDR_MARS_LOCK_P20_NO": ("· Casillas 11 y 14: §R20 colonos§!", "· Slots 11 and 14: §R20 settlers§!"),
            "MDR_MARS_LOCK_TECH_OK": ("§G· Casillas 4 y 12: superficie e impresión 3D§!", "§G· Slots 4 and 12: surface and 3D printing§!"), "MDR_MARS_LOCK_TECH_NO": ("· Casillas 4 y 12: §Roperaciones de superficie e impresión 3D§!", "· Slots 4 and 12: §Rsurface operations and 3D printing§!"),
            "MDR_MARS_FOOTER": ("§gCada planeta tiene su plano y sus módulos; se abren con investigaciones, la sede y los colonos.§!", "§gEach planet has its own plan and modules; they open with research, the headquarters and settlers.§!"),
            "MDR_MARS_OPEN": ("Ver la colonia", "View the colony"), "MDR_MARS_OPEN_TT": (f"Abre el plano de la colonia de {of(COLONY, 0)}.", f"Opens the plan of the {COLONY[2]} colony."),
        }
        for x, key in zip(sp.SUPPLIES, ("WATER", "FOOD", "ENERGY", "OXYGEN")):
            w[f"MDR_MARS_{key}_V"] = (f"§Y[?{P}_{x}|0]§! ([?{P}_{x}_net|+1])", f"§Y[?{P}_{x}|0]§! ([?{P}_{x}_net|+1])")
        for m in MODULES:
            K = f"MDR_MARS_MOD_{m[0].upper()}"
            w[f"{K}_NAME"] = (m[2], m[3])
            w[f"{K}_DESC"] = (m[4], m[5])
            w[f"{K}_COST"] = (f"§Y$${num(m[6])}B§!", f"§Y$${num(m[6])}B§!")
            w[f"{K}_WEEKS"] = (f"{m[7]} semanas", f"{m[7]} weeks")
            w[f"{K}_GIVES"] = (f"§G{m[11]}§!", f"§G{m[12]}§!")
            w[f"{K}_TT"] = (f"§Y{m[2]}§!\\n{m[4]}\\n§G{m[11]}§!", f"§Y{m[3]}§!\\n{m[5]}\\n§G{m[12]}§!")
            if m[8]:
                w[f"{K}_REQ_OK"] = (f"§GRequisito cumplido:§! {req_text(m[8], 'spanish')}", f"§GRequirement met:§! {req_text(m[8], 'english')}")
                w[f"{K}_REQ_NO"] = (f"§RFalta:§! {req_text(m[8], 'spanish')}", f"§RMissing:§! {req_text(m[8], 'english')}")
            else:
                w[f"{K}_REQ_OK"] = w[f"{K}_REQ_NO"] = ("§GSin requisitos.§!", "§GNo requirements.§!")
            short = SHORT[m[0]]
            w[f"MDR_MARS_COUNT_{m[0].upper()}"] = (f"{short[0]}: §Y[?mdr_mars_n_{m[0]}|0]§!", f"{short[1]}: §Y[?mdr_mars_n_{m[0]}|0]§!")
        for slot in SLOTS:
            n = slot[0]
            size = ("módulo grande", "large module") if size_of(slot[1]) == "L" else ("módulo chico", "small module")
            lock = (f"§RCerrada:§! se abre con {req_text(slot[4], 'spanish')}." if slot[4] else "", f"§RLocked:§! opens with {req_text(slot[4], 'english')}." if slot[4] else "")
            w[f"MDR_MARS_SLOT_{n}_TT"] = (f"§YCasilla {n}§! · {size[0]}", f"§YSlot {n}§! · {size[1]}")
            w[f"MDR_MARS_SLOT_{n}_LOCKED"] = lock
            w[f"MDR_MARS_SLOT_{n}_WEEKS"] = (f"§Y[?mdr_mars_s{n}_left|0]§! sem.", f"§Y[?mdr_mars_s{n}_left|0]§! wk")
            w[f"MDR_MARS_SEL_WORK_{n}"] = (f"§YEn obra:§! [mdr_mars_job_name_{n}], faltan [?mdr_mars_s{n}_left|0] semanas.", f"§YUnder construction:§! [mdr_mars_job_name_{n}], [?mdr_mars_s{n}_left|0] weeks left.")
            w[f"MDR_MARS_WORK_{n}"] = (f"§Y[mdr_mars_job_name_{n}]§! · casilla {n} · faltan [?mdr_mars_s{n}_left|0] semanas", f"§Y[mdr_mars_job_name_{n}]§! · slot {n} · [?mdr_mars_s{n}_left|0] weeks left")
            for key, (es_, en_) in (("LOCKED", ("CERRADA", "LOCKED")), ("WORK", ("EN OBRA", "UNDER CONSTRUCTION")), ("BUILT", ("[mdr_mars_built_name_" + str(n) + "]", "[mdr_mars_built_name_" + str(n) + "]")), ("FREE", ("LIBRE", "FREE"))):
                w[f"MDR_MARS_T_{n}_{key}"] = (f"CASILLA {n} · {es_}", f"SLOT {n} · {en_}")
        emit(f"localisation/{lang}/mdr_space_colony_l_{lang}.yml", "".join(f' {k}: "{v[idx]}"\n' for k, v in w.items()))
    # Route state for the chip.
    emit("common/scripted_localisation/mdr_space_colony_loc.txt", f"defined_text = {{\n\tname = mdr_mars_route_state\n\ttext = {{\n\t\ttrigger = {{ has_country_flag = {P}_route }}\n\t\tlocalization_key = MDR_MARS_ROUTE_ON_V\n\t}}\n\ttext = {{\n\t\tlocalization_key = MDR_MARS_ROUTE_OFF_V\n\t}}\n}}\n")


def write_all():
    BUF.clear()
    for colony in COLONIES:
        setup(colony)
        logic()
        art()
        window()
        scripted_gui()
        texts()
    shared_art()
    heads = {
        "interface/mdr_space_colony.gui": ("# Generated by herramientas/space_colony.py.\nguiTypes = {\n", "}\n"),
        "common/scripted_guis/mdr_space_colony_gui.txt": ("# Generated by herramientas/space_colony.py.\nscripted_gui = {\n", "}\n"),
        "interface/mdr_space_colony.gfx": ("# Generated by herramientas/space_colony.py.\nspriteTypes = {\n", "}\n"),
    }
    for path, parts in BUF.items():
        head, tail = heads.get(path, ("", ""))
        body = head + "".join(parts) + tail
        if path.endswith(".yml"):
            lang = path.split("/")[1]
            with open(path, "wb") as f:
                f.write(b"\xef\xbb\xbf" + (f"l_{lang}:\n" + body).encode("utf-8"))
        else:
            with open(path, "wb") as f:
                f.write(body.encode("utf-8"))


def shared_art():
    # Colony switcher: the planet of each colony, small, and a ring for the one shown.
    from make_space_icons import save_dds
    gfx = ""
    for colony in COLONIES:
        planet = Image.open(f"gfx/interface/mdr/space/icons/planet_{colony[13]}.dds").convert("RGBA")
        scale = 30 / max(planet.width, planet.height)
        img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
        small = planet.resize((max(1, round(planet.width * scale)), max(1, round(planet.height * scale))), Image.LANCZOS)
        img.alpha_composite(small, ((32 - small.width) // 2, (32 - small.height) // 2))
        save_dds(img, f"{OUT}go_{colony[0]}.dds")
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_colony_go_{colony[0]}"\n\t\ttextureFile = "{OUT}go_{colony[0]}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    save_dds(theme.selection_ring(36), f"{OUT}go_ring.dds")
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_colony_go_ring"\n\t\ttextureFile = "{OUT}go_ring.dds"\n\t}}\n'
    BUF.setdefault("interface/mdr_space_colony.gfx", []).append(gfx)
    # Names of the colonies for the switcher.
    for idx, lang in enumerate(("spanish", "english")):
        lines = "".join(f' MDR_COLONY_GO_{c[0].upper()}: "{"Colonia de " + of(c, 0) if idx == 0 else c[2] + " colony"}"\n' for c in COLONIES)
        BUF.setdefault(f"localisation/{lang}/mdr_space_colony_l_{lang}.yml", []).append(lines)


if __name__ == "__main__":
    write_all()
    print("ok")
