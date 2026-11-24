# Walker (mech) designer art (DISEÑO.md): MD's walker drawing (shipped as Ghana's "tank") for every walker, instead of
# the T-90 MD shows, with each installed module drawn in amber. Also fixes MD's window names: several walker files
# copied the wrong name (the generic artillery and destroyer windows, and Brazil's and China's in all three families,
# share one name), so those walkers never found their window. Each window is named after its file here.
# Writes gfx/interface/equipmentdesigner/mdr_walkers/, interface/mdr_designer_walkers.gfx and full replacements of
# MD's tank_chassis_super_heavy_tank*.gui. Run from the mod folder after each Millennium Dawn update:
# uv run --with pillow --with numpy python herramientas/make_designer_walkers.py [preview]
import glob
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_designer_art import box4, drawing, fill_mask, write_dds  # noqa: E402
from make_designer_ships import Pen, lit  # noqa: E402

MD = "../Millennium-Dawn-2.0.0/"
ED = "gfx/interface/equipmentdesigner/"
T = ED + "tanks/Countries/Ghana/gah_heavy_tank_"
TEX = ED + "mdr_walkers/"
GFX_FILE = "interface/mdr_designer_walkers.gfx"
GUI_DIR = "interface/equipmentdesigner/tanks/"
W, H = 508, 248

ARMS = {"walker_armament_slot_1": (262, 112), "walker_armament_slot_2": (200, 38),
        "walker_armament_slot_3": (150, 70), "walker_armament_slot_4": (240, 150)}
WEAPONS = {"walker_tank_module_tank_barrel": "barrel", "walker_tank_module_railgun": "railgun",
           "walker_tank_module_vls": "vls", "walker_tank_module_heavy_machinegun": "hmg",
           "walker_tank_module_flamethrower": "flamer", "walker_tank_module_rocket_launcher": "rockets",
           "walker_armament_category": "barrel", "walker_light_armament_category": "hmg"}
SPECIAL = {"tank_additional_armor_era": "era", "tank_additional_armor_spaced": "spaced", "tank_smoke_module": "smoke",
           "tank_aa_module": "aa", "tank_support_drone_module": "drone"}


def layers():
    L = np.array(Image.open(MD + T + "blueprint.dds").convert("RGBA")).astype(float)[..., 3] / 255.0
    head, legs = fill_mask(T + "turret"), fill_mask(T + "suspension")
    torso = np.zeros_like(L)
    torso[42:112, 140:250] = 1
    torso *= (1 - head) * (1 - legs)
    out = {"body": np.maximum(L * head, L * torso), "legs2": L * legs,
           "engine": np.maximum(L * torso * (np.arange(W) < 175)[None, :], drawing(ED + "tanks/generic_tank_engine", True))}

    def pen(f):
        p = Pen(W, H)
        f(p)
        return p.done()

    def legs4(p):
        # a second pair of legs behind, dashed
        for x0 in (128, 102):
            p.dashed(x0 + 40, 125, x0 + 20, 175)
            p.dashed(x0 + 20, 175, x0 + 30, 228)
            p.dashed(x0 + 10, 228, x0 + 50, 228)
    out["legs4"] = np.maximum(out["legs2"], pen(legs4))

    def armor(p):
        p.rect(150, 50, 172, 100)
        p.rect(176, 50, 198, 100)
        p.line((205, 30), (262, 30), (270, 80))
    out["armor"] = pen(armor)

    for slot, (x, y) in ARMS.items():
        def weapon(kind, x=x, y=y):
            def f(p):
                p.rect(x - 8, y - 5, x + 4, y + 5)
                if kind == "barrel":
                    p.line((x + 4, y - 1.5), (x + 62, y - 1.5))
                    p.line((x + 4, y + 1.5), (x + 62, y + 1.5))
                    p.rect(x + 62, y - 3, x + 70, y + 3)
                elif kind == "railgun":
                    for dy in (-3, 3):
                        p.line((x + 4, y + dy), (x + 74, y + dy))
                    for k in range(4):
                        p.line((x + 14 + k * 16, y - 3), (x + 14 + k * 16, y + 3))
                elif kind == "vls":
                    p.rect(x - 10, y - 14, x + 10, y - 5)
                    for k in range(1, 4):
                        p.line((x - 10 + k * 5, y - 14), (x - 10 + k * 5, y - 5))
                elif kind == "hmg":
                    p.line((x + 4, y), (x + 30, y))
                    p.rect(x + 8, y + 1, x + 14, y + 6)
                elif kind == "flamer":
                    p.line((x + 4, y), (x + 26, y))
                    p.line((x + 26, y - 3), (x + 30, y - 5))
                    p.line((x + 26, y + 3), (x + 30, y + 5))
                    p.circle(x - 2, y + 11, 5, 3)
                elif kind == "rockets":
                    p.rect(x + 4, y - 6, x + 30, y + 6)
                    for k in range(3):
                        p.circle(x + 26, y - 3 + k * 3, 1.2)
            return f
        for kind in set(WEAPONS.values()):
            out["%s_%s" % (kind, slot)] = pen(weapon(kind))

    def era(p):
        for r in range(3):
            for c in range(3):
                p.rect(146 + c * 9, 50 + r * 14, 153 + c * 9, 61 + r * 14)

    def spaced(p):
        p.rect(150, 135, 178, 160)
        p.rect(150, 165, 178, 195)

    def smoke(p):
        for k in range(4):
            p.line((248 + k * 4, 45), (252 + k * 4, 38))
            p.circle(252.5 + k * 4, 37, 1.5)

    def aa(p):
        p.line((180, 30), (180, 20))
        p.rect(170, 12, 194, 16)
        p.rect(170, 7, 194, 11)

    def drone(p):
        p.circle(140, 20, 4, 2.4)
        p.line((127, 18), (153, 18))
        p.circle(127, 16, 6, 1.3)
        p.circle(153, 16, 6, 1.3)
    for name, f in (("era", era), ("spaced", spaced), ("smoke", smoke), ("aa", aa), ("drone", drone)):
        out[name] = pen(f)
    return out


def main(preview):
    if os.path.isdir(TEX):
        shutil.rmtree(TEX)
    os.makedirs(TEX)
    placed, images, sprites = {}, {}, [("GFX_mdr_walker_bp", T + "blueprint")]
    for part in ("gun", "turret", "suspension"):
        sprites.append(("GFX_mdr_walker_hl_" + part, T + part))
    for layer, strength in layers().items():
        im = lit(strength)
        a = np.array(im)[..., 3]
        if a.max() < 8:
            continue
        ys, xs = np.nonzero(a > 3)
        x0, y0, x1, y1 = box4(xs, ys, im.size)
        write_dds(TEX + layer + ".dds", im.crop((x0, y0, x1, y1)))
        sprites.append(("GFX_mdr_walker_" + layer, TEX + layer))
        placed[layer] = (int(x0), int(y0))
        images[layer] = im
    gfx = ["spriteTypes = {"]
    for n, t in sprites:
        gfx += ["\tspriteType = {", '\t\tname = "%s"' % n, '\t\ttextureFile = "%s.dds"' % t, "\t}"]
    open(GFX_FILE, "w", encoding="utf-8", newline="\n").write("\n".join(gfx + ["}"]) + "\n")

    def icon(sp, t, name="mdr_part", xy=None):
        x, y = xy if xy else placed[sp]
        return [t + "iconType = {", t + '\tname = "%s"' % name, t + '\tspriteType = "GFX_mdr_walker_%s"' % sp,
                t + "\tposition = { x=%d y=%d }" % (x, y), t + "}"]

    def win(name, body, t):
        return [t + "containerWindowType = {", t + '\tname = "%s"' % name, t + "\tposition = { x=0 y=0 }",
                t + "\tsize = { width=100% height=100% }"] + body + [t + "}"]

    def hl(slot, part, t):
        return win(slot + "@highlight", icon("hl_" + part, t + "\t", "blueprint", (0, 0)), t)

    def slots(t):
        out = []
        for slot in ARMS:
            body = []
            for mod, kind in WEAPONS.items():
                body += win(mod, icon("%s_%s" % (kind, slot), t + "\t\t"), t + "\t")
            body += hl(slot, "gun", t + "\t")
            out += win(slot, body, t)
        out += win("walker_body_slot", win("walker_body_slot", icon("body", t + "\t\t"), t + "\t") + hl("walker_body_slot", "turret", t + "\t"), t)
        out += win("walker_engine_slot", win("walker_engine_slot", icon("engine", t + "\t\t"), t + "\t"), t)
        out += win("walker_suspension_slot", win("walker_tank_legs_four_category", icon("legs4", t + "\t\t"), t + "\t")
                   + win("walker_suspension_slot", icon("legs2", t + "\t\t"), t + "\t") + hl("walker_suspension_slot", "suspension", t + "\t"), t)
        for slot in ["walker_special_type_slot_%d" % i for i in (1, 2, 3)] + ["special_type_slot_%d" % i for i in (4, 5, 6)]:
            body = []
            for cat, kind in SPECIAL.items():
                body += win(cat, icon(kind, t + "\t\t"), t + "\t")
            out += win(slot, body, t)
        out += win("armor_type_slot", win("armor_type_slot", icon("armor", t + "\t\t"), t + "\t"), t)
        for slot in ("ammunition_load_slot", "battlestation_type_slot"):
            out += win(slot, [], t)
        return out

    written = 0
    for f in sorted(glob.glob(MD + GUI_DIR + "tank_chassis_super_heavy_tank*.gui")):
        base = os.path.basename(f)
        m = re.fullmatch(r"tank_chassis_super_heavy_tank(_artillery|_destroyer)?(_[a-z]{3})?\.gui", base)
        if not m:
            continue
        name = "equipment_designer_super_heavy_tank%s_chassis%s" % (m.group(1) or "", m.group(2) or "")
        out = ["# Realpolitik: replaces Millennium Dawn's file of the same path. Walker drawing, the window named after",
               "# its file (MD's had copied names), and each installed module drawn in amber",
               "# (generated by herramientas/make_designer_walkers.py, see DISENO.md).", "", "guiTypes = {",
               "\tcontainerWindowType = {", '\t\tname = "%s"' % name,
               "\t\t# NOTE: to keep aligned with the window \"equipment_modules\" in tank_designer_view.gui",
               "\t\tposition = { x=0 y=0 }", "\t\tsize = { width=508 height=248 }"]
        out += icon("bp", "\t\t", "equipment_image_overlay", (0, 0))
        out += win("module_slots", slots("\t\t\t"), "\t\t")
        out += ["\t}", "}"]
        open(GUI_DIR + base, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
        written += 1
    if preview:
        bg = Image.open(MD + ED + "tanks/generic_tank_blueprint_background.dds").convert("RGBA")
        sets = [["body", "engine", "legs2", "barrel_walker_armament_slot_1", "vls_walker_armament_slot_2", "era", "smoke"],
                ["legs4", "armor", "railgun_walker_armament_slot_1", "rockets_walker_armament_slot_4",
                 "hmg_walker_armament_slot_3", "drone", "aa", "spaced"]]
        sheet = Image.new("RGB", (W * 2, H))
        for c, s in enumerate(sets):
            b = bg.copy()
            b.alpha_composite(Image.open(MD + T + "blueprint.dds").convert("RGBA"))
            for layer in s:
                b.alpha_composite(images[layer])
            sheet.paste(b.convert("RGB"), (c * W, 0))
        sheet.save("herramientas/vista_diseno/mechs_todos.png")
    print("files:", written, "sprites:", len(sprites))


if __name__ == "__main__":
    main("preview" in sys.argv)
