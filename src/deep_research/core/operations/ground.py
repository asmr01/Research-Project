"""GROUND: Verify claims with web search."""

from __future__ import annotations

import logging
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation

logger = logging.getLogger(__name__)

GROUND_PROMPT = """You are a fact-checking agent. Given an answer, extract key claims and assess their verifiability.

Answer to verify:
{answer}

Web search results:
{search_results}

Rules:
- For each major claim, note whether it is SUPPORTED, PARTIALLY SUPPORTED, or UNSUPPORTED by the search results
- Provide corrected information where search results contradict the answer
- Format your response as a grounded version of the original answer with inline citations
"""

EXTRACT_CLAIMS_PROMPT = """Extract 3-5 key factual claims from this text that can be verified via web search. Return one claim per line, prefixed with "- ".

Text: {text}
"""


class GroundOperation(Operation):
    name = "ground"

    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        from deep_research.providers import call_llm

        model = context.get("model", "haiku")
        web_search = context.get("web_search", False)

        if not web_search:
            # Without web search, just mark as explored
            logger.info("Web search disabled, skipping grounding")
            return []

        # Extract key claims
        claims_response = await call_llm(
            EXTRACT_CLAIMS_PROMPT.format(text=node.content[:1500]),
            model=model,
        )

        claims = []
        for line in claims_response.strip().split("\n"):
            line = line.strip()
            if line.startswith("- "):
                claims.append(line[2:].strip())

        if not claims:
            return []

        # Search for each claim
        search_results = []
        for claim in claims[:5]:
            try:
                results = await _web_search(claim)
                search_results.append(f"Claim: {claim}\nResults: {results}")
            except Exception as e:
                logger.warning(f"Web search failed for claim: {e}")
                search_results.append(f"Claim: {claim}\nResults: (search failed)")

        # Ground the answer
        prompt = GROUND_PROMPT.format(
            answer=node.content,
            search_results="\n\n".join(search_results),
        )

        content = await call_llm(prompt, model=model)

        grounded_node = Node(
            node_type=NodeType.GROUNDED_CLAIM,
            content=content,
            status=EpistemicStatus.GROUNDED,
            depth=node.depth,
            parent_id=node.parent_id,
            model=model,
            metadata={"claims_checked": len(claims)},
        )

        return [grounded_node]


async def _web_search(query: str) -> str:
    """Perform a web search. Uses httpx to query a search API."""
    import httpx
    import os

    # Try multiple search backends
    # 1. SerpAPI
    serp_key = os.environ.get("SERPAPI_KEY")
    if serp_key:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={"q": query, "api_key": serp_key, "num": 3},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("organic_results", [])
                return "\n".join(
                    f"- {r.get('title', '')}: {r.get('snippet', '')}"
                    for r in results[:3]
                )

    # 2. Fallback: return a note that web search is not configured
    return "(Web search API not configured. Set SERPAPI_KEY for web grounding.)"
