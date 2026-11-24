# Draws the Economy screen of interface/MD_countryeconomyview.gui roughly as the game would: real sprites, approximate fonts and
# sample numbers. Only to check the layout without opening the game. Run from the mod folder:
#   python herramientas/vista_economia/render_economia.py <out.png> [gui file]
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else "interface/MD_countryeconomyview.gui"
MD = "../Millennium-Dawn-2.0.3/"
GAME = (__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/")


def tokens(text):
    return re.findall(r'"[^"]*"|#[^\n]*|[{}=]|[^\s{}="#]+', text)


def parse(toks, i=0):
    out = []
    while i < len(toks):
        t = toks[i]
        if t.startswith("#"):
            i += 1
            continue
        if t == "}":
            return out, i + 1
        if i + 1 < len(toks) and toks[i + 1] == "=":
            if i + 2 < len(toks) and toks[i + 2] == "{":
                sub, i = parse([x for x in toks], i + 3)
                out.append((t.lower(), sub))
            else:
                out.append((t.lower(), toks[i + 2].strip('"') if i + 2 < len(toks) else ""))
                i += 3
        else:
            i += 1
    return out, i


def clean(text):
    return "\n".join(l.split("#")[0] if '"' not in l else l for l in text.split("\n"))


sprites = {}
for f in glob.glob(GAME + "interface/*.gfx") + glob.glob(MD + "interface/*.gfx") + glob.glob("interface/*.gfx"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'(\w+)\s*=\s*\{([^{}]*?name\s*=\s*"(GFX_\w+)"[^{}]*)\}', t):
        body = m.group(2)
        tf = re.search(r'texture[Ff]ile1?\s*=\s*"([^"]+)"', body)
        if not tf:
            continue
        nf = re.search(r"noOfFrames\s*=\s*(\d+)", body)
        bs = re.search(r"borderSize\s*=\s*\{\s*x\s*=\s*(\d+)", body)
        sprites[m.group(3)] = (tf.group(1).replace("\\\\", "/"), int(nf.group(1)) if nf else 1, int(bs.group(1)) if bs else 0)

cache = {}


def load(name, frame=1):
    if name not in sprites:
        return None
    path, frames, _ = sprites[name]
    key = (name, frame)
    if key in cache:
        return cache[key]
    im = None
    for root in ("", "./", MD, GAME):
        for p in (root + path, root + path.replace(".tga", ".dds")):
            if os.path.exists(p):
                try:
                    im = Image.open(p).convert("RGBA")
                except Exception:
                    im = None
                break
        if im:
            break
    if im:
        w = im.width // frames
        im = im.crop(((frame - 1) * w, 0, frame * w, im.height))
    cache[key] = im
    return im


def nine(src, w, h, b):
    b = max(2, min(b, src.width // 2 - 1, src.height // 2 - 1))
    out = Image.new("RGBA", (max(w, 1), max(h, 1)))
    for sy0, sy1, dy0, dy1 in ((0, b, 0, b), (b, src.height - b, b, h - b), (src.height - b, src.height, h - b, h)):
        for sx0, sx1, dx0, dx1 in ((0, b, 0, b), (b, src.width - b, b, w - b), (src.width - b, src.width, w - b, w)):
            if dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


loc = {}
for f in glob.glob(MD + "localisation/spanish/*.yml") + glob.glob("localisation/spanish/*.yml") + glob.glob(MD + "localisation/english/*.yml"):
    for line in open(f, encoding="utf-8-sig", errors="ignore"):
        m = re.match(r' (\w+):\d* "(.*)"', line)
        if m and m.group(1) not in loc:
            loc[m.group(1)] = m.group(2)

FONT = {"hoi_30header": 20, "hoi_30": 20, "hoi_24header": 17, "hoi_20bs": 13, "hoi_18mbs": 13, "hoi_16mbs": 12, "hoi_14": 11}
COL = {"Y": (255, 214, 72), "G": (90, 220, 90), "R": (235, 80, 70), "H": (255, 214, 72), "W": (232, 232, 226)}


def resolve(key):
    s = loc.get(key, key)
    for _ in range(4):
        s = re.sub(r"\$(\w+)\$", lambda m: loc.get(m.group(1), ""), s)
    s = re.sub(r"\[[^\]]*\]", "12.3", s)
    s = re.sub(r"£\w+", "", s)
    return s.replace("\\n", " ")


def draw_text(d, x, y, w, font, s, fmt):
    f = ImageFont.truetype("arialbd.ttf" if font.endswith("bs") or "header" in font else "arial.ttf", FONT.get(font, 12))
    col = (232, 232, 226)
    parts = []
    for p in re.split(r"(§[A-Za-z!])", s):
        if p.startswith("§"):
            col = COL.get(p[1], (232, 232, 226))
        elif p:
            parts.append((p, col))
    tw = sum(d.textlength(p, font=f) for p, _ in parts)
    cx = x
    if fmt == "right":
        cx = x + w - tw
    elif fmt == "center":
        cx = x + (w - tw) / 2
    for p, c in parts:
        d.text((cx, y), p, font=f, fill=c)
        cx += d.textlength(p, font=f)


def num(v, default=0):
    m = re.match(r"-?\d+", str(v))
    return int(m.group(0)) if m else default


def pair(block, key):
    for k, v in block:
        if k == key and isinstance(v, list):
            vals = {a: b for a, b in v if isinstance(b, str)}
            return vals
    return None


def get(block, key):
    for k, v in block:
        if k == key:
            return v
    return None


def draw(im, d, block, ox, oy, w, h, depth=0):
    bg = get(block, "background")
    if isinstance(bg, list):
        sp = get(bg, "quadtexturesprite") or get(bg, "spritetype")
        pic = load(sp) if sp else None
        if pic and w > 0 and h > 0 and sp not in ("GFX_tiled_window_transparent",):
            im.alpha_composite(nine(pic, w, h, sprites[sp][2] or 8), (ox, oy))
    for k, v in block:
        if not isinstance(v, list):
            continue
        p = pair(v, "position") or {}
        x, y = ox + num(p.get("x")), oy + num(p.get("y"))
        sz = pair(v, "size") or {}
        if k == "containerwindowtype":
            nm = get(v, "name")
            cw = num(sz.get("width"), w) if "%" not in str(sz.get("width", "")) else w
            ch = num(sz.get("height"), 560) if "%" not in str(sz.get("height", "")) else min(h, 560)
            draw(im, d, v, x, y, cw, ch, depth + 1)
        elif k == "icontype":
            sp = get(v, "spritetype") or get(v, "quadtexturesprite")
            pic = load(sp, num(get(v, "frame"), 1)) if sp else None
            if pic:
                sc = get(v, "scale")
                if sc:
                    pic = pic.resize((int(pic.width * float(sc)), max(1, int(pic.height * float(sc)))))
                im.alpha_composite(pic, (x, y))
        elif k == "buttontype":
            sp = get(v, "spritetype") or get(v, "quadtexturesprite")
            pic = load(sp, num(get(v, "frame"), 1)) if sp else None
            if pic:
                if sz.get("width"):
                    pic = pic.resize((num(sz["width"]), num(sz["height"])))
                im.alpha_composite(pic, (x, y))
                t = get(v, "buttontext")
                if t:
                    draw_text(d, x, y + (pic.height - 14) // 2, pic.width, "hoi_16mbs", resolve(t), "center")
        elif k == "instanttextboxtype":
            fmt = (get(v, "format") or "left").lower()
            mw = num(get(v, "maxwidth"), 150)
            draw_text(d, x, y, mw, get(v, "font") or "hoi_16mbs", resolve(get(v, "text") or ""), fmt)


text = clean(open(SRC, encoding="utf-8-sig").read())
tree, _ = parse(tokens(text))
root = None
for k, v in tree[0][1] if tree and tree[0][0] == "guitypes" else tree:
    if k == "containerwindowtype" and get(v, "name") == "MD_countryeconomyview":
        root = v
W, H = 960, 1000
im = Image.new("RGBA", (W, H), (20, 22, 26, 255))
d = ImageDraw.Draw(im)
draw(im, d, root, 0, 0, 939, H)
im.convert("RGB").save(OUT)
print("ok")
