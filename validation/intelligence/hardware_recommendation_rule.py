from validation.intelligence.recommendation_rule import (
    RecommendationRule,
)

from validation.intelligence.recommended_result import (
    RecommendationResult,
)

from domain.hardware_recommendation_engine import (
    HardwareRecommendationEngine,
)


class HardwareRecommendationRule(
    RecommendationRule
):

    def recommend(
        self,
        panel_specs
    ):

        results = []

        engine = (
            HardwareRecommendationEngine()
        )

        for panel in panel_specs:

            role = getattr(
                panel,
                "role",
                None,
            )

            span = getattr(
                panel,
                "width",
                0,
            )

            thickness = getattr(
                panel,
                "thickness",
                18,
            )

            recommendation = (
                engine.recommend(
                    role=role,
                    span=span,
                    thickness=thickness,
                )
            )

            if recommendation is None:
                continue

            results.append(
                RecommendationResult(
                    category="HARDWARE",
                    title=recommendation.hardware_type,
                    message=recommendation.reason,
                )
            )

        return results
