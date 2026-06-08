from validation.intelligence.engineering.recommendations.engineering_recommendation import (
    EngineeringRecommendation,
)

from validation.intelligence.engineering.recommendations.recommendation_registry import (
    RECOMMENDATIONS,
)

from validation.intelligence.engineering.recommendations.recommendation_priority import (
    RecommendationPriority,
)


class EngineeringRecommendationEngine:

    def generate(
        self,
        warning_codes,
    ):

        recommendations = []

        for code in warning_codes:

            data = RECOMMENDATIONS.get(code)

            if not data:
                continue

            recommendations.append(
                EngineeringRecommendation(
                    title=data["title"],
                    description=data["description"],
                    severity=data["severity"],
                    priority=RecommendationPriority.for_code(
                        code
                    ),
                )
            )

        return recommendations
