"""Perspective expansion recipe - multi-angle analysis with blind spot detection."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from deep_research.core.chef import MasterChef, CookResult
from deep_research.core.strategy import perspective_strategy

logger = logging.getLogger(__name__)


async def run_perspective_expansion(
    question: str,
    output_dir: Path,
    model: str = "opus",
    researcher_model: str = "haiku",
    max_parallel: int = 10,
    **kwargs: Any,
) -> CookResult:
    """Run perspective expansion on a question.

    Identifies multiple perspectives/frameworks, explores each one,
    detects blind spots, and synthesizes into a multi-perspective analysis.
    """
    chef = MasterChef(
        output_dir=output_dir,
        max_parallel=max_parallel,
        max_depth=2,
    )

    # Register operations
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
        perspective_strategy,
        context={
            "model": model,
            "researcher_model": researcher_model,
            **kwargs,
        },
    )

    # Write perspectives report
    perspectives_path = output_dir / "PERSPECTIVES.md"
    from deep_research.core.node import NodeType
    perspectives = result.graph.nodes_by_type(NodeType.PERSPECTIVE)
    if perspectives:
        lines = [
            "# Perspective Analysis",
            "",
            f"**Question**: {question}",
            "",
            "## Perspectives Explored",
            "",
        ]
        for p in perspectives:
            lines.append(f"### {p.content}")
            # Find answers for this perspective
            children = result.graph.get_children(p.id)
            for c in children:
                if c.node_type == NodeType.ANSWER:
                    lines.extend(["", c.content, ""])
            lines.append("---")
        perspectives_path.write_text("\n".join(lines))

    return result
