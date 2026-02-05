"""Data sources for aggregating Mass General Psychiatry information."""

from .base import DataItem, DataSource
from .patient_reviews import PatientReviewAggregator
from .employee_reviews import EmployeeReviewAggregator
from .quality import QualityMetricsCollector
from .financial import FinancialOperationalCollector
from .news import NewsCollector

# Legacy import for backwards compatibility
from .reviews import ReviewAggregator

__all__ = [
    "DataItem",
    "DataSource",
    "PatientReviewAggregator",
    "EmployeeReviewAggregator",
    "QualityMetricsCollector",
    "FinancialOperationalCollector",
    "NewsCollector",
    "ReviewAggregator",  # Legacy
]
