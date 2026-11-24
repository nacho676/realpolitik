# Generates the ammunition, clean technology and climate adaptation research lines: common/technologies/mdr_ammo_techs.txt and
# mdr_green_techs.txt, interface/mdr_tech_lines.gfx, their icons and localisation/*/mdr_tech_lines_l_*.yml.
# Run from the mod folder: python herramientas/make_tech_lines.py [preview.png]
import os
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

N = 64
S = 8
INK = (16, 14, 10, 255)
ICON_DIR = "gfx/interface/technologies/mdr/"
ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII"]

AMMO = [
    ("Cadenas de montaje de munición", "Ammunition Assembly Chains", "Cada puesto hace una sola tarea, y la fábrica rinde mucho más.", "Each station does one task, and the plant makes far more."),
    ("Detonadores fiables", "Reliable Fuzes", "Menos proyectiles fallados, y menos munición gastada para lograr lo mismo.", "Fewer duds, and less ammunition spent to achieve the same result."),
    ("Líneas de cartuchos automáticas", "Automatic Cartridge Lines", "Máquinas que arman cartuchos sin parar, con menos manos y menos errores.", "Machines assemble cartridges nonstop, with fewer hands and fewer errors."),
    ("Pólvoras de doble base", "Double-Base Propellants", "Pólvoras más estables, que duran más tiempo guardadas.", "More stable propellants that keep longer in storage."),
    ("Prensas de alta velocidad", "High-Speed Presses", "Prensas que forman vainas en una fracción del tiempo.", "Presses form casings in a fraction of the time."),
    ("Explosivos insensibles", "Insensitive Explosives", "Cargas que resisten golpes y calor, y se pueden apilar con más seguridad.", "Charges that withstand shock and heat can be stacked more safely."),
    ("Fábricas modulares de munición", "Modular Ammunition Plants", "Líneas que cambian de calibre en horas, no en semanas.", "Lines switch caliber in hours, not weeks."),
    ("Vainas de polímero", "Polymer Casings", "Vainas livianas y baratas que ahorran metal.", "Light, cheap casings save metal."),
    ("Impresión de cargas", "Printed Charges", "Cargas impresas capa por capa, a medida de cada arma.", "Charges printed layer by layer, tailored to each weapon."),
    ("Depósitos automatizados", "Automated Depots", "Almacenes subterráneos que funcionan casi sin personal.", "Underground depots run almost without staff."),
    ("Fabricación sin operarios", "Lights-Out Manufacturing", "Plantas que trabajan las 24 horas, sin personal en la línea.", "Plants run around the clock with no one on the line."),
    ("Nanoenergéticos", "Nanoenergetics", "Materiales que liberan su energía de forma exacta y estable.", "Materials release their energy precisely and stably."),
]
CLEAN = [
    ("Filtros de partículas", "Particulate Filters", "Filtros en chimeneas que retienen el hollín antes de que salga.", "Chimney filters catch soot before it escapes."),
    ("Lavadores de gases", "Gas Scrubbers", "Torres que quitan el azufre del humo de las fábricas.", "Towers strip sulfur from factory smoke."),
    ("Tratamiento de efluentes", "Effluent Treatment", "Plantas que limpian el agua antes de devolverla a los ríos.", "Plants clean water before it returns to the rivers."),
    ("Producción más limpia", "Cleaner Production", "Rediseñar los procesos para emitir menos desde el principio.", "Redesigning processes to emit less from the start."),
    ("Economía circular", "Circular Economy", "Los residuos de una fábrica son la materia prima de otra.", "One factory's waste is another's raw material."),
    ("Captura de carbono", "Carbon Capture", "Atrapar el CO2 de las chimeneas y guardarlo bajo tierra.", "Trapping chimney CO2 and storing it underground."),
    ("Química verde", "Green Chemistry", "Reacciones que usan menos sustancias tóxicas.", "Reactions that use fewer toxic substances."),
    ("Acero y cemento sin carbono", "Carbon-Free Steel and Cement", "Hidrógeno y nuevos hornos para las industrias que más emiten.", "Hydrogen and new kilns for the highest-emitting industries."),
    ("Captura directa del aire", "Direct Air Capture", "Plantas que retiran del aire el CO2 ya emitido.", "Plants remove already emitted CO2 from the air."),
    ("Industria de emisión cero", "Zero-Emission Industry", "Fábricas que no dejan nada en el aire ni en el agua.", "Factories leave nothing in the air or water."),
]
ADAPT = [
    ("Mapas de riesgo", "Risk Mapping", "Saber qué zonas se inundan o se queman permite prevenir.", "Knowing which areas flood or burn makes prevention possible."),
    ("Códigos de construcción climáticos", "Climate Building Codes", "Edificios pensados para resistir tormentas y olas de calor.", "Buildings designed to withstand storms and heatwaves."),
    ("Alerta temprana por satélite", "Satellite Early Warning", "Días de aviso para evacuar y proteger lo que importa.", "Days of warning to evacuate and protect what matters."),
    ("Defensas costeras y fluviales", "Coastal and River Defenses", "Diques y barreras que crecen junto con el nivel del agua.", "Dikes and barriers grow with the water level."),
    ("Ciudades esponja", "Sponge Cities", "Suelos y parques que absorben la lluvia en vez de inundarse.", "Soil and parks absorb rain instead of flooding."),
    ("Infraestructura resiliente", "Resilient Infrastructure", "Redes y caminos que siguen funcionando durante el desastre.", "Grids and roads keep working through the disaster."),
    ("Modelado climático de precisión", "Precision Climate Modeling", "Predecir cada evento extremo con tiempo para actuar.", "Predicting each extreme event in time to act."),
]
# Effects of each technology, in order.
AMMO_FX = [
    [('mdr_ammo_gain_factor', 0.048), ('line_change_production_efficiency_factor', 0.025)],
    [('mdr_ammo_gain_factor', 0.02), ('supply_consumption_factor', -0.005), ('mdr_ammo_storage_factor', 0.03), ('production_speed_mdr_fortified_ammo_depot_factor', 0.1)],
    [('mdr_ammo_gain_factor', 0.052), ('production_factory_efficiency_gain_factor', 0.02)],
    [('mdr_ammo_storage_factor', 0.073), ('mdr_ammo_gain_factor', 0.01)],
    [('mdr_ammo_gain_factor', 0.035), ('production_lack_of_resource_penalty_factor', -0.01), ('mdr_ammo_storage_factor', 0.025), ('production_speed_mdr_fortified_ammo_depot_factor', 0.05)],
    [('mdr_ammo_gain_factor', 0.01), ('production_factory_max_efficiency_factor', 0.01), ('mdr_ammo_storage_factor', 0.02), ('production_speed_mdr_fortified_ammo_depot_factor', 0.075)],
    [('mdr_ammo_storage_factor', 0.02), ('supply_consumption_factor', -0.01), ('mdr_ammo_gain_factor', 0.015), ('line_change_production_efficiency_factor', 0.03)],
    [('mdr_ammo_gain_factor', 0.045), ('production_lack_of_resource_penalty_factor', -0.02), ('production_factory_start_efficiency_factor', 0.02)],
    [('mdr_ammo_gain_factor', 0.04), ('industrial_capacity_factory', 0.01), ('line_change_production_efficiency_factor', 0.015)],
    [('mdr_ammo_storage_factor', 0.077), ('production_speed_mdr_fortified_ammo_depot_factor', 0.1), ('mdr_ammo_gain_factor', 0.015)],
    [('mdr_ammo_gain_factor', 0.055), ('industrial_capacity_factory', 0.01), ('production_factory_max_efficiency_factor', 0.01)],
    [('mdr_ammo_gain_factor', 0.03), ('mdr_ammo_storage_factor', 0.03)],
]
CLEAN_FX = [
    [('mdr_pollution_factor', -0.035)],
    [('mdr_pollution_factor', -0.03), ('production_speed_fossil_powerplant_factor', 0.05)],
    [('mdr_pollution_factor', -0.02), ('production_speed_mdr_desalination_plant_factor', 0.1)],
    [('mdr_pollution_factor', -0.03), ('energy_use_modifier_civs', -0.01)],
    [('mdr_pollution_factor', -0.025), ('production_speed_mdr_recycling_plant_factor', 0.15)],
    [('mdr_pollution_factor', -0.04), ('energy_use_multiplier', 0.01)],
    [('mdr_pollution_factor', -0.02), ('production_speed_synthetic_refinery_factor', 0.1)],
    [('mdr_pollution_factor', -0.035), ('production_speed_mdr_electric_arc_furnace_factor', 0.15)],
    [('mdr_pollution_factor', -0.04), ('energy_use_multiplier', 0.015)],
    [('mdr_pollution_factor', -0.045), ('renewable_energy_gain_multiplier', 0.02)],
]
ADAPT_FX = [
    [('mdr_disaster_resilience', 0.05)],
    [('mdr_disaster_resilience', 0.03), ('repair_speed_infrastructure_factor', 0.05)],
    [('mdr_disaster_resilience', 0.04), ('production_speed_mdr_early_warning_center_factor', 0.15)],
    [('mdr_disaster_resilience', 0.03), ('production_speed_mdr_coastal_dikes_factor', 0.15)],
    [('mdr_disaster_resilience', 0.04), ('production_speed_infrastructure_factor', 0.03)],
    [('mdr_disaster_resilience', 0.04), ('repair_speed_infrastructure_factor', 0.1)],
    [('mdr_disaster_resilience', 0.04), ('agricolture_productivity_modifier', 0.01)],
]


def layer():
    return Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))


def P(*pts):
    return [(x * S, y * S) for x, y in pts]


def B(x0, y0, x1, y1):
    return [x0 * S, y0 * S, x1 * S, y1 * S]


def shade(draw, top, bottom):
    mask = Image.new("L", (N * S, N * S), 0)
    draw(ImageDraw.Draw(mask))
    a = np.array(mask) > 0
    ys = np.where(a.any(axis=1))[0]
    if len(ys) == 0:
        return layer()
    t = np.clip((np.arange(N * S) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)[:, None]
    rgb = np.array(top)[None, :] * (1 - t) + np.array(bottom)[None, :] * t
    arr = np.zeros((N * S, N * S, 4), dtype=np.uint8)
    arr[..., :3] = rgb[:, None, :].astype(np.uint8)
    arr[..., 3] = np.array(mask)
    edge = mask.filter(ImageFilter.MaxFilter(2 * S + 1))
    out = Image.new("RGBA", (N * S, N * S), INK[:3] + (0,))
    out.putalpha(edge)
    out.alpha_composite(Image.fromarray(arr, "RGBA"))
    return out


def shell(im, x, y, h):
    """A standing cartridge."""
    w = 4.2
    im.alpha_composite(shade(lambda d: d.polygon(P((x - w, y), (x + w, y), (x + w, y - h * 0.6), (x + w * 0.6, y - h * 0.7), (x + w * 0.6, y - h * 0.76), (x - w * 0.6, y - h * 0.76), (x - w * 0.6, y - h * 0.7), (x - w, y - h * 0.6)), fill=255), (240, 196, 96), (150, 96, 26)))
    im.alpha_composite(shade(lambda d: (d.pieslice(B(x - w * 0.6, y - h * 1.04, x + w * 0.6, y - h * 0.5), 180, 360, fill=255), d.rectangle(B(x - w * 0.6, y - h * 0.78, x + w * 0.6, y - h * 0.74), fill=255)), (205, 130, 78), (130, 66, 34)))


def ammo(stage):
    """A crate with more cartridges as the line advances."""
    stage *= 2  # twelve steps drawn like the old twenty-three
    im = layer()
    count = 2 + stage // 6
    span = 44
    for i in range(count):
        x = 32 - span / 2 + (i + 0.5) * span / count
        shell(im, x, 37, 30)
    im.alpha_composite(shade(lambda d: d.rectangle(B(7, 34, 57, 55), fill=255), (118, 134, 74), (56, 68, 34)))
    d = ImageDraw.Draw(im)
    d.rectangle(B(7, 39.5, 57, 41), fill=INK)
    d.rectangle(B(13, 34, 15, 55), fill=(58, 70, 34, 255))
    d.rectangle(B(49, 34, 51, 55), fill=(58, 70, 34, 255))
    if stage >= 6:
        d.rectangle(B(25, 44, 39, 50), fill=(225, 205, 110, 255), outline=INK, width=S // 2)
    if stage >= 12:
        d.ellipse(B(50, 7, 59, 16), fill=(120, 215, 240, 255), outline=INK, width=S // 2)
    return im


def clean(stage):
    """A factory whose smoke turns into clean air and leaves."""
    im = layer()
    t = stage / 9
    for i, x in enumerate((18, 30)):
        grey = int(70 + 170 * t)
        for k in range(3):
            r = 3.5 + k * 1.4
            cx, cy = x + 3 + k * 4, 20 - k * 6
            d = ImageDraw.Draw(im)
            d.ellipse(B(cx - r, cy - r, cx + r, cy + r), fill=(grey, grey, min(255, grey + 12), int(235 - 150 * t)))
    im.alpha_composite(shade(lambda d: (d.rectangle(B(15, 20, 21, 38), fill=255), d.rectangle(B(27, 20, 33, 38), fill=255)), (150, 154, 160), (84, 88, 94)))
    im.alpha_composite(shade(lambda d: d.polygon(P((8, 54), (8, 36), (20, 30), (20, 36), (32, 30), (32, 36), (44, 30), (44, 54)), fill=255), (130, 140, 150), (68, 76, 86)))
    d = ImageDraw.Draw(im)
    for x in (13, 23, 33):
        d.rectangle(B(x, 42, x + 5, 47), fill=(240, 220, 120, 255), outline=INK, width=S // 2)
    leaf = lambda dr: dr.polygon(P((42, 22), (54, 12), (60, 8), (60, 18), (54, 26), (45, 29)), fill=255)
    im.alpha_composite(shade(leaf, (150, 230, 96), (54, 150, 58)))
    d = ImageDraw.Draw(im)
    d.line(P((43, 30), (58, 10)), fill=INK, width=S // 2 + 1)
    return im


def adapt(stage):
    """A shield over a house, facing the storm."""
    im = layer()
    t = stage / 6
    im.alpha_composite(shade(lambda d: (d.ellipse(B(6, 3, 26, 19), fill=255), d.ellipse(B(18, 1, 44, 21), fill=255), d.ellipse(B(36, 5, 58, 21), fill=255)), (120, 130, 150), (58, 64, 82)))
    d = ImageDraw.Draw(im)
    for x in (12, 26, 40, 52):
        d.line(P((x, 22), (x - 3, 30)), fill=(120, 200, 245, 255), width=int(1.6 * S))
    shield = lambda dr: dr.polygon(P((32, 22), (52, 28), (52, 40), (46, 50), (32, 58), (18, 50), (12, 40), (12, 28)), fill=255)
    im.alpha_composite(shade(shield, (int(70 + 40 * t), int(150 + 60 * t), int(205 + 30 * t)), (22, int(70 + 50 * t), 120)))
    im.alpha_composite(shade(lambda dr: dr.polygon(P((32, 28), (44, 38), (40, 38), (40, 48), (24, 48), (24, 38), (20, 38)), fill=255), (245, 238, 215), (178, 165, 132)))
    d = ImageDraw.Draw(im)
    d.rectangle(B(29, 41, 35, 48), fill=(112, 76, 44, 255), outline=INK, width=S // 2)
    return im


def numeral(text):
    t = layer()
    d = ImageDraw.Draw(t)
    font = ImageFont.truetype("C:/Windows/Fonts/timesbi.ttf", (17 if len(text) < 4 else 13) * S)
    box = d.textbbox((0, 0), text, font=font)
    d.text((61 * S - box[2], 63 * S - box[3]), text, font=font, fill=(240, 236, 50, 255), stroke_width=S, stroke_fill=(15, 15, 5, 255))
    return t


def save_dds(img, path):
    w, h = img.size
    r, g, b, a = img.split()
    data = Image.merge("RGBA", (b, g, r, a)).tobytes()
    head = struct.pack("<4s7I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1) + b"\0" * 44
    head += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    head += struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(head + data)


def tech(key, i, total, year, cost, x, y, folder, cats, effects, ai):
    s = f"\t{key}_{i} = {{\n\t\tresearch_cost = {cost}\n\t\tstart_year = {year}\n\n"
    s += "".join(f"\t\t{a} = {b}\n" for a, b in effects)
    s += "\n\t\tcategories = {\n" + "".join(f"\t\t\t{c}\n" for c in cats) + "\t\t}\n\n"
    if i < total:
        s += f"\t\tpath = {{\n\t\t\tleads_to_tech = {key}_{i + 1}\n\t\t\tresearch_cost_coeff = 1\n\t\t}}\n"
    s += f"\t\tfolder = {{\n\t\t\tname = {folder}\n\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t}}\n\n"
    s += "\t\tai_will_do = {\n\t\t\tbase = 1\n" + "".join(f"\t\t\tmodifier = {{ add = 10 {m} }}\n" for m in ai) + "\t\t}\n\t}\n"
    return s


LINES = [
    ("mdr_ammo_tech", AMMO, ammo, [1965 + 10 * i for i in range(12)]),
    ("mdr_clean_tech", CLEAN, clean, [1985 + 10 * i for i in range(10)]),
    ("mdr_adapt_tech", ADAPT, adapt, [1985 + 15 * i for i in range(7)]),
]

# Technologies.
a = "technologies = {\n\t# Ammunition branch, infantry folder, column 13 (11 = camouflage). One technology every ten years, from the folder's first year.\n"
for i, year in enumerate(LINES[0][3], 1):
    a += "\n" + tech("mdr_ammo_tech", i, 12, year, 1.75, 13, (year - 1965) // 5 * 2, "infantry_folder", ["CAT_inf", "CAT_Military"],
                     AMMO_FX[i - 1],
                     ["num_of_military_factories > 10", "has_war = yes"])
a += "}\n"
g = "technologies = {\n\t# Environment branches in the civilian folder, right of uranium mining (column 44).\n\t# Clean technology, column 46: less pollution per building.\n"
for i, year in enumerate(LINES[1][3], 1):
    g += "\n" + tech("mdr_clean_tech", i, 10, year, 1.75, 46, 2 + (year - 1985) // 5 * 2, "civilian_folder", ["CAT_industry", "CAT_Civilian"],
                     CLEAN_FX[i - 1], ["num_of_civilian_factories > 20", "any_owned_state = { OR = { has_dynamic_modifier = { modifier = mdr_pollution_high } has_dynamic_modifier = { modifier = mdr_pollution_severe } } }"])
g += "\n\t# Climate adaptation, column 48: less cost and more chance of lighter damage from storms, floods, fires and heatwaves.\n"
for i, year in enumerate(LINES[2][3], 1):
    g += "\n" + tech("mdr_adapt_tech", i, 7, year, 1.75, 48, 2 + (year - 1985) // 5 * 2, "civilian_folder", ["CAT_industry", "CAT_Civilian"],
                     ADAPT_FX[i - 1], ["check_variable = { gdp_per_capita > 10 }", "has_idea = mdr_disaster_severe"])
g += "}\n"
open("common/technologies/mdr_ammo_techs.txt", "w", encoding="utf-8", newline="\n").write(a)
open("common/technologies/mdr_green_techs.txt", "w", encoding="utf-8", newline="\n").write(g)

# Icons and sprites.
sheet = Image.new("RGBA", (10 * 72, 5 * 72), (45, 58, 40, 255))
gfx = "# Generated by herramientas/make_tech_lines.py.\nspriteTypes = {\n"
slot = 0
for key, names, draw, years in LINES:
    for i in range(len(names)):
        if key in ("mdr_ammo_tech", "mdr_clean_tech", "mdr_adapt_tech"):
            # Drawn by herramientas/make_ammo_icons.py, make_clean_icons.py and make_adapt_icons.py; keep those files.
            icon = Image.open(ICON_DIR + f"{key}_{i + 1}.dds").convert("RGBA")
        else:
            art = draw(i)
            art.alpha_composite(numeral(ROMAN[i]))
            icon = art.resize((N, N), Image.LANCZOS)
            save_dds(icon, ICON_DIR + f"{key}_{i + 1}.dds")
        gfx += f"\tspriteType = {{ name = \"GFX_{key}_{i + 1}_medium\" texturefile = \"{ICON_DIR}{key}_{i + 1}.dds\" }}\n"
        sheet.alpha_composite(icon, ((slot % 10) * 72 + 4, (slot // 10) * 72 + 4))
        slot += 1
gfx += "}\n"
open("interface/mdr_tech_lines.gfx", "w", encoding="utf-8", newline="\n").write(gfx)
if len(sys.argv) > 1:
    sheet.save(sys.argv[1])

# Texts.
EXTRA = {
    "spanish": {
        "mdr_ammo_storage_factor": "£infantry_equipment_texticon Almacenamiento de munición",
        "mdr_pollution_factor": "£resources_texticon Contaminación por edificio",
        "mdr_disaster_resilience": "£resources_texticon Resiliencia a desastres climáticos",
        "mdr_food_spoilage_factor": "£wheat_texticon Grano perdido en depósitos",
        "mdr_food_storage_factor": "£wheat_texticon Almacenamiento de comida",
        "mdr_pandemic_resilience": "£resources_texticon Resiliencia a pandemias",
        "mdr_ammo_storage_factor_desc": "Munición que el país puede tener guardada.",
        "mdr_pollution_factor_desc": "Contaminación que emite cada edificio del país.",
        "mdr_disaster_resilience_desc": "Baja el costo de tormentas, inundaciones, incendios y olas de calor, y da la misma probabilidad de que sus daños sean menores.",
        "mdr_food_spoilage_factor_desc": "Grano que se pierde cada semana en los depósitos.",
        "mdr_food_storage_factor_desc": "Comida que el país puede tener guardada.",
        "mdr_pandemic_resilience_desc": "Parte de los castigos de una pandemia que el país compensa.",
        "mdr_pandemic_relief": "Respuesta a la pandemia",
        "INFANTRY_TITLE_AMMO": "Munición",
        "INFANTRY_TITLE_AMMO_DESC": "Producir más munición y guardarla mejor.",
        "CIVILIAN_TITLE_ENVIRONMENT": "MEDIO AMBIENTE",
        "CIVILIAN_TITLE_ENVIRONMENT_DESC": "Contaminar menos y resistir mejor un clima que cambia.",
    },
    "english": {
        "mdr_ammo_storage_factor": "£infantry_equipment_texticon Ammunition Storage",
        "mdr_pollution_factor": "£resources_texticon Pollution per Building",
        "mdr_disaster_resilience": "£resources_texticon Climate Disaster Resilience",
        "mdr_food_spoilage_factor": "£wheat_texticon Grain Lost in Storage",
        "mdr_food_storage_factor": "£wheat_texticon Food Storage",
        "mdr_pandemic_resilience": "£resources_texticon Pandemic Resilience",
        "mdr_ammo_storage_factor_desc": "Ammunition the country can keep in storage.",
        "mdr_pollution_factor_desc": "Pollution emitted by each building of the country.",
        "mdr_disaster_resilience_desc": "Lowers the cost of storms, floods, fires and heatwaves, and gives the same chance that their damage is lighter.",
        "mdr_food_spoilage_factor_desc": "Grain lost in storage each week.",
        "mdr_food_storage_factor_desc": "Food the country can keep in storage.",
        "mdr_pandemic_resilience_desc": "Share of a pandemic's penalties that the country offsets.",
        "mdr_pandemic_relief": "Pandemic Response",
        "INFANTRY_TITLE_AMMO": "Ammunition",
        "INFANTRY_TITLE_AMMO_DESC": "Making more ammunition and storing it better.",
        "CIVILIAN_TITLE_ENVIRONMENT": "ENVIRONMENT",
        "CIVILIAN_TITLE_ENVIRONMENT_DESC": "Polluting less and standing up better to a changing climate.",
    },
}
for lang, name_i, desc_i in (("spanish", 0, 2), ("english", 1, 3)):
    out = f"\ufeffl_{lang}:\n"
    for key, names, draw, years in LINES:
        for i, row in enumerate(names, 1):
            out += f' {key}_{i}: "{row[name_i]}"\n {key}_{i}_desc: "{row[desc_i]}"\n'
    for k, v in EXTRA[lang].items():
        out += f' {k}: "{v}"\n'
    open(f"localisation/{lang}/mdr_tech_lines_l_{lang}.yml", "w", encoding="utf-8", newline="\n").write(out)
print("ok", slot, "techs")
