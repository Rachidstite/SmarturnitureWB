from validation.intelligence.drill_inside_panel_rule import (
    DrillInsidePanelRule,
)


class RulesRegistry:

    @staticmethod
    def get_rules():

        return [
            DrillInsidePanelRule(),
        ]
