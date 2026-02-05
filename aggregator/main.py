#!/usr/bin/env python3
"""Main entry point for the Mass General Psychiatry Information Aggregator.

This tool aggregates information about Mass General Psychiatry from various
online sources including patient reviews, provider reviews, quality metrics,
and news articles.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from .report import ReportGenerator
from .sources import NewsCollector, QualityMetricsCollector, ReviewAggregator


class MassGeneralPsychiatryAggregator:
    """Main aggregator class for Mass General Psychiatry information."""

    DEFAULT_SEARCH_TERM = "Massachusetts General Hospital Psychiatry"
    ALTERNATIVE_TERMS = [
        "Mass General Psychiatry",
        "MGH Psychiatry",
        "Mass General Behavioral Health",
        "Massachusetts General Hospital Mental Health",
    ]

    def __init__(self, output_dir: str | Path = "reports"):
        self.output_dir = Path(output_dir)
        self.review_aggregator = ReviewAggregator()
        self.quality_collector = QualityMetricsCollector()
        self.news_collector = NewsCollector()
        self.collected_data: dict[str, list[Any]] = {}

    def collect_all(self, search_term: str | None = None) -> dict[str, Any]:
        """Collect data from all sources.

        Args:
            search_term: Optional custom search term. Uses default if not provided.

        Returns:
            Dictionary containing all collected data.
        """
        term = search_term or self.DEFAULT_SEARCH_TERM

        print(f"Collecting data for: {term}")
        print("-" * 50)

        # Collect from all sources
        print("Gathering review sources...")
        reviews = self.review_aggregator.collect(term)

        print("Gathering quality metrics sources...")
        quality = self.quality_collector.collect(term)

        print("Gathering news sources...")
        news = self.news_collector.collect(term)

        self.collected_data = {
            "search_term": term,
            "collected_at": datetime.now().isoformat(),
            "reviews": reviews,
            "quality_metrics": quality,
            "news": news,
        }

        print(f"\nCollection complete!")
        print(f"  - Review sources: {len(reviews)}")
        print(f"  - Quality sources: {len(quality)}")
        print(f"  - News sources: {len(news)}")

        return self.collected_data

    def generate_report(
        self,
        include_search_queries: bool = True,
        formats: list[str] | None = None,
    ) -> list[Path]:
        """Generate a report from collected data.

        Args:
            include_search_queries: Whether to include search queries in the report.
            formats: Output formats ('markdown', 'json'). Defaults to both.

        Returns:
            List of paths to generated report files.
        """
        if not self.collected_data:
            raise ValueError("No data collected. Run collect_all() first.")

        report = ReportGenerator("Mass General Psychiatry")

        # Set metadata
        report.set_metadata(
            "executive_summary",
            "This report aggregates publicly available information about "
            "Massachusetts General Hospital's Psychiatry department, including "
            "patient reviews, quality metrics, and news coverage. The data sources "
            "and search queries are provided to enable verification and further research.",
        )

        sources_used = []

        # Add review section
        review_platforms = self.review_aggregator.get_platform_info()
        sources_used.extend([p["name"] for p in review_platforms])
        report.add_section(
            "Patient & Provider Reviews",
            self.collected_data["reviews"],
            summary="Information from major healthcare review platforms. "
            "These sources provide patient feedback and provider ratings.",
        )

        # Add quality metrics section
        quality_sources = self.quality_collector.get_available_sources()
        sources_used.extend([s["name"] for s in quality_sources])
        report.add_section(
            "Quality Metrics & Ratings",
            self.collected_data["quality_metrics"],
            summary="Quality data from official healthcare rating organizations "
            "and accreditation bodies.",
        )

        # Add psychiatry-specific metrics info
        psych_metrics = self.quality_collector.get_psychiatry_metrics()
        report.set_metadata("psychiatry_metrics_tracked", psych_metrics)

        # Add news section
        news_sources = self.news_collector.get_source_info()
        sources_used.extend([s["name"] for s in news_sources])
        report.add_section(
            "News & Media Coverage",
            self.collected_data["news"],
            summary="News articles, press releases, and media coverage.",
        )

        report.set_metadata("sources_used", list(set(sources_used)))
        report.set_metadata("search_term", self.collected_data["search_term"])
        report.set_metadata("alternative_search_terms", self.ALTERNATIVE_TERMS)

        # Save report
        saved_files = report.save(self.output_dir, formats)

        print(f"\nReport generated:")
        for f in saved_files:
            print(f"  - {f}")

        return saved_files

    def get_search_queries(self) -> dict[str, list[str]]:
        """Get all search queries that would be used for data collection.

        Returns:
            Dictionary mapping source types to their search queries.
        """
        queries = {
            "reviews": [],
            "quality": [],
            "news": [],
        }

        for item in self.collected_data.get("reviews", []):
            if "search_query" in item.metadata:
                queries["reviews"].append(item.metadata["search_query"])

        for item in self.collected_data.get("quality_metrics", []):
            if "search_query" in item.metadata:
                queries["quality"].append(item.metadata["search_query"])

        for item in self.collected_data.get("news", []):
            if "search_queries" in item.metadata:
                queries["news"].extend(item.metadata["search_queries"])

        return queries

    def print_summary(self) -> None:
        """Print a summary of available data sources."""
        print("\n" + "=" * 60)
        print("MASS GENERAL PSYCHIATRY INFORMATION AGGREGATOR")
        print("=" * 60)

        print("\n📋 REVIEW PLATFORMS:")
        for platform in self.review_aggregator.get_platform_info():
            print(f"  • {platform['name']}: {platform['description']}")

        print("\n📊 QUALITY DATA SOURCES:")
        for source in self.quality_collector.get_available_sources():
            print(f"  • {source['name']}: {source['description']}")

        print("\n📰 NEWS SOURCES:")
        for source in self.news_collector.get_source_info():
            print(f"  • {source['name']}: {source['description']}")

        print("\n🔍 PSYCHIATRY-SPECIFIC METRICS TRACKED:")
        for metric in self.quality_collector.get_psychiatry_metrics()[:5]:
            print(f"  • {metric}")
        print("  • ...")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Aggregate information about Mass General Psychiatry from online sources"
    )
    parser.add_argument(
        "--search-term",
        "-s",
        default=None,
        help="Custom search term (default: Massachusetts General Hospital Psychiatry)",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json", "both"],
        default="both",
        help="Output format (default: both)",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary of available data sources and exit",
    )

    args = parser.parse_args()

    aggregator = MassGeneralPsychiatryAggregator(output_dir=args.output_dir)

    if args.summary:
        aggregator.print_summary()
        return 0

    # Collect data
    aggregator.collect_all(search_term=args.search_term)

    # Determine formats
    formats = None
    if args.format == "markdown":
        formats = ["markdown"]
    elif args.format == "json":
        formats = ["json"]

    # Generate report
    aggregator.generate_report(formats=formats)

    return 0


if __name__ == "__main__":
    sys.exit(main())
