"""Operation protocol - epistemic transitions on nodes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from deep_research.core.node import Node
from deep_research.core.graph import KnowledgeGraph


class Operation(ABC):
    """Base class for epistemic operations on the knowledge graph."""

    name: str = "operation"

    @abstractmethod
    async def execute(
        self,
        node: Node,
        graph: KnowledgeGraph,
        context: dict[str, Any],
    ) -> list[Node]:
        """Execute operation on a node, returning new nodes to add to the graph.

        Args:
            node: The node to operate on.
            graph: The knowledge graph.
            context: Execution context (model config, output_dir, etc.)

        Returns:
            List of new nodes produced by this operation.
        """
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
