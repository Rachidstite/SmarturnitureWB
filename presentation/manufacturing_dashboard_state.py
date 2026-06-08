from dataclasses import dataclass, field


@dataclass(frozen=True)
class ManufacturingDashboardState:

    score: int

    grade: str

    warning_count: int

    recommendation_count: int

    recommendations: list = field(default_factory=list)

    cost_impact_count: int = 0

    can_export: bool = True

    @classmethod
    def from_viewmodel(
        cls,
        viewmodel,
    ):
        return cls(
            score=viewmodel.score,
            grade=viewmodel.grade,
            warning_count=viewmodel.warning_count,
            recommendation_count=viewmodel.recommendation_count,
            recommendations=getattr(
                viewmodel,
                "recommendations",
                []
            ),
            cost_impact_count=viewmodel.cost_impact_count,
            can_export=viewmodel.can_export,
        )
