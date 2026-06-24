from manufacturing.cabinet_structural_report import CabinetStructuralReport


class CabinetStructuralBuilder:

    def build(
        self,
        back_panel_intelligence_report,
        drawer_intelligence_report=None,
        shelf_structural_report=None,
    ):
        structural_risk = "LOW"
        stability_risk = "LOW"
        requires_center_support = False
        requires_reinforcement = False
        anti_racking_risk = "LOW"

        back_panel_decision = getattr(back_panel_intelligence_report, "decision", None)
        back_panel_structural = getattr(
            back_panel_intelligence_report,
            "structural",
            None,
        )

        if getattr(back_panel_decision, "requires_review", False):
            structural_risk = "MEDIUM"

        if getattr(back_panel_structural, "structural_risk", "LOW") == "HIGH":
            structural_risk = "HIGH"

        if getattr(back_panel_structural, "requires_reinforcement", False):
            requires_reinforcement = True

        racking_resistance = getattr(
            back_panel_structural,
            "racking_resistance",
            "UNKNOWN",
        )
        if racking_resistance == "LOW":
            anti_racking_risk = "HIGH"
        elif racking_resistance == "MEDIUM":
            anti_racking_risk = "MEDIUM"
        else:
            anti_racking_risk = "LOW"

        drawer_decision = getattr(drawer_intelligence_report, "decision", None)
        if drawer_intelligence_report is not None and getattr(
            drawer_decision,
            "requires_review",
            False,
        ):
            stability_risk = "MEDIUM"

        if shelf_structural_report is not None:
            if getattr(shelf_structural_report, "span_risk", "LOW") == "HIGH":
                structural_risk = "HIGH"
            if getattr(shelf_structural_report, "support_required", False):
                requires_reinforcement = True
            if getattr(shelf_structural_report, "sagging_risk", "LOW") == "HIGH":
                stability_risk = "MEDIUM"

        if structural_risk == "HIGH" or anti_racking_risk == "HIGH":
            requires_center_support = True

        shelf_recommendation = getattr(
            shelf_structural_report,
            "shelf_recommendation",
            "",
        )

        if structural_risk == "HIGH" or anti_racking_risk == "HIGH":
            structural_recommendation = "Cabinet requires structural reinforcement review"
        elif (
            structural_risk == "MEDIUM"
            or stability_risk == "MEDIUM"
            or anti_racking_risk == "MEDIUM"
        ):
            structural_recommendation = "Cabinet should be reviewed before production"
        else:
            structural_recommendation = ""

        if shelf_recommendation:
            structural_recommendation = shelf_recommendation

        return CabinetStructuralReport(
            structural_risk=structural_risk,
            stability_risk=stability_risk,
            requires_center_support=requires_center_support,
            requires_reinforcement=requires_reinforcement,
            anti_racking_risk=anti_racking_risk,
            structural_recommendation=structural_recommendation,
            shelf_structural=(
                shelf_structural_report
                if shelf_structural_report is not None
                else CabinetStructuralReport().shelf_structural
            ),
        )
