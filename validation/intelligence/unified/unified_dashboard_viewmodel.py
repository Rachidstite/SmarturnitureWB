from dataclasses import dataclass, field


@dataclass
class UnifiedDashboardViewModel:

    score: int

    grade: str

    error_count: int

    warning_count: int

    recommendation_count: int = 0

    recommendations: list = field(
        default_factory=list
    )

    can_export: bool = True

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

            recommendations=[
                getattr(
                    r,
                    "message",
                    str(r)
                )
                for r in getattr(
                    report,
                    "recommendations",
                    [],
                )
            ],

            can_export=(
                len(
                    getattr(
                        report,
                        "errors",
                        [],
                    )
                ) == 0
            ),
        )
