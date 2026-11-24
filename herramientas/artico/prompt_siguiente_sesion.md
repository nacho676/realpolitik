# Novedades y siguiente paso: Ártico corregido + Antártida

Revisé con otra sesión lo que escribiste en `herramientas/artico/limite_mapa.md`. Abajo están lo que se encontró,
lo que decidí y lo que tenés que hacer. La meta es que el mapa quede como en las imágenes de vista previa
(rutas al final): mirálas antes de empezar.

## 1. Lo que se comprobó del límite

- Tu conclusión era correcta: el único tope está en el búfer de 50 MB. Se desensambló la función que crashea,
  `hoi4.exe + 0x124AB40`. Arma la textura con el ancho y alto del mapa, no con los de terrain.bmp, así que achicar
  terrain.bmp no sirve. Tiene un modo a media resolución, pero solo se activa si el ancho supera el máximo de
  textura de la placa (16384).
- Prueba: una **copia** del ejecutable (`hoi4_mapa_grande.exe`, en la carpeta del juego) con el búfer cambiado a
  128 MB cargó un mapa de 5632 × 3072 y la partida arrancó. Con eso se ve que no hay otro límite en el
  ejecutable. El hoi4.exe original no se tocó.
- **Decisión:** no vamos a parchear el juego, porque cada jugador tendría que modificar el suyo. Todo tiene que
  entrar en 50 MB.

## 2. Problema de Rusia: la costa norte de Siberia es una línea recta

Lo vi en el juego: desde Yamal hasta Chukotka, la costa es plana, justo arriba del borde de MD.

- **Causa principal:** `seam_morph()`. En las primeras SEAM=24 filas mezcla la última fila de MD (en Siberia es
  toda tierra) con la costa real. Ahí la costa real está muy cerca del borde, así que queda aplastada.
- **Causa menor:** MD tiene un poco de tierra que en la realidad es mar.

**Arreglo aprobado:**
- Sector: de 30°E hacia el este hasta el corte de Bering (x ≈ 3113 hasta 5632).
- En las filas nuevas de ese sector, usar la costa real directamente (`Geo.A`), **sin** seam_morph.
- Recortar la tierra de MD que es mar en la realidad, pero solo:
  - en las 220 filas bajo el borde;
  - después de `binary_opening` con 4 iteraciones, para sacar el ruido de calibración;
  - y solo las zonas conectadas al mar del borde.
- Cada provincia de MD conserva al menos su 35 % más al sur, así que ninguna desaparece. En la vista previa
  quedaron 10 provincias recortadas, ~4900 px, como máximo un 15 % de una provincia.
- Después:
  - recalcular las posiciones (buildings, unitstacks) de las provincias recortadas para que caigan en tierra;
  - marcar como costeras y dar puerto a las que ganan costa;
  - adaptar la comprobación de "filas de MD idénticas" para permitir solo estos recortes.
- Código de la vista previa: `rusia_costa.py` (ruta al final).

## 3. Reparto de filas: norte comprimido + Antártida abajo

La vista previa usó 5632 × 2327: norte 179 filas, MD 2048, sur 100 filas con la Antártida de 60°S a 90°S.
**Pero 2327 no se puede usar:** trees.bmp, world_normal.bmp y los colormaps .dds miden la mitad del mapa, y
colormap_water_2.dds 1/8. El alto tiene que ser divisible por 8, y todos los mapas que funcionan tienen alto
múltiplo de 256.

- **Usá 2304 de alto total, repartido 164 norte / 92 sur**, la misma proporción que en las imágenes.
- Si querés acercarte más, probá 2320 (múltiplo de 8: por ejemplo 172 / 100). Verificá en el juego que carga, y
  si falla, volvé a 2304.

**Norte:**
- Comprimir la franja actual de 256 filas a 164, sin perder tierra: al norte de 83,6° no hay.
- Ajustar NEW, LAT_TOP y la compresión en `Projection` (`room`, `gz`).
- El arreglo de Siberia (sección 2) va dentro de esta franja.

**Sur:**
- Calibrar la proyección del sur de MD con ciudades al sur de unos 20°S (Chile, Argentina, Sudáfrica,
  Australia, Nueva Zelanda). `control_points()` hoy usa solo ciudades al norte de 40°.
- El sur de MD está comprimido: Cabo de Hornos queda unas 22 filas sobre el borde de abajo y el cabo Agulhas
  unas 73. Verificalo.
- Generalizar el script a dos franjas (arriba y abajo) con la misma lógica de costa, empalme y provincias.
- Pocas provincias grandes en el hielo. Islas subantárticas si alcanzan el tamaño mínimo: Georgias del Sur,
  Orcadas y Shetland del Sur, Kerguelen, Heard, Bouvet, Macquarie.
- Regiones estratégicas del Océano Austral.
- **Preguntame antes de crear estados:** dueños, reclamos y qué hacer con el Tratado Antártico.

**Coordenadas: lo más delicado.** HOI4 mide z desde abajo. Las filas de arriba no movían nada, pero las de
**abajo suben la z de todo el mapa de MD**:
- Sumá las filas del sur a la coordenada vertical en buildings.txt, unitstacks.txt, weatherpositions.txt y
  ambient_object.txt, en adjacencies.csv si tiene coordenadas distintas de -1, y en cualquier otro archivo con
  coordenadas de mapa. Buscalos con grep y no supongas.
- Extendé todas las imágenes por abajo: los .bmp se guardan de abajo hacia arriba y los .dds de arriba hacia
  abajo. Eso incluye las de media resolución y las de 1/4 y 1/8.

## 4. Otros arreglos
- **Rayas en el mapa de colores:** en `colormap_rgb_cityemissivemask_a.dds`, la franja ártica tiene rayas
  verticales, como si se hubiera estirado la última fila. Regenerala con colores de hielo y tundra, y revisá
  colormap_water_0.
- **fow_rgb_waterspec_a.dds** necesita sus 12 niveles de mipmap (`write_dds_levels()`). Sin ellos, el juego la
  rechaza: "larger than MAX_TEXTURE_SIZE".

## 5. Limpieza de la prueba
Preguntame si el juego está cerrado y después:
- restaurá `Documents\Paradox Interactive\Hearts of Iron IV\dlc_load.json` a
  `{"enabled_mods":["mod/Millennium_Dawn.mod","mod/MD_Realismo.mod"],"disabled_dlcs":[]}`;
- borrá `mod\MDR_prueba_mapa\` y `mod\MDR_prueba_mapa.mod`;
- preguntame si borro `hoi4_mapa_grande.exe`.

## 6. Orden
1. Limpieza.
2. Norte comprimido + arreglo de Siberia.
3. Sur: Antártida + desplazamiento de coordenadas.
4. Rayas del colormap y mipmaps de la niebla de guerra.
5. Vistas previas: mostrámelas y esperá mi OK.
6. `instalar`, probar en el juego y revisar error.log y crashes.
7. Actualizar limite_mapa.md e instalado.txt.

## Imágenes y scripts de referencia
Carpeta: `herramientas/artico/vistas/`
- `vista_mapa.png`: actual vs. propuesta del mundo entero (norte comprimido + Antártida).
- `rusia_costa.png`: Rusia ahora / cambios en rojo / resultado con la costa real.
- `vista.py`, `rusia_costa.py`: el código que generó esas vistas.
- `prueba.py`: el script del mapa estirado y del ejecutable de prueba.
