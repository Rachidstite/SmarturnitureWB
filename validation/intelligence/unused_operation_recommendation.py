from validation.intelligence.recommended_result import (
    RecommendationResult,
)

from validation.intelligence.recommendation_rule import (
    RecommendationRule,
)


class UnusedOperationRecommendation(
    RecommendationRule
):

    def recommend(
        self,
        panel_specs
    ):

        results = []

        for panel in panel_specs:

            for op in getattr(
                panel,
                "unified_operations",
                []
            ):

                if not op.metadata.get(
                    "hardware_intent"
                ):

                    results.append(
                        RecommendationResult(
                            category="OPTIMIZATION",
                            title="Unused operation",
                            message=(
                                "Operation has no hardware intent"
                            )
                        )
                    )

        return results
