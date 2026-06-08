from dataclasses import dataclass, field


@dataclass
class ManufacturingDashboardViewModel:

    score: int

    grade: str

    warning_count: int

    structural_warning_count: int = 0

    recommendation_count: int = 0

    recommendations: list = field(default_factory=list)

    cost_impact_count: int = 0

    can_export: bool = True

    @classmethod
    def from_report(
        cls,
        report
    ):
        return cls(
            score=report.score.score,
            grade=report.score.grade,
            warning_count=len(
                report.warnings
            ),

            structural_warning_count=len(
                getattr(
                    report,
                    "structural_warnings",
                    []
                )
            ),

            recommendation_count=len(
                report.recommendations
            ),

            recommendations=[
                getattr(
                    r,
                    "message",
                    str(r)
                )
                for r in report.recommendations
            ],

            cost_impact_count=len(
                report.cost_impacts
            ),

            can_export=report.can_export,
        )
