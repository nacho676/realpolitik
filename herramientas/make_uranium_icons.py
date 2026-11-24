# Uranium mining research icons (mdr_uranium_tech_1..5): one scene per technique, in the style of make_ammo_icons.py
# (isometric scene with volume, radiation triangle and yellow Roman numeral), drawn at 8x and reduced to 64x64.
# Writes gfx/interface/technologies/mdr/mdr_uranium_tech_<n>.dds.
# Run from the mod folder: python herramientas/make_uranium_icons.py [preview.png]
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ammo_icons as A  # noqa: E402  (shared drawing helpers and save_dds)

S, W, N, INK = A.S, A.W, A.N, A.INK
YELLOW = (236, 200, 40)
ORE = (214, 180, 60)


def strip(im, a, b, ad, bd, t0, t1, c, seed=0):
    """Band of a vertical face between heights t0 and t1 (0 = top edge, 1 = bottom edge)."""
    poly = [A.lerp(a, ad, t0), A.lerp(b, bd, t0), A.lerp(b, bd, t1), A.lerp(a, ad, t1)]
    m = A.mask_of(lambda d: d.polygon(A.P(poly), fill=255))
    im.alpha_composite(A.noisy(A.vgrad(m, c, tuple(int(v * 0.78) for v in c)), 7, seed))


def earth_slab(im, top=((168, 156, 104), (140, 128, 82)), ore_band=(0.42, 0.7), h=9):
    L, F, R, Bk = (3, 41), (32, 55), (61, 41), (32, 27)
    Ld, Fd, Rd = A.iso_box(im, L, F, R, Bk, h, top, ((120, 92, 60), (96, 72, 46)), ((96, 72, 46), (72, 54, 34)), 1.0, 6)
    for a, b, ad, bd, k in ((L, F, Ld, Fd, 1.0), (F, R, Fd, Rd, 0.8)):
        strip(im, a, b, ad, bd, 0.0, 0.16, tuple(int(v * k) for v in (110, 120, 60)), 1)
        strip(im, a, b, ad, bd, 0.16, ore_band[0], tuple(int(v * k) for v in (128, 98, 64)), 2)
        strip(im, a, b, ad, bd, ore_band[0], ore_band[1], tuple(int(v * k) for v in ORE), 3)
        strip(im, a, b, ad, bd, ore_band[1], 1.0, tuple(int(v * k) for v in (110, 106, 100)), 4)
    d = ImageDraw.Draw(im)
    d.line(A.P([Ld, Fd, Rd]), fill=INK + (255,), width=int(0.8 * S))
    return L, F, R, Bk, Ld, Fd, Rd


def trefoil_badge(im):
    d = ImageDraw.Draw(im)
    tri = [(1.5, 63), (15, 63), (8.25, 51)]
    d.polygon(A.P(tri), fill=INK + (255,))
    inner = [(3.6, 61.8), (12.9, 61.8), (8.25, 53.5)]
    d.polygon(A.P(inner), fill=YELLOW + (255,))
    cx, cy, r = 8.25, 58.6, 2.7
    for a0 in (-90, 30, 150):
        d.pieslice([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], a0 - 30, a0 + 30, fill=INK + (255,))
    d.ellipse([(cx - 0.9) * S, (cy - 0.9) * S, (cx + 0.9) * S, (cy + 0.9) * S], fill=YELLOW + (255,))
    d.ellipse([(cx - 0.55) * S, (cy - 0.55) * S, (cx + 0.55) * S, (cy + 0.55) * S], fill=INK + (255,))


def drum(im, cx, by, h=9, r=3.4):
    full, col = A.solid(cx, by, h, r, [(0, 1), (1, 1)], [(0, 1, YELLOW, 0.5)], rings=[(0.33, (150, 120, 20)), (0.66, (150, 120, 20))])
    A.place(im, full, col, 0.7)
    A.top_disc(im, cx, by - h, r, (220, 186, 36), (150, 120, 20))
    d = ImageDraw.Draw(im)
    y = by - h * 0.5
    d.ellipse([(cx - 1.3) * S, (y - 1.3) * S, (cx + 1.3) * S, (y + 1.3) * S], fill=INK + (255,))
    d.ellipse([(cx - 0.4) * S, (y - 0.4) * S, (cx + 0.4) * S, (y + 0.4) * S], fill=YELLOW + (255,))


def pipe(im, pts, c=(176, 182, 190), w=1.3):
    d = ImageDraw.Draw(im)
    d.line(A.P(pts), fill=INK + (255,), width=int((w + 0.9) * S), joint="curve")
    d.line(A.P(pts), fill=c + (255,), width=int(w * S), joint="curve")
    d.line(A.P([(x - 0.25 * w, y - 0.25 * w) for x, y in pts]), fill=tuple(min(255, v + 45) for v in c) + (255,), width=max(2, int(w * 0.35 * S)), joint="curve")


# ---------------------------------------------------------------- 3D helpers on the floor grid
# World axes: x toward the front right, y toward the back right, z up. The floor of A.floor() is 32 x 32 from O.
O = (3, 50)
EXV, EYV = (0.9, 0.45), (0.9, -0.45)
VIEW = np.array([1.0, -1.0, 0.9]) / np.linalg.norm([1.0, -1.0, 0.9])
LIGHT = np.array([-0.45, -1.0, 1.15]) / np.linalg.norm([-0.45, -1.0, 1.15])


def pr(x, y, z, o=O):
    return (o[0] + x * EXV[0] + y * EYV[0], o[1] + x * EXV[1] + y * EYV[1] - z)


def shade(base, n, amb=0.42, dif=0.72, spec=0.18):
    n = np.asarray(n, float)
    n = n / (np.linalg.norm(n) + 1e-9)
    lam = max(0.0, float(n @ LIGHT))
    h = (LIGHT + VIEW) / np.linalg.norm(LIGHT + VIEW)
    sp = max(0.0, float(n @ h)) ** 24 * spec
    return tuple(int(min(255, v * (amb + dif * lam) + 255 * sp)) for v in base)


def outlined(im, lay, px=0.8):
    im.alpha_composite(A.outline(lay.getchannel("A").point(lambda a: 255 if a > 40 else 0), px))
    im.alpha_composite(lay)


def box3(im, x, y, z, a, b, c, base, edge=0.9, noise=3, lines=True, o=O):
    """Box from (x, y, z) with size a (x), b (y), c (z), shaded from its colour."""
    L, F, R, Bk = pr(x, y, z + c, o), pr(x + a, y, z + c, o), pr(x + a, y + b, z + c, o), pr(x, y + b, z + c, o)
    top = (shade(base, (0, 0, 1)), shade(base, (0, 0, 1), 0.36))
    left = (shade(base, (0, -1, 0)), shade(base, (0, -1, 0), 0.3))
    right = (shade(base, (1, 0, 0)), shade(base, (1, 0, 0), 0.3))
    return A.iso_box(im, L, F, R, Bk, c, top, left, right, edge, noise)


def cyl(im, p0, axis, length, r, base, rings=(), cap=None, n=56, edge=0.8, spec=0.22, draw=True, o=O):
    """Cylinder from world point p0 along axis 'x', 'y' or 'z'. rings: (t 0..1, colour, width)."""
    k = "xyz".index(axis)
    u, v = [np.eye(3)[i] for i in range(3) if i != k]
    ax = np.eye(3)[k]
    p0 = np.asarray(p0, float)
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    angs = np.linspace(0, 2 * math.pi, n + 1)
    S2 = lambda p: pr(*p, o=o)
    for a0, a1 in zip(angs, angs[1:]):
        nm = u * math.cos((a0 + a1) / 2) + v * math.sin((a0 + a1) / 2)
        if nm @ VIEW <= -0.05:
            continue
        q0, q1 = r * (u * math.cos(a0) + v * math.sin(a0)), r * (u * math.cos(a1) + v * math.sin(a1))
        quad = [S2(p0 + q0), S2(p0 + q1), S2(p0 + q1 + ax * length), S2(p0 + q0 + ax * length)]
        c = shade(base, nm, spec=spec) + (255,)
        d.polygon(A.P(quad), fill=c, outline=c)
    a_view = math.atan2(v @ VIEW, u @ VIEW)  # the visible half of a ring, as one unbroken arc
    half = np.linspace(a_view - math.pi / 2, a_view + math.pi / 2, n // 2 + 1)
    for t, c, w in rings:
        pts = [S2(p0 + ax * length * t + r * 1.01 * (u * math.cos(a) + v * math.sin(a))) for a in half]
        if len(pts) > 1:
            d.line(A.P(pts), fill=c + (255,), width=int(w * S), joint="curve")
    for end, sgn in ((0, -1), (1, 1)):
        if ax @ VIEW * sgn > 0:
            ring = [S2(p0 + ax * length * end + r * (u * math.cos(a) + v * math.sin(a))) for a in angs]
            cc = cap or base
            d.polygon(A.P(ring), fill=shade(cc, ax * sgn, spec=0.05) + (255,), outline=A.INK + (255,), width=max(2, S // 3))
            ce = p0 + ax * length * end
    if draw:
        outlined(im, lay, edge)
    return lay


def terrain(im, f, x0, x1, y0, y1, n, color, skirt=None, edge=0.9, o=O, base_z=0.02, faces="xy"):
    """Height field z = f(x, y) drawn back to front, each cell shaded by its slope. color(x, y, z) -> rgb.
    skirt: colour of the cut faces at x = x1 and y = y0 (a block), or None (sits on the floor)."""
    xs, ys = np.linspace(x0, x1, n + 1), np.linspace(y0, y1, n + 1)
    Z = np.array([[f(x, y) for y in ys] for x in xs])
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    cells = sorted(((i, j) for i in range(n) for j in range(n)), key=lambda c: c[0] - (n - 1 - c[1]))
    cells = sorted(cells, key=lambda c: xs[c[0]] - ys[c[1]])
    for i, j in cells:
        if max(Z[i, j], Z[i + 1, j], Z[i, j + 1], Z[i + 1, j + 1]) <= base_z:
            continue
        p = [(xs[i], ys[j], Z[i, j]), (xs[i + 1], ys[j], Z[i + 1, j]), (xs[i + 1], ys[j + 1], Z[i + 1, j + 1]), (xs[i], ys[j + 1], Z[i, j + 1])]
        a, b, c = np.array(p[0]), np.array(p[1]), np.array(p[3])
        nm = np.cross(b - a, c - a)
        cx, cy, cz = np.mean(p, 0)
        col = shade(color(cx, cy, cz), nm, 0.4, 0.75, 0.06) + (255,)
        d.polygon(A.P([pr(*q, o=o) for q in p]), fill=col, outline=col)
    if skirt:
        def wall(a, b, za, zb, nm):
            top = max(za, zb)
            for z0 in np.arange(0, top, 0.5):
                z1 = min(top, z0 + 0.5)
                ta, tb = min(za, z1), min(zb, z1)
                if ta <= z0 and tb <= z0:
                    continue
                poly = [pr(*a, max(z0, 0), o=o), pr(*b, max(z0, 0), o=o), pr(*b, max(tb, z0), o=o), pr(*a, max(ta, z0), o=o)]
                c = shade(skirt((z0 + z1) / 2), nm, 0.45, 0.7, 0.0) + (255,)
                d.polygon(A.P(poly), fill=c, outline=c)
        if "y" in faces:
            for i in range(n):
                wall((xs[i], y0), (xs[i + 1], y0), Z[i, 0], Z[i + 1, 0], (0, -1, 0))
        if "x" in faces:
            for j in range(n):
                wall((x1, ys[j]), (x1, ys[j + 1]), Z[n, j], Z[n, j + 1], (1, 0, 0))
    outlined(im, lay, edge)
    return lay


def rock_heap(im, poly, base=(96, 88, 78), speck=ORE, n=120, seed=1):
    m = A.mask_of(lambda d: d.polygon(A.P(poly), fill=255))
    im.alpha_composite(A.outline(m, 0.9))
    im.alpha_composite(A.noisy(A.vgrad(m, tuple(int(v * 1.35) for v in base), base), 12, seed))
    rng = np.random.default_rng(seed)
    g = A.layer()
    d = ImageDraw.Draw(g)
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    for _ in range(n):
        x, y = rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))
        r = rng.uniform(0.5, 1.2)
        k = rng.uniform(0.7, 1.45)
        c = speck if rng.random() < 0.3 else tuple(int(v * k) for v in base)
        d.ellipse([(x - r) * S, (y - r * 0.8) * S, (x + r) * S, (y + r * 0.8) * S], fill=tuple(min(255, v) for v in c) + (255,), outline=INK + (200,), width=max(1, S // 5))
    g.putalpha(Image.fromarray(np.minimum(np.array(g.getchannel("A")), np.array(m)), "L"))
    im.alpha_composite(g)


# ---------------------------------------------------------------- I: in-situ leaching (well field over an ore layer)
def icon_1():
    im = A.layer()
    L, F, R, Bk, Ld, Fd, Rd = earth_slab(im)
    # processing tank and drum at the back
    A.ellipse_shadow(im, 40, 37, 7, 2.6)
    full, col = A.solid(39, 36, 13, 6, [(0, 1), (1, 1)], [(0, 1, (200, 206, 212), 0.5)], rings=[(0.5, (150, 156, 164))])
    A.place(im, full, col, 0.9)
    A.top_disc(im, 39, 23, 6, (214, 220, 226), (150, 156, 164))
    drum(im, 49, 41)
    # wells on the front edges: wellhead on top, casing visible down the cut face into the ore
    w1, w2 = A.lerp(L, F, 0.45), A.lerp(F, R, 0.42)
    for w, cap in ((w1, (70, 120, 200)), (w2, (80, 170, 80))):
        pipe(im, [(w[0], w[1] - 0.5), (w[0], w[1] + 9 * 0.62)], (150, 156, 164), 1.1)
        full, col = A.solid(w[0], w[1] - 0.5, 4, 1.6, [(0, 1), (1, 1)], [(0, 1, (176, 182, 190), 0.6)])
        A.place(im, full, col, 0.6)
        A.top_disc(im, w[0], w[1] - 4.5, 1.6, cap, A.INK[:3])
    # surface header pipes from the wells to the tank
    pipe(im, [(w1[0], w1[1] - 3.2), (w1[0] + 9, w1[1] - 7.7), (34.5, 34)], (170, 176, 184), 1.0)
    pipe(im, [(w2[0], w2[1] - 3.2), (w2[0] - 4, w2[1] - 5.2), (40, 34.5)], (170, 176, 184), 1.0)
    return im


# ---------------------------------------------------------------- II: high-yield milling (ball mill and yellowcake)
MILL = (100, 132, 112)
CONC = (170, 166, 154)


def yellow_pile(cx, cy, rx, ry, h, seed=5):
    rng = np.random.default_rng(seed)
    bumps = [(rng.uniform(-0.5, 0.5) * rx, rng.uniform(-0.5, 0.5) * ry, rng.uniform(0.2, 0.5) * h) for _ in range(4)]

    def f(x, y):
        q = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
        z = h * max(0.0, 1 - q) ** 0.9
        for bx, by, bh in bumps:
            z += bh * math.exp(-(((x - cx - bx) / (rx * 0.35)) ** 2 + ((y - cy - by) / (ry * 0.35)) ** 2)) * (q < 1)
        return z
    return f


def icon_2():
    im = A.layer()
    A.floor(im)
    Y = 3.0
    A.shadow(im, [pr(5, 4 + Y, 0), pr(25, 4 + Y, 0), pr(25, 27 + Y, 0), pr(5, 27 + Y, 0)], 150, 1.8)
    # concrete saddles under the shell
    box3(im, 8, 21 + Y, 0, 12, 3.4, 6.2, CONC, 0.8)
    # drive: motor and pinion beside the ring gear
    box3(im, 23, 17.5 + Y, 0, 6, 5, 4.6, (70, 92, 140), 0.8)
    cyl(im, (26, 18 + Y, 4.6), "z", 1.2, 1.8, (150, 156, 164))
    # shell in two parts around the ring gear, back to front
    cyl(im, (14, 18.6 + Y, 11), "y", 6.4, 7.6, MILL, rings=[(0.5, (60, 72, 64), 0.5)])
    cyl(im, (14, 17.2 + Y, 11), "y", 1.4, 9.0, (150, 120, 60), rings=[(0.25, (90, 70, 30), 0.35), (0.75, (90, 70, 30), 0.35)], cap=(170, 140, 70))
    box3(im, 8, 7 + Y, 0, 12, 3.4, 6.2, CONC, 0.8)
    cyl(im, (14, 6.2 + Y, 11), "y", 11.0, 7.6, MILL, rings=[(0.33, (60, 72, 64), 0.5), (0.66, (60, 72, 64), 0.5)], cap=(120, 150, 130))
    # bolt circle on the front head and the discharge trunnion
    d = ImageDraw.Draw(im)
    for k in range(10):
        a = k * 2 * math.pi / 10
        p = pr(14 + 5.6 * math.cos(a), 6.2 + Y, 11 + 5.6 * math.sin(a))
        d.ellipse([(p[0] - 0.45) * S, (p[1] - 0.45) * S, (p[0] + 0.45) * S, (p[1] + 0.45) * S], fill=(60, 72, 64, 255))
    cyl(im, (14, 2.6 + Y, 11), "y", 3.6, 2.6, (150, 156, 164), cap=(120, 126, 134))
    # chute from the trunnion down to the yellowcake pile
    c0, c1 = pr(14, 2.4 + Y, 9.2), pr(13, 0.8 + Y, 4.0)
    A.iso_box(im, (c0[0] - 1.3, c0[1]), (c0[0] + 0.3, c0[1] + 0.8), (c0[0] + 1.6, c0[1] + 0.1), (c0[0], c0[1] - 0.7), c0[1] - c1[1] + 1.5,
              ((150, 156, 164), (130, 136, 144)), ((120, 126, 134), (96, 100, 108)), ((96, 100, 108), (74, 78, 84)), 0.7)
    terrain(im, yellow_pile(12, 3.2, 7.5, 3.6, 4.2, 5), 3, 21, -0.5, 7.5, 28, lambda x, y, z: (246, 204, 64))
    # drum of concentrate
    drum(im, *pr(27, 6, 0))
    return im


# ---------------------------------------------------------------- III: automated mining (benched hill and driverless haul truck)
def bench_wall(x, y):
    """Open-pit wall rising toward the back in benches; the bench lines bend a little."""
    yy = y - 1.2 * math.sin(x / 6.1)
    lvl = np.clip((yy - 11.0) / 5.6, 0, 3.6)
    k = math.floor(lvl)
    fr = lvl - k
    return 5.0 * (k + min(1.0, fr / 0.3))


def hashn(x, y):
    v = math.sin(x * 12.9898 + y * 78.233) * 43758.5453
    return v - math.floor(v)


def strata(z):
    if 8.0 < z < 11.4:
        return (212, 176, 64)  # uranium-bearing sandstone
    if z < 4:
        return (118, 104, 86)
    return (150, 120, 84) if int(z / 2.2) % 2 else (134, 108, 76)


def wall_color(x, y, z):
    n = (hashn(round(x * 2) / 2, round(y * 2) / 2) - 0.5) * 18
    steep = abs(bench_wall(x, y + 0.2) - bench_wall(x, y - 0.2)) > 0.4
    if steep:
        c = tuple(int(v * 0.86) for v in strata(z))
    else:
        c = (196, 170, 70) if 8.0 < z < 11.4 else (176, 160, 128)  # dusty bench floor (haul road)
    return tuple(max(0, min(255, v + n)) for v in c)


def icon_3():
    im = A.layer()
    A.floor(im)
    terrain(im, bench_wall, 0, 32.2, 9, 32.2, 70, wall_color, skirt=strata, faces="x", edge=1.0)
    # driverless haul truck crossing the pit floor toward the front right
    TX, TY = 5.0, 1.2
    A.shadow(im, [pr(TX, TY - 0.5, 0), pr(TX + 19, TY - 0.5, 0), pr(TX + 19, TY + 10, 0), pr(TX, TY + 10, 0)], 170, 1.2)
    TRUCK = (242, 184, 40)
    for wx in (TX + 4.0, TX + 14.6):  # far wheels
        cyl(im, (wx, TY + 7.4, 3.3), "y", 1.8, 3.3, (54, 54, 56), cap=(46, 46, 48))
    box3(im, TX + 1, TY + 1.8, 2.6, 17, 6, 1.6, (92, 94, 98), 0.7)
    # dump body at the back, engine module (no cab) at the front
    box3(im, TX, TY + 0.8, 4.2, 12.4, 8.2, 5.4, TRUCK, 0.9)
    pile = yellow_pile(TX + 6.2, TY + 4.9, 6.2, 4.0, 3.4, 11)
    terrain(im, lambda x, y: 9.6 + pile(x, y), TX + 0.3, TX + 12.1, TY + 1.1, TY + 8.7, 26,
            lambda x, y, z: (226, 190, 70) if hashn(round(x * 1.5), round(y * 1.5)) > 0.72 else (128, 118, 104), base_z=9.62)
    box3(im, TX + 13, TY + 1.4, 4.2, 5.4, 7.0, 3.8, TRUCK, 0.9)
    d = ImageDraw.Draw(im)
    for k in range(5):  # radiator grille on the nose
        a, b = pr(TX + 18.4, TY + 2.4 + k * 1.2, 4.8), pr(TX + 18.4, TY + 2.4 + k * 1.2, 7.4)
        d.line(A.P([a, b]), fill=(120, 84, 16, 255), width=int(0.5 * S))
    for wx in (TX + 4.0, TX + 14.6):  # near wheels with hubs
        cyl(im, (wx, TY - 0.4, 3.3), "y", 1.9, 3.3, (56, 56, 58), cap=(40, 40, 42))
        p = pr(wx, TY - 0.4, 3.3)
        d = ImageDraw.Draw(im)
        d.ellipse([(p[0] - 1.2) * S, (p[1] - 1.2) * S, (p[0] + 1.2) * S, (p[1] + 1.2) * S], fill=(156, 160, 166, 255), outline=A.INK + (255,), width=S // 3)
    # sensor mast: lidar drum and an amber beacon where the cab would be
    cyl(im, (TX + 15.4, TY + 4.6, 8.0), "z", 3.0, 0.45, (60, 64, 70))
    cyl(im, (TX + 15.4, TY + 4.6, 11.0), "z", 1.6, 1.4, (44, 48, 54), rings=[(0.5, (120, 200, 230), 0.45)])
    A.glow(im, *pr(TX + 16.8, TY + 2.4, 8.6), 1.7, (255, 150, 40), 240)
    return im


# ---------------------------------------------------------------- IV: bioleaching (irrigated heap and lined solution pond)
SLAB = (3, 41)


def icon_4():
    im = A.layer()
    L, F, R, Bk, Ld, Fd, Rd = earth_slab(im)
    heap = [(9, 38), (18, 28), (34, 23), (48, 28), (52, 34), (40, 41), (22, 43)]
    rock_heap(im, heap, (110, 100, 86), ORE, 200, 9)
    d = ImageDraw.Draw(im)
    for k in range(4):
        a, b = (17 + k * 5, 37 - k * 1.5), (31 + k * 5, 31 - k * 1.5)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(0.6 * S))
        for t in (0.2, 0.5, 0.8):
            p = A.lerp(a, b, t)
            d.ellipse([(p[0] - 0.5) * S, (p[1] + 0.4) * S, (p[0] + 0.5) * S, (p[1] + 1.6) * S], fill=(120, 190, 240, 255))
    # lined collection pond sunk into the ground in front of the heap
    q = lambda x, y, z: pr(x, y, z, SLAB)
    x0, x1, y0, y1, dep, lev = 15, 29.5, 2.2, 12.5, 4.5, 2.3
    liner = (44, 46, 50)
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([q(x0, y1, 0), q(x1, y1, 0), q(x1, y1, -dep), q(x0, y1, -dep)]), fill=shade(liner, (0, -1, 0), 0.5) + (255,))
    dl.polygon(A.P([q(x0, y0, 0), q(x0, y1, 0), q(x0, y1, -dep), q(x0, y0, -dep)]), fill=shade(liner, (1, 0, 0), 0.5) + (255,))
    surf = [q(x0, y0, -lev), q(x1, y0, -lev), q(x1, y1, -lev), q(x0, y1, -lev)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(surf), fill=255))
    lay.alpha_composite(A.noisy(A.vgrad(m, (92, 168, 136), (46, 118, 100)), 5, 3))
    dl = ImageDraw.Draw(lay)
    # wet line on the liner just above the solution, and soft ripples
    dl.line(A.P([q(x0, y0, -lev + 0.5), q(x0, y1, -lev + 0.5), q(x1, y1, -lev + 0.5)]), fill=(90, 96, 100, 255), width=max(2, S // 3))
    for k in range(3):
        p = q(x0 + 3.5 + k * 3.8, y0 + 3 + k * 2, -lev)
        dl.arc([(p[0] - 2.2) * S, (p[1] - 0.7) * S, (p[0] + 2.2) * S, (p[1] + 0.7) * S], 200, 340, fill=(170, 220, 196, 255), width=max(2, S // 3))
    rim = A.mask_of(lambda dd: dd.polygon(A.P([q(x0, y0, 0), q(x1, y0, 0), q(x1, y1, 0), q(x0, y1, 0)]), fill=255))
    im.alpha_composite(A.outline(rim, 0.9))
    im.alpha_composite(lay)
    # berm on the front edges so the water sits below the rim
    for bx, by, ba, bb in ((x0 - 0.6, y0 - 1.2, x1 - x0 + 1.8, 1.2), (x1, y0 - 1.2, 1.2, y1 - y0 + 1.6)):
        L2, F2, R2, B2 = q(bx, by, 0.7), q(bx + ba, by, 0.7), q(bx + ba, by + bb, 0.7), q(bx, by + bb, 0.7)
        A.iso_box(im, L2, F2, R2, B2, 0.9, ((150, 140, 96), (130, 120, 80)), ((112, 100, 68), (92, 82, 54)), ((92, 82, 54), (72, 64, 42)), 0.6)
    # pipe from the heap toe into the pond, and the pump line out
    pipe(im, [q(12, 13.5, 0.6), q(16.5, 12.8, 0.6), q(18, 11, -0.6)], (60, 64, 70), 0.9)
    pipe(im, [q(27, 11, -0.6), q(30.5, 12.5, 1.2), q(31.5, 17, 1.2)], (60, 64, 70), 0.9)
    return im


# ---------------------------------------------------------------- V: seawater extraction (moored adsorbent braids, boat hauling one)
BRAID = (224, 200, 104)
SEA = (3, 37)


def braid(d, top, length, seed, w=1.7):
    """Thick twisted rope of adsorbent fibre hanging straight down."""
    pts = [(top[0] + 0.35 * math.sin(j * 0.9 + seed), top[1] + j * length / 8) for j in range(9)]
    d.line(A.P(pts), fill=INK + (255,), width=int((w + 0.9) * S), joint="curve")
    d.line(A.P(pts), fill=BRAID + (255,), width=int(w * S), joint="curve")
    d.line(A.P([(x - w * 0.22, y) for x, y in pts]), fill=(248, 236, 170, 255), width=max(2, int(w * 0.3 * S)), joint="curve")
    for j in range(1, int(length / 1.3)):  # twist
        y = top[1] + j * 1.3
        x = top[0] + 0.35 * math.sin((y - top[1]) / length * 8 * 0.9 + seed)
        d.line(A.P([(x - w * 0.45, y - 0.45), (x + w * 0.45, y + 0.45)]), fill=(150, 124, 46, 255), width=max(2, S // 3))


def hull(im, x0, x1, y0, y1, zt, base):
    """Boat hull with the bow toward +x, from the waterline (z = 0) up to the deck."""
    ym = (y0 + y1) / 2
    top = [(x0, y0), (x1 - 4, y0), (x1, ym), (x1 - 4, y1), (x0, y1)]
    bot = [(x0 + 0.6, y0 + 1.1), (x1 - 5, y0 + 1.1), (x1 - 1.6, ym), (x1 - 5, y1 - 1.1), (x0 + 0.6, y1 - 1.1)]
    q = lambda p, z: pr(p[0], p[1], z, SEA)
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    n = len(top)
    for i in range(n):
        a, b, c = np.array(top[i] + (zt,)), np.array(top[(i + 1) % n] + (zt,)), np.array(bot[i] + (0,))
        nm = np.cross(c - a, b - a)
        if nm @ VIEW <= 0:
            continue
        col = shade(base, nm) + (255,)
        d.polygon(A.P([q(top[i], zt), q(top[(i + 1) % n], zt), q(bot[(i + 1) % n], 0), q(bot[i], 0)]), fill=col, outline=col)
    d.polygon(A.P([q(p, zt) for p in top]), fill=shade((150, 140, 120), (0, 0, 1)) + (255,))
    d.line(A.P([q(p, zt) for p in top] + [q(top[0], zt)]), fill=(236, 236, 230, 255), width=int(0.5 * S))
    outlined(im, lay, 0.9)


def icon_5():
    im = A.layer()
    q = lambda x, y, z: pr(x, y, z, SEA)
    h = 14
    L, F, R, Bk = q(0, 0, 0), q(32.2, 0, 0), q(32.2, 32.2, 0), q(0, 32.2, 0)
    Ld, Fd, Rd = (L[0], L[1] + h), (F[0], F[1] + h), (R[0], R[1] + h)
    im.alpha_composite(A.outline(A.mask_of(lambda d: d.polygon(A.P([L, Bk, R, Rd, Fd, Ld]), fill=255)), 1.0))
    lf = A.mask_of(lambda d: d.polygon(A.P([L, F, Fd, Ld]), fill=255))
    rf = A.mask_of(lambda d: d.polygon(A.P([F, R, Rd, Fd]), fill=255))
    im.alpha_composite(A.vgrad(lf, (70, 150, 196), (20, 62, 104)))
    im.alpha_composite(A.vgrad(rf, (52, 122, 170), (14, 46, 84)))
    for a, b, ad, bd, k in ((L, F, Ld, Fd, 1.0), (F, R, Fd, Rd, 0.8)):
        strip(im, a, b, ad, bd, 0.86, 1.0, tuple(int(v * k) for v in (182, 162, 112)), 6)
    # three moorings per cut face: float on top, braid down, concrete anchor on the sea floor
    d = ImageDraw.Draw(im)
    tops = [A.lerp(L, F, t) for t in (0.2, 0.5, 0.8)] + [A.lerp(F, R, t) for t in (0.2, 0.5, 0.8)]
    for k, p in enumerate(tops):
        bottom = (p[0], p[1] + h * 0.86)
        d.line(A.P([(p[0], p[1] + h * 0.7), bottom]), fill=(40, 40, 40, 255), width=max(2, S // 3))
        A.iso_box(im, (bottom[0] - 1.6, bottom[1] - 1.2), (bottom[0], bottom[1] - 0.4), (bottom[0] + 1.6, bottom[1] - 1.2), (bottom[0], bottom[1] - 2.0), 1.4,
                  ((150, 150, 146), (130, 130, 126)), ((116, 116, 112), (96, 96, 92)), ((96, 96, 92), (76, 76, 72)), 0.5)
        d = ImageDraw.Draw(im)
        braid(d, (p[0], p[1] + 0.8), h * 0.66, k)
    # sea surface with soft swell
    top = A.mask_of(lambda dd: dd.polygon(A.P([L, F, R, Bk]), fill=255))
    im.alpha_composite(A.noisy(A.vgrad(top, (104, 172, 212), (64, 128, 184)), 5, 4))
    d = ImageDraw.Draw(im)
    d.line(A.P([L, F, R]), fill=(206, 236, 250, 255), width=int(0.6 * S))
    for x, y in ((6, 6), (12, 26), (4, 18), (26, 28), (20, 4)):
        p = q(x, y, 0)
        d.arc([(p[0] - 2.4) * S, (p[1] - 0.8) * S, (p[0] + 2.4) * S, (p[1] + 0.8) * S], 200, 340, fill=(196, 230, 246, 255), width=max(2, S // 3))
    # floats and the line joining them
    pipe(im, [tops[0], tops[2], F, tops[5]], (80, 80, 76), 0.45)
    for p in tops:
        full, col = A.solid(p[0], p[1] + 0.8, 2.8, 2.1, [(0, 1), (0.75, 1), (1, 0.55)], [(0, 1, (240, 128, 36), 0.6)], rings=[(0.45, (250, 240, 230))])
        A.place(im, full, col, 0.6)
    # work boat at the back hauling a loaded braid aboard
    hull(im, 2, 27, 15, 27, 3.6, (214, 70, 54))
    box3(im, 3, 17, 3.6, 6.4, 8, 6.2, (236, 236, 232), 0.8, o=SEA)
    box3(im, 4, 18.4, 9.8, 4.2, 5.2, 1.0, (60, 64, 72), 0.6, o=SEA)
    d = ImageDraw.Draw(im)
    for k in range(3):
        a = pr(9.4, 18.4 + k * 2.0, 7.4, SEA)
        d.line(A.P([a, (a[0], a[1] - 1.8)]), fill=(40, 70, 110, 255), width=int(1.0 * S))
    drum(im, *q(13.5, 22, 3.6), 5.0, 2.2)
    cyl(im, (21, 21, 3.6), "z", 12.0, 0.85, (238, 184, 40), o=SEA)
    base, tip = q(21, 21, 15.2), q(31.5, 22, 14.2)
    d = ImageDraw.Draw(im)
    d.line(A.P([base, tip]), fill=INK + (255,), width=int(2.4 * S))
    d.line(A.P([base, tip]), fill=(238, 184, 40, 255), width=int(1.3 * S))
    d.line(A.P([tip, (tip[0], tip[1] + 2.5)]), fill=INK + (255,), width=int(0.45 * S))
    braid(d, (tip[0], tip[1] + 2.5), 12.0, 2, 1.8)
    for k in range(3):  # sea water dripping off it
        p = (tip[0] + 0.4 * (k - 1), tip[1] + 15.8 + k * 1.3)
        d.ellipse([(p[0] - 0.4) * S, (p[1] - 0.55) * S, (p[0] + 0.4) * S, (p[1] + 0.55) * S], fill=(206, 236, 250, 255))
    return im


ROMAN = ["I", "II", "III", "IV", "V"]
DRAW = [icon_1, icon_2, icon_3, icon_4, icon_5]
if __name__ == "__main__":
    preview = Image.new("RGBA", (5 * 70 + 6, 76), (52, 58, 52, 255))
    for i, draw in enumerate(DRAW):
        big = draw()
        trefoil_badge(big)
        big.alpha_composite(A.numeral(ROMAN[i]))
        icon = big.resize((N, N), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=0))
        A.save_dds(icon, f"gfx/interface/technologies/mdr/mdr_uranium_tech_{i + 1}.dds")
        preview.alpha_composite(icon, (6 + i * 70, 6))
    if len(sys.argv) > 1:
        preview.save(sys.argv[1])
    print("5 uranium icons written")
