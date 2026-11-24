"""Generates the ship sale window, its tables and texts.

Outputs:
  interface/mdr_ship_sale.gui, interface/mdr_ship_sale.gfx, gfx/interface/mdr/ship_sale/*.dds
  common/scripted_guis/mdr_ship_sale_gui.txt
  common/scripted_effects/mdr_ship_sale_gen.txt
  common/scripted_localisation/mdr_ship_sale_loc.txt
  localisation/{spanish,english}/mdr_ship_sale_l_*.yml
Hulls, slots and years come from Millennium Dawn (ship_data.py). Run from the mod folder after each MD update:
  python herramientas/make_ship_sale.py
The hand-written logic is common/scripted_effects/mdr_ship_sale.txt.
"""
import os
import re
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ship_data  # noqa: E402

MD = "../Millennium-Dawn-2.0.3/"
GAME = (__import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/") + "/")
GFX = "gfx/interface/mdr/ship_sale/"
SPACE = "gfx/interface/mdr/space/icons/"

# Sale types, in arrow order: unit type, reference price (billions), days to build one with few dockyards, topview,
# Spanish, English.
TYPES = [
    ("carrier", 4.7, 2517, "carrier", "Portaaviones", "Carrier"),
    ("helicopter_operator", 1.26, 1438, "helicopter_operator", "Portahelicópteros", "Helicopter Carrier"),
    ("battleship", 3.1, 2163, "battleship", "Acorazado", "Battleship"),
    ("battle_cruiser", 2.6, 1977, "battle_cruiser", "Crucero de batalla", "Battlecruiser"),
    ("cruiser", 1.47, 1621, "cruiser", "Crucero", "Cruiser"),
    ("stealth_destroyer", 1.6, 1443, "stealth_destroyer", "Destructor furtivo", "Stealth Destroyer"),
    ("destroyer", 1.14, 1262, "destroyer", "Destructor", "Destroyer"),
    ("screen_destroyer", 0.88, 1083, "destroyer", "Destructor de escolta", "Escort Destroyer"),
    ("stealth_frigate", 0.6, 1079, "destroyer", "Fragata furtiva", "Stealth Frigate"),
    ("frigate", 0.43, 903, "destroyer", "Fragata", "Frigate"),
    ("heavy_frigate", 0.62, 997, "destroyer", "Fragata pesada", "Heavy Frigate"),
    ("corvette", 0.17, 541, "destroyer", "Corbeta", "Corvette"),
    ("stealth_corvette", 0.24, 638, "destroyer", "Corbeta furtiva", "Stealth Corvette"),
    ("patrol_boat", 0.06, 213, "destroyer", "Lancha patrullera", "Patrol Boat"),
    ("missile_submarine", 2.3, 1797, "submarine", "Submarino lanzamisiles", "Missile Submarine"),
    ("attack_submarine", 0.74, 1259, "submarine", "Submarino de ataque", "Attack Submarine"),
    ("repair_ship", 0.21, 719, "destroyer", "Buque de reparación", "Repair Ship"),
    ("support_ship", 0.21, 723, "destroyer", "Buque de apoyo", "Support Ship"),
]
T = len(TYPES)
TYPE_OF_ARCH = {"carrier": 1, "helicopter_operator": 2, "battleship_hull_0": 3, "battle_cruiser": 4, "cruiser": 5,
                "stealth_destroyer": 6, "destroyer": 7, "stealth_frigate": 9, "frigate": 10, "corvette": 12,
                "stealth_corvette": 13, "patrol_boat": 14, "missile_submarine": 15, "attack_submarine": 16}
TOPVIEWS = ["carrier", "helicopter_operator", "battleship", "battle_cruiser", "cruiser", "stealth_destroyer", "destroyer", "submarine"]
SLOT_NAMES = {
    "front_1_custom_slot": ("Proa 1", "Front 1"), "front_2_custom_slot": ("Proa 2", "Front 2"),
    "mid_1_custom_slot": ("Centro 1", "Mid 1"), "mid_2_custom_slot": ("Centro 2", "Mid 2"), "mid_3_custom_slot": ("Centro 3", "Mid 3"),
    "rear_1_custom_slot": ("Popa 1", "Rear 1"), "rear_2_custom_slot": ("Popa 2", "Rear 2"),
    "fixed_ship_battery_slot": ("Batería", "Battery"), "fixed_ship_battery_slot_2": ("Batería 2", "Battery 2"),
    "fixed_ship_battery_slot_3": ("Batería 3", "Battery 3"), "fixed_ship_battery_slot_4": ("Batería 4", "Battery 4"),
    "fixed_ship_auxillary_slot": ("Auxiliar", "Auxiliary"), "fixed_ship_auxillary_slot_1": ("Auxiliar 1", "Auxiliary 1"),
    "fixed_ship_auxillary_slot_2": ("Auxiliar 2", "Auxiliary 2"), "fixed_ship_auxillary_slot_3": ("Auxiliar 3", "Auxiliary 3"),
    "fixed_ship_radar_slot": ("Radar/Sonar", "Radar/Sonar"), "fixed_ship_fire_control_system_slot": ("Control de tiro", "Fire Control"),
    "fixed_ship_engine_slot": ("Motor", "Engine"), "fixed_ship_flight_deck": ("Cubierta", "Flight Deck"),
    "fixed_ship_missile_ammo_slot": ("Munición", "Ammunition"),
}
DESIGNS = 12          # export design names "Export 1" .. "Export 12", made by the player in MD's designer
ROWS = 7              # contract rows
TOP_MAX, BOTTOM_MAX = 7, 8

hulls, _modules, unlock = ship_data.load()
HULLS = sorted(hulls, key=lambda h: (TYPE_OF_ARCH.get(hulls[h]["archetype"], 99), hulls[h]["year"]))
HULLS = [h for h in HULLS if hulls[h]["archetype"] in TYPE_OF_ARCH and unlock.get(h)]
H = len(HULLS)


def layout(h):
    slots = [(s, r) for s, r, cs in hulls[h]["slots"] if cs]
    top = [x for x in slots if "custom" in x[0]][:TOP_MAX]
    bottom = [x for x in slots if "custom" not in x[0]][:BOTTOM_MAX]
    return tuple(top), tuple(bottom)


LAYOUTS = []
for h in HULLS:
    if layout(h) not in LAYOUTS:
        LAYOUTS.append(layout(h))

# Ready-made designs by role (ship_presets.py): designs 1..NR are these, NR+1.. are the player's "Export N".
import ship_presets  # noqa: E402
PRESETS, _ = ship_presets.build(hulls, _modules, unlock)
ROLES = ship_presets.ROLES
NR = len(ROLES)
ALL_DESIGNS = NR + DESIGNS
CODES = {"carrier": "CV", "helicopter_operator": "LHD", "battleship_hull_0": "BB", "battle_cruiser": "BC", "cruiser": "CG",
         "stealth_destroyer": "DDX", "destroyer": "DDG", "stealth_frigate": "FFX", "frigate": "FFG", "corvette": "FS",
         "stealth_corvette": "FSX", "patrol_boat": "PB", "missile_submarine": "SSG", "attack_submarine": "SSK"}


def variant_name(h, r):
    return f"Export {CODES[hulls[h]['archetype']]}-{hulls[h]['year']} {ROLES[r - 1][3]}"


# Module pictures: MD names them GFX_SMI_<module> (or its gfx key). Only modules with a picture are drawn.
_SPRITES = set()
for _f in __import__("glob").glob(MD + "interface/*.gfx"):
    _SPRITES.update(re.findall(r'name\s*=\s*"(GFX_SMI_\w+)"', open(_f, encoding="utf-8", errors="ignore").read()))


def sprite_of(m):
    for g in ("GFX_SMI_" + (_modules[m].get("gfx") or m), "GFX_SMI_" + m):
        if g in _SPRITES:
            return g
    return None


def slot_module(h, r, row, k):
    top, bottom = layout(h)
    lst = top if row == "t" else bottom
    if k > len(lst):
        return None
    m = PRESETS[(h, ROLES[r - 1][0])].get(lst[k - 1][0])
    return m if m and sprite_of(m) else None


MODS = sorted({slot_module(h, r, row, k) for h in HULLS for r in range(1, NR + 1) for row, n in (("t", TOP_MAX), ("b", BOTTOM_MAX)) for k in range(1, n + 1)} - {None})
MOD_IDX = {m: i for i, m in enumerate(MODS, 1)}


def spew(path, text, bom=False):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8-sig" if bom else "utf-8", newline="\n") as f:
        f.write(text)


# ---------------------------------------------------------------- textures
def save_dds(img, path):
    a = np.array(img.convert("RGBA"), dtype=np.uint8)
    h, w = a.shape[:2]
    head = struct.pack("<4s7I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1) + b"\0" * 44
    head += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000) + struct.pack("<5I", 0x1000, 0, 0, 0, 0)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(head + a[:, :, [2, 1, 0, 3]].tobytes())


def img(path):
    for root in ("", MD, GAME):
        if os.path.exists(root + path):
            return Image.open(root + path).convert("RGBA")
    raise FileNotFoundError(path)


def nine(src, w, h, b):
    out = Image.new("RGBA", (w, h))
    for sy0, sy1, dy0, dy1 in ((0, b, 0, b), (b, src.height - b, b, h - b), (src.height - b, src.height, h - b, h)):
        for sx0, sx1, dx0, dx1 in ((0, b, 0, b), (b, src.width - b, b, w - b), (src.width - b, src.width, w - b, w)):
            if dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(src.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0)), (dx0, dy0))
    return out


BUTTONS = {"w150": (150, 34), "w186": (186, 34), "w206": (206, 38), "w96": (96, 26)}


def textures():
    btn = img(SPACE + "btn_123x34.dds")
    for name, (w, h) in BUTTONS.items():
        save_dds(nine(btn, w, h, 10), f"{GFX}btn_{name}.dds")
    tab = img(SPACE + "sidetab.dds")
    half = tab.width // 2
    strip = Image.new("RGBA", (2 * 196, 32))
    strip.alpha_composite(nine(tab.crop((0, 0, half, 32)), 196, 32, 10), (0, 0))
    strip.alpha_composite(nine(tab.crop((half, 0, tab.width, 32)), 196, 32, 10), (196, 0))
    save_dds(strip, f"{GFX}sidetab.dds")
    # Blueprint: plain grid, no photo.
    w, h = 712, 300
    bp = Image.new("RGBA", (w, h), (22, 66, 128, 255))
    d = ImageDraw.Draw(bp)
    for x in range(0, w, 16):
        d.line([(x, 0), (x, h)], fill=(66, 120, 190, 255) if x % 80 == 0 else (40, 92, 160, 255))
    for y in range(0, h, 16):
        d.line([(0, y), (w, y)], fill=(66, 120, 190, 255) if y % 80 == 0 else (40, 92, 160, 255))
    d.rectangle([0, 0, w - 1, h - 1], outline=(96, 150, 220, 255), width=2)
    save_dds(bp, f"{GFX}blueprint.dds")
    # Slot box with the base game's empty slot picture.
    box = Image.new("RGBA", (86, 74), (14, 30, 54, 230))
    ImageDraw.Draw(box).rectangle([0, 0, 85, 73], outline=(96, 150, 220, 255), width=1)
    box.alpha_composite(img("gfx/interface/equipmentdesigner/equipment_module_bg.dds"), (5, 5))
    box.alpha_composite(img("gfx/interface/equipmentdesigner/module_slot_icon_empty.dds"), (5, 7))
    save_dds(box, f"{GFX}slot.dds")
    save_dds(Image.new("RGBA", (76, 42), (0, 0, 0, 0)), f"{GFX}mod_placeholder.dds")
    # Flag frame for the header: the game's overlay on a smaller white mask (the flag is drawn through the mask).
    fw, fh = 66, 42
    Image.new("RGB", (fw, fh), (255, 255, 255)).save(f"{GFX}flag_mask.tga")
    save_dds(img("gfx/interface/flag_overlay.dds").resize((fw, fh), Image.LANCZOS), f"{GFX}flag_overlay.dds")
    # Meters: 51 frames, 0 to 100%.
    for name, (w, h) in {"meter": (300, 14), "rowbar": (196, 8)}.items():
        s = Image.new("RGBA", (w * 51, h))
        for f in range(51):
            fr = Image.new("RGBA", (w, h), (30, 40, 60, 255) if name == "rowbar" else (60, 20, 16, 255))
            fill = round(w * f / 50)
            if fill:
                fr.paste((70, 140, 230, 255) if name == "rowbar" else (60, 170, 70, 255), (0, 0, fill, h))
            ImageDraw.Draw(fr).rectangle([0, 0, w - 1, h - 1], outline=(10, 14, 22, 255))
            s.alpha_composite(fr, (f * w, 0))
        save_dds(s, f"{GFX}{name}.dds")


def gfx():
    out = "# Generated by herramientas/make_ship_sale.py.\nspriteTypes = {\n"
    for name in BUTTONS:
        out += f'\tspriteType = {{\n\t\tname = "GFX_mdr_sale_btn_{name}"\n\t\ttextureFile = "{GFX}btn_{name}.dds"\n\t\tnoOfFrames = 1\n\t\teffectFile = "gfx/FX/buttonstate.lua"\n\t}}\n'
    out += f'\tmaskedShieldType = {{\n\t\tname = "GFX_mdr_sale_flag"\n\t\ttextureFile1 = "{GFX}flag_overlay.dds"\n\t\ttextureFile2 = "{GFX}flag_mask.tga"\n\t\teffectFile = "gfx/FX/maskedflag.lua"\n\t}}\n'
    out += f'\tspriteType = {{\n\t\tname = "GFX_mdr_sale_sidetab"\n\t\ttextureFile = "{GFX}sidetab.dds"\n\t\tnoOfFrames = 2\n\t}}\n'
    for name in ("blueprint", "slot", "mod_placeholder"):
        out += f'\tspriteType = {{\n\t\tname = "GFX_mdr_sale_{name}"\n\t\ttextureFile = "{GFX}{name}.dds"\n\t}}\n'
    for name in ("meter", "rowbar"):
        out += f'\tspriteType = {{\n\t\tname = "GFX_mdr_sale_{name}"\n\t\ttextureFile = "{GFX}{name}.dds"\n\t\tnoOfFrames = 51\n\t}}\n'
    return out + "}\n"


# ---------------------------------------------------------------- window
# One movable window. Each tab's elements are plain leaves with their own visibility trigger: the game
# does not hide nested containers by trigger (a page inside a container stayed drawn over the others).
W, Hh = 1200, 740
gui = []
TAG = {}      # element name -> modes where it shows
CUR = None    # modes of the elements being added; None for the frame
OX, OY = 0, 0  # offset of the page being drawn


def _put(name):
    if CUR is not None:
        TAG[name] = CUR


def text(name, x, y, w, key, font="hoi_16mbs", fmt="left", h=18, tt=None):
    _put(name)
    t = f' pdx_tooltip = "{tt}"' if tt else ""
    at = "" if tt else " alwaystransparent = yes"
    gui.append(f'\t\tinstantTextboxType = {{ name = "{name}" position = {{ x = {x + OX} y = {y + OY} }} font = "{font}" borderSize = {{ x = 0 y = 0 }} text = "{key}" maxWidth = {w} maxHeight = {h} format = {fmt}{t}{at} }}')


def button(name, x, y, sprite, label=None, tt=None, font="hoi_16mbs", sound="click_default", frame=None):
    _put(name)
    s = f'\t\tbuttonType = {{ name = "{name}" position = {{ x = {x + OX} y = {y + OY} }} quadTextureSprite = "{sprite}"'
    if frame:
        s += f" frame = {frame}"
    if label:
        s += f' buttonText = "{label}" buttonFont = "{font}"'
    if tt:
        s += f' pdx_tooltip = "{tt}"'
    gui.append(s + f" clicksound = {sound} }}")


def icon(name, x, y, sprite, frame=None, scale=None, tt=None):
    _put(name)
    s = f'\t\ticonType = {{ name = "{name}" spriteType = "{sprite}" position = {{ x = {x + OX} y = {y + OY} }}'
    if frame:
        s += f" frame = {frame}"
    if scale:
        s += f" scale = {scale}"
    s += f' pdx_tooltip = "{tt}"' if tt else " alwaystransparent = yes"
    gui.append(s + " }")


def panel(name, x, y, w, h):
    gui.append(f'\t\tcontainerWindowType = {{ name = "{name}" position = {{ x = {x} y = {y} }} size = {{ width = {w} height = {h} }} background = {{ name = "Background" quadTextureSprite = "GFX_mdr_space_panel" }} }}')


ARROW_L, ARROW_R = "GFX_mdr_space_arrow_left", "GFX_mdr_space_arrow_right"
MINUS, PLUS = "GFX_small_minus_button", "GFX_small_plus_button"
TABS = [("fleet", 0), ("batch", 2), ("refit", 3), ("build", 1), ("contracts", 4)]
FLEET, BATCH, BUILD, CONTRACTS, SELL = {0}, {2}, {1, 3}, {4}, {0, 1, 2, 3}
CX, CY, CW = 236, 76, 716


def page(modes, oy=CY):
    global CUR, OX, OY
    CUR, OX, OY = modes, CX, oy


def frame_only():
    global CUR, OX, OY
    CUR, OX, OY = None, 0, 0


def build_window():
    frame_only()
    gui.append('\tcontainerWindowType = {\n\t\tname = "mdr_ship_sale_window"\n\t\tposition = { x = -600 y = -370 }\n'
               f'\t\tsize = {{ width = {W} height = {Hh} }}\n\t\torientation = center\n\t\tmoveable = yes\n'
               '\t\tbackground = { name = "Background" quadTextureSprite = "GFX_mdr_space_window" }\n')
    icon("mdr_sale_backdrop", 2, 2, "GFX_mdr_space_backdrop", scale=1.33)
    # Header: flags centred in the 58 px band.
    icon("mdr_sale_header", 6, 6, "GFX_mdr_space_header", scale=1.32)
    button("mdr_sale_flag_seller", 22, 14, "GFX_mdr_sale_flag")
    text("mdr_sale_seller_name", 100, 14, 200, "MDR_SALE_SELLER", "hoi_24header", h=24)
    text("mdr_sale_seller_label", 100, 42, 200, "MDR_SALE_SELLER_LABEL")
    icon("mdr_sale_arrow", 304, 26, ARROW_R)
    button("mdr_sale_flag_buyer", 338, 14, "GFX_mdr_sale_flag")
    text("mdr_sale_buyer_name", 416, 14, 300, "MDR_SALE_BUYER", "hoi_24header", h=24)
    text("mdr_sale_buyer_label", 416, 42, 300, "MDR_SALE_BUYER_LABEL")
    for i, k in enumerate(("TREASURY", "DOCKS", "ORDERS", "DELIVERED")):
        x = 802 + i * 88
        text(f"mdr_sale_top_l{i}", x, 16, 84, f"MDR_SALE_TOP_{k}")
        text(f"mdr_sale_top_v{i}", x, 36, 84, f"MDR_SALE_TOP_{k}_V", "hoi_18mbs")
    button("mdr_sale_close", W - 34, 12, "GFX_closebutton", sound="click_close")

    # Left column.
    panel("mdr_sale_left", 14, 76, 212, 610)
    text("mdr_sale_left_title", 28, 88, 190, "MDR_SALE_SECTION_OPS")
    for i, (tab, _) in enumerate(TABS):
        y = 110 + i * 38
        button(f"mdr_sale_tab_{tab}_off", 22, y, "GFX_mdr_sale_sidetab", frame=1, tt=f"MDR_SALE_TAB_{tab.upper()}_TT", sound="click_checkbox")
        button(f"mdr_sale_tab_{tab}_on", 22, y, "GFX_mdr_sale_sidetab", frame=2, tt=f"MDR_SALE_TAB_{tab.upper()}_TT", sound="click_checkbox")
        text(f"mdr_sale_tab_{tab}_text", 36, y + 8, 176, f"MDR_SALE_TAB_{tab.upper()}")
    text("mdr_sale_state_title", 28, 318, 190, "MDR_SALE_SECTION_STATE")
    for i, k in enumerate(("REL", "NAVY", "PENDING", "SANCTION", "PORT")):
        text(f"mdr_sale_state_{i}_l", 28, 344 + i * 44, 190, f"MDR_SALE_STATE_{k}", "hoi_16mbs")
        text(f"mdr_sale_state_{i}_v", 28, 362 + i * 44, 190, f"MDR_SALE_STATE_{k}_V", "hoi_16mbs")

    # Right column: operations in progress.
    rx = 962
    panel("mdr_sale_right", rx, 76, 224, 610)
    text("mdr_sale_ops_title", rx + 14, 88, 196, "MDR_SALE_OPS_TITLE")
    icon("mdr_sale_ops_rule", rx + 14, 106, "GFX_mdr_space_rule")
    text("mdr_sale_ops_build", rx + 14, 116, 196, "MDR_SALE_OPS_BUILD")
    for r in (1, 2):
        y = 140 + (r - 1) * 56
        text(f"mdr_sale_op{r}_text", rx + 14, y, 196, f"MDR_SALE_OP{r}")
        icon(f"mdr_sale_op{r}_bar", rx + 14, y + 20, "GFX_mdr_sale_rowbar")
        text(f"mdr_sale_op{r}_days", rx + 14, y + 32, 196, f"MDR_SALE_OP{r}_DAYS")
    icon("mdr_sale_ops_rule2", rx + 14, 262, "GFX_mdr_space_rule")
    text("mdr_sale_ops_refit", rx + 14, 272, 196, "MDR_SALE_OPS_REFIT")
    text("mdr_sale_op3_text", rx + 14, 294, 196, "MDR_SALE_OP3")
    icon("mdr_sale_op3_bar", rx + 14, 314, "GFX_mdr_sale_rowbar")
    text("mdr_sale_op3_days", rx + 14, 326, 196, "MDR_SALE_OP3_DAYS")
    icon("mdr_sale_ops_rule3", rx + 14, 356, "GFX_mdr_space_rule")
    text("mdr_sale_ops_queue", rx + 14, 366, 196, "MDR_SALE_OPS_QUEUE")
    text("mdr_sale_ops_queue_v", rx + 14, 388, 196, "MDR_SALE_OPS_QUEUE_V", h=40)
    icon("mdr_sale_ops_rule4", rx + 14, 436, "GFX_mdr_space_rule")
    text("mdr_sale_ops_done", rx + 14, 446, 196, "MDR_SALE_OPS_DONE")
    for r in (1, 2, 3):
        text(f"mdr_sale_h{r}", rx + 14, 448 + r * 22, 196, f"MDR_SALE_H{r}")

    # The centre and bottom panels are shared by every tab; only their contents change.
    panel("mdr_sale_center", CX, CY, CW, 500)
    panel("mdr_sale_bottom", CX, 584, CW, 102)
    page_fleet()
    page_batch()
    page_build()
    page_contracts()
    summary()
    frame_only()
    button("mdr_sale_close_bottom", W - 16 - 150, Hh - 46, "GFX_mdr_sale_btn_w150", "MDR_SALE_CLOSE", sound="click_close")
    gui.append("\t}")


def page_fleet():
    page(FLEET)
    text("mdr_sale_fleet_title", 14, 12, 680, "MDR_SALE_FLEET_TITLE", "hoi_18mbs")
    icon("mdr_sale_fleet_rule", 14, 34, "GFX_mdr_space_rule")
    rows = [("type", "MDR_SALE_LBL_TYPE", "MDR_SALE_TYPE_VALUE", ARROW_L, ARROW_R, "prev", "next"),
            ("gen", "MDR_SALE_LBL_GEN", "MDR_SALE_GEN_VALUE", ARROW_L, ARROW_R, "prev", "next"),
            ("qty", "MDR_SALE_LBL_QTY", "MDR_SALE_QTY_VALUE", MINUS, PLUS, "minus", "plus")]
    for i, (k, lbl, val, s1, s2, n1, n2) in enumerate(rows):
        y = 50 + i * 40
        text(f"mdr_sale_lbl_{k}", 24, y + 6, 200, lbl, "hoi_18mbs")
        button(f"mdr_sale_{k}_{n1}", 250, y + 2, s1)
        text(f"mdr_sale_val_{k}", 280, y + 6, 300, val, "hoi_16mbs", "center")
        button(f"mdr_sale_{k}_{n2}", 590, y + 2, s2)
    icon("mdr_sale_fleet_bp", 2, 176, "GFX_mdr_sale_blueprint")
    for tv in TOPVIEWS:
        icon(f"mdr_sale_fleet_tv_{tv}", 104, 200, f"GFX_SD_tv_{tv}")
    text("mdr_sale_fleet_info", 14, 440, 690, "MDR_SALE_INFO_FLEET", h=60)


def page_batch():
    page(BATCH)
    text("mdr_sale_batch_title", 14, 12, 680, "MDR_SALE_BATCH_TITLE", "hoi_18mbs")
    icon("mdr_sale_batch_rule", 14, 34, "GFX_mdr_space_rule")
    for t in range(1, T + 1):
        col, row = (t - 1) // 9, (t - 1) % 9
        x, y = 14 + col * 352, 48 + row * 44
        text(f"mdr_sale_lot{t}_name", x, y + 6, 230, f"MDR_SALE_LOT{t}")
        button(f"mdr_sale_lot{t}_minus", x + 234, y + 2, MINUS)
        text(f"mdr_sale_lot{t}_qty", x + 262, y + 6, 40, f"MDR_SALE_LOT{t}_V", "hoi_18mbs", "center")
        button(f"mdr_sale_lot{t}_plus", x + 306, y + 2, PLUS)
    text("mdr_sale_batch_info", 14, 448, 690, "MDR_SALE_INFO_BATCH", h=50)


def page_build():
    page(BUILD)
    text("mdr_sale_build_title", 14, 10, 690, "MDR_SALE_BUILD_TITLE", "hoi_18mbs")
    icon("mdr_sale_build_rule", 14, 30, "GFX_mdr_space_rule")
    text("mdr_sale_build_legend", 14, 38, 690, "MDR_SALE_BUILD_LEGEND")
    text("mdr_sale_build_note", 14, 58, 690, "MDR_SALE_BUILD_NOTE", h=32)
    button("mdr_sale_hull_prev", 14, 94, ARROW_L)
    text("mdr_sale_hull_value", 40, 96, 300, "MDR_SALE_HULL_VALUE", "hoi_18mbs", "center")
    button("mdr_sale_hull_next", 344, 94, ARROW_R)
    text("mdr_sale_bqty_lbl", 400, 96, 110, "MDR_SALE_LBL_QTY", "hoi_18mbs")
    button("mdr_sale_bqty_minus", 512, 94, MINUS)
    text("mdr_sale_bqty_value", 540, 96, 40, "MDR_SALE_BQTY_VALUE", "hoi_18mbs", "center")
    button("mdr_sale_bqty_plus", 584, 94, PLUS)
    icon("mdr_sale_build_bp", 2, 124, "GFX_mdr_sale_blueprint")
    for tv in TOPVIEWS:
        icon(f"mdr_sale_build_tv_{tv}", 104, 150, f"GFX_SD_tv_{tv}")
    for row, n, y, step in (("t", TOP_MAX, 132, 92), ("b", BOTTOM_MAX, 344, 88)):
        for k in range(1, n + 1):
            x = 10 + (k - 1) * step
            icon(f"mdr_sale_slot_{row}{k}", x, y, "GFX_mdr_sale_slot")
            icon(f"mdr_sale_mod_{row}{k}", x + 5, y + 7, "GFX_mdr_sale_mod_placeholder", tt=f"MDR_SALE_MOD_{row.upper()}{k}_TT")
            text(f"mdr_sale_slot_{row}{k}_name", x, y + 54, 86, f"MDR_SALE_SLOT_{row.upper()}{k}", "hoi_16mbs", "center")
            text(f"mdr_sale_slot_{row}{k}_req", x + 74, y + 2, 12, "MDR_SALE_REQ")
    text("mdr_sale_design_lbl", 14, 440, 180, "MDR_SALE_LBL_DESIGN", "hoi_18mbs")
    button("mdr_sale_design_prev", 196, 438, ARROW_L)
    text("mdr_sale_design_value", 222, 440, 180, "MDR_SALE_DESIGN_VALUE", "hoi_18mbs", "center")
    button("mdr_sale_design_next", 406, 438, ARROW_R)
    text("mdr_sale_design_help", 440, 432, 266, "MDR_SALE_DESIGN_HELP", h=64)


def page_contracts():
    page(CONTRACTS)
    text("mdr_sale_contracts_title", 14, 12, 690, "MDR_SALE_CONTRACTS_TITLE", "hoi_18mbs")
    icon("mdr_sale_contracts_rule", 14, 34, "GFX_mdr_space_rule")
    for r in range(1, ROWS + 1):
        y = 46 + (r - 1) * 64
        button(f"mdr_sale_c{r}_flag", 14, y + 4, "GFX_flag_small")
        text(f"mdr_sale_c{r}_text", 60, y, 420, f"MDR_SALE_C{r}", "hoi_18mbs")
        text(f"mdr_sale_c{r}_sub", 60, y + 22, 420, f"MDR_SALE_C{r}_SUB")
        icon(f"mdr_sale_c{r}_bar", 60, y + 42, "GFX_mdr_sale_rowbar")
        button(f"mdr_sale_c{r}_cancel", 600, y + 10, "GFX_mdr_sale_btn_w96", "MDR_SALE_CANCEL_ROW", "MDR_SALE_CANCEL_ROW_TT")
    text("mdr_sale_contracts_empty", 14, 60, 690, "MDR_SALE_CONTRACTS_EMPTY")
    page(CONTRACTS, 584)
    text("mdr_sale_contracts_sum", 14, 14, 690, "MDR_SALE_CONTRACTS_SUM", "hoi_16mbs", h=80)


def summary():
    page(SELL, 584)
    text("mdr_sale_sum_cost", 14, 10, 470, "MDR_SALE_SUM_COST", "hoi_16mbs")
    text("mdr_sale_sum_price", 14, 32, 470, "MDR_SALE_SUM_PRICE", "hoi_16mbs")
    text("mdr_sale_sum_chance", 14, 56, 220, "MDR_SALE_CHANCE", "hoi_16mbs")
    icon("mdr_sale_sum_bar", 236, 58, "GFX_mdr_sale_meter")
    text("mdr_sale_sum_reason", 14, 78, 690, "MDR_SALE_REASON")
    text("mdr_sale_pct_lbl", 498, 10, 70, "MDR_SALE_LBL_PCT", "hoi_18mbs")
    button("mdr_sale_pct_minus", 566, 8, MINUS)
    text("mdr_sale_pct_value", 590, 10, 90, "MDR_SALE_PCT_VALUE", "hoi_16mbs", "center")
    button("mdr_sale_pct_plus", 682, 8, PLUS)
    button("mdr_sale_gift", 548, 46, "GFX_mdr_sale_btn_w150", "MDR_SALE_GIFT", "MDR_SALE_GIFT_TT")
    global OX, OY
    OX, OY = 0, 0
    button("mdr_sale_send", W - 16 - 150 - 196, Hh - 46, "GFX_mdr_sale_btn_w186", "MDR_SALE_SEND", "MDR_SALE_SEND_TT")


# ---------------------------------------------------------------- scripted GUI
def modes_cond(modes):
    parts = [f"check_variable = {{ mdr_sale_mode = {m} }}" for m in sorted(modes)]
    return parts[0] if len(parts) == 1 else "OR = { " + " ".join(parts) + " }"


def scripted_gui():
    e, props = [], []
    vis, enabled = {}, {}  # element -> extra visibility condition / enabled condition
    e.append("mdr_sale_close_click = { clr_country_flag = mdr_sale_open }")
    e.append("mdr_sale_close_bottom_click = { clr_country_flag = mdr_sale_open }")
    for tab, mode in TABS:
        for st in ("off", "on"):
            e.append(f"mdr_sale_tab_{tab}_{st}_click = {{ set_variable = {{ mdr_sale_mode = {mode} }} mdr_sale_ui_refresh = yes }}")
        vis[f"mdr_sale_tab_{tab}_on"] = f"check_variable = {{ mdr_sale_mode = {mode} }}"
        vis[f"mdr_sale_tab_{tab}_off"] = f"NOT = {{ check_variable = {{ mdr_sale_mode = {mode} }} }}"
    e.append(f"mdr_sale_type_prev_click = {{ add_to_variable = {{ mdr_sale_type = -1 }} if = {{ limit = {{ check_variable = {{ mdr_sale_type < 1 }} }} set_variable = {{ mdr_sale_type = {T} }} }} set_variable = {{ mdr_sale_gen = 0 }} mdr_sale_ui_refresh = yes }}")
    e.append(f"mdr_sale_type_next_click = {{ add_to_variable = {{ mdr_sale_type = 1 }} if = {{ limit = {{ check_variable = {{ mdr_sale_type > {T} }} }} set_variable = {{ mdr_sale_type = 1 }} }} set_variable = {{ mdr_sale_gen = 0 }} mdr_sale_ui_refresh = yes }}")
    e.append("mdr_sale_gen_prev_click = { set_temp_variable = { mdr_sale_dir = -1 } mdr_sale_gen_step = yes mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_gen_next_click = { set_temp_variable = { mdr_sale_dir = 1 } mdr_sale_gen_step = yes mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_qty_minus_click = { add_to_variable = { mdr_sale_qty = -1 } clamp_variable = { var = mdr_sale_qty min = 1 max = 20 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_qty_plus_click = { add_to_variable = { mdr_sale_qty = 1 } clamp_variable = { var = mdr_sale_qty min = 1 max = 20 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_bqty_minus_click = { add_to_variable = { mdr_sd_qty = -1 } clamp_variable = { var = mdr_sd_qty min = 1 max = 6 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_bqty_plus_click = { add_to_variable = { mdr_sd_qty = 1 } clamp_variable = { var = mdr_sd_qty min = 1 max = 6 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_pct_minus_click = { add_to_variable = { mdr_sale_pct = -10 } clamp_variable = { var = mdr_sale_pct min = 10 max = 300 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_pct_plus_click = { add_to_variable = { mdr_sale_pct = 10 } clamp_variable = { var = mdr_sale_pct min = 10 max = 300 } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_gift_click = { if = { limit = { check_variable = { mdr_sale_pct = 0 } } set_variable = { mdr_sale_pct = 100 } } else = { set_variable = { mdr_sale_pct = 0 } } mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_hull_prev_click = { set_temp_variable = { mdr_sale_dir = -1 } mdr_sd_hull_step = yes mdr_sale_ui_refresh = yes }")
    e.append("mdr_sale_hull_next_click = { set_temp_variable = { mdr_sale_dir = 1 } mdr_sd_hull_step = yes mdr_sale_ui_refresh = yes }")
    e.append(f"mdr_sale_design_prev_click = {{ add_to_variable = {{ mdr_sd_design = -1 }} if = {{ limit = {{ check_variable = {{ mdr_sd_design < 1 }} }} set_variable = {{ mdr_sd_design = {ALL_DESIGNS} }} }} mdr_sale_ui_refresh = yes }}")
    e.append(f"mdr_sale_design_next_click = {{ add_to_variable = {{ mdr_sd_design = 1 }} if = {{ limit = {{ check_variable = {{ mdr_sd_design > {ALL_DESIGNS} }} }} set_variable = {{ mdr_sd_design = 1 }} }} mdr_sale_ui_refresh = yes }}")
    for t in range(1, T + 1):
        e.append(f"mdr_sale_lot{t}_minus_click = {{ add_to_variable = {{ mdr_sale_lot_{t} = -1 }} clamp_variable = {{ var = mdr_sale_lot_{t} min = 0 max = 20 }} mdr_sale_ui_refresh = yes }}")
        e.append(f"mdr_sale_lot{t}_plus_click = {{ add_to_variable = {{ mdr_sale_lot_{t} = 1 }} clamp_variable = {{ var = mdr_sale_lot_{t} min = 0 max = 20 }} mdr_sale_ui_refresh = yes }}")
    for r in range(1, ROWS + 1):
        e.append(f"mdr_sale_c{r}_cancel_click = {{ set_temp_variable = {{ mdr_sale_i = {r - 1} }} if = {{ limit = {{ check_variable = {{ mdr_sc_buyer^num > mdr_sale_i }} }} mdr_sale_close_order = yes }} mdr_sale_ui_refresh = yes }}")
        for el in ("flag", "text", "sub", "bar", "cancel"):
            vis[f"mdr_sale_c{r}_{el}"] = f"check_variable = {{ mdr_sc_buyer^num > {r - 1} }}"
        props.append(f'mdr_sale_c{r}_flag = {{ image = "[?ROOT.mdr_sale_c{r}_who.GetFlag]" }}')
        props.append(f"mdr_sale_c{r}_bar = {{ frame = mdr_sale_c{r}_frame }}")
    e.append("mdr_sale_send_click = { mdr_sale_send_offer = yes mdr_sale_ui_refresh = yes }")
    # mdr_sale_pending: an offer to a player buyer is waiting for its answer (mdr_ship_sale.2)
    enabled["mdr_sale_send"] = "check_variable = { mdr_sale_valid = 1 } check_variable = { mdr_sale_prob > 0 } NOT = { has_country_flag = mdr_sale_pending }"
    vis["mdr_sale_contracts_empty"] = "check_variable = { mdr_sc_buyer^num < 1 }"
    for r in (1, 2, 3):
        for el in ("text", "bar", "days"):
            vis[f"mdr_sale_op{r}_{el}"] = f"check_variable = {{ mdr_sale_op{r}_on = 1 }}"
        props.append(f"mdr_sale_op{r}_bar = {{ frame = mdr_sale_op{r}_frame }}")
    for i, tv in enumerate(TOPVIEWS, 1):
        vis[f"mdr_sale_fleet_tv_{tv}"] = f"check_variable = {{ mdr_sale_tv = {i} }}"
        vis[f"mdr_sale_build_tv_{tv}"] = f"check_variable = {{ mdr_sd_tv = {i} }}"
    for row, n, idx in (("t", TOP_MAX, 0), ("b", BOTTOM_MAX, 1)):
        for k in range(1, n + 1):
            ok = [i for i, L in enumerate(LAYOUTS, 1) if len(L[idx]) >= k]
            req = [i for i, L in enumerate(LAYOUTS, 1) if len(L[idx]) >= k and L[idx][k - 1][1]]
            has = ("OR = { " + " ".join(f"check_variable = {{ mdr_sd_layout = {i} }}" for i in ok) + " }") if ok else "always = no"
            for el in ("", "_name"):
                vis[f"mdr_sale_slot_{row}{k}{el}"] = has
            vis[f"mdr_sale_slot_{row}{k}_req"] = ("OR = { " + " ".join(f"check_variable = {{ mdr_sd_layout = {i} }}" for i in req) + " }") if req else "always = no"
            vis[f"mdr_sale_mod_{row}{k}"] = f"{has} check_variable = {{ mdr_sd_m{row}{k} > 0 }}"
            props.append(f'mdr_sale_mod_{row}{k} = {{ image = "[mdr_sale_mod_{row}{k}_gfx]" }}')
    props.append('mdr_sale_flag_seller = { image = "[ROOT.GetFlag]" }')
    props.append('mdr_sale_flag_buyer = { image = "[?ROOT.mdr_sale_target.GetFlag]" }')
    props.append("mdr_sale_sum_bar = { frame = mdr_sale_prob_frame }")
    trg = []
    for name in sorted(set(vis) | set(TAG)):
        conds = []
        if name in TAG:
            conds.append(modes_cond(TAG[name]))
        if name in vis:
            conds.append(vis[name])
        trg.append(f"{name}_visible = {{ {' '.join(conds)} }}")
    for name, c in enabled.items():
        trg.append(f"{name}_click_enabled = {{ {c} }}")
    out = ("# Generated by herramientas/make_ship_sale.py. Ship sale window: ROOT is the player who sells, mdr_sale_target the buyer.\n"
           "scripted_gui = {\n\tmdr_ship_sale_panel = {\n\t\twindow_name = \"mdr_ship_sale_window\"\n\t\tcontext_type = player_context\n"
           "\t\tdirty = global.mdr_sale_dirty\n\t\tvisible = { has_country_flag = mdr_sale_open }\n\n\t\tproperties = {\n")
    out += "".join(f"\t\t\t{p}\n" for p in props)
    out += "\t\t}\n\n\t\teffects = {\n" + "".join(f"\t\t\t{x}\n" for x in e) + "\t\t}\n\n\t\ttriggers = {\n" + "".join(f"\t\t\t{x}\n" for x in trg) + "\t\t}\n\t}\n}\n"
    return out


# ---------------------------------------------------------------- tables (effects)
def effects():
    o = ["# Generated by herramientas/make_ship_sale.py. Tables by ship type (mdr_sale_type 1 to %d) and by hull (mdr_sd_hull 1 to %d)." % (T, H), ""]
    # Sale types.
    o.append("# Seller scope. Output: mdr_sale_base, mdr_sale_have, mdr_sale_days_base, mdr_sale_tv.")
    o.append("mdr_sale_read_type = {")
    for i, (u, p, days, tv, _, _) in enumerate(TYPES, 1):
        o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_type = {i} }} }} set_variable = {{ mdr_sale_base = {p} }} set_variable = {{ mdr_sale_have = num_ships_with_type@{u} }} set_variable = {{ mdr_sale_days_base = {days} }} set_variable = {{ mdr_sale_tv = {TOPVIEWS.index(tv) + 1} }} }}")
    o.append("}\n")
    o.append("# Output: temp mdr_sale_count, ships of type mdr_sale_cur_type; temp mdr_sale_cur_base, its reference price.")
    o.append("mdr_sale_count_type = {\n\tset_temp_variable = { mdr_sale_count = 0 }")
    for i, (u, p, *_r) in enumerate(TYPES, 1):
        o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_type = {i} }} }} set_temp_variable = {{ mdr_sale_count = num_ships_with_type@{u} }} set_temp_variable = {{ mdr_sale_cur_base = {p} }} }}")
    o.append("}\n")
    o.append("# Seller scope, temp mdr_sale_cur_type: removes one ship of that type (it goes into the refit yard).")
    o.append("mdr_sale_take_one = {")
    for i, (u, *_r) in enumerate(TYPES, 1):
        o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_type = {i} }} }} destroy_ships = {{ type = {u} count = 1 }} }}")
    o.append("}\n")
    # Hulls by type, for the hull year row of the fleet page.
    by_type = {i: [] for i in range(1, T + 1)}
    for h in hulls:
        t = TYPE_OF_ARCH.get(hulls[h]["archetype"])
        if t:
            by_type[t].append(h)
    for t in by_type:
        by_type[t].sort(key=lambda h: hulls[h]["year"])
    o.append("# Output: mdr_sale_gen_ok, whether the seller has a ship with the chosen hull.")
    o.append("mdr_sale_check_gen = {\n\tset_variable = { mdr_sale_gen_ok = 0 }")
    for t, hs in by_type.items():
        for g, h in enumerate(hs, 1):
            o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_type = {t} }} check_variable = {{ mdr_sale_gen = {g} }} has_navy_size = {{ archetype = {h} size > 0 }} }} set_variable = {{ mdr_sale_gen_ok = 1 }} }}")
    o.append("}\n")
    o.append("mdr_sale_read_year = {\n\tset_variable = { mdr_sale_year = 0 }")
    for t, hs in by_type.items():
        for g, h in enumerate(hs, 1):
            o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_type = {t} }} check_variable = {{ mdr_sale_gen = {g} }} }} set_variable = {{ mdr_sale_year = {hulls[h]['year']} }} }}")
    o.append("}\n")
    o.append("mdr_sale_read_gen_max = {\n\tset_variable = { mdr_sale_gen_max = 0 }")
    for t, hs in by_type.items():
        if hs:
            o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_type = {t} }} }} set_variable = {{ mdr_sale_gen_max = {len(hs)} }} }}")
    o.append("}\n")
    o.append("""# Steps to the next or previous hull the seller really has, through 0 (any hull). Input temp mdr_sale_dir, 1 or -1.
mdr_sale_gen_step = {
	mdr_sale_read_gen_max = yes
	set_temp_variable = { mdr_sale_go = 1 }
	set_temp_variable = { mdr_sale_guard = 0 }
	while_loop_effect = {
		limit = { check_variable = { mdr_sale_go = 1 } check_variable = { mdr_sale_guard < 30 } }
		add_to_temp_variable = { mdr_sale_guard = 1 }
		add_to_variable = { mdr_sale_gen = mdr_sale_dir }
		if = { limit = { check_variable = { mdr_sale_gen > mdr_sale_gen_max } } set_variable = { mdr_sale_gen = 0 } }
		if = { limit = { check_variable = { mdr_sale_gen < 0 } } set_variable = { mdr_sale_gen = mdr_sale_gen_max } }
		mdr_sale_check_gen = yes
		if = { limit = { OR = { check_variable = { mdr_sale_gen = 0 } check_variable = { mdr_sale_gen_ok = 1 } } } set_temp_variable = { mdr_sale_go = 0 } }
	}
}
""")
    o.append("# Country scope: the seller, global.mdr_sale_to the buyer. Input temps mdr_sale_cur_type, mdr_sale_cur_gen. A ship in refit stays until it is ready.")
    o.append("mdr_sale_try_send = {\n\tvar:global.mdr_sale_to = {\n\t\tPREV = {")
    for t, (u, *_r) in enumerate(TYPES, 1):
        o.append(f'\t\t\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_type = {t} }} check_variable = {{ mdr_sale_cur_gen = 0 }} }} transfer_ship = {{ prefer_name = "Vender" type = {u} exclude_refitting = yes target = PREV }} }}')
        for g, h in enumerate(by_type[t], 1):
            o.append(f'\t\t\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_type = {t} }} check_variable = {{ mdr_sale_cur_gen = {g} }} }}\n\t\t\t\tset_temp_variable = {{ mdr_sale_was = num_ships }}\n\t\t\t\ttransfer_ship = {{ prefer_name = "Vender" type = {h} exclude_refitting = yes target = PREV }}\n\t\t\t\tif = {{ limit = {{ check_variable = {{ num_ships = mdr_sale_was }} has_navy_size = {{ archetype = {h} size > 0 }} }} transfer_ship = {{ prefer_name = "Vender" type = {u} exclude_refitting = yes target = PREV }} }}\n\t\t\t}}')
    o.append("\t\t}\n\t}\n}\n")
    # Hulls for the designer.
    o.append("# Seller scope. Output: mdr_sd_type (sale type), mdr_sd_year, mdr_sd_layout, mdr_sd_tv, mdr_sd_ok (hull researched).")
    o.append("mdr_sd_read_hull = {\n\tset_variable = { mdr_sd_ok = 0 }")
    for i, h in enumerate(HULLS, 1):
        d = hulls[h]
        t = TYPE_OF_ARCH[d["archetype"]]
        o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sd_hull = {i} }} }} set_variable = {{ mdr_sd_type = {t} }} set_variable = {{ mdr_sd_year = {d['year']} }} set_variable = {{ mdr_sd_layout = {LAYOUTS.index(layout(h)) + 1} }} set_variable = {{ mdr_sd_tv = {TOPVIEWS.index(TYPES[t - 1][3]) + 1} }} if = {{ limit = {{ has_tech = {unlock[h]} }} set_variable = {{ mdr_sd_ok = 1 }} }} }}")
    o.append("}\n")
    o.append(f"""# Steps to the next or previous hull the seller has researched. Input temp mdr_sale_dir, 1 or -1.
mdr_sd_hull_step = {{
	set_temp_variable = {{ mdr_sale_go = 1 }}
	set_temp_variable = {{ mdr_sale_guard = 0 }}
	while_loop_effect = {{
		limit = {{ check_variable = {{ mdr_sale_go = 1 }} check_variable = {{ mdr_sale_guard < {H + 1} }} }}
		add_to_temp_variable = {{ mdr_sale_guard = 1 }}
		add_to_variable = {{ mdr_sd_hull = mdr_sale_dir }}
		if = {{ limit = {{ check_variable = {{ mdr_sd_hull > {H} }} }} set_variable = {{ mdr_sd_hull = 1 }} }}
		if = {{ limit = {{ check_variable = {{ mdr_sd_hull < 1 }} }} set_variable = {{ mdr_sd_hull = {H} }} }}
		mdr_sd_read_hull = yes
		if = {{ limit = {{ check_variable = {{ mdr_sd_ok = 1 }} }} set_temp_variable = {{ mdr_sale_go = 0 }} }}
	}}
}}
""")
    # Ready-made designs: module pictures for the window and whether the seller has every module's technology.
    o.append("# Seller scope. Output: mdr_sd_mt1..7 and mdr_sd_mb1..8 (module picture per slot, 0 none), mdr_sd_pok, mdr_sd_custom.")
    o.append("mdr_sd_read_design = {\n\tset_variable = { mdr_sd_pok = 1 }")
    o.append(f"\tset_variable = {{ mdr_sd_custom = mdr_sd_design }}\n\tadd_to_variable = {{ mdr_sd_custom = -{NR} }}")
    for row, n in (("t", TOP_MAX), ("b", BOTTOM_MAX)):
        for k in range(1, n + 1):
            o.append(f"\tset_variable = {{ mdr_sd_m{row}{k} = 0 }}")
    o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sd_design < {NR + 1} }} }}")
    for i, h in enumerate(HULLS, 1):
        o.append(f"\t\tif = {{ limit = {{ check_variable = {{ mdr_sd_hull = {i} }} }}")
        for r in range(1, NR + 1):
            sets = " ".join(f"set_variable = {{ mdr_sd_m{row}{k} = {MOD_IDX[m]} }}" for row, n in (("t", TOP_MAX), ("b", BOTTOM_MAX)) for k in range(1, n + 1) if (m := slot_module(h, r, row, k)))
            techs = sorted({unlock[m] for m in PRESETS[(h, ROLES[r - 1][0])].values() if unlock.get(m)})
            need = " ".join(f"has_tech = {t}" for t in techs)
            chk = f" if = {{ limit = {{ NOT = {{ AND = {{ {need} }} }} }} set_variable = {{ mdr_sd_pok = 0 }} }}" if techs else ""
            o.append(f"\t\t\tif = {{ limit = {{ check_variable = {{ mdr_sd_design = {r} }} }} {sets}{chk} }}")
        o.append("\t\t}")
    o.append("\t}\n}\n")
    o.append("# Seller scope (ROOT), global.mdr_sale_to the buyer. Input temps mdr_sale_cur_hull, mdr_sale_cur_design.")
    o.append("# Ready-made designs are created in the seller the first time (obsolete, so they stay out of its production list,")
    o.append("# as the base game does in _generic_decisions.txt). \"Export N\" is the seller's own design; if there is none, the hull's basic one.")
    o.append("mdr_sd_deliver = {")
    for i, h in enumerate(HULLS, 1):
        o.append(f"\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_hull = {i} }} }}")
        for r in range(1, NR + 1):
            name = variant_name(h, r)
            mods = " ".join(f"{slot} = {m}" for slot, m in PRESETS[(h, ROLES[r - 1][0])].items())
            o.append(f'\t\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_design = {r} }} }}\n'
                     f'\t\t\tif = {{ limit = {{ NOT = {{ has_country_flag = mdr_sdv_{i}_{r} }} }}\n'
                     f'\t\t\t\tcreate_equipment_variant = {{ name = "{name}" type = {h} parent_version = 0 obsolete = yes modules = {{ {mods} }} }}\n'
                     f'\t\t\t\tset_country_flag = mdr_sdv_{i}_{r}\n\t\t\t}}\n'
                     f'\t\t\tvar:global.mdr_sale_to = {{ create_ship = {{ type = {h} equipment_variant = "{name}" creator = ROOT }} }}\n\t\t}}')
        for dsg in range(1, DESIGNS + 1):
            o.append(f'\t\tif = {{ limit = {{ check_variable = {{ mdr_sale_cur_design = {NR + dsg} }} }} var:global.mdr_sale_to = {{ create_ship = {{ type = {h} equipment_variant = "Export {dsg}" creator = ROOT }} }} }}')
        o.append("\t}")
    o.append("}\n")
    return "\n".join(o)


# ---------------------------------------------------------------- scripted localisation
def defined(name, cases, default=None):
    s = f"defined_text = {{\n\tname = {name}\n"
    for trig, key in cases:
        s += f"\ttext = {{\n\t\ttrigger = {{ {trig} }}\n\t\tlocalization_key = {key}\n\t}}\n"
    if default:
        s += f"\ttext = {{\n\t\tlocalization_key = {default}\n\t}}\n"
    return s + "}\n\n"


def scripted_loc():
    s = "# Generated by herramientas/make_ship_sale.py.\n"
    s += defined("mdr_sale_type_text", [(f"check_variable = {{ mdr_sale_type = {i} }}", f"MDR_SALE_TYPE_{i}") for i in range(1, T + 1)])
    s += defined("mdr_sd_type_text", [(f"check_variable = {{ mdr_sd_type = {i} }}", f"MDR_SALE_TYPE_{i}") for i in range(1, T + 1)])
    for r in range(1, ROWS + 1):
        s += defined(f"mdr_sale_c{r}_type_text", [(f"check_variable = {{ mdr_sale_c{r}_type = {i} }}", f"MDR_SALE_TYPE_{i}") for i in range(1, T + 1)])
        s += defined(f"mdr_sale_c{r}_kind_text", [(f"check_variable = {{ mdr_sale_c{r}_kind = {k} }}", f"MDR_SALE_KIND_{k}") for k in (0, 1, 3)])
    for r in (1, 2, 3):
        s += defined(f"mdr_sale_op{r}_type_text", [(f"check_variable = {{ mdr_sale_op{r}_type = {i} }}", f"MDR_SALE_TYPE_{i}") for i in range(1, T + 1)])
        s += defined(f"mdr_sale_h{r}_type_text", [(f"check_variable = {{ mdr_sale_h{r}_type = {i} }}", f"MDR_SALE_TYPE_{i}") for i in range(1, T + 1)], "MDR_SALE_NONE")
    s += defined("mdr_sale_gen_text", [("check_variable = { mdr_sale_gen = 0 }", "MDR_SALE_GEN_ANY")], "MDR_SALE_GEN_YEAR")
    s += defined("mdr_sale_price_text", [("check_variable = { mdr_sale_pct = 0 }", "MDR_SALE_PRICE_GIFT")], "MDR_SALE_PRICE_PCT")
    s += defined("mdr_sale_cost_text", [("check_variable = { mdr_sale_mode = 0 }", "MDR_SALE_COST_FLEET"), ("check_variable = { mdr_sale_mode = 2 }", "MDR_SALE_COST_BATCH")], "MDR_SALE_COST_BUILD")
    s += defined("mdr_sale_rel_text", [(f"check_variable = {{ mdr_sale_rel = {k} }}", f"MDR_SALE_REL_{k}") for k in (1, 2, 3, 4)])
    s += defined("mdr_sale_sanction_text", [("check_variable = { mdr_sale_sanctioned = 1 }", "MDR_SALE_SANCTION_YES")], "MDR_SALE_SANCTION_NO")
    s += defined("mdr_sale_port_text", [("check_variable = { mdr_sale_port = 1 }", "MDR_SALE_PORT_YES")], "MDR_SALE_PORT_NO")
    s += defined("mdr_sale_reason_text", [(f"check_variable = {{ mdr_sale_reason = {k} }}", f"MDR_SALE_REASON_{k}") for k in range(1, 11)], "MDR_SALE_REASON_0")
    s += defined("mdr_sale_build_title_text", [("check_variable = { mdr_sale_mode = 3 }", "MDR_SALE_REFIT_TITLE_T")], "MDR_SALE_BUILD_TITLE_T")
    s += defined("mdr_sale_build_note_text", [("check_variable = { mdr_sale_mode = 3 }", "MDR_SALE_REFIT_NOTE_T")], "MDR_SALE_BUILD_NOTE_T")
    s += defined("mdr_sale_design_text", [(f"check_variable = {{ mdr_sd_design = {r} }}", f"MDR_SD_ROLE_{r}") for r in range(1, NR + 1)], "MDR_SALE_DESIGN_CUSTOM")
    s += defined("mdr_sale_design_help_text", [(f"check_variable = {{ mdr_sd_design < {NR + 1} }} check_variable = {{ mdr_sd_pok = 0 }}", "MDR_SALE_DESIGN_HELP_MISSING"),
                                               (f"check_variable = {{ mdr_sd_design < {NR + 1} }}", "MDR_SALE_DESIGN_HELP_PRESET")], "MDR_SALE_DESIGN_HELP_CUSTOM")
    for row, n in (("t", TOP_MAX), ("b", BOTTOM_MAX)):
        for k in range(1, n + 1):
            here = sorted({MOD_IDX[m] for h in HULLS for r in range(1, NR + 1) if (m := slot_module(h, r, row, k))})
            s += defined(f"mdr_sale_mod_{row}{k}_gfx", [(f"check_variable = {{ mdr_sd_m{row}{k} = {i} }}", f"MDR_SD_GFX_{i}") for i in here], "MDR_SD_GFX_0")
            s += defined(f"mdr_sale_mod_{row}{k}_name", [(f"check_variable = {{ mdr_sd_m{row}{k} = {i} }}", MODS[i - 1]) for i in here], "MDR_SALE_NONE")
    s += defined("mdr_sd_hull_text", [(f"check_variable = {{ mdr_sd_hull = {i} }}", f"MDR_SD_HULL_{i}") for i in range(1, H + 1)])
    for k in range(1, TOP_MAX + 1):
        s += defined(f"mdr_sale_slot_t{k}_text", [(f"check_variable = {{ mdr_sd_layout = {i} }}", f"MDR_SD_SLOT_{L[0][k - 1][0].upper()}") for i, L in enumerate(LAYOUTS, 1) if len(L[0]) >= k])
    for k in range(1, BOTTOM_MAX + 1):
        s += defined(f"mdr_sale_slot_b{k}_text", [(f"check_variable = {{ mdr_sd_layout = {i} }}", f"MDR_SD_SLOT_{L[1][k - 1][0].upper()}") for i, L in enumerate(LAYOUTS, 1) if len(L[1]) >= k])
    for t in range(1, T + 1):
        s += defined(f"mdr_sale_lot{t}_text", [(f"check_variable = {{ mdr_sale_lot_{t} > 0 }}", f"MDR_SALE_LOT{t}_ON")], f"MDR_SALE_LOT{t}_OFF")
    tabs_cases = []
    for tab, mode in TABS:
        s += defined(f"mdr_sale_tab_{tab}_text", [(f"check_variable = {{ mdr_sale_mode = {mode} }}", f"MDR_SALE_TAB_{tab.upper()}_ON")], f"MDR_SALE_TAB_{tab.upper()}_OFF")
    return s


# ---------------------------------------------------------------- texts
ES = r'''
 mdr_sell_ship: "Vender barcos"
 MDR_SELL_SHIP: "Vender barcos"
 MDR_SELL_SHIP_TITLE: "Vender barcos"
 MDR_SELL_SHIP_ACTION_DESC: "Abre la oficina de ventas navales: vender o regalar barcos de la flota, en lote, reacondicionados o construidos para este país."
 mdr_sale_rival_tt: "No es un país rival"
 mdr_sale_port_tt: "Tiene un puerto"
 mdr_sale_cooldown_tt: "Pasaron 30 días desde que nos rechazó una oferta"
 MDR_SALE_SELLER: "[ROOT.GetName]"
 MDR_SALE_SELLER_LABEL: "§YARMADA VENDEDORA§!"
 MDR_SALE_BUYER: "[?ROOT.mdr_sale_target.GetName]"
 MDR_SALE_BUYER_LABEL: "COMPRADOR · Tesoro §Y$$[?ROOT.mdr_sale_buyer_money|1]B§!"
 MDR_SALE_TOP_TREASURY: "TESORO"
 MDR_SALE_TOP_TREASURY_V: "§Y$$[?ROOT.treasury|1]B§!"
 MDR_SALE_TOP_DOCKS: "ASTILLEROS"
 MDR_SALE_TOP_DOCKS_V: "§Y[?ROOT.num_of_naval_factories|0]§!"
 MDR_SALE_TOP_ORDERS: "PEDIDOS"
 MDR_SALE_TOP_ORDERS_V: "§Y[?ROOT.mdr_sc_buyer^num|0]§!"
 MDR_SALE_TOP_DELIVERED: "ENTREGADOS"
 MDR_SALE_TOP_DELIVERED_V: "§G[?ROOT.mdr_sale_delivered|0]§!"
 MDR_SALE_SECTION_OPS: "OPERACIONES"
 MDR_SALE_SECTION_STATE: "ESTADO"
 MDR_SALE_TAB_FLEET: "[ROOT.mdr_sale_tab_fleet_text]"
 MDR_SALE_TAB_FLEET_ON: "§YTransferir / Vender§!"
 MDR_SALE_TAB_FLEET_OFF: "Transferir / Vender"
 MDR_SALE_TAB_FLEET_TT: "Vender o regalar barcos que ya están en tu flota."
 MDR_SALE_TAB_BATCH: "[ROOT.mdr_sale_tab_batch_text]"
 MDR_SALE_TAB_BATCH_ON: "§YVenta en lote§!"
 MDR_SALE_TAB_BATCH_OFF: "Venta en lote"
 MDR_SALE_TAB_BATCH_TT: "Vender varios tipos de barco juntos, a un mismo porcentaje del valor."
 MDR_SALE_TAB_REFIT: "[ROOT.mdr_sale_tab_refit_text]"
 MDR_SALE_TAB_REFIT_ON: "§YVender y reacondicionar§!"
 MDR_SALE_TAB_REFIT_OFF: "Vender y reacondicionar"
 MDR_SALE_TAB_REFIT_TT: "Un barco tuyo entra al astillero, se reconstruye con un diseño de exportación y sale para el comprador. Más rápido y barato que construir uno nuevo."
 MDR_SALE_TAB_BUILD: "[ROOT.mdr_sale_tab_build_text]"
 MDR_SALE_TAB_BUILD_ON: "§YConstruir barco§!"
 MDR_SALE_TAB_BUILD_OFF: "Construir barco"
 MDR_SALE_TAB_BUILD_TT: "Construir barcos nuevos para este país en tus astilleros, con un diseño de exportación."
 MDR_SALE_TAB_CONTRACTS: "[ROOT.mdr_sale_tab_contracts_text]"
 MDR_SALE_TAB_CONTRACTS_ON: "§YContratos§!"
 MDR_SALE_TAB_CONTRACTS_OFF: "Contratos"
 MDR_SALE_TAB_CONTRACTS_TT: "Todos los pedidos abiertos, con su avance. Se pueden cancelar."
 MDR_SALE_STATE_REL: "Relación"
 MDR_SALE_STATE_REL_V: "[ROOT.mdr_sale_rel_text]"
 MDR_SALE_REL_1: "§GAmistosa§!"
 MDR_SALE_REL_2: "§YBuena§!"
 MDR_SALE_REL_3: "§gFría§!"
 MDR_SALE_REL_4: "§RHostil§!"
 MDR_SALE_STATE_NAVY: "Barcos en tu armada"
 MDR_SALE_STATE_NAVY_V: "§Y[?ROOT.num_ships|0]§!"
 MDR_SALE_STATE_PENDING: "Pendientes con este país"
 MDR_SALE_STATE_PENDING_V: "§Y[?ROOT.mdr_sale_pending|0]§! barcos"
 MDR_SALE_STATE_SANCTION: "Riesgo de sanción"
 MDR_SALE_STATE_SANCTION_V: "[ROOT.mdr_sale_sanction_text]"
 MDR_SALE_SANCTION_YES: "§RAlto: está sancionado§!"
 MDR_SALE_SANCTION_NO: "§GNinguno§!"
 MDR_SALE_STATE_PORT: "Puerto del comprador"
 MDR_SALE_STATE_PORT_V: "[ROOT.mdr_sale_port_text]"
 MDR_SALE_PORT_YES: "§GTiene§!"
 MDR_SALE_PORT_NO: "§RNo tiene§!"
 MDR_SALE_OPS_TITLE: "OPERACIONES EN CURSO"
 MDR_SALE_OPS_BUILD: "CONSTRUCCIÓN: §Y[?ROOT.mdr_sale_n_build|0]§! barcos"
 MDR_SALE_OPS_REFIT: "REACONDICIONAMIENTO: §Y[?ROOT.mdr_sale_n_refit|0]§!"
 MDR_SALE_OPS_QUEUE: "COLA DE ENVÍOS: §Y[?ROOT.mdr_sale_n_queue|0]§!"
 MDR_SALE_OPS_QUEUE_V: "§gBarcos de tu flota esperando estar en puerto.§!"
 MDR_SALE_OPS_DONE: "ENTREGADOS: §G[?ROOT.mdr_sale_delivered|0]§!"
 MDR_SALE_OP1: "[?ROOT.mdr_sale_op1_who.GetName] · [ROOT.mdr_sale_op1_type_text]"
 MDR_SALE_OP1_DAYS: "§g[?ROOT.mdr_sale_op1_pct|0]% · próximo en [?ROOT.mdr_sale_op1_days|0] días§!"
 MDR_SALE_OP2: "[?ROOT.mdr_sale_op2_who.GetName] · [ROOT.mdr_sale_op2_type_text]"
 MDR_SALE_OP2_DAYS: "§g[?ROOT.mdr_sale_op2_pct|0]% · próximo en [?ROOT.mdr_sale_op2_days|0] días§!"
 MDR_SALE_OP3: "[?ROOT.mdr_sale_op3_who.GetName] · [ROOT.mdr_sale_op3_type_text]"
 MDR_SALE_OP3_DAYS: "§g[?ROOT.mdr_sale_op3_pct|0]% · sale en [?ROOT.mdr_sale_op3_days|0] días§!"
 MDR_SALE_H1: "[?ROOT.mdr_sale_h1_who.GetName] · [ROOT.mdr_sale_h1_type_text]"
 MDR_SALE_H2: "[?ROOT.mdr_sale_h2_who.GetName] · [ROOT.mdr_sale_h2_type_text]"
 MDR_SALE_H3: "[?ROOT.mdr_sale_h3_who.GetName] · [ROOT.mdr_sale_h3_type_text]"
 MDR_SALE_NONE: "§g—§!"
 MDR_SALE_FLEET_TITLE: "TRANSFERIR O VENDER BARCOS DE TU FLOTA"
 MDR_SALE_LBL_TYPE: "§YTipo§!"
 MDR_SALE_LBL_GEN: "§YAño del casco§!"
 MDR_SALE_LBL_QTY: "§YCantidad§!"
 MDR_SALE_LBL_PCT: "§YPrecio§!"
 MDR_SALE_LBL_DESIGN: "§YDiseño§!"
 MDR_SALE_TYPE_VALUE: "[ROOT.mdr_sale_type_text]  (tenés [?ROOT.mdr_sale_have|0])"
 MDR_SALE_GEN_VALUE: "[ROOT.mdr_sale_gen_text]"
 MDR_SALE_GEN_ANY: "Cualquiera"
 MDR_SALE_GEN_YEAR: "[?ROOT.mdr_sale_year|0]"
 MDR_SALE_QTY_VALUE: "[?ROOT.mdr_sale_qty|0]"
 MDR_SALE_INFO_FLEET: "El juego elige un barco de este tipo y sale apenas esté en puerto. Para mandar uno concreto, renombralo a §YVender§!. Si a los 180 días no salió, se devuelve el dinero."
 MDR_SALE_BATCH_TITLE: "VENTA EN LOTE: VARIOS TIPOS A LA VEZ"
 MDR_SALE_INFO_BATCH: "Cada barco vale el 71% de su tipo nuevo, por el porcentaje elegido abajo. Salen apenas estén en puerto; a los 180 días lo que no salió se devuelve."
 MDR_SALE_BUILD_TITLE: "[ROOT.mdr_sale_build_title_text]"
 MDR_SALE_BUILD_TITLE_T: "CONSTRUIR BARCO PARA [?ROOT.mdr_sale_target.GetName]"
 MDR_SALE_REFIT_TITLE_T: "VENDER Y REACONDICIONAR: USA UN BARCO TUYO DE ESTE TIPO (TENÉS [?ROOT.mdr_sd_have|0])"
 MDR_SALE_BUILD_LEGEND: "§R*§! Ranura obligatoria  ·  Pasá el mouse por un módulo para ver su nombre."
 MDR_SALE_BUILD_NOTE: "[ROOT.mdr_sale_build_note_text]"
 MDR_SALE_BUILD_NOTE_T: "Hace falta al menos un astillero. Mientras construís para otros, tus astilleros rinden un poco menos."
 MDR_SALE_REFIT_NOTE_T: "El barco viejo sale de tu flota al aceptar y vuelve a salir del astillero con el diseño elegido, en el 39% del tiempo."
 MDR_SALE_HULL_VALUE: "[ROOT.mdr_sd_hull_text]"
 MDR_SALE_BQTY_VALUE: "[?ROOT.mdr_sd_qty|0]"
 MDR_SALE_REQ: "§R*§!"
 MDR_SALE_BUILD_STATS: "Precio de referencia: §Y$$[?ROOT.mdr_sale_ref|2]B§!\nEn tu armada: §Y[?ROOT.mdr_sd_have|0]§! de este tipo"
 MDR_SALE_DESIGN_VALUE: "[ROOT.mdr_sale_design_text]"
 MDR_SALE_DESIGN_HELP: "[ROOT.mdr_sale_design_help_text]"
 MDR_SALE_CONTRACTS_TITLE: "CONTRATOS ABIERTOS"
 MDR_SALE_CONTRACTS_EMPTY: "§gNo hay pedidos abiertos.§!"
 MDR_SALE_KIND_0: "De tu flota"
 MDR_SALE_KIND_1: "Construcción"
 MDR_SALE_KIND_3: "Reacondicionamiento"
 MDR_SALE_CANCEL_ROW: "Cancelar"
 MDR_SALE_CANCEL_ROW_TT: "Cancela lo que todavía no salió y le devuelve el dinero al comprador. Lo que ya gastaste en el astillero no vuelve."
 MDR_SALE_SUM_COST: "[ROOT.mdr_sale_cost_text]"
 MDR_SALE_COST_FLEET: "Sale de tu flota apenas esté en puerto · plazo §Y180 días§!"
 MDR_SALE_COST_BATCH: "Lote: §Y[?ROOT.mdr_sale_lot_count|0]§! barcos · plazo §Y180 días§!"
 MDR_SALE_COST_BUILD: "Tu costo: §Y$$[?ROOT.mdr_sale_cost|2]B§!  ·  Plazo: §Y[?ROOT.mdr_sale_days|0] días§! por barco"
 MDR_SALE_SUM_PRICE: "Total: §G$$[?ROOT.mdr_sale_total|2]B§!  ($$[?ROOT.mdr_sale_unit|2]B cada uno)"
 MDR_SALE_CHANCE: "Probabilidad de que acepte: §Y[?ROOT.mdr_sale_prob|0]%§!"
 MDR_SALE_PCT_VALUE: "[ROOT.mdr_sale_price_text]"
 MDR_SALE_PRICE_GIFT: "§GRegalo§!"
 MDR_SALE_PRICE_PCT: "§Y[?ROOT.mdr_sale_pct|0]%§!"
 MDR_SALE_GIFT: "Regalar"
 MDR_SALE_GIFT_TT: "Lo regalamos: no cobramos y mejora su opinión de nosotros. Casi siempre acepta. Tocá otra vez para volver a vender."
 MDR_SALE_REASON: "[ROOT.mdr_sale_reason_text]"
 MDR_SALE_REASON_0: ""
 MDR_SALE_REASON_1: "§RNo le alcanza el dinero para pagar esto.§!"
 MDR_SALE_REASON_2: "§RNo tenés barcos de este tipo.§!"
 MDR_SALE_REASON_3: "§RHace falta al menos un astillero.§!"
 MDR_SALE_REASON_4: "§RTodavía no investigaste este casco.§!"
 MDR_SALE_REASON_5: "§RNo elegiste ningún barco.§!"
 MDR_SALE_REASON_6: "§RNo tenés suficientes barcos de este tipo para reacondicionar.§!"
 MDR_SALE_REASON_7: "§RNo te alcanza el tesoro para pagar la obra.§!"
 MDR_SALE_REASON_8: "§RTe rechazó una oferta hace menos de 30 días.§!"
 MDR_SALE_REASON_9: "§RNo puede comprar: no tiene puerto, es rival o está en guerra con nosotros.§!"
 MDR_SALE_SEND: "Enviar oferta"
 MDR_SALE_SEND_TT: "El comprador decide al instante según la probabilidad. Si acepta, paga todo y empieza el pedido."
 MDR_SALE_CLOSE: "Cerrar"
 mdr_sale_undelivered: "No entregó los barcos que vendió"
 mdr_sale_gift: "Nos regaló barcos"
 mdr_sale_to_sanctioned: "Le vendió barcos a un país sancionado"
 mdr_sale_dockyards: "Astilleros ocupados en exportaciones"
 mdr_sale_dockyards_desc: "Parte de nuestros astilleros trabaja en barcos para otros países."
 MDR_RULE_SHIPS: "Venta de barcos"
 MDR_RULE_SHIPS_ENABLED_DESC: "Los países pueden vender, regalar, reacondicionar y construir barcos para otros desde Diplomacia."
 MDR_RULE_SHIPS_DISABLED_DESC: "Sin venta de barcos entre países."
 mdr_ship_sale.1.t: "Quieren comprarnos un barco"
 mdr_ship_sale.1.d: "[From.GetNameDefCap] quiere comprarnos un barco de nuestra flota y ofrece $$[?global.mdr_sale_offer_price|2]B."
 mdr_ship_sale.1.a: "Aceptar la venta"
 mdr_ship_sale.1.b: "No está a la venta"
 MDR_SALE_DESIGN_CUSTOM: "§YExport [?ROOT.mdr_sd_custom|0]§! (tuyo)"
 MDR_SALE_DESIGN_HELP_PRESET: "Diseño listo, con módulos de la época del casco. Se crea solo al entregar: no hace falta ir a Producción."
 MDR_SALE_DESIGN_HELP_MISSING: "§RTe falta investigar algún módulo de este diseño.§! Probá otra función o un casco más viejo."
 MDR_SALE_DESIGN_HELP_CUSTOM: "En §YProducción§!, diseñá un barco sobre §Yeste mismo casco§! y ponele de nombre §YExport [?ROOT.mdr_sd_custom|0]§!. Si no existe, sale el diseño básico del casco."
 MDR_SALE_REASON_10: "§RTe falta investigar algún módulo de este diseño.§!"
 MDR_SALE_CONTRACTS_SUM: "Pedidos abiertos: §Y[?ROOT.mdr_sc_buyer^num|0]§!  ·  En construcción: §Y[?ROOT.mdr_sale_n_build|0]§!  ·  Reacondicionando: §Y[?ROOT.mdr_sale_n_refit|0]§!  ·  En cola: §Y[?ROOT.mdr_sale_n_queue|0]§!\nLa lista muestra los primeros 7 pedidos."
'''

EN = r'''
 mdr_sell_ship: "Sell Ships"
 MDR_SELL_SHIP: "Sell Ships"
 MDR_SELL_SHIP_TITLE: "Sell Ships"
 MDR_SELL_SHIP_ACTION_DESC: "Opens the naval sales office: sell or give ships from the fleet, in batches, refitted or built for this country."
 mdr_sale_rival_tt: "Is not a rival"
 mdr_sale_port_tt: "Has a port"
 mdr_sale_cooldown_tt: "30 days have passed since it rejected an offer"
 MDR_SALE_SELLER: "[ROOT.GetName]"
 MDR_SALE_SELLER_LABEL: "§YSENDING NAVY§!"
 MDR_SALE_BUYER: "[?ROOT.mdr_sale_target.GetName]"
 MDR_SALE_BUYER_LABEL: "BUYER · Treasury §Y$$[?ROOT.mdr_sale_buyer_money|1]B§!"
 MDR_SALE_TOP_TREASURY: "TREASURY"
 MDR_SALE_TOP_TREASURY_V: "§Y$$[?ROOT.treasury|1]B§!"
 MDR_SALE_TOP_DOCKS: "DOCKYARDS"
 MDR_SALE_TOP_DOCKS_V: "§Y[?ROOT.num_of_naval_factories|0]§!"
 MDR_SALE_TOP_ORDERS: "ORDERS"
 MDR_SALE_TOP_ORDERS_V: "§Y[?ROOT.mdr_sc_buyer^num|0]§!"
 MDR_SALE_TOP_DELIVERED: "DELIVERED"
 MDR_SALE_TOP_DELIVERED_V: "§G[?ROOT.mdr_sale_delivered|0]§!"
 MDR_SALE_SECTION_OPS: "OPERATIONS"
 MDR_SALE_SECTION_STATE: "STATUS"
 MDR_SALE_TAB_FLEET: "[ROOT.mdr_sale_tab_fleet_text]"
 MDR_SALE_TAB_FLEET_ON: "§YTransfer / Sell§!"
 MDR_SALE_TAB_FLEET_OFF: "Transfer / Sell"
 MDR_SALE_TAB_FLEET_TT: "Sell or give ships already in your fleet."
 MDR_SALE_TAB_BATCH: "[ROOT.mdr_sale_tab_batch_text]"
 MDR_SALE_TAB_BATCH_ON: "§YBatch Sale§!"
 MDR_SALE_TAB_BATCH_OFF: "Batch Sale"
 MDR_SALE_TAB_BATCH_TT: "Sell several ship types together, at one percentage of their value."
 MDR_SALE_TAB_REFIT: "[ROOT.mdr_sale_tab_refit_text]"
 MDR_SALE_TAB_REFIT_ON: "§YSell and Refit§!"
 MDR_SALE_TAB_REFIT_OFF: "Sell and Refit"
 MDR_SALE_TAB_REFIT_TT: "One of your ships goes into the dockyard, is rebuilt with an export design and leaves for the buyer. Faster and cheaper than building a new one."
 MDR_SALE_TAB_BUILD: "[ROOT.mdr_sale_tab_build_text]"
 MDR_SALE_TAB_BUILD_ON: "§YBuild Ship§!"
 MDR_SALE_TAB_BUILD_OFF: "Build Ship"
 MDR_SALE_TAB_BUILD_TT: "Build new ships for this country in your dockyards, with an export design."
 MDR_SALE_TAB_CONTRACTS: "[ROOT.mdr_sale_tab_contracts_text]"
 MDR_SALE_TAB_CONTRACTS_ON: "§YContracts§!"
 MDR_SALE_TAB_CONTRACTS_OFF: "Contracts"
 MDR_SALE_TAB_CONTRACTS_TT: "Every open order, with its progress. They can be cancelled."
 MDR_SALE_STATE_REL: "Relations"
 MDR_SALE_STATE_REL_V: "[ROOT.mdr_sale_rel_text]"
 MDR_SALE_REL_1: "§GFriendly§!"
 MDR_SALE_REL_2: "§YGood§!"
 MDR_SALE_REL_3: "§gCold§!"
 MDR_SALE_REL_4: "§RHostile§!"
 MDR_SALE_STATE_NAVY: "Ships in your navy"
 MDR_SALE_STATE_NAVY_V: "§Y[?ROOT.num_ships|0]§!"
 MDR_SALE_STATE_PENDING: "Pending with this country"
 MDR_SALE_STATE_PENDING_V: "§Y[?ROOT.mdr_sale_pending|0]§! ships"
 MDR_SALE_STATE_SANCTION: "Sanction risk"
 MDR_SALE_STATE_SANCTION_V: "[ROOT.mdr_sale_sanction_text]"
 MDR_SALE_SANCTION_YES: "§RHigh: it is sanctioned§!"
 MDR_SALE_SANCTION_NO: "§GNone§!"
 MDR_SALE_STATE_PORT: "Buyer's port"
 MDR_SALE_STATE_PORT_V: "[ROOT.mdr_sale_port_text]"
 MDR_SALE_PORT_YES: "§GYes§!"
 MDR_SALE_PORT_NO: "§RNone§!"
 MDR_SALE_OPS_TITLE: "CURRENT OPERATIONS"
 MDR_SALE_OPS_BUILD: "CONSTRUCTION: §Y[?ROOT.mdr_sale_n_build|0]§! ships"
 MDR_SALE_OPS_REFIT: "REFITS: §Y[?ROOT.mdr_sale_n_refit|0]§!"
 MDR_SALE_OPS_QUEUE: "TRANSFER QUEUE: §Y[?ROOT.mdr_sale_n_queue|0]§!"
 MDR_SALE_OPS_QUEUE_V: "§gShips from your fleet waiting to be in port.§!"
 MDR_SALE_OPS_DONE: "DELIVERED: §G[?ROOT.mdr_sale_delivered|0]§!"
 MDR_SALE_OP1: "[?ROOT.mdr_sale_op1_who.GetName] · [ROOT.mdr_sale_op1_type_text]"
 MDR_SALE_OP1_DAYS: "§g[?ROOT.mdr_sale_op1_pct|0]% · next in [?ROOT.mdr_sale_op1_days|0] days§!"
 MDR_SALE_OP2: "[?ROOT.mdr_sale_op2_who.GetName] · [ROOT.mdr_sale_op2_type_text]"
 MDR_SALE_OP2_DAYS: "§g[?ROOT.mdr_sale_op2_pct|0]% · next in [?ROOT.mdr_sale_op2_days|0] days§!"
 MDR_SALE_OP3: "[?ROOT.mdr_sale_op3_who.GetName] · [ROOT.mdr_sale_op3_type_text]"
 MDR_SALE_OP3_DAYS: "§g[?ROOT.mdr_sale_op3_pct|0]% · leaves in [?ROOT.mdr_sale_op3_days|0] days§!"
 MDR_SALE_H1: "[?ROOT.mdr_sale_h1_who.GetName] · [ROOT.mdr_sale_h1_type_text]"
 MDR_SALE_H2: "[?ROOT.mdr_sale_h2_who.GetName] · [ROOT.mdr_sale_h2_type_text]"
 MDR_SALE_H3: "[?ROOT.mdr_sale_h3_who.GetName] · [ROOT.mdr_sale_h3_type_text]"
 MDR_SALE_NONE: "§g—§!"
 MDR_SALE_FLEET_TITLE: "TRANSFER OR SELL SHIPS FROM YOUR FLEET"
 MDR_SALE_LBL_TYPE: "§YType§!"
 MDR_SALE_LBL_GEN: "§YHull Year§!"
 MDR_SALE_LBL_QTY: "§YQuantity§!"
 MDR_SALE_LBL_PCT: "§YPrice§!"
 MDR_SALE_LBL_DESIGN: "§YDesign§!"
 MDR_SALE_TYPE_VALUE: "[ROOT.mdr_sale_type_text]  (you have [?ROOT.mdr_sale_have|0])"
 MDR_SALE_GEN_VALUE: "[ROOT.mdr_sale_gen_text]"
 MDR_SALE_GEN_ANY: "Any"
 MDR_SALE_GEN_YEAR: "[?ROOT.mdr_sale_year|0]"
 MDR_SALE_QTY_VALUE: "[?ROOT.mdr_sale_qty|0]"
 MDR_SALE_INFO_FLEET: "The game picks a ship of this type and it leaves as soon as it is in port. To send a specific one, rename it §YVender§!. If it has not left after 180 days, the money goes back."
 MDR_SALE_BATCH_TITLE: "BATCH SALE: SEVERAL TYPES AT ONCE"
 MDR_SALE_INFO_BATCH: "Each ship is worth 71% of a new one of its type, times the percentage chosen below. They leave as soon as they are in port; after 180 days what has not left is refunded."
 MDR_SALE_BUILD_TITLE: "[ROOT.mdr_sale_build_title_text]"
 MDR_SALE_BUILD_TITLE_T: "BUILD A SHIP FOR [?ROOT.mdr_sale_target.GetName]"
 MDR_SALE_REFIT_TITLE_T: "SELL AND REFIT: USES ONE OF YOUR SHIPS OF THIS TYPE (YOU HAVE [?ROOT.mdr_sd_have|0])"
 MDR_SALE_BUILD_LEGEND: "§R*§! Required slot  ·  Hover over a module to see its name."
 MDR_SALE_BUILD_NOTE: "[ROOT.mdr_sale_build_note_text]"
 MDR_SALE_BUILD_NOTE_T: "At least one dockyard is needed. While you build for others, your dockyards produce a little less."
 MDR_SALE_REFIT_NOTE_T: "The old ship leaves your fleet on acceptance and comes out of the dockyard with the chosen design, in 39% of the time."
 MDR_SALE_HULL_VALUE: "[ROOT.mdr_sd_hull_text]"
 MDR_SALE_BQTY_VALUE: "[?ROOT.mdr_sd_qty|0]"
 MDR_SALE_REQ: "§R*§!"
 MDR_SALE_BUILD_STATS: "Reference price: §Y$$[?ROOT.mdr_sale_ref|2]B§!\nIn your navy: §Y[?ROOT.mdr_sd_have|0]§! of this type"
 MDR_SALE_DESIGN_VALUE: "[ROOT.mdr_sale_design_text]"
 MDR_SALE_DESIGN_HELP: "[ROOT.mdr_sale_design_help_text]"
 MDR_SALE_CONTRACTS_TITLE: "OPEN CONTRACTS"
 MDR_SALE_CONTRACTS_EMPTY: "§gNo open orders.§!"
 MDR_SALE_KIND_0: "From your fleet"
 MDR_SALE_KIND_1: "Construction"
 MDR_SALE_KIND_3: "Refit"
 MDR_SALE_CANCEL_ROW: "Cancel"
 MDR_SALE_CANCEL_ROW_TT: "Cancels what has not left yet and refunds the buyer. What you already spent in the dockyard does not come back."
 MDR_SALE_SUM_COST: "[ROOT.mdr_sale_cost_text]"
 MDR_SALE_COST_FLEET: "Leaves your fleet as soon as it is in port · deadline §Y180 days§!"
 MDR_SALE_COST_BATCH: "Batch: §Y[?ROOT.mdr_sale_lot_count|0]§! ships · deadline §Y180 days§!"
 MDR_SALE_COST_BUILD: "Your cost: §Y$$[?ROOT.mdr_sale_cost|2]B§!  ·  Time: §Y[?ROOT.mdr_sale_days|0] days§! per ship"
 MDR_SALE_SUM_PRICE: "Total: §G$$[?ROOT.mdr_sale_total|2]B§!  ($$[?ROOT.mdr_sale_unit|2]B each)"
 MDR_SALE_CHANCE: "Chance of acceptance: §Y[?ROOT.mdr_sale_prob|0]%§!"
 MDR_SALE_PCT_VALUE: "[ROOT.mdr_sale_price_text]"
 MDR_SALE_PRICE_GIFT: "§GGift§!"
 MDR_SALE_PRICE_PCT: "§Y[?ROOT.mdr_sale_pct|0]%§!"
 MDR_SALE_GIFT: "Give"
 MDR_SALE_GIFT_TT: "We give it away: no payment, and its opinion of us improves. Almost always accepted. Click again to go back to selling."
 MDR_SALE_REASON: "[ROOT.mdr_sale_reason_text]"
 MDR_SALE_REASON_0: ""
 MDR_SALE_REASON_1: "§RIt cannot afford this.§!"
 MDR_SALE_REASON_2: "§RYou have no ships of this type.§!"
 MDR_SALE_REASON_3: "§RAt least one dockyard is needed.§!"
 MDR_SALE_REASON_4: "§RYou have not researched this hull yet.§!"
 MDR_SALE_REASON_5: "§RNo ship chosen.§!"
 MDR_SALE_REASON_6: "§RYou do not have enough ships of this type to refit.§!"
 MDR_SALE_REASON_7: "§RYour treasury cannot pay for the work.§!"
 MDR_SALE_REASON_8: "§RIt rejected an offer less than 30 days ago.§!"
 MDR_SALE_REASON_9: "§RIt cannot buy: no port, a rival or at war with us.§!"
 MDR_SALE_SEND: "Send Offer"
 MDR_SALE_SEND_TT: "The buyer decides at once according to the chance. If it accepts, it pays everything and the order starts."
 MDR_SALE_CLOSE: "Close"
 mdr_sale_undelivered: "Did not deliver the ships it sold"
 mdr_sale_gift: "Gave us ships"
 mdr_sale_to_sanctioned: "Sold ships to a sanctioned country"
 mdr_sale_dockyards: "Dockyards busy with exports"
 mdr_sale_dockyards_desc: "Part of our dockyards works on ships for other countries."
 MDR_RULE_SHIPS: "Ship Sales"
 MDR_RULE_SHIPS_ENABLED_DESC: "Countries can sell, give, refit and build ships for others from Diplomacy."
 MDR_RULE_SHIPS_DISABLED_DESC: "No ship sales between countries."
 mdr_ship_sale.1.t: "They Want to Buy a Ship"
 mdr_ship_sale.1.d: "[From.GetNameDefCap] wants to buy a ship from our fleet and offers $$[?global.mdr_sale_offer_price|2]B."
 mdr_ship_sale.1.a: "Accept the sale"
 mdr_ship_sale.1.b: "It is not for sale"
 MDR_SALE_DESIGN_CUSTOM: "§YExport [?ROOT.mdr_sd_custom|0]§! (yours)"
 MDR_SALE_DESIGN_HELP_PRESET: "Ready-made design, with modules of the hull's era. It is created on delivery: no need to go to Production."
 MDR_SALE_DESIGN_HELP_MISSING: "§RYou have not researched every module of this design.§! Try another role or an older hull."
 MDR_SALE_DESIGN_HELP_CUSTOM: "In §YProduction§!, design a ship on §Ythis same hull§! and name it §YExport [?ROOT.mdr_sd_custom|0]§!. If there is none, the hull's basic design is built."
 MDR_SALE_REASON_10: "§RYou have not researched every module of this design.§!"
 MDR_SALE_CONTRACTS_SUM: "Open orders: §Y[?ROOT.mdr_sc_buyer^num|0]§!  ·  Building: §Y[?ROOT.mdr_sale_n_build|0]§!  ·  Refitting: §Y[?ROOT.mdr_sale_n_refit|0]§!  ·  Queued: §Y[?ROOT.mdr_sale_n_queue|0]§!\nThe list shows the first 7 orders."
'''


NL = chr(10)


def texts():
    for lang, body, n in (("spanish", ES, 4), ("english", EN, 5)):
        x = f"l_{lang}:" + body
        for i, ty in enumerate(TYPES, 1):
            x += f' MDR_SALE_TYPE_{i}: "{ty[n]}"\n'
            x += f' MDR_SALE_LOT{i}: "[ROOT.mdr_sale_lot{i}_text]"\n'
            have = "tenés" if lang == "spanish" else "you have"
            x += f' MDR_SALE_LOT{i}_ON: "§Y{ty[n]}§! ({have} [?ROOT.mdr_sale_lothave_{i}|0])"\n'
            x += f' MDR_SALE_LOT{i}_OFF: "{ty[n]} §g({have} [?ROOT.mdr_sale_lothave_{i}|0])§!"\n'
            x += f' MDR_SALE_LOT{i}_V: "[?ROOT.mdr_sale_lot_{i}|0]"\n'
        for i, h in enumerate(HULLS, 1):
            t = TYPES[TYPE_OF_ARCH[hulls[h]["archetype"]] - 1]
            x += f' MDR_SD_HULL_{i}: "{t[n]} de {hulls[h]["year"]}"\n' if lang == "spanish" else f' MDR_SD_HULL_{i}: "{hulls[h]["year"]} {t[n]}"\n'
        for k in range(1, TOP_MAX + 1):
            x += f' MDR_SALE_SLOT_T{k}: "[ROOT.mdr_sale_slot_t{k}_text]"' + NL
        for k in range(1, BOTTOM_MAX + 1):
            x += f' MDR_SALE_SLOT_B{k}: "[ROOT.mdr_sale_slot_b{k}_text]"' + NL
        for r, role in enumerate(ROLES, 1):
            x += f' MDR_SD_ROLE_{r}: "§Y{role[1] if lang == "spanish" else role[2]}§!"' + NL
        x += ' MDR_SD_GFX_0: "GFX_mdr_sale_mod_placeholder"' + NL
        for m, i in MOD_IDX.items():
            x += f' MDR_SD_GFX_{i}: "{sprite_of(m)}"' + NL
        for row, n in (("t", TOP_MAX), ("b", BOTTOM_MAX)):
            for k in range(1, n + 1):
                x += f' MDR_SALE_MOD_{row.upper()}{k}_TT: "[ROOT.mdr_sale_mod_{row}{k}_name]"' + NL
        for slot, names in SLOT_NAMES.items():
            x += f' MDR_SD_SLOT_{slot.upper()}: "{names[0 if lang == "spanish" else 1]}"\n'
        for r in range(1, ROWS + 1):
            if lang == "spanish":
                x += f' MDR_SALE_C{r}: "[?ROOT.mdr_sale_c{r}_who.GetName] · [ROOT.mdr_sale_c{r}_type_text] ×[?ROOT.mdr_sale_c{r}_qty|0]"\n'
                x += f' MDR_SALE_C{r}_SUB: "§g[ROOT.mdr_sale_c{r}_kind_text] · $$[?ROOT.mdr_sale_c{r}_unit|2]B cada uno · quedan [?ROOT.mdr_sale_c{r}_days|0] días§!"\n'
            else:
                x += f' MDR_SALE_C{r}: "[?ROOT.mdr_sale_c{r}_who.GetName] · [ROOT.mdr_sale_c{r}_type_text] ×[?ROOT.mdr_sale_c{r}_qty|0]"\n'
                x += f' MDR_SALE_C{r}_SUB: "§g[ROOT.mdr_sale_c{r}_kind_text] · $$[?ROOT.mdr_sale_c{r}_unit|2]B each · [?ROOT.mdr_sale_c{r}_days|0] days left§!"\n'
        spew(f"localisation/{lang}/mdr_ship_sale_l_{lang}.yml", x, bom=True)


def main():
    textures()
    spew("interface/mdr_ship_sale.gfx", gfx())
    build_window()
    spew("interface/mdr_ship_sale.gui", "# Generated by herramientas/make_ship_sale.py.\nguiTypes = {\n" + "\n".join(gui) + "\n}\n")
    spew("common/scripted_guis/mdr_ship_sale_gui.txt", scripted_gui())
    spew("common/scripted_effects/mdr_ship_sale_gen.txt", effects())
    spew("common/scripted_localisation/mdr_ship_sale_loc.txt", scripted_loc())
    texts()
    print(f"{T} types, {H} hulls, {len(LAYOUTS)} slot layouts")


if __name__ == "__main__":
    main()
