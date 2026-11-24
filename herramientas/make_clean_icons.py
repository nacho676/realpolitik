# Clean technology research icons (mdr_clean_tech_1..10): one scene per technology, in the style of make_ammo_icons.py
# and make_uranium_icons.py (whose 3D helpers it uses), drawn at 8x and reduced to 64x64.
# Writes gfx/interface/technologies/mdr/mdr_clean_tech_<n>.dds. make_tech_lines.py does not redraw these.
# Run from the mod folder: python herramientas/make_clean_icons.py [preview.png]
import math
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_ammo_icons as A  # noqa: E402
import make_uranium_icons as U  # noqa: E402

S, N, INK = A.S, A.N, A.INK
pr, box3, cyl, pipe, shade = U.pr, U.box3, U.cyl, U.pipe, U.shade
BRICK = (168, 86, 62)
STEEL = (176, 182, 190)
CONC = (176, 172, 160)


def dot(d, p, r, fill, outline=None):
    d.ellipse([(p[0] - r) * S, (p[1] - r) * S, (p[0] + r) * S, (p[1] + r) * S], fill=fill + (255,),
              outline=(outline + (255,)) if outline else None, width=max(2, S // 3))


def hopper(im, x, y, a, b, z_top, z_tip, base, o=U.O):
    """Inverted pyramid under a box: square (x, y, a, b) at z_top narrowing to a spout at z_tip."""
    cx, cy = x + a / 2, y + b / 2
    sp = 0.7
    tip = [(cx - sp, cy - sp), (cx + sp, cy - sp), (cx + sp, cy + sp), (cx - sp, cy + sp)]
    top = [(x, y), (x + a, y), (x + a, y + b), (x, y + b)]
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    for i, nm in ((0, (0, -1, -0.6)), (1, (1, 0, -0.6))):
        j = (i + 1) % 4
        poly = [pr(*top[i], z_top, o), pr(*top[j], z_top, o), pr(*tip[j], z_tip, o), pr(*tip[i], z_tip, o)]
        c = shade(base, nm) + (255,)
        d.polygon(A.P(poly), fill=c, outline=c)
    U.outlined(im, lay, 0.7)


def wisp(im, p, n=4, c=(236, 238, 240), a=150):
    """Thin clean vapour rising from a stack."""
    lay = A.layer()
    d = ImageDraw.Draw(lay)
    for k in range(n):
        r = 1.6 + k * 0.9
        q = (p[0] + k * 1.6 + 0.6 * math.sin(k * 2), p[1] - 1.5 - k * 2.6)
        d.ellipse([(q[0] - r) * S, (q[1] - r * 0.7) * S, (q[0] + r) * S, (q[1] + r * 0.7) * S], fill=c + (int(a * (1 - k / (n + 1))),))
    im.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.5 * S)))


def pipe3(im, pts, c=STEEL, w=1.3, o=U.O):
    pipe(im, [pr(*p, o) for p in pts], c, w)


# ---------------------------------------------------------------- I: particulate filters (baghouse between the works and the chimney)
def icon_1():
    im = A.layer()
    A.floor(im)
    A.shadow(im, [pr(1, 16, 0), pr(12, 16, 0), pr(12, 30, 0), pr(1, 30, 0)], 140, 1.6)
    # old works hall at the back left, brick, with windows
    box3(im, 1, 16, 0, 11, 14, 11, BRICK, 0.9)
    d = ImageDraw.Draw(im)
    for k in range(3):
        a = pr(2.0 + k * 3.4, 16, 8.6)
        b = pr(4.0 + k * 3.4, 16, 8.6)
        d.polygon(A.P([a, b, (b[0], b[1] + 4.2), (a[0], a[1] + 4.2)]), fill=(56, 62, 72, 255))
    # brick chimney at the back right
    A.ellipse_shadow(im, *pr(26, 23, 0), 4, 1.6)
    cyl(im, (26, 23, 0), "z", 33, 2.8, BRICK, rings=[(t, (120, 58, 40), 0.35) for t in (0.2, 0.4, 0.6, 0.8)] + [(0.96, (60, 60, 60), 0.7)], cap=(50, 46, 44))
    wisp(im, pr(26, 23, 33.5))
    # dirty gas duct from the hall into the back of the baghouse
    pipe3(im, [(12, 20, 12.5), (17.5, 20, 12.5), (17.5, 14, 12.5)], (118, 112, 104), 2.3)
    # baghouse on legs with hoppers and a dust bin
    BX, BY, BZ, BS = 12.5, 4.5, 7.0, 10
    A.shadow(im, [pr(BX, BY, 0), pr(BX + BS, BY, 0), pr(BX + BS, BY + BS, 0), pr(BX, BY + BS, 0)], 160, 1.4)
    for lx, ly in ((BX + 0.4, BY + BS - 0.6), (BX + BS - 0.6, BY + BS - 0.6), (BX + 0.4, BY + 0.4), (BX + BS - 0.6, BY + 0.4)):
        cyl(im, (lx, ly, 0), "z", BZ, 0.5, (90, 96, 104))
    hs = BS / 2
    for hx, hy in ((BX, BY + hs), (BX + hs, BY + hs), (BX, BY), (BX + hs, BY)):
        hopper(im, hx, hy, hs, hs, BZ, 3.2, (150, 156, 164))
    box3(im, BX + 0.8, BY - 0.6, 0, 4.0, 3.4, 2.2, (70, 80, 64), 0.7)
    box3(im, BX, BY, BZ, BS, BS, 8.5, (198, 202, 206), 0.9)
    d = ImageDraw.Draw(im)
    for k in range(1, 4):  # panel seams
        a, b = pr(BX + k * BS / 4, BY, BZ + 0.6), pr(BX + k * BS / 4, BY, BZ + 7.9)
        d.line(A.P([a, b]), fill=(140, 146, 152, 255), width=max(2, S // 3))
        a, b = pr(BX + BS, BY + k * BS / 4, BZ + 0.6), pr(BX + BS, BY + k * BS / 4, BZ + 7.9)
        d.line(A.P([a, b]), fill=(118, 124, 130, 255), width=max(2, S // 3))
    # clean gas duct from the baghouse to the chimney
    pipe3(im, [(BX + BS, BY + 6.5, BZ + 5), (26, BY + 6.5, BZ + 5), (26, 20.5, BZ + 5)], (188, 194, 200), 2.3)
    return im


# ---------------------------------------------------------------- III: effluent treatment (clarifiers, murky then clear, outfall to the river)
def clarifier(im, cx, cy, r, h, water, ripple):
    A.ellipse_shadow(im, *pr(cx + 1, cy, 0), r * 1.1, r * 0.55, 150, 1.2)
    cyl(im, (cx, cy, 0), "z", h, r, CONC, cap=(196, 192, 182))
    d = ImageDraw.Draw(im)
    c = pr(cx, cy, h)
    rr = r - 0.9
    k = 1.27  # the floor grid squashes circles to this width-to-height ratio
    d.ellipse([(c[0] - rr * k) * S, (c[1] - rr * k * 0.5) * S, (c[0] + rr * k) * S, (c[1] + rr * k * 0.5) * S], fill=water + (255,), outline=(110, 106, 98, 255), width=max(2, S // 3))
    for f in (0.45, 0.75):
        d.arc([(c[0] - rr * k * f) * S, (c[1] - rr * k * 0.5 * f) * S, (c[0] + rr * k * f) * S, (c[1] + rr * k * 0.5 * f) * S], 200, 340, fill=ripple + (255,), width=max(2, S // 3))
    # scraper bridge from the centre drive to the rim, and the drive
    a, b = pr(cx, cy, h + 0.6), pr(cx + r * 0.95, cy - r * 0.2, h + 0.6)
    d.line(A.P([a, b]), fill=INK + (255,), width=int(1.6 * S))
    d.line(A.P([a, b]), fill=(236, 182, 44, 255), width=int(0.8 * S))
    cyl(im, (cx, cy, h), "z", 1.6, 1.0, (90, 96, 104))


def icon_3():
    im = A.layer()
    A.floor(im)
    # river along the front left edge
    river = [pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 4.2, 0), pr(0, 4.2, 0)]
    m = A.mask_of(lambda d: d.polygon(A.P(river), fill=255))
    im.alpha_composite(A.noisy(A.vgrad(m, (80, 150, 200), (54, 116, 170)), 4, 2))
    d = ImageDraw.Draw(im)
    for x in (5, 14, 25):
        p = pr(x, 2.1, 0)
        d.arc([(p[0] - 2) * S, (p[1] - 0.6) * S, (p[0] + 2) * S, (p[1] + 0.6) * S], 200, 340, fill=(200, 232, 248, 255), width=max(2, S // 3))
    d.line(A.P([pr(0, 4.2, 0), pr(32.2, 4.2, 0)]), fill=(110, 104, 84, 255), width=int(0.6 * S))
    # control building at the back right
    box3(im, 22, 22, 0, 9, 9, 7, (206, 204, 196), 0.9)
    d = ImageDraw.Draw(im)
    for k in range(2):
        a, b = pr(23.5 + k * 4, 22, 5.2), pr(25.5 + k * 4, 22, 5.2)
        d.polygon(A.P([a, b, (b[0], b[1] + 2.6), (a[0], a[1] + 2.6)]), fill=(56, 62, 72, 255))
    # aeration basin: concrete walls, brown water foaming with air
    X0, Y0, XA, YB, H = 1.5, 14, 16, 15, 4.0
    box3(im, X0, Y0, 0, XA, YB, H, CONC, 0.9)
    q4 = [pr(X0 + 0.9, Y0 + 0.9, H), pr(X0 + XA - 0.9, Y0 + 0.9, H), pr(X0 + XA - 0.9, Y0 + YB - 0.9, H), pr(X0 + 0.9, Y0 + YB - 0.9, H)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(q4), fill=255))
    im.alpha_composite(A.noisy(A.vgrad(m, (138, 128, 82), (112, 104, 64)), 6, 5))
    d = ImageDraw.Draw(im)
    d.polygon(A.P(q4), outline=(96, 92, 84, 255), width=max(2, S // 3))
    rng = np.random.default_rng(7)
    for _ in range(36):
        p = pr(rng.uniform(X0 + 1.6, X0 + XA - 1.6), rng.uniform(Y0 + 1.6, Y0 + YB - 1.6), H)
        dot(d, p, rng.uniform(0.35, 0.75), (236, 234, 220))
    pipe3(im, [(X0 + XA, Y0 + 3, 2.0), (18.5, Y0 + 3, 2.0), (18.5, 13, 2.0)], (120, 126, 134), 1.2)
    clarifier(im, 22, 11.5, 8.2, 3.8, (70, 150, 196), (190, 226, 244))
    pipe3(im, [(18, 5.2, 1.4), (15.5, 3.6, 1.4), (15, 3.2, 0.2)], (120, 126, 134), 1.2)
    d = ImageDraw.Draw(im)
    p = pr(15, 2.6, 0)
    d.arc([(p[0] - 1.6) * S, (p[1] - 0.5) * S, (p[0] + 1.6) * S, (p[1] + 0.5) * S], 0, 360, fill=(220, 240, 250, 255), width=max(2, S // 3))
    return im


# ---------------------------------------------------------------- VI: carbon capture and storage (absorber, injection well, CO2 under a cap rock)
GEO = (3, 37)


def icon_6():
    im = A.layer()
    q = lambda x, y, z: pr(x, y, z, GEO)
    h = 14
    L, F, R, Bk = q(0, 0, 0), q(32.2, 0, 0), q(32.2, 32.2, 0), q(0, 32.2, 0)
    Ld, Fd, Rd = A.iso_box(im, L, F, R, Bk, h, ((150, 146, 112), (126, 122, 92)), ((120, 96, 66), (96, 74, 50)), ((96, 76, 52), (74, 58, 40)), 1.0, 5)
    bands = [(0.0, 0.12, (104, 116, 64)), (0.12, 0.36, (140, 112, 80)), (0.36, 0.5, (84, 82, 88)), (0.5, 0.84, (196, 168, 112)), (0.84, 1.0, (110, 104, 98))]
    for a, b, ad, bd, k in ((L, F, Ld, Fd, 1.0), (F, R, Fd, Rd, 0.8)):
        for t0, t1, c in bands:
            U.strip(im, a, b, ad, bd, t0, t1, tuple(int(v * k) for v in c), int(t0 * 10))
    d = ImageDraw.Draw(im)
    # CO2 held in the porous sandstone under the dark cap rock
    rng = np.random.default_rng(3)
    for a, b, ad, bd in ((L, F, Ld, Fd), (F, R, Fd, Rd)):
        for _ in range(16):
            u, v = rng.uniform(0.06, 0.94), rng.uniform(0.55, 0.8)
            p = A.lerp(A.lerp(a, b, u), A.lerp(ad, bd, u), v)
            r = rng.uniform(0.5, 0.95)
            dot(d, p, r, (196, 220, 236), (90, 110, 130))
    d.line(A.P([Ld, Fd, Rd]), fill=INK + (255,), width=int(0.8 * S))
    # injection well down the cut face into the sandstone
    w = A.lerp(L, F, 0.36)
    pipe(im, [(w[0], w[1]), (w[0], w[1] + h * 0.72)], (176, 182, 190), 1.0)
    d = ImageDraw.Draw(im)
    for k in range(3):
        dot(d, (w[0] - 1.6 + k * 1.6, w[1] + h * 0.76), 0.8, (210, 230, 242), (90, 110, 130))
    # power station hall, chimney, absorber column and compressor on the surface
    box3(im, 1, 19, 0, 12, 12, 8, (196, 194, 186), 0.9, o=GEO)
    cyl(im, (21, 27, 0), "z", 24, 2.4, (196, 194, 188), rings=[(0.9, (200, 70, 50), 0.9), (0.84, (240, 240, 240), 0.8)], cap=(70, 66, 62), o=GEO)
    cyl(im, (17, 15, 0), "z", 17, 3.6, (214, 218, 224), rings=[(t, (150, 156, 164), 0.4) for t in (0.25, 0.5, 0.75)], cap=(190, 194, 200), o=GEO)
    pipe(im, [q(13, 22, 5), q(15.5, 18, 5)], (150, 156, 164), 1.4)
    box3(im, 8, 4.5, 0, 6, 4.5, 3.6, (70, 110, 160), 0.8, o=GEO)
    pipe(im, [q(17, 13, 4), q(14, 8, 2.6)], (150, 156, 164), 1.1)
    pipe(im, [q(9, 4.5, 1.6), q(11.6, 0.4, 1.6), (w[0], w[1] + 0.2)], (150, 156, 164), 1.1)
    cyl(im, (11.6, 0.6, 0), "z", 2.2, 0.9, (220, 70, 50), o=GEO)
    return im


# ---------------------------------------------------------------- shared pieces for the later icons
def windows(im, x0, y, z, n, step, w=2.0, hgt=2.6, o=U.O, c=(56, 62, 72)):
    """Row of windows on a front-left face (y fixed)."""
    d = ImageDraw.Draw(im)
    for k in range(n):
        a, b = pr(x0 + k * step, y, z, o), pr(x0 + k * step + w, y, z, o)
        d.polygon(A.P([a, b, (b[0], b[1] + hgt), (a[0], a[1] + hgt)]), fill=c + (255,))


def solar_rows(im, x0, y0, x1, y1, z, rows, o=U.O):
    """Tilted solar panel rows on a flat roof or the ground, facing the front left."""
    d = ImageDraw.Draw(im)
    depth = (y1 - y0) / rows
    for r in reversed(range(rows)):
        ya = y0 + r * depth + depth * 0.15
        yb = ya + depth * 0.62
        quad = [pr(x0, ya, z + 0.3, o), pr(x1, ya, z + 0.3, o), pr(x1, yb, z + 1.9, o), pr(x0, yb, z + 1.9, o)]
        d.polygon(A.P(quad), fill=(40, 58, 96, 255), outline=INK + (255,), width=max(2, S // 3))
        for k in range(1, 4):
            t = k / 4
            d.line(A.P([A.lerp(quad[0], quad[1], t), A.lerp(quad[3], quad[2], t)]), fill=(120, 150, 196, 255), width=max(2, S // 4))
        d.line(A.P([A.lerp(quad[0], quad[3], 0.5), A.lerp(quad[1], quad[2], 0.5)]), fill=(120, 150, 196, 255), width=max(2, S // 4))
        d.line(A.P([quad[3], quad[2]]), fill=(170, 196, 230, 255), width=max(2, S // 4))


def fan_on_face(d, cx, y, cz, r, o=U.O, blades=5, spin=0.3):
    """Round fan set into a front-left face (normal -y)."""
    ring = [pr(cx + r * math.cos(a), y, cz + r * math.sin(a), o) for a in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(A.P(ring), fill=(34, 38, 44, 255), outline=INK + (255,), width=max(2, S // 3))
    inner = [pr(cx + r * 0.86 * math.cos(a), y, cz + r * 0.86 * math.sin(a), o) for a in np.linspace(0, 2 * math.pi, 40)]
    d.polygon(A.P(inner), fill=(56, 62, 70, 255))
    for k in range(blades):
        a = spin + k * 2 * math.pi / blades
        p0 = pr(cx, y, cz, o)
        p1 = pr(cx + r * 0.8 * math.cos(a), y, cz + r * 0.8 * math.sin(a), o)
        p2 = pr(cx + r * 0.8 * math.cos(a + 0.55), y, cz + r * 0.8 * math.sin(a + 0.55), o)
        d.polygon(A.P([p0, p1, p2]), fill=(150, 158, 168, 255))
    hub = [pr(cx + r * 0.2 * math.cos(a), y, cz + r * 0.2 * math.sin(a), o) for a in np.linspace(0, 2 * math.pi, 20)]
    d.polygon(A.P(hub), fill=(196, 200, 206, 255), outline=INK + (255,))


def bale(im, x, y, z, a, b, c, base):
    box3(im, x, y, z, a, b, c, base, 0.6, 6)
    d = ImageDraw.Draw(im)
    for t in (0.3, 0.7):  # straps
        d.line(A.P([pr(x + a * t, y, z + c), pr(x + a * t, y, z)]), fill=(30, 30, 30, 255), width=max(2, S // 4))
        d.line(A.P([pr(x + a, y + b * t, z + c), pr(x + a, y + b * t, z)]), fill=(30, 30, 30, 255), width=max(2, S // 4))


# ---------------------------------------------------------------- II: gas scrubbers (wet scrubber tower, gypsum by-product)
def icon_2():
    im = A.layer()
    A.floor(im)
    # boiler hall at the back left
    box3(im, 1, 18, 0, 11, 12, 12, (186, 184, 176), 0.9)
    windows(im, 2.2, 18, 9.6, 3, 3.4, 2.0, 3.6)
    # concrete stack at the back right with a white steam plume
    A.ellipse_shadow(im, *pr(26, 25, 0), 4, 1.6)
    cyl(im, (26, 25, 0), "z", 32, 2.6, (200, 198, 192), rings=[(0.93, (200, 64, 48), 1.1), (0.86, (240, 240, 240), 1.0), (0.79, (200, 64, 48), 1.0)], cap=(60, 58, 56))
    wisp(im, pr(26, 25, 32.5), 5, (244, 246, 248), 190)
    # flue duct hall -> scrubber, scrubber -> stack
    pipe3(im, [(12, 23, 9), (16, 23, 9), (16, 17, 9)], (120, 116, 108), 2.2)
    # scrubber tower with spray levels and the slurry tank under it
    A.ellipse_shadow(im, *pr(17, 12, 0), 6.5, 2.6)
    cyl(im, (17, 12, 0), "z", 22, 5.0, (206, 210, 216), rings=[(t, (120, 126, 134), 0.5) for t in (0.18, 0.5, 0.62, 0.74)], cap=(170, 174, 180))
    pipe3(im, [(19, 15, 21), (19, 15, 24), (26, 22.5, 24)], (188, 194, 200), 2.0)
    d = ImageDraw.Draw(im)
    for k in range(3):  # spray header nozzles showing through an inspection window
        p = pr(17 + 3.4, 12 - 3.4, 13 + k * 2.6)
        dot(d, p, 0.55, (90, 150, 210), INK[:3])
    # gypsum by-product: conveyor out and a white pile
    pipe3(im, [(21, 8, 4), (27, 4, 6.5)], (60, 64, 70), 1.0)
    U.terrain(im, U.yellow_pile(26, 5, 5.5, 4.0, 4.6, 8), 20, 32, 0.5, 9.5, 24, lambda x, y, z: (226, 224, 214))
    return im


# ---------------------------------------------------------------- IV: cleaner production (efficient plant: solar roof, heat recovery, water recycling)
def icon_4():
    im = A.layer()
    A.floor(im)
    A.shadow(im, [pr(1, 9, 0), pr(22, 9, 0), pr(22, 30, 0), pr(1, 30, 0)], 140, 1.8)
    box3(im, 1, 10, 0, 21, 20, 8, (222, 224, 226), 0.9)
    windows(im, 2.4, 10, 6.4, 5, 3.9, 2.6, 2.4, c=(70, 120, 170))
    solar_rows(im, 2, 11, 21, 29, 8, 4)
    # heat recovery unit with two fans on the roof edge
    box3(im, 15.5, 11.2, 8, 5.2, 4.2, 2.4, (120, 160, 120), 0.7)
    d = ImageDraw.Draw(im)
    for k in range(2):
        c = pr(16.8 + k * 2.6, 13.3, 10.4)
        d.ellipse([(c[0] - 1.1) * S, (c[1] - 0.55) * S, (c[0] + 1.1) * S, (c[1] + 0.55) * S], fill=(40, 44, 50, 255), outline=INK + (255,), width=max(2, S // 4))
    # recycled water tank and loop back into the plant
    A.ellipse_shadow(im, *pr(27, 9, 0), 5, 2)
    cyl(im, (27, 9, 0), "z", 9, 3.6, (90, 150, 200), rings=[(0.5, (60, 110, 160), 0.5)], cap=(110, 170, 216))
    pipe3(im, [(23.5, 9, 2.5), (22, 9, 2.5), (22, 15, 2.5)], (150, 156, 164), 1.1)
    # short stack with nothing coming out
    cyl(im, (5, 26, 8), "z", 6, 1.0, (180, 184, 190), cap=(60, 60, 60))
    return im


# ---------------------------------------------------------------- V: circular economy (recycling yard feeding the factory)
BALES = [(70, 120, 190), (150, 156, 164), (176, 140, 90), (90, 150, 80)]


def icon_5():
    im = A.layer()
    A.floor(im)
    # factory at the back, with the intake door the conveyor runs into
    A.shadow(im, [pr(5, 16, 0), pr(31, 16, 0), pr(31, 31, 0), pr(5, 31, 0)], 140, 1.6)
    box3(im, 5, 16, 0, 26, 15, 11, (204, 200, 190), 0.9)
    windows(im, 20.5, 16, 9.2, 3, 3.4, 2.2, 2.8)
    windows(im, 6.5, 16, 9.2, 2, 3.4, 2.2, 2.8)
    d = ImageDraw.Draw(im)
    a, b = pr(15.6, 16, 9.6), pr(18.4, 16, 9.6)
    d.polygon(A.P([a, b, (b[0], b[1] + 4.2), (a[0], a[1] + 4.2)]), fill=(40, 42, 46, 255))
    # inclined belt conveyor from the yard up to the door
    x0, x1, ya, yb, za, zb = 16, 18, 2.0, 16, 1.4, 9.0
    for t in (0.3, 0.65):
        y, z = ya + (yb - ya) * t, za + (zb - za) * t
        cyl(im, (17, y, 0), "z", z - 0.5, 0.45, (90, 96, 104))
    lay = A.layer()
    dl = ImageDraw.Draw(lay)
    dl.polygon(A.P([pr(x1, ya, za), pr(x1, yb, zb), pr(x1, yb, zb - 1.3), pr(x1, ya, za - 1.3)]), fill=(236, 182, 44, 255))
    dl.polygon(A.P([pr(x0, ya, za), pr(x1, ya, za), pr(x1, yb, zb), pr(x0, yb, zb)]), fill=(52, 54, 58, 255))
    dl.polygon(A.P([pr(x0, ya, za), pr(x1, ya, za), pr(x1, ya, za - 1.3), pr(x0, ya, za - 1.3)]), fill=(200, 150, 30, 255))
    U.outlined(im, lay, 0.7)
    for t, col in ((0.7, BALES[2]), (0.35, BALES[0])):
        y, z = ya + (yb - ya) * t, za + (zb - za) * t
        bale(im, 16.1, y - 1.1, z, 1.8, 2.2, 1.7, col)
    # stack of baled plastic, metal, paper and glass in the yard
    A.shadow(im, [pr(1, 1, 0), pr(11, 1, 0), pr(11, 13, 0), pr(1, 13, 0)], 150, 1.2)
    k = 0
    for z in (0, 3.0):
        for bx, by in ((1.5, 9), (6.5, 9), (1.5, 4), (6.5, 4)):
            if z > 0 and (bx, by) in ((6.5, 4), (1.5, 4)):
                continue
            bale(im, bx, by, z, 4.0, 4.2, 3.0, BALES[k % 4])
            k += 1
    # new product leaving on the right: coils of sheet made from the scrap
    for cy in (10, 5):
        cyl(im, (24, cy, 2.3), "x", 4.0, 2.3, (176, 182, 190), cap=(150, 156, 164), rings=[(0.5, (120, 126, 134), 0.4)])
        d = ImageDraw.Draw(im)
        dot(d, pr(28.05, cy, 2.3), 0.7, (90, 96, 104))
    return im


# ---------------------------------------------------------------- VII: green chemistry (bio-fermenter fed by plant biomass)
def dome_cyl(im, x, y, h, r, base, o=U.O):
    cyl(im, (x, y, 0), "z", h, r, base, rings=[(0.3, (130, 136, 144), 0.4), (0.7, (130, 136, 144), 0.4)], o=o)
    U.terrain(im, lambda px, py: h + 0.62 * math.sqrt(max(0.0, r * r - (px - x) ** 2 - (py - y) ** 2)),
              x - r, x + r, y - r, y + r, 22, lambda px, py, pz: base, edge=0.6, o=o, base_z=h + 0.01)


def bio_drum(im, x, y):
    cyl(im, (x, y, 0), "z", 5.6, 1.9, (70, 140, 70), rings=[(0.33, (40, 90, 40), 0.4), (0.66, (40, 90, 40), 0.4)], cap=(80, 156, 80))


def icon_7():
    im = A.layer()
    A.floor(im)
    # small lab block at the back left with a green roof edge
    box3(im, 1, 19, 0, 10, 11, 7, (214, 214, 206), 0.9)
    windows(im, 2.2, 19, 5.4, 3, 3.0, 1.8, 2.2, c=(70, 120, 170))
    # two stainless fermenters with sight glasses showing the green broth
    for fx, fy, hh in ((17, 21, 15), (24, 13, 15)):
        A.ellipse_shadow(im, *pr(fx + 1, fy, 0), 6, 2.4)
        dome_cyl(im, fx, fy, hh, 4.0, (210, 214, 220))
        d = ImageDraw.Draw(im)
        a, b = pr(fx + 2.0, fy - 3.4, 3.0), pr(fx + 3.1, fy - 2.3, 3.0)
        d.polygon(A.P([a, b, (b[0], b[1] - 8), (a[0], a[1] - 8)]), fill=(30, 34, 38, 255))
        d.polygon(A.P([(a[0] + 0.25, a[1] - 0.4), (b[0] - 0.25, b[1] - 0.4), (b[0] - 0.25, b[1] - 5.2), (a[0] + 0.25, a[1] - 5.2)]), fill=(110, 186, 80, 255))
    # pile of plant biomass (wood chips and straw) feeding them
    U.terrain(im, U.yellow_pile(8, 7, 6.5, 5.0, 4.6, 3), 0.5, 15.5, 0.5, 13.5, 30,
              lambda x, y, z: (176, 150, 84) if U.hashn(round(x * 2), round(y * 2)) > 0.55 else (110, 140, 60))
    # drums of bio-based product
    for dx, dy in ((17.5, 4.5), (22, 4.5), (19.8, 0.8)):
        bio_drum(im, dx, dy)
    return im


# ---------------------------------------------------------------- VIII: carbon-free steel and cement (hydrogen tanks, furnace hall, steel beams)
def ibeam(im, x, y, z, length, base):
    """I-beam lying along x: bottom flange, web, top flange."""
    box3(im, x, y, z, length, 2.4, 0.5, base, 0.5, 2)
    box3(im, x, y + 0.95, z + 0.5, length, 0.5, 1.6, base, 0.5, 2)
    box3(im, x, y, z + 2.1, length, 2.4, 0.5, base, 0.5, 2)


def icon_8():
    im = A.layer()
    A.floor(im)
    # furnace hall at the back right with the glow of the electric furnace in the door
    box3(im, 15, 16, 0, 16, 14, 12, (120, 128, 140), 0.9)
    d = ImageDraw.Draw(im)
    a, b = pr(19, 16, 7.5), pr(25, 16, 7.5)
    door = [a, b, (b[0], b[1] + 7.5), (a[0], a[1] + 7.5)]
    m = A.mask_of(lambda dd: dd.polygon(A.P(door), fill=255))
    im.alpha_composite(A.vgrad(m, (255, 200, 90), (230, 90, 30)))
    d = ImageDraw.Draw(im)
    d.polygon(A.P(door), outline=INK + (255,), width=max(2, S // 3))
    # electrodes on the roof and no chimney smoke
    for k in range(3):
        cyl(im, (21 + k * 2.2, 23, 12), "z", 4 + k * 0.6, 0.6, (70, 70, 74))
    # hydrogen tanks on saddles at the left
    for ty in (22, 15.5):
        box3(im, 3, ty - 2, 0, 2, 4, 2.4, (176, 172, 160), 0.6)
        box3(im, 10, ty - 2, 0, 2, 4, 2.4, (176, 172, 160), 0.6)
        cyl(im, (1.5, ty, 4.8), "x", 12, 2.8, (230, 232, 234), rings=[(0.5, (60, 120, 200), 0.9)], cap=(214, 218, 222))
    pipe3(im, [(13.5, 15.5, 4.8), (16, 15.5, 4.8), (16, 15.5, 3)], (150, 156, 164), 1.0)
    # stack of green steel beams in front
    A.shadow(im, [pr(9, 1, 0), pr(26, 1, 0), pr(26, 9, 0), pr(9, 9, 0)], 150, 1.2)
    for row, (by, bz) in enumerate(((5.6, 0), (2.4, 0), (4.0, 2.6))):
        ibeam(im, 10, by, bz, 15, (150, 160, 172))
    return im


# ---------------------------------------------------------------- IX: direct air capture (stacked fan modules, CO2 to storage)
def icon_9():
    im = A.layer()
    A.floor_dark(im)
    A.shadow(im, [pr(2, 6, 0), pr(26, 6, 0), pr(26, 16, 0), pr(2, 16, 0)], 160, 1.6)
    # storage tank and wellhead at the back
    A.ellipse_shadow(im, *pr(25, 26, 0), 5, 2)
    cyl(im, (25, 26, 0), "z", 10, 3.4, (214, 218, 224), rings=[(0.5, (150, 156, 164), 0.5)], cap=(196, 200, 206))
    # two by two collector modules, each with three fans on its face
    for z in (0.0, 7.0):
        for k, x in enumerate((2.0, 14.0)):
            box3(im, x, 8, z, 11.6, 8, 7.0, (150, 158, 170), 0.8)
            d = ImageDraw.Draw(im)
            for f in range(3):
                fan_on_face(d, x + 2.1 + f * 3.7, 8, z + 3.5, 1.6, spin=0.3 + f + z)
            a, b = pr(x, 8, z + 0.5), pr(x + 11.6, 8, z + 0.5)
            d.line(A.P([a, b]), fill=A.CYAN + (255,), width=max(2, S // 4))
    pipe3(im, [(25.6, 12, 14), (25.6, 18, 14), (25.6, 22.6, 8)], (150, 156, 164), 1.2)
    return im


# ---------------------------------------------------------------- X: zero-emission industry (green-roof plant, wind turbine, solar, clean river)
def icon_10():
    im = A.layer()
    A.floor_dark(im)
    # clean river along the front left edge
    river = [pr(0, 0, 0), pr(32.2, 0, 0), pr(32.2, 4.0, 0), pr(0, 4.0, 0)]
    m = A.mask_of(lambda d: d.polygon(A.P(river), fill=255))
    im.alpha_composite(A.noisy(A.vgrad(m, (90, 166, 210), (60, 128, 180)), 4, 2))
    d = ImageDraw.Draw(im)
    for x in (6, 20):
        p = pr(x, 2, 0)
        d.arc([(p[0] - 2) * S, (p[1] - 0.6) * S, (p[0] + 2) * S, (p[1] + 0.6) * S], 200, 340, fill=(210, 236, 250, 255), width=max(2, S // 3))
    # wind turbine at the back
    tx, ty = 6, 27
    cyl(im, (tx, ty, 0), "z", 24, 0.9, (226, 228, 230))
    box3(im, tx - 1, ty - 1.2, 24, 3.2, 2.2, 1.6, (226, 228, 230), 0.6)
    hub = pr(tx + 0.4, ty - 1.6, 24.8)
    d = ImageDraw.Draw(im)
    for k in range(3):
        a = 1.2 + k * 2 * math.pi / 3
        tip = pr(tx + 0.4 + 11 * math.cos(a), ty - 1.6, 24.8 + 11 * math.sin(a))
        side = pr(tx + 0.4 + 1.8 * math.cos(a + 0.45), ty - 1.6, 24.8 + 1.8 * math.sin(a + 0.45))
        d.polygon(A.P([hub, side, tip]), fill=(236, 238, 240, 255), outline=INK + (255,), width=max(2, S // 3))
    dot(d, hub, 0.9, (200, 204, 210), INK[:3])
    # plant with a planted roof
    A.shadow(im, [pr(10, 9, 0), pr(30, 9, 0), pr(30, 26, 0), pr(10, 26, 0)], 150, 1.6)
    box3(im, 10, 10, 0, 20, 16, 9, (210, 214, 218), 0.9)
    windows(im, 11.4, 10, 7.2, 5, 3.7, 2.4, 3.2, c=(70, 120, 170))
    U.terrain(im, lambda x, y: 9.0 + 0.5 + 0.35 * math.sin(x * 1.3) * math.sin(y * 1.1), 10.4, 29.6, 10.4, 25.6, 24,
              lambda x, y, z: (96, 150, 66) if U.hashn(round(x), round(y)) > 0.3 else (120, 170, 80), base_z=9.0)
    # solar field in front of the plant
    solar_rows(im, 4, 4.6, 26, 9.4, 0, 2)
    return im


ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
DRAW = [icon_1, icon_2, icon_3, icon_4, icon_5, icon_6, icon_7, icon_8, icon_9, icon_10]
if __name__ == "__main__":
    preview = Image.new("RGBA", (10 * 70 + 6, 76), (52, 58, 52, 255))
    for i, draw in enumerate(DRAW):
        big = draw()
        big.alpha_composite(A.numeral(ROMAN[i]))
        icon = big.resize((N, N), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=0))
        A.save_dds(icon, f"gfx/interface/technologies/mdr/mdr_clean_tech_{i + 1}.dds")
        preview.alpha_composite(icon, (6 + i * 70, 6))
    if len(sys.argv) > 1:
        preview.save(sys.argv[1])
    print("10 clean technology icons written")
