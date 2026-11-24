# Draws interface/mdr_ship_sale.gui as the game would, roughly: real sprites, approximate fonts, sample values.
# Checks the layout without opening the game. Run from the mod folder: python herramientas/vista_barcos/render_gui.py <out folder>
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
MD = "../Millennium-Dawn-2.0.0/"
GAME = (__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/")
sprites = {}
for f in glob.glob(GAME + "interface/*.gfx") + glob.glob(MD + "interface/*.gfx") + glob.glob("interface/*.gfx"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'(\w+)\s*=\s*\{\s*name\s*=\s*"(GFX_\w+)"\s*texture[Ff]ile1?\s*=\s*"([^"]+)"(?:[^}]*?noOfFrames\s*=\s*(\d+))?(?:[^}]*?borderSize\s*=\s*\{\s*x\s*=\s*(\d+))?', t):
        sprites[m.group(2)] = (m.group(3).replace("\\\\", "/").replace("//", "/"), int(m.group(4) or 1), int(m.group(5) or 0), m.group(1))


def load(name, frame=1):
    if name not in sprites:
        return None
    path, frames, _, _ = sprites[name]
    for root in ("", MD, GAME):
        for p in (root + path, root + path.replace(".tga", ".dds")):
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA")
                w = im.width // frames
                return im.crop(((frame - 1) * w, 0, frame * w, im.height))
    return None


def nine(src, w, h, b):
    out = Image.new("RGBA", (w, h))
    for sy0, sy1, dy0, dy1 in ((0, b, 0, b), (b, src.height - b, b, h - b), (src.height - b, src.height, h - b, h)):
        for sx0, sx1, dx0, dx1 in ((0, b, 0, b), (b, src.width - b, b, w - b), (src.width - b, src.width, w - b, w)):
            if dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


loc = {}
for line in open("localisation/spanish/mdr_ship_sale_l_spanish.yml", encoding="utf-8-sig"):
    m = re.match(r' (\w+):\d* "(.*)"', line)
    if m:
        loc[m.group(1)] = m.group(2)
SAMPLE = {"ROOT.GetName": "Rusia", "?ROOT.mdr_sale_target.GetName": "Vietnam", "?ROOT.mdr_sale_buyer_money|1": "41.2",
          "?ROOT.treasury|1": "272.0", "?ROOT.num_of_naval_factories|0": "19", "?ROOT.mdr_sc_buyer^num|0": "3", "?ROOT.mdr_sale_delivered|0": "4",
          "?ROOT.num_ships|0": "152", "?ROOT.mdr_sale_pending|0": "2", "?ROOT.mdr_sale_have|0": "17", "?ROOT.mdr_sale_qty|0": "2",
          "?ROOT.mdr_sale_year|0": "1990", "?ROOT.mdr_sale_cost|2": "2.18", "?ROOT.mdr_sale_days|0": "912", "?ROOT.mdr_sale_total|2": "2.74",
          "?ROOT.mdr_sale_unit|2": "1.37", "?ROOT.mdr_sale_prob|0": "71", "?ROOT.mdr_sale_pct|0": "120", "?ROOT.mdr_sale_ref|2": "1.14",
          "?ROOT.mdr_sd_qty|0": "2", "?ROOT.mdr_sd_design|0": "3", "?ROOT.mdr_sd_have|0": "9", "?ROOT.mdr_sale_n_build|0": "3",
          "?ROOT.mdr_sale_n_refit|0": "1", "?ROOT.mdr_sale_n_queue|0": "2", "?ROOT.mdr_sale_last_who.GetName": "Vietnam",
          "?ROOT.mdr_sale_lot_count|0": "5"}
for r in (1, 2, 3):
    SAMPLE.update({f"?ROOT.mdr_sale_op{r}_who.GetName": ["India", "Argelia", "Vietnam"][r - 1], f"?ROOT.mdr_sale_op{r}_pct|0": str([38, 81, 55][r - 1]), f"?ROOT.mdr_sale_op{r}_days|0": str([254, 77, 120][r - 1]),
                   f"?ROOT.mdr_sale_h{r}_who.GetName": ["Vietnam", "Siria", "Argelia"][r - 1]})
for r in range(1, 9):
    SAMPLE.update({f"?ROOT.mdr_sale_c{r}_who.GetName": "India", f"?ROOT.mdr_sale_c{r}_qty|0": "2", f"?ROOT.mdr_sale_c{r}_unit|2": "1.37", f"?ROOT.mdr_sale_c{r}_days|0": "254"})
for t in range(1, 19):
    SAMPLE[f"?ROOT.mdr_sale_lothave_{t}|0"] = str((t * 7) % 23)
    SAMPLE[f"?ROOT.mdr_sale_lot_{t}|0"] = "2" if t in (10, 12) else "0"
DEFINED = {"ROOT.mdr_sale_type_text": "Destructor", "ROOT.mdr_sale_gen_text": "1990", "ROOT.mdr_sale_price_text": loc["MDR_SALE_PRICE_PCT"],
           "ROOT.mdr_sale_rel_text": loc["MDR_SALE_REL_1"], "ROOT.mdr_sale_sanction_text": loc["MDR_SALE_SANCTION_NO"], "ROOT.mdr_sale_port_text": loc["MDR_SALE_PORT_YES"],
           "ROOT.mdr_sale_reason_text": "", "ROOT.mdr_sd_hull_text": "Destructor de 2005",
           "ROOT.mdr_sale_op1_type_text": "Destructor", "ROOT.mdr_sale_op2_type_text": "Fragata", "ROOT.mdr_sale_op3_type_text": "Corbeta",
           "ROOT.mdr_sale_h1_type_text": "Destructor", "ROOT.mdr_sale_h2_type_text": "Corbeta", "ROOT.mdr_sale_h3_type_text": "Lancha patrullera"}
for r in range(1, 9):
    DEFINED[f"ROOT.mdr_sale_c{r}_type_text"] = ["Destructor", "Fragata", "Corbeta"][r % 3]
    DEFINED[f"ROOT.mdr_sale_c{r}_kind_text"] = ["Construcción", "De tu flota", "Reacondicionamiento"][r % 3]
SLOTS_T = ["Proa 1", "Centro 1", "Centro 2", "Popa 1"]
SLOTS_B = ["Batería", "Auxiliar", "Auxiliar 2", "Auxiliar 3", "Radar/Sonar", "Control de tiro", "Motor"]
for k, n in enumerate(SLOTS_T, 1):
    DEFINED[f"ROOT.mdr_sale_slot_t{k}_text"] = n
for k, n in enumerate(SLOTS_B, 1):
    DEFINED[f"ROOT.mdr_sale_slot_b{k}_text"] = n
for t in range(1, 19):
    DEFINED[f"ROOT.mdr_sale_lot{t}_text"] = loc[f"MDR_SALE_LOT{t}_ON" if t in (10, 12) else f"MDR_SALE_LOT{t}_OFF"]
COL = {"Y": (255, 214, 72), "G": (90, 220, 90), "R": (235, 80, 70), "g": (150, 160, 175)}
FONT = {"hoi_16mbs": ("arialbd.ttf", 12), "hoi_18mbs": ("arialbd.ttf", 14), "hoi_24header": ("georgia.ttf", 20)}


def resolve(key, mode):
    s = loc.get(key, key)
    defined = dict(DEFINED)
    for tab, m in (("fleet", 0), ("batch", 2), ("refit", 3), ("build", 1), ("contracts", 4)):
        defined[f"ROOT.mdr_sale_tab_{tab}_text"] = loc[f"MDR_SALE_TAB_{tab.upper()}_{'ON' if m == mode else 'OFF'}"]
    defined["ROOT.mdr_sale_cost_text"] = loc["MDR_SALE_COST_FLEET" if mode == 0 else ("MDR_SALE_COST_BATCH" if mode == 2 else "MDR_SALE_COST_BUILD")]
    defined["ROOT.mdr_sale_build_title_text"] = loc["MDR_SALE_REFIT_TITLE_T" if mode == 3 else "MDR_SALE_BUILD_TITLE_T"]
    defined["ROOT.mdr_sale_build_note_text"] = loc["MDR_SALE_REFIT_NOTE_T" if mode == 3 else "MDR_SALE_BUILD_NOTE_T"]
    for _ in range(5):
        s = re.sub(r"\[([^\]]+)\]", lambda m: defined.get(m.group(1), SAMPLE.get(m.group(1), m.group(0))), s)
    return s.replace("$$", "$").replace("\\n", "\n")


def draw_text(d, x, y, w, font, s, fmt):
    f = ImageFont.truetype(*FONT.get(font, ("arial.ttf", 12)))
    for li, line in enumerate(s.split("\n")):
        parts, c = [], (232, 232, 226)
        for p in re.split(r"(§[A-Za-z!])", line):
            if p.startswith("§"):
                c = COL.get(p[1], (232, 232, 226))
            elif p:
                parts.append((p, c))
        words = []
        for p, c in parts:
            for tok in re.findall(r"\S+\s*", p):
                words.append((tok, c))
        lines, cur, width = [], [], 0
        for tok, c in words:
            tw = d.textlength(tok, font=f)
            if width + d.textlength(tok.rstrip(), font=f) > w and cur:
                lines.append((cur, width))
                cur, width = [], 0
            cur.append((tok, c))
            width += tw
        if cur:
            lines.append((cur, width))
        for i, (ln, lw) in enumerate(lines):
            cx = x + (w - lw) / 2 if fmt == "center" else x
            for tok, c in ln:
                d.text((cx, y), tok, font=f, fill=c)
                cx += d.textlength(tok, font=f)
            y += f.size + 4


ALL = open("interface/mdr_ship_sale.gui", encoding="utf-8").read()
# Which tab shows each element, and a sample ready-made design (2005 destroyer, air defence) for the slots.
sys.path.insert(0, "herramientas")
import make_ship_sale as gen  # noqa: E402
gen.build_window()
SAMPLE_HULL = gen.HULLS.index("destroyer_hull_3") + 1
SAMPLE_MODS = {f"mdr_sale_mod_{row}{k}": gen.sprite_of(m) for row, n in (("t", gen.TOP_MAX), ("b", gen.BOTTOM_MAX)) for k in range(1, n + 1) if (m := gen.slot_module(gen.HULLS[SAMPLE_HULL - 1], 2, row, k))}
DEFINED["ROOT.mdr_sale_design_text"] = loc["MDR_SD_ROLE_2"]
DEFINED["ROOT.mdr_sale_design_help_text"] = loc["MDR_SALE_DESIGN_HELP_PRESET"]


def hidden(name, mode):
    if name in gen.TAG and mode not in gen.TAG[name]:
        return True
    if name.startswith("mdr_sale_mod_"):
        return name not in SAMPLE_MODS
    if re.match(r"mdr_sale_(fleet|build)_tv_", name):
        return not name.endswith("_destroyer") or name.endswith("stealth_destroyer")
    m = re.match(r"mdr_sale_slot_([tb])(\d)", name)
    if m:
        return int(m.group(2)) > (len(SLOTS_T) if m.group(1) == "t" else len(SLOTS_B)) or (name.endswith("_req") and m.group(1) == "t")
    m = re.match(r"mdr_sale_tab_(\w+)_(on|off)$", name)
    if m:
        cur = {0: "fleet", 2: "batch", 3: "refit", 1: "build", 4: "contracts"}[mode]
        return (m.group(1) == cur) != (m.group(2) == "on")
    if name == "mdr_sale_send" and mode == 4:
        return True
    if name == "mdr_sale_contracts_empty":
        return True
    m = re.match(r"mdr_sale_c(\d)_", name)
    if m:
        return int(m.group(1)) > 3
    return False


def render(mode):
    src = ALL.split(chr(10) + chr(9) + "containerWindowType = {" + chr(10))[1]
    W, H = 1200, 740
    im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    im.alpha_composite(nine(load("GFX_mdr_space_window"), W, H, 24))
    d = ImageDraw.Draw(im)
    texts = []
    ox = oy = 0
    skip_depth = None
    depth = 1
    for line in src.split("\n"):
        s = line.strip()
        m = re.match(r'containerWindowType = \{ name = "(\w+)" position = \{ x = (-?\d+) y = (-?\d+) \} size = \{ width = (\d+) height = (\d+) \}', s)
        if m and skip_depth is None:
            pic = load("GFX_mdr_space_panel")
            im.alpha_composite(nine(pic, int(m.group(4)), int(m.group(5)), 8), (ox + int(m.group(2)), oy + int(m.group(3))))
            continue
        if s == "containerWindowType = {":
            depth += 1
            pending = True
            continue
        if s.startswith('name = "') and depth >= 2:
            cur = s.split('"')[1]
            continue
        if s.startswith("position = {") and depth >= 2 and skip_depth is None:
            m = re.search(r"x = (-?\d+) y = (-?\d+)", s)
            ox, oy = int(m.group(1)), int(m.group(2))
            continue
        if s == "}" and depth >= 2:
            if skip_depth == depth:
                skip_depth = None
            depth -= 1
            ox = oy = 0
            continue
        if skip_depth is not None:
            continue
        m = re.search(r'name = "(\w+)"', s)
        if not m or hidden(m.group(1), mode):
            continue
        name = m.group(1)
        pm = re.search(r"position = \{ x = (-?\d+) y = (-?\d+) \}", s)
        if not pm:
            continue
        x, y = ox + int(pm.group(1)), oy + int(pm.group(2))
        if s.startswith("iconType"):
            sp = re.search(r'spriteType = "(\w+)"', s).group(1)
            sp = SAMPLE_MODS.get(name, sp)
            fr = 26 if "bar" in name else 1
            pic = load(sp, fr)
            if pic:
                sc = re.search(r"scale = ([\d.]+)", s)
                if sc:
                    k = float(sc.group(1))
                    pic = pic.resize((int(pic.width * k), int(pic.height * k)))
                im.alpha_composite(pic, (x, y))
        elif s.startswith("buttonType"):
            sp = re.search(r'quadTextureSprite = "(\w+)"', s).group(1)
            fr = re.search(r"frame = (\d)", s)
            if "flag" in name:
                fl = Image.open(MD + "gfx/flags/" + ("SOV_democratic.tga" if name == "mdr_sale_flag_seller" else ("VIE_democratic.tga" if name == "mdr_sale_flag_buyer" else "RAJ_democratic.tga"))).convert("RGBA")
                size = (66, 42) if "seller" in name or "buyer" in name else (41, 26)
                im.alpha_composite(fl.resize(size), (x, y))
                continue
            pic = load(sp, int(fr.group(1)) if fr else 1)
            if pic:
                im.alpha_composite(pic, (x, y))
                t = re.search(r'buttonText = "(\w+)"', s)
                if t:
                    texts.append((x, y + (pic.height - 14) // 2, pic.width, "hoi_16mbs", resolve(t.group(1), mode), "center"))
        elif s.startswith("instantTextboxType"):
            mm = re.search(r'font = "(\w+)".*?text = "(\w+)" maxWidth = (\d+).*?format = (\w+)', s)
            texts.append((x, y, int(mm.group(3)), mm.group(1), resolve(mm.group(2), mode), mm.group(4)))
    for t in texts:
        draw_text(d, *t)
    return im


names = {0: "flota", 2: "lote", 1: "construir", 3: "reacondicionar", 4: "contratos"}
for mode, n in names.items():
    render(mode).convert("RGB").save(os.path.join(OUT, f"ventana_{n}.png"))
print("ok")
