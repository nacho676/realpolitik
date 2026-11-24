# Draws the decoration of the nuclear panel (gfx/interface/mdr/nuclear/) with the look of Cold War Iron Curtain's console:
# near-black metal, green-tinted recessed panels in thick grey bevels, big DEFCON tiles, a red seven-segment clock, key
# switches, two-line launch indicators and the round launch button on a hazard plate. Our own drawings. Also the toolbar
# button and the longer top bar strip. BOX holds the layout shared with make_nuclear.py. Run from the mod folder:
#     python herramientas/make_nuclear_art.py
import math
import os
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = "gfx/interface/mdr/nuclear/"
S = 3  # supersampling
W, H = 560, 1000  # same size as Cold War Iron Curtain's WMD_tab

# Layout of the window (x0, y0, x1, y1), measured on Cold War Iron Curtain's window. make_nuclear.py places the widgets
# on these boxes.
BOX = {
    "title": (8, 4, 551, 42),
    "defcon": (150, 45, 409, 101),
    "pan_l": (8, 103, 276, 370), "pan_r": (282, 103, 552, 370),
    "groove1": (8, 375, 552, 385),
    "band": (8, 400, 552, 466),
    "clock": (175, 406, 380, 462),
    "pan_e": (8, 475, 274, 738), "pan_t": (282, 475, 552, 738),
    "groove2": (8, 745, 552, 755),
    "status": (13, 853, 552, 905),
    "console": (4, 910, 555, 995),
}
CLOCK_GROUPS = [189, 253, 317]  # left edge of each two-digit box, 52 px wide
DIGIT_Y = 418
DIGITS = [(x + dx, DIGIT_Y) for x in CLOCK_GROUPS for dx in (3, 27)]  # 22 x 34 each
DEFCON_X = [156, 207, 258, 309, 360]  # 44 x 46 tiles, DEFCON 5 to 1
DEFCON_Y = 51

AMBER, RED, GREEN = (255, 176, 46), (226, 40, 32), (80, 230, 110)
TINT_TOP, TINT_BOT = (42, 48, 42), (24, 28, 24)


def save_dds(img, path):
    a = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w = a.shape[:2]
    head = struct.pack("<4s7I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1) + b"\0" * 44
    head += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000) + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(head + a[:, :, [2, 1, 0, 3]].tobytes())


def font(size, bold=True):
    # Bahnschrift (Windows) has the squared console digits of the original; Arial as fallback.
    try:
        f = ImageFont.truetype("bahnschrift.ttf", size)
        f.set_variation_by_name("Bold" if bold else "SemiBold")
        return f
    except (OSError, ValueError):
        pass
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def gradient(w, h, top, bot):
    t = np.linspace(0, 1, h)[:, None, None]
    rgb = np.array(top, float) + (np.array(bot, float) - np.array(top, float)) * t
    a = np.broadcast_to(rgb, (h, w, 3))
    return Image.fromarray(np.dstack([a, np.full((h, w), 255.0)]).astype(np.uint8), "RGBA")


def brushed(img, seed, strength=3.5):
    # Fine horizontal grain, like brushed steel.
    rng = np.random.default_rng(seed)
    a = np.array(img, float)
    h, w = a.shape[:2]
    rows = rng.normal(0, strength, (h, 1))
    grain = rows + rng.normal(0, strength * 0.35, (h, w))
    a[:, :, :3] = np.clip(a[:, :, :3] + grain[:, :, None], 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def bevel(img, width=3, light=70, dark=70):
    d = ImageDraw.Draw(img)
    w, h = img.size
    for i in range(width):
        k = 1 - i / width
        d.line([(i, i), (w - 1 - i, i)], fill=(255, 255, 255, int(light * k)))
        d.line([(i, i), (i, h - 1 - i)], fill=(255, 255, 255, int(light * k * 0.7)))
        d.line([(i, h - 1 - i), (w - 1 - i, h - 1 - i)], fill=(0, 0, 0, int(dark * k + 60)))
        d.line([(w - 1 - i, i), (w - 1 - i, h - 1 - i)], fill=(0, 0, 0, int(dark * k + 40)))
    return img


def over(base, layer):
    return Image.alpha_composite(base, layer)


def inner_fill(w, h, top, bot, glow=0.0):
    # Recessed panel face: vertical gradient, darker edges, and optionally the soft light patch at the top of the lists.
    img = np.array(gradient(w, h, top, bot), float)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy))
    img[:, :, :3] *= (0.78 + 0.22 * np.clip(edge / 9.0, 0, 1))[:, :, None]
    if glow:
        r = np.sqrt(((xx - w / 2) / (w * 0.62)) ** 2 + ((yy + h * 0.08) / (h * 0.62)) ** 2)
        img[:, :, :3] += (glow * np.clip(1 - r, 0, 1) ** 1.6)[:, :, None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")


def frame_box(img, box, top=TINT_TOP, bot=TINT_BOT, glow=0.0, frame=3):
    # Thick bevelled grey frame around a dark green-grey face, like the original's terminals.
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rectangle([x0, y0, x1, y1], fill=(12, 13, 12, 255))
    for i in range(frame):
        k = i / max(1, frame - 1)
        lt = tuple(int(78 - 18 * k) for _ in range(3))
        dk = tuple(int(44 - 10 * k) for _ in range(3))
        d.line([(x0 + 1 + i, y0 + 1 + i), (x1 - 1 - i, y0 + 1 + i)], fill=lt + (255,))
        d.line([(x0 + 1 + i, y0 + 1 + i), (x0 + 1 + i, y1 - 1 - i)], fill=lt + (255,))
        d.line([(x0 + 1 + i, y1 - 1 - i), (x1 - 1 - i, y1 - 1 - i)], fill=dk + (255,))
        d.line([(x1 - 1 - i, y0 + 1 + i), (x1 - 1 - i, y1 - 1 - i)], fill=dk + (255,))
    ix0, iy0, ix1, iy1 = x0 + frame + 2, y0 + frame + 2, x1 - frame - 2, y1 - frame - 2
    d.rectangle([ix0 - 1, iy0 - 1, ix1 + 1, iy1 + 1], outline=(8, 8, 8, 255))
    img.paste(inner_fill(ix1 - ix0 + 1, iy1 - iy0 + 1, top, bot, glow), (ix0, iy0))


def groove(img, box):
    x0, y0, x1, y1 = box
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x0, y0, x1, y1], radius=3, fill=(30, 31, 31, 255), outline=(12, 13, 12, 255))
    d.line([(x0 + 3, y0 + 1), (x1 - 3, y0 + 1)], fill=(14, 15, 14, 255))
    d.line([(x0 + 3, y1 - 1), (x1 - 3, y1 - 1)], fill=(58, 58, 60, 255))


SEGS = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6}
DIGIT_SEGS = ["abcdef", "bc", "abged", "abgcd", "fgbc", "afgcd", "afgedc", "abc", "abcdefg", "abcdfg", "g"]


def seven_seg(d, x, y, w, h, segs, color, t):
    # Hexagonal segments of a seven-segment digit in a w x h box (supersampled coordinates).
    m = t * 0.5
    xl, xr, yt, ym, yb = x + m, x + w - m, y + m, y + h / 2, y + h - m

    def hseg(xa, xb, yc):
        return [(xa + m, yc), (xa + t, yc - m), (xb - t, yc - m), (xb - m, yc), (xb - t, yc + m), (xa + t, yc + m)]

    def vseg(xc, ya, yb_):
        return [(xc, ya + m), (xc + m, ya + t), (xc + m, yb_ - t), (xc, yb_ - m), (xc - m, yb_ - t), (xc - m, ya + t)]

    shapes = {"a": hseg(xl, xr, yt), "g": hseg(xl, xr, ym), "d": hseg(xl, xr, yb), "f": vseg(xl, yt, ym), "b": vseg(xr, yt, ym),
              "e": vseg(xl, ym, yb), "c": vseg(xr, ym, yb)}
    for s in segs:
        d.polygon(shapes[s], fill=color)


def window_bg():
    img = brushed(gradient(W, H, (34, 34, 35), (27, 27, 28)), 1, 1.6)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = BOX["title"]
    d.rectangle([x0, y0, x1, y1], fill=(18, 18, 19, 255))
    d.line([(x0, y1 + 1), (x1, y1 + 1)], fill=(58, 58, 60, 255))
    # DEFCON tile tray.
    x0, y0, x1, y1 = BOX["defcon"]
    d.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=(20, 22, 21, 255), outline=(10, 10, 10, 255), width=1)
    d.rounded_rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], radius=4, outline=(52, 56, 54, 255), width=1)
    for k in ("pan_l", "pan_r", "pan_e", "pan_t"):
        frame_box(img, BOX[k], (34, 39, 34), (18, 21, 18), glow=34, frame=5)
    groove(img, BOX["groove1"])
    groove(img, BOX["groove2"])
    frame_box(img, BOX["band"], (28, 31, 28), (22, 25, 22), frame=3)
    # Clock: black display, a dark red box per digit pair with unlit segments, lit colons between the pairs.
    x0, y0, x1, y1 = BOX["clock"]
    d.rectangle([x0, y0, x1, y1], fill=(5, 3, 4, 255), outline=(60, 58, 60, 255), width=2)
    d.line([(x0 + 2, y0 + 2), (x1 - 2, y0 + 2)], fill=(0, 0, 0, 255))
    big = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(big)
    for gx in CLOCK_GROUPS:
        bd.rectangle([gx * S, (DIGIT_Y - 4) * S, (gx + 52) * S - 1, (DIGIT_Y + 38) * S - 1], fill=(30, 10, 8, 255), outline=(54, 18, 14, 255), width=S)
    for x, y in DIGITS:
        seven_seg(bd, (x + 1) * S, (y + 1) * S, 20 * S, 32 * S, "abcdefg", (50, 17, 15, 255), 4 * S)
    for g in range(2):
        cx = (CLOCK_GROUPS[g] + 58) * S
        for cy in (DIGIT_Y + 11, DIGIT_Y + 23):
            bd.ellipse([cx - 2.5 * S, cy * S - 2.5 * S, cx + 2.5 * S, cy * S + 2.5 * S], fill=(170, 36, 28, 255))
    img = over(img, big.resize((W, H), Image.LANCZOS))
    d = ImageDraw.Draw(img)
    # Status display and console tray.
    x0, y0, x1, y1 = BOX["status"]
    d.rectangle([x0, y0, x1, y1], fill=(10, 10, 10, 255))
    d.rectangle([x0 + 1, y0 + 1, x1 - 1, y1 - 1], outline=(58, 57, 58, 255), width=2)
    img.paste(gradient(x1 - x0 - 7, y1 - y0 - 7, (14, 13, 14), (26, 25, 26)), (x0 + 4, y0 + 4))
    x0, y0, x1, y1 = BOX["console"]
    d.rectangle([x0, y0, x1, y1], fill=(22, 22, 23, 255))
    d.line([(x0, y0), (x1, y0)], fill=(10, 10, 10, 255))
    d.line([(x0, y0 + 1), (x1, y0 + 1)], fill=(56, 56, 58, 255))
    return bevel(img, 4, 50, 80)


def plate(w, h, fill_top, fill_bot, edge=(10, 10, 10), light=(70, 70, 72), radius=3):
    # Rounded console key at S scale: black outline, a light rim at the top-left and a gradient face.
    big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    d.rounded_rectangle([0, 0, w * S - 1, h * S - 1], radius=radius * S, fill=edge + (255,))
    d.rounded_rectangle([S, S, w * S - 1 - S, h * S - 1 - S], radius=radius * S, fill=light + (255,))
    face = gradient(w * S - 4 * S, h * S - 4 * S, fill_top, fill_bot)
    mask = Image.new("L", face.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, face.width - 1, face.height - 1], radius=max(1, radius - 1) * S, fill=255)
    big.paste(face, (2 * S, 2 * S), mask)
    return big


def sheet(frames):
    w, h = frames[0].size
    out = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        out.paste(f, (i * w, 0))
    return out


def defcon_tile(n):
    # 44 x 46. Off: dark tile with a grey embossed digit. Current: the level's colour rim, dark tinted face, white digit.
    colors = {5: (96, 176, 128), 4: (96, 176, 128), 3: (226, 190, 70), 2: (232, 110, 50), 1: (232, 52, 40)}
    w, h = 44, 46
    frames = []
    for lit in (False, True):
        c = colors[n]
        if lit:
            big = plate(w, h, tuple(int(v * 0.3) for v in c), tuple(int(v * 0.2) for v in c), (8, 8, 8), c, 4)
        else:
            big = plate(w, h, (40, 38, 42), (30, 29, 32), (8, 8, 8), (52, 50, 54), 4)
        d = ImageDraw.Draw(big)
        f = font(40 * S)
        txt = str(n)
        bb = d.textbbox((0, 0), txt, font=f)
        tx, ty = (w * S - (bb[2] - bb[0])) / 2 - bb[0], (h * S - (bb[3] - bb[1])) / 2 - bb[1]
        if lit:
            d.text((tx, ty), txt, font=f, fill=(250, 250, 250, 255), stroke_width=S, stroke_fill=(10, 14, 12, 255))
        else:
            d.text((tx + S, ty + S), txt, font=f, fill=(18, 18, 20, 255))
            d.text((tx, ty), txt, font=f, fill=(62, 59, 64, 255))
        small = big.resize((w, h), Image.LANCZOS)
        if lit:
            glow = Image.new("RGBA", (w, h), c + (0,))
            glow.putalpha(small.split()[3].filter(ImageFilter.GaussianBlur(2)).point(lambda v: v // 4))
            small = Image.alpha_composite(glow, small)
        frames.append(small)
    return sheet(frames)


def arrow_button(w, h, side):
    # "< RAISE" / "LOWER >" keys: black key with a grey rim and a light triangle; the label is game text.
    frames = []
    for hover in (False, True):
        top, bot = ((34, 34, 36), (24, 24, 25)) if hover else ((26, 26, 27), (18, 18, 19))
        big = plate(w, h, top, bot, (6, 6, 6), (58, 58, 60), 3)
        d = ImageDraw.Draw(big)
        cy, s = h * S / 2, 6 * S
        cx = 17 * S if side == "l" else (w - 17) * S
        pts = [(cx - s, cy), (cx + s * 0.8, cy - s), (cx + s * 0.8, cy + s)] if side == "l" else [(cx + s, cy), (cx - s * 0.8, cy - s), (cx - s * 0.8, cy + s)]
        d.polygon(pts, fill=(196, 196, 196, 255))
        frames.append(big.resize((w, h), Image.LANCZOS))
    return sheet(frames)


def key_button(w, h, top, bot, rim, top2, bot2, rim2):
    return sheet([plate(w, h, top, bot, (6, 6, 6), rim, 3).resize((w, h), Image.LANCZOS),
                  plate(w, h, top2, bot2, (6, 6, 6), rim2, 3).resize((w, h), Image.LANCZOS)])


def strike_button(n):
    # 30 x 30 strike level key with its digit; frame 2 is the selected level.
    w = h = 30
    frames = []
    for lit in (False, True):
        big = plate(w, h, (48, 49, 51) if lit else (26, 26, 27), (36, 37, 39) if lit else (18, 18, 19), (6, 6, 6),
                    (150, 150, 152) if lit else (50, 50, 52), 4)
        d = ImageDraw.Draw(big)
        f = font(21 * S)
        bb = d.textbbox((0, 0), str(n), font=f)
        d.text(((w * S - (bb[2] - bb[0])) / 2 - bb[0], (h * S - (bb[3] - bb[1])) / 2 - bb[1]), str(n), font=f,
               fill=(236, 236, 236, 255) if lit else (92, 92, 94, 255))
        frames.append(big.resize((w, h), Image.LANCZOS))
    return sheet(frames)


def clock_digit():
    # 11 frames of 22 x 34: digits 0-9 and a dash. Lit red segments on transparent, over the unlit ones of the background.
    w, h = 22, 34
    frames = []
    for segs in DIGIT_SEGS:
        big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        seven_seg(ImageDraw.Draw(big), S, S, 20 * S, 32 * S, segs, (236, 52, 38, 255), 4 * S)
        small = big.resize((w, h), Image.LANCZOS)
        glow = Image.new("RGBA", (w, h), (255, 40, 30, 0))
        glow.putalpha(small.split()[3].filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: v // 3))
        frames.append(Image.alpha_composite(glow, small))
    return sheet(frames)


def lamp(color, w, h):
    # Indicator key: dark grey; lit, its face glows in its colour. The label is game text drawn on top.
    frames = []
    for lit in (False, True):
        if lit:
            big = plate(w, h, tuple(int(v * 0.62) for v in color), tuple(int(v * 0.4) for v in color), (6, 6, 6), color, 3)
        else:
            big = plate(w, h, (38, 38, 39), (30, 30, 31), (8, 8, 8), (54, 54, 56), 3)
        small = big.resize((w, h), Image.LANCZOS)
        if lit:
            glow = Image.new("RGBA", (w, h), color + (0,))
            glow.putalpha(small.split()[3].filter(ImageFilter.GaussianBlur(2)).point(lambda v: v // 5))
            small = Image.alpha_composite(glow, small)
        frames.append(small)
    return sheet(frames)


def key_switch():
    # 70 x 76 key plate: barrel at the lower left with the key slot upright (frame 1, OFF) or turned (frame 2, ARM),
    # a tick under OFF and a bracket by ARM. The OFF / ARM words are game text.
    w, h = 70, 76
    frames = []
    for armed in (False, True):
        big = plate(w, h, (46, 46, 47), (34, 34, 35), (8, 8, 8), (70, 70, 72), 4)
        d = ImageDraw.Draw(big)
        cx, cy, r = 25 * S, 40 * S, 13 * S
        d.line([(cx, 18 * S), (cx, 25 * S)], fill=(206, 84, 70, 255), width=int(1.5 * S))
        d.line([(47 * S, 28 * S), (56 * S, 28 * S), (56 * S, 34 * S)], fill=(206, 84, 70, 255), width=int(1.5 * S))
        d.ellipse([cx - r - 2 * S, cy - r - 2 * S, cx + r + 2 * S, cy + r + 2 * S], fill=(16, 16, 16, 255))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(112, 112, 114, 255))
        d.ellipse([cx - r + 2 * S, cy - r + 2 * S, cx + r - 2 * S, cy + r - 2 * S], fill=(150, 150, 152, 255))
        d.ellipse([cx - r + 4 * S, cy - r + 3 * S, cx + 2 * S, cy - 2 * S], fill=(196, 196, 198, 255))
        ang = math.radians(60 if armed else 0)
        dx, dy = math.sin(ang), -math.cos(ang)
        L, Wd = 9 * S, 1.8 * S
        px, py = -dy, dx
        d.polygon([(cx + dx * L + px * Wd, cy + dy * L + py * Wd), (cx + dx * L - px * Wd, cy + dy * L - py * Wd),
                   (cx - dx * L - px * Wd, cy - dy * L - py * Wd), (cx - dx * L + px * Wd, cy - dy * L + py * Wd)], fill=(24, 24, 26, 255))
        if armed:
            d.ellipse([cx + dx * 11 * S - 2 * S, cy + dy * 11 * S - 2 * S, cx + dx * 11 * S + 2 * S, cy + dy * 11 * S + 2 * S], fill=(236, 56, 40, 255))
        frames.append(big.resize((w, h), Image.LANCZOS))
    return sheet(frames)


def launch_button():
    # 66 x 84 hazard plate with a tab on top and the round button: frame 1 locked (grey), frame 2 armed (red, glowing).
    w, h = 66, 84
    frames = []
    for armed in (False, True):
        big = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(big)
        d.rectangle([22 * S, 0, 44 * S, 7 * S], fill=(96, 96, 98, 255), outline=(10, 10, 10, 255), width=S)
        y0 = 6 * S
        d.rectangle([0, y0, w * S - 1, h * S - 1], fill=(14, 14, 14, 255))
        stripe = 5 * S
        for x in range(-h * S, w * S + h * S, stripe * 2):
            d.polygon([(x, h * S), (x + stripe, h * S), (x + stripe + h * S, y0), (x + h * S, y0)], fill=(118, 118, 120, 255))
        d.rectangle([4 * S, y0 + 4 * S, (w - 4) * S - 1, h * S - 4 * S - 1], fill=(14, 14, 14, 255))
        big.paste(gradient((w - 10) * S, (h - 14) * S, (112, 112, 114), (82, 82, 84)), (5 * S, y0 + 5 * S))
        cx, cy, r = w * S / 2, (y0 + h * S) / 2, 22 * S
        d.ellipse([cx - r - 2 * S, cy - r - 2 * S, cx + r + 2 * S, cy + r + 2 * S], fill=(58, 58, 60, 255))
        face = (214, 40, 30) if armed else (164, 164, 166)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face + (255,))
        d.ellipse([cx - r * 0.65, cy - r * 0.75, cx + r * 0.2, cy - r * 0.1], fill=(255, 255, 255, 70 if armed else 50))
        small = big.resize((w, h), Image.LANCZOS)
        if armed:
            glow = Image.new("RGBA", (w, h), (255, 50, 30, 0))
            ring = Image.new("L", (w, h), 0)
            ImageDraw.Draw(ring).ellipse([w / 2 - 26, (y0 / S + h) / 2 - 26, w / 2 + 26, (y0 / S + h) / 2 + 26], fill=150)
            glow.putalpha(ring.filter(ImageFilter.GaussianBlur(3)))
            small = Image.alpha_composite(small, glow)
            small.alpha_composite(big.resize((w, h), Image.LANCZOS).crop((9, 21, 57, 69)), (9, 21))
        frames.append(small)
    return sheet(frames)


def checkbox():
    w = h = 18
    frames = []
    for on in (False, True):
        big = plate(w, h, (20, 20, 21), (14, 14, 15), (6, 6, 6), (110, 110, 112), 2)
        d = ImageDraw.Draw(big)
        if on:
            d.line([(4 * S, 4 * S), ((w - 5) * S, (h - 5) * S)], fill=(240, 60, 45, 255), width=2 * S)
            d.line([((w - 5) * S, 4 * S), (4 * S, (h - 5) * S)], fill=(240, 60, 45, 255), width=2 * S)
        frames.append(big.resize((w, h), Image.LANCZOS))
    return sheet(frames)


def round_flag():
    # Masked flag sprite: a 40 x 26 quad (the flag keeps its shape), shown through a 25 px circle, with a dark glossy rim.
    w, h, r = 40, 26, 12.5
    mask = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(mask).ellipse([(w / 2 - r) * S, (h / 2 - r) * S, (w / 2 + r) * S, (h / 2 + r) * S], fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    m = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m.putalpha(mask)
    ov = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = (w / 2 * S, h / 2 * S)
    d.ellipse([c[0] - r * S, c[1] - r * S, c[0] + r * S, c[1] + r * S], outline=(10, 10, 10, 230), width=int(1.4 * S))
    d.ellipse([c[0] - r * 0.7 * S, c[1] - r * 0.85 * S, c[0] + r * 0.5 * S, c[1] - r * 0.2 * S], fill=(255, 255, 255, 46))
    return m, ov.resize((w, h), Image.LANCZOS)


def trefoil(size, fg, bg):
    big = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    c = size * S / 2
    d.ellipse([0, 0, size * S - 1, size * S - 1], fill=bg)
    R, r0 = size * S * 0.44, size * S * 0.1
    for k in range(3):
        a0 = math.radians(-90 + 120 * k - 30)
        a1 = math.radians(-90 + 120 * k + 30)
        pts = [(c + r0 * 1.6 * math.cos(a0), c + r0 * 1.6 * math.sin(a0))]
        pts += [(c + R * math.cos(a0 + (a1 - a0) * t / 12), c + R * math.sin(a0 + (a1 - a0) * t / 12)) for t in range(13)]
        pts += [(c + r0 * 1.6 * math.cos(a1), c + r0 * 1.6 * math.sin(a1))]
        d.polygon(pts, fill=fg)
    d.ellipse([c - r0, c - r0, c + r0, c + r0], fill=fg)
    return big.resize((size, size), Image.LANCZOS)


def topbar_button():
    # A copy of Millennium Dawn's International Systems toolbar button (our colored copy): same box, frame and hover
    # frame. The globe is wiped row by row with the box's own color at that row (taken just inside the left edge),
    # then the yellow radiation trefoil goes in its place.
    src = np.array(Image.open("gfx/interface/topbar/toolbar/missile_button.dds").convert("RGBA"), dtype=float)
    h, w = src.shape[:2]
    fw = w // 2
    out = src.copy()
    for f in range(2):
        x0 = f * fw
        for y in range(2, h - 2):
            out[y, x0 + 7:x0 + fw - 7] = src[y, x0 + 6]
    img = Image.fromarray(out.astype(np.uint8), "RGBA")
    size = 29
    for f, color in enumerate(((238, 196, 40, 255), (255, 222, 80, 255))):
        t = trefoil(size, color, (0, 0, 0, 0))
        img.alpha_composite(t, (f * fw + (fw - size) // 2, (h - size) // 2))
    return img


def topbar_background():
    # Millennium Dawn's top bar with its button strip one button (55 px) longer, so the nuclear button sits inside it,
    # after International Systems. Only the strip rows (36 and below) move; the bar above stays as it is.
    src = np.array(Image.open("../Millennium-Dawn-2.0.3/gfx/interface/topbar/background_extended_missiles_officer_coprs.dds").convert("RGBA"))
    out = src.copy()
    x0, x1, grow, y0 = 700, 900, 55, 36
    out[y0:, x0 + grow:x1 + grow] = src[y0:, x0:x1]
    out[y0:, x0:x0 + grow] = src[y0:, x0 - grow:x0]
    return Image.fromarray(out, "RGBA")


def main():
    os.makedirs(OUT, exist_ok=True)
    art = {
        "window": window_bg(),
        "btn_calm": arrow_button(104, 34, "l"),
        "btn_alert": arrow_button(104, 34, "r"),
        "btn_wide": key_button(111, 34, (34, 34, 35), (24, 24, 25), (60, 60, 62), (44, 44, 46), (32, 32, 34), (96, 96, 98)),
        "btn_mark": key_button(144, 32, (78, 70, 82), (60, 53, 63), (96, 88, 100), (92, 84, 96), (72, 64, 76), (130, 120, 134)),
        "strike_1": strike_button(1),
        "strike_2": strike_button(2),
        "strike_3": strike_button(3),
        "digit": clock_digit(),
        "lamp_target": lamp(GREEN, 48, 34),
        "lamp_missile": lamp(AMBER, 48, 34),
        "lamp_confirm": lamp(RED, 48, 34),
        "con_go": lamp(GREEN, 74, 30),
        "con_on": lamp(AMBER, 74, 30),
        "con_nogo": lamp(RED, 74, 30),
        "key": key_switch(),
        "launch": launch_button(),
        "topbar": topbar_button(),
        "check": checkbox(),
    }
    for n in range(1, 6):
        art[f"defcon_{n}"] = defcon_tile(n)
    mask, ring = round_flag()
    art["flag_ring"] = ring
    for name, img in art.items():
        save_dds(img, f"{OUT}{name}.dds")
    mask.save(f"{OUT}flag_mask.tga")
    # Drawings of the previous layout that are no longer used.
    for old in ("terminal", "terminal_low", "strip", "status", "clock", "btn_raise", "btn_lower", "btn_auth", "panel_go",
                "panel_nogo", "key_l", "key_r"):
        if os.path.exists(f"{OUT}{old}.dds"):
            os.remove(f"{OUT}{old}.dds")
    save_dds(topbar_background(), "gfx/interface/topbar/mdr_topbar_background.dds")
    print(f"{len(art) + 1} images in {OUT}")


if __name__ == "__main__":
    main()
