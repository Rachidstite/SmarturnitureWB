from dataclasses import dataclass

from validation.intelligence.recommended_result import (
    RecommendationResult,
)


@dataclass
class RecommendationReport:

    recommendations: list[RecommendationResult]
