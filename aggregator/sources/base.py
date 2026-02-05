"""Base class for data sources."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DataItem:
    """A single piece of collected data."""

    source: str
    source_url: str
    title: str
    content: str
    collected_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "source": self.source,
            "source_url": self.source_url,
            "title": self.title,
            "content": self.content,
            "collected_at": self.collected_at.isoformat(),
            "metadata": self.metadata,
        }


class DataSource(ABC):
    """Abstract base class for data sources."""

    def __init__(self, name: str):
        self.name = name
        self.items: list[DataItem] = []

    @abstractmethod
    def collect(self, search_term: str) -> list[DataItem]:
        """Collect data from this source.

        Args:
            search_term: The term to search for.

        Returns:
            List of collected data items.
        """
        pass

    def get_items(self) -> list[DataItem]:
        """Get all collected items."""
        return self.items

    def clear(self) -> None:
        """Clear collected items."""
        self.items = []
