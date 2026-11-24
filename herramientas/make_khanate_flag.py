"""Flag of the Mongol Empire (cosmetic tag MDR_MON_KHANATE, focus mdr_mon_G15).

The version shown on Wikipedia ("Flag of The Mongol Empire 3"): blue field with the top of the soyombo in white,
a small three-tongued flame, a large sun and a large crescent holding it.
Drawn large and scaled down to the three HOI4 flag sizes (82x52, 41x26, 10x7), 32-bit TGA.
Writes gfx/flags/MDR_MON_KHANATE.tga (+ medium/, small/) and a preview PNG with --preview <path>.

Run from the mod folder:  python herramientas/make_khanate_flag.py
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
S = 16  # supersampling
W, H = 82 * S, 52 * S
BLUE, WHITE = (0, 76, 168), (255, 255, 255)


def draw():
    im = Image.new("RGBA", (W, H), BLUE + (255,))
    d = ImageDraw.Draw(im)
    cx = W / 2
    # flame: three tongues on a small base, near the top
    fw, fy = H * 0.12, H * 0.235
    d.ellipse([cx - fw * 0.62, fy - fw * 0.45, cx + fw * 0.62, fy + fw * 0.5], fill=WHITE)
    for dx, h, w in ((-fw * 0.42, fw * 0.95, 0.27), (0, fw * 1.4, 0.3), (fw * 0.42, fw * 0.95, 0.27)):
        d.ellipse([cx + dx - fw * w, fy - fw * 0.35, cx + dx + fw * w, fy + fw * 0.2], fill=WHITE)
        d.polygon([(cx + dx - fw * w, fy - fw * 0.1), (cx + dx + fw * w, fy - fw * 0.1), (cx + dx, fy - h)], fill=WHITE)
    # the flame's blue core, as in the drawing
    d.ellipse([cx - fw * 0.13, fy - fw * 0.2, cx + fw * 0.13, fy + fw * 0.12], fill=BLUE)
    # sun
    r = H * 0.165
    sy = H * 0.47
    d.ellipse([cx - r, sy - r, cx + r, sy + r], fill=WHITE)
    # crescent below, its horns rising to the sun's middle
    R = H * 0.26
    cy = H * 0.51
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=WHITE)
    R2 = R * 0.93
    d.ellipse([cx - R2, cy - R2 - H * 0.075, cx + R2, cy + R2 - H * 0.075], fill=BLUE)
    d.ellipse([cx - r, sy - r, cx + r, sy + r], fill=WHITE)
    return im


def main():
    big = draw()
    out = {"": (82, 52), "medium/": (41, 26), "small/": (10, 7)}
    for sub, size in out.items():
        p = ROOT / "gfx/flags" / sub / "MDR_MON_KHANATE.tga"
        p.parent.mkdir(parents=True, exist_ok=True)
        big.resize(size, Image.LANCZOS).save(p)
    if "--preview" in sys.argv:
        prev = sys.argv[sys.argv.index("--preview") + 1]
        sheet = Image.new("RGB", (82 * 4 + 41 * 4 + 60, 52 * 4 + 20), (40, 40, 44))
        sheet.paste(big.resize((82 * 4, 52 * 4), Image.LANCZOS), (10, 10))
        sheet.paste(big.resize((82, 52), Image.LANCZOS).resize((41 * 4, 26 * 4), Image.NEAREST), (82 * 4 + 30, 10))
        sheet.save(prev)
    print("flags written")


if __name__ == "__main__":
    main()
