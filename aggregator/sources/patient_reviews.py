"""Patient review aggregation from healthcare review platforms and social media."""

import re
from dataclasses import dataclass
from typing import Any

from .base import DataItem, DataSource


@dataclass
class PatientReviewSummary:
    """Summary of patient reviews from a source."""

    source_name: str
    source_url: str
    average_rating: float | None
    total_reviews: int
    rating_distribution: dict[int, int]
    recent_reviews: list[dict[str, Any]]
    common_praises: list[str]
    common_complaints: list[str]


class PatientReviewAggregator(DataSource):
    """Aggregates patient reviews and experiences from multiple platforms."""

    # Healthcare review platforms (patient-focused)
    REVIEW_PLATFORMS = {
        "healthgrades": {
            "name": "Healthgrades",
            "url": "https://www.healthgrades.com/",
            "description": "Patient reviews, provider ratings, and hospital quality data",
            "review_type": "patient",
        },
        "vitals": {
            "name": "Vitals",
            "url": "https://www.vitals.com/",
            "description": "Patient reviews and doctor ratings",
            "review_type": "patient",
        },
        "zocdoc": {
            "name": "Zocdoc",
            "url": "https://www.zocdoc.com/",
            "description": "Appointment booking with verified patient reviews",
            "review_type": "patient",
        },
        "google_reviews": {
            "name": "Google Reviews",
            "url": "https://www.google.com/maps/",
            "description": "Google Maps business reviews from patients",
            "review_type": "patient",
        },
        "yelp": {
            "name": "Yelp",
            "url": "https://www.yelp.com/",
            "description": "Consumer reviews including healthcare facilities",
            "review_type": "patient",
        },
        "ratemds": {
            "name": "RateMDs",
            "url": "https://www.ratemds.com/",
            "description": "Doctor ratings and patient reviews",
            "review_type": "patient",
        },
        "webmd": {
            "name": "WebMD Physician Directory",
            "url": "https://doctor.webmd.com/",
            "description": "Patient reviews and physician ratings",
            "review_type": "patient",
        },
        "caring": {
            "name": "Caring.com",
            "url": "https://www.caring.com/",
            "description": "Senior care and mental health facility reviews",
            "review_type": "patient",
        },
    }

    # Social media and community platforms
    SOCIAL_PLATFORMS = {
        "reddit": {
            "name": "Reddit",
            "url": "https://www.reddit.com/",
            "description": "Community discussions and patient experiences",
            "subreddits": [
                "r/boston",
                "r/massachusetts",
                "r/mentalhealth",
                "r/depression",
                "r/anxiety",
                "r/bipolar",
                "r/ADHD",
                "r/therapy",
                "r/psychiatry",
                "r/askdocs",
            ],
            "review_type": "community",
        },
        "facebook": {
            "name": "Facebook Reviews",
            "url": "https://www.facebook.com/",
            "description": "Facebook page reviews and community groups",
            "review_type": "community",
        },
        "patient_forums": {
            "name": "Patient Forums",
            "url": "",
            "description": "Various patient community forums and support groups",
            "review_type": "community",
        },
    }

    def __init__(self):
        super().__init__("Patient Review Aggregator")
        self.summaries: list[PatientReviewSummary] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect patient review data for the given search term.

        Args:
            search_term: Institution or provider to search for.

        Returns:
            List of DataItem objects with review information.
        """
        self.items = []

        # Collect from review platforms
        for source_id, source_info in self.REVIEW_PLATFORMS.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Patient reviews: {search_term}",
                content=f"Patient reviews on {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "review_platform",
                    "review_type": source_info["review_type"],
                    "search_query": self._build_search_query(search_term, source_id),
                },
            )
            self.items.append(item)

        # Collect from social/community platforms
        for source_id, source_info in self.SOCIAL_PLATFORMS.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Community discussions: {search_term}",
                content=f"Patient discussions on {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "social_platform",
                    "review_type": source_info["review_type"],
                    "search_queries": self._build_social_queries(search_term, source_id),
                },
            )
            self.items.append(item)

        return self.items

    def _build_search_query(self, search_term: str, source_id: str) -> str:
        """Build a search query for the given review platform."""
        query_templates = {
            "healthgrades": f"site:healthgrades.com {search_term}",
            "vitals": f"site:vitals.com {search_term}",
            "zocdoc": f"site:zocdoc.com {search_term}",
            "google_reviews": f"{search_term} reviews",
            "yelp": f"site:yelp.com {search_term}",
            "ratemds": f"site:ratemds.com {search_term}",
            "webmd": f"site:doctor.webmd.com {search_term}",
            "caring": f"site:caring.com {search_term}",
        }
        return query_templates.get(source_id, search_term)

    def _build_social_queries(self, search_term: str, source_id: str) -> list[str]:
        """Build search queries for social/community platforms."""
        if source_id == "reddit":
            subreddits = self.SOCIAL_PLATFORMS["reddit"]["subreddits"]
            queries = [
                f"site:reddit.com {search_term}",
                f"site:reddit.com Mass General psychiatry",
                f"site:reddit.com MGH mental health",
                f"site:reddit.com Massachusetts General Hospital psychiatry experience",
            ]
            # Add subreddit-specific queries
            for sub in subreddits[:5]:
                queries.append(f"site:reddit.com/{sub} Mass General")
            return queries
        elif source_id == "facebook":
            return [
                f"site:facebook.com {search_term} reviews",
                f"site:facebook.com Mass General Psychiatry",
            ]
        else:
            return [f"{search_term} patient forum", f"{search_term} patient experience"]

    def get_reddit_queries(self, search_term: str) -> list[str]:
        """Get Reddit-specific search queries.

        Args:
            search_term: Institution to search for.

        Returns:
            List of Reddit search queries.
        """
        subreddits = self.SOCIAL_PLATFORMS["reddit"]["subreddits"]
        base_terms = [
            search_term,
            "Mass General Psychiatry",
            "MGH psychiatry",
            "Massachusetts General Hospital mental health",
        ]

        queries = []
        for term in base_terms:
            queries.append(f"site:reddit.com {term}")

        for sub in subreddits:
            queries.append(f"site:reddit.com/{sub} \"Mass General\"")
            queries.append(f"site:reddit.com/{sub} MGH psychiatry")

        return queries

    def parse_rating(self, rating_text: str) -> float | None:
        """Parse a rating from text format."""
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
        """Extract common positive and negative themes from patient reviews."""
        positive_keywords = [
            "caring", "compassionate", "listened", "helpful", "thorough",
            "professional", "knowledgeable", "patient", "understanding",
            "attentive", "responsive", "excellent", "recommend", "comfortable",
            "supportive", "effective treatment", "life-changing",
        ]

        negative_keywords = [
            "long wait", "rushed", "dismissive", "rude", "didn't listen",
            "expensive", "billing issues", "hard to reach", "no improvement",
            "side effects", "overmedicated", "understaffed", "impersonal",
            "difficult scheduling", "poor communication", "felt ignored",
        ]

        praises = []
        complaints = []
        all_text = " ".join(reviews).lower()

        for keyword in positive_keywords:
            if keyword in all_text:
                praises.append(keyword.title())

        for keyword in negative_keywords:
            if keyword in all_text:
                complaints.append(keyword.title())

        return praises[:7], complaints[:7]

    def get_platform_info(self) -> list[dict[str, Any]]:
        """Get information about supported platforms."""
        platforms = []

        for source_id, info in self.REVIEW_PLATFORMS.items():
            platforms.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "review_platform",
            })

        for source_id, info in self.SOCIAL_PLATFORMS.items():
            platforms.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "social_platform",
            })

        return platforms
