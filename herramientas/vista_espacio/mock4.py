import re, sys, itertools

sp = sys.argv[1]
src = open(sp + "/mock.py", encoding="utf-8").read()
head = src[:src.index("pages = [render(")]
head = head.replace('for line in open("localisation/spanish/mdr_space_l_spanish.yml", encoding="utf-8-sig"):\n', 'for line in itertools.chain(open("localisation/spanish/mdr_space_l_spanish.yml", encoding="utf-8-sig"), open("localisation/spanish/mdr_space_program_l_spanish.yml", encoding="utf-8-sig")):\n')
exec(compile(head, "mock", "exec"))
loc = {k: v.replace("\\n", " · ").replace("$$", "$") for k, v in loc.items()}
sample.update({"?mdr_space_active|0": "1", "?mdr_space_slots|0": "2", "?mdr_space_hq|0": "3", "?mdr_space_prestige|0": "28", "?mdr_space_scientists|0": "1240", "?mdr_space_engineers|0": "3800", "?mdr_space_astronauts|0": "40", "?global.mdr_space_debris|0": "9", "mdr_space_body_name": "Marte", "mdr_space_body_text": "Agua, CO2 y gravedad útil. El gran destino: se puede colonizar.", "mdr_space_body_state": "§GYa llegamos.§!", "mdr_space_body_step": "§RFalta:§! Aerofrenado", "mdr_space_next_step": loc["MDR_SPACE_STEP_IDLE"].replace("[mdr_space_suggest]","Banco de motores"), "?mdr_col_moon_pop|0": "16", "?mdr_col_moon_cap|0": "40", "?mdr_col_moon_morale|0": "82", "?mdr_col_moon_greenhouse|0": "2", "?mdr_col_moon_mine|0": "1", "?mdr_col_moon_reactor|0": "1", "?mdr_col_moon_workshop|0": "0", "?mdr_col_moon_water|0": "61", "?mdr_col_moon_food|0": "48", "?mdr_col_moon_energy|0": "70", "?mdr_col_moon_oxygen|0": "55", "?mdr_space_site_levels|0": "5", "?mdr_space_site_speed_pct|1": "21.5", "?mdr_space_site_reliability_pct|1": "8.5", "?mdr_space_site_cost_pct|1": "6.0", "?mdr_space_site_science_week|1": "7.3", "mdr_space_typed": "Roscosmos", "mdr_space_goal_now": "Vuelo tripulado", "mdr_space_goal_now_status": "§RFalta:§! Cuerpo de astronautas", "mdr_space_suggest": "Banco de motores", "mdr_col_moon_step": "§RFalta:§! Inyección translunar", "mdr_col_mars_step": "§RFalta:§! Asistencia gravitatoria", "?mdr_space_budget_week|3": "0.176", "?mdr_space_payroll|3": "0.112", "?mdr_space_week_cost|3": "0.288", "?mdr_space_chance_pct|0": "89"})
for key in list(loc):
    m = re.match(r"MDR_S[AG]_(\w+)_STATUS$", key)
    if m:
        sample[f"mdr_s{'a' if key.startswith('MDR_SA') else 'g'}_{m.group(1).lower()}_status"] = "§RFalta:§! Navegación interplanetaria" if hash(key) % 2 else "§GListo para iniciar§!"
for name in list(win):
    b = win[name]
    b = re.sub(r"\t\tbuttonType = \{ name = \"mdr_sa\w+_(?:queue|unqueue)\"[^\n]*\n", "", b)
    b = re.sub(r"\t\tbuttonType = \{ name = \"mdr_(?:pc|col_route)\w*_off\"[^\n]*\n", "", b)
    b = re.sub(r"\t\tbuttonType = \{ name = \"mdr_sg_\w+_claim\"[^\n]*\n", "", b)
    b = re.sub(r"\t\ticonType = \{ name = \"mdr_space_body_(?:ring|photo)_(?:1|2|3|4|6|7|8)\"[^\n]*\n", "", b)
    win[name] = b
_load = load
# Finance chart: sample years, oldest first, and their bar heights.
SPEND = {4: ("2001", "7.9", 39), 3: ("2002", "8.4", 42), 2: ("2003", "8.8", 44), 1: ("2004", "10.1", 51), 0: ("2005", "4.6", 24)}
sample.update({f"?mdr_space_spend_y{i}|0": v[0] for i, v in SPEND.items()})
sample.update({f"?mdr_space_spend_{i}|1": v[1] for i, v in SPEND.items()})
sample.update({"?mdr_space_contract_cost|3": "0.090", "mdr_pc_launch_signed_name": "Arianespace", "mdr_pc_launch_signed_cost": loc["MDR_PCO_ARIANESPACE_COST"], "mdr_pc_sat_signed_name": loc["MDR_PC_NONE"], "mdr_pc_sat_signed_cost": "", "mdr_pc_crew_signed_name": "Glavkosmos", "mdr_pc_crew_signed_cost": loc["MDR_PCO_GLAVKOSMOS_COST"], "mdr_pc_data_signed_name": loc["MDR_PC_NONE"], "mdr_pc_data_signed_cost": ""})
sample["?mdr_space_budget_pct|2"] = "0.13"
for svc, cid in (("launch", "SPACEX"), ("sat", "LORAL"), ("crew", "GLAVKOSMOS"), ("data", "PLANET")):
    sample[f"mdr_pc_{svc}_view_name"] = loc[f"MDR_PCO_{cid}"]
    sample[f"mdr_pc_{svc}_view_info"] = loc[f"MDR_PCO_{cid}_INFO"].replace("[USA.GetName]", "Estados Unidos").replace("[SOV.GetName]", "Rusia")
sample["mdr_pc_launch_view_state"] = loc["MDR_PCO_SPACEX_SOON"]
sample["mdr_pc_sat_view_state"] = loc["MDR_PCO_LORAL_FREE"]
sample["mdr_pc_crew_view_state"] = loc["MDR_PCO_GLAVKOSMOS_ON"]
sample["mdr_pc_data_view_state"] = loc["MDR_PCO_PLANET_SOON"]
_bars = itertools.cycle([SPEND[i][2] for i in (4, 3, 2, 1, 0)])
def load(name, frame=1):
    return _load(name, next(_bars) if name == "GFX_mdr_space_chart_bar" else frame)
globals()["load"] = load
names = [("mdr_space_solar_window", 6), ("mdr_space_goals_window", 2), ("mdr_space_colony_moon_window", 8), ("mdr_space_colony_none_window", 8)]
views = [render(n, k) for n, k in names]
W_ = views[0].width
sheet = Image.new("RGBA", (2 * W_ + 30, 2 * views[0].height + 30), (58, 74, 58, 255))
for i, v in enumerate(views):
    sheet.alpha_composite(v, (10 + i % 2 * (W_ + 10), 10 + i // 2 * (views[0].height + 10)))
sheet.convert("RGB").save(sp + "/menu_mock4.png")
planets = Image.new("RGBA", (900, 130), (10, 12, 20, 255))
x = 8
for n in ("mercury", "venus", "earth", "moon", "mars", "asteroids", "jupiter", "saturn"):
    im = Image.open(f"gfx/interface/mdr/space/icons/planet_{n}.dds").convert("RGBA")
    big = im.resize((im.width * 2, im.height * 2), Image.LANCZOS)
    planets.alpha_composite(big, (x, 2))
    x += big.width + 8
planets.convert("RGB").save(sp + "/planets.png")
print(sheet.size)
