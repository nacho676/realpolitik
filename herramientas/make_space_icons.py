# Generates the icons of the space programme menu and interface/mdr_space_icons.gfx.
# Same rules as Millennium Dawn's ledger icons: 28 x 27, flat fill, light gold at the top to brown at the bottom, no outline,
# details as gaps in the shape. The launch base's frame in the building strips is drawn here too.
# Run from the mod folder: python herramientas/make_space_icons.py
import math, struct
import sys
import numpy as np
sys.path.insert(0, 'herramientas')
import space_program
import space_theme as theme
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, S = 28, 27, 16
OUT = "gfx/interface/mdr/space/icons/"
# Icons: ice white at the top to sky blue at the bottom (space_theme.py).
TOP, BOTTOM = np.array([236, 246, 255.0]), np.array([104, 186, 236.0])


def canvas():
    m = Image.new("L", (W * S, H * S), 0)
    return m, ImageDraw.Draw(m)


def pts(p):
    return [(x * S, y * S) for x, y in p]


def poly(d, p, fill=255):
    d.polygon(pts(p), fill=fill)


def disc(d, x, y, r, fill=255):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=fill)


def ring(d, x, y, r, width, fill=255):
    d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], outline=fill, width=round(width * S))


def bar(d, x0, y0, x1, y1, width, fill=255):
    d.line(pts([(x0, y0), (x1, y1)]), fill=fill, width=round(width * S))
    disc(d, x0, y0, width / 2, fill)
    disc(d, x1, y1, width / 2, fill)


def rotated(p, cx, cy, angle):
    a = math.radians(angle)
    return [(cx + (x - cx) * math.cos(a) - (y - cy) * math.sin(a), cy + (x - cx) * math.sin(a) + (y - cy) * math.cos(a)) for x, y in p]


def ellipse_points(cx, cy, rx, ry, angle, start=0, end=360):
    p = [(cx + rx * math.cos(math.radians(t)), cy + ry * math.sin(math.radians(t))) for t in range(start, end + 1, 3)]
    return rotated(p, cx, cy, angle)


def rocket_shape(cx, cy, h, w):
    # Upright, nose at the top: body and two fins.
    top, base = cy - h / 2, cy + h / 2
    body = [(cx, top), (cx + w * 0.3, top + h * 0.14), (cx + w * 0.5, top + h * 0.36), (cx + w * 0.5, base - h * 0.18), (cx + w * 0.3, base - h * 0.08), (cx - w * 0.3, base - h * 0.08), (cx - w * 0.5, base - h * 0.18), (cx - w * 0.5, top + h * 0.36), (cx - w * 0.3, top + h * 0.14)]
    left = [(cx - w * 0.5, base - h * 0.36), (cx - w * 1.08, base), (cx - w * 0.5, base - h * 0.16)]
    right = [(cx + w * 0.5, base - h * 0.36), (cx + w * 1.08, base), (cx + w * 0.5, base - h * 0.16)]
    return body, left, right


def icon_programme():
    # A rocket rising out of a planet, cut out of the disc.
    m, d = canvas()
    disc(d, 14, 13.5, 13)
    for part in rocket_shape(14, 12, 19, 6.2):
        poly(d, rotated(part, 14, 13.5, 38), 0)
    trail = rotated([(12.6, 21.2), (15.4, 21.2), (14.6, 29), (13.4, 29)], 14, 13.5, 38)
    poly(d, trail, 0)
    for x, y, r in ((7.5, 8.5, 1.1), (19.5, 20.5, 1.2), (6, 15.5, 0.75)):
        disc(d, x, y, r, 0)
    window = rotated([(14, 9.5)], 14, 13.5, 38)[0]
    disc(d, window[0], window[1], 1.15)
    return m


def icon_summary():
    # Tracking dish on its mount, with its signal.
    m, d = canvas()
    bowl = ellipse_points(11, 11.5, 10, 10, 0, 45, 225)
    poly(d, bowl)
    cut = ellipse_points(14.3, 8.2, 8.9, 4.2, 45)
    poly(d, cut, 0)
    bar(d, 7.6, 15, 14.3, 8.3, 1.25)
    disc(d, 14.8, 7.8, 1.9)
    poly(d, [(8.2, 16.5), (12.2, 18.4), (15.4, 25), (3.4, 25)])
    poly(d, [(7.2, 23.2), (9.3, 20), (11.4, 23.2)], 0)
    bar(d, 1.5, 26, 17.5, 26, 1.8)
    d.arc([10 * S, 2 * S, 22 * S, 14 * S], 285, 355, fill=255, width=round(1.6 * S))
    d.arc([6.5 * S, -1.5 * S, 25.5 * S, 17.5 * S], 290, 350, fill=255, width=round(1.6 * S))
    return m


def icon_goals():
    # A flag planted on the Moon.
    m, d = canvas()
    poly(d, ellipse_points(14, 36, 21, 16, 0, 180, 360))
    for x, y, r in ((6.5, 24, 1.5), (20, 23.5, 1.9), (13.5, 25.6, 0.9)):
        disc(d, x, y, r, 0)
    bar(d, 9, 1.2, 9, 21, 1.9)
    wave = [(9.6, 1.5)]
    for t in range(0, 101, 5):
        wave.append((9.6 + t * 0.165, 2 + 1.1 * math.sin(t / 100 * math.pi * 2)))
    wave.append((26, 7.4))
    wave.append((22.8, 7.9 + 1))
    for t in range(100, -1, -5):
        wave.append((9.6 + t * 0.14, 11.4 + 1.1 * math.sin(t / 100 * math.pi * 2)))
    poly(d, wave)
    disc(d, 16.6, 6.9, 1.9, 0)
    return m


def icon_projects():
    # Drafting compass over the arc it has just drawn.
    m, d = canvas()
    disc(d, 14, 3.4, 3.4)
    disc(d, 14, 3.4, 1.15, 0)
    poly(d, [(12.2, 5.6), (15, 6.6), (9.6, 21), (6.4, 25.8), (6.8, 20.2)])
    poly(d, [(15.8, 5.6), (13, 6.6), (18.4, 21), (21.6, 25.8), (21.2, 20.2)])
    bar(d, 10.4, 13, 17.6, 13, 1.5)
    d.arc([1.2 * S, 3 * S, 26.8 * S, 28.6 * S], 40, 140, fill=255, width=round(1.8 * S))
    return m


def icon_staff():
    # Astronaut, from the chest up.
    m, d = canvas()
    disc(d, 14, 9.8, 9.8)
    d.rounded_rectangle([1.6 * S, 18.4 * S, 26.4 * S, 34 * S], radius=6.5 * S, fill=255)
    disc(d, 14, 9.8, 11, 0)
    disc(d, 14, 9.8, 9.8)
    d.rounded_rectangle([6.2 * S, 5.2 * S, 21.8 * S, 14.6 * S], radius=4.3 * S, fill=0)
    poly(d, [(9, 7.2), (12.4, 7.2), (9.2, 12.4), (8, 11)])
    d.rounded_rectangle([9.2 * S, 22.2 * S, 18.8 * S, 26 * S], radius=0.9 * S, fill=0)
    d.rectangle([10.9 * S, 23.3 * S, 12.5 * S, 24.9 * S], fill=255)
    d.rectangle([15.5 * S, 23.3 * S, 17.1 * S, 24.9 * S], fill=255)
    return m


def icon_finance():
    # Coin with its rim and the dollar cut out.
    m, d = canvas()
    disc(d, 14, 13.5, 13.2)
    ring(d, 14, 13.5, 11.2, 0.95, 0)
    font = ImageFont.truetype("arialbd.ttf", 19 * S)
    box = d.textbbox((0, 0), "$", font=font)
    d.text((14 * S - (box[0] + box[2]) / 2, 13.5 * S - (box[1] + box[3]) / 2), "$", font=font, fill=0)
    return m


def icon_solar():
    # Ringed planet with two stars.
    m, d = canvas()
    disc(d, 14, 13.5, 8.2)
    band = ellipse_points(14, 13.5, 13.4, 4.7, -22, 0, 180)
    inner = ellipse_points(14, 13.5, 10.6, 2.9, -22, 0, 180)
    poly(d, band + inner[::-1], 0)
    outer = ellipse_points(14, 13.5, 12.9, 4.3, -22, 0, 360)
    hole = ellipse_points(14, 13.5, 11.1, 3.2, -22, 0, 360)
    ringmask = Image.new("L", m.size, 0)
    r = ImageDraw.Draw(ringmask)
    poly(r, outer)
    poly(r, hole, 0)
    # The back of the ring passes behind the planet.
    r.ellipse([(14 - 8.8) * S, (13.5 - 8.8) * S, (14 + 8.8) * S, (13.5 + 8.8) * S], fill=0)
    front = Image.new("L", m.size, 0)
    f = ImageDraw.Draw(front)
    poly(f, ellipse_points(14, 13.5, 12.9, 4.3, -22, 0, 180) + ellipse_points(14, 13.5, 11.1, 3.2, -22, 0, 180)[::-1])
    m.paste(255, mask=ringmask)
    m.paste(255, mask=front)
    for x, y, r_ in ((4.5, 4.2, 1.3), (24, 23, 1.05)):
        poly(d, [(x, y - r_ * 2), (x + r_ * 0.45, y - r_ * 0.45), (x + r_ * 2, y), (x + r_ * 0.45, y + r_ * 0.45), (x, y + r_ * 2), (x - r_ * 0.45, y + r_ * 0.45), (x - r_ * 2, y), (x - r_ * 0.45, y - r_ * 0.45)])
    return m


def icon_decisions():
    # The nib of a pen, ready to sign.
    m, d = canvas()
    d.rounded_rectangle([9 * S, 0.4 * S, 19 * S, 5.4 * S], radius=1 * S, fill=255)
    poly(d, [(8.2, 7), (19.8, 7), (23.8, 14.6), (14, 26.8), (4.2, 14.6)])
    d.line(pts([(14, 26.8), (14, 15)]), fill=0, width=round(1.15 * S))
    disc(d, 14, 13.2, 2.5, 0)
    poly(d, [(7.6, 12.4), (9.3, 9.2), (10.2, 9.2), (9.2, 13.8)], 0)
    poly(d, [(20.4, 12.4), (18.7, 9.2), (17.8, 9.2), (18.8, 13.8)], 0)
    return m


def icon_colonies():
    # Geodesic dome on the surface, with a mast.
    m, d = canvas()
    poly(d, ellipse_points(14, 21.4, 12.6, 15, 0, 180, 360))
    for a in (((4.4, 21.4), (9, 11.8)), ((9, 11.8), (14, 21.4)), ((14, 21.4), (19, 11.8)), ((19, 11.8), (23.6, 21.4)), ((5.2, 13), (22.8, 13)), ((9, 11.8), (14, 6.2)), ((19, 11.8), (14, 6.2))):
        d.line(pts(a), fill=0, width=round(0.95 * S))
    poly(d, [(11.8, 21.4), (11.8, 17.6), (16.2, 17.6), (16.2, 21.4)], 0)
    bar(d, 14, 6.4, 14, 1.6, 1.15)
    disc(d, 14, 1.7, 1.4)
    bar(d, 0.8, 24.6, 27.2, 24.6, 2.6)
    return m


def icon_atom():
    # Atom: three orbits around the nucleus.
    m, d = canvas()
    for angle in (0, 60, 120):
        outer = ellipse_points(14, 13.5, 13, 5, angle)
        inner = ellipse_points(14, 13.5, 11.4, 3.6, angle)
        ring_mask = Image.new("L", m.size, 0)
        r = ImageDraw.Draw(ring_mask)
        poly(r, outer)
        poly(r, inner, 0)
        m.paste(255, mask=ring_mask)
    disc(d, 14, 13.5, 2.6)
    return m


def icon_flask():
    # Laboratory flask.
    m, d = canvas()
    d.rounded_rectangle([9.6 * S, 0.8 * S, 18.4 * S, 3.4 * S], radius=0.9 * S, fill=255)
    poly(d, [(11.2, 3.4), (16.8, 3.4), (16.8, 10.4), (25.2, 24), (24.4, 26.4), (3.6, 26.4), (2.8, 24), (11.2, 10.4)])
    poly(d, [(12.8, 4.8), (15.2, 4.8), (15.2, 10.8), (19.4, 17.4), (8.6, 17.4), (12.8, 10.8)], 0)
    disc(d, 10, 21.6, 1.4, 0)
    disc(d, 16.6, 22.6, 1.1, 0)
    return m


def icon_spaceport():
    # Rocket beside its service tower, on the pad.
    m, d = canvas()
    for part in rocket_shape(17.5, 12.2, 22, 5.2):
        poly(d, part)
    d.rectangle([4 * S, 3 * S, 6.2 * S, 24 * S], fill=255)
    d.rectangle([8.6 * S, 3 * S, 10 * S, 24 * S], fill=255)
    for y in (3, 7, 11, 15, 19):
        d.rectangle([4 * S, y * S, 10 * S, (y + 1.2) * S], fill=255)
    d.rectangle([10 * S, 9 * S, 14.8 * S, 10.2 * S], fill=255)
    d.rectangle([10 * S, 15 * S, 14.8 * S, 16.2 * S], fill=255)
    bar(d, 2, 25.2, 26, 25.2, 2.4)
    return m


ICONS = {
    "programme": icon_programme,
    "summary": icon_summary,
    "goals": icon_goals,
    "projects": icon_projects,
    "staff": icon_staff,
    "finance": icon_finance,
    "solar": icon_solar,
    "decisions": icon_decisions,
    "colonies": icon_colonies,
    "atom": icon_atom,
    "flask": icon_flask,
}


def finish(mask):
    small = Image.new("L", (W, H), 0)
    small.paste(mask.resize((24, 23), Image.LANCZOS), (2, 2))
    t = np.clip((np.arange(H) - 2) / 22, 0, 1)[:, None, None]
    rgb = np.broadcast_to(TOP + (BOTTOM - TOP) * t, (H, W, 3))
    return Image.fromarray(np.dstack([rgb, np.array(small, dtype=float)]).astype(np.uint8))


def save_dds(img, path):
    a = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w = a.shape[:2]
    head = struct.pack("<4s7I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1) + b"\0" * 44
    head += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000) + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(head + a[:, :, [2, 1, 0, 3]].tobytes())








def earth_art():
    src = Image.open("../Millennium-Dawn-2.0.0/gfx/interface/techtree/network_centric_techtree_bg.dds").convert("RGBA")
    a = np.array(src, dtype=float)
    a[:, :, 3] = np.clip(a[:, :, 3] * 4.2, 0, 255)
    return Image.fromarray(a.astype(np.uint8))






def map_icon():
    # Same drawing as the air base and missile site icons: black shape, white outline and a little grey pointer below.
    S2 = 12
    m = Image.new("L", (27 * S2, 30 * S2), 0)
    d = ImageDraw.Draw(m)
    for part in rocket_shape(15.2, 11.6, 21, 5.2):
        d.polygon([(x * S2, y * S2) for x, y in part], fill=255)
    d.rectangle([5 * S2, 4 * S2, 6.6 * S2, 22 * S2], fill=255)
    d.rectangle([8.4 * S2, 4 * S2, 9.6 * S2, 22 * S2], fill=255)
    for y in (4, 8, 12, 16, 20):
        d.rectangle([5 * S2, y * S2, 9.6 * S2, (y + 1) * S2], fill=255)
    d.rectangle([9.6 * S2, 9 * S2, 13 * S2, 10 * S2], fill=255)
    outline = m.filter(ImageFilter.MaxFilter(2 * int(S2 * 0.8) + 1))
    img = Image.new("RGBA", m.size, (0, 0, 0, 0))
    img.paste((255, 255, 255, 255), mask=outline)
    img.paste((8, 8, 10, 255), mask=m)
    ImageDraw.Draw(img).polygon([(9.5 * S2, 24.4 * S2), (17.5 * S2, 24.4 * S2), (13.5 * S2, 28.6 * S2)], fill=(150, 150, 150, 255))
    return img.resize((27, 30), Image.LANCZOS)






PLANETS = {b[0]: b[3] for b in space_program.BODIES}


def noise(shape, seed, cells, octaves=5):
    # Soft random texture: several layers of random values, enlarged.
    rng = np.random.default_rng(seed)
    out = np.zeros(shape)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = cells * 2 ** o
        grid = Image.fromarray((rng.random((max(2, n), max(2, n * 2))) * 255).astype(np.uint8))
        out += np.array(grid.resize((shape[1], shape[0]), Image.BICUBIC), dtype=float) / 255 * amp
        total += amp
        amp *= 0.55
    out /= total
    return (out - out.min()) / (out.max() - out.min())


def surface(name, h, w):
    # Colour map of a body, in latitude and longitude, 0-255.
    lat = np.linspace(-1, 1, h)[:, None] * np.ones((h, w))
    n = noise((h, w), sum(map(ord, name)), 4)
    fine = noise((h, w), sum(map(ord, name)) + 9, 12, 4)
    def mix(a, b, m):
        return np.array(a, dtype=float) + (np.array(b, dtype=float) - np.array(a, dtype=float)) * m[:, :, None]
    if name == "earth":
        land = n > 0.54
        img = mix((16, 52, 112), (34, 96, 164), fine)
        ground = mix((70, 112, 58), (150, 132, 84), fine)
        img[land] = ground[land]
        ice = np.abs(lat) > 0.8 + (fine - 0.5) * 0.14
        img[ice] = (232, 238, 242)
        clouds = noise((h, w), 77, 6, 5)
        c = np.clip((clouds - 0.58) * 4.5, 0, 0.85)[:, :, None]
        return img * (1 - c) + 245 * c
    if name == "mars":
        img = mix((150, 70, 38), (214, 128, 78), n)
        img = img * (0.86 + 0.28 * fine[:, :, None])
        img[np.abs(lat) > 0.86 + (fine - 0.5) * 0.1] = (236, 226, 216)
        return img
    if name == "venus":
        sw = noise((h, w), 31, 3, 4)
        bands = (np.sin(lat * 9 + sw * 7) + 1) / 2
        return mix((186, 146, 86), (240, 218, 164), bands * 0.7 + fine * 0.3)
    if name == "jupiter":
        wob = (fine - 0.5) * 0.09
        v = lat + wob
        bands = (np.sin(v * 15) + np.sin(v * 7.3 + 1) * 0.6 + 1.6) / 3.2
        img = mix((142, 96, 66), (238, 214, 176), bands)
        spot = ((np.linspace(-1, 1, w)[None, :] - 0.15) / 0.2) ** 2 + ((lat - 0.3) / 0.1) ** 2 < 1
        img[spot] = (186, 84, 56)
        return img
    if name == "saturn":
        v = lat + (fine - 0.5) * 0.03
        return mix((176, 142, 92), (238, 220, 170), (np.sin(v * 13) + 1) / 2)
    # Moon and Mercury: grey, with craters.
    base = ((118, 116, 112), (196, 194, 188)) if name == "moon" else ((104, 92, 82), (178, 164, 148))
    img = mix(base[0], base[1], n * 0.6 + fine * 0.4)
    rng = np.random.default_rng(5 + len(name))
    yy, xx = np.mgrid[0:h, 0:w]
    for _ in range(38):
        cx, cy, r = rng.integers(0, w), rng.integers(0, h), rng.integers(3, max(5, h // 9))
        d = ((xx - cx) ** 2 + (yy - cy) ** 2) / r ** 2
        img[d < 1] *= 0.78
        img[(d >= 1) & (d < 1.35)] *= 1.1
    return img


def sphere(name, size, radius=None, atmosphere=None):
    # Globe lit from the upper left, with darker edges and a thin atmosphere if it has one.
    k = 5
    full = size * k
    r = (radius or size * 0.46) * k
    tex = surface(name, 256, 512)
    yy, xx = np.mgrid[0:full, 0:full]
    x, y = (xx - full / 2) / r, (yy - full / 2) / r
    d2 = x ** 2 + y ** 2
    inside = d2 <= 1
    z = np.sqrt(np.clip(1 - d2, 0, 1))
    lon = np.arctan2(x, z) / np.pi
    lat = np.arcsin(np.clip(y, -1, 1)) / (np.pi / 2)
    u = ((lon * 0.5 + 0.5) * 511).astype(int)
    v = ((lat * 0.5 + 0.5) * 255).astype(int)
    col = tex[v, u]
    light = np.clip(x * -0.52 + y * -0.5 + z * 0.69, 0, 1)
    shade = 0.1 + 1.02 * light ** 0.85
    rgb = np.clip(col * shade[:, :, None], 0, 255)
    a = np.zeros((full, full))
    a[inside] = 255
    out = np.dstack([rgb, a])
    if atmosphere:
        glow = np.clip(1 - (np.sqrt(d2) - 1) / 0.09, 0, 1) * (d2 > 1)
        rim = np.clip(light * 0 + (x * -0.52 + y * -0.5 + 0.6), 0.15, 1)
        out[:, :, :3][~inside] = atmosphere
        out[:, :, 3] = np.where(inside, 255, glow ** 2 * 170 * rim)
        edge = np.clip((np.sqrt(d2) - 0.86) / 0.14, 0, 1) * inside * 0.55 * np.clip(light * 2, 0, 1)
        out[:, :, :3] = out[:, :, :3] * (1 - edge[:, :, None]) + np.array(atmosphere, dtype=float) * edge[:, :, None]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def planet(name):
    size = PLANETS[name]
    if name == "asteroids":
        k = 5
        img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
        rng = np.random.default_rng(12)
        for _ in range(11):
            s = int(rng.integers(5, 13)) * k
            rock = sphere("moon", s // k * 2, radius=s // k * 0.82).resize((s, s), Image.LANCZOS)
            rock = rock.rotate(int(rng.integers(0, 360)))
            img.alpha_composite(rock, (int(rng.integers(0, size * k - s)), int(rng.integers(0, size * k - s))))
        return img.resize((size, size), Image.LANCZOS)
    if name == "saturn":
        k = 5
        full = size * k
        body = sphere("saturn", size, radius=size * 0.27)
        yy, xx = np.mgrid[0:full, 0:full]
        x, y = (xx - full / 2) / (full / 2), (yy - full / 2) / (full / 2)
        ang = np.radians(-14)
        rx = x * np.cos(ang) - y * np.sin(ang)
        ry = (x * np.sin(ang) + y * np.cos(ang)) / 0.3
        d = np.sqrt(rx ** 2 + ry ** 2)
        band = (d > 0.62) & (d < 0.96) & ~((d > 0.8) & (d < 0.835))
        tone = 150 + 60 * np.sin(d * 58)
        ring_rgb = np.dstack([tone * 1.08, tone * 0.98, tone * 0.76, band * 225.0])
        ring_img = Image.fromarray(np.clip(ring_rgb, 0, 255).astype(np.uint8))
        back = np.array(ring_img)
        back[(ry > 0)] = 0
        front = np.array(ring_img)
        front[(ry <= 0)] = 0
        img = Image.fromarray(back)
        img.alpha_composite(body)
        img.alpha_composite(Image.fromarray(front))
        return img.resize((size, size), Image.LANCZOS)
    glow = {"earth": (120, 176, 255), "venus": (246, 226, 170), "mars": (230, 160, 120), "jupiter": (232, 208, 170)}.get(name)
    return sphere(name, size, atmosphere=glow).resize((size, size), Image.LANCZOS)




def solar_map():
    # The Sun on the left, the orbits passing through each body, and stars. The planets are buttons over it.
    w, h = space_program.SOLAR_W, space_program.SOLAR_H
    t_ = np.linspace(0, 1, w)[None, :, None]
    base = np.array([20, 26, 42.0]) * (1 - t_) + np.array([7, 9, 15.0]) * t_
    cloud = noise((h, w), 3, 3, 5)[:, :, None]
    rgb = base + cloud * np.array([20, 16, 34.0]) * 0.6
    rng = np.random.default_rng(7)
    for x, y, v, s in zip(rng.integers(0, w, 420), rng.integers(0, h, 420), rng.integers(70, 235, 420), rng.random(420)):
        rgb[y, x] = v
        if s > 0.93 and 0 < x < w - 1 and 0 < y < h - 1:
            rgb[y, x + 1] = rgb[y, x - 1] = rgb[y + 1, x] = rgb[y - 1, x] = v * 0.5
    cx, cy = space_program.SOLAR_SUN
    yy, xx = np.mgrid[0:h, 0:w]
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    glow = np.clip(1 - dist / 240, 0, 1) ** 2.4
    rgb = rgb + glow[:, :, None] * np.array([255, 190, 96.0]) * 0.72
    disc_ = np.clip((86 - dist) / 3, 0, 1)
    core = np.clip(1 - dist / 86, 0, 1) ** 0.5
    sun = np.dstack([np.full((h, w), 255.0), 196 + core * 56, 92 + core * 130])
    rgb = rgb * (1 - disc_[:, :, None]) + sun * disc_[:, :, None]
    img = Image.fromarray(np.dstack([np.clip(rgb, 0, 255), np.full((h, w), 255.0)]).astype(np.uint8)).resize((w * 3, h * 3), Image.LANCZOS)
    d = ImageDraw.Draw(img)
    ratio = 1.0
    for b in space_program.BODIES:
        if b[0] == "moon":
            continue
        bx, by = space_program.SOLAR_POS[b[0]]
        rx = float(np.hypot(bx - cx, (by - cy) / ratio))
        d.ellipse([(cx - rx) * 3, (cy - rx * ratio) * 3, (cx + rx) * 3, (cy + rx * ratio) * 3], outline=(64, 92, 132, 255), width=2)
    img = img.resize((w, h), Image.LANCZOS)
    a = np.array(img)
    a[0, :, :3] = a[-1, :, :3] = theme.LINE
    a[:, 0, :3] = a[:, -1, :3] = theme.LINE
    return Image.fromarray(a)




def tab_button():
    # Millennium Dawn's tab (two frames of 90 x 53), narrower keeping its corners, so eight fit in its panel's width.
    src = Image.open("../Millennium-Dawn-2.0.0/gfx/interface/scripted_gui/missiles/missiles_gui_ledger_btn.dds").convert("RGBA")
    out = Image.new("RGBA", (132, 53), (0, 0, 0, 0))
    for f in range(2):
        x = f * 90
        out.paste(src.crop((x, 0, x + 24, 53)), (f * 66, 0))
        out.paste(src.crop((x + 24, 0, x + 66, 53)).resize((18, 53), Image.LANCZOS), (f * 66 + 24, 0))
        out.paste(src.crop((x + 66, 0, x + 90, 53)), (f * 66 + 42, 0))
    return out


def spaceport_strips():
    # Same orange and dark outline as the other Realpolitik buildings, on the background of the strip.
    mask = icon_spaceport()
    a = np.array(mask, dtype=float) / 255
    level = np.linspace(1, 0, a.shape[0])[:, None]
    stops = np.array([[186, 84, 10.0], [240, 138, 28], [255, 192, 74]])
    pos = level * (len(stops) - 1)
    low = np.minimum(pos.astype(int), len(stops) - 2)
    rgb = stops[low] + (stops[low + 1] - stops[low]) * (pos - low)[:, :, None]
    rim = np.array(mask.filter(ImageFilter.MaxFilter(2 * int(S * 0.7) + 1)), dtype=float) / 255
    colour = rgb * a[:, :, None] + np.array([28, 14, 4.0]) * (1 - a[:, :, None])
    img = Image.fromarray(np.clip(np.dstack([colour, rim * 255]), 0, 255).astype(np.uint8))
    img = img.crop(img.getbbox())
    scale = min(34 / img.width, 33 / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    icon = Image.new("RGBA", (46, 46), (0, 0, 0, 0))
    icon.alpha_composite(img, ((46 - img.width) // 2, (46 - img.height) // 2))
    root = "gfx/interface/buildings/"
    with_bg = Image.open(root + "building_icon_strip.dds").convert("RGBA")
    bare = Image.open(root + "building_icon_without_bg_strip.dds").convert("RGBA")
    # The background is what the frames show where their icon leaves it uncovered.
    frames = [f for f in range(48) if f != 47]
    wb = np.array(with_bg, dtype=float)
    nb = np.array(bare, dtype=float)
    stack = np.stack([wb[0:46, f * 46:(f + 1) * 46] for f in frames])
    clear = np.stack([nb[0:46, f * 46:(f + 1) * 46, 3] < 8 for f in frames])
    stack[~clear] = np.nan
    bg = Image.fromarray(np.nan_to_num(np.nanmedian(stack, axis=0)).astype(np.uint8))
    bg.alpha_composite(icon)
    x = 47 * 46
    with_bg.paste(bg, (x, 0))
    bare.paste(icon, (x, 0))
    save_dds(with_bg, root + "building_icon_strip.dds")
    save_dds(bare, root + "building_icon_without_bg_strip.dds")


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    gfx = "# Generated by herramientas/make_space_icons.py.\nspriteTypes = {\n"
    for name, draw in ICONS.items():
        save_dds(finish(draw()), f"{OUT}{name}.dds")
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_icon_{name}"\n\t\ttextureFile = "{OUT}{name}.dds"\n\t}}\n'
    for name, art in (("panel", theme.panel_sprite()), ("rule", theme.rule_sprite()), ("hero", theme.hero_sprite(earth_art())), ("backdrop", theme.backdrop_sprite(earth_art()))):
        save_dds(art, f"{OUT}{name}.dds")
        if name == "panel":
            gfx += f'\tcorneredTileSpriteType = {{\n\t\tname = "GFX_mdr_space_panel"\n\t\ttextureFile = "{OUT}panel.dds"\n\t\tborderSize = {{ x = 8 y = 8 }}\n\t}}\n'
        else:
            gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_{name}"\n\t\ttextureFile = "{OUT}{name}.dds"\n\t}}\n'
    save_dds(theme.window_sprite(), f"{OUT}window.dds")
    gfx += f'\tcorneredTileSpriteType = {{\n\t\tname = "GFX_mdr_space_window"\n\t\ttextureFile = "{OUT}window.dds"\n\t\tborderSize = {{ x = 24 y = 24 }}\n\t}}\n'
    # Buttons light up and sink like the game's own, with its button shader.
    for name, art in (("btn_71x26", theme.button(71, 26)), ("btn_123x34", theme.button(123, 34)), ("arrow_left", theme.arrow("left")), ("arrow_right", theme.arrow("right"))):
        save_dds(art, f"{OUT}{name}.dds")
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_{name}"\n\t\ttextureFile = "{OUT}{name}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    extras ={"site_mapicon": (map_icon(), 1), "meter": (theme.meter(), 51), "chart_bar": (theme.chart_bar(), 51), "navtab": (theme.nav_tab(), 2), "sidetab": (theme.side_tab(), 2),"solar_map": (solar_map(), 1)}
    for name in PLANETS:
        extras["planet_" + name] = (planet(name), 1)
    extras["header"] = (theme.header_sprite(), 1)
    # Category banners of Projects and Decisions, from Millennium Dawn's space pictures.
    art = "../Millennium-Dawn-2.0.0/gfx/event_pictures/generic/space_stuff/"
    for short, names in (("p", space_program.CAT_ART_P), ("d", space_program.CAT_ART_D)):
        for n, pic in enumerate(names):
            save_dds(theme.banner(Image.open(f"{art}{pic}.dds")), f"{OUT}banner_{short}{n + 1}.dds")
            gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_banner_{short}{n + 1}"\n\t\ttextureFile = "{OUT}banner_{short}{n + 1}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    extras["banner_sel"] = (theme.banner_selected(), 1)
    for n, pic in enumerate(space_program.COLONY_ART):
        save_dds(theme.banner(Image.open(f"{art}{pic}.dds"), 370, 56), f"{OUT}banner_col{n + 1}.dds")
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_banner_col{n + 1}"\n\t\ttextureFile = "{OUT}banner_col{n + 1}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    extras["banner_col_sel"] = (theme.banner_selected(370, 56), 1)
    for n, pic in enumerate(space_program.GOAL_ART):
        extras[f"goal_{n}"] = (theme.card(Image.open(f"{art}{pic}.dds"), 134, 112), 1)
    for n, card in enumerate(space_program.CARDS):
        save_dds(theme.card(Image.open(f"{art}{card[0]}.dds")), f"{OUT}card_{n}.dds")
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_card_{n}"\n\t\ttextureFile = "{OUT}card_{n}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    for size in sorted({s + 10 for s in PLANETS.values()}):
        extras[f"ring_{size}"] = (theme.selection_ring(size), 1)
    for name, (art, frames) in extras.items():
        save_dds(art, f"{OUT}{name}.dds")
        count = f"\t\tnoOfFrames = {frames}\n" if frames > 1 else ""
        gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_{name}"\n\t\ttextureFile = "{OUT}{name}.dds"\n{count}\t}}\n'
    save_dds(tab_button(), f"{OUT}tab_btn.dds")
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_tab_btn"\n\t\ttextureFile = "{OUT}tab_btn.dds"\n\t\tnoOfFrames = 2\n\t}}\n'
    save_dds(theme.budget_bar(), f"{OUT}budget_bar.dds")
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_budget_bar"\n\t\ttextureFile = "{OUT}budget_bar.dds"\n\t\tnoOfFrames = 51\n\t}}\n'
    ring_img = Image.new("RGBA", (74, 66), (0, 0, 0, 0))
    ImageDraw.Draw(ring_img).rounded_rectangle([1, 1, 72, 64], radius=8, outline=(226, 196, 120, 255), width=2)
    save_dds(ring_img, f"{OUT}logo_ring.dds")
    gfx += f'\tspriteType = {{\n\t\tname = "GFX_mdr_space_logo_ring"\n\t\ttextureFile = "{OUT}logo_ring.dds"\n\t}}\n'
    gfx += "}\n"
    with open("interface/mdr_space_icons.gfx", "wb") as f:
        f.write(gfx.encode("utf-8"))
    spaceport_strips()
    print("ok", len(ICONS))
