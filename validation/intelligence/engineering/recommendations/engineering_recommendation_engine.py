from validation.intelligence.engineering.recommendations.engineering_recommendation import (
    EngineeringRecommendation,
)

from validation.intelligence.engineering.recommendations.recommendation_registry import (
    RECOMMENDATIONS,
)

from validation.intelligence.engineering.recommendations.recommendation_priority import (
    RecommendationPriority,
)

from validation.intelligence.engineering.roi.engineering_roi_engine import (
    EngineeringROIEngine,
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

            roi = (
                EngineeringROIEngine()
                .evaluate(code)
            )

            recommendations.append(
                EngineeringRecommendation(
                    title=data["title"],
                    description=data["description"],
                    severity=data["severity"],
                    priority=RecommendationPriority.for_code(
                        code
                    ),
                    roi_rating=roi.rating,
                    roi_score=roi.score,
                )
            )

        return recommendations
