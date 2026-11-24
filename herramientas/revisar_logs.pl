# Reads the game's logs after playing and writes herramientas/informe_logs.txt: our errors grouped by system,
# the in-game diagnostic results (MDR DIAG lines) and whether the game log ends cleanly.
# Run from the mod folder: perl herramientas/revisar_logs.pl
use strict; use warnings;
my $LOGS = '../../logs';
sub slurp { open my $h, '<:raw', $_[0] or return ''; local $/; my $t = <$h>; close $h; $t // '' }

my $err = slurp("$LOGS/error.log");
my $game = slurp("$LOGS/game.log");
my (%ours, %copy, %md, %base, %known); my $total = 0;

# Things that look like errors and are not.
my @false = (
	[qr/Unexpected token: context_type/, 'context_type en ventanas de Diplomacia: Millennium Dawn avisa que es falso'],
	[qr/Invalid supported_version/, 'supported_version en los .mod: el mismo aviso da Millennium Dawn'],
	[qr/Unknown promotion "mdr_pow_\d+"/, 'Filas vacias de prisioneros antes de capturar a alguien'],
);
my %sys = (
	mdr_ammo=>'Municion', mdr_food=>'Comida', mdr_wheat=>'Comida', mdr_cropland=>'Comida', mdr_fertilizer=>'Comida',
	mdr_uranium=>'Uranio', mdr_rare_earth=>'Tierras raras', mdr_ree=>'Tierras raras', mdr_buildings=>'Edificios',
	mdr_climate=>'Clima', mdr_pollution=>'Clima', mdr_society=>'Sociedad', mdr_civil=>'Leyes civiles', mdr_retire=>'Leyes civiles', mdr_media=>'Ley de medios',
	mdr_economy=>'Economia', mdr_economic=>'Economia', mdr_shock=>'Shocks', mdr_trade=>'Comercio', mdr_strait=>'Estrechos', mdr_disaster=>'Desastres',
	mdr_covid=>'COVID', mdr_treat=>'Tratados', mdr_military=>'Militar', mdr_capitulation=>'Capitulacion', mdr_nuclear=>'Nuclear',
	mdr_pow=>'Prisioneros', mdr_prison=>'Prisioneros', mdr_sale=>'Venta de barcos', mdr_ship=>'Venta de barcos', mdr_sell=>'Venta de barcos',
	mdr_space=>'Espacio', mdr_alert=>'Alertas', mdr_demo=>'Demografia', mdr_diag=>'Diagnostico', mdr_arctic=>'Mapa', mdr_rule=>'Reglas', mdr_ai=>'IA',
);
sub system_of { my $l = shift; for my $k (sort { length $b <=> length $a } keys %sys) { return $sys{$k} if $l =~ /\b$k/i; } 'Otros de Realpolitik' }

for my $l (split /\r?\n/, $err) {
	next unless $l =~ /\S/; $total++;
	(my $m = $l) =~ s/^\[[^\]]*\](?:\[[^\]]*\])?(?:\[[^\]]*\])?:?\s*//;
	my $hit = 0;
	for my $f (@false) { if ($m =~ $f->[0]) { $known{$f->[1]}++; $hit = 1; last } }
	next if $hit;
	if ($m =~ /mdr_|MDR_|Realpolitik|MD_Realismo/) { $ours{system_of($m)}{$m}++ }
	elsif ($m =~ m{((?:common|events|interface|localisation|gfx)/[^\s:"]+?\.\w+)} && -e $1) { $copy{$m}++ }
	elsif ($m =~ m{common/|events/|interface/|localisation/|gfx/}) { $md{$m}++ }
	else { $base{$m}++ }
}

my @out;
my $ours_n = 0; $ours_n += scalar keys %{$ours{$_}} for keys %ours;
push @out, "Informe de registros", "error.log: $total lineas. Nuestras (distintas): $ours_n. En copias de MD: ".scalar(keys %copy).". De MD o del juego: ".(scalar(keys %md) + scalar(keys %base)).".", '';

# How the session ended.
my @tail = split /\r?\n/, $game; my $last = $tail[-1] // '';
push @out, "Ultima linea de game.log: ".substr($last,0,120);
my ($crash) = sort { -M $a <=> -M $b } grep { -d } glob("$LOGS/../crashes/*");
push @out, "ATENCION: el juego se cerro de golpe en esta sesion: $crash" if $crash && -e "$LOGS/game.log" && -M $crash <= -M "$LOGS/game.log";
push @out, '';

# Speed: game days per real minute, from the timestamps of game.log ([hh:mm:ss][yyyy.mm.dd.hh]). Pauses count as slow time.
{
	my (%first, @months, $prev, $wrap);
	for my $l (@tail) {
		next unless $l =~ /^\[(\d+):(\d+):(\d+)\]\[(\d+)\.(\d+)\.(\d+)\.\d+\]/;
		my $s = $1*3600 + $2*60 + $3;
		$wrap += 86400 if defined $prev && $s < $prev - 3600;
		$prev = $s;
		my $m = "$4.$5";
		my $day = ($4*12 + $5)*30.44 + $6;
		push @months, $m unless exists $first{$m};
		$first{$m} //= [$s + ($wrap // 0), $day];
	}
	if (@months > 2) {
		push @out, "Velocidad (dias de juego por minuto real; las pausas cuentan como lentitud):";
		for my $i (0 .. $#months - 1) {
			my ($a, $b) = ($first{$months[$i]}, $first{$months[$i+1]});
			my $min = ($b->[0] - $a->[0]) / 60;
			push @out, sprintf("  %s: %.1f", $months[$i], $min > 0 ? ($b->[1] - $a->[1]) / $min : 0);
		}
		my ($a, $b) = ($first{$months[0]}, $first{$months[-1]});
		my $min = ($b->[0] - $a->[0]) / 60;
		push @out, sprintf("  Promedio: %.1f dias por minuto", $min > 0 ? ($b->[1] - $a->[1]) / $min : 0), '';
	}
}

# In-game diagnostic.
my @diag = grep { /MDR DIAG/ } @tail;
# Automatic mode: the whole session, not just the last run. Same message on other days counts once.
my @auto = grep { /MDR DIAG (FALLA|AVISO|PRUEBA|AUTO)/ } @diag;
if (grep { /MDR DIAG AUTO/ } @auto) {
	my (%n, @order);
	for (@auto) { (my $m = $_) =~ s/^\[[^\]]*\]\[[^\]]*\]:\s*//; my $k = $m; $k =~ s/\s*\[?\d{1,2} \w+,? \d{4}\]?.*$// if $k =~ /FALLA|AVISO/; push @order, $k unless $n{$k}++; }
	my @fa = grep { /FALLA/ } @order; my @av = grep { /AVISO/ } @order; my @pr = grep { /PRUEBA|AUTO/ } @order;
	my ($runs) = scalar grep { /MDR DIAG FIN/ } @diag;
	push @out, "== Modo automatico: $runs controles completos, ".scalar(@fa)." fallas distintas, ".scalar(@av)." avisos distintos";
	push @out, "-- Fallas (xN = cuantas veces se repitio)", (map { "  x$n{$_}  $_" } @fa), '' if @fa;
	push @out, "-- Avisos (pueden ser casualidad; mirarlos)", (map { "  x$n{$_}  $_" } @av), '' if @av;
	push @out, "-- Pruebas que corrieron", (map { "  $_" } @pr), '';
}
if (@diag) {
	my $st = 0; for my $i (0..$#diag) { $st = $i if $diag[$i] =~ /MDR DIAG INICIO/; }
	@diag = @diag[$st..$#diag];
	my @f = grep { /MDR DIAG FALLA/ } @diag; my @ok = grep { /MDR DIAG OK/ } @diag; my @info = grep { /MDR DIAG INFO/ } @diag;
	push @out, "== Autodiagnostico del juego (ultima corrida): ".scalar(@ok)." OK, ".scalar(@f)." FALLA";
	s/^\[[^\]]*\]\[[^\]]*\]:\s*// for @f, @info;
	push @out, (map { "  $_" } @f), '';
	push @out, "-- Datos", (map { "  $_" } @info), '' if @info;
}
else { push @out, "== Autodiagnostico: no se corrio en esta sesion (decision Diagnostico completo).", ''; }

# AI at war (MDR AI lines, monthly with the diagnostics rule): first and last month per country.
my (%war, @worder);
for (grep { /MDR AI guerra/ } @tail) {
	my ($who) = /:\s*([^:]+?):\s*MDR AI guerra/ or next;
	my ($date) = /(\d{1,2} \w+,? \d{4})/;
	my %v = /(\w+) (-?[\d.]+)/g;
	push @worder, $who unless $war{$who};
	my $w = $war{$who} //= { first => {%v}, from => $date // '?', n => 0, cas => 0, short => 0 };
	$w->{last} = {%v}; $w->{to} = $date // '?'; $w->{n}++;
	$w->{cas} += $v{bajas_mes_k} // 0;
	$w->{short} = $v{escasez} if ($v{escasez} // 0) > $w->{short};
}
if (@worder) {
	push @out, "== IA en guerra: ".scalar(@worder)." paises (meses, divisiones y estados al inicio -> al final, bajas en miles, bajas por estado ganado)";
	for my $c (@worder) {
		my $w = $war{$c}; my ($f, $l) = ($w->{first}, $w->{last});
		my $gain = ($l->{estados} // 0) - ($f->{estados} // 0);
		my $per = $gain > 0 ? sprintf('%.1f', $w->{cas} / $gain) : '-';
		push @out, sprintf "  %-22s %3d meses (%s a %s)  div %s->%s  estados %s->%s  bajas %.1f  por estado %s  territorio %s%%  rendicion %s%%  enemigos %s  peor escasez %d",
			substr($c,0,22), $w->{n}, $w->{from}, $w->{to}, $f->{div} // '?', $l->{div} // '?', $f->{estados} // '?', $l->{estados} // '?',
			$w->{cas}, $per, $l->{territorio} // '?', $l->{rendicion} // '?', $l->{enemigos} // '?', $w->{short};
	}
	push @out, '';
}
else { push @out, "== IA en guerra: no hay lineas MDR AI (hace falta la regla de diagnostico y alguna guerra).", ''; }

for my $s (sort keys %ours) {
	push @out, "== $s (".scalar(keys %{$ours{$s}}).")";
	push @out, map { "  x$ours{$s}{$_}  ".substr($_,0,190) } sort { $ours{$s}{$b} <=> $ours{$s}{$a} } keys %{$ours{$s}};
	push @out, '';
}
if (%known) { push @out, "== Avisos conocidos, no son errores"; push @out, map { "  x$known{$_}  $_" } sort keys %known; push @out, ''; }
if (%copy) { push @out, "== En archivos de MD que copiamos (mirar si tambien pasa en el original)"; push @out, map { "  x$copy{$_}  ".substr($_,0,170) } sort { $copy{$b} <=> $copy{$a} } keys %copy; push @out, ''; }
my @mdl = sort { $md{$b} <=> $md{$a} } keys %md;
push @out, "== De Millennium Dawn o del juego (las 25 mas repetidas; no son nuestras salvo que digan lo contrario)";
push @out, map { "  x$md{$_}  ".substr($_,0,170) } grep { defined } @mdl[0..24];
open my $o, '>:raw', 'herramientas/informe_logs.txt' or die; print $o join("\n",@out), "\n"; close $o;
print join("\n", @out[0..1]), "\n";
print map { sprintf "%-24s %d\n", $_, scalar keys %{$ours{$_}} } sort keys %ours;
print map { "$_\n" } grep { /Autodiagnostico|ATENCION|IA en guerra/ } @out;
