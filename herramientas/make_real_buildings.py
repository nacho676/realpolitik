"""Realpolitik buildings that already existed in 2000, in their real states.

Only large, well-known installations (no spreading over the map). What opened after 2000 is left to the game.
Uranium mines and rare earth complexes are placed in mdr_uranium.txt and mdr_rare_earths_start.txt;
cropland comes from FAO data (mdr_cropland_start.txt); Dutch dikes stay in mdr_disasters.txt.

Provincial buildings (dikes, fishing ports) go in the province of the state's main port (largest naval base),
unless the entry asks for every coastal province.

Writes common/scripted_effects/mdr_real_buildings_gen.txt. Run:
    python herramientas/make_real_buildings.py
"""
import re
import sys
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
MD = MOD.parent / "Millennium-Dawn-2.0.3"
OUT = MOD / "common" / "scripted_effects" / "mdr_real_buildings_gen.txt"

# (state id, owner in 2000, level, note)
STATE_BUILDINGS = {
    "mdr_early_warning_center": [  # national warning centres working in 2000
        (615, "JAP", 1, "Japan Meteorological Agency, Tokyo"),
        (612, "JAP", 1, "Osaka regional tsunami and quake centre"),
        (817, "USA", 1, "Pacific Tsunami Warning Center, Hawaii"),
        (814, "USA", 1, "West Coast and Alaska Tsunami Warning Center, Palmer"),
        (795, "USA", 1, "National Hurricane Center, Miami"),
        (799, "USA", 1, "Storm Prediction Center, Norman"),
        (468, "CHL", 1, "SHOA tsunami service, Valparaiso"),
        (598, "TAI", 1, "Central Weather Bureau, Taipei"),
        (1230, "PHI", 1, "PAGASA, Manila"),
        (547, "CHI", 1, "China Meteorological Administration, Beijing"),
    ],
    "mdr_desalination_plant": [  # large plants running in 2000
        (174, "SAU", 1, "Jubail"),
        (177, "SAU", 1, "Jeddah"),
        (180, "UAE", 1, "Taweelah, Abu Dhabi"),
        (179, "UAE", 1, "Jebel Ali, Dubai"),
        (172, "KUW", 1, "Doha West and Shuwaikh"),
        (181, "QAT", 1, "Ras Abu Fontas"),
        (423, "BHR", 1, "Sitra"),
        (182, "OMA", 1, "Ghubrah, Muscat"),
        (95, "SPR", 1, "Canary Islands, since the 1960s"),
        (94, "SPR", 1, "Palma de Mallorca, 1999"),
    ],
    "mdr_recycling_plant": [  # industrial scrap and waste recycling leaders in 2000
        (39, "GER", 2, "Ruhr"),
        (43, "GER", 1, "Bavaria"),
        (42, "GER", 1, "Baden-Wurttemberg"),
        (615, "JAP", 2, "Kanto"),
        (612, "JAP", 1, "Kansai"),
        (604, "KOR", 1, "Gyeonggi"),
        (46, "HOL", 1, "Randstad"),
        (50, "BEL", 1, "Flanders"),
        (35, "SWE", 1, "Gothenburg"),
        (74, "SWI", 1, "Swiss plateau"),
        (76, "AUS", 1, "Lower Austria"),
        (4, "DEN", 1, "Zealand"),
        (811, "USA", 1, "California"),
        (771, "USA", 1, "Pennsylvania"),
    ],
    "mdr_regional_university": [  # big university centres outside the capital
        (767, "USA", 2, "Harvard and MIT"),
        (811, "USA", 2, "Stanford, Berkeley, Caltech"),
        (769, "USA", 1, "Columbia, Cornell"),
        (14, "ENG", 1, "Cambridge"),
        (15, "ENG", 1, "Oxford"),
        (43, "GER", 1, "Munich"),
        (42, "GER", 1, "Heidelberg"),
        (612, "JAP", 1, "Kyoto and Osaka"),
        (62, "FRA", 1, "Lyon and Grenoble"),
        (763, "CAN", 1, "Toronto"),
        (540, "CHI", 1, "Fudan and Jiao Tong, Shanghai"),
        (471, "RAJ", 1, "IIT Bombay"),
        (644, "SOV", 1, "Saint Petersburg"),
        (72, "SWI", 1, "Lausanne and Geneva"),
        (743, "AST", 1, "Melbourne"),
    ],
}

# (state id, owner, all coastal provinces?, note)
PROVINCE_BUILDINGS = {
    "mdr_fishing_port": [  # main fishing ports of 2000
        (904, "PRU", False, "Chimbote"),
        (463, "CHL", False, "Talcahuano and Puerto Montt"),
        (30, "NRY", False, "Alesund"),
        (31, "NRY", False, "Tromso"),
        (7, "ICE", False, "Reykjavik"),
        (617, "JAP", False, "Kushiro"),
        (616, "JAP", False, "Kesennuma"),
        (609, "JAP", False, "Nagasaki"),
        (1137, "SOV", False, "Petropavlovsk"),
        (643, "SOV", False, "Murmansk"),
        (692, "SOV", False, "Vladivostok"),
        (944, "SPR", False, "Vigo"),
        (378, "MOR", False, "Agadir"),
        (538, "CHI", False, "Zhoushan"),
        (435, "CHI", False, "Yantai"),
        (814, "USA", False, "Dutch Harbor"),
        (767, "USA", False, "New Bedford"),
        (760, "CAN", False, "Halifax"),
        (759, "CAN", False, "St. John's"),
        (509, "SIA", False, "Songkhla"),
        (518, "VIE", False, "Ca Mau"),
        (605, "KOR", False, "Busan"),
        (599, "TAI", False, "Kaohsiung"),
        (283, "NAM", False, "Walvis Bay"),
        (281, "SAF", False, "Cape Town"),
        (6, "DEN", False, "Esbjerg"),
        (1195, "ENG", False, "Peterhead"),
        (64, "FRA", False, "Lorient"),
        (453, "ARG", False, "Mar del Plata"),
    ],
    "mdr_coastal_dikes": [  # sea defences besides the Netherlands (mdr_disasters.txt)
        (13, "ENG", False, "Thames Barrier"),
        (1080, "GER", True, "Hamburg flood defences"),
        (37, "GER", True, "North Sea dikes, Schleswig-Holstein"),
        (38, "GER", True, "North Sea dikes, Lower Saxony"),
        (50, "BEL", True, "Sigma Plan, Flanders"),
        (6, "DEN", True, "West Jutland dikes"),
        (797, "USA", False, "New Orleans levees"),
        (615, "JAP", False, "Tokyo Bay sea walls"),
        (612, "JAP", False, "Osaka Bay sea walls"),
        (616, "JAP", False, "Taro sea wall"),
    ],
}


def state_files():
    files = {}
    for d in (MD / "history" / "states", MOD / "history" / "states"):
        for f in d.glob("*.txt"):
            files[int(f.name.split("-")[0].strip())] = f
    return files


COASTAL = {int(row.split(";")[0]) for row in (MOD / "map" / "definition.csv").read_text(encoding="utf-8").splitlines()
           if row.count(";") >= 5 and row.split(";")[4] == "land" and row.split(";")[5] == "true"}


def owner_and_port(path):
    """Owner in 2000 and the province for a port building: largest naval base, else the first coastal province."""
    text = re.sub(r"#.*", "", path.read_text(encoding="utf-8", errors="replace"))
    owner = re.search(r"\bowner\s*=\s*(\w+)", text)
    ports = [(int(lv), int(p)) for p, lv in re.findall(r"\b(\d+)\s*=\s*\{[^{}]*?naval_base\s*=\s*(\d+)", text)]
    if ports:
        return (owner.group(1) if owner else None), max(ports)[1]
    provs = re.search(r"provinces\s*=\s*\{([^}]*)\}", text)
    coastal = [int(p) for p in (provs.group(1).split() if provs else []) if int(p) in COASTAL]
    return (owner.group(1) if owner else None), (coastal[0] if coastal else None)


def main():
    files = state_files()
    errors = []
    out = ["# Generated by herramientas/make_real_buildings.py - do not edit by hand.",
           "# Realpolitik buildings that existed in 2000, in their real states. Runs once at game start.",
           "mdr_real_buildings_start = {",
           "\tif = { limit = { NOT = { has_global_flag = mdr_real_buildings_added } }",
           "\t\tset_global_flag = mdr_real_buildings_added"]
    for btype, rows in STATE_BUILDINGS.items():
        out.append(f"\t\t# {btype}")
        for sid, tag, level, note in rows:
            owner, _ = owner_and_port(files[sid])
            if owner != tag:
                errors.append(f"{btype} {sid}: owner {owner}, expected {tag}")
            out.append(f"\t\t{sid} = {{ add_building_construction = {{ type = {btype} level = {level} instant_build = yes }} }}"
                       f" # {note} ({tag})")
    for btype, rows in PROVINCE_BUILDINGS.items():
        out.append(f"\t\t# {btype}")
        for sid, tag, every, note in rows:
            owner, port = owner_and_port(files[sid])
            if owner != tag:
                errors.append(f"{btype} {sid}: owner {owner}, expected {tag}")
            if every:
                where = "province = { all_provinces = yes limit_to_coastal = yes }"
            elif port:
                where = f"province = {port}"  # same form as the base game's bunkers
            else:
                errors.append(f"{btype} {sid}: no coastal province to place it")
                continue
            out.append(f"\t\t{sid} = {{ add_building_construction = {{ type = {btype} level = 1 instant_build = yes"
                       f" {where} }} }} # {note} ({tag})")
    out += ["\t}", "}"]
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {sum(len(r) for r in STATE_BUILDINGS.values())} state and "
          f"{sum(len(r) for r in PROVINCE_BUILDINGS.values())} provincial placements")


if __name__ == "__main__":
    main()
