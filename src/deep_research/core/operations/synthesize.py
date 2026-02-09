"""SYNTHESIZE: Combine findings into higher-level synthesis."""

from __future__ import annotations

import logging
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation

logger = logging.getLogger(__name__)

SYNTHESIZE_PROMPT = """You are a research synthesis agent. Combine the following findings into a comprehensive, well-structured synthesis.

Original Question: {question}

Findings:
{findings}

Rules:
- Weave all findings into a coherent narrative
- Identify key themes and patterns across findings
- Note any contradictions or tensions between findings
- Highlight the most important insights
- Structure with clear sections and headings (use ##)
- Aim for a thorough synthesis (400-800 words)
- End with key takeaways
"""


class SynthesizeOperation(Operation):
    name = "synthesize"

    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        from deep_research.providers import call_llm

        model = context.get("merger_model") or context.get("model", "haiku")

        # Gather child answers and syntheses
        children = graph.get_children(node.id)
        findings = []
        for child in children:
            if child.node_type in (NodeType.ANSWER, NodeType.GROUNDED_CLAIM, NodeType.SYNTHESIS):
                findings.append(f"### {child.content[:100]}\n{child.content}")
            # Also check children of children (answers of sub-questions)
            for grandchild in graph.get_children(child.id):
                if grandchild.node_type in (
                    NodeType.ANSWER,
                    NodeType.GROUNDED_CLAIM,
                    NodeType.SYNTHESIS,
                ):
                    findings.append(
                        f"### Re: {child.content[:80]}\n{grandchild.content}"
                    )

        if not findings:
            logger.info(f"No findings to synthesize for node {node.id}")
            return []

        prompt = SYNTHESIZE_PROMPT.format(
            question=node.content,
            findings="\n\n---\n\n".join(findings),
        )

        content = await call_llm(prompt, model=model)

        synth_node = Node(
            node_type=NodeType.SYNTHESIS,
            content=content,
            status=EpistemicStatus.SYNTHESIZED,
            depth=node.depth,
            parent_id=node.id,
            model=model,
        )

        node.status = EpistemicStatus.SYNTHESIZED
        return [synth_node]
