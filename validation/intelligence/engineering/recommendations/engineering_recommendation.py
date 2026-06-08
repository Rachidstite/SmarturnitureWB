from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringRecommendation:

    title: str

    description: str

    severity: str

    priority: str
