"""Mongolia focus tree (Realpolitik): focus table and generator.

Writes:
  common/national_focus/mdr_mongolia.txt
  localisation/{spanish,english}/mdr_mongolia_focus_l_*.yml
Ideas, events and scripted parts are hand-written: common/ideas/mdr_mongolia_ideas.txt,
events/mdr_mongolia_events.txt, common/scripted_effects/mdr_mongolia.txt.
Icons are Millennium Dawn sprites (interface/goals*.gfx); the script checks every name exists.

Run from the mod folder:  python herramientas/make_mongolia.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MD = ROOT.parent / "Millennium-Dawn-2.0.0"

E, W = 596, 597  # Eastern (Ulaanbaatar, Gobi) and Western Mongolia
P_MPP, P_DP, P_NAT = 4, 18, 20  # MD party slots in Mongolia: People's Party, Democratic Party, nationalists


# ---------- effect helpers (Paradox script snippets) ----------
def pp(n): return f"add_political_power = {n}"
def stab(v): return f"add_stability = {v}"
def ws(v): return f"add_war_support = {v}"
def idea(i): return f"add_ideas = {i}"
def tidea(i, d): return f"add_timed_idea = {{ idea = {i} days = {d} }}"
def swap(a, b): return f"swap_ideas = {{ remove_idea = {a} add_idea = {b} }}"
def rmidea(i): return f"if = {{ limit = {{ has_idea = {i} }} remove_ideas = {i} }}"
def exp(n): return f"army_experience = {n}"
def man(n): return f"add_manpower = {n}"
def flag(f): return f"set_country_flag = {f}"
def corr_down(): return "decrease_corruption = yes"
def corr_up(): return "increase_corruption = yes"
def growth(): return "increase_economic_growth = yes"
def claim(s): return f"add_state_claim = {s}"


def money(b):
    return f"set_temp_variable = {{ treasury_change = {b} }}\n\t\t\tmodify_treasury_effect = yes"


def party(idx, v):
    return (f"set_temp_variable = {{ party_index = {idx} }}\n\t\t\tset_temp_variable = {{ party_popularity_increase = {v} }}\n"
            f"\t\t\tset_temp_variable = {{ temp_outlook_increase = {v} }}\n\t\t\tchange_relative_party_popularity = yes")


def build(state, btype, lvl=1):
    return (f"{state} = {{ add_building_construction = {{ type = {btype} level = {lvl} instant_build = yes }} }}")


def opin(tag, mod):
    return f"if = {{ limit = {{ country_exists = {tag} }} {tag} = {{ add_opinion_modifier = {{ target = ROOT modifier = {mod} }} }} }}"


def wargoal(state):
    return (f"if = {{ limit = {{ {state} = {{ NOT = {{ is_owned_by = ROOT }} }} }}\n"
            f"\t\t\t\t{state} = {{ owner = {{ save_event_target_as = mdr_mon_target }} }}\n"
            f"\t\t\t\tcreate_wargoal = {{ type = take_state_focus target = event_target:mdr_mon_target generator = {{ {state} }} }}\n"
            "\t\t\t}")


def join_offer(state):
    # A small owner that is not Russia or China gets an offer to join instead of a war goal.
    return (f"if = {{ limit = {{ {state} = {{ NOT = {{ is_owned_by = ROOT }} owner = {{ NOT = {{ original_tag = SOV original_tag = CHI }} }} }} }}\n"
            f"\t\t\t\t{state} = {{ owner = {{ country_event = {{ id = mdr_mon.3 days = 3 }} }} }}\n"
            f"\t\t\t}}\n\t\t\telse = {{\n\t\t\t\t{wargoal(state)}\n\t\t\t}}")


# ---------- the tree ----------
# (id, prerequisites [AND of OR-groups], exclusive, cost, icon, filters, effects, available, ai, es, en, desc_es, desc_en)
F = []


def f(fid, pre, cost, icon, filt, eff, es, en, des, den, mutex=(), avail=None, ai=10, bypass=None):
    F.append(dict(id=f"mdr_mon_{fid}", pre=[[f"mdr_mon_{p}" for p in g] for g in pre],
                  mutex=[f"mdr_mon_{m}" for m in mutex], cost=cost, icon=icon, filt=filt, eff=eff, avail=avail,
                  ai=ai, es=es, en=en, des=des, den=den, bypass=bypass, branch=fid[0]))


POL, ECO, DIP, MIL, STA, INT = ("FOCUS_FILTER_POLITICAL", "FOCUS_FILTER_ECONOMY", "FOCUS_FILTER_DIPLOMACY",
                                "FOCUS_FILTER_ARMY_XP", "FOCUS_FILTER_STABILITY", "FOCUS_FILTER_INTERNAL_AFFAIRS")
COR = "FOCUS_FILTER_CORRUPTION"

# Politics
f("P1", [], 5, "focus_AFG_parliamentary_democracy", [POL], [stab(0.07), pp(43)],
  "Elecciones del Gran Jural de 2000", "The 2000 State Great Khural Election",
  "El Partido del Pueblo ganó 72 de los 76 escaños. Empieza una nueva etapa.",
  "The People's Party won 72 of the 76 seats. A new period begins.", ai=40)
f("P2", [["P1"]], 10, "Generic_Socialist_Industry", [POL], [party(P_MPP, 0.07), corr_down()],
  "El gobierno de Enkhbayar", "The Enkhbayar Government",
  "Un primer ministro reformista al frente de un partido que viene del régimen anterior.",
  "A reformist prime minister leading a party that comes from the old regime.", ai=30)
f("P3", [["P2"]], 10, "BRA_electoral_reforms", [POL, INT], [tidea("mdr_mon_civil_service", 1460)],
  "Reforma de la administración pública", "Civil Service Reform",
  "Menos cargos políticos y más funcionarios de carrera.", "Fewer political posts and more career officials.")
f("P4", [["P3"]], 10, "BLR_Anti_Corruption", [POL, COR], [corr_down(), pp(23)],
  "Ley anticorrupción de 2006", "The 2006 Anti-Corruption Law",
  "Nace la Agencia Independiente contra la Corrupción.", "The Independent Authority Against Corruption is born.",
  avail="date > 2005.6.1")
f("P5", [["P2"]], 10, "KHM_democratic_coalition", [POL], [stab(0.05), party(P_MPP, -0.03)],
  "La coalición de 2004", "The 2004 Coalition",
  "El empate en el Gran Jural obliga a gobernar entre los dos grandes partidos.",
  "A hung Great Khural forces the two big parties to govern together.", avail="date > 2004.1.1")
f("P6", [["P5"]], 10, "focus_PER_stage_mass_protests", [POL, STA], ["country_event = { id = mdr_mon.1 }"],
  "Los disturbios del 1 de julio de 2008", "The 1 July 2008 Riots",
  "Denuncias de fraude, la sede del partido en llamas y cinco muertos. Hay que decidir cómo responder.",
  "Fraud claims, the party headquarters on fire and five dead. We must decide how to respond.",
  avail="date > 2008.1.1")
# three exclusive paths
f("P7A", [["P6"]], 10, "BRA_democracy_triumphant", [POL], [stab(0.11), idea("mdr_mon_democracy")],
  "Democracia consolidada", "Consolidated Democracy",
  "Elecciones limpias, alternancia y una prensa que puede criticar.",
  "Clean elections, alternation in power and a press free to criticise.", mutex=("P7B", "P7C"), ai=30)
f("P8A", [["P7A"]], 10, "MEX_Defend_the_constitution", [POL, COR], [corr_down(), money(0.07)],
  "Ley de transparencia", "Transparency Law", "Las cuentas públicas, a la vista de todos.",
  "Public accounts open to everyone.")
f("P9A", [["P8A"]], 10, "BRA_decentralization", [POL, INT], [stab(0.03), pp(17)],
  "Descentralización de los aimags", "Decentralisation of the Aimags",
  "Las provincias manejan parte de su presupuesto.", "The provinces run part of their own budget.")
f("P10A", [["P9A"]], 10, "ARM_constitution", [POL], [stab(0.07), party(P_DP, 0.05)],
  "Reforma constitucional de 2019", "The 2019 Constitutional Reform",
  "Un solo mandato presidencial y un primer ministro más fuerte.",
  "A single presidential term and a stronger prime minister.", avail="date > 2015.1.1")
f("P11A", [["P10A"]], 10, "focus_generic_expand_gold_mining", [POL, ECO], [corr_down(), stab(0.05)],
  "Control ciudadano de la minería", "Citizen Oversight of Mining",
  "Los contratos mineros pasan por el Gran Jural y se publican.",
  "Mining contracts go through the Great Khural and are published.")
f("P7B", [["P6"]], 10, "Generic_Socialist_Industry", [POL], [pp(57), stab(-0.03), idea("mdr_mon_party_state")],
  "Hegemonía del Partido del Pueblo", "People's Party Hegemony",
  "El partido controla el Estado, los sindicatos y las empresas públicas.",
  "The party controls the state, the unions and the public companies.", mutex=("P7A", "P7C"), ai=12)
f("P8B", [["P7B"]], 10, "secret_police", [POL], ["mdr_mon_media_step_up = yes"],
  "Medios afines", "Friendly Media", "La prensa crítica pierde la publicidad del Estado.",
  "The critical press loses state advertising.")
f("P9B", [["P8B"]], 10, "CUB_mining", [POL, ECO, COR], [corr_up(), tidea("mdr_mon_mining_patronage", 1825)],
  "Clientelismo de la minería", "Mining Patronage", "Las licencias mineras se reparten entre los leales.",
  "Mining licences are shared among the loyal.")
f("P10B", [["P9B"]], 10, "GEO_Industrialize_the_Countryside", [POL, ECO], [growth(), party(P_MPP, 0.07)],
  "Estado desarrollista", "Developmental State", "El Estado guía la inversión hacia la industria.",
  "The state steers investment towards industry.")
f("P11B", [["P10B"]], 10, "SOV_unity_party", [POL], [stab(0.07), pp(37)],
  "Sucesión ordenada", "Orderly Succession", "El partido elige a sus sucesores sin sobresaltos.",
  "The party picks its successors without upheaval.")
f("P7C", [["P6"]], 10, "focus_generic_military_dictatorship", [POL], [pp(77), tidea("mdr_mon_strongman_unrest", 365), idea("mdr_mon_strongman")],
  "El hombre fuerte", "The Strongman",
  "Se suspende el Gran Jural. El orden primero, las elecciones después.",
  "The Great Khural is suspended. Order first, elections later.", mutex=("P7A", "P7B"), ai=2)
f("P8C", [["P7C"]], 10, "secret_police", [POL, INT], ["mdr_mon_surveillance_step_up = yes"],
  "Vigilancia de la capital", "Watching the Capital", "Cámaras y agentes en cada distrito de Ulán Bator.",
  "Cameras and agents in every district of Ulaanbaatar.")
f("P9C", [["P8C"]], 10, "CIS_military_army", [POL, MIL], [ws(0.11), tidea("mdr_mon_loyal_army", 1825)],
  "Un ejército leal", "A Loyal Army", "Los generales reciben ascensos y negocios.",
  "The generals receive promotions and business.")
f("P10C", [["P9C"]], 10, "CUB_mining", [POL, ECO], ["mdr_mon_seize_mines = yes"],
  "El Estado minero", "The Mining State", "Las minas extranjeras pasan a manos del Estado.",
  "Foreign mines pass into state hands.")
f("P11C", [["P10C"]], 10, "blr_referendum_belarus_2004", [POL], [tidea("mdr_mon_leader_referendum", 730)],
  "Referéndum del líder", "The Leader's Referendum", "Un plebiscito para quedarse sin límite de mandatos.",
  "A plebiscite to stay on without term limits.")
f("P12", [["P11A", "P11B", "P11C"]], 10, "focus_DEN_national_unity", [POL, STA], [stab(0.05), pp(29)],
  "Fin de la transición", "The End of the Transition",
  "Treinta años después del comunismo, el sistema político ya tiene su forma.",
  "Thirty years after communism, the political system has taken its shape.")

# Mining economy
f("E1", [], 5, "focus_generic_expand_gold_mining", [ECO], [build(E, "infrastructure"), pp(19)],
  "Inventario geológico nacional", "National Geological Survey",
  "Mapear lo que hay bajo la estepa y el Gobi.", "Map what lies under the steppe and the Gobi.", ai=35)
f("E2", [["E1"]], 10, "geo_goldmine", [ECO], [money(0.07)],
  "El descubrimiento de Oyu Tolgoi", "The Discovery of Oyu Tolgoi",
  "Uno de los mayores yacimientos de cobre y oro del mundo, en el sur del Gobi (2001).",
  "One of the world's largest copper and gold deposits, in the southern Gobi (2001).", ai=30)
f("E3", [["E1"]], 10, "CUB_mining", [ECO], ["add_resource = { type = steel amount = 3 state = 596 }", opin("SOV", "mdr_mon_rel_15")],
  "Modernizar Erdenet", "Modernise Erdenet", "La mina de cobre compartida con Rusia recibe equipos nuevos.",
  "The copper mine shared with Russia gets new equipment.")
f("E4", [["E1"]], 10, "coal_mining", [ECO], ["add_resource = { type = oil amount = 5 state = 596 }"],
  "Tavan Tolgoi", "Tavan Tolgoi", "Uno de los mayores depósitos de carbón sin explotar del mundo.",
  "One of the largest untapped coal deposits in the world.")
f("E5A", [["E2"]], 10, "examine_foreign_laws", [ECO], ["mdr_mon_invite_rio_tinto = yes", tidea("mdr_mon_open_mining", 1825)],
  "Abrir las puertas", "Open the Doors", "Las grandes mineras extranjeras son bienvenidas.",
  "The big foreign mining companies are welcome.", mutex=("E5B",), ai=30)
f("E6A", [["E5A"]], 10, "focus_RAJ_issue_bonds_on_the_stock_market", [ECO], ["mdr_mon_rio_tinto_deal = yes", money(0.29)],
  "El acuerdo de inversión de 2009", "The 2009 Investment Agreement",
  "Rio Tinto e Ivanhoe se comprometen a construir la mina; el Estado se queda con el 34%.",
  "Rio Tinto and Ivanhoe commit to building the mine; the state keeps 34%.", avail="date > 2008.6.1")
f("E7A", [["E6A"]], 10, "focus_RAJ_issue_bonds_on_the_stock_market", [ECO], [tidea("mdr_mon_stock_exchange", 1825)],
  "La bolsa de Ulán Bator", "The Ulaanbaatar Stock Exchange", "Capital local para empresas locales.",
  "Local capital for local companies.")
f("E5B", [["E2"]], 10, "BLR_Expand_Naftan_Refinery", [ECO], [idea("mdr_mon_resource_nationalism"), party(P_NAT, 0.03)],
  "Nacionalismo de los recursos", "Resource Nationalism",
  "Impuesto extraordinario de 68% sobre el cobre y el oro (2006).", "A 68% windfall tax on copper and gold (2006).",
  mutex=("E5A",), ai=8)
f("E6B", [["E5B"]], 10, "economic_hard_glass_factory", [ECO], [idea("mdr_mon_erdenes")],
  "Erdenes Mongol", "Erdenes Mongol", "Una empresa estatal con parte de cada gran proyecto.",
  "A state company with a share of every big project.")
f("E7B", [["E6B"]], 10, "focus_CHI_promote_national_currency", [ECO], [party(P_NAT, 0.07), stab(0.03)],
  "Mongolia para los mongoles", "Mongolia for the Mongols", "Los recursos del país, para el país.",
  "The country's resources, for the country.")
f("E8", [["E7A", "E7B"]], 10, "money", [ECO], [tidea("mdr_mon_copper_exports", 3650)],
  "Impuesto a la exportación de cobre", "Copper Export Duty", "Cada camión que cruza la frontera deja algo.",
  "Every truck crossing the border leaves something behind.")
f("E9", [["E4"]], 10, "Generic_Railroads", [ECO], [build(E, "infrastructure", 2)],
  "El ferrocarril del carbón", "The Coal Railway", "Una línea desde Tavan Tolgoi hasta la frontera china.",
  "A line from Tavan Tolgoi to the Chinese border.")
f("E10A", [["E9"]], 10, "SOV_i_like_trains", [ECO, DIP], [opin("SOV", "mdr_mon_rel_15"), opin("CHI", "mdr_mon_rel_neg_15")],
  "Trocha rusa", "Russian Gauge", "Las vías siguen el ancho ruso: el ferrocarril queda atado a Moscú.",
  "The tracks follow the Russian gauge: the railway stays tied to Moscow.", mutex=("E10B",), ai=15)
f("E10B", [["E9"]], 10, "Generic_Train", [ECO, DIP], [opin("CHI", "mdr_mon_rel_15"), money(0.11), tidea("mdr_mon_china_dependence", 1825)],
  "Trocha china", "Chinese Gauge", "Exportar a China sale más barato, pero dependemos más de Pekín.",
  "Exporting to China gets cheaper, but we depend more on Beijing.", mutex=("E10A",), ai=10)
f("E11", [["E8"]], 10, "Generic_Loadsamoney", [ECO, STA], [tidea("mdr_mon_human_development_fund", 1095)],
  "Fondo de Desarrollo Humano", "Human Development Fund", "Reparto en efectivo de la renta minera (2008).",
  "Cash handouts from mining revenue (2008).", mutex=("E12",), ai=10)
f("E12", [["E8"]], 10, "focus_generic_stockpile_currency", [ECO], ["set_variable = { mdr_fund_rate = 1 }", "add_to_variable = { mdr_fund_balance = 0.29 }"],
  "Fondo del Futuro", "Future Heritage Fund", "Ahorrar la renta minera para cuando se acabe el cobre.",
  "Save the mining revenue for when the copper runs out.", mutex=("E11",), ai=20)
f("E13", [["E8"]], 10, "modern_refinery_industry", [ECO], [build(E, "industrial_complex")],
  "Una fundición de cobre propia", "Our Own Copper Smelter", "Vender cátodos y no solo concentrado.",
  "Sell cathodes, not just concentrate.")
f("E14", [["E1"]], 10, "uranium_production", [ECO], [build(E, "mdr_uranium_mine")],
  "El uranio de Dornod", "Dornod Uranium", "Reabrir la mina de la era soviética en el este.",
  "Reopen the Soviet-era mine in the east.")
f("E15", [["E14"]], 10, "uranium_processing", [ECO], [build(E, "mdr_uranium_mine"), pp(17)],
  "Ley de energía nuclear de 2009", "The 2009 Nuclear Energy Law", "Nace MonAtom para vender el uranio.",
  "MonAtom is created to sell the uranium.", avail="date > 2008.6.1")
f("E16", [["E1"]], 10, "economic_machina_tools_factory", [ECO], [build(W, "mdr_rare_earth_complex")],
  "Las tierras raras de Khalzan Buregtei", "Khalzan Buregtei Rare Earths", "Un yacimiento de tierras raras en Khovd.",
  "A rare earth deposit in Khovd.")
f("E17", [["E3"]], 10, "economic_silk_factory", [ECO], [build(E, "industrial_complex")],
  "La cachemira", "Cashmere", "Mongolia produce cerca de un tercio de la cachemira del mundo: hay que hilarla en casa.",
  "Mongolia produces about a third of the world's cashmere: we should spin it at home.")
f("E18", [["E17"]], 10, "Tourism_is_our_oil", [ECO], [tidea("mdr_mon_tourism", 3650)],
  "Turismo de la estepa", "Steppe Tourism", "Campamentos de ger, el Gobi y el Naadam para los visitantes.",
  "Ger camps, the Gobi and the Naadam for visitors.")
f("E19", [["E13"], ["E9"]], 10, "construct_factory", [ECO], [build(E, "industrial_complex", 2)],
  "Ciudad industrial de Sainshand", "Sainshand Industrial City", "Refinería, acería y química en el desierto.",
  "Refinery, steel and chemicals in the desert.")
f("E20", [["E8"]], 10, "IMF_Bailout_Focus_Icon", [ECO], [money(1.3), tidea("mdr_mon_imf_program", 1095)],
  "Programa con el FMI", "IMF Programme", "Un rescate a cambio de ajustar el gasto (2017).",
  "A bailout in exchange for spending cuts (2017).", avail="check_variable = { debt_ratio > 0.7 }")
f("E21", [["E20", "E12"]], 10, "focus_generic_currency_reforms", [ECO], [tidea("mdr_mon_stable_togrog", 1825)],
  "Un tugrik estable", "A Stable Tögrög", "Menos inflación y deuda más barata.", "Less inflation and cheaper debt.")
f("E22", [["E19"], ["E21"]], 10, "economic_community", [ECO], [growth(), idea("mdr_mon_diversified")],
  "La economía de los diez millones", "The Ten-Million Economy", "Una economía que ya no vive solo del cobre.",
  "An economy that no longer lives on copper alone.")

# Steppe and herders
f("S1", [], 5, "winter_warfare", [STA], ["mdr_mon_dzud_relief = yes"],
  "Emergencia del dzud", "Dzud Emergency",
  "El invierno de 1999-2002 mató unos 11 millones de animales. Forraje, transporte y ayuda.",
  "The winters of 1999-2002 killed about 11 million animals. Fodder, transport and aid.", ai=45)
f("S2", [["S1"]], 10, "agriculture", [STA, ECO], [flag("mdr_mon_fodder_reserves")],
  "Reservas nacionales de forraje", "National Fodder Reserves", "Depósitos de heno en cada provincia para el próximo dzud.",
  "Hay stores in every province for the next dzud.", ai=30)
f("S3", [["S2"]], 10, "focus_RAJ_issue_bonds_on_the_stock_market", [STA, ECO], [flag("mdr_mon_livestock_insurance"), stab(0.02)],
  "Seguro ganadero por índice", "Index-Based Livestock Insurance",
  "Un seguro que paga según la mortandad de la zona (2005).", "Insurance that pays out by local livestock losses (2005).")
f("S4", [["S2"]], 10, "focus_SIA_irrigation", [STA, ECO], ["mdr_mon_steppe_wells = yes"],
  "Pozos en la estepa", "Steppe Wells", "Agua para el ganado y para unos pocos cultivos.",
  "Water for the herds and for a few crops.")
f("S5", [["S3"]], 10, "Farm_national_movement", [STA], [stab(0.03), tidea("mdr_mon_herder_coops", 3650)],
  "Cooperativas de pastores", "Herder Cooperatives", "Juntos venden mejor la lana y la carne.",
  "Together they sell wool and meat for more.")
f("S6", [["S5"]], 10, "focus_CHL_focus_on_cattle_and_wool", [STA], [stab(0.02), man(3000)],
  "Un veterinario en cada sum", "A Vet in Every Sum", "Menos animales muertos por enfermedades.",
  "Fewer animals lost to disease.")
f("S7", [["S1"]], 10, "focus_generic_winter_warfare", [STA], ["mdr_mon_dzud_2010 = yes"],
  "El dzud de 2010", "The 2010 Dzud",
  "Otro invierno terrible. Con reservas y seguro, el daño es mucho menor.",
  "Another terrible winter. With reserves and insurance, the damage is far smaller.", avail="date > 2009.10.1", ai=40)
f("S8", [], 5, "generic_housing", [STA, INT], [man(29000), tidea("mdr_mon_ger_districts", 3650)],
  "Los distritos de ger", "The Ger Districts", "Medio país se mudó a Ulán Bator, a barrios de yurtas sin servicios.",
  "Half the country moved to Ulaanbaatar, into yurt districts with no services.", ai=25)
f("S9", [["S8"]], 10, "Coal_Power_Plant", [STA], [pp(11)],
  "El smog de Ulán Bator", "Ulaanbaatar's Smog", "Las estufas a carbón hacen de la capital una de las más contaminadas del mundo.",
  "Coal stoves make the capital one of the most polluted in the world.")
f("S10A", [["S9"]], 10, "economic_water_supply", [STA], [rmidea("mdr_mon_ger_districts"), money(-0.13)],
  "Estufas limpias", "Clean Stoves", "Subsidios para cambiar las estufas: rápido pero caro.",
  "Subsidies to replace the stoves: quick but costly.", mutex=("S10B",), ai=15)
f("S10B", [["S9"]], 10, "focus_generic_low_cost_housing", [STA], [rmidea("mdr_mon_ger_districts"), build(E, "industrial_complex")],
  "Departamentos para los ger", "Apartments for the Ger Districts", "Barrios nuevos con calefacción central.",
  "New neighbourhoods with central heating.", mutex=("S10A",), ai=10)
f("S11", [["S10A", "S10B"]], 10, "windmills", [STA, ECO], [build(E, "renewable_energy_infra")],
  "Parque eólico de Salkhit", "Salkhit Wind Farm", "El primer parque eólico del país (2013).", "The country's first wind farm (2013).",
  avail="date > 2011.1.1")
f("S12", [["S11"]], 10, "BRA_reforest_amazon", [STA], [stab(0.02), "mdr_mon_green_wall = yes"],
  "La Gran Muralla Verde", "The Great Green Wall", "Árboles contra el avance del desierto.", "Trees against the advance of the desert.")
f("S13", [["S12"]], 10, "economic_water_supply", [STA, ECO], [build(E, "infrastructure")],
  "El agua del Gobi", "Water for the Gobi", "Pozos profundos y tuberías para la minería del sur.",
  "Deep wells and pipelines for the southern mines.")
f("S14", [["S6"], ["S12"]], 10, "focus_CHL_focus_on_cattle_and_wool", [STA], [idea("mdr_mon_modern_nomads"), stab(0.05)],
  "Nómadas del siglo XXI", "Twenty-First-Century Nomads", "Paneles solares, teléfonos y mercados para la vida nómada.",
  "Solar panels, phones and markets for nomadic life.")

# Third neighbour
f("X1", [], 5, "Trade_with_the_east", [DIP], [pp(23)],
  "El concepto de 1994", "The 1994 Foreign Policy Concept", "Equilibrio entre los dos gigantes y amigos lejanos.",
  "Balance between the two giants, and friends far away.", ai=40)
f("X2", [["X1"]], 10, "LIB_prohibit_nuclear", [DIP], ["mdr_mon_nuclear_free = yes"],
  "Zona libre de armas nucleares", "Nuclear-Weapon-Free Status",
  "Los cinco miembros permanentes reconocen el estatus de Mongolia (2012).",
  "The five permanent members recognise Mongolia's status (2012).")
f("X3", [["X2"]], 10, "NKO_korea_peace", [DIP], [pp(37), opin("NKO", "mdr_mon_rel_15"), opin("KOR", "mdr_mon_rel_15"), opin("JAP", "mdr_mon_rel_15")],
  "El Diálogo de Ulán Bator", "The Ulaanbaatar Dialogue", "Una mesa neutral para hablar de Corea.",
  "A neutral table to talk about Korea.")
f("X4", [["X1"]], 10, "ExpandTrade", [DIP], [opin("USA", "mdr_mon_rel_25"), money(0.29)],
  "Socio de Estados Unidos", "Partner of the United States", "La Cuenta del Desafío del Milenio financia obras.",
  "The Millennium Challenge Account funds projects.")
f("X5", [["X1"]], 10, "Generic_Republican_Japanese_Diplomacy", [DIP, ECO], [opin("JAP", "mdr_mon_rel_25"), build(E, "industrial_complex")],
  "Acuerdo económico con Japón", "Economic Partnership with Japan", "El primer tratado de libre comercio de Mongolia (2015).",
  "Mongolia's first free trade agreement (2015).", avail="date > 2013.1.1")
f("X6", [["X1"]], 10, "NKO_korea_rebuild", [DIP], [opin("KOR", "mdr_mon_rel_25"), tidea("mdr_mon_remittances", 3650)],
  "Corea, el hermano lejano", "Korea, the Distant Brother", "Decenas de miles de mongoles trabajan en Corea del Sur.",
  "Tens of thousands of Mongolians work in South Korea.")
f("X7", [["X4"]], 10, "align_to_nato", [DIP, MIL], [exp(15), opin("USA", "mdr_mon_rel_15")],
  "Socio de la OTAN", "NATO Partner", "Un programa de asociación individual.", "An individual partnership programme.")
f("X8", [["X1"]], 10, "European_Society", [DIP, ECO], [tidea("mdr_mon_gsp_plus", 3650)],
  "La Unión Europea", "The European Union", "Preferencias arancelarias a cambio de derechos y buen gobierno.",
  "Tariff preferences in exchange for rights and good governance.")
f("X9A", [["X4"], ["X5"]], 10, "CHI_russia_china_equal_partners", [DIP], [idea("mdr_mon_third_neighbor")],
  "El tercer vecino", "The Third Neighbour", "Ni Moscú ni Pekín deciden por nosotros.",
  "Neither Moscow nor Beijing decides for us.", mutex=("X9B", "X9C"), ai=30)
f("X9B", [["X4"], ["X5"]], 10, "CHI_pro_china_russia", [DIP], [idea("mdr_mon_beijing_tilt"), opin("CHI", "mdr_mon_rel_50"), build(E, "infrastructure")],
  "Acercarse a Pekín", "Closer to Beijing", "Inversión china a cambio de dependencia.",
  "Chinese investment in exchange for dependence.", mutex=("X9A", "X9C"), ai=8)
f("X9C", [["X4"], ["X5"]], 10, "SOV_russian_mongolia", [DIP], [idea("mdr_mon_moscow_tilt"), opin("SOV", "mdr_mon_rel_50")],
  "Acercarse a Moscú", "Closer to Moscow", "Combustible y armas rusas baratas, como en los viejos tiempos.",
  "Cheap Russian fuel and weapons, like the old days.", mutex=("X9A", "X9B"), ai=8)
f("X10", [["X9A", "X9C"]], 10, "JAP_russian_diplomacy", [DIP], [opin("SOV", "mdr_mon_rel_25"), pp(19)],
  "El tratado con Rusia de 2019", "The 2019 Treaty with Russia", "Una asociación estratégica integral.",
  "A comprehensive strategic partnership.", avail="date > 2016.1.1")
f("X11", [["X9A", "X9B"]], 10, "IND_silkroad", [DIP, ECO], [build(E, "infrastructure"), build(W, "infrastructure")],
  "El corredor de la Franja y la Ruta", "The Belt and Road Corridor", "El corredor China–Mongolia–Rusia pasa por nuestras rutas.",
  "The China–Mongolia–Russia corridor runs along our roads.", avail="date > 2013.6.1")
f("X12", [["X9B", "X9C"]], 10, "CIS_diplomacy", [DIP], [opin("CHI", "mdr_mon_rel_15"), opin("SOV", "mdr_mon_rel_15")],
  "Observadores en la OCS", "Observers in the SCO", "Sentarse a la mesa de la Organización de Cooperación de Shanghái.",
  "A seat at the Shanghai Cooperation Organisation table.")
f("X13", [["X10"], ["X11"]], 10, "focus_DEN_national_unity", [DIP], [idea("mdr_mon_no_master")],
  "Ningún vecino nos manda", "No Neighbour Rules Us", "Mongolia trata con todos y no obedece a nadie.",
  "Mongolia deals with everyone and obeys no one.")
f("X14", [["X6"]], 10, "Generic_Religious_Unity", [DIP], [pp(17), opin("KOR", "mdr_mon_rel_15")],
  "La diáspora mongola", "The Mongol Diaspora", "Lazos con los mongoles de Rusia, China y el mundo.",
  "Ties with the Mongols of Russia, China and the world.")
f("X15", [["X3"]], 10, "ARM_peace_policy", [DIP], [pp(43)],
  "Mongolia en las Naciones Unidas", "Mongolia at the United Nations", "Presidir foros y ganar peso diplomático.",
  "Chairing forums and gaining diplomatic weight.")

# Armed forces
f("M1", [], 5, "CUB_armyreformsnine", [MIL], [tidea("mdr_mon_army_reform", 1825)],
  "Reforma de las Fuerzas Armadas", "Armed Forces Reform", "Del ejército soviético a una fuerza profesional.",
  "From a Soviet-style army to a professional force.", ai=35)
f("M2", [["M1"]], 10, "focus_ETH_peacekeeping_forces", [MIL], [exp(10), idea("mdr_mon_peacekeepers")],
  "Cascos azules", "Blue Helmets", "Las primeras misiones de paz de la ONU (2002).", "The first UN peacekeeping missions (2002).")
f("M3", [["M2"]], 10, "Generic_Infantry_Training", [MIL], [exp(15)],
  "El centro de Cinco Colinas", "Five Hills Training Centre", "Entrenamiento para misiones de paz (2006).",
  "Peace operations training (2006).")
f("M4", [["M2"], ["X4"]], 10, "NATO_squad_doctrine", [MIL], [exp(15), tidea("mdr_mon_khaan_quest", 1825)],
  "Ejercicio Khaan Quest", "Exercise Khaan Quest", "Maniobras anuales con Estados Unidos desde 2003.",
  "Yearly manoeuvres with the United States since 2003.")
f("M5", [["M4"]], 10, "coalition_army", [MIL], [exp(25), opin("USA", "mdr_mon_rel_25")],
  "Irak y Afganistán", "Iraq and Afghanistan", "Soldados mongoles en las dos guerras.", "Mongolian soldiers in both wars.",
  avail="date > 2003.3.1")
f("M6", [["M1"]], 10, "ARM_ssr_border_troops", [MIL], [f"{E} = {{ add_building_construction = {{ type = bunker level = 1 province = {{ all_provinces = yes limit_to_border = yes }} instant_build = yes }} }}"],
  "Guardia de frontera", "Border Guard", "4.700 km con China y 3.500 con Rusia.", "4,700 km with China and 3,500 with Russia.")
f("M7", [["M1"]], 10, "FRA_Reform_Military_Mass_Mobilization_Conscription", [MIL], [man(11000)],
  "Reservistas de la estepa", "Steppe Reservists", "Cada pastor sabe montar y disparar.", "Every herder can ride and shoot.")
f("M8", [["M6"]], 10, "air_defense", [MIL], [build(E, "air_base")],
  "Defensa aérea", "Air Defence", "Proteger Ulán Bator, la única gran ciudad.", "Protect Ulaanbaatar, the only big city.")
f("M9", [["M8"]], 10, "Generic_Transport_Helicopter", [MIL], [exp(10), tidea("mdr_mon_helicopters", 1825)],
  "Helicópteros Mi-171", "Mi-171 Helicopters", "Transporte en un país sin caminos.", "Transport in a country without roads.")
f("M10A", [["M5"]], 10, "ARM_peacekeepers", [MIL], [rmidea("mdr_mon_peacekeepers"), idea("mdr_mon_expeditionary")],
  "Fuerza expedicionaria de paz", "Expeditionary Peace Force", "Pocos soldados, muy entrenados, para las misiones.",
  "Few, highly trained soldiers for the missions.", mutex=("M10B",), ai=25)
f("M10B", [["M5"]], 10, "Generic_Soldiers_Defense", [MIL], [idea("mdr_mon_total_defense")],
  "Defensa total de la estepa", "Total Defence of the Steppe", "Cada valle una trinchera, cada pastor un soldado.",
  "Every valley a trench, every herder a soldier.", mutex=("M10A",), ai=10)
f("M11", [["M10A", "M10B"]], 10, "focus_CHI_guerrilla_warfare", [MIL], [tidea("mdr_mon_steppe_mobility", 3650)],
  "Fuerzas móviles de la estepa", "Mobile Steppe Forces", "Motorizadas, ligeras y rápidas.", "Motorised, light and fast.")
f("M12", [["M11"]], 10, "construct_factory", [MIL], [build(E, "arms_factory")],
  "Industria de defensa nacional", "National Defence Industry", "Reparar y fabricar en casa.", "Repair and build at home.")
f("M13", [["M12"]], 10, "cavalry", [MIL], [exp(10), tidea("mdr_mon_steppe_mobility", 1825)],
  "Caballería moderna", "Modern Cavalry", "Jinetes con radios y misiles: la tradición, al día.",
  "Riders with radios and missiles: tradition, updated.")
f("M14", [["M12"]], 10, "Korean_Peoples_Airforce_Roundel", [MIL], [build(W, "air_base")],
  "Una fuerza aérea propia", "An Air Force of Our Own", "Aviones de entrenamiento y una segunda base.",
  "Training aircraft and a second base.")
f("M15", [["M13"]], 10, "horse_white_plain", [MIL], [idea("mdr_mon_khan_guard")],
  "La guardia del kan", "The Khan's Guard", "Una unidad de élite con los colores de Gengis.",
  "An elite unit in Genghis's colours.", avail="has_completed_focus = mdr_mon_G1")

# Identity
f("I1", [], 5, "focus_DEN_national_unity", [STA], [idea("mdr_mon_chinggis"), party(P_NAT, 0.03)],
  "Gengis Kan, padre de la nación", "Chinggis Khaan, Father of the Nation", "Su nombre y su rostro vuelven a todas partes.",
  "His name and his face return everywhere.", ai=35)
f("I2", [["I1"]], 10, "Generic_Major_City", [STA], [stab(0.05)],
  "Aeropuerto Gengis Kan", "Chinggis Khaan Airport", "El aeropuerto de la capital cambia de nombre (2005).",
  "The capital's airport is renamed (2005).", avail="date > 2004.6.1")
f("I3", [["I1"]], 10, "focus_DEN_national_unity", [STA], [tidea("mdr_mon_800_years", 365)],
  "800 años del Gran Estado Mongol", "800 Years of the Great Mongol State", "El Naadam del aniversario, en 2006.",
  "The anniversary Naadam, in 2006.", avail="date > 2006.1.1")
f("I4", [["I3"]], 10, "BRA_rio_statue", [STA], [stab(0.03), tidea("mdr_mon_tourism_statue", 3650)],
  "El monumento ecuestre", "The Equestrian Statue", "Gengis Kan a caballo, 40 metros de acero (2008).",
  "Chinggis Khaan on horseback, 40 metres of steel (2008).", avail="date > 2007.6.1")
f("I5", [["I1"]], 10, "buddhism", [STA], [stab(0.05), opin("BHU", "mdr_mon_rel_15")],
  "El renacer budista", "The Buddhist Revival", "Gandan y los monasterios se llenan otra vez.",
  "Gandan and the monasteries fill up again.")
f("I6", [["I3"]], 10, "MEX_Rewrite_the_constitution", [STA], [tidea("mdr_mon_script_transition", 730), stab(0.03)],
  "El alfabeto tradicional", "The Traditional Script", "La escritura vertical vuelve a los documentos oficiales (ley de 2015).",
  "The vertical script returns to official documents (2015 law).", avail="date > 2014.1.1")
f("I7", [["I2"]], 10, "focus_generic_horse_studs", [STA], [stab(0.03), ws(0.03)],
  "Los juegos del Naadam", "The Naadam Games", "Lucha, arco y carreras de caballos para todo el país.",
  "Wrestling, archery and horse racing for the whole country.")
f("I8", [["I6"], ["I5"]], 10, "focus_DEN_national_unity", [STA], [idea("mdr_mon_nation_of_mongols"), opin("CHI", "mdr_mon_rel_neg_15")],
  "Mongolia, nación de los mongoles", "Mongolia, Nation of the Mongols", "Somos el hogar de todos los mongoles, también de los que viven afuera.",
  "We are the home of all Mongols, including those living abroad.")
f("I9", [["I8"], ["X14"]], 10, "Generic_Religious_Unity", [STA, DIP], [pp(23), stab(0.02)],
  "El kurultái de los pueblos mongoles", "The Kurultai of the Mongol Peoples", "Una gran asamblea cultural de todos los mongoles.",
  "A great cultural assembly of all Mongols.")
f("I10", [["I9"]], 10, "Generic_Religious_Unity", [STA, DIP], [idea("mdr_mon_mongol_world")],
  "El mundo mongol", "The Mongol World", "Cultura, idioma y turismo: el poder blando de la estepa.",
  "Culture, language and tourism: the soft power of the steppe.",
  avail="NOT = { has_completed_focus = mdr_mon_G1 }")

# Pan-Mongol path (only with a weakened neighbour)
WEAK = "mdr_mon_neighbor_weak = yes"
f("G1", [["I9"], ["M13"]], 10, "focus_CHI_mongolian_unification", [POL, DIP], [party(P_NAT, 0.11), opin("CHI", "mdr_mon_rel_neg_15"), opin("SOV", "mdr_mon_rel_neg_15")],
  "El despertar panmongol", "The Pan-Mongol Awakening", "Los vecinos tambalean: es la hora de los mongoles de afuera.",
  "Our neighbours are faltering: it is the hour of the Mongols abroad.",
  avail=WEAK, ai=0)
f("G2", [["G1"]], 10, "Generic_Religious_Unity", [DIP], [pp(29), party(P_NAT, 0.05)],
  "El Congreso de los Pueblos Mongoles", "The Congress of the Mongol Peoples", "Reclamos culturales, todavía no militares.",
  "Cultural claims, not yet military ones.")
f("G3", [["G2"]], 10, "focus_CHI_mongolian_unification_2", [DIP], [money(-0.07), "mdr_mon_fund_separatists = { STATE = 556 }"],
  "Apoyar a Mongolia Interior", "Support Inner Mongolia", "Dinero y voz para los mongoles de China.",
  "Money and a voice for the Mongols of China.", avail="mdr_mon_china_weak = yes")
f("G4", [["G3"]], 10, "blr_territorial_claims", [DIP], [claim(556), wargoal(556)],
  "Reclamar Mongolia Interior", "Claim Inner Mongolia", "La tierra de nuestros hermanos del sur.",
  "The land of our southern brothers.", avail="mdr_mon_china_weak = yes")
f("G5", [["G4"]], 10, "Claim_Budjak", [DIP], [claim(1097), wargoal(1097)],
  "Hulunbuir y Barga", "Hulunbuir and Barga", "Los pastos del noreste, donde viven los barga.",
  "The northeastern pastures where the Barga live.", avail="mdr_mon_china_weak = yes")
f("G6", [["G2"]], 10, "SOV_russian_mongolia", [DIP], [money(-0.07), "mdr_mon_fund_separatists = { STATE = 1011 }"],
  "Apoyar a Tuvá", "Support Tuva", "Los tuvanos comparten con nosotros la estepa y el budismo.",
  "The Tuvans share the steppe and Buddhism with us.", avail="mdr_mon_russia_weak = yes")
f("G7", [["G6"]], 10, "blr_territorial_claims", [DIP], [claim(1011), join_offer(1011)],
  "Tuvá en el imperio", "Tuva in the Empire", "Si Tuvá ya es libre, le ofrecemos unirse; si no, la reclamamos.",
  "If Tuva is already free, we invite it to join; if not, we claim it.", avail="mdr_mon_russia_weak = yes")
f("G8", [["G6"]], 10, "Claim_Budjak", [DIP], [money(-0.07), "mdr_mon_fund_separatists = { STATE = 686 }"],
  "Apoyar a Buriatia", "Support Buryatia", "Los buriatos, mongoles a orillas del Baikal.",
  "The Buryats, Mongols on the shores of Baikal.", avail="mdr_mon_russia_weak = yes")
f("G9", [["G8"]], 10, "blr_territorial_claims", [DIP], [claim(686), join_offer(686)],
  "Buriatia en el imperio", "Buryatia in the Empire", "Si Buriatia ya es libre, le ofrecemos unirse; si no, la reclamamos.",
  "If Buryatia is already free, we invite it to join; if not, we claim it.", avail="mdr_mon_russia_weak = yes")
f("G10", [["G9"]], 10, "Generic_Religious_Unity", [DIP], [pp(17), opin("SOV", "mdr_mon_rel_neg_15")],
  "Los calmucos del Volga", "The Kalmyks of the Volga", "Hermanos lejanos, demasiado lejos para alcanzarlos: solo un lazo cultural.",
  "Distant brothers, too far to reach: only a cultural bond.")
f("G11", [["G4", "G7", "G9"]], 10, "focus_AFG_integrate_tajik_and_uzbek_republics", [POL], [flag("mdr_mon_integrate")],
  "Integrar a los hermanos", "Integrate Our Brothers", "Los estados mongoles que controlemos se vuelven núcleo con dos años de estabilidad.",
  "Mongol states we control become cores after two stable years.")
f("G12", [["G11"]], 10, "focus_ICE_reclaiming_the_empire", [POL], [idea("mdr_mon_khanate_law")],
  "La ley del Imperio", "The Law of the Empire", "Todos los hombres de la estepa, al servicio del imperio.",
  "Every man of the steppe, in the service of the empire.")
f("G13", [["G12"], ["M15"]], 10, "cavalry", [MIL], [man(23000), exp(25)],
  "El ejército de los diez mil", "The Army of Ten Thousand", "Una nueva generación de jinetes llama a las armas.",
  "A new generation of riders answers the call to arms.")
f("G14", [["G11"]], 10, "Great_northern_railway", [ECO], ["mdr_mon_khanate_railway = yes"],
  "El ferrocarril del imperio", "The Imperial Railway", "Vías hasta los nuevos estados.", "Tracks out to the new states.")
f("G15", [["G12"]], 10, "focus_ICE_reclaiming_the_empire", [POL], ["mdr_mon_proclaim_khanate = yes"],
  "Proclamar el Imperio Mongol", "Proclaim the Mongol Empire", "Ocho siglos después, el imperio vuelve.",
  "Eight centuries later, the empire returns.",
  avail="controls_state = 596 controls_state = 597 controls_state = 556 OR = { controls_state = 1011 controls_state = 686 }")
f("G16", [["G15"]], 10, "Generic_Redraw_Borders", [DIP], ["mdr_mon_world_alarm = yes"],
  "El imperio y el mundo", "The Empire and the World", "Japón, Corea y Kazajistán miran con miedo hacia la estepa.",
  "Japan, Korea and Kazakhstan look at the steppe with fear.")
f("G17", [["G15"]], 10, "economic_community", [ECO], [idea("mdr_mon_pax_mongolica")],
  "Pax Mongolica", "Pax Mongolica", "Paz, comercio y caminos seguros en toda la estepa.",
  "Peace, trade and safe roads across the steppe.", avail="has_stability > 0.6")


# ---------- layout ----------
ORDER = ["P", "E", "S", "X", "M", "I", "G"]


def layout():
    by = {x["id"]: x for x in F}
    depth = {}

    def d(fid):
        if fid in depth:
            return depth[fid]
        fo = by[fid]
        depth[fid] = 0 if not fo["pre"] else 1 + max(d(p) for g in fo["pre"] for p in g)
        return depth[fid]

    for x in F:
        d(x["id"])
    pos, x0 = {}, 0
    for br in ORDER:
        items = [x for x in F if x["branch"] == br]
        rows = {}
        for it in items:
            rows.setdefault(depth[it["id"]], []).append(it)
        width = max(len(r) for r in rows.values()) * 2
        for dep, r in rows.items():
            start = x0 + (width - len(r) * 2) // 2
            for i, it in enumerate(r):
                pos[it["id"]] = (start + i * 2, dep)
        x0 += width + 1
    return pos, x0


def gen_tree(icons):
    pos, max_x = layout()
    out = ["# Generated by herramientas/make_mongolia.py. Do not edit by hand.",
           "focus_tree = {", "\tid = mdr_mongolia_focus",
           "\tshared_focus = mdr_demo_root # Realpolitik: hidden demography branch (common/national_focus/mdr_demography.txt)",
           "\tcountry = {", "\t\tbase = 0", "\t\tmodifier = { add = 10 original_tag = MON }", "\t}",
           "\tdefault = no", "\treset_on_civilwar = no",
           "\tinitial_show_position = { focus = mdr_mon_P1 }",
           f"\tcontinuous_focus_position = {{ x = 50 y = 1700 }}", ""]
    missing = []
    for x in F:
        if x["icon"] not in icons:
            missing.append((x["id"], x["icon"]))
        px, py = pos[x["id"]]
        out += ["\tfocus = {", f"\t\tid = {x['id']}", f"\t\ticon = {x['icon']}", f"\t\tx = {px}", f"\t\ty = {py}",
                f"\t\tcost = {x['cost']}"]
        for g in x["pre"]:
            out.append("\t\tprerequisite = { " + " ".join(f"focus = {p}" for p in g) + " }")
        if x["mutex"]:
            out.append("\t\tmutually_exclusive = { " + " ".join(f"focus = {m}" for m in x["mutex"]) + " }")
        if x["avail"]:
            out.append(f"\t\tavailable = {{ {x['avail']} }}")
        out.append("\t\tsearch_filters = { " + " ".join(x["filt"]) + " }")
        out.append("\t\tcompletion_reward = {")
        out.append(f"\t\t\tlog = \"[GetDateText]: [Root.GetName]: Focus {x['id']}\"")
        for e in x["eff"]:
            out.append("\t\t\t" + e)
        out.append("\t\t}")
        out.append(f"\t\tai_will_do = {{ base = {x['ai']} }}")
        out += ["\t}", ""]
    out += ["}", ""]
    return "\n".join(out), missing, max_x


def gen_loc(lang):
    es = lang == "spanish"
    out = [f"l_{lang}:", f' mdr_mongolia_focus: "{"Mongolia" if es else "Mongolia"}"']
    for x in F:
        name = (x["es"] if es else x["en"]).replace('"', "'")
        desc = (x["des"] if es else x["den"]).replace('"', "'")
        out += [f' {x["id"]}: "{name}"', f' {x["id"]}_desc: "{desc}"']
    return "\n".join(out) + "\n"


def main():
    gfx = "".join(p.read_text(encoding="utf-8", errors="replace") for p in (MD / "interface").glob("goals*.gfx"))
    icons = set(re.findall(r'name\s*=\s*"([^"]+)"', gfx))
    tree, missing, max_x = gen_tree(icons)
    if missing:
        raise SystemExit(f"Icons missing in Millennium Dawn: {missing}")
    ids = [x["id"] for x in F]
    assert len(ids) == len(set(ids)), "duplicate focus id"
    known = set(ids)
    for x in F:
        for g in x["pre"]:
            for p in g:
                assert p in known, (x["id"], p)
        for m in x["mutex"]:
            assert m in known, (x["id"], m)
    (ROOT / "common/national_focus/mdr_mongolia.txt").write_text(tree, encoding="utf-8", newline="\n")
    for lang in ("spanish", "english"):
        (ROOT / f"localisation/{lang}/mdr_mongolia_focus_l_{lang}.yml").write_text(gen_loc(lang), encoding="utf-8-sig", newline="\n")
    print(f"{len(F)} focuses, tree width {max_x}")


if __name__ == "__main__":
    main()
