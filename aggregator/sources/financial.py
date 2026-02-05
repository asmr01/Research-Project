"""Financial and operational information collection for healthcare institutions."""

from dataclasses import dataclass
from typing import Any

from .base import DataItem, DataSource


@dataclass
class FinancialMetric:
    """A financial or operational metric."""

    name: str
    value: str | float | None
    period: str
    source: str
    category: str
    notes: str = ""


class FinancialOperationalCollector(DataSource):
    """Collects financial and operational data about healthcare institutions.

    This includes revenue, operating margins, patient volumes, staffing data,
    and other operational metrics from public filings and reports.
    """

    # Public financial data sources
    FINANCIAL_SOURCES = {
        "form_990": {
            "name": "IRS Form 990",
            "url": "https://projects.propublica.org/nonprofits/",
            "description": "Tax filings for nonprofit hospitals (via ProPublica)",
            "metrics": [
                "Total revenue",
                "Total expenses",
                "Net assets",
                "Executive compensation",
                "Program expenses",
                "Fundraising expenses",
            ],
        },
        "cms_cost_reports": {
            "name": "CMS Hospital Cost Reports",
            "url": "https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/Cost-Reports",
            "description": "Medicare cost reports with detailed financial data",
            "metrics": [
                "Operating costs",
                "Patient revenue",
                "Charity care",
                "Bad debt",
                "Medicare/Medicaid mix",
            ],
        },
        "state_filings": {
            "name": "Massachusetts Health Policy Commission",
            "url": "https://www.mass.gov/orgs/health-policy-commission",
            "description": "State-required hospital financial filings",
            "metrics": [
                "Operating margin",
                "Total margin",
                "Days cash on hand",
                "Community benefits",
            ],
        },
        "charity_navigator": {
            "name": "Charity Navigator",
            "url": "https://www.charitynavigator.org/",
            "description": "Nonprofit ratings and financial health scores",
            "metrics": [
                "Overall score",
                "Financial health",
                "Accountability",
                "Program expenses ratio",
            ],
        },
        "guidestar": {
            "name": "GuideStar/Candid",
            "url": "https://www.guidestar.org/",
            "description": "Nonprofit organization data and financials",
            "metrics": [
                "Revenue trends",
                "Expense breakdown",
                "Leadership compensation",
            ],
        },
    }

    # Operational data sources
    OPERATIONAL_SOURCES = {
        "cms_hospital_data": {
            "name": "CMS Hospital General Information",
            "url": "https://data.cms.gov/",
            "description": "Hospital operational data from CMS",
            "metrics": [
                "Bed count",
                "Hospital type",
                "Ownership",
                "Emergency services",
            ],
        },
        "aha_data": {
            "name": "American Hospital Association",
            "url": "https://www.aha.org/",
            "description": "Hospital statistics and operational data",
            "metrics": [
                "Staffed beds",
                "Admissions",
                "Outpatient visits",
                "FTE employees",
                "Average length of stay",
            ],
        },
        "dartmouth_atlas": {
            "name": "Dartmouth Atlas of Health Care",
            "url": "https://www.dartmouthatlas.org/",
            "description": "Healthcare utilization and spending data",
            "metrics": [
                "Spending per patient",
                "Hospital days per capita",
                "Physician supply",
                "Care variation",
            ],
        },
        "hcahps": {
            "name": "HCAHPS Survey Results",
            "url": "https://www.medicare.gov/care-compare/",
            "description": "Patient experience survey scores",
            "metrics": [
                "Overall rating",
                "Communication scores",
                "Responsiveness",
                "Cleanliness",
                "Quietness",
            ],
        },
    }

    # News and analysis sources for financial/operational info
    NEWS_SOURCES = {
        "becker": {
            "name": "Becker's Hospital Review",
            "url": "https://www.beckershospitalreview.com/",
            "description": "Healthcare business news and financial analysis",
            "topics": [
                "Hospital finances",
                "M&A activity",
                "Executive moves",
                "Operational changes",
            ],
        },
        "modern_healthcare": {
            "name": "Modern Healthcare",
            "url": "https://www.modernhealthcare.com/",
            "description": "Healthcare business and policy news",
            "topics": [
                "Financial performance",
                "Industry trends",
                "Policy impacts",
            ],
        },
        "healthcare_dive": {
            "name": "Healthcare Dive",
            "url": "https://www.healthcaredive.com/",
            "description": "Healthcare industry news and analysis",
            "topics": [
                "Financial news",
                "Operational updates",
                "Market analysis",
            ],
        },
        "fierce_healthcare": {
            "name": "Fierce Healthcare",
            "url": "https://www.fiercehealthcare.com/",
            "description": "Healthcare business intelligence",
            "topics": [
                "Payer news",
                "Provider operations",
                "Financial trends",
            ],
        },
        "advisory_board": {
            "name": "Advisory Board",
            "url": "https://www.advisory.com/",
            "description": "Healthcare research and consulting insights",
            "topics": [
                "Best practices",
                "Benchmarking",
                "Strategic insights",
            ],
        },
    }

    # Psychiatry-specific operational metrics
    PSYCHIATRY_METRICS = [
        "Psychiatric bed count",
        "Average length of stay - psychiatric",
        "Psychiatric admissions",
        "Outpatient mental health visits",
        "Emergency psychiatric evaluations",
        "Telepsychiatry utilization",
        "Psychiatric readmission rates",
        "Staff-to-patient ratios (psychiatric)",
        "Psychiatrist FTEs",
        "Psychologist FTEs",
        "Social worker FTEs",
        "Psychiatric nurse FTEs",
    ]

    def __init__(self):
        super().__init__("Financial & Operational Collector")
        self.metrics: list[FinancialMetric] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect financial and operational data for the given institution.

        Args:
            search_term: Institution to search for.

        Returns:
            List of DataItem objects with financial/operational information.
        """
        self.items = []

        # Collect from financial sources
        for source_id, source_info in self.FINANCIAL_SOURCES.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Financial data: {search_term}",
                content=f"Financial information from {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "financial",
                    "metrics": source_info["metrics"],
                    "search_query": self._build_search_query(search_term, source_id, "financial"),
                },
            )
            self.items.append(item)

        # Collect from operational sources
        for source_id, source_info in self.OPERATIONAL_SOURCES.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Operational data: {search_term}",
                content=f"Operational data from {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "operational",
                    "metrics": source_info["metrics"],
                    "search_query": self._build_search_query(search_term, source_id, "operational"),
                },
            )
            self.items.append(item)

        # Collect from news/analysis sources
        for source_id, source_info in self.NEWS_SOURCES.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Financial news: {search_term}",
                content=f"Business news from {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "news",
                    "topics": source_info["topics"],
                    "search_queries": self._build_news_queries(search_term, source_id),
                },
            )
            self.items.append(item)

        # Add psychiatry-specific metrics item
        psych_item = DataItem(
            source="Psychiatry Operational Metrics",
            source_url="",
            title=f"Psychiatry operations: {search_term}",
            content="Behavioral health and psychiatry operational indicators",
            metadata={
                "source_type": "psychiatry_specific",
                "metrics_to_find": self.PSYCHIATRY_METRICS,
            },
        )
        self.items.append(psych_item)

        return self.items

    def _build_search_query(self, search_term: str, source_id: str, source_type: str) -> str:
        """Build a search query for financial/operational sources."""
        # Use Mass General Brigham as the parent organization for financial data
        org_names = [
            "Massachusetts General Hospital",
            "Mass General Brigham",
            "Partners HealthCare",  # Former name
        ]

        if source_type == "financial":
            query_templates = {
                "form_990": "site:projects.propublica.org Massachusetts General Hospital 990",
                "cms_cost_reports": "Massachusetts General Hospital CMS cost report",
                "state_filings": "site:mass.gov Massachusetts General Hospital financial report",
                "charity_navigator": "site:charitynavigator.org Mass General Brigham",
                "guidestar": "site:guidestar.org Massachusetts General Hospital",
            }
        else:  # operational
            query_templates = {
                "cms_hospital_data": "site:data.cms.gov Massachusetts General Hospital",
                "aha_data": "Massachusetts General Hospital AHA statistics",
                "dartmouth_atlas": "site:dartmouthatlas.org Massachusetts General Hospital",
                "hcahps": "Massachusetts General Hospital HCAHPS scores",
            }

        return query_templates.get(source_id, f"{search_term} {source_id}")

    def _build_news_queries(self, search_term: str, source_id: str) -> list[str]:
        """Build search queries for financial/business news sources."""
        base_queries = []

        site_domains = {
            "becker": "beckershospitalreview.com",
            "modern_healthcare": "modernhealthcare.com",
            "healthcare_dive": "healthcaredive.com",
            "fierce_healthcare": "fiercehealthcare.com",
            "advisory_board": "advisory.com",
        }

        domain = site_domains.get(source_id, "")

        if domain:
            base_queries = [
                f"site:{domain} Massachusetts General Hospital",
                f"site:{domain} Mass General Brigham",
                f"site:{domain} MGH",
            ]
        else:
            base_queries = [
                f"{search_term} financial news",
                f"{search_term} operating margin",
            ]

        # Add topic-specific queries
        base_queries.extend([
            f"Massachusetts General Hospital revenue 2024",
            f"Mass General Brigham financial performance",
            f"MGH psychiatry expansion investment",
        ])

        return base_queries

    def get_financial_metrics_to_track(self) -> list[str]:
        """Get list of key financial metrics to track."""
        return [
            "Total operating revenue",
            "Total operating expenses",
            "Operating margin",
            "Net patient revenue",
            "Charity care (as % of expenses)",
            "Bad debt expense",
            "Days cash on hand",
            "Current ratio",
            "Debt-to-capitalization",
            "Executive compensation",
            "Community benefit spending",
        ]

    def get_operational_metrics_to_track(self) -> list[str]:
        """Get list of key operational metrics to track."""
        return [
            "Licensed beds",
            "Staffed beds",
            "Average daily census",
            "Total admissions",
            "Outpatient visits",
            "Emergency department visits",
            "Average length of stay",
            "Occupancy rate",
            "Case mix index",
            "FTE employees",
            "Nurse-to-patient ratio",
        ]

    def get_psychiatry_metrics(self) -> list[str]:
        """Get psychiatry-specific operational metrics."""
        return self.PSYCHIATRY_METRICS.copy()

    def get_source_info(self) -> list[dict[str, Any]]:
        """Get information about all data sources."""
        sources = []

        for source_id, info in self.FINANCIAL_SOURCES.items():
            sources.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "financial",
                "metrics": info["metrics"],
            })

        for source_id, info in self.OPERATIONAL_SOURCES.items():
            sources.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "operational",
                "metrics": info["metrics"],
            })

        for source_id, info in self.NEWS_SOURCES.items():
            sources.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "news",
                "topics": info["topics"],
            })

        return sources
