"""Employee and provider review aggregation from workplace review platforms."""

import re
from dataclasses import dataclass
from typing import Any

from .base import DataItem, DataSource


@dataclass
class EmployeeReviewSummary:
    """Summary of employee reviews from a source."""

    source_name: str
    source_url: str
    overall_rating: float | None
    total_reviews: int
    recommend_to_friend_pct: float | None
    ceo_approval_pct: float | None
    pros: list[str]
    cons: list[str]
    ratings_breakdown: dict[str, float]  # e.g., work-life balance, compensation, etc.


class EmployeeReviewAggregator(DataSource):
    """Aggregates employee and provider reviews from workplace review platforms.

    This covers reviews from healthcare workers including doctors, nurses,
    psychiatrists, therapists, administrative staff, and other employees.
    """

    # General workplace review platforms
    WORKPLACE_PLATFORMS = {
        "glassdoor": {
            "name": "Glassdoor",
            "url": "https://www.glassdoor.com/",
            "description": "Employee reviews, salaries, and company insights",
            "metrics": [
                "Overall rating",
                "Work-life balance",
                "Culture & values",
                "Career opportunities",
                "Compensation & benefits",
                "Senior management",
            ],
        },
        "indeed": {
            "name": "Indeed Company Reviews",
            "url": "https://www.indeed.com/cmp",
            "description": "Employee reviews and salary information",
            "metrics": [
                "Overall rating",
                "Work-life balance",
                "Pay & benefits",
                "Job security",
                "Management",
            ],
        },
        "linkedin": {
            "name": "LinkedIn",
            "url": "https://www.linkedin.com/",
            "description": "Professional network with company insights and employee perspectives",
            "metrics": [
                "Employee count",
                "Growth trends",
                "Employee testimonials",
            ],
        },
        "comparably": {
            "name": "Comparably",
            "url": "https://www.comparably.com/",
            "description": "Workplace culture and compensation data",
            "metrics": [
                "Culture score",
                "CEO rating",
                "Diversity score",
                "Compensation",
                "Work-life balance",
            ],
        },
        "fairygodboss": {
            "name": "Fairygodboss",
            "url": "https://fairygodboss.com/",
            "description": "Women's workplace reviews and ratings",
            "metrics": [
                "Overall rating",
                "Women's satisfaction",
                "Maternity leave",
                "Flexibility",
            ],
        },
        "inhersight": {
            "name": "InHerSight",
            "url": "https://www.inhersight.com/",
            "description": "Women-focused workplace ratings and reviews",
            "metrics": [
                "Overall score",
                "Equal opportunities",
                "Paid time off",
                "Management",
            ],
        },
    }

    # Healthcare-specific employee review platforms
    HEALTHCARE_PLATFORMS = {
        "nurse_reviews": {
            "name": "Nurse.org / NurseRecruiter",
            "url": "https://nurse.org/",
            "description": "Nursing job reviews and hospital ratings for nurses",
            "roles": ["RN", "LPN", "NP", "Psychiatric Nurse"],
            "metrics": [
                "Nurse satisfaction",
                "Staffing ratios",
                "Management support",
                "Work environment",
            ],
        },
        "doximity": {
            "name": "Doximity",
            "url": "https://www.doximity.com/",
            "description": "Physician network with residency and employer reviews",
            "roles": ["Physician", "Psychiatrist", "Resident"],
            "metrics": [
                "Residency rankings",
                "Work-life balance",
                "Compensation",
                "Teaching quality",
            ],
        },
        "medscape": {
            "name": "Medscape Physician Compensation",
            "url": "https://www.medscape.com/",
            "description": "Physician salary reports and career satisfaction surveys",
            "roles": ["Physician", "Psychiatrist", "Specialist"],
            "metrics": [
                "Compensation data",
                "Burnout rates",
                "Career satisfaction",
            ],
        },
        "sermo": {
            "name": "Sermo",
            "url": "https://www.sermo.com/",
            "description": "Physician community with workplace discussions",
            "roles": ["Physician", "Specialist"],
            "metrics": [
                "Peer discussions",
                "Practice insights",
            ],
        },
        "allnurses": {
            "name": "AllNurses",
            "url": "https://allnurses.com/",
            "description": "Nursing community forum with hospital reviews",
            "roles": ["RN", "LPN", "CNA", "NP", "Psychiatric Nurse"],
            "metrics": [
                "Hospital reviews",
                "Work environment",
                "Management feedback",
            ],
        },
        "studentdoctor": {
            "name": "Student Doctor Network",
            "url": "https://www.studentdoctor.net/",
            "description": "Medical student and resident forums with program reviews",
            "roles": ["Medical Student", "Resident", "Fellow"],
            "metrics": [
                "Residency reviews",
                "Program quality",
                "Training experience",
            ],
        },
        "reddit_medicine": {
            "name": "Reddit Medical Communities",
            "url": "https://www.reddit.com/",
            "description": "Healthcare worker discussions on Reddit",
            "subreddits": [
                "r/medicine",
                "r/nursing",
                "r/Residency",
                "r/medicalschool",
                "r/psychiatry",
                "r/psychotherapy",
                "r/socialwork",
            ],
            "roles": ["All healthcare workers"],
        },
    }

    def __init__(self):
        super().__init__("Employee Review Aggregator")
        self.summaries: list[EmployeeReviewSummary] = []

    def collect(self, search_term: str) -> list[DataItem]:
        """Collect employee review data for the given institution.

        Args:
            search_term: Institution to search for.

        Returns:
            List of DataItem objects with employee review information.
        """
        self.items = []

        # Collect from general workplace platforms
        for source_id, source_info in self.WORKPLACE_PLATFORMS.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Employee reviews: {search_term}",
                content=f"Workplace reviews on {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "workplace_platform",
                    "metrics": source_info["metrics"],
                    "search_query": self._build_search_query(search_term, source_id),
                },
            )
            self.items.append(item)

        # Collect from healthcare-specific platforms
        for source_id, source_info in self.HEALTHCARE_PLATFORMS.items():
            item = DataItem(
                source=source_info["name"],
                source_url=source_info["url"],
                title=f"Healthcare worker reviews: {search_term}",
                content=f"Reviews on {source_info['name']}: {source_info['description']}",
                metadata={
                    "source_id": source_id,
                    "source_type": "healthcare_platform",
                    "roles": source_info.get("roles", []),
                    "search_queries": self._build_healthcare_queries(search_term, source_id),
                },
            )
            self.items.append(item)

        return self.items

    def _build_search_query(self, search_term: str, source_id: str) -> str:
        """Build a search query for workplace review platforms."""
        # Institution variations
        variations = [
            "Massachusetts General Hospital",
            "Mass General",
            "MGH",
            "Mass General Brigham",
        ]

        query_templates = {
            "glassdoor": f"site:glassdoor.com Massachusetts General Hospital reviews",
            "indeed": f"site:indeed.com/cmp Massachusetts General Hospital reviews",
            "linkedin": f"site:linkedin.com/company Massachusetts General Hospital",
            "comparably": f"site:comparably.com Massachusetts General Hospital",
            "fairygodboss": f"site:fairygodboss.com Massachusetts General Hospital",
            "inhersight": f"site:inhersight.com Massachusetts General Hospital",
        }

        return query_templates.get(source_id, f"{search_term} employee reviews")

    def _build_healthcare_queries(self, search_term: str, source_id: str) -> list[str]:
        """Build search queries for healthcare-specific platforms."""
        base_queries = []

        if source_id == "nurse_reviews":
            base_queries = [
                "Massachusetts General Hospital nurse reviews",
                "MGH nursing jobs reviews",
                "Mass General psychiatric nurse experience",
                "site:nurse.org Massachusetts General",
            ]
        elif source_id == "doximity":
            base_queries = [
                "site:doximity.com Massachusetts General Hospital",
                "MGH psychiatry residency reviews",
                "Mass General physician reviews",
            ]
        elif source_id == "medscape":
            base_queries = [
                "Massachusetts General Hospital psychiatrist salary",
                "MGH physician compensation",
            ]
        elif source_id == "allnurses":
            base_queries = [
                "site:allnurses.com Massachusetts General Hospital",
                "site:allnurses.com MGH",
                "site:allnurses.com Mass General nursing",
            ]
        elif source_id == "studentdoctor":
            base_queries = [
                "site:studentdoctor.net Massachusetts General Hospital",
                "site:studentdoctor.net MGH psychiatry residency",
                "site:studentdoctor.net Mass General",
            ]
        elif source_id == "reddit_medicine":
            subreddits = self.HEALTHCARE_PLATFORMS["reddit_medicine"]["subreddits"]
            base_queries = [f"site:reddit.com/{sub} Mass General" for sub in subreddits[:4]]
            base_queries.extend([
                "site:reddit.com/r/medicine MGH",
                "site:reddit.com/r/nursing Massachusetts General Hospital",
                "site:reddit.com/r/Residency MGH psychiatry",
            ])
        else:
            base_queries = [f"{search_term} {source_id} reviews"]

        return base_queries

    def get_role_specific_queries(self, role: str) -> list[str]:
        """Get search queries specific to a healthcare role.

        Args:
            role: Healthcare role (e.g., "nurse", "psychiatrist", "resident").

        Returns:
            List of role-specific search queries.
        """
        role_queries = {
            "nurse": [
                "Massachusetts General Hospital nurse reviews Glassdoor",
                "MGH nursing staff experience",
                "Mass General psychiatric nurse jobs reviews",
                "site:allnurses.com MGH",
            ],
            "psychiatrist": [
                "Massachusetts General Hospital psychiatrist reviews",
                "MGH psychiatry department work environment",
                "Mass General psychiatrist Glassdoor",
                "site:doximity.com MGH psychiatry",
            ],
            "resident": [
                "MGH psychiatry residency reviews",
                "Massachusetts General Hospital residency experience",
                "site:studentdoctor.net MGH psychiatry",
                "Mass General residency pros cons",
            ],
            "therapist": [
                "Massachusetts General Hospital therapist reviews",
                "MGH social worker experience",
                "Mass General behavioral health therapist",
            ],
            "administrative": [
                "Massachusetts General Hospital administrative staff reviews",
                "MGH front desk receptionist reviews Glassdoor",
                "Mass General hospital administration jobs",
            ],
        }

        return role_queries.get(role.lower(), [f"Massachusetts General Hospital {role} reviews"])

    def parse_rating(self, rating_text: str) -> float | None:
        """Parse a rating from text format."""
        patterns = [
            r"(\d+\.?\d*)\s*(?:out of|/)\s*5",
            r"(\d+\.?\d*)\s*stars?",
            r"rating[:\s]+(\d+\.?\d*)",
            r"(\d+)%\s*(?:recommend|approval)",
        ]

        for pattern in patterns:
            match = re.search(pattern, rating_text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    # Convert percentage to 5-point scale if needed
                    if value > 5:
                        value = value / 20  # Convert 100% scale to 5-point
                    return value
                except ValueError:
                    continue
        return None

    def extract_themes(self, reviews: list[str]) -> tuple[list[str], list[str]]:
        """Extract common positive and negative themes from employee reviews."""
        positive_keywords = [
            "great benefits", "good work-life balance", "collaborative",
            "learning opportunities", "supportive management", "prestigious",
            "cutting-edge", "research opportunities", "professional development",
            "job security", "mission-driven", "meaningful work", "great colleagues",
            "good compensation", "teaching hospital", "academic environment",
        ]

        negative_keywords = [
            "long hours", "burnout", "understaffed", "bureaucratic",
            "poor management", "low pay", "high turnover", "stressful",
            "work-life imbalance", "politics", "slow promotion", "outdated systems",
            "poor communication", "overworked", "demanding", "no work-life balance",
        ]

        pros = []
        cons = []
        all_text = " ".join(reviews).lower()

        for keyword in positive_keywords:
            if keyword in all_text:
                pros.append(keyword.title())

        for keyword in negative_keywords:
            if keyword in all_text:
                cons.append(keyword.title())

        return pros[:7], cons[:7]

    def get_platform_info(self) -> list[dict[str, Any]]:
        """Get information about supported platforms."""
        platforms = []

        for source_id, info in self.WORKPLACE_PLATFORMS.items():
            platforms.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "workplace_platform",
                "metrics": info["metrics"],
            })

        for source_id, info in self.HEALTHCARE_PLATFORMS.items():
            platforms.append({
                "id": source_id,
                "name": info["name"],
                "url": info["url"],
                "description": info["description"],
                "type": "healthcare_platform",
                "roles": info.get("roles", []),
            })

        return platforms
