from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedScore:

    score: int

    grade: str

    explanation: str
