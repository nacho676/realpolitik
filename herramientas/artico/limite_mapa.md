# Límite de tamaño del mapa en HOI4 1.19.2 (Operation Postern, a729)

Conclusión: el área del mapa (ancho × alto) no puede pasar de 13.107.200 píxeles. Con el ancho de Millennium Dawn
(5632) eso da un máximo de 2327 filas. MD usa 2048, así que quedan unas 279. Además el alto tiene que ser múltiplo
de 64 (si no, el juego avisa "Topology texture width and height must both be factors of 64" y se cierra): el máximo
que sirve es 2304, 256 filas más que MD.
El límite está escrito como número fijo dentro de hoi4.exe. Ningún define, ajuste ni parámetro de arranque lo cambia.

## Cómo se comprobó

1. Mapa de 5632 × 2560: el juego carga la historia (2000.01.01) y crashea al armar los gráficos del mapa.
   Crash: EXCEPTION_ACCESS_VIOLATION (escritura) en hoi4.exe + 0x124AF11 (`mov [r12], al`).
   Pila: pdxmaptexturegeneration.cpp, llamado desde pdxmap.cpp en la etapa LOAD_GFX_PDXMAP_TEXTURES.
2. Ese código arma una textura de terreno de 4 bytes por píxel a partir de map/terrain.bmp
   (la tabla que usa es el índice de textura de cada color de terrain.bmp de 00_terrain.txt).
3. Registros del volcado (crashes/hoi4_20261025_184639/minidump.dmp): imagen de 5632 × 2560, 8 bits;
   fila 2328, columna 2545. Bytes escritos al fallar: (2328 × 5632 + 2545) × 4 = 52.455.364
   ≈ 50 MB (52.428.800) más 26 KB ya usados.
4. El destino es el búfer de la aplicación en [CApplication + 0x348]. Se crea al iniciar el juego
   (código en hoi4.exe + 0x22187CA, dirección relativa a la base de la imagen):
       mov dword [rdi+0x350], 0x3200000   ; tamaño: 50 MB
       mov ecx, 0x3200000
       call malloc
       mov [rdi+0x348], rax
   También lo usa otro código con el aviso "nBufferSize <= CApplication::AccessInstance().GetUnsafeScratchBufferSize()".
   El número 0x3200000 es fijo en el ejecutable.
5. Prueba que descarta el resto: el mapa de MD estirado a 2560 filas, sin ninguna provincia nueva ni línea de texto
   cambiada, crashea igual en la misma dirección. Con 2304 filas (51,9 MB) carga y se juega.
6. Coincidencia con otros mods: Full World Map usa 5120 × 2560. 5120 × 2560 × 4 = 52.428.800 bytes,
   exactamente los 50 MB. Es el tamaño máximo que entra.

## Por qué no se puede tener el mundo entero sin aplastar

- Para el Ártico completo y la Antártida, con la misma escala que el resto, harían falta unas 3000 filas o más.
- Con 5632 de ancho entran solo 2327.
- Para que entren hay que achicar todo el mapa a lo ancho (por ejemplo, unos 4300 × 3000). Eso obliga a
  reescalar las 16.500 provincias de MD, que pierden forma o desaparecen; a recalcular todas las posiciones; y se
  rompe con cada actualización de MD. Ya no sería el mapa de MD.
- El único otro camino es parchear hoi4.exe (cambiar 0x3200000 en las dos instrucciones). Eso no es un mod:
  cada jugador tendría que modificar su ejecutable, y cada actualización de HOI4 lo deshace.
- Además, MD ya deforma el norte: corta Canadá en unos 63°N.

## Lo que sí se puede

- Repartir las 256 filas entre norte y sur (se usan 184 y 72).
- O todo al norte.

## Por qué no hay vuelta vertical (subir y aparecer abajo)

La vuelta horizontal está hecha en el ejecutable: el mapa, la cámara y el minimapa repiten el mundo a los costados.
No hay nada parecido en vertical: ningún define, ni en el juego base ni en MD, y el minimapa del ejecutable solo
arma copias a los costados. Los mods de "mapa completo" no dan la vuelta arriba y abajo: ponen el mundo entero
dentro de los 50 MB, con un marco en cada borde.

Una copia del ejecutable con el búfer en 128 MB (ya borrada) cargó un mapa de 5632 × 3072. Eso confirma que no hay
otro tope, pero se decidió no parchear el juego.

## Cómo quedó (herramientas/construir_mapa.py)

- **Tamaño:** 5632 × 2304 = 51,9 MB del búfer, 512 KB por debajo del tope. El alto es múltiplo de 64.
  Una prueba con 2320 filas entró en el búfer pero el juego la rechazó por no ser múltiplo de 64.
- **Norte, 184 filas:** hasta 85° N. Cada longitud usa una escala que crece de a poco desde la de MD en el borde
  (`Projection`: cuadrática), así la tierra cerca del borde de MD casi no se aplasta.
- **Sur, 72 filas:** desde el borde de MD (entre unos 40° S y 57° S, según la longitud) hasta 90° S.
  La proyección del sur se calibra con las ciudades de MD al sur de 20° S.
- **Coordenadas:** toda z de MD sube 72: buildings.txt, unitstacks.txt, weatherpositions.txt, ambient_object.txt
  y adjacencies.csv. Una búsqueda en MD y en el juego base no encontró otros archivos con coordenadas del mapa.
- **Siberia:** al este de 30° E (y en las columnas de Chukotka del otro lado del corte), las filas nuevas siguen la
  costa real. Además se recorta la tierra de MD que en la realidad es mar: 10 provincias, ~5200 píxeles, cada una
  conserva al menos su 35 % más al sur. Las posiciones que caían en lo recortado se mueven a la tierra de su
  provincia, y las provincias que ganan costa reciben puerto. Parte de la costa recta de Siberia oriental es del
  mapa de MD y no se toca.
- **Antártida:** sin dueño (Tratado Antártico), intransitable, con los reclamos reales como `add_claim_by`.
- **Marcos:** los dos marcos del borde del mapa de ambient_object.txt se corren a los bordes nuevos.
- **Provincias:** bordes irregulares como los de MD (centros por k-means y un ruido suave en la distancia). Las
  de mar se cortan por cuerpo de agua, de unos 2500 píxeles junto a la costa y 6000 mar adentro, y cada una va a
  la región que tiene la mayor parte. Las provincias de MD cortadas en el borde, de tierra y de mar, crecen en un
  arco de hasta 24 filas, así no queda una línea recta donde terminaba el mapa.
- **Relieve, terreno y colores:** salen de datos reales, pero con el estilo de MD:
  - alturas de ETOPO 2022 (NOAA), pasadas a valores de MD comparando con la tierra de MD de las 250 filas junto a
    cada borde, más el grano fino que tiene el relieve de MD;
  - terreno con los mismos tipos que MD usa en el norte (nieve en el hielo, roca, colinas, pantano y llanura);
  - colores de Blue Marble (NASA Earth Observatory) ajustados a la paleta de MD; el hielo, también el de la
    Antártida, con el color del hielo de Groenlandia de MD.
  Los datos están en `herramientas/artico/datos/` (`etopo_norte.npz`, `etopo_sur.npz`, `blue_marble_200407.jpg`).
- **fow_rgb_waterspec_a.dds:** queda la del juego base y el juego la estira. Una copia sin comprimir, aun con sus
  12 mipmaps, la rechaza con "larger than MAX_TEXTURE_SIZE".
