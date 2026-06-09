from validation.intelligence.unused_operation_recommendation import (
    UnusedOperationRecommendation,
)

from validation.intelligence.hardware_recommendation_rule import (
    HardwareRecommendationRule,
)


class RecommendationRegistry:

    @staticmethod
    def get_rules():

        return [
            UnusedOperationRecommendation(),
            HardwareRecommendationRule(),
        ]
