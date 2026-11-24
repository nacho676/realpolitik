"""Build a graphify knowledge graph of the mod without an LLM.

Paradox script is not a language graphify parses, so this reads it directly:
definitions (effects, triggers, events, decisions, ideas, buildings, GUIs...)
become nodes, and every name used inside a definition becomes an edge.
Python tools go through graphify's own AST pass. Docs (*.md) link to the
files and definitions they mention.

Run from the mod folder with graphify's interpreter:
    uv tool run --from graphifyy python herramientas/grafo_mod.py
Output: graphify-out/ (graph.json, graph.html, GRAPH_REPORT.md)

Millennium Dawn itself (its files are only read; the user asked for the graph inside it):
    uv tool run --from graphifyy python herramientas/grafo_mod.py --md
Output: Millennium-Dawn-2.0.3/graphify-out/
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

MOD = Path(__file__).resolve().parent.parent
MD_MODE = "--md" in sys.argv
ROOT = MOD.parent / "Millennium-Dawn-2.0.3" if MD_MODE else MOD
OUT = ROOT / "graphify-out"  # only adds this folder; MD's own files are never written
# keys whose value is a variable or flag name (used when there is no mdr_ prefix to go by)
VAR_KEYS = {"var", "set_variable", "add_to_variable", "subtract_from_variable",
            "multiply_variable", "divide_variable", "clamp_variable", "check_variable",
            "has_variable", "clear_variable", "set_temp_variable", "set_country_flag",
            "has_country_flag", "clr_country_flag", "set_global_flag", "has_global_flag",
            "clr_global_flag", "set_state_flag", "has_state_flag", "clr_state_flag"}

# folder -> (kind, depth at which definitions live)
FOLDERS = {
    "common/scripted_effects": ("effect", 0),
    "common/scripted_triggers": ("trigger", 0),
    "common/scripted_guis": ("gui", 1),
    "common/scripted_diplomatic_actions": ("diplo_action", 1),
    "common/decisions": ("decision", 1),
    "common/decisions/categories": ("decision_category", 0),
    "common/ideas": ("idea", 2),
    "common/buildings": ("building", 1),
    "common/dynamic_modifiers": ("modifier", 0),
    "common/opinion_modifiers": ("opinion", 1),
    "common/modifier_definitions": ("modifier_def", 0),
    "common/ai_strategy": ("ai_strategy", 0),
    "common/technologies": ("tech", 1),
    "common/game_rules": ("game_rule", 0),
    "common/resources": ("resource", 1),
    "common/map_modes": ("map_mode", 0),
    "common/on_actions": ("on_action", 1),
    "common/scripted_localisation": ("loc", None),  # defined_text = { name = X }
    "common/national_focus": ("focus", None),  # focus = { id = X }
    "events": ("event", None),  # *_event = { id = X }
}

KEYWORDS = {"yes", "no", "newline", "if", "else", "else_if", "limit", "AND", "OR", "NOT",
             "always", "hidden_effect", "trigger", "effect", "modifier", "allowed", "available",
             "visible", "random_list", "ai_will_do", "factor", "add", "value", "text"}

TOKEN = re.compile(r'"[^"]*"|[{}]|[<>!]?=|<|>|[^\s{}=<>"#]+')


def tokenize(text):
    out = []
    for line in text.splitlines():
        # drop comments outside quotes
        buf, q = [], False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == "#" and not q:
                break
            buf.append(ch)
        out.extend(TOKEN.findall("".join(buf)))
    return out


def blocks(tokens, depth_target):
    """Yield (name, body_tokens) for `name = {` blocks opened at depth_target."""
    depth, i, n = 0, 0, len(tokens)
    while i < n:
        t = tokens[i]
        if t == "{":
            depth += 1
        elif t == "}":
            depth -= 1
        elif (depth == depth_target and i + 2 < n and tokens[i + 1] == "="
              and tokens[i + 2] == "{"):
            j, d = i + 3, 1
            while j < n and d:
                if tokens[j] == "{":
                    d += 1
                elif tokens[j] == "}":
                    d -= 1
                j += 1
            yield t, tokens[i + 3:j - 1]
            i = j
            continue
        i += 1


def id_blocks(tokens, key):
    """Yield (id, body) for top-level blocks whose `key = X` names them."""
    for _, body in blocks(tokens, 0):
        # focus trees nest focuses one level deeper
        candidates = [body] + [b for _, b in blocks(body, 0)]
        for b in candidates:
            for k in range(len(b) - 2):
                if b[k] == key and b[k + 1] == "=":
                    yield b[k + 2].strip('"'), b
                    break


def file_kind(rel):
    best = None
    for folder, spec in FOLDERS.items():
        if rel.startswith(folder + "/") and (best is None or len(folder) > len(best[0])):
            best = (folder, spec)
    return best[1] if best else None


def nid(kind, name):
    return re.sub(r"[^a-z0-9_]", "_", f"{kind}_{name}".lower())


def main():
    defs = {}  # name -> node id
    nodes, bodies = {}, []
    if MD_MODE:
        files = sorted(p for d in ("common", "events") for p in (ROOT / d).rglob("*.txt"))
    else:
        files = sorted(p for p in ROOT.rglob("*.txt")
                       if p.name.startswith("mdr_") and "graphify-out" not in p.parts)
        files += [ROOT / "events/pandemics.txt"]
    for p in files:
        rel = p.relative_to(ROOT).as_posix()
        spec = file_kind(rel)
        if not spec:
            continue
        kind, depth = spec
        toks = tokenize(p.read_text(encoding="utf-8", errors="replace"))
        fid = nid("file", rel)
        nodes[fid] = dict(id=fid, label=rel, file_type="code", source_file=rel)
        if kind == "loc":
            found = id_blocks(toks, "name")
        elif kind == "focus":
            found = id_blocks(toks, "id")
        elif kind == "event":
            found = id_blocks(toks, "id")
        else:
            found = blocks(toks, depth)
        for name, body in found:
            if name in KEYWORDS:  # stray braces in some MD files expose script keywords
                continue
            # `id = SOV` / `id = ROOT` inside nested scopes is a target, not a definition
            if kind in ("event", "focus") and (re.fullmatch(r"[A-Z]{3}|ROOT|FROM|PREV|THIS", name)
                                               or (kind == "event" and "." not in name)):
                continue
            if kind == "on_action":
                name = f"{name}@{p.stem}"
            i = nid(kind, name)
            nodes[i] = dict(id=i, label=f"{name} ({kind})", file_type="code", source_file=rel)
            defs.setdefault(name.split("@")[0] if kind != "on_action" else name, i)
            bodies.append((i, fid, body, rel))

    edges, var_users = [], defaultdict(set)
    var_file = {}
    for i, fid, body, rel in bodies:
        edges.append(dict(source=fid, target=i, relation="contains", source_file=rel))
        seen = set()
        prev = [None, None, None]  # last tokens, to see `key = X` and `key = { X`
        for t in body:
            t = t.strip('"')
            after_var_key = (prev[-1] == "=" and prev[-2] in VAR_KEYS) or (
                prev[-1] == "{" and prev[-2] == "=" and prev[-3] in VAR_KEYS)
            prev = prev[1:] + [t]
            if t in seen:
                continue
            target = defs.get(t)
            if target and target != i:
                seen.add(t)
                edges.append(dict(source=i, target=target, relation="calls", source_file=rel))
            elif ((t.startswith("mdr_") if not MD_MODE else after_var_key)
                  and re.fullmatch(r"[A-Za-z_][\w.@^:]*", t)):
                seen.add(t)
                v = t.split("^")[0].split("@")[0].split(":")[0]
                var_users[v].add(i)
                var_file.setdefault(v, rel)
    # shared variables/flags: only those touched by 2+ definitions
    for v, users in var_users.items():
        if len(users) < 2 or v in defs:
            continue
        vid = nid("var", v)
        nodes[vid] = dict(id=vid, label=f"{v} (variable/flag)", file_type="concept",
                          source_file=var_file[v])
        for u in users:
            edges.append(dict(source=u, target=vid, relation="shares_data_with",
                              source_file=var_file[v]))

    # docs: link to the files and definitions they mention
    file_by_name = {Path(n["label"]).name: k for k, n in nodes.items() if k.startswith("file_")}
    for md in sorted(ROOT.glob("*.md")):
        did = nid("doc", md.name)
        nodes[did] = dict(id=did, label=md.name, file_type="document", source_file=md.name)
        text = md.read_text(encoding="utf-8", errors="replace")
        hits = set(re.findall(r"\w+_[\w.]+" if MD_MODE else r"mdr_[\w.]+", text))
        for h in hits:
            tgt = file_by_name.get(h) or defs.get(h) or defs.get(h.rstrip("."))
            if not tgt and h.endswith(".txt"):
                tgt = file_by_name.get(h)
            if tgt:
                edges.append(dict(source=did, target=tgt, relation="references", source_file=md.name))

    for e in edges:
        e.update(confidence="EXTRACTED", confidence_score=1.0, weight=1.0, _origin="ast")
    for n in nodes.values():
        n.update(source_location=None, _origin="ast")

    # graphify's own AST for the Python tools
    from graphify.extract import extract
    py = [] if MD_MODE else sorted((ROOT / "herramientas").glob("*.py"))
    ast = extract(py, cache_root=ROOT, root=ROOT) if py else {"nodes": [], "edges": []}
    for n in ast["nodes"]:
        nodes.setdefault(n["id"], n)
    edges += ast["edges"]

    extraction = dict(nodes=list(nodes.values()), edges=edges, hyperedges=[],
                      input_tokens=0, output_tokens=0)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".graphify_extract.json").write_text(json.dumps(extraction, ensure_ascii=False),
                                                encoding="utf-8")
    print(f"Extraction: {len(nodes)} nodes, {len(edges)} edges")

    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.analyze import god_nodes, surprising_connections, suggest_questions
    from graphify.report import generate
    from graphify.export import to_json

    G = build_from_json(extraction, root=str(ROOT), directed=True)
    communities = cluster(G)
    cohesion = score_all(G, communities)
    # name each community after its most common source folder/file stem
    labels = {}
    for cid, members in communities.items():
        stems = Counter()
        for m in members:
            sf = G.nodes[m].get("source_file") or ""
            stem = Path(sf).stem.replace("mdr_", "")
            stems[re.sub(r"_(gen|loc|gui|events|decisions|triggers|ai)$", "", stem)] += 1
        top = [s for s, _ in stems.most_common(2) if s]
        labels[cid] = " + ".join(top) or f"Community {cid}"
    gods = god_nodes(G)
    surprises = surprising_connections(G, communities)
    questions = suggest_questions(G, communities, labels)
    to_json(G, communities, str(OUT / "graph.json"), force=True, community_labels=labels)
    detection = {"total_files": len(files) + len(py), "total_words": 0,
                 "files": {"code": [str(f) for f in files + py], "document": [], "paper": [],
                           "image": [], "video": []}}
    report = generate(G, communities, cohesion, labels, gods, surprises, detection,
                      {"input": 0, "output": 0}, str(ROOT), suggested_questions=questions)
    (OUT / "GRAPH_REPORT.md").write_text(report, encoding="utf-8")
    (OUT / ".graphify_labels.json").write_text(
        json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8")
    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
          f"{len(communities)} communities")


if __name__ == "__main__":
    sys.exit(main())
