# One more resource box in the tank, plane and ship designers, for the fifth material (MAX_EQUIPMENT_RESOURCES_NEED in zz_mdr_defines.lua):
# a wider background and copies of Millennium Dawn's views with a wider text box. Run from the mod folder after each Millennium Dawn update:
# python herramientas/make_designer_resources.py
import os
import re
import struct
import sys

from PIL import Image

MD = "../Millennium-Dawn-2.0.0/"
TEXTURE = "gfx/interface/equipmentdesigner/tanks/resources_bg.dds"
EXTRA = 24
EDGE = 20

# View: text box width, and where the refit cost starts (None keeps it, the wider box does not reach it).
VIEWS = {
    "interface/tank_designer_view.gui": (150, 660),
    "interface/plane_designer_view.gui": (115, None),
    "interface/equipmentdesignerview.gui": (115, None),
}


def write_dds(path, im):
    w, h = im.size
    header = struct.pack("<4s7I44x2I4s5I5I", b"DDS ", 124, 0x100F, h, w, w * 4, 0, 1,
                         32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000, 0x1000, 0, 0, 0, 0)
    r, g, b, a = im.split()
    open(path, "wb").write(header + Image.merge("RGBA", (b, g, r, a)).tobytes())


def wider_texture():
    im = Image.open(MD + TEXTURE).convert("RGBA")
    w, h = im.size
    new = Image.new("RGBA", (w + EXTRA, h))
    new.paste(im.crop((0, 0, EDGE, h)), (0, 0))
    new.paste(im.crop((EDGE, 0, w - EDGE, h)).resize((w + EXTRA - 2 * EDGE, h), Image.NEAREST), (EDGE, 0))
    new.paste(im.crop((w - EDGE, 0, w, h)), (w + EXTRA - EDGE, 0))
    os.makedirs(os.path.dirname(TEXTURE), exist_ok=True)
    write_dds(TEXTURE, new)


def wider_view(name, width, refit_x):
    text = open(MD + name, encoding="utf-8", newline="").read()
    text, n = re.subn(r'(name = "production_resources"(?:(?!instantTextboxType).)*?maxWidth = )\d+', r"\g<1>%d" % width, text, count=1, flags=re.S)
    if n != 1:
        sys.exit("no production_resources in " + name)
    if refit_x is not None:
        text, n = re.subn(r'(name = "refit_cost"\s*position = \{ x= *)\d+', r"\g<1>%d" % refit_x, text, count=1)
        if n != 1:
            sys.exit("no refit_cost in " + name)
    open(name, "w", encoding="utf-8", newline="").write(text)


wider_texture()
for view, (box, refit) in VIEWS.items():
    wider_view(view, box, refit)
print("ok")
