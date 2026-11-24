# Helicopter designer art (DISEÑO.md): MD's helicopter blueprints (side view, nose to the right) with each installed
# module drawn in amber. MD's helicopter windows (heavy_tank_chassis = attack, heavy_tank_amphibious_chassis =
# transport) have empty slots and use one drawing for everyone; Italy gets MD's unused Italian drawing.
# Places on each drawing are set by hand below (two drawings only). Writes gfx/interface/equipmentdesigner/mdr_helis/,
# interface/mdr_designer_helis.gfx and full replacements of MD's tank_chassis_heavy_tank(_amphibious)(_TAG).gui.
# Run from the mod folder after each Millennium Dawn update:
# uv run --with pillow --with numpy python herramientas/make_designer_helicopters.py [preview]
import glob
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_designer_art import box4, write_dds  # noqa: E402
from make_designer_ships import Pen, lit  # noqa: E402

MD = "../Millennium-Dawn-2.0.3/"
ED = "gfx/interface/equipmentdesigner/"
TEX = ED + "mdr_helis/"
GFX_FILE = "interface/mdr_designer_helis.gfx"
GUI_DIR = "interface/equipmentdesigner/tanks/"
HELI_SPRITE = "GFX_TC_attack_helicopter_airframe"
W, H = 508, 248

# Points on each drawing (pixels of the 508 x 248 image)
DRAW = {
    "generic": {"tex": ED + "helicopters/generic/generic_helicopter_blueprint", "hub": (318, 92),
                "rotor": ((100, 72), (503, 105)), "tail": (48, 80), "engine": (235, 95, 400, 130),
                "body": (100, 108, 472, 195), "cabin": (300, 138, 385, 178), "cockpit": (392, 120, 470, 185),
                "chin": (445, 186), "sensor": (468, 150),
                "mounts": {"helicopter_wing_mount_1": (238, 172), "helicopter_wing_mount_2": (272, 175),
                           "helicopter_body_mount_1": (305, 190), "helicopter_body_mount_2": (340, 190)},
                "flares": (150, 138), "aps": (402, 126), "antenna": (185, 110)},
    "ita": {"tex": ED + "helicopters/countries/italy/ita_helicopter_blueprint", "hub": (300, 74),
            "rotor": ((90, 76), (500, 92)), "tail": (40, 95), "engine": (200, 84, 330, 120),
            "body": (50, 95, 456, 178), "cabin": (240, 118, 320, 160), "cockpit": (330, 98, 452, 165),
            "chin": (430, 172), "sensor": (452, 140),
            "mounts": {"helicopter_wing_mount_1": (232, 166), "helicopter_wing_mount_2": (266, 168),
                       "helicopter_body_mount_1": (196, 166), "helicopter_body_mount_2": (165, 164)},
            "flares": (118, 136), "aps": (332, 108), "antenna": (150, 118)},
}
TAGS = {"ita": "ita"}

WEAPONS = {"helicopter_atgm_type": "atgm", "helicopter_heavy_atgm_type": "atgm_heavy",
           "helicopter_multiple_atgm_type": "atgm_rack", "helicopter_rockets_type": "rockets",
           "helicopter_gun_pods_type": "gunpod", "helicopter_wing_armament": "aam", "defensive_guns": "doorgun",
           "helicopter_drone_control_type_category": "drone"}
SLOTS = [
    ("nose_gun_type_slot", [("helicopter_light_nose_gun", "gun_light"), ("helicopter_medium_nose_gun", "gun_medium"),
                            ("helicopter_heavy_nose_gun", "gun_heavy")]),
    ("top_mount_type_slot", [("helicopter_mast_mounted_radar", "mast_radar"), ("helicopter_mast_mounted_camera", "mast_cam")]),
    ("helicopter_body_layout", [("gunship_layout", "cabin"), ("light_gunship_layout", "cabin"),
                                ("gunship_transport_layout", "cabin_troops"), ("transport_layout", "cabin_troops"),
                                ("heavy_transport_layout", "cabin_troops")]),
    ("chassis_type_slot", [("helicopter_chassis_type", "body"), ("chassis_type_slot", "body")]),
    ("engine_type_slot", [("helicopter_coaxial_engine_type", "engine_coax"), ("engine_type_slot", "engine")]),
    ("armor_type_slot", [("armor_type_slot", "armor")]),
] + [(m, [(c, k) for c, k in WEAPONS.items()]) for m in ("helicopter_body_mount_1", "helicopter_body_mount_2",
                                                        "helicopter_wing_mount_1", "helicopter_wing_mount_2")] + [
    ("sensor_and_avionics_slot", [("helicopter_sensor_and_avionics_type", "sensor")]),
] + [(d, [("helicopter_defence_type", "flares"), ("helicopter_stealth_module", "stealth"),
          ("helicopter_em_lock_type", "antenna"), ("helicopter_active_defence_type", "aps")])
     for d in ("defence_type_slot", "defence_type_slot_2")]


def region(L, box):
    x0, y0, x1, y1 = box
    m = np.zeros_like(L)
    m[y0:y1, x0:x1] = 1
    return L * m


def layers(name):
    d = DRAW[name]
    L = np.array(Image.open(MD + d["tex"] + ".dds").convert("RGBA")).astype(float)[..., 3] / 255.0
    (rx0, ry0), (rx1, ry1) = d["rotor"]
    rotor = np.zeros_like(L)
    for x in range(rx0, rx1):
        y = int(ry0 + (ry1 - ry0) * (x - rx0) / (rx1 - rx0))
        rotor[max(0, y - 4):y + 5, x] = 1
    hx, hy = d["hub"]
    rotor[max(0, hy - 14):hy + 10, hx - 16:hx + 16] = 1
    out = {}

    def pen(f):
        p = Pen(W, H)
        f(p)
        return p.done()

    out["body"] = region(L, d["body"]) * (1 - rotor)
    out["engine"] = np.maximum(region(L, d["engine"]), L * rotor)

    def coax(p):
        (a, b), (c, e) = d["rotor"]
        p.line((a + 20, b - 10), (c - 20, e - 10))
        p.line((hx, hy), (hx, hy - 10))
    out["engine_coax"] = np.maximum(out["engine"], pen(coax))

    def armor(p):
        x0, y0, x1, y1 = d["cockpit"]
        p.line((x0 + 4, y1 - 4), (x0 + 10, y0 + 8), (x1 - 18, y0 + 8), (x1 - 4, y1 - 10))
    out["armor"] = np.maximum(region(L, d["cockpit"]), pen(armor))
    out["cabin"] = region(L, d["cabin"])

    def troops(p):
        x0, y0, x1, y1 = d["cabin"]
        p.rect(x0 + 6, y0 + 6, x0 + (x1 - x0) * 0.55, y1 - 4)
        for k in range(4):
            p.circle(x0 + 12 + k * (x1 - x0) * 0.18, (y0 + y1) / 2 + 2, 2.5)
    out["cabin_troops"] = np.maximum(out["cabin"], pen(troops))

    cx, cy = d["chin"]

    def gun(n, length):
        def f(p):
            p.circle(cx, cy, 5)
            for k in range(n):
                yy = cy + (k - (n - 1) / 2) * 2.2
                p.line((cx + 4, yy), (cx + 4 + length, yy))
        return f
    out["gun_light"] = pen(gun(1, 14))
    out["gun_medium"] = pen(gun(1, 20))
    out["gun_heavy"] = pen(gun(3, 18))

    def mast_radar(p):
        p.line((hx, hy - 4), (hx, hy - 14))
        p.circle(hx, hy - 19, 11, 5)
    out["mast_radar"] = pen(mast_radar)

    def mast_cam(p):
        p.line((hx, hy - 4), (hx, hy - 12))
        p.circle(hx, hy - 17, 5)
        p.circle(hx + 1.5, hy - 17, 1.8)
    out["mast_cam"] = pen(mast_cam)

    sx, sy = d["sensor"]

    def sensor(p):
        p.circle(sx, sy, 6)
        p.circle(sx + 2, sy, 2.5)
        p.line((sx - 4, sy - 6), (sx - 4, sy - 9))
    out["sensor"] = pen(sensor)

    fx, fy = d["flares"]

    def flares(p):
        p.rect(fx - 6, fy - 4, fx + 6, fy + 4)
        for k in range(4):
            p.circle(fx - 10 - k * 6, fy + 6 + k * 4, 1.4)
    out["flares"] = pen(flares)

    def stealth(p):
        x0, y0, x1, y1 = d["body"]
        p.line((x0 + 40, (y0 + y1) / 2), (x0 + 120, y0 + 12), (x1 - 80, y0 + 12), (x1 - 10, (y0 + y1) / 2 + 10))
    out["stealth"] = pen(stealth)

    ax, ay = d["antenna"]

    def antenna(p):
        p.line((ax, ay), (ax + 3, ay - 12))
        p.line((ax + 10, ay), (ax + 13, ay - 9))
        p.circle(ax + 3.5, ay - 13, 1.8)
    out["antenna"] = pen(antenna)

    px, py = d["aps"]

    def aps(p):
        p.rect(px - 6, py - 4, px + 6, py + 4)
        p.line((px + 6, py), (px + 11, py - 4))
        p.rect(px - 40, py + 2, px - 30, py + 8)
    out["aps"] = pen(aps)

    for mount, (mx, my) in d["mounts"].items():
        def weapon(kind, mx=mx, my=my):
            def f(p):
                p.line((mx, my - 9), (mx, my - 4))
                if kind in ("atgm", "atgm_heavy"):
                    n = 2 if kind == "atgm" else 4
                    for k in range(n):
                        y = my - 3 + k * 3.2
                        p.rect(mx - 9, y, mx + 9, y + 2.6)
                elif kind == "atgm_rack":
                    for r in range(2):
                        for c in range(4):
                            p.circle(mx - 6 + c * 4, my - 1 + r * 4, 1.6)
                    p.rect(mx - 9, my - 3.5, mx + 9, my + 5.5)
                elif kind == "rockets":
                    p.rect(mx - 10, my - 3, mx + 7, my + 4)
                    p.line((mx + 7, my - 3), (mx + 11, my + 0.5), (mx + 7, my + 4))
                elif kind == "gunpod":
                    p.rect(mx - 9, my - 3, mx + 5, my + 3)
                    p.line((mx + 5, my), (mx + 15, my))
                elif kind == "aam":
                    p.rect(mx - 10, my - 1.5, mx + 8, my + 1.5)
                    p.line((mx + 8, my - 1.5), (mx + 12, my), (mx + 8, my + 1.5))
                    p.line((mx - 10, my - 1.5), (mx - 13, my - 4))
                elif kind == "doorgun":
                    p.line((mx - 4, my - 4), (mx + 12, my - 1))
                    p.rect(mx - 7, my - 6, mx - 2, my - 2)
                elif kind == "drone":
                    p.circle(mx, my + 2, 5, 2)
                    p.line((mx - 8, my - 1), (mx + 8, my - 1))
            return f
        for kind in set(WEAPONS.values()):
            out["%s_%s" % (kind, mount)] = pen(weapon(kind))
    return out


def main(preview):
    if os.path.isdir(TEX):
        shutil.rmtree(TEX)
    os.makedirs(TEX)
    placed, images, sprites = {}, {}, []
    for name, d in DRAW.items():
        placed[name], images[name] = {}, {}
        sprites.append(("GFX_mdr_heli_bp_%s" % name, d["tex"]))
        for layer, strength in layers(name).items():
            im = lit(strength)
            a = np.array(im)[..., 3]
            if a.max() < 8:
                continue
            ys, xs = np.nonzero(a > 3)
            x0, y0, x1, y1 = box4(xs, ys, im.size)
            write_dds(TEX + "%s_%s.dds" % (name, layer), im.crop((x0, y0, x1, y1)))
            sprites.append(("GFX_mdr_heli_%s_%s" % (name, layer), TEX + "%s_%s" % (name, layer)))
            placed[name][layer] = (int(x0), int(y0))
            images[name][layer] = im
    gfx = ["spriteTypes = {"]
    for n, t in sprites:
        gfx += ["\tspriteType = {", '\t\tname = "%s"' % n, '\t\ttextureFile = "%s.dds"' % t, "\t}"]
    open(GFX_FILE, "w", encoding="utf-8", newline="\n").write("\n".join(gfx + ["}"]) + "\n")

    def win(name, body, t):
        return [t + "containerWindowType = {", t + '\tname = "%s"' % name, t + "\tposition = { x=0 y=0 }",
                t + "\tsize = { width=100% height=100% }"] + body + [t + "}"]

    written = 0
    for f in sorted(glob.glob(MD + GUI_DIR + "tank_chassis_heavy_tank*.gui")):
        base = os.path.basename(f)
        if not re.fullmatch(r"tank_chassis_heavy_tank(_amphibious)?(_[a-z]{3})?\.gui", base):
            continue
        text = open(f, encoding="utf-8").read()
        found = re.findall(r'name\s*=\s*"(equipment_designer_heavy_tank(?:_amphibious)?_chassis(?:_([a-z]{3}))?)"', text)
        sprites_used = set(re.findall(r'spriteType\s*=\s*"(GFX_TC_[^"]+)"', text))
        if not found or sprites_used != {HELI_SPRITE}:
            continue  # e.g. Japan's transport helicopter window shows a tank in MD: left as it is
        out = ["# Realpolitik: replaces Millennium Dawn's file of the same path. Each installed module drawn in amber",
               "# (generated by herramientas/make_designer_helicopters.py, see DISENO.md).", "", "guiTypes = {"]
        for wname, tag in found:
            draw = TAGS.get(tag, "generic")
            body = ["\t\ticonType = {", '\t\t\tname = "equipment_image_overlay"', '\t\t\tspriteType = "GFX_mdr_heli_bp_%s"' % draw,
                    "\t\t\tposition = { x=0 y=0 }", "\t\t}"]
            slots = []
            for slot, mods in SLOTS:
                inner = []
                for mod, layer in mods:
                    key = layer if layer in placed[draw] else "%s_%s" % (layer, slot)
                    if key in placed[draw]:
                        x, y = placed[draw][key]
                        inner += win(mod, ["\t\t\t\t\t\ticonType = {", '\t\t\t\t\t\t\tname = "mdr_part"',
                                           '\t\t\t\t\t\t\tspriteType = "GFX_mdr_heli_%s_%s"' % (draw, key),
                                           "\t\t\t\t\t\t\tposition = { x=%d y=%d }" % (x, y), "\t\t\t\t\t\t}"], "\t\t\t\t\t")
                slots += win(slot, inner, "\t\t\t\t")
            body += win("module_slots", slots, "\t\t\t")
            out += ["\tcontainerWindowType = {", '\t\tname = "%s"' % wname,
                    "\t\t# NOTE: to keep aligned with the window \"equipment_modules\" in tank_designer_view.gui",
                    "\t\tposition = { x=0 y=0 }", "\t\tsize = { width=508 height=248 }"] + body + ["\t}"]
        out.append("}")
        open(GUI_DIR + base, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")
        written += 1
    if preview:
        bg = Image.open(MD + ED + "tanks/generic_tank_blueprint_background.dds").convert("RGBA")
        sets = [["body", "engine", "armor", "cabin", "gun_heavy", "mast_radar", "sensor", "flares"]
                + ["%s_%s" % (k, m) for k, m in (("atgm_rack", "helicopter_wing_mount_1"), ("rockets", "helicopter_wing_mount_2"),
                                                  ("gunpod", "helicopter_body_mount_1"), ("aam", "helicopter_body_mount_2"))],
                ["engine_coax", "cabin_troops", "gun_light", "mast_cam", "antenna", "aps"]
                + ["%s_%s" % (k, m) for k, m in (("atgm", "helicopter_wing_mount_1"), ("atgm_heavy", "helicopter_wing_mount_2"),
                                                  ("doorgun", "helicopter_body_mount_1"), ("drone", "helicopter_body_mount_2"))]]
        sheet = Image.new("RGB", (W * 2, H * len(DRAW)))
        for r, name in enumerate(DRAW):
            for c, s in enumerate(sets):
                b = bg.copy()
                b.alpha_composite(Image.open(MD + DRAW[name]["tex"] + ".dds").convert("RGBA"))
                for layer in s:
                    if layer in images[name]:
                        b.alpha_composite(images[name][layer])
                sheet.paste(b.convert("RGB"), (c * W, r * H))
        sheet.save("herramientas/vista_diseno/helicopteros_todos.png")
    print("files:", written, "sprites:", len(sprites))


if __name__ == "__main__":
    main("preview" in sys.argv)
