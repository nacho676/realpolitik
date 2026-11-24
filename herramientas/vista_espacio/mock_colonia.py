# Rough preview of the Mars colony window (interface/mdr_space_colony.gui) in a sample state: some modules built,
# one under construction, slots locked, slot 8 chosen. Run from the mod folder:
# python herramientas/vista_espacio/mock_colonia.py herramientas/vista_espacio
import glob, re, sys

sys.path.insert(0, "herramientas")
sp = sys.argv[1]
src = open(sp + "/mock.py", encoding="utf-8").read()
head = src[:src.index("g = open(")]
exec(compile(head, "mock", "exec"))
for f in glob.glob("localisation/spanish/mdr_space*_l_spanish.yml"):
    for line in open(f, encoding="utf-8-sig"):
        m = re.match(r' (\w+):\d* "(.*)"', line)
        if m:
            loc[m.group(1)] = m.group(2).replace("\\n", " · ").replace("$$", "$")
import space_colony as sc

BUILT = {1: "hab", 5: "greenhouse", 7: "drill", 2: "solar", 13: "reactor"}
WORK = {6: ("lab", 9)}
SEL, VIEW = 8, "medical"
locked = {s[0] for s in sc.SLOTS if s[4] in ("h:4", "p:20", "t:surface", "t:printing")}
keep = set()
for s in sc.SLOTS:
    n = s[0]
    state = "locked" if n in locked else "work" if n in WORK else "built" if n in BUILT else "open"
    keep.add(f"mdr_mars_slot_{n}_{state}")
    if n in BUILT:
        keep.add(f"mdr_mars_slot_{n}_mod_{BUILT[n]}")
    if state == "open":
        keep.add(f"mdr_mars_slot_{n}_plus")
    if state == "work":
        keep.add(f"mdr_mars_slot_{n}_weeks")
        keep.add(f"mdr_mars_slot_{n}_weeksbg")
    if n == SEL:
        keep.add(f"mdr_mars_slot_{n}_ring")
keep.add(f"mdr_mars_view_{VIEW}")
keep.add("mdr_mars_route_off")
g = open("interface/mdr_space_colony.gui", encoding="utf-8").read()
lines = []
for line in g.split("\n"):
    m = re.search(r'name = "(mdr_mars_(?:slot_\d+_\w+|view_\w+|route_o\w+))"', line)
    if m and not re.match(r"mdr_mars_view_(name|desc|cost|weeks|gives|req|state)", m.group(1)) and not m.group(1).endswith(("_l",)) and m.group(1) not in keep:
        continue
    lines.append(line)
g = "\n".join(lines)
blocks = re.split(r"^\tcontainerWindowType = \{\n", g, flags=re.M)[1:]
win = {re.search(r'name = "(\w+)"', b).group(1): b for b in blocks}
hide_prefix = ()
exec(compile(src[src.index("def render"):src.index("pages = [")], "mock_render", "exec"))
m = next(x for x in sc.MODULES if x[0] == VIEW)
sample.update({"?mdr_col_mars_pop|0": "18", "?mdr_col_mars_cap|0": "32", "?mdr_col_mars_morale|0": "74", "?mdr_mars_science_total|1": "2.2",
               "?mdr_mars_built|0": "5", "?mdr_mars_jobs|0": "1", "mdr_mars_route_state": loc["MDR_MARS_ROUTE_ON_V"].replace("$$", "$"),
               "?mdr_col_mars_water|0": "61", "?mdr_col_mars_food|0": "44", "?mdr_col_mars_energy|0": "72", "?mdr_col_mars_oxygen|0": "31",
               "?mdr_col_mars_water_net|+1": "+0.6", "?mdr_col_mars_food_net|+1": "-0.1", "?mdr_col_mars_energy_net|+1": "+0.8", "?mdr_col_mars_oxygen_net|+1": "-0.3",
               "mdr_mars_sel_title": "CASILLA 8 · LIBRE", "mdr_mars_sel_state": loc["MDR_MARS_SEL_READY"],
               "mdr_mars_view_name": m[2], "mdr_mars_view_desc": m[4], "mdr_mars_view_cost": f"§Y${m[6]}B§!".replace(".", ","), "mdr_mars_view_weeks": f"{m[7]} semanas", "mdr_mars_view_gives": f"§G{m[11]}§!",
               "mdr_mars_view_req": loc[f"MDR_MARS_MOD_{VIEW.upper()}_REQ_OK"], "mdr_mars_works": "§YLaboratorio de radiación§! · casilla 6 · faltan 9 semanas",
               "mdr_mars_lock_h3": loc["MDR_MARS_LOCK_H3_OK"], "mdr_mars_lock_h4": loc["MDR_MARS_LOCK_H4_NO"], "mdr_mars_lock_p20": loc["MDR_MARS_LOCK_P20_NO"], "mdr_mars_lock_tech": loc["MDR_MARS_LOCK_TECH_NO"],
               "?mdr_mars_s6_left|0": "9"})
for x in sc.MODULES:
    sample[f"?mdr_mars_n_{x[0]}|0"] = str(sum(1 for v in BUILT.values() if v == x[0]))
_load = load
FRAMES = {"water": 31, "food": 23, "energy": 37, "oxygen": 16}
order = iter(["water", "food", "energy", "oxygen"])


def load(name, frame=1):
    if name == "GFX_mdr_space_meter":
        return _load(name, FRAMES[next(order)])
    return _load(name, frame)


globals()["load"] = load
im = render("mdr_mars_window", 0)
bg = tile("GFX_mdr_space_window", im.width, im.height)
base = Image.new("RGBA", im.size, (24, 50, 62, 255))
base.alpha_composite(bg)
a = im.copy()
px = a.load()
for yy in range(a.height):
    for xx in range(a.width):
        r, g_, b, al = px[xx, yy]
        if (r, g_, b) == (24, 26, 28) or (r, g_, b) == (88, 86, 80):
            px[xx, yy] = (0, 0, 0, 0)
base.alpha_composite(a)
base.convert("RGB").save(sp + "/colonia_marte_mock.png")
print(base.size)
