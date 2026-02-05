"""Data sources for aggregating Mass General Psychiatry information."""

from .base import DataSource
from .reviews import ReviewAggregator
from .quality import QualityMetricsCollector
from .news import NewsCollector

__all__ = ["DataSource", "ReviewAggregator", "QualityMetricsCollector", "NewsCollector"]
