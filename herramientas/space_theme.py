# Look of the space programme menu: Millennium Dawn's petrol blue (its md_tiled_window2_border is 17, 41, 51) made a
# little lighter, steel grey buttons like its own, thin rounded borders and one sky blue accent. Used by make_space_icons.py; every sprite of the menu frame, tabs, buttons and bars is drawn here.
import numpy as np
from PIL import Image, ImageDraw

# Palette.
NIGHT = (24, 50, 62)
GLASS = (33, 64, 79)
GLASS_HI = (46, 86, 104)
LINE = (78, 118, 136)
ACCENT = (104, 190, 236)
ACCENT_DEEP = (44, 118, 176)
ICE = (226, 240, 255)
K = 4  # drawn this many times larger, then reduced, for smooth edges


def _rounded(w, h, r, fill, border=None, width=1):
    img = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w * K - 1, h * K - 1], radius=r * K, fill=fill, outline=border, width=width * K if border else 0)
    return img.resize((w, h), Image.LANCZOS)


def _vertical(w, h, top, bottom):
    t = np.linspace(0, 1, h)[:, None, None]
    rgb = np.array(top, dtype=float) * (1 - t) + np.array(bottom, dtype=float) * t
    return np.broadcast_to(rgb, (h, w, 3)).copy()


def _horizontal(w, h, left, right):
    t = np.linspace(0, 1, w)[None, :, None]
    rgb = np.array(left, dtype=float) * (1 - t) + np.array(right, dtype=float) * t
    return np.broadcast_to(rgb, (h, w, 3)).copy()


def _masked(rgb, mask_img):
    a = np.array(mask_img, dtype=float)
    return Image.fromarray(np.dstack([rgb, a[:, :, 3]]).astype(np.uint8))


def window_sprite():
    # Cornered tile for the whole window: the 2 px accent on top stretches with the width.
    w = h = 96
    img = _rounded(w, h, 10, NIGHT + (250,), LINE, 1)
    d = ImageDraw.Draw(img)
    d.line([(10, 1), (w - 11, 1)], fill=ACCENT + (255,), width=2)
    return img


def panel_sprite():
    return _rounded(32, 32, 6, GLASS + (232,), LINE, 1)


def rule_sprite():
    # Under section titles: a short bright stroke that fades out.
    a = np.zeros((2, 230, 4), dtype=np.uint8)
    a[:, :, :3] = ACCENT
    a[:, :, 3] = np.concatenate([np.full(36, 255), np.linspace(150, 0, 194)]).astype(np.uint8)
    return Image.fromarray(a)


def hero_sprite(earth):
    # Banner: deep blue with the planet's limb, a cyan stripe on the left.
    w, h = 748, 130
    base = _horizontal(w, h, (44, 92, 118), (26, 52, 66))
    img = Image.fromarray(np.dstack([base, np.full((h, w), 255.0)]).astype(np.uint8))
    art = np.array(earth.crop((0, 110, 560, 236)).resize((w, h), Image.LANCZOS), dtype=float)
    art[:, :, :3] = art[:, :, :3] * np.array([0.8, 0.96, 1.08])
    img.alpha_composite(Image.fromarray(np.clip(art, 0, 255).astype(np.uint8)))
    frame = _rounded(w, h, 8, (0, 0, 0, 255), LINE, 1)
    out = _masked(np.array(img, dtype=float)[:, :, :3], frame)
    d = ImageDraw.Draw(out)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, outline=LINE + (255,), width=1)
    d.rectangle([1, 12, 4, h - 13], fill=ACCENT + (255,))
    return out


def backdrop_sprite(earth, w=900, h=686):
    art = earth.crop((120, 0, 850, 660)).resize((w, h), Image.LANCZOS)
    a = np.array(art, dtype=float)
    a[:, :, :3] = a[:, :, :3] * np.array([0.55, 0.8, 1.15])
    a[:, :, 3] *= 0.32
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def header_sprite(w=894):
    # Title bar: fades in from the left and ends in a cyan line.
    h = 46
    rgb = _horizontal(w, h, (48, 88, 108), NIGHT)
    alpha = np.broadcast_to(np.linspace(235, 0, w)[None, :], (h, w)).copy()
    a = np.dstack([rgb, alpha])
    a[h - 2:, :, :3] = ACCENT
    a[h - 2:, :, 3] = np.linspace(255, 0, w)
    return Image.fromarray(a.astype(np.uint8))


def nav_tab():
    # Two frames of 90 x 53: resting and chosen.
    out = Image.new("RGBA", (180, 53), (0, 0, 0, 0))
    out.alpha_composite(_rounded(90, 53, 7, GLASS + (235,), LINE, 1), (0, 0))
    on = _rounded(90, 53, 7, (0, 0, 0, 255), ACCENT, 1)
    on = _masked(_vertical(90, 53, (58, 106, 128), (34, 66, 82)), on)
    d = ImageDraw.Draw(on)
    d.rounded_rectangle([0, 0, 89, 52], radius=7, outline=ACCENT + (255,), width=1)
    d.rectangle([12, 49, 77, 51], fill=ACCENT + (255,))
    out.alpha_composite(on, (90, 0))
    return out


def button(w, h):
    shape = _rounded(w, h, 5, (0, 0, 0, 255))
    img = _masked(_vertical(w, h, (92, 106, 122), (56, 66, 78)), shape)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=5, outline=(150, 166, 184, 255), width=1)
    d.line([(5, 1), (w - 6, 1)], fill=(190, 204, 218, 150), width=1)
    return img


def arrow(direction):
    w = h = 22
    img = _rounded(w, h, 11, GLASS_HI + (255,), ACCENT, 1)
    big = Image.new("RGBA", (w * K, h * K), (0, 0, 0, 0))
    pts = [(13, 6), (8, 11), (13, 16)] if direction == "left" else [(9, 6), (14, 11), (9, 16)]
    ImageDraw.Draw(big).line([(x * K, y * K) for x, y in pts], fill=ICE + (255,), width=2 * K, joint="curve")
    img.alpha_composite(big.resize((w, h), Image.LANCZOS))
    return img


def _track(w, h):
    cell = np.zeros((h, w, 4), dtype=np.uint8)
    cell[:, :] = LINE + (255,)
    cell[1:-1, 1:-1] = (18, 36, 46, 255)
    return cell


def budget_bar(frames=51):
    # Bright up to 1% of GDP, dimmer above, where each point returns less; white mark at 1%.
    w, h = 304, 16
    strip = np.zeros((h, w * frames, 4), dtype=np.uint8)
    fill_rgb = _horizontal(w - 4, h - 4, ACCENT_DEEP, ACCENT)
    one = round((w - 4) * 0.2)
    for f in range(frames):
        cell = _track(w, h)
        n = round((w - 4) * f / (frames - 1))
        rgb = fill_rgb[:, :n].copy()
        rgb[:, one:] *= 0.55
        cell[2:-2, 2:2 + n, :3] = rgb.astype(np.uint8)
        cell[1:-1, 2 + one] = ICE + (255,)
        strip[:, f * w:(f + 1) * w] = cell
    return Image.fromarray(strip)


def meter(frames=51):
    w, h = 164, 12
    strip = np.zeros((h, w * frames, 4), dtype=np.uint8)
    fill_rgb = _horizontal(w - 4, h - 4, ACCENT_DEEP, ACCENT)
    for f in range(frames):
        cell = _track(w, h)
        n = round((w - 4) * f / (frames - 1))
        cell[2:-2, 2:2 + n, :3] = fill_rgb[:, :n].astype(np.uint8)
        strip[:, f * w:(f + 1) * w] = cell
    return Image.fromarray(strip)


def chart_bar(frames=51):
    # Upright bar of the Finance chart, filled from the bottom: frame 1 empty, frame 51 full.
    w, h = 36, 100
    strip = np.zeros((h, w * frames, 4), dtype=np.uint8)
    full = _vertical(w - 4, h - 2, (125, 220, 255), ACCENT_DEEP)
    for f in range(frames):
        cell = np.zeros((h, w, 4), dtype=np.uint8)
        cell[h - 1, :] = LINE + (255,)
        n = round((h - 2) * f / (frames - 1))
        if n:
            cell[h - 1 - n:h - 1, 2:-2, :3] = full[h - 2 - n:].astype(np.uint8)
            cell[h - 1 - n:h - 1, 2:-2, 3] = 255
            cell[h - 1 - n, 2:-2] = ICE + (255,)
        strip[:, f * w:(f + 1) * w] = cell
    return Image.fromarray(strip)


def selection_ring(size):
    k = 6
    img = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    ImageDraw.Draw(img).ellipse([k, k, size * k - k, size * k - k], outline=ACCENT + (255,), width=2 * k)
    return img.resize((size, size), Image.LANCZOS)


def side_tab(w=118, h=32):
    # Side bar entry, two frames: resting (bare, it lights up on hover) and chosen (glass with a cyan stripe on the left).
    out = Image.new("RGBA", (w * 2, h), (0, 0, 0, 0))
    out.alpha_composite(_rounded(w, h, 5, GLASS + (90,)), (0, 0))
    on = _masked(_horizontal(w, h, (64, 116, 140), (38, 72, 88)), _rounded(w, h, 5, (0, 0, 0, 255)))
    d = ImageDraw.Draw(on)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=5, outline=(104, 160, 186, 255), width=1)
    d.rectangle([0, 5, 2, h - 6], fill=ACCENT + (255,))
    out.alpha_composite(on, (w, 0))
    return out


def banner(photo, w=748, h=34):
    # Category strip: a slice of the picture on the left that fades into the glass, darkened under the name.
    out = _rounded(w, h, 5, GLASS + (240,), LINE, 1)
    pic = photo.convert("RGBA")
    scale = 320 / pic.width
    pic = pic.resize((320, max(h, round(pic.height * scale))), Image.LANCZOS)
    top = (pic.height - h) // 2
    a = np.array(pic.crop((0, top, 320, top + h)), dtype=float)
    fade = np.clip((320 - np.arange(320)) / 160, 0, 1)
    a[:, :, :3] *= 0.62
    a[:, :, 3] = 255 * fade[None, :]
    strip = Image.fromarray(a.astype(np.uint8))
    mask = _rounded(w, h, 5, (0, 0, 0, 255))
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    layer.alpha_composite(strip, (0, 0))
    layer.putalpha(Image.fromarray(np.minimum(np.array(layer)[:, :, 3], np.array(mask)[:, :, 3]).astype(np.uint8)))
    out.alpha_composite(layer)
    ImageDraw.Draw(out).rounded_rectangle([0, 0, w - 1, h - 1], radius=5, outline=LINE + (255,), width=1)
    return out


def card(photo, w=146, h=86):
    # Shortcut tile: the picture fills it, darker at the bottom where its name goes.
    pic = photo.convert("RGBA")
    scale = max(w / pic.width, h / pic.height)
    pic = pic.resize((round(pic.width * scale), round(pic.height * scale)), Image.LANCZOS)
    left, top = (pic.width - w) // 2, (pic.height - h) // 2
    a = np.array(pic.crop((left, top, left + w, top + h)), dtype=float)
    shade = np.clip((np.arange(h) - h * 0.35) / (h * 0.65), 0, 1)[:, None] * 0.75
    a[:, :, :3] *= 1 - shade[:, :, None]
    a[:, :, 3] = 255
    img = _masked(a[:, :, :3], _rounded(w, h, 6, (0, 0, 0, 255)))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, w - 1, h - 1], radius=6, outline=LINE + (255,), width=1)
    return img


def banner_selected(w=748, h=34):
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=5, outline=ACCENT + (255,), width=2)
    d.rectangle([2, 6, 4, h - 7], fill=ACCENT + (255,))
    return img
