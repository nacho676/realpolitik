# Plane designer art (DISEÑO.md, stage 6): MD's airframe blueprints (side view, nose to the right) with each installed
# module drawn in amber. MD's plane windows have no module slots at all; this adds them.
# The wing shape goes in a small top-view inset at the top right, as the armour cut-away does in the tank designer.
# Writes gfx/interface/equipmentdesigner/mdr_planes/, interface/mdr_designer_planes.gfx and a full replacement of
# MD's interface/equipmentdesigner/MD_plane_airframe.gui. Run from the mod folder after each Millennium Dawn update:
# uv run --with pillow --with numpy python herramientas/make_designer_planes.py [preview]
import glob
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_designer_art import LIT, box4, write_dds  # noqa: E402
from make_designer_ships import Pen  # noqa: E402

MD = "../Millennium-Dawn-2.0.3/"
GUI = "interface/equipmentdesigner/MD_plane_airframe.gui"
TEX = "gfx/interface/equipmentdesigner/mdr_planes/"
GFX_FILE = "interface/mdr_designer_planes.gfx"

ENGINES = {"plane_jet_single": ("jet", 1), "plane_light_single": ("jet", 1), "plane_jet_double": ("jet", 2),
           "plane_light_double": ("jet", 2), "plane_jet_quad": ("jet", 4), "plane_jet_six": ("jet", 6),
           "plane_jet_eight": ("jet", 8), "plane_nuclear_eight": ("jet", 8), "plane_prop_single": ("prop", 1),
           "plane_prop_double": ("prop", 2), "plane_prop_quad": ("prop", 4), "plane_prop_six": ("prop", 6),
           "plane_prop_eight": ("prop", 8), "plane_light_quadcopter": ("prop", 4), "plane_solar_single": ("solar", 1),
           "plane_solar_double": ("solar", 2)}
WINGS = ["wing_straight", "wing_swept", "wing_variable", "wing_diamond", "wing_delta", "wing_delta_canard",
         "wing_fwdswept", "wing_flyingwing", "wing_blended", "wing_future_1", "wing_future_2"]
WEAPONS = {"plane_fighter_weapons": "missile", "plane_intercept_weapons": "missile", "plane_stealth_weapons": "missile",
           "plane_stealth_mr_weapons": "missile", "plane_stealth_cas_weapons": "bomb_guided",
           "plane_cas_weapons": "rocket_pod", "plane_guided_bombs": "bomb_guided", "plane_nav_weapons": "ashm",
           "plane_heavy_nav_weapons": "ashm", "plane_strategic_bombs_category": "bomb",
           "plane_heavy_strike_modules": "ashm", "plane_drone_systems": "drone", "plane_droneswarm_weapon": "drone"}
WEAPON_SLOTS = {"fixed_main_weapon_slot": 0.55, "fixed_auxiliary_weapon_slot_1": 0.44,
                "fixed_auxiliary_weapon_slot_2": 0.66, "fixed_auxiliary_weapon_slot_3": 0.34,
                "fixed_auxiliary_weapon_slot_4": 0.76}
SPECIAL = {"plane_countermeasures": "flares", "plane_refueling_systems": "probe", "plane_recon_tgp_systems": "pod",
           "plane_awacs_module": "awacs", "plane_stealth_shape": "stealth", "plane_thrust_vectoring": "vector",
           "plane_asw_systems": "mad", "plane_gunship_modules": "gunship"}
SPECIAL_SLOTS = ["special_slot_type_%d" % i for i in range(1, 6)]


def lit(strength):
    glow = np.array(Image.fromarray((np.clip(strength, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2.5))) / 255.0
    alpha = np.clip(np.maximum(strength, glow * 0.57), 0, 1)
    h, w = strength.shape
    return Image.fromarray(np.dstack([np.broadcast_to(LIT, (h, w, 3)), alpha * 255]).astype("uint8"), "RGBA")


class Plane:
    def __init__(self, texture):
        a = np.array(Image.open(MD + texture).convert("RGBA")).astype(float)
        self.H, self.W = a.shape[:2]
        self.L = a[..., 3] / 255.0
        m = self.L > 0.35
        cols = np.nonzero(m.sum(axis=0) > 0)[0]
        self.x0, self.x1 = float(cols.min()), float(cols.max())
        tops, bots = [], []
        for c in range(int(self.x0 + self.len * 0.3), int(self.x0 + self.len * 0.7)):
            ys = np.nonzero(m[:, c])[0]
            if len(ys):
                tops.append(ys.min())
                bots.append(ys.max())
        mids = (np.array(tops) + np.array(bots)) / 2
        self.cy = float(np.median(mids))
        self.hf = float(np.clip(np.percentile((np.array(bots) - np.array(tops)) / 2, 25), 5, 22))
        self.s = float(np.clip(self.hf * 0.8, 5, 13))

    @property
    def len(self):
        return self.x1 - self.x0

    def x_at(self, f):
        return self.x0 + self.len * f

    def region(self, fx0, fx1, fy0=-9.0, fy1=9.0):
        m = np.zeros_like(self.L)
        y0, y1 = int(self.cy + fy0 * self.hf), int(self.cy + fy1 * self.hf)
        m[max(0, y0):max(0, y1), int(self.x_at(fx0)):int(self.x_at(fx1))] = 1
        return self.L * m

    def draw(self, kind, arg=None):
        p = Pen(self.W, self.H)
        s, cy, hf = self.s, self.cy, self.hf
        belly = cy + hf
        if kind == "fins":
            return self.region(0.0, 0.2, -9, -0.6)
        if kind == "engine_tail":
            out = self.region(0.0, 0.2)
            if arg == "jet":
                x = self.x0 + 2
                p.line((x + s * 1.2, cy - s * 0.45), (x, cy - s * 0.3), (x, cy + s * 0.3), (x + s * 1.2, cy + s * 0.45))
            return np.maximum(out, p.done())
        if kind == "engine":
            typ, n = arg
            if typ == "jet":
                if n == 2:
                    x, y = self.x0 + 2, cy + hf * 0.5
                    p.line((x + s * 1.2, y - s * 0.45), (x, y - s * 0.3), (x, y + s * 0.3), (x + s * 1.2, y + s * 0.45))
                for k in range(n // 2 if n > 2 else 0):
                    xx = self.x_at(0.38 + k * 0.1)
                    p.circle(xx, belly + s * 0.9, s * 1.1, s * 0.45)
                    p.line((xx - s * 1.1, belly + s * 0.9), (xx - s * 1.5, belly + s * 0.9))
            elif typ == "prop":
                if n == 1:
                    x = self.x1 + 2
                    p.line((x, cy - s * 2.2), (x, cy + s * 2.2))
                    p.circle(x - 1.5, cy, s * 0.3)
                for k in range(n // 2):
                    xx = self.x_at(0.4 + k * 0.1)
                    p.circle(xx, belly + s * 0.8, s * 0.9, s * 0.4)
                    p.line((xx + s * 1.0, belly + s * 0.8 - s * 1.4), (xx + s * 1.0, belly + s * 0.8 + s * 1.4))
            else:
                p.rect(self.x_at(0.3), cy - hf - s * 0.5, self.x_at(0.7), cy - hf - s * 0.1)
                for k in range(1, 6):
                    xx = self.x_at(0.3 + k * 0.4 / 6)
                    p.line((xx, cy - hf - s * 0.5), (xx, cy - hf - s * 0.1))
            return p.done()
        if kind == "wing":
            # top-view inset at the top right: fuselage line and the wing planform
            cx, cy2, r = self.W - 46, 34, 26
            p.line((cx - r * 1.1, cy2), (cx + r * 1.1, cy2))
            shapes = {
                "wing_straight": [(0.05, 0), (0.05, 0.95), (-0.25, 0.95), (-0.25, 0)],
                "wing_swept": [(0.2, 0), (-0.35, 0.9), (-0.55, 0.9), (-0.25, 0)],
                "wing_variable": [(0.2, 0), (-0.15, 0.95), (-0.32, 0.95), (-0.2, 0)],
                "wing_diamond": [(0.3, 0), (-0.2, 0.7), (-0.45, 0.65), (-0.45, 0)],
                "wing_delta": [(0.45, 0), (-0.55, 0.8), (-0.55, 0)],
                "wing_delta_canard": [(0.3, 0), (-0.55, 0.8), (-0.55, 0)],
                "wing_fwdswept": [(-0.05, 0), (0.25, 0.9), (0.08, 0.9), (-0.35, 0)],
                "wing_flyingwing": [(0.6, 0), (-0.3, 1.0), (-0.45, 0.85), (-0.3, 0.5), (-0.5, 0.25), (-0.35, 0)],
                "wing_blended": [(0.5, 0), (0.1, 0.25), (-0.4, 0.85), (-0.55, 0.8), (-0.45, 0)],
                "wing_future_1": [(0.55, 0), (-0.4, 0.9), (-0.55, 0.6), (-0.6, 0)],
                "wing_future_2": [(0.5, 0), (0.0, 0.5), (-0.5, 0.9), (-0.6, 0.4), (-0.45, 0)],
            }
            pts = shapes[arg]
            for side in (-1, 1):
                p.line(*[(cx + x * r, cy2 + side * y * r) for x, y in pts])
            if arg == "wing_delta_canard":
                for side in (-1, 1):
                    p.line((cx + 0.75 * r, cy2), (cx + 0.55 * r, cy2 + side * 0.3 * r), (cx + 0.45 * r, cy2))
            if arg == "wing_variable":
                p.circle(cx + 0.05 * r, cy2, 2)
            return p.done()
        if kind in ("missile", "ashm", "bomb", "bomb_guided", "rocket_pod", "drone"):
            x, y = self.x_at(arg), belly + s * 0.9
            p.line((x - s * 0.8, belly + 0.5), (x - s * 0.6, y - s * 0.35))
            if kind in ("missile", "ashm"):
                ln = s * (2.6 if kind == "missile" else 3.4)
                r = s * (0.18 if kind == "missile" else 0.28)
                p.rect(x - ln / 2, y - r, x + ln / 2, y + r)
                p.line((x + ln / 2, y - r), (x + ln / 2 + r * 2.5, y), (x + ln / 2, y + r))
                p.line((x - ln / 2, y - r), (x - ln / 2 - r * 1.5, y - r * 3))
                p.line((x - ln / 2, y + r), (x - ln / 2 - r * 1.5, y + r * 3))
            elif kind in ("bomb", "bomb_guided"):
                p.circle(x, y, s * 0.95, s * 0.36)
                p.line((x - s * 0.95, y), (x - s * 1.4, y - s * 0.4), (x - s * 1.4, y + s * 0.4), (x - s * 0.95, y))
                if kind == "bomb_guided":
                    p.circle(x + s * 1.05, y, s * 0.16)
            elif kind == "rocket_pod":
                p.rect(x - s * 1.1, y - s * 0.4, x + s * 0.9, y + s * 0.4)
                p.line((x + s * 0.9, y - s * 0.4), (x + s * 1.2, y), (x + s * 0.9, y + s * 0.4))
                for k in range(3):
                    p.circle(x - s * 0.7 + k * s * 0.55, y, s * 0.15)
            else:
                p.circle(x, y, s * 0.6, s * 0.22)
                p.line((x - s * 0.4, y - s * 0.7), (x + s * 0.2, y + s * 0.7))
            return p.done()
        if kind == "gun":
            x, y = self.x_at(0.8), cy + hf * 0.3
            p.rect(x - s * 0.5, y - s * 0.18, x + s * 0.2, y + s * 0.18)
            p.line((x + s * 0.2, y), (x + s * 1.3, y))
            return p.done()
        if kind == "pod":
            x, y = self.x_at(0.68), belly + s * 0.7
            p.circle(x, y, s * 1.0, s * 0.32)
            p.circle(x + s * 0.9, y, s * 0.2)
            return p.done()
        if kind == "flares":
            for k in range(5):
                p.circle(self.x0 - 4 - k * s * 0.7, cy + hf * 0.6 + k * s * 0.45, s * 0.14)
            return p.done()
        if kind == "probe":
            x, y = self.x_at(0.86), cy - hf * 0.7
            p.line((x, y), (self.x1 + s * 0.4, y - s * 0.5))
            p.circle(self.x1 + s * 0.55, y - s * 0.55, s * 0.18)
            return p.done()
        if kind == "awacs":
            x, y = self.x_at(0.42), cy - hf - s * 1.3
            p.line((x - s * 0.5, cy - hf), (x - s * 0.3, y + s * 0.3))
            p.line((x + s * 0.5, cy - hf), (x + s * 0.3, y + s * 0.3))
            p.circle(x, y, s * 2.4, s * 0.4)
            return p.done()
        if kind == "stealth":
            p.line((self.x_at(0.12), cy), (self.x_at(0.35), cy - hf * 0.8), (self.x_at(0.7), cy - hf * 0.8), (self.x_at(0.95), cy))
            p.line((self.x_at(0.12), cy), (self.x_at(0.35), cy + hf * 0.8), (self.x_at(0.7), cy + hf * 0.8), (self.x_at(0.95), cy))
            return p.done()
        if kind == "vector":
            x = self.x0 + 1
            for dy in (-0.5, -0.17, 0.17, 0.5):
                p.line((x, cy + dy * s), (x - s * 0.8, cy + dy * s * 1.5))
            return p.done()
        if kind == "mad":
            p.line((self.x0, cy), (self.x0 - s * 2.5, cy))
            p.circle(self.x0 - s * 2.6, cy, s * 0.2)
            for k in range(3):
                p.circle(self.x_at(0.3 + k * 0.06), belly + s * 0.5, s * 0.15)
            return p.done()
        if kind == "gunship":
            for k in range(3):
                x = self.x_at(0.45 + k * 0.08)
                p.line((x, cy + hf * 0.4), (x + s * 0.4, cy + hf + s * 0.9))
            return p.done()
        raise ValueError(kind)


def main(preview):
    if os.path.isdir(TEX):
        shutil.rmtree(TEX)
    os.makedirs(TEX)
    sprite_tex = {}
    for f in glob.glob(MD + "interface/*.gfx"):
        for n, t in re.findall(r'name\s*=\s*"(GFX_TC_[^"]+)"\s*textureFile\s*=\s*"([^"]+)"', open(f, encoding="utf-8", errors="ignore").read()):
            sprite_tex[n] = t
    text = open(MD + GUI, encoding="utf-8").read()
    windows = re.findall(r'name\s*=\s*"(equipment_designer_[a-z_0-9]+)".*?spriteType\s*=\s*"([^"]+)"', text, flags=re.S)
    # Plane types MD left without a window (the designer showed them empty): use their base airframe's drawing
    have = {n for n, _ in windows}
    for fam, base in (("medium_plane_suicide_airframe", "medium_plane_airframe"),):
        for i in range(7):
            src = dict(windows).get("equipment_designer_%s_%d" % (base, i))
            if src and "equipment_designer_%s_%d" % (fam, i) not in have:
                windows.append(("equipment_designer_%s_%d" % (fam, i), src))
    planes, made, sprites, previews = {}, {}, [], {}
    # MD's windows for generation 5 point to sprites it never defined: borrow the next generation's drawing
    for _, sp in windows:
        if sp not in sprite_tex:
            m = re.fullmatch(r"(.+_)(\d)", sp)
            for d in ((int(m.group(2)) + 1, int(m.group(2)) - 1) if m else ()):
                if m.group(1) + str(d) in sprite_tex:
                    sprite_tex[sp] = sprite_tex[m.group(1) + str(d)]
                    sprites.append((sp, sprite_tex[sp][:-4]))
                    break

    def layer(tex, kind, arg, tag, shared=False):
        key = ("all" if shared else os.path.basename(tex)[:-4], tag)
        if key not in made:
            plane = planes.setdefault(tex, Plane(tex))
            im = lit(plane.draw(kind, arg))
            a = np.array(im)[..., 3]
            if a.max() < 8:
                made[key] = None
                return None
            ys, xs = np.nonzero(a > 3)
            x0, y0, x1, y1 = box4(xs, ys, im.size)
            name = "%s_%s" % key
            write_dds(TEX + name + ".dds", im.crop((x0, y0, x1, y1)))
            sprites.append(("GFX_mdr_plane_" + name, TEX + name))
            made[key] = ("GFX_mdr_plane_" + name, int(x0), int(y0), im)
        return made[key]

    def container(name, *entries):
        out = ["containerWindowType = {", '\tname = "%s"' % name, "\tposition = { x=0 y=0 }", "\tsize = { width=100% height=100% }"]
        for i, entry in enumerate(e for e in entries if e):
            sp, x, y, _ = entry
            out += ["\ticonType = {", '\t\tname = "mdr_part_%d"' % i, '\t\tspriteType = "%s"' % sp, "\t\tposition = { x=%d y=%d }" % (x, y), "\t}"]
        return out + ["}"]

    out = ["# Realpolitik: replaces Millennium Dawn's file of the same path. Same windows, plus module slots with each",
           "# installed module drawn in amber (generated by herramientas/make_designer_planes.py, see DISENO.md).", "",
           "guiTypes = {"]
    for name, sprite in windows:
        tex = sprite_tex.get(sprite)
        body = ["containerWindowType = {", '\tname = "%s"' % name, "\tposition = { x=0 y=0 }",
                "\tsize = { width=584 height=248 }", "\ticonType = {", '\t\tname = "equipment_image_overlay"',
                '\t\tspriteType = "%s"' % sprite, "\t}"]
        slots = []
        if tex and os.path.exists(MD + tex):
            pv = previews.setdefault(tex, [])
            eng = [container(c, layer(tex, "engine_tail", v[0], "tail_" + v[0]), layer(tex, "engine", v, "engine_%s%d" % v))
                   for c, v in ENGINES.items()]
            slots.append(("engine_type_slot", eng))
            pv += [made[(os.path.basename(tex)[:-4], "tail_jet")], made[(os.path.basename(tex)[:-4], "engine_jet2")]]
            fins = layer(tex, "fins", None, "fins")
            wings = [container(w, fins, layer(tex, "wing", w, w, True)) for w in WINGS]
            slots.append(("wingform_type_slot", wings))
            pv += [fins, made[("all", "wing_delta")]]
            for slot, at in WEAPON_SLOTS.items():
                inner = []
                for cat, kind in WEAPONS.items():
                    inner += container(cat, layer(tex, kind, at, "%s_%d" % (kind, at * 100)))
                slots.append((slot, [inner]))
            pv.append(made[(os.path.basename(tex)[:-4], "missile_55")])
            pv.append(made[(os.path.basename(tex)[:-4], "bomb_guided_66")])
            slots.append(("fixed_gun_slot", [container("plane_multipurpose_gun", layer(tex, "gun", None, "gun")),
                                             container("plane_recon_tgp_systems", layer(tex, "pod", None, "pod"))]))
            pv.append(made[(os.path.basename(tex)[:-4], "gun")])
            for slot in SPECIAL_SLOTS:
                slots.append((slot, [container(c, layer(tex, k, None, k)) for c, k in SPECIAL.items()]))
            pv.append(made[(os.path.basename(tex)[:-4], "flares")])
            pv.append(made[(os.path.basename(tex)[:-4], "probe")])
        if slots:
            ms = ["containerWindowType = {", '\tname = "module_slots"', "\tposition = { x=0 y=0 }",
                  "\tsize = { width=100% height=100% }"]
            for slot, conts in slots:
                ms += ["\tcontainerWindowType = {", '\t\tname = "%s"' % slot, "\t\tposition = { x=0 y=0 }",
                       "\t\tsize = { width=100% height=100% }"]
                for c in conts:
                    ms += ["\t\t" + line for line in c]
                ms.append("\t}")
            body += ["\t" + line for line in ms + ["}"]]
        out += ["\t" + line for line in body + ["}"]]
    out.append("}")
    open(GUI, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
    gfx = ["spriteTypes = {"]
    for n, t in sprites:
        gfx += ["\tspriteType = {", '\t\tname = "%s"' % n, '\t\ttextureFile = "%s.dds"' % t, "\t}"]
    open(GFX_FILE, "w", encoding="utf-8", newline="\n").write("\n".join(gfx + ["}"]) + "\n")
    if preview:
        bg = Image.open(MD + "gfx/interface/equipmentdesigner/planes/generic_plane_blueprint_background.dds").convert("RGBA")
        items = sorted(previews.items())
        sheet = Image.new("RGB", (584 * 3, 248 * ((len(items) + 2) // 3)))
        for i, (tex, ims) in enumerate(items):
            b = bg.copy()
            b.alpha_composite(Image.open(MD + tex).convert("RGBA"))
            for e in ims:
                if e:
                    b.alpha_composite(e[3])
            sheet.paste(b.convert("RGB"), ((i % 3) * 584, (i // 3) * 248))
        sheet.save("herramientas/vista_diseno/aviones_todos.png")
    print("windows:", len(windows), "airframes:", len(planes), "sprites:", len(sprites))


if __name__ == "__main__":
    main("preview" in sys.argv)
