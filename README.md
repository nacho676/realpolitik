# Millennium Dawn: Realpolitik

A realism submod for **Millennium Dawn 2.0.0 (Developer Version)** for Hearts of Iron IV.

It adds real-world 2000 economics, ammunition, food, uranium, rare earths, climate, disasters, multinational companies, straits, a space program, ship sales, captured generals, a Mongolia focus tree, and much more. Everything is designed to work alongside Millennium Dawn without breaking its systems.

## Requirements

You need one of these mods installed and enabled:

- Millennium Dawn: Developer Version
- Millennium Dawn: A Modern Day Mod

## Installation

1. Download the latest version from the **Releases** section of this repository.
2. Unzip the `realpolitik` folder into your HOI4 mod folder:
   `Documents\Paradox Interactive\Hearts of Iron IV\mod\`
3. Open the Paradox Launcher, enable **Millennium Dawn: Realpolitik** together with Millennium Dawn, and start a game.

If the mod does not appear in the launcher, check that the folder has the `descriptor.mod` file at its root.

## Game rules

Under the **Realpolitik** rule group you can choose:

| Rule | Options |
|---|---|
| COVID | Historical (default), dynamic, original MD, or disabled |
| Disasters | Historical, dynamic, or disabled |
| International events | Historical (treaties and strait crises on their real dates) or dynamic (only from decisions and chance) |
| Market shocks | Historical or dynamic |
| Ammunition, food, climate, straits, protests | Enabled (default) or disabled |
| Diagnostic mode | The game tests itself and writes to `game.log` |

## Systems

| System | What it does |
|---|---|
| **Ammunition** | National stockpile in thousands of crates, shown in the top bar. Military factories produce it, and it is used in combat, in yearly maneuvers, and in peacetime training. Without ammunition, attack and defense are penalized. Countries can buy it abroad; the AI buys on its own |
| **Food** | Grain in thousands of tons: production minus consumption, plus imports minus exports, with storage. A world market price moves up and down. Hunger if supply runs out |
| **Cropland** | A building that gives 10 grain per level. Output depends on infrastructure, soil, and climate. Fertilizers add to it. Starting levels follow FAO data from 2000 |
| **Uranium** | A ninth resource. Nuclear enrichment plants and nuclear ICBM and IRBM lines consume it. Mines in any state, with rising costs per level. Its own market and price |
| **Rare earths** | An eleventh resource. Microchip plants, and weapons and electronics in the military factories, consume it. Complexes in any state, up to 20 levels. Historical context: China's 2010 export quotas, Mountain Pass, Mount Weld. China starts with about 58% of production |
| **New buildings** | See the building table below |
| **Economy** | Situation in 2000, a stabilization fund, fuel subsidies, capital controls, price freezes, industrial subsidies, and oil booms and crises (Dutch disease). GDP and debt are calibrated to real 2000 data for about 180 countries |
| **Multinationals** | 28 real companies from 2000 (ExxonMobil, Shell, BP, Rio Tinto, Nestlé, Toyota, Intel, Foxconn…) with headquarters and presence levels in other countries. Host countries get royalties and taxes. Decisions let you nationalize or invite companies. The AI nationalizes extractive firms under communist or nationalist governments |
| **Market shocks** | Oil, grain, uranium, and rare earths with price multipliers that rise and fall. Historical (2007, 2008, 2010…) or dynamic |
| **Trade laws** | Isolated Economy and Bloc Economy. Economic protectionism (renamed from MD's "Closed Economy") |
| **Straits** | Bab el-Mandeb, Suez, Bosphorus, Malacca, Panama, Gibraltar, and Hormuz. Whoever controls their states can close them during war (up to 120 days). Closures reroute trade and raise oil prices |
| **Media law** | Five levels, from free press to total control. Starting level per country |
| **Civil laws** | Assembly, civil society, unions, and surveillance. They move protests and can trigger hidden discontent |
| **Retirement age** | 60, 62, 65, 67, or 70. Higher ages mean more workforce and cheaper pensions, but protests |
| **Demography** | Aging from 2000 onward. A hidden reform branch is added to all focus trees |
| **Climate and pollution** | Pollution per state (spreading to neighbors), three levels with penalties, global warming that worsens disasters, Kyoto and Paris, and a map mode |
| **Disasters** | Earthquakes, tsunamis, storms, floods, wildfires, heat waves, industrial, nuclear and tornado accidents, with regional and seasonal risk. Early warning centers and dikes reduce damage |
| **COVID** | Outbreak in Hubei in December 2019, with a start date for each country. Vaccines from December 2020 |
| **Treaties** | NPT, CTBT, START, INF, ABM, CFE, Open Skies, Ottawa, cluster munitions, JCPOA, Kyoto, and Paris. Its own tab in "International systems" |
| **Military** | Reserves frozen by sanctions, recruitment crises, reservist mobilization, recruitment campaigns, desertion and military courts. Wounded return based on MD's health law |
| **Research** | Own technology lines for ammunition, clean technology, and climate adaptation, plus fertilizers and late genetics that offset pandemics |
| **War exhaustion** | From 0 to 30%, always visible in the top bar. It rises with casualties, occupied territory, shortages, and war duration. It drops slowly in peace. Above 15% it adds hidden discontent |
| **Capitulation** | Surrender depends on the territory and population kept, war support, and stability. Keeping 85% of the territory means no capitulation ("National resistance") |
| **Nuclear** | World reactions, embargoes, and radiation. Each bomb kills part of the target state's population and adds long-term radiation that damages resources and construction |
| **Space program** | Stages 1 to 3, projects, missions that can fail, private companies, orbital debris, a solar system map, and colonies (Moon, Mars, Venus, Mercury, asteroids, Callisto, Titan). Spaceports use real 2000 sites where available. Budget from 0 to 5% of GDP |
| **Ship sales** | A window to sell ships, trade them in bulk, refit them with export designs, build ships, and manage contracts. The AI sells to friends and offers to buy |
| **Captured generals** | Real generals from other countries can be captured when capitals or large states fall, or when their armies are destroyed. They can be used, put on public trial, executed, or exiled |
| **Alerts** | Six alerts in MD's system: ammunition, food, discontent, straits, uranium, and rare earths |
| **Building slots** | Each state gets half its base slots once (×1.5), and the cap rises from 80 to 104 |
| **Arctic map** | Map expanded to 85° N and to Antarctica, with 30 new polar states and Arctic terrain |
| **Globe (in development)** | Zooming far out curves the map into a sphere. Turned off with `MDR_GLOBE_ON = 0` in `constants.fxh` |
| **Mongolia** | Its own focus tree with 123 focuses in 7 branches: politics, mining economy, steppe and dzud, the third neighbor, armed forces, national identity, and a Pan-Mongol path |
| **AI** | Normal, Improved (default), and Expert difficulty, with no cheats. Improved AI adapts its stance to enemy strength, avoids attacking without ammunition, and asks for peace when losing |

## Buildings

| Building | Type | Max | Effect |
|---|---|---|---|
| Uranium mine | State | 10 | +5 uranium per level |
| Early warning center | State | 1 | Less disaster damage |
| Coastal dikes | Province | 1 per province | Less tsunami, storm, and flood damage |
| Cropland soil | Hidden marker | 1 | Allows cropland |
| Cropland | State | 10 | +10 grain per level |
| Rare earth complex | State | 20 | +6 rare earths per level |
| Desalination plant | State, coastal | 1 | Improves dry state soil |
| Recycling plant | State | 3 | +1 steel and +1 aluminum, less pollution |
| Regional university | State | 2 | +0.4% research each and state growth |
| Electric steel mill | Shared | 2 | +4 steel with high energy use |
| Data center | Shared | 5 | Large GDP boost, high energy use, needs level 2 internet |
| Smart grid | Shared | 1 | Saves 15% of building energy in the state |
| Fishing port | Province, coastal | 1 per province | Fish for food |
| Fortified ammunition depot | Province | 1 per province | +60,000 crates of capacity |
| Science campus | Special project | 1 per state | +7% to its state's special project |

## Interface changes

- **Construction:** five columns, with our buildings' speed percentages.
- **State view:** wider, with more building and slot space.
- **Trade and economy:** new resources, a resource price row, and an automatic import panel.
- **Top bar:** ammunition, food, and war exhaustion boxes.
- **Politics:** a "Society and Information" category with its own icon.
- **International systems:** treaty tab.
- **Main menu:** REALPOLITIK logo and version notice.
- **Map:** country colors, lakes, and softer borders.

## Testing

The mod includes a **diagnostic mode** (Realpolitik rules). When it is on, the game tests the mod on its own and writes results to `game.log`. Lines marked `MDR DIAG OK`, `FALLA`, `AVISO`, and `PRUEBA` show what passed, what failed, and what was tested. After 160 game days it opens a summary window.

To check for errors without opening the game, run `perl herramientas/revisar_mod.pl`.

## Development

- Technical guide (in Spanish): [CLAUDE.md](CLAUDE.md)
- Compatibility with Millennium Dawn, including the files we replace and their MD5 hashes: [COMPATIBILIDAD.md](COMPATIBILIDAD.md) (Spanish)

After every Millennium Dawn update, run `herramientas/actualizar_arboles.ps1` and `python herramientas/construir_mapa.py instalar`, then follow the steps in COMPATIBILIDAD.md.

## Credits

Based on the work of the Millennium Dawn team. Millennium Dawn is open source. This submod is not an official Paradox Interactive product.
