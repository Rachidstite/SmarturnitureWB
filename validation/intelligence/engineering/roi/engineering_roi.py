from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringROI:

    code: str

    rating: str

    score: int
