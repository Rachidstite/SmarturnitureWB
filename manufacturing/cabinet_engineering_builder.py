from manufacturing.cabinet_engineering_report import CabinetEngineeringReport


TALL = 1800.0
VERY_TALL = 2200.0
WIDE = 1000.0
VERY_WIDE = 1200.0


class CabinetEngineeringBuilder:

    def build(self, cabinet_height=0.0, cabinet_width=0.0):
        if cabinet_height >= VERY_TALL:
            cabinet_height_risk = "HIGH"
        elif cabinet_height >= TALL:
            cabinet_height_risk = "MEDIUM"
        else:
            cabinet_height_risk = "LOW"

        if cabinet_width >= VERY_WIDE:
            cabinet_width_risk = "HIGH"
        elif cabinet_width >= WIDE:
            cabinet_width_risk = "MEDIUM"
        else:
            cabinet_width_risk = "LOW"

        center_divider_required = cabinet_width_risk == "HIGH"
        wall_anchoring_recommended = cabinet_height_risk == "HIGH"
        shelf_support_recommended = (
            cabinet_width_risk == "HIGH" or cabinet_height_risk == "HIGH"
        )

        if cabinet_width_risk == "HIGH" or cabinet_height_risk == "HIGH":
            engineering_recommendation = "Cabinet engineering review required"
        elif cabinet_width_risk == "MEDIUM" or cabinet_height_risk == "MEDIUM":
            engineering_recommendation = "Cabinet engineering review recommended"
        else:
            engineering_recommendation = ""

        return CabinetEngineeringReport(
            cabinet_height_risk=cabinet_height_risk,
            cabinet_width_risk=cabinet_width_risk,
            center_divider_required=center_divider_required,
            wall_anchoring_recommended=wall_anchoring_recommended,
            shelf_support_recommended=shelf_support_recommended,
            engineering_recommendation=engineering_recommendation,
        )
