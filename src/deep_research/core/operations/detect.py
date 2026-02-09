"""DETECT: Identify blind spots, tensions, and hidden assumptions."""

from __future__ import annotations

import logging
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation

logger = logging.getLogger(__name__)

DETECT_ASSUMPTIONS_PROMPT = """You are a critical analysis agent. Identify hidden assumptions and blind spots in this question.

Question: {question}

Rules:
- List 2-4 hidden assumptions the question makes
- For each, explain why it might be wrong
- Format: One assumption per line, prefixed with "- "
"""

DETECT_TENSIONS_PROMPT = """You are a tension detection agent. Given these findings, identify contradictions and unresolved tensions.

Question: {question}

Findings:
{findings}

Rules:
- Identify 2-4 tensions or contradictions between findings
- For each, explain both sides
- Format: One tension per line, prefixed with "- "
"""


class DetectOperation(Operation):
    name = "detect"

    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        from deep_research.providers import call_llm

        model = context.get("model", "haiku")
        detect_type = context.get("detect_type", "tensions")

        if detect_type == "assumptions":
            prompt = DETECT_ASSUMPTIONS_PROMPT.format(question=node.content)
        else:
            children = graph.get_children(node.id)
            findings = "\n".join(
                f"- {c.content[:200]}" for c in children
                if c.node_type in (NodeType.ANSWER, NodeType.GROUNDED_CLAIM)
            )
            if not findings:
                return []
            prompt = DETECT_TENSIONS_PROMPT.format(
                question=node.content,
                findings=findings,
            )

        response = await call_llm(prompt, model=model)

        new_nodes = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                content = line[2:].strip()
                if content:
                    ntype = NodeType.BLIND_SPOT if detect_type == "assumptions" else NodeType.TENSION
                    new_nodes.append(Node(
                        node_type=ntype,
                        content=content,
                        status=EpistemicStatus.EXPLORED,
                        depth=node.depth,
                        parent_id=node.id,
                        model=model,
                    ))

        return new_nodes
