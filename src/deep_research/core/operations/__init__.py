"""Concrete operations for the research framework."""

from deep_research.core.operations.decompose import DecomposeOperation
from deep_research.core.operations.answer import AnswerOperation
from deep_research.core.operations.synthesize import SynthesizeOperation
from deep_research.core.operations.detect import DetectOperation
from deep_research.core.operations.ground import GroundOperation

__all__ = [
    "DecomposeOperation",
    "AnswerOperation",
    "SynthesizeOperation",
    "DetectOperation",
    "GroundOperation",
]
