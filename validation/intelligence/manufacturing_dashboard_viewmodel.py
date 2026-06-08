from dataclasses import dataclass


@dataclass
class ManufacturingDashboardViewModel:

    score: int

    grade: str

    warning_count: int

    structural_warning_count: int

    recommendation_count: int

    recommendations: list

    cost_impact_count: int

    can_export: bool

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
                report.structural_warnings
            ),

            recommendation_count=len(
                report.recommendations
            ),

            recommendations=[
                r.message
                for r in report.recommendations
            ],

            cost_impact_count=len(
                report.cost_impacts
            ),
            can_export=report.can_export,
        )
