# Ammunition research icons (mdr_ammo_tech_1..12): one scene per technology, drawn at 8x and reduced to 64x64.
# Writes gfx/interface/technologies/mdr/mdr_ammo_tech_<n>.dds. make_tech_lines.py does not redraw these.
# Run from the mod folder: python herramientas/make_ammo_icons.py [preview.png]
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
N, S = (64, 8)
W = N * S
INK = (18, 15, 10)
BRASS = (214, 168, 74)
COPPER = (186, 104, 60)
OLIVE = (108, 118, 62)
STEEL = (170, 176, 184)

def layer():
    return Image.new('RGBA', (W, W), (0, 0, 0, 0))

def P(pts):
    return [(x * S, y * S) for x, y in pts]

def mask_of(fn):
    m = Image.new('L', (W, W), 0)
    fn(ImageDraw.Draw(m))
    return m

def outline(m, px=1.0):
    k = int(px * S) * 2 + 1
    o = Image.new('RGBA', (W, W), INK + (0,))
    o.putalpha(m.filter(ImageFilter.MaxFilter(k)))
    return o

def paint(m, rgb):
    arr = np.zeros((W, W, 4), np.uint8)
    arr[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    arr[..., 3] = np.array(m)
    return Image.fromarray(arr, 'RGBA')

def vgrad(m, top, bot):
    a = np.array(m) > 0
    ys = np.where(a.any(1))[0]
    if len(ys) == 0:
        return layer()
    t = np.clip((np.arange(W) - ys[0]) / max(1, ys[-1] - ys[0]), 0, 1)[:, None, None]
    rgb = np.array(top)[None, None] * (1 - t) + np.array(bot)[None, None] * t
    return paint(m, np.broadcast_to(rgb, (W, W, 3)))

def round_shade(m, base, spec=0.55):
    """Cylinder shading per row (works for any upright round body). Light from the upper left."""
    a = np.array(m) > 0
    any_ = a.any(1)
    left = np.where(any_, a.argmax(1), 0)
    right = np.where(any_, W - 1 - a[:, ::-1].argmax(1), 1)
    x = (np.arange(W)[None, :] - left[:, None]) / np.maximum(1, right - left)[:, None]
    x = np.clip(x, 0, 1)
    f = 0.55 + 0.75 * np.sin(np.pi * np.clip(x * 1.15, 0, 1)) ** 0.8 - 0.25 * x
    hl = np.exp(-((x - 0.3) / 0.07) ** 2) * spec
    rgb = np.array(base)[None, None, :] * f[..., None] + 255 * hl[..., None]
    return paint(m, rgb)

def noisy(lay, amount=6, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, amount, (W // 4, W // 4)).astype(np.float32)
    n = np.array(Image.fromarray(n).resize((W, W), Image.BICUBIC))
    arr = np.array(lay).astype(np.float32)
    arr[..., :3] += n[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')

def band(m, y0, y1):
    """Part of a mask between two y values (in icon units)."""
    a = np.array(m).copy()
    a[:int(y0 * S)] = 0
    a[int(y1 * S):] = 0
    return Image.fromarray(a, 'L')

def place(im, full, col, px=0.8, angle=0, pivot=None):
    o = outline(full, px)
    if angle:
        pv = (pivot[0] * S, pivot[1] * S)
        o = o.rotate(angle, resample=Image.BICUBIC, center=pv)
        col = col.rotate(angle, resample=Image.BICUBIC, center=pv)
    im.alpha_composite(o)
    im.alpha_composite(col)

def ogive(t0, t1, r0, r1, steps=8, power=1.8):
    return [(t0 + (t1 - t0) * k / steps, r1 + (r0 - r1) * (1 - (k / steps) ** power)) for k in range(steps + 1)]
CART_PROF = [(0, 1), (0.6, 1), (0.7, 0.62), (0.76, 0.62)] + ogive(0.76, 1.0, 0.6, 0.0)

def cartridge(im, cx, by, h, w=4.4, angle=0, pivot=None, case=BRASS):
    full, col = solid(cx, by, h, w / 2, CART_PROF, [(0, 0.761, case, 0.55), (0.76, 1.0, COPPER, 0.45)], rings=[(0.08, (120, 84, 30))])
    place(im, full, col, 0.7, angle, pivot)

def floor(im):
    ground = [(3, 50), (32, 36), (61, 50), (32, 63)]
    mg = mask_of(lambda d: d.polygon(P(ground), fill=255))
    im.alpha_composite(outline(mg, 0.8))
    im.alpha_composite(noisy(vgrad(mg, (150, 146, 128), (96, 92, 78)), 4, 3))
    d = ImageDraw.Draw(im)
    for t in (0.33, 0.66):
        d.line(P([(3 + 29 * t, 50 - 14 * t), (32 + 29 * t, 63 - 13 * t)]), fill=(84, 82, 70, 255), width=S // 3)

def shadow(im, poly, strength=150, blur=2.2):
    m = mask_of(lambda d: d.polygon(P(poly), fill=strength))
    s = Image.new('RGBA', (W, W), (10, 10, 6, 0))
    s.putalpha(m.filter(ImageFilter.GaussianBlur(blur * S)))
    im.alpha_composite(s)

def ellipse_shadow(im, cx, cy, rx, ry, strength=150, blur=1.4):
    m = mask_of(lambda d: d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], fill=strength))
    s = Image.new('RGBA', (W, W), (10, 10, 6, 0))
    s.putalpha(m.filter(ImageFilter.GaussianBlur(blur * S)))
    im.alpha_composite(s)

def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)

def wood_face(m, base, dark, seams):
    lay = noisy(vgrad(m, base, dark), 6, 7)
    d = ImageDraw.Draw(lay)
    for a, b in seams:
        d.line(P([a, b]), fill=(30, 36, 18, 255), width=max(2, S // 3))
    lay.putalpha(m)
    return lay

def icon_1():
    im = layer()
    floor(im)
    shadow(im, [(10, 50), (31, 60), (56, 49), (35, 40)])
    L, F, R, Bk = ((6, 31), (28, 42), (58, 29), (36, 18))
    h = 16
    Ld, Fd, Rd = ((L[0], L[1] + h), (F[0], F[1] + h), (R[0], R[1] + h))
    im.alpha_composite(outline(mask_of(lambda d: d.polygon(P([L, Bk, R, Rd, Fd, Ld]), fill=255)), 1.0))
    im.alpha_composite(vgrad(mask_of(lambda d: d.polygon(P([L, F, R, Bk]), fill=255)), (40, 44, 26), (64, 70, 40)))
    slots = []
    for row in range(3):
        for c in range(4):
            u, v = (0.2 + 0.3 * row, 0.14 + 0.24 * c)
            slots.append(lerp(lerp(L, F, u), lerp(Bk, R, u), v))
    for x, y in sorted(slots, key=lambda q: q[1]):
        cartridge(im, x, y + 3.5, 16.5)
    left = mask_of(lambda d: d.polygon(P([L, F, Fd, Ld]), fill=255))
    right = mask_of(lambda d: d.polygon(P([F, R, Rd, Fd]), fill=255))
    im.alpha_composite(wood_face(left, (122, 134, 70), (82, 92, 46), [(lerp(L, Ld, t), lerp(F, Fd, t)) for t in (0.34, 0.67)]))
    im.alpha_composite(wood_face(right, (92, 104, 52), (58, 66, 32), [(lerp(F, Fd, t), lerp(R, Rd, t)) for t in (0.34, 0.67)]))
    d = ImageDraw.Draw(im)
    d.line(P([L, F, R]), fill=(160, 170, 100, 255), width=int(1.1 * S))
    d.line(P([F, Fd]), fill=(54, 62, 30, 255), width=int(1.6 * S))
    for a, b in ((L, Ld), (R, Rd)):
        d.line(P([a, b]), fill=(70, 80, 40, 255), width=int(1.4 * S))
    hx, hy = ((L[0] + F[0]) / 2, (L[1] + F[1]) / 2 + 6)
    box = [(hx - 3.2) * S, (hy - 1.5) * S, (hx + 3.2) * S, (hy + 3.5) * S]
    d.arc(box, 20, 160, fill=INK + (255,), width=int(0.9 * S))
    d.arc(box, 20, 160, fill=(196, 176, 120, 255), width=int(0.45 * S))
    s0, s1 = (lerp(F, Fd, 0.16), lerp(R, Rd, 0.16))
    d.line(P([lerp(s0, s1, 0.18), lerp(s0, s1, 0.82)]), fill=(232, 200, 72, 255), width=int(1.3 * S))
    a0, a1 = (lerp(F, Fd, 0.5), lerp(R, Rd, 0.5))
    for k in range(3):
        x0 = lerp(a0, a1, 0.3 + 0.17 * k)
        d.line(P([x0, (x0[0], x0[1] + 3.2)]), fill=(232, 200, 72, 255), width=int(0.7 * S))
    cartridge(im, 11, 58, 14, angle=68, pivot=(11, 58))
    cartridge(im, 40, 62, 14, angle=-80, pivot=(40, 62))
    return im
SHELL_PROF = [(0, 0.94), (0.03, 1.0), (0.6, 1.0)] + ogive(0.6, 0.86, 1.0, 0.36) + [(0.86, 0.36), (0.87, 0.4)] + ogive(0.87, 1.0, 0.4, 0.08, 6, 1.4)

def icon_3():
    im = layer()
    floor(im)
    L, F, R, Bk = ((28, 24), (43, 31.5), (61, 22.5), (46, 15))
    h = 21
    Ld, Fd, Rd = ((L[0], L[1] + h), (F[0], F[1] + h), (R[0], R[1] + h))
    shadow(im, [(26, 46), (44, 55), (62, 45), (46, 37)], 160, 1.8)
    E0, E1 = ((lerp(L, F, 0.18)[0], lerp(L, F, 0.18)[1] + 14), (lerp(L, F, 0.82)[0], lerp(L, F, 0.82)[1] + 14))
    S0, S1 = ((E0[0] - 26, E0[1] + 13), (E1[0] - 26, E1[1] + 13))
    shadow(im, [S0, E0, (E1[0], E1[1] + 6), (S1[0], S1[1] + 6)], 120, 1.2)
    body = mask_of(lambda d: d.polygon(P([L, Bk, R, Rd, Fd, Ld]), fill=255))
    im.alpha_composite(outline(body, 1.0))
    top = mask_of(lambda d: d.polygon(P([L, F, R, Bk]), fill=255))
    lf = mask_of(lambda d: d.polygon(P([L, F, Fd, Ld]), fill=255))
    rf = mask_of(lambda d: d.polygon(P([F, R, Rd, Fd]), fill=255))
    im.alpha_composite(noisy(vgrad(top, (176, 184, 190), (146, 154, 162)), 3, 1))
    im.alpha_composite(noisy(vgrad(lf, (132, 142, 152), (96, 104, 114)), 3, 2))
    im.alpha_composite(noisy(vgrad(rf, (98, 106, 116), (68, 74, 82)), 3, 4))
    d = ImageDraw.Draw(im)
    d.line(P([L, F, R]), fill=(206, 212, 218, 255), width=int(0.8 * S))
    d.line(P([F, Fd]), fill=(70, 76, 84, 255), width=int(1.0 * S))
    stripe = mask_of(lambda dd: dd.polygon(P([lerp(L, Ld, 0.05), lerp(F, Fd, 0.05), lerp(F, Fd, 0.2), lerp(L, Ld, 0.2)]), fill=255))
    st = layer()
    sd = ImageDraw.Draw(st)
    for k in range(-4, 12):
        x = L[0] + k * 2.6
        sd.polygon(P([(x, 10), (x + 1.3, 10), (x + 1.3 + 30, 70), (x + 30, 70)]), fill=(28, 24, 16, 255))
    yel = paint(stripe, np.broadcast_to(np.array((230, 190, 50)), (W, W, 3)))
    st_m = Image.fromarray(np.minimum(np.array(st.getchannel('A')), np.array(stripe)), 'L')
    blk = Image.new('RGBA', (W, W), (28, 24, 16, 0))
    blk.putalpha(st_m)
    im.alpha_composite(yel)
    im.alpha_composite(blk)
    pc = lerp(lerp(F, R, 0.55), lerp(Fd, Rd, 0.55), 0.35)
    panel = [(pc[0] - 5, pc[1] + 0.5), (pc[0] + 5, pc[1] - 4.5), (pc[0] + 5, pc[1] + 1.5), (pc[0] - 5, pc[1] + 6.5)]
    d.polygon(P(panel), fill=(44, 50, 58, 255), outline=INK + (255,), width=S // 3)
    for k, c in enumerate([(90, 230, 90), (240, 190, 50), (220, 60, 50)]):
        x, y = (pc[0] - 2.8 + k * 2.8, pc[1] + 1.2 - k * 1.4)
        d.ellipse([(x - 0.9) * S, (y - 0.9) * S, (x + 0.9) * S, (y + 0.9) * S], fill=c + (255,))
    lc = lerp(lerp(L, R, 0.5), Bk, 0.3)
    full, col = solid(lc[0], lc[1], 5, 1.6, [(0, 1), (0.5, 1), (1, 0.6)], [(0, 1, (70, 220, 90), 0.6)])
    place(im, full, col, 0.6)
    hole = [E0, E1, (E1[0], E1[1] - 10), (E0[0], E0[1] - 10)]
    hm = mask_of(lambda dd: dd.polygon(P(hole), fill=255))
    im.alpha_composite(outline(hm, 0.5))
    im.alpha_composite(vgrad(hm, (40, 30, 20), (150, 90, 30)))
    belt = mask_of(lambda dd: dd.polygon(P([S0, E0, E1, S1]), fill=255))
    side = mask_of(lambda dd: dd.polygon(P([S1, E1, (E1[0], E1[1] + 4), (S1[0], S1[1] + 4)]), fill=255))
    both = Image.fromarray(np.maximum(np.array(belt), np.array(side)), 'L')
    im.alpha_composite(outline(both, 0.8))
    im.alpha_composite(vgrad(belt, (64, 64, 62), (44, 44, 42)))
    im.alpha_composite(vgrad(side, (120, 126, 132), (80, 86, 92)))
    d = ImageDraw.Draw(im)
    for k in range(1, 12):
        t = k / 12
        d.line(P([lerp(S0, E0, t), lerp(S1, E1, t)]), fill=(30, 30, 28, 255), width=max(2, S // 4))
    for k in range(6):
        c = lerp((S1[0], S1[1] + 2), (E1[0], E1[1] + 2), (k + 0.5) / 6)
        d.ellipse([(c[0] - 1.1) * S, (c[1] - 1.1) * S, (c[0] + 1.1) * S, (c[1] + 1.1) * S], fill=(40, 42, 46, 255), outline=(170, 176, 184, 255), width=S // 4)
    mids = [lerp(lerp(S0, S1, 0.5), lerp(E0, E1, 0.5), t) for t in (0.12, 0.33, 0.54, 0.75)]
    for x, y in sorted(mids, key=lambda q: q[1]):
        cartridge(im, x, y + 1.2, 15, 4.6)
    return im

def grains(im, cx, cy, rx, ry, n, seed, size=1.0, clip=None):
    rng = np.random.default_rng(seed)
    g = layer()
    d = ImageDraw.Draw(g)
    pts = []
    while len(pts) < n:
        x, y = rng.uniform(-1, 1, 2)
        if x * x + y * y <= 1:
            pts.append((cx + x * rx, cy + y * ry))
    for x, y in sorted(pts, key=lambda p: p[1]):
        r = size * rng.uniform(0.75, 1.15)
        tone = rng.integers(0, 3)
        base = [(70, 78, 58), (88, 96, 70), (56, 62, 48)][tone]
        d.ellipse([(x - r) * S, (y - r * 0.7) * S, (x + r) * S, (y + r * 0.7) * S], fill=base + (255,), outline=INK + (255,), width=max(1, S // 4))
        d.ellipse([(x - r * 0.45) * S, (y - r * 0.5) * S, (x - r * 0.05) * S, (y - r * 0.15) * S], fill=(150, 160, 120, 255))
    if clip is not None:
        g.putalpha(Image.fromarray(np.minimum(np.array(g.getchannel('A')), np.array(clip)), 'L'))
    im.alpha_composite(g)

def icon_4():
    im = layer()
    floor(im)
    cx, top_y, bot_y, rx, ry = (24, 27, 50, 12, 4.6)
    ellipse_shadow(im, cx + 2, bot_y + 1, rx + 2, ry + 1.5)
    body = mask_of(lambda d: (d.rectangle([(cx - rx) * S, top_y * S, (cx + rx) * S, bot_y * S], fill=255), d.ellipse([(cx - rx) * S, (bot_y - ry) * S, (cx + rx) * S, (bot_y + ry) * S], fill=255), d.ellipse([(cx - rx) * S, (top_y - ry) * S, (cx + rx) * S, (top_y + ry) * S], fill=255)))
    place(im, body, round_shade(body, OLIVE, 0.35), 1.0)
    d = ImageDraw.Draw(im)
    for y in (top_y + 2.2, bot_y - 2.2):
        d.arc([(cx - rx) * S, (y - ry) * S, (cx + rx) * S, (y + ry) * S], 0, 180, fill=(70, 78, 40, 255), width=int(0.6 * S))
    lab = mask_of(lambda dd: dd.rectangle([(cx - rx) * S, (top_y + 8) * S, (cx + rx) * S, (top_y + 14) * S], fill=255))
    lab = Image.fromarray(np.minimum(np.array(lab), np.array(body)), 'L')
    im.alpha_composite(round_shade(lab, (214, 186, 70), 0.3))
    for k in range(4):
        x = cx - 6 + k * 3.6
        d.rectangle([x * S, (top_y + 9.6) * S, (x + 2) * S, (top_y + 12.4) * S], fill=(40, 34, 20, 255))
    mouth = mask_of(lambda dd: dd.ellipse([(cx - rx + 1.2) * S, (top_y - ry + 0.6) * S, (cx + rx - 1.2) * S, (top_y + ry - 0.6) * S], fill=255))
    im.alpha_composite(paint(mouth, np.broadcast_to(np.array((40, 44, 32)), (W, W, 3))))
    grains(im, cx, top_y, rx - 2, ry - 1.2, 40, 3, 1.15, clip=mouth)
    d = ImageDraw.Draw(im)
    d.ellipse([(cx - rx) * S, (top_y - ry) * S, (cx + rx) * S, (top_y + ry) * S], outline=(160, 168, 110, 255), width=int(0.7 * S))
    lid = layer()
    lm = mask_of(lambda dd: dd.ellipse([3 * S, 30 * S, 13 * S, 54 * S], fill=255))
    lid.alpha_composite(outline(lm, 0.8))
    lid.alpha_composite(noisy(vgrad(lm, (138, 148, 84), (76, 84, 44)), 4, 9))
    ImageDraw.Draw(lid).ellipse([4.6 * S, 32.5 * S, 11.4 * S, 51.5 * S], outline=(70, 78, 40, 255), width=int(0.6 * S))
    im.alpha_composite(lid.rotate(-14, resample=Image.BICUBIC, center=(8 * S, 52 * S)))
    grains(im, 30, 56, 10, 3.6, 46, 5, 1.2)
    grains(im, 31, 55, 5, 1.8, 14, 6, 1.2)
    cx2, by2, h2, w2 = (48, 58, 38, 13)
    ellipse_shadow(im, cx2 + 1, by2, 7, 2.2)
    full, col = solid(cx2, by2, h2, w2 / 2, CART_PROF, [(0, 0.761, BRASS, 0.55), (0.76, 1.0, COPPER, 0.45)], rings=[(0.08, (120, 84, 30))])
    place(im, full, col, 0.9)
    cut = mask_of(lambda dd: dd.rectangle([(cx2 - 2.2) * S, (by2 - h2 * 0.58) * S, (cx2 + w2 / 2 - 0.9) * S, (by2 - h2 * 0.12) * S], fill=255))
    im.alpha_composite(paint(cut, np.broadcast_to(np.array((34, 36, 28)), (W, W, 3))))
    grains(im, cx2 + 1, by2 - h2 * 0.35, 4.5, h2 * 0.25, 40, 8, 1.0, clip=cut)
    d = ImageDraw.Draw(im)
    d.rectangle([(cx2 - 2.2) * S, (by2 - h2 * 0.58) * S, (cx2 + w2 / 2 - 0.9) * S, (by2 - h2 * 0.12) * S], outline=(246, 214, 130, 255), width=int(0.5 * S))
    return im

def numeral(text):
    t = layer()
    d = ImageDraw.Draw(t)
    font = ImageFont.truetype('C:/Windows/Fonts/timesbi.ttf', (17 if len(text) < 4 else 13) * S)
    box = d.textbbox((0, 0), text, font=font)
    d.text((61 * S - box[2], 63 * S - box[3]), text, font=font, fill=(240, 236, 50, 255), stroke_width=S, stroke_fill=(15, 15, 5, 255))
    return t
import math
import os
TILT = 0.3
CYAN = (90, 220, 240)

def curve_mask(cx, yb, rb, above):
    """Pixels above (or below) the front half of an ellipse edge at height yb with radius rb."""
    xs = np.arange(W) / S
    yc = yb + TILT * np.sqrt(np.clip(rb * rb - (xs - cx) ** 2, 0, None))
    ys = np.arange(W)[:, None] / S
    return ys < yc[None, :] if above else ys >= yc[None, :]

def solid(cx, by, h, half, prof, sections, rings=()):
    ts, rs = ([p[0] for p in prof], [p[1] for p in prof])
    r0 = prof[0][1] * half
    left = [(cx - half * r, by - h * t) for t, r in prof]
    right = [(cx + half * r, by - h * t) for t, r in reversed(prof)]
    arc = [(cx + r0 * math.cos(a), by + r0 * TILT * math.sin(a)) for a in np.linspace(0, math.pi, 16)]
    full = mask_of(lambda d: d.polygon(P(left + right[:-1] + arc), fill=255))
    fa = np.array(full) > 0
    col = layer()
    for t0, t1, c, sp in sections:
        m = fa.copy()
        if t0 > 0:
            m &= curve_mask(cx, by - h * t0, np.interp(t0, ts, rs) * half, True)
        if t1 < 1:
            m &= curve_mask(cx, by - h * t1, np.interp(t1, ts, rs) * half, False)
        col.alpha_composite(round_shade(Image.fromarray((m * 255).astype(np.uint8), 'L'), c, sp))
    d = ImageDraw.Draw(col)
    for t, c in rings:
        r = np.interp(t, ts, rs) * half
        y = by - h * t
        pts = [(cx + r * math.cos(a), y + r * TILT * math.sin(a)) for a in np.linspace(0, math.pi, 14)]
        d.line(P(pts), fill=c + (255,), width=int(0.55 * S), joint='curve')
    col.putalpha(Image.fromarray(np.minimum(np.array(col.getchannel('A')), np.array(full)), 'L'))
    return (full, col)

def top_disc(im, cx, y, r, fill, rim):
    d = ImageDraw.Draw(im)
    d.ellipse([(cx - r) * S, (y - r * TILT) * S, (cx + r) * S, (y + r * TILT) * S], fill=fill + (255,), outline=rim + (255,), width=max(2, S // 3))

def on_layer(fn):
    lay = layer()
    fn(lay)
    return lay

def rotated(im, fn, angle, pivot):
    lay = on_layer(fn)
    im.alpha_composite(lay.rotate(angle, resample=Image.BICUBIC, center=(pivot[0] * S, pivot[1] * S)))

def iso_box(im, L, F, R, Bk, h, top, left, right, edge=1.0, noise=3):
    Ld, Fd, Rd = ((L[0], L[1] + h), (F[0], F[1] + h), (R[0], R[1] + h))
    im.alpha_composite(outline(mask_of(lambda d: d.polygon(P([L, Bk, R, Rd, Fd, Ld]), fill=255)), edge))
    for poly, c in (([L, F, R, Bk], top), ([L, F, Fd, Ld], left), ([F, R, Rd, Fd], right)):
        m = mask_of(lambda d: d.polygon(P(poly), fill=255))
        im.alpha_composite(noisy(vgrad(m, c[0], c[1]), noise, int(sum(c[0]))))
    d = ImageDraw.Draw(im)
    d.line(P([L, F, R]), fill=tuple((min(255, v + 40) for v in top[0])) + (255,), width=int(0.6 * S))
    return (Ld, Fd, Rd)

def floor_dark(im):
    ground = [(3, 50), (32, 36), (61, 50), (32, 63)]
    mg = mask_of(lambda d: d.polygon(P(ground), fill=255))
    im.alpha_composite(outline(mg, 0.8))
    im.alpha_composite(noisy(vgrad(mg, (70, 76, 84), (40, 44, 50)), 3, 3))
    d = ImageDraw.Draw(im)
    d.line(P([(9, 47), (32, 59), (55, 47)]), fill=CYAN + (255,), width=int(0.5 * S))
    for t in (0.33, 0.66):
        d.line(P([(3 + 29 * t, 50 - 14 * t), (32 + 29 * t, 63 - 13 * t)]), fill=(30, 34, 40, 255), width=S // 3)

def glow(im, cx, cy, r, c=CYAN, a=170):
    m = mask_of(lambda d: d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=a))
    g = Image.new('RGBA', (W, W), c + (0,))
    g.putalpha(m.filter(ImageFilter.GaussianBlur(r * S * 0.5)))
    im.alpha_composite(g)

def icon_2():
    im = layer()
    floor(im)
    ellipse_shadow(im, 43, 49, 7, 2.6)
    ellipse_shadow(im, 30, 56, 9, 3.2)
    ellipse_shadow(im, 14, 58, 5, 2)
    shell(im, 43, 48, 27, 10, fuze=False, body=(96, 106, 56))
    shell(im, 29, 56, 37, 13)

    def spanner(l):
        d = ImageDraw.Draw(l)
        d.line(P([(40, 59), (54, 59)]), fill=INK + (255,), width=int(2.6 * S))
        d.line(P([(40, 59), (54, 59)]), fill=(150, 156, 164, 255), width=int(1.3 * S))
        d.ellipse([52 * S, 56.6 * S, 57 * S, 61.4 * S], fill=(150, 156, 164, 255), outline=INK + (255,), width=int(0.7 * S))
        d.ellipse([53.8 * S, 58.2 * S, 55.2 * S, 59.8 * S], fill=(96, 92, 78, 255))
    rotated(im, spanner, 18, (47, 59))
    fuze(im, 14, 59, 15, 9)
    return im

def shell(im, cx, by, h, w, fuze=True, body=OLIVE):
    prof = SHELL_PROF if fuze else [p for p in SHELL_PROF if p[0] <= 0.86] + [(0.865, 0.0)]
    secs = [(0, 0.03, (120, 120, 112), 0.3), (0.03, 0.11, COPPER, 0.5), (0.11, 0.861 if fuze else 1.0, body, 0.3)]
    if fuze:
        secs.append((0.86, 1.0, (150, 156, 160), 0.45))
    rings = [(0.11, INK), (0.42, (214, 190, 64)), (0.47, (214, 190, 64))]
    if fuze:
        rings += [(0.9, (80, 84, 90)), (0.94, (80, 84, 90))]
    full, col = solid(cx, by, h, w / 2, prof, secs, rings)
    place(im, full, col, 0.9)
    if not fuze:
        top_disc(im, cx, by - h * 0.86, w / 2 * 0.36, (26, 24, 20), (150, 150, 140))

def fuze(im, cx, by, h, w):
    prof = [(0, 0.56), (0.32, 0.56), (0.34, 1.0), (0.46, 1.0)] + ogive(0.46, 1.0, 0.92, 0.12, 6, 1.3)
    rings = [(t, (70, 74, 80)) for t in (0.08, 0.16, 0.24)] + [(0.6, (100, 104, 110))]
    full, col = solid(cx, by, h, w / 2, prof, [(0, 0.33, (130, 132, 128), 0.35), (0.33, 1.0, (150, 156, 160), 0.5)], rings)
    place(im, full, col, 0.8)
    d = ImageDraw.Draw(im)
    y = by - h * 0.76
    r = w * 0.3
    d.line(P([(cx - r + k * r / 6, y + TILT * r * math.sin(math.pi * k / 12)) for k in range(13)]), fill=(200, 50, 40, 255), width=int(0.8 * S))

def lying_shell(im, x, y, h, w, band=(70, 120, 200)):

    def draw(l):
        full, col = solid(x, y, h, w / 2, SHELL_PROF, [(0, 0.03, (120, 120, 112), 0.3), (0.03, 0.11, COPPER, 0.5), (0.11, 0.861, OLIVE, 0.3), (0.86, 1.0, (150, 156, 160), 0.45)], [(0.11, INK), (0.4, band), (0.44, band), (0.48, band), (0.9, (80, 84, 90))])
        place(l, full, col, 0.8)
    rotated(im, draw, -90, (x, y - h / 2))

def icon_6():
    im = layer()
    floor(im)
    shadow(im, [(8, 50), (28, 59), (56, 47), (36, 38)], 170, 1.8)
    iso_box(im, (8, 46), (28, 55), (54, 43), (34, 34), 4, ((150, 120, 80), (120, 92, 60)), ((120, 92, 60), (90, 68, 44)), ((100, 76, 50), (72, 54, 36)), 0.8, 6)
    d = ImageDraw.Draw(im)
    for t in (0.33, 0.66):
        d.line(P([lerp((8, 46), (34, 34), t), lerp((28, 55), (54, 43), t)]), fill=(90, 68, 44, 255), width=max(2, S // 3))
    h, w = (33, 9.6)
    bottom = [(37, 35.5), (32.5, 40.5), (28, 45.5)]
    middle = [((bottom[0][0] + bottom[1][0]) / 2, (bottom[0][1] + bottom[1][1]) / 2 - 7.2), ((bottom[1][0] + bottom[2][0]) / 2, (bottom[1][1] + bottom[2][1]) / 2 - 7.2)]
    top = [((middle[0][0] + middle[1][0]) / 2, (middle[0][1] + middle[1][1]) / 2 - 7.2)]
    for cx, cy in bottom + middle + top:
        lying_shell(im, cx, cy + h / 2, h, w)
    return im

def ribbed(im, a, b, c, d_, n, col):
    dr = ImageDraw.Draw(im)
    for k in range(1, n):
        t = k / n
        dr.line(P([lerp(a, b, t), lerp(d_, c, t)]), fill=col + (255,), width=max(2, S // 3))

def icon_7():
    im = layer()
    floor(im)
    shadow(im, [(6, 46), (30, 58), (58, 45), (34, 34)], 170, 1.8)
    mods = [((22, 28), (40, 37), (58, 28), (40, 19), 12, ((170, 174, 176), (150, 154, 156)), ((140, 144, 148), (110, 114, 118)), ((112, 116, 120), (84, 88, 92))), ((6, 38), (24, 47), (40, 39), (22, 30), 12, ((196, 178, 130), (176, 158, 112)), ((170, 150, 100), (130, 112, 72)), ((140, 122, 80), (104, 88, 56))), ((22, 17), (40, 26), (58, 17), (40, 8), 10, ((140, 154, 92), (120, 134, 74)), ((110, 124, 64), (84, 96, 46)), ((90, 102, 52), (64, 74, 36)))]
    order = [0, 2, 1]
    for i in order:
        L, F, R, Bk, h, t, l, r = mods[i]
        Ld, Fd, Rd = iso_box(im, L, F, R, Bk, h, t, l, r)
        ribbed(im, L, F, Fd, Ld, 7, tuple((max(0, v - 30) for v in l[1])))
        ribbed(im, F, R, Rd, Fd, 7, tuple((max(0, v - 25) for v in r[1])))
    d = ImageDraw.Draw(im)
    L, F, R, Bk, h = mods[1][:5]
    a, b = (lerp(F, R, 0.3), lerp(F, R, 0.62))
    door = [(a[0], a[1] + 3), (b[0], b[1] + 3), (b[0], b[1] + h), (a[0], a[1] + h)]
    d.polygon(P(door), fill=(60, 52, 36, 255), outline=INK + (255,), width=S // 2)
    glow(im, lerp(a, b, 0.5)[0], a[1] + 1.2, 1.6, (255, 200, 90), 220)
    for x, y in ((40, 56), (46, 53), (52, 50)):
        ellipse_shadow(im, x, y, 2.6, 1, 120, 0.6)
    for x, y in ((52, 50), (46, 53), (40, 56)):
        shell(im, x, y, 13, 4.6)
    return im

def icon_9():
    im = layer()
    floor_dark(im)
    shadow(im, [(10, 48), (32, 59), (54, 48), (32, 37)], 170, 1.8)
    L, F, R, Bk = ((10, 44), (32, 55), (54, 44), (32, 33))
    iso_box(im, L, F, R, Bk, 4, ((70, 76, 86), (56, 60, 70)), ((52, 56, 64), (38, 42, 48)), ((40, 44, 50), (28, 30, 36)))
    full, col = solid(32, 46, 13, 7, [(0, 1), (1, 1)], [(0, 1, (176, 150, 96), 0.4)], rings=[(t / 10, (120, 98, 60)) for t in range(1, 10)])
    place(im, full, col, 0.7)
    top_disc(im, 32, 33, 7, (150, 128, 82), (220, 196, 140))
    glow(im, 32, 33, 5)
    d = ImageDraw.Draw(im)
    tops = [(x, y - 32) for x, y in (L, F, R, Bk)]
    for (x, y), (tx, ty) in zip((L, F, R, Bk), tops):
        if (x, y) == Bk:
            continue
        d.line(P([(x, y), (tx, ty)]), fill=INK + (255,), width=int(2.2 * S))
        d.line(P([(x, y), (tx, ty)]), fill=(120, 128, 140, 255), width=int(1.1 * S))
    for a, b in ((0, 3), (3, 2), (0, 1), (1, 2)):
        d.line(P([tops[a], tops[b]]), fill=INK + (255,), width=int(2.2 * S))
        d.line(P([tops[a], tops[b]]), fill=(140, 148, 160, 255), width=int(1.1 * S))
    g0, g1 = (lerp(tops[0], tops[3], 0.5), lerp(tops[1], tops[2], 0.5))
    d.line(P([g0, g1]), fill=INK + (255,), width=int(2.4 * S))
    d.line(P([g0, g1]), fill=(170, 176, 188, 255), width=int(1.2 * S))
    hc = lerp(g0, g1, 0.5)
    iso_box(im, (hc[0] - 4, hc[1]), (hc[0], hc[1] + 2), (hc[0] + 4, hc[1]), (hc[0], hc[1] - 2), 6, ((200, 206, 214), (180, 186, 194)), ((150, 156, 166), (120, 126, 136)), ((120, 126, 136), (96, 100, 110)), 0.7)
    d = ImageDraw.Draw(im)
    d.polygon(P([(hc[0] - 1.2, hc[1] + 8), (hc[0] + 1.2, hc[1] + 8), (hc[0], hc[1] + 10.5)]), fill=(230, 236, 240, 255), outline=INK + (255,))
    glow(im, hc[0], hc[1] + 11, 2.2, CYAN, 230)
    d.line(P([(hc[0], hc[1] + 10.5), (32, 33)]), fill=CYAN + (255,), width=int(0.6 * S))
    d.line(P([F, tops[1]]), fill=INK + (255,), width=int(2.2 * S))
    d.line(P([F, tops[1]]), fill=(120, 128, 140, 255), width=int(1.1 * S))
    return im

def limb(im, a, b, wdt, c):
    d = ImageDraw.Draw(im)
    d.line(P([a, b]), fill=INK + (255,), width=int((wdt + 1.6) * S))
    d.line(P([a, b]), fill=c[1] + (255,), width=int(wdt * S))
    off = (-0.3 * wdt, -0.3 * wdt)
    d.line(P([(a[0] + off[0], a[1] + off[1]), (b[0] + off[0], b[1] + off[1])]), fill=c[0] + (255,), width=int(wdt * 0.45 * S))
    for p in (a, b):
        r = wdt * 0.62
        d.ellipse([(p[0] - r) * S, (p[1] - r) * S, (p[0] + r) * S, (p[1] + r) * S], fill=c[1] + (255,), outline=INK + (255,), width=int(0.7 * S))
        d.ellipse([(p[0] - r * 0.4) * S, (p[1] - r * 0.4) * S, (p[0] + r * 0.4) * S, (p[1] + r * 0.4) * S], fill=(40, 44, 50, 255))

def icon_5():
    im = layer()
    floor(im)
    shadow(im, [(12, 50), (31, 59), (52, 49), (33, 40)], 170, 1.8)
    red, redd = (((196, 82, 50), (150, 56, 34)), ((140, 50, 30), (100, 34, 20)))
    BL, BF, BR, BB = ((14, 42), (31, 50.5), (50, 41), (33, 32.5))
    iso_box(im, BL, BF, BR, BB, 5, ((126, 130, 136), (106, 110, 116)), ((100, 104, 112), (72, 76, 84)), ((80, 84, 92), (56, 60, 66)))
    iso_box(im, (26, 40.5), (32, 43.5), (38.5, 40), (32.5, 37), 3.5, ((84, 88, 96), (70, 74, 80)), ((70, 74, 80), (50, 54, 60)), ((56, 60, 66), (40, 44, 50)), 0.7)
    full, col = solid(32.3, 40.3, 6.5, 2.4, [(0, 1), (1, 1)], [(0, 1, BRASS, 0.6)])
    place(im, full, col, 0.6)
    top_disc(im, 32.3, 33.8, 2.4, (110, 78, 28), (240, 210, 120))
    for cx, by in ((18, 42.5), (46.5, 41.5)):
        full, col = solid(cx, by, 24, 2.3, [(0, 1), (1, 1)], [(0, 1, (176, 182, 190), 0.6)], rings=[(0.05, (90, 94, 100))])
        place(im, full, col, 0.7)
    CL, CF, CR, CB = ((14, 14), (31, 22.5), (50, 13), (33, 4.5))
    Ld, Fd, Rd = iso_box(im, CL, CF, CR, CB, 7, red, red, redd)
    d = ImageDraw.Draw(im)
    for t in (0.33, 0.66):
        d.line(P([lerp(CL, CF, t), lerp(Ld, Fd, t)]), fill=(120, 40, 24, 255), width=int(0.5 * S))
        d.line(P([lerp(CF, CR, t), lerp(Fd, Rd, t)]), fill=(90, 30, 18, 255), width=int(0.5 * S))
    for cx, cy in ((18, 13.5), (46.5, 12.5)):
        full, col = solid(cx, cy, 1.6, 3.0, [(0, 1), (1, 1)], [(0, 1, (150, 156, 164), 0.5)])
        place(im, full, col, 0.6)
        top_disc(im, cx, cy - 1.6, 3.0, (176, 182, 190), (110, 114, 120))
    full, col = solid(32, 13.5, 6, 4.2, [(0, 1), (1, 1)], [(0, 1, (170, 176, 184), 0.6)], rings=[(0.5, (100, 104, 110))])
    place(im, full, col, 0.8)
    top_disc(im, 32, 7.5, 4.2, (190, 196, 204), (110, 114, 120))
    full, col = solid(32, 31.5, 4.5, 2.2, [(0, 1), (1, 1)], [(0, 1, (190, 196, 204), 0.7)])
    place(im, full, col, 0.6)
    full, col = solid(32, 28, 1.6, 4.0, [(0, 1), (1, 1)], [(0, 1, (120, 126, 134), 0.5)])
    place(im, full, col, 0.6)
    iso_box(im, (5, 50.5), (12, 54), (19, 50.5), (12, 47), 3, ((96, 100, 106), (80, 84, 90)), ((70, 74, 80), (56, 60, 66)), ((60, 64, 70), (46, 50, 56)), 0.7)
    for x, y in sorted([(9.5, 50.5), (12.5, 49), (15.5, 50.5), (12.5, 52)], key=lambda q: q[1]):
        full, col = solid(x, y, 4, 1.4, [(0, 1), (1, 1)], [(0, 1, BRASS, 0.6)])
        place(im, full, col, 0.5)
        top_disc(im, x, y - 4, 1.4, (110, 78, 28), (240, 210, 120))
    return im

def icon_8():
    im = layer()
    floor(im)
    ellipse_shadow(im, 28, 54, 7, 2.4)
    ellipse_shadow(im, 40, 49, 7, 2.4)
    POLY = (54, 60, 58)
    full, col = solid(40, 49, 38, 6, CART_PROF, [(0, 0.761, BRASS, 0.55), (0.76, 1.0, COPPER, 0.45)], rings=[(0.08, (120, 84, 30))])
    place(im, full, col, 0.9)
    full, col = solid(27, 54, 38, 6, CART_PROF, [(0, 0.12, (170, 174, 180), 0.6), (0.12, 0.761, POLY, 0.3), (0.76, 1.0, COPPER, 0.45)], rings=[(0.12, (30, 32, 30)), (0.5, (80, 160, 110))])
    place(im, full, col, 0.9)

    def loose(l):
        full, col = solid(15, 57, 12, 2.5, [(0, 1), (0.12, 1), (0.6, 1), (0.7, 0.62), (0.78, 0.62)], [(0, 0.12, (170, 174, 180), 0.6), (0.12, 0.78, POLY, 0.3)])
        place(l, full, col, 0.6)
    rotated(im, loose, 70, (15, 57))
    return im

def icon_11():
    im = layer()
    floor_dark(im)
    S0, E0, E1, S1 = ((4, 44), (27, 32.5), (33, 35.5), (10, 47))
    shadow(im, [S0, E0, (E1[0], E1[1] + 5), (S1[0], S1[1] + 5)], 140, 1.0)
    belt = mask_of(lambda d: d.polygon(P([S0, E0, E1, S1]), fill=255))
    side = mask_of(lambda d: d.polygon(P([S1, E1, (E1[0], E1[1] + 3.5), (S1[0], S1[1] + 3.5)]), fill=255))
    im.alpha_composite(outline(Image.fromarray(np.maximum(np.array(belt), np.array(side)), 'L'), 0.8))
    im.alpha_composite(vgrad(belt, (64, 66, 70), (46, 48, 52)))
    im.alpha_composite(vgrad(side, (96, 102, 110), (66, 70, 78)))
    d = ImageDraw.Draw(im)
    for k in range(1, 10):
        d.line(P([lerp(S0, E0, k / 10), lerp(S1, E1, k / 10)]), fill=(30, 30, 32, 255), width=max(2, S // 4))
    for k in range(5):
        c = lerp((S1[0], S1[1] + 1.8), (E1[0], E1[1] + 1.8), (k + 0.5) / 5)
        d.ellipse([(c[0] - 1) * S, (c[1] - 1) * S, (c[0] + 1) * S, (c[1] + 1) * S], fill=(40, 42, 46, 255), outline=(150, 156, 164, 255), width=S // 4)
    d.line(P([(S1[0], S1[1] + 3.5), (E1[0], E1[1] + 3.5)]), fill=CYAN + (255,), width=int(0.45 * S))
    for t in (0.18, 0.48):
        x, y = lerp(lerp(S0, S1, 0.5), lerp(E0, E1, 0.5), t)
        shell(im, x, y + 1.2, 12, 4.4)
    full, col = solid(46, 55, 5, 7, [(0, 1), (0.7, 1), (1, 0.75)], [(0, 1, (62, 66, 74), 0.4)], rings=[(0.35, CYAN)])
    place(im, full, col, 0.9)
    arm = ((96, 102, 114), (60, 64, 74))
    j0, j1, j2 = ((46, 48), (51, 25), (31, 17))
    limb(im, j0, j1, 5.0, arm)
    limb(im, j1, j2, 3.8, arm)
    d = ImageDraw.Draw(im)
    wrist = (31, 21.5)
    d.line(P([j2, wrist]), fill=INK + (255,), width=int(3.2 * S))
    d.line(P([j2, wrist]), fill=(70, 74, 84, 255), width=int(1.9 * S))
    shell(im, 31, 33.5, 13, 4.8)
    for sx in (-1, 1):
        d.line(P([(31 + sx * 1.2, 21.5), (31 + sx * 3.4, 23.5), (31 + sx * 3.0, 27.5)]), fill=INK + (255,), width=int(1.9 * S), joint='curve')
        d.line(P([(31 + sx * 1.2, 21.5), (31 + sx * 3.4, 23.5), (31 + sx * 3.0, 27.5)]), fill=(150, 156, 166, 255), width=int(0.9 * S), joint='curve')
    glow(im, j1[0], j1[1], 1.8, CYAN, 200)
    glow(im, j0[0], j0[1], 1.6, CYAN, 180)
    return im

def icon_12():
    """Nanoenergetics: a realistic lab bench look. Matte projectile with a cutaway of fine grey nano-powder, and a sample vial."""
    im = layer()
    floor_dark(im)
    shadow(im, [(16, 52), (32, 60), (50, 51), (34, 43)], 170, 1.4)
    iso_box(im, (18, 49), (32, 56), (48, 48.5), (34, 41.5), 3.5, ((84, 90, 100), (70, 76, 86)), ((64, 70, 80), (46, 50, 58)), ((52, 56, 64), (36, 40, 46)), 0.8)
    prof = [(0, 0.92), (0.04, 1.0), (0.6, 1.0)] + ogive(0.6, 1.0, 1.0, 0.04, 10, 1.7)
    cx, by, h, w = (33, 49, 42, 13)
    full, col = solid(cx, by, h, w / 2, prof, [(0, 0.05, (110, 114, 120), 0.4), (0.05, 0.62, (78, 84, 92), 0.3), (0.62, 1.0, (96, 102, 110), 0.35)], rings=[(0.05, INK), (0.12, (150, 120, 60)), (0.15, (150, 120, 60)), (0.62, (50, 54, 60))])
    place(im, full, col, 1.0)
    x0, x1, y0, y1 = (cx - 0.5, cx + w / 2 - 1.1, by - h * 0.56, by - h * 0.2)
    cut = mask_of(lambda d: d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], fill=255))
    rng = np.random.default_rng(4)
    base = rng.normal(150, 28, (W, W))
    base = np.array(Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'L').filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32)
    rgb = np.stack([base * 1.02, base * 1.0, base * 0.96], -1)
    im.alpha_composite(paint(cut, rgb))
    d = ImageDraw.Draw(im)
    d.rectangle([x0 * S, y0 * S, x1 * S, y1 * S], outline=(30, 32, 36, 255), width=int(0.6 * S))
    d.line(P([(x0 + 0.4, y0 + 0.6), (x0 + 0.4, y1 - 0.6)]), fill=(200, 204, 210, 255), width=int(0.4 * S))
    vx, vb = (13, 57)
    ellipse_shadow(im, vx + 1, vb, 4, 1.4)
    full, col = solid(vx, vb, 13, 3.2, [(0, 1), (1, 1)], [(0, 1, (190, 206, 214), 0.8)])
    glass = col.copy()
    a = np.array(glass.getchannel('A')).astype(np.float32) * 0.55
    glass.putalpha(Image.fromarray(a.astype(np.uint8), 'L'))
    powder, pcol = solid(vx, vb, 6, 3.0, [(0, 1), (1, 1)], [(0, 1, (140, 142, 146), 0.3)])
    im.alpha_composite(outline(full, 0.6))
    im.alpha_composite(pcol)
    im.alpha_composite(glass)
    top_disc(im, vx, vb - 6, 3.0, (156, 158, 162), (110, 112, 116))
    capf, capc = solid(vx, vb - 13, 3, 3.5, [(0, 1), (1, 1)], [(0, 1, (40, 44, 52), 0.4)])
    place(im, capf, capc, 0.6)
    return im

def vadd(a, b, k=1.0):
    return (a[0] + b[0] * k, a[1] + b[1] * k)

def ammo_crate(im, L, Lv, Dv, h, k_len=0.8, k_dep=0.8):
    Lt = (L[0], L[1] - h)
    F = vadd(Lt, Lv, k_len)
    R = vadd(F, Dv, k_dep)
    Bk = vadd(Lt, Dv, k_dep)
    Ld, Fd, Rd = iso_box(im, Lt, F, R, Bk, h, ((140, 152, 84), (124, 136, 72)), ((112, 124, 62), (84, 94, 44)), ((90, 100, 50), (64, 72, 34)), 0.6, 4)
    d = ImageDraw.Draw(im)
    a, b = (lerp(Lt, Ld, 0.45), lerp(F, Fd, 0.45))
    d.line(P([lerp(a, b, 0.2), lerp(a, b, 0.8)]), fill=(226, 196, 70, 255), width=int(0.6 * S))

def post(im, a, b, c):
    d = ImageDraw.Draw(im)
    d.line(P([a, b]), fill=INK + (255,), width=int(2.5 * S))
    d.line(P([a, b]), fill=c + (255,), width=int(1.3 * S))

def icon_10():
    im = layer()
    floor(im)
    NB, NL = (2, 2)
    Lv = (12.5, 6.25)
    Dv = (9.0, -4.5)
    LH = 11.0
    FB0 = (17, 40)
    up = (70, 92, 132)
    beam = (226, 124, 40)
    shadow(im, [FB0, vadd(FB0, Lv, NB), vadd(vadd(FB0, Lv, NB), Dv), vadd(FB0, Dv)], 170, 1.4)
    for k in range(NB + 1):
        b0 = vadd(vadd(FB0, Lv, k), Dv)
        post(im, b0, (b0[0], b0[1] - NL * LH - 1), up)
    for lvl in range(NL):
        y = -lvl * LH
        f0 = (FB0[0], FB0[1] + y)
        deck = [f0, vadd(f0, Lv, NB), vadd(vadd(f0, Lv, NB), Dv), vadd(f0, Dv)]
        dm = mask_of(lambda d: d.polygon(P(deck), fill=255))
        im.alpha_composite(vgrad(dm, (96, 100, 108), (76, 80, 88)))
        for i in range(NB):
            if (lvl, i) == (1, 1):
                continue
            L = vadd(vadd(f0, Lv, i + 0.1), Dv, 0.1)
            ammo_crate(im, L, Lv, Dv, LH * 0.62)
        d = ImageDraw.Draw(im)
        d.line(P([f0, vadd(f0, Lv, NB)]), fill=INK + (255,), width=int(1.7 * S))
        d.line(P([f0, vadd(f0, Lv, NB)]), fill=beam + (255,), width=int(0.9 * S))
    for k in range(NB + 1):
        f = vadd(FB0, Lv, k)
        post(im, (f[0], f[1] + 0.4), (f[0], f[1] - NL * LH - 1), up)
    top0 = (FB0[0], FB0[1] - NL * LH)
    d = ImageDraw.Draw(im)
    d.line(P([top0, vadd(top0, Lv, NB)]), fill=INK + (255,), width=int(1.7 * S))
    d.line(P([top0, vadd(top0, Lv, NB)]), fill=beam + (255,), width=int(0.9 * S))
    foot = vadd(vadd(FB0, Lv, 0.95), Dv, -1.0)
    r0, r1 = (vadd(foot, Lv, -1.6), vadd(foot, Lv, 1.4))
    d.line(P([r0, r1]), fill=INK + (255,), width=int(1.5 * S))
    d.line(P([r0, r1]), fill=(150, 156, 164, 255), width=int(0.6 * S))
    yel = ((246, 196, 60), (226, 172, 40))
    yeld = ((214, 160, 36), (170, 124, 24))
    yeldd = ((176, 130, 26), (134, 98, 18))
    tL = vadd(foot, Lv, -0.35)
    iso_box(im, (tL[0], tL[1] - 3), vadd((tL[0], tL[1] - 3), Lv, 0.7), vadd(vadd((tL[0], tL[1] - 3), Lv, 0.7), Dv, 0.6), vadd((tL[0], tL[1] - 3), Dv, 0.6), 3, yel, yeld, yeldd, 0.8)
    m0 = vadd(foot, Dv, 0.05)
    m1 = vadd(m0, Lv, 0.22)
    for m in (m0, m1):
        post(im, (m[0], m[1] - 3), (m[0], m[1] - NL * LH - 4), (236, 182, 44))
    d = ImageDraw.Draw(im)
    d.line(P([(m0[0], m0[1] - NL * LH - 4), (m1[0], m1[1] - NL * LH - 4)]), fill=INK + (255,), width=int(1.9 * S))
    d.line(P([(m0[0], m0[1] - NL * LH - 4), (m1[0], m1[1] - NL * LH - 4)]), fill=(236, 182, 44, 255), width=int(0.9 * S))
    glow(im, m0[0] + 1.2, m0[1] - NL * LH - 5.5, 1.5, (255, 150, 40), 230)
    cy = -LH * 1 - 1.2
    cL = (m0[0] - 0.6, m0[1] + cy)
    iso_box(im, (cL[0], cL[1] - 3), vadd((cL[0], cL[1] - 3), Lv, 0.32), vadd(vadd((cL[0], cL[1] - 3), Lv, 0.32), Dv, 0.5), vadd((cL[0], cL[1] - 3), Dv, 0.5), 3.2, yel, yeld, yeldd, 0.7)
    fork0 = vadd(vadd(cL, Lv, 0.05), Dv, 0.4)
    d = ImageDraw.Draw(im)
    for k in (0.06, 0.26):
        a = vadd(fork0, Lv, k)
        d.line(P([a, vadd(a, Dv, 1.1)]), fill=INK + (255,), width=int(1.2 * S))
        d.line(P([a, vadd(a, Dv, 1.1)]), fill=(120, 124, 130, 255), width=int(0.5 * S))
    ammo_crate(im, vadd(vadd(cL, Lv, -0.1), Dv, 0.55), Lv, Dv, LH * 0.62)
    return im


def save_dds(img, path):
    w, h = img.size
    r, g, b, a = img.split()
    data = Image.merge('RGBA', (b, g, r, a)).tobytes()
    head = struct.pack('<4s7I', b'DDS ', 124, 0x100F, h, w, w * 4, 0, 1) + bytes(44)
    head += struct.pack('<2I4s5I', 32, 0x41, bytes(4), 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    head += struct.pack('<5I', 0x1000, 0, 0, 0, 0)
    with open(path, 'wb') as f:
        f.write(head + data)


ROMAN = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII']
DRAW = [icon_1, icon_2, icon_3, icon_4, icon_5, icon_6, icon_7, icon_8, icon_9, icon_10, icon_11, icon_12]
if __name__ == '__main__':
    preview = Image.new('RGBA', (12 * 70 + 6, 76), (52, 58, 52, 255))
    for i, draw in enumerate(DRAW):
        big = draw()
        big.alpha_composite(numeral(ROMAN[i]))
        icon = big.resize((N, N), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=0))
        save_dds(icon, f'gfx/interface/technologies/mdr/mdr_ammo_tech_{i + 1}.dds')
        preview.alpha_composite(icon, (6 + i * 70, 6))
    if len(sys.argv) > 1:
        preview.save(sys.argv[1])
    print('12 ammunition icons written')
