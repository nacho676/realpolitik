# Builds a test mod whose map is MD_Realismo's map padded to 3072 rows (top rows copy the top edge),
# and a copy of hoi4.exe whose scratch buffer is 128 MB instead of 50 MB.
import os, struct, shutil, sys
import pefile

DOCS = __import__("os").environ.get("HOI4_DOCS", __import__("os").path.expanduser("~/Documents/Paradox Interactive/Hearts of Iron IV"))
SRC = os.path.join(DOCS, "mod", "MD_Realismo", "map")
OUT = os.path.join(DOCS, "mod", "MDR_prueba_mapa")
GAME = __import__("os").environ.get("HOI4_DIR", "C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV").replace("\\", "/").rstrip("/")
ROWS = int(sys.argv[1]) if len(sys.argv) > 1 else 3072
NEW_SIZE = 0x8000000

def pad_bmp(name):
    b = bytearray(open(os.path.join(SRC, name), "rb").read())
    off, = struct.unpack_from("<I", b, 10)
    w, h = struct.unpack_from("<ii", b, 18)
    bpp, = struct.unpack_from("<H", b, 28)
    stride = (w * bpp // 8 + 3) & ~3
    target = ROWS * w // 5632
    top = b[off + (h - 1) * stride: off + h * stride]   # bottom-up: last row is the top
    body = b[:off + h * stride] + top * (target - h)
    struct.pack_into("<i", body, 22, target)
    struct.pack_into("<I", body, 34, stride * target)
    struct.pack_into("<I", body, 2, len(body))
    return bytes(body)

def pad_dds(name):
    b = open(os.path.join(SRC, name), "rb").read()
    h, w, pitch = struct.unpack_from("<III", b, 12)
    target = ROWS * w // 5632
    hdr = bytearray(b[:128])
    struct.pack_into("<I", hdr, 12, target)
    struct.pack_into("<I", hdr, 28, 1)   # level 0 only
    top = b[128:128 + pitch]             # top-down: first row is the top
    return bytes(hdr) + top * (target - h) + b[128:128 + pitch * h]

def build_mod():
    os.makedirs(os.path.join(OUT, "map", "terrain"), exist_ok=True)
    for f in os.listdir(SRC):
        if f.endswith(".bmp"):
            open(os.path.join(OUT, "map", f), "wb").write(pad_bmp(f))
    for f in os.listdir(os.path.join(SRC, "terrain")):
        if f.endswith(".dds"):
            open(os.path.join(OUT, "map", "terrain", f), "wb").write(pad_dds(os.path.join("terrain", f)))
    desc = 'version="1"\nname="MDR prueba mapa"\nsupported_version="1.19.*"\n'
    open(os.path.join(OUT, "descriptor.mod"), "w").write(desc)
    open(os.path.join(DOCS, "mod", "MDR_prueba_mapa.mod"), "w").write(
        desc + f'path="{OUT.replace(os.sep, "/")}"\n')

def build_exe():
    src = os.path.join(GAME, "hoi4.exe")
    dst = os.path.join(GAME, "hoi4_mapa_grande.exe")
    pe = pefile.PE(src, fast_load=True)
    data = bytearray(open(src, "rb").read())
    o = pe.get_offset_from_rva(0x22187CA)
    old = bytes.fromhex("C78750030000 00002003 B9 00002003")
    assert data[o:o + len(old)] == old, data[o:o + 16].hex()
    struct.pack_into("<I", data, o + 6, NEW_SIZE)
    struct.pack_into("<I", data, o + 11, NEW_SIZE)
    open(dst, "wb").write(data)
    print("exe", dst)

build_mod()
build_exe()
print("rows", ROWS)
