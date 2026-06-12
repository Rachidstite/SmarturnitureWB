from cost_intelligence.offcut_classification import OffcutClassification
from cost_intelligence.offcut_reuse_policy import OffcutReusePolicy


class OffcutClassifier:

    def __init__(
        self,
        policy=None,
    ):
        if policy is None:
            policy = OffcutReusePolicy(
                material="",
                thickness=0,
                min_width=80,
                min_height=80,
                min_area=10000,
            )

        self.policy = policy

    def classify(
        self,
        offcut,
    ):
        policy = self.policy

        if offcut.width < policy.min_width:
            return OffcutClassification(
                offcut_id=offcut.id,
                reusable=False,
                reason="Width below minimum",
            )

        if offcut.height < policy.min_height:
            return OffcutClassification(
                offcut_id=offcut.id,
                reusable=False,
                reason="Height below minimum",
            )

        if offcut.area < policy.min_area:
            return OffcutClassification(
                offcut_id=offcut.id,
                reusable=False,
                reason="Area below minimum",
            )

        return OffcutClassification(
            offcut_id=offcut.id,
        )
