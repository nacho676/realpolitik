# Ship designer art (DISEÑO.md, stage 5): each installed module drawn in amber, seen from above, in its place on MD's
# top views (bow to the right). MD's hull windows already list a container per allowed category in each slot, all
# empty but one; this copies them and puts an icon in each container.
# Writes gfx/interface/equipmentdesigner/mdr_ships/, interface/mdr_designer_ships.gfx and full replacements of
# MD's interface/equipmentdesigner/MD_ship_hull_*.gui. Run from the mod folder after each Millennium Dawn update:
# uv run --with pillow --with numpy python herramientas/make_designer_ships.py [preview]
import glob
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_designer_art import LIT, box4, write_dds  # noqa: E402

from PIL import ImageFilter  # noqa: E402

MD = "../Millennium-Dawn-2.0.3/"
TEX = "gfx/interface/equipmentdesigner/mdr_ships/"
GFX_FILE = "interface/mdr_designer_ships.gfx"
SS = 4

# Where each slot sits, as a fraction of the hull length from the stern
SLOT_AT = {"fixed_ship_battery_slot": 0.84, "front_1_custom_slot": 0.76, "front_2_custom_slot": 0.68,
           "mid_3_custom_slot": 0.62, "fixed_ship_radar_slot": 0.55, "mid_1_custom_slot": 0.47,
           "mid_2_custom_slot": 0.39, "fixed_ship_engine_slot": 0.33, "fixed_ship_auxillary_slot": 0.3,
           "rear_2_custom_slot": 0.24, "rear_1_custom_slot": 0.14}
# Category -> icon. Internal modules (fuel, fire control, missile load, drone control, upgrades) are not drawn.
ICON = {"light_guns": "gun_light", "heavy_guns": "gun_heavy", "gun_battery": "gun_heavy", "railguns": "railgun",
        "railgun_battery": "railgun", "point_defense_system": "ciws", "naval_adl": "laser", "turret_missile": "launcher",
        "vls_small": "vls_small", "vls_large": "vls_large", "vls_capital": "vls_large", "vls_sub": "vls_sub",
        "torpedoes": "torpedo", "anti_ship_torpedoes": "torpedo", "nuclear_torpedoes": "torpedo",
        "anti_ship_nuclear_torpedoes": "torpedo", "anti_ship_drone_torpedoes": "torpedo",
        "anti_submarine_mortar": "asw_mortar", "minelaying": "mines", "mineclearing": "sweep",
        "light_helipad": "helipad", "helipads": "helipad", "flight_decks": "flightdeck", "light_flight_decks": "flightdeck",
        "deck_takeoff": "flightdeck", "radar": "radar", "drone_radar": "drone_radar", "esm": "esm", "sub_esm": "esm",
        "radar_jammer": "esm", "sonar": "sonar", "surface_power_source": "engine",
        "light_surface_power_source": "engine", "sub_power_source": "engine"}
# Preview: one module per slot, the first of these it allows
PREFER = ["flightdeck", "gun_light", "gun_heavy", "vls_large", "vls_sub", "launcher", "radar", "engine", "helipad", "ciws",
          "torpedo", "vls_small"]
# Icons drawn at a fixed place whatever the slot
FIXED_AT = {"sonar": 0.93, "engine": 0.36}


class Pen:
    def __init__(self, w, h):
        self.W, self.H = w, h
        self.im = Image.new("L", (w * SS, h * SS), 0)
        self.d = ImageDraw.Draw(self.im)
        self.w = int(1.3 * SS)

    def p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, *pts):
        self.d.line(self.p(pts), fill=255, width=self.w, joint="curve")

    def rect(self, x0, y0, x1, y1):
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], outline=255, width=self.w)

    def circle(self, cx, cy, rx, ry=None):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], outline=255, width=self.w)

    def dashed(self, x0, y0, x1, y1, dash=3.0):
        n = max(1, int(np.hypot(x1 - x0, y1 - y0) / dash))
        for i in range(0, n, 2):
            a, b = i / n, min(1, (i + 1) / n)
            self.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b))

    def dashed_ellipse(self, cx, cy, rx, ry, n=28):
        for i in range(0, n, 2):
            a0, a1 = 2 * np.pi * i / n, 2 * np.pi * (i + 1) / n
            self.line((cx + rx * np.cos(a0), cy + ry * np.sin(a0)), (cx + rx * np.cos(a1), cy + ry * np.sin(a1)))

    def done(self):
        return np.array(self.im.resize((self.W, self.H), Image.LANCZOS)) / 255.0


class Hull:
    def __init__(self, texture):
        a = np.array(Image.open(MD + texture).convert("RGBA")).astype(float)
        self.H, self.W = a.shape[:2]
        m = a[..., 3] > 128
        cols = np.nonzero(m.sum(axis=0) > 2)[0]
        self.x0, self.x1 = cols.min(), cols.max()
        self.m = m
        mid = m[:, int(self.x0 + (self.x1 - self.x0) * 0.5)]
        ys = np.nonzero(mid)[0]
        self.cy = (ys.min() + ys.max()) / 2
        self.half = (ys.max() - ys.min()) / 2
        self.s = float(np.clip(self.half * 0.62, 6, 17))

    def x_at(self, f):
        return self.x0 + (self.x1 - self.x0) * f

    def half_at(self, x):
        ys = np.nonzero(self.m[:, int(np.clip(x, 0, self.W - 1))])[0]
        return (ys.max() - ys.min()) / 2 if len(ys) else self.half

    def icon(self, kind, f):
        p = Pen(self.W, self.H)
        x, y, s, L = self.x_at(f), self.cy, self.s, self.x1 - self.x0
        hw = self.half_at(x)
        if kind == "gun_light":
            p.circle(x, y, s * 0.55)
            p.line((x + s * 0.5, y), (x + s * 1.5, y))
        elif kind == "gun_heavy":
            p.rect(x - s * 0.8, y - s * 0.7, x + s * 0.6, y + s * 0.7)
            for dy in (-0.4, 0, 0.4):
                p.line((x + s * 0.6, y + dy * s), (x + s * 2.0, y + dy * s))
        elif kind == "railgun":
            p.rect(x - s * 0.7, y - s * 0.55, x + s * 0.5, y + s * 0.55)
            for dy in (-0.25, 0.25):
                p.line((x + s * 0.5, y + dy * s), (x + s * 2.6, y + dy * s))
        elif kind == "ciws":
            p.circle(x, y, s * 0.36)
            p.circle(x, y, s * 0.14)
            p.line((x + s * 0.34, y), (x + s * 0.85, y))
        elif kind == "laser":
            p.circle(x, y, s * 0.36)
            p.line((x + s * 0.36, y), (x + s * 0.6, y - s * 0.22), (x + s * 0.84, y), (x + s * 0.6, y + s * 0.22), (x + s * 0.36, y))
        elif kind == "launcher":
            for side in (-1, 1):
                yy = y + side * min(hw * 0.5, s * 0.75)
                p.rect(x - s * 0.6, yy - s * 0.24, x + s * 0.6, yy + s * 0.24)
                p.line((x - s * 0.4, yy), (x + s * 0.4, yy))
        elif kind in ("vls_small", "vls_large"):
            rows, cols = (2, 4) if kind == "vls_small" else (3, 6)
            c = s * 0.32
            ox, oy = x - cols * c / 2, y - rows * c / 2
            p.rect(ox, oy, ox + cols * c, oy + rows * c)
            for i in range(1, cols):
                p.line((ox + i * c, oy), (ox + i * c, oy + rows * c))
            for j in range(1, rows):
                p.line((ox, oy + j * c), (ox + cols * c, oy + j * c))
        elif kind == "vls_sub":
            for i in range(4):
                for j in (-1, 1):
                    p.circle(x - s * 0.9 + i * s * 0.6, y + j * s * 0.3, s * 0.2)
        elif kind == "torpedo":
            for side in (-1, 1):
                yy = y + side * hw * 0.7
                for k in range(3):
                    p.line((x - s * 0.6, yy + side * k * 1.6), (x + s * 0.6, yy + side * k * 1.6 - side * s * 0.3))
        elif kind == "asw_mortar":
            p.rect(x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3)
            for a in np.linspace(-0.9, 0.9, 5):
                p.line((x + s * 0.3, y + a * s * 0.25), (x + s * 0.8, y + a * s * 0.6))
        elif kind == "mines":
            for side in (-1, 1):
                yy = y + side * hw * 0.45
                p.line((x + s * 1.2, yy), (self.x0 + 2, yy))
                for k in range(3):
                    p.circle(x - k * s * 0.7, yy, s * 0.16)
        elif kind == "sweep":
            for side in (-1, 1):
                p.dashed(self.x0 + 4, y + side * hw * 0.3, self.x0 - s * 2.2, y + side * (hw + s * 1.1))
        elif kind == "helipad":
            r = min(s * 0.95, hw * 0.85)
            p.circle(x, y, r)
            p.line((x - r * 0.35, y - r * 0.4), (x - r * 0.35, y + r * 0.4))
            p.line((x + r * 0.35, y - r * 0.4), (x + r * 0.35, y + r * 0.4))
            p.line((x - r * 0.35, y), (x + r * 0.35, y))
        elif kind == "flightdeck":
            x0, x1 = self.x_at(0.06), self.x_at(0.86)
            h = hw * 0.75
            p.rect(x0, y - h, x1, y + h)
            p.dashed(x0 + 4, y, x1 - 4, y, 5)
            p.line((x0 + L * 0.05, y + h * 0.7), (self.x_at(0.55), y - h * 0.8))
        elif kind == "radar":
            p.rect(x - s * 0.3, y - s * 0.3, x + s * 0.3, y + s * 0.3)
            p.line((x - s * 0.9, y - s * 0.35), (x + s * 0.9, y + s * 0.35))
            p.circle(x, y, s * 1.0)
        elif kind == "drone_radar":
            p.circle(x, y - s * 0.9, s * 0.2)
            for dx in (-1, 1):
                for dy in (-1, 1):
                    p.line((x, y - s * 0.9), (x + dx * s * 0.5, y - s * 0.9 + dy * s * 0.35))
                    p.circle(x + dx * s * 0.55, y - s * 0.9 + dy * s * 0.4, s * 0.18)
        elif kind == "esm":
            for dy in (-0.45, 0.45):
                p.circle(x - s * 0.2, y + dy * s, s * 0.26)
            p.line((x - s * 0.2, y - s * 0.2), (x - s * 0.2, y + s * 0.2))
        elif kind == "sonar":
            p.dashed_ellipse(x, y, s * 1.1, hw * 0.55)
        elif kind == "engine":
            p.dashed_ellipse(x, y, L * 0.09, hw * 0.45)
            p.circle(x + L * 0.02, y, s * 0.35, s * 0.25)
        return p.done()


def lit(strength):
    glow = np.array(Image.fromarray((np.clip(strength, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2.5))) / 255.0
    alpha = np.clip(np.maximum(strength, glow * 0.57), 0, 1)
    h, w = strength.shape
    return Image.fromarray(np.dstack([np.broadcast_to(LIT, (h, w, 3)), alpha * 255]).astype("uint8"), "RGBA")


def sprite_textures():
    tex = {}
    for f in glob.glob(MD + "interface/*.gfx"):
        for name, path in re.findall(r'name\s*=\s*"(GFX_SD_[^"]+)"\s*textureFile\s*=\s*"([^"]+)"', open(f, encoding="utf-8", errors="ignore").read()):
            tex[name] = path
    return tex


def main(preview):
    if os.path.isdir(TEX):
        shutil.rmtree(TEX)
    os.makedirs(TEX)
    textures = sprite_textures()
    hulls, made, sprites = {}, {}, []
    previews, images = {}, {}
    for f in sorted(glob.glob(MD + "interface/equipmentdesigner/MD_ship_hull_*.gui")):
        lines = open(f, encoding="utf-8").read().split("\n")
        out, stack, image, pending = [], [], None, None
        for line in lines:
            out.append(line)
            m = re.search(r'spriteType\s*=\s*"(GFX_SD_[^"]+)"', line)
            if m and stack and stack[-1] is not None and stack[-1].startswith("equipment_image"):
                image = m.group(1)
            if re.search(r"(containerWindowType|iconType)\s*=\s*\{", line):
                stack.append(None)
                continue
            m = re.search(r'name\s*=\s*"([^"]+)"', line)
            if m and stack and stack[-1] is None:
                stack[-1] = m.group(1)
                mod = re.fullmatch(r"module_(.+)_category", m.group(1))
                slot = stack[-2] if len(stack) > 1 else None
                if mod and slot in SLOT_AT and ICON.get(mod.group(1)) and image in textures:
                    pending = (slot, ICON[mod.group(1)])
            if pending and re.search(r"size\s*=\s*\{", line):
                slot, kind = pending
                pending = None
                tv = textures[image]
                hull = hulls.setdefault(tv, Hull(tv))
                at = FIXED_AT.get(kind, SLOT_AT[slot])
                key = (os.path.basename(tv)[:-4], kind, round(at * 100))
                if key not in made:
                    im = lit(hull.icon(kind, at))
                    a = np.array(im)[..., 3]
                    ys, xs = np.nonzero(a > 3)
                    x0, y0, x1, y1 = box4(xs, ys, im.size)
                    name = "%s_%s_%d" % key
                    write_dds(TEX + name + ".dds", im.crop((x0, y0, x1, y1)))
                    sprites.append(("GFX_mdr_ship_" + name, TEX + name))
                    made[key] = ("GFX_mdr_ship_" + name, int(x0), int(y0))
                    images[key] = im
                previews.setdefault(tv, {}).setdefault(slot, {})[kind] = images[key]
                sp, x, y = made[key]
                ind = re.match(r"\s*", line).group(0)
                out += [ind + "iconType = {", ind + '\tname = "mdr_part"', ind + '\tspriteType = "%s"' % sp,
                        ind + "\tposition = { x=%d y=%d }" % (x, y), ind + "}"]
            if "}" in line and "{" not in line:
                for _ in range(line.count("}")):
                    if stack:
                        stack.pop()
        dest = "interface/equipmentdesigner/" + os.path.basename(f)
        head = "# Realpolitik: copy of Millennium Dawn's file with an amber icon in each module container\n" \
               "# (generated by herramientas/make_designer_ships.py, see DISENO.md).\n"
        open(dest, "w", encoding="utf-8", newline="\n").write(head + "\n".join(out))
    gfx = ["spriteTypes = {"]
    for n, t in sprites:
        gfx += ["\tspriteType = {", '\t\tname = "%s"' % n, '\t\ttextureFile = "%s.dds"' % t, "\t}"]
    open(GFX_FILE, "w", encoding="utf-8", newline="\n").write("\n".join(gfx + ["}"]) + "\n")
    if preview:
        sheet = Image.new("RGB", (508 * 2, 248 * 4), (20, 30, 60))
        for i, (tv, ims) in enumerate(sorted(previews.items())):
            base = Image.new("RGBA", (508, 248), (20, 30, 60, 255))
            base.alpha_composite(Image.open(MD + tv).convert("RGBA"))
            for slot, kinds in ims.items():
                for k in PREFER:
                    if k in kinds:
                        base.alpha_composite(kinds[k])
                        break
            sheet.paste(base.convert("RGB"), ((i % 2) * 508, (i // 2) * 248))
        sheet.save("herramientas/vista_diseno/barcos_todos.png")
    print("hulls:", len(hulls), "sprites:", len(sprites))


if __name__ == "__main__":
    main("preview" in sys.argv)
