#!/usr/bin/env bash
# Deep Research - Fractal exploration through recursive AI agents
# Usage: ./deep-research.sh [OPTIONS] "Your question"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Defaults
MODEL="opus"
RESEARCHER="haiku"
DEPTH=2
PARALLEL=10
WEB_FLAG=""
STRATEGY="recursive_research"
OUTPUT=""
LEAVES=""
MERGER=""

show_help() {
    cat <<'HELP'
Deep Research - Fractal exploration through recursive AI agents

Usage: ./deep-research.sh [OPTIONS] "Your question"

Options:
  -m MODEL       Orchestrator model (default: opus)
  -r MODEL       Researcher model (default: haiku)
  -l MODELS      Leaf ensemble, comma-separated (e.g. "haiku,gemini:flash")
  --merger MODEL  Model for merging ensembles
  -d DEPTH       Max depth, 0=unlimited (default: 2)
  -p PARALLEL    Max concurrent agents (default: 10)
  -w             Enable web search grounding
  -s STRATEGY    Strategy: recursive_research, socratic, perspective_expander, grounded_research
  -o DIR         Output directory
  -h             Show this help

Examples:
  ./deep-research.sh "What makes startups successful?"
  ./deep-research.sh -d 2 -m opus -r haiku "Your question"
  ./deep-research.sh -s grounded_research -w "Current state of AI"
  ./deep-research.sh -l "haiku,gemini:flash" --merger kimi:kimi "Your question"
HELP
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m) MODEL="$2"; shift 2 ;;
        -r) RESEARCHER="$2"; shift 2 ;;
        -l) LEAVES="$2"; shift 2 ;;
        --merger) MERGER="$2"; shift 2 ;;
        -d) DEPTH="$2"; shift 2 ;;
        -p) PARALLEL="$2"; shift 2 ;;
        -w) WEB_FLAG="--web"; shift ;;
        -s) STRATEGY="$2"; shift 2 ;;
        -o) OUTPUT="$2"; shift 2 ;;
        -h|--help) show_help; exit 0 ;;
        -*) echo "Unknown option: $1"; show_help; exit 1 ;;
        *) QUESTION="$1"; shift ;;
    esac
done

if [[ -z "${QUESTION:-}" ]]; then
    echo "Error: No question provided."
    show_help
    exit 1
fi

# Build command
CMD=(deep-research research
    -m "$MODEL"
    -r "$RESEARCHER"
    -d "$DEPTH"
    -p "$PARALLEL"
    --strategy "$STRATEGY"
)

[[ -n "$WEB_FLAG" ]] && CMD+=("$WEB_FLAG")
[[ -n "$LEAVES" ]] && CMD+=(-l "$LEAVES")
[[ -n "$MERGER" ]] && CMD+=(--merger "$MERGER")
[[ -n "$OUTPUT" ]] && CMD+=(-o "$OUTPUT")

CMD+=("$QUESTION")

# Run
exec "${CMD[@]}"
