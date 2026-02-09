"""Knowledge graph with persistence and traversal."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from deep_research.core.node import Node, NodeType, EpistemicStatus


class KnowledgeGraph:
    """A directed graph of typed nodes with checkpoint support."""

    def __init__(self) -> None:
        self._nodes: dict[str, Node] = {}
        self._root_id: str | None = None

    @property
    def root(self) -> Node | None:
        if self._root_id:
            return self._nodes.get(self._root_id)
        return None

    @property
    def size(self) -> int:
        return len(self._nodes)

    def add_node(self, node: Node) -> Node:
        self._nodes[node.id] = node
        if node.parent_id is None and self._root_id is None:
            self._root_id = node.id
        if node.parent_id and node.parent_id in self._nodes:
            self._nodes[node.parent_id].add_child(node.id)
        return node

    def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    def get_children(self, node_id: str) -> list[Node]:
        node = self._nodes.get(node_id)
        if not node:
            return []
        return [self._nodes[cid] for cid in node.children_ids if cid in self._nodes]

    def get_ancestors(self, node_id: str) -> list[Node]:
        ancestors = []
        current = self._nodes.get(node_id)
        while current and current.parent_id:
            parent = self._nodes.get(current.parent_id)
            if parent:
                ancestors.append(parent)
            current = parent
        return ancestors

    def nodes_by_type(self, node_type: NodeType) -> list[Node]:
        return [n for n in self._nodes.values() if n.node_type == node_type]

    def nodes_by_status(self, status: EpistemicStatus) -> list[Node]:
        return [n for n in self._nodes.values() if n.status == status]

    def nodes_at_depth(self, depth: int) -> list[Node]:
        return [n for n in self._nodes.values() if n.depth == depth]

    def leaves(self) -> list[Node]:
        return [n for n in self._nodes.values() if n.is_leaf]

    def unanswered_questions(self) -> list[Node]:
        return [
            n for n in self._nodes.values()
            if n.node_type == NodeType.QUESTION and n.status == EpistemicStatus.UNKNOWN
        ]

    def max_depth(self) -> int:
        if not self._nodes:
            return 0
        return max(n.depth for n in self._nodes.values())

    def walk_depth_first(self, node_id: str | None = None) -> Iterator[Node]:
        start_id = node_id or self._root_id
        if not start_id or start_id not in self._nodes:
            return
        node = self._nodes[start_id]
        yield node
        for child_id in node.children_ids:
            yield from self.walk_depth_first(child_id)

    def walk_breadth_first(self) -> Iterator[Node]:
        if not self._root_id:
            return
        queue = [self._root_id]
        while queue:
            nid = queue.pop(0)
            node = self._nodes.get(nid)
            if node:
                yield node
                queue.extend(node.children_ids)

    def save(self, path: Path) -> None:
        data = {
            "root_id": self._root_id,
            "nodes": {nid: n.model_dump() for nid, n in self._nodes.items()},
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))

    @classmethod
    def load(cls, path: Path) -> KnowledgeGraph:
        data = json.loads(path.read_text())
        graph = cls()
        graph._root_id = data["root_id"]
        for nid, ndata in data["nodes"].items():
            graph._nodes[nid] = Node(**ndata)
        return graph

    def summary(self) -> dict:
        type_counts: dict[str, int] = {}
        status_counts: dict[str, int] = {}
        for n in self._nodes.values():
            type_counts[n.node_type.value] = type_counts.get(n.node_type.value, 0) + 1
            status_counts[n.status.value] = status_counts.get(n.status.value, 0) + 1
        return {
            "total_nodes": self.size,
            "max_depth": self.max_depth(),
            "types": type_counts,
            "statuses": status_counts,
        }
