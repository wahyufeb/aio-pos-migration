"""Code-only, AST-only rebuild of graphify-out/ for aio-pos. No LLM calls, no token cost.

Run through app-knowledge/rebuild-graph.sh (it picks graphify's Python interpreter).
Must run as a real file (not stdin): graphify's AST extraction uses a process pool.
"""
import collections
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    from graphify.analyze import god_nodes, suggest_questions, surprising_connections
    from graphify.build import build_from_json
    from graphify.cluster import cluster, score_all
    from graphify.detect import detect, save_manifest
    from graphify.export import to_json
    from graphify.extract import extract
    from graphify.report import generate

    src = os.environ["SRC"]
    out = Path("graphify-out")

    d = detect(Path(src))
    code = [f for f in d["files"]["code"] if f.endswith((".vue", ".js"))]
    d["files"] = {"code": code, "document": [], "paper": [], "image": [], "video": []}
    d["total_files"] = len(code)

    ext = extract([Path(f) for f in code], cache_root=Path("."))
    ext.update({"hyperedges": [], "input_tokens": 0, "output_tokens": 0})

    # Guard: refuse to write anything if extraction clearly failed.
    old = out / "graph.json"
    if old.exists():
        old_n = len(json.loads(old.read_text())["nodes"])
        if len(ext["nodes"]) < 0.8 * old_n:
            print(f"ABORT: extraction produced {len(ext['nodes'])} nodes vs {old_n} in the current graph. Nothing written.")
            return 1

    G = build_from_json(ext, root=src)
    comms = cluster(G)
    coh = score_all(G, comms)

    labels, used = {}, collections.Counter()
    for cid, nodes in comms.items():
        files = collections.Counter(G.nodes[n].get("source_file", "") for n in nodes if n in G)
        f = files.most_common(1)[0][0] if files else ""
        parts = f.split("/")
        stem = parts[-1].rsplit(".", 1)[0] or "misc"
        if stem == "index" and len(parts) > 1:
            stem = parts[-2]
        lab = f"{parts[0] if len(parts) > 1 else 'root'}: {stem}"
        if len(files) > 1:
            lab += f" (+{len(files) - 1} files)"
        used[lab] += 1
        labels[cid] = lab if used[lab] == 1 else f"{lab} #{used[lab]}"

    gods, surprises = god_nodes(G), surprising_connections(G, comms)
    qs = suggest_questions(G, comms, labels)
    report = generate(G, comms, coh, labels, gods, surprises, d, {"input": 0, "output": 0}, ".", suggested_questions=qs)
    to_json(G, comms, str(out / "graph.json"))
    (out / "GRAPH_REPORT.md").write_text(report)
    (out / ".graphify_labels.json").write_text(json.dumps({str(k): v for k, v in labels.items()}))
    save_manifest(d["files"])

    cp = out / "cost.json"
    cost = json.loads(cp.read_text()) if cp.exists() else {"runs": [], "total_input_tokens": 0, "total_output_tokens": 0}
    cost["runs"].append({"date": datetime.now(timezone.utc).isoformat(), "input_tokens": 0, "output_tokens": 0, "files": len(code)})
    cp.write_text(json.dumps(cost, indent=2))

    print(f"Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(comms)} communities from {len(code)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
