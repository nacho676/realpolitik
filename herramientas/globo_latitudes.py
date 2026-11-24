"""Where each point of the map really is on Earth, for the globe shader (MdrGlobeLat and MdrGlobeLonOffset in
gfx/FX/standardfuncsgfx.fxh).

Millennium Dawn's map is not a regular projection: its top edge is 63 N in Canada and much higher in Russia, so one latitude
per row deforms the north. This fits latitude and longitude as functions of both map coordinates, from the same calibration
that builds the Arctic (construir_mapa.py), and prints the shader functions. Run it again if the map changes.

    python herramientas/globo_latitudes.py
"""
import os
import sys

import numpy as np
from numpy.polynomial.chebyshev import chebvander

import construir_mapa as cm
from construir_mapa import Projection, choose_transform, control_points

DEGREE_Z = 13    # Chebyshev polynomials of the row
HARMONICS = 8    # waves around the map
GRID = 1.5


def basis(u, v):
    """Columns: every Chebyshev polynomial of the row with every wave of the column. Powers of the row would need
    coefficients in the millions, and the shader's 32-bit floats lose whole degrees with those."""
    cheb = chebvander(2 * v - 1, DEGREE_Z)
    cols = []
    for i in range(DEGREE_Z + 1):
        p = cheb[:, i]
        cols.append(p)
        for h in range(1, HARMONICS + 1):
            cols.append(p * np.cos(2 * np.pi * h * u))
            cols.append(p * np.sin(2 * np.pi * h * u))
    return np.column_stack(cols)


def samples(md):
    rep = []
    x, z, lon, lat = [], [], [], []
    for south, lats in ((False, np.arange(30.0, cm.LAT_TOP + 0.01, GRID)), (True, np.arange(-20.0, -90.01, -GRID))):
        proj = Projection(choose_transform(*control_points(md, rep, south), rep, south), south)
        lons = np.arange(cm.LON_CUT, cm.LON_CUT + 360.0, GRID)
        ll = np.array([(a, b) for a in lons for b in lats])
        q = proj(ll)
        x.append(q[:, 0]); z.append(q[:, 1]); lon.append(ll[:, 0]); lat.append(ll[:, 1])
    # In between, the cities of the map themselves.
    import json
    with open(os.path.join(cm.DATA, 'ne_10m_populated_places_simple.geojson'), encoding='utf-8') as f:
        places = json.load(f)['features']
    by_name = {}
    for ft in places:
        p = ft['properties']
        for n in {p['name'], p['nameascii']}:
            if n:
                by_name.setdefault(cm.norm_name(n), []).append((p['longitude'], p['latitude']))
    cx, cz, clon, clat = [], [], [], []
    for _, name, px, pz in md.victory_points():
        cands = by_name.get(cm.norm_name(name))
        if not cands:
            continue
        a, b = min(cands, key=lambda c: abs((c[0] + 180) * cm.W / 360 - px))
        if abs((a + 180) * cm.W / 360 - px) < 120 and -25 < b < 35:
            cx.append(px); cz.append(pz); clon.append(a); clat.append(b)
    return (np.concatenate(x), np.concatenate(z), np.concatenate(lon), np.concatenate(lat),
            np.array(cx), np.array(cz), np.array(clon), np.array(clat))


def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi


def emit(name, c, comment):
    print('\t// ' + comment)
    print('\tfloat %s( float x, float z )' % name)
    print('\t{')
    print('\t\tfloat v = saturate( z / MAP_SIZE_Y );')
    print('\t\tfloat a = x / MAP_SIZE_X * 6.28318f;')
    names = []
    print('\t\tfloat c1 = cos( a );')
    print('\t\tfloat s1 = sin( a );')
    names += ['c1', 's1']
    for h in range(2, HARMONICS + 1):
        print('\t\tfloat c%d = c%d * c1 - s%d * s1;' % (h, h - 1, h - 1))
        print('\t\tfloat s%d = s%d * c1 + c%d * s1;' % (h, h - 1, h - 1))
        names += ['c%d' % h, 's%d' % h]
    n = 1 + 2 * HARMONICS
    print('\t\tfloat t = 2.0f * v - 1.0f;')
    print('\t\tfloat b1 = 0.0f;')
    print('\t\tfloat b2 = 0.0f;')
    print('\t\tfloat n = 0.0f;')

    def row(i):
        r = c[i * n:(i + 1) * n]
        terms = ['%.6ff' % r[0]] + ['%.6ff * %s' % (k, m) for k, m in zip(r[1:], names)]
        return ' + '.join(terms).replace('+ -', '- ')

    for i in range(DEGREE_Z, 0, -1):
        print('\t\tn = 2.0f * t * b1 - b2 + ' + row(i) + ';')
        print('\t\tb2 = b1;')
        print('\t\tb1 = n;')
    print('\t\treturn t * b1 - b2 + ' + row(0) + ';')
    print('\t}')
    print()


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    md = cm.MD(os.path.abspath(os.path.join(cm.MOD, '..', 'Millennium-Dawn-2.0.0')))
    x, z, lon, lat, cx, cz, clon, clat = samples(md)
    keep = (z + cm.SOUTH >= 0) & (z + cm.SOUTH <= cm.TOTAL)
    x, z, lon, lat = x[keep], z[keep], lon[keep], lat[keep]

    X = np.concatenate([x, cx])
    V = (np.concatenate([z, cz]) + cm.SOUTH) / cm.TOTAL
    U = (X % cm.W) / cm.W
    LON = np.radians(np.concatenate([lon, clon]))
    LAT = np.radians(np.concatenate([lat, clat]))
    W = np.concatenate([np.ones(len(x)), np.full(len(cx), 3.0)])

    # The bottom row closes on the south pole; the top row is 85 N at every longitude (the sphere behind the map, in
    # sky.shader, shows through the rest of the way to the pole).
    ue = np.linspace(0, 1, 200, endpoint=False)
    ends = 60.0
    A = basis(np.concatenate([U, ue, ue]), np.concatenate([V, np.ones(200), np.zeros(200)]))
    y = np.concatenate([LAT, np.full(200, np.radians(cm.LAT_TOP)), np.full(200, -np.pi / 2)])
    w = np.concatenate([W, np.full(400, ends)])
    c_lat = np.linalg.lstsq(A * w[:, None], y * w, rcond=None)[0]

    # Longitude: the regular part is the column itself; this fits what the map adds to it.
    off = wrap(LON - 2 * np.pi * U)
    mean = np.arctan2(np.sin(off).mean(), np.cos(off).mean())
    off = wrap(off - mean)
    B = basis(U, V)
    c_lon = np.linalg.lstsq(B * W[:, None], off * W, rcond=None)[0]

    err_lat = np.degrees(np.abs(basis(U, V) @ c_lat - LAT))
    err_lon = np.degrees(np.abs(wrap(basis(U, V) @ c_lon - off)))
    print('// Muestras: %d. Error de latitud: media %.2f, p99 %.2f. Error de longitud: media %.2f, p99 %.2f (grados).'
          % (len(U), err_lat.mean(), np.percentile(err_lat, 99), err_lon.mean(), np.percentile(err_lon, 99)))
    uu, vv = np.meshgrid(np.linspace(0, 1, 64, endpoint=False), np.linspace(0, 1, 400))
    grid = (basis(uu.ravel(), vv.ravel()) @ c_lat).reshape(vv.shape)
    print('// Filas donde la latitud baja al subir (debería ser casi 0): %.2f%%; rango %.1f a %.1f.'
          % (100 * (np.diff(grid, axis=0) < 0).mean(), np.degrees(grid.min()), np.degrees(grid.max())))
    north = np.degrees(LAT) > 60
    print('// Error de latitud al norte de 60: media %.2f, p99 %.2f. De longitud: media %.2f, p99 %.2f.'
          % (err_lat[north].mean(), np.percentile(err_lat[north], 99), err_lon[north].mean(), np.percentile(err_lon[north], 99)))
    for name, (u, r) in {'Canada norte': (0.20, 2100), 'Rusia norte': (0.72, 2100), 'Europa': (0.52, 1650)}.items():
        print('// %s (fila %d): latitud %.1f' % (name, r, np.degrees((basis(np.array([u]), np.array([r / cm.TOTAL])) @ c_lat)[0])))
    # What the shader's 32-bit floats do with it (Clenshaw, like the emitted code).
    def shader(u, v, c):
        n = 1 + 2 * HARMONICS
        t = np.float32(2 * v - 1)
        a = np.float32(u * 6.28318)
        wave = [np.ones_like(a)]
        for h in range(1, HARMONICS + 1):
            wave += [np.cos(np.float32(h) * a), np.sin(np.float32(h) * a)]
        rows = [sum(np.float32(c[i * n + j]) * wave[j] for j in range(n)) for i in range(DEGREE_Z + 1)]
        b1, b2 = np.zeros_like(t), np.zeros_like(t)
        for i in range(DEGREE_Z, 0, -1):
            b1, b2 = np.float32(2) * t * b1 - b2 + rows[i], b1
        return t * b1 - b2 + rows[0]
    uu32, vv32 = uu.ravel().astype(np.float32), vv.ravel().astype(np.float32)
    print('// Coeficiente mayor: %.3f. Error en 32 bits: %.4f grados en latitud, %.4f en longitud.'
          % (max(np.abs(c_lat).max(), np.abs(c_lon).max()),
             np.degrees(np.abs(shader(uu32, vv32, c_lat) - basis(uu.ravel(), vv.ravel()) @ c_lat).max()),
             np.degrees(np.abs(shader(uu32, vv32, c_lon) - basis(uu.ravel(), vv.ravel()) @ c_lon).max())))
    print()
    emit('MdrGlobeLat', c_lat, 'Generated by herramientas/globo_latitudes.py: map position to latitude (radians).')
    emit('MdrGlobeLonOffset', c_lon, 'Generated by herramientas/globo_latitudes.py: what the map adds to the longitude of its column (radians).')


if __name__ == '__main__':
    main()
