"""Adds the missing Arctic and Antarctica to Millennium Dawn's map for Realpolitik.

Run it again after each Millennium Dawn update, so the map never falls behind:
    python herramientas/construir_mapa.py vista-previa   # calibration and previews only
    python herramientas/construir_mapa.py construir      # builds every file in the staging folder and checks it
    python herramientas/construir_mapa.py instalar       # builds, checks and, if all is right, copies it into the mod
Nothing is written in the mod unless every check passes; the files it replaces are copied to the staging folder first.

Millennium Dawn's map stops at a straight line in the north (z = 2047) and in the south (z = 0). This tool projects
the real coasts of Natural Earth (public domain, herramientas/artico/datos/) onto MD's own distorted projection and
adds NORTH rows above and SOUTH rows below. Every MD coordinate moves up by SOUTH. MD's pixels stay identical except
where the real Siberian coast is carved out of MD's last rows. The states, victory points and sea regions come
from herramientas/artico/estados.txt. Why the map cannot be taller: herramientas/artico/limite_mapa.md.
The new land's relief and colours come from NOAA's ETOPO 2022 and NASA's Blue Marble (credit: NASA Earth
Observatory), both in herramientas/artico/datos/, turned into MD's own style with MD's land next to each edge.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata

import numpy as np
from PIL import Image, ImageDraw
from scipy.cluster.vq import kmeans2
from scipy.interpolate import RBFInterpolator
from scipy.ndimage import (binary_dilation, binary_erosion, binary_opening, distance_transform_edt, find_objects,
                           gaussian_filter, gaussian_filter1d, label, map_coordinates, zoom)
from shapely.geometry import box, shape

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.dirname(HERE)
GAME = __import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/")
DATA = os.path.join(HERE, 'artico', 'datos')
W, H = 5632, 2048   # MD's map, checked on load
# HOI4 builds a 4-byte-per-pixel terrain texture in a fixed 50 MB buffer (pdxmaptexturegeneration.cpp): with MD's
# width the map can be at most 2327 rows tall, or the game crashes while loading. The height must also be a multiple
# of 64 ("Topology texture width and height must both be factors of 64"), so 2048 + 256 = 2304 is the largest.
NORTH, SOUTH = 184, 72  # rows added above and below MD's map
TOP = H + NORTH     # MD-coordinate z of the top row + 1 (the north canvas)
TOTAL = TOP + SOUTH
LAT_TOP = 85.0      # latitude that reaches the top row (some sea above the tips of Greenland and Ellesmere)
LAT_BOTTOM = -90.0  # latitude of the bottom row
MAX_TERRAIN_BUFFER = 50 * 1024 * 1024
Z0 = 1500           # lowest MD row used to fit the coasts
SEAM = 16           # rows above the edge where MD's last row turns into the real coast
DECAY = 90.0        # rows over which the coast fit fades out north of the edge
LON_CUT = -169.0    # MD's map wraps in the Bering Strait: longitudes west of it go to the east end
RUSSIA_LON = 30.0   # east of it the new rows follow the real coast and MD land that is really sea is carved out
CARVE_ROWS, CARVE_OPEN, CARVE_KEEP = 220, 4, 0.35
FILL_COLS, FILL_ROWS = 100, 60  # near the Bering wrap, MD sea that is really land (MD splits Chukotka) becomes land
FILL_KEEP = 40      # smaller pieces of sea the fill leaves of an MD sea province are filled too
COAST_STRIP = 40    # in the Russian sector, new land at most this tall above MD's edge goes to MD's province below
NORMAL_K = 5.47     # MD's world_normal: R = 127 - k * dh/dx, G = 127 + k * dh/dy (half-size heights)
EDGE_TAPER = 6      # MD's land heights slope down in its last rows at the north edge: they keep the height below
EDGE_NORMAL_ROWS = 4  # MD's last normal rows at the north edge are tilted by that slope: drawn again
BRIDGE_GAP, BRIDGE_ROWS = 40, 8  # MD sea runs this short between land of one MD state get land this tall above
MIN_ISLAND = 40     # smaller islands are left out (too small for a province)
MIN_LAKE = 300      # smaller enclosed water becomes land
LAND_SIZE, ICE_SIZE = 900, 2500           # target province area in pixels
ANTARCTIC_SIZE = 9000                     # Antarctica's ice: few, big provinces
SEA_SIZE, OCEAN_SIZE, OCEAN_DIST = 2500, 6000, 60  # MD's sea provinces near the north edge: about 2500 to 2900
EDGE_CAP = 24       # rows at most that an MD province on the edge grows into the new band
ARCTIC_TERRAIN = 'mdr_arctic'             # terrain of new land provinces in definition.csv
WHOLE_ISLAND = 15000                      # islands smaller than this go whole to the state holding most of them
# Tundra and ice: slow, narrow fronts, high attrition, no deep fortifications. Icon: interface/mdr_arctic.gfx.
ARCTIC_CATEGORY = '''
	mdr_arctic = {
		color = { 225 235 250 }
		movement_cost = 1.8
		attrition = 0.4
		combat_width = 100
		combat_support_width = 50
		ai_terrain_importance_factor = 2.0
		match_value = 3
		sound_type = plains
		buildings_max_level = {
			bunker = 1
			coastal_bunker = 1
		}

		units = {
			attack = -0.25
			defence = 0.1
			movement = -0.3
		}

		supply_flow_penalty_factor = 0.2

		truck_attrition_factor = 1.0
	}
'''
SEA_HEIGHT, LAND_HEIGHT = 88, 97          # heightmap values MD uses at the edge
ETOPO_NORTH, ETOPO_SOUTH = 'etopo_norte.npz', 'etopo_sur.npz'  # NOAA ETOPO 2022, ice surface, 4 arc-minutes
BLUE_MARBLE = 'blue_marble_200407.jpg'    # NASA Blue Marble Next Generation, July 2004, 5400 x 2700
CAL_ROWS = 250      # MD rows next to each edge whose land sets the style (heights, colours) of the new land
MOUNTAIN_RELIEF, HILL_RELIEF = 150.0, 60.0  # local spread of the real heights (metres) for mountains and hills
SECTORS = [(-169, -100, 'Alaska y oeste de Canadá'), (-100, -60, 'este de Canadá'), (-60, -10, 'Groenlandia'),
           (-10, 60, 'Escandinavia y Barents'), (60, 120, 'Siberia occidental y Taimyr'),
           (120, 191, 'Siberia oriental y Chukotka')]
CROPS = [(0, 1000, 'alaska'), (900, 1900, 'canada'), (1850, 2850, 'groenlandia'), (2800, 3800, 'barents'),
         (3700, 4700, 'taimyr'), (4600, 5632, 'chukotka')]
LAND_STACKS = (0, 1, 2, 3, 4, 5, 9, 10, 21, 22, 23, 24, 25, 26, 38)
SEA_STACKS = (0, 1, 2, 3, 4, 5, 9, 10, 11, 12, 13, 14, 15, 21, 22, 23, 24, 25, 26, 30, 31, 32, 33, 34, 38)
STATE_BUILDINGS = ['industrial_complex'] * 6 + ['arms_factory'] * 6 + [
    'synthetic_refinery', 'stronghold_network', 'rocket_site_spawn', 'mdr_spaceport_spawn', 'renewable_energy_infra', 'radar_station',
    'nuclear_reactor_spawn', 'nuclear_reactor', 'internet_station', 'fuel_silo', 'fossil_powerplant',
    'anti_air_building', 'air_base']
PROVINCE_BUILDINGS = ['bunker', 'supply_node', 'special_project_facility_spawn']
COAST_BUILDINGS = ['naval_supply_hub', 'coastal_bunker', 'naval_base_spawn', 'floating_harbor']
IMAGES = ['provinces', 'heightmap', 'terrain', 'rivers', 'cities', 'trees', 'world_normal']
HALF = ('trees', 'world_normal')
COLORMAPS = ['colormap_rgb_cityemissivemask_a', 'colormap_water_0']
# MD files with map coordinates: (file, separator, x field, z field); the z of each one moves up by SOUTH
COORD_FILES = [('unitstacks.txt', 2, 4), ('buildings.txt', 2, 4), ('weatherpositions.txt', 1, 3)]


def key_of(rgb):
    rgb = rgb.astype(np.int32)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def unwrap(lon):
    return np.where(lon < LON_CUT, lon + 360.0, lon)


def norm_name(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z]', '', s)


def z_of(r):
    """z of a row of the enlarged map (row 0 is the top)."""
    return TOTAL - 1 - r


def half(mask):
    return mask.reshape(mask.shape[0] // 2, 2, mask.shape[1] // 2, 2).mean((1, 3)) > 0.5


# ---------------------------------------------------------------- Millennium Dawn's map

class MD:
    def __init__(self, path):
        self.path = path
        self.prov = np.asarray(Image.open(self.file('map', 'provinces.bmp')).convert('RGB'))
        if self.prov.shape[:2] != (H, W):
            raise SystemExit('provinces.bmp de MD no mide %d x %d' % (W, H))
        self.key = key_of(self.prov)
        self.types, self.ids, self.continent = {}, {}, {}
        with open(self.file('map', 'definition.csv'), encoding='latin-1') as f:
            for line in f:
                p = line.strip().split(';')
                if len(p) > 7 and p[0].isdigit():
                    k = (int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])
                    self.ids[k] = int(p[0])
                    if p[0] != '0':
                        self.types[k] = p[4]
                        self.continent[int(p[0])] = int(p[7])
        self.max_province = max(self.ids.values())
        self.land = np.isin(self.key, [c for c, t in self.types.items() if t in ('land', 'lake')])
        self.landtype = np.isin(self.key, [c for c, t in self.types.items() if t == 'land'])
        self.sea = np.isin(self.key, [c for c, t in self.types.items() if t == 'sea'])
        u, inv = np.unique(self.key, return_inverse=True)
        self.idmap = np.array([self.ids.get(int(c), 0) for c in u], np.int32)[inv].reshape(self.key.shape)
        self.type_of = {self.ids[k]: t for k, t in self.types.items()}
        self.pos = {}
        with open(self.file('map', 'unitstacks.txt'), encoding='utf-8-sig') as f:
            for line in f:
                p = line.strip().split(';')
                if len(p) >= 5 and p[1] == '0':
                    self.pos[int(p[0])] = (float(p[2]), float(p[4]))
        self.max_state = max(int(re.match(r'\d+', n).group()) for n in os.listdir(self.file('history', 'states'))
                             if re.match(r'\d+', n))
        self.max_region = max(int(re.match(r'\d+', n).group())
                              for n in os.listdir(self.file('map', 'strategicregions')) if re.match(r'\d+', n))

    def file(self, *parts):
        return os.path.join(self.path, *parts)

    def coastal(self):
        """MD land provinces that touch the sea on MD's own map."""
        ids = self.idmap
        out = set()
        for a, b in ((ids[:, :-1], ids[:, 1:]), (ids[:-1], ids[1:]), (ids[:, -1:], ids[:, :1])):
            m = a != b
            for p, q in set(zip(a[m].tolist(), b[m].tolist())):
                if self.type_of.get(p) == 'land' and self.type_of.get(q) == 'sea':
                    out.add(p)
                if self.type_of.get(q) == 'land' and self.type_of.get(p) == 'sea':
                    out.add(q)
        return out

    def states_of_provinces(self):
        out = {}
        for n in os.listdir(self.file('history', 'states')):
            with open(self.file('history', 'states', n), encoding='utf-8-sig', errors='replace') as f:
                t = f.read()
            m = re.search(r'\bid\s*=\s*(\d+)', t)
            if not m:
                continue
            for x in re.search(r'provinces\s*=\s*\{([^}]*)\}', t).group(1).split():
                out[int(x)] = int(m.group(1))
        return out

    def victory_points(self):
        out = []
        with open(self.file('localisation', 'english', 'victory_points_l_english.yml'), encoding='utf-8-sig') as f:
            for line in f:
                m = re.match(r'\s*VICTORY_POINTS_(\d+):\d*\s*"([^"]*)"', line)
                if m and int(m.group(1)) in self.pos:
                    out.append((int(m.group(1)), m.group(2)) + self.pos[int(m.group(1))])
        return out


# ---------------------------------------------------------------- Our Arctic and Antarctic data

def parse_zone(text):
    polys = []
    for part in text.split('|'):
        lon1, lat1, lon2, lat2 = map(float, part.split())
        polys.append(box(lon1, lat1, lon2, lat2))
    return polys


def is_south(zone):
    return all(p.bounds[3] <= 0 for p in zone)


def load_data():
    states, vps, regions, seas = [], [], [], []
    with open(os.path.join(HERE, 'artico', 'estados.txt'), encoding='utf-8') as f:
        for n, line in enumerate(f, 1):
            line = line.split('#')[0].strip()
            if not line:
                continue
            p = [x.strip() for x in line.split(';')]
            kind = p[0]
            if kind == 'estado' and len(p) in (8, 9):
                opts = p[8].split() if len(p) == 9 else []
                cores = [c for o in opts if o.startswith('núcleos=') for c in o.split('=')[1].split(',')]
                claims = [c for o in opts if o.startswith('reclamos=') for c in o.split('=')[1].split(',')]
                zone = parse_zone(p[7])
                states.append(dict(name=p[1], owner=None if p[2] == '-' else p[2], category=p[3],
                                   manpower=int(p[4]), en=p[5], es=p[6],
                                   zone=zone, south=is_south(zone), impassable='intransitable' in opts,
                                   cores=([p[2]] if p[2] != '-' else []) + cores, claims=claims,
                                   mass=[tuple(map(float, o.split('=')[1].split(','))) for o in opts
                                         if o.startswith('masa=')][:1],
                                   annex='anexo' in opts,
                                   coast=[(int(o.split('=')[1].split(':')[0]), o.split(':')[1]) for o in opts
                                          if o.startswith('costa=')][:1]))
            elif kind == 'vp' and len(p) == 6:
                lon, lat = map(float, p[4].split())
                vps.append(dict(state=p[1], en=p[2], es=p[3], lon=lon, lat=lat, points=int(p[5])))
            elif kind == 'region' and len(p) == 5:
                regions.append(dict(name=p[1], en=p[2], es=p[3], states=p[4].split()))
            elif kind == 'mar' and len(p) == 6:
                zone = parse_zone(p[5])
                seas.append(dict(name=p[1], naval=p[2], en=p[3], es=p[4], zone=zone, south=is_south(zone)))
            else:
                raise SystemExit('estados.txt, línea %d: no la entiendo: %s' % (n, line))
    names = {s['name'] for s in states}
    for v in vps:
        if v['state'] not in names:
            raise SystemExit('estados.txt: punto de victoria de un estado que no existe: %s' % v['state'])
    in_regions = [s for r in regions for s in r['states']]
    for s in names:
        if in_regions.count(s) != 1:
            raise SystemExit('estados.txt: el estado %s tiene que estar en una sola región' % s)
    return states, vps, regions, seas


# ---------------------------------------------------------------- Calibration: (lon, lat) -> MD's (x, z)

def control_points(md, rep, south):
    """MD's victory points whose name matches a Natural Earth city north of 40 degrees (or south of 20 degrees S)."""
    with open(os.path.join(DATA, 'ne_10m_populated_places_simple.geojson'), encoding='utf-8') as f:
        places = json.load(f)['features']
    by_name = {}
    for ft in places:
        p = ft['properties']
        if (p['latitude'] < -20) if south else (p['latitude'] > 40):
            for n in {p['name'], p['nameascii']}:
                if n:
                    by_name.setdefault(norm_name(n), []).append((p['longitude'], p['latitude']))
    P, Q = [], []
    for _, name, x, z in md.victory_points():
        cands = by_name.get(norm_name(name))
        if not cands:
            continue
        lon, lat = min(cands, key=lambda c: abs((c[0] + 180) * W / 360 - x))
        if abs((lon + 180) * W / 360 - x) < 120:
            lon = float(unwrap(lon))
            if lon > 180 and x < W / 2:
                x += W
            P.append((lon, lat))
            Q.append((x, z))
    P, Q = np.array(P), np.array(Q)
    side = 'al sur de 20° S' if south else 'al norte de 40°'
    rep.append('Puntos de control (%s): %d ciudades de MD con el mismo nombre en Natural Earth.' % (side, len(P)))
    for _ in range(5):
        r = np.linalg.norm(fit(('tps', 2000.0), P, Q)(P) - Q, axis=1)
        bad = r > max(60.0, 4 * np.median(r))
        if not bad.any():
            break
        P, Q = P[~bad], Q[~bad]
    rep.append('Quedan %d después de quitar los que no encajan (mismo nombre, otro lugar).' % len(P))
    return P, Q


def poly_features(P, deg):
    u = (P[:, 0] - 11.0) / 180.0
    v = (P[:, 1] - 60.0) / 30.0
    return np.column_stack([u ** i * v ** j for i in range(deg + 1) for j in range(deg + 1 - i)])


def fit(kind, P, Q):
    if kind[0] == 'tps':
        return RBFInterpolator(P, Q, kernel='thin_plate_spline', smoothing=kind[1], degree=1)
    if kind[0] == 'poly':
        c = np.linalg.lstsq(poly_features(P, kind[1]), Q, rcond=None)[0]
        return lambda X: poly_features(np.asarray(X, float), kind[1]) @ c
    # one affine per longitude sector
    fits = []
    for a, b, _ in SECTORS:
        m = (P[:, 0] >= a) & (P[:, 0] < b)
        fits.append(np.linalg.lstsq(poly_features(P[m], 1), Q[m], rcond=None)[0] if m.sum() >= 6 else None)

    def f(X):
        X = np.asarray(X, float)
        out = np.zeros((len(X), 2))
        for i, (a, b, _) in enumerate(SECTORS):
            c = fits[i] if fits[i] is not None else next(c for c in fits if c is not None)
            m = (X[:, 0] >= a) & (X[:, 0] < b) if 0 < i < len(SECTORS) - 1 else \
                ((X[:, 0] < b) if i == 0 else (X[:, 0] >= a))
            out[m] = poly_features(X[m], 1) @ c
        return out
    return f


CANDIDATES = [('sectors',), ('poly', 2), ('poly', 3), ('tps', 200.0), ('tps', 1000.0), ('tps', 5000.0),
              ('tps', 20000.0)]


def kind_name(k):
    return {'sectors': 'afín por sector', 'poly': 'polinómica de grado %s', 'tps': 'placa delgada, suavizado %s'}[
        k[0]].replace('%s', str(int(k[1])) if len(k) > 1 else '')


def choose_transform(P, Q, rep, south):
    """5-fold cross-validation: each candidate is scored on cities it did not see."""
    folds = np.random.default_rng(0).permutation(len(P)) % 5
    far = P[:, 1] < -40 if south else P[:, 1] > 60
    rep.append('Error de validación cruzada (en píxeles, con ciudades que no se usaron para ajustar):')
    rep.append('  %-34s %8s %8s %18s' % ('transformación', 'media', 'p90', 'media cerca del borde'))
    best = None
    for k in CANDIDATES:
        err = np.zeros(len(P))
        for i in range(5):
            tr = folds != i
            err[~tr] = np.linalg.norm(fit(k, P[tr], Q[tr])(P[~tr]) - Q[~tr], axis=1)
        edge = err[far].mean() if far.any() else err.mean()
        score = err.mean() + edge
        rep.append('  %-34s %8.1f %8.1f %18.1f' % (kind_name(k), err.mean(), np.percentile(err, 90), edge))
        if best is None or score < best[0]:
            best = (score, k)
    rep.append('Elegida: %s.' % kind_name(best[1]))
    rep.append('')
    # the map wraps in the Bering Strait: cities near the cut also count from the other side, so both ends of
    # the fit meet there without a gap
    west = P[:, 0] > LON_CUT + 300
    east = P[:, 0] < LON_CUT + 60
    P = np.vstack([P, P[west] - [360, 0], P[east] + [360, 0]])
    Q = np.vstack([Q, Q[west] - [W, 0], Q[east] + [W, 0]])
    return fit(best[1], P, Q)


class Projection:
    """The calibrated transform inside MD's map. Past MD's edge each longitude starts at MD's own vertical scale and
    squeezes little by little towards the pole, so the last latitude (LAT_TOP in the north, LAT_BOTTOM in the south)
    still lands inside the new rows and the coasts next to the edge are not flattened."""

    def __init__(self, f, south):
        self.f, self.south = f, south
        self.lons = np.arange(LON_CUT, LON_CUT + 360.0, 0.25)
        lats = np.arange(-10.0, -89.9, -0.05) if south else np.arange(45.0, 89.9, 0.05)
        lat_e = np.empty(len(self.lons))
        for i, lo in enumerate(self.lons):
            z = f(np.column_stack([np.full(len(lats), lo), lats]))[:, 1]
            past = np.nonzero(z <= 0 if south else z >= H - 1)[0]
            lat_e[i] = lats[past[0]] if len(past) else lats[-1]
        self.lat_e = gaussian_filter1d(lat_e, 8, mode='wrap')
        step = 3.0 if south else -3.0
        a = f(np.column_stack([self.lons, self.lat_e + step]))
        b = f(np.column_stack([self.lons, self.lat_e]))
        g = (b - a) / -step
        total = (SOUTH if south else NORTH) - 4
        self.span = np.maximum(np.abs((LAT_BOTTOM if south else LAT_TOP) - self.lat_e), 1.0)
        self.gx = np.clip(gaussian_filter1d(g[:, 0], 8, mode='wrap'), -10, 10)
        # z(d) = g0 d - k d^2 over the span d (degrees past the edge): MD's slope at the edge, all rows used at the end,
        # never folding back (g0 is capped so the slope at the end stays positive)
        self.g0 = np.clip(np.minimum(gaussian_filter1d(g[:, 1], 8, mode='wrap'), 1.9 * total / self.span), 1, 35)
        self.k = np.maximum(self.g0 * self.span - total, 0) / self.span ** 2

    def __call__(self, ll):
        ll = np.asarray(ll, float)
        out = self.f(ll)
        le = np.interp(ll[:, 0], self.lons, self.lat_e, period=360)
        past = ll[:, 1] < le if self.south else ll[:, 1] > le
        if past.any():
            lon = ll[past, 0]
            d = np.abs(ll[past, 1] - le[past])
            span, g0, k = (np.interp(lon, self.lons, v, period=360) for v in (self.span, self.g0, self.k))
            inside = np.minimum(d, span)
            dz = g0 * inside - k * inside ** 2 + np.maximum(d - span, 0) * np.maximum(g0 - 2 * k * span, 0.5)
            base = self.f(np.column_stack([lon, le[past]]))
            sign = -1.0 if self.south else 1.0
            out[past, 0] = base[:, 0] + sign * d * np.interp(lon, self.lons, self.gx, period=360)
            out[past, 1] = base[:, 1] + sign * dz
        return out


# ---------------------------------------------------------------- Natural Earth shapes

def load_polygons(names, lat_min, lat_max):
    """Polygons between two latitudes. A polygon that crosses the Bering cut is split there, and the part west of
    it moves to the east end of the map."""
    clip = box(-180, lat_min, 180, lat_max)
    west, east = box(-180, -90, LON_CUT, 90), box(LON_CUT, -90, 180, 90)
    out = []
    for name in names:
        with open(os.path.join(DATA, name + '.geojson'), encoding='utf-8') as f:
            feats = json.load(f)['features']
        for ft in feats:
            g = shape(ft['geometry']).intersection(clip)
            for p in ([g] if g.geom_type == 'Polygon' else getattr(g, 'geoms', [])):
                if p.geom_type != 'Polygon' or p.is_empty:
                    continue
                for side, shift in ((west, 360.0), (east, 0.0)):
                    q = p.intersection(side)
                    for r in ([q] if q.geom_type == 'Polygon' else getattr(q, 'geoms', [])):
                        if r.geom_type == 'Polygon' and not r.is_empty:
                            out.append((r, shift))
    return out


def densify(c, step=0.05):
    a, b = c[:-1], c[1:]
    n = np.maximum(1, (np.hypot(*(b - a).T) / step).astype(int))
    idx = np.repeat(np.arange(len(a)), n)
    t = (np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)) / np.repeat(n, n)
    return np.vstack([a[idx] + (b - a)[idx] * t[:, None], c[-1:]])


def rasterize(polys, proj, values=None, z_top=TOP - 1, rows=TOP - Z0):
    """Polygons drawn on a canvas whose row r is z = z_top - r. With `values`, polygon i is drawn with values[i]
    (later ones on top); without, the result is a land mask."""
    im = Image.new('L', (W, rows), 0)
    dr = ImageDraw.Draw(im)
    for i, (p, shift) in enumerate(polys):
        v = 255 if values is None else values[i]
        for ring, fill in [(p.exterior, v)] + [(h, 0) for h in p.interiors]:
            xy = proj(densify(np.asarray(ring.coords) + [shift, 0.0]))
            for off in (0, -W, W):
                pts = list(zip(xy[:, 0] + off, z_top - xy[:, 1]))
                if len(pts) > 2:
                    dr.polygon(pts, fill=fill)
    a = np.asarray(im)
    return a > 0 if values is None else a


def splat(proj, lon, lat, values, z_top, rows):
    """A field on a longitude-latitude grid (values[lat, lon, channel]) drawn on a canvas like rasterize's: each
    pixel gets the mean of the samples that land in it, and pixels no sample reaches take their neighbours'."""
    lon = (np.asarray(lon, float) - LON_CUT) % 360 + LON_CUT
    order = np.argsort(lon)
    lon, values = lon[order], values[:, order]
    # the projection on a coarse lattice, interpolated for every sample
    glon = np.arange(LON_CUT, LON_CUT + 360.3, 0.25)
    glat = np.arange(lat.min() - 0.1, lat.max() + 0.2, 0.1)
    xz = proj(np.stack(np.meshgrid(glon, glat), -1).reshape(-1, 2)).reshape(len(glat), len(glon), 2)
    i, j = np.meshgrid(np.interp(lat, glat, np.arange(len(glat))), np.interp(lon, glon, np.arange(len(glon))),
                       indexing='ij')
    x = map_coordinates(xz[..., 0], [i, j], order=1)
    z = map_coordinates(xz[..., 1], [i, j], order=1)
    r, c = np.round(z_top - z).astype(int), np.round(x).astype(int) % W
    ok = (r >= 0) & (r < rows)
    at = r[ok] * W + c[ok]
    count = np.bincount(at, minlength=rows * W).reshape(rows, W).astype(np.float32)
    out = np.empty((rows, W, values.shape[2]), np.float32)
    have = count > 0
    _, (nr, nc) = distance_transform_edt(~have, return_indices=True)
    for k in range(values.shape[2]):
        s = np.bincount(at, weights=values[..., k][ok], minlength=rows * W).reshape(rows, W)
        m = np.where(have, s / np.maximum(count, 1), 0).astype(np.float32)
        out[..., k] = np.where(have, m, m[nr, nc])
    return out


def height_style(e_cal, h_cal):
    """Metres to MD's heightmap values: the quantiles of MD's land heights matched to the real heights at the same
    pixels, so new land rises as MD's land next to it does (higher ground goes on with the slope of MD's highest)."""
    q = np.linspace(0, 1, 201)
    ek = np.maximum.accumulate(np.quantile(e_cal, q)) + q * 1e-3
    hk = np.quantile(h_cal, q).astype(float)
    slope = (hk[-1] - hk[-21]) / max(ek[-1] - ek[-21], 1.0)
    return lambda e: np.where(e > ek[-1], hk[-1] + (e - ek[-1]) * slope, np.interp(e, ek, hk))


def edge_offset(md_h, new_h, land):
    """Per column, how much higher MD's land is than the styled real heights in a few rows next to an edge (0 where
    there is no land), smoothed along the edge."""
    s = gaussian_filter1d(np.where(land, md_h - new_h, 0).sum(0), 15, mode='wrap')
    n = gaussian_filter1d(land.sum(0).astype(float), 15, mode='wrap')
    return np.where(n > 0.5, s / np.maximum(n, 1e-6), 0)


def colour_style(src, dst):
    """Blue Marble's colours to MD's colormap: a fit (quadratic in each channel) on the same land pixels."""
    f = lambda c: np.column_stack([c, c * c / 255, np.ones(len(c))])
    coef, *_ = np.linalg.lstsq(f(src), dst.astype(float), rcond=None)
    return lambda c: np.clip(f(c) @ coef, 0, 255)


def halve(a):
    """Mean of every 2 x 2 block (full size to the colour maps' half size)."""
    return a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2, -1).mean((1, 3))


def load_etopo(name):
    """ETOPO 2022 (NOAA, ice surface) heights in metres: latitudes ascending, longitudes 0 to 360, channel axis."""
    d = np.load(os.path.join(DATA, name))
    return d['lon'], d['lat'], d['z'].astype(np.float32)[..., None]


def load_blue_marble():
    """NASA's Blue Marble (July 2004, credit: NASA Earth Observatory) as RGB, latitudes ascending."""
    a = np.asarray(Image.open(os.path.join(DATA, BLUE_MARBLE)).convert('RGB'), np.float32)[::-1]
    h, w = a.shape[:2]
    lat = -90 + (np.arange(h) + 0.5) * 180 / h
    lon = -180 + (np.arange(w) + 0.5) * 360 / w
    return lon, lat, a


# ---------------------------------------------------------------- Coast fit against MD's own coasts (north)

def register(A, B, rep):
    """Smooth displacement u so that A(p + u(p)) matches B(p) where MD has rows (demons, coarse to fine).
    North of the edge u fades out over DECAY rows, so the far Arctic keeps its real shape."""
    known = np.zeros(A.shape, bool)
    known[NORTH:] = True
    pad = 128

    def padx(a):
        return np.concatenate([a[:, -pad:], a, a[:, :pad]], axis=1).astype(np.float32)

    a_full, b_full, k_full = padx(A), padx(B), padx(known)
    u = None
    for lev, sig_img, sig_u, iters in [(32, 2.0, 2.0, 80), (16, 1.5, 2.5, 80), (8, 1.0, 3.0, 80), (4, 1.0, 3.0, 60)]:
        a = gaussian_filter(zoom(a_full, 1 / lev, order=1), sig_img)
        b = gaussian_filter(zoom(b_full, 1 / lev, order=1), sig_img)
        k = zoom(k_full, 1 / lev, order=0)
        h, w = a.shape
        u = np.zeros((2, h, w), np.float32) if u is None else \
            np.stack([zoom(c, (h / c.shape[0], w / c.shape[1]), order=1) for c in u]) * 2
        rr, cc = np.mgrid[0:h, 0:w].astype(np.float32)
        gb = np.stack(np.gradient(b))
        for _ in range(iters):
            aw = map_coordinates(a, [rr + u[0], cc + u[1]], order=1, mode='nearest')
            g = (np.stack(np.gradient(aw)) + gb) / 2
            diff = (aw - b) * k
            u -= diff * g / ((g ** 2).sum(0) + diff ** 2 + 1e-4)
            u = np.stack([gaussian_filter(c, sig_u) for c in u])
    u = np.stack([zoom(c, (a_full.shape[0] / c.shape[0], a_full.shape[1] / c.shape[1]), order=1) for c in u]) * 4
    u = u[:, :, pad:-pad]
    u[:, :NORTH] = u[:, NORTH:NORTH + 1] * np.exp(-(NORTH - np.arange(NORTH)) / DECAY)[:, None]
    rr, cc = np.mgrid[0:A.shape[0], 0:W].astype(np.float32)
    sr, sc = rr + u[0], cc + u[1]
    det = np.gradient(sr)[0] * np.gradient(sc)[1] - np.gradient(sr)[1] * np.gradient(sc)[0]
    rep.append('Ajuste de costas del norte: desplazamiento máximo %.0f píxeles; jacobiano mínimo %.2f (mayor que 0: '
               'la deformación no se pliega).' % (np.abs(u).max(), det.min()))
    if det.min() <= 0:
        raise SystemExit('El ajuste de costas se pliega: revisar la calibración.')
    return np.stack([np.clip(sr, 0, A.shape[0] - 1), sc % W])


class Geo:
    """Everything that turns longitude and latitude into pixels of the enlarged map."""

    def __init__(self, md, rep):
        f = choose_transform(*control_points(md, rep, False), rep, False)
        self.proj = Projection(f, False)
        f = choose_transform(*control_points(md, rep, True), rep, True)
        self.proj_s = Projection(f, True)
        rep.append('Borde norte de MD: entre %.1f° y %.1f°; borde sur: entre %.1f° y %.1f°.'
                   % (self.proj.lat_e.min(), self.proj.lat_e.max(), self.proj_s.lat_e.max(), self.proj_s.lat_e.min()))
        self.A = rasterize(load_polygons(['ne_10m_land', 'ne_10m_minor_islands'], 38, 90), self.proj)
        self.B = np.zeros(self.A.shape, bool)
        self.B[NORTH:] = md.land[:TOP - Z0 - NORTH]
        self.coords = register(self.A, self.B, rep)

    def warp(self, img, rows=None):
        c = self.coords if rows is None else self.coords[:, :rows]
        return map_coordinates(img, c, order=0, mode='grid-wrap')

    def raster_north(self, polys, values=None):
        """North rows only, fitted to MD's coasts (row r is the map's row r)."""
        a = rasterize(polys, self.proj, values)
        return self.warp(a.astype(np.uint8), NORTH) > 0 if values is None else self.warp(a, NORTH)

    def raster_south(self, polys, values=None):
        """South rows only (row s is the map's row NORTH + H + s)."""
        return rasterize(polys, self.proj_s, values, z_top=-1, rows=SOUTH)

    def field_north(self, lon, lat, values):
        """A gridded field on the north rows and MD's rows below them down to Z0 (row r is the map's row r), fitted
        to MD's coasts like the coastlines."""
        keep = lat > 40
        a = splat(self.proj, lon, lat[keep], values[keep], TOP - 1, TOP - Z0)
        return np.stack([map_coordinates(a[..., k], self.coords, order=1, mode='grid-wrap')
                         for k in range(a.shape[2])], -1)

    def field_south(self, lon, lat, values, md_rows):
        """The same on MD's last md_rows rows and the south rows (row s is the map's row NORTH + H - md_rows + s)."""
        keep = lat < -20
        return splat(self.proj_s, lon, lat[keep], values[keep], md_rows - 1, md_rows + SOUTH)

    def pixel(self, lon, lat):
        """(row, column) of a point in the enlarged map."""
        if lat < 0:
            x, z = self.proj_s(np.array([[float(unwrap(lon)), lat]]))[0]
            return int(round(TOTAL - 1 - (z + SOUTH))), int(round(x)) % W
        x, z = self.proj(np.array([[float(unwrap(lon)), lat]]))[0]
        p0 = np.array([TOP - 1 - z, x % W])
        p = p0.copy()
        for _ in range(30):
            s = np.array([map_coordinates(self.coords[0], [[p[0]], [p[1]]], order=1)[0],
                          map_coordinates(self.coords[1], [[p[0]], [p[1]]], order=1)[0]])
            d = s - p0
            d[1] = (d[1] + W / 2) % W - W / 2
            p = p - d
            p[0] = np.clip(p[0], 0, self.coords.shape[1] - 1)
            p[1] %= W
        return int(round(p[0])), int(round(p[1])) % W


def soften_coast(land, ice, rng):
    """Antarctica's coast is squeezed into few rows (about 8 columns per row), so it comes out in long straight
    steps. Near the big land masses the coast moves up to about a row, in short waves along it, which breaks them.
    Small islands are left as they are."""
    parts, _ = label(land)
    sizes = np.bincount(parts.ravel())
    sizes[0] = 0
    near = binary_dilation(sizes[parts] >= WHOLE_ISLAND, iterations=3)
    near[-6:] = False                      # the last rows (the pole) are a thin strip: kept whole
    waves = []
    for sigma, amp in (((1.0, 8.0), 1.0), ((1.0, 8.0), 3.0)):
        n = gaussian_filter(rng.standard_normal(land.shape), sigma, mode=('nearest', 'wrap'))
        waves.append(n / n.std() * amp)
    rr, cc = np.mgrid[0:land.shape[0], 0:land.shape[1]].astype(np.float32)
    at = [rr + waves[0], cc + waves[1]]
    moved = lambda m: map_coordinates(m.astype(np.float32), at, order=1, mode='nearest') > 0.5
    return np.where(near, moved(land), land), np.where(near, moved(ice), ice)


def seam_morph(new_land, md_top):
    """Within SEAM rows of the edge, the coast blends from MD's last row into the real coast, so every land or sea
    run that reaches MD's edge goes on without a straight cut."""
    def sdf(m):
        return distance_transform_edt(m) - distance_transform_edt(~m)
    d_md = sdf(np.tile(md_top, (3, 1)))[1]
    d_ne = sdf(new_land)
    out = new_land.copy()
    for i in range(SEAM):
        r = NORTH - 1 - i             # i = 0 is the row right above MD's edge
        w = (i + 1) / (SEAM + 1)
        w = w * w * (3 - 2 * w)
        out[r] = (1 - w) * d_md + w * d_ne[r] > 0
    return out


def carve_siberia(md, A, russia):
    """MD land that is sea in reality, in the Russian columns and within CARVE_ROWS of the north edge, reached from
    the open sea there. Calibration noise is opened away and every MD province keeps its southern CARVE_KEEP share."""
    rows = A.shape[0] - NORTH
    cut = np.zeros((H, W), bool)
    cut[:rows] = md.landtype[:rows] & ~A[NORTH:]
    cut[:, ~russia] = False
    cut[CARVE_ROWS:] = False
    cut = binary_opening(cut, iterations=CARVE_OPEN)
    parts, _ = label(cut)
    touch = np.unique(parts[0][cut[0]])
    cut = np.isin(parts, touch[touch > 0])
    for p in np.unique(md.idmap[cut]):
        rr, cc = np.nonzero(md.idmap == p)
        keep = rr >= np.quantile(rr, 1 - CARVE_KEEP)
        cut[rr[keep], cc[keep]] = False
    return cut


def wrap_nearest(src, pad=256):
    """Indices (rows, cols) of the nearest src pixel for every pixel, across the east-west wrap."""
    p = np.concatenate([src[:, -pad:], src, src[:, :pad]], 1)
    _, idx = distance_transform_edt(~p, return_indices=True)
    return idx[0][:, pad:-pad], (idx[1][:, pad:-pad] - pad) % src.shape[1]


def fill_bering(md, A, russia):
    """MD sea that is land in reality next to the Bering wrap, within FILL_ROWS of the north edge: MD cuts the tip of
    Chukotka off there, so it looks like an island. Only pieces that touch MD land. What the fill leaves of an MD sea
    province in pieces smaller than FILL_KEEP is filled too (no specks of sea in the land, no channels cut through
    the coast for them). Returns the fill and the sea provinces it took whole: they move to the new sea."""
    rows = A.shape[0] - NORTH
    f = np.zeros((H, W), bool)
    f[:rows] = md.sea[:rows] & A[NORTH:]
    f[:, FILL_COLS:W - FILL_COLS] = False
    f[:, ~russia] = False
    f[FILL_ROWS:] = False
    f = binary_opening(f, iterations=2)
    pad = FILL_COLS
    wrapped = lambda a: np.concatenate([a[:, -pad:], a, a[:, :pad]], 1)
    parts, _ = label(wrapped(f))
    touch = np.unique(parts[binary_dilation(wrapped(md.landtype)) & (parts > 0)])
    f &= np.isin(parts, touch[touch > 0])[:, pad:-pad]
    touched = np.unique(md.idmap[f])
    for p in touched:
        m = md.idmap == p
        left, _ = label(m & ~f)
        sizes = np.bincount(left.ravel())
        near = np.unique(left[binary_dilation(f & m) & (left > 0)])      # pieces the fill cut off
        f |= np.isin(left, near[sizes[near] < FILL_KEEP])
    gone = [int(p) for p in touched if not ((md.idmap == p) & ~f).any()]
    return f, gone


def edge_lakes(md, russia):
    """MD's lakes in the Russian sector that reach the north edge: the gulfs of the Ob, the Taz and the Yenisei,
    which MD drew as lakes cut off at the edge. They open onto the new sea and become sea provinces."""
    lake = md.land & ~md.landtype
    return sorted(int(i) for i in np.unique(md.idmap[0][lake[0] & russia]))


# ---------------------------------------------------------------- Provinces of the new rows

def border_noise(shape, rng):
    """A smooth random displacement (2, rows, W) added to pixel positions before they pick their nearest province
    centre: borders come out winding like MD's instead of straight Voronoi lines."""
    out = []
    for _ in range(2):
        f = np.zeros(shape, np.float32)
        for sigma, amp in ((14.0, 9.0), (5.0, 3.5), (2.0, 1.2)):
            n = gaussian_filter(rng.standard_normal(shape).astype(np.float32), sigma, mode=('nearest', 'wrap'))
            f += n / (n.std() + 1e-6) * amp
        out.append(f)
    return np.stack(out)


def seeds_of(pts, target, rng):
    """About len(pts) / target province centres spread over the pixels `pts` (k-means)."""
    n = max(1, int(round(len(pts) / target)))
    if n == 1:
        return pts.mean(0, keepdims=True)
    sample = pts[rng.choice(len(pts), min(len(pts), 20000), replace=False)].astype(float)
    seeds, _ = kmeans2(sample, n, iter=20, minit='++', seed=int(rng.integers(1 << 30)))
    return seeds


def nearest_seed(pts, seeds, noise):
    """Index of the nearest centre for every pixel, measured from its position moved by `noise`."""
    q = pts.astype(np.float32) + noise[:, pts[:, 0], pts[:, 1]].T
    lab = np.empty(len(pts), int)
    for i in range(0, len(pts), 100000):
        lab[i:i + 100000] = ((q[i:i + 100000, None, :] - seeds[None]) ** 2).sum(-1).argmin(1)
    return lab


def split(mask, target, rng, noise):
    """Cuts one connected piece into provinces of about `target` pixels with winding borders."""
    pts = np.argwhere(mask)
    seeds = seeds_of(pts, target, rng)
    if len(seeds) == 1:
        return np.zeros(len(pts), int), pts
    return nearest_seed(pts, seeds, noise), pts


def edge_caps(ids, kind, rng):
    """Rows above the edge that MD's provinces of one kind (kind: their columns on MD's last row) grow into: a
    smooth winding line, 3 to EDGE_CAP rows tall, so the border with the new provinces is not one straight line along
    MD's old edge. (An arch per province, as before, read as a row of scallops.)"""
    n = np.zeros(W)
    for sigma, amp in ((60.0, 1.0), (18.0, 0.45)):
        f = gaussian_filter1d(rng.standard_normal(W), sigma, mode='wrap')
        n += f / (f.std() + 1e-9) * amp
    cap = np.clip(11 + 5.3 * n, 3, EDGE_CAP)
    return np.maximum(np.round(np.where(kind, cap, 0)), 3).astype(int)


def fix_fragments(lab, cls):
    """Every province keeps only its largest connected part; the rest go to the nearest province of the same kind
    (land or sea). Labels <= 0 are not touched."""
    for _ in range(3):
        orphans = np.zeros(lab.shape, bool)
        for i, sl in enumerate(find_objects(np.where(lab > 0, lab, 0)), 1):
            if sl is None:
                continue
            m = lab[sl] == i
            parts, n = label(m)
            if n > 1:
                sizes = np.bincount(parts.ravel())[1:]
                orphans[sl] |= m & (parts != sizes.argmax() + 1)
        if not orphans.any():
            return
        for c in (True, False):
            hole = orphans & (cls == c)
            if hole.any():
                src = (lab > 0) & (cls == c) & ~orphans
                _, idx = distance_transform_edt(~src, return_indices=True)
                lab[hole] = lab[idx[0][hole], idx[1][hole]]


def four_way(full):
    """2x2 blocks where four different provinces meet (the map wraps east to west). HOI4 refuses to load them."""
    f = np.concatenate([full, full[:, :1]], 1)
    p, q, r, s = f[:-1, :-1], f[:-1, 1:], f[1:, :-1], f[1:, 1:]
    return (p != q) & (p != r) & (p != s) & (q != r) & (q != s) & (r != s)


def remove_x_crossings(ids, cls, editable):
    """In every four-way block, one editable pixel takes the province of a side neighbour of the same kind, never one
    across the east-west wrap (its province would span the whole map). If none fits, an editable pixel takes the
    province, land or sea, of the pixel above or below it."""
    for _ in range(20):
        blocks = np.argwhere(four_way(ids))
        if not len(blocks):
            return
        for i, j in blocks:
            corners = [(i, j), (i, j + 1), (i + 1, j + 1), (i + 1, j)]
            done = False
            for same_kind in (True, False):
                for k, (a, b) in enumerate(corners):
                    if not editable[a, b % W]:
                        continue
                    for c, d in (corners[k - 1], corners[(k + 1) % 4]):
                        if (b < W) == (d < W) and (not same_kind and d == b or cls[c, d % W] == cls[a, b % W]):
                            ids[a, b % W] = ids[c, d % W]
                            cls[a, b % W] = cls[c, d % W]
                            done = True
                            break
                    if done:
                        break
                if done:
                    break
    raise SystemExit('Quedan cruces de cuatro provincias que no se pudieron arreglar.')


def build_band(land, ice, state_zone, sea_zone, edge, md_near, states, seas, seam, rng, first_label, ice_size,
               strip=None):
    """Provinces of one new band, drawn as if MD's map lay right below it (the south band arrives flipped).
    edge: MD's row next to the band (ids, land, landtype, sea). md_near: MD's land rows next to the band.
    strip: columns where a thin coast (land at most COAST_STRIP tall above the edge) goes wholly to MD's provinces,
    so MD's states reach the sea there without a straight border along the edge.
    Returns labels (> 0 new provinces, < 0 an MD province id), the land mask, the MD slivers and the maps from
    label to state or sea region."""
    R = land.shape[0]
    lab = np.zeros(land.shape, np.int64)
    ext = np.zeros(land.shape, bool)
    noise = border_noise(land.shape, rng)
    _, idx = distance_transform_edt(~np.vstack([np.zeros((R - 1, W), bool), edge['landtype'][None]]),
                                    return_indices=True)
    if seam:
        # pieces of land that grow out of MD's land along the edge, inside an arch over each MD province: MD's own
        # provinces
        rise = (R - 1 - np.arange(R))[:, None] + 0.5 * noise[0]     # rows above the edge, winding
        band = rise < edge_caps(edge['ids'], edge['landtype'], rng)[None, :]
        comp, _ = label(land & band)
        touching = np.unique(comp[R - 1][edge['land'] & land[R - 1]])
        ext = np.isin(comp, touching[touching > 0])
        if strip is not None:
            run = np.zeros(W, np.int64)
            alive = edge['land'].copy()
            for r in range(R - 1, -1, -1):
                alive &= land[r]
                if not alive.any():
                    break
                run += alive
            cols = strip & (run > 0) & (run <= COAST_STRIP)
            ext |= (np.arange(R)[:, None] >= R - run[None, :]) & cols[None, :] & land
            # small bits of new land left next to that coast join it too
            bits, _ = label(land & ~ext)
            sizes = np.bincount(bits.ravel())
            near = np.unique(bits[binary_dilation(ext) & (bits > 0)])
            near = near[sizes[near] < LAND_SIZE]
            ext |= np.isin(bits, near) & (bits > 0)
        lab[ext] = -edge['ids'][idx[1][ext]]

    newland = land & ~ext & (state_zone > 0)
    parts, n = label(newland)
    newland &= np.bincount(parts.ravel())[parts] >= MIN_ISLAND
    water = ~(newland | ext)
    wparts, _ = label(water)
    open_ids = np.union1d(wparts[0], wparts[R - 1][~edge['land']])
    wsizes = np.bincount(wparts.ravel())
    enclosed = ~np.isin(wparts, open_ids) & water & (wsizes[wparts] < MIN_LAKE)
    newland |= enclosed & (state_zone > 0)
    water &= ~newland
    e = enclosed & (state_zone == 0)
    if e.any() and ext.any():
        near = distance_transform_edt(~ext, return_indices=True)[1]
        lab[e] = lab[near[0][e], near[1][e]]
        ext |= e
        water &= ~e

    # water cut off from the new ocean joins the MD sea zone it opens onto (or becomes land if it opens onto none)
    wparts, n = label(water)
    wsizes = np.bincount(wparts.ravel())
    wsizes[0] = 0
    for wi in range(1, n + 1):
        if wi == wsizes.argmax():
            continue
        m = wparts == wi
        if (m[R - 1] & edge['sea']).any():
            # shared among the MD sea provinces it opens onto, with winding borders
            cols = np.nonzero(m[R - 1] & edge['sea'])[0]
            pids = edge['ids'][cols]
            opens = np.unique(pids)
            seeds = np.array([[R - 1, cols[pids == p].mean()] for p in opens])
            lab[m] = -opens[nearest_seed(np.argwhere(m), seeds, noise)]
        elif (m & (state_zone > 0)).all():
            newland |= m
        elif ext.any():
            lab[m] = -edge['ids'][idx[1][m]]
            ext |= m
        else:
            # enclosed water with no MD sea to join: land of the nearest state
            _, zidx = distance_transform_edt(state_zone == 0, return_indices=True)
            state_zone[m] = state_zone[zidx[0][m], zidx[1][m]]
            newland |= m
        water &= ~m
    land = newland | ext

    # an island that lies mostly in one state's zone belongs wholly to it; big land masses keep the zone split
    # (a strip that touches MD's land or the edge is not an island: it keeps the split, so borders like Alaska and
    # Canada's go on)
    parts, n = label(newland)
    attached = np.unique(parts[binary_dilation(ext, iterations=2) | (np.arange(R) == R - 1)[:, None]])
    for pi, sl in enumerate(find_objects(parts), 1):
        m = parts[sl] == pi
        zones = state_zone[sl][m]
        counts = np.bincount(zones[zones > 0])
        if pi not in attached and m.sum() < WHOLE_ISLAND and len(counts) and counts.max() >= 0.5 * m.sum():
            state_zone[sl][m] = counts.argmax()

    # "anexo" states form no state: their land joins the nearest MD land province on the edge (a coast that came
    # out in loose strips, or the half of an island MD already has)
    # Each piece takes the MD province it touches most along the coast it shares with MD's land (the rest of its
    # island); a piece that touches none takes the one at the nearest edge column.
    for si, s in enumerate(states):
        m = newland & (state_zone == si + 1)
        if not (s.get('annex') and m.any()):
            continue
        pieces, n = label(m)
        for pi in range(1, n + 1):
            piece = pieces == pi
            ring = binary_dilation(piece, iterations=2) & ~piece
            touch = -lab[ring & ext]
            if touch.size:
                lab[piece] = -np.bincount(touch).argmax()
            else:
                lab[piece] = -edge['ids'][idx[1][piece]]
            ext |= piece
        newland &= ~m

    next_label = first_label
    prov_state, prov_sea = {}, {}
    for si in range(len(states)):
        pieces, n = label(newland & (state_zone == si + 1))
        for pi in range(1, n + 1):
            m = pieces == pi
            sub, pts = split(m, ice_size if ice[m].mean() > 0.5 else LAND_SIZE, rng, noise)
            lab[pts[:, 0], pts[:, 1]] = sub + next_label
            for j in range(sub.max() + 1):
                prov_state[next_label + j] = si
            next_label += sub.max() + 1

    # sea provinces: per connected body of water, small ones along the coasts and bigger ones in open ocean, cut with
    # no regard to the sea regions; each then joins the region that holds most of it (no thin strips where a region
    # ends)
    sea_zone = np.where(water, sea_zone, 0)
    if (water & (sea_zone == 0)).any():
        _, near = distance_transform_edt(sea_zone == 0, return_indices=True)
        hole = water & (sea_zone == 0)
        sea_zone[hole] = sea_zone[near[0][hole], near[1][hole]]
    far = distance_transform_edt(~np.vstack([land, md_near]))[:R] > OCEAN_DIST
    bodies, n = label(water)
    for bi in range(1, n + 1):
        pts = np.argwhere(bodies == bi)
        is_far = far[pts[:, 0], pts[:, 1]]
        seeds = np.vstack([seeds_of(p, t, rng) for p, t in ((pts[~is_far], SEA_SIZE), (pts[is_far], OCEAN_SIZE))
                           if len(p)])
        sub = nearest_seed(pts, seeds, noise) if len(seeds) > 1 else np.zeros(len(pts), int)
        lab[pts[:, 0], pts[:, 1]] = sub + next_label
        zones = sea_zone[pts[:, 0], pts[:, 1]]
        for j in np.unique(sub):
            z = zones[sub == j]
            prov_sea[next_label + j] = int(np.bincount(z[z > 0]).argmax()) - 1
        next_label += sub.max() + 1
    if seam:
        # MD's sea provinces on the edge grow the same way into the open water right above them
        own = edge['own_sea']
        sea_band = rise < edge_caps(edge['ids'], own, rng)[None, :]
        comp, _ = label(water & sea_band)
        touching = np.unique(comp[R - 1][own & water[R - 1]])
        sext = np.isin(comp, touching[touching > 0])
        _, sidx = distance_transform_edt(~np.vstack([np.zeros((R - 1, W), bool), own[None]]), return_indices=True)
        lab[sext] = -edge['ids'][sidx[1][sext]]
        # water the arches cut off from the rest of its body of water goes whole to the MD province it touches most
        rest, _ = label(water & ~sext)
        sizes = np.bincount(rest.ravel())
        sizes[0] = 0
        for bi in range(1, n + 1):
            pieces = np.unique(rest[bodies == bi])
            pieces = pieces[pieces > 0]
            for pi in pieces[pieces != pieces[sizes[pieces].argmax()]] if len(pieces) > 1 else ():
                m = rest == pi
                ring = lab[binary_dilation(m) & sext]
                if ring.size:
                    lab[m] = -np.bincount(-ring).argmax()
    cls = land.copy()
    fix_fragments(lab, cls)
    for _ in range(2):
        sizes = np.bincount(np.where(lab > 0, lab, 0).ravel(), minlength=next_label)
        small = (lab > 0) & (sizes[np.where(lab > 0, lab, 0)] < np.where(cls, MIN_ISLAND, 200))
        if not small.any():
            break
        for c in (True, False):
            hole = small & (cls == c)
            src = (lab > 0) & (cls == c) & ~small
            if hole.any() and src.any():
                _, near = distance_transform_edt(~src, return_indices=True)
                lab[hole] = lab[near[0][hole], near[1][hole]]
    fix_fragments(lab, cls)
    return lab, cls, ext & cls, prov_state, prov_sea, next_label


class World:
    """The whole enlarged map: MD's provinces in the middle, the new north and south bands, states and regions."""

    def __init__(self, md, geo, data, rep):
        states, vps, regions, seas = data
        self.md, self.geo, self.states, self.vps, self.regions, self.seas = md, geo, states, vps, regions, seas
        rng = np.random.default_rng(1)
        north_st = [i for i, s in enumerate(states) if not s['south']]
        south_st = [i for i, s in enumerate(states) if s['south']]
        north_sea = [i for i, s in enumerate(seas) if not s['south']]
        south_sea = [i for i, s in enumerate(seas) if s['south']]

        # ---- north: real coast fitted to MD's, east of RUSSIA_LON the real coast as it is and MD carved to it
        self.Aw = geo.warp(geo.A.astype(np.uint8)) > 0
        russia = self.russian_columns(geo)
        self.carve = carve_siberia(md, geo.A, russia)
        # Chukotka joined across the Bering wrap: the filled sea goes to the nearest MD land province on its own side
        # of the wrap (a province with pixels at both ends of the map crashes the game)
        self.fill, self.gone = fill_bering(md, geo.A, russia)
        self.lost = self.carve | self.fill              # MD pixels that change province
        self.md_ids = md.idmap.copy()
        _, (nr, nc) = distance_transform_edt(~(md.landtype & ~self.carve), return_indices=True)
        self.md_ids[self.fill] = md.idmap[nr[self.fill], nc[self.fill]]
        # MD's lakes cut off at the edge (gulfs of the Ob, Taz, Yenisei) become sea
        self.lakes = edge_lakes(md, russia)
        self.lake = np.isin(md.idmap, self.lakes)
        md_land = (md.land & ~self.carve & ~self.lake) | self.fill
        md_landtype = (md.landtype & ~self.carve) | self.fill
        md_sea = (md.sea & ~self.fill) | self.carve | self.lake
        land_n = seam_morph(self.Aw[:NORTH], md_land[0])
        land_n[:, russia] = geo.A[:NORTH, russia]
        land_n[NORTH - BRIDGE_ROWS:] |= self.bridges(md, russia, md.sea[0] & ~self.fill[0])
        # each lake mouth opens onto the new sea: no land between it and open water
        for c in np.nonzero(self.lake[0])[0]:
            r = NORTH - 1
            while r >= NORTH - 40 and land_n[r, c]:
                land_n[r, c] = False
                r -= 1
        edge_n = dict(ids=self.md_ids[0], land=md_land[0], landtype=md_landtype[0], sea=md_sea[0],
                      own_sea=((md.sea & ~self.fill) | self.lake)[0])    # MD's own sea provinces on the edge
        ice_n = geo.raster_north(load_polygons(['ne_10m_glaciated_areas'], 38, 90))
        zones_st = self.zones(states, north_st, geo.raster_north)
        zones_st, strait = self.limit_to_mass(zones_st, land_n, states, north_st, geo.raster_north)
        land_n &= ~strait
        # "costa=N:other": the state keeps only land within N pixels of the sea, its inland goes to "other", so its
        # border with that state follows the coast instead of the zone's straight lines
        inland = distance_transform_edt(land_n)
        for n, i in enumerate(north_st):
            for depth, other in states[i]['coast']:
                to = [m for m, j in enumerate(north_st) if states[j]['name'] == other]
                if not to:
                    raise SystemExit('estados.txt: costa= de %s apunta a un estado que no existe: %s'
                                     % (states[i]['name'], other))
                zones_st[(zones_st == n + 1) & (inland > depth)] = to[0] + 1
        zones_sea = self.zones(seas, north_sea, geo.raster_north)
        lab_n, cls_n, ext_n, ps_n, pz_n, nl = build_band(
            land_n, ice_n, zones_st, zones_sea, edge_n, md_land[:64], [states[i] for i in north_st],
            [seas[i] for i in north_sea], SEAM, rng, 1, ICE_SIZE, strip=russia)
        ps_n = {k: north_st[v] for k, v in ps_n.items()}
        pz_n = {k: north_sea[v] for k, v in pz_n.items()}

        # ---- south: the real coast as it is, drawn flipped so MD's map lies right below it like in the north
        land_s = geo.raster_south(load_polygons(['ne_10m_land', 'ne_10m_minor_islands'], -90, -25))
        ice_s = geo.raster_south(load_polygons(['ne_10m_glaciated_areas'], -90, -25)) > 0
        land_s, ice_s = soften_coast(land_s, ice_s, rng)
        zst_s = self.zones(states, south_st, geo.raster_south)
        zsea_s = self.zones(seas, south_sea, geo.raster_south)
        edge_s = dict(ids=md.idmap[-1], land=md.land[-1], landtype=md.landtype[-1], sea=md.sea[-1])
        lab_s, cls_s, _, ps_s, pz_s, _ = build_band(
            land_s[::-1], ice_s[::-1], zst_s[::-1].copy(), zsea_s[::-1].copy(), edge_s, md.land[-64:][::-1],
            [states[i] for i in south_st], [seas[i] for i in south_sea], 0, rng, nl, ANTARCTIC_SIZE)
        lab_s, cls_s = lab_s[::-1], cls_s[::-1]
        ps_s = {k: south_st[v] for k, v in ps_s.items()}
        pz_s = {k: south_sea[v] for k, v in pz_s.items()}

        # ---- number the new provinces after MD's, in map order (north band, then south band)
        ids = np.zeros((TOTAL, W), np.int64)
        land = np.zeros((TOTAL, W), bool)
        ids[NORTH:NORTH + H] = self.md_ids
        land[NORTH:NORTH + H] = md_landtype
        labs = np.zeros((TOTAL, W), np.int64)
        labs[:NORTH] = lab_n
        labs[NORTH + H:] = lab_s
        land[:NORTH], land[NORTH + H:] = cls_n, cls_s
        ids[labs < 0] = -labs[labs < 0]
        firsts = {l: (sl[0].start, sl[1].start) for l, sl in enumerate(find_objects(np.where(labs > 0, labs, 0)), 1)
                  if sl is not None}
        self.new_ids = {}
        nid = md.max_province + 1
        for l in sorted(firsts, key=lambda l: firsts[l]):
            self.new_ids[l] = nid
            nid += 1
        lut = np.zeros(max(firsts) + 1, np.int64)
        for l, i in self.new_ids.items():
            lut[l] = i
        ids[labs > 0] = lut[labs[labs > 0]]

        # carved MD land joins the new sea province right above it
        rows = NORTH + CARVE_ROWS
        carve_full = np.zeros((TOTAL, W), bool)
        carve_full[NORTH:NORTH + H] = self.carve
        src = np.zeros((rows, W), bool)
        src[:NORTH] = (ids[:NORTH] > md.max_province) & ~land[:NORTH]
        _, near = distance_transform_edt(~src, return_indices=True)
        cm = carve_full[:rows]
        ids[:rows][cm] = ids[:rows][near[0][cm], near[1][cm]]

        # an MD sea province the Bering fill took whole moves to the new sea right off the coast where it was, as big
        # as it was, on its own side of the wrap
        for p in self.gone:
            was = np.zeros((TOTAL, W), bool)
            was[NORTH:NORTH + H] = md.idmap == p
            cols = np.nonzero(was.any(0))[0]
            side = np.arange(W) < W // 2 if cols.max() < W // 2 else np.arange(W) >= W // 2
            free = np.zeros_like(was)
            free[:NORTH] = (ids[:NORTH] > md.max_province) & ~land[:NORTH] & side
            d = distance_transform_edt(~was)
            rr, cc = np.nonzero(free)
            take = np.argsort(d[rr, cc], kind='stable')[:int(was.sum())]
            ids[rr[take], cc[take]] = p

        editable = carve_full.copy()
        editable[NORTH:NORTH + H] |= self.fill
        editable[:NORTH] = True
        editable[NORTH + H:] = True
        remove_x_crossings(ids, land, editable)
        self.ids, self.land, self.editable = ids, land, editable
        self.carve_full = carve_full
        self.ext = np.zeros((TOTAL, W), bool)
        self.ext[:NORTH] = ext_n & land[:NORTH] & (ids[:NORTH] <= md.max_province)
        self.ice = np.zeros((TOTAL, W), bool)
        self.ice[:NORTH], self.ice[NORTH + H:] = ice_n, ice_s
        self.newland = land & (ids > md.max_province)
        self.is_land = {self.new_ids[l]: True for l in list(ps_n) + list(ps_s) if l in self.new_ids}
        self.is_land.update({self.new_ids[l]: False for l in list(pz_n) + list(pz_s) if l in self.new_ids})
        self.state_of = {self.new_ids[l]: s for l, s in list(ps_n.items()) + list(ps_s.items()) if l in self.new_ids}
        self.sea_of = {self.new_ids[l]: s for l, s in list(pz_n.items()) + list(pz_s.items()) if l in self.new_ids}
        present = set(np.unique(ids[ids > md.max_province]).tolist())
        for d in (self.is_land, self.state_of, self.sea_of):
            for k in [k for k in d if k not in present]:
                del d[k]
        self.join_sea_regions()
        # each opened lake joins the sea region of the new sea at its mouth
        self.lake_sea = {}
        near = None
        for p in self.lakes:
            cols = np.nonzero(md.idmap[0] == p)[0]
            above = [int(i) for i in ids[NORTH - 1, cols] if int(i) in self.sea_of]
            if not above:
                if near is None:
                    near = wrap_nearest(np.isin(ids[:NORTH], list(self.sea_of)))
                above = [int(ids[near[0][NORTH - 1, c], near[1][NORTH - 1, c]]) for c in cols]
            self.lake_sea[p] = self.sea_of[max(set(above), key=above.count)]
        # an MD sea province moved to the new sea leaves its MD region the same way (HOI4 rejects a naval region
        # split in pieces): it joins the region of the new sea around it
        for p in self.gone:
            ring = binary_dilation(ids == p) & (ids != p)
            around = [int(i) for i in ids[ring] if int(i) in self.sea_of]
            self.lake_sea[p] = self.sea_of[max(set(around), key=around.count)]
        lost = np.bincount(md.idmap[self.carve], minlength=md.max_province + 1)
        rep.append('')
        rep.append('Provincias nuevas: %d de tierra y %d de mar (norte y sur). %d píxeles nuevos se suman a %d '
                   'provincias de MD del borde norte.' % (sum(self.is_land.values()),
                                                         sum(1 for v in self.is_land.values() if not v),
                                                         int(self.ext.sum()), len(np.unique(ids[self.ext]))))
        rep.append('Costa real de Siberia: %d píxeles de tierra de MD pasan a mar, en %d provincias.'
                   % (int(self.carve.sum()), int((lost > 0).sum())))
        gained = np.bincount(md.idmap[self.fill], minlength=md.max_province + 1)
        rep.append('Chukotka unida en el corte de Bering: %d píxeles de mar de MD pasan a tierra (provincias de mar %s).'
                   % (int(self.fill.sum()), ', '.join(str(p) for p in np.nonzero(gained)[0])))
        if self.gone:
            rep.append('Provincias de mar de MD que el relleno tapó enteras y pasan al mar nuevo frente a la costa: %s.'
                       % ', '.join(map(str, self.gone)))
        rep.append('Lagos de MD cortados en el borde que pasan a ser mar (golfos del Obi, Taz y Yeniséi): %s.'
                   % ', '.join(map(str, self.lakes)))

    def zones(self, items, which, raster):
        """Zone index + 1 of every pixel of a band (0 = none); earlier items win where zones overlap."""
        polys = [((p, 0.0), n + 1) for n in reversed(range(len(which))) for p in items[which[n]]['zone']]
        return raster([p for p, _ in polys], [v for _, v in polys]).astype(np.int64)

    def russian_columns(self, geo):
        """Columns from RUSSIA_LON eastwards to the Bering cut, including the tip of Chukotka that MD draws at the
        west end of the map."""
        p = geo.proj
        def x_at(lon):
            return int(round(p(np.array([[lon, np.interp(lon, p.lons, p.lat_e, period=360)]]))[0][0]))
        cols = np.zeros(W, bool)
        cols[x_at(RUSSIA_LON):] = True
        cols[:max(0, x_at(LON_CUT + 359.99) - W)] = True
        return cols

    def bridges(self, md, russia, sea):
        """Columns over a short run of sea on MD's last row (`sea`, after the Bering fill), in the Russian sector,
        with land of the same MD state on both sides: MD cut that land there, so the new rows join it."""
        state = md.states_of_provinces()
        top = self.md_ids[0]
        out = np.zeros(W, bool)
        x = 0
        while x < W:
            if not sea[x]:
                x += 1
                continue
            s = x
            while x < W and sea[x]:
                x += 1
            run = list(range(s, x))
            if s == 0 or x == W:                 # the run may go on across the east-west seam
                continue
            left, right = state.get(int(top[s - 1])), state.get(int(top[x % W]))
            if len(run) <= BRIDGE_GAP and left and left == right and russia[s]:
                out[run] = True
        # the run that crosses the seam: from the last land at the east end to the first land at the west end
        e = W - 1
        while sea[e]:
            e -= 1
        b = 0
        while sea[b]:
            b += 1
        if W - 1 - e + b <= BRIDGE_GAP and state.get(int(top[e])) and state.get(int(top[e])) == state.get(int(top[b])):
            out[e + 1:] = True
            out[:b] = True
        return np.broadcast_to(out, (BRIDGE_ROWS, W))

    def limit_to_mass(self, zones, land, states, which, raster):
        """States with a "masa" point only take the land mass around that point: elsewhere their pixels go to the
        states whose zones come next. Narrow straits are opened first, so two masses do not merge across them."""
        masses = [n for n, i in enumerate(which) if states[i]['mass']]
        if not masses:
            return zones, np.zeros(land.shape, bool)
        free = self.zones(states, [i for i in which if not states[i]['mass']], raster)
        free = np.where(free > 0, np.array([0] + [n + 1 for n, i in enumerate(which) if not states[i]['mass']])[free],
                        0)
        # each land pixel belongs to the nearest core of the land eroded past its narrow straits
        core, _ = label(binary_erosion(land, iterations=3))
        mine = set()
        for n in masses:
            r, c = self.geo.pixel(*states[which[n]]['mass'][0])
            if 0 <= r < land.shape[0] and core[r, c]:
                mine.add(int(core[r, c]))
        # only big masses compete with the chosen one; islets go to whichever big mass is nearer
        sizes = np.bincount(core.ravel())
        rivals = (sizes >= 2000) | np.isin(np.arange(len(sizes)), list(mine))
        rivals[0] = False
        _, idx = distance_transform_edt(~rivals[core], return_indices=True)
        nearest = core[idx[0], idx[1]]
        # islets go with the big mass whose land is nearest
        comps, _ = label(land)
        csize = np.bincount(comps.ravel())
        big = land & (csize[comps] >= 2000)
        _, idx = distance_transform_edt(~big, return_indices=True)
        small = land & ~big
        nearest[small] = nearest[idx[0][small], idx[1][small]]
        own = land & np.isin(nearest, list(mine))
        # a sea channel four pixels wide keeps the mass apart from its neighbours (Nares Strait)
        cut = land & ~own & binary_dilation(own, iterations=4)
        # islets left a few pixels off the mass's coast (also those the channel cut loose) go with it
        comps, _ = label(land & ~cut & ~own)
        csize = np.bincount(comps.ravel())
        close = np.unique(comps[binary_dilation(own, iterations=8) & (comps > 0) & (csize[comps] < 300)])
        own |= np.isin(comps, close[close > 0])
        mass_state = np.isin(zones, [n + 1 for n in masses])
        out = np.where(mass_state & ~own, free, zones)
        # land of the mass outside its states' boxes, and in no other state's box, takes the nearest of those states
        # (Svalbard's islands lie nearer Greenland than any other big land, but they are Svalbard's)
        stray = own & ~mass_state & (free == 0)
        if stray.any():
            _, idx = distance_transform_edt(~(mass_state & own), return_indices=True)
            out[stray] = zones[idx[0][stray], idx[1][stray]]
        return out, cut

    def neighbours(self, rows=(slice(None),)):
        """Pairs of different provinces that touch within the given row slices (the map wraps east to west)."""
        pairs = set()
        for sl in rows:
            a = self.ids[sl]
            for x, y in ((a[:, :-1], a[:, 1:]), (a[:-1], a[1:]), (a[:, -1:], a[:, :1])):
                m = x != y
                for p, q in set(zip(x[m].tolist(), y[m].tolist())):
                    pairs.add((p, q))
                    pairs.add((q, p))
        return pairs

    def new_rows(self):
        """The row slices that can hold new provinces or their neighbours."""
        return slice(0, NORTH + CARVE_ROWS + 1), slice(NORTH + H - 1, TOTAL)

    def join_sea_regions(self):
        """HOI4 refuses a sea region in pieces: provinces cut off from the rest of their region join the
        neighbouring new region they touch most."""
        adj = {}
        for p, q in self.neighbours(self.new_rows()):
            if p in self.sea_of and q in self.sea_of:
                adj.setdefault(p, set()).add(q)
        for _ in range(10):
            moved = False
            for zi in range(len(self.seas)):
                left = {p for p, z in self.sea_of.items() if z == zi}
                parts = []
                while left:
                    seen = {left.pop()}
                    stack = list(seen)
                    while stack:
                        for q in adj.get(stack.pop(), ()):
                            if q in left:
                                left.discard(q)
                                seen.add(q)
                                stack.append(q)
                    parts.append(seen)
                parts.sort(key=len, reverse=True)
                for part in parts[1:]:
                    others = [self.sea_of[q] for p in part for q in adj.get(p, ()) if self.sea_of[q] != zi]
                    if others:
                        target = max(set(others), key=others.count)
                        for p in part:
                            self.sea_of[p] = target
                        moved = True
            if not moved:
                return

    def objects(self):
        """bounding slices of every new province id."""
        base = self.md.max_province
        rel = np.where(self.ids > base, self.ids - base, 0)
        return {i + base: sl for i, sl in enumerate(find_objects(rel), 1) if sl is not None}

    def interior(self, pid, sl):
        """Pixel deepest inside the province (never in the sea, even on thin islands)."""
        m = self.ids[sl] == pid
        d = distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1]
        r, c = np.unravel_index(d.argmax(), d.shape)
        return r + sl[0].start, c + sl[1].start


# ---------------------------------------------------------------- Writing the files

def new_colors(md, n, rng):
    used = set(md.ids)
    out = []
    while len(out) < n:
        c = tuple(int(v) for v in rng.integers(1, 255, 3))
        k = (c[0] << 16) | (c[1] << 8) | c[2]
        if k not in used:
            used.add(k)
            out.append(c)
    return out


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def newline_of(data):
    return b'\r\n' if b'\r\n' in data[:2000] else b'\n'


def append_lines(md_bytes, lines):
    nl = newline_of(md_bytes)
    out = md_bytes if md_bytes.endswith(b'\n') or not md_bytes else md_bytes + nl
    return out + nl.join(l.encode('utf-8') for l in lines) + nl


def height_of(hm, r, c):
    return max(9.5, hm[r, c] / 10.0)


def shift_number(text, delta):
    """A coordinate moved by delta, written with as many decimals as it had."""
    dec = len(text.split('.')[1]) if '.' in text else 0
    return '%.*f' % (dec, float(text) + delta)


def rotate_periods(weather, months):
    """The 12 monthly weather periods with their contents moved `months` ahead (southern seasons); each period keeps
    its dates. `weather` is the whole weather={ ... } block."""
    core = weather.rstrip()
    core = core[:-1].rstrip()                       # without the block's own closing brace
    parts = core.split('period={')
    heads = [p[:p.index('}') + 1] for p in parts[1:]]
    bodies = [p[p.index('}') + 1:].rstrip() for p in parts[1:]]
    bodies = bodies[-months:] + bodies[:-months]
    return parts[0] + ''.join('period={' + h + b + '\n\t\t' for h, b in zip(heads, bodies)).rstrip() + '\n\t}'


class Writer:
    def __init__(self, md, world, rep, out, game):
        self.md, self.w, self.rep, self.out, self.game = md, world, rep, out, game
        self.files = {}           # path inside the mod -> bytes
        self.images = {}

    def put(self, rel, data):
        self.files[rel] = data

    def build(self):
        md, w = self.md, self.w
        rng = np.random.default_rng(2)
        self.objs = w.objects()
        self.colors = dict(zip(sorted(self.objs), new_colors(md, len(self.objs), rng)))
        # states whose land all went into MD's edge provinces get no id; the rest are numbered without gaps
        used = sorted(set(w.state_of.values()))
        skipped = [s['name'] for i, s in enumerate(w.states) if i not in used]
        if skipped:
            self.rep.append('Estados sin tierra nueva (su costa ya es parte de MD), se omiten: ' + ', '.join(skipped))
        self.state_ids = {si: md.max_state + 1 + n for n, si in enumerate(used)}
        names = {w.states[si]['name'] for si in used}
        regions = [ri for ri, r in enumerate(w.regions) if names & set(r['states'])]
        seas = sorted(set(w.sea_of.values()))
        empty = [s['name'] for i, s in enumerate(w.seas) if i not in seas]
        if empty:
            self.rep.append('Regiones de mar sin provincias (su zona es toda tierra), se omiten: ' + ', '.join(empty))
        self.sea_region_ids = {zi: md.max_region + 1 + n for n, zi in enumerate(seas)}
        self.land_region_ids = {ri: md.max_region + 1 + len(seas) + n for n, ri in enumerate(regions)}
        self.relocate_build()
        self.images_build()
        self.coast_build()
        self.definition()
        self.positions()
        self.history()
        self.regions_files()
        self.localisation()
        self.ambient_objects()
        self.terrain_file()
        self.adjacencies()

    # ---- MD positions that fell into pixels their province lost (carved land, filled sea)

    def relocate_build(self):
        """Nearest pixel of the same province for every lost pixel, per MD province that lost some (rows of the whole
        map: a sea province the Bering fill took whole is in the new band)."""
        md, w = self.md, self.w
        self.moved = {}
        for p in np.unique(md.idmap[w.lost]):
            rr, cc = np.nonzero(md.idmap == p)
            rr = rr + NORTH
            if int(p) in w.gone:
                rr, cc = np.r_[rr, np.nonzero(w.ids == p)[0]], np.r_[cc, np.nonzero(w.ids == p)[1]]
            r0, r1, c0, c1 = rr.min(), rr.max() + 1, cc.min(), cc.max() + 1
            keep = w.ids[r0:r1, c0:c1] == p
            if int(p) not in w.gone:          # MD's rows only, as before
                keep &= ~w.lost[r0 - NORTH:r1 - NORTH, c0:c1]
            _, idx = distance_transform_edt(~keep, return_indices=True)
            self.moved[int(p)] = (r0, c0, idx)

    def relocate(self, x, z_md):
        """(x, z) in MD's coordinates moved onto what is left of its province if it fell in a lost pixel."""
        r, c = H - 1 - int(round(z_md)), int(round(x)) % W
        if not (0 <= r < H) or not self.w.lost[r, c]:
            return None
        p = int(self.md.idmap[r, c])
        if p not in self.moved:
            return None
        r0, c0, idx = self.moved[p]
        r += NORTH
        nr, nc = idx[0][r - r0, c - c0] + r0, idx[1][r - r0, c - c0] + c0
        return float(nc), float(H - 1 - (nr - NORTH))

    # ---- images

    def band_images(self, rows, edge_row, md_hm, e, height, offset, grain):
        """Heights and terrain of a new band from the real heights e (metres); edge_row is MD's row next to it (0 for
        the north, H-1 for the south), height turns metres into MD's heightmap values, offset (per column) is how
        much higher MD draws its land right at the edge than that, and grain is the spread of MD's fine bumps."""
        w = self.w
        land, ice = w.land[rows], w.ice[rows] & w.land[rows]
        n = land.shape[0]
        d = np.arange(n)[::-1] if edge_row == 0 else np.arange(n)
        # MD's difference at the edge fades out to the north, so the land goes on at MD's height there
        hm = height(e) + offset[None] * np.exp(-d / 40.0)[:, None]
        hm = gaussian_filter(np.where(land, hm, SEA_HEIGHT).astype(np.float32), 1.0)
        bumps = gaussian_filter(np.random.default_rng(2).standard_normal(land.shape), 0.7)
        hm += np.where(land, bumps / bumps.std() * grain, 0)
        # the first rows blend into MD's edge row, so there is no step (a cliff in 3D, a line of light)
        k = np.exp(-d / 4.0)[:, None]
        hm = k * md_hm[edge_row][None].astype(np.float32) + (1 - k) * hm
        hm = np.where(land, np.maximum(hm, LAND_HEIGHT), SEA_HEIGHT)
        # MD's own northern terrain (as in its Greenland, Canada and Siberia): snow plains on ice, rock on mountains,
        # grassy hills, marsh on the flat coastal lowland and plains elsewhere
        g = gaussian_filter(e, 2.0)
        relief = np.sqrt(np.maximum(gaussian_filter(e * e, 2.0) - g * g, 0))
        tr = np.where(ice, 19, np.where((relief > MOUNTAIN_RELIEF) | (e > 900), 11,
                                        np.where(relief > HILL_RELIEF, 20, np.where((e < 30) & (relief < 8), 9, 0))))
        return np.clip(hm, 0, 255).round().astype(np.uint8), np.where(land, tr, 15).astype(np.uint8)

    def images_build(self):
        md, w = self.md, self.w
        N, S = slice(0, NORTH), slice(NORTH + H, TOTAL)
        id_to_rgb = {i: np.array(((k >> 16) & 255, (k >> 8) & 255, k & 255), np.uint8) for k, i in md.ids.items()}
        id_to_rgb.update({i: np.array(c, np.uint8) for i, c in self.colors.items()})
        uniq, inv = np.unique(w.ids, return_inverse=True)
        self.images['provinces'] = np.stack([id_to_rgb[int(i)] for i in uniq])[inv].reshape(TOTAL, W, 3)

        carve, fill, lake = w.carve, w.fill, w.lake
        hm_md = np.asarray(Image.open(md.file('map', 'heightmap.bmp'))).copy()
        tr_md = np.asarray(Image.open(md.file('map', 'terrain.bmp'))).copy()
        taper = np.zeros((H, W), bool)
        taper[:EDGE_TAPER] = md.landtype[:EDGE_TAPER] | fill[:EDGE_TAPER]
        hm_md = np.where(taper, np.broadcast_to(hm_md[EDGE_TAPER], (H, W)), hm_md)
        # real heights and colours, turned into MD's style with MD's own land in the CAL_ROWS rows next to each edge
        geo = w.geo
        e_n = geo.field_north(*load_etopo(ETOPO_NORTH))[..., 0]
        e_s = geo.field_south(*load_etopo(ETOPO_SOUTH), CAL_ROWS)[..., 0]
        cal_n = (md.landtype & ~carve & ~fill)[:CAL_ROWS]
        cal_s = md.landtype[H - CAL_ROWS:]
        height_n = height_style(e_n[NORTH:NORTH + CAL_ROWS][cal_n], hm_md[:CAL_ROWS][cal_n])
        height_s = height_style(e_s[:CAL_ROWS][cal_s], hm_md[H - CAL_ROWS:][cal_s])
        near = slice(EDGE_TAPER, EDGE_TAPER + 10)                  # MD's rows next to the north edge
        off_n = edge_offset(hm_md[near], height_n(e_n[NORTH:][near]), cal_n[near])
        near = slice(CAL_ROWS - EDGE_TAPER - 10, CAL_ROWS - EDGE_TAPER)   # and next to the south edge
        off_s = edge_offset(hm_md[H - CAL_ROWS:][near], height_s(e_s[near]), cal_s[near])
        fine = hm_md - gaussian_filter(hm_md.astype(np.float32), 2.0)
        grain_n, grain_s = fine[:CAL_ROWS][cal_n].std(), fine[H - CAL_ROWS:][cal_s].std()
        hm_n, tr_n = self.band_images(N, 0, hm_md, e_n[:NORTH], height_n, off_n, grain_n)
        hm_s, tr_s = self.band_images(S, H - 1, hm_md, e_s[CAL_ROWS:], height_s, off_s, grain_s)
        # filled sea takes the terrain of the nearest MD land; opened lakes sit at sea level
        nr, nc = wrap_nearest(md.landtype & ~carve)
        hm = np.where(carve, SEA_HEIGHT, hm_md)
        hm = np.where(lake, np.minimum(hm_md, SEA_HEIGHT), hm)
        hm = np.where(fill, np.maximum(hm_md, LAND_HEIGHT), hm)
        tr = np.where(carve | lake, 15, tr_md)
        tr = np.where(fill, tr_md[nr, nc], tr)
        self.hm = np.vstack([hm_n, hm.astype(np.uint8), hm_s])
        self.images['heightmap'] = self.hm
        self.images['terrain'] = np.vstack([tr_n, tr.astype(np.uint8), tr_s])
        rv_md = np.asarray(Image.open(md.file('map', 'rivers.bmp')))
        rv = np.where(carve | lake, 254, np.where(fill, 255, rv_md))
        self.images['rivers'] = np.vstack([np.where(w.land[N], 255, 254), rv,
                                           np.where(w.land[S], 255, 254)]).astype(np.uint8)
        ct_md = np.asarray(Image.open(md.file('map', 'cities.bmp')))
        self.images['cities'] = np.vstack([np.full((NORTH, W), 15), ct_md, np.full((SOUTH, W), 15)]).astype(np.uint8)

        carve_h = carve.reshape(H // 2, 2, W // 2, 2).any((1, 3))
        tree_md = np.asarray(Image.open(md.file('map', 'trees.bmp')))
        self.images['trees'] = np.vstack([np.zeros((NORTH // 2, W // 2)), np.where(carve_h, 0, tree_md),
                                          np.zeros((SOUTH // 2, W // 2))]).astype(np.uint8)
        nm_md = np.asarray(Image.open(md.file('map', 'world_normal.bmp')).convert('RGB'))
        # the bands' relief from their heights with MD's own formula, and MD's tilted edge rows drawn again, so the
        # light does not change in a line where MD ends
        flat = lambda n: np.broadcast_to(np.array([127, 127, 255], np.uint8), (n, W // 2, 3))
        nm = np.vstack([flat(NORTH // 2), nm_md, flat(SOUTH // 2)])
        h2 = self.hm.astype(np.float32).reshape(TOTAL // 2, 2, W // 2, 2).mean((1, 3))
        gx = (np.roll(h2, -1, 1) - np.roll(h2, 1, 1)) / 2
        gy = np.gradient(h2, axis=0)
        r = np.clip(127 - NORMAL_K * gx, 0, 255)
        g = np.clip(127 + NORMAL_K * gy, 0, 255)
        nx, ny = (r - 127) / 128, (g - 127) / 128
        b = 127 + 128 * np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
        calc = np.stack([r, g, b], -1).round().astype(np.uint8)
        redo = np.zeros(TOTAL // 2, bool)
        redo[:NORTH // 2 + EDGE_NORMAL_ROWS] = True
        redo[NORTH // 2 + H // 2:] = True
        nm[redo] = calc[redo]
        self.images['world_normal'] = nm

        # colour maps: new sea in the mean colour MD gives the sea near that edge (no streaks), new land in Blue
        # Marble's colours turned into MD's with a fit on MD's land next to the edge
        cm_md = read_dds(md.file('map', 'terrain', COLORMAPS[0] + '.dds'))
        wm_md = read_dds(md.file('map', 'terrain', COLORMAPS[1] + '.dds'))
        bm = load_blue_marble()
        c_n, c_s = halve(geo.field_north(*bm)), halve(geo.field_south(*bm, CAL_ROWS))
        hc = CAL_ROWS // 2
        cal_n = md.landtype[:CAL_ROWS].reshape(hc, 2, W // 2, 2).all((1, 3))
        cal_s = md.landtype[H - CAL_ROWS:].reshape(hc, 2, W // 2, 2).all((1, 3))
        colour_n = colour_style(c_n[NORTH // 2:NORTH // 2 + hc][cal_n], cm_md[:hc][cal_n][:, :3])
        colour_s = colour_style(c_s[:hc][cal_s], cm_md[H // 2 - hc:][cal_s][:, :3])
        # ice, north and south, in the colours of MD's Greenland ice (its snow plains)
        on_ice = cal_n & (tr_md[:CAL_ROWS:2, ::2] == 19)
        colour_ice = colour_style(c_n[NORTH // 2:NORTH // 2 + hc][on_ice], cm_md[:hc][on_ice][:, :3])
        sea_h = md.sea[::2, ::2]
        bands = []
        # (band rows, MD rows for the mean sea colour, styled colours of the band, of MD's rows next to the edge and
        # those rows' MD colours and land)
        for rows, edge, col, colour, md_col, md_cm, md_land in (
                (N, slice(0, 40), c_n[:NORTH // 2], colour_n, c_n[NORTH // 2 + 2:NORTH // 2 + 8], cm_md[2:8],
                 cal_n[2:8]),
                (S, slice(H // 2 - 40, H // 2), c_s[hc:], colour_s, c_s[hc - 8:hc - 2], cm_md[H // 2 - 8:H // 2 - 2],
                 cal_s[hc - 8:hc - 2])):
            n = (rows.stop - rows.start) // 2
            lnd = half(w.land[rows])
            near = H // 2 - 1 if rows is S else 0
            d = np.arange(n)[::-1] if rows is N else np.arange(n)
            cm = np.empty((n, W // 2, 4), np.float32)
            cm[:] = cm_md[edge][sea_h[edge]].mean(0)
            cm[..., :3][lnd] = colour(col[lnd])
            ic = half(w.ice[rows] & w.land[rows])
            cm[..., :3][ic] = colour_ice(col[ic])
            # MD's own difference from the styled colours next to the edge fades out away from it (no step)
            styled = colour(md_col.reshape(-1, 3)).reshape(md_col.shape)
            fade = np.exp(-d / 20.0)[:, None]
            for ch in range(3):
                off = edge_offset(md_cm[..., ch].astype(float), styled[..., ch], md_land)
                cm[..., ch] += np.where(lnd, off[None] * fade, 0)
            wm = np.empty((n, W // 2, 4), np.float32)
            wm[:] = wm_md[edge][sea_h[edge]].mean(0)
            # the very first rows blend from MD's edge row, column by column, so neither the land nor the water
            # shows a line where MD ends
            k = np.exp(-d / 1.5)[:, None, None]
            cm = k * cm_md[near][None].astype(np.float32) + (1 - k) * cm
            cm[..., 3] = 0
            k = np.exp(-d / 16.0)[:, None, None]
            wm = k * wm_md[near][None].astype(np.float32) + (1 - k) * wm
            bands.append((np.clip(cm, 0, 255).round().astype(np.uint8), wm.round().astype(np.uint8)))
        # filled sea in the colours of the nearest MD land
        cm_mid = cm_md.copy()
        fill_h = half(fill)
        if fill_h.any():
            hr, hc = wrap_nearest(half(md.landtype & ~carve & ~fill))
            cm_mid[fill_h] = cm_md[hr[fill_h], hc[fill_h]]
        self.images[COLORMAPS[0]] = mark_sea_in_colormap(np.vstack([bands[0][0], cm_mid, bands[1][0]]), self.hm)
        self.images[COLORMAPS[1]] = np.vstack([bands[0][1], wm_md, bands[1][1]])

    # ---- adjacency of new provinces and of MD's provinces that gain a coast

    def coast_build(self):
        """For each new land province and each MD land province that gains a coast: the sea provinces it touches
        and a coast pixel facing each."""
        md, w = self.md, self.w
        sea_ids = {i for i, l in w.is_land.items() if not l} | {i for i, t in md.type_of.items() if t == 'sea'} | \
            set(w.lakes)
        md_coastal = md.coastal()
        self.coast, self.md_coast = {}, {}
        for rows in (slice(0, NORTH + CARVE_ROWS + 2), slice(NORTH + H - 2, TOTAL)):
            full = w.ids[rows]
            base = rows.start
            cand = [int(p) for p in np.unique(full) if (int(p) in w.is_land and w.is_land[int(p)]) or
                    (int(p) <= md.max_province and md.type_of.get(int(p)) == 'land' and int(p) not in md_coastal)]
            rel = np.zeros(full.shape, np.int64)
            index = {p: n + 1 for n, p in enumerate(cand)}
            lut = np.zeros(int(full.max()) + 1, np.int64)
            for p, n in index.items():
                lut[p] = n
            rel = lut[full]
            for p, sl in zip(cand, find_objects(rel)):
                if sl is None:
                    continue
                r0, r1 = max(0, sl[0].start - 1), min(full.shape[0], sl[0].stop + 1)
                c0, c1 = max(0, sl[1].start - 1), min(W, sl[1].stop + 1)
                sub = full[r0:r1, c0:c1]
                m = sub == p
                ring = binary_dilation(m) & ~m
                touching = {}
                for r, c in np.argwhere(ring):
                    o = int(sub[r, c])
                    if o in sea_ids and o not in touching:
                        nb = np.argwhere(m[max(0, r - 1):r + 2, max(0, c - 1):c + 2])
                        rr, cc = nb[0] + [max(0, r - 1), max(0, c - 1)]
                        touching[o] = (rr + r0 + base, cc + c0)
                if p > md.max_province:
                    self.coast[p] = touching
                elif touching:
                    self.md_coast[p] = sorted(touching.items())[0]
        for p in w.is_land:
            if w.is_land[p]:
                self.coast.setdefault(p, {})

    # ---- text files

    def definition(self):
        md, w = self.md, self.w
        lines = []
        for pid, sl in sorted(self.objs.items()):
            r, g, b = self.colors[pid]
            if w.is_land[pid]:
                coastal = 'true' if self.coast[pid] else 'false'
                lines.append('%d;%d;%d;%d;land;%s;%s;%d' % (pid, r, g, b, coastal, ARCTIC_TERRAIN,
                                                           self.continent_of(pid, sl)))
            else:
                lines.append('%d;%d;%d;%d;sea;true;ocean;0' % (pid, r, g, b))
        self.new_definition = lines
        self.put('map/definition.csv', append_lines(self.md_definition(), lines))

    def md_definition(self):
        """MD's definition.csv with the opened lakes turned into coastal sea."""
        src = read_bytes(self.md.file('map', 'definition.csv'))
        nl = newline_of(src)
        out = []
        for raw in src.split(nl):
            p = raw.decode('latin-1').split(';')
            if len(p) > 7 and p[0].isdigit() and int(p[0]) in self.w.lakes:
                p[4:8] = ['sea', 'true', 'ocean', '0']
            out.append(';'.join(p).encode('latin-1'))
        return nl.join(out)

    def without_lakes(self, provs, *folder):
        """MD's files in a folder (map/strategicregions, history/states) that list one of provs (opened lakes, moved
        sea provinces), with it taken out of their provinces block and every other byte as in MD.
        Returns {relative path: bytes}."""
        out = {}
        lakes = {str(p).encode() for p in provs}
        for name in sorted(os.listdir(self.md.file(*folder))):
            src = read_bytes(self.md.file(*folder, name))
            m = re.search(rb'provinces\s*=\s*\{([^}]*)\}', src)
            if not m or not lakes & set(m.group(1).split()):
                continue
            body = re.sub(rb'(?<!\d)(%s)(?!\d)' % b'|'.join(lakes), b'', m.group(1))
            rel = '/'.join(folder + (name,))
            if os.path.exists(os.path.join(MOD, *folder, name)) and rel not in installed():
                raise SystemExit('El mod ya tiene su propio %s: no lo piso para sacar el lago.' % rel)
            out[rel] = src[:m.start(1)] + body + src[m.end(1):]
        return out

    def continent_of(self, pid, sl):
        """Continent of the nearest MD land province, looking into MD's map from the band's side."""
        md = self.md
        r, c = self.w.interior(pid, sl)
        rows = slice(0, 400) if r < NORTH else slice(H - 600, H)
        for dc in range(0, W // 2, 8):
            for cc in ((c + dc) % W, (c - dc) % W):
                hit = np.nonzero(md.landtype[rows, cc])[0]
                if len(hit):
                    rr = hit[0] if r < NORTH else hit[-1]
                    i = int(md.idmap[rows.start + rr, cc])
                    if md.continent.get(i):
                        return md.continent[i]
        return 1

    def shifted_md_lines(self, name, xf, zf):
        """MD's lines with z moved up by SOUTH and positions in carved land moved onto their province."""
        src = read_bytes(self.md.file('map', name))
        nl = newline_of(src)
        out = []
        for raw in src.split(nl):
            line = raw.decode('utf-8')
            p = line.split(';')
            if len(p) > zf:
                moved = self.relocate(float(p[xf]), float(p[zf]))
                if moved:
                    p[xf] = shift_number(p[xf], moved[0] - float(p[xf]))
                    p[zf] = shift_number(p[zf], moved[1] - float(p[zf]))
                p[zf] = shift_number(p[zf], SOUTH)
            out.append(';'.join(p).encode('utf-8'))
        return nl.join(out)

    def positions(self):
        md, w, hm = self.md, self.w, self.hm
        stacks, builds, weather = [], [], []
        self.center = {}
        for pid, sl in sorted(self.objs.items()):
            r, c = w.interior(pid, sl)
            self.center[pid] = (r, c)
            types = LAND_STACKS if w.is_land[pid] else SEA_STACKS
            stacks += ['%d;%d;%.2f;%.2f;%.2f;0.00;0.50' % (pid, t, c, height_of(hm, r, c), z_of(r)) for t in types]
        # the opened lakes had no sea positions in MD
        for pid in [p for p in w.lakes if p not in md.pos]:
            sl = find_objects((w.ids == pid).astype(np.int8))[0]
            r, c = w.interior(pid, sl)
            stacks += ['%d;%d;%.2f;%.2f;%.2f;0.00;0.50' % (pid, t, c, height_of(hm, r, c), z_of(r)) for t in SEA_STACKS]
        # buildings: per state at the centre of its largest province, per province at its centre, ports on coasts
        for si in self.state_ids:
            provs = [p for p, st in w.state_of.items() if st == si]
            big = max(provs, key=self.size)
            r, c = self.center[big]
            for b in STATE_BUILDINGS:
                builds.append('%d;%s;%.2f;%.2f;%.2f;0.00;0' % (self.state_ids[si], b, c, height_of(hm, r, c), z_of(r)))
            for p in provs:
                r, c = self.center[p]
                for b in PROVINCE_BUILDINGS:
                    builds.append('%d;%s;%.2f;%.2f;%.2f;0.00;0' % (self.state_ids[si], b, c, height_of(hm, r, c),
                                                                   z_of(r)))
                if self.coast[p]:
                    sea, (rr, cc) = sorted(self.coast[p].items())[0]
                    for b in COAST_BUILDINGS:
                        adj = sea if b in ('naval_base_spawn', 'floating_harbor') else 0
                        builds.append('%d;%s;%.2f;%.2f;%.2f;0.00;%d' % (self.state_ids[si], b, cc, 9.5, z_of(rr), adj))
        md_state = md.states_of_provinces()
        for pid, (sea, (rr, cc)) in sorted(self.md_coast.items()):
            for b in COAST_BUILDINGS:
                adj = sea if b in ('naval_base_spawn', 'floating_harbor') else 0
                builds.append('%d;%s;%.2f;%.2f;%.2f;0.00;%d' % (md_state[pid], b, cc, 9.5, z_of(rr), adj))
        for zi in self.sea_region_ids:
            provs = [p for p, s in w.sea_of.items() if s == zi]
            for p in sorted(provs, key=lambda p: -self.size(p))[:2]:
                r, c = self.center[p]
                weather.append('%d;%.2f;9.50;%.2f;big' % (self.sea_region_ids[zi], c, z_of(r)))
        for ri, reg in enumerate(w.regions):
            if ri not in self.land_region_ids:
                continue
            provs = [p for p, st in w.state_of.items() if w.states[st]['name'] in reg['states']]
            for p in sorted(provs, key=lambda p: -self.size(p))[:2]:
                r, c = self.center[p]
                weather.append('%d;%.2f;%.2f;%.2f;small' % (self.land_region_ids[ri], c, height_of(hm, r, c), z_of(r)))
        self.new_stacks, self.new_builds = stacks, builds
        new = {'unitstacks.txt': stacks, 'buildings.txt': builds, 'weatherpositions.txt': weather}
        for name, xf, zf in COORD_FILES:
            self.put('map/' + name, append_lines(self.shifted_md_lines(name, xf, zf), new[name]))

    def size(self, pid):
        return int((self.w.ids[self.objs[pid]] == pid).sum())

    def vp_province(self, v, si):
        r, c = self.w.geo.pixel(v['lon'], v['lat'])
        provs = [p for p, st in self.w.state_of.items() if st == si]
        if 0 <= r < TOTAL and self.w.ids[r, c] in provs:
            return int(self.w.ids[r, c])
        return min(provs, key=lambda p: (self.center[p][0] - r) ** 2 + (self.center[p][1] - c) ** 2)

    def history(self):
        w = self.w
        self.vp_ids = []
        for si, s in enumerate(w.states):
            if si not in self.state_ids:
                continue
            provs = sorted(p for p, st in w.state_of.items() if st == si)
            sid = self.state_ids[si]
            vps = [(self.vp_province(v, si), v) for v in w.vps if v['state'] == s['name']]
            self.vp_ids += [(p, v) for p, v in vps]
            ports = [p for p in provs if self.coast[p]]
            lines = ['state = {', '\tid = %d' % sid, '\tname = "STATE_%d" # %s' % (sid, s['en']),
                     '\tmanpower = %d' % s['manpower'], '', '\tstate_category = %s' % s['category'], '',
                     '\thistory = {']
            if s['owner']:
                lines.append('\t\towner = %s' % s['owner'])
            if vps:
                lines.append('\t\tvictory_points = {')
                lines += ['\t\t\t%d %d' % (p, v['points']) for p, v in vps]
                lines.append('\t\t}')
            lines += ['\t\tbuildings = {', '\t\t\tinfrastructure = 1']
            if vps and vps[0][0] in ports and not s['impassable']:
                lines += ['\t\t\t%d = {' % vps[0][0], '\t\t\t\tnaval_base = 1', '\t\t\t}']
            lines.append('\t\t}')
            lines += ['\t\tadd_core_of = %s' % c for c in s['cores']]
            lines += ['\t\tadd_claim_by = %s' % c for c in s['claims']]
            lines.append('\t\tset_state_flag = mdr_polar   # low disaster risk (common/scripted_effects/mdr_disasters.txt)')
            # ice keeps both economy values low, so frozen land never gives free growth
            frozen = s['category'] in ('state_inhospitable', 'state_military_base')
            lines += ['\t\tset_variable = { state_renewable_capacity_factor_modifier_var = %.3f }'
                      % (0.4 if frozen else 0.6),
                      '\t\tset_variable = { productivity_state_var = %d }' % (300 if frozen else 500), '\t}', '']
            if s['impassable']:
                lines += ['\timpassable = yes', '']
            lines += ['\tprovinces = { %s }' % ' '.join(map(str, provs)), '}', '']
            self.put('history/states/%d-%s.txt' % (sid, s['en']), '\n'.join(lines).encode('utf-8'))
        # the opened lakes are sea now: out of MD's states
        for rel, data in self.without_lakes(self.w.lakes, 'history', 'states').items():
            self.put(rel, data)

    def regions_files(self):
        md, w = self.md, self.w
        sea_src = read_bytes(md.file('map', 'strategicregions', '46-Barents Sea.txt')).decode('latin-1')
        land_src = read_bytes(md.file('map', 'strategicregions', '20-Northern Siberia.txt')).decode('latin-1')

        def weather(src):
            return src[src.index('\tweather={'):].rstrip().rstrip('}').rstrip()

        for zi, s in enumerate(w.seas):
            if zi not in self.sea_region_ids:
                continue
            rid = self.sea_region_ids[zi]
            provs = sorted([p for p, z in w.sea_of.items() if z == zi] + [p for p, z in w.lake_sea.items() if z == zi])
            # frozen in winter, open in summer (southern seas: seasons six months later)
            text = rotate_periods(weather(sea_src), 6) if s['south'] else weather(sea_src)
            periods = text.split('period={')
            for m in range(1, len(periods)):
                month = (m + 5) % 12 + 1 if s['south'] else m
                ice = 1.0 if month in (1, 2, 3, 4, 5, 12) else (0.5 if month in (6, 11) else 0.0)
                if s['name'] in ('artico_central', 'weddell', 'ross'):
                    ice = 1.0
                periods[m] = re.sub(r'arctic_water=[\d.]+', 'arctic_water=%.3f' % ice, periods[m])
            text = 'period={'.join(periods)
            body = ['strategic_region={', '\tid=%d' % rid, '\tname="STRATEGICREGION_%d"' % rid, '\tprovinces={',
                    '\t\t' + ' '.join(map(str, provs)) + ' ', '\t}', '\tnaval_terrain=%s' % s['naval'], text, '}', '']
            self.put('map/strategicregions/%d-%s.txt' % (rid, s['en']), '\n'.join(body).encode('utf-8'))
        for ri, reg in enumerate(w.regions):
            if ri not in self.land_region_ids:
                continue
            rid = self.land_region_ids[ri]
            provs = sorted(p for p, st in w.state_of.items() if w.states[st]['name'] in reg['states'])
            south = w.states[w.state_of[provs[0]]]['south']
            text = rotate_periods(weather(land_src), 6) if south else weather(land_src)
            body = ['strategic_region={', '\tid=%d' % rid, '\tname="STRATEGICREGION_%d"' % rid, '\tprovinces={',
                    '\t\t' + ' '.join(map(str, provs)) + ' ', '\t}', text, '}', '']
            self.put('map/strategicregions/%d-%s.txt' % (rid, reg['en']), '\n'.join(body).encode('utf-8'))
        # the opened lakes leave MD's land regions (they joined the new sea region at their mouth), and the sea
        # provinces moved to the new sea leave MD's sea regions
        for rel, data in self.without_lakes(list(w.lake_sea), 'map', 'strategicregions').items():
            self.put(rel, data)

    def localisation(self):
        w = self.w
        for lang, key in (('english', 'en'), ('spanish', 'es')):
            lines = ['l_%s:' % lang, ' mdr_arctic: "%s"' % ('Arctic' if key == 'en' else 'Ártico'),
                     ' mdr_arctic_desc: "%s"' % (
                         'Tundra and ice. Armies move slowly, suffer heavy attrition and fight on narrow fronts.'
                         if key == 'en' else 'Tundra y hielo. Los ejércitos avanzan lento, sufren mucho desgaste '
                         'y combaten en frentes angostos.')]
            lines += [' STATE_%d: "%s"' % (self.state_ids[i], s[key]) for i, s in enumerate(w.states)
                      if i in self.state_ids]
            lines += [' VICTORY_POINTS_%d: "%s"' % (p, v[key]) for p, v in self.vp_ids]
            lines += [' STRATEGICREGION_%d: "%s"' % (self.sea_region_ids[i], s[key]) for i, s in enumerate(w.seas)
                      if i in self.sea_region_ids]
            lines += [' STRATEGICREGION_%d: "%s"' % (self.land_region_ids[i], r[key])
                      for i, r in enumerate(w.regions) if i in self.land_region_ids]
            self.put('localisation/%s/mdr_arctic_map_l_%s.yml' % (lang, lang),
                     b'\xef\xbb\xbf' + ('\n'.join(lines) + '\n').encode('utf-8'))

    def ambient_objects(self):
        """MD's ambient_object.txt with every object moved up by SOUTH. HOI4's frames along the edges keep their
        distance to the map's own edges: the top one moves up by the whole new height, the bottom one stays. From afar
        they are hidden in pdxmesh.shader (MDR_GLOBE_FRAME_HIDE)."""
        src = read_bytes(self.md.file('map', 'ambient_object.txt')).decode('latin-1')
        pos = r'(position=\{\s*[-\d.]+\s+[-\d.]+\s+)([-\d.]+)'
        parts, last = [], 0
        for frame, delta in (('frame_border_entity', NORTH + SOUTH), ('frame_border_bottom_entity', 0)):
            m = re.search(r'type=\{\s*type="%s".*?(?=\ntype=\{)' % frame, src, re.S)
            if not m:
                raise SystemExit('No encuentro el marco %s en ambient_object.txt de MD.' % frame)
            parts.append((m.start(), m.end(), delta))
        out, last = [], 0
        for a, b, delta in sorted(parts):
            out.append(re.sub(pos, lambda m: m.group(1) + shift_number(m.group(2), SOUTH), src[last:a]))
            out.append(re.sub(pos, lambda m: m.group(1) + shift_number(m.group(2), delta), src[a:b]))
            last = b
        out.append(re.sub(pos, lambda m: m.group(1) + shift_number(m.group(2), SOUTH), src[last:]))
        text = ''.join(out)
        # The camera can go about 1300 past the map (the globe needs it): six more frames each way cover that. Each is 210 tall.
        for frame, positions in (('frame_border_entity', (2651.0, 2856.0, 3061.0, 3266.0, 3471.0, 3676.0)),
                                 ('frame_border_bottom_entity', (-345.0, -550.0, -755.0, -960.0, -1165.0, -1370.0))):
            m = re.search(r'(type=\{\s*type="%s".*?)(\r?\n\}\r?\n)' % frame, text, re.S)
            o = re.search(r'\r?\n\tobject=\{.*\}', m.group(1), re.S)
            extra = ''
            for k, z in enumerate(positions):
                copy = re.sub(r'(position=\{\s*[-\d.]+\s+[-\d.]+\s+)([-\d.]+)', lambda q: q.group(1) + '%.3f' % z, o.group(0))
                extra += re.sub(r'name="([^"]+)"', lambda q: 'name="%s_%d"' % (q.group(1), k + 2), copy)
            text = text[:m.end(1)] + extra + text[m.end(1):]
        self.put('map/ambient_object.txt', text.encode('latin-1'))

    def adjacencies(self):
        """MD's adjacencies.csv with the y of every drawn crossing moved up by SOUTH."""
        src = read_bytes(self.md.file('map', 'adjacencies.csv'))
        nl = newline_of(src)
        out = []
        for raw in src.split(nl):
            p = raw.decode('latin-1').split(';')
            if len(p) > 7 and p[0].lstrip('-').isdigit():
                for i in (5, 7):
                    if p[i] not in ('-1', ''):
                        p[i] = shift_number(p[i], SOUTH)
            out.append(';'.join(p).encode('latin-1'))
        self.put('map/adjacencies.csv', nl.join(out))

    def terrain_file(self):
        """MD's 00_terrain.txt with the Arctic terrain added as the last category; nothing else changes."""
        src = read_bytes(self.md.file('common', 'terrain', '00_terrain.txt')).decode('utf-8')
        i = src.index('{', src.index('categories = {'))
        depth = 0
        for j in range(i, len(src)):
            depth += {'{': 1, '}': -1}.get(src[j], 0)
            if depth == 0:
                break
        self.put('common/terrain/00_terrain.txt', (src[:j] + ARCTIC_CATEGORY + src[j:]).encode('utf-8'))

    # ---- saving

    def save(self, folder):
        for rel, data in self.files.items():
            p = os.path.join(folder, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, 'wb') as f:
                f.write(data)
        md = self.md
        os.makedirs(os.path.join(folder, 'map', 'terrain'), exist_ok=True)
        for name in IMAGES:
            src = Image.open(md.file('map', name + '.bmp'))
            a = self.images[name]
            im = Image.fromarray(a, 'RGB' if a.ndim == 3 else 'P')
            if src.mode == 'P':
                im.putpalette(src.getpalette())
            im.save(os.path.join(folder, 'map', name + '.bmp'))
        for name in COLORMAPS:
            write_dds(md.file('map', 'terrain', name + '.dds'), self.images[name],
                      os.path.join(folder, 'map', 'terrain', name + '.dds'))
        self.game_textures(folder)

    def game_textures(self, folder):
        """Base-game textures that MD does not replace but that follow the map's size: the two smaller water
        colour maps (half and a quarter of colormap_water_0). The base game's fog and water-shine map stays as it
        is: the game stretches it, and an uncompressed copy is refused ("larger than MAX_TEXTURE_SIZE")."""
        template = self.md.file('map', 'terrain', COLORMAPS[1] + '.dds')
        water = Image.fromarray(self.images[COLORMAPS[1]][..., [2, 1, 0, 3]], 'RGBA')
        for i, name in ((1, 'colormap_water_1'), (2, 'colormap_water_2')):
            im = water.resize((W // 2 >> i, TOTAL // 2 >> i), Image.BOX)
            write_dds_levels(template, [np.asarray(im)], os.path.join(folder, 'map', 'terrain', name + '.dds'))


def write_dds_levels(template, levels, path):
    """Uncompressed 32-bit DDS (the format of MD's colormaps) from RGBA levels, largest first."""
    b = bytearray(read_bytes(template)[:128])
    h, w = levels[0].shape[:2]
    b[12:16] = h.to_bytes(4, 'little')
    b[16:20] = w.to_bytes(4, 'little')
    b[20:24] = (w * 4).to_bytes(4, 'little')
    b[28:32] = len(levels).to_bytes(4, 'little')
    flags = int.from_bytes(b[8:12], 'little') | 0x20000
    b[8:12] = flags.to_bytes(4, 'little')
    b[108:112] = (0x1000 | (0x400008 if len(levels) > 1 else 0)).to_bytes(4, 'little')
    with open(path, 'wb') as f:
        f.write(bytes(b) + b''.join(np.ascontiguousarray(l[..., [2, 1, 0, 3]]).tobytes() for l in levels))


def read_dds(path):
    b = read_bytes(path)
    h, w = int.from_bytes(b[12:16], 'little'), int.from_bytes(b[16:20], 'little')
    if b[84:88] != b'\x00\x00\x00\x00' or int.from_bytes(b[88:92], 'little') != 32 or len(b) != 128 + w * h * 4:
        raise SystemExit('%s no es una DDS de 32 bits sin comprimir y sin mipmaps' % path)
    return np.frombuffer(b, np.uint8, offset=128).reshape(h, w, 4).copy()


def mark_sea_in_colormap(cm, hm):
    """The globe tells sea from land by this map's blue minus red (MdrGlobeSea in gfx/FX/standardfuncsgfx.fxh): the terrain's
    heights stop matching once its mesh spreads. Sea goes to MD's own sea colour, without the coasts' soft halos, and land is
    never that blue. cm is BGRA, hm the heightmap (twice as big)."""
    sea = hm.astype(np.float32).reshape(hm.shape[0] // 2, 2, W // 2, 2).mean((1, 3)) < 95
    out = cm.copy()
    out[..., :3][sea] = (142, 102, 79)
    out[..., 0][~sea] = np.minimum(out[..., 0].astype(int), out[..., 2].astype(int) + 12)[~sea]
    return out


def write_dds(src_path, pixels, path):
    """Same header as MD's file with the new height; the pixel data are rows top to bottom."""
    b = bytearray(read_bytes(src_path)[:128])
    b[12:16] = pixels.shape[0].to_bytes(4, 'little')
    with open(path, 'wb') as f:
        f.write(bytes(b) + np.ascontiguousarray(pixels).tobytes())


# ---------------------------------------------------------------- Checks

def check(md, wr, folder, rep):
    errors = []
    w = wr.w
    rep.append('')
    rep.append('Comprobaciones:')
    if W * TOTAL * 4 > MAX_TERRAIN_BUFFER - (64 << 10):    # the game had 26 KB of that buffer in use already
        errors.append('el mapa de %d x %d no entra en el búfer de terreno del juego (50 MB)' % (W, TOTAL))
    if TOTAL % 64:
        errors.append('el alto del mapa (%d) no es múltiplo de 64' % TOTAL)

    changed = w.carve | w.fill | w.lake          # the only MD pixels a build may change
    carve_h = changed.reshape(H // 2, 2, W // 2, 2).any((1, 3))
    for name in IMAGES:
        src = Image.open(md.file('map', name + '.bmp'))
        out = Image.open(os.path.join(folder, 'map', name + '.bmp'))
        hf = name in HALF
        size = (W // 2, TOTAL // 2) if hf else (W, TOTAL)
        if out.size != size or out.mode != src.mode:
            errors.append('%s: mide %s en modo %s' % (name, out.size, out.mode))
            continue
        if src.mode == 'P' and out.getpalette()[:len(src.getpalette())] != src.getpalette():
            errors.append('%s: la paleta cambió' % name)
        a, b = np.asarray(out), np.asarray(src)
        rows = slice(NORTH // 2, NORTH // 2 + H // 2) if hf else slice(NORTH, NORTH + H)
        same = (a[rows] == b) if a.ndim == 2 else (a[rows] == b).all(-1)
        allowed = carve_h.copy() if hf else changed
        if name == 'world_normal':
            allowed[:EDGE_NORMAL_ROWS] = True
        if name == 'heightmap':
            allowed[:EDGE_TAPER] = True
        if (~same & ~allowed).any():
            errors.append('%s: cambiaron píxeles de MD fuera de la costa de Siberia, Chukotka y los golfos' % name)
    for name in COLORMAPS:
        a = read_dds(os.path.join(folder, 'map', 'terrain', name + '.dds'))
        b = read_dds(md.file('map', 'terrain', name + '.dds'))
        if a.shape != (TOTAL // 2, W // 2, 4):
            errors.append('%s.dds: mide %s' % (name, a.shape[:2]))
            continue
        if name == COLORMAPS[0]:
            b = mark_sea_in_colormap(b, np.asarray(Image.open(os.path.join(folder, 'map', 'heightmap.bmp')))[NORTH:NORTH + H])
        diff =(a[NORTH // 2:NORTH // 2 + H // 2] != b).any(-1)
        if (diff & ~(half(w.fill) if name == COLORMAPS[0] else np.zeros_like(diff))).any():
            errors.append('%s.dds: cambiaron filas de MD' % name)
    for name, tw, th in (('colormap_water_1', W // 4, TOTAL // 4), ('colormap_water_2', W // 8, TOTAL // 8)):
        b = read_bytes(os.path.join(folder, 'map', 'terrain', name + '.dds'))
        if (int.from_bytes(b[16:20], 'little'), int.from_bytes(b[12:16], 'little')) != (tw, th):
            errors.append('%s.dds no mide %d x %d' % (name, tw, th))
    terrain = wr.files['common/terrain/00_terrain.txt'].decode('utf-8')
    at = terrain.index('mdr_arctic = {')
    if not terrain.index('categories = {') < at < terrain.index('\nterrain = {'):
        errors.append('00_terrain.txt: el terreno Ártico no quedó dentro de categories')
    src = read_bytes(md.file('map', 'definition.csv'))
    old = src.rstrip(b'\r\n').split(newline_of(src))
    new = wr.files['map/definition.csv'].split(newline_of(src))
    bad = [a for a, b in zip(old, new) if a != b and not (a.split(b';')[0].isdigit() and
                                                          int(a.split(b';')[0]) in w.lakes)]
    if bad or len(new) < len(old):
        errors.append('definition.csv: cambiaron líneas de MD que no son los lagos abiertos')
    for rel in wr.files:
        if rel.startswith(('history/states/', 'map/strategicregions/')) and \
                os.path.exists(md.file(*rel.split('/'))):
            for p in w.lakes:
                if re.search(rb'(?<!\d)%d(?!\d)' % p, re.search(rb'provinces\s*=\s*\{([^}]*)\}',
                                                                  wr.files[rel]).group(1)):
                    errors.append('%s todavía lista el lago %d' % (rel, p))
    regions_of = {}
    for rel, data in wr.files.items():
        if rel.startswith('map/strategicregions/'):
            for i in re.search(rb'provinces\s*=\s*\{([^}]*)\}', data).group(1).split():
                regions_of.setdefault(int(i), []).append(rel)
    for p in np.unique(md.idmap[w.fill]):
        ring = binary_dilation(w.ids == p) & (w.ids != p)
        if not any(int(q) in w.sea_of or md.type_of.get(int(q)) == 'sea' for q in np.unique(w.ids[ring])):
            errors.append('la provincia de mar %d quedó encerrada por el relleno de Chukotka' % p)
    for p in list(w.lakes) + w.gone:
        if len(regions_of.get(p, [])) != 1:
            errors.append('la provincia %d (lago abierto o mar movido) no está en exactamente una región de mar '
                          'nueva' % p)
    # HOI4 rejects a naval strategic region split in pieces ("is fractioned"): every sea region the build writes is
    # one piece
    a, b = w.ids, np.roll(w.ids, -1, 1)
    pairs = np.concatenate([np.stack([a[a != b], b[a != b]], 1), np.stack([w.ids[:-1][w.ids[:-1] != w.ids[1:]],
                                                                           w.ids[1:][w.ids[:-1] != w.ids[1:]]], 1)])
    pairs = np.unique(pairs, axis=0)
    touch = {}
    for x, y in pairs.tolist():
        touch.setdefault(x, set()).add(y)
        touch.setdefault(y, set()).add(x)
    for rel, data in wr.files.items():
        if rel.startswith('map/strategicregions/'):
            provs = {int(i) for i in re.search(rb'provinces\s*=\s*\{([^}]*)\}', data).group(1).split()}
            if not all(p in w.sea_of or p in w.lake_sea or md.type_of.get(p) == 'sea' for p in provs):
                continue
            seen, todo = set(), [min(provs)]
            while todo:
                q = todo.pop()
                if q not in seen:
                    seen.add(q)
                    todo += [n for n in touch.get(q, ()) if n in provs and n not in seen]
            if seen != provs:
                errors.append('%s quedó partida en pedazos (aisladas: %s)'
                              % (rel, ' '.join(map(str, sorted(provs - seen)[:10]))))
        ring = binary_dilation(w.ids == p) & (w.ids != p)
        if not any(int(q) in w.sea_of or md.type_of.get(int(q)) == 'sea' for q in np.unique(w.ids[ring])):
            errors.append('el lago abierto %d no toca ningún mar' % p)

    # MD's coordinate lines: same fields, z up by SOUTH; a moved position lands on its own province's land
    ids = w.ids
    for name, xf, zf in COORD_FILES:
        src = read_bytes(md.file('map', name))
        old = src.rstrip(b'\r\n').split(newline_of(src))
        new = wr.files['map/' + name].split(newline_of(src))
        bad = 0
        for a, b in zip(old, new):
            pa, pb = a.decode('utf-8').split(';'), b.decode('utf-8').split(';')
            if len(pa) <= zf:
                bad += a != b
                continue
            same = all(x == y for i, (x, y) in enumerate(zip(pa, pb)) if i not in (xf, zf)) and len(pa) == len(pb)
            dz = float(pb[zf]) - float(pa[zf])
            if not same or (abs(dz - SOUTH) > 1e-6 and wr.relocate(float(pa[xf]), float(pa[zf])) is None):
                bad += 1
        if bad:
            errors.append('%s: %d líneas de MD cambiaron más que la altura' % (name, bad))

    prov = np.asarray(Image.open(os.path.join(folder, 'map', 'provinces.bmp')).convert('RGB'))
    k = key_of(prov)
    defined = dict(md.ids)
    for line in wr.new_definition:
        p = line.split(';')
        c = (int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])
        if c in defined:
            errors.append('color repetido en la provincia %s' % p[0])
        defined[c] = int(p[0])
    present = np.unique(k)
    if any(c not in defined for c in present):
        errors.append('hay colores del mapa sin definir')
    present_ids = {defined[c] for c in present if c in defined}
    if [p for p in wr.objs if p not in present_ids]:
        errors.append('provincias nuevas sin píxeles')
    lost = [i for i in md.ids.values() if i and i not in present_ids]
    if lost:
        errors.append('provincias de MD que se quedaron sin píxeles: %s' % lost[:10])
    if sorted(wr.objs) != list(range(md.max_province + 1, md.max_province + 1 + len(wr.objs))):
        errors.append('los ids de provincias nuevas no siguen a los de MD sin huecos')

    for p, land in w.is_land.items():
        if land and p not in w.state_of:
            errors.append('provincia de tierra %d sin estado' % p)
        if not land and (p not in w.sea_of or p in w.state_of):
            errors.append('provincia de mar %d sin región o dentro de un estado' % p)
    for p, v in wr.vp_ids:
        if p not in w.state_of:
            errors.append('punto de victoria %s fuera de su estado' % v['en'])
    for line in wr.new_stacks:
        p = line.split(';')
        if ids[TOTAL - 1 - int(round(float(p[4]))), int(float(p[2]))] != int(p[0]):
            errors.append('posición de unidad fuera de la provincia %s' % p[0])
            break
    for pid, sl in wr.objs.items():
        if sl[1].stop - sl[1].start > W // 2:
            errors.append('la provincia %d cruza medio mapa (caja demasiado grande)' % pid)
    # no province may have pixels at both ends of the map: the game crashes
    md_wide = {i for i, sl in enumerate(find_objects(md.idmap), 1) if sl and sl[1].stop - sl[1].start > W // 2}
    wide = [i for i, sl in enumerate(find_objects(w.ids), 1)
            if sl and sl[1].stop - sl[1].start > W // 2 and i not in md_wide]
    if wide:
        errors.append('provincias que quedaron a los dos lados del borde del mapa: %s' % wide[:10])
    adj = {}
    for p, q in w.neighbours(w.new_rows()):
        adj.setdefault(p, set()).add(q)
    for zi in wr.sea_region_ids:
        provs = {p for p, z in w.sea_of.items() if z == zi}
        seen = {min(provs)}
        stack = list(seen)
        while stack:
            for q in adj.get(stack.pop(), ()):
                if q in provs and q not in seen:
                    seen.add(q)
                    stack.append(q)
        if seen != provs:
            errors.append('la región de mar %s quedó partida' % w.seas[zi]['name'])
    rep.append('  Provincias de MD que ahora tocan el mar nuevo y reciben puerto: %d.' % len(wr.md_coast))
    crossings = int(four_way(k).sum())
    if crossings:
        errors.append('%d cruces de cuatro provincias en un punto' % crossings)
    seam = int((w.land[NORTH - 1] != ((md.land[0] & ~w.carve[0] & ~w.lake[0]) | w.fill[0])).sum())
    rep.append('  Empalme en el borde norte: %d columnas donde la fila nueva no sigue a la última de MD.' % seam)
    if errors:
        rep += ['  ERROR: ' + e for e in errors]
    else:
        rep.append('  Todo bien: píxeles y líneas de MD iguales (salvo la altura, la costa de Siberia, Chukotka en el '
                   'corte de Bering y los golfos abiertos), colores '
                   'únicos, cada provincia nueva con píxeles, estado o región, y referencias válidas.')
    return errors


# ---------------------------------------------------------------- Report and previews

def band_fit(Aw, B, rep):
    rep.append('')
    rep.append('Coincidencia de tierra con MD en las 250 filas bajo el borde norte (1 = igual):')
    band = slice(NORTH, NORTH + 250)
    for a, b, name in SECTORS:
        x0 = int((a + 180) * W / 360) % W
        x1 = min(W, int((b + 180) * W / 360))
        sa, sb = Aw[band, x0:x1], B[band, x0:x1]
        union = (sa | sb).sum()
        rep.append('  %-28s %.2f' % (name, (sa & sb).sum() / union if union else 1.0))


def previews(out, md, land, ids=None, carve=None):
    """Whole map at a quarter of its size, and the two new bands with MD's nearest rows at full size."""
    img = np.zeros((TOTAL, W, 3), np.uint8)
    img[:] = (70, 110, 160)
    img[land] = (176, 160, 112)
    img[NORTH:NORTH + H][md.land & ~land[NORTH:NORTH + H]] = (176, 160, 112)
    new = np.ones((TOTAL, W), bool)
    new[NORTH:NORTH + H] = False
    img[new & land] = (236, 242, 248)
    if ids is not None:
        bord = ((ids != np.roll(ids, 1, 0)) | (ids != np.roll(ids, 1, 1))) & new
        img[bord] = (40, 60, 100)
    if carve is not None:
        img[NORTH:NORTH + H][carve] = (220, 70, 60)
    img[NORTH, :12] = img[NORTH + H, :12] = (255, 210, 0)
    im = Image.fromarray(img)
    paths = []
    p = os.path.join(out, 'vista_general.png')
    im.resize((W // 4, TOTAL // 4), Image.LANCZOS).save(p)
    paths.append(p)
    for x0, x1, name in CROPS:
        p = os.path.join(out, 'vista_norte_%s.png' % name)
        im.crop((x0, 0, x1, NORTH + 260)).save(p)
        paths.append(p)
    for k in range(4):
        p = os.path.join(out, 'vista_sur_%d.png' % k)
        im.crop((k * W // 4, NORTH + H - 160, (k + 1) * W // 4, TOTAL)).save(p)
        paths.append(p)
    return paths


# ---------------------------------------------------------------- Main

MANIFEST = os.path.join(HERE, 'artico', 'instalado.txt')


def installed():
    """Files of the mod that an earlier build installed."""
    if not os.path.exists(MANIFEST):
        return []
    with open(MANIFEST, encoding='utf-8') as f:
        return [l.strip() for l in f if l.strip()]


def install(staging, rep):
    backup = os.path.join(staging, 'copia_de_seguridad')
    if os.path.isdir(backup):
        shutil.rmtree(backup)
    built = os.path.join(staging, 'mod')
    manifest = MANIFEST
    new = []
    for root, _, files in os.walk(built):
        for f in files:
            new.append(os.path.relpath(os.path.join(root, f), built).replace('\\', '/'))
    old = installed()
    for rel in sorted(set(old) | set(new)):
        dst = os.path.join(MOD, rel)
        if os.path.exists(dst):
            os.makedirs(os.path.dirname(os.path.join(backup, rel)), exist_ok=True)
            shutil.copy2(dst, os.path.join(backup, rel))
            if rel not in new:
                os.remove(dst)          # generated by an earlier build, no longer part of the map
    for rel in new:
        dst = os.path.join(MOD, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(built, rel), dst)
    with open(manifest, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted(new)) + '\n')
    rep.append('')
    rep.append('Instalado en el mod (%d archivos; %d de antes ya no hacían falta y se quitaron). Copia de lo '
               'reemplazado: %s' % (len(new), len(set(old) - set(new)), backup))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paso', choices=['vista-previa', 'construir', 'instalar'])
    ap.add_argument('--md', default=os.path.join(MOD, '..', 'Millennium-Dawn-2.0.3'))
    ap.add_argument('--juego', default=GAME, help='carpeta del juego base')
    ap.add_argument('--salida', default=os.path.join(tempfile.gettempdir(), 'mdr_mapa'))
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    os.makedirs(args.salida, exist_ok=True)
    md = MD(os.path.abspath(args.md))
    rep = ['Construcción del Ártico y la Antártida para Realpolitik', 'MD: ' + md.path,
           'Mapa: %d x %d (norte %d filas, MD %d, sur %d).' % (W, TOTAL, NORTH, H, SOUTH), '']
    data = load_data()
    geo = Geo(md, rep)
    world = World(md, geo, data, rep)
    band_fit(world.Aw, geo.B, rep)
    errors = []
    if args.paso == 'vista-previa':
        paths = previews(args.salida, md, world.land, world.ids, world.carve)
    else:
        wr = Writer(md, world, rep, args.salida, args.juego)
        wr.build()
        built = os.path.join(args.salida, 'mod')
        if os.path.isdir(built):
            shutil.rmtree(built)
        wr.save(built)
        errors = check(md, wr, built, rep)
        paths = previews(args.salida, md, world.land, world.ids, world.carve)
        if args.paso == 'instalar':
            if errors:
                rep.append('')
                rep.append('No se instaló nada: hay errores.')
            else:
                install(args.salida, rep)
    with open(os.path.join(args.salida, 'informe.txt'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(rep) + '\n')
    print('\n'.join(rep))
    print('\nVistas previas:\n  ' + '\n  '.join(paths))
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
