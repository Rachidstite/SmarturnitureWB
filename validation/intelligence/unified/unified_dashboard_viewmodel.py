from dataclasses import dataclass


@dataclass
class UnifiedDashboardViewModel:

    score: int

    grade: str

    error_count: int

    warning_count: int

    recommendation_count: int = 0

    @classmethod
    def from_report(
        cls,
        report,
    ):
        return cls(
            score=report.score.score,
            grade=report.score.grade,
            error_count=len(
                getattr(
                    report,
                    "errors",
                    [],
                )
            ),
            warning_count=len(
                getattr(
                    report,
                    "warnings",
                    [],
                )
            ),
            recommendation_count=len(
                getattr(
                    report,
                    "recommendations",
                    [],
                )
            ),
        )
