from dataclasses import dataclass


@dataclass
class RecommendationResult:

    category: str

    title: str

    message: str
