# CLAUDE.md: Millennium Dawn: Realpolitik

Guía completa del submod: qué es, cómo trabajar en él, qué sistemas tiene y dónde está cada cosa.
El detalle fino de cada dependencia con Millennium Dawn (huellas MD5, líneas exactas, pruebas) está en
[COMPATIBILIDAD.md](COMPATIBILIDAD.md). Esta guía es el mapa; COMPATIBILIDAD es el inventario.

## Qué es

Submod de realismo para **Millennium Dawn 2.0.0 (Developer Version)** de Hearts of Iron IV.
Nombre en el lanzador: "Millennium Dawn: Realpolitik" (`descriptor.mod`, versión 0.1.0).
Depende de "Millennium Dawn: Developer Version" o "Millennium Dawn: A Modern Day Mod".

- Carpeta del submod: `Documents/Paradox Interactive/Hearts of Iron IV/mod/MD_Realismo`
- Carpeta de MD (solo lectura): `.../mod/Millennium-Dawn-2.0.0`

## Reglas de trabajo (pedidas por el usuario)

1. **Nunca modificar la carpeta de Millennium Dawn.** Todo cambio va en `MD_Realismo`, como copia o como reemplazo
   con la misma ruta. El submod tiene que funcionar descargándolo y activándolo, sin hacer nada más.
2. **Responder en español** y terminar cada respuesta con `BLUF`. Ir al grano.
3. **Realismo con cuidado:** que no rompa nada de MD. Números aproximados y no redondos (por ejemplo 0,57 y no 0,5).
4. **Íconos:** los espíritus y modificadores usan ilustraciones de MD. Solo los edificios, recursos y leyes de comercio
   tienen íconos propios.
5. **Todo instantáneo:** lo que da un edificio tiene que verse apenas termina la obra, como en el juego base.
6. **No preguntar lo que se puede decidir.** Cuando el usuario pide elegir, se elige y se explica.
7. Las partidas de desarrollo pueden romperse entre versiones: no hace falta compatibilidad con partidas viejas.
8. **Ningún sistema sin IA:** cada decisión, ley o edificio nuevo lleva un `ai_will_do` o una estrategia de IA real, no `base = 0`.

## Convenciones de archivos

- Prefijo `mdr_` en todo lo propio (archivos, variables, ideas, eventos, decisiones, edificios).
- `.txt`: UTF-8 **sin** BOM, tabulaciones, llave de apertura en la misma línea.
- `.yml` de textos: UTF-8 **con** BOM. Siempre en español (`localisation/spanish/`) e inglés (`localisation/english/`).
- Comentarios del código en inglés, cortos, solo cuando explican algo que no es obvio.
- Las variables de HOI4 guardan **3 decimales**: multiplicar primero y dividir al final
  (por ejemplo `× 0,57 × presupuesto ÷ 1000`, nunca `× 0,00057`).

## Cómo carga el juego lo nuestro

| Qué | Cómo |
|---|---|
| Archivos de MD reemplazados | Misma ruta y mismo nombre en `MD_Realismo`: el nuestro gana. Cada uno está en la tabla de COMPATIBILIDAD con su huella MD5 |
| Parámetros (defines) | `common/defines/zz_mdr_defines.lua` carga después de `MD_defines.lua` por orden alfabético |
| Textos de MD | MD carga sus `localisation/*/replace/` después de los nuestros. Para pisar una clave de MD hay que ponerla en `localisation/<idioma>/replace/` (ver `mdr_replace_l_*.yml`) o copiar su archivo `replace` entero |
| Traducción de MD al español | Copias enteras de archivos de MD en `localisation/spanish/` con el mismo nombre y solo los valores traducidos |
| Árboles de enfoque | Los 99 archivos de MD están copiados solo para agregar `shared_focus = mdr_demo_root` (rama de demografía). Hay que regenerarlos con `herramientas/actualizar_arboles.ps1` en cada actualización de MD |

## Mapa de carpetas

| Carpeta | Qué hay |
|---|---|
| `common/scripted_effects/` | Toda la lógica. Un archivo `mdr_<sistema>.txt` por sistema (ver la tabla de sistemas). `mdr_00_core.txt` tiene las constantes globales, el registro de sistemas, el inicio de cada país (`mdr_country_init`) y la pasada semanal del mundo. `00_money_system.txt` es copia de MD con los ganchos de cultivos y edificios |
| `common/on_actions/mdr_on_actions.txt` | Calendario de todo: inicio, diario (solo jugadores), semanal, mensual y eventos del juego |
| `common/buildings/` | `mdr_buildings.txt` (edificios propios) y `00_buildings.txt` (copia de MD con 2 líneas) |
| `common/ideas/` | Leyes y espíritus propios, y la copia de `AA_law_economics.txt` (leyes de comercio) |
| `common/idea_tags/00_idea.txt` | Copia de MD con la categoría "Sociedad e Información" |
| `common/decisions/` | Decisiones propias y sus categorías (`categories/mdr_categories.txt`) |
| `common/dynamic_modifiers/` | Modificadores dinámicos (contaminación, tamaño de yacimientos, resistencia nacional, edificios) |
| `common/scripted_triggers/mdr_triggers.txt` | Condiciones reusables: reglas activadas (`mdr_ammo_on`, etc.), sanciones, miembros de tratados, compra de munición de la IA |
| `common/scripted_guis/` | Etiquetas de velocidad de construcción, pestaña de tratados, panel de uranio |
| `common/scripted_localisation/` | Textos dinámicos (barra de munición, días hasta llenar o vaciar) |
| `common/game_rules/mdr_game_rules.txt` | Reglas de partida del grupo "Realpolitik" |
| `common/resources/mdr_resources.txt` | Recursos nuevos: uranio (9), granos (10), tierras raras (11) |
| `common/technologies/mdr_fertilizers.txt` | Rama de 10 tecnologías de fertilizantes |
| `common/ai_strategy/` | IA de edificios, comida, uranio y tierras raras |
| `common/map_modes/` | Modos de mapa propios: contaminación, clima y suelos |
| `common/modifier_definitions/` | 3 modificadores propios: producción de munición, pesca y depósitos de munición |
| `common/opinion_modifiers/` | Leyes de comercio cerradas, cierre de estrechos |
| `common/national_focus/` | Copias de MD (ver arriba) y `mdr_demography.txt` (rama oculta de reformas demográficas) |
| `common/terrain/00_terrain.txt` | Copia de MD con el terreno nuevo `mdr_arctic` |
| `events/` | Eventos propios `mdr_*_events.txt` y `pandemics.txt` (copia de MD con el COVID histórico) |
| `history/states/` | 33 estados nuevos del Ártico y la Antártida, y 2 estados de MD modificados |
| `map/` | Mapa agrandado (Ártico y Antártida), reglas de estrechos (`adjacency_rules.txt`) y regiones nuevas |
| `interface/` | Copias de pantallas de MD (construcción, estado, comercio, economía, política, barra superior, etc.) y `mdr_realpolitik.gui`, `mdr_treaties.gui` y sus `.gfx` |
| `gfx/` | Tiras de íconos de edificios y recursos, íconos de leyes de comercio, logo, botones de colores, alertas, efectos del mapa |
| `localisation/` | Textos propios `mdr_*_l_<idioma>.yml`, reemplazos en `replace/` y la traducción de MD al español |
| `herramientas/` | Generadores que tienen que vivir con el mod (mapa del Ártico, árboles de enfoque) |

## Calendario (`mdr_on_actions.txt`)

| Cuándo | Qué corre |
|---|---|
| Al empezar (`on_startup`) | Constantes, espacios de edificios ×1,5, yacimientos de uranio, edificios de desastres, zonas de peligro, tierras de cultivo, tierras raras, clima, desastres históricos pasados, inicio de cada país, mercados mundiales |
| Cada día (solo jugadores) | Refresco de los paneles de MD, comida, munición, desalinizadoras, pestaña de tratados, alertas |
| Cada semana (cada país) | Respaldo de todo lo de inicio si faltó, ley de medios, leyes civiles, economía, militar, comida, munición, uranio, tierras raras, edificios, clima, comercio, capitulación, deserción. Y una pasada global (`mdr_weekly_global`) |
| Cada mes | Desastres, tratados, reservas, dependencia del petróleo, sociedad, heridos; y por el mundo: desastres y clima |
| Eventos del juego | Cambio de control de un estado (capitulación), general derrotado (captura), bomba nuclear (consecuencias) |

## Reglas de partida (grupo "Realpolitik")

| Regla | Opciones |
|---|---|
| COVID | Histórico (por defecto), dinámico, original de MD, desactivado |
| Desastres | Histórico, dinámico, desactivado |
| Acontecimientos internacionales | Históricos (tratados y crisis de estrechos en sus fechas reales) o dinámicos (solo por decisiones y al azar) |
| Shocks de mercado | Histórico o dinámico |
| Munición, Comida, Clima, Estrechos, Protestas (solo el estallido social) | Activado (por defecto) o desactivado |
| Modo diagnóstico | El juego se prueba solo (pruebas forzadas y control semanal de todo) y escribe en `game.log`; también muestra decisiones de prueba |

## Sistemas

| Sistema | Qué hace | Archivos |
|---|---|---|
| **Munición** | Reserva nacional en miles de cajas, en la barra superior como el combustible. La producen las fábricas militares (150 cajas por día cada una) y la guardan (20.000 + 40.000 por fábrica + depósitos). Se gasta en combate según las bajas de la semana (25 cajas por baja, con tope de 40 cajas por día cada 1.000 soldados), en maniobras todo el año (0,57 cajas por día cada 1.000 soldados según el gasto militar) y en entrenamiento solo en paz. Ocho semanas de gracia al empezar una guerra. Sin munición, castigos crecientes de ataque y defensa. Compra en el exterior con decisiones; la IA compra sola | `mdr_ammo.txt`, `mdr_ammo_decisions.txt`, `topbar.gui` |
| **Comida** | Granos en miles de toneladas: producción menos consumo más importaciones menos exportaciones, con depósitos. Mercado mundial con precio que sube y baja. Hambre si falta | `mdr_food.txt`, `mdr_wheat.txt`, `mdr_food_ai.txt` |
| **Tierras de cultivo** | Edificio que da 10 granos por nivel como recurso del estado (lo multiplican infraestructura, suelo y clima; cada fertilizante suma +1 fijo). Solo en estados con suelo cultivable. Niveles iniciales de la FAO de 2000 | `mdr_cropland*.txt`, `mdr_fertilizers.txt` |
| **Uranio** | Noveno recurso. Lo consumen las plantas de enriquecimiento de MD (2 cada una; sin él cae el combustible nuclear) y las líneas de ICBM e IRBM nucleares (1 por fábrica). Minas en cualquier estado; cada nivel cuesta más que el anterior. Mercado y precio propios, panel junto al almacenamiento. Los íconos de sus 5 investigaciones son escenas en volumen como los de munición (usan las funciones de `make_ammo_icons.py`) y los dibuja `herramientas/make_uranium_icons.py` | `mdr_uranium.txt`, `mdr_uranium_ai.txt` |
| **Tierras raras** | Undécimo recurso. Lo consumen las plantas de microchips (1 cada una) y, por fábrica, MANPADS, ATGM y módulos electrónicos de tanques, aviones, helicópteros y barcos (radares, sonares y control de tiro desde la 2.ª generación, incluidos los analógicos) (`herramientas/make_rare_earth_costs.py`). Complejos (6 por nivel, hasta 20) en cualquier estado; cada nivel cuesta más que el anterior. Historia: cuotas chinas 2010, Mountain Pass, Mount Weld. Al empezar el mundo produce unas 440 al día (73 niveles), cerca de 30% más de lo que gasta (unas 340 por las líneas de producción de 2000 y las plantas de microchips); China tiene 58% (la realidad es 80 a 87%) y los demás le compran. Cascos nuevos (copias de `MD_tank_chassis.txt`, `MD_mtg_ships.txt` y `MD_plane_airframes.txt`), por fábrica y según el año del casco: hasta 1985 no gastan, de 1986 a 2014 gastan 1, de 2015 a 2054 gastan 2 y desde 2055 gastan 3 (tanques: 1965 y 1975 en 0, 1995 en 1, 2015 y 2035 en 2, 2055 y 2075 en 3). Los aviones empiezan antes: el fuselaje de 1965 no gasta, el de 1985 (cuarta generación) gasta 1, los de 2015 y 2035 gastan 2 y los de 2055 y 2075 gastan 3. Los roles del chasis medio (SPG, IFV, APC…) y de los aviones heredan lo mismo; helicópteros y mechs no. Misiles (balísticos, nucleares, de crucero, hipersónicos y tierra-aire, copias de `MD_ballistic_missiles.txt`, `MD_nuclear_missiles.txt`, `MD_guided_missiles.txt` y `MD_sam_missile.txt`): todos gastan 1 por fábrica y los de 2045 en adelante gastan 2. Con la regla de diagnóstico, la primera semana escribe en `game.log` la oferta y la demanda mundial (`MDR REE start`) | `mdr_rare_earths*.txt`, `mdr_rare_earths_ai.txt` |
| **Edificios nuevos** | Ver la tabla de edificios | `mdr_buildings.txt` (definición y cuentas) |
| **Economía** | Situación de 2000, fondo de estabilización (rinde 3% al año), subsidios a los combustibles, control de capitales, congelamiento de precios, subsidios industriales, auge y crisis del petróleo (enfermedad holandesa). **PIB y deuda reales de 2000:** PIB del Banco Mundial (PPA) en la escala de MD (×0,859, medida contra sus PIB per cápita iniciales) mediante un factor fijo por país sobre `gdp_total` (`mdr_gdp_calibrate`, que se mide las primeras 4 semanas y queda fijo; tope 0,37 a 2,71), así el crecimiento de MD sigue igual; deuda pública con la proporción del FMI de 2000 sobre ese PIB. El tesoro de MD ya era real (reservas de 2000 ×1,46) y no se toca. El gráfico del PIB de MD se repara solo cada día si quedó en 0 (`mdr_gdp_graph_heal`). 180 países con PIB y 165 con deuda; sin datos, queda lo de MD. Datos en `herramientas/datos_economia/`, generador `herramientas/make_real_economy.py` | `mdr_economy.txt`, `mdr_economic_policy_*.txt`, `mdr_real_economy.txt` |
| **Multinacionales** | 28 empresas reales del 2000 (ExxonMobil, Shell, BP, Rio Tinto, Cogema, Nestlé, Toyota, Intel, Foxconn…) con sede y presencia de nivel 1 a 5 en otros países. Cada mes: el anfitrión cobra regalías e impuestos (37% extractivas, 23% el resto) y +0,13% de productividad por nivel; la sede cobra 21% de lo que se gana afuera. Ingreso adicional de MD. Decisiones: nacionalizar (61% de la ganancia, opinión −47 de la sede, 5 años de Riesgo de expropiación) e invitar (nivel 1, 3 años de exención). Se congelan con guerra, embargo o sanciones y a los 6 meses se van; crecen con estabilidad. IA: nacionaliza extractivas con gobiernos comunistas o nacionalistas, invita en democracias y países pobres | `mdr_mnc.txt`, `mdr_mnc_gen.txt` y `mdr_mnc_decisions.txt` (generados por `herramientas/make_mnc.py`, que tiene la tabla de empresas) |
| **Shocks de mercado** | Petróleo, granos, uranio y tierras raras con multiplicadores que suben y vuelven. Históricos (2007, 2008, 2010…) o dinámicos | `mdr_shocks.txt`, `mdr_shock_events.txt` |
| **Leyes de comercio** | Economía Aislada (`min_export = 0`: el 0% de los recursos sale al mercado, haya compradores o no, y sí puede comprar; autocracias o en guerra; Estado Rentista solo sin elecciones) y Economía de Bloque (`min_export` de 0,5 y +6% a las exportaciones). Las dos funcionan solo con porcentajes fijos, como las leyes del juego base: no tocan la opinión de nadie ni cortan el comercio con nadie. No hay opiniones comerciales propias. "Economía Cerrada" de MD pasa a llamarse Proteccionista | `AA_law_economics.txt` (copia) |
| **Estrechos** | Bab el-Mandeb, Suez, Bósforo, Malaca, Panamá, Gibraltar y Ormuz. Quien controla sus estados puede cerrarlos en guerra (máximo 120 días). El cierre corta las rutas de comercio por el mapa (`adjacency_rules.txt`) y el juego busca otra salida. Sube el petróleo. Eventos históricos: Ever Given, sequía de Panamá, ataques hutíes | `mdr_straits.txt`, `mdr_straits_decisions.txt`, `map/adjacency_rules.txt` |
| **Ley de medios** | 5 niveles, de a uno, de prensa libre a control total. Nivel inicial por país | `mdr_media_law.txt` |
| **Leyes civiles** | Reunión, sociedad civil (ONG), sindicatos y vigilancia. Las tres primeras saltan a cualquier nivel; vigilancia de a uno. Mueven las protestas de MD y un descontento oculto que puede estallar | `mdr_civil_laws.txt` (ideas y efectos) |
| **Edad de jubilación** | 60, 62, 65, 67 o 70 años, de a uno. Más edad: más mano de obra y pensiones más baratas. Subirla trae protestas y, en democracias, −3% de estabilidad | `mdr_civil_laws.txt` |
| **Demografía** | Envejecimiento en 2000 y después; rama oculta de reformas en todos los árboles de enfoque | `mdr_demography.txt` (efectos y enfoques) |
| **Clima y contaminación** | Contaminación por estado (con 12% de los vecinos), tres niveles con castigo, calentamiento global que agrava desastres, Kioto y París, modo de mapa | `mdr_climate.txt`, `mdr_climate_events.txt` |
| **Desastres** | Terremotos, tsunamis, tormentas, inundaciones, incendios, olas de calor, accidentes industriales, nucleares y tornados, con perfil de riesgo por región y temporada. Históricos o dinámicos. Centro de alerta temprana y diques los reducen | `mdr_disasters.txt`, `mdr_disaster_*.txt` |
| **COVID** | Brote histórico en Hubei en diciembre de 2019, fecha propia por país, vacunación desde diciembre de 2020 | `mdr_covid.txt`, `pandemics.txt` (copia) |
| **Tratados** | TNP, CTBT, START, INF, ABM, FACE, Cielos Abiertos, Ottawa, municiones en racimo, JCPOA, Kioto y París. Pestaña propia en "Sistemas internacionales" de MD | `mdr_treaties.txt`, `mdr_treaties_gui.txt`, `mdr_treaties.gui` |
| **Militar** | Reservas congeladas por sanciones, crisis de reclutamiento, movilización de reservistas, campañas de reclutamiento, deserción y tribunales militares, heridos que vuelven según la ley de salud de MD (15% a 40%) | `mdr_military.txt`, `mdr_military_decisions.txt` |
| **Investigaciones propias** | Munición (12, cada 10 años desde 1965), de las que un país arranca con las 3 primeras si ya tiene las armas de infantería de 1965, 1975 o 1985 (`mdr_ammo_tech_start`), Tecnología limpia (10) y Adaptación climática (7), generadas por `herramientas/make_tech_lines.py`. Los íconos de munición, tecnología limpia y adaptación son una escena distinta por investigación, en el estilo de los de fertilizantes, y los dibujan `herramientas/make_ammo_icons.py`, `make_clean_icons.py` y `make_adapt_icons.py` (`make_tech_lines.py` ya no los toca). Cada investigación tiene efectos propios: están en las listas `*_FX` del generador, y en los fertilizantes y `industry.txt` directamente. Genética tardía compensa parte de las pandemias. `common/technologies/industry.txt` es una copia de MD con esas mejoras | `mdr_ammo_techs.txt`, `mdr_green_techs.txt`, `mdr_pandemic_relief.txt` |
| **Cansancio de guerra** | De 0 a 30%, caja siempre visible en la barra superior (x = 1135, a la derecha de la experiencia aérea). Sube cada semana en guerra con las bajas por millón de habitantes, los estados propios ocupados, la falta de munición o comida y la duración; más en democracias, menos sin elecciones, con medios controlados o con mucho apoyo a la guerra. En paz baja 0,71% por semana. Castiga estabilidad, apoyo a la guerra, moral, organización, reclutamiento y reparaciones (modificador dinámico `mdr_war_exhaustion`); por encima de 15% suma descontento oculto. Las 16 guerras que MD arranca en 2000 empiezan con su cansancio (`mdr_war_exhaustion_start`: Sierra Leona 19,3%, Congo 18,2%, Eritrea 17,8%, Afganistán y Angola 17,1%, Sri Lanka 16%, Rusia 7,1%…; los rebeldes algo menos; cualquier otro en guerra 3,3%). Los 36 países con guerras en los años 90 arrancan con cansancio de posguerra (Burundi 8,2%, Rwanda 7,2%, Serbia 6,8%, Argelia 6,7%, Irak 5,8%… hasta 0,9%; Latinoamérica entre 0,9% y 3,7%), que en paz baja solo 0,07% por semana durante 5 años (marca `mdr_wex_postwar`). Aparte del cansancio "anti-bully" de MD | `mdr_war_exhaustion.txt` |
| **Capitulación** | Rendición según el territorio y la población que se conserva, el apoyo a la guerra y la estabilidad. Con el 85% del territorio no capitula aunque caiga la capital ("Resistencia nacional") | `mdr_capitulation.txt` |
| **Armas nucleares** | Reacciones del mundo, embargos, noticia, ánimo del atacado y media cosecha en el estado. **Radiación:** cada bomba mata 7,3% del estado (hasta 1,1 millones, `add_manpower` en el estado), suma 37 a la radiación del estado (`mdr_rad`, baja 6% por mes, castiga recursos y construcción) y 4,3 a la mundial (`global.mdr_rad_world`, baja 2% por mes). Con la del estado sobre 50 y la mundial sobre 30, el estado sigue perdiendo gente. Desde 10, la mundial castiga a todos los países. La noticia muestra los muertos del ataque y el total (`global.mdr_nuke_deaths_k`) | `mdr_nuclear.txt`, `mdr_radiation.txt` |
| **Panel nuclear (DEFCON)** | Quitado el 23 de noviembre de 2026 por inútil (era casi decoración). Se borraron la ventana, DEFCON, la disuasión, el arsenal real de 2000 y el botón. Copias de seguridad en la carpeta temporal de esa sesión; las reacciones a una bomba (`mdr_nuclear.txt`) siguen. La franja de botones de la barra superior quedó 55 px más larga (`mdr_topbar_background.dds`), vacía al final | `mdr_nuclear.txt` |
| **Programa espacial** | Etapas 1 a 3. Objetivos, proyectos con cola, misiones que pueden fallar, sede y personal, sector privado con 21 empresas reales (una por servicio), basura orbital, IA limitada, sistema solar, y colonias con módulos y rutas de carga (todo en tablas de `herramientas/space_program.py`). Pestaña propia con 76 tecnologías hasta 2075 (la columna Viajes espaciales abre los destinos; sus íconos son escenas dibujadas, una por tecnología, con `herramientas/make_space_tech_icons.py`, y `make_space.py` solo comprueba que estén), cuatro niveles de inicio en 2000, crear la agencia desde el menú, con nombre e insignia en una ventana igual a la de la agencia de inteligencia (el nombre se escribe con el teclado físico mediante atajos de botones fuera de pantalla: una ventana de mod no puede leer un campo de texto), edificio `mdr_spaceport` (cosmódromo, con las bases reales de 2000 en la provincia de la base cuando MD tiene ciudad cerca; modelo del silo ×1,37; sin ícono en el mapa, solo el modelo 3D; `rocket_site` de MD es para misiles), presupuesto de 0 a 5% del PBI en pasos de 0,01% (valores reales de 2000) (por encima de 1% rinde 35%), nombres reales de agencias y un menú propio con 9 páginas (Finanzas con gráfico de gasto de 5 años y contratos privados), con los gráficos de MD e iconos propios (`herramientas/make_space_icons.py`), que se abre desde una pestaña dentro de su Programa Espacial; Los satélites de MD no se tocan. El menú abre centrado y se arrastra. **Modo automático** como quinta página del menú Ajustes de automatización de MD (`herramientas/space_auto.py`). **Colonias** (Luna, Marte, Venus, Mercurio, asteroides, Calisto y Titán) en una ventana con el plano y las casillas de la estación antártica de MD, con colores, costos, luz solar y módulos propios de cada lugar: se elige casilla, módulo con flechas y "Enviar a construir" (`herramientas/space_colony.py`) | `mdr_space.txt`, `mdr_space_gui.txt`, `herramientas/make_space.py`, `make_space_gui.py`, `make_space_icons.py`, `make_space_tech_icons.py` |
| **Venta de barcos** | Clic derecho en un país → Vender barcos abre una ventana propia de 1200 × 740 (estilo del menú espacial) con encabezado de vendedor y comprador (banderas y nombres reales) y cinco pestañas (una sola ventana que se arrastra; cada elemento se oculta según la pestaña): **Transferir/Vender** (tipo, año del casco, cantidad), **Venta en lote** (varios tipos a la vez, 71% del valor), **Vender y reacondicionar** (un barco tuyo se reconstruye con un diseño de exportación: 39% del tiempo, 41% del costo), **Construir barco** (casco investigado, plano con sus ranuras reales y 4 diseños listos por función con los íconos de sus módulos, de `herramientas/ship_presets.py`, que se crean solos al entregar, o "Export 1" a "Export 12" hechos en el diseñador de MD; se entrega con `create_ship` y `creator = ROOT`; plazo según astilleros y −3,1% de producción de astilleros por pedido) y **Contratos** (avance y cancelación). Columna de operaciones en curso. Precio, regalo y probabilidad de aceptar; la oferta siempre le llega al comprador como evento (`mdr_ship_sale.2`) un día después, con la oferta congelada (`mdr_sale_p_*`); la IA acepta con la probabilidad mostrada, y el botón Enviar queda bloqueado hasta que conteste; 30 días de espera si rechaza. La IA vende a amigos y te ofrece comprar. Contexto completo en VENTA_BARCOS.md | `mdr_ship_sale.txt`, `mdr_ship_sale_actions.txt`, `herramientas/make_ship_sale.py` y `ship_data.py` (tablas, ventana y textos) |
| **Generales capturados** | Generales reales de otros países. Caen al tomar capitales o estados grandes, al derrotar su división, al capitular y al anexar (tope según el tamaño del ejército). Presos hasta el final de la guerra en un menú propio: lista a la izquierda, ficha con retrato, habilidades y rasgos, y barras de resistencia y cooperación con 6 operaciones que tardan días. Usar pide 60% de cooperación y juicio público 30% o menos de resistencia; también ejecutar y exiliar. Paz blanca o derrota: vuelven a su país | `mdr_prisoners.txt`, `herramientas/make_prisoners.pl` (ranuras y menú) |
| **Alertas** | Seis alertas en el sistema de MD: munición, comida, descontento, estrechos, uranio, tierras raras | `mdr_alerts.txt` |
| **Espacios de edificios** | Cada estado recibe una vez la mitad de su base (×1,5) y el tope sube de 80 a 104 | `mdr_00_core.txt`, `zz_mdr_defines.lua` |
| **Mapa del Ártico** | Mapa de 5632 × 2304 con 184 filas arriba (hasta 85° N) y 72 abajo (Antártida), estados polares y terreno ártico. 30 estados nuevos (1251 a 1280). Nueva Zembla, la costa del Láptev y el norte de Chukotka no son estados: su tierra se suma a las provincias de MD (opción `anexo` de `estados.txt`), así Nueva Zembla queda entera en Arcángel. Los estados costeros del norte de Groenlandia son anillos sobre la costa (opción `costa=`), como los de MD, y el casquete queda adentro. El borde con las provincias de MD es una línea ondulada suave (`edge_caps`), no una fila de arcos. **Los números de estado se asignan en orden al construir: si cambia un estado, revisar las referencias** (hoy: Svalbard 1251 en `mdr_space.txt`) | `herramientas/construir_mapa.py`, `map/`, `history/states/` |
| **Globo (en desarrollo)** | Al alejar el zoom por encima de 1800 el mapa se curva, muy despacio al principio, hasta ser una esfera a 3000. Al alejar queda de frente el lugar que se miraba, y moviendo la cámara hacia el norte o el sur se llega a los polos y se puede pasar un poco más allá. Con zoom normal no cambia nada, salvo que la cámara se puede alejar hasta unas 1300 unidades del borde del mapa (lo exige el globo). El clic con zoom lejano no coincide con lo que se ve. El mapa se enrolla como una hoja. Curvados: terreno, mar (lo pinta el terreno), fronteras, ríos, estrechos, nombres, frentes, comercio y árboles. Además: día y noche con nuestro mapa, atmósfera, y estrellas, sol y luna (`sky.shader`). De `pdxmesh.shader` solo se toca el efecto de los marcos del mapa, que se ocultan con zoom lejos; los modelos ya están ocultos a esa distancia. Apagar: `MDR_GLOBE_ON = 0` en `constants.fxh` | `gfx/FX/` (`MdrGlobePos` en `standardfuncsgfx.fxh`), `herramientas/globo_latitudes.py`, `herramientas/globo_groenlandia.py` |
| **Árbol de Mongolia** | Árbol propio (MD le daba el genérico): 123 enfoques en 7 ramas. Política con tres caminos tras los disturbios de 2008 (democracia, partido hegemónico, hombre fuerte), economía minera (Oyu Tolgoi con Rio Tinto de nuestras multinacionales o nacionalismo de los recursos, Tavan Tolgoi, trocha rusa o china, Fondo de Desarrollo Humano o Fondo del Futuro, uranio y tierras raras), estepa (dzud de 2000 al empezar y de 2010, que pega menos con reservas de forraje y seguro ganadero; distritos de ger y smog), tercer vecino, fuerzas armadas (cascos azules, Khaan Quest), identidad nacional y camino panmongol: solo con Rusia o China debilitadas (`mdr_mon_neighbor_weak`), reclamos sobre Mongolia Interior, Hulunbuir, Tuvá y Buriatia (a los países ya separados se les ofrece unirse, evento `mdr_mon.3`) y el formable Imperio Mongol (etiqueta cosmética `MDR_MON_KHANATE`: nombre, bandera azul con la llama, el sol y la luna en blanco, como la que muestra Wikipedia, de `herramientas/make_khanate_flag.py`, color de mapa en nuestra copia de `common/countries/cosmetic.txt` y un nuevo jefe de Estado, el Gran Kan Temüjin II, con rasgo propio `mdr_mon_great_khan`). Si nunca se abre, cierra con "El mundo mongol". Íconos de MD (el generador comprueba que existan) | `herramientas/make_mongolia.py` (tabla de enfoques, genera `common/national_focus/mdr_mongolia.txt` y sus textos), `mdr_mongolia.txt`, `mdr_mongolia_ideas.txt`, `mdr_mongolia_events.txt` |
| **Diagnóstico** | Decisiones de prueba y registro con la regla de diagnóstico | `mdr_diagnostics_decisions.txt` |
| **IA** | Regla "Inteligencia artificial": Normal, Mejorada (por defecto) y Experta, sin trampas (triggers `mdr_ai_improved`, `mdr_ai_expert`). **Todas:** parámetros más prudentes (avances cortos, guarnición en el frente, atacar solo descansada, motorizar al 93%), embargos que se levantan con déficit de 10 o más (salvo bomba nuclear o sanciones), y peso de IA en leyes civiles y de jubilación, política económica, tratados, diques y alerta temprana. **Mejorada:** posturas ofensiva, cuidadosa o defensiva según la fuerza enemiga, sin atacar sin munición, defensa de la capital, equipar antes de crecer, fábricas militares si falta munición, pocos búnkeres, y pedir la paz cuando pierde (evento al jugador). **Experta:** ataca con menos ventaja, más concentración, y los vecinos contienen a quien controla 1,7 veces sus estados iniciales. Con la regla de diagnóstico, cada mes una línea `MDR AI guerra` por país en guerra, resumida por `revisar_logs.pl` en "IA en guerra". Detalle y estado en `MEJORAR IA.md` | `mdr_ai.txt`, `mdr_war_ai.txt`, `mdr_ai_events.txt`, `zz_mdr_defines.lua` |

## Edificios propios (`common/buildings/mdr_buildings.txt`)

| Edificio | Tipo | Máximo | Efecto | Casilla de ícono |
|---|---|---|---|---|
| Mina de uranio | Estatal | 10 | +5 uranio por nivel (`state_resource_uranium`), hasta 10 con las 5 tecnologías de minería | 39 |
| Centro de alerta temprana | Estatal | 1 | Menos daño de desastres | 41 |
| Diques costeros | Provincial | 1 por provincia | Menos daño de tsunamis, tormentas e inundaciones | 25 (presa de MD) |
| Suelo cultivable | Marcador oculto | 1 | Permite tierras de cultivo | 43 |
| Tierras de cultivo | Estatal | 10 | +10 granos por nivel (`state_resource_wheat`) | 42 |
| Complejo de tierras raras | Estatal | 20 | +6 tierras raras por nivel (`state_resource_rare_earths`) | 44 |
| Desalinizadora | Estatal, costera | 1 | Mejora el suelo seco del estado | 46 |
| Planta de reciclaje | Estatal | 3 | +1 acero y +1 aluminio, baja la contaminación | 47 |
| Universidad regional | Estatal | 2 | +0,4% de investigación cada una (hasta 10) y crecimiento del estado | 49 |
| Acería eléctrica | Compartido | 2 | +4 acero con mucha energía | 50 |
| Centro de datos | Compartido | 5 | Mucho PBI, mucha energía; pide red de internet nivel 2 | 51 |
| Red inteligente | Compartido | 1 | Ahorra 15% de la energía de los edificios del estado (hasta 1,25 GW) | 52 |
| Puerto pesquero | Provincial, costero | 1 por provincia | Pescado para la comida | 54 |
| Depósito de munición fortificado | Provincial | 1 por provincia | +60.000 cajas de capacidad | 55 |
| Campus científico | Proyecto especial | 1 por estado | +7% a la instalación especial de su estado (hasta 3 por tipo) | 56 |

Las casillas 48 y 53 de la tira quedaron sin uso (complejo turístico y centro de ciberdefensa, borrados).
Trabajadores, PBI e impuestos de cada edificio: tabla al principio de `common/scripted_effects/mdr_buildings.txt`.
Energía: `energy_use` de MD en `country_modifiers`, que el juego multiplica por nivel.

## Interfaz cambiada

| Pantalla | Cambio |
|---|---|
| Construcción | 5 columnas. Los porcentajes de velocidad de nuestros edificios están en `mdr_construction_speeds` (`interface/mdr_realpolitik.gui`), con variantes según `nuclear_technology` y `stronghold_building_1`. Se generan con `make_speeds.pl` |
| Vista de estado | 140 px más ancha, 3 columnas de edificios estatales, 9 filas (27 casillas), grilla de espacios de 13 columnas (104) |
| Comercio y Economía | 939 px de ancho, 11 columnas de recursos, fila de precios con uranio, granos y tierras raras; el panel de Economía centrado. Bloque compacto de importación automática a la izquierda de los filtros por región (casilla, fábricas destinadas, prioridades por recurso). La compra la hace el motor: un script solo puede abrir comercio (`create_import`), no cerrarlo |
| Barra superior | Cajas de munición y comida; el dinero de MD anclado a la izquierda de la fecha |
| Política | Categoría "Sociedad e Información" con ícono propio (tira de 9 casillas) |
| Sistemas internacionales | Pestaña de tratados |
| Menú principal | Logo con "REALPOLITIK" y aviso de versión |
| Mapa | Colores de país parejos al alejar que tiñen el terreno sin tapar el relieve (`GB_RELIEF` en `constants.fxh`), lagos pintados de agua sobre el color del país (`LAKE_COLOR`), contorno entre países más suave, flechas de planes más vivas, botones y modos de mapa con colores por área |
| Diseñadores de tanques, barcos y aviones | Solo la casilla extra de recursos (`make_designer_resources.py`). El dibujo en ámbar de las piezas puestas se quitó el 23 de noviembre de 2026 (salía mal puesto); los generadores `make_designer_*.py` siguen en `herramientas/` y DISEÑO.md cuenta cómo era |

## Herramientas

- **Grafo del mod (consultar antes de buscar en los archivos):** `graphify-out/graph.json`, resumen en
  `graphify-out/GRAPH_REPORT.md`. Uso: `graphify explain "mdr_ammo_weekly"`, `graphify query "pregunta"`,
  `graphify path "A" "B"`. No se actualiza solo: después de cambiar archivos, rehacerlo con
  `uv tool run --from graphifyy python herramientas/grafo_mod.py`. No cubre las ventanas `.gui` de MD.
- **Grafo de Millennium Dawn (aparte):** `../Millennium-Dawn-2.0.0/graphify-out/graph.json` (88.000 nodos, 155 MB;
  cada consulta tarda unos 20 s). Consultar desde esa carpeta o con `--graph`. Rehacer después de cada
  actualización de MD con `... grafo_mod.py --md` (unos 5 min). Es lo único que se agrega en la carpeta de MD.
- `herramientas/make_real_buildings.py`: edificios de Realpolitik que existían en 2000 en sus estados reales (alerta temprana, desalinizadoras, reciclaje, universidades, puertos pesqueros y diques fuera de Países Bajos), sin llenar el mapa. Uranio y tierras raras se colocan en `mdr_uranium.txt` y `mdr_rare_earths_start.txt`, con niveles según la producción de 2000 (WNA y USGS).
- `herramientas/actualizar_arboles.ps1`: vuelve a copiar los árboles de enfoque de MD y agrega la rama de demografía.
  **Correr después de cada actualización de MD.**
- `herramientas/construir_mapa.py instalar`: regenera el mapa del Ártico sobre el mapa nuevo de MD. Datos y notas en
  `herramientas/artico/`. **Correr después de cada actualización de MD.**
- `herramientas/globo_latitudes.py` y después `herramientas/globo_groenlandia.py`: imprimen las funciones del globo que dicen dónde está cada punto del mapa en la Tierra. Hay que pegarlas en `standardfuncsgfx.fxh` si el mapa cambia.
- Generadores usados en las sesiones de Claude (tiras de íconos, etiquetas de construcción, pantalla de comercio, logo,
  listas de cultivos y yacimientos): `make_building_icons.ps1`, `make_speeds.pl`, `make_tradeview.pl`, `make_logo.ps1`,
  `make_rare_earths.ps1` y otros. Estaban en la carpeta temporal de la sesión, que el sistema puede borrar; si se
  necesitan otra vez, rehacerlos con la información de COMPATIBILIDAD.md o guardarlos en `herramientas/`.

## Lo que aprendimos del motor (no repetir errores)

- **Antes de copiar un archivo de MD o del juego al mod,** mirar si ya está en el mod: varias sesiones trabajan en la misma carpeta y una copia limpia pisa sus cambios.
- **Globo y pedazos que faltan:** el juego descarta lo que queda fuera de la vista plana, y lo más lejano a la cámara. La vista se ensancha con la altura hasta un límite lejano de unos 4200 (es una estimación: a 3420 casi no gana ancho y a 4300 no dibuja el mapa), y subir la cámara exige más margen porque el juego la frena según su vista. Se probó 3380, que según las cuentas deja menos nombres afuera, pero aleja demasiado la cámara: queda en 3000. El plano de lejanía sí se evita limitando la profundidad en cada shader. Lo que no se dibuja se cubre repartiendo la malla del terreno (`MdrGlobeSpreadWidth`): sus texturas la siguen, así que no se estira nada.
- **Altura del terreno:** viene en cada vértice (`VertexIn.height`), no en una textura; si la malla se mueve deja de coincidir. Para saber qué es mar sin la altura se usa el mapa de color, que `mark_sea_in_colormap` deja en un color fijo (79, 102, 142), porque traía halos junto a las costas. El mapa de tipos de terreno no sirve: océano y desierto comparten la textura 9.
- **Topes de la cámara:** alejar el zoom deja la cámara en su tope, y lo que muestra el shader depende solo de la posición de la cámara. Lo que no se quiere ver al alejar no puede estar en ese tope ni en el camino hasta él: con un margen de 500 el polo aparecía al alejar desde el norte. Con márgenes de 1300 y 1280 la cámara no se frena antes de llegar a las puntas del mapa. Y lo que siga el giro de la cámara no puede clavarse en un valor mientras ella sigue avanzando: se siente pegado. Más allá del polo el globo sigue girando (`MDR_GLOBE_PAST_POLE`).
- **Escalar el enrollado:** cualquier factor sobre el radio o las longitudes tiene que empezar en 1 cuando la curva empieza. A radio enorme, multiplicar las longitudes ensancha todo el mapa de golpe, y se ve como un cambio de tamaño a mitad del zoom.
- **Nombres en latitudes altas:** el mapa es igual de ancho a 70° que en el ecuador y la esfera no, así que las letras se aprietan. Un vértice no sabe a qué letra pertenece: no se pueden ensanchar una por una, y se desvanecen. Groenlandia es la excepción: es un solo texto en un lugar conocido, así que se le aplica la inversa de la deformación del globo (`MdrGlobeGreenlandName`).
- **Lo que el juego no dibuja también vale para los nombres:** solo manda los que entran en su vista plana, y un shader no puede pedirle más. En el globo las latitudes altas se ven más allá de esa vista, así que ahí faltan nombres según hacia dónde mire la cámara. El terreno se puede repartir; un nombre que no llega al shader, no.
- **Reloj del cielo:** `vGlobalTime` y `FoWTime` siguen corriendo en pausa (probado). Lo que frena es la hora del juego (`DayNight_Hour_SunDir.x`). El sol y la luna (`MdrNightAngle` de `sky.shader`) dan una vuelta por día con esa hora: el sol sobre el medio del día y la luna sobre la noche. Si esa hora avanza de a una, son 15° por hora y un shader no puede suavizarlo, porque no guarda memoria. Una onda de ida y vuelta da saltos chicos, pero no completa el ciclo.
- **Rendimiento de los shaders del globo:** la placa de video calcula las dos ramas de una cuenta aunque el resultado se multiplique por 0. Toda función del globo que corre por vértice o por píxel tiene que salir antes cuando `MdrGlobeBend()` es 0 (mapa plano); si no, el mapa laguea al moverlo aunque el globo no se use. Ya lo hacen `MdrGlobeSpreadShare`, `MdrGlobeNameShow`, `MdrGlobeRoll` y `MdrGlobeAtmosphere`.
- **Rendimiento del script:** no sacar y volver a poner modificadores de opinión con todos los países cada semana (el juego recalcula las relaciones). Guardar en un arreglo a quién se le puso y tocar solo lo que cambió.
- **Vueltas en un shader:** una coordenada que da la vuelta (`fmod`) entre dos vértices tira un triángulo a través de todo lo que hay en medio. Se ve como franjas estiradas.
- **Fórmulas en shaders:** los shaders usan 32 bits. Con coeficientes grandes (potencias de grado alto) se pierden grados enteros y el mapa tiembla; usar Chebyshev con Clenshaw.
- **Mapa de MD:** no es una proyección regular. Una fila no es una sola latitud (63° N en Canadá, 74° N en Rusia): para ubicar algo en la Tierra hay que usar fila y columna.
- **Agua y globo:** el agua de HOI4 son pocos cuadrados grandes con las costas recortadas por píxel. Curvada por vértices no sirve: el mar lo pinta el terreno.
- **Shaders:** `constants.fxh` es un bloque `Code` que termina en `]]`. En `standardfuncsgfx.fxh` solo el primer bloque `Code` llega a los shaders de vértices; `cam_distance` y el resto son de píxeles. `d3dcompiler_47.dll` de Windows permite compilar una función suelta sin abrir el juego.
- **Recursos de edificios:** `local_resources_<recurso>` en un edificio da un número fijo que la infraestructura **no**
  multiplica. Para que escale, usar `state_modifiers = { state_resource_<recurso> = N }`: es instantáneo y se multiplica.
  `local_resources_<recurso>_factor` dentro de un edificio no funcionó.
- **Limitar dónde se construye:** la única forma que funciona es un edificio marcador con `is_buildable = no` y
  `only_display_if_exists = yes` más `building_prerequisite` en el edificio real. El límite por terreno
  (`buildings_max_level` en `00_terrain.txt`) no frena edificios estatales. `hide_if_missing_tech` no esconde el
  marcador: lo muestra como "requiere tecnología" con máximo 0.
- **No hay aviso de construcción terminada:** no existe un `on_action` para eso. Lo que depende de un edificio tiene que
  estar en el propio edificio; un script diario siempre llega un día tarde.
- **Opinión comercial:** el modificador con `trade = yes` sobre la opinión de otro país hacia nosotros bloquea lo que nos
  vende. Para cortar las dos direcciones, aplicarlo de los dos lados, como el embargo de MD.
- **Leyes con requisito de nivel anterior:** llevan `cancel_if_invalid = no`, si no el juego las revierte solas.
- **Ilustraciones de ideas:** usar imágenes de 60×68 o 64×64. Las de 45×45 (espíritus del cuerpo de oficiales) se ven
  chicas en la barra de categorías.
- **Ventanas de MD:** cambiar la altura con un número fijo rompe el armado; mover posiciones de a una fila (37 px en la
  vista de estado) y correr todo lo de abajo.
- **Textos con `\n`:** las sustituciones con expresiones regulares fallan con el `\n` literal; usar reemplazo literal.
- **`perl -i` con `or die`:** si muere en la primera línea no cambia nada, pero no avisa qué se aplicó; verificar
  siempre el resultado.
- **IA:** la lógica de frentes y movimiento de divisiones es del programa del juego. Se puede ajustar con parámetros
  globales (`NDefines.NAI` en `zz_mdr_defines.lua`) y con estrategias condicionales (`ai_strategy`), no más.

## Cómo buscar errores

1. **Sin abrir el juego:** `perl herramientas/revisar_mod.pl` escribe `herramientas/informe_revision.txt`: llaves, codificación, textos e imágenes que faltan, efectos, eventos, modificadores y menús sin definir, variables y marcas sin usar, y copias de MD que cambiaron.
2. **Dentro del juego (automático):** con la regla de diagnóstico el juego se prueba solo, sin tocar nada (`mdr_diag_auto_daily`, llamado cada día desde `on_daily`). Durante 160 días fuerza situaciones y revisa el resultado días después: reiniciar el país, vaciar munición y comida, cerrar y reabrir Suez, cuatro shocks de mercado, un desastre, capturar un general, una oferta de barco, COVID y vacunas. Desde el día 8, cada semana corre en silencio el control completo (`mdr_diag_run`): los sistemas del jugador, todos los países y estados, y datos de MD (PBI, partidos que suman 100%). Escribe en `game.log` líneas `MDR DIAG OK`, `FALLA`, `AVISO` (puede ser casualidad) y `PRUEBA`; al día 160 abre la ventana de resumen. Un script no puede escribir en `error.log`: ahí solo escribe el motor, y `revisar_logs.pl` junta los dos. Las pruebas y los controles se agregan en `herramientas/make_diagnostico.pl` (lista `@plan` para pruebas, `@always` y `@world` para controles). La categoría de decisiones sigue para forzar algo a mano.
3. **Después de jugar:** `perl herramientas/revisar_logs.pl` escribe `herramientas/informe_logs.txt`: errores nuestros de `error.log` por sistema, resultado del diagnóstico, lo que es de MD y la velocidad (días de juego por minuto real, mes por mes, sacada de las horas de `game.log`; sirve para comparar antes y después de un cambio de rendimiento). Correrlo antes de volver a abrir el juego, porque al abrirlo se borran los registros.

## Cómo probar

1. En el lanzador, activar Millennium Dawn y Realpolitik.
2. Empezar en 2000 con la regla "Realpolitik > Modo diagnóstico: Activado".
3. Poner velocidad máxima y dejarlo solo al menos 160 días de juego (el plan de pruebas automático); para lo básico alcanza una semana.
4. Revisar `Documents/Paradox Interactive/Hearts of Iron IV/logs/error.log`: no debe haber líneas con `mdr_`.
5. Revisar `game.log`: deben aparecer "MDR core initialized" y "MDR country init".
6. Las pruebas por sistema están en la columna "Prueba tras actualizar" de COMPATIBILIDAD.md.

## Después de cada actualización de MD

1. Comparar las huellas MD5 de la tabla "Archivos de MD reemplazados" de COMPATIBILIDAD.md. Por cada una que cambió,
   copiar el archivo nuevo de MD y repetir el cambio descrito.
2. Correr `herramientas/actualizar_arboles.ps1` y `python herramientas/construir_mapa.py instalar`.
3. Volver a copiar los archivos de traducción al español y traducir las claves nuevas.
4. Seguir "Cómo probar".

## Ideas pendientes

- **IA:** escrita entera, falta probarla (ver `MEJORAR IA.md`).
- **Ideas del canal de submods de MD en Discord:** el usuario va a pegar el canal en un archivo de texto para revisarlo.
