from validation.intelligence.unused_operation_recommendation import (
    UnusedOperationRecommendation,
)


class RecommendationRegistry:

    @staticmethod
    def get_rules():

        return [
            UnusedOperationRecommendation(),
        ]
