"""Greenland on the globe. Millennium Dawn draws it off (its south half lies several degrees west of the real one) and almost no
cities are there to calibrate MdrGlobeLat and MdrGlobeLonOffset, which leave it deformed. This fits the map's coast onto the real
one from Natural Earth and prints MdrGlobeGreenland, a correction that only acts around the island, for
gfx/FX/standardfuncsgfx.fxh. Run it again if the map or those two functions change.

    python herramientas/globo_groenlandia.py [vista.png]
"""
import json
import os
import re
import sys

import numpy as np
from numpy.polynomial.chebyshev import chebvander
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree

Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
W, H = 5632.0, 2304.0
BOX = (1640.0, 2740.0, 1860.0, 2400.0)  # x and z where the correction acts; it fades out to nothing at the edges
FADE = 80.0
SEED = (2200, 2150)                     # a column and a row of the island, row 0 at the bottom
DEGREE = 7
NAME_BOX = (1800.0, 2600.0, 2000.0, 2300.0)  # where the game puts the island's name on the map
NAME_CENTER = (2265.3, 2147.2)               # where the game has the name on the map, measured from a screenshot of the globe
NAME_BASELINE = (415.0, 78.1)                # and the name from end to end, measured the same way
NAME_DEGREE = 4                              # of the polynomials that place its vertices
NAME_ANGLE = 60.0                            # its slant on the globe, in degrees from east
NAME_SCALE = 0.533                           # its size on the globe against the map's: about 225 long, with room at that slant
TIPS = [(2114, 1920, -43.9, 59.8), (2306, 2299, -31.0, 83.6), (1746, 2273, -73.0, 78.2), (2640, 2276, -11.6, 81.3)]


def shader_coefficients(text, name):
    body = text[text.index('float %s( float x, float z )' % name):]
    body = body[:body.index(';', body.index('return')) + 1]
    rows = []
    for line in re.findall(r'(?:n = 2\.0f \* t \* b1 - b2 \+|return t \* b1 - b2 \+) (.*?);', body):
        terms = dict((n or '1', float(k)) for k, n in re.findall(r'([+-]?\d+\.\d+)(?:\*([cs]\d))?', line.replace('f', '').replace(' ', '')))
        rows.append([terms['1']] + [terms[p + str(h)] for h in range(1, 9) for p in 'cs'])
    return np.array(rows[::-1])


def evaluate(c, x, z):
    """c[degree, wave] at the points x, z of the same shape, as the shader does."""
    a = x.ravel() / W * 6.28318
    waves = np.stack([np.ones_like(a)] + [f(h * a) for h in range(1, 9) for f in (np.cos, np.sin)], 1)
    cheb = chebvander(2 * np.clip(z.ravel() / H, 0, 1) - 1, c.shape[0] - 1)
    return ((cheb @ c) * waves).sum(1).reshape(x.shape)


def real_outline():
    with open(os.path.join(HERE, 'artico', 'datos', 'ne_10m_land.geojson'), encoding='utf-8') as f:
        features = json.load(f)['features']
    best = np.zeros((0, 2))
    for ft in features:
        g = ft['geometry']
        for p in (g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]):
            r = np.array(p[0])
            if r[:, 0].min() > -80 and r[:, 0].max() < -5 and r[:, 1].min() > 55 and len(r) > len(best):
                best = r
    return best


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def window(x, z):
    return (smoothstep(BOX[0], BOX[0] + FADE, x) * smoothstep(BOX[1], BOX[1] - FADE, x)
            * smoothstep(BOX[2], BOX[2] + FADE, z) * smoothstep(BOX[3], BOX[3] - FADE, z))


def basis(x, z):
    u = (2 * x - BOX[0] - BOX[1]) / (BOX[1] - BOX[0])
    v = (2 * z - BOX[2] - BOX[3]) / (BOX[3] - BOX[2])
    cu, cv = chebvander(u, DEGREE), chebvander(v, DEGREE)
    return np.stack([cu[:, i] * cv[:, j] for i in range(DEGREE + 1) for j in range(DEGREE + 1 - i)], 1)


def polar(lon, lat):
    """Degrees from the pole, turned to the island's middle: a flat plane without a problem at the pole."""
    r = 90.0 - lat
    a = np.radians(lon + 42.0)
    return np.stack([r * np.sin(a), r * np.cos(a)], -1)


def unpolar(p):
    return np.degrees(np.arctan2(p[..., 0], p[..., 1])) - 42.0, 90.0 - np.hypot(p[..., 0], p[..., 1])


def name_spot(island, fixed, want, length, radius):
    """The map position where the straight text has most room on the island as the globe draws it."""
    iz, ix = np.nonzero(island)
    ix, iz = ix[::2].astype(float), iz[::2].astype(float)
    lon, lat = fixed(ix, iz)
    q = polar(lon, lat) * np.pi / 180 * radius
    res = 2.0
    low = q.min(0) - 40
    pixels = ((q - low) / res).astype(int)
    size = pixels.max(0) + 40
    grid = np.zeros((size[1], size[0]), bool)
    grid[pixels[:, 1], pixels[:, 0]] = True
    grid = ndimage.binary_fill_holes(ndimage.binary_closing(grid, iterations=2))
    room = ndimage.distance_transform_edt(grid) * res
    best = (-1.0, None)
    for gy, gx in zip(*np.nonzero(room > 8)):
        if (gx + gy) % 3:
            continue
        c = np.array([gx, gy]) * res + low
        a = np.arctan2(c[0], c[1])
        east, north = np.array([np.cos(a), -np.sin(a)]), np.array([-np.sin(a), -np.cos(a)])
        along = east * want[0] + north * want[1]
        side = -east * want[1] + north * want[0]
        pts = np.array([c + along * s * length + side * t * length for s in np.linspace(-0.5, 0.5, 13) for t in (-0.06, 0, 0.06)])
        ij = ((pts - low) / res).astype(int)
        if ij.min() < 0 or (ij[:, 0] >= size[0]).any() or (ij[:, 1] >= size[1]).any():
            continue
        clear = room[ij[:, 1], ij[:, 0]].min()
        if clear > best[0]:
            best = (clear, c)
    print('// Nombre: margen hasta la costa en el mejor lugar: %.0f.' % best[0])
    return np.array([ix, iz])[:, np.argmin(((q - best[1]) ** 2).sum(1))]


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    with open(os.path.join(MOD, 'gfx', 'FX', 'standardfuncsgfx.fxh'), encoding='utf-8-sig') as f:
        text = f.read()
    c_lat, c_lon = shader_coefficients(text, 'MdrGlobeLat'), shader_coefficients(text, 'MdrGlobeLonOffset')
    hm = np.asarray(Image.open(os.path.join(MOD, 'map', 'heightmap.bmp')))[::-1]
    land = hm >= 95
    labels = ndimage.label(land)[0]
    island = labels == labels[SEED[1], SEED[0]]

    def now(x, z):
        return np.degrees(x / W * 6.28318 + evaluate(c_lon, x, z)), np.degrees(evaluate(c_lat, x, z))

    # The map's longitude has an origin of its own: the tips say which.
    tx, tz = np.array([t[0] for t in TIPS], float), np.array([t[1] for t in TIPS], float)
    shift = np.median(np.array([t[2] for t in TIPS]) - now(tx, tz)[0])

    edge = island & ~ndimage.binary_erosion(island)
    ez, ex = np.nonzero(edge)
    ex, ez = ex.astype(float)[::3], ez.astype(float)[::3]
    elon, elat = now(ex, ez)
    src = polar(elon + shift, elat)
    outline = real_outline()
    dense = polar(outline[:, 0], outline[:, 1])
    tree = cKDTree(dense)
    tip_src = polar(now(tx, tz)[0] + shift, now(tx, tz)[1])
    tip_dst = polar(np.array([t[2] for t in TIPS]), np.array([t[3] for t in TIPS]))
    print('// Costa del mapa contra la real, antes: %.2f grados de media, %.2f el peor 1%%.' % (tree.query(src)[0].mean(), np.percentile(tree.query(src)[0], 99)))

    # Iterative closest point with a smooth warp that gets stiffer less and less, pulling both ways: each point of the map's
    # coast to the real coast and each point of the real coast to the map's, or the real coast's capes are never reached.
    # The tips hold it while it starts.
    warped = src.copy()
    warp = None
    sample = np.arange(0, len(src), 4)
    reach = dense[np.arange(0, len(dense), max(len(dense) // 500, 1))]
    for smooth in (3000.0, 3000.0, 1000.0, 1000.0, 300.0, 300.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0):
        target = dense[tree.query(warped[sample])[1]]
        back = cKDTree(warped).query(reach)[1]
        a = np.vstack([src[sample], src[back], tip_src])
        b = np.vstack([target, reach, tip_dst])
        warp = RBFInterpolator(a, b - a, kernel='thin_plate_spline', smoothing=smooth, degree=1)
        warped = src + warp(src)
    dist = tree.query(warped)[0]
    print('// Después del ajuste: %.2f grados de media, %.2f el peor 1%%.' % (dist.mean(), np.percentile(dist, 99)))

    # What the correction has to be: the warp on the island, nothing on the other land in the box, free over the sea.
    gx, gz = np.meshgrid(np.arange(BOX[0], BOX[1] + 1, 6.0), np.arange(BOX[2], min(BOX[3], H - 1), 6.0))
    gx, gz = gx.ravel(), gz.ravel()
    ix, iz = gx.astype(int), gz.astype(int)
    near = ndimage.binary_dilation(island, iterations=8)[iz, ix]
    other = land[iz, ix] & ~near
    glon, glat = now(gx, gz)
    gp = polar(glon + shift, glat)
    moved = gp + warp(gp)
    mlon, mlat = unpolar(moved)
    dlat = np.radians(mlat - glat)
    dlon = np.radians(mlon - (glon + shift))
    dlon = (dlon + np.pi) % (2 * np.pi) - np.pi
    dlat[~near], dlon[~near] = 0.0, 0.0
    # Near the pole a small move is a big change of longitude, and the island's middle is what must fit: weigh by the real size.
    weight = np.where(near, 1.0, np.where(other, 1.0, 0.04))
    A = basis(gx, gz) * window(gx, gz)[:, None]
    fit_lat = np.linalg.lstsq(A * weight[:, None], dlat * weight, rcond=None)[0]
    wlon = weight * np.cos(np.radians(glat))
    fit_lon = np.linalg.lstsq(A * wlon[:, None], dlon * wlon, rcond=None)[0]

    def fixed(x, z):
        b = basis(x, z) * window(x, z)[:, None]
        lon, lat = now(x, z)
        return lon + np.degrees(b @ fit_lon) + shift, lat + np.degrees(b @ fit_lat)

    flon, flat = fixed(ex, ez)
    final = tree.query(polar(flon, flat))[0]
    print('// Con la corrección en el shader: %.2f grados de media, %.2f el peor 1%%.' % (final.mean(), np.percentile(final, 99)))
    for t in TIPS:
        lo, la = fixed(np.array([float(t[0])]), np.array([float(t[1])]))
        print('//   punta x %d fila %d: lat %.1f lon %.1f; real lat %.1f lon %.1f' % (t[0], t[1], la[0], lo[0], t[3], t[2]))
    o = other
    print('// Otra tierra en la zona: se mueve %.2f grados de media, %.2f como máximo.' % (
        np.hypot(np.degrees(A[o] @ fit_lat), np.degrees(A[o] @ fit_lon) * np.cos(np.radians(glat[o]))).mean(),
        np.hypot(np.degrees(A[o] @ fit_lat), np.degrees(A[o] @ fit_lon) * np.cos(np.radians(glat[o]))).max()))
    # No fold: going north or east on the map must keep going that way on the globe.
    px, pz = np.meshgrid(np.arange(BOX[0], BOX[1], 8.0), np.arange(BOX[2], H - 8, 8.0))
    plon, plat = fixed(px.ravel(), pz.ravel())
    p = polar(plon, plat).reshape(px.shape + (2,))
    du, dv = np.diff(p, axis=1)[:-1], np.diff(p, axis=0)[:, :-1]
    det = du[..., 0] * dv[..., 1] - du[..., 1] * dv[..., 0]
    folded = det > 0 if np.median(det) < 0 else det < 0
    on_land = land[pz[:-1, :-1].astype(int), px[:-1, :-1].astype(int)]
    print('// Celdas dadas vuelta en la zona: %d de %d, %d sobre tierra.' % (folded.sum(), det.size, (folded & on_land).sum()))
    # The same island as an area, on a plane of the real size.
    def raster(points):
        im = Image.new('L', (1400, 1400), 0)
        ImageDraw.Draw(im).polygon(list(map(tuple, (points + [40.0, 12.0]) * 17.0)), fill=1) if len(points) else None
        return np.asarray(im, bool)

    real_area = raster(dense)
    iz2, ix2 = np.nonzero(island)
    ix2, iz2 = ix2[::2].astype(float), iz2[::2].astype(float)

    def area(lon, lat):
        q = ((polar(lon, lat) + [40.0, 12.0]) * 17.0).astype(int)
        m = np.zeros((1400, 1400), bool)
        m[q[:, 1], q[:, 0]] = True
        return ndimage.binary_closing(m, iterations=2)

    blon, blat = now(ix2, iz2)
    before, after = area(blon + shift, blat), area(*fixed(ix2, iz2))
    print('// Superficie en común con la real (1 es perfecto): antes %.3f, después %.3f.' % (
        (before & real_area).sum() / (before | real_area).sum(), (after & real_area).sum() / (after | real_area).sum()))
    print('// Coeficiente mayor: %.3f.' % max(np.abs(fit_lat).max(), np.abs(fit_lon).max()))
    print()

    def emit(c):
        n = 0
        terms = []
        for i in range(DEGREE + 1):
            for j in range(DEGREE + 1 - i):
                terms.append('%.5ff * cu%d * cv%d' % (c[n], i, j))
                n += 1
        return ' + '.join(terms).replace('+ -', '- ')

    print('\t// Generated by herramientas/globo_groenlandia.py: what Greenland needs on top of those two (radians): latitude, longitude.')
    print('\tfloat2 MdrGlobeGreenland( float x, float z )')
    print('\t{')
    print('\t\tx = fmod_loop( x / MAP_SIZE_X, 1.0f ) * MAP_SIZE_X;')
    print('\t\tif( x <= %.1ff || x >= %.1ff || z <= %.1ff )' % (BOX[0], BOX[1], BOX[2]))
    print('\t\t\treturn float2( 0.0f, 0.0f );')
    print('\t\tfloat vWindow = smoothstep( %.1ff, %.1ff, x ) * ( 1.0f - smoothstep( %.1ff, %.1ff, x ) ) * smoothstep( %.1ff, %.1ff, z ) * ( 1.0f - smoothstep( %.1ff, %.1ff, z ) );' % (
        BOX[0], BOX[0] + FADE, BOX[1] - FADE, BOX[1], BOX[2], BOX[2] + FADE, BOX[3] - FADE, BOX[3]))
    print('\t\tfloat u = ( 2.0f * x - %.1ff ) / %.1ff;' % (BOX[0] + BOX[1], BOX[1] - BOX[0]))
    print('\t\tfloat v = ( 2.0f * z - %.1ff ) / %.1ff;' % (BOX[2] + BOX[3], BOX[3] - BOX[2]))
    print('\t\tfloat cu0 = 1.0f;')
    print('\t\tfloat cv0 = 1.0f;')
    print('\t\tfloat cu1 = u;')
    print('\t\tfloat cv1 = v;')
    for i in range(2, DEGREE + 1):
        print('\t\tfloat cu%d = 2.0f * u * cu%d - cu%d;' % (i, i - 1, i - 2))
        print('\t\tfloat cv%d = 2.0f * v * cv%d - cv%d;' % (i, i - 1, i - 2))
    print('\t\tfloat vLat = ' + emit(fit_lat) + ';')
    print('\t\tfloat vLon = ' + emit(fit_lon) + ';')
    print('\t\treturn float2( vLat, vLon ) * vWindow;')
    print('\t}')

    # The name. On the globe a column at this latitude is much narrower than on the map, so the letters squeeze and shear into a
    # band. Undoing what the globe does where the text goes, for the vertices of that text alone, leaves them upright.
    step = 8.0
    base = np.array(NAME_BASELINE) / np.hypot(*NAME_BASELINE)
    want = np.array([np.cos(np.radians(NAME_ANGLE)), np.sin(np.radians(NAME_ANGLE))])
    # The rotation that takes the map's baseline to the slant it has on the globe.
    Q = np.array([[want[0] * base[0] + want[1] * base[1], want[0] * base[1] - want[1] * base[0]],
                  [want[1] * base[0] - want[0] * base[1], want[0] * base[0] + want[1] * base[1]]])
    B = NAME_SCALE * Q
    radius = W / 6.28318

    def seen(p):
        lon, lat = fixed(np.array([p[0]]), np.array([p[1]]))
        return polar(lon, lat)[0] * np.pi / 180 * radius

    # Where on the map each point of the straight text must be, found by turning the globe's own position around: the map is
    # not regular here, and one width per latitude still left letters almost twice as wide as others.
    target = name_spot(island, fixed, want, NAME_SCALE * np.hypot(*NAME_BASELINE), radius)
    centre = seen(target)
    east = seen(target + [step, 0]) - seen(target - [step, 0])
    east /= np.hypot(*east)
    north = seen(target + [0, step]) - seen(target - [0, step])
    north -= east * (north @ east)
    north /= np.hypot(*north)

    def solve(g):
        p = target.copy()
        goal = centre + east * g[0] + north * g[1]
        for _ in range(12):
            jac = np.column_stack([(seen(p + [step, 0]) - seen(p - [step, 0])) / (2 * step), (seen(p + [0, step]) - seen(p - [0, step])) / (2 * step)])
            move = np.linalg.lstsq(jac, goal - seen(p), rcond=None)[0]
            p = p + move * min(1.0, 60.0 / max(np.hypot(*move), 1e-6))  # short steps: a long one leaves the map, where nothing changes
            p[1] = min(p[1], H - 2 * step)
        return p

    length = NAME_SCALE * np.hypot(*NAME_BASELINE)
    points, spots = [], []
    for a in np.linspace(-0.62, 0.62, 25):
        for b in np.linspace(-0.2, 0.2, 7):
            g = want * a * length + np.array([-want[1], want[0]]) * b * length
            points.append(g)
            spots.append(solve(g))
    points, spots = np.array(points), np.array(spots)
    powers = [(i, j) for i in range(NAME_DEGREE + 1) for j in range(NAME_DEGREE + 1 - i)]

    def monomials(g):
        return np.stack([(g[..., 0] / 150.0) ** i * (g[..., 1] / 150.0) ** j for i, j in powers], -1)

    fit_x = np.linalg.lstsq(monomials(points), spots[:, 0], rcond=None)[0]
    fit_z = np.linalg.lstsq(monomials(points), spots[:, 1], rcond=None)[0]

    def placed(d):
        m = monomials(B @ d)
        return np.array([m @ fit_x, m @ fit_z])

    along = np.array(NAME_BASELINE, float)
    up = np.array([-base[1], base[0]]) * 20.0
    widths, tall = [], []
    for k in np.linspace(-0.5, 0.45, 20):
        widths.append(np.hypot(*(seen(placed(along * (k + 0.05))) - seen(placed(along * k)))) / (NAME_SCALE * 0.05 * np.hypot(*along)))
        tall.append(np.hypot(*(seen(placed(along * k + up)) - seen(placed(along * k)))) / (NAME_SCALE * 20.0))
    print('// Nombre: en el globo mide %.0f de largo; ancho de sus letras entre %.2f y %.2f, alto entre %.2f y %.2f (1 es sin deformar).' % (
        NAME_SCALE * np.hypot(*along), min(widths), max(widths), min(tall), max(tall)))
    ends = [placed(along * k) for k in (-0.5, 0.5)]
    print('// Nombre: sus puntas caen en x %.0f, fila %.0f y x %.0f, fila %.0f; %s tierra.' % (
        ends[0][0], ends[0][1], ends[1][0], ends[1][1], 'las dos sobre' if all(island[int(e[1]), int(e[0])] for e in ends) else 'alguna fuera de'))
    print()
    print('\t// Generated by herramientas/globo_groenlandia.py: the text over the island, in a box that nothing else reaches.')
    print('\tfloat MdrGlobeInGreenlandName( float x, float z )')
    print('\t{')
    print('\t\tx = fmod_loop( x / MAP_SIZE_X, 1.0f ) * MAP_SIZE_X;')
    print('\t\treturn ( x > %.1ff && x < %.1ff && z > %.1ff && z < %.1ff ) ? 1.0f : 0.0f;' % NAME_BOX)
    print('\t}')
    print()
    print('\t// Generated by herramientas/globo_groenlandia.py: undoes what the globe does to the letters of that text. vShare is 0 on the flat map.')
    print('\tfloat2 MdrGlobeGreenlandName( float2 vPos, float vShare )')
    print('\t{')
    print('\t\tif( vShare <= 0.0f || MdrGlobeInGreenlandName( vPos.x, vPos.y ) < 0.5f )')
    print('\t\t\treturn vPos;')
    print('\t\tfloat vX = fmod_loop( vPos.x / MAP_SIZE_X, 1.0f ) * MAP_SIZE_X;')
    print('\t\tfloat2 d = float2( vX - %.1ff, vPos.y - %.1ff );' % NAME_CENTER)
    print('\t\tfloat2 g = float2( %.5ff * d.x + %.5ff * d.y, %.5ff * d.x + %.5ff * d.y );' % (B[0, 0], B[0, 1], B[1, 0], B[1, 1]))
    print('\t\tfloat u = g.x / 150.0f;')
    print('\t\tfloat v = g.y / 150.0f;')

    def poly(c):
        terms = []
        for k, (i, j) in zip(c, powers):
            terms.append(' * '.join(['%.4ff' % k] + ['u'] * i + ['v'] * j))
        return ' + '.join(terms).replace('+ -', '- ')

    print('\t\tfloat vNewX = ' + poly(fit_x) + ';')
    print('\t\tfloat vNewZ = ' + poly(fit_z) + ';')
    print('\t\treturn vPos + vShare * float2( vNewX - vX, vNewZ - vPos.y );')
    print('\t}')
    print()

    if len(sys.argv) > 1:
        size, scale = 1100, 26.0
        img = Image.new('RGB', (size, size), (10, 20, 40))
        d = ImageDraw.Draw(img)

        def screen(p):
            return size / 2 + (p[..., 0]) * scale, size / 2 + (p[..., 1] - 18.0) * scale

        rx, ry = screen(dense)
        d.polygon(list(zip(rx, ry)), fill=(50, 110, 70))
        qx, qy = screen(polar(flon, flat))
        for a, b in zip(qx, qy):
            d.ellipse((a - 1, b - 1, a + 1, b + 1), fill=(255, 240, 90))
        img.save(sys.argv[1])


if __name__ == '__main__':
    main()
