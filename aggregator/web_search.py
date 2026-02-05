"""Web search functionality for aggregating online information."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import quote_plus


@dataclass
class SearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str
    source: str
    date: datetime | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source,
            "date": self.date.isoformat() if self.date else None,
            "metadata": self.metadata or {},
        }


class WebSearchManager:
    """Manages web searches for healthcare information aggregation."""

    # Pre-defined search queries for Mass General Psychiatry
    SEARCH_QUERIES = {
        "reviews": [
            "Massachusetts General Hospital Psychiatry reviews",
            "Mass General Psychiatry patient reviews",
            "MGH Behavioral Health reviews ratings",
            "Massachusetts General Hospital mental health patient experience",
            '"Mass General" psychiatry Healthgrades',
            '"Massachusetts General Hospital" psychiatry Vitals reviews',
        ],
        "quality_metrics": [
            "Massachusetts General Hospital Psychiatry quality ratings",
            "MGH Psychiatry US News ranking",
            "Mass General Behavioral Health accreditation",
            "Massachusetts General Hospital mental health outcomes",
            "MGH Psychiatry Joint Commission",
            "Mass General Hospital CMS quality ratings",
        ],
        "provider_info": [
            "Massachusetts General Hospital Psychiatry doctors",
            "MGH Psychiatry department providers",
            "Mass General mental health specialists",
            "Massachusetts General Hospital psychiatrists",
        ],
        "services": [
            "Massachusetts General Hospital Psychiatry services",
            "MGH inpatient psychiatry programs",
            "Mass General outpatient mental health",
            "Massachusetts General Hospital behavioral health programs",
            "MGH Psychiatry telehealth telepsychiatry",
        ],
        "news": [
            "Massachusetts General Hospital Psychiatry news 2024 2025",
            "MGH mental health research",
            "Mass General Psychiatry awards recognition",
            "Massachusetts General Hospital behavioral health expansion",
        ],
        "research": [
            "Massachusetts General Hospital Psychiatry research publications",
            "MGH Psychiatry clinical trials",
            "Mass General mental health studies",
        ],
    }

    def __init__(self):
        self.results: dict[str, list[SearchResult]] = {}

    def get_search_queries(self, category: str | None = None) -> dict[str, list[str]]:
        """Get search queries for one or all categories.

        Args:
            category: Optional category to filter by.

        Returns:
            Dictionary of category to queries.
        """
        if category:
            return {category: self.SEARCH_QUERIES.get(category, [])}
        return self.SEARCH_QUERIES.copy()

    def build_google_search_url(self, query: str) -> str:
        """Build a Google search URL for the given query."""
        encoded_query = quote_plus(query)
        return f"https://www.google.com/search?q={encoded_query}"

    def build_search_urls(self) -> dict[str, list[dict[str, str]]]:
        """Build search URLs for all predefined queries.

        Returns:
            Dictionary mapping categories to lists of {query, url} dicts.
        """
        urls = {}
        for category, queries in self.SEARCH_QUERIES.items():
            urls[category] = [
                {"query": q, "url": self.build_google_search_url(q)} for q in queries
            ]
        return urls

    def parse_rating_from_text(self, text: str) -> dict[str, Any] | None:
        """Extract rating information from text.

        Args:
            text: Text that may contain rating information.

        Returns:
            Dictionary with rating info or None.
        """
        patterns = [
            # "4.5 out of 5 stars"
            (r"(\d+\.?\d*)\s*(?:out of|/)\s*5\s*stars?", "stars"),
            # "Rating: 4.5"
            (r"rating[:\s]+(\d+\.?\d*)", "rating"),
            # "4.5 stars"
            (r"(\d+\.?\d*)\s*stars?", "stars"),
            # "92% would recommend"
            (r"(\d+)%\s*(?:would\s+)?recommend", "recommend_pct"),
            # "87% patient satisfaction"
            (r"(\d+)%\s*(?:patient\s+)?satisfaction", "satisfaction_pct"),
        ]

        for pattern, rating_type in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    return {"type": rating_type, "value": value, "raw_match": match.group(0)}
                except ValueError:
                    continue

        return None

    def parse_review_count(self, text: str) -> int | None:
        """Extract review count from text.

        Args:
            text: Text that may contain review count.

        Returns:
            Number of reviews or None.
        """
        patterns = [
            r"(\d+,?\d*)\s*reviews?",
            r"(\d+,?\d*)\s*ratings?",
            r"based on\s*(\d+,?\d*)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(",", ""))
                except ValueError:
                    continue

        return None

    def categorize_content(self, text: str) -> list[str]:
        """Categorize content based on keywords.

        Args:
            text: Text to categorize.

        Returns:
            List of applicable categories.
        """
        categories = []
        text_lower = text.lower()

        category_keywords = {
            "patient_review": ["patient", "review", "experience", "visit", "appointment"],
            "quality_metric": ["rating", "quality", "score", "ranking", "accreditation"],
            "provider_info": ["doctor", "physician", "psychiatrist", "provider", "specialist"],
            "service_info": ["program", "service", "treatment", "therapy", "inpatient", "outpatient"],
            "research": ["research", "study", "clinical trial", "publication"],
            "news": ["news", "announced", "award", "recognition", "expansion"],
        }

        for category, keywords in category_keywords.items():
            if any(kw in text_lower for kw in keywords):
                categories.append(category)

        return categories if categories else ["general"]


def get_aggregation_report_template() -> str:
    """Get a template for the aggregation report."""
    return """
# Mass General Psychiatry Information Report

## Overview
This report compiles publicly available information about Massachusetts General
Hospital's Psychiatry and Behavioral Health services.

## Data Sources Searched

### Review Platforms
- Healthgrades
- Vitals
- Zocdoc
- Google Reviews
- Yelp
- RateMDs

### Quality & Rating Organizations
- CMS Hospital Compare (Medicare)
- U.S. News & World Report
- Leapfrog Hospital Safety Grade
- The Joint Commission
- SAMHSA

### News & Information
- Institution press releases
- Healthcare industry publications
- Local news outlets
- Medical journals (PubMed)

## Search Queries Used
{search_queries}

## Findings

### Patient Reviews
{patient_reviews}

### Quality Metrics
{quality_metrics}

### Provider Information
{provider_info}

### Services & Programs
{services}

### Recent News
{news}

## Methodology
Data was aggregated from publicly available online sources. Information accuracy
depends on source reliability and currency. Users should verify critical information
through official channels.

---
Generated: {timestamp}
"""
