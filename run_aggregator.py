#!/usr/bin/env python3
"""
Mass General Psychiatry Information Aggregator

A tool to collect and compile information about Massachusetts General Hospital's
Psychiatry department from various online sources including:
- Patient and provider reviews
- Quality metrics and ratings
- News and media coverage

Usage:
    python run_aggregator.py                    # Run full aggregation
    python run_aggregator.py --summary          # Show available data sources
    python run_aggregator.py --queries          # Show search queries
    python run_aggregator.py --live             # Perform live web searches
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from aggregator.main import MassGeneralPsychiatryAggregator
from aggregator.web_search import WebSearchManager


def run_summary():
    """Print summary of available data sources."""
    aggregator = MassGeneralPsychiatryAggregator()
    aggregator.print_summary()


def show_search_queries():
    """Display all search queries that would be used."""
    search_manager = WebSearchManager()
    queries = search_manager.get_search_queries()

    print("\n" + "=" * 60)
    print("SEARCH QUERIES FOR MASS GENERAL PSYCHIATRY")
    print("=" * 60)

    for category, query_list in queries.items():
        print(f"\n📌 {category.upper().replace('_', ' ')}")
        print("-" * 40)
        for i, query in enumerate(query_list, 1):
            print(f"  {i}. {query}")

    print("\n" + "=" * 60)


def run_aggregation(output_dir: str = "reports", formats: list[str] | None = None):
    """Run the full aggregation process."""
    aggregator = MassGeneralPsychiatryAggregator(output_dir=output_dir)

    print("\n" + "=" * 60)
    print("STARTING DATA AGGREGATION")
    print("=" * 60 + "\n")

    # Collect data
    aggregator.collect_all()

    # Generate report
    saved_files = aggregator.generate_report(formats=formats)

    print("\n" + "=" * 60)
    print("AGGREGATION COMPLETE")
    print("=" * 60)

    return saved_files


def generate_live_search_report():
    """Generate a report template with live search instructions."""
    search_manager = WebSearchManager()
    urls = search_manager.build_search_urls()

    report_lines = [
        "# Mass General Psychiatry - Live Search Guide",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## How to Use This Guide",
        "",
        "This guide provides pre-built search queries to find information about",
        "Massachusetts General Hospital's Psychiatry department. Click the links",
        "or copy the queries into your preferred search engine.",
        "",
    ]

    for category, query_data in urls.items():
        report_lines.append(f"## {category.replace('_', ' ').title()}")
        report_lines.append("")

        for item in query_data:
            report_lines.append(f"### Query: {item['query']}")
            report_lines.append(f"[Search Google]({item['url']})")
            report_lines.append("")

    # Save the guide
    output_path = Path("reports/live_search_guide.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines))

    print(f"\nLive search guide saved to: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Mass General Psychiatry Information Aggregator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_aggregator.py                 Run full aggregation
  python run_aggregator.py --summary       Show data source summary
  python run_aggregator.py --queries       Show all search queries
  python run_aggregator.py --live          Generate live search guide
  python run_aggregator.py -o ./output     Save reports to ./output
        """,
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary of available data sources",
    )
    parser.add_argument(
        "--queries",
        action="store_true",
        help="Display all search queries",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Generate live search guide with clickable links",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="reports",
        help="Output directory for reports (default: reports)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["markdown", "json", "both"],
        default="both",
        help="Output format (default: both)",
    )

    args = parser.parse_args()

    if args.summary:
        run_summary()
        return 0

    if args.queries:
        show_search_queries()
        return 0

    if args.live:
        generate_live_search_report()
        return 0

    # Default: run full aggregation
    formats = None
    if args.format == "markdown":
        formats = ["markdown"]
    elif args.format == "json":
        formats = ["json"]

    run_aggregation(output_dir=args.output, formats=formats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
