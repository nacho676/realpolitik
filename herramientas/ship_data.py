"""Reads Millennium Dawn's ship hulls, slots, modules and the technologies that unlock them.

Used by make_ship_sale.py. Everything comes from MD, so a new MD version needs no change here
unless MD renames the files.
"""
import glob
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT.parent / "Millennium-Dawn-2.0.0"
TOKEN = re.compile(r'"[^"]*"|[{}]|[<>!]?=|<|>|[^\s{}=<>"]+')


def tokenize(text):
    text = re.sub(r"#[^\n]*", "", text)
    return TOKEN.findall(text)


def parse(tokens, i=0):
    """Returns (list of (key, op, value), next index). Values are strings or nested lists."""
    out = []
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t == "}":
            return out, i + 1
        if t == "{":  # anonymous block
            val, i = parse(tokens, i + 1)
            out.append((None, "=", val))
            continue
        if i + 1 < n and tokens[i + 1] in ("=", "<", ">", "<=", ">=", "!="):
            op = tokens[i + 1]
            if i + 2 < n and tokens[i + 2] == "{":
                val, i = parse(tokens, i + 3)
            else:
                val, i = tokens[i + 2].strip('"'), i + 3
            out.append((t, op, val))
        else:  # bare value inside a list block
            out.append((t.strip('"'), None, None))
            i += 1
    return out, i


def read(path):
    return parse(tokenize(Path(path).read_text(encoding="utf-8", errors="replace")))[0]


def get(block, key, default=None):
    for k, _, v in block:
        if k == key:
            return v
    return default


def bare(block):
    return [k for k, op, _ in block if op is None]


def variables(paths):
    out = {}
    for p in paths:
        for m in re.finditer(r"^\s*(@\w+)\s*=\s*(-?[\d.]+)", Path(p).read_text(encoding="utf-8", errors="replace"), re.M):
            out[m.group(1)] = float(m.group(2))
    return out


def num(v, vars_):
    if isinstance(v, str):
        if v.startswith("@"):
            return vars_.get(v, 0.0)
        try:
            return float(v)
        except ValueError:
            return 0.0
    return 0.0


def load():
    ships_file = MD / "common/units/equipment/MD_mtg_ships.txt"
    vars_ = variables([ships_file])
    equipments = get(read(ships_file), "equipments")
    raw = {k: v for k, _, v in equipments if isinstance(v, list)}

    def stat(name, key, seen=()):
        b = raw[name]
        v = get(b, key)
        if v is not None:
            return num(v, vars_)
        for ref in (get(b, "parent"), get(b, "archetype")):
            if ref and ref in raw and ref not in seen:
                return stat(ref, key, seen + (name,))
        return 0.0

    def slots_of(name, seen=()):
        b = raw[name]
        s = get(b, "module_slots")
        if isinstance(s, list):
            out = []
            for k, _, v in s:
                out.append((k, get(v, "required") == "yes", bare(get(v, "allowed_module_categories", []))))
            return out
        for ref in (get(b, "parent"), get(b, "archetype")):
            if ref and ref in raw and ref not in seen:
                return slots_of(ref, seen + (name,))
        return []

    def limits_of(name):
        b = raw[name]
        lim = [(get(v, "category"), v) for k, _, v in b if k == "module_count_limit"]
        if not lim and get(b, "archetype"):
            return limits_of(get(b, "archetype"))
        out = {}
        for cat, v in lim:
            for k, op, val in v:
                if k == "count":
                    out[cat] = int(float(val)) - (1 if op == "<" else 0)
        return out

    hulls = {}
    for name, b in raw.items():
        if get(b, "is_archetype") == "yes" or get(b, "archetype") is None:
            continue
        if get(b, "is_buildable") == "no":
            continue
        hulls[name] = {
            "archetype": get(b, "archetype"),
            "year": int(float(get(b, "year", "0"))),
            "slots": slots_of(name),
            "limits": limits_of(name),
            "cost": stat(name, "build_cost_ic"),
            "speed": stat(name, "naval_speed"),
            "range": stat(name, "naval_range"),
            "hp": stat(name, "max_strength"),
        }

    modules = {}
    for f in sorted(glob.glob(str(MD / "common/units/equipment/modules/*ship*.txt"))):
        mv = variables([f])
        top = get(read(f), "equipment_modules") or []
        for name, _, b in top:
            if not isinstance(b, list) or name is None:
                continue
            cat = get(b, "category")
            if not cat:
                continue
            stats = {}
            for k, _, v in (get(b, "add_stats") or []):
                stats[k] = num(v, mv)
            for k, _, v in (get(b, "multiply_stats") or []):
                stats["x_" + k] = num(v, mv)
            modules[name] = {"category": cat, "stats": stats, "gfx": get(b, "gfx")}

    # Technology that unlocks each hull and module.
    unlock = {}
    for f in glob.glob(str(MD / "common/technologies/*.txt")):
        text = Path(f).read_text(encoding="utf-8", errors="replace")
        if "enable_equipment" not in text:
            continue
        techs = get(read(f), "technologies") or []
        for tech, _, b in techs:
            if not isinstance(b, list):
                continue
            for key in ("enable_equipments", "enable_equipment_modules"):
                for item in bare(get(b, key) or []):
                    unlock.setdefault(item, tech)
    return hulls, modules, unlock


if __name__ == "__main__":
    hulls, modules, unlock = load()
    print(len(hulls), "hulls,", len(modules), "modules")
    cats = {}
    for m, d in modules.items():
        cats.setdefault(d["category"], []).append(m)
    for h, d in sorted(hulls.items(), key=lambda x: (x[1]["archetype"], x[1]["year"])):
        opts = [sum(len(cats.get(c, [])) for c in cs) for _, _, cs in d["slots"]]
        print(f"{h:34} {d['archetype']:22} {d['year']} slots={len(d['slots'])} opts={opts} tech={unlock.get(h)} cost={d['cost']}")
    print("modules without tech:", sum(1 for m in modules if m not in unlock))
    print("biggest categories:", sorted(((len(v), k) for k, v in cats.items()), reverse=True)[:8])


def tech_years():
    """Start year of every MD technology that has one."""
    out = {}
    for f in glob.glob(str(MD / "common/technologies/*.txt")):
        text = Path(f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^\t(\w+)\s*=\s*\{(.*?)^\t\}", text, re.S | re.M):
            y = re.search(r"start_year\s*=\s*(\d+)", m.group(2))
            if y:
                out[m.group(1)] = int(y.group(1))
    return out
