"""Review aggregation from various healthcare review platforms."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import DataItem, DataSource


@dataclass
class ReviewSummary:
    """Summary of reviews from a source."""

    source_name: str
    source_url: str
    average_rating: float | None
    total_reviews: int
    rating_distribution: dict[int, int]
    recent_reviews: list[dict[str, Any]]
    pros: list[str]
    cons: list[str]


class ReviewAggregator(DataSource):
    """Aggregates patient and provider reviews from multiple platforms."""

    # Known review platforms for healthcare
    REVIEW_SOURCES = {
        "healthgrades": {
            "name": "Healthgrades",
            "search_url": "https://www.healthgrades.com/",
            "description": "Patient reviews and provider ratings",
        },
        "vitals": {
            "name": "Vitals",
            "search_url": "https://www.vitals.com/",
            "description": "Doctor reviews and ratings",
        },
        "zocdoc": {
            "name": "Zocdoc",
            "search_url": "https://www.zocdoc.com/",
            "description": "Appointment booking and patient reviews",
        },
        "google": {
            "name": "Google Reviews",
            "search_url": "https://www.google.com/maps/",
            "description": "Google Maps business reviews",
        },
        "yelp": {
            "name": "Yelp",
            "search_url": "https://www.yelp.com/",
            "description": "Consumer reviews platform",
        },
        "ratemds": {
            "name": "RateMDs",
            "search_url": "https://www.ratemds.com/",
            "description": "Doctor ratings and reviews",
        },
    }

    def __init__(self):
        super().__init__("Review Aggregator")
        self.summaries: list[ReviewSummary] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect review data for the given search term.

        This method prepares search queries for various review platforms.
        Actual data collection requires web scraping or API access.

        Args:
            search_term: Institution or provider to search for.

        Returns:
            List of DataItem objects with review information.
        """
        self.items = []

        # Generate search queries for each platform
        for source_id, source_info in self.REVIEW_SOURCES.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["search_url"],
                title=f"Review search: {search_term}",
                content=f"Search for '{search_term}' on {source_info['name']}",
                metadata={
                    "source_id": source_id,
                    "description": source_info["description"],
                    "search_query": self._build_search_query(search_term, source_id),
                },
            )
            self.items.append(item)

        return self.items

    def _build_search_query(self, search_term: str, source_id: str) -> str:
        """Build a search query URL for the given source."""
        encoded_term = search_term.replace(" ", "+")

        query_templates = {
            "healthgrades": f"site:healthgrades.com {search_term}",
            "vitals": f"site:vitals.com {search_term}",
            "zocdoc": f"site:zocdoc.com {search_term}",
            "google": f"{search_term} reviews",
            "yelp": f"site:yelp.com {search_term}",
            "ratemds": f"site:ratemds.com {search_term}",
        }

        return query_templates.get(source_id, search_term)

    def parse_rating(self, rating_text: str) -> float | None:
        """Parse a rating from text format.

        Args:
            rating_text: Text containing a rating (e.g., "4.5 out of 5").

        Returns:
            Numeric rating or None if parsing fails.
        """
        patterns = [
            r"(\d+\.?\d*)\s*(?:out of|/)\s*5",
            r"(\d+\.?\d*)\s*stars?",
            r"rating[:\s]+(\d+\.?\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, rating_text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue

        return None

    def extract_sentiment(self, reviews: list[str]) -> tuple[list[str], list[str]]:
        """Extract common positive and negative themes from reviews.

        Args:
            reviews: List of review texts.

        Returns:
            Tuple of (pros list, cons list).
        """
        positive_keywords = [
            "excellent",
            "great",
            "wonderful",
            "caring",
            "professional",
            "helpful",
            "knowledgeable",
            "thorough",
            "compassionate",
            "attentive",
            "friendly",
            "efficient",
        ]

        negative_keywords = [
            "wait",
            "rushed",
            "rude",
            "unprofessional",
            "dismissive",
            "expensive",
            "long wait",
            "difficult",
            "poor",
            "terrible",
            "awful",
            "disappointing",
        ]

        pros = []
        cons = []

        all_text = " ".join(reviews).lower()

        for keyword in positive_keywords:
            if keyword in all_text:
                pros.append(keyword.capitalize())

        for keyword in negative_keywords:
            if keyword in all_text:
                cons.append(keyword.capitalize())

        return pros[:5], cons[:5]

    def get_platform_info(self) -> list[dict[str, str]]:
        """Get information about supported review platforms."""
        return [
            {
                "id": source_id,
                "name": info["name"],
                "url": info["search_url"],
                "description": info["description"],
            }
            for source_id, info in self.REVIEW_SOURCES.items()
        ]
