"""Typed nodes with epistemic state tracking."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    QUESTION = "question"
    ANSWER = "answer"
    INSIGHT = "insight"
    BLIND_SPOT = "blind_spot"
    TENSION = "tension"
    SYNTHESIS = "synthesis"
    PERSPECTIVE = "perspective"
    GROUNDED_CLAIM = "grounded_claim"
    WEB_RESULT = "web_result"


class EpistemicStatus(str, Enum):
    UNKNOWN = "unknown"
    EXPLORED = "explored"
    VALIDATED = "validated"
    SYNTHESIZED = "synthesized"
    GROUNDED = "grounded"
    REFUTED = "refuted"


class Node(BaseModel):
    """A typed content unit in the knowledge graph."""

    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:12])
    node_type: NodeType
    content: str
    status: EpistemicStatus = EpistemicStatus.UNKNOWN
    depth: int = 0
    parent_id: str | None = None
    children_ids: list[str] = Field(default_factory=list)
    model: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def add_child(self, child_id: str) -> None:
        if child_id not in self.children_ids:
            self.children_ids.append(child_id)

    @property
    def is_leaf(self) -> bool:
        return len(self.children_ids) == 0

    @property
    def is_question(self) -> bool:
        return self.node_type == NodeType.QUESTION

    @property
    def is_answer(self) -> bool:
        return self.node_type == NodeType.ANSWER
