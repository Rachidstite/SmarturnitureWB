from manufacturing.drawer_structural_report import DrawerStructuralReport


class DrawerStructuralBuilder:

    def build(self, validation_report):
        structural_risk = "HIGH" if getattr(validation_report, "requires_review", False) else "LOW"
        requires_reinforcement = bool(getattr(validation_report, "requires_review", False))

        if getattr(validation_report, "drawer_width_risk", "") == "HIGH":
            slide_capacity_risk = "HIGH"
        else:
            slide_capacity_risk = "LOW"

        if getattr(validation_report, "bottom_panel_warning", ""):
            bottom_panel_risk = "MEDIUM"
        else:
            bottom_panel_risk = "LOW"

        structural_recommendation = ""
        if structural_risk == "HIGH":
            structural_recommendation = "Review drawer structure and slide capacity"

        return DrawerStructuralReport(
            structural_risk=structural_risk,
            slide_capacity_risk=slide_capacity_risk,
            bottom_panel_risk=bottom_panel_risk,
            requires_reinforcement=requires_reinforcement,
            structural_recommendation=structural_recommendation,
        )
