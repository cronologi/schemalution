#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIAGRAM_DIR="$ROOT_DIR/assets/diagrams"
GRAPHVIZ_ENGINE="${GRAPHVIZ_ENGINE:-dot}"
GRAPHVIZ_FORMAT="${GRAPHVIZ_FORMAT:-svg:cairo}"

if ! command -v dot >/dev/null 2>&1; then
  echo "Error: graphviz (dot) is required to render diagrams." >&2
  exit 1
fi

if [ ! -d "$DIAGRAM_DIR" ]; then
  echo "Error: $DIAGRAM_DIR does not exist." >&2
  exit 1
fi

rendered=0

for diagram in "$DIAGRAM_DIR"/*.dot "$DIAGRAM_DIR"/*.gv; do
  [ -e "$diagram" ] || continue
  output="${diagram%.*}.svg"
  dot -K"$GRAPHVIZ_ENGINE" -T"$GRAPHVIZ_FORMAT" "$diagram" -o "$output"
  rendered=$((rendered + 1))
done

if [ "$rendered" -eq 0 ]; then
  echo "No Graphviz files found in $DIAGRAM_DIR (.dot/.gv)."
  exit 0
fi

echo "Rendered $rendered Graphviz diagram(s) to $DIAGRAM_DIR using engine '$GRAPHVIZ_ENGINE' and format '$GRAPHVIZ_FORMAT'."
