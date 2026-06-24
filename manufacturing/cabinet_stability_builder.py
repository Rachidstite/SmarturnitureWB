from manufacturing.cabinet_stability_report import CabinetStabilityReport


TALL_CABINET_THRESHOLD = 1800.0
WIDE_CABINET_THRESHOLD = 1000.0


class CabinetStabilityBuilder:

    def build(self, cabinet_structural_report, cabinet_height=0.0, cabinet_width=0.0):
        tipping_risk = "LOW"
        large_span_risk = "LOW"

        if cabinet_height >= TALL_CABINET_THRESHOLD:
            tipping_risk = "MEDIUM"
        if (
            cabinet_height >= TALL_CABINET_THRESHOLD
            and getattr(cabinet_structural_report, "structural_risk", "LOW") == "HIGH"
        ):
            tipping_risk = "HIGH"

        if cabinet_width >= WIDE_CABINET_THRESHOLD:
            large_span_risk = "MEDIUM"
        if getattr(cabinet_structural_report, "anti_racking_risk", "LOW") == "HIGH":
            large_span_risk = "HIGH"

        wall_anchoring_required = tipping_risk == "HIGH"

        if tipping_risk == "HIGH":
            stability_recommendation = "Cabinet should be anchored and structurally reviewed"
        elif tipping_risk == "MEDIUM" or large_span_risk == "MEDIUM":
            stability_recommendation = "Cabinet stability should be reviewed"
        else:
            stability_recommendation = ""

        return CabinetStabilityReport(
            tipping_risk=tipping_risk,
            wall_anchoring_required=wall_anchoring_required,
            large_span_risk=large_span_risk,
            stability_recommendation=stability_recommendation,
        )
