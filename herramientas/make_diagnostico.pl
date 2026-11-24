# Generates the in-game self check: common/scripted_effects/mdr_diagnostics_gen.txt. Each check writes one "MDR DIAG OK" or
# "MDR DIAG FALLA" line in game.log; herramientas/revisar_logs.pl summarises them. Run from the mod folder: perl herramientas/make_diagnostico.pl
# Add a check as [system, what is being checked, condition that must hold, value to show when it fails].
use strict; use warnings;
my $N = 10;
sub range { my ($v,$a,$b) = @_; "NOT = { check_variable = { $v < $a } } NOT = { check_variable = { $v > $b } }" }

# Checks on the country that runs it. Conditions of a system are skipped if its rule is off.
my @on_ammo = (
	['Municion','reserva entre 0 y la capacidad',"NOT = { check_variable = { mdr_ammo_k < 0 } } NOT = { check_variable = { mdr_ammo_k > mdr_ammo_capacity_k } }",'mdr_ammo_k'],
	['Municion','capacidad positiva','check_variable = { mdr_ammo_capacity_k > 0 }','mdr_ammo_capacity_k'],
	['Municion','produccion no negativa','NOT = { check_variable = { mdr_ammo_gain_k < 0 } }','mdr_ammo_gain_k'],
	['Municion','consumo no negativo','NOT = { check_variable = { mdr_ammo_use_k < 0 } }','mdr_ammo_use_k'],
	['Municion','barra entre 0 y 100',range('mdr_ammo_bar_pct',0,100),'mdr_ammo_bar_pct'],
);
my @on_food = (
	['Comida','reserva no negativa','NOT = { check_variable = { mdr_food_stock < 0 } }','mdr_food_stock'],
	['Comida','reserva dentro de la capacidad','NOT = { check_variable = { mdr_food_stock > mdr_food_capacity } }','mdr_food_stock'],
	['Comida','capacidad positiva','check_variable = { mdr_food_capacity > 0 }','mdr_food_capacity'],
	['Comida','precio mundial de comida positivo','check_variable = { global.mdr_food_price > 0 }','global.mdr_food_price'],
	['Comida','precio de granos positivo','check_variable = { global.mdr_wheat_price > 0 }','global.mdr_wheat_price'],
);
my @on_climate = (
	['Clima','calentamiento razonable',range('global.mdr_warming',0.5,6),'global.mdr_warming'],
	['Clima','emisiones no negativas','NOT = { check_variable = { global.mdr_emissions_index < 0 } }','global.mdr_emissions_index'],
);
my @on_society = (
);
my @always = (
	['Nucleo','constantes iniciadas','has_global_flag = mdr_core_init','global.mdr_version'],
	['Nucleo','pais iniciado','has_country_flag = mdr_country_init','global.mdr_version'],
	['Nucleo','espacios de edificio agregados','has_global_flag = mdr_state_slots_added','global.mdr_version'],
	['Uranio','minas de 2000 colocadas','has_global_flag = mdr_uranium_deposits_added','global.mdr_uranium_price'],
	['Tierras raras','plantas de 2000 colocadas','has_global_flag = mdr_rare_earths_added','global.mdr_ree_price'],
	['Comida','suelo cultivable de 2000 colocado','has_global_flag = mdr_cropland_added','global.mdr_wheat_price'],
	['Nucleo','corre el chequeo diario','check_variable = { global.mdr_diag_days > 0 }','global.mdr_diag_days'],
	['Nucleo','corre el chequeo semanal (hace falta una semana de juego)','check_variable = { global.mdr_diag_weeks > 0 }','global.mdr_diag_weeks'],
	['Nucleo','corre el chequeo mensual (hace falta un mes de juego)','check_variable = { global.mdr_diag_months > 0 }','global.mdr_diag_months'],
	['Leyes','ley de medios entre 1 y 5',range('mdr_media_level',1,5),'mdr_media_level'],
	['Leyes','reunion entre 1 y 4',range('mdr_assembly_level',1,4),'mdr_assembly_level'],
	['Leyes','sociedad civil entre 1 y 4',range('mdr_ngo_level',1,4),'mdr_ngo_level'],
	['Leyes','sindicatos entre 1 y 4',range('mdr_union_level',1,4),'mdr_union_level'],
	['Leyes','vigilancia entre 1 y 4',range('mdr_surveillance_level',1,4),'mdr_surveillance_level'],
	['Leyes','jubilacion entre 1 y 5',range('mdr_retire_level',1,5),'mdr_retire_level'],
	['Leyes','descontento oculto entre 0 y 100',range('mdr_unrest_hidden',0,100),'mdr_unrest_hidden'],
	['Economia','fondo no negativo','NOT = { check_variable = { mdr_fund_balance < 0 } }','mdr_fund_balance'],
	['Uranio','precio positivo','check_variable = { global.mdr_uranium_price > 0 }','global.mdr_uranium_price'],
	['Uranio','necesidad no negativa','NOT = { check_variable = { mdr_uranium_need < 0 } }','mdr_uranium_need'],
	['Tierras raras','precio positivo','check_variable = { global.mdr_ree_price > 0 }','global.mdr_ree_price'],
	['Edificios','PIB de edificios no negativo','NOT = { check_variable = { mdr_buildings_gdp < 0 } }','mdr_buildings_gdp'],
	['Capitulacion','territorio entre 0 y 1',range('mdr_cap_t',0,1.001),'mdr_cap_t'],
	['Prisioneros','cuenta no negativa','NOT = { check_variable = { mdr_pow_count < 0 } }','mdr_pow_count'],
	['Prisioneros','cuenta igual a las filas ocupadas','check_variable = { mdr_pow_count = mdr_diag_pow_rows }','mdr_pow_count'],
	['Venta de barcos','listas de pedidos del mismo largo','check_variable = { mdr_sc_buyer^num = mdr_sc_type^num } check_variable = { mdr_sc_buyer^num = mdr_sc_gen^num } check_variable = { mdr_sc_buyer^num = mdr_sc_qty^num } check_variable = { mdr_sc_buyer^num = mdr_sc_unit^num } check_variable = { mdr_sc_buyer^num = mdr_sc_days^num } check_variable = { mdr_sc_buyer^num = mdr_sc_wait^num } check_variable = { mdr_sc_buyer^num = mdr_sc_kind^num } check_variable = { mdr_sc_buyer^num = mdr_sc_total^num }','mdr_sc_buyer^num'],
	['Espacio','nivel entre 0 y 3',range('mdr_space_tier',0,3),'mdr_space_tier'],
	['Espacio','presupuesto entre 0 y 500 (centesimos del PBI)',range('mdr_space_budget',0,500),'mdr_space_budget'],
	['Uranio','faltante no negativo','NOT = { check_variable = { mdr_uranium_shortfall < 0 } }','mdr_uranium_shortfall'],
	['Tierras raras','faltante no negativo','NOT = { check_variable = { mdr_ree_shortfall < 0 } }','mdr_ree_shortfall'],
	['Militar','desercion no negativa','NOT = { check_variable = { mdr_desertion_k < 0 } }','mdr_desertion_k'],
	['Shocks','multiplicador del petroleo entre 0,3 y 3',range('global.mdr_shock_oil',0.3,3),'global.mdr_shock_oil'],
	['Shocks','multiplicador de granos entre 0,3 y 3',range('global.mdr_shock_grain',0.3,3),'global.mdr_shock_grain'],
	['Shocks','multiplicador del uranio entre 0,3 y 3',range('global.mdr_shock_uranium',0.3,3),'global.mdr_shock_uranium'],
	['Shocks','multiplicador de tierras raras entre 0,3 y 3',range('global.mdr_shock_ree',0.3,3),'global.mdr_shock_ree'],
	(map { ['Estrechos',"estrecho $_ cerrado tiene quien lo cerro","OR = { NOT = { has_global_flag = mdr_strait_${_}_closed } check_variable = { global.mdr_strait_${_}_closer > 0 } }","global.mdr_strait_${_}_closer"] } 1..7),
	['Millennium Dawn','PBI positivo','check_variable = { gdp_total > 0 }','gdp_total'],
	['Millennium Dawn','popularidad de los partidos suma 1','check_variable = { mdr_diag_pop_sum > 0.95 } check_variable = { mdr_diag_pop_sum < 1.05 }','mdr_diag_pop_sum'],
);
# Sum of Millennium Dawn's party popularities in the current country, into temp variable mdr_diag_pop_sum.
my $POP_SUM = "set_temp_variable = { mdr_diag_pop_sum = 0 } for_each_loop = { array = party_pop_array value = mdr_diag_pv add_to_temp_variable = { mdr_diag_pop_sum = mdr_diag_pv } }";

sub check { my ($s,$l,$c,$v,$ind) = @_; $ind //= "\t";
	"${ind}if = { limit = { $c }\n$ind\tlog = \"MDR DIAG OK $s: $l\"\n$ind\tadd_to_variable = { global.mdr_diag_ok = 1 }\n$ind}\n${ind}else = {\n$ind\tlog = \"MDR DIAG FALLA $s: $l (valor [?$v]) [Root.GetName] [GetDateText]\"\n$ind\tadd_to_variable = { global.mdr_diag_bad = 1 }\n$ind}\n" }
# Like check, but a miss is only worth a look (it can happen by chance), so it does not count as a failure.
sub warn_check { my ($s,$l,$c,$v,$ind) = @_; $ind //= "\t";
	"${ind}if = { limit = { $c }\n$ind\tlog = \"MDR DIAG OK $s: $l\"\n$ind\tadd_to_variable = { global.mdr_diag_ok = 1 }\n$ind}\n${ind}else = {\n$ind\tlog = \"MDR DIAG AVISO $s: $l (valor [?$v]) [Root.GetName] [GetDateText]\"\n$ind}\n" }

my $e = "# Generated by herramientas/make_diagnostico.pl. The self check of the diagnostic mode, run by the decision mdr_diag_full.\n\n";
$e .= "# Country scope: the player who runs it.\nmdr_diag_run = {\n\tlog = \"MDR DIAG INICIO [GetDateText] [Root.GetName]\"\n\tset_variable = { global.mdr_diag_ok = 0 }\n\tset_variable = { global.mdr_diag_bad = 0 }\n";
$e .= "\tset_temp_variable = { mdr_diag_pow_rows = 0 }\n\t$POP_SUM\n";
$e .= "\tif = { limit = { check_variable = { global.mdr_pow_owner_$_ = THIS.id } } add_to_temp_variable = { mdr_diag_pow_rows = 1 } }\n" for 1..$N;
$e .= check(@$_) for @always;
$e .= "\tif = { limit = { mdr_ammo_on = yes } mdr_diag_run_ammo = yes }\n\tif = { limit = { mdr_food_on = yes } mdr_diag_run_food = yes }\n\tif = { limit = { mdr_climate_on = yes } mdr_diag_run_climate = yes }\n\tif = { limit = { mdr_society_on = yes } mdr_diag_run_society = yes }\n\tmdr_diag_run_world = yes\n\tmdr_diag_run_slots = yes\n\tmdr_diag_run_orders = yes\n\tmdr_diag_run_info = yes\n";
$e .= "\tlog = \"MDR DIAG FIN: [?global.mdr_diag_ok] OK, [?global.mdr_diag_bad] FALLA\"\n";
# The automatic weekly run sets mdr_diag_quiet so no window interrupts an unattended game.
$e .= "\tif = { limit = { NOT = { check_variable = { mdr_diag_quiet = 1 } } } country_event = { id = mdr_diag.1 } }\n}\n\n";
for my $x (['ammo',\@on_ammo],['food',\@on_food],['climate',\@on_climate],['society',\@on_society]) { $e .= "mdr_diag_run_$x->[0] = {\n"; $e .= check(@$_) for @{$x->[1]}; $e .= "}\n\n"; }

# World: every country and state.
$e .= "# Every country and state: counts how many break a rule, so one line reports the whole world.\nmdr_diag_run_world = {\n";
my @world = (
	['Mundo','paises sin iniciar','mdr_w_init','NOT = { has_country_flag = mdr_country_init }'],
	['Mundo','paises sin ley de medios','mdr_w_media','NOT = { check_variable = { mdr_media_level > 0 } }'],
	['Mundo','paises sin edad de jubilacion','mdr_w_retire','NOT = { check_variable = { mdr_retire_level > 0 } }'],
	['Mundo','paises con municion fuera de rango','mdr_w_ammo','mdr_ammo_on = yes OR = { check_variable = { mdr_ammo_k < 0 } check_variable = { mdr_ammo_k > mdr_ammo_capacity_k } }'],
	['Mundo','paises con comida negativa','mdr_w_food','mdr_food_on = yes check_variable = { mdr_food_stock < 0 }'],
	['Mundo','paises con prisioneros negativos','mdr_w_ai','check_variable = { mdr_pow_ai_held < 0 }'],
	['Mundo','paises sin leyes civiles','mdr_w_civil','NOT = { check_variable = { mdr_assembly_level > 0 } }'],
	['Mundo','paises con descontento fuera de rango','mdr_w_unrest','OR = { check_variable = { mdr_unrest_hidden < 0 } check_variable = { mdr_unrest_hidden > 100 } }'],
	['Mundo','paises con fondo de estabilizacion negativo','mdr_w_fund','check_variable = { mdr_fund_balance < 0 }'],
	['Mundo','paises con presupuesto espacial fuera de rango','mdr_w_space','OR = { check_variable = { mdr_space_budget < 0 } check_variable = { mdr_space_budget > 500 } }'],
	['Mundo','paises con nivel espacial fuera de rango','mdr_w_tier','OR = { check_variable = { mdr_space_tier < 0 } check_variable = { mdr_space_tier > 3 } }'],
	['Mundo','paises con faltante de uranio negativo','mdr_w_u','check_variable = { mdr_uranium_shortfall < 0 }'],
	['Mundo','paises con faltante de tierras raras negativo','mdr_w_ree','check_variable = { mdr_ree_shortfall < 0 }'],
	['Mundo','paises con desercion negativa','mdr_w_des','check_variable = { mdr_desertion_k < 0 }'],
	['Mundo','paises con comida por encima de la capacidad','mdr_w_foodcap','mdr_food_on = yes check_variable = { mdr_food_stock > mdr_food_capacity } check_variable = { mdr_food_capacity > 0 }'],
	['Millennium Dawn','paises con PBI no positivo','mdr_w_gdp','NOT = { check_variable = { gdp_total > 0 } }'],
	['Millennium Dawn','paises cuyos partidos no suman 100%','mdr_w_pop','OR = { check_variable = { mdr_diag_pop_sum < 0.95 } check_variable = { mdr_diag_pop_sum > 1.05 } }'],
);
$e .= "\tset_temp_variable = { $_->[2] = 0 }\n" for @world;
$e .= "\tevery_country = {\n\t\tlimit = { exists = yes }\n\t\t$POP_SUM\n";
$e .= "\t\tif = { limit = { $_->[3] } add_to_temp_variable = { $_->[2] = 1 } }\n" for @world;
$e .= "\t}\n";
# Millennium Dawn's own data is only a warning: a country it never set up is its matter, not ours.
$e .= ($_->[0] eq 'Millennium Dawn' ? \&warn_check : \&check)->($_->[0],$_->[1],"check_variable = { $_->[2] = 0 }",$_->[2]) for @world;
$e .= "\tset_temp_variable = { mdr_w_pol = 0 }\n\tset_temp_variable = { mdr_w_a = 0 }\n\tevery_state = {\n\t\tif = { limit = { OR = { check_variable = { mdr_pollution < 0 } check_variable = { mdr_pollution > 100 } } } add_to_temp_variable = { mdr_w_pol = 1 } }\n\t\tif = { limit = { has_state_flag = mdr_arable_land } add_to_temp_variable = { mdr_w_a = 1 } }\n\t}\n";
$e .= check('Clima','estados con contaminacion fuera de rango','check_variable = { mdr_w_pol = 0 }','mdr_w_pol');
$e .= check('Comida','hay estados con suelo cultivable','check_variable = { mdr_w_a > 0 }','mdr_w_a');
$e .= "}\n\n";

# Prisoner slots of this country.
$e .= "mdr_diag_run_slots = {\n";
for my $i (1..$N) {
	$e .= "\tif = { limit = { check_variable = { global.mdr_pow_owner_$i = THIS.id } }\n";
	$e .= check('Prisioneros',"fila $i, estado 0 o 1",range("global.mdr_pow_status_$i",0,1),"global.mdr_pow_status_$i","\t\t");
	$e .= check('Prisioneros',"fila $i, resistencia entre 0 y 100",range("global.mdr_pow_res_$i",0,100),"global.mdr_pow_res_$i","\t\t");
	$e .= check('Prisioneros',"fila $i, cooperacion entre 0 y 100",range("global.mdr_pow_coop_$i",0,100),"global.mdr_pow_coop_$i","\t\t");
	$e .= check('Prisioneros',"fila $i, operacion entre 0 y 6",range("global.mdr_pow_op_$i",0,6),"global.mdr_pow_op_$i","\t\t");
	$e .= check('Prisioneros',"fila $i, tiene pais de origen","check_variable = { global.mdr_pow_from_$i > 0 }","global.mdr_pow_from_$i","\t\t");
	$e .= "\t\tlog = \"MDR DIAG INFO Prisionero fila $i: [mdr_pow_$i.GetName], nivel [?global.mdr_pow_skill_$i], retrato [?global.mdr_pow_face_$i], estado [?global.mdr_pow_status_$i]\"\n\t}\n";
}
$e .= "}\n\n";

# Ship orders of this country.
$e .= "mdr_diag_run_orders = {\n\tset_temp_variable = { mdr_diag_o_bad = 0 }\n\tfor_each_loop = {\n\t\tarray = mdr_sc_buyer\n\t\tvalue = mdr_diag_b\n\t\tindex = mdr_diag_i\n\t\tset_temp_variable = { mdr_diag_x = mdr_sc_qty^mdr_diag_i }\n\t\tif = { limit = { check_variable = { mdr_diag_x < 1 } } add_to_temp_variable = { mdr_diag_o_bad = 1 } }\n\t\tset_temp_variable = { mdr_diag_x = mdr_sc_unit^mdr_diag_i }\n\t\tif = { limit = { check_variable = { mdr_diag_x < 0 } } add_to_temp_variable = { mdr_diag_o_bad = 1 } }\n\t\tset_temp_variable = { mdr_diag_x = mdr_sc_type^mdr_diag_i }\n\t\tif = { limit = { OR = { check_variable = { mdr_diag_x < 1 } check_variable = { mdr_diag_x > 18 } } } add_to_temp_variable = { mdr_diag_o_bad = 1 } }\n\t\tset_temp_variable = { mdr_diag_q = mdr_sc_qty^mdr_diag_i }\n\t\tset_temp_variable = { mdr_diag_d = mdr_sc_days^mdr_diag_i }\n\t\tlog = \"MDR DIAG INFO Pedido: comprador [?mdr_diag_b], tipo [?mdr_diag_x], cantidad [?mdr_diag_q], dias [?mdr_diag_d]\"\n\t}\n";
$e .= check('Venta de barcos','pedidos con datos validos','check_variable = { mdr_diag_o_bad = 0 }','mdr_diag_o_bad');
$e .= "}\n\n";

# Data worth seeing, not pass or fail.
$e .= "mdr_diag_run_info = {\n";
my @info = (
	'Reglas: municion [?global.mdr_diag_r1], comida [?global.mdr_diag_r2], clima [?global.mdr_diag_r3], estrechos [?global.mdr_diag_r4], protestas [?global.mdr_diag_r5], barcos [?global.mdr_diag_r6] (1 activada)',
	'Municion: reserva [?mdr_ammo_k], capacidad [?mdr_ammo_capacity_k], produccion [?mdr_ammo_gain_k], consumo [?mdr_ammo_use_k], maniobras [?mdr_ammo_drill_k]',
	'Comida: reserva [?mdr_food_stock], capacidad [?mdr_food_capacity], dias [?mdr_food_days]',
	'Precios: comida [?global.mdr_food_price], granos [?global.mdr_wheat_price], uranio [?global.mdr_uranium_price], tierras raras [?global.mdr_ree_price]',
	'Clima: calentamiento [?global.mdr_warming], emisiones [?global.mdr_emissions_index]',
	'Sociedad: protesta [?protest_strength], descontento [?mdr_unrest_hidden]',
	'Barcos: total [?num_ships], pedidos [?mdr_sc_buyer^num]',
	'Ticks: dias [?global.mdr_diag_days], semanas [?global.mdr_diag_weeks], meses [?global.mdr_diag_months]',
	'Mundo: [?mdr_w_a] estados con suelo cultivable',
);
my @rules = (['mdr_ammo_on',1],['mdr_food_on',2],['mdr_climate_on',3],['mdr_straits_on',4],['mdr_society_on',5],['mdr_ships_on',6]);
for my $r (@rules) { $e .= "\tset_variable = { global.mdr_diag_r$r->[1] = 0 }\n\tif = { limit = { $r->[0] = yes } set_variable = { global.mdr_diag_r$r->[1] = 1 } }\n"; }
$e .= "\tlog = \"MDR DIAG INFO $_\"\n" for @info;
for my $i (1..7) { $e .= "\tif = { limit = { has_global_flag = mdr_strait_${i}_closed } log = \"MDR DIAG INFO Estrecho $i cerrado\" }\n"; }
$e .= "}\n";

# ---- Automatic mode: with the diagnostic rule on, the game tests itself while it runs unattended. ----
# Called every day for the player (on_daily). global.mdr_diag_days counts the days since the start.
# Each test: [day, name, guard, effect that forces the situation, [[day to verify, what, condition, value, warn?], ...]].
# Days leave a week between tests so every weekly system has run before the result is read.
my @plan = (
	[2, 'Reiniciar el pais', 'always = yes', 'mdr_init_constants = yes mdr_country_init = yes',
		[[3, 'el pais queda iniciado', 'has_country_flag = mdr_country_init', 'global.mdr_version']]],
	[10, 'Vaciar la municion', 'mdr_ammo_on = yes', 'set_variable = { mdr_ammo_k = 0 } mdr_ammo_update_display = yes',
		[[24,'las fabricas militares la vuelven a llenar', 'OR = { NOT = { num_of_military_factories > 0 } check_variable = { mdr_ammo_k > 0 } }', 'mdr_ammo_k'],
		 [24, 'la reserva sigue dentro de la capacidad', 'NOT = { check_variable = { mdr_ammo_k > mdr_ammo_capacity_k } }', 'mdr_ammo_k']]],
	[30, 'Vaciar la comida', 'mdr_food_on = yes', 'set_variable = { mdr_food_stock = 0 }',
		[[38, 'la reserva no queda negativa', 'NOT = { check_variable = { mdr_food_stock < 0 } }', 'mdr_food_stock'],
		 [38, 'la capacidad sigue positiva', 'check_variable = { mdr_food_capacity > 0 }', 'mdr_food_capacity']]],
	[40, 'Cerrar el canal de Suez', 'mdr_straits_on = yes NOT = { has_global_flag = mdr_strait_2_closed }', 'set_temp_variable = { mdr_strait_id = 2 } mdr_strait_close = yes',
		[[41, 'Suez queda cerrado', 'has_global_flag = mdr_strait_2_closed', 'global.mdr_strait_2_closer'],
		 [41, 'queda anotado quien lo cerro', 'check_variable = { global.mdr_strait_2_closer > 0 }', 'global.mdr_strait_2_closer']]],
	[45, 'Reabrir el canal de Suez', 'has_global_flag = mdr_strait_2_closed', 'set_temp_variable = { mdr_strait_id = 2 } mdr_strait_reopen = yes',
		[[46, 'Suez queda abierto', 'NOT = { has_global_flag = mdr_strait_2_closed }', 'global.mdr_strait_2_closer']]],
	(map { my ($n,$r,$g) = @$_;
		[46 + 2*$r, "Shock de $n", 'always = yes', "set_temp_variable = { mdr_shock_res = $r } set_temp_variable = { mdr_shock_target = 1.6 } set_temp_variable = { mdr_shock_weeks = 4 } set_temp_variable = { mdr_shock_cause = 0 } mdr_shock_start = yes",
			[[62, "el precio de $n sube", "check_variable = { global.mdr_shock_$g > 1.01 }", "global.mdr_shock_$g"],
			 [150, "el precio de $n vuelve cerca de lo normal", "check_variable = { global.mdr_shock_$g < 1.25 }", "global.mdr_shock_$g", 1]]] }
		(['petroleo',1,'oil'],['granos',2,'grain'],['uranio',3,'uranium'],['tierras raras',4,'ree'])),
	[70, 'Forzar un desastre', 'always = yes', 'clr_country_flag = mdr_disaster_cooldown set_temp_variable = { mdr_dis_type = 0 } mdr_disaster_random_strike = yes',
		[[71, 'el desastre ocurre y deja la espera entre desastres', 'has_country_flag = mdr_disaster_cooldown', 'global.mdr_version']]],
	[80, 'Capturar un general de un vecino', 'any_neighbor_country = { exists = yes }',
		'set_variable = { global.mdr_diag_pow_before = mdr_pow_count } random_neighbor_country = { limit = { exists = yes } set_temp_variable = { mdr_pow_max = mdr_pow_lost } add_to_temp_variable = { mdr_pow_max = 1 } mdr_pow_take = yes }',
		[[81, 'hay un preso mas (puede faltar si el vecino no tiene generales)', 'check_variable = { mdr_pow_count > global.mdr_diag_pow_before }', 'mdr_pow_count', 1],
		 [81, 'la cuenta de presos no pasa de 10', range('mdr_pow_count',0,10), 'mdr_pow_count']]],
	[90, 'Un vecino pide comprar un barco', 'mdr_ships_on = yes any_neighbor_country = { exists = yes }',
		'random_neighbor_country = { limit = { exists = yes } country_event = { id = mdr_diag.2 } }',
		[[110, 'las listas de pedidos siguen del mismo largo', 'check_variable = { mdr_sc_buyer^num = mdr_sc_qty^num }', 'mdr_sc_buyer^num']]],
	[100, 'Empezar el COVID historico', 'NOT = { has_global_flag = mdr_covid_launched } NOT = { has_global_flag = COVID_start_of_pandemic } NOT = { has_game_rule = { rule = mdr_rule_covid option = disabled } }', 'mdr_covid_launch = yes',
		[[101, 'el COVID queda lanzado', 'has_global_flag = mdr_covid_launched', 'global.mdr_version']]],
	[130, 'Empezar las vacunas', 'has_global_flag = mdr_covid_launched NOT = { has_global_flag = mdr_covid_vaccines_started }', 'mdr_covid_vaccines = yes',
		[[131, 'las vacunas quedan en marcha', 'has_global_flag = mdr_covid_vaccines_started', 'global.mdr_version']]],
);
my $LAST = 160;
my %by_day;
for my $t (@plan) {
	my ($d,$name,$guard,$fx,$ver) = @$t;
	push @{$by_day{$d}}, "\t\tif = { limit = { $guard }\n\t\t\tlog = \"MDR DIAG PRUEBA $name: empieza [GetDateText]\"\n\t\t\tset_global_flag = mdr_diag_t_$d\n\t\t\t$fx\n\t\t}\n\t\telse = { log = \"MDR DIAG INFO Prueba salteada (no corresponde en esta partida): $name\" }\n";
	for my $v (@$ver) {
		my ($vd,$what,$c,$val,$w) = @$v;
		push @{$by_day{$vd}}, "\t\tif = { limit = { has_global_flag = mdr_diag_t_$d }\n" . ($w ? \&warn_check : \&check)->('Prueba', "$name: $what", $c, $val, "\t\t\t") . "\t\t}\n";
	}
}
$e .= "\n# Automatic mode (generated). Player scope, every day, only with the diagnostic rule.\nmdr_diag_auto_daily = {\n";
$e .= "\tif = { limit = { check_variable = { global.mdr_diag_days = 1 } }\n\t\tlog = \"MDR DIAG AUTO INICIO [GetDateText] [Root.GetName]: pruebas hasta el dia $LAST, despues un control completo por semana\"\n\t}\n";
for my $d (sort { $a <=> $b } keys %by_day) { $e .= "\tif = { limit = { check_variable = { global.mdr_diag_days = $d } }\n" . join('', @{$by_day{$d}}) . "\t}\n"; }
# Full quiet check every week (day 8, 15, 22...), and the summary window once the tests are over.
$e .= "\tset_temp_variable = { mdr_diag_wk = global.mdr_diag_days }\n\tmodulo_temp_variable = { mdr_diag_wk = 7 }\n";
$e .= "\tif = { limit = { check_variable = { mdr_diag_wk = 1 } check_variable = { global.mdr_diag_days > 1 } }\n\t\tset_temp_variable = { mdr_diag_quiet = 1 }\n\t\tmdr_diag_run = yes\n\t}\n";
$e .= "\tif = { limit = { check_variable = { global.mdr_diag_days = $LAST } }\n\t\tlog = \"MDR DIAG AUTO FIN [GetDateText]: termino el plan de pruebas; sigue el control semanal\"\n\t\tset_temp_variable = { mdr_diag_quiet = 0 }\n\t\tmdr_diag_run = yes\n\t}\n}\n";

open my $o, '>:raw', 'common/scripted_effects/mdr_diagnostics_gen.txt' or die; print $o $e; close $o;
print "ok\n";
