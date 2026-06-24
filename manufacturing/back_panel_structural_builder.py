from manufacturing.back_panel_fixing_strategy import BackPanelFixingStrategy
from manufacturing.back_panel_structural_report import BackPanelStructuralReport


class BackPanelStructuralBuilder:

    def build(self, validation_report, fixing_report):
        requires_center_support = getattr(
            validation_report,
            "center_support_required",
            False,
        )
        structural_risk = "HIGH" if requires_center_support else "LOW"
        requires_reinforcement = bool(requires_center_support)

        strategy = getattr(fixing_report, "strategy", "")
        if strategy == BackPanelFixingStrategy.GROOVE:
            racking_resistance = "HIGH"
        elif strategy == BackPanelFixingStrategy.SCREWED:
            racking_resistance = "MEDIUM"
        elif strategy == BackPanelFixingStrategy.STAPLED:
            racking_resistance = "LOW"
        else:
            racking_resistance = "UNKNOWN"

        structural_recommendation = ""
        if structural_risk == "HIGH":
            structural_recommendation = "Add center support or reinforcement"

        if strategy == BackPanelFixingStrategy.STAPLED and requires_center_support:
            structural_risk = "HIGH"
            requires_reinforcement = True
            structural_recommendation = "Replace stapled fixing or add reinforcement"
        elif strategy == BackPanelFixingStrategy.GROOVE and requires_center_support:
            structural_recommendation = "Consider center support for large cabinet"

        return BackPanelStructuralReport(
            structural_risk=structural_risk,
            racking_resistance=racking_resistance,
            requires_center_support=requires_center_support,
            requires_reinforcement=requires_reinforcement,
            structural_recommendation=structural_recommendation,
        )
