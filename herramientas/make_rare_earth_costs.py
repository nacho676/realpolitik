# Adds 1 rare earth to the electronics modules and guided weapons, on copies of Millennium Dawn's files. Only pieces that really use
# magnets, lasers and sensors. Older analog levels pay nothing.
# Run from the mod folder after each Millennium Dawn update: python herramientas/make_rare_earth_costs.py
import re
import sys

MD = "../Millennium-Dawn-2.0.0/common/units/equipment/"
OUT = "common/units/equipment/"
CATEGORIES = {
    "tank_atgm_module", "afv_atgm_module", "tank_aa_module",
    "tank_electric_engine_type", "czech_electric_engine_type",
    "helicopter_sensor_and_avionics_type",
    "module_fire_control_system_category", "module_capital_fire_control_system_category", "module_screen_fire_control_system_category",
    "module_railguns_category", "module_railgun_battery_category",
    "plane_awacs_module", "plane_avionics",
    "tank_battlestation_module",
    "module_radar_category", "module_sonar_category",
    "spaa_radar_systems", "spaa_off_vehicle_radar_systems",
}
MODULES_EXTRA = {
    "tank_railgun_cannon_1", "tank_railgun_cannon_2", "tank_focused_laser_beam_cannon",
    "hardkill_system_gen1", "hardkill_system_gen2", "hardkill_system_gen3", "hardkill_system_gen4",
    "tank_unmanned_turret", "ifv_unmanned_turret", "crows_mg",
}
OLD = {
    "tank_battlestation_1", "tank_battlestation_2",
    "avionics_manned_1", "weap_buff_awacs_1",
    # Ships: only the first generation is free. Cold War radars, sonars and fire control already used samarium-cobalt
    # magnets, so the analog sets and the second generation pay too, as plane avionics do.
    "module_radar_1", "module_sonar_1",
    "spaa_radar_gen1", "spaa_radar_gen2", "spaa_off_vehicle_radar_gen1", "spaa_off_vehicle_radar_gen2",
}
GENERIC = {"MD_anti_air.txt": {"AA_Equipment"}, "MD_anti_tank.txt": {"L_AT_Equipment", "H_AT_Equipment"}}


def add_modules(name):
    text = open(MD + "modules/" + name, encoding="utf-8", newline="").read()
    done = []

    def block(m):
        mod, body = m.group(1), m.group(2)
        cat = re.search(r"\bcategory\s*=\s*(\w+)", body)
        if not cat or mod in OLD or not (cat.group(1) in CATEGORIES or mod in MODULES_EXTRA):
            return m.group(0)
        new, n = re.subn(r"(build_cost_resources\s*=\s*\{)", r"\1 rare_earths = 1", body, count=1)
        if n == 0:
            # Modules without materials (analog fire control) get a block of their own after the category.
            new, n = re.subn(r"(\bcategory\s*=\s*\w+\r?\n)", r"\1\t\tbuild_cost_resources = { rare_earths = 1 }\n", body, count=1)
        if n == 0:
            sys.exit("no place for materials in " + mod)
        done.append(mod)
        return m.group(0).replace(body, new, 1)

    text = re.sub(r"(?m)^\t(\w+)\s*=\s*\{(.*?)^\t\}", block, text, flags=re.S | re.M)
    open(OUT + "modules/" + name, "w", encoding="utf-8", newline="").write(text)
    return done


def add_generic(name, wanted):
    text = open(MD + name, encoding="utf-8", newline="").read()
    done = []

    def block(m):
        if m.group(1) not in wanted:
            return m.group(0)
        new, n = re.subn(r"(resources\s*=\s*\{)", r"\1 rare_earths = 1", m.group(2), count=1)
        if n == 0:
            sys.exit("no resources in " + m.group(1))
        done.append(m.group(1))
        return m.group(0).replace(m.group(2), new, 1)

    text = re.sub(r"(?m)^\t(\w+)\s*=\s*\{(.*?)^\t\}", block, text, flags=re.S | re.M)
    if set(done) != wanted:
        sys.exit("missing %s in %s" % (wanted - set(done), name))
    open(OUT + name, "w", encoding="utf-8", newline="").write(text)
    return done


import os
os.makedirs(OUT + "modules", exist_ok=True)
total = 0
for f in ("MD_tank_modules.txt", "MD_plane_modules.txt", "MD_helicopter_modules.txt", "MD_ship_modules.txt", "MD_arty_modules.txt"):
    d = add_modules(f)
    total += len(d)
    print(f, len(d), " ".join(d))
for f, w in GENERIC.items():
    print(f, add_generic(f, w))
print("ok", total)
