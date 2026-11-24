from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, K = 508, 248, 2

def load(n):
    return np.array(Image.open(n + '.png').convert('RGBA')).astype(float)

bg = load('generic_tank_blueprint_background')
bp = load('generic_heavy_tank_blueprint_alt')
lines = bp[..., 3] / 255.0  # line strength of the hull drawing

def fill_mask(n):
    a = load(n)
    m = (a[..., 3] > 10) & (a[..., 2] - a[..., 0] > 20)
    im = Image.fromarray((m * 255).astype('uint8')).filter(ImageFilter.MaxFilter(5))
    return np.array(im) / 255.0

def overlay_alpha(n):
    a = load(n)
    gray = (a[..., 2] - a[..., 0] <= 20) & (np.abs(a[..., 0] - a[..., 1]) < 25) & (a[..., 0] > 100) & (a[..., 0] < 200)
    al = a[..., 3] / 255.0
    al[gray] = 0  # drop grey leader lines
    return al

masks = {
    'gun': fill_mask('generic_heavy_tank_gun_alt'),
    'turret': fill_mask('generic_heavy_tank_turret_alt'),
    'susp': fill_mask('generic_heavy_tank_suspension_alt'),
}
era = np.zeros((H, W)); era[121:155, 163:378] = 1
masks['era'] = era
engine_bay = np.zeros((H, W)); engine_bay[112:150, 8:92] = 1
masks['engine'] = engine_bay
extra = {'engine': overlay_alpha('generic_tank_engine'), 'armor': overlay_alpha('generic_tank_armor')}

def new_bg():
    lum = bg[..., :3].mean(axis=2) / 255.0
    base = np.array([11, 19, 29.0]); hi = np.array([34, 58, 80.0])
    rgb = base + (lum[..., None] ** 1.3) * (hi - base) * 2.2
    return np.clip(rgb, 0, 255)

DIM = np.array([104, 128, 150.0]); CYAN = np.array([92, 228, 255.0])

def carousel():
    im = Image.new('L', (W * 4, H * 4), 0); d = ImageDraw.Draw(im)
    cx, cy, rx, ry = 198 * 4, 141 * 4, 36 * 4, 7 * 4
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=255, width=5)
    for i in range(-5, 6):
        x = cx + i * rx / 6
        d.line([x, cy - ry * 0.75, x, cy + ry * 0.75], fill=255, width=4)
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=255, width=4)
    return np.array(im.resize((W, H), Image.LANCZOS)) / 255.0

def render(parts, autoloader=False):
    rgb = new_bg()
    on = np.zeros((H, W))
    for p in parts:
        if p in masks:
            on = np.maximum(on, masks[p])
    hot = lines * on
    cold = lines * (1 - on)
    glow_src = hot.copy()
    add = []
    for p in parts:
        if p in extra:
            add.append(extra[p])
    if autoloader:
        add.append(carousel())
    for a in add:
        glow_src = np.maximum(glow_src, a)
    rgb = rgb * (1 - cold[..., None] * 0.55) + DIM * cold[..., None] * 0.55
    g = np.array(Image.fromarray((glow_src * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(3))) / 255.0
    rgb = rgb + CYAN * g[..., None] * 0.55
    rgb = rgb * (1 - glow_src[..., None]) + CYAN * glow_src[..., None]
    if not parts:
        pass
    img = Image.fromarray(np.clip(rgb, 0, 255).astype('uint8'))
    return img.resize((W * K, H * K), Image.LANCZOS)

def today():
    c = Image.fromarray(bg.astype('uint8')); c.alpha_composite(Image.fromarray(bp.astype('uint8')))
    return c.convert('RGB').resize((W * K, H * K), Image.LANCZOS)

def font(sz, bold=False):
    for f in (['bahnschrift.ttf'] if not bold else ['seguisb.ttf', 'bahnschrift.ttf']) + ['segoeui.ttf', 'arial.ttf']:
        try:
            return ImageFont.truetype('C:/Windows/Fonts/' + f, sz)
        except OSError:
            pass
    return ImageFont.load_default()

PAD = 36; PW, PH = W * K, H * K
CW = PAD * 3 + PW * 2; CH = 1560
cv = Image.new('RGB', (CW, CH), (17, 20, 24)); d = ImageDraw.Draw(cv)
d.text((PAD, 24), 'Diseñador de tanques: prueba de estilo con el T-90M', font=font(40, True), fill=(230, 236, 240))
d.text((PAD, 76), 'Solo una maqueta: no se cambió nada del juego. Plano e imágenes de MD; colores y cargador son la propuesta.',
       font=font(22), fill=(150, 160, 170))

def panel(img, x, y, title, sub):
    d.text((x, y), title, font=font(28, True), fill=(225, 230, 235))
    d.text((x, y + 36), sub, font=font(20), fill=(140, 150, 160))
    cv.paste(img, (x, y + 70))
    d.rectangle([x - 1, y + 69, x + PW, y + 70 + PH], outline=(60, 70, 80), width=2)

y1 = 130
panel(today(), PAD, y1, 'Hoy en MD', 'Azul saturado; el dibujo es igual pongas lo que pongas')
panel(render([]), PAD * 2 + PW, y1, 'Propuesta, casco vacío', 'Plano apagado: todavía no se puso ninguna pieza')

y2 = y1 + 70 + PH + 50
full = render(['gun', 'susp', 'engine'], autoloader=True)
panel(full, PAD, y2, 'Propuesta, T-90M a medio armar', 'Lo puesto se enciende; torreta y blindaje todavía apagados')

# small labels pointing at the drawing
lab = font(19)
def tag(px, py, tx, ty, text):
    X, Y = PAD + px * K, y2 + 70 + py * K
    TX, TY = PAD + tx * K, y2 + 70 + ty * K
    d.line([X, Y, TX, TY], fill=(92, 228, 255), width=2)
    w = d.textlength(text, font=lab)
    d.rectangle([TX - 6, TY - 15, TX + w + 6, TY + 13], fill=(10, 30, 42), outline=(92, 228, 255))
    d.text((TX, TY - 13), text, font=lab, fill=(200, 245, 255))
tag(198, 141, 200, 222, 'Carga automática (carrusel)')
tag(50, 40, 120, 30, 'Motor diésel V-92')
tag(430, 110, 395, 88, 'Cañón 125 mm')

# side list
lx = PAD * 2 + PW; ly = y2 + 70
d.rounded_rectangle([lx, ly, lx + PW, ly + PH], radius=8, fill=(22, 27, 33), outline=(60, 70, 80), width=2)
d.text((lx + 28, ly + 22), 'Casillas del T-90M', font=font(26, True), fill=(225, 230, 235))
rows = [
    ('Cañón principal', 'Cañón 125 mm', True),
    ('Torreta', 'Sin elegir (casilla vacía)', False),
    ('Blindaje', 'Sin elegir (casilla vacía)', False),
    ('Motor', 'Diésel V-92 (despiece arriba a la izq.)', True),
    ('Suspensión', 'Orugas, 6 ruedas por lado', True),
    ('Cargador', 'Carga automática: carrusel nuevo', True),
    ('Munición', 'Interna: no se dibuja', False),
    ('Puesto de combate', 'Interno: no se dibuja', False),
]
yy = ly + 74
for slot, name, vis in rows:
    col = (92, 228, 255) if vis else (90, 100, 110)
    d.rounded_rectangle([lx + 28, yy + 4, lx + 46, yy + 22], radius=4, fill=col if vis else None, outline=col, width=2)
    d.text((lx + 62, yy), slot, font=font(21, True), fill=(220, 226, 232) if vis else (130, 140, 150))
    d.text((lx + 290, yy), name, font=font(21), fill=(170, 220, 235) if vis else (110, 120, 130))
    yy += 44
d.text((lx + 28, ly + PH - 44), 'Cian = puesta y visible   ·   Gris = vacía o interna', font=font(19), fill=(140, 150, 160))

# palette strip
y3 = y2 + 70 + PH + 40
d.text((PAD, y3), 'Colores propuestos', font=font(26, True), fill=(225, 230, 235))
sw = [((11, 19, 29), 'Fondo del plano', '#0B131D'), ((104, 128, 150), 'Líneas apagadas', '#688096'),
      ((92, 228, 255), 'Pieza puesta', '#5CE4FF'), ((22, 27, 33), 'Panel de datos', '#161B21')]
x = PAD
for c, n, hx in sw:
    d.rounded_rectangle([x, y3 + 44, x + 70, y3 + 104], radius=6, fill=c, outline=(80, 90, 100))
    d.text((x + 86, y3 + 48), n, font=font(21, True), fill=(220, 226, 232))
    d.text((x + 86, y3 + 76), hx, font=font(19), fill=(140, 150, 160))
    x += 500
cv = cv.crop((0, 0, CW, y3 + 130))
cv.save('t90_prueba.png')
print(cv.size)
