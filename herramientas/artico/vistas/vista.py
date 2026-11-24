# Preview: current map (2304 rows) vs. proposal (north strip squeezed, Antarctica strip added; 2327 rows).
import sys, json, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

S = sys.argv[1]
DATA = __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "..", "datos")
land = np.load(os.path.join(S, "land.npy"))           # 2304 x 5632, top-down
H, W = land.shape
NORTH_OLD, MD = 256, 2048
NORTH_NEW, SOUTH = 179, 100
LAT_S0 = -60.0                                         # latitude at the top of the new south strip
LON_CUT = -169.0
SEA, LAND, ICE = (70, 110, 160), (176, 160, 112), (236, 242, 248)

def antarctica():
    m = Image.new("L", (W, SOUTH), 0)
    d = ImageDraw.Draw(m)
    for fn, val in (("ne_10m_land.geojson", 1), ("ne_10m_glaciated_areas.geojson", 2)):
        gj = json.load(open(os.path.join(DATA, fn), encoding="utf-8"))
        for f in gj["features"]:
            g = f["geometry"]
            polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
            for poly in polys:
                ring = np.array(poly[0])
                if ring[:, 1].max() > LAT_S0 + 2:
                    continue
                x = (ring[:, 0] - LON_CUT) / 360 * W
                y = (LAT_S0 - ring[:, 1]) / (LAT_S0 + 90) * SOUTH
                for off in (0, W, -W):
                    d.polygon(list(zip(x + off, y)), fill=val if val == 1 else 2)
    a = np.asarray(m)
    return a

def paint(mask_land, ice=None):
    img = np.empty(mask_land.shape + (3,), np.uint8)
    img[:] = SEA
    img[mask_land] = LAND
    if ice is not None:
        img[ice] = ICE
    return img

now = paint(land)
north = Image.fromarray(paint(land[:NORTH_OLD])).resize((W, NORTH_NEW), Image.LANCZOS)
ant = antarctica()
south = paint(ant > 0, ant > 0)                       # Antarctica is all ice
prop = np.vstack([np.asarray(north), paint(land[NORTH_OLD:]), south])

scale = 4
def small(a):
    return Image.fromarray(a).resize((W // scale, a.shape[0] // scale), Image.LANCZOS)

a, b = small(now), small(prop)
pad, title = 16, 34
font = ImageFont.truetype("arial.ttf", 20)
fsmall = ImageFont.truetype("arial.ttf", 14)
out = Image.new("RGB", (a.width + 2 * pad, a.height + b.height + 2 * title + 3 * pad), (24, 26, 30))
d = ImageDraw.Draw(out)
y = pad
d.text((pad, y), "AHORA: 5632 x 2304 (norte hasta 84,5°, sin Antártida)", fill="white", font=font)
y += title
out.paste(a, (pad, y))
d.line([(pad, y + NORTH_OLD // scale), (pad + a.width, y + NORTH_OLD // scale)], fill=(255, 210, 0), width=1)
d.text((pad + 4, y + 2), "franja ártica agregada (256 filas)", fill=(255, 210, 0), font=fsmall)
y += a.height + pad
d.text((pad, y), "PROPUESTA: 5632 x 2327 (entra en los 50 MB) - norte 179 filas, Antártida 100 filas", fill="white", font=font)
y += title
out.paste(b, (pad, y))
for r in (NORTH_NEW, NORTH_NEW + MD):
    d.line([(pad, y + r // scale), (pad + b.width, y + r // scale)], fill=(255, 210, 0), width=1)
d.text((pad + 4, y + 2), "Ártico (179 filas, más chato)", fill=(255, 210, 0), font=fsmall)
d.text((pad + 4, y + (NORTH_NEW + MD) // scale + 2), "Antártida (100 filas)", fill=(255, 210, 0), font=fsmall)
out.save(os.path.join(S, "vista_mapa.png"))
print(out.size)
