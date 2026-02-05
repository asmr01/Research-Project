"""Report generation for aggregated healthcare data."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .sources.base import DataItem


@dataclass
class ReportSection:
    """A section of the report."""

    title: str
    content: str
    items: list[dict[str, Any]]
    summary: str = ""


class ReportGenerator:
    """Generates formatted reports from aggregated data."""

    def __init__(self, institution_name: str):
        self.institution_name = institution_name
        self.sections: list[ReportSection] = []
        self.generated_at = datetime.now()
        self.metadata: dict[str, Any] = {}

    def add_section(
        self,
        title: str,
        items: list[DataItem],
        summary: str = "",
    ) -> None:
        """Add a section to the report.

        Args:
            title: Section title.
            items: List of DataItem objects for this section.
            summary: Optional summary text for the section.
        """
        section = ReportSection(
            title=title,
            content="",
            items=[item.to_dict() for item in items],
            summary=summary,
        )
        self.sections.append(section)

    def add_web_results(
        self,
        title: str,
        results: list[dict[str, Any]],
        summary: str = "",
    ) -> None:
        """Add web search results as a section.

        Args:
            title: Section title.
            results: List of web search results.
            summary: Optional summary text.
        """
        section = ReportSection(
            title=title,
            content="",
            items=results,
            summary=summary,
        )
        self.sections.append(section)

    def set_metadata(self, key: str, value: Any) -> None:
        """Set metadata for the report."""
        self.metadata[key] = value

    def generate_markdown(self) -> str:
        """Generate a Markdown-formatted report.

        Returns:
            Markdown string of the report.
        """
        lines = []

        # Header
        lines.append(f"# {self.institution_name} - Information Report")
        lines.append("")
        lines.append(f"**Generated:** {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Table of contents
        lines.append("## Table of Contents")
        lines.append("")
        for i, section in enumerate(self.sections, 1):
            anchor = section.title.lower().replace(" ", "-").replace("/", "")
            lines.append(f"{i}. [{section.title}](#{anchor})")
        lines.append("")

        # Executive Summary
        if self.metadata.get("executive_summary"):
            lines.append("## Executive Summary")
            lines.append("")
            lines.append(self.metadata["executive_summary"])
            lines.append("")

        # Sections
        for section in self.sections:
            lines.append(f"## {section.title}")
            lines.append("")

            if section.summary:
                lines.append(section.summary)
                lines.append("")

            if section.items:
                for item in section.items:
                    self._format_item(lines, item)

            lines.append("")

        # Methodology note
        lines.append("---")
        lines.append("")
        lines.append("## Methodology")
        lines.append("")
        lines.append(
            "This report was compiled by aggregating publicly available information "
            "from various healthcare data sources, review platforms, and news outlets. "
            "Data accuracy depends on source reliability and currency."
        )
        lines.append("")

        # Sources list
        if self.metadata.get("sources_used"):
            lines.append("### Sources Consulted")
            lines.append("")
            for source in self.metadata["sources_used"]:
                lines.append(f"- {source}")
            lines.append("")

        return "\n".join(lines)

    def _format_item(self, lines: list[str], item: dict[str, Any]) -> None:
        """Format a single data item for the report."""
        if "title" in item:
            lines.append(f"### {item.get('title', 'Untitled')}")
            lines.append("")

        if "source" in item:
            source_url = item.get("source_url", "")
            if source_url:
                lines.append(f"**Source:** [{item['source']}]({source_url})")
            else:
                lines.append(f"**Source:** {item['source']}")
            lines.append("")

        if "content" in item:
            lines.append(item["content"])
            lines.append("")

        if "metadata" in item and item["metadata"]:
            meta = item["metadata"]
            if "rating" in meta:
                lines.append(f"**Rating:** {meta['rating']}")
            if "review_count" in meta:
                lines.append(f"**Reviews:** {meta['review_count']}")
            if "search_query" in meta:
                lines.append(f"*Search query: {meta['search_query']}*")
            lines.append("")

    def generate_json(self) -> str:
        """Generate a JSON-formatted report.

        Returns:
            JSON string of the report.
        """
        report_data = {
            "institution": self.institution_name,
            "generated_at": self.generated_at.isoformat(),
            "metadata": self.metadata,
            "sections": [
                {
                    "title": section.title,
                    "summary": section.summary,
                    "items": section.items,
                }
                for section in self.sections
            ],
        }
        return json.dumps(report_data, indent=2)

    def save(self, output_dir: str | Path, formats: list[str] | None = None) -> list[Path]:
        """Save the report to files.

        Args:
            output_dir: Directory to save reports to.
            formats: List of formats to generate ('markdown', 'json'). Defaults to both.

        Returns:
            List of paths to saved files.
        """
        if formats is None:
            formats = ["markdown", "json"]

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = self.generated_at.strftime("%Y%m%d_%H%M%S")
        base_name = f"report_{self.institution_name.lower().replace(' ', '_')}_{timestamp}"

        saved_files = []

        if "markdown" in formats:
            md_path = output_path / f"{base_name}.md"
            md_path.write_text(self.generate_markdown())
            saved_files.append(md_path)

        if "json" in formats:
            json_path = output_path / f"{base_name}.json"
            json_path.write_text(self.generate_json())
            saved_files.append(json_path)

        return saved_files
