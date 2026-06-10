from validation.intelligence.engineering.roi.engineering_roi import (
    EngineeringROI,
)

from validation.intelligence.engineering.roi.roi_registry import (
    ROI_REGISTRY,
)


class EngineeringROIEngine:

    def evaluate(
        self,
        code,
    ):

        data = ROI_REGISTRY.get(
            code,
            {
                "rating": "LOW",
                "score": 20,
            },
        )

        return EngineeringROI(
            code=code,
            rating=data["rating"],
            score=data["score"],
        )
