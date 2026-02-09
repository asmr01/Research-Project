"""DECOMPOSE: Break a question into sub-questions or perspectives."""

from __future__ import annotations

import logging
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation

logger = logging.getLogger(__name__)

DECOMPOSE_PROMPT = """You are a research decomposition agent. Given a question, break it down into {target_angles} distinct sub-questions that together would provide a comprehensive answer.

Question: {question}

Context chain: {context_chain}

Rules:
- Each sub-question should explore a DIFFERENT angle
- Sub-questions should be specific and answerable
- Together they should cover the full scope of the original question
- Return ONLY the sub-questions, one per line, prefixed with "- "
"""

SOCRATIC_PROMPT = """You are a Socratic questioning agent. Given a question, challenge its assumptions and generate {target_angles} deeper, more precise questions.

Question: {question}

Rules:
- Identify hidden assumptions in the question
- Generate questions that challenge those assumptions
- Each question should push toward deeper understanding
- Return ONLY the questions, one per line, prefixed with "- "
"""

PERSPECTIVE_PROMPT = """You are a perspective expansion agent. Given a question, identify {target_angles} distinct perspectives or frameworks through which to analyze it.

Question: {question}

Rules:
- Each perspective should be genuinely different (e.g., economic, psychological, historical, ethical)
- Name the perspective, then state the question from that angle
- Format: "- [Perspective Name]: Reframed question"
"""


class DecomposeOperation(Operation):
    name = "decompose"

    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        from deep_research.providers import call_llm

        mode = context.get("mode", "default")
        target_angles = context.get("target_angles", 4)
        model = context.get("model", "haiku")

        # Build context chain from ancestors
        ancestors = graph.get_ancestors(node.id)
        context_chain = " → ".join(a.content[:80] for a in reversed(ancestors))
        if not context_chain:
            context_chain = "(root question)"

        if mode == "socratic":
            prompt = SOCRATIC_PROMPT.format(
                question=node.content,
                target_angles=target_angles,
            )
        elif mode == "perspectives":
            prompt = PERSPECTIVE_PROMPT.format(
                question=node.content,
                target_angles=target_angles,
            )
        else:
            prompt = DECOMPOSE_PROMPT.format(
                question=node.content,
                target_angles=target_angles,
                context_chain=context_chain,
            )

        response = await call_llm(prompt, model=model)

        # Parse sub-questions from response
        new_nodes = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                content = line[2:].strip()
                if not content:
                    continue

                ntype = NodeType.PERSPECTIVE if mode == "perspectives" else NodeType.QUESTION
                sub_node = Node(
                    node_type=ntype,
                    content=content,
                    depth=node.depth + 1,
                    parent_id=node.id,
                    model=model,
                )
                new_nodes.append(sub_node)

        logger.info(f"Decomposed into {len(new_nodes)} sub-questions (depth {node.depth + 1})")
        return new_nodes
