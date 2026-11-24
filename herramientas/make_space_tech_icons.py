# Icons of the space programme technologies (gfx/interface/mdr/space/tech_<name>.dds, 64 x 64): one drawn scene per
# technology, in the style of make_ammo_icons.py, using the 3D helpers of make_uranium_icons.py and make_clean_icons.py.
# Scenes on Earth sit on a floor tile; orbital ones float over the curve of the Earth; others on the Moon, Mars or in space.
# make_space.py no longer crops Millennium Dawn's pictures for these. Run from the mod folder:
# python herramientas/make_space_tech_icons.py [preview.png]
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ammo_icons as A  # noqa: E402
import make_uranium_icons as U  # noqa: E402
import make_clean_icons as C  # noqa: E402

S, N, INK = A.S, A.N, A.INK
pr, box3, cyl, pipe, shade = U.pr, U.box3, U.cyl, U.pipe, U.shade
pipe3, dot, windows = C.pipe3, C.dot, C.windows
CONC = (176, 172, 160)
WHITE = (232, 234, 236)
PANEL = (40, 60, 120)


# ---------------------------------------------------------------- shared space pieces
def rocket(im, cx, by, h, half, body=WHITE, band=(40, 40, 44), fins=(60, 64, 72)):
    """Upright rocket in screen units: base centre (cx, by), height h, radius half."""
    prof = [(0, 0.86), (0.03, 1.0), (0.74, 1.0)] + A.ogive(0.74, 1.0, 1.0, 0.05, 8, 1.6)
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):  # fins behind the body edge
        fin = [(cx + sx * half * 0.8, by - h * 0.2), (cx + sx * half * 2.0, by - h * 0.02), (cx + sx * half * 2.0, by + 0.4), (cx + sx * half * 0.8, by)]
        d.polygon(A.P(fin), fill=fins + (255,), outline=INK + (255,), width=max(2, S // 2))
    full, col = A.solid(cx, by, h, half, prof, [(0, 0.12, band, 0.4), (0.12, 0.6, body, 0.55), (0.6, 0.66, band, 0.4), (0.66, 1.0, body, 0.55)],
                        rings=[(0.36, (190, 194, 200))])
    A.place(im, full, col, 0.9)
    bell, bcol = A.solid(cx, by + 2.2, 2.4, half * 0.8, [(0, 1.0), (1, 0.55)], [(0, 1, (70, 72, 78), 0.3)])
    A.place(im, bell, bcol, 0.6)


def lattice(im, x0, y0, x1, y1, z0, z1, levels, c=(200, 70, 50), o=U.O):
    """Square lattice tower between two corners, with X bracing on the two faces we see."""
    d = ImageDraw.Draw(im)
    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    lines = [[pr(*p, z0, o), pr(*p, z1, o)] for p in corners]
    for k in range(levels):
        za, zb = z0 + (z1 - z0) * k / levels, z0 + (z1 - z0) * (k + 1) / levels
        for a, b in ((corners[0], corners[1]), (corners[1], corners[2])):
            lines += [[pr(*a, za, o), pr(*b, zb, o)], [pr(*b, za, o), pr(*a, zb, o)], [pr(*a, zb, o), pr(*b, zb, o)]]
    for ln in lines:
        d.line(A.P(ln), fill=INK + (255,), width=int(0.85 * S))
    for ln in lines:
        d.line(A.P(ln), fill=c + (255,), width=max(2, int(0.4 * S)))


def panel_xz(im, x0, x1, y, z0, z1, o, cells=4):
    """Solar array in the x-z plane (faces the front left)."""
    quad = [pr(x0, y, z1, o), pr(x1, y, z1, o), pr(x1, y, z0, o), pr(x0, y, z0, o)]
    d = ImageDraw.Draw(im)
    m = A.mask_of(lambda dd: dd.polygon(A.P(quad), fill=255))
    im.alpha_composite(A.outline(m, 0.6))
    im.alpha_composite(A.vgrad(m, (70, 96, 160), (36, 52, 104)))
    d = ImageDraw.Draw(im)
    for k in range(1, cells):
        t = k / cells
        d.line(A.P([A.lerp(quad[0], quad[1], t), A.lerp(quad[3], quad[2], t)]), fill=(150, 176, 220, 255), width=max(2, S // 4))
    d.line(A.P([A.lerp(quad[0], quad[3], 0.5), A.lerp(quad[1], quad[2], 0.5)]), fill=(150, 176, 220, 255), width=max(2, S // 4))


def vnoise3(p, freq, seed):
    """Smooth 3D value noise at points p (n x 3, roughly in -1..1), between 0 and 1."""
    g = int(2 * freq + 4)
    grid = np.random.default_rng(seed).random((g, g, g)).astype(np.float32)
    q = p * freq + freq + 1.5
    i = np.floor(q).astype(int)
    f = q - i
    f = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[:, 0] if dx else 1 - f[:, 0]) * (f[:, 1] if dy else 1 - f[:, 1]) * (f[:, 2] if dz else 1 - f[:, 2])
                out = out + w * grid[(i[:, 0] + dx) % g, (i[:, 1] + dy) % g, (i[:, 2] + dz) % g]
    return out


def fbm(p, freq, octaves, seed):
    total, amp, norm = 0, 1.0, 0
    for k in range(octaves):
        total = total + amp * vnoise3(p, freq * 2 ** k, seed + k)
        norm += amp
        amp *= 0.5
    return total / norm


def earth_sphere(im, cx, cy, r, light=(-0.62, -0.5, 0.6), spin=(0.4, 0.3), seed=21, outline=0.7):
    """The Earth as a lit sphere: oceans, continents with deserts and forests, polar ice, cloud swirls,
    a soft day-night line and the blue haze of the atmosphere toward the edge."""
    ys, xs = np.mgrid[0:A.W, 0:A.W]
    nx = (xs / S - cx) / r
    ny = (ys / S - cy) / r
    d2 = nx * nx + ny * ny
    inside = d2 < 1
    nxi, nyi = nx[inside], ny[inside]
    nzi = np.sqrt(np.clip(1 - nxi * nxi - nyi * nyi, 0, 1))
    # rotate the globe so the continents sit at a pleasant angle
    a, b = spin
    x1 = nxi * math.cos(a) + nzi * math.sin(a)
    z1 = -nxi * math.sin(a) + nzi * math.cos(a)
    y2 = nyi * math.cos(b) - z1 * math.sin(b)
    z2 = nyi * math.sin(b) + z1 * math.cos(b)
    p = np.stack([x1, y2, z2], -1).astype(np.float32)
    lat = np.abs(y2)
    h = fbm(p, 1.6, 5, seed)
    land = h > 0.53
    ocean = np.stack([18 + 30 * h, 58 + 60 * h, 120 + 70 * h], -1)
    green = np.array([70, 112, 58]); dry = np.array([176, 150, 100]); ice = np.array([236, 240, 244])
    desert = np.clip((fbm(p, 2.2, 3, seed + 9) - 0.45) * 4, 0, 1)[:, None]
    lcol = green * (1 - desert) + dry * desert
    lcol = lcol * (0.8 + 0.5 * (h[:, None] - 0.53))
    col = np.where(land[:, None], lcol, ocean)
    polar = np.clip((lat - 0.86) * 10, 0, 1)[:, None]
    col = col * (1 - polar) + ice * polar
    # clouds stretched along the latitude lines, with a few swirls
    pc = p * np.array([1.0, 2.2, 1.0], np.float32)
    c = fbm(pc + 0.35 * (fbm(p, 2.0, 2, seed + 30)[:, None] - 0.5), 2.4, 5, seed + 50)
    cloud = np.clip((c - 0.5) * 3.2, 0, 0.92)[:, None]
    col = col * (1 - cloud) + 245 * cloud
    # light: soft terminator, faint night side, a small glint on the sea
    L = np.array(light, float); L /= np.linalg.norm(L)
    nrm = np.stack([nxi, nyi, nzi], -1)
    lam = nrm @ np.array([L[0], L[1], L[2]])
    day = np.clip((lam + 0.12) / 0.35, 0, 1)[:, None]
    shade = (0.22 + 0.9 * np.clip(lam, 0, 1))[:, None]
    lit = col * shade
    night = np.array([10, 16, 32]) + col * 0.05
    col = lit * day + night * (1 - day)
    hv = L + np.array([0, 0, 1.0]); hv /= np.linalg.norm(hv)
    glint = (np.clip(nrm @ hv, 0, 1) ** 220 * (~land) * (1 - cloud[:, 0]))[:, None]
    col = col + 70 * glint
    # atmosphere: haze toward the edge on the day side
    fres = ((1 - nzi) ** 2.2)[:, None] * np.clip(lam + 0.35, 0, 1)[:, None]
    col = col * (1 - fres * 0.75) + np.array([120, 180, 250]) * fres * 0.75
    arr = np.zeros((A.W, A.W, 4), np.uint8)
    rgb = np.zeros((A.W, A.W, 3), np.float32)
    rgb[inside] = col
    arr[..., :3] = np.clip(rgb, 0, 255)
    arr[..., 3] = inside * 255
    lay = Image.fromarray(arr, "RGBA").filter(ImageFilter.GaussianBlur(0.35 * S / 4))
    lay.putalpha(Image.fromarray((inside * 255).astype(np.uint8)))
    if outline:
        im.alpha_composite(A.outline(lay.getchannel("A"), outline))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    d.arc([(cx - r + 0.2) * S, (cy - r + 0.2) * S, (cx + r - 0.2) * S, (cy + r - 0.2) * S], 150, 300, fill=(150, 205, 250, 255), width=max(2, int(0.45 * S)))


def atmosphere_halo(im, cx, cy, r, width=1.6):
    """Thin blue layer of air just outside the edge of the planet."""
    m = A.mask_of(lambda d: d.ellipse([(cx - r - width) * S, (cy - r - width) * S, (cx + r + width) * S, (cy + r + width) * S], fill=170))
    m = m.filter(ImageFilter.GaussianBlur(width * S * 0.45))
    halo = Image.new("RGBA", (A.W, A.W), (120, 186, 250, 0))
    halo.putalpha(m)
    im.alpha_composite(halo)


def earth_limb(im):
    atmosphere_halo(im, 32, 123, 76)
    earth_sphere(im, 32, 123, 76, light=(-0.55, -0.75, 0.38), spin=(5.0, -0.5), seed=21)


def small_earth(im, cx, cy, r):
    atmosphere_halo(im, cx, cy, r, 0.9)
    earth_sphere(im, cx, cy, r, light=(-0.9, -0.2, 0.38), spin=(0.3, 0.2), seed=33, outline=0.6)


def moon_ground(x, y):
    z = 3.0 + 0.25 * math.sin(x * 0.7) * math.cos(y * 0.6)
    for cx, cy, r in ((24, 7, 4.5), (6, 26, 3.5), (27, 25, 2.6)):
        dd = math.hypot(x - cx, y - cy) / r
        if dd < 1:
            z -= 1.6 * (1 - dd * dd)
        elif dd < 1.5:
            z += 0.7 * (1.5 - dd) / 0.5
    return z


def moon_color(x, y, z):
    n = (U.hashn(round(x * 2), round(y * 2)) - 0.5) * 18
    return tuple(int(v + n) for v in (150, 148, 144))


def moon_tile(im):
    U.terrain(im, moon_ground, 0, 32.2, 0, 32.2, 48, moon_color, skirt=lambda z: (104, 102, 100), edge=0.9)


# ---------------------------------------------------------------- launcher: rocket on its pad with the service tower
def icon_launcher():
    im = A.layer()
    A.floor(im)
    box3(im, 5, 5, 0, 22, 22, 2.5, CONC, 0.9)
    d = ImageDraw.Draw(im)
    trench = [pr(14, 5, 2.5), pr(20, 5, 2.5), pr(20, 5, 0.6), pr(14, 5, 0.6)]
    d.polygon(A.P(trench), fill=(40, 40, 44, 255))
    lattice(im, 7, 15, 11, 19, 2.5, 34, 7)
    base = pr(17, 13, 3.4)
    for z in (18, 27):  # umbilical arms
        a, b = pr(11, 15, z), (base[0] - 2.6, base[1] - z + 3.4)
        d = ImageDraw.Draw(im)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.1 * S))
        d.line(A.P([a, b]), fill=(200, 70, 50, 255), width=max(2, int(0.5 * S)))
    rocket(im, base[0], base[1], 33, 3.0)
    return im


# ---------------------------------------------------------------- station: modules, truss and solar wings above the Earth
def icon_station():
    im = A.layer()
    earth_limb(im)
    o = (32, 30)
    for y in (15, 11):  # far wings
        panel_xz(im, -8.5, 8.5, y, -2.8, 2.8, o)
    box3(im, -0.8, -16.5, -0.8, 1.6, 33, 1.6, (200, 204, 210), 0.6, o=o)
    cyl(im, (-10.5, 0, 0), "x", 21, 2.6, WHITE, rings=[(0.25, (170, 176, 184), 0.4), (0.5, (170, 176, 184), 0.4), (0.75, (170, 176, 184), 0.4)], o=o)
    cyl(im, (0, -4.2, 0), "y", 8.4, 2.2, WHITE, rings=[(0.5, (170, 176, 184), 0.4)], o=o)
    cyl(im, (10.5, 0, 0), "x", 4.0, 1.7, (200, 204, 210), o=o)  # docked capsule
    box3(im, 3.5, -1.2, 2.4, 5, 2.4, 5.4, (236, 236, 232), 0.5, o=o)  # radiator
    for y in (-11, -15):  # near wings
        panel_xz(im, -8.5, 8.5, y, -2.8, 2.8, o)
    return im


# ---------------------------------------------------------------- habitat: lunar modules under regolith, solar mast, Earth in the sky
def icon_habitat():
    im = A.layer()
    d = ImageDraw.Draw(im)
    # the Earth hanging over the horizon
    small_earth(im, 12, 15, 7.0)
    moon_tile(im)
    gz = 3.0
    # inflatable module covered by a regolith berm, and a rigid module joined by a node
    U.terrain(im, lambda x, y: gz + max(0.0, 5.8 * (1 - ((x - 9) / 7.5) ** 2 - ((y - 20) / 6) ** 2)) ** 0.8, 1, 17, 13, 27, 26,
              lambda x, y, z: moon_color(x, y, z), base_z=gz + 0.05)
    cyl(im, (10, 9.5, gz + 2.6), "x", 13, 2.6, WHITE, rings=[(0.33, (170, 176, 184), 0.4), (0.66, (170, 176, 184), 0.4)])
    cyl(im, (14.5, 9.5, gz + 2.6), "y", 4.4, 1.5, (200, 204, 210))
    d = ImageDraw.Draw(im)
    for k in range(3):
        dot(d, pr(13 + k * 3.6, 6.9, gz + 3.2), 0.55, (90, 150, 210), INK[:3])
    # solar mast and a small rover
    cyl(im, (26, 18, gz), "z", 11, 0.4, (150, 156, 164))
    panel_xz(im, 22.5, 29.5, 18, gz + 9, gz + 14, U.O, 3)
    box3(im, 24, 3, gz + 1.2, 4.6, 3.2, 1.6, (214, 170, 70), 0.6)
    for wx in (24.8, 27.8):
        cyl(im, (wx, 2.6, gz + 0.9), "y", 0.8, 0.9, (60, 60, 64))
    return im


# ---------------------------------------------------------------- more shared pieces
STEEL_SS = (196, 200, 206)
SOOT = (70, 64, 58)


def body_rocket(im, cx, by, h, half, sections, nose=0.24, fins=None, rings=(), bell=True, bell_c=(70, 72, 78)):
    """Upright rocket in screen units with any colour sections (t0, t1, colour, spec)."""
    top = 1 - nose
    prof = [(0, 1.0), (top, 1.0)] + A.ogive(top, 1.0, 1.0, 0.06, 8, 1.6)
    if fins:
        d = ImageDraw.Draw(im)
        for sx in (-1, 1):
            fin = [(cx + sx * half * 0.8, by - h * 0.16), (cx + sx * half * 1.9, by - h * 0.01), (cx + sx * half * 1.9, by + 0.4), (cx + sx * half * 0.8, by)]
            d.polygon(A.P(fin), fill=fins + (255,), outline=INK + (255,), width=max(2, S // 2))
    full, col = A.solid(cx, by, h, half, prof, sections, rings=rings)
    A.place(im, full, col, 0.9)
    if bell:
        b, bc = A.solid(cx, by + 2.0, 2.2, half * 0.75, [(0, 1.0), (1, 0.55)], [(0, 1, bell_c, 0.3)])
        A.place(im, b, bc, 0.6)


def flame(im, cx, top, length, width):
    """Exhaust plume under an engine: white-yellow core fading to orange."""
    m = A.mask_of(lambda d: d.polygon(A.P([(cx - width, top), (cx + width, top), (cx + width * 0.35, top + length * 0.6), (cx, top + length), (cx - width * 0.35, top + length * 0.6)]), fill=255))
    m = m.filter(ImageFilter.GaussianBlur(0.4 * S))
    im.alpha_composite(A.vgrad(m, (255, 246, 200), (240, 120, 40)))


def legs(im, cx, by, half, spread, drop):
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):
        a, b = (cx + sx * half * 0.8, by - 4), (cx + sx * (half + spread), by + drop)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.2 * S))
        d.line(A.P([a, b]), fill=(60, 60, 64, 255), width=max(2, int(0.55 * S)))


def sea_tile(im):
    L, F, R, Bk = pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 32.2, 0), pr(0, 32.2, 0)
    m = A.mask_of(lambda d: d.polygon(A.P([L, F, R, Bk]), fill=255))
    im.alpha_composite(A.outline(m, 0.8))
    im.alpha_composite(A.noisy(A.vgrad(m, (70, 140, 196), (40, 100, 160)), 4, 6))
    d = ImageDraw.Draw(im)
    for x, y in ((4, 6), (12, 2), (26, 4), (5, 22), (28, 27), (14, 29)):
        p = pr(x, y, 0)
        d.arc([(p[0] - 2.2) * S, (p[1] - 0.7) * S, (p[0] + 2.2) * S, (p[1] + 0.7) * S], 200, 340, fill=(190, 226, 246, 255), width=max(2, S // 3))


def planet(im, cx, cy, r, kind, light=(-0.7, -0.4, 0.55), spin=(0.5, 0.2), seed=5, outline=0.6):
    """A small lit globe of Mars, the Moon or another body."""
    ys, xs = np.mgrid[0:A.W, 0:A.W]
    nx, ny = (xs / S - cx) / r, (ys / S - cy) / r
    inside = nx * nx + ny * ny < 1
    nxi, nyi = nx[inside], ny[inside]
    nzi = np.sqrt(np.clip(1 - nxi * nxi - nyi * nyi, 0, 1))
    a, b = spin
    x1, z1 = nxi * math.cos(a) + nzi * math.sin(a), -nxi * math.sin(a) + nzi * math.cos(a)
    y2, z2 = nyi * math.cos(b) - z1 * math.sin(b), nyi * math.sin(b) + z1 * math.cos(b)
    p = np.stack([x1, y2, z2], -1).astype(np.float32)
    h = fbm(p, 1.8, 5, seed)
    if kind == "mars":
        col = np.array([196, 104, 60]) * (0.75 + 0.5 * h[:, None])
        dark = np.clip((h - 0.56) * 6, 0, 1)[:, None]
        col = col * (1 - dark * 0.45)
        cap = np.clip((np.abs(y2) - 0.88) * 12, 0, 1)[:, None]
        col = col * (1 - cap) + np.array([240, 236, 230]) * cap
        haze = np.array([230, 170, 130])
    elif kind == "moon":
        col = np.array([176, 174, 170]) * (0.8 + 0.4 * h[:, None])
        mare = np.clip((fbm(p, 1.2, 3, seed + 3) - 0.55) * 6, 0, 1)[:, None]
        col = col * (1 - mare * 0.4)
        haze = None
    elif kind == "venus":
        band = fbm(p * np.array([1, 3, 1], np.float32), 1.6, 4, seed)
        col = np.array([236, 206, 140]) * (0.8 + 0.4 * band[:, None])
        haze = np.array([250, 230, 180])
    elif kind == "jupiter":
        band = np.sin(y2 * 14 + 2 * fbm(p, 2, 3, seed)) * 0.5 + 0.5
        col = np.array([214, 180, 140]) * (0.75 + 0.35 * band[:, None])
        haze = None
    elif kind == "titan":
        col = np.array([214, 150, 70]) * (0.85 + 0.3 * h[:, None])
        haze = np.array([240, 190, 110])
    else:  # asteroid grey-brown
        col = np.array([140, 126, 110]) * (0.7 + 0.6 * h[:, None])
        haze = None
    L = np.array(light, float); L /= np.linalg.norm(L)
    lam = np.stack([nxi, nyi, nzi], -1) @ L
    day = np.clip((lam + 0.1) / 0.3, 0, 1)[:, None]
    col = col * (0.2 + 0.9 * np.clip(lam, 0, 1))[:, None] * day + np.array([12, 12, 16]) * (1 - day)
    if haze is not None:
        fres = ((1 - nzi) ** 2.2)[:, None] * np.clip(lam + 0.35, 0, 1)[:, None]
        col = col * (1 - fres * 0.6) + haze * fres * 0.6
    arr = np.zeros((A.W, A.W, 4), np.uint8)
    rgb = np.zeros((A.W, A.W, 3), np.float32)
    rgb[inside] = col
    arr[..., :3] = np.clip(rgb, 0, 255)
    arr[..., 3] = inside * 255
    lay = Image.fromarray(arr, "RGBA")
    if outline:
        im.alpha_composite(A.outline(lay.getchannel("A"), outline))
    im.alpha_composite(lay)


def stars(im, n=14, seed=3, box=(2, 2, 62, 40)):
    """A few faint stars for scenes set in deep space."""
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        r = rng.uniform(0.25, 0.5)
        d.ellipse([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], fill=(220, 226, 240, int(rng.uniform(120, 220))))


def spaceship_h(im, o, x0, length, r, color, rings=(), cap=None):
    """Horizontal cylinder along x in a floating scene with origin o."""
    cyl(im, (x0, 0, 0), "x", length, r, color, rings=rings, cap=cap, o=o)


# ---------------------------------------------------------------- foundations: drafting table with the rocket blueprint and a model
def icon_foundations():
    im = A.layer()
    A.floor(im)
    # drafting table
    for lx, ly in ((5, 6), (23, 6), (5, 20), (23, 20)):
        cyl(im, (lx, ly, 0), "z", 7, 0.5, (110, 80, 50))
    box3(im, 4, 5, 7, 21, 17, 1.0, (150, 110, 70), 0.8)
    sheet = [pr(5, 6, 8.05), pr(24, 6, 8.05), pr(24, 21, 8.05), pr(5, 21, 8.05)]
    d = ImageDraw.Draw(im)
    d.polygon(A.P(sheet), fill=(44, 80, 150, 255), outline=(220, 230, 250, 255), width=max(2, S // 4))
    w = lambda x, y: pr(x, y, 8.05)
    for a, b in (((8, 12), (20, 12)), ((8, 15), (20, 15)), ((20, 12), (23, 13.5)), ((23, 13.5), (20, 15)), ((8, 12), (6.5, 10.5)), ((8, 15), (6.5, 16.5)),
                 ((11, 12), (11, 15)), ((15, 12), (15, 15)), ((7, 8), (11, 8)), ((7, 19), (14, 19))):
        d.line(A.P([w(*a), w(*b)]), fill=(220, 232, 250, 255), width=max(2, S // 3))
    # model rocket on a stand and a desk globe
    p = pr(26, 26, 0)
    box3(im, 24.5, 24.5, 0, 3, 3, 1.4, (60, 60, 64), 0.6)
    body_rocket(im, p[0], p[1] - 1.4, 20, 1.9, [(0, 0.15, (40, 40, 44), 0.4), (0.15, 1.0, WHITE, 0.55)], fins=(200, 60, 50), bell=False)
    g = pr(9, 24, 0)
    box3(im, 7.6, 22.6, 0, 2.8, 2.8, 1.0, (110, 80, 50), 0.6)
    d = ImageDraw.Draw(im)
    d.line(A.P([(g[0], g[1] - 1), (g[0], g[1] - 5)]), fill=INK + (255,), width=int(0.6 * S))
    earth_sphere(im, g[0], g[1] - 8.6, 4.2, spin=(5.0, -0.2), seed=21, outline=0.6)
    return im


# ---------------------------------------------------------------- heavy: core stage with two solid boosters
def icon_heavy():
    im = A.layer()
    A.floor(im)
    box3(im, 5, 5, 0, 22, 22, 2.5, CONC, 0.9)
    lattice(im, 6, 18, 10, 22, 2.5, 38, 8)
    p = pr(18, 14, 3.4)
    boost = [(0, 0.08, (60, 60, 64), 0.3), (0.08, 1.0, (226, 226, 222), 0.55)]
    body_rocket(im, p[0] + 4.4, p[1] - 0.6, 22, 1.8, boost, nose=0.16)
    body_rocket(im, p[0], p[1], 40, 3.4, [(0, 0.1, (60, 60, 64), 0.4), (0.1, 0.7, (234, 232, 226), 0.55), (0.7, 0.74, (40, 40, 44), 0.4), (0.74, 1.0, WHITE, 0.55)],
                nose=0.2, rings=[(0.4, (190, 194, 200))])
    body_rocket(im, p[0] - 4.4, p[1] + 0.6, 22, 1.8, boost, nose=0.16)
    return im


# ---------------------------------------------------------------- cryogenic: frosted hydrogen-oxygen stage venting on its cradle
def icon_cryogenic():
    im = A.layer()
    A.floor(im)
    for cx in (8, 20):
        box3(im, cx, 9, 0, 3, 8, 4.0, (60, 90, 150), 0.7)
    # the stage lying along x: frosted tank, then the engine
    cyl(im, (2, 13, 8.2), "x", 22, 5.6, (232, 236, 240), rings=[(0.45, (150, 160, 176), 0.6), (0.48, (150, 160, 176), 0.6)], cap=(216, 222, 230))
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(2)
    for _ in range(70):  # frost patches on the tank
        x, a = rng.uniform(3, 23), rng.uniform(-1.4, 1.2)
        p = pr(x, 13 + 5.6 * math.cos(a) * -1 * 0 - 5.6 * math.sin(-a) * 0, 8.2 + 5.6 * math.sin(a))
        p = pr(x, 13 - 5.6 * math.cos(a), 8.2 + 5.6 * math.sin(a))
        r = rng.uniform(0.3, 0.8)
        d.ellipse([(p[0] - r) * S, (p[1] - r * 0.5) * S, (p[0] + r) * S, (p[1] + r * 0.5) * S], fill=(250, 252, 255, 200))
    im.alpha_composite(lay)
    cyl(im, (24, 13, 8.2), "x", 3, 2.4, (120, 126, 134))
    cone = [pr(27, 13 - 1.8, 8.2 + 1.8), pr(27, 13 + 1.8, 8.2 - 1.8)]
    d = ImageDraw.Draw(im)
    bell = [pr(27, 13 - 2.0, 8.2), pr(31.5, 13 - 4.0, 8.2), pr(31.5, 13 + 1.0, 8.2 - 4.5), pr(27, 13 + 1.2, 8.2 - 1.8)]
    cyl(im, (27, 13, 8.2), "x", 4.4, 3.4, (150, 96, 60), cap=(40, 30, 26))
    # boil-off venting from the top of the tank
    C.wisp(im, pr(10, 10, 13.8), 5, (246, 248, 250), 210)
    return im


# ---------------------------------------------------------------- smalllauncher: small black rocket on a seaside pad
def icon_smalllauncher():
    im = A.layer()
    sea_tile(im)
    U.terrain(im, lambda x, y: 2.0 if x + y * 0.6 > 9 else 0.0, 0, 32.2, 0, 32.2, 32,
              lambda x, y, z: (120, 142, 90) if (x + y) % 7 > 1 else (132, 150, 96), skirt=lambda z: (110, 92, 70), base_z=0.5)
    box3(im, 12, 8, 2.0, 14, 14, 1.8, CONC, 0.8)
    p = pr(19, 14, 3.8)
    body_rocket(im, p[0], p[1], 32, 2.3, [(0, 0.82, (36, 36, 40), 0.3), (0.82, 1.0, (214, 214, 210), 0.5)], nose=0.16)
    box3(im, 2, 18, 2.0, 9, 9, 5.0, (226, 226, 222), 0.8)
    windows(im, 3.2, 18, 3.6, 2, 3.6, 2.2, 2.4, c=(70, 120, 170))
    return im


# ---------------------------------------------------------------- reusable: first stage touching down on the landing pad
def icon_reusable():
    im = A.layer()
    A.floor(im)
    box3(im, 5, 5, 0, 22, 22, 1.2, CONC, 0.9)
    d = ImageDraw.Draw(im)
    c = pr(16, 16, 1.25)
    d.ellipse([(c[0] - 12) * S, (c[1] - 6) * S, (c[0] + 12) * S, (c[1] + 6) * S], outline=(236, 236, 230, 255), width=int(0.8 * S))
    for a, b in (((10, 16), (22, 16)), ((16, 10), (16, 22))):
        d.line(A.P([pr(*a, 1.25), pr(*b, 1.25)]), fill=(236, 236, 230, 255), width=int(0.8 * S))
    by = c[1] - 7
    flame(im, c[0], by + 2.4, 7.5, 2.0)
    legs(im, c[0], by, 2.6, 4.0, 2.6)
    body_rocket(im, c[0], by, 30, 2.6, [(0, 0.3, SOOT, 0.3), (0.3, 0.55, (150, 146, 140), 0.45), (0.55, 1.0, WHITE, 0.55)], nose=0.05, bell=True)
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):  # grid fins at the top
        a = (c[0] + sx * 2.6, by - 27)
        d.rectangle([min(a[0], a[0] + sx * 2.2) * S, (a[1] - 1) * S, max(a[0], a[0] + sx * 2.2) * S, (a[1] + 1) * S], fill=(80, 80, 86, 255), outline=INK + (255,), width=max(2, S // 3))
    return im


# ---------------------------------------------------------------- rapidreuse: sooty booster back on the drone ship, ready again
def icon_rapidreuse():
    im = A.layer()
    sea_tile(im)
    box3(im, 4, 7, 0, 24, 18, 2.6, (90, 96, 104), 0.9)
    d = ImageDraw.Draw(im)
    c = pr(16, 16, 2.65)
    d.ellipse([(c[0] - 9) * S, (c[1] - 4.5) * S, (c[0] + 9) * S, (c[1] + 4.5) * S], outline=(236, 214, 80, 255), width=int(0.7 * S))
    for x, y in ((5, 8), (26, 8), (5, 23), (26, 23)):  # thruster pods at the corners
        box3(im, x - 1, y - 1, 2.6, 2.4, 2.4, 1.6, (236, 236, 232), 0.5)
    by = c[1]
    legs(im, c[0], by - 1.5, 2.6, 4.0, 1.5)
    body_rocket(im, c[0], by - 1.5, 30, 2.6, [(0, 0.55, SOOT, 0.3), (0.55, 0.8, (128, 124, 118), 0.4), (0.8, 1.0, (190, 188, 182), 0.5)], nose=0.05)
    # crane arm reaching to lift it
    lattice(im, 26, 20, 27.5, 21.5, 2.6, 26, 5, (236, 182, 44))
    a, b = pr(26.7, 20.7, 26), (c[0] + 3, by - 26)
    d = ImageDraw.Draw(im)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(1.3 * S))
    d.line(A.P([a, b]), fill=(236, 182, 44, 255), width=int(0.6 * S))
    return im


# ---------------------------------------------------------------- superheavy: stainless steel giant beside the catch tower
def icon_superheavy():
    im = A.layer()
    A.floor(im)
    box3(im, 4, 4, 0, 24, 24, 3.0, CONC, 0.9)
    lattice(im, 5, 17, 10, 22, 3.0, 41, 8, (60, 62, 68))
    p = pr(18, 13, 4.0)
    for z in (31, 34):  # catch arms
        a, b = pr(10, 18, z), (p[0] - 1, p[1] - z + 4)
        d = ImageDraw.Draw(im)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.4 * S))
        d.line(A.P([a, b]), fill=(90, 92, 100, 255), width=int(0.7 * S))
    body_rocket(im, p[0], p[1], 41, 4.0, [(0, 0.55, STEEL_SS, 0.7), (0.55, 0.57, (130, 134, 140), 0.4), (0.57, 1.0, (210, 214, 218), 0.75)],
                nose=0.12, rings=[(0.2, (150, 154, 160)), (0.4, (150, 154, 160)), (0.75, (150, 154, 160))], bell=False)
    d = ImageDraw.Draw(im)
    for sx in (-1, 1):  # forward flaps of the ship
        a = (p[0] + sx * 4.0, p[1] - 41 * 0.86)
        d.polygon(A.P([a, (a[0] + sx * 2.4, a[1] + 1), (a[0] + sx * 2.4, a[1] + 4), (a[0], a[1] + 4)]), fill=(150, 154, 160, 255), outline=INK + (255,), width=max(2, S // 3))
    return im


# ---------------------------------------------------------------- refuel: tanker and ship joined tail to tail above the Earth
def icon_refuel():
    im = A.layer()
    earth_limb(im)
    o = (32, 28)
    ss = [(0, 1, STEEL_SS, 0.7)]
    for x0, ln in ((-20, 18), (2, 18)):
        cyl(im, (x0, 0, 0), "x", ln, 3.4, STEEL_SS, rings=[(0.3, (150, 154, 160), 0.4), (0.6, (150, 154, 160), 0.4)], cap=(214, 218, 222), o=o)
    d = ImageDraw.Draw(im)
    a, b = pr(-2, 0, 0, o), pr(2, 0, 0, o)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(2.4 * S))
    d.line(A.P([a, b]), fill=(236, 182, 44, 255), width=int(1.2 * S))
    for x in (-22, 20.5):  # pointed ends
        sgn = -1 if x < 0 else 1
        tip = pr(x + sgn * 3.4, 0, 0, o)
        base0, base1 = pr(x + (0 if sgn > 0 else 2), 0, 3.4, o), pr(x + (0 if sgn > 0 else 2), 0, -3.4, o)
        d.polygon(A.P([base0, tip, base1]), fill=(206, 210, 216, 255), outline=INK + (255,), width=max(2, S // 2))
    C.wisp(im, pr(0, 0, 2, o), 3, (236, 244, 250), 120)
    return im


# ---------------------------------------------------------------- nuclear: reactor, shadow shield and long hydrogen tanks heading for Mars
def icon_nuclear():
    im = A.layer()
    stars(im, 16, 7)
    planet(im, 50, 13, 6, "mars", spin=(0.8, 0.2), seed=4)
    o = (29, 38)
    cyl(im, (-19, 0, 0), "x", 16, 4.6, (236, 236, 232), rings=[(0.33, (176, 180, 186), 0.4), (0.66, (176, 180, 186), 0.4)], cap=(220, 222, 226), o=o)
    box3(im, -3, -0.8, -0.8, 11, 1.6, 1.6, (150, 156, 164), 0.5, o=o)  # truss to keep the crew far from the reactor
    cyl(im, (8, 0, 0), "x", 1.2, 3.8, (60, 62, 70), o=o)  # shadow shield
    cyl(im, (9.2, 0, 0), "x", 4.6, 2.6, (196, 160, 70), rings=[(0.5, (140, 110, 40), 0.4)], o=o)  # reactor
    cyl(im, (13.8, 0, 0), "x", 5.0, 3.2, (110, 76, 52), cap=(40, 30, 26), o=o)  # nozzle
    return im


# ---------------------------------------------------------------- electric: ion engines on a solar-electric tug
def icon_electric():
    im = A.layer()
    stars(im, 16, 9)
    o = (26, 30)
    for y in (12, 8):
        panel_xz(im, -9, 9, y, -2.6, 2.6, o)
    box3(im, -4, -5, -3, 8, 10, 6, (214, 170, 70), 0.8, o=o)  # body in gold foil
    for y in (-8, -12):
        panel_xz(im, -9, 9, y, -2.6, 2.6, o)
    for k, z in enumerate((-1.6, 1.6)):  # two thrusters with their blue beams
        e = pr(4, 0, z, o)
        cyl(im, (4, 0, z), "x", 1.4, 1.2, (90, 96, 104), cap=(60, 80, 140), o=o)
        lay = A.layer()
        dl = ImageDraw.Draw(lay)
        tip = pr(18, 0, z * 1.5, o)
        dl.polygon(A.P([(e[0] + 1.2, e[1] - 1.0), tip, (e[0] + 1.2, e[1] + 1.0)]), fill=(120, 180, 255, 150))
        im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.5 * S)))
    return im


# ---------------------------------------------------------------- fullflow: a big methane engine firing on its test stand
def icon_fullflow():
    im = A.layer()
    A.floor(im)
    box3(im, 4, 14, 0, 24, 14, 22, CONC, 0.9)
    d = ImageDraw.Draw(im)
    a, b = pr(12, 14, 4), pr(22, 14, 4)
    d.polygon(A.P([a, b, (b[0], b[1] - 18), (a[0], a[1] - 18)]), fill=(60, 60, 64, 255))
    e = pr(17, 10, 14)
    # engine: turbopumps, chamber and the bell pointing down
    box3(im, 14, 10, 15, 6, 4, 4, (90, 96, 104), 0.6)
    for sx in (-1, 1):
        cyl(im, (17 + sx * 2.4, 9, 12), "z", 3.5, 1.1, (176, 182, 190))
    full, col = A.solid(e[0], e[1] + 6, 8, 2.2, [(0, 1.0), (0.6, 0.55), (0.8, 0.45), (1.0, 0.55)], [(0, 0.65, (176, 104, 60), 0.6), (0.65, 1, (150, 156, 164), 0.5)])
    A.place(im, full, col, 0.8)
    flame(im, e[0], e[1] + 6.4, 13, 2.6)
    return im


# ---------------------------------------------------------------- massdriver: electromagnetic launch track on the Moon
def icon_massdriver():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    rail0, rail1 = (2, 6, gz + 0.6), (30, 22, gz + 14)
    for t in np.linspace(0, 1, 8):  # supports
        x, y, z = (rail0[i] + (rail1[i] - rail0[i]) * t for i in range(3))
        if z > gz + 1.2:
            cyl(im, (x, y, gz), "z", z - gz - 0.4, 0.35, (150, 156, 164))
    d = ImageDraw.Draw(im)
    a, b = pr(*rail0), pr(*rail1)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(2.2 * S))
    d.line(A.P([a, b]), fill=(180, 186, 194, 255), width=int(1.2 * S))
    for t in np.linspace(0.05, 0.95, 9):  # magnetic coil rings
        p = A.lerp(a, b, t)
        d.ellipse([(p[0] - 1.4) * S, (p[1] - 1.9) * S, (p[0] + 1.4) * S, (p[1] + 1.9) * S], outline=(196, 120, 60, 255), width=int(0.5 * S))
    p = A.lerp(a, b, 0.8)  # cargo bucket leaving the track
    box3(im, 25, 18, gz + 13, 3, 2, 2.4, (214, 170, 70), 0.6)
    small_earth(im, 11, 13, 5.5)
    return im


# ---------------------------------------------------------------- cruiser: the interplanetary ship between Earth and Mars
def icon_cruiser():
    im = A.layer()
    stars(im, 18, 11, (2, 2, 62, 60))
    small_earth(im, 9, 52, 5.5)
    planet(im, 54, 12, 5, "mars", spin=(0.8, 0.2), seed=4)
    o = (30, 33)
    cyl(im, (-16, 0, 0), "x", 11, 3.8, (236, 236, 232), rings=[(0.5, (176, 180, 186), 0.4)], cap=(220, 222, 226), o=o)
    for k, y in enumerate((3.0, -3.0)):
        cyl(im, (-5, y, 0), "x", 13, 2.5, (196, 200, 206), o=o)
    panel_xz(im, -14, -6, 9, -2.4, 2.4, o, 3)
    cyl(im, (8, 0, 0), "x", 4, 3.8, (90, 96, 104), o=o)
    cyl(im, (12, 0, 0), "x", 3.6, 3.0, (110, 76, 52), cap=(40, 30, 26), o=o)
    return im


# ---------------------------------------------------------------- helpers for the later columns
GOLD = (214, 170, 70)
MARS = (186, 100, 62)


def capsule(im, cx, by, h, half, body=(226, 226, 222), shield=(60, 50, 44)):
    """Crew capsule seen upright: dark heat shield below, cone body, docking ring on top."""
    full, col = A.solid(cx, by, h, half, [(0, 0.96), (0.08, 1.0), (0.82, 0.5), (0.9, 0.42), (1.0, 0.4)],
                        [(0, 0.08, shield, 0.3), (0.08, 0.82, body, 0.55), (0.82, 1.0, (150, 156, 164), 0.45)])
    A.place(im, full, col, 0.8)
    d = ImageDraw.Draw(im)
    for sx in (-0.38, 0.12):  # windows
        c = (cx + sx * half, by - h * 0.5)
        d.ellipse([(c[0] - 0.7) * S, (c[1] - 0.9) * S, (c[0] + 0.7) * S, (c[1] + 0.9) * S], fill=(40, 60, 90, 255), outline=INK + (255,), width=max(2, S // 4))


def astronaut(im, cx, cy, s=1.0, suit=(236, 236, 232), lean=0.0):
    """Small figure in a spacesuit: backpack, body, limbs and a gold visor."""
    d = ImageDraw.Draw(im)
    def ln(a, b, w):
        a, b = (cx + a[0] * s, cy + a[1] * s), (cx + b[0] * s, cy + b[1] * s)
        d.line(A.P([a, b]), fill=INK + (255,), width=int((w + 0.9) * S * s))
        d.line(A.P([a, b]), fill=suit + (255,), width=int(w * S * s))
    d.rounded_rectangle([(cx - 2.2 * s) * S, (cy - 4.6 * s) * S, (cx + 1.2 * s) * S, (cy + 0.6 * s) * S], radius=int(S * s), fill=(200, 200, 196, 255), outline=INK + (255,), width=int(0.6 * S * s))
    ln((-0.6, -1), (-1.4 + lean, 5.2), 1.5)
    ln((0.6, -1), (1.6 + lean, 5.0), 1.5)
    ln((-0.4, -3.6), (-3.2, -0.6), 1.2)
    ln((0.6, -3.6), (3.2, -1.6 - lean), 1.2)
    d.rounded_rectangle([(cx - 1.6 * s) * S, (cy - 4.4 * s) * S, (cx + 1.8 * s) * S, (cy + 0.4 * s) * S], radius=int(S * s), fill=suit + (255,), outline=INK + (255,), width=int(0.6 * S * s))
    d.ellipse([(cx - 1.6 * s) * S, (cy - 8.0 * s) * S, (cx + 1.8 * s) * S, (cy - 4.4 * s) * S], fill=suit + (255,), outline=INK + (255,), width=int(0.6 * S * s))
    d.ellipse([(cx - 0.6 * s) * S, (cy - 7.2 * s) * S, (cx + 1.5 * s) * S, (cy - 5.2 * s) * S], fill=(214, 160, 50, 255))


def satellite(im, o, bus=GOLD, span=8.0, size=3.0, dish_r=0.0, panel_h=2.2):
    """Generic satellite floating at origin o: box body with two solar wings along y."""
    # wings run along y: draw them as panels in the y-z plane is not visible, so use x-z panels side by side along y
    wing = lambda y0, y1: panel_xz(im, -span / 2, span / 2, y0, -panel_h, panel_h, o, 4)
    wing(size / 2 + 2.2, None)
    box3(im, -size / 2, -size / 2, -size / 2, size, size, size, bus, 0.7, o=o)
    if dish_r:
        d = ImageDraw.Draw(im)
        c = pr(0, -size / 2 - 0.3, size / 2 + dish_r * 0.5, o)
        d.ellipse([(c[0] - dish_r) * S, (c[1] - dish_r * 0.5) * S, (c[0] + dish_r) * S, (c[1] + dish_r * 0.5) * S], fill=(236, 238, 240, 255), outline=INK + (255,), width=max(2, S // 2))
    wing(-size / 2 - 2.2, None)


def dish(im, c, nrm, r, o=U.O, legs=True):
    nrm = np.asarray(nrm, float); nrm /= np.linalg.norm(nrm)
    u = np.cross(nrm, [0, 0, 1.0]); u /= np.linalg.norm(u)
    v = np.cross(nrm, u)
    c = np.asarray(c, float)
    rim = [pr(*(c + r * (u * math.cos(a) + v * math.sin(a))), o) for a in np.linspace(0, 2 * math.pi, 48)]
    inner = [pr(*(c - nrm * r * 0.25 + r * 0.6 * (u * math.cos(a) + v * math.sin(a))), o) for a in np.linspace(0, 2 * math.pi, 48)]
    lay = A.layer()
    m = A.mask_of(lambda d: d.polygon(A.P(rim), fill=255))
    lay.alpha_composite(A.vgrad(m, (236, 238, 242), (176, 182, 190)))
    m2 = A.mask_of(lambda d: d.polygon(A.P(inner), fill=255))
    lay.alpha_composite(A.vgrad(m2, (200, 204, 210), (156, 162, 170)))
    U.outlined(im, lay, 0.8)
    feed = pr(*(c + nrm * r * 0.7), o)
    d = ImageDraw.Draw(im)
    if legs:
        for a in (0, 2.1, 4.2):
            p = pr(*(c + r * 0.9 * (u * math.cos(a) + v * math.sin(a))), o)
            d.line(A.P([p, feed]), fill=(90, 96, 104, 255), width=max(2, S // 3))
    dot(d, feed, 0.7, (90, 96, 104), INK[:3])
    return feed


def ball(im, cx, cy, r, color, spec=0.5):
    """Sphere (tank, dome lamp) in screen units."""
    prof = [(t, math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))) for t in np.linspace(0, 1, 15)]
    prof[0] = (0, 0.25)
    full, col = A.solid(cx, cy + r * (1 - 0.0), 2 * r, r, prof, [(0, 1, color, spec)])
    A.place(im, full, col, 0.7)


def mars_ground(x, y):
    z = 3.0 + 0.6 * math.sin(x * 0.4) * math.cos(y * 0.3) + 0.3 * math.sin(x * 1.3 + y)
    for cx, cy, r in ((25, 25, 3.5),):
        dd = math.hypot(x - cx, y - cy) / r
        if dd < 1:
            z -= 1.4 * (1 - dd * dd)
    return z


def mars_color(x, y, z):
    n = (U.hashn(round(x * 2), round(y * 2)) - 0.5) * 22
    return tuple(int(v + n) for v in (190, 104, 64))


def mars_tile(im):
    U.terrain(im, mars_ground, 0, 32.2, 0, 32.2, 44, mars_color, skirt=lambda z: (130, 70, 44), edge=0.9)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(6)
    for _ in range(12):  # rocks
        x, y = rng.uniform(2, 30), rng.uniform(2, 30)
        dot(d, pr(x, y, mars_ground(x, y) + 0.3), rng.uniform(0.4, 0.8), (120, 70, 50), INK[:3])


def limb(im, kind, cy=123, r=76):
    """Curve of a planet at the bottom of the icon."""
    if kind == "earth":
        return earth_limb(im)
    halo = {"mars": (230, 170, 140), "venus": (250, 220, 160), "titan": (240, 180, 100)}.get(kind)
    if halo:
        m = A.mask_of(lambda d: d.ellipse([(32 - r - 1.4) * S, (cy - r - 1.4) * S, (32 + r + 1.4) * S, (cy + r + 1.4) * S], fill=150))
        hl = Image.new("RGBA", (A.W, A.W), halo + (0,))
        hl.putalpha(m.filter(ImageFilter.GaussianBlur(0.6 * S)))
        im.alpha_composite(hl)
    planet(im, 32, cy, r, kind, light=(-0.5, -0.8, 0.35), spin=(1.2, -0.5), seed=4, outline=0.8)


def sun(im, cx, cy, r):
    m = A.mask_of(lambda d: d.ellipse([(cx - r * 1.8) * S, (cy - r * 1.8) * S, (cx + r * 1.8) * S, (cy + r * 1.8) * S], fill=120))
    g = Image.new("RGBA", (A.W, A.W), (255, 200, 90, 0))
    g.putalpha(m.filter(ImageFilter.GaussianBlur(r * S * 0.6)))
    im.alpha_composite(g)
    d = ImageDraw.Draw(im)
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=(255, 236, 160, 255), outline=(240, 170, 60, 255), width=int(0.5 * S))


def asteroid(im, cx, cy, r, seed=3, light=(-0.7, -0.5, 0.5)):
    """Lumpy rock: a lit sphere with a noisy outline and a few craters."""
    tmp = A.layer()
    planet(tmp, cx, cy, r * 1.15, "asteroid", light=light, spin=(0.3, 0.4), seed=seed, outline=0)
    ang = np.arctan2(*(np.mgrid[0:A.W, 0:A.W][::-1] / S - np.array([cx, cy])[:, None, None])[::-1])
    yy, xx = np.mgrid[0:A.W, 0:A.W] / S
    ang = np.arctan2(yy - cy, xx - cx)
    rad = r * (1 + 0.16 * np.sin(3 * ang + seed) + 0.1 * np.sin(5 * ang + 2 * seed) + 0.06 * np.sin(9 * ang))
    m = (np.hypot(xx - cx, yy - cy) < rad).astype(np.uint8) * 255
    tmp.putalpha(Image.fromarray(np.minimum(np.array(tmp.getchannel("A")), m)))
    im.alpha_composite(A.outline(tmp.getchannel("A"), 0.7))
    im.alpha_composite(tmp)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    for _ in range(4):
        a, f, cr = rng.uniform(0, 6.28), rng.uniform(0.1, 0.6), rng.uniform(0.6, 1.3) * r / 6
        p = (cx + math.cos(a) * f * r, cy + math.sin(a) * f * r * 0.8)
        d.ellipse([(p[0] - cr) * S, (p[1] - cr * 0.7) * S, (p[0] + cr) * S, (p[1] + cr * 0.7) * S], fill=(90, 82, 74, 200), outline=(170, 160, 146, 200), width=max(2, S // 4))


def dashed(im, pts, c=(240, 220, 90), w=0.5, on=2, off=2):
    d = ImageDraw.Draw(im)
    for k in range(0, len(pts) - 1, on + off):
        seg = pts[k:k + on + 1]
        if len(seg) > 1:
            d.line(A.P(seg), fill=c + (255,), width=max(2, int(w * S)))


# ---------------------------------------------------------------- column 1: life and safety
def icon_crewed():
    im = A.layer()
    earth_limb(im)
    o = (36, 30)
    panel_xz(im, 0, 9, 7.5, -2.4, 2.4, o, 3)
    cyl(im, (0, 0, 0), "x", 11, 4.6, (236, 236, 232), rings=[(0.5, (176, 180, 186), 0.5)], cap=(210, 214, 220), o=o)
    panel_xz(im, 0, 9, -7.5, -2.4, 2.4, o, 3)
    c = pr(0, 0, 0, o)
    cap = A.layer()
    capsule(cap, 32, 46, 14, 6.4)
    im.alpha_composite(cap.rotate(90, resample=Image.BICUBIC, center=(32 * S, 46 * S), translate=((c[0] - 32) * S, (c[1] - 46) * S)))
    return im


def icon_longstay():
    im = A.layer()
    earth_limb(im)
    o = (36, 22)
    cyl(im, (-14, 0, 0), "x", 26, 3.8, (236, 236, 232), rings=[(t, (176, 180, 186), 0.4) for t in (0.25, 0.5, 0.75)], cap=(214, 218, 222), o=o)
    d = ImageDraw.Draw(im)
    for k in range(3):
        dot(d, pr(-9 + k * 7, -3.5, 1.6, o), 0.6, (60, 90, 140), INK[:3])
    hand = pr(-4, -3.8, -2.6, o)
    astronaut(im, 22, 40, 1.15, lean=0.6)
    d = ImageDraw.Draw(im)
    pts = [(25.6, 38.2), (28, 36.5), (hand[0], hand[1])]
    d.line(A.P(pts), fill=(236, 220, 140, 255), width=max(2, S // 3), joint="curve")
    return im


def icon_commercialcrew():
    im = A.layer()
    A.floor(im)
    box3(im, 5, 5, 0, 22, 22, 2.5, CONC, 0.9)
    lattice(im, 6, 17, 11, 22, 2.5, 38, 8, (60, 62, 68))
    p = pr(18, 13, 3.4)
    body_rocket(im, p[0], p[1], 31, 2.9, [(0, 0.08, (40, 40, 44), 0.4), (0.08, 1.0, WHITE, 0.55)], nose=0.0001, bell=True)
    capsule(im, p[0], p[1] - 31, 6.5, 3.3, body=(236, 236, 232), shield=(40, 40, 44))
    a, b = pr(11, 18, 35), (p[0] - 3, p[1] - 34.5)
    d = ImageDraw.Draw(im)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(1.8 * S))
    d.line(A.P([a, b]), fill=(226, 226, 222, 255), width=int(1.0 * S))
    return im


def icon_lifesupport():
    im = A.layer()
    A.floor_dark(im)
    # water recovery tanks, air revitalisation rack and a plant chamber
    for k, (x, y) in enumerate(((4, 20), (9.5, 20))):
        cyl(im, (x + 2, y + 2, 0), "z", 13, 2.4, (90, 150, 210), rings=[(0.33, (60, 110, 170), 0.4), (0.66, (60, 110, 170), 0.4)], cap=(120, 176, 226))
    box3(im, 15, 17, 0, 12, 8, 14, (196, 200, 206), 0.9)
    d = ImageDraw.Draw(im)
    for k in range(3):
        a, b = pr(16 + k * 3.6, 17, 11), pr(18.4 + k * 3.6, 17, 11)
        d.polygon(A.P([a, b, (b[0], b[1] + 8), (a[0], a[1] + 8)]), fill=(60, 66, 76, 255), outline=INK + (255,), width=max(2, S // 4))
        dot(d, A.lerp(a, b, 0.5), 0.5, A.CYAN)
    box3(im, 6, 4, 0, 14, 8, 6, (214, 218, 224), 0.9)
    tray = [pr(7, 5, 6.05), pr(19, 5, 6.05), pr(19, 11, 6.05), pr(7, 11, 6.05)]
    d = ImageDraw.Draw(im)
    d.polygon(A.P(tray), fill=(70, 60, 50, 255))
    rng = np.random.default_rng(4)
    for _ in range(26):
        x, y = rng.uniform(7.6, 18.4), rng.uniform(5.6, 10.4)
        p = pr(x, y, 6.1)
        dot(d, (p[0], p[1] - 0.8), rng.uniform(0.6, 1.0), (90, 160, 70), (40, 90, 30))
    pipe3(im, [(8.5, 22, 11), (8.5, 22, 15), (21, 21, 15), (21, 21, 14)], (150, 156, 164), 0.9)
    return im


def icon_radiation():
    im = A.layer()
    stars(im, 14, 5)
    sun(im, 9, 10, 4.5)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(8)
    for _ in range(9):  # solar particles stopped by the shield
        y = rng.uniform(16, 42)
        x0 = rng.uniform(12, 18)
        d.line(A.P([(x0, y - 4), (x0 + 6, y)]), fill=(250, 220, 120, 230), width=max(2, int(0.35 * S)))
    o = (36, 32)
    cyl(im, (-12, 0, 0), "x", 22, 5.2, (90, 96, 108), rings=[(0.2, (60, 64, 72), 0.6), (0.8, (60, 64, 72), 0.6)], cap=(70, 120, 180), o=o)
    d = ImageDraw.Draw(im)
    c = pr(-12, 0, 0, o)
    for f, col in ((0.78, (60, 64, 72)), (0.56, (236, 236, 232)), (0.34, (120, 170, 220))):  # shielding layers seen in the end
        r = 5.2 * f
        ring = [pr(-12, r * math.cos(a), r * math.sin(a), o) for a in np.linspace(0, 2 * math.pi, 40)]
        d.polygon(A.P(ring), fill=col + (255,), outline=INK + (255,), width=max(2, S // 4))
    return im


def icon_surface():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    for wx in (8, 18):
        cyl(im, (wx, 15.2, gz + 1.4), "y", 1.2, 1.5, (60, 60, 64))
    box3(im, 6, 6, gz + 1.8, 15, 9, 5.8, (232, 232, 228), 0.9)
    d = ImageDraw.Draw(im)
    a, b = pr(21, 8, gz + 6.4), pr(21, 13, gz + 6.4)
    d.polygon(A.P([a, b, (b[0], b[1] + 2.6), (a[0], a[1] + 2.6)]), fill=(40, 60, 90, 255), outline=INK + (255,), width=max(2, S // 4))
    for wx in (8, 18):
        cyl(im, (wx, 4.6, gz + 1.4), "y", 1.4, 1.6, (60, 60, 64), cap=(46, 46, 48))
    box3(im, 8, 8, gz + 7.6, 4, 3, 1.0, GOLD, 0.5)
    p = pr(25, 6, gz)
    astronaut(im, p[0], p[1] - 5.4, 1.0)
    return im


def icon_deepmission():
    im = A.layer()
    stars(im, 18, 13, (2, 2, 62, 62))
    small_earth(im, 54, 50, 3.4)
    planet(im, 9, 10, 4.5, "mars", spin=(0.8, 0.2), seed=4)
    o = (30, 32)
    cyl(im, (-12, 0, 0), "x", 9, 5.4, (226, 220, 206), rings=[(t, (190, 180, 160), 0.6) for t in (0.2, 0.4, 0.6, 0.8)], cap=(210, 204, 190), o=o)
    cyl(im, (-3, 0, 0), "x", 9, 2.6, (236, 236, 232), o=o)
    panel_xz(im, -2, 5, 6, -2, 2, o, 3)
    cyl(im, (6, 0, 0), "x", 3.6, 3.0, (90, 96, 104), o=o)
    cyl(im, (9.6, 0, 0), "x", 3.0, 2.4, (110, 76, 52), cap=(40, 30, 26), o=o)
    return im


def icon_marslanding():
    im = A.layer()
    mars_tile(im)
    p = pr(16, 14, 3.4)
    legs(im, p[0], p[1], 4.0, 4.2, 1.2)
    body_rocket(im, p[0], p[1], 36, 4.0, [(0, 1.0, STEEL_SS, 0.7)], nose=0.14, rings=[(0.3, (150, 154, 160)), (0.6, (150, 154, 160))], bell=False)
    d = ImageDraw.Draw(im)
    a = (p[0] - 4, p[1] - 14)
    d.line(A.P([a, (a[0] - 3.4, p[1] + 1)]), fill=INK + (255,), width=int(1.4 * S))
    d.line(A.P([a, (a[0] - 3.4, p[1] + 1)]), fill=(150, 154, 160, 255), width=int(0.6 * S))
    q = pr(25, 6, 3.6)
    astronaut(im, q[0], q[1] - 5.2, 0.95)
    return im


def icon_gravity():
    im = A.layer()
    earth_limb(im)
    o = (32, 26)
    R = 13
    ring = [(R * math.cos(a), 0, R * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 73)]
    d = ImageDraw.Draw(im)
    for a in np.linspace(0, 2 * math.pi, 7)[:-1]:  # spokes
        d.line(A.P([pr(0, 0, 0, o), pr(R * math.cos(a), 0, R * math.sin(a), o)]), fill=INK + (255,), width=int(1.3 * S))
        d.line(A.P([pr(0, 0, 0, o), pr(R * math.cos(a), 0, R * math.sin(a), o)]), fill=(196, 200, 206, 255), width=int(0.6 * S))
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    for (x0, _, z0), (x1, _, z1) in zip(ring, ring[1:]):
        a = math.atan2(z0, x0)
        c = shade((226, 226, 222), (math.cos(a), -0.8, math.sin(a)))
        dl.line(A.P([pr(x0, 0, z0, o), pr(x1, 0, z1, o)]), fill=c + (255,), width=int(3.4 * S))
    U.outlined(im, lay, 0.8)
    d = ImageDraw.Draw(im)
    for a in np.linspace(0, 2 * math.pi, 13)[:-1]:
        dot(d, pr(R * math.cos(a), -1.0, R * math.sin(a), o), 0.4, (60, 90, 140))
    cyl(im, (0, -3, 0), "y", 6, 2.0, (196, 200, 206), cap=(170, 176, 184), o=o)
    return im


def icon_torpor():
    im = A.layer()
    A.floor_dark(im)
    for k, y in enumerate((20, 13, 6)):
        cyl(im, (5, y, 2.6), "x", 20, 2.6, (214, 218, 224), cap=(190, 196, 204))
        d = ImageDraw.Draw(im)
        win = [pr(8, y - 1.2, 4.8), pr(22, y - 1.2, 4.8), pr(22, y - 2.2, 3.6), pr(8, y - 2.2, 3.6)]
        d.polygon(A.P(win), fill=(70, 120, 150, 255), outline=INK + (255,), width=max(2, S // 4))
        hd = pr(10, y - 1.6, 4.4)
        dot(d, hd, 0.7, (200, 170, 150))
        dot(d, pr(25.2, y, 2.6), 0.4, A.CYAN if k != 1 else (120, 230, 120))
    return im


def icon_biosphere():
    im = A.layer()
    mars_tile(im)
    gz = 3.4
    cx, cy, R = 15, 15, 11
    U.terrain(im, lambda x, y: gz + 0.2, cx - R, cx + R, cy - R, cy + R, 6, lambda x, y, z: (110, 150, 70), base_z=gz)
    for tx, ty in ((10, 18), (16, 11), (19, 19), (12, 12)):
        h = 4 + (tx % 3)
        a, b = pr(tx, ty, gz), pr(tx, ty, gz + h)
        d = ImageDraw.Draw(im)
        d.line(A.P([a, b]), fill=(110, 80, 50, 255), width=int(0.6 * S))
        ball(im, b[0], b[1] - 2.8, 2.8, (80, 140, 60), 0.2)
    lay = A.layer()
    U.terrain(lay, lambda x, y: gz + 0.62 * math.sqrt(max(0.0, R * R - (x - cx) ** 2 - (y - cy) ** 2)) * 1.25,
              cx - R, cx + R, cy - R, cy + R, 30, lambda x, y, z: (180, 214, 236), edge=0.7, base_z=gz + 0.05)
    lay.putalpha(lay.getchannel("A").point(lambda a: int(a * 0.42)))
    im.alpha_composite(lay)
    d = ImageDraw.Draw(im)
    for a in np.linspace(0.2, math.pi - 0.2, 5):  # dome ribs
        pts = [pr(cx + R * math.cos(a) * math.cos(t), cy + R * math.sin(a) * math.cos(t) * -1 + 0, gz + R * 0.775 * math.sin(t)) for t in np.linspace(0, math.pi / 2, 12)]
    c = pr(cx, cy, gz)
    d.ellipse([(c[0] - R * 1.27) * S, (c[1] - R * 0.64) * S, (c[0] + R * 1.27) * S, (c[1] + R * 0.64) * S], outline=(200, 206, 214, 255), width=int(0.5 * S))
    return im


# ---------------------------------------------------------------- column 2: resources and energy
def icon_tracking():
    im = A.layer()
    A.floor(im)
    box3(im, 2, 20, 0, 10, 9, 6, (220, 222, 224), 0.9)
    windows(im, 3.2, 20, 4.6, 3, 3.0, 1.8, 2.0, c=(70, 120, 170))
    for (x, y, r, nrm) in ((22, 22, 5.0, (-0.5, 0.3, 0.8)), (12, 8, 4.0, (-0.3, 0.6, 0.75)), (25, 8, 3.4, (0.3, 0.2, 0.9))):
        A.ellipse_shadow(im, *pr(x, y, 0), r, r * 0.4)
        cyl(im, (x, y, 0), "z", r * 0.9 + 2, 0.9, (150, 156, 164))
        dish(im, (x, y, r * 0.9 + 3.4), nrm, r)
    return im


def icon_powerarrays():
    im = A.layer()
    earth_limb(im)
    o = (32, 28)
    for y in (16, 11.5, 7):
        panel_xz(im, -10, 10, y, -3.4, 3.4, o, 6)
    box3(im, -2.6, -2.6, -2.6, 5.2, 5.2, 5.2, GOLD, 0.7, o=o)
    for y in (-7, -11.5, -16):
        panel_xz(im, -10, 10, y, -3.4, 3.4, o, 6)
    return im


def icon_rtg():
    im = A.layer()
    stars(im, 16, 21)
    planet(im, 12, 12, 7, "jupiter", spin=(0.2, 0.2), seed=3)
    o = (34, 32)
    box3(im, -3, -3, -3, 6, 6, 6, GOLD, 0.7, o=o)
    dish(im, (0, -1, 6.5), (0, -0.25, 1), 7.5, o)
    box3(im, 3, -0.4, -0.4, 6, 0.8, 0.8, (90, 96, 104), 0.5, o=o)
    cyl(im, (9, 0, 0), "x", 6, 1.5, (50, 50, 54), rings=[(t, (90, 90, 96), 0.4) for t in (0.2, 0.4, 0.6, 0.8)], cap=(60, 60, 64), o=o)
    d = ImageDraw.Draw(im)
    for t in (0.2, 0.5, 0.8):  # cooling fins
        x = 9 + 6 * t
        for a in (0.5, 2.6):
            p0 = pr(x, 1.5 * math.cos(a), 1.5 * math.sin(a), o)
            p1 = pr(x, 3.2 * math.cos(a), 3.2 * math.sin(a), o)
            d.line(A.P([p0, p1]), fill=INK + (255,), width=int(0.9 * S))
            d.line(A.P([p0, p1]), fill=(70, 70, 76, 255), width=int(0.45 * S))
    return im


def icon_prospecting():
    im = A.layer()
    stars(im, 14, 3)
    planet(im, 32, 124, 76, "moon", light=(-0.5, -0.8, 0.35), spin=(1.0, -0.4), seed=9, outline=0.8)
    o = (30, 24)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    a = pr(0, 0, 0, o)
    dl.polygon(A.P([a, (a[0] - 9, 52), (a[0] + 9, 56)]), fill=(140, 220, 255, 60))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6 * S)))
    satellite(im, o, GOLD, 10, 3.6, 0, 2.0)
    return im


def icon_solar():
    im = A.layer()
    earth_limb(im)
    o = (32, 27)
    panel_xz(im, -15, -2.6, 9, -2.4, 2.4, o, 8)
    panel_xz(im, 2.6, 15, 9, -2.4, 2.4, o, 8)
    box3(im, -2.6, -2.6, -2.6, 5.2, 5.2, 5.2, (226, 226, 222), 0.7, o=o)
    panel_xz(im, -15, -2.6, -9, -2.4, 2.4, o, 8)
    panel_xz(im, 2.6, 15, -9, -2.4, 2.4, o, 8)
    d = ImageDraw.Draw(im)
    for x in (-15, -2.6, 2.6, 15):  # roll-out booms
        for y in (9, -9):
            d.line(A.P([pr(x, y, 2.4, o), pr(x, y, -2.4, o)]), fill=(196, 200, 206, 255), width=max(2, S // 3))
    return im


def icon_lunarice():
    im = A.layer()
    gz = 3.0

    def ground(x, y):
        z = moon_ground(x, y)
        dd = math.hypot(x - 12, y - 18) / 9
        if dd < 1:
            z -= 4.5 * (1 - dd * dd)
        elif dd < 1.3:
            z += 1.6 * (1.3 - dd) / 0.3
        return z

    def color(x, y, z):
        dd = math.hypot(x - 12, y - 18) / 9
        if dd < 0.75:
            n = U.hashn(round(x * 2), round(y * 2))
            return (60, 64, 76) if n > 0.35 else (200, 214, 230)  # shadowed floor with frost
        return moon_color(x, y, z)
    U.terrain(im, ground, 0, 32.2, 0, 32.2, 52, color, skirt=lambda z: (104, 102, 100), edge=0.9)
    # drill rig and a water tank
    lattice(im, 20, 8, 22, 10, gz, gz + 12, 4, (236, 182, 44))
    box3(im, 18, 6, gz, 6, 6, 2.0, (214, 214, 210), 0.7)
    cyl(im, (27, 18, gz), "z", 6, 2.4, (90, 150, 210), rings=[(0.5, (60, 110, 170), 0.4)], cap=(120, 176, 226))
    pipe3(im, [(23, 9, gz + 1), (27, 15.6, gz + 1)], (150, 156, 164), 0.8)
    return im


def icon_fission():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    p = pr(15, 15, gz)
    cyl(im, (15, 15, gz), "z", 7, 1.8, (196, 160, 70), rings=[(0.5, (140, 110, 40), 0.4)])
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    for k, a in enumerate(np.linspace(0, 2 * math.pi, 9)[:-1]):  # umbrella of radiator panels
        b = a + 2 * math.pi / 8
        q = [pr(15 + 1.8 * math.cos(a), 15 + 1.8 * math.sin(a), gz + 13), pr(15 + 1.8 * math.cos(b), 15 + 1.8 * math.sin(b), gz + 13),
             pr(15 + 7 * math.cos(b), 15 + 7 * math.sin(b), gz + 7.4), pr(15 + 7 * math.cos(a), 15 + 7 * math.sin(a), gz + 7.4)]
        nm = (math.cos((a + b) / 2), math.sin((a + b) / 2), 0.8)
        c = shade((70, 74, 82), nm) + (255,)
        dl.polygon(A.P(q), fill=c, outline=(40, 42, 46, 255))
    U.outlined(im, lay, 0.7)
    cyl(im, (15, 15, gz + 13), "z", 2.4, 1.2, (150, 156, 164))
    pipe3(im, [(18, 12, gz + 0.3), (28, 4, gz + 0.3)], (60, 60, 64), 0.6)
    box3(im, 25, 2, gz, 5, 4, 2.6, (226, 226, 222), 0.6)
    return im


def icon_regolith():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    box3(im, 16, 16, gz, 12, 12, 8, (210, 212, 216), 0.9)
    d = ImageDraw.Draw(im)
    hopper = [pr(17, 16, gz + 8), pr(23, 16, gz + 8), pr(22, 16, gz + 11), pr(18, 16, gz + 11)]
    cyl(im, (26, 24, gz + 8), "z", 3, 1.6, (236, 236, 232), cap=(90, 150, 210))
    # excavator with a bucket drum and a pile of soil
    for wx in (6, 13):
        cyl(im, (wx, 9.6, gz + 1.0), "y", 1.0, 1.1, (60, 60, 64))
    box3(im, 4, 4, gz + 1.0, 11, 6, 3.0, (214, 170, 70), 0.8)
    cyl(im, (1.6, 3, gz + 2.4), "y", 7, 2.2, (150, 156, 164), rings=[(t, (90, 96, 104), 0.4) for t in (0.25, 0.5, 0.75)], cap=(120, 126, 134))
    for wx in (6, 13):
        cyl(im, (wx, 3.2, gz + 1.0), "y", 1.0, 1.1, (60, 60, 64), cap=(46, 46, 48))
    pipe3(im, [(15, 7, gz + 3.8), (19, 15.6, gz + 9.5)], (150, 156, 164), 1.0)
    return im


def icon_marsfuel():
    im = A.layer()
    mars_tile(im)
    gz = 3.4
    box3(im, 4, 18, gz, 10, 10, 6, (220, 222, 224), 0.9)
    for (x, y, c) in ((18, 25, (236, 236, 232)), (27, 25, (226, 230, 236))):
        p = pr(x, y, gz)
        cyl(im, (x, y, gz), "z", 1.5, 1.2, (150, 156, 164))
        ball(im, p[0], p[1] - 1.5 - 4.0, 4.0, c, 0.5)
    pipe3(im, [(14, 23, gz + 2), (15.5, 25, gz + 2)], (150, 156, 164), 0.8)
    for k in range(3):
        C.solar_rows(im, 2 + k * 0, 3, 14, 13, gz, 3) if k == 0 else None
    return im


def icon_asteroidsurvey():
    im = A.layer()
    stars(im, 16, 31, (2, 2, 62, 62))
    asteroid(im, 40, 38, 14, seed=5)
    o = (16, 18)
    satellite(im, o, GOLD, 8, 3.0, 0, 1.8)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    a = pr(1.6, -1.6, 0, o)
    dl.polygon(A.P([a, (34, 30), (42, 46)]), fill=(140, 220, 255, 60))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.5 * S)))
    return im


def icon_asteroidmining():
    im = A.layer()
    stars(im, 14, 41, (2, 2, 62, 62))
    asteroid(im, 30, 40, 18, seed=8)
    o = (38, 18)
    cyl(im, (-4, 0, 0), "x", 12, 2.8, (226, 226, 222), rings=[(0.5, (176, 180, 186), 0.4)], cap=(214, 218, 222), o=o)
    box3(im, 2, -2, -6, 3, 3, 4, (90, 96, 104), 0.5, o=o)
    d = ImageDraw.Draw(im)
    a = pr(3.5, -0.5, -6, o)
    for dx in (-4, 0, 4):  # anchoring legs into the rock
        d.line(A.P([pr(dx, 0, -2.6, o), (a[0] + dx - 6, a[1] + 10)]), fill=INK + (255,), width=int(1.1 * S))
        d.line(A.P([pr(dx, 0, -2.6, o), (a[0] + dx - 6, a[1] + 10)]), fill=(150, 156, 164, 255), width=int(0.5 * S))
    for k in range(3):  # ore containers
        box3(im, -4 + k * 3.6, 3, 2.8, 3, 3, 3, (214, 170, 70), 0.5, o=o)
    return im


def icon_powerbeam():
    im = A.layer()
    earth_limb(im)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([(30, 24), (34, 24), (40, 52), (24, 52)]), fill=(255, 210, 120, 90))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.8 * S)))
    o = (32, 18)
    for y in (12, 6):
        panel_xz(im, -20, 20, y, -3, 3, o, 10)
    box3(im, -2.4, -2.4, -4, 4.8, 4.8, 4.8, (226, 226, 222), 0.7, o=o)
    dish(im, (0, 0, -5.2), (0.0, -0.4, -1.0), 3.2, o, legs=False)
    for y in (-6, -12):
        panel_xz(im, -20, 20, y, -3, 3, o, 10)
    return im


def icon_helium():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    # big harvester crawling over the regolith with its intake and conveyor
    for wx in (5, 12, 19):
        cyl(im, (wx, 19.6, gz + 1.3), "y", 1.2, 1.4, (60, 60, 64))
    box3(im, 3, 11, gz + 1.6, 20, 9, 6, (214, 170, 70), 0.9)
    box3(im, 14, 13, gz + 7.6, 7, 5, 4, (226, 226, 222), 0.6)
    for wx in (5, 12, 19):
        cyl(im, (wx, 10.4, gz + 1.3), "y", 1.2, 1.4, (60, 60, 64), cap=(46, 46, 48))
    cyl(im, (23, 11, gz + 2.4), "y", 9, 2.0, (150, 156, 164), rings=[(t, (90, 96, 104), 0.4) for t in (0.25, 0.5, 0.75)], cap=(120, 126, 134))
    # helium-3 canisters
    for k in range(3):
        cyl(im, (6 + k * 3.4, 4, gz), "z", 4.4, 1.3, (176, 196, 226), rings=[(0.75, (90, 120, 170), 0.4)], cap=(196, 212, 236))
    return im


# ---------------------------------------------------------------- column 3: orbital defense
def debris_bits(im, n, seed, box=(4, 6, 60, 46)):
    rng = np.random.default_rng(seed)
    d = ImageDraw.Draw(im)
    for _ in range(n):
        x, y = rng.uniform(box[0], box[2]), rng.uniform(box[1], box[3])
        s_ = rng.uniform(0.5, 1.4)
        a = rng.uniform(0, 6.28)
        pts = [(x + s_ * math.cos(a + k * 2.1) * rng.uniform(0.6, 1.2), y + s_ * math.sin(a + k * 2.1) * rng.uniform(0.6, 1.2)) for k in range(3)]
        d.polygon(A.P(pts), fill=(150, 150, 146, 255), outline=INK + (255,), width=max(2, S // 3))


def orbit_arc(im, cy, rx, ry, c=(150, 200, 240), w=0.4):
    pts = [(32 + rx * math.cos(a), cy + ry * math.sin(a)) for a in np.linspace(math.pi * 1.05, math.pi * 1.95, 60)]
    dashed(im, pts, c, w, 2, 2)


def icon_debris():
    im = A.layer()
    earth_limb(im)
    orbit_arc(im, 44, 34, 18)
    orbit_arc(im, 50, 30, 30, (240, 200, 120))
    debris_bits(im, 22, 3)
    o = (22, 22)
    satellite(im, o, (150, 146, 140), 6, 2.6, 0, 1.4)  # dead satellite
    d = ImageDraw.Draw(im)
    cyl(im, (6, 8, 4), "x", 6, 1.6, (176, 180, 186), cap=(120, 126, 134), o=(22, 22))  # spent stage
    return im


def icon_awareness():
    im = A.layer()
    A.floor(im)
    # phased-array radar building: two sloped faces with round arrays
    X, Y, a, b, h = 5, 6, 18, 18, 18
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    top = h
    front = [pr(X, Y, 0), pr(X + a, Y, 0), pr(X + a - 3, Y + 5, top), pr(X + 3, Y + 5, top)]
    right = [pr(X + a, Y, 0), pr(X + a, Y + b, 0), pr(X + a - 5, Y + b - 3, top), pr(X + a - 3, Y + 5, top)]
    roof = [pr(X + 3, Y + 5, top), pr(X + a - 3, Y + 5, top), pr(X + a - 5, Y + b - 3, top), pr(X + 3, Y + b - 3, top)]
    dl.polygon(A.P(roof), fill=shade(CONC, (0, 0, 1)) + (255,))
    dl.polygon(A.P(front), fill=shade(CONC, (0, -1, 0.35)) + (255,))
    dl.polygon(A.P(right), fill=shade(CONC, (1, 0, 0.35)) + (255,))
    U.outlined(im, lay, 0.9)
    d = ImageDraw.Draw(im)
    for face, nm in ((front, (0, -1, 0.35)), (right, (1, 0, 0.35))):
        c = A.lerp(A.lerp(face[0], face[1], 0.5), A.lerp(face[3], face[2], 0.5), 0.5)
        rx, ry = abs(face[1][0] - face[0][0]) * 0.32, 6.2
        d.ellipse([(c[0] - rx) * S, (c[1] - ry) * S, (c[0] + rx) * S, (c[1] + ry) * S], fill=(110, 116, 126, 255), outline=INK + (255,), width=max(2, S // 3))
        for k in range(-3, 4):
            d.line(A.P([(c[0] - rx * 0.9, c[1] + k * 1.6 + (face[1][1] - face[0][1]) * -0.0), (c[0] + rx * 0.9, c[1] + k * 1.6 - (face[1][1] - face[0][1]) * 0.25)]), fill=(140, 146, 156, 255), width=max(2, S // 4))
    return im


def icon_hardening():
    im = A.layer()
    stars(im, 14, 15)
    d = ImageDraw.Draw(im)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.line(A.P([(2, 12), (22, 26)]), fill=(255, 80, 60, 200), width=int(0.9 * S))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.3 * S)))
    o = (34, 32)
    satellite(im, o, GOLD, 12, 4.4, 0, 2.6)
    box3(im, -4.2, -3.2, -3.2, 1.4, 6.4, 6.4, (110, 116, 126), 0.7, o=o)  # armour plate facing the threat
    d = ImageDraw.Draw(im)
    for k in range(5):  # sparks where the beam stops on the plate
        a = k * 1.25
        p = (22 + 1.6 * math.cos(a), 26 + 1.6 * math.sin(a))
        d.line(A.P([(22, 26), p]), fill=(255, 210, 120, 255), width=max(2, S // 3))
    return im


def icon_spacecommand():
    im = A.layer()
    A.floor(im)
    box3(im, 4, 10, 0, 20, 16, 9, (196, 196, 188), 0.9)
    windows(im, 5.4, 10, 7.2, 5, 3.8, 2.4, 2.4, c=(70, 120, 170))
    p = pr(9, 18, 9)
    ball(im, p[0], p[1] - 4.6, 4.2, (236, 238, 240), 0.4)
    dish(im, (18, 18, 13.5), (-0.4, -0.3, 0.86), 3.6)
    cyl(im, (18, 18, 9), "z", 3, 0.6, (150, 156, 164))
    cyl(im, (27, 6, 0), "z", 16, 0.3, (190, 194, 200))
    d = ImageDraw.Draw(im)
    f = pr(27, 6, 16)
    d.polygon(A.P([f, (f[0] + 5, f[1] + 1.2), (f[0] + 5, f[1] + 4.2), (f[0], f[1] + 3)]), fill=(40, 60, 130, 255), outline=INK + (255,), width=max(2, S // 3))
    return im


def icon_avoidance():
    im = A.layer()
    earth_limb(im)
    o = (34, 26)
    pts = [(10 + t * 40, 32 - 8 * math.sin(t * 2.4)) for t in np.linspace(0, 1, 40)]
    dashed(im, [(x, y + 0) for x, y in pts], (150, 200, 240), 0.4)
    satellite(im, o, GOLD, 9, 3.2, 0, 2.0)
    C.wisp(im, pr(1.6, 0, -1.6, o), 2, (236, 240, 248), 160)
    debris_bits(im, 1, 4, (44, 36, 46, 40))
    d = ImageDraw.Draw(im)
    for k in range(3):  # streak of the debris piece
        d.line(A.P([(46 + k * 2.6, 39 + k * 0.6), (48 + k * 2.6, 39.5 + k * 0.6)]), fill=(200, 200, 196, 200), width=max(2, S // 3))
    return im


def icon_cleanup():
    im = A.layer()
    earth_limb(im)
    # old rocket stage tumbling, the servicer catching it with a net
    o = (24, 22)
    cyl(im, (-8, 0, 0), "x", 14, 2.6, (176, 180, 186), rings=[(0.5, (120, 126, 134), 0.4)], cap=(120, 126, 134), o=o)
    d = ImageDraw.Draw(im)
    net = [(28, 12), (40, 10), (44, 28), (32, 32)]
    for t in np.linspace(0, 1, 6):
        d.line(A.P([A.lerp(net[0], net[1], t), A.lerp(net[3], net[2], t)]), fill=(236, 214, 120, 230), width=max(2, S // 4))
        d.line(A.P([A.lerp(net[0], net[3], t), A.lerp(net[1], net[2], t)]), fill=(236, 214, 120, 230), width=max(2, S // 4))
    o2 = (50, 30)
    satellite(im, o2, (226, 226, 222), 6, 3.0, 0, 1.6)
    for q in net[1:3]:
        d = ImageDraw.Draw(im)
        d.line(A.P([q, pr(0, 0, 0, o2)]), fill=(200, 190, 140, 255), width=max(2, S // 4))
    return im


def icon_patrol():
    im = A.layer()
    earth_limb(im)
    satellite(im, (40, 30), (110, 116, 126), 12, 4.4, 2.6, 2.4)  # foreign satellite
    satellite(im, (16, 16), GOLD, 5, 2.4, 0, 1.2)  # small inspector
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([(17.5, 17), (36, 26), (40, 34)]), fill=(200, 230, 255, 70))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.4 * S)))
    return im


def icon_planetary():
    im = A.layer()
    stars(im, 16, 17, (2, 2, 62, 30))
    d = ImageDraw.Draw(im)
    d.line(A.P([(46, 6), (58, 12)]), fill=(240, 220, 170, 255), width=int(0.7 * S))
    dot(d, (46, 6), 0.9, (250, 240, 200))
    A.floor(im)
    box3(im, 7, 10, 0, 16, 16, 7, (226, 226, 222), 0.9)
    c = pr(15, 18, 7)
    U.terrain(im, lambda x, y: 7 + 0.9 * math.sqrt(max(0.0, 7.6 ** 2 - (x - 15) ** 2 - (y - 18) ** 2)), 7.4, 22.6, 10.4, 25.6, 26,
              lambda x, y, z: (236, 236, 232), base_z=7.05)
    d = ImageDraw.Draw(im)
    slit = [pr(15, 14, 13.4), pr(15, 18.5, 13.9), pr(17.6, 21, 12.6), pr(17.6, 16.5, 12.2)]
    d.polygon(A.P(slit), fill=(30, 34, 44, 255))
    return im


def icon_deflection():
    im = A.layer()
    stars(im, 14, 19, (2, 2, 62, 62))
    asteroid(im, 40, 36, 15, seed=12)
    asteroid(im, 54, 14, 3.6, seed=2)
    o = (12, 14)
    d = ImageDraw.Draw(im)
    pts = [(14, 16), (20, 20), (26, 25)]
    dashed(im, pts + [(30, 28)], (240, 220, 120), 0.5, 1, 1)
    satellite(im, o, (226, 226, 222), 10, 2.8, 0, 1.0)
    return im


def icon_cislunar():
    im = A.layer()
    stars(im, 14, 23, (2, 2, 62, 62))
    small_earth(im, 13, 46, 9)
    planet(im, 52, 14, 6, "moon", spin=(0.2, 0.1), seed=9)
    path = [(13 + (52 - 13) * t, 46 + (14 - 46) * t - 10 * math.sin(math.pi * t)) for t in np.linspace(0.12, 0.88, 40)]
    path2 = [(13 + (52 - 13) * t + 4, 46 + (14 - 46) * t + 7 * math.sin(math.pi * t)) for t in np.linspace(0.12, 0.88, 40)]
    dashed(im, path, (150, 200, 240), 0.45)
    dashed(im, path2, (240, 200, 120), 0.45)
    for (x, y) in (path[14], path2[26]):
        satellite(im, (x, y), GOLD, 4, 1.8, 0, 1.0)
    return im


def icon_baseguard():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    cx, cy = 16, 16
    U.terrain(im, lambda x, y: gz + max(0.0, 3.2 - abs(math.hypot(x - cx, y - cy) - 10.5) * 1.6), 3, 29.5, 3, 29.5, 40, moon_color, base_z=gz + 0.05)
    cyl(im, (12, 16, gz), "x", 9, 2.4, WHITE, rings=[(0.5, (176, 180, 186), 0.4)])
    p = pr(18, 20, gz)
    U.terrain(im, lambda x, y: gz + 0.6 * math.sqrt(max(0.0, 16 - (x - 19) ** 2 - (y - 21) ** 2)) * 1.2, 15, 23, 17, 25, 18, moon_color, base_z=gz + 0.05)
    cyl(im, (24, 9, gz), "z", 5, 0.5, (150, 156, 164))
    dish(im, (24, 9, gz + 6.8), (-0.4, -0.4, 0.82), 2.6)
    return im


# ---------------------------------------------------------------- column 4: orbital industry
def icon_microgravity():
    im = A.layer()
    A.floor_dark(im)
    box3(im, 4, 14, 0, 22, 12, 16, (214, 218, 224), 0.9)
    d = ImageDraw.Draw(im)
    win = [pr(7, 14, 13), pr(23, 14, 13), pr(23, 14, 4), pr(7, 14, 4)]
    d.polygon(A.P(win), fill=(40, 52, 70, 255), outline=INK + (255,), width=max(2, S // 3))
    for k in range(2):  # glove ports
        c = pr(10 + k * 9, 14, 5)
        d.ellipse([(c[0] - 1.4) * S, (c[1] - 1.4) * S, (c[0] + 1.4) * S, (c[1] + 1.4) * S], fill=(30, 30, 34, 255), outline=(150, 156, 164, 255), width=max(2, S // 4))
    for (x, z, r) in ((12, 10, 1.6), (16, 8.5, 1.0), (19, 11, 0.7)):  # floating water spheres
        p = pr(x, 13, z)
        ball(im, p[0], p[1] - r, r, (120, 180, 230), 0.8)
    rng = np.random.default_rng(2)
    for _ in range(3):  # protein crystals
        p = pr(rng.uniform(8, 22), 13, rng.uniform(5, 7))
        d = ImageDraw.Draw(im)
        d.polygon(A.P([(p[0], p[1] - 1.2), (p[0] + 0.8, p[1]), (p[0], p[1] + 1.2), (p[0] - 0.8, p[1])]), fill=(150, 220, 236, 255), outline=INK + (255,), width=max(2, S // 4))
    return im


def icon_smallsat():
    im = A.layer()
    L, F, R, Bk = pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 32.2, 0), pr(0, 32.2, 0)
    m = A.mask_of(lambda d: d.polygon(A.P([L, F, R, Bk]), fill=255))
    im.alpha_composite(A.outline(m, 0.8))
    im.alpha_composite(A.noisy(A.vgrad(m, (236, 238, 240), (196, 200, 206)), 3, 2))  # clean room floor
    for k, (x, y) in enumerate(((20, 20), (6, 20), (20, 6), (6, 6))):
        box3(im, x, y, 0, 6, 6, 1.2, (90, 96, 104), 0.5)
        box3(im, x + 0.8, y + 0.8, 1.2, 4.4, 4.4, 5.0, GOLD, 0.7)
        d = ImageDraw.Draw(im)
        a, b = pr(x + 0.8, y + 0.8, 6.0), pr(x + 5.2, y + 0.8, 6.0)
        d.polygon(A.P([a, b, (b[0], b[1] + 4.4), (a[0], a[1] + 4.4)]), fill=(40, 58, 110, 255), outline=INK + (255,), width=max(2, S // 4))
    return im


def icon_commercialsat():
    im = A.layer()
    earth_limb(im)
    o = (32, 24)
    satellite(im, o, (226, 226, 222), 22, 5.0, 0, 2.8)
    dish(im, (-3.6, -1, 1), (-1, -0.3, 0.3), 3.4, o, legs=False)
    dish(im, (3.6, -1, 1), (1, -0.6, 0.3), 3.0, o, legs=False)
    return im


def icon_constellation():
    im = A.layer()
    earth_limb(im)
    for k in range(9):
        t = k / 8
        x = 6 + 52 * t
        y = 38 - 16 * math.sin(math.pi * t) + 4
        o = (x, y - 6)
        box3(im, -1.6, -0.8, -0.2, 3.2, 1.6, 0.4, (200, 204, 210), 0.5, o=o)
        d = ImageDraw.Draw(im)
        a, b = pr(1.6, 0, 0.2, o), pr(5.6, 0, 0.2, o)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.4 * S))
        d.line(A.P([a, b]), fill=(70, 96, 160, 255), width=int(0.8 * S))
    for k in range(7):
        t = (k + 0.5) / 7
        x = 10 + 44 * t
        y = 22 - 10 * math.sin(math.pi * t)
        dot(ImageDraw.Draw(im), (x, y), 0.6, (220, 224, 230))
    return im


def icon_servicing():
    im = A.layer()
    earth_limb(im)
    satellite(im, (40, 28), (110, 116, 126), 16, 4.6, 0, 2.6)
    o = (18, 20)
    box3(im, -2.6, -2.6, -2.6, 5.2, 5.2, 5.2, (226, 226, 222), 0.7, o=o)
    panel_xz(im, -2, 2, 5, -2.6, 2.6, o, 2)
    d = ImageDraw.Draw(im)
    j0, j1, j2 = pr(2.6, 0, 1, o), (29, 16), (34.5, 26)
    for a, b in ((j0, j1), (j1, j2)):
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.8 * S))
        d.line(A.P([a, b]), fill=(226, 226, 222, 255), width=int(0.9 * S))
    dot(d, j1, 0.9, (150, 156, 164), INK[:3])
    pts = [pr(0, 2.6, -2, o), (24, 30), (32, 33), (36, 30)]
    d.line(A.P(pts), fill=(236, 182, 44, 255), width=max(2, int(0.5 * S)), joint="curve")
    return im


def icon_manufacturing():
    im = A.layer()
    earth_limb(im)
    o = (30, 26)
    panel_xz(im, -10, 10, 7, -2.4, 2.4, o, 5)
    cyl(im, (-10, 0, 0), "x", 20, 4.0, (226, 226, 222), rings=[(t, (176, 180, 186), 0.4) for t in (0.25, 0.5, 0.75)], cap=(210, 214, 220), o=o)
    box3(im, -6, -1, 4, 9, 2, 6, (236, 236, 232), 0.5, o=o)  # radiator
    panel_xz(im, -10, 10, -7, -2.4, 2.4, o, 5)
    p = pr(11, 0, 0, o)
    cap = A.layer()
    capsule(cap, 32, 46, 9, 4.0, body=(214, 214, 210))
    im.alpha_composite(cap.rotate(-90, resample=Image.BICUBIC, center=(32 * S, 46 * S), translate=((p[0] + 6 - 32) * S, (p[1] - 46 + 1) * S)))
    return im


def icon_printing():
    im = A.layer()
    stars(im, 12, 27)
    o = (14, 30)
    box3(im, -5, -5, -5, 10, 10, 10, (226, 226, 222), 0.8, o=o)
    d = ImageDraw.Draw(im)
    # truss beam coming out of the printer
    x0, x1 = 5, 34
    for t in np.linspace(0, 1, 12):
        x = x0 + (x1 - x0) * t
        for (y, z) in ((-1.6, -1.6), (1.6, -1.6), (0, 1.6)):
            pass
    edges = [((-1.6, -1.6), (1.6, -1.6)), ((1.6, -1.6), (0, 1.6)), ((0, 1.6), (-1.6, -1.6))]
    lines = []
    for (y, z) in ((-1.6, -1.6), (1.6, -1.6), (0, 1.6)):
        lines.append([pr(x0, y, z, o), pr(x1, y, z, o)])
    for k in range(10):
        xa, xb = x0 + (x1 - x0) * k / 10, x0 + (x1 - x0) * (k + 1) / 10
        for (a, b) in edges:
            lines.append([pr(xa, *a, o), pr(xb, *b, o)])
    for ln in lines:
        d.line(A.P(ln), fill=INK + (255,), width=int(0.8 * S))
    for ln in lines:
        d.line(A.P(ln), fill=(200, 204, 210, 255), width=max(2, int(0.36 * S)))
    j0, j1, j2 = pr(3, -2, 5, o), (34, 4), (40, 14)
    for a, b in ((j0, j1), (j1, j2)):
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.6 * S))
        d.line(A.P([a, b]), fill=(236, 182, 44, 255), width=int(0.8 * S))
    A.glow(im, *j2, 1.0, (255, 200, 120), 220)
    return im


def icon_assembly():
    im = A.layer()
    earth_limb(im)
    o = (30, 26)
    cyl(im, (-14, 0, 0), "x", 12, 4.4, STEEL_SS, rings=[(0.5, (150, 154, 160), 0.4)], cap=(196, 200, 206), o=o)
    d = ImageDraw.Draw(im)
    for x in (-2, 3, 8, 13):  # open frame of the unfinished hull
        ring = [pr(x, 4.4 * math.cos(a), 4.4 * math.sin(a), o) for a in np.linspace(0, 2 * math.pi, 40)]
        d.line(A.P(ring), fill=INK + (255,), width=int(0.9 * S))
        d.line(A.P(ring), fill=(196, 200, 206, 255), width=max(2, int(0.4 * S)))
    for a in np.linspace(0, 2 * math.pi, 7)[:-1]:
        ln = [pr(-2, 4.4 * math.cos(a), 4.4 * math.sin(a), o), pr(13, 4.4 * math.cos(a), 4.4 * math.sin(a), o)]
        d.line(A.P(ln), fill=INK + (255,), width=int(0.9 * S))
        d.line(A.P(ln), fill=(196, 200, 206, 255), width=max(2, int(0.4 * S)))
    j0, j1, j2 = (8, 12), (16, 6), (24, 18)
    for a, b in ((j0, j1), (j1, j2)):
        d.line(A.P([a, b]), fill=INK + (255,), width=int(1.5 * S))
        d.line(A.P([a, b]), fill=(236, 182, 44, 255), width=int(0.7 * S))
    box3(im, 1, -2, 4.6, 4, 4, 2.2, GOLD, 0.5, o=o)
    return im


def icon_lunarfactory():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    box3(im, 4, 14, gz, 16, 13, 9, (200, 204, 210), 0.9)
    cyl(im, (24, 21, gz), "z", 13, 2.6, (150, 156, 164), rings=[(0.5, (110, 116, 126), 0.4)], cap=(90, 96, 104))
    d = ImageDraw.Draw(im)
    a, b = pr(8, 14, gz + 3), pr(12, 14, gz + 3)
    door = [a, b, (b[0], b[1] - 4), (a[0], a[1] - 4)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(door), fill=255))
    im.alpha_composite(A.vgrad(m, (255, 200, 90), (230, 100, 40)))
    C.solar_rows(im, 2, 2, 14, 10, gz, 2)
    for k in range(3):
        box3(im, 18 + k * 3.4, 4, gz, 3, 3, 1.4, (150, 156, 166), 0.4)
    return im


def icon_shipyard():
    im = A.layer()
    earth_limb(im)
    o = (32, 26)
    cyl(im, (-12, 0, 0), "x", 22, 4.0, STEEL_SS, rings=[(t, (150, 154, 160), 0.4) for t in (0.3, 0.6)], cap=(196, 200, 206), o=o)
    d = ImageDraw.Draw(im)
    lines = []
    for x in (-15, -5, 5, 15):
        for (y, z) in ((-7, -7), (7, -7), (7, 7), (-7, 7)):
            pass
        sq = [(-7, -7), (7, -7), (7, 7), (-7, 7), (-7, -7)]
        lines.append([pr(x, y, z, o) for y, z in sq])
    for (y, z) in ((-7, -7), (7, -7), (7, 7), (-7, 7)):
        lines.append([pr(-15, y, z, o), pr(15, y, z, o)])
    for ln in lines:
        d.line(A.P(ln), fill=INK + (255,), width=int(0.9 * S))
        d.line(A.P(ln), fill=(236, 182, 44, 255), width=max(2, int(0.42 * S)))
    return im


def icon_platform():
    im = A.layer()
    earth_limb(im)
    o = (32, 26)
    R = 17
    U.terrain(im, lambda x, y: 0.6 if math.hypot(x, y) < R else -5, -R, R, -R, R, 36, lambda x, y, z: (196, 200, 206) if (int(math.hypot(x, y) / 3) % 2) else (176, 180, 188),
              o=o, base_z=-1)
    for (x, y) in ((-6, 4), (4, -6), (6, 6), (-5, -6), (0, 0)):
        box3(im, x - 2, y - 2, 0.6, 4, 4, 3 + (abs(x) % 3), (226, 226, 222), 0.5, o=o)
    return im


def icon_elevator():
    im = A.layer()
    sea_tile(im)
    box3(im, 8, 8, 0, 16, 16, 3.0, (150, 156, 164), 0.9)
    box3(im, 11, 11, 3.0, 10, 10, 3.0, (226, 226, 222), 0.8)
    top = pr(16, 16, 6)
    d = ImageDraw.Draw(im)
    d.line(A.P([top, (top[0], -2)]), fill=INK + (255,), width=int(1.2 * S))
    d.line(A.P([top, (top[0], -2)]), fill=(200, 204, 210, 255), width=int(0.5 * S))
    o = (top[0] - 13.5, top[1] - 26 - 0)
    box3(im, -1.6, -1.6, 0, 3.2, 3.2, 4, GOLD, 0.6, o=(top[0] - 0.0 - 0 * 1, top[1] - 26))
    return im


# ---------------------------------------------------------------- column 5: space travel
def orrery(im, cx, cy, radii, dashes=True):
    for r in radii:
        pts = [(cx + r * math.cos(a), cy + r * 0.5 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 90)]
        dashed(im, pts, (150, 170, 200), 0.35, 2, 1) if dashes else None


def icon_navigation():
    im = A.layer()
    stars(im, 16, 51, (2, 2, 62, 62))
    cx, cy = 30, 34
    orrery(im, cx, cy, (12, 22))
    sun(im, cx, cy, 3.4)
    e = (cx + 12 * math.cos(2.4), cy + 6 * math.sin(2.4))
    m = (cx + 22 * math.cos(-0.5), cy + 11 * math.sin(-0.5))
    pts = []
    for t in np.linspace(0, 1, 40):  # transfer arc from Earth to Mars
        a = 2.4 + (2 * math.pi - 0.5 - 2.4) * t
        r = 12 + 10 * t
        pts.append((cx + r * math.cos(a), cy + r * 0.5 * math.sin(a)))
    d = ImageDraw.Draw(im)
    d.line(A.P(pts), fill=(240, 220, 90, 255), width=int(0.6 * S), joint="curve")
    earth_sphere(im, *e, 2.6, spin=(5.0, -0.2), seed=21, outline=0.5)
    planet(im, *m, 2.2, "mars", seed=4, outline=0.5)
    satellite(im, pts[22], GOLD, 3, 1.4, 0, 0.8)
    return im


def icon_gravityassist():
    im = A.layer()
    stars(im, 16, 53, (2, 2, 62, 62))
    planet(im, 30, 36, 13, "venus", spin=(0.3, 0.2), seed=6)
    pts = [(2 + t * 60, 12 + 30 * math.exp(-((t - 0.45) / 0.2) ** 2) * 0.9 + 6 * t) for t in np.linspace(0, 1, 50)]
    pts = [(x, y if not (abs(x - 30) < 13 and y > 26) else y) for x, y in pts]
    dashed(im, pts, (240, 220, 90), 0.5)
    satellite(im, pts[38], GOLD, 4, 1.8, 0, 1.0)
    return im


def icon_translunar():
    im = A.layer()
    stars(im, 16, 57, (2, 2, 62, 62))
    planet(im, 50, 16, 12, "moon", light=(-0.8, -0.3, 0.5), spin=(0.2, 0.1), seed=9)
    small_earth(im, 8, 54, 5)
    o = (22, 38)
    cyl(im, (-6, 0, 0), "x", 7, 2.6, (226, 226, 222), cap=(210, 214, 220), o=o)
    p = pr(-6, 0, 0, o)
    cap = A.layer()
    capsule(cap, 32, 46, 6, 3.4)
    im.alpha_composite(cap.rotate(-90, resample=Image.BICUBIC, center=(32 * S, 46 * S), translate=((p[0] + 4.6 - 32 + 7.6) * S * 0 + (pr(1, 0, 0, o)[0] + 3.2 - 32) * S, (pr(1, 0, 0, o)[1] - 46) * S)))
    cyl(im, (-9, 0, 0), "x", 3, 1.8, (110, 76, 52), cap=(40, 30, 26), o=o)
    return im


def icon_deepnet():
    im = A.layer()
    A.floor(im)
    A.ellipse_shadow(im, *pr(16, 16, 0), 10, 4)
    box3(im, 11, 11, 0, 10, 10, 6, CONC, 0.8)
    cyl(im, (16, 16, 6), "z", 5, 2.2, (150, 156, 164))
    dish(im, (16, 16, 17), (-0.35, -0.45, 0.82), 12.5)
    box3(im, 2, 24, 0, 6, 6, 4, (220, 222, 224), 0.6)
    return im


def icon_precisionland():
    im = A.layer()
    moon_tile(im)
    gz = 3.0
    c = pr(16, 14, moon_ground(16, 14) + 0.05)
    d = ImageDraw.Draw(im)
    d.ellipse([(c[0] - 7) * S, (c[1] - 3.5) * S, (c[0] + 7) * S, (c[1] + 3.5) * S], outline=(240, 220, 90, 255), width=int(0.6 * S))
    d.ellipse([(c[0] - 1.2) * S, (c[1] - 0.6) * S, (c[0] + 1.2) * S, (c[1] + 0.6) * S], fill=(240, 220, 90, 255))
    by = c[1] - 14
    flame(im, c[0], by + 2.0, 8, 1.6)
    legs(im, c[0], by, 3.4, 3.2, 1.8)
    box3(im, 0, 0, 0, 1, 1, 1, GOLD, 0.1, o=(-50, -50))
    full, col = A.solid(c[0], by, 8, 4.2, [(0, 1.0), (0.6, 1.0), (1.0, 0.6)], [(0, 1, GOLD, 0.6)], rings=[(0.6, (150, 110, 40))])
    A.place(im, full, col, 0.8)
    return im


def icon_aerobrake():
    im = A.layer()
    stars(im, 12, 61, (2, 2, 62, 30))
    limb(im, "mars", 128, 78)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([(22, 34), (14, 20), (34, 14), (44, 30)]), fill=(255, 150, 60, 150))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.6 * S)))
    cap = A.layer()
    capsule(cap, 32, 46, 12, 7.0, body=(214, 214, 210), shield=(70, 50, 40))
    im.alpha_composite(cap.rotate(-130, resample=Image.BICUBIC, center=(32 * S, 40 * S), translate=(-2 * S, -14 * S)))
    return im


def icon_transithab():
    im = A.layer()
    stars(im, 16, 63, (2, 2, 62, 62))
    o = (30, 32)
    cyl(im, (-14, 0, 0), "x", 14, 7.0, (226, 220, 206), rings=[(t, (186, 176, 156), 0.6) for t in (0.17, 0.34, 0.5, 0.67, 0.84)], cap=(214, 208, 192), o=o)
    d = ImageDraw.Draw(im)
    for k in range(3):
        dot(d, pr(-10 + k * 4, -6.4, 2.6, o), 0.6, (60, 90, 140), INK[:3])
    cyl(im, (0, 0, 0), "x", 8, 2.6, (236, 236, 232), o=o)
    panel_xz(im, 1, 8, 7, -2.2, 2.2, o, 3)
    cyl(im, (8, 0, 0), "x", 3.4, 2.8, (90, 96, 104), o=o)
    cyl(im, (11.4, 0, 0), "x", 2.6, 2.2, (110, 76, 52), cap=(40, 30, 26), o=o)
    return im


def icon_marstransfer():
    im = A.layer()
    stars(im, 12, 67, (2, 2, 62, 30))
    limb(im, "mars", 126, 78)
    o = (26, 22)
    cyl(im, (-10, 0, 0), "x", 9, 3.6, (226, 220, 206), rings=[(0.5, (186, 176, 156), 0.5)], cap=(214, 208, 192), o=o)
    cyl(im, (-1, 0, 0), "x", 7, 2.4, (236, 236, 232), o=o)
    cyl(im, (6, 0, 0), "x", 3.2, 2.6, (110, 76, 52), cap=(40, 30, 26), o=o)
    p = pr(9.2, 0, 0, o)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([(p[0] + 0.6, p[1] - 2.4), (p[0] + 10, p[1] + 2.4), (p[0] + 0.6, p[1] + 2.4)]), fill=(255, 210, 140, 200))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.7 * S)))
    q = (44, 34)
    full, col = A.solid(q[0], q[1], 5, 2.6, [(0, 1.0), (0.6, 1.0), (1.0, 0.6)], [(0, 1, GOLD, 0.6)])
    A.place(im, full, col, 0.7)
    dashed(im, [(30, 26 + k * 0.0) for k in range(1)] + [(30 + t * 14, 25 + t * 9) for t in np.linspace(0, 1, 10)], (240, 220, 90), 0.4, 1, 1)
    return im


def icon_venusfloat():
    im = A.layer()
    # cloud deck of Venus as the floor
    L, F, R, Bk = pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 32.2, 0), pr(0, 32.2, 0)
    m = A.mask_of(lambda d: d.polygon(A.P([L, F, R, Bk]), fill=255))
    im.alpha_composite(A.outline(m, 0.8))
    im.alpha_composite(A.noisy(A.vgrad(m, (240, 214, 150), (206, 170, 100)), 10, 5))
    d = ImageDraw.Draw(im)
    for x, y in ((6, 6), (20, 4), (8, 22), (26, 20), (16, 14)):
        p = pr(x, y, 0)
        d.arc([(p[0] - 3) * S, (p[1] - 1) * S, (p[0] + 3) * S, (p[1] + 1) * S], 200, 340, fill=(250, 236, 200, 255), width=max(2, S // 3))
    o = (32, 22)
    cyl(im, (-12, 0, 0), "x", 24, 6.0, (236, 236, 232), rings=[(t, (196, 196, 190), 0.5) for t in (0.2, 0.4, 0.6, 0.8)], cap=(220, 222, 226), o=o)
    d = ImageDraw.Draw(im)
    for x in (-6, 6):
        d.line(A.P([pr(x, 0, -6, o), pr(x * 0.6, 0, -11, o)]), fill=INK + (255,), width=int(0.6 * S))
    box3(im, -5, -2, -13.5, 10, 4, 3, (200, 204, 210), 0.7, o=o)
    d = ImageDraw.Draw(im)
    for k in range(3):
        dot(d, pr(-3.4 + k * 3.4, -2, -12, o), 0.55, (60, 90, 140), INK[:3])
    return im


def icon_asteroidnav():
    im = A.layer()
    stars(im, 14, 71, (2, 2, 62, 62))
    asteroid(im, 26, 40, 17, seed=15)
    o = (44, 16)
    cyl(im, (-4, 0, 0), "x", 9, 2.8, (226, 226, 222), rings=[(0.5, (176, 180, 186), 0.4)], cap=(214, 218, 222), o=o)
    panel_xz(im, -3, 4, 5, -1.6, 1.6, o, 2)
    d = ImageDraw.Draw(im)
    for q in ((30, 30), (36, 36)):  # tethers to the rock
        d.line(A.P([pr(-3, 0, -2, o), q]), fill=(236, 214, 120, 255), width=max(2, int(0.4 * S)))
    return im


def icon_outerprop():
    im = A.layer()
    stars(im, 12, 73, (2, 2, 62, 62))
    planet(im, 44, 46, 22, "jupiter", light=(-0.7, -0.5, 0.5), spin=(0.2, 0.25), seed=3)
    planet(im, 14, 48, 3.0, "moon", seed=11)
    o = (24, 20)
    cyl(im, (-12, 0, 0), "x", 8, 3.0, (236, 236, 232), cap=(214, 218, 222), o=o)
    box3(im, -4, -0.7, -0.7, 10, 1.4, 1.4, (150, 156, 164), 0.5, o=o)
    box3(im, -2, 2, -0.4, 6, 0.4, 5, (236, 236, 232), 0.4, o=o)
    cyl(im, (6, 0, 0), "x", 4, 3.4, (70, 74, 82), rings=[(0.5, (40, 160, 200), 0.6)], o=o)
    cyl(im, (10, 0, 0), "x", 3.4, 2.6, (110, 76, 52), cap=(40, 30, 26), o=o)
    return im


def icon_titanentry():
    im = A.layer()
    planet(im, 50, 10, 5.5, "jupiter", spin=(0.1, 0.5), seed=7)
    d = ImageDraw.Draw(im)
    d.ellipse([39 * S, 8 * S, 61 * S, 12.5 * S], outline=(210, 196, 160, 255), width=int(0.6 * S))  # Saturn's rings

    def ground(x, y):
        return 2.0 + 0.4 * math.sin(x * 0.5) * math.cos(y * 0.4)

    def color(x, y, z):
        lake = math.hypot(x - 9, y - 9) < 6.5 or math.hypot(x - 14, y - 5) < 4
        return (60, 50, 44) if lake else (186, 132, 70)
    U.terrain(im, ground, 0, 32.2, 0, 32.2, 36, color, skirt=lambda z: (130, 90, 50), edge=0.9)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.rectangle([0, 0, A.W, A.W], fill=(230, 170, 90, 50))
    im.alpha_composite(Image.fromarray(np.minimum(np.array(lay), np.dstack([np.full((A.W, A.W), 255)] * 3 + [np.array(im.getchannel("A")) // 5]).astype(np.uint8))) if False else A.layer())
    # probe under its parachute
    c = (30, 30)
    d = ImageDraw.Draw(im)
    canopy = [(c[0] - 9, c[1] - 14), (c[0] + 9, c[1] - 14)]
    d.chord([(c[0] - 9) * S, (c[1] - 20) * S, (c[0] + 9) * S, (c[1] - 8) * S], 180, 360, fill=(236, 120, 50, 255), outline=INK + (255,), width=int(0.6 * S))
    for k in range(-2, 3):
        d.line(A.P([(c[0] + k * 4.2, c[1] - 14), (c[0], c[1] - 2)]), fill=(236, 230, 210, 255), width=max(2, S // 4))
    full, col = A.solid(c[0], c[1] + 1.5, 4, 3.4, [(0, 0.6), (0.4, 1.0), (1.0, 0.7)], [(0, 1, (226, 226, 222), 0.5)])
    A.place(im, full, col, 0.7)
    return im


def icon_solarnet():
    im = A.layer()
    stars(im, 16, 77, (2, 2, 62, 62))
    cx, cy = 32, 32
    orrery(im, cx, cy, (8, 15, 23))
    sun(im, cx, cy, 3.2)
    nodes = []
    for r, a, kind in ((8, 2.6, "earth"), (15, -0.6, "mars"), (23, 1.2, "jupiter"), (23, 3.6, "moon")):
        p = (cx + r * math.cos(a), cy + r * 0.5 * math.sin(a))
        nodes.append(p)
        if kind == "earth":
            earth_sphere(im, *p, 2.2, spin=(5.0, -0.2), seed=21, outline=0.5)
        else:
            planet(im, *p, 2.0 if kind != "jupiter" else 3.0, kind, seed=4, outline=0.5)
    for a, b in ((0, 1), (1, 2), (0, 3), (1, 3)):
        pts = [A.lerp(nodes[a], nodes[b], t) for t in np.linspace(0.12, 0.88, 16)]
        dashed(im, pts, (240, 220, 90), 0.35, 1, 1)
    for k in range(3):
        mid = A.lerp(nodes[k], nodes[k + 1], 0.5)
        satellite(im, mid, GOLD, 2.6, 1.2, 0, 0.6)
    return im


NAMES = ['foundations', 'launcher', 'heavy', 'cryogenic', 'smalllauncher', 'reusable', 'rapidreuse', 'superheavy', 'refuel', 'nuclear', 'electric', 'fullflow', 'massdriver', 'cruiser', 'crewed', 'station', 'longstay', 'commercialcrew', 'lifesupport', 'radiation', 'habitat', 'surface', 'deepmission', 'marslanding', 'gravity', 'torpor', 'biosphere', 'tracking', 'powerarrays', 'rtg', 'prospecting', 'solar', 'lunarice', 'fission', 'regolith', 'marsfuel', 'asteroidsurvey', 'asteroidmining', 'powerbeam', 'helium', 'debris', 'awareness', 'hardening', 'spacecommand', 'avoidance', 'cleanup', 'patrol', 'planetary', 'deflection', 'cislunar', 'baseguard', 'microgravity', 'smallsat', 'commercialsat', 'constellation', 'servicing', 'manufacturing', 'printing', 'assembly', 'lunarfactory', 'shipyard', 'platform', 'elevator', 'navigation', 'gravityassist', 'translunar', 'deepnet', 'precisionland', 'aerobrake', 'transithab', 'marstransfer', 'venusfloat', 'asteroidnav', 'outerprop', 'titanentry', 'solarnet']
OUT = "gfx/interface/mdr/space/"
if __name__ == "__main__":
    preview = Image.new("RGBA", (14 * 70 + 6, 6 * 70 + 6), (30, 34, 40, 255))
    for k, name in enumerate(NAMES):
        icon = globals()["icon_" + name]().resize((N, N), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=0))
        A.save_dds(icon, f"{OUT}tech_{name}.dds")
        preview.alpha_composite(icon, (6 + (k % 14) * 70, 6 + (k // 14) * 70))
    if len(sys.argv) > 1:
        preview.save(sys.argv[1])
    print(f"{len(NAMES)} space technology icons written")
