"""Ready-made export designs: for each MD hull, four roles with the modules of the hull's own era.

Used by make_ship_sale.py. A role is an order of preference among module categories; each slot takes the first
category it allows and, in it, the newest module whose technology starts no later than the hull's year.
Category limits of the hull (module_count_limit) are respected.
"""
import ship_data

ROLES = [  # key, Spanish, English, code in the design name
    ("mp", "Multipropósito", "Multi-role", "MP"),
    ("aa", "Antiaéreo", "Air Defence", "AA"),
    ("asw", "Antisubmarino", "Anti-Submarine", "ASW"),
    ("asuw", "Antibuque", "Anti-Ship", "ASuW"),
]
GUNS = ["module_light_guns_category", "module_gun_battery_category", "module_heavy_guns_category", "module_naval_adl_category"]
WEAPONS = {
    "mp": ["module_vls_large_category", "module_vls_small_category", "module_turret_missile_category", "module_point_defense_system_category",
           "module_torpedoes_category", "module_light_helipad_category", "module_helipads_category", "module_anti_ship_torpedoes_category"],
    "aa": ["module_vls_large_category", "module_vls_capital_category", "module_vls_small_category", "module_point_defense_system_category",
           "module_naval_adl_category", "module_turret_missile_category", "module_esm_category", "module_radar_jammer_category"],
    "asw": ["module_torpedoes_category", "module_light_helipad_category", "module_helipads_category", "module_anti_submarine_mortar_category",
            "module_vls_small_category", "module_point_defense_system_category", "module_esm_category"],
    "asuw": ["module_turret_missile_category", "module_anti_ship_torpedoes_category", "module_vls_large_category", "module_vls_small_category",
             "module_heavy_guns_category", "module_point_defense_system_category", "module_radar_jammer_category"],
}
SUB_WEAPONS = {
    "mp": ["module_anti_ship_torpedoes_category", "module_vls_sub_category", "module_torpedoes_category", "module_sub_esm_category"],
    "aa": ["module_vls_sub_category", "module_anti_ship_torpedoes_category", "module_sub_esm_category", "module_torpedoes_category"],
    "asw": ["module_torpedoes_category", "module_anti_ship_torpedoes_category", "module_sub_esm_category", "module_vls_sub_category"],
    "asuw": ["module_anti_ship_torpedoes_category", "module_vls_sub_category", "module_torpedoes_category", "module_sub_esm_category"],
}
AMMO = {"mp": "module_missile_ammo_balanced_category", "aa": "module_missile_ammo_air_defense_category",
        "asw": "module_missile_ammo_asw_category", "asuw": "module_missile_ammo_anti_ship_category"}
SUB_AMMO = "module_sub_missile_ammo_anti_ship_category"
SMALL = {"corvette", "stealth_corvette", "patrol_boat", "frigate", "stealth_frigate"}
CAPITAL = {"carrier", "battleship_hull_0", "battle_cruiser", "cruiser", "helicopter_operator"}
PER_CATEGORY = 2  # at most two modules of one kind: real ships mix their weapons
MISSILE_CATS = {"module_vls_large_category", "module_vls_small_category", "module_vls_capital_category", "module_turret_missile_category", "module_vls_sub_category"}


def build(hulls, modules, unlock):
    years = ship_data.tech_years()
    by_cat = {}
    for m, d in modules.items():
        by_cat.setdefault(d["category"], []).append(m)

    def year_of(m):
        t = unlock.get(m)
        return years.get(t, 0) if t else 0

    def best(cat, limit, small=False, nuclear=False):
        ok = [m for m in by_cat.get(cat, []) if year_of(m) <= limit and (unlock.get(m) is None or unlock.get(m) in years)]
        # Export ships use conventional power, and small hulls carry a 76 mm gun.
        if not nuclear:
            ok = [m for m in ok if "reactor" not in m and "nuclear" not in m] or ok
        if cat == "module_light_guns_category":
            want = "76mm" if small else "127mm"
            ok = [m for m in ok if want in m] or ok
        if not ok:
            return None
        # Newest first; on a tie the later one in MD's list (usually the better tier).
        order = {m: i for i, m in enumerate(by_cat[cat])}
        return max(ok, key=lambda m: (year_of(m), order[m]))

    out = {}
    for h, d in hulls.items():
        sub = "submarine" in d["archetype"]
        small = d["archetype"] in SMALL
        capital = d["archetype"] in CAPITAL
        for role, *_ in ROLES:
            counts, design = {}, {}
            for i, (slot, required, cats) in enumerate(d["slots"]):
                if not cats:
                    continue
                if slot == "fixed_ship_engine_slot" or slot == "fixed_ship_flight_deck":
                    prefs = list(cats)
                elif "fire_control" in slot:
                    prefs = (["module_capital_fire_control_system_category"] if capital else ["module_fire_control_system_category", "module_screen_fire_control_system_category"]) + list(cats)
                elif slot == "fixed_ship_radar_slot":
                    prefs = (["module_sonar_category", "module_radar_category"] if role == "asw" or sub else ["module_radar_category", "module_sonar_category"]) + list(cats)
                elif slot.startswith("fixed_ship_battery_slot") and not sub:
                    prefs = GUNS + WEAPONS[role]
                else:
                    pool = SUB_WEAPONS[role] if sub else WEAPONS[role]
                    # Multi-role spreads its weapons: each slot starts further down the list.
                    shift = i % len(pool) if role == "mp" else 0
                    prefs = pool[shift:] + pool[:shift] + GUNS
                pick = None
                for cat in prefs + list(cats):
                    if cat not in cats:
                        continue
                    if counts.get(cat, 0) >= min(d["limits"].get(cat, 99), PER_CATEGORY) and not required:
                        continue
                    pick = best(cat, d["year"], small, d["archetype"] == "carrier")
                    if pick:
                        counts[cat] = counts.get(cat, 0) + 1
                        break
                if pick:
                    design[slot] = pick
            # Missiles need ammunition in the ammo slot, as MD's own designs do.
            if any(modules[m]["category"] in MISSILE_CATS for m in design.values()) and any(s == "fixed_ship_missile_ammo_slot" for s, _, _ in d["slots"]):
                ammo = best(SUB_AMMO if sub else AMMO[role], d["year"], small)
                if ammo:
                    design["fixed_ship_missile_ammo_slot"] = ammo
            out[(h, role)] = design
    return out, unlock


if __name__ == "__main__":
    hulls, modules, unlock = ship_data.load()
    presets, _ = build(hulls, modules, unlock)
    for h in ("destroyer_hull_3", "corvette_hull_2", "frigate_hull_4", "attack_submarine_hull_3", "carrier_hull_3", "patrol_boat_hull_1"):
        for role, *_ in ROLES:
            print(h, role, presets[(h, role)])
        print()
    req_missing = 0
    for (h, r), dsg in presets.items():
        for s, req, cats in hulls[h]["slots"]:
            if req and cats and s not in dsg:
                req_missing += 1
                print("required slot empty:", h, r, s)
    print("designs", len(presets), "required empty", req_missing, "modules used", len({m for d in presets.values() for m in d.values()}))
