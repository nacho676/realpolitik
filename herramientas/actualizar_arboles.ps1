# Copies every Millennium Dawn focus tree into Realpolitik and adds the hidden demography branch (mdr_demo_root) to it.
# Run it again after each Millennium Dawn update, so the copies never fall behind:
#   powershell -ExecutionPolicy Bypass -File herramientas\actualizar_arboles.ps1
# Each copy differs from Millennium Dawn's file only by one line after every "focus_tree = {"; the script checks that
# and refuses to write a file that differs in anything else. It also places the branch right of each tree's last focus.
param(
	[string]$md = (Join-Path $PSScriptRoot '..\..\Millennium-Dawn-2.0.0'),
	[string]$mod = (Join-Path $PSScriptRoot '..')
)
$ErrorActionPreference = 'Stop'
$src = Join-Path $md 'common\national_focus'
$dst = Join-Path $mod 'common\national_focus'
$utf8 = New-Object Text.UTF8Encoding $false
$insert = "`tshared_focus = mdr_demo_root # Realpolitik: hidden demography branch (common/national_focus/mdr_demography.txt)"

Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Text;

public static class MdrFocusScan {
	public static Dictionary<string, double> X = new Dictionary<string, double>();
	public static Dictionary<string, string> Rel = new Dictionary<string, string>();
	// tree id -> focus ids defined inside it, and shared roots it references
	public static Dictionary<string, List<string>> TreeFocuses = new Dictionary<string, List<string>>();
	public static Dictionary<string, List<string>> TreeShared = new Dictionary<string, List<string>>();

	static List<string> Tokens(string text) {
		var t = new List<string>(); int i = 0, n = text.Length;
		while (i < n) {
			char c = text[i];
			if (c == '#') { while (i < n && text[i] != '\n') i++; continue; }
			if (char.IsWhiteSpace(c)) { i++; continue; }
			if (c == '{' || c == '}' || c == '=') { t.Add(c.ToString()); i++; continue; }
			if (c == '"') { int s = i++; while (i < n && text[i] != '"') i++; i++; t.Add(text.Substring(s, Math.Min(i, n) - s)); continue; }
			int b = i; while (i < n && !char.IsWhiteSpace(text[i]) && text[i] != '{' && text[i] != '}' && text[i] != '=' && text[i] != '#') i++;
			t.Add(text.Substring(b, i - b));
		}
		return t;
	}

	// Reads one block starting after its "{": returns top-level key = value pairs and the index after the closing "}".
	static int Block(List<string> t, int i, Action<string, string, int> onPair) {
		int depth = 1;
		while (i < t.Count && depth > 0) {
			if (t[i] == "{") { depth++; i++; continue; }
			if (t[i] == "}") { depth--; i++; continue; }
			if (i + 2 < t.Count && t[i + 1] == "=") {
				if (depth == 1) onPair(t[i], t[i + 2], i + 2);
				i += 2; continue;
			}
			i++;
		}
		return i;
	}

	static void ReadFocus(List<string> t, int open, List<string> into) {
		string id = null, rel = null; double x = 0;
		Block(t, open + 1, (k, v, at) => {
			if (k == "id") id = v;
			else if (k == "x") double.TryParse(v, System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out x);
			else if (k == "relative_position_id") rel = v;
		});
		if (id == null) return;
		X[id] = x; if (rel != null) Rel[id] = rel;
		if (into != null) into.Add(id);
	}

	public static void Scan(string text) {
		var t = Tokens(text);
		for (int i = 0; i + 2 < t.Count; i++) {
			if (t[i + 1] != "=" || t[i + 2] != "{") continue;
			if (t[i] == "shared_focus") { ReadFocus(t, i + 2, null); continue; }
			if (t[i] != "focus_tree") continue;
			string treeId = null; var focuses = new List<string>(); var shared = new List<string>();
			int end = Block(t, i + 3, (k, v, at) => {
				if (k == "id") treeId = v;
				else if (k == "shared_focus" && v != "{") shared.Add(v);
				else if (k == "focus" && v == "{") ReadFocus(t, at, focuses);
			});
			if (treeId != null) { TreeFocuses[treeId] = focuses; TreeShared[treeId] = shared; }
			i = end - 1;
		}
	}

	public static double AbsX(string id) {
		double x = 0; int guard = 0;
		while (id != null && X.ContainsKey(id) && guard++ < 50) { x += X[id]; id = Rel.ContainsKey(id) ? Rel[id] : null; }
		return x;
	}

	static string Root(string id) {
		int guard = 0;
		while (Rel.ContainsKey(id) && guard++ < 50) id = Rel[id];
		return id;
	}

	// Rightmost absolute x of a tree, its own focuses and the shared branches it references.
	public static int MaxX(string tree) {
		double max = 0;
		foreach (var id in TreeFocuses[tree]) max = Math.Max(max, AbsX(id));
		var roots = new HashSet<string>(TreeShared[tree]);
		foreach (var id in X.Keys) if (roots.Contains(Root(id))) max = Math.Max(max, AbsX(id));
		return (int)Math.Ceiling(max);
	}
}
"@

$files = Get-ChildItem $src -Filter *.txt
foreach ($f in $files) { [MdrFocusScan]::Scan([IO.File]::ReadAllText($f.FullName)) }
$offsets = @()
foreach ($tree in ([MdrFocusScan]::TreeFocuses.Keys | Sort-Object)) {
	$offsets += "`t`toffset = { x = $([MdrFocusScan]::MaxX($tree) + 4) y = 0 trigger = { has_focus_tree = $tree } }"
}

# Copies with the one inserted line, checked against the original.
$copied = 0
foreach ($f in $files) {
	$orig = [IO.File]::ReadAllText($f.FullName)
	if ($orig -notmatch '(?m)^focus_tree = \{') { continue }
	$new = [regex]::Replace($orig, '(?m)^(focus_tree = \{[^\n]*\n)', { param($m) $m.Groups[1].Value + "$insert`n" })
	if ($new.Replace("$insert`n", '') -ne $orig) { throw "Copy of $($f.Name) would differ from Millennium Dawn in more than the inserted line" }
	[IO.File]::WriteAllText((Join-Path $dst $f.Name), $new, $utf8)
	$copied++
}

# Positions of the branch: one offset per tree, written into the root focus between the markers.
$branch = Join-Path $dst 'mdr_demography.txt'
$text = [IO.File]::ReadAllText($branch)
$text = [regex]::Replace($text, '(?s)(\t\t# BEGIN offsets\n).*?(\t\t# END offsets)', { param($m) $m.Groups[1].Value + ($offsets -join "`n") + "`n" + $m.Groups[2].Value })
[IO.File]::WriteAllText($branch, $text, $utf8)
"$copied files copied, $([MdrFocusScan]::TreeFocuses.Count) trees, $($offsets.Count) offsets"
