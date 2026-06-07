from validation.intelligence.recommendation_registry import (
    RecommendationRegistry,
)


class RecommendationEngine:

    def recommend(
        self,
        panel_specs
    ):

        results = []

        for rule in (
            RecommendationRegistry
            .get_rules()
        ):

            results.extend(
                rule.recommend(
                    panel_specs
                )
            )

        return results
