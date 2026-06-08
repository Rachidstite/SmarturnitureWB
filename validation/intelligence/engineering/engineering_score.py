from dataclasses import dataclass


@dataclass(frozen=True)
class EngineeringScore:

    score: int

    grade: str

    explanation: str
