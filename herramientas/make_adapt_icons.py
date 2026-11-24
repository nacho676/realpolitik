# Climate adaptation research icons (mdr_adapt_tech_1..7): one scene per technology, in the style of make_ammo_icons.py,
# using the 3D helpers of make_uranium_icons.py and the pieces of make_clean_icons.py. Drawn at 8x and reduced to 64x64.
# Writes gfx/interface/technologies/mdr/mdr_adapt_tech_<n>.dds. make_tech_lines.py does not redraw these.
# Run from the mod folder: python herramientas/make_adapt_icons.py [preview.png]
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
GEO = (3, 37)


def house(im, x, y, z, a, b, h, wall, roof, o=U.O):
    """Small house with a pitched roof (ridge along x)."""
    box3(im, x, y, z, a, b, h, wall, 0.7, o=o)
    ridge = z + h + b * 0.45
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    front = [pr(x, y, z + h, o), pr(x + a, y, z + h, o), pr(x + a, y + b / 2, ridge, o), pr(x, y + b / 2, ridge, o)]
    gable = [pr(x + a, y, z + h, o), pr(x + a, y + b, z + h, o), pr(x + a, y + b / 2, ridge, o)]
    d.polygon(A.P(front), fill=shade(roof, (0, -1, 1.1)) + (255,))
    d.polygon(A.P(gable), fill=shade(wall, (1, 0, 0)) + (255,))
    U.outlined(im, lay, 0.7)


# ---------------------------------------------------------------- I: risk mapping (relief model with flood and fire zones marked)
def river_y(x):
    return 11 + 3.5 * math.sin(x / 5.5)


def relief(x, y):
    dd = abs(y - river_y(x))
    if dd < 1.3:
        return 3.6
    h = 3.6 + 0.22 * (dd - 1.3) ** 1.25
    h += 6.5 * math.exp(-((x - 8) ** 2 + (y - 25) ** 2) / 34) + 5.0 * math.exp(-((x - 25) ** 2 + (y - 27) ** 2) / 26)
    return h


def relief_color(x, y, z):
    dd = abs(y - river_y(x))
    if dd < 1.3:
        return (70, 140, 204)
    if dd < 5.2:
        return (214, 92, 70) if U.hashn(round(x * 1.5), round(y * 1.5)) > 0.25 else (196, 120, 90)  # flood zone
    if z > 9.0:
        return (236, 150, 52)  # wildfire zone on the dry hills
    return (126, 156, 86) if z < 6.2 else (150, 160, 96)


def icon_1():
    im = A.layer()
    A.floor(im)
    A.shadow(im, [pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 32.2, 0), pr(0, 32.2, 0)], 150, 1.6)
    # wooden plinth of the planning model, then the relief on it
    box3(im, 1, 1, 0, 30.2, 30.2, 3.0, (150, 104, 62), 0.9, 6)
    U.terrain(im, relief, 2, 30.2, 2, 30.2, 52, relief_color, skirt=lambda z: (176, 150, 112) if z > 3.0 else (150, 104, 62), edge=0.9)
    # marker pins on the threatened places
    for px, py, c in ((10, 15.5, (220, 40, 40)), (20, 8.5, (220, 40, 40)), (9, 25, (250, 170, 40))):
        z = relief(px, py)
        d = ImageDraw.Draw(im)
        a, b = pr(px, py, z), pr(px, py, z + 4.8)
        d.line(A.P([a, b]), fill=INK + (255,), width=int(0.7 * S))
        d.line(A.P([a, b]), fill=(200, 204, 210, 255), width=max(2, int(0.3 * S)))
        dot(d, pr(px, py, z + 4.8), 1.1, c, INK[:3])
    return im


# ---------------------------------------------------------------- IV: coastal and river defenses (dike holding the sea above the land)
SEA_LEVEL = 7.0


def dike(x, y):
    if y >= 19:
        return 1.5  # sea bed
    if y >= 15.5:
        return 1.5 + (19 - y) / 3.5 * 8.5  # sea-side slope
    if y >= 13.5:
        return 10.0  # crest
    if y >= 9.5:
        return 10.0 - (13.5 - y) / 4 * 6  # land-side slope
    return 4.0  # polder


def dike_color(x, y, z):
    if y >= 19:
        return (184, 166, 118)
    if y >= 15.5:
        return (150, 146, 136) if z < SEA_LEVEL + 0.6 else (160, 158, 150)  # stone revetment
    if y >= 13.5:
        return (120, 118, 112)  # road on the crest
    if y >= 9.5:
        return (108, 156, 76)
    return (118, 160, 80) if U.hashn(round(x / 3), round(y / 3)) > 0.4 else (150, 168, 84)


def icon_4():
    im = A.layer()
    soil = lambda z: (150, 120, 84) if z > 3 else (120, 100, 76)
    # sea side first, then the water, then the dike and the land in front of it
    U.terrain(im, dike, 0, 32.2, 16, 32.2, 40, dike_color, skirt=soil, faces="x", edge=0.9)
    top = [pr(0, 16.6, SEA_LEVEL), pr(32.2, 16.6, SEA_LEVEL), pr(32.2, 32.2, SEA_LEVEL), pr(0, 32.2, SEA_LEVEL)]
    side = [pr(32.2, 16.6, SEA_LEVEL), pr(32.2, 32.2, SEA_LEVEL), pr(32.2, 32.2, 1.5), pr(32.2, 16.6, 1.5)]
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    d.polygon(A.P(side), fill=(40, 96, 150, 215))
    m = A.mask_of(lambda dd: dd.polygon(A.P(top), fill=255))
    lay.alpha_composite(A.noisy(A.vgrad(m, (96, 162, 206), (66, 128, 184)), 4, 4))
    d = ImageDraw.Draw(lay)
    for x, y in ((8, 26), (20, 29), (26, 21), (4, 20)):
        p = pr(x, y, SEA_LEVEL)
        d.arc([(p[0] - 2.2) * S, (p[1] - 0.7) * S, (p[0] + 2.2) * S, (p[1] + 0.7) * S], 200, 340, fill=(206, 236, 250, 255), width=max(2, S // 3))
    d.line(A.P([pr(32.2, 16.6, SEA_LEVEL), pr(32.2, 32.2, SEA_LEVEL)]), fill=(206, 236, 250, 255), width=int(0.5 * S))
    im.alpha_composite(A.outline(lay.getchannel("A").point(lambda a: 255 if a > 40 else 0), 0.9))
    im.alpha_composite(lay)
    U.terrain(im, dike, 0, 32.2, 0, 16.6, 44, dike_color, skirt=soil, faces="xy", edge=0.9)
    # concrete crown wall on the sea edge of the crest
    box3(im, 0.4, 15.0, 10.0, 31.6, 0.9, 1.8, CONC, 0.7)
    # houses on the polder, well below the sea outside
    house(im, 4, 3, 4, 5, 4.5, 3.4, (226, 220, 206), (176, 70, 52))
    house(im, 13, 4.5, 4, 5, 4.5, 3.4, (214, 208, 190), (150, 70, 56))
    house(im, 22, 2.5, 4, 5, 4.5, 3.4, (226, 220, 206), (176, 70, 52))
    return im


# ---------------------------------------------------------------- VII: precision climate modelling (supercomputer hall and weather radar)
def radome(im, x, y, z, r):
    c = pr(x, y, z)
    prof = [(t, math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))) for t in np.linspace(0, 1, 15)]
    prof[0] = (0, 0.35)
    full, col = A.solid(c[0], c[1] + r * 0.2, 2 * r, r, prof, [(0, 1, (236, 238, 240), 0.35)])
    A.place(im, full, col, 0.9)
    d = ImageDraw.Draw(im)
    for f in (0.35, 0.65):  # panel seams
        yy = c[1] + r * 0.2 - 2 * r * f
        w = r * math.sqrt(max(0.0, 1 - (2 * f - 1) ** 2))
        d.arc([(c[0] - w) * S, (yy - w * A.TILT) * S, (c[0] + w) * S, (yy + w * A.TILT) * S], 0, 180, fill=(170, 176, 184, 255), width=max(2, S // 4))


def icon_7():
    im = A.layer()
    A.floor_dark(im)
    # weather radar on its tower at the back
    for lx, ly in ((22, 22), (27, 22), (22, 27), (27, 27)):
        cyl(im, (lx, ly, 0), "z", 13, 0.45, (150, 156, 166))
    box3(im, 21.5, 21.5, 13, 6, 6, 1.4, (150, 156, 166), 0.7)
    radome(im, 24.5, 24.5, 14.4, 5.2)
    # rows of supercomputer cabinets
    A.shadow(im, [pr(2, 3, 0), pr(20, 3, 0), pr(20, 17, 0), pr(2, 17, 0)], 170, 1.4)
    for ry in (12.5, 4.0):
        for k in range(4):
            x = 2.5 + k * 4.3
            box3(im, x, ry, 0, 3.9, 4.4, 11, (52, 58, 70), 0.7)
            d = ImageDraw.Draw(im)
            for j in range(5):  # status lights on the doors
                a = pr(x + 0.8, ry, 1.6 + j * 2.0)
                b = pr(x + 3.1, ry, 1.6 + j * 2.0)
                d.line(A.P([a, b]), fill=(70, 80, 96, 255), width=max(2, S // 4))
                dot(d, A.lerp(a, b, 0.15), 0.3, A.CYAN if (j + k) % 3 else (120, 230, 120))
    # cooling pipes from the cabinets to a chiller
    box3(im, 22, 4, 0, 7, 6, 4.5, (120, 130, 144), 0.8)
    d = ImageDraw.Draw(im)
    for k in range(2):
        c = pr(24 + k * 3, 7, 4.5)
        d.ellipse([(c[0] - 1.2) * S, (c[1] - 0.6) * S, (c[0] + 1.2) * S, (c[1] + 0.6) * S], fill=(34, 38, 44, 255), outline=INK + (255,), width=max(2, S // 4))
    pipe3(im, [(19.8, 6, 8), (22, 6, 8), (22, 6, 4.5)], (90, 150, 210), 1.0)
    return im


# ---------------------------------------------------------------- shared pieces
def flood_floor(im, level=0.0, o=U.O):
    """Whole floor tile as flood water."""
    L, F, R, Bk = pr(0, 0, level, o), pr(32.2, 0, level, o), pr(32.2, 32.2, level, o), pr(0, 32.2, level, o)
    m = A.mask_of(lambda d: d.polygon(A.P([L, F, R, Bk]), fill=255))
    im.alpha_composite(A.outline(m, 0.8))
    im.alpha_composite(A.noisy(A.vgrad(m, (110, 150, 170), (70, 110, 140)), 4, 9))
    d = ImageDraw.Draw(im)
    for x, y in ((5, 5), (14, 3), (25, 6), (4, 16), (28, 26), (12, 28)):
        p = pr(x, y, level, o)
        d.arc([(p[0] - 2.2) * S, (p[1] - 0.7) * S, (p[0] + 2.2) * S, (p[1] + 0.7) * S], 200, 340, fill=(196, 222, 236, 255), width=max(2, S // 3))


def tree(im, x, y, z, h, r, crown=(86, 140, 62), o=U.O):
    a, b = pr(x, y, z, o), pr(x, y, z + h, o)
    d = ImageDraw.Draw(im)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(1.2 * S))
    d.line(A.P([a, b]), fill=(110, 80, 50, 255), width=int(0.6 * S))
    prof = [(t, math.sqrt(max(0.0, 1 - (2 * t - 1) ** 2))) for t in np.linspace(0, 1, 13)]
    prof[0] = (0, 0.3)
    full, col = A.solid(b[0], b[1] + r * 0.6, 2 * r, r, prof, [(0, 1, crown, 0.15)])
    A.place(im, full, A.noisy(col, 10, int(x * 7 + y)), 0.7)


def shutter_window(im, x0, y, z, w=2.2, hgt=3.0, o=U.O):
    d = ImageDraw.Draw(im)
    a, b = pr(x0, y, z, o), pr(x0 + w, y, z, o)
    d.polygon(A.P([a, b, (b[0], b[1] + hgt), (a[0], a[1] + hgt)]), fill=(52, 92, 70, 255), outline=INK + (255,), width=max(2, S // 4))
    for k in range(1, 5):  # slats
        t = k / 5 * hgt
        d.line(A.P([(a[0], a[1] + t), (b[0], b[1] + t)]), fill=(90, 140, 110, 255), width=max(2, S // 4))


# ---------------------------------------------------------------- II: climate building codes (house on piers, cool roof, storm shutters)
def icon_2():
    im = A.layer()
    flood_floor(im)
    # concrete piers standing in the flood water
    for px in (6.5, 14, 21.5):
        for py in (21, 9):
            cyl(im, (px, py, 0), "z", 5.0, 0.9, CONC)
    # two-storey house with a white reflective roof and shuttered windows
    X, Y, Z, a, b, h = 5, 8, 5.0, 18, 14, 9.5
    box3(im, X, Y, Z, a, b, h, (232, 214, 170), 0.9)
    ridge = Z + h + b * 0.4
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    front = [pr(X - 0.6, Y - 0.6, Z + h), pr(X + a + 0.6, Y - 0.6, Z + h), pr(X + a + 0.6, Y + b / 2, ridge), pr(X - 0.6, Y + b / 2, ridge)]
    gable = [pr(X + a, Y, Z + h), pr(X + a, Y + b, Z + h), pr(X + a, Y + b / 2, ridge)]
    d.polygon(A.P(gable), fill=shade((232, 214, 170), (1, 0, 0)) + (255,))
    d.polygon(A.P(front), fill=shade((240, 242, 244), (0, -1, 1.1)) + (255,))
    for k in range(1, 6):  # standing seams of the metal roof
        t = k / 6
        d.line(A.P([A.lerp(front[0], front[1], t), A.lerp(front[3], front[2], t)]), fill=(196, 200, 206, 255), width=max(2, S // 4))
    U.outlined(im, lay, 0.8)
    for k in range(4):
        shutter_window(im, X + 1.3 + k * 4.3, Y, Z + 7.6)
        shutter_window(im, X + 1.3 + k * 4.3, Y, Z + 3.4)
    d = ImageDraw.Draw(im)
    a0, b0 = pr(X + a, Y + 5.5, Z + 6.5), pr(X + a, Y + 8.5, Z + 6.5)  # side door
    d.polygon(A.P([a0, b0, (b0[0], b0[1] + 6.5), (a0[0], a0[1] + 6.5)]), fill=(120, 76, 46, 255), outline=INK + (255,), width=max(2, S // 4))
    # steps down to the water
    for k in range(4):
        box3(im, X + a + 0.2, Y + 5.3, Z - 1.25 - k * 1.25, 1.6 + k * 1.3, 3.4, 1.25, CONC, 0.5)
    return im


# ---------------------------------------------------------------- III: satellite early warning (satellite, ground station dish, siren)
def dish(im, c, nrm, r, o=U.O):
    nrm = np.asarray(nrm, float)
    nrm /= np.linalg.norm(nrm)
    u = np.cross(nrm, [0, 0, 1.0])
    u /= np.linalg.norm(u)
    v = np.cross(nrm, u)
    c = np.asarray(c, float)
    rim = [pr(*(c + r * (u * math.cos(a) + v * math.sin(a))), o) for a in np.linspace(0, 2 * math.pi, 48)]
    inner = [pr(*(c - nrm * r * 0.25 + r * 0.6 * (u * math.cos(a) + v * math.sin(a))), o) for a in np.linspace(0, 2 * math.pi, 48)]
    lay = A.layer()
    m = A.mask_of(lambda d: d.polygon(A.P(rim), fill=255))
    lay.alpha_composite(A.vgrad(m, (236, 238, 242), (176, 182, 190)))
    m2 = A.mask_of(lambda d: d.polygon(A.P(inner), fill=255))
    lay.alpha_composite(A.vgrad(m2, (196, 200, 208), (150, 156, 166)))
    U.outlined(im, lay, 0.8)
    feed = pr(*(c + nrm * r * 0.7), o)
    d = ImageDraw.Draw(im)
    for a in (0, 2.1, 4.2):
        p = pr(*(c + r * 0.9 * (u * math.cos(a) + v * math.sin(a))), o)
        d.line(A.P([p, feed]), fill=(90, 96, 104, 255), width=max(2, S // 3))
    dot(d, feed, 0.8, (90, 96, 104), INK[:3])
    return feed


def icon_3():
    im = A.layer()
    A.floor(im)
    # control building at the back left
    box3(im, 1, 18, 0, 10, 11, 6.5, (220, 222, 224), 0.9)
    windows(im, 2.4, 18, 5.0, 3, 3.0, 1.8, 2.2, c=(70, 120, 170))
    # ground station dish on its pedestal, aimed at the satellite
    A.ellipse_shadow(im, *pr(19, 15, 0), 6, 2.4)
    box3(im, 16.5, 12.5, 0, 5, 5, 2.0, CONC, 0.7)
    cyl(im, (19, 15, 2.0), "z", 6.5, 1.3, (150, 156, 164))
    feed = dish(im, (19, 15, 12.0), (-0.75, 0.25, 0.62), 7.0)
    # warning siren on a mast at the front
    cyl(im, (8, 5, 0), "z", 14, 0.4, (120, 126, 134))
    for k, dz in enumerate((14.2, 12.6)):
        cyl(im, (8.4, 5, dz), "x", 2.4, 0.75 + 0.1 * k, (226, 70, 50), cap=(40, 40, 44))
    # satellite in orbit above the scene, with the signal down to the dish
    sat = (4.5, 24, 28.5)
    sp = pr(*sat)
    d = ImageDraw.Draw(im)
    for k in range(5):  # dashed downlink
        t0, t1 = 0.12 + k * 0.17, 0.2 + k * 0.17
        d.line(A.P([A.lerp(sp, feed, t0), A.lerp(sp, feed, t1)]), fill=(240, 220, 90, 255), width=int(0.6 * S))
    for sx in (-1, 1):
        x0 = sat[0] + (1.7 if sx > 0 else -8.7)
        quad = [pr(x0, sat[1] - 0.2, sat[2] + 2.0), pr(x0 + 7, sat[1] - 0.2, sat[2] + 2.0), pr(x0 + 7, sat[1] + 3.8, sat[2] + 2.0), pr(x0, sat[1] + 3.8, sat[2] + 2.0)]
        d = ImageDraw.Draw(im)
        d.polygon(A.P(quad), fill=(40, 58, 110, 255), outline=INK + (255,), width=max(2, S // 3))
        for k in range(1, 4):
            d.line(A.P([A.lerp(quad[0], quad[1], k / 4), A.lerp(quad[3], quad[2], k / 4)]), fill=(120, 150, 210, 255), width=max(2, S // 4))
    box3(im, sat[0] - 1.7, sat[1] - 0.2, sat[2], 3.4, 4.0, 4.0, (214, 170, 70), 0.7)
    cyl(im, (sat[0], sat[1] + 1.8, sat[2] - 1.4), "z", 1.4, 0.9, (200, 204, 210))
    return im


# ---------------------------------------------------------------- V: sponge city (park soaking up rain, gravel bed and cistern underneath)
def icon_5():
    im = A.layer()
    q = lambda x, y, z: pr(x, y, z, GEO)
    h = 14
    L, F, R, Bk = q(0, 0, 0), q(32.2, 0, 0), q(32.2, 32.2, 0), q(0, 32.2, 0)
    Ld, Fd, Rd = A.iso_box(im, L, F, R, Bk, h, ((118, 164, 80), (100, 146, 66)), ((120, 96, 66), (96, 74, 50)), ((96, 76, 52), (74, 58, 40)), 1.0, 5)
    bands = [(0.0, 0.14, (92, 70, 48)), (0.14, 0.4, (150, 146, 140)), (0.4, 1.0, (134, 106, 74))]
    for a, b, ad, bd, k in ((L, F, Ld, Fd, 1.0), (F, R, Fd, Rd, 0.8)):
        for t0, t1, c in bands:
            U.strip(im, a, b, ad, bd, t0, t1, tuple(int(v * k) for v in c), int(t0 * 10) + 3)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(5)
    for a, b, ad, bd in ((L, F, Ld, Fd), (F, R, Fd, Rd)):  # gravel stones
        for _ in range(40):
            u, v = rng.uniform(0.03, 0.97), rng.uniform(0.17, 0.37)
            dot(d, A.lerp(A.lerp(a, b, u), A.lerp(ad, bd, u), v), rng.uniform(0.3, 0.6), (190, 186, 178), (110, 106, 100))

    def face_pt(u, v):
        return A.lerp(A.lerp(L, F, u), A.lerp(Ld, Fd, u), v)
    # underground cistern seen in the cut, holding the stored rain
    tank = [face_pt(0.2, 0.47), face_pt(0.8, 0.47), face_pt(0.8, 0.88), face_pt(0.2, 0.88)]
    d.polygon(A.P(tank), fill=(60, 64, 70, 255), outline=INK + (255,), width=max(2, S // 3))
    water = [face_pt(0.22, 0.6), face_pt(0.78, 0.6), face_pt(0.78, 0.86), face_pt(0.22, 0.86)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(water), fill=255))
    im.alpha_composite(A.vgrad(m, (90, 166, 214), (40, 100, 160)))
    d = ImageDraw.Draw(im)
    for u in (0.35, 0.5, 0.65):  # water seeping down through the gravel
        for v in (0.18, 0.28, 0.38):
            p = face_pt(u + v * 0.05, v)
            d.ellipse([(p[0] - 0.4) * S, (p[1] - 0.6) * S, (p[0] + 0.4) * S, (p[1] + 0.6) * S], fill=(110, 180, 230, 255))
    d.line(A.P([Ld, Fd, Rd]), fill=INK + (255,), width=int(0.8 * S))
    # rain garden: sunken bed with water and reeds
    rg = [q(14, 4, 0), q(26, 4, 0), q(26, 12, 0), q(14, 12, 0)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(rg), fill=255))
    im.alpha_composite(A.outline(m, 0.6))
    im.alpha_composite(A.vgrad(m, (90, 156, 196), (70, 130, 176)))
    d = ImageDraw.Draw(im)
    for k in range(9):
        p = q(15 + (k * 3.7) % 10.5, 5 + (k * 2.3) % 6.5, 0)
        d.line(A.P([p, (p[0] + 0.3, p[1] - 2.4)]), fill=(60, 110, 50, 255), width=max(2, S // 3))
    # permeable paving path and an apartment block at the back
    path = [q(2, 14, 0), q(30, 14, 0), q(30, 17, 0), q(2, 17, 0)]
    d.polygon(A.P(path), fill=(176, 170, 156, 255))
    for k in range(14):
        dot(d, q(3 + k * 2, 15.5, 0), 0.35, (120, 116, 106))
    box3(im, 16, 21, 0, 13, 9, 13, (214, 206, 190), 0.9, o=GEO)
    windows(im, 17.3, 21, 11.2, 4, 3.0, 1.8, 2.0, o=GEO)
    windows(im, 17.3, 21, 6.8, 4, 3.0, 1.8, 2.0, o=GEO)
    for tx, ty in ((5, 24), (8, 8), (4, 4)):
        tree(im, tx, ty, 0, 4.0, 3.4, o=GEO)
    # rain falling on the park
    d = ImageDraw.Draw(im)
    for k in range(14):
        x, y = 6 + (k * 7.3) % 44, 6 + (k * 5.1) % 14
        d.line(A.P([(x, y), (x - 0.8, y + 2.2)]), fill=(150, 200, 236, 255), width=max(2, S // 3))
    return im


# ---------------------------------------------------------------- VI: resilient infrastructure (raised highway and hardened pylon over a flood)
def pylon(im, x, y, z0, hgt):
    d = ImageDraw.Draw(im)
    base, top = 2.6, 0.7
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    pt = lambda c, f: pr(x + c[0] * (base + (top - base) * f), y + c[1] * (base + (top - base) * f), z0 + hgt * f)
    lines = [[pt(c, 0), pt(c, 1)] for c in corners]
    for c0, c1 in ((corners[0], corners[1]), (corners[1], corners[2])):  # bracing on the two faces we see
        for k in range(5):
            f0, f1 = k / 5, (k + 1) / 5
            lines.append([pt(c0, f0), pt(c1, f1)])
            lines.append([pt(c1, f0), pt(c0, f1)])
    arms = ((0.72, 6.5), (0.92, 5.0))
    for f, arm in arms:  # cross-arms along x
        zc = z0 + hgt * f
        lines.append([pr(x - arm, y, zc), pr(x + arm, y, zc)])
    for ln in lines:
        d.line(A.P(ln), fill=INK + (255,), width=int(0.9 * S))
    for ln in lines:
        d.line(A.P(ln), fill=(176, 182, 190, 255), width=max(2, int(0.42 * S)))
    for f, arm in arms:  # insulators
        zc = z0 + hgt * f
        for sx in (-1, 1):
            p = pr(x + sx * arm, y, zc)
            d.line(A.P([p, (p[0], p[1] + 1.4)]), fill=(80, 120, 170, 255), width=int(0.5 * S))


def icon_6():
    im = A.layer()
    flood_floor(im)
    # hardened pylon on a raised concrete plinth at the back
    box3(im, 18, 20, 0, 9, 9, 3.0, CONC, 0.8)
    pylon(im, 22.5, 24.5, 3.0, 22)
    # substation on a raised platform at the back left
    box3(im, 1, 18, 0, 12, 12, 3.0, CONC, 0.8)
    for k in range(3):
        cyl(im, (3.5 + k * 3.6, 24, 3.0), "z", 3.2, 1.1, (130, 136, 146), rings=[(0.5, (90, 96, 104), 0.4)])
    box3(im, 2.4, 19, 3.0, 4.2, 3.2, 2.8, (90, 110, 150), 0.6)
    # elevated highway on piers, crossing in front, with traffic
    for px in (3, 13, 23):
        cyl(im, (px, 9.5, 0), "z", 7.5, 1.1, CONC)
    box3(im, 0, 6.5, 7.5, 32.2, 6.0, 1.8, (150, 150, 146), 0.9)
    d = ImageDraw.Draw(im)
    d.line(A.P([pr(0, 9.5, 9.32), pr(32.2, 9.5, 9.32)]), fill=(236, 220, 120, 255), width=max(2, S // 3))
    box3(im, 0, 6.5, 9.3, 32.2, 0.4, 0.9, (196, 196, 190), 0.5)
    box3(im, 6, 7.2, 9.3, 4.2, 2.0, 1.6, (200, 60, 50), 0.6)
    box3(im, 18, 10.0, 9.3, 4.6, 2.0, 1.7, (60, 110, 180), 0.6)
    return im


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII"]
DRAW = [icon_1, icon_2, icon_3, icon_4, icon_5, icon_6, icon_7]
if __name__ == "__main__":
    preview = Image.new("RGBA", (7 * 70 + 6, 76), (52, 58, 52, 255))
    for i, draw in enumerate(DRAW):
        big = draw()
        big.alpha_composite(A.numeral(ROMAN[i]))
        icon = big.resize((N, N), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=0))
        A.save_dds(icon, f"gfx/interface/technologies/mdr/mdr_adapt_tech_{i + 1}.dds")
        preview.alpha_composite(icon, (6 + i * 70, 6))
    if len(sys.argv) > 1:
        preview.save(sys.argv[1])
    print("7 climate adaptation icons written")
