#!/usr/bin/env bash
# Psychiatric Feedback Research - Domain-specific wrapper for Deep Research
#
# Researches psychiatric patient feedback, treatment experiences, and care quality
# using fractal AI agent exploration.
#
# Usage:
#   ./psychiatric-feedback-research.sh "What are patients' biggest concerns about antidepressants?"
#   ./psychiatric-feedback-research.sh -w "Latest patient satisfaction trends in psychiatric care"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Domain-specific defaults
MODEL="opus"
RESEARCHER="haiku"
DEPTH=2
PARALLEL=10
WEB_FLAG=""
STRATEGY="recursive_research"
OUTPUT=""

# Domain context injected into every question
DOMAIN_CONTEXT="Focus on psychiatric patient feedback, mental health treatment experiences, and clinical care quality. Consider perspectives from: patients, clinicians, caregivers, and researchers. Ground findings in published psychiatric literature, patient surveys, and clinical studies where possible."

show_help() {
    cat <<'HELP'
Psychiatric Feedback Research
Domain-specific Deep Research for psychiatric patient experiences and treatment outcomes.

Usage: ./psychiatric-feedback-research.sh [OPTIONS] "Your question"

Options:
  -m MODEL       Orchestrator model (default: opus)
  -r MODEL       Researcher model (default: haiku)
  -d DEPTH       Max depth (default: 2)
  -p PARALLEL    Max concurrent agents (default: 10)
  -w             Enable web search for current data
  -s STRATEGY    Research strategy (default: recursive_research)
  -o DIR         Output directory

Strategies:
  recursive_research    - Standard fractal decomposition (default)
  socratic              - Challenge assumptions about psychiatric care
  perspective_expander  - Patient/clinician/caregiver/researcher angles
  grounded_research     - Web-verified psychiatric findings

Examples:
  # General overview
  ./psychiatric-feedback-research.sh "What are patients' biggest concerns about antidepressants?"

  # Medication-specific
  ./psychiatric-feedback-research.sh "What do patients report about SSRI side effects?"

  # Therapy approach
  ./psychiatric-feedback-research.sh "How do patients compare therapy and medication effectiveness?"

  # Access barriers
  ./psychiatric-feedback-research.sh "What barriers prevent patients from continuing psychiatric treatment?"

  # With web search (for current data)
  ./psychiatric-feedback-research.sh -w "Latest patient satisfaction trends in psychiatric care"

  # Multi-perspective analysis
  ./psychiatric-feedback-research.sh -s perspective_expander "How do patients experience involuntary commitment?"

  # Socratic inquiry
  ./psychiatric-feedback-research.sh -s socratic "Is medication-first always the best approach?"
HELP
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -m) MODEL="$2"; shift 2 ;;
        -r) RESEARCHER="$2"; shift 2 ;;
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

# Enrich the question with domain context
ENRICHED_QUESTION="[Psychiatric Patient Feedback Research] ${QUESTION}

Context: ${DOMAIN_CONTEXT}"

# Set domain-specific output directory
if [[ -z "$OUTPUT" ]]; then
    DATE_SLUG=$(date +%Y-%m-%d)
    Q_SLUG=$(echo "$QUESTION" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | head -c 50)
    OUTPUT="reports/psychiatric/${DATE_SLUG}-${Q_SLUG}"
fi

# Build and run command
CMD=(deep-research research
    -m "$MODEL"
    -r "$RESEARCHER"
    -d "$DEPTH"
    -p "$PARALLEL"
    --strategy "$STRATEGY"
    -o "$OUTPUT"
)

[[ -n "$WEB_FLAG" ]] && CMD+=("$WEB_FLAG")

CMD+=("$ENRICHED_QUESTION")

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         Psychiatric Feedback Research                    ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║ Question: $(echo "$QUESTION" | head -c 45)..."
echo "║ Strategy: $STRATEGY"
echo "║ Model:    $MODEL → $RESEARCHER"
echo "║ Output:   $OUTPUT"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

exec "${CMD[@]}"
