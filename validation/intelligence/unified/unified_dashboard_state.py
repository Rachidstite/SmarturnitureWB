from dataclasses import dataclass


@dataclass(frozen=True)
class UnifiedDashboardState:

    score: int

    grade: str

    error_count: int

    warning_count: int

    recommendation_count: int

    @classmethod
    def from_viewmodel(
        cls,
        viewmodel,
    ):
        return cls(
            score=viewmodel.score,
            grade=viewmodel.grade,
            error_count=viewmodel.error_count,
            warning_count=viewmodel.warning_count,
            recommendation_count=viewmodel.recommendation_count,
        )
