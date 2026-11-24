# Previews of every colony window, reusing mock_colonia.py with the names of each colony.
# Run from the mod folder: python herramientas/vista_espacio/mock_colonias.py herramientas/vista_espacio [moon mars ...]
import sys

sys.path.insert(0, "herramientas")
import space_colony as sc

sp_dir = sys.argv[1]
keys = sys.argv[2:] or [c[0] for c in sc.COLONIES]
src = open(sp_dir + "/mock_colonia.py", encoding="utf-8").read()
for key in keys:
    colony = next(c for c in sc.COLONIES if c[0] == key)
    sc.setup(colony)
    code = src.replace("mdr_col_mars", f"mdr_col_{key}").replace("mdr_mars", f"mdr_{key}").replace("MDR_MARS", f"MDR_{key.upper()}")
    code = code.replace("colonia_marte_mock.png", f"colonia_{key}_mock.png")
    code = code.replace("import space_colony as sc\n", "import space_colony as sc\nsc.setup(COLONY_FOR_MOCK)\n")
    sys.argv = ["mock_colonia.py", sp_dir]
    exec(compile(code, f"mock_{key}", "exec"), {"COLONY_FOR_MOCK": colony, "__name__": "__main__"})
