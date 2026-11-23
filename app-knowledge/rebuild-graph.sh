#!/usr/bin/env bash
# Code-only, AST-only rebuild of graphify-out/ for ~/Work/aio-pos. No LLM calls, no token cost.
#
# Why not `/graphify ... --update`: incremental update re-detects the whole aio-pos repo (437 docs,
# 249 images) and treats .vue as non-code, so it would launch LLM subagents. Use this script instead.
#
# Usage (from anywhere):  bash app-knowledge/rebuild-graph.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"   # aio-pos-migration
export SRC="${AIO_POS_DIR:-$HOME/Work/aio-pos}"
cd "$ROOT"
mkdir -p graphify-out
PY="$(cat graphify-out/.graphify_python 2>/dev/null || echo python3)"
"$PY" -c "import graphify" || { echo "graphify not installed for $PY"; exit 1; }
echo "$SRC" > graphify-out/.graphify_root

"$PY" "$ROOT/app-knowledge/rebuild_graph.py"

graphify export html >/dev/null 2>&1 || echo "html export failed (graph.json and report are still updated)"
echo "Rebuilt from aio-pos@$(git -C "$SRC" rev-parse --short HEAD). Update source-sha in app-knowledge/aio-pos-guide.md §17."
