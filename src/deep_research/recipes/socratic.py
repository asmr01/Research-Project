"""Socratic inquiry recipe - challenge assumptions and improve questions."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from deep_research.core.chef import MasterChef, CookResult
from deep_research.core.strategy import socratic_strategy

logger = logging.getLogger(__name__)


async def run_socratic_inquiry(
    question: str,
    output_dir: Path,
    model: str = "opus",
    researcher_model: str = "haiku",
    max_parallel: int = 10,
    **kwargs: Any,
) -> CookResult:
    """Run Socratic inquiry on a question.

    Challenges assumptions, generates deeper questions, then researches
    the improved question set.
    """
    chef = MasterChef(
        output_dir=output_dir,
        max_parallel=max_parallel,
        max_depth=2,
    )

    from deep_research.core.operations import (
        DecomposeOperation,
        AnswerOperation,
        SynthesizeOperation,
        DetectOperation,
    )
    chef.register_operation(DecomposeOperation())
    chef.register_operation(AnswerOperation())
    chef.register_operation(SynthesizeOperation())
    chef.register_operation(DetectOperation())

    result = await chef.cook(
        question,
        socratic_strategy,
        context={
            "model": model,
            "researcher_model": researcher_model,
            **kwargs,
        },
    )

    # Write Socratic report
    socratic_path = output_dir / "SOCRATIC.md"
    from deep_research.core.node import NodeType
    blind_spots = result.graph.nodes_by_type(NodeType.BLIND_SPOT)

    lines = [
        "# Socratic Inquiry",
        "",
        f"**Original Question**: {question}",
        "",
    ]

    if blind_spots:
        lines.extend([
            "## Hidden Assumptions Identified",
            "",
        ])
        for bs in blind_spots:
            lines.append(f"- {bs.content}")
        lines.append("")

    questions = result.graph.nodes_by_type(NodeType.QUESTION)
    improved = [q for q in questions if q.depth > 0]
    if improved:
        lines.extend([
            "## Improved Questions",
            "",
        ])
        for q in improved:
            lines.append(f"- {q.content}")
        lines.append("")

    synth = result.final_synthesis
    if synth:
        lines.extend([
            "## Synthesis",
            "",
            synth.content,
        ])

    socratic_path.write_text("\n".join(lines))

    return result
