from validation.intelligence.engineering.recommendations.engineering_recommendation import (
    EngineeringRecommendation,
)

from validation.intelligence.engineering.recommendations.recommendation_registry import (
    RECOMMENDATIONS,
)


class EngineeringRecommendationEngine:

    def generate(
        self,
        warning_codes,
    ):

        recommendations = []

        for code in warning_codes:

            data = RECOMMENDATIONS.get(code)

            if data is None:
                continue

            recommendations.append(
                EngineeringRecommendation(
                    title=data["title"],
                    description=data["description"],
                    severity=data["severity"],
                )
            )

        return recommendations
