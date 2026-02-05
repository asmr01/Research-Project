#!/usr/bin/env python3
"""
Live data aggregation using web searches.

This module provides functionality to perform live web searches and aggregate
real data about Mass General Psychiatry from various online sources.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .report import ReportGenerator
from .web_search import SearchResult, WebSearchManager


@dataclass
class AggregatedData:
    """Container for aggregated data from web searches."""

    query: str
    category: str
    results: list[dict[str, Any]] = field(default_factory=list)
    collected_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "category": self.category,
            "results": self.results,
            "collected_at": self.collected_at.isoformat(),
            "metadata": self.metadata,
        }


class LiveAggregator:
    """Performs live web searches to aggregate healthcare data.

    This class is designed to work with external web search capabilities
    (APIs, browser automation, or manual search execution) to collect
    real data about Mass General Psychiatry.
    """

    INSTITUTION_NAME = "Massachusetts General Hospital Psychiatry"

    # Key URLs for direct access
    DIRECT_URLS = {
        "mgh_psychiatry": "https://www.massgeneral.org/psychiatry",
        "mgh_behavioral_health": "https://www.massgeneral.org/behavioral-health",
        "us_news_mgh": "https://health.usnews.com/best-hospitals/area/ma/massachusetts-general-hospital-6140430",
        "healthgrades_mgh": "https://www.healthgrades.com/hospital-directory/ma-massachusetts/massachusetts-general-hospital-hosptl0029871",
        "cms_compare": "https://www.medicare.gov/care-compare/",
        "leapfrog": "https://www.hospitalsafetygrade.org/",
    }

    def __init__(self, search_function: Callable[[str], list[dict]] | None = None):
        """Initialize the live aggregator.

        Args:
            search_function: Optional function that takes a search query string
                           and returns a list of search results as dictionaries
                           with keys: title, url, snippet.
        """
        self.search_manager = WebSearchManager()
        self.search_function = search_function
        self.aggregated_data: list[AggregatedData] = []
        self.raw_results: dict[str, list[dict]] = {}

    def set_search_function(self, func: Callable[[str], list[dict]]) -> None:
        """Set the search function to use for web searches."""
        self.search_function = func

    def search(self, query: str) -> list[dict[str, Any]]:
        """Perform a web search.

        Args:
            query: Search query string.

        Returns:
            List of search results.
        """
        if self.search_function:
            return self.search_function(query)

        # Return empty list if no search function is configured
        # This allows the tool to be used in "dry run" mode
        return []

    def collect_reviews(self) -> AggregatedData:
        """Collect review data from web searches."""
        queries = self.search_manager.get_search_queries("reviews")["reviews"]
        all_results = []

        for query in queries:
            results = self.search(query)
            all_results.extend(results)

        data = AggregatedData(
            query="reviews",
            category="Patient & Provider Reviews",
            results=all_results,
            metadata={"queries_used": queries, "source_count": len(queries)},
        )

        self.aggregated_data.append(data)
        return data

    def collect_quality_metrics(self) -> AggregatedData:
        """Collect quality metrics from web searches."""
        queries = self.search_manager.get_search_queries("quality_metrics")["quality_metrics"]
        all_results = []

        for query in queries:
            results = self.search(query)
            all_results.extend(results)

        data = AggregatedData(
            query="quality_metrics",
            category="Quality Metrics & Ratings",
            results=all_results,
            metadata={"queries_used": queries, "source_count": len(queries)},
        )

        self.aggregated_data.append(data)
        return data

    def collect_news(self) -> AggregatedData:
        """Collect news articles from web searches."""
        queries = self.search_manager.get_search_queries("news")["news"]
        all_results = []

        for query in queries:
            results = self.search(query)
            all_results.extend(results)

        data = AggregatedData(
            query="news",
            category="News & Media Coverage",
            results=all_results,
            metadata={"queries_used": queries, "source_count": len(queries)},
        )

        self.aggregated_data.append(data)
        return data

    def collect_provider_info(self) -> AggregatedData:
        """Collect provider information from web searches."""
        queries = self.search_manager.get_search_queries("provider_info")["provider_info"]
        all_results = []

        for query in queries:
            results = self.search(query)
            all_results.extend(results)

        data = AggregatedData(
            query="provider_info",
            category="Provider Information",
            results=all_results,
            metadata={"queries_used": queries, "source_count": len(queries)},
        )

        self.aggregated_data.append(data)
        return data

    def collect_services(self) -> AggregatedData:
        """Collect services information from web searches."""
        queries = self.search_manager.get_search_queries("services")["services"]
        all_results = []

        for query in queries:
            results = self.search(query)
            all_results.extend(results)

        data = AggregatedData(
            query="services",
            category="Services & Programs",
            results=all_results,
            metadata={"queries_used": queries, "source_count": len(queries)},
        )

        self.aggregated_data.append(data)
        return data

    def collect_all(self) -> list[AggregatedData]:
        """Collect data from all categories.

        Returns:
            List of AggregatedData objects for each category.
        """
        self.aggregated_data = []

        print("Collecting reviews...")
        self.collect_reviews()

        print("Collecting quality metrics...")
        self.collect_quality_metrics()

        print("Collecting news...")
        self.collect_news()

        print("Collecting provider info...")
        self.collect_provider_info()

        print("Collecting services...")
        self.collect_services()

        print(f"Collection complete. {len(self.aggregated_data)} categories collected.")
        return self.aggregated_data

    def add_search_results(self, category: str, results: list[dict[str, Any]]) -> None:
        """Manually add search results for a category.

        This is useful when search results are obtained externally
        (e.g., from an API or manual search).

        Args:
            category: Category name (reviews, quality_metrics, news, etc.)
            results: List of result dictionaries.
        """
        self.raw_results[category] = results

        data = AggregatedData(
            query=category,
            category=category,
            results=results,
            metadata={"manually_added": True},
        )
        self.aggregated_data.append(data)

    def generate_report(self, output_dir: str | Path = "reports") -> list[Path]:
        """Generate a report from collected data.

        Args:
            output_dir: Directory to save the report.

        Returns:
            List of paths to generated report files.
        """
        report = ReportGenerator(self.INSTITUTION_NAME)

        report.set_metadata(
            "executive_summary",
            f"This report compiles information about {self.INSTITUTION_NAME} "
            "gathered from live web searches across multiple categories including "
            "patient reviews, quality metrics, news coverage, and service information.",
        )

        sources_used = set()

        for data in self.aggregated_data:
            # Convert results to DataItem-like format for the report
            items = []
            for result in data.results:
                items.append({
                    "title": result.get("title", ""),
                    "source": result.get("source", "Web Search"),
                    "source_url": result.get("url", ""),
                    "content": result.get("snippet", ""),
                    "metadata": result.get("metadata", {}),
                })
                if result.get("source"):
                    sources_used.add(result["source"])

            report.add_web_results(
                title=data.category,
                results=items,
                summary=f"Results from {len(data.results)} search results.",
            )

        report.set_metadata("sources_used", list(sources_used))
        report.set_metadata("collection_timestamp", datetime.now().isoformat())

        return report.save(output_dir)

    def get_direct_urls(self) -> dict[str, str]:
        """Get direct URLs for key information sources."""
        return self.DIRECT_URLS.copy()

    def export_queries(self, output_path: str | Path | None = None) -> str:
        """Export all search queries as JSON.

        Args:
            output_path: Optional path to save the queries.

        Returns:
            JSON string of all queries.
        """
        queries = self.search_manager.get_search_queries()
        queries_json = json.dumps(queries, indent=2)

        if output_path:
            Path(output_path).write_text(queries_json)

        return queries_json
