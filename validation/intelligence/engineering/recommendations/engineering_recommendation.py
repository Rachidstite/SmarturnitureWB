from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringRecommendation:

    title: str

    description: str

    severity: str

    priority: str

    roi_rating: str = "LOW"

    roi_score: int = 0
