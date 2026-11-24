# Rough preview of the menu pages from interface/mdr_space.gui: real sprites, approximate fonts, sample values.
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

sp = sys.argv[1]
MD = "../Millennium-Dawn-2.0.0/"
GAME = (__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/")
sprites = {}
for f in glob.glob(GAME + "interface/*.gfx") + glob.glob(MD + "interface/*.gfx") + glob.glob("interface/*.gfx"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'name\s*=\s*"(GFX_\w+)"\s*texture[Ff]ile\s*=\s*"([^"]+)"(?:\s*noOfFrames\s*=\s*(\d+))?', t, re.I):
        sprites[m.group(1)] = (m.group(2), int(m.group(3) or 1))


def load(name, frame=1):
    if name not in sprites:
        return None
    path, frames = sprites[name]
    for root in ("", MD, GAME):
        for p in (root + path, root + path.replace(".tga", ".dds")):
            if os.path.exists(p):
                im = Image.open(p).convert("RGBA")
                w = im.width // frames
                return im.crop(((frame - 1) * w, 0, frame * w, im.height))
    return None


loc = {}
for line in open("localisation/spanish/mdr_space_l_spanish.yml", encoding="utf-8-sig"):
    m = re.match(r' (\w+):\d* "(.*)"', line)
    if m:
        loc[m.group(1)] = m.group(2)
sample = {"mdr_space_agency_name": "Roscosmos", "ROOT.GetName": "Rusia", "mdr_space_tier_text": "Potencia espacial", "?mdr_space_techs|0": "8", "?mdr_space_sites|0": "4", "?mdr_space_budget_pct|1": "0.3", "?mdr_space_science|0": "126", "?mdr_space_bonus_research_pct|1": "0.6", "mdr_space_next_tech": "Cápsula reutilizable", "?gdp_total|0": "3049", "?mdr_space_year_cost|2": "9.14", "?mdr_space_week_cost|3": "0.176", "?treasury|1": "40.0", "?mdr_space_science_week|1": "9.6", "?mdr_space_bonus_sites_pct|0": "3", "mdr_space_minus_text": "-0,1%", "mdr_space_plus_text": "+0,1%", "mdr_space_priority_sites": loc.get("MDR_SPACE_PRIORITY_SITES_OK", ""), "mdr_space_priority_budget": loc.get("MDR_SPACE_PRIORITY_BUDGET_OK", ""), "mdr_space_req_tech": loc.get("MDR_SPACE_REQ_TECH_NO", ""), "mdr_space_req_gdp": loc.get("MDR_SPACE_REQ_GDP_OK", ""), "mdr_space_req_money": loc.get("MDR_SPACE_REQ_MONEY_OK", "")}
sample.update({"?mdr_space_sites|0": "4", "?mdr_space_site_speed_pct|1": "12.9", "?mdr_space_site_reliability_pct|1": "5.1", "?mdr_space_site_cost_pct|1": "3.6", "?mdr_space_site_science_week|1": "3.2"})
COLORS = {"Y": (255, 214, 72), "G": (90, 220, 90), "R": (235, 80, 70), "W": (255, 255, 255)}
FONT = {"hoi_16mbs": ("arialbd.ttf", 12), "hoi_18mbs": ("arialbd.ttf", 14), "hoi_18": ("arial.ttf", 14), "hoi_24header": ("georgia.ttf", 20), "hoi_36header": ("georgia.ttf", 22)}


def resolve(key):
    s = loc.get(key, key)
    for _ in range(4):
        s = re.sub(r"\[([^\]]+)\]", lambda m: sample.get(m.group(1), m.group(0)), s)
        s = re.sub(r"\$(MDR_SPACE_\w+)\$", lambda m: "63", s)
    return s


def segments(s):
    out, colour = [], (232, 232, 226)
    for part in re.split(r"(§[A-Za-z!])", s):
        if part.startswith("§"):
            colour = COLORS.get(part[1], (232, 232, 226)) if part[1] != "!" else (232, 232, 226)
        elif part:
            out.append((part, colour))
    return out


def draw_text(d, x, y, w, font, s, fmt):
    f = ImageFont.truetype(*FONT.get(font, ("arial.ttf", 12)))
    words = []
    for text_, c in segments(s):
        for token in re.findall(r"\S+\s*", text_):
            words.append((token, c))
    lines, cur, width = [], [], 0
    for token, c in words:
        tw = d.textlength(token, font=f)
        if width + d.textlength(token.rstrip(), font=f) > w and cur:
            lines.append((cur, width))
            cur, width = [], 0
        cur.append((token, c))
        width += tw
    if cur:
        lines.append((cur, width))
    for i, (line, lw) in enumerate(lines):
        cx = x + (w - lw) / 2 if fmt == "center" else (x + w - lw if fmt == "right" else x)
        for token, c in line:
            d.text((cx, y + i * (f.size + 4)), token, font=f, fill=c)
            cx += d.textlength(token, font=f)


def tile(name, w, h):
    src = load(name)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if src is None:
        return out
    b = 64 if "window2" in name else 40
    b = min(b, src.width // 2 - 1, src.height // 2 - 1)
    for sy0, sy1, dy0, dy1 in ((0, b, 0, b), (b, src.height - b, b, h - b), (src.height - b, src.height, h - b, h)):
        for sx0, sx1, dx0, dx1 in ((0, b, 0, b), (b, src.width - b, b, w - b), (src.width - b, src.width, w - b, w)):
            if dx1 > dx0 and dy1 > dy0 and sx1 > sx0 and sy1 > sy0:
                out.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


g = open("interface/mdr_space.gui", encoding="utf-8").read()
blocks = re.split(r"^\tcontainerWindowType = \{\n", g, flags=re.M)[1:]
win = {re.search(r'name = "(\w+)"', b).group(1): b for b in blocks}
hide_prefix = ("mdr_space_picture_usa", "mdr_space_picture_chi", "mdr_space_picture_any", "mdr_space_logo_usa", "mdr_space_logo_any", "mdr_space_logo_chi", "mdr_space_logo_fra", "mdr_space_logo_eng", "mdr_space_logo_raj", "mdr_space_logo_isr")


def render(name, nav_on, hide=()):
    b = win[name]
    size = re.search(r"size = \{ width = (\d+) height = (\d+) \}", b)
    W, H = int(size.group(1)), int(size.group(2))
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    im.paste((24, 26, 28, 255), (0, 0, W, H))
    ImageDraw.Draw(im).rectangle([0, 0, W - 1, H - 1], outline=(88, 86, 80, 255), width=2)
    d = ImageDraw.Draw(im)
    lines = b.split("\n")
    i = 0
    text_after = []
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if s.startswith("containerWindowType"):
            chunk = "\n".join(lines[i:i + 9])
            m = re.search(r'name = "(\w+)"\s*position = \{ x = (-?\d+) y = (-?\d+) \}\s*size = \{ width = (-?\d+) height = (\d+) \}', chunk)
            sp_ = re.search(r'quadTextureSprite = "(\w+)"', chunk)
            if m and sp_:
                pic = load(sp_.group(1))
                if pic and sp_.group(1) == "GFX_mdr_space_panel":
                    w_, h_ = int(m.group(4)), int(m.group(5))
                    if w_ < 0:
                        w_ = W - int(m.group(2)) + w_
                    out = Image.new("RGBA", (w_, h_), (0, 0, 0, 0))
                    b_ = 8
                    for sx0, sx1, dx0, dx1 in ((0, b_, 0, b_), (b_, 16, b_, w_ - b_), (16, 24, w_ - b_, w_)):
                        for sy0, sy1, dy0, dy1 in ((0, b_, 0, b_), (b_, 16, b_, h_ - b_), (16, 24, h_ - b_, h_)):
                            out.alpha_composite(pic.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
                    im.alpha_composite(out, (int(m.group(2)), int(m.group(3))))
                elif pic:
                    im.alpha_composite(pic, (int(m.group(2)), int(m.group(3))))
        if s.startswith("iconType") and "{" in s and "name =" in s:
            m = re.search(r'name = "(\w+)" spriteType = "(\w+)" position = \{ x = (-?\d+) y = (-?\d+) \}(?: scale = ([\d.]+))?', s)
            if m and m.group(1) not in hide and not m.group(1).endswith(tuple(f"_{n}" for n in ("space", "rocketry", "orbit", "moon", "landmars", "marsbase", "mars", "asteroid"))) and m.group(1) not in hide_prefix:
                pic = load(m.group(2))
                if pic:
                    if m.group(5):
                        k = float(m.group(5))
                        pic = pic.resize((int(pic.width * k), int(pic.height * k)), Image.LANCZOS)
                    im.alpha_composite(pic, (int(m.group(3)), int(m.group(4))))
        if s.startswith("buttonType") and "position" in s:
            m = re.search(r'name = "(\w+)" position = \{ x = (-?\d+) y = (-?\d+) \} (?:quadTextureSprite|spriteType) = "(\w+)"(?: frame = (\d))?', s)
            if m and int(m.group(2)) > -100:
                state_on = m.group(1).endswith("_on")
                state_off = m.group(1).endswith("_off")
                num = re.search(r"nav_(\d)_", m.group(1))
                draw = True
                if num and (state_on or state_off):
                    draw = (int(num.group(1)) == nav_on) == state_on
                if draw:
                    pic = load(m.group(4), int(m.group(5) or 1))
                    if pic:
                        im.alpha_composite(pic, (int(m.group(2)), int(m.group(3))))
                        t = re.search(r'buttonText = "(\w+)"', s)
                        if t:
                            text_after.append((int(m.group(2)), int(m.group(3)) + (pic.height - 12) // 2 - 1, pic.width, "hoi_16mbs", resolve(t.group(1)), "center"))
        if s.startswith("instantTextbox"):
            m = re.search(r'name = "(\w+)" position = \{ x = (-?\d+) y = (-?\d+) \} font = "(\w+)".*?text = "(\w+)" maxWidth = (\d+).*?format = (\w+)', s)
            if m:
                text_after.append((int(m.group(2)), int(m.group(3)), int(m.group(6)), m.group(4), resolve(m.group(5)), m.group(7)))
        i += 1
    for x, y, w, font, val, fmt in text_after:
        draw_text(d, x, y, w, font, val, fmt)
    return im


pages = [render("mdr_space_summary_window", 1), render("mdr_space_finance_window", 5), render("mdr_space_none_window", 0)]
sheet = Image.new("RGBA", (sum(p.width for p in pages) + 40, pages[0].height + 20), (58, 74, 58, 255))
x = 10
for p in pages:
    sheet.alpha_composite(p, (x, 10))
    x += p.width + 10
sheet.convert("RGB").save(sp + "/menu_mock.png")
print(sheet.size)
