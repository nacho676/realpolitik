# Preview of the new ship sale window (stage 1): real sprites from our space menu, MD and the base game, sample values.
# Run from the mod folder: python herramientas/vista_barcos/mock.py <output folder>
import glob, os, re, sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
MD = "../Millennium-Dawn-2.0.0/"
GAME = (__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/")
ICONS = "gfx/interface/mdr/space/icons/"

sprites = {}
for f in glob.glob(GAME + "interface/*.gfx") + glob.glob(MD + "interface/*.gfx"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    for m in re.finditer(r'name\s*=\s*"(GFX_\w+)"\s*texture[Ff]ile\s*=\s*"([^"]+)"', t):
        sprites[m.group(1)] = m.group(2)


def img(path):
    for root in ("", MD, GAME):
        for p in (root + path, root + path.replace(".tga", ".dds")):
            if os.path.exists(p):
                return Image.open(p).convert("RGBA")
    raise FileNotFoundError(path)


def sprite(name):
    return img(sprites[name])


def nine(src, w, h, b=None):
    b = b or min(src.width, src.height) // 3
    out = Image.new("RGBA", (w, h))
    for sy0, sy1, dy0, dy1 in ((0, b, 0, b), (b, src.height - b, b, h - b), (src.height - b, src.height, h - b, h)):
        for sx0, sx1, dx0, dx1 in ((0, b, 0, b), (b, src.width - b, b, w - b), (src.width - b, src.width, w - b, w)):
            if dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


F = {k: ImageFont.truetype(*v) for k, v in {"s": ("arialbd.ttf", 12), "m": ("arialbd.ttf", 14), "n": ("arial.ttf", 13),
                                             "h": ("georgia.ttf", 22), "t": ("georgia.ttf", 17)}.items()}
WHITE, GREY, YEL, GRN, RED, BLUE = (232, 232, 226), (150, 160, 175), (255, 214, 72), (90, 220, 90), (235, 80, 70), (120, 180, 255)

W, H = 1280, 800
im = Image.new("RGBA", (W, H), (0, 0, 0, 255))
im.alpha_composite(nine(img(ICONS + "window.dds"), W, H, 32))
back = img(ICONS + "backdrop.dds").resize((W - 16, H - 16))
back.putalpha(70)
im.alpha_composite(back, (8, 8))
d = ImageDraw.Draw(im)


def text(x, y, s, font="n", col=WHITE, w=None, align="left"):
    """Draws text with §Y..§! colour codes."""
    parts, c = [], col
    for p in re.split(r"(§[A-Za-z!])", s):
        if p.startswith("§"):
            c = {"Y": YEL, "G": GRN, "R": RED, "B": BLUE, "g": GREY}.get(p[1], col)
        elif p:
            parts.append((p, c))
    total = sum(d.textlength(p, font=F[font]) for p, _ in parts)
    if w and align == "center":
        x += (w - total) / 2
    elif w and align == "right":
        x += w - total
    for p, c in parts:
        d.text((x, y), p, font=F[font], fill=c)
        x += d.textlength(p, font=F[font])


def panel(x, y, w, h):
    im.alpha_composite(nine(img(ICONS + "panel.dds"), w, h, 8), (x, y))


def button(x, y, label, w=123, h=34, hot=False):
    b = nine(img(ICONS + "btn_123x34.dds"), w, h, 10)
    im.alpha_composite(b, (x, y))
    if hot:
        d.rectangle([x + 1, y + 1, x + w - 2, y + h - 2], outline=(214, 170, 60), width=2)
    text(x, y + (h - 14) // 2, label, "s", WHITE, w, "center")


def rule(x, y, w=230):
    im.alpha_composite(img(ICONS + "rule.dds").resize((w, 2)), (x, y))


def flag(tag, x, y, h=44):
    f = img(f"gfx/flags/{tag}_democratic.tga")
    im.alpha_composite(f.resize((int(f.width * h / f.height), h)), (x, y))


# Header: seller, buyer, quick numbers.
im.alpha_composite(img(ICONS + "header.dds").resize((W - 24, 58)), (12, 12))
flag("ARG", 26, 19)
text(98, 20, "Argentina", "h", WHITE)
text(98, 47, "ARMADA VENDEDORA", "s", YEL)
d.polygon([(284, 36), (306, 36), (306, 30), (318, 41), (306, 52), (306, 46), (284, 46)], fill=GREY)
flag("URG", 330, 19)
text(402, 20, "Uruguay", "h", WHITE)
text(402, 47, "COMPRADOR · opinión §G+15§!", "s", GREY)
button(560, 24, "Elegir país")
for i, (lbl, val) in enumerate((("TESORO", "§Y$272.0B§!"), ("ASTILLEROS", "§Y19§!"), ("PEDIDOS", "§Y2§!"), ("ENTREGADOS", "§G4§!"))):
    x = 740 + i * 128
    d.line([(x, 20), (x, 62)], fill=(60, 90, 130), width=1)
    text(x + 10, 22, lbl, "s", WHITE)
    text(x + 10, 42, val, "m")

# Left column: sections like the space menu.
panel(16, 80, 224, 664)
y = 92
for title, tabs in (("OPERACIONES", ["Transferir / Vender", "Venta en lote", "Vender y reacondicionar", "Construir barco", "Contratos"]),):
    text(30, y, title, "s", WHITE)
    y += 22
    for i, t in enumerate(tabs):
        tab = img(ICONS + "sidetab.dds")
        on = t == "Construir barco"
        if on:
            im.alpha_composite(nine(tab.crop((118, 0, 236, 32)), 206, 32, 10), (24, y))
        text(40, y + 8, t, "m", YEL if on else WHITE)
        y += 36
y += 14
text(30, y, "ESTADO", "s", WHITE)
y += 24
for a, b in (("Oficina de enlace naval", "§GActiva§!"), ("Barcos en alta mar", "§Y3§!"), ("Relación", "§GAmistosa§!"), ("Riesgo de sanción", "§GNinguno§!")):
    text(32, y, a, "n", GREY)
    text(32, y + 16, b, "s")
    y += 40

# Center: Build ship page.
cx, cw = 252, 744
panel(cx, 80, cw, 92)
text(cx + 14, 90, "CLASE DE EXPORTACIÓN: §YExportación 3§! (nombre automático)", "m")
rule(cx + 14, 110, 360)
text(cx + 14, 118, "§R*§! Obligatoria y vacía  |  §G*§! Obligatoria y puesta  |  sin * opcional", "n", GREY)
text(cx + 14, 138, "Hace falta al menos un astillero. Tocá una casilla para ver los módulos que investigaste.", "n", GREY)
hull = img(MD + "gfx/interface/equipmentdesigner/naval/topviews/topview_destroyer.dds")
im.alpha_composite(hull.crop((20, 90, 490, 160)).resize((141, 21)), (cx + 14, 182))
text(cx + 170, 184, "Casco: §YDestructor 1990§!", "m")
for i, b in enumerate(("Casco", "Ícono del barco", "Lista de modelos")):
    button(cx + cw - 3 * 128 + i * 128, 176, b)

# Blueprint: plain grid (no watermark) with MD's top view of the hull.
bx, by, bw, bh = cx, 218, cw, 330
bp = Image.new("RGBA", (bw, bh), (22, 66, 128, 255))
bd = ImageDraw.Draw(bp)
for gx in range(0, bw, 16):
    bd.line([(gx, 0), (gx, bh)], fill=(40, 92, 160, 255) if gx % 80 else (66, 120, 190, 255))
for gy in range(0, bh, 16):
    bd.line([(0, gy), (bw, gy)], fill=(40, 92, 160, 255) if gy % 80 else (66, 120, 190, 255))
im.alpha_composite(nine(img(ICONS + "panel.dds"), bw, bh, 8), (bx, by))
im.alpha_composite(bp.crop((4, 4, bw - 4, bh - 4)), (bx + 4, by + 4))
big = hull.resize((int(hull.width * 1.3), int(hull.height * 1.3)))
im.alpha_composite(big, (bx + (bw - big.width) // 2, by + (bh - big.height) // 2))

slot_bg = img("gfx/interface/equipmentdesigner/equipment_module_bg.dds")
empty = img("gfx/interface/equipmentdesigner/module_slot_icon_empty.dds")


def slot(x, y, label, module=None, req=False):
    box = Image.new("RGBA", (86, 78), (14, 30, 54, 230))
    ImageDraw.Draw(box).rectangle([0, 0, 85, 77], outline=(96, 150, 220, 255), width=1)
    im.alpha_composite(box, (x, y))
    im.alpha_composite(slot_bg, (x + 5, y + 5))
    im.alpha_composite(sprite(module) if module else empty, (x + 5, y + 7))
    text(x, y + 56, label, "s", WHITE, 86, "center")
    if req:
        text(x + 76, y + 1, "*", "m", GRN if module else RED)


top = [("Proa 1", "GFX_SMI_module_naval_vls_cells_64", False), ("Centro 1", None, False), ("Centro 2", "GFX_SMI_module_ram_2", False), ("Popa 1", "GFX_SMI_module_light_helipad_1", False)]
for i, (l, m, r) in enumerate(top):
    slot(bx + 14 + i * 94, by + 10, l, m, r)
bottom = [("Batería", "GFX_SMI_module_76mm_gun_2", True), ("Auxiliar", "GFX_SMI_module_ciws_2", False), ("Auxiliar 2", None, False),
          ("Auxiliar 3", None, False), ("Radar/Sonar", "GFX_SMI_module_radar_3", True), ("Control de tiro", "GFX_SMI_module_screen_digital_integrated_fire_control", True),
          ("Munición", None, True), ("Motor", "GFX_SMI_module_surface_jet_turbine_power2", True)]
for i, (l, m, r) in enumerate(bottom):
    slot(bx + 14 + i * 90, by + bh - 88, l, m, r)
text(bx + bw - 250, by + 16, "VELOCIDAD §Y29 nudos§!", "s")
text(bx + bw - 250, by + 34, "ANTIBUQUE §Y61§!   ANTIAÉREO §Y48§!", "s")
text(bx + bw - 250, by + 52, "ANTISUBMARINO §Y22§!   ALCANCE §Y4.800 km§!", "s")

panel(cx, 556, cw, 46)
text(cx + 14, 570, "Nombre al entregar: §YARA Rosales§!", "m")
button(cx + cw - 2 * 171 - 8, 562, "Nombre al entregar", 165)
button(cx + cw - 171 - 4, 562, "Nombre de clase", 165)

button(cx, 612, "Diseños de exportación", 196, 38, hot=True)
text(cx + 208, 624, "Diseño: §YPersonalizado§!", "m")
button(cx + cw - 2 * 186 - 6, 612, "Cronograma de entregas", 186, 38)
button(cx + cw - 186, 612, "Construir como regalo", 186, 38)

panel(cx, 660, cw, 84)
text(cx + 14, 670, "Tu costo: §Y$0,54B§!   ·   Plazo: §Y412 días§! con 19 astilleros   ·   Precio: §Y120%§! → §G$0,65B§!", "m")
text(cx + 14, 694, "Probabilidad de que acepte: §Y71%§!", "m")
bar = Image.new("RGBA", (300, 12), (60, 20, 16, 255))
bar.paste((60, 170, 70, 255), (0, 0, 213, 12))
im.alpha_composite(bar, (cx + 268, 697))
text(cx + 14, 716, "Se cobra al aceptar. El barco sale de tu astillero y llega a su puerto con el nombre elegido.", "n", GREY)

# Right column: operations in progress.
rx, rw = 1008, 256
panel(rx, 80, rw, 664)
text(rx + 14, 92, "OPERACIONES EN CURSO", "s")
rule(rx + 14, 110, rw - 28)
y = 122
text(rx + 14, y, "CONSTRUCCIÓN: §Y2 pedidos§!", "s")
y += 22
for name, pct in (("Uruguay · Destructor", 38), ("Chile · Fragata (Exp. 2)", 81)):
    text(rx + 14, y, name, "n")
    pb = Image.new("RGBA", (rw - 28, 8), (30, 40, 60, 255))
    pb.paste((70, 140, 230, 255), (0, 0, int((rw - 28) * pct / 100), 8))
    im.alpha_composite(pb, (rx + 14, y + 18))
    text(rx + 14, y + 28, f"{pct}% · entrega en {int((100 - pct) * 4.1)} días", "n", GREY)
    y += 54
y += 6
for title, lines in (("REACONDICIONAMIENTO", ["§gNingún barco en el astillero.§!"]), ("COLA DE ENVÍOS: §Y1§!", ["Paraguay · Lancha patrullera", "§gSale apenas termine su misión.§!"]),
                     ("ENTREGADOS: §G4§!", ["Uruguay · La Argentina (DDG)", "Uruguay · Espora (KKG)", "Bolivia · 2 lanchas"])):
    rule(rx + 14, y, rw - 28)
    y += 8
    text(rx + 14, y, title, "s")
    y += 22
    for l in lines:
        text(rx + 14, y, l, "n")
        y += 18
    y += 10

button(W - 16 - 140, H - 46, "Cerrar", 140, 34)
button(W - 16 - 140 - 190, H - 46, "Enviar oferta", 180, 34, hot=True)
im.convert("RGB").save(OUT)
print(OUT)
