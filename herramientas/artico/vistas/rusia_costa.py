# Preview of option 2 over Russia: carve the real Arctic coast into MD's top rows, but every MD province keeps
# at least its southern KEEP share. argv: herramientas dir, scratchpad dir
import sys, os
sys.path.insert(0, sys.argv[1])
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import binary_opening, label, binary_dilation
import construir_mapa as cm

S = sys.argv[2]
KEEP = 0.35
cache = os.path.join(S, 'realA.npy')
md = cm.MD(os.path.abspath(os.path.join(cm.MOD, '..', 'Millennium-Dawn-2.0.0')))
if os.path.exists(cache):
    A = np.load(cache)
else:
    A = cm.Geo(md, []).A.astype(bool)
    np.save(cache, A)
N = cm.NEW
R = A.shape[0]                                   # enlarged-map rows covered by A (new rows + MD's top rows)
land_now = np.load(os.path.join(S, 'land.npy'))[:R]   # current mod, same rows
ids_md = md.id_map()[:R - N]

x0 = int((30 - cm.LON_CUT) / 360 * cm.W)         # Kola peninsula eastwards to the Bering cut
reg = np.zeros((R, cm.W), bool)
reg[:, x0:] = True

# MD land that is sea in reality, near the north edge only, reached from the open sea, without calibration noise
cut = np.zeros((R, cm.W), bool)
cut[N:] = land_now[N:] & ~A[N:]
cut &= reg
cut[N + 220:] = False
cut = binary_opening(cut, iterations=4)
lab, n = label(cut)
touch = np.unique(lab[N][cut[N]])
cut = np.isin(lab, touch[touch > 0])

# every MD province keeps its southern KEEP share
protect = np.zeros_like(cut)
sub = cut[N:]
for p in np.unique(ids_md[sub]):
    rr, cc = np.nonzero(ids_md == p)
    thr = np.quantile(rr, 1 - KEEP)
    keep = rr >= thr
    protect[N + rr[keep], cc[keep]] = True
cut &= ~protect

new = land_now.copy()
new[N:] &= ~cut[N:]
new[:N][:, x0:] = A[:N, x0:]                     # new rows over Russia follow the real coast

lost = np.bincount(ids_md[cut[N:]], minlength=ids_md.max() + 1)
tot = np.bincount(ids_md.ravel(), minlength=ids_md.max() + 1)
aff = np.nonzero(lost)[0]
print('provincias de MD recortadas:', len(aff), ' píxeles que pasan a mar:', int(cut.sum()),
      ' recorte máximo de una provincia: %.0f%%' % (100 * (lost[aff] / tot[aff]).max()))

SEA, LAND, CUT = (70, 110, 160), (176, 160, 112), (220, 70, 60)
def paint(m, extra=None):
    a = np.empty(m.shape + (3,), np.uint8)
    a[:] = SEA
    a[m] = LAND
    if extra is not None:
        a[extra] = CUT
    # MD province borders, faint
    b = np.zeros(m.shape, bool)
    idb = ids_md
    e = (idb[1:] != idb[:-1])[:, :] ; b[N + 1:][e] = True
    e = (idb[:, 1:] != idb[:, :-1]); b[N:, 1:][e] = True
    a[b & m] = (a[b & m] * 0.75).astype(np.uint8)
    return a

y1 = 620
panels = [('AHORA (como está en el juego)', paint(land_now)[:y1, x0:]),
          ('CAMBIOS: en rojo, la tierra de MD que pasa a ser mar', paint(land_now, cut)[:y1, x0:]),
          ('RESULTADO: costa real de Siberia', paint(new)[:y1, x0:])]
font = ImageFont.truetype('arial.ttf', 22)
w = cm.W - x0
sc = 2
out = Image.new('RGB', (w // sc, len(panels) * (y1 // sc + 40)), (24, 26, 30))
d = ImageDraw.Draw(out)
for i, (t, a) in enumerate(panels):
    y = i * (y1 // sc + 40)
    d.text((8, y + 8), t, fill='white', font=font)
    im = Image.fromarray(a).resize((w // sc, y1 // sc), Image.LANCZOS)
    out.paste(im, (0, y + 40))
    d.line([(0, y + 40 + N // sc), (w // sc, y + 40 + N // sc)], fill=(255, 210, 0))
out.save(os.path.join(S, 'rusia_costa.png'))
print(out.size)
