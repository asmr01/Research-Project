"""ANSWER: Generate an answer for a question node."""

from __future__ import annotations

import logging
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation

logger = logging.getLogger(__name__)

ANSWER_PROMPT = """You are a research agent answering a specific question in depth.

Question: {question}

Context chain (ancestor questions): {context_chain}

Rules:
- Provide a thorough, evidence-based answer
- Acknowledge uncertainty where appropriate
- Include specific examples, data, or references when possible
- Be concise but comprehensive (aim for 200-400 words)
- Structure your response with clear paragraphs
"""

ENSEMBLE_MERGE_PROMPT = """You are merging multiple answers to the same question from different models/perspectives.

Question: {question}

Answers to merge:
{answers}

Rules:
- Synthesize all answers into one comprehensive response
- Preserve unique insights from each answer
- Resolve contradictions by noting them explicitly
- Aim for 300-500 words
"""


class AnswerOperation(Operation):
    name = "answer"

    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        from deep_research.providers import call_llm

        researcher_model = context.get("researcher_model", context.get("model", "haiku"))
        leaf_models = context.get("leaf_models")
        merger_model = context.get("merger_model")

        ancestors = graph.get_ancestors(node.id)
        context_chain = " → ".join(a.content[:80] for a in reversed(ancestors))
        if not context_chain:
            context_chain = "(root question)"

        prompt = ANSWER_PROMPT.format(
            question=node.content,
            context_chain=context_chain,
        )

        if leaf_models and len(leaf_models) > 1:
            # Ensemble mode: multiple models answer, then merge
            import asyncio
            tasks = [call_llm(prompt, model=m) for m in leaf_models]
            responses = await asyncio.gather(*tasks, return_exceptions=True)

            valid_responses = []
            for i, resp in enumerate(responses):
                if isinstance(resp, Exception):
                    logger.warning(f"Ensemble model {leaf_models[i]} failed: {resp}")
                else:
                    valid_responses.append(f"### Model: {leaf_models[i]}\n{resp}")

            if len(valid_responses) > 1 and merger_model:
                merge_prompt = ENSEMBLE_MERGE_PROMPT.format(
                    question=node.content,
                    answers="\n\n---\n\n".join(valid_responses),
                )
                content = await call_llm(merge_prompt, model=merger_model)
            elif valid_responses:
                content = valid_responses[0]
            else:
                content = "(All ensemble models failed to respond)"
        else:
            content = await call_llm(prompt, model=researcher_model)

        answer_node = Node(
            node_type=NodeType.ANSWER,
            content=content,
            status=EpistemicStatus.EXPLORED,
            depth=node.depth,
            parent_id=node.id,
            model=researcher_model,
        )

        node.status = EpistemicStatus.EXPLORED
        return [answer_node]
