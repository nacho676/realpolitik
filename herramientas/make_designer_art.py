# Equipment designer art (DISEÑO.md, stages 2 to 4): MD's blueprints and colours, with each installed module drawn in
# amber in its place. Main battle tanks (medium_tank_chassis) and light tanks (medium_tank_destroyer_chassis), with each
# country's own drawing (MD ships them but its windows point most countries to the generic one).
# Writes gfx/interface/equipmentdesigner/mdr/, interface/mdr_designer.gfx, full replacements of MD's window files and
# interface/equipmentdesigner/tanks/mdr_tank_chassis_shared.gui (countries that share a drawing, per MD's own list).
# Run from the mod folder after each Millennium Dawn update:
# uv run --with pillow --with numpy python herramientas/make_designer_art.py [preview]
import glob
import os
import re
import shutil
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

MD = "../Millennium-Dawn-2.0.0/"
TEX = "gfx/interface/equipmentdesigner/mdr/"
GFX_FILE = "interface/mdr_designer.gfx"
GUI_DIR = "interface/equipmentdesigner/tanks/"
SHARED_FILE = GUI_DIR + "mdr_tank_chassis_shared.gui"
TANKS = "gfx/interface/equipmentdesigner/tanks/"
W, H = 508, 248
SS = 4  # supersampling for drawn parts
LIT = np.array([255, 186, 58.0])  # installed module: amber stands out on MD's blue and white

# drawing: (blueprint, gun, turret, suspension), MD textures under TANKS without ".dds"
DRAWINGS = {
    "mbt_generic": ["generic/generic_heavy_tank_%s_alt" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_usa": ["Countries/America/USA_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_bra": ["Countries/Brazil/BRA_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_chi": ["Countries/China/chi_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_eng": ["Countries/England/eng_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_fra": ["Countries/France/FRA_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_ger": ["Countries/Germany/GER_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_isr": ["Countries/Israel/isr_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_ita": ["Countries/Italy/ita_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "mbt_pol": ["Countries/Poland/pol_heavy_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "lt_generic": ["generic/generic_light_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "lt_bra": ["Countries/Brazil/BRA_light_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "lt_fra": ["Countries/France/FRA_light_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "lt_ita": ["Countries/Italy/ita_light_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
    "lt_sov": ["Countries/Russia/SOV_light_tank_%s" % p for p in ("blueprint", "gun", "turret", "suspension")],
}
DRAWINGS = {k: [TANKS + p for p in v] for k, v in DRAWINGS.items()}
ED = "gfx/interface/equipmentdesigner/"
PARTS = ("blueprint", "gun", "turret", "suspension")
DRAWINGS.update({
    "spg_generic": [ED + "spart/generic/generic_spg_%s_alt" % p for p in PARTS],
    "spg_ger": [ED + "spart/Countries/Germany/ger_spg_%s" % p for p in PARTS],
    "spg_sov": [ED + "spart/Countries/Russia/sov_spg_%s" % p for p in PARTS],
    "spaa_generic": [ED + "spart/generic/generic_spaa_%s" % p for p in PARTS],
    "spaa_ita": [ED + "spart/Countries/Italy/ita_spaa_%s" % p for p in PARTS],
    "ifv_generic": [ED + "afv/generic/generic_afv_%s_alt" % p for p in PARTS],
    "apc_generic": [ED + "afv/generic/generic_apc_%s_alt" % p for p in PARTS],
    "apc_ita": [ED + "afv/Countries/Italy/ita_apc_%s" % p for p in PARTS],
})
ENGINE_DRAWING = {"mbt": TANKS + "generic_tank_engine", "lt": ED + "spart/generic/generic_spg_engine",
                  "spg": ED + "spart/generic/generic_spg_engine", "spaa": ED + "spart/generic/generic_spg_engine",
                  "ifv": ED + "afv/generic/generic_afv_engine", "apc": ED + "afv/generic/generic_apc_engine"}
ENGINE_HIGHLIGHT = {"mbt": "GFX_TM_heavy_tank_chassis_engine_type_slot", "lt": "GFX_TM_light_tank_engine",
                    "spg": "GFX_TM_spart_engine", "spaa": "GFX_TM_spaa_engine", "ifv": "GFX_TM_afv_hull_engine",
                    "apc": "GFX_TM_afv_hull_engine"}
ARMOR_DRAWING = TANKS + "generic_tank_armor"

# Window tag -> drawing. Ghana's own drawing is a walker (an MD joke): it keeps the generic tank.
MBT_TAGS = {"usa": "mbt_usa", "egy": "mbt_usa", "kuw": "mbt_usa", "sau": "mbt_usa", "mor": "mbt_usa", "ast": "mbt_usa",
            "jap": "mbt_usa", "bra": "mbt_bra", "chi": "mbt_chi", "eng": "mbt_eng", "fra": "mbt_fra", "ger": "mbt_ger",
            "isr": "mbt_isr", "ita": "mbt_ita", "pol": "mbt_pol"}
LT_TAGS = {"bra": "lt_bra", "fra": "lt_fra", "ita": "lt_ita", "sov": "lt_sov"}
# Countries without a window of their own, from the list at the top of MD's tank_chassis_medium_tank_*.gui
GER_GROUP = ["spr", "por", "den", "hol", "swi", "cze", "slo", "aus", "fin", "swe", "nry", "tur", "gre", "can", "hun",
             "bel", "chl", "kor", "tai"]
SHARED_MBT = dict([("uae", "mbt_fra"), ("saf", "mbt_eng")] + [(t, "mbt_ger") for t in GER_GROUP])
SHARED_LT = {"uae": "lt_fra", "sov": "lt_sov"}
SPG_TAGS = {"ger": "spg_ger", "sov": "spg_sov"}
SHARED_SPG = dict((t, "spg_ger") for t in GER_GROUP)
# file prefix, chassis, tag -> drawing, default drawing, extra windows
TYPES = [("tank_chassis_medium_tank", "medium_tank_chassis", MBT_TAGS, "mbt_generic", SHARED_MBT),
         ("tank_chassis_medium_tank_destroyer", "medium_tank_destroyer_chassis", LT_TAGS, "lt_generic", SHARED_LT),
         ("tank_chassis_medium_tank_artillery", "medium_tank_artillery_chassis", SPG_TAGS, "spg_generic", SHARED_SPG),
         ("tank_chassis_medium_tank_rocket", "medium_tank_rocket_chassis", SPG_TAGS, "spg_generic", SHARED_SPG),
         ("tank_chassis_medium_tank_aa", "medium_tank_aa_chassis", {"ita": "spaa_ita"}, "spaa_generic", {}),
         ("tank_chassis_medium_tank_flame", "medium_tank_flame_chassis", {}, "ifv_generic", {}),
         ("tank_chassis_medium_tank_amphibious", "medium_tank_amphibious_chassis", {"ita": "apc_ita"}, "apc_generic", {})]

# Slot -> [(window name: module, its GFX, its category or the slot itself, layer)]
CANNON = ["tank_large_main_armament", "tank_small_medium_main_armament", "tank_small_main_armament", "assault_gun", "art_gun_module"]
AUTOCANNON = ["autocannon_vehicle", "spaa_autocannon_systems", "light_afv_apc_main_armament"]
SPECIAL = ([("tank_additional_armor_era", "era"), ("tank_additional_armor_spaced", "spaced"), ("tank_aa_module", "aa"),
            ("tank_support_drone_module", "drone")]
           + [(m, "smoke") for m in ("smoke_launchers", "smoke_launchers_2", "smoke_launchers_3")]
           + [("hardkill_system_gen%d" % i, "aps") for i in (1, 2, 3, 4)]
           + [("defensive_jammers", "jammer"), ("tank_laser_point_defense", "laser"), ("tank_smoke_module", "smoke"),
              ("afv_gun_ports", "gunports"), ("afv_mine_protection", "mineprot"), ("afv_reverse_doors", "reardoor"),
              ("front_mounted_engine", "engine_front"), ("tank_dozer_blades", "dozer")])
MISSILE_PACKS = {"two_missile_pack": 2, "four_missile_pack": 4, "eight_missile_pack": 8, "sixteen_missile_pack": 16,
                 "thirty_two_missile_pack": 32}
SLOTS = [
    ("main_armament_slot", [(c, "gun") for c in CANNON] + [(c, "autocannon") for c in AUTOCANNON]
     + [("missile_launcher_systems", "atgm"), ("art_rocket_module", "rocketpod"), ("main_armament_slot", "gun")], "gun"),
    ("secondary_armament_slot", [], None),
    ("turret_type_slot", [("turret_type_slot", "turret")], "turret"),
    ("reload_type_slot", [("manual_loading", "load_manual"), ("automatic_loading", "load_auto"),
                          ("revolver_magazine", "load_revolver")]
     + [(m, "missiles_%d" % n) for m, n in MISSILE_PACKS.items()], None),
] + [("special_type_slot_%d" % i, SPECIAL, None) for i in (1, 2, 3)] + [("battlestation_type_slot", [], None)] + [
    ("special_type_slot_%d" % i, SPECIAL, None) for i in (4, 5, 6)] + [
    ("ammunition_load_slot", [], None),
    ("engine_type_slot", [("engine_type_slot", "engine")], "engine"),
    ("suspension_type_slot", [("suspension_type_slot", "susp")], "susp"),
    ("armor_type_slot", [("tank_armor_type", "armor_steel"), ("light_afv_armor_type", "armor_steel"),
                         ("tank_heavy_armor_type", "armor_comp"), ("light_afv_heavy_armor_type", "armor_comp"),
                         ("tank_stealth_armor", "armor_stealth"), ("armor_type_slot", "armor_steel")], "armor"),
]


def write_dds(path, im):
    # DXT5, like most of MD's textures: the full-height strips below would weigh hundreds of MB uncompressed
    im.convert("RGBA").save(path, pixel_format="DXT5")


def box4(xs, ys, size):
    # Crop only the sides and keep the full height at y=0, like MD's one working part image (the corvette's CIWS):
    # in the game, a part placed with a y position showed 1 or 2 pixels above the blueprint. Sides in multiples of 4
    # for DXT5.
    w, h = size
    x0 = max(0, (int(xs.min()) - 1) // 4 * 4)
    x1 = min(w, -(-(int(xs.max()) + 2) // 4) * 4)
    return x0, 0, x1, h


def load(path):
    return np.array(Image.open(MD + path + ".dds").convert("RGBA")).astype(float)


def fill_mask(path):
    # MD's highlight images: purple fill over the part, grey leader line
    a = load(path)
    m = (a[..., 3] > 10) & (a[..., 2] - a[..., 0] > 20)
    return np.array(Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(5))) / 255.0


def drawing(path, dense_only=False):
    # MD's exploded drawings without their grey leader lines
    a = load(path)
    grey = (a[..., 2] - a[..., 0] <= 20) & (np.abs(a[..., 0] - a[..., 1]) < 25) & (a[..., 0] > 100) & (a[..., 0] < 200)
    al = a[..., 3] / 255.0
    al[grey] = 0
    if not dense_only:
        return al
    # engines: drop thin leader lines of other colours, keep only the dense drawing
    dense = np.array(Image.fromarray(((al > 0.3) * 255).astype("uint8")).filter(ImageFilter.BoxBlur(6))) / 255.0 > 0.3
    keep = np.array(Image.fromarray((dense * 255).astype("uint8")).filter(ImageFilter.MaxFilter(11))) / 255.0
    return al * keep


def box(y0, y1, x0, x1):
    m = np.zeros((H, W))
    m[max(0, int(y0)):max(0, int(y1)), max(0, int(x0)):max(0, int(x1))] = 1
    return m


def bbox(m, thr=0.3):
    ys, xs = np.nonzero(m > thr)
    return xs.min(), ys.min(), xs.max(), ys.max()


class Pen:
    # Thin blueprint lines, drawn supersampled
    def __init__(self):
        self.im = Image.new("L", (W * SS, H * SS), 0)
        self.d = ImageDraw.Draw(self.im)
        self.w = int(1.3 * SS)

    def p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def line(self, *pts):
        self.d.line(self.p(pts), fill=255, width=self.w, joint="curve")

    def rect(self, x0, y0, x1, y1):
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], outline=255, width=self.w)

    def poly(self, *pts):
        self.d.polygon(self.p(pts), outline=255, width=self.w)

    def circle(self, cx, cy, rx, ry=None):
        ry = rx if ry is None else ry
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], outline=255, width=self.w)

    def arc(self, cx, cy, r, a0, a1):
        self.d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], a0, a1, fill=255, width=self.w)

    def done(self):
        return np.array(self.im.resize((W, H), Image.LANCZOS)) / 255.0


class Tank:
    def __init__(self, name):
        self.name = name
        self.kind = name.split("_")[0]
        bp, gun, turret, susp = DRAWINGS[name]
        self.lines = load(bp)[..., 3] / 255.0
        self.gun = fill_mask(gun)
        self.turret = fill_mask(turret)
        self.susp = fill_mask(susp)
        L = self.lines
        self.tx0, self.ty0, self.tx1, self.ty1 = bbox(self.turret)
        self.sx0, self.sy0, self.sx1, self.sy1 = bbox(self.susp)
        self.gx0, self.gy0, self.gx1, self.gy1 = bbox(self.gun)
        tw = self.tx1 - self.tx0
        # turret roof: highest line inside the turret, over its middle half
        cols = range(int(self.tx0 + tw * 0.25), int(self.tx1 - tw * 0.25))
        tops = [np.argmax((L[:, c] * self.turret[:, c]) > 0.4) for c in cols if ((L[:, c] * self.turret[:, c]) > 0.4).any()]
        self.roof = float(np.median(tops)) if tops else self.ty0 + (self.ty1 - self.ty0) * 0.3
        # turret body: widest run of the turret mask a little below the roof (the roof machine gun sticks out)
        row = self.turret[int(self.roof + (self.ty1 - self.roof) * 0.45)] > 0.5
        if row.any():
            xs = np.nonzero(row)[0]
            self.tx0, self.tx1 = xs.min(), xs.max()
        self.yh0 = self.ty1 - 4
        self.yh1 = max(self.sy0 + 6, self.yh0 + 18)
        # hull length from its lower half: the barrel's break marks reach the upper half
        band = (L * (1 - self.gun))[int((self.yh0 + self.yh1) / 2):int(self.yh1)] > 0.3
        xs = np.nonzero(band.any(axis=0))[0]
        self.x0, self.x1 = xs.min(), xs.max()
        gm = (L * self.gun) > 0.3
        self.gy = float(np.median(np.nonzero(gm)[0])) if gm.any() else (self.gy0 + self.gy1) / 2
        self.gstart = max(self.gx0, self.tx1 - 8)

    def hull(self):
        return box(self.yh0 - 2, self.yh1 + 2, self.x0, self.x1 + 1) * (1 - self.turret) * (1 - self.susp) * (1 - self.gun)

    def layers(self):
        L, hw, hh = self.lines, self.x1 - self.x0, self.yh1 - self.yh0
        tw, th = self.tx1 - self.tx0, self.ty1 - self.roof
        rear = 0.24 * hw
        hull = self.hull()
        bay = box(self.yh0 - 2, self.yh1 + 2, self.x0, self.x0 + rear)
        front = box(self.yh0 - 2, self.yh1 + 2, self.x1 - rear, self.x1 + 1)
        cross = drawing(ARMOR_DRAWING)
        out = {
            "gun": L * self.gun,
            "turret": L * self.turret,
            "susp": L * self.susp,
            "engine": np.maximum(L * hull * bay, drawing(ENGINE_DRAWING[self.kind], True)),
            "engine_front": L * hull * front,
            "armor_steel": np.maximum(L * hull * (1 - bay), cross),
        }

        def pen(f):
            p = Pen()
            f(p)
            return p.done()

        # cannon replaced by a thin autocannon: barrel, muzzle brake, mantlet
        def autocannon(p):
            x0, y, ln = self.gstart, self.gy, (self.gx1 - self.gstart) * 0.43
            p.rect(x0 - 4, y - 4, x0 + 6, y + 4)
            p.line((x0 + 6, y - 1.3), (x0 + ln, y - 1.3))
            p.line((x0 + 6, y + 1.3), (x0 + ln, y + 1.3))
            p.rect(x0 + ln, y - 2.4, x0 + ln + 7, y + 2.4)
        out["autocannon"] = pen(autocannon)

        def atgm(p):
            x, y = self.tx0 + tw * 0.42, self.roof - 3
            p.rect(x, y - 8, x + tw * 0.34, y - 2)
            p.line((x + 3, y - 5), (x + tw * 0.34 - 3, y - 5))
            p.line((x + tw * 0.17, y - 2), (x + tw * 0.17, y + 2))
        out["atgm"] = pen(atgm)

        def rocketpod(p):
            x, y, w, h = self.tx0 + tw * 0.15, self.roof - 3, tw * 0.62, 14
            p.rect(x, y - h, x + w, y)
            for i in range(1, 4):
                p.line((x + 2, y - h + i * h / 4), (x + w - 2, y - h + i * h / 4))
        out["rocketpod"] = pen(rocketpod)

        # composite: hull, glacis plate and turret front blocks
        def comp(p):
            fx = self.x1 - hw * 0.13
            p.poly((fx, self.yh0 + 1), (self.x1 - 2, self.yh0 + hh * 0.45), (self.x1 - 6, self.yh0 + hh * 0.58), (fx - 4, self.yh0 + 3))
            bx = self.tx1 - tw * 0.26
            for i in range(2):
                y0 = self.roof + 2 + i * th * 0.4
                p.rect(bx, y0, self.tx1 - 3, y0 + th * 0.34)
        out["armor_comp"] = np.maximum(out["armor_steel"], pen(comp))

        # stealth: angled facets over hull side and turret
        def stealth(p):
            y0, y1 = self.yh0 + 2, self.yh1 - 3
            p.line((self.x0 + hw * 0.08, y1), (self.x0 + hw * 0.18, y0), (self.x1 - hw * 0.2, y0), (self.x1 - hw * 0.06, y1))
            p.line((self.tx0 + tw * 0.1, self.ty1 - 2), (self.tx0 + tw * 0.22, self.roof + 2), (self.tx1 - tw * 0.18, self.roof + 2), (self.tx1 - 2, self.ty1 - 3))
        out["armor_stealth"] = np.maximum(out["armor_steel"], pen(stealth))

        def era(p):
            y0, y1 = self.yh0 + 1, self.yh0 + max(9, hh * 0.42)
            n = int(hw * 0.56 / 13)
            x = self.x0 + hw * 0.34
            for i in range(n):
                p.rect(x + i * 13, y0, x + i * 13 + 11, y1)
            for i in range(2):
                y = self.roof + 3 + i * th * 0.36
                for j in range(3):
                    xx = self.tx1 - tw * 0.3 + j * tw * 0.09
                    p.rect(xx, y, xx + tw * 0.075, y + th * 0.3)
        out["era"] = L * box(121, 155, 163, 378) if self.name == "mbt_generic" else pen(era)

        def spaced(p):
            y0, y1 = self.sy0 - 2, self.sy0 + (self.sy1 - self.sy0) * 0.3
            x, end = self.x0 + hw * 0.06, self.x1 - hw * 0.07
            while x + 20 < end:
                p.rect(x, y0, x + 24, y1)
                p.line((x + 3, y0 + 2.5), (x + 21, y0 + 2.5))
                x += 27
        out["spaced"] = pen(spaced)

        def smoke(p):
            x, y = self.tx1 - tw * 0.3, self.roof + 3
            for i in range(4):
                xx = x + i * 4.5
                p.line((xx, y), (xx + 4, y - 6))
                p.circle(xx + 4.5, y - 6.8, 1.6)
        out["smoke"] = pen(smoke)

        def aps(p):
            p.rect(self.tx1 - 9, self.roof + 1, self.tx1 - 3, self.roof + 9)
            p.rect(self.tx0 + 4, self.roof + 1, self.tx0 + 10, self.roof + 9)
            x = self.tx0 + tw * 0.3
            p.rect(x, self.roof - 7, x + 16, self.roof - 1)
            p.line((x + 3, self.roof - 7), (x + 7, self.roof - 12))
            p.line((x + 9, self.roof - 7), (x + 13, self.roof - 12))
        out["aps"] = pen(aps)

        def jammer(p):
            x = self.tx0 + tw * 0.22
            p.line((x, self.roof), (x, self.roof - 9))
            p.arc(x, self.roof - 9, 6, 180, 360)
            p.line((x - 6, self.roof - 9), (x + 6, self.roof - 9))
        out["jammer"] = pen(jammer)

        def laser(p):
            x = self.tx0 + tw * 0.4
            p.rect(x, self.roof - 8, x + 14, self.roof - 1)
            p.line((x + 14, self.roof - 5), (x + 26, self.roof - 5))
            p.circle(x + 7, self.roof - 4.5, 2)
        out["laser"] = pen(laser)

        def aa(p):
            x = self.tx0 + tw * 0.5
            p.line((x, self.roof), (x, self.roof - 8))
            p.rect(x - 9, self.roof - 13, x + 13, self.roof - 9)
            p.rect(x - 9, self.roof - 17.5, x + 13, self.roof - 13.5)
        out["aa"] = pen(aa)

        def drone(p):
            x, y = self.tx0 + tw * 0.3, self.roof - 26
            p.circle(x, y, 4, 2.4)
            p.line((x - 13, y - 2), (x + 13, y - 2))
            for dx in (-13, 13):
                p.circle(x + dx, y - 3.5, 6, 1.3)
        out["drone"] = pen(drone)

        def gunports(p):
            y = self.yh0 + hh * 0.5
            for i in range(4):
                p.circle(self.x0 + hw * (0.3 + i * 0.13), y, 2.2)
        out["gunports"] = pen(gunports)

        def mineprot(p):
            p.line((self.x0 + hw * 0.1, self.yh1 - 1), (self.x0 + hw * 0.5, self.yh1 + 3), (self.x1 - hw * 0.12, self.yh1 - 1))
        out["mineprot"] = pen(mineprot)

        def reardoor(p):
            p.rect(self.x0 + 2, self.yh0 + hh * 0.22, self.x0 + 2 + hw * 0.07, self.yh1 - hh * 0.18)
            p.line((self.x0 + 4, self.yh0 + hh * 0.5), (self.x0 + 4 + hw * 0.03, self.yh0 + hh * 0.5))
        out["reardoor"] = pen(reardoor)

        def dozer(p):
            x, y0, y1 = self.x1 + 3, self.sy0 - 2, self.sy1 - 6
            p.line((self.x1 - 8, self.yh1), (x + 4, y0 + 4))
            p.line((x + 2, y0), (x + 12, (y0 + y1) / 2), (x + 3, y1))
            p.line((x + 6, y0), (x + 15, (y0 + y1) / 2), (x + 7, y1))
        out["dozer"] = pen(dozer)

        def load_manual(p):
            x, y = self.tx0 + tw * 0.05, self.roof + th * 0.3
            for r in range(2):
                for c in range(4):
                    p.circle(x + 4 + c * 7, y + r * 7, 2.6)
        out["load_manual"] = pen(load_manual)

        def load_auto(p):
            cx, cy = (self.tx0 + self.tx1) / 2, self.yh0 + hh * 0.62
            rx = tw * 0.2
            ry = rx * 0.19
            p.circle(cx, cy, rx, ry)
            for i in range(-5, 6):
                x = cx + i * rx / 6
                p.line((x, cy - ry * 0.75), (x, cy + ry * 0.75))
            p.circle(cx, cy, 3.5)
        out["load_auto"] = pen(load_auto)

        def load_revolver(p):
            r = max(5.5, min(10, th * 0.32))
            cx, cy = self.tx0 + r + 4, self.roof + th * 0.5
            p.circle(cx, cy, r)
            for k in range(6):
                a = k * np.pi / 3
                p.circle(cx + np.cos(a) * r * 0.6, cy + np.sin(a) * r * 0.6, r * 0.22)
        out["load_revolver"] = pen(load_revolver)

        for n in MISSILE_PACKS.values():
            rows, cols = {2: (1, 2), 4: (2, 2), 8: (2, 4), 16: (4, 4), 32: (4, 8)}[n]

            def pack(p, rows=rows, cols=cols):
                x, y1 = self.tx0 + tw * 0.2, self.roof - 2
                y0 = y1 - rows * 5 - 2
                p.rect(x, y0, x + cols * 5 + 2, y1)
                for r in range(rows):
                    for c in range(cols):
                        p.circle(x + 3.5 + c * 5, y0 + 3.5 + r * 5, 1.5)
            out["missiles_%d" % n] = pen(pack)
        return out


def lit(strength):
    # Amber lines plus a soft glow, on transparency
    glow = np.array(Image.fromarray((np.clip(strength, 0, 1) * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(3))) / 255.0
    alpha = np.clip(np.maximum(strength, glow * 0.57), 0, 1)
    rgb = np.broadcast_to(LIT, (H, W, 3))
    return Image.fromarray(np.dstack([rgb, alpha * 255]).astype("uint8"), "RGBA")


def build_textures():
    # returns {drawing: {layer: (x, y)}}; each layer cropped to what it covers
    if os.path.isdir(TEX):
        shutil.rmtree(TEX)
    placed, images = {}, {}
    for name in DRAWINGS:
        t = Tank(name)
        os.makedirs(TEX + name, exist_ok=True)
        placed[name], images[name] = {}, {}
        for layer, strength in t.layers().items():
            im = lit(strength)
            a = np.array(im)[..., 3]
            if a.max() < 8:
                continue
            ys, xs = np.nonzero(a > 3)
            x0, y0, x1, y1 = box4(xs, ys, im.size)
            write_dds(TEX + "%s/%s.dds" % (name, layer), im.crop((x0, y0, x1, y1)))
            placed[name][layer] = (int(x0), int(y0))
            images[name][layer] = im
    return placed, images


def write_gfx(placed):
    out = ["spriteTypes = {"]

    def sprite(name, tex):
        out.extend(["\tspriteType = {", '\t\tname = "%s"' % name, '\t\ttextureFile = "%s.dds"' % tex, "\t}"])
    for name, (bp, gun, turret, susp) in DRAWINGS.items():
        sprite("GFX_mdr_bp_%s" % name, bp)
        for part, tex in (("gun", gun), ("turret", turret), ("susp", susp)):
            sprite("GFX_mdr_hl_%s_%s" % (name, part), tex)
        for layer in placed[name]:
            sprite("GFX_mdr_%s_%s" % (name, layer), TEX + "%s/%s" % (name, layer))
    out.append("}")
    open(GFX_FILE, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


def win(name, body):
    out = ["containerWindowType = {", '\tname = "%s"' % name, "\tposition = { x=0 y=0 }", "\tsize = { width=100% height=100% }"]
    out += ["\t" + line for line in body]
    return out + ["}"]


def icon(name, sprite, x=0, y=0):
    return ["iconType = {", '\tname = "%s"' % name, '\tspriteType = "%s"' % sprite, "\tposition = { x=%d y=%d }" % (x, y), "}"]


def window(win_name, draw, placed):
    kind = draw.split("_")[0]
    highlights = {
        "gun": [("blueprint", "GFX_mdr_hl_%s_gun" % draw)],
        "turret": [("blueprint", "GFX_mdr_hl_%s_turret" % draw)],
        "susp": [("blueprint", "GFX_mdr_hl_%s_susp" % draw)],
        "engine": [("blueprint", ENGINE_HIGHLIGHT[kind])],
        "armor": [("blueprint_generic", "GFX_TM_tank_armor"), ("blueprint", "GFX_TM_heavy_tank_chassis_armor_type_slot")],
    }
    slots = []
    for slot, modules, hl in SLOTS:
        body = []
        for mod, layer in modules:
            if layer in placed[draw]:
                x, y = placed[draw][layer]
                body += win(mod, icon("mdr_part", "GFX_mdr_%s_%s" % (draw, layer), x, y))
        if hl:
            inner = []
            for n, s in highlights[hl]:
                inner += icon(n, s)
            body += win(slot + "@highlight", inner)
        slots += win(slot, body)
    top = ["containerWindowType = {", '\tname = "%s"' % win_name,
           "\t# NOTE: to keep aligned with the window \"equipment_modules\" in tank_designer_view.gui",
           "\tposition = { x=0 y=0 }", "\tsize = { width=508 height=248 }"]
    top += ["\t" + line for line in icon("equipment_image_overlay", "GFX_mdr_bp_%s" % draw)]
    top += ["\t" + line for line in win("module_slots", slots)]
    return top + ["}"]


HEAD = ["# Generated by herramientas/make_designer_art.py (Realpolitik). Each country's own tank drawing, and each installed",
        "# module drawn in amber in its place (see DISENO.md in the mod folder).", ""]


def write_gui(path, windows, placed, replaces_md):
    out = list(HEAD)
    if replaces_md:
        out.insert(0, "# Replaces Millennium Dawn's file of the same path.")
    out.append("guiTypes = {")
    for name, draw in windows:
        out += ["\t" + line for line in window(name, draw, placed)]
    out.append("}")
    open(path, "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")


def write_guis(placed):
    os.makedirs(GUI_DIR, exist_ok=True)
    md_names = set()
    for f in glob.glob(MD + "interface/**/*.gui", recursive=True):
        md_names.update(re.findall(r'name\s*=\s*"(equipment_designer_[a-z_]+)"', open(f, encoding="utf-8", errors="ignore").read()))
    written = []
    shared = []
    for prefix, chassis, tags, default, extra in TYPES:
        shared += [("equipment_designer_%s_%s" % (chassis, t), d) for t, d in extra.items()]
        pattern = re.compile(r'name\s*=\s*"(equipment_designer_%s(?:_([a-z]{3}))?)"' % chassis)
        for f in sorted(glob.glob(MD + GUI_DIR + prefix + "*.gui")):
            base = os.path.basename(f)
            if not re.fullmatch(prefix + r"(_[a-z]{3})?\.gui", base):
                continue
            windows = [(n, tags.get(tag, default)) for n, tag in pattern.findall(open(f, encoding="utf-8").read())]
            if windows:
                write_gui(GUI_DIR + base, windows, placed, True)
                written.append(base)
    clash = [n for n, _ in shared if n in md_names]
    assert not clash, "MD already has: %s" % clash
    write_gui(SHARED_FILE, shared, placed, False)
    return written


def preview(images):
    # Every drawing with a typical set of modules, on MD's background
    bg = Image.open(MD + TANKS + "generic_tank_blueprint_background.dds").convert("RGBA")
    sets = [("gun", "turret", "susp", "engine", "armor_comp", "era", "smoke", "load_auto"),
            ("autocannon", "turret", "susp", "armor_stealth", "spaced", "aps", "drone", "load_manual", "dozer"),
            ("atgm", "turret", "susp", "armor_steel", "jammer", "aa", "load_revolver", "missiles_8", "reardoor", "gunports")]
    names = list(DRAWINGS)
    sheet = Image.new("RGB", (W * 3, H * len(names)), (0, 0, 0))
    for r, name in enumerate(names):
        for c, layers in enumerate(sets):
            im = bg.copy()
            im.alpha_composite(Image.open(MD + DRAWINGS[name][0] + ".dds").convert("RGBA"))
            for layer in layers:
                if layer in images[name]:
                    im.alpha_composite(images[name][layer])
            ImageDraw.Draw(im).text((6, 4), name, fill=(255, 255, 0))
            sheet.paste(im.convert("RGB"), (c * W, r * H))
    os.makedirs("herramientas/vista_diseno", exist_ok=True)
    sheet.save("herramientas/vista_diseno/tanques_todos.png")


if __name__ == "__main__":
    # MD's first-test file names of this generator, no longer used
    for old in glob.glob(TEX + "mdr_*.dds"):
        os.remove(old)
    placed, images = build_textures()
    write_gfx(placed)
    files = write_guis(placed)
    if "preview" in sys.argv:
        preview(images)
    print("drawings:", len(placed), "files:", len(files) + 1, "sprites:", sum(len(v) for v in placed.values()))
