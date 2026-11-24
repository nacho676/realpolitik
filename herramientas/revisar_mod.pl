# Reviews MD_Realismo without opening the game and writes herramientas/informe_revision.txt.
# Run from the mod folder: perl herramientas/revisar_mod.pl
# ERROR: almost surely broken. AVISO: worth a look; it can be correct. It reads Millennium Dawn and the base game only to know what exists.
use strict; use warnings;
use File::Find; use Digest::MD5;

my $MD = '../Millennium-Dawn-2.0.3';
my ($GAME) = grep { -d $_ } ($ENV{HOI4_DIR} // '', 'C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV');
$GAME //= '';

my (%rep, %seen);
sub add { my ($sev,$sec,$msg) = @_; return if $seen{"$sec|$msg"}++; push @{$rep{$sev}{$sec}}, $msg; }
sub slurp { open my $h, '<:raw', $_[0] or return ''; local $/; my $t = <$h>; close $h; $t // '' }
sub strip { my $t = shift; my $o = ''; for my $l (split /\n/, $t, -1) { my $q = 0; my $r = ''; for my $c (split //, $l) { $q = !$q if $c eq '"'; last if $c eq '#' && !$q; $r .= $c; } $o .= "$r\n"; } $o }
sub files { my ($root,$re) = @_; my @f; return @f unless -d $root; find({ no_chdir => 1, wanted => sub { push @f, $File::Find::name if -f $_ && /$re/ } }, $root); sort @f }
sub short { my $f = shift; $f =~ s{^\./}{}; $f }

# Own files: everything of ours plus the copies that call our code. National focus copies only change one line.
my @txt = grep { !m{common/national_focus/(?!mdr_)} && !m{/herramientas/} } files('.', qr/\.txt$/);
@txt = grep { !m{^\./(map|history|herramientas)/} } @txt;
my @gui = files('./interface', qr/\.gui$/);
my @gfx = files('./interface', qr/\.gfx$/);
my %body; $body{$_} = strip(slurp($_)) for @txt, @gui, @gfx;
my @own = grep { m{/mdr_[^/]*$} } (@txt, @gui, @gfx);
my $all = join("\n", map { $body{$_} } @txt, @gui);

# 1. File format.
for my $f (@txt, @gui, @gfx, files('./map', qr/adjacency_rules\.txt$/)) {
	my $raw = slurp($f); my $t = $body{$f} // strip($raw);
	(my $q = $t) =~ s/"[^"\n]*"//g;
	my $o = () = $q =~ /\{/g; my $c = () = $q =~ /\}/g;
	add('ERROR','Llaves',short($f).": $o abren y $c cierran") if $o != $c;
	if ($f =~ m{/mdr_[^/]*$} && substr($raw,0,3) eq "\xEF\xBB\xBF") { add('AVISO','Codificacion',short($f).": .txt o .gui con BOM"); }
}
my %ylocal;
for my $lang (qw(spanish english)) {
	for my $f (files("./localisation/$lang", qr/\.yml$/)) {
		next unless $f =~ m{/mdr_[^/]*$} || $f =~ m{/replace/mdr_};
		my $raw = slurp($f);
		add('ERROR','Codificacion',short($f).": texto sin BOM") unless substr($raw,0,3) eq "\xEF\xBB\xBF";
		add('ERROR','Codificacion',short($f).": no empieza con l_$lang:") unless $raw =~ /\A(?:\xEF\xBB\xBF)?\s*l_$lang:/;
		my $n = 0; my %dup;
		for my $l (split /\r?\n/, $raw) { $n++; next if $n == 1 || $l =~ /^\s*(#|$)/;
			if ($l !~ /^ ?[\w.\-]+:\d* *".*" *(#.*)?$/) { add('ERROR','Formato de textos',short($f).":$n: linea mal formada: ".substr($l,0,70)); next }
			my ($k) = $l =~ /^ ?([\w.\-]+):/;
			add('ERROR','Formato de textos',short($f).": clave repetida $k") if $dup{$k}++;
			# A dollar sign is written $$: with two lone ones, the game reads what is between them as a key and eats it.
			if ($f =~ /mdr_/) { (my $c = $l) =~ s/\$\$//g; add('ERROR','Formato de textos',short($f).": $k tiene dos \$ sueltos, va \$\$") if $c =~ /\$\[[^\$]*\$/; }
			$ylocal{$lang}{$k} = short($f);
		}
	}
}

# 2. What exists: effects, triggers, loc keys, sprites, elements.
sub defs { my ($dir) = @_; my %d; for my $f (files($dir, qr/\.txt$/)) { my $t = strip(slurp($f)); $d{$1} = 1 while $t =~ /^(\w+)\s*=\s*\{/mg; } %d }
my %eff  = (defs('./common/scripted_effects'), defs("$MD/common/scripted_effects"), $GAME ? defs("$GAME/common/scripted_effects") : ());
my %trig = (defs('./common/scripted_triggers'), defs("$MD/common/scripted_triggers"), $GAME ? defs("$GAME/common/scripted_triggers") : ());
my %my_eff = defs('./common/scripted_effects'); my %my_trig = defs('./common/scripted_triggers');
my %locs;
for my $lang (qw(spanish english)) {
	for my $base ('.', $MD, $GAME) { next unless $base;
		for my $f (files("$base/localisation/$lang", qr/\.yml$/)) { my $t = slurp($f); $locs{$lang}{$1} = 1 while $t =~ /^ ?([\w.\-]+):\d* *"/mg; }
	}
}
my %sprite;
for my $base ('.', $MD, $GAME) { next unless $base;
	for my $f (files("$base/interface", qr/\.gfx$/), files("$base/gfx", qr/\.gfx$/)) { my $t = slurp($f); $sprite{$1} = 1 while $t =~ /name\s*=\s*"?(GFX_\w+)"?/g; }
}
my %element;
for my $base ('.', $MD, $GAME) { next unless $base;
	for my $f (files("$base/interface", qr/\.gui$/)) { my $t = slurp($f); $element{$1} = 1 while $t =~ /name\s*=\s*"?([\w\-]+)"?/g; }
}
my %defined_text;
for my $base ('.', $MD, $GAME) { next unless $base;
	for my $f (files("$base/common/scripted_localisation", qr/\.txt$/)) { my $t = strip(slurp($f)); $defined_text{$1} = 1 while $t =~ /\bname\s*=\s*"?(\w+)"?/g; }
}
sub has_loc { my ($k,$l) = @_; $locs{$l}{$k} }
sub need_loc { my ($k,$where,$sev) = @_; return if !$k || $k =~ /[\[\s]/; $sev //= 'ERROR';
	for my $l (qw(spanish english)) { add($sev,"Textos que faltan","$k ($l), usado en $where") unless has_loc($k,$l); } }

# 3. Calls to our effects and triggers.
my %called;
for my $f (@txt, @gui) { my $t = $body{$f};
	while ($t =~ /\b(mdr_\w+)\s*=\s*(yes|no)\b/g) { my $n = $1; $called{$n} = 1;
		add('ERROR','Efectos o condiciones sin definir',"$n, llamado en ".short($f)) unless $eff{$n} || $trig{$n}; }
}
for my $n (sort keys %my_eff) { next unless $n =~ /^mdr_/; add('AVISO','Efectos que nadie usa',$n) unless $called{$n}; }
for my $n (sort keys %my_trig) { next unless $n =~ /^mdr_/; add('AVISO','Condiciones que nadie usa',$n) unless $called{$n}; }

# 4. Events.
my %ev_def; my %ev_only;
for my $f (files('./events', qr/\.txt$/)) { my $t = strip(slurp($f));
	next unless $f =~ m{/mdr_};
	my %ns; $ns{$1} = 1 while $t =~ /^add_namespace\s*=\s*(\w+)/mg;
	while ($t =~ /^\w*event\s*=\s*\{(.*?)^\}/msg) { my $b = $1;
		my ($id) = $b =~ /^\tid\s*=\s*([\w.]+)/m or next;
		add('ERROR','Eventos',"$id, repetido en ".short($f)) if $ev_def{$id};
		$ev_def{$id} = short($f); $ev_only{$id} = 1 if $b =~ /is_triggered_only\s*=\s*yes/;
		my ($ns) = $id =~ /^(\w+)\./; add('ERROR','Eventos',"$id sin add_namespace en ".short($f)) unless $ns{$ns};
		unless ($b =~ /hidden\s*=\s*yes/) {
			for my $w (qw(title desc)) { while ($b =~ /^\t$w\s*=\s*"?([\w.]+)"?\s*$/mg) { need_loc($1,"evento $id") } }
			while ($b =~ /^\t\tname\s*=\s*"?([\w.]+)"?\s*$/mg) { need_loc($1,"evento $id") }
		}
		if ($b =~ /^\tpicture\s*=\s*"?(GFX_\w+)/m) { add('ERROR','Imagenes',"$1, evento $id") unless $sprite{$1} }
	}
}
my %ev_ref; my $evall = $all; for my $f (files('./events', qr/\.txt$/)) { $evall .= "\n".strip(slurp($f)) if !exists $body{$f}; }
while ($evall =~ /\b(?:id\s*=\s*|(?:country|state|news|unit_leader)_event\s*=\s*)(mdr\w*\.\d+)/g) { $ev_ref{$1}++; }
for my $id (sort keys %ev_ref) { add('ERROR','Eventos',"$id se dispara y no existe") unless $ev_def{$id}; }
for my $id (sort keys %ev_only) { add('AVISO','Eventos que nada dispara',"$id (".$ev_def{$id}.")") if ($ev_ref{$id} // 0) < 2; }

# 5. Variables and flags.
my (%wr,%rd);
sub base { my $v = shift; $v =~ s/\^.*$//; $v =~ s/^.*\.//; $v =~ s/\@.*$//; $v }
my $code = $all; for my $f (files('./events', qr/\.txt$/)) { $code .= "\n".strip(slurp($f)) if $f =~ m{/mdr_} && !exists $body{$f}; }
my $locall = ''; for my $lang (qw(spanish english)) { for my $f (files("./localisation/$lang", qr/mdr_.*\.yml$/)) { $locall .= slurp($f); } }
my $verb = qr/set_variable|add_to_variable|subtract_from_variable|multiply_variable|divide_variable|set_temp_variable|add_to_temp_variable|subtract_from_temp_variable|multiply_temp_variable|divide_temp_variable/;
while ($code =~ /\b$verb\s*=\s*\{\s*([\w.^@]+)\s*=/g) { my $v = base($1); $wr{$v}++ if $v =~ /^mdr_/; }
while ($code =~ /\b(?:set_variable|set_temp_variable)\s*=\s*\{\s*var\s*=\s*([\w.^@]+)/g) { my $v = base($1); $wr{$v}++ if $v =~ /^mdr_/; }
while ($code =~ /\bset_temp_variable_to_random\s*=\s*\{\s*var\s*=\s*([\w.]+)/g) { $wr{base($1)}++; }
while ($code =~ /\b(?:add_to_array|add_to_temp_array)\s*=\s*\{\s*(?:array\s*=\s*)?([\w.]+)/g) { $wr{base($1)}++; }
while ($code =~ /\b(?:value|index|break)\s*=\s*(mdr_\w+)/g) { $wr{$1}++; }
# Read means any use other than the left side of a write (a modifier value, an array index, a scope, a text).
my %left;
while ($code =~ /\b$verb\s*=\s*\{\s*([\w.^@]+)\s*=/g) { my $v = base($1); $left{$v}++ if $v =~ /^mdr_/; }
while ($code =~ /\b(?:set_variable|set_temp_variable)\s*=\s*\{\s*var\s*=\s*([\w.^@]+)/g) { my $v = base($1); $left{$v}++ if $v =~ /^mdr_/; }
my %used; my $hay = $code."\n".$locall;
for my $f (files('./common/dynamic_modifiers', qr/\.txt$/), files('./common/scripted_localisation', qr/\.txt$/)) { $hay .= "\n".strip(slurp($f)); }
$used{$1}++ while $hay =~ /\b(mdr_\w+)/g;
for my $v (sort keys %wr) { next unless $v =~ /^mdr_/; add('AVISO','Variables que se escriben y nadie lee',$v) if ($used{$v} // 0) <= ($left{$v} // 0); }
# Read without any write: only where the code clearly reads a variable.
while ($hay =~ /check_variable\s*=\s*\{\s*([\w.^@]+)/g) { my $v = base($1); $rd{$v}++ if $v =~ /^mdr_/; }
while ($hay =~ /\[\?([\w.^]+)/g) { my $v = base($1); $rd{$v}++ if $v =~ /^mdr_/; }
for my $v (sort keys %rd) { next if $wr{$v} || $eff{$v} || $trig{$v}; add('AVISO','Variables que se leen y nadie escribe',$v); }

my (%fset,%fget);
for my $f (files('./history/states', qr/\.txt$/)) { my $x = slurp($f); $fset{$1}++ while $x =~ /set_state_flag\s*=\s*(mdr_\w+)/g; }
while ($code =~ /set_(?:country|global|state)_flag\s*=\s*(?:\{\s*flag\s*=\s*)?(mdr_\w+)/g) { $fset{$1}++ }
while ($code =~ /has_(?:country|global|state)_flag\s*=\s*(?:\{\s*flag\s*=\s*)?(mdr_\w+)/g) { $fget{$1}++ }
while ($code =~ /(?:clr_country_flag|clr_global_flag|clr_state_flag)\s*=\s*(mdr_\w+)/g) { $fget{$1} //= 0 }
for my $v (sort keys %fget) { next unless $fget{$v}; add('ERROR','Marcas que se miran y nunca se ponen',$v) unless $fset{$v}; }
for my $v (sort keys %fset) { add('AVISO','Marcas que se ponen y nadie mira',$v) unless $fget{$v}; }

# 6. Definitions other things point at.
my (%idea,%dyn,%opin,%bld,%tech,%rule,%trait);
for my $f (files('./common/ideas', qr/\.txt$/), files("$MD/common/ideas", qr/\.txt$/)) { my $t = strip(slurp($f)); $idea{$1} = 1 while $t =~ /^\t\t(\w+)\s*=\s*\{/mg; }
for my $f (files('./common/dynamic_modifiers', qr/\.txt$/), files("$MD/common/dynamic_modifiers", qr/\.txt$/)) { my $t = strip(slurp($f)); $dyn{$1} = 1 while $t =~ /^(\w+)\s*=\s*\{/mg; }
for my $f (files('./common/opinion_modifiers', qr/\.txt$/), files("$MD/common/opinion_modifiers", qr/\.txt$/)) { my $t = strip(slurp($f)); $opin{$1} = 1 while $t =~ /^\t(\w+)\s*=\s*\{/mg; }
for my $f (files('./common/buildings', qr/\.txt$/)) { my $t = strip(slurp($f)); $bld{$1} = 1 while $t =~ /^\t(\w+)\s*=\s*\{/mg; }
for my $f (files('./common/technologies', qr/\.txt$/)) { my $t = strip(slurp($f)); $tech{$1} = 1 while $t =~ /^\t(\w+)\s*=\s*\{/mg; }
for my $f (files('./common/game_rules', qr/\.txt$/)) { my $t = strip(slurp($f)); $rule{$1} = 1 while $t =~ /^(\w+)\s*=\s*\{/mg; }
while ($code =~ /\b(?:has_idea|add_ideas|remove_ideas|add_timed_idea\s*=\s*\{\s*idea|remove_idea|add_idea)\s*=\s*(mdr_\w+)/g) { add('ERROR','Ideas sin definir',$1) unless $idea{$1}; }
while ($code =~ /\b(?:add_ideas|remove_ideas)\s*=\s*\{([^{}]*)\}/g) { for my $i (split ' ', $1) { add('ERROR','Ideas sin definir',$i) if $i =~ /^mdr_/ && !$idea{$i}; } }
while ($code =~ /\bmodifier\s*=\s*(mdr_\w+)/g) { my $m = $1; add('ERROR','Modificadores sin definir',$m) unless $dyn{$m} || $opin{$m}; }
while ($code =~ /(?:building_level\@|\bbuilding\s*=\s*)(mdr_\w+)/g) { add('ERROR','Edificios sin definir',$1) unless $bld{$1}; }
while ($code =~ /add_building_construction\s*=\s*\{\s*type\s*=\s*(mdr_\w+)/g) { add('ERROR','Edificios sin definir',$1) unless $bld{$1}; }
while ($code =~ /has_tech\s*=\s*(mdr_\w+)/g) { add('ERROR','Tecnologias sin definir',$1) unless $tech{$1}; }
while ($code =~ /rule\s*=\s*(mdr_\w+)/g) { add('ERROR','Reglas sin definir',$1) unless $rule{$1}; }

# 7. Texts of what we define.
for my $f (grep { m{common/decisions/} && m{/mdr_} } @txt) { next if $f =~ /categories/; my $t = $body{$f};
	while ($t =~ /^(\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) }
	while ($t =~ /^\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) }
}
for my $f (files('./common/decisions/categories', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^(\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) } }
for my $f (files('./common/buildings', qr/mdr_/)) { my $t = strip(slurp($f)); $t =~ s/^spawn_points\s*=\s*\{.*//ms; while ($t =~ /^\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)); need_loc("$1_desc",short($f),'AVISO'); } }
for my $f (files('./common/dynamic_modifiers', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) } }
for my $f (files('./common/opinion_modifiers', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) } }
for my $f (files('./common/ideas', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^\t\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) } }
for my $f (files('./common/unit_leader', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)) } }
for my $f (files('./common/technologies', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /^\t(mdr_\w+)\s*=\s*\{/mg) { need_loc($1,short($f)); need_loc("$1_desc",short($f),'AVISO'); } }
for my $f (files('./common/game_rules', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /(?:name|text|desc)\s*=\s*"(MDR_\w+)"/g) { need_loc($1,short($f)) } }
for my $f (files('./common/scripted_localisation', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /localization_key\s*=\s*"?([\w.\-]+)"?/g) { need_loc($1,short($f)) } }
for my $f (files('./common/scripted_diplomatic_actions', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /\b(?:send_description|receive_description|accept_title|accept_description|reject_title|reject_description|tooltip)\s*=\s*"?(\w+)"?/g) { need_loc($1,short($f)) } }
for my $f (@own) { next unless $f =~ /\.txt$/; my $t = $body{$f}; while ($t =~ /\b(?:tooltip|custom_effect_tooltip)\s*=\s*"?(\w+)"?/g) { need_loc($1,short($f)) } }
for my $f (grep { m{/mdr_} } @gui) { my $t = $body{$f}; while ($t =~ /\b(?:text|buttonText|pdx_tooltip|pdx_tooltip_delayed)\s*=\s*"(\w+)"/g) { need_loc($1,short($f)) } }

# Texts inside texts.
for my $lang (qw(spanish english)) { for my $f (files("./localisation/$lang", qr/mdr_.*\.yml$/)) { my $t = slurp($f);
	while ($t =~ /\[(?!\?)(?:\w+\.)?(mdr_\w+)\]/g) { my $d = $1; add('ERROR','Textos dentro de textos',"[$d] en ".short($f)." no es un texto del sistema") unless $defined_text{$d}; }
	while ($t =~ /\$(mdr_\w+|MDR_\w+)\$/g) { add('ERROR','Textos dentro de textos',"\$$1\$ en ".short($f)." no existe") unless has_loc($1,$lang); }
} }
# One language without the other.
for my $k (sort keys %{$ylocal{spanish}}) { next if $ylocal{english}{$k} || $locs{english}{$k}; add('AVISO','Clave solo en espanol',$k); }
for my $k (sort keys %{$ylocal{english}}) { next if $ylocal{spanish}{$k} || $locs{spanish}{$k}; add('AVISO','Clave solo en ingles',$k); }

# 8. Pictures.
for my $f (@own) { my $t = $body{$f}; next if $f =~ /\.gfx$/ && $f =~ /faces/;
	while ($t =~ /\b(GFX_\w+)/g) { my $s = $1; next if $f =~ /\.gfx$/; add('ERROR','Imagenes',"$s, en ".short($f)) unless $sprite{$s}; }
}
for my $f (files('./common/ideas', qr/mdr_/)) { my $t = strip(slurp($f)); while ($t =~ /picture\s*=\s*(\w+)/g) { my $p = $1; add('ERROR','Imagenes',"idea picture $p, en ".short($f)) unless $sprite{"GFX_idea_$p"} || $sprite{"GFX_$p"} || $sprite{$p}; } }
for my $f (grep { m{common/decisions/mdr_} } @txt) { my $t = $body{$f}; while ($t =~ /\bicon\s*=\s*(\w+)/g) { my $p = $1; add('ERROR','Imagenes',"decision icon $p, en ".short($f)) unless $sprite{"GFX_decision_$p"} || $sprite{$p} || $sprite{"GFX_$p"}; } }
for my $f (grep { m{/mdr_} } @gfx) { my $t = $body{$f}; while ($t =~ /texture[Ff]ile\d?\s*=\s*"([^"]+)"/g) { my $p = $1; $p =~ s{//}{/}g;
	add('ERROR','Imagenes',"archivo $p, en ".short($f)) unless -f "./$p" || -f "$MD/$p" || ($GAME && -f "$GAME/$p"); } }

# 9. Menus: scripted GUI against windows.
for my $f (grep { m{common/scripted_guis/mdr_} } @txt) { my $t = $body{$f};
	while ($t =~ /\bwindow_name\s*=\s*"?([\w\-]+)"?/g) { add('ERROR','Menus',"ventana $1 de ".short($f)." no existe") unless $element{$1}; }
	# Element names may end in _left/_right, so try the full name before stripping a modifier.
	while ($t =~ /^\s*(\w+)_(click|click_enabled|visible)\s*=\s*\{/mg) { my ($e,$k) = ($1,$2); $e =~ s/_(?:control|shift|alt|right)\z// unless $element{$e}; next if $e =~ /^(?:ai_enabled)$/; add('ERROR','Menus',"$e ($k) en ".short($f)." no existe en ninguna ventana") unless $element{$e}; }
	if ($t =~ /properties\s*=\s*\{(.*?)\n\t\t\}/s) { my $p = $1; while ($p =~ /^\s*(\w+)\s*=\s*\{/mg) { add('ERROR','Menus',"$1 (properties) en ".short($f)." no existe") unless $element{$1}; } }
}
my $sg = join("\n", map { $body{$_} } grep { m{common/scripted_guis/} } @txt);
for my $f (grep { m{/mdr_} } @gui) { my $t = $body{$f};
	while ($t =~ /buttonType\s*=\s*\{/g) { my $i = pos($t); my $s = $i; my $d = 1; while ($d && $i < length $t) { my $c = substr($t,$i++,1); $d++ if $c eq '{'; $d-- if $c eq '}'; } my $b = substr($t,$s,$i-$s); my ($n) = $b =~ /name\s*=\s*"([\w\-]+)"/ or next; next if $b =~ /alwaystransparent\s*=\s*yes/;
		add('AVISO','Botones sin accion',"$n en ".short($f)) unless $sg =~ /\b${n}_click\b/; }
}

# 10. Copies of Millennium Dawn that changed there.
my $cmp = slurp('COMPATIBILIDAD.md');
while ($cmp =~ /^\| `([^`]+)` \| `([0-9a-f]{32})`/mg) { my ($p,$h) = ($1,$2);
	my $src = -f "$MD/$p" ? "$MD/$p" : ($GAME && -f "$GAME/$p") ? "$GAME/$p" : '';
	unless ($src) { add('AVISO','Copias de MD',"$p: no esta en MD ni en el juego"); next }
	my $now = Digest::MD5::md5_hex(slurp($src));
	add('AVISO','Copias de MD',"$p: el original cambio, hay que revisar la copia") if $now ne $h;
	add('ERROR','Copias de MD',"$p: figura como copia y no esta en el mod") unless -f "./$p";
}

# Report.
my @out; my %n = (ERROR => 0, AVISO => 0);
for my $sev (qw(ERROR AVISO)) { for my $sec (sort keys %{$rep{$sev} // {}}) { my @m = sort @{$rep{$sev}{$sec}}; $n{$sev} += @m;
	push @out, "== $sev: $sec (".scalar(@m).")", (map { "  $_" } @m), ''; } }
my $head = "Revision de MD_Realismo\nErrores: $n{ERROR}   Avisos: $n{AVISO}\nJuego base: ".($GAME || 'no encontrado (algunas cosas pueden salir como faltantes)')."\n\n";
open my $o, '>:raw', 'herramientas/informe_revision.txt' or die; print $o $head, join("\n",@out), "\n"; close $o;
print $head;
for my $sev (qw(ERROR AVISO)) { for my $sec (sort keys %{$rep{$sev} // {}}) { printf "%-6s %-46s %d\n", $sev, $sec, scalar @{$rep{$sev}{$sec}}; } }
