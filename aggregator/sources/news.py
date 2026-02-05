"""News and article collection about healthcare institutions."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import DataItem, DataSource


@dataclass
class NewsArticle:
    """A news article or press release."""

    title: str
    source: str
    url: str
    date: datetime | None
    summary: str
    category: str


class NewsCollector(DataSource):
    """Collects news articles and press releases about healthcare institutions."""

    # News and information sources
    NEWS_SOURCES = {
        "institution_news": {
            "name": "Institution News/Press Releases",
            "description": "Official news and announcements from the institution",
            "url_pattern": "news OR press release",
        },
        "medical_journals": {
            "name": "Medical Journals & Publications",
            "description": "Research publications and clinical studies",
            "url_pattern": "pubmed OR medical journal",
        },
        "healthcare_news": {
            "name": "Healthcare Industry News",
            "description": "Coverage from healthcare industry publications",
            "sources": [
                "Modern Healthcare",
                "Becker's Hospital Review",
                "Healthcare Dive",
                "Fierce Healthcare",
            ],
        },
        "local_news": {
            "name": "Local News Coverage",
            "description": "Coverage from local news outlets",
            "url_pattern": "Boston Globe OR WBUR OR Boston Herald",
        },
        "awards_recognition": {
            "name": "Awards & Recognition",
            "description": "Industry awards and accolades",
            "url_pattern": "award OR recognition OR honor",
        },
    }

    # Categories of news to track
    NEWS_CATEGORIES = [
        "Clinical achievements",
        "Research breakthroughs",
        "New programs/services",
        "Leadership changes",
        "Facility expansions",
        "Community outreach",
        "Patient stories",
        "Awards and recognition",
        "Regulatory/compliance news",
        "Financial/operational updates",
    ]

    def __init__(self):
        super().__init__("News Collector")
        self.articles: list[NewsArticle] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect news and articles about the given institution.

        Args:
            search_term: Institution to search for.

        Returns:
            List of DataItem objects with news information.
        """
        self.items = []

        # Generate search items for each news source type
        for source_id, source_info in self.NEWS_SOURCES.items():
            item = DataItem(
                source=source_info["name"],
                source_url="",
                title=f"News search: {search_term}",
                content=f"Search for news about {search_term}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "search_queries": self._build_search_queries(search_term, source_id),
                },
            )
            self.items.append(item)

        return self.items

    def _build_search_queries(self, search_term: str, source_id: str) -> list[str]:
        """Build search queries for news about the institution."""
        base_queries = []

        if source_id == "institution_news":
            base_queries = [
                f"{search_term} news",
                f"{search_term} press release",
                f"{search_term} announcement",
            ]
        elif source_id == "medical_journals":
            base_queries = [
                f"{search_term} research study",
                f"{search_term} clinical trial",
                f"site:pubmed.gov {search_term}",
            ]
        elif source_id == "healthcare_news":
            sources = self.NEWS_SOURCES[source_id].get("sources", [])
            base_queries = [f'"{search_term}" {source}' for source in sources[:2]]
            base_queries.append(f"{search_term} healthcare news")
        elif source_id == "local_news":
            base_queries = [
                f"{search_term} Boston Globe",
                f"{search_term} Boston news",
                f"{search_term} Massachusetts healthcare",
            ]
        elif source_id == "awards_recognition":
            base_queries = [
                f"{search_term} award",
                f"{search_term} best hospital",
                f"{search_term} recognition",
            ]

        return base_queries

    def get_news_categories(self) -> list[str]:
        """Get list of news categories being tracked."""
        return self.NEWS_CATEGORIES.copy()

    def get_source_info(self) -> list[dict[str, Any]]:
        """Get information about news sources."""
        return [
            {
                "id": source_id,
                "name": info["name"],
                "description": info["description"],
            }
            for source_id, info in self.NEWS_SOURCES.items()
        ]
