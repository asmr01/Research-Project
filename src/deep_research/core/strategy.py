"""Declarative research strategies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from deep_research.core.node import NodeType


@dataclass
class StrategyStep:
    """A single step in a research strategy."""
    operation: str  # Operation name: "decompose", "answer", "synthesize", "detect", "ground"
    applies_to: NodeType  # Which node types this step processes
    produces: NodeType  # What node type it produces
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Strategy:
    """A declarative recipe that orchestrates operations."""
    name: str
    description: str
    steps: list[StrategyStep]
    config: dict[str, Any] = field(default_factory=dict)

    def get_steps_for(self, node_type: NodeType) -> list[StrategyStep]:
        return [s for s in self.steps if s.applies_to == node_type]


# --- Built-in Strategies ---

recursive_research_strategy = Strategy(
    name="recursive_research",
    description="Decompose questions recursively, answer leaves, synthesize up",
    steps=[
        StrategyStep(
            operation="decompose",
            applies_to=NodeType.QUESTION,
            produces=NodeType.QUESTION,
            config={"target_angles": 4},
        ),
        StrategyStep(
            operation="answer",
            applies_to=NodeType.QUESTION,
            produces=NodeType.ANSWER,
        ),
        StrategyStep(
            operation="synthesize",
            applies_to=NodeType.ANSWER,
            produces=NodeType.SYNTHESIS,
        ),
    ],
)

socratic_strategy = Strategy(
    name="socratic",
    description="Challenge assumptions and improve questions before researching",
    steps=[
        StrategyStep(
            operation="detect",
            applies_to=NodeType.QUESTION,
            produces=NodeType.BLIND_SPOT,
            config={"detect_type": "assumptions"},
        ),
        StrategyStep(
            operation="decompose",
            applies_to=NodeType.QUESTION,
            produces=NodeType.QUESTION,
            config={"target_angles": 3, "mode": "socratic"},
        ),
        StrategyStep(
            operation="answer",
            applies_to=NodeType.QUESTION,
            produces=NodeType.ANSWER,
        ),
        StrategyStep(
            operation="synthesize",
            applies_to=NodeType.ANSWER,
            produces=NodeType.SYNTHESIS,
        ),
    ],
)

perspective_strategy = Strategy(
    name="perspective_expander",
    description="Multi-angle analysis with blind spot detection",
    steps=[
        StrategyStep(
            operation="decompose",
            applies_to=NodeType.QUESTION,
            produces=NodeType.PERSPECTIVE,
            config={"mode": "perspectives"},
        ),
        StrategyStep(
            operation="answer",
            applies_to=NodeType.PERSPECTIVE,
            produces=NodeType.ANSWER,
        ),
        StrategyStep(
            operation="detect",
            applies_to=NodeType.ANSWER,
            produces=NodeType.BLIND_SPOT,
        ),
        StrategyStep(
            operation="synthesize",
            applies_to=NodeType.ANSWER,
            produces=NodeType.SYNTHESIS,
        ),
    ],
)

grounded_research_strategy = Strategy(
    name="grounded_research",
    description="Web-verified answers with source grounding",
    steps=[
        StrategyStep(
            operation="decompose",
            applies_to=NodeType.QUESTION,
            produces=NodeType.QUESTION,
            config={"target_angles": 3},
        ),
        StrategyStep(
            operation="answer",
            applies_to=NodeType.QUESTION,
            produces=NodeType.ANSWER,
        ),
        StrategyStep(
            operation="ground",
            applies_to=NodeType.ANSWER,
            produces=NodeType.GROUNDED_CLAIM,
        ),
        StrategyStep(
            operation="synthesize",
            applies_to=NodeType.GROUNDED_CLAIM,
            produces=NodeType.SYNTHESIS,
        ),
    ],
)

STRATEGIES: dict[str, Strategy] = {
    "recursive_research": recursive_research_strategy,
    "socratic": socratic_strategy,
    "perspective_expander": perspective_strategy,
    "grounded_research": grounded_research_strategy,
}
