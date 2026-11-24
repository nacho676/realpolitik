import glob, re, sys

g = open("interface/mdr_space.gui", encoding="utf-8").read()
s = open("common/scripted_guis/mdr_space_gui.txt", encoding="utf-8").read()
blocks = re.split(r"^\tcontainerWindowType = \{\n", g, flags=re.M)
win = {re.search(r'name = "(\w+)"', b).group(1): b for b in blocks[1:]}
print(len(win), "windows", sum(len(b) for b in win.values()) // 1024, "KB gui", len(s) // 1024, "KB logic")
bad = 0
for gui in re.finditer(r'window_name = "(\w+)".*?(?=\n\tmdr_\w+_gui = \{|\Z)', s, re.S):
    w, txt = gui.group(1), gui.group(0)
    if w not in win:
        print("NO WINDOW", w)
        continue
    els = set(re.findall(r'name = "(\w+)"', win[w]))
    # Element names may end in _left/_right: try the full name before stripping a click modifier.
    used = set()
    for name in re.findall(r"^\t\t\t(\w+)_(?:click_enabled|click|visible) = ", txt, re.M):
        if name not in els:
            name = re.sub(r"_(?:control|shift|alt|right)$", "", name)
        used.add(name)
    if used - els:
        bad += 1
        print(w, "sin elemento", sorted(used - els)[:8])
print("ventanas con faltantes:", bad)
sprites = set()
for f in glob.glob("interface/*.gfx") + glob.glob("../Millennium-Dawn-2.0.3/interface/**/*.gfx", recursive=True) + glob.glob(__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/interface/**/*.gfx", recursive=True):
    sprites |= set(re.findall(r'name\s*=\s*"(GFX_\w+)"', open(f, encoding="utf-8", errors="ignore").read()))
print("sprites faltantes:", sorted(set(re.findall(r'"(GFX_\w+)"', g)) - sprites)[:20])
loc = {}
for lang in ("spanish", "english"):
    keys = set()
    for f in glob.glob(f"localisation/{lang}/*.yml") + glob.glob(f"localisation/{lang}/replace/*.yml") + glob.glob(f"../Millennium-Dawn-2.0.3/localisation/{lang}/*.yml"):
        keys |= set(re.findall(r"^ ([\w.\-]+):\d* ", open(f, encoding="utf-8-sig", errors="ignore").read(), re.M))
    loc[lang] = keys
    need = set(re.findall(r'(?:text|buttonText|pdx_tooltip|pdx_tooltip_delayed) = "([A-Za-z_0-9]+)"', g))
    print(lang, "faltan", sorted(k for k in need if k and k not in keys)[:14])
    prog = open(f"localisation/{lang}/mdr_space_program_l_{lang}.yml", encoding="utf-8-sig").read()
    nested = set(re.findall(r"\$([A-Za-z_0-9]+)\$", prog))
    print(lang, "anidadas faltan", sorted(k for k in nested if k not in keys)[:14])
    dollars = [l[:70] for l in prog.split("\n") if len(re.findall(r"(?<!\$)\$(?!\$)", l)) % 2]
    print(lang, "con $ impar", dollars[:4])
# Effects, triggers and variables named in the GUI exist?
eff = open("common/scripted_effects/mdr_space_program.txt", encoding="utf-8").read() + open("common/scripted_effects/mdr_space.txt", encoding="utf-8").read() + open("common/scripted_effects/mdr_space_keyboard.txt", encoding="utf-8").read()
defined = set(re.findall(r"^(\w+) = \{", eff, re.M))
called = set(re.findall(r"\b(mdr_(?:sa|col|space)_\w+) = yes", s + eff))
trig = open("common/scripted_triggers/mdr_space_program_triggers.txt", encoding="utf-8").read() + open("common/scripted_triggers/mdr_triggers.txt", encoding="utf-8").read()
tdef = set(re.findall(r"^(\w+) = \{", trig, re.M))
print("efectos/triggers sin definir:", sorted(c for c in called if c not in defined and c not in tdef)[:14])
print("efectos", len(defined), "triggers", len(tdef))
d = open("common/technologies/mdr_space.txt", encoding="utf-8").read()
print("techs con efecto único:", d.count("on_research_complete"), "con 3+ efectos ok")
tech = set(re.findall(r"^\t(mdr_sp_\w+) = \{", d, re.M))
import importlib, sys as _s
_s.path.insert(0, "herramientas")
import space_program as sp
miss = [r for a, _ in sp.ACTIONS for r in a[9] if r.startswith("t:") and sp.tid(r[2:]) not in tech]
miss += [r for g_ in sp.GOALS for r in g_[5] if r.startswith("t:") and sp.tid(r[2:]) not in tech]
names = {a[0] for a, _ in sp.ACTIONS}
miss2 = [r for a, _ in sp.ACTIONS for r in a[9] if r.startswith("a:") and r[2:] not in names]
print("techs inexistentes:", miss, "acciones inexistentes:", miss2)
print("por categoría:", [sum(1 for a in sp.PROJECTS if a[1] == k) for k in range(1, 6)], [sum(1 for a in sp.MISSIONS if a[1] == k) for k in range(1, 6)])
docs = open(__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/documentation/modifiers_documentation.md", encoding="utf-8", errors="ignore").read()
mods = set(re.findall(r"^\t\t([a-z_]+) = -?[\d.]+$", d, re.M)) - {"research_cost", "start_year", "x", "y", "research_cost_coeff", "level"}
own = set()
for f in glob.glob("common/modifier_definitions/*.txt") + glob.glob("../Millennium-Dawn-2.0.3/common/modifier_definitions/*.txt"):
    own |= set(re.findall(r"^(\w+) = \{", open(f, encoding="utf-8", errors="ignore").read(), re.M))
print("modificadores dudosos:", sorted(m for m in mods if m not in own and not re.search(r"\b" + m + r"\b", docs))[:14])
