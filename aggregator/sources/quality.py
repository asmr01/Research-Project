"""Quality metrics collection from official healthcare data sources."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import DataItem, DataSource


@dataclass
class QualityMetric:
    """A single quality metric."""

    name: str
    value: str | float
    benchmark: str | float | None
    source: str
    description: str
    period: str | None = None


class QualityMetricsCollector(DataSource):
    """Collects quality metrics from official healthcare data sources."""

    # Official quality data sources
    QUALITY_SOURCES = {
        "cms_hospital_compare": {
            "name": "CMS Hospital Compare",
            "url": "https://www.medicare.gov/care-compare/",
            "description": "Official Medicare quality ratings and measures",
            "metrics": [
                "Overall hospital rating",
                "Patient experience",
                "Timely and effective care",
                "Readmission rates",
                "Safety of care",
            ],
        },
        "us_news": {
            "name": "U.S. News & World Report",
            "url": "https://health.usnews.com/best-hospitals",
            "description": "Hospital and specialty rankings",
            "metrics": [
                "Best Hospitals ranking",
                "Psychiatry specialty ranking",
                "Patient outcomes",
                "Patient safety",
            ],
        },
        "leapfrog": {
            "name": "Leapfrog Hospital Safety Grade",
            "url": "https://www.hospitalsafetygrade.org/",
            "description": "Hospital safety ratings (A-F grades)",
            "metrics": [
                "Overall safety grade",
                "Infection rates",
                "Problems with surgery",
                "Practices to prevent errors",
            ],
        },
        "joint_commission": {
            "name": "The Joint Commission",
            "url": "https://www.qualitycheck.org/",
            "description": "Accreditation and quality certification",
            "metrics": [
                "Accreditation status",
                "Certification programs",
                "Performance measures",
            ],
        },
        "samhsa": {
            "name": "SAMHSA Treatment Locator",
            "url": "https://findtreatment.samhsa.gov/",
            "description": "Substance abuse and mental health services information",
            "metrics": [
                "Treatment services offered",
                "Payment options",
                "Special programs",
            ],
        },
        "nami": {
            "name": "NAMI (National Alliance on Mental Illness)",
            "url": "https://www.nami.org/",
            "description": "Mental health resources and provider information",
            "metrics": [
                "Provider listings",
                "Program information",
                "Community feedback",
            ],
        },
    }

    # Psychiatry-specific metrics to look for
    PSYCHIATRY_METRICS = [
        "Inpatient psychiatric care quality",
        "Outpatient mental health services",
        "Suicide risk assessment protocols",
        "Patient satisfaction in behavioral health",
        "Average length of stay - psychiatric",
        "Readmission rates - psychiatric",
        "Follow-up after hospitalization for mental illness",
        "Screening for clinical depression",
        "Antidepressant medication management",
        "ADHD medication follow-up",
        "Substance use disorder treatment",
        "Crisis intervention availability",
        "Telepsychiatry services",
    ]

    def __init__(self):
        super().__init__("Quality Metrics Collector")
        self.metrics: list[QualityMetric] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect quality metrics data for the given institution.

        Args:
            search_term: Institution to search for.

        Returns:
            List of DataItem objects with quality metrics information.
        """
        self.items = []

        # Generate data items for each quality source
        for source_id, source_info in self.QUALITY_SOURCES.items():
            metrics_desc = ", ".join(source_info["metrics"][:3])
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Quality metrics: {search_term}",
                content=f"Quality data from {source_info['name']}: {source_info['description']}. Key metrics: {metrics_desc}",
                metadata={
                    "source_id": source_id,
                    "available_metrics": source_info["metrics"],
                    "search_query": self._build_search_query(search_term, source_id),
                },
            )
            self.items.append(item)

        # Add psychiatry-specific metrics item
        psych_item = DataItem(
            source="Psychiatry Quality Metrics",
            source_url="",
            title=f"Psychiatry-specific metrics for {search_term}",
            content="Behavioral health and psychiatry quality indicators to search for",
            metadata={
                "metrics_to_find": self.PSYCHIATRY_METRICS,
                "category": "psychiatry_specific",
            },
        )
        self.items.append(psych_item)

        return self.items

    def _build_search_query(self, search_term: str, source_id: str) -> str:
        """Build a search query for the given source."""
        source_info = self.QUALITY_SOURCES[source_id]

        if source_id == "cms_hospital_compare":
            return f"site:medicare.gov {search_term} hospital quality"
        elif source_id == "us_news":
            return f"site:health.usnews.com {search_term} ranking"
        elif source_id == "leapfrog":
            return f"site:hospitalsafetygrade.org {search_term}"
        elif source_id == "joint_commission":
            return f"site:qualitycheck.org {search_term}"
        else:
            return f"{search_term} {source_info['name']} quality"

    def get_available_sources(self) -> list[dict[str, Any]]:
        """Get information about available quality data sources."""
        return [
            {
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "metrics": info["metrics"],
            }
            for source_id, info in self.QUALITY_SOURCES.items()
        ]

    def get_psychiatry_metrics(self) -> list[str]:
        """Get list of psychiatry-specific metrics to track."""
        return self.PSYCHIATRY_METRICS.copy()
